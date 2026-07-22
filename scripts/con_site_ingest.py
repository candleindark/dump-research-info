#!/usr/bin/env python3
"""Snapshot and audit the current Center for Open Neuroscience website source.

The upstream Pelican source is an input, not a canonical metadata format. This
adapter pins its exact Git commit, extracts a reviewable inventory, and compares
entity blocks with existing Things v2 records without changing those records.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import unicodedata
from collections.abc import Iterable, Iterator
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.parse import quote, urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup, Comment, Tag


SOURCE_REPOSITORY = "con/centerforopenneuroscience.org"
SOURCE_URL = f"https://github.com/{SOURCE_REPOSITORY}"
PUBLIC_URL = "https://centerforopenneuroscience.org/"
SOURCE_FILES = (
    "content/pages/engage.html",
    "content/pages/projects.html",
    "content/pages/support.html",
    "content/pages/whoweare.html",
    "theme/templates/index.html",
    "theme/templates/base.html",
    "pelicanconf.py",
    "publishconf.py",
    "content/CNAME",
)
PAGE_URLS = {
    "content/pages/engage.html": urljoin(PUBLIC_URL, "engage"),
    "content/pages/projects.html": urljoin(PUBLIC_URL, "projects"),
    "content/pages/support.html": urljoin(PUBLIC_URL, "support"),
    "content/pages/whoweare.html": urljoin(PUBLIC_URL, "whoweare"),
    "theme/templates/index.html": PUBLIC_URL,
    "theme/templates/base.html": PUBLIC_URL,
}
HTML_FILES = frozenset(PAGE_URLS)
ENTITY_CLASSES = {
    "people": "XYZPerson",
    "projects": "XYZProject",
}
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$", re.IGNORECASE)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def request_bytes(url: str, accept: str | None = None) -> bytes:
    headers = {"User-Agent": "dump-research-info CON source adapter"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if accept:
        headers["Accept"] = accept
    request = Request(url, headers=headers)
    try:
        with urlopen(request, timeout=60) as response:
            return response.read()
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GET {url} failed with HTTP {error.code}: {detail}") from error


def request_json(url: str) -> Any:
    return json.loads(request_bytes(url, "application/vnd.github+json"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def fetch_snapshot(repository: str, ref: str | None) -> dict[str, Any]:
    api_root = f"https://api.github.com/repos/{repository}"
    repository_info = request_json(api_root)
    resolved_ref = ref or repository_info["default_branch"]
    commit_info = request_json(f"{api_root}/commits/{quote(resolved_ref, safe='')}")
    commit = commit_info["sha"]
    files: list[dict[str, Any]] = []

    for path in SOURCE_FILES:
        raw_url = (
            "https://raw.githubusercontent.com/"
            f"{repository}/{commit}/{quote(path, safe='/')}"
        )
        content = request_bytes(raw_url).decode("utf-8")
        files.append(
            {
                "content": content,
                "path": path,
                "sha256": sha256_text(content),
            }
        )

    return {
        "format_version": 1,
        "source": {
            "commit": commit,
            "commit_date": commit_info["commit"]["committer"]["date"],
            "fetched_at": utc_now(),
            "ref": resolved_ref,
            "repository": repository,
            "url": f"https://github.com/{repository}",
        },
        "files": files,
    }


def snapshot_files(snapshot: dict[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in snapshot.get("files", []):
        path = item.get("path")
        content = item.get("content")
        expected_hash = item.get("sha256")
        if not isinstance(path, str) or not isinstance(content, str):
            raise ValueError("Snapshot files require string path and content values")
        if sha256_text(content) != expected_hash:
            raise ValueError(f"Snapshot checksum mismatch for {path}")
        result[path] = content

    missing = set(SOURCE_FILES) - result.keys()
    if missing:
        raise ValueError(f"Snapshot is missing source files: {sorted(missing)}")
    return result


def normalized_text(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).casefold()
    return "".join(character for character in value if character.isalnum())


def clean_text(node: Tag) -> str:
    pieces: list[str] = []
    for item in node.stripped_strings:
        if isinstance(item, Comment):
            continue
        text = " ".join(str(item).split())
        if not text or "{%" in text or "{{" in text:
            continue
        pieces.append(text)
    return " ".join(pieces)


def deduplicate(values: Iterable[Any], key) -> list[Any]:
    result: list[Any] = []
    seen: set[Any] = set()
    for value in values:
        marker = key(value)
        if marker in seen:
            continue
        seen.add(marker)
        result.append(value)
    return result


def enclosing_row(node: Tag) -> Tag:
    current: Tag | None = node
    while current is not None:
        if current.name == "div" and "row" in current.get("class", []):
            return current
        parent = current.parent
        current = parent if isinstance(parent, Tag) else None
    return node


def resolve_reference(raw: str, base_url: str) -> str:
    raw = raw.strip()
    if not raw or raw.startswith("javascript:"):
        return raw
    return urljoin(base_url, raw)


def links_from(node: Tag, base_url: str) -> list[dict[str, str]]:
    links: list[dict[str, str]] = []
    for anchor in node.find_all("a", href=True):
        raw = str(anchor["href"]).strip()
        resolved = resolve_reference(raw, base_url)
        if not resolved:
            continue
        links.append(
            {
                "label": clean_text(anchor),
                "raw": raw,
                "url": resolved,
            }
        )
    return deduplicate(links, lambda item: (item["label"], item["url"]))


def images_from(node: Tag, base_url: str) -> list[dict[str, str]]:
    images: list[dict[str, str]] = []
    for image in node.find_all("img", src=True):
        raw = str(image["src"]).strip()
        images.append(
            {
                "alt": str(image.get("alt", "")).strip(),
                "raw": raw,
                "url": resolve_reference(raw, base_url),
            }
        )
    return deduplicate(images, lambda item: (item["alt"], item["url"]))


def text_blocks_from(node: Tag, names: tuple[str, ...] = ("p", "li")) -> list[str]:
    blocks = (clean_text(element) for element in node.find_all(names))
    return deduplicate((block for block in blocks if block), normalized_text)


def generic_file_inventory(path: str, content: str) -> dict[str, Any]:
    soup = BeautifulSoup(content, "html.parser")
    for element in soup.find_all(("script", "style")):
        element.decompose()
    for comment in soup.find_all(string=lambda value: isinstance(value, Comment)):
        comment.extract()
    base_url = PAGE_URLS[path]

    headings: list[dict[str, Any]] = []
    for heading in soup.find_all(re.compile(r"^h[1-6]$")):
        text = clean_text(heading)
        if not text:
            continue
        headings.append(
            {
                "id": str(heading.get("id", "")),
                "level": int(heading.name[1]),
                "line": heading.sourceline,
                "text": text,
            }
        )

    blocks: list[str] = []
    for element in soup.find_all(("p", "li", "address")):
        text = clean_text(element)
        if text:
            blocks.append(text)

    return {
        "headings": headings,
        "images": images_from(soup, base_url),
        "links": links_from(soup, base_url),
        "public_url": base_url,
        "sha256": sha256_text(content),
        "text_blocks": deduplicate(blocks, normalized_text),
    }


def extract_people(content: str) -> list[dict[str, Any]]:
    path = "content/pages/whoweare.html"
    base_url = PAGE_URLS[path]
    soup = BeautifulSoup(content, "html.parser")
    people: list[dict[str, Any]] = []
    group = ""

    for heading in soup.find_all(("h2", "h3")):
        name = clean_text(heading)
        if not name:
            continue
        if heading.name == "h2":
            group = name
            continue

        row = enclosing_row(heading)
        positions = [clean_text(item) for item in row.select("div.position")]
        descriptions = [clean_text(item) for item in row.select("div.description")]
        text_blocks = [item for item in positions + descriptions if item]
        people.append(
            {
                "description": " ".join(descriptions),
                "group": group,
                "heading_id": str(heading.get("id", "")),
                "images": images_from(row, base_url),
                "line": heading.sourceline,
                "links": links_from(row, base_url),
                "name": name,
                "positions": positions,
                "source_path": path,
                "text_blocks": deduplicate(text_blocks, normalized_text),
            }
        )
    return people


def extract_heading_rows(
    path: str,
    content: str,
    item_label: str,
) -> list[dict[str, Any]]:
    base_url = PAGE_URLS[path]
    soup = BeautifulSoup(content, "html.parser")
    entries: list[dict[str, Any]] = []
    category = ""
    for heading in soup.find_all(("h1", "h2")):
        title = clean_text(heading)
        if not title:
            continue
        if heading.name == "h1":
            category = title
            continue
        row = enclosing_row(heading)
        entries.append(
            {
                "category": category,
                "heading_id": str(heading.get("id", "")),
                "images": images_from(row, base_url),
                "line": heading.sourceline,
                "links": links_from(row, base_url),
                item_label: title,
                "source_path": path,
                "text_blocks": text_blocks_from(row),
            }
        )
    return entries


def extract_supporters(content: str) -> list[dict[str, Any]]:
    path = "content/pages/support.html"
    base_url = PAGE_URLS[path]
    soup = BeautifulSoup(content, "html.parser")
    supporters: list[dict[str, Any]] = []
    for position, element in enumerate(soup.select("div.supporter"), start=1):
        links = links_from(element, base_url)
        images = images_from(element, base_url)
        name = clean_text(element)
        if not name:
            name = next((image["alt"] for image in images if image["alt"]), "")
        supporters.append(
            {
                "images": images,
                "line": element.sourceline,
                "links": links,
                "name": name or f"Supporter {position}",
                "source_path": path,
            }
        )
    return supporters


def build_inventory(snapshot: dict[str, Any]) -> dict[str, Any]:
    files = snapshot_files(snapshot)
    source = snapshot["source"]
    return {
        "format_version": 1,
        "source": {
            "commit": source["commit"],
            "repository": source["repository"],
            "url": source["url"],
        },
        "pages": {
            path: generic_file_inventory(path, files[path])
            for path in sorted(HTML_FILES)
        },
        "people": extract_people(files["content/pages/whoweare.html"]),
        "projects": extract_heading_rows(
            "content/pages/projects.html",
            files["content/pages/projects.html"],
            "title",
        ),
        "engagement_topics": extract_heading_rows(
            "content/pages/engage.html",
            files["content/pages/engage.html"],
            "title",
        ),
        "supporters": extract_supporters(files["content/pages/support.html"]),
    }


def iter_strings(value: Any, path: str = "$") -> Iterator[tuple[str, str]]:
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from iter_strings(item, f"{path}[{index}]")
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from iter_strings(item, f"{path}.{key}")


def load_records(data_root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted(data_root.glob("**/*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        values = payload if isinstance(payload, list) else [payload]
        for index, value in enumerate(values):
            if not isinstance(value, dict):
                continue
            strings = list(iter_strings(value))
            records.append(
                {
                    "class": path.stem,
                    "file": str(path),
                    "index": index,
                    "pid": value.get("pid", ""),
                    "strings": strings,
                    "text_keys": {
                        normalized_text(text) for _, text in strings if text.strip()
                    },
                    "reference_keys": set().union(
                        *(reference_keys(text) for _, text in strings)
                    ),
                }
            )
    return records


def canonical_url(value: str) -> str | None:
    value = value.strip()
    if not value:
        return None
    if value.startswith(("mailto:", "tel:")):
        return value.casefold()
    try:
        parsed = urlsplit(value)
    except ValueError:
        return None
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    host = parsed.netloc.casefold()
    if host.startswith("www."):
        host = host[4:]
    path = parsed.path.rstrip("/") or "/"
    return urlunsplit(("https", host, path, parsed.query, ""))


def reference_keys(value: str) -> set[str]:
    value = value.strip()
    keys: set[str] = set()
    canonical = canonical_url(value)
    if canonical:
        keys.add(f"url:{canonical}")
        parsed = urlsplit(canonical)
        host = parsed.netloc
        identifier = parsed.path.strip("/")
        if host in {"doi.org", "dx.doi.org"} and identifier:
            keys.add(f"doi:{identifier.casefold()}")
        if host == "orcid.org" and identifier:
            keys.add(f"orcid:{identifier.casefold()}")
    if DOI_RE.match(value):
        keys.add(f"doi:{value.casefold().rstrip('.')}" )
    if re.fullmatch(r"\d{4}-\d{4}-\d{4}-\d{3}[\dX]", value, re.IGNORECASE):
        keys.add(f"orcid:{value.casefold()}")
    return keys


def is_external_url(value: str) -> bool:
    canonical = canonical_url(value)
    if canonical is None:
        return value.startswith(("mailto:", "tel:"))
    return urlsplit(canonical).netloc != "centerforopenneuroscience.org"


def public_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "class": record["class"],
        "file": record["file"],
        "index": record["index"],
        "pid": record["pid"],
    }


def coverage_for_items(
    items: list[dict[str, Any]],
    name_key: str,
    expected_class: str,
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    class_records = [record for record in records if record["class"] == expected_class]
    result: list[dict[str, Any]] = []
    for item in items:
        name = item[name_key]
        name_key_normalized = normalized_text(name)
        matches = [
            record
            for record in class_records
            if name_key_normalized in record["text_keys"]
        ]
        matched_references = set().union(
            *(record["reference_keys"] for record in matches)
        )
        matched_text = set().union(*(record["text_keys"] for record in matches))
        external_links = [
            link for link in item.get("links", []) if is_external_url(link["url"])
        ]
        missing_links = [
            link
            for link in external_links
            if not (reference_keys(link["url"]) & matched_references)
        ]
        text_blocks = [
            block for block in item.get("text_blocks", []) if len(block.strip()) >= 3
        ]
        missing_text = [
            block for block in text_blocks if normalized_text(block) not in matched_text
        ]
        result.append(
            {
                "category": item.get("category", item.get("group", "")),
                "matched_records": [public_record(record) for record in matches],
                "missing_external_links": missing_links,
                "missing_text_blocks": missing_text,
                "modeled": bool(matches),
                "name": name,
                "source_external_link_count": len(external_links),
                "source_path": item["source_path"],
                "source_text_block_count": len(text_blocks),
            }
        )
    return result


def apply_alias_resolutions(
    records: list[dict[str, Any]],
    resolutions: dict[str, Any],
) -> list[dict[str, str]]:
    applied: list[dict[str, str]] = []
    for alias in resolutions.get("entity_aliases", []):
        source_name = alias.get("source_name")
        target_class = alias.get("target_class")
        target_pid = alias.get("target_pid")
        required = (source_name, target_class, target_pid)
        if not all(isinstance(value, str) and value for value in required):
            raise ValueError(
                "Entity aliases require source_name, target_class, and target_pid"
            )
        targets = [
            record
            for record in records
            if record["class"] == target_class and record["pid"] == target_pid
        ]
        if not targets:
            raise ValueError(
                f"Alias target {target_class} {target_pid} does not exist in the data"
            )
        for target in targets:
            target["text_keys"].add(normalized_text(source_name))
        applied.append(
            {
                "source_name": source_name,
                "target_class": target_class,
                "target_pid": target_pid,
            }
        )
    return applied


def build_coverage(
    inventory: dict[str, Any],
    data_root: Path,
    resolutions: dict[str, Any],
) -> dict[str, Any]:
    records = load_records(data_root)
    applied_aliases = apply_alias_resolutions(records, resolutions)
    people = coverage_for_items(
        inventory["people"], "name", ENTITY_CLASSES["people"], records
    )
    projects = coverage_for_items(
        inventory["projects"], "title", ENTITY_CLASSES["projects"], records
    )
    all_reference_keys = set().union(*(record["reference_keys"] for record in records))

    external_links: list[dict[str, str]] = []
    local_images: list[dict[str, str]] = []
    for page in inventory["pages"].values():
        external_links.extend(
            link for link in page["links"] if is_external_url(link["url"])
        )
        local_images.extend(
            image
            for image in page["images"]
            if urlsplit(image["url"]).netloc == "centerforopenneuroscience.org"
        )
    external_links = deduplicate(external_links, lambda item: item["url"])
    local_images = deduplicate(local_images, lambda item: item["url"])
    unrepresented_external_links = [
        link
        for link in external_links
        if not (reference_keys(link["url"]) & all_reference_keys)
    ]

    review_queue: list[dict[str, Any]] = []
    for entity_type, entries, target_class in (
        ("person", people, "XYZPerson"),
        ("project", projects, "XYZProject"),
    ):
        for entry in entries:
            if not entry["modeled"]:
                review_queue.append(
                    {
                        "kind": "missing_entity",
                        "name": entry["name"],
                        "source_path": entry["source_path"],
                        "suggested_target_class": target_class,
                        "entity_type": entity_type,
                    }
                )
                continue
            if entry["missing_external_links"]:
                review_queue.append(
                    {
                        "kind": "unmodeled_entity_links",
                        "name": entry["name"],
                        "links": entry["missing_external_links"],
                        "source_path": entry["source_path"],
                        "entity_type": entity_type,
                    }
                )
            if entry["missing_text_blocks"]:
                review_queue.append(
                    {
                        "kind": "unmodeled_entity_text",
                        "name": entry["name"],
                        "source_path": entry["source_path"],
                        "text_blocks": entry["missing_text_blocks"],
                        "entity_type": entity_type,
                    }
                )

    summary = {
        "external_links_not_represented": len(unrepresented_external_links),
        "external_links_on_source_site": len(external_links),
        "local_image_references": len(local_images),
        "modeled_people": sum(item["modeled"] for item in people),
        "modeled_projects": sum(item["modeled"] for item in projects),
        "record_count": len(records),
        "resolved_entity_aliases": len(applied_aliases),
        "review_item_count": len(review_queue),
        "source_people": len(people),
        "source_projects": len(projects),
    }
    return {
        "format_version": 1,
        "source": inventory["source"],
        "resolutions": {
            "aliases": applied_aliases,
            "reviewed_against_commit": resolutions.get("reviewed_against_commit"),
            "source_commit_matches_review": (
                resolutions.get("reviewed_against_commit")
                == inventory["source"]["commit"]
            ),
        },
        "summary": summary,
        "people": people,
        "projects": projects,
        "editorial_inventory": {
            "engagement_topics": inventory["engagement_topics"],
            "supporters": inventory["supporters"],
            "homepage": inventory["pages"]["theme/templates/index.html"],
            "shared_footer": inventory["pages"]["theme/templates/base.html"],
        },
        "local_images": local_images,
        "review_queue": review_queue,
        "unrepresented_external_links": unrepresented_external_links,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--refresh",
        action="store_true",
        help="Fetch a new source snapshot before rebuilding reports",
    )
    mode.add_argument(
        "--check",
        action="store_true",
        help="Fail if committed reports differ from the pinned snapshot and data",
    )
    parser.add_argument("--repository", default=SOURCE_REPOSITORY)
    parser.add_argument("--ref", help="Git ref to snapshot (default: upstream default branch)")
    parser.add_argument(
        "--snapshot",
        type=Path,
        default=Path("inputs/con_site/snapshot.json"),
    )
    parser.add_argument(
        "--inventory",
        type=Path,
        default=Path("inputs/con_site/inventory.json"),
    )
    parser.add_argument(
        "--coverage",
        type=Path,
        default=Path("inputs/con_site/coverage.json"),
    )
    parser.add_argument(
        "--resolutions",
        type=Path,
        default=Path("inputs/con_site/resolutions.json"),
    )
    parser.add_argument("--data-root", type=Path, default=Path("data"))
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.refresh:
        snapshot = fetch_snapshot(args.repository, args.ref)
        write_json(args.snapshot, snapshot)
    else:
        if not args.snapshot.exists():
            raise SystemExit(f"No snapshot at {args.snapshot}; run with --refresh first")
        snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))

    inventory = build_inventory(snapshot)
    resolutions = (
        json.loads(args.resolutions.read_text(encoding="utf-8"))
        if args.resolutions.exists()
        else {}
    )
    coverage = build_coverage(inventory, args.data_root, resolutions)
    if args.check:
        stale: list[Path] = []
        for path, generated in (
            (args.inventory, inventory),
            (args.coverage, coverage),
        ):
            committed = (
                json.loads(path.read_text(encoding="utf-8"))
                if path.exists()
                else None
            )
            if committed != generated:
                stale.append(path)
        if stale:
            joined = ", ".join(str(path) for path in stale)
            raise SystemExit(
                f"Generated CON source reports are stale: {joined}; "
                "run `pixi run con-site-audit`"
            )
    else:
        write_json(args.inventory, inventory)
        write_json(args.coverage, coverage)
    print(json.dumps(coverage["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1) from error
