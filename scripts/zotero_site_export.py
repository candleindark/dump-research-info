#!/usr/bin/env python3
"""Render reviewed Zotero publications as upstream-compatible site YAML.

The output is a migration candidate, not a website runtime dependency. The
website repository remains the authority after a reviewer copies and commits
the candidate records.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from typing import Any

import yaml

from zotero_ingest import validate_snapshot


DOI_SLUG = re.compile(r"[^a-z0-9]+")
ZOTERO_IDENTIFIER = re.compile(r"^zotero:group:(\d+):item:([A-Z0-9]+)$")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_policy(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("format_version") != 1:
        raise ValueError("Site migration policy must use format_version: 1")
    return value


def unique_strings(value: Any, label: str) -> set[str]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item for item in value
    ):
        raise ValueError(f"{label} must be a list of non-empty strings")
    if len(value) != len(set(value)):
        raise ValueError(f"{label} contains duplicate values")
    return set(value)


def policy_mapping(value: Any, label: str) -> dict[str, str]:
    if not isinstance(value, dict) or not all(
        isinstance(key, str) and key and isinstance(item, str) and item.strip()
        for key, item in value.items()
    ):
        raise ValueError(f"{label} must map non-empty strings to rationales")
    return value


def identifier_values(record: dict[str, Any], schema_type: str) -> list[str]:
    return [
        str(identifier["notation"])
        for identifier in record.get("identifiers", [])
        if isinstance(identifier, dict)
        and identifier.get("schema_type") == schema_type
        and identifier.get("notation")
    ]


def site_pid(record: dict[str, Any], overrides: dict[str, str]) -> str:
    source_pid = str(record.get("pid", ""))
    if source_pid in overrides:
        return overrides[source_pid]
    dois = identifier_values(record, "dlthings:DOI")
    if len(dois) == 1:
        slug = DOI_SLUG.sub("-", dois[0].casefold()).strip("-")
        return f"xyzrins:publications/doi-{slug}"
    zotero = identifier_values(record, "dlthings:Identifier")
    keys = sorted(
        match.group(2).casefold()
        for value in zotero
        if (match := ZOTERO_IDENTIFIER.fullmatch(value))
    )
    if not keys:
        raise ValueError(f"{source_pid}: no stable DOI or Zotero item identifier")
    return f"xyzrins:publications/zotero-{keys[0]}"


def add_schema_types(values: Any, schema_type: str) -> list[dict[str, Any]]:
    if not isinstance(values, list):
        raise ValueError(f"Expected a list of {schema_type} values")
    result: list[dict[str, Any]] = []
    for value in values:
        if not isinstance(value, dict):
            raise ValueError(f"Expected a mapping in {schema_type} values")
        typed = dict(value)
        typed["schema_type"] = schema_type
        result.append(typed)
    return result


def render_publication(
    record: dict[str, Any], policy: dict[str, Any], counters: Counter[str]
) -> dict[str, Any]:
    source_pid = str(record.get("pid", ""))
    if not source_pid or not record.get("title"):
        raise ValueError("Every source publication must define pid and title")
    overrides = policy.get("pid_overrides", {})
    if not isinstance(overrides, dict):
        raise ValueError("pid_overrides must be a mapping")
    allowed_people = unique_strings(
        policy.get("allowed_attribution_targets"), "allowed_attribution_targets"
    )
    omitted_people = policy_mapping(
        policy.get("omitted_attribution_targets"), "omitted_attribution_targets"
    )
    allowed_topics = unique_strings(
        policy.get("allowed_about_targets"), "allowed_about_targets"
    )
    omitted_generation = policy_mapping(
        policy.get("omitted_generation_objects"), "omitted_generation_objects"
    )
    allowed_curated_generation = unique_strings(
        policy.get("allowed_curated_generation_targets"),
        "allowed_curated_generation_targets",
    )
    curated_generations = policy.get("curated_generations")
    if not isinstance(curated_generations, dict):
        raise ValueError("curated_generations must be a mapping")

    output: dict[str, Any] = {
        "pid": site_pid(record, overrides),
        "schema_type": "xyzri:XYZPublication",
        "title": record["title"],
        "display_label": record.get("display_label", record["title"]),
    }
    for field in ("description", "kind"):
        if record.get(field):
            output[field] = record[field]
    if identifiers := record.get("identifiers"):
        output["identifiers"] = identifiers

    attributions: list[dict[str, Any]] = []
    for attribution in record.get("attributed_to", []):
        if not isinstance(attribution, dict) or not attribution.get("object"):
            raise ValueError(f"{source_pid}: malformed attribution")
        target = str(attribution["object"])
        if target in allowed_people:
            typed = dict(attribution)
            typed["schema_type"] = "dlthings:Attribution"
            attributions.append(typed)
        elif target in omitted_people:
            counters[f"omitted attribution {target}"] += 1
        else:
            raise ValueError(f"{source_pid}: unreviewed attribution target {target}")
    if attributions:
        output["attributed_to"] = attributions

    about = record.get("about", [])
    if not isinstance(about, list):
        raise ValueError(f"{source_pid}: about must be a list")
    unknown_topics = sorted(set(about) - allowed_topics)
    if unknown_topics:
        raise ValueError(f"{source_pid}: unreviewed topic targets {unknown_topics}")
    if about:
        output["about"] = about

    if attributes := record.get("attributes"):
        output["attributes"] = add_schema_types(
            attributes, "dlthings:AttributeSpecification"
        )
    for generation in record.get("generated_by", []):
        if not isinstance(generation, dict) or not generation.get("object"):
            raise ValueError(f"{source_pid}: malformed generation")
        target = str(generation["object"])
        if target not in omitted_generation:
            raise ValueError(f"{source_pid}: unreviewed generation target {target}")
        counters[f"omitted generation {target}"] += 1
    curated = curated_generations.get(source_pid, [])
    if not isinstance(curated, list):
        raise ValueError(f"{source_pid}: curated_generations must be a list")
    retained: list[dict[str, Any]] = []
    for generation in curated:
        if not isinstance(generation, dict) or not generation.get("object"):
            raise ValueError(f"{source_pid}: malformed curated generation")
        target = str(generation["object"])
        if target not in allowed_curated_generation:
            raise ValueError(
                f"{source_pid}: unreviewed curated generation target {target}"
            )
        typed = {key: value for key, value in generation.items() if key != "rationale"}
        typed["schema_type"] = "dlthings:Generation"
        retained.append(typed)
    if retained:
        output["generated_by"] = retained
    return output


def yaml_bytes(record: dict[str, Any]) -> bytes:
    return yaml.safe_dump(
        record,
        allow_unicode=True,
        sort_keys=False,
        width=88,
    ).encode("utf-8")


def directory_digest(files: dict[str, bytes]) -> str:
    digest = hashlib.sha256()
    for name, payload in sorted(files.items()):
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(payload)
        digest.update(b"\0")
    return digest.hexdigest()


def command_export(args: argparse.Namespace) -> None:
    records = load_json(args.publications)
    snapshot = load_json(args.snapshot)
    policy = load_policy(args.policy)
    if not isinstance(records, list) or not all(
        isinstance(record, dict) for record in records
    ):
        raise ValueError("Promoted publications must be a JSON array of objects")
    source = snapshot.get("source") if isinstance(snapshot, dict) else None
    if not isinstance(source, dict):
        raise ValueError("Snapshot has no source provenance")
    validate_snapshot(snapshot)
    snapshot_keys = {
        str(item.get("data", item).get("key", ""))
        for item in snapshot["items"]
        if isinstance(item.get("data", item), dict)
    }
    source_group = int(source["group_id"])
    for record in records:
        zotero_identifiers = identifier_values(record, "dlthings:Identifier")
        matches = [
            match
            for value in zotero_identifiers
            if (match := ZOTERO_IDENTIFIER.fullmatch(value))
        ]
        if not matches:
            raise ValueError(f"{record.get('pid')}: no Zotero source identifier")
        for match in matches:
            if (
                int(match.group(1)) != source_group
                or match.group(2) not in snapshot_keys
            ):
                raise ValueError(
                    f"{record.get('pid')}: Zotero identifier is outside the snapshot"
                )

    counters: Counter[str] = Counter()
    curated_generations = policy.get("curated_generations", {})
    if not isinstance(curated_generations, dict):
        raise ValueError("curated_generations must be a mapping")
    source_pids = {str(record.get("pid", "")) for record in records}
    stale_curated = sorted(set(curated_generations) - source_pids)
    if stale_curated:
        raise ValueError(
            f"Curated generations target absent source records: {stale_curated}"
        )
    rendered = [render_publication(record, policy, counters) for record in records]
    by_pid = {record["pid"]: record for record in rendered}
    if len(by_pid) != len(rendered):
        raise ValueError("Site publication PID generation produced a collision")
    files = {
        f"{record['pid'].split('/')[-1]}.yaml": yaml_bytes(record)
        for record in rendered
    }
    if len(files) != len(rendered):
        raise ValueError("Site publication filenames are not unique")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    existing = {path.name for path in args.output_dir.glob("*.yaml")}
    for stale in sorted(existing - set(files)):
        (args.output_dir / stale).unlink()
    for name, payload in sorted(files.items()):
        (args.output_dir / name).write_bytes(payload)

    report = {
        "format_version": 1,
        "source": {
            "api_root": source.get("api_root"),
            "content_sha256": source.get("content_sha256"),
            "fetched_at": source.get("fetched_at"),
            "group_id": source.get("group_id"),
            "library_version": source.get("library_version"),
            "zotero_api_version": source.get("zotero_api_version"),
        },
        "inputs": {
            "policy_sha256": hashlib.sha256(args.policy.read_bytes()).hexdigest(),
            "publications_sha256": hashlib.sha256(
                args.publications.read_bytes()
            ).hexdigest(),
        },
        "output": {
            "publication_count": len(rendered),
            "sha256": directory_digest(files),
            "kinds": dict(
                sorted(Counter(str(record.get("kind")) for record in rendered).items())
            ),
        },
        "reviewed_omissions": dict(sorted(counters.items())),
        "pid_map": [
            {"site_pid": target["pid"], "source_pid": source_record["pid"]}
            for source_record, target in zip(records, rendered, strict=True)
        ],
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        f"Rendered {len(rendered)} site publication candidates to "
        f"{args.output_dir}; review {args.report}."
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publications", type=Path, required=True)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    return parser


def main() -> None:
    command_export(build_parser().parse_args())


if __name__ == "__main__":
    main()
