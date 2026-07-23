#!/usr/bin/env python3
"""Build a static CON website from validated source-scoped JSON records."""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import shutil
from typing import Any, Iterable
import unicodedata

from jinja2 import Environment, FileSystemLoader, select_autoescape
import yaml


@dataclass(frozen=True)
class ClassConfig:
    singular: str
    plural: str
    path: str
    intro: str


CLASS_CONFIG = {
    "XYZPerson": ClassConfig(
        "Person",
        "People",
        "people",
        "Researchers, engineers, maintainers, and collaborators connected to CON.",
    ),
    "XYZOrganization": ClassConfig(
        "Organization",
        "Organizations",
        "organizations",
        "Institutions, communities, and funders participating in open neuroscience.",
    ),
    "XYZProject": ClassConfig(
        "Project",
        "Projects",
        "projects",
        "Collective efforts that turn open-science principles into working infrastructure.",
    ),
    "XYZGrant": ClassConfig(
        "Grant",
        "Grants",
        "grants",
        "Awards and funding relationships supporting the center's work.",
    ),
    "XYZPublication": ClassConfig(
        "Publication",
        "Publications",
        "publications",
        "Articles, preprints, reports, and other published research outputs.",
    ),
    "XYZDataset": ClassConfig(
        "Dataset",
        "Datasets",
        "datasets",
        "Reusable research data published through open repositories and archives.",
    ),
    "XYZInstrument": ClassConfig(
        "Software",
        "Software",
        "software",
        "Software and operational tools used to make research reproducible.",
    ),
}

CLASS_ORDER = tuple(CLASS_CONFIG)
DEFAULT_SOURCE_ORDER = (
    "con_site",
    "zotero_centerforopenneuroscience",
    "pool_psychoinformatics_de",
)
SOURCE_ORDER_BY_CLASS = {
    "XYZDataset": (
        "zotero_centerforopenneuroscience",
        "con_site",
        "pool_psychoinformatics_de",
    ),
    "XYZPublication": (
        "zotero_centerforopenneuroscience",
        "con_site",
        "pool_psychoinformatics_de",
    ),
    "XYZPublicationVenue": (
        "pool_psychoinformatics_de",
        "zotero_centerforopenneuroscience",
        "con_site",
    ),
}

RELATION_FIELDS = {
    "about": "Topics",
    "associated_with": "People and partners",
    "attributed_to": "Contributors",
    "derived_from": "Derived from",
    "generated_by": "Publication context",
    "influenced_by": "Influenced by",
    "part_of": "Part of",
    "relations": "Related records",
    "revision_of": "Revision of",
    "specialization_of": "Specialization of",
    "used": "Uses",
}

FACT_FIELDS = {
    "application_deadline": "Application deadline",
    "ended": "Ended",
    "keywords": "Keywords",
    "short_name": "Short name",
    "started": "Started",
}

HIDDEN_FIELDS = {
    "additional_names",
    "annotations",
    "attributes",
    "broad_mappings",
    "characterized_by",
    "close_mappings",
    "depiction",
    "description",
    "display_label",
    "display_note",
    "editorial_notes",
    "exact_mappings",
    "family_name",
    "formatted_name",
    "given_name",
    "honorific_name_prefix",
    "honorific_name_suffix",
    "identifiers",
    "kind",
    "name",
    "narrow_mappings",
    "nickname",
    "pid",
    "related_mappings",
    "schema_type",
    "title",
    *RELATION_FIELDS,
}


def clean_text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def has_value(value: Any) -> bool:
    return value not in (None, "", [], {})


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def slugify(value: str) -> str:
    text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text[:64] or "record"


def normalize_base_path(value: str) -> str:
    value = f"/{value.strip('/')}" if value.strip("/") else "/"
    return value if value.endswith("/") else f"{value}/"


def with_base(base_path: str, relative: str = "") -> str:
    relative = relative.lstrip("/")
    return f"{base_path}{relative}" if relative else base_path


