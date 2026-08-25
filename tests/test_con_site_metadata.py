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
        "schema_type": "xyzri:XYZOrganization",
        "pid": "ror:04fa4r544",
        "name": "ORCID",
    }
    assert records["ror:026ytr635"] == {
        "schema_type": "xyzri:XYZOrganization",
        "pid": "ror:026ytr635",
        "name": "ISSN International Centre",
    }


def test_publication_roles_match_public_things_identities():
    records = {record["pid"]: record for record in _records()}

    assert records["obo:MS_1002034"] == {
        "schema_type": "xyzri:XYZAgentRole",
        "pid": "obo:MS_1002034",
        "display_label": "First author",
    }
    assert records["obo:MS_1002035"] == {
        "schema_type": "xyzri:XYZAgentRole",
        "pid": "obo:MS_1002035",
        "display_label": "Senior author",
    }
    assert records["obo:MS_1002036"] == {
        "schema_type": "xyzri:XYZAgentRole",
        "pid": "obo:MS_1002036",
        "display_label": "Co-author",
    }
