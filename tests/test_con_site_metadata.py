import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CON_SITE = ROOT / "data" / "con_site"
PRESENTATION_ROUTES = {
    "https://centerforopenneuroscience.org/",
    "https://centerforopenneuroscience.org/projects",
    "https://centerforopenneuroscience.org/whoweare",
}


def _records() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for path in sorted(CON_SITE.glob("XYZ*.json")):
        records.extend(json.loads(path.read_text(encoding="utf-8")))
    return records


def test_presentation_routes_are_not_things_about_targets():
    violations = [
        (record["pid"], target)
        for record in _records()
        for target in record.get("about", [])
        if target in PRESENTATION_ROUTES
    ]

    assert violations == []


def test_con_homepage_uses_the_qualified_attribute_pattern():
    con = next(record for record in _records() if record["pid"] == "ror:04tfhh831")

    assert {
        "schema_type": "dlthings:AttributeSpecification",
        "value": "https://centerforopenneuroscience.org/",
        "predicate": "foaf:homepage",
    } in con["attributes"]


def test_identifier_creators_match_public_things_records():
    records = {record["pid"]: record for record in _records()}

    assert records["rrid:SCR_002630"] == {
        "schema_type": "xyzri:XYZOrganization",
        "pid": "rrid:SCR_002630",
        "name": "GitHub",
    }
    assert records["ror:04fa4r544"] == {
        "annotations": {
            "obo:NCIT_C54269": "m.szczepanik@fz-juelich.de",
            "sio:SIO_001083": "2026-01-19T17:44:59.765383",
        },
        "characterized_by": [
            {"object": "http://orcid.org/", "predicate": "rdfs:seeAlso"},
            {
                "object": "https://en.wikipedia.org/wiki/ORCID",
                "predicate": "rdfs:seeAlso",
            },
        ],
        "schema_type": "xyzri:XYZOrganization",
        "pid": "ror:04fa4r544",
        "name": "ORCID",
        "at_location": "geodata:4348599",
    }