def load_entity_media(
    config_path: Path,
    inventory_path: Path,
    site_root: Path,
    base_path: str,
) -> dict[str, dict[str, Any]]:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    approval = config.get("approval", {})
    if approval.get("status") != "approved":
        raise ValueError(f"Entity media are not approved in {config_path}")

    media: dict[str, dict[str, Any]] = {}
    specifications = (
        ("people", "name", "portrait"),
        ("projects", "title", "logo"),
    )
    for section, name_field, image_kind in specifications:
        mappings = config.get("entities", {}).get(section, {})
        seen_names: set[str] = set()
        for order, entry in enumerate(inventory.get(section, [])):
            source_name = clean_text(entry.get(name_field))
            if source_name not in mappings:
                raise ValueError(
                    f"Missing {section} media decision for {source_name!r} in {config_path}"
                )
            pid = clean_text(mappings[source_name])
            if not pid or pid in media:
                raise ValueError(f"Invalid or duplicate entity media PID: {pid!r}")
            seen_names.add(source_name)

            images = entry.get("images", [])
            image_url = None
            image_alt = source_name
            if images:
                image = images[0]
                source_ref = clean_text(image.get("raw") or image.get("url"))
                marker = "/theme/img/"
                if marker in source_ref:
                    relative = source_ref.split(marker, 1)[1]
                elif source_ref.startswith("theme/img/"):
                    relative = source_ref.removeprefix("theme/img/")
                else:
                    raise ValueError(f"Unsupported current-site image reference: {source_ref}")
                asset_path = Path("assets") / "current-site" / relative
                if not (site_root / asset_path).is_file():
                    raise ValueError(f"Missing approved current-site asset: {asset_path}")
                image_url = with_base(base_path, asset_path.as_posix())
                image_alt = clean_text(image.get("alt")) or source_name

            media[pid] = {
                "display_group": clean_text(entry.get("group") or entry.get("category")),
                "display_order": order,
                "image": image_url,
                "image_alt": image_alt,
                "image_kind": image_kind,
            }

        stale_names = sorted(set(mappings) - seen_names)
        if stale_names:
            raise ValueError(
                f"Stale {section} media decisions in {config_path}: {stale_names}"
            )
    return media


def record_label(record: dict[str, Any]) -> str:
    for field in (
        "display_label",
        "formatted_name",
        "title",
        "name",
        "short_name",
        "notation",
        "pid",
    ):
        if value := clean_text(record.get(field)):
            return value
    return "Untitled record"


def source_rank(class_name: str, source: str) -> tuple[int, str]:
    order = SOURCE_ORDER_BY_CLASS.get(class_name, DEFAULT_SOURCE_ORDER)
    try:
        return order.index(source), source
    except ValueError:
        return len(order), source


def merge_list(values: Iterable[Any]) -> list[Any]:
    merged: list[Any] = []
    seen: set[str] = set()
    for value in values:
        candidates = value if isinstance(value, list) else [value]
        for candidate in candidates:
            key = canonical(candidate)
            if key not in seen:
                merged.append(candidate)
                seen.add(key)
    return merged


def load_observations(data_root: Path) -> tuple[dict[tuple[str, str], list[dict[str, Any]]], dict[str, Any]]:
    observations: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    malformed: list[dict[str, Any]] = []
    source_counts: dict[str, int] = defaultdict(int)

    for source_dir in sorted(path for path in data_root.iterdir() if path.is_dir()):
        for path in sorted(source_dir.glob("*.json")):
            with path.open(encoding="utf-8") as stream:
                records = json.load(stream)
            if not isinstance(records, list):
                malformed.append({"file": str(path), "reason": "not a JSON array"})
                continue
            for index, record in enumerate(records):
                if not isinstance(record, dict) or not clean_text(record.get("pid")):
                    malformed.append(
                        {"file": str(path), "index": index, "reason": "missing record PID"}
                    )
                    continue
                source_counts[source_dir.name] += 1
                observations[(path.stem, str(record["pid"]))].append(
                    {
                        "file": str(path),
                        "record": record,
                        "source": source_dir.name,
                    }
                )
    return observations, {
        "malformed": malformed,
        "source_counts": dict(sorted(source_counts.items())),
        "source_record_count": sum(source_counts.values()),
    }


