#!/usr/bin/env python3
"""Validate class-named JSON arrays with a dump-things-service endpoint."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import time
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, sort_keys=True)
        stream.write("\n")
    temporary.replace(path)


def wait_for_service(service_url: str, timeout: int) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urlopen(f"{service_url}/server", timeout=2) as response:
                if response.status == 200:
                    return
        except URLError:
            time.sleep(1)
    raise TimeoutError(f"Validation service did not become ready: {service_url}")


def json_files(paths: Iterable[Path]) -> list[Path]:
    files: set[Path] = set()
    for path in paths:
        if path.is_dir():
            files.update(path.glob("*.json"))
        elif path.suffix == ".json":
            files.add(path)
        else:
            raise ValueError(f"Not a JSON file or source directory: {path}")
    return sorted(files)


def validation_jobs(paths: Iterable[Path]) -> list[dict[str, Any]]:
    jobs: list[dict[str, Any]] = []
    for path in json_files(paths):
        with path.open(encoding="utf-8") as stream:
            records = json.load(stream)
        if not isinstance(records, list):
            raise ValueError(f"Expected a JSON array: {path}")
        for index, record in enumerate(records):
            if not isinstance(record, dict):
                raise ValueError(f"Expected an object at {path}[{index}]")
            jobs.append(
                {
                    "class": path.stem,
                    "file": str(path),
                    "index": index,
                    "pid": record.get("pid"),
                    "record": record,
                }
            )
    return jobs


def validate_job(
    job: dict[str, Any],
    service_url: str,
    collection: str,
    token: str,
) -> dict[str, Any]:
    body = json.dumps(job["record"]).encode()
    request = Request(
        f"{service_url}/{collection}/validate/record/{job['class']}",
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-DumpThings-Token": token,
        },
    )
    result = {key: job[key] for key in ("class", "file", "index", "pid")}
    try:
        with urlopen(request, timeout=60) as response:
            response.read()
            result["status"] = response.status
    except HTTPError as error:
        raw = error.read().decode(errors="replace")
        try:
            result["detail"] = json.loads(raw)
        except json.JSONDecodeError:
            result["detail"] = raw
        result["status"] = error.code
    except Exception as error:  # report connection and timeout failures uniformly
        result["detail"] = f"{type(error).__name__}: {error}"
        result["status"] = 0
    return result


def run(args: argparse.Namespace) -> int:
    service_url = args.service_url.rstrip("/")
    wait_for_service(service_url, args.wait_timeout)
    jobs = validation_jobs(args.paths)

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(
            pool.map(
                lambda job: validate_job(
                    job, service_url, args.collection, args.token
                ),
                jobs,
            )
        )

    failures = [
        result for result in results if not 200 <= int(result["status"]) < 300
    ]
    status_by_class: dict[str, Counter[str]] = defaultdict(Counter)
    for result in results:
        status_by_class[result["class"]][str(result["status"])] += 1

    report = {
        "collection": args.collection,
        "failures": failures,
        "invalid_count": len(failures),
        "record_count": len(results),
        "service": service_url,
        "status_by_class": {
            class_name: dict(sorted(counts.items()))
            for class_name, counts in sorted(status_by_class.items())
        },
        "valid_count": len(results) - len(failures),
    }
    if args.report:
        atomic_write_json(args.report, report)
    print(json.dumps({key: value for key, value in report.items() if key != "failures"}, indent=2))
    if failures:
        print(json.dumps({"failures": failures}, indent=2))
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", type=Path, nargs="+")
    parser.add_argument("--service-url", default="http://localhost:8111")
    parser.add_argument("--collection", default="research_info")
    parser.add_argument(
        "--token",
        default=os.environ.get("DUMP_THINGS_TOKEN", "write_collection_token"),
    )
    parser.add_argument("--report", type=Path)
    parser.add_argument("--wait-timeout", type=int, default=60)
    parser.add_argument("--workers", type=int, default=4)
    return parser


def main() -> None:
    raise SystemExit(run(build_parser().parse_args()))


if __name__ == "__main__":
    main()
