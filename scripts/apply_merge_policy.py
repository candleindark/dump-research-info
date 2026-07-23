#!/usr/bin/env python3
"""Apply reviewed scalar merge decisions to a generated copy of Things data."""

from __future__ import annotations

import argparse
import copy
import json
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml


RecordRef = tuple[str, dict[str, Any]]
ConflictKey = tuple[str, str, str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    return parser.parse_args()


def canonical_key(class_name: str, pid: str, field: str) -> ConflictKey:
    return class_name, pid.casefold(), field


def is_present_scalar(value: Any) -> bool:
    return not isinstance(value, (dict, list)) and value not in (None, "")


def value_key(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def load_documents(
    data_root: Path,
) -> tuple[list[tuple[Path, str, list[dict[str, Any]]]], dict[tuple[str, str], list[RecordRef]]]:
    documents: list[tuple[Path, str, list[dict[str, Any]]]] = []
    groups: dict[tuple[str, str], list[RecordRef]] = defaultdict(list)

    for path in sorted(data_root.rglob("*.json")):
        relative = path.relative_to(data_root)
        if len(relative.parts) < 2:
            raise ValueError(f"Expected source/Class.json below {data_root}: {relative}")
        source = relative.parts[0]
        records = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(records, list):
            raise ValueError(f"Expected a JSON array: {path}")
        cloned = copy.deepcopy(records)
        documents.append((relative, source, cloned))
        class_name = path.stem
        for record in cloned:
            if not isinstance(record, dict) or not isinstance(record.get("pid"), str):
                raise ValueError(f"Expected every {path} record to have a string pid")
            groups[(class_name, record["pid"].casefold())].append((source, record))

    return documents, groups


def detect_conflicts(
    groups: dict[tuple[str, str], list[RecordRef]],
) -> dict[ConflictKey, dict[str, Any]]:
    conflicts: dict[ConflictKey, dict[str, Any]] = {}
    for (class_name, canonical_pid), records in sorted(groups.items()):
        fields = sorted({field for _, record in records for field in record if field != "pid"})
        for field in fields:
            variants: dict[str, dict[str, Any]] = {}
            for source, record in records:
                value = record.get(field)
                if not is_present_scalar(value):
                    continue
                variant = variants.setdefault(value_key(value), {"value": value, "sources": []})
                if source not in variant["sources"]:
                    variant["sources"].append(source)
            if len(variants) > 1:
                pid = records[0][1]["pid"]
                key = canonical_key(class_name, pid, field)
                conflicts[key] = {
                    "class": class_name,
                    "pid": pid,
                    "field": field,
                    "variants": sorted(variants.values(), key=lambda item: value_key(item["value"])),
                }
    return conflicts


def load_policy(path: Path) -> tuple[dict[str, Any], dict[ConflictKey, dict[str, Any]]]:
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict) or document.get("format_version") != 1:
        raise ValueError("Merge policy must be a mapping with format_version: 1")

    policies: dict[ConflictKey, dict[str, Any]] = {}
    for item in document.get("conflicts", []):
        key = canonical_key(item["class"], item["pid"], item["field"])
        if key in policies:
            raise ValueError(f"Duplicate policy entry: {key}")
        resolution = item.get("resolution", {})
        if ("source" in resolution) == ("value" in resolution):
            raise ValueError(f"Resolution must define exactly one of source or value: {key}")
        policies[key] = item
    return document, policies


def choose_value(
    key: ConflictKey,
    policy: dict[str, Any],
    records: list[RecordRef],
) -> Any:
    resolution = policy["resolution"]
    if "value" in resolution:
        return resolution["value"]

    source = resolution["source"]
    values = {
        value_key(record.get(key[2])): record.get(key[2])
        for record_source, record in records
        if record_source == source and is_present_scalar(record.get(key[2]))
    }
    if len(values) != 1:
        raise ValueError(
            f"Policy source {source!r} supplies {len(values)} values for {key}; expected exactly one"
        )
    return next(iter(values.values()))


def main() -> int:
    args = parse_args()
    data_root = args.data_root.resolve()
    output = args.output.resolve()
    if output == data_root or data_root in output.parents:
        raise ValueError("Output must not be the input data directory or a child of it")

    documents, groups = load_documents(data_root)
    policy_document, policies = load_policy(args.policy)
    conflicts = detect_conflicts(groups)
    observed = set(conflicts)
    approved = set(policies)
    if observed != approved:
        missing = sorted(observed - approved)
        stale = sorted(approved - observed)
        raise ValueError(f"Merge policy mismatch; unapproved={missing}, stale={stale}")

    resolutions: list[dict[str, Any]] = []
    for key in sorted(observed):
        class_name, canonical_pid, field = key
        records = groups[(class_name, canonical_pid)]
        selected = choose_value(key, policies[key], records)
        changed = 0
        for _, record in records:
            if is_present_scalar(record.get(field)) and record[field] != selected:
                record[field] = selected
                changed += 1
        resolutions.append(
            {
                **conflicts[key],
                "selected": selected,
                "resolution": policies[key]["resolution"],
                "rationale": policies[key].get("rationale"),
                "evidence": policies[key].get("evidence", []),
                "changed_records": changed,
            }
        )

    remaining = detect_conflicts(groups)
    if remaining:
        raise ValueError(f"Resolved data still contains scalar conflicts: {sorted(remaining)}")

    if output.exists():
        shutil.rmtree(output)
    for relative, _, records in documents:
        destination = output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(records, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    report = {
        "format_version": 1,
        "policy": str(args.policy),
        "policy_description": policy_document.get("description"),
        "source_documents": len(documents),
        "source_records": sum(len(records) for _, _, records in documents),
        "observed_conflicts": len(conflicts),
        "remaining_conflicts": 0,
        "resolutions": resolutions,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "observed_conflicts": len(conflicts),
                "remaining_conflicts": 0,
                "output": str(args.output),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