def merge_observations(
    observations: dict[tuple[str, str], list[dict[str, Any]]]
) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    merged_by_class: dict[str, list[dict[str, Any]]] = defaultdict(list)
    conflicts: list[dict[str, Any]] = []

    for (class_name, pid), entries in sorted(observations.items()):
        entries = sorted(entries, key=lambda entry: source_rank(class_name, entry["source"]))
        keys = sorted({key for entry in entries for key in entry["record"]})
        merged: dict[str, Any] = {"pid": pid}

        for key in keys:
            if key == "pid":
                continue
            choices = [
                (entry["source"], entry["record"][key])
                for entry in entries
                if key in entry["record"] and has_value(entry["record"][key])
            ]
            if not choices:
                continue
            if any(isinstance(value, list) for _, value in choices):
                merged[key] = merge_list(value for _, value in choices)
            else:
                merged[key] = choices[0][1]

            distinct = {canonical(value) for _, value in choices}
            if len(distinct) > 1 and not any(isinstance(value, list) for _, value in choices):
                conflicts.append(
                    {
                        "class": class_name,
                        "field": key,
                        "pid": pid,
                        "selected_source": choices[0][0],
                        "values": [
                            {"source": source, "value": value} for source, value in choices
                        ],
                    }
                )

        merged["_sources"] = [entry["source"] for entry in entries]
        merged_by_class[class_name].append(merged)

    for records in merged_by_class.values():
        records.sort(key=lambda record: (record_label(record).casefold(), record["pid"]))
    return merged_by_class, conflicts


def friendly_curie(value: str) -> str:
    tail = value.rsplit("/", 1)[-1].rsplit("#", 1)[-1]
    if ":" in tail:
        tail = tail.split(":", 1)[-1]
    return re.sub(r"[_-]+", " ", tail).strip().title() or value


def publication_date(record: dict[str, Any]) -> str:
    for event in record.get("generated_by", []):
        if isinstance(event, dict) and clean_text(event.get("at_time")):
            return clean_text(event["at_time"])
    for attribute in record.get("attributes", []):
        if not isinstance(attribute, dict):
            continue
        if attribute.get("predicate") in {"dcterms:issued", "schema:datePublished"}:
            return clean_text(attribute.get("value"))
    return ""


