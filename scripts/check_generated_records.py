#!/usr/bin/env python3
"""Check or promote non-empty generated Things record arrays."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generated", type=Path, required=True)
    parser.add_argument("--promoted", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--promote", action="store_true")
    return parser.parse_args()


def load_nonempty(directory: Path) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for path in sorted(directory.glob("*.json")):
        records = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(records, list):
            raise ValueError(f"Expected a JSON array: {path}")
        if records:
            result[path.name] = records
    return result


def load_promoted(directory: Path) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for path in sorted(directory.glob("*.json")):
        records = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(records, list):
            raise ValueError(f"Expected a JSON array: {path}")
        result[path.name] = records
    return result


def main() -> int:
    args = parse_args()
    generated = load_nonempty(args.generated)
    promoted = load_promoted(args.promoted) if args.promoted.exists() else {}
    generated_names = set(generated)
    promoted_names = set(promoted)
    extra = sorted(promoted_names - generated_names)
    if extra:
        raise ValueError(
            f"Promoted files no longer have non-empty generated counterparts: {extra}"
        )

    if args.check:
        stale = sorted(
            name
            for name in generated_names | promoted_names
            if generated.get(name) != promoted.get(name)
        )
        if stale:
            raise ValueError(f"Promoted Things records are stale: {stale}")
        print(json.dumps({"checked_files": len(generated), "status": "current"}, sort_keys=True))
        return 0

    args.promoted.mkdir(parents=True, exist_ok=True)
    for name, records in generated.items():
        (args.promoted / name).write_text(
            json.dumps(records, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    print(json.dumps({"promoted_files": len(generated), "output": str(args.promoted)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
