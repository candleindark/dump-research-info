from __future__ import annotations

import argparse
from copy import deepcopy
from email.message import Message
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "zotero_ingest", ROOT / "scripts" / "zotero_ingest.py"
)
assert SPEC is not None and SPEC.loader is not None
ZOTERO = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ZOTERO
SPEC.loader.exec_module(ZOTERO)


def record(key: str) -> dict[str, object]:
    return {"key": key, "data": {"key": key, "version": 1}}


def result(version: int, records: list[dict[str, object]], endpoint: str):
    return ZOTERO.PaginatedResult(
        records=tuple(records),
        library_version=version,
        response_api_version="3",
        total_results=len(records),
        urls=(f"https://api.zotero.org/groups/6197458/{endpoint}?start=0",),
    )


class ZoteroAcquisitionTests(unittest.TestCase):
    def test_current_and_historical_collection_labels_classify_identically(
        self,
    ) -> None:
        for label in ("Articles", "CON Articles"):
            snapshot = {
                "collections": [{"data": {"key": "COLL0001", "name": label}}],
                "items": [
                    {
                        "data": {
                            "key": "ITEM0001",
                            "itemType": "document",
                            "collections": ["COLL0001"],
                        }
                    }
                ],
            }
            item = ZOTERO.source_items(snapshot)[0]
            self.assertTrue(item.selected)
            self.assertEqual(
                ZOTERO.classify(item),
                ("XYZPublication", "bibo:Document", None),
            )

    def test_fetch_json_honors_rate_limit_and_api_version_headers(self) -> None:
        retry_headers = Message()
        retry_headers["Retry-After"] = "0.25"
        throttled = HTTPError(
            "https://api.zotero.org/test",
            429,
            "Too Many Requests",
            retry_headers,
            None,
        )
        response = io.BytesIO(b"[]")
        response.headers = Message()
        response.headers["Zotero-API-Version"] = "3"
        with (
            patch.object(ZOTERO, "urlopen", side_effect=[throttled, response]),
            patch.object(ZOTERO.time, "sleep") as sleep,
        ):
            payload, headers = ZOTERO.fetch_json(
                "https://api.zotero.org/test", "test-agent"
            )
        self.assertEqual(payload, [])
        self.assertEqual(headers["zotero-api-version"], "3")
        sleep.assert_called_once_with(0.25)

    def test_fetch_paginated_reads_every_page_at_one_library_version(self) -> None:
        first = [record(f"A{index:03}") for index in range(100)]
        last = [record("A100")]
        headers = {
            "last-modified-version": "42",
            "total-results": "101",
            "zotero-api-version": "3",
        }
        with patch.object(
            ZOTERO,
            "fetch_json",
            side_effect=[(first, headers), (last, headers)],
        ) as fetch:
            fetched = ZOTERO.fetch_paginated(
                "https://api.zotero.org/groups/6197458",
                "items/top",
                "test-agent",
            )

        self.assertEqual(len(fetched.records), 101)
        self.assertEqual(fetched.library_version, 42)
        self.assertIn("start=0", fetch.call_args_list[0].args[0])
        self.assertIn("start=100", fetch.call_args_list[1].args[0])

    def test_fetch_paginated_rejects_a_library_change(self) -> None:
        first = [record(f"A{index:03}") for index in range(100)]
        with patch.object(
            ZOTERO,
            "fetch_json",
            side_effect=[
                (
                    first,
                    {
                        "last-modified-version": "42",
                        "total-results": "101",
                        "zotero-api-version": "3",
                    },
                ),
                (
                    [record("A100")],
                    {
                        "last-modified-version": "43",
                        "total-results": "101",
                        "zotero-api-version": "3",
                    },
                ),
            ],
        ):
            with self.assertRaisesRegex(ZOTERO.SnapshotChanged, "changed"):
                ZOTERO.fetch_paginated(
                    "https://api.zotero.org/groups/6197458",
                    "items/top",
                    "test-agent",
                )

    def test_command_fetch_retries_the_whole_cross_endpoint_snapshot(self) -> None:
        collections = [record("COLL0001")]
        items = [record("ITEM0001")]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "snapshot.json"
            args = argparse.Namespace(
                expected_library_version=44,
                group_id=6197458,
                output=output,
                snapshot_attempts=2,
                user_agent="test-agent",
            )
            with patch.object(
                ZOTERO,
                "fetch_paginated",
                side_effect=[
                    result(42, collections, "collections"),
                    result(43, items, "items/top"),
                    result(44, collections, "collections"),
                    result(44, items, "items/top"),
                ],
            ):
                ZOTERO.command_fetch(args)

            snapshot = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(snapshot["source"]["library_version"], 44)
        self.assertEqual(snapshot["source"]["snapshot_attempt"], 2)
        self.assertEqual(
            snapshot["source"]["content_sha256"],
            ZOTERO.source_content_sha256(collections, items),
        )
        ZOTERO.validate_snapshot(snapshot)

    def test_validate_snapshot_detects_payload_tampering(self) -> None:
        collections = [record("COLL0001")]
        items = [record("ITEM0001")]
        snapshot = {
            "source": {
                "api_root": "https://api.zotero.org/groups/6197458",
                "collection_urls": [
                    "https://api.zotero.org/groups/6197458/collections?start=0"
                ],
                "content_sha256": ZOTERO.source_content_sha256(collections, items),
                "fetched_at": "2026-08-11T12:00:00+00:00",
                "group_id": 6197458,
                "item_urls": [
                    "https://api.zotero.org/groups/6197458/items/top?start=0"
                ],
                "library_version": 44,
                "response_api_version": "3",
                "snapshot_attempt": 1,
                "total_collections": 1,
                "total_top_level_items": 1,
                "zotero_api_version": "3",
            },
            "collections": collections,
            "items": items,
        }
        ZOTERO.validate_snapshot(snapshot)
        changed = deepcopy(snapshot)
        changed["items"][0]["data"]["title"] = "changed"
        with self.assertRaisesRegex(ValueError, "content_sha256"):
            ZOTERO.validate_snapshot(changed)


if __name__ == "__main__":
    unittest.main()