class SiteModel:
    def __init__(
        self,
        merged: dict[str, list[dict[str, Any]]],
        base_path: str,
        entity_media: dict[str, dict[str, Any]],
    ) -> None:
        self.merged = merged
        self.base_path = base_path
        self.entity_media = entity_media
        self.labels: dict[str, str] = {}
        self.entity_records: dict[tuple[str, str], dict[str, Any]] = {}
        self.routes: dict[tuple[str, str], str] = {}
        self.pid_routes: dict[str, list[str]] = defaultdict(list)

        for records in merged.values():
            for record in records:
                self.labels[str(record["pid"])] = record_label(record)
        for class_name in CLASS_ORDER:
            for record in merged.get(class_name, []):
                key = (class_name, str(record["pid"]))
                label = record_label(record)
                digest = hashlib.sha256(str(record["pid"]).encode()).hexdigest()[:8]
                relative = f"{CLASS_CONFIG[class_name].path}/{slugify(label)}-{digest}/"
                self.entity_records[key] = record
                self.routes[key] = with_base(base_path, relative)
                self.pid_routes[str(record["pid"])].append(self.routes[key])

        self.incoming: dict[tuple[str, str], list[tuple[str, str]]] = defaultdict(list)
        entity_pids = set(self.pid_routes)
        for source_key, record in self.entity_records.items():
            for referenced_pid in self.walk_strings(record):
                if referenced_pid == source_key[1] or referenced_pid not in entity_pids:
                    continue
                for target_key in self.entity_records:
                    if target_key[1] == referenced_pid:
                        self.incoming[target_key].append(source_key)

    @staticmethod
    def walk_strings(value: Any) -> Iterable[str]:
        if isinstance(value, str):
            yield value
        elif isinstance(value, dict):
            for item in value.values():
                yield from SiteModel.walk_strings(item)
        elif isinstance(value, list):
            for item in value:
                yield from SiteModel.walk_strings(item)

    def label(self, value: Any) -> str:
        if isinstance(value, dict):
            value = value.get("object") or value.get("pid") or value.get("value")
        text = clean_text(value)
        return self.labels.get(text, friendly_curie(text)) if text else "Unspecified"

    def href(self, value: Any) -> str | None:
        if isinstance(value, dict):
            value = value.get("object") or value.get("pid")
        text = clean_text(value)
        routes = self.pid_routes.get(text, [])
        if len(routes) == 1:
            return routes[0]
        if text.startswith(("http://", "https://")):
            return text
        return None

    def ref(self, value: Any) -> dict[str, Any]:
        if isinstance(value, dict):
            target = value.get("object") or value.get("pid") or value.get("value")
            metadata: list[str] = []
            for role in value.get("roles", []):
                metadata.append(self.label(role))
            if at_time := clean_text(value.get("at_time")):
                metadata.append(at_time)
            if location := value.get("at_location"):
                metadata.append(self.label(location))
            return {
                "href": self.href(target),
                "label": self.label(target),
                "metadata": metadata,
            }
        return {"href": self.href(value), "label": self.label(value), "metadata": []}

    def prepare(self, class_name: str, record: dict[str, Any]) -> dict[str, Any]:
        config = CLASS_CONFIG[class_name]
        key = (class_name, str(record["pid"]))
        label = record_label(record)
        relations: list[dict[str, Any]] = []
        for field, heading in RELATION_FIELDS.items():
            value = record.get(field)
            if not has_value(value):
                continue
            values = value if isinstance(value, list) else [value]
            relations.append(
                {"heading": heading, "items": [self.ref(item) for item in values]}
            )

        attributes = []
        for attribute in record.get("attributes", []):
            if not isinstance(attribute, dict):
                continue
            if attribute.get("predicate") == "foaf:depiction":
                continue
            value = attribute.get("value")
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False, sort_keys=True)
            attributes.append(
                {
                    "label": self.label(attribute.get("predicate")),
                    "value": clean_text(value),
                }
            )

        facts = []
        for field, heading in FACT_FIELDS.items():
            if not has_value(record.get(field)):
                continue
            value = record[field]
            if isinstance(value, list):
                value = ", ".join(self.label(item) for item in value)
            elif isinstance(value, dict):
                value = self.label(value)
            facts.append({"label": heading, "value": clean_text(value)})
        for field in sorted(set(record) - HIDDEN_FIELDS - set(FACT_FIELDS) - {"_sources"}):
            value = record[field]
            if isinstance(value, (dict, list)) or not has_value(value):
                continue
            facts.append({"label": friendly_curie(field), "value": clean_text(value)})

        identifiers = []
        for identifier in record.get("identifiers", []):
            if not isinstance(identifier, dict):
                continue
            notation = clean_text(identifier.get("notation"))
            identifiers.append(
                {
                    "href": notation if notation.startswith(("http://", "https://")) else None,
                    "label": self.label(identifier.get("schema_type") or "Identifier"),
                    "value": notation,
                }
            )

        backlinks = []
        seen_backlinks: set[tuple[str, str]] = set()
        for backlink_key in self.incoming.get(key, []):
            if backlink_key in seen_backlinks:
                continue
            backlinks.append(
                {
                    "href": self.routes[backlink_key],
                    "kicker": CLASS_CONFIG[backlink_key[0]].singular,
                    "label": record_label(self.entity_records[backlink_key]),
                }
            )
            seen_backlinks.add(backlink_key)
        backlinks.sort(key=lambda item: (item["kicker"], item["label"].casefold()))

        kind = self.ref(record["kind"]) if has_value(record.get("kind")) else None
        topics = [self.ref(value) for value in record.get("about", [])]
        description = clean_text(record.get("description") or record.get("display_note"))
        date = publication_date(record)
        media = self.entity_media.get(str(record["pid"]), {})
        return {
            "attributes": attributes,
            "backlinks": backlinks,
            "class_name": class_name,
            "config": config,
            "date": date,
            "description": description,
            "display_group": clean_text(media.get("display_group")),
            "display_order": media.get("display_order"),
            "facts": facts,
            "href": self.routes[key],
            "identifiers": identifiers,
            "image": media.get("image"),
            "image_alt": clean_text(media.get("image_alt")) or label,
            "image_kind": clean_text(media.get("image_kind")),
            "kind": kind,
            "kind_label": kind["label"] if kind else config.singular,
            "label": label,
            "pid": record["pid"],
            "relations": relations,
            "sources": record.get("_sources", []),
            "topics": topics,
        }


