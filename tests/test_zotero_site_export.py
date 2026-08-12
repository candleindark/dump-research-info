from __future__ import annotations

import argparse
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location(
    "zotero_site_export", SCRIPTS / "zotero_site_export.py"
)
assert SPEC is not None and SPEC.loader is not None
EXPORT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = EXPORT
SPEC.loader.exec_module(EXPORT)


class ZoteroSiteExportTests(unittest.TestCase):
    def export(self, root: Path) -> tuple[Path, Path]:
        output = root / "records"
        report = root / "report.json"
        EXPORT.command_export(
            argparse.Namespace(
                publications=(
                    ROOT / "data/zotero_centerforopenneuroscience/XYZPublication.json"
                ),
                snapshot=(
                    ROOT / "inputs/zotero_centerforopenneuroscience/snapshot.json"
                ),
                policy=(
                    ROOT / "inputs/zotero_centerforopenneuroscience/site-migration.yaml"
                ),
                output_dir=output,
                report=report,
            )
        )
        return output, report

    def test_full_export_is_deterministic_and_uses_explicit_curie_types(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first, first_report = self.export(root / "first")
            second, second_report = self.export(root / "second")
            first_files = {
                path.name: path.read_bytes() for path in sorted(first.glob("*.yaml"))
            }
            second_files = {
                path.name: path.read_bytes() for path in sorted(second.glob("*.yaml"))
            }
            self.assertEqual(first_files, second_files)
            self.assertEqual(first_report.read_bytes(), second_report.read_bytes())

            records = [yaml.safe_load(payload) for payload in first_files.values()]
            report = json.loads(first_report.read_text(encoding="utf-8"))

        self.assertEqual(len(records), 126)
        self.assertEqual(report["output"]["publication_count"], 126)
        self.assertIn(
            "xyzrins:publications/datalad-joss-2021",
            {record["pid"] for record in records},
        )
        datalad = next(
            record
            for record in records
            if record["pid"] == "xyzrins:publications/datalad-joss-2021"
        )
        self.assertEqual(
            datalad["generated_by"],
            [
                {
                    "object": "xyzrins:projects/datalad",
                    "at_location": "ISSN:2475-9066",
                    "at_time": "2021-07-01",
                    "schema_type": "dlthings:Generation",
                }
            ],
        )
        self.assertTrue(
            all(record["schema_type"] == "xyzri:XYZPublication" for record in records)
        )
        self.assertEqual(
            [record["pid"] for record in records if "generated_by" in record],
            ["xyzrins:publications/datalad-joss-2021"],
        )
        for record in records:
            for attribution in record.get("attributed_to", []):
                self.assertEqual(attribution["schema_type"], "dlthings:Attribution")
            for attribute in record.get("attributes", []):
                self.assertEqual(
                    attribute["schema_type"],
                    "dlthings:AttributeSpecification",
                )

    def test_export_fails_closed_on_an_unreviewed_relationship_target(self) -> None:
        policy = EXPORT.load_policy(
            ROOT / "inputs/zotero_centerforopenneuroscience/site-migration.yaml"
        )
        record = {
            "pid": "https://doi.org/10.1234/example",
            "title": "Example",
            "kind": "bibo:Article",
            "identifiers": [
                {"notation": "10.1234/example", "schema_type": "dlthings:DOI"},
                {
                    "notation": "zotero:group:6197458:item:ABCD1234",
                    "schema_type": "dlthings:Identifier",
                },
            ],
            "attributed_to": [
                {"object": "xyzrins:persons/unreviewed", "roles": ["marcrel:aut"]}
            ],
        }
        with self.assertRaisesRegex(ValueError, "unreviewed attribution target"):
            EXPORT.render_publication(record, deepcopy(policy), EXPORT.Counter())


if __name__ == "__main__":
    unittest.main()
