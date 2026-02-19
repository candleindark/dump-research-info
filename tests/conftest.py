import json

import pytest


@pytest.fixture(scope="session")
def sample_source_dir(tmp_path_factory):
    """A source directory pre-populated with two small JSON class files.

    Session-scoped so files are created once and shared across all tests.
    """
    tmp_path = tmp_path_factory.mktemp("sample_source")
    data = {
        "XYZGrant": [
            {"pid": "https://example.com/grant/1", "title": "Test Grant"},
        ],
        "XYZPerson": [
            {"pid": "https://example.com/person/1"},
            {"pid": "https://example.com/person/2"},
        ],
    }
    for class_name, records in data.items():
        (tmp_path / f"{class_name}.json").write_text(json.dumps(records))
    return tmp_path