def public_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in record.items()
        if key not in {"_sources", "annotations", "editorial_notes"}
    }


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, sort_keys=True)
        stream.write("\n")


def build(args: argparse.Namespace) -> dict[str, Any]:
    base_path = normalize_base_path(args.base_path)
    observations, load_report = load_observations(args.data_root)
    merged, conflicts = merge_observations(observations)
    entity_media = load_entity_media(
        args.entity_assets,
        args.con_site_inventory,
        args.site_root,
        base_path,
    )
    model = SiteModel(merged, base_path, entity_media)

    output = args.output
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    shutil.copytree(args.site_root / "assets", output / "assets", dirs_exist_ok=True)

    environment = Environment(
        loader=FileSystemLoader(args.site_root / "templates"),
        autoescape=select_autoescape(("html", "xml")),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    items_by_class: dict[str, list[dict[str, Any]]] = {}
    for class_name in CLASS_ORDER:
        items = [model.prepare(class_name, record) for record in merged.get(class_name, [])]
        if class_name == "XYZPublication":
            items.sort(key=lambda item: (item["date"], item["label"].casefold()), reverse=True)
        elif class_name in {"XYZPerson", "XYZProject"}:
            items.sort(
                key=lambda item: (
                    item["display_order"] is None,
                    item["display_order"] if item["display_order"] is not None else 0,
                    item["label"].casefold(),
                )
            )
        else:
            items.sort(key=lambda item: item["label"].casefold())
        items_by_class[class_name] = items

    nav = [
        {
            "count": len(items_by_class[class_name]),
            "href": with_base(base_path, f"{CLASS_CONFIG[class_name].path}/"),
            "label": CLASS_CONFIG[class_name].plural,
        }
        for class_name in CLASS_ORDER
    ]
    common = {
        "base_path": base_path,
        "github_url": args.github_url,
        "nav": nav,
        "search_index_url": with_base(base_path, "assets/search-index.json"),
        "site_title": "Center for Open Neuroscience",
    }

    def render(relative: str, template_name: str, **context: Any) -> None:
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        template = environment.get_template(template_name)
        target.write_text(template.render(**common, **context), encoding="utf-8")

    con_org = next(
        (
            item
            for item in items_by_class["XYZOrganization"]
            if "center for open neuroscience" in item["label"].casefold()
        ),
        None,
    )
    mission = (
        con_org["description"]
        if con_org and con_org["description"]
        else "Open infrastructure, reusable data, and transparent methods for neuroscience."
    )
    stats = [
        {"label": "people", "value": len(items_by_class["XYZPerson"])},
        {"label": "projects", "value": len(items_by_class["XYZProject"])},
        {"label": "research outputs", "value": len(items_by_class["XYZPublication"])},
        {"label": "datasets", "value": len(items_by_class["XYZDataset"])},
    ]
    render(
        "index.html",
        "index.html",
        body_class="home",
        datasets=items_by_class["XYZDataset"][:4],
        description=mission,
        mission=mission,
        page_title="Modeled open neuroscience",
        projects=[item for item in items_by_class["XYZProject"] if item["description"]][:6],
        publications=items_by_class["XYZPublication"][:8],
        stats=stats,
    )

    for class_name in CLASS_ORDER:
        config = CLASS_CONFIG[class_name]
        items = items_by_class[class_name]
        render(
            f"{config.path}/index.html",
            "listing.html",
            body_class="listing",
            config=config,
            description=config.intro,
            items=items,
            page_title=config.plural,
        )
        for item in items:
            structured = {
                "@context": "https://schema.org",
                "@id": item["pid"],
                "@type": config.singular,
                "description": item["description"] or None,
                "image": item["image"] or None,
                "name": item["label"],
            }
            structured_json = json.dumps(structured, ensure_ascii=False).replace("</", "<\\/")
            relative = item["href"].removeprefix(base_path)
            render(
                f"{relative}index.html",
                "detail.html",
                body_class="detail",
                description=item["description"] or f"{config.singular}: {item['label']}",
                item=item,
                page_title=item["label"],
                structured_json=structured_json,
            )

    search_index = [
        {
            "category": CLASS_CONFIG[class_name].plural,
            "description": item["description"],
            "keywords": " ".join(
                [item["kind_label"], *(topic["label"] for topic in item["topics"])]
            ),
            "title": item["label"],
            "url": item["href"],
        }
        for class_name in CLASS_ORDER
        for item in items_by_class[class_name]
    ]
    write_json(output / "assets" / "search-index.json", search_index)
    write_json(
        output / "assets" / "modeled-records.json",
        {
            class_name: [public_record(record) for record in merged.get(class_name, [])]
            for class_name in CLASS_ORDER
        },
    )
    (output / ".nojekyll").write_text("", encoding="utf-8")
    render(
        "404.html",
        "listing.html",
        body_class="listing not-found",
        config=ClassConfig("Page", "Page not found", "", "The modeled record may have moved."),
        description="The modeled record may have moved. Use search or return to the index.",
        items=[],
        page_title="Page not found",
    )

    report = {
        **load_report,
        "base_path": base_path,
        "entity_counts": {
            class_name: len(items_by_class[class_name]) for class_name in CLASS_ORDER
        },
        "merge_conflict_count": len(conflicts),
        "merge_conflicts": conflicts,
        "merged_record_count": sum(len(records) for records in merged.values()),
        "page_count": 2 + len(CLASS_ORDER) + sum(len(items) for items in items_by_class.values()),
    }
    write_json(args.report, report)
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=Path("data"))
    parser.add_argument("--site-root", type=Path, default=Path("site"))
    parser.add_argument(
        "--entity-assets", type=Path, default=Path("site/entity-assets.yaml")
    )
    parser.add_argument(
        "--con-site-inventory",
        type=Path,
        default=Path("inputs/con_site/inventory.json"),
    )
    parser.add_argument("--output", type=Path, default=Path("build/site"))
    parser.add_argument("--report", type=Path, default=Path("build/site-merge-report.json"))
    parser.add_argument("--base-path", default="/")
    parser.add_argument(
        "--github-url", default="https://github.com/con/dump-research-info"
    )
    return parser


def main() -> None:
    report = build(build_parser().parse_args())
    print(
        f"Built {report['page_count']} pages from {report['source_record_count']} "
        f"source records with {report['merge_conflict_count']} merge conflicts."
    )


if __name__ == "__main__":
    main()
