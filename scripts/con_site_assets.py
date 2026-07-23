#!/usr/bin/env python3
"""Fetch or verify image assets referenced by the pinned legacy CON inventory."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen


IMAGE_RE = re.compile(r"\.(?:png|jpe?g|gif|svg|webp)(?:\?.*)?$", re.IGNORECASE)
LEGACY_HOST = "centerforopenneuroscience.org"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--asset-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--commit", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--fetch", action="store_true")
    mode.add_argument("--check", action="store_true")
    return parser.parse_args()


def strings(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for child in value.values():
            yield from strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from strings(child)
    elif isinstance(value, str):
        yield value


def source_path(reference: str) -> str | None:
    if not IMAGE_RE.search(reference):
        return None
    parsed = urlparse(reference)
    if parsed.netloc and parsed.netloc != LEGACY_HOST:
        return None
    path = parsed.path.lstrip("/")
    if not path.startswith("theme/img/"):
        return None
    return "theme/static/img/" + path.removeprefix("theme/img/")


def referenced_assets(inventory: dict[str, Any]) -> dict[str, list[str]]:
    result: dict[str, set[str]] = {}
    for reference in strings(inventory):
        path = source_path(reference)
        if path:
            result.setdefault(path, set()).add(reference)
    return {path: sorted(references) for path, references in sorted(result.items())}


def relative_asset_path(path: str) -> Path:
    prefix = "theme/static/img/"
    if not path.startswith(prefix):
        raise ValueError(f"Unexpected source image path: {path}")
    return Path(path.removeprefix(prefix))


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_one(repository: str, commit: str, path: str) -> tuple[str, bytes, str]:
    encoded = "/".join(quote(part) for part in path.split("/"))
    url = f"https://raw.githubusercontent.com/{repository}/{commit}/{encoded}"
    request = Request(url, headers={"User-Agent": "dump-research-info/0.1"})
    with urlopen(request, timeout=30) as response:
        return path, response.read(), url


def build_manifest(args: argparse.Namespace, references: dict[str, list[str]]) -> dict[str, Any]:
    fetched: dict[str, tuple[bytes, str]] = {}
    with ThreadPoolExecutor(max_workers=8) as executor:
        for path, data, url in executor.map(
            lambda path: fetch_one(args.repository, args.commit, path),
            references,
        ):
            fetched[path] = (data, url)

    assets = []
    for path in sorted(references):
        data, url = fetched[path]
        relative = relative_asset_path(path)
        destination = args.asset_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        media_type = mimetypes.guess_type(destination.name)[0] or "application/octet-stream"
        assets.append(
            {
                "category": relative.parts[0],
                "media_type": media_type,
                "references": references[path],
                "sha256": sha256(data),
                "size": len(data),
                "source_path": path,
                "source_url": url,
                "site_path": f"assets/legacy/{relative.as_posix()}",
                "web_path": f"/assets/legacy/{relative.as_posix()}",
            }
        )
    return {
        "format_version": 1,
        "source": {
            "repository": args.repository,
            "commit": args.commit,
            "inventory": str(args.inventory),
        },
        "asset_count": len(assets),
        "total_bytes": sum(asset["size"] for asset in assets),
        "assets": assets,
    }


def check_manifest(
    args: argparse.Namespace,
    references: dict[str, list[str]],
    manifest: dict[str, Any],
) -> None:
    expected_source = {
        "repository": args.repository,
        "commit": args.commit,
        "inventory": str(args.inventory),
    }
    if manifest.get("format_version") != 1 or manifest.get("source") != expected_source:
        raise ValueError("Asset manifest source metadata is stale")
    entries = {entry["source_path"]: entry for entry in manifest.get("assets", [])}
    if set(entries) != set(references):
        raise ValueError("Asset manifest paths do not match the current legacy inventory")

    expected_files = set()
    for path, entry in entries.items():
        if entry.get("references") != references[path]:
            raise ValueError(f"Asset references are stale: {path}")
        destination = args.asset_root / relative_asset_path(path)
        expected_files.add(destination)
        if not destination.exists():
            raise ValueError(f"Mirrored asset is missing: {destination}")
        data = destination.read_bytes()
        if len(data) != entry.get("size") or sha256(data) != entry.get("sha256"):
            raise ValueError(f"Mirrored asset does not match its manifest: {destination}")

    actual_files = {path for path in args.asset_root.rglob("*") if path.is_file()}
    if actual_files != expected_files:
        extras = sorted(str(path) for path in actual_files - expected_files)
        raise ValueError(f"Untracked files are present in the legacy asset tree: {extras}")
    if manifest.get("asset_count") != len(entries):
        raise ValueError("Asset manifest count is stale")
    if manifest.get("total_bytes") != sum(entry["size"] for entry in entries.values()):
        raise ValueError("Asset manifest byte count is stale")


def main() -> int:
    inventory = json.loads(parse_args().inventory.read_text(encoding="utf-8"))
    args = parse_args()
    references = referenced_assets(inventory)
    if args.fetch:
        manifest = build_manifest(args, references)
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(
            json.dumps(
                {
                    "asset_count": manifest["asset_count"],
                    "total_bytes": manifest["total_bytes"],
                },
                sort_keys=True,
            )
        )
        return 0

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    check_manifest(args, references, manifest)
    print(json.dumps({"checked_assets": len(references), "status": "current"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
