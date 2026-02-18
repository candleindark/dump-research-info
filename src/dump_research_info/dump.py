# SPDX-FileCopyrightText: 2026-present Isaac To <candleindark@gmail.com>
#
# SPDX-License-Identifier: MIT
from pydantic import DirectoryPath, HttpUrl, validate_call


@validate_call
async def dump_records(
    *,
    source: DirectoryPath,
    service_url: HttpUrl,
    token: str,
    collection: str,
    dry_run: bool,
) -> None:
    """Dump gathered research metadata records to a dump-things-server.

    Read JSON files from `source` and POST each record to the server
    at `service_url` in the given `collection`, authenticating with
    `token`.

    Parameters
    ----------
    source
        Directory containing JSON files named after data model class
        names (e.g., `XYZPerson.json`). May be relative to CWD or
        absolute.
    service_url
        Base URL of the dump-things-server instance
        (e.g., `http://localhost:8111`).
    token
        Authentication token sent as the `X-DumpThings-Token` header.
    collection
        Name of the target collection on the server
        (e.g., `research_info`).
    dry_run
        If `True`, print a summary of what would be posted (record
        counts per class and target URLs) without making any HTTP
        requests.
    """
    raise NotImplementedError(
        "dump_records is not yet implemented. "
        "This stub will be replaced in Step 2."
    )
