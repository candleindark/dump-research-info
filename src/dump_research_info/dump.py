import asyncio
from pathlib import Path
from typing import Any

import httpx
from pydantic import DirectoryPath, HttpUrl, TypeAdapter, validate_call

_records_adapter: TypeAdapter[list[dict[str, Any]]] = TypeAdapter(
    list[dict[str, Any]]
)


async def _post_record(
    client: httpx.AsyncClient,
    endpoint: str,
    record: dict[str, Any],
    token: str,
) -> str | None:
    """POST a single record to the server.

    Returns an error message on failure, `None` on success.
    """
    try:
        response = await client.post(
            endpoint,
            json=record,
            headers={"X-DumpThings-Token": token},
        )
    except httpx.RequestError as e:
        return str(e)

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        return f"HTTP {e.response.status_code}: {e.response.text}"

    return None


async def _post_class_file(
    client: httpx.AsyncClient,
    file_path: Path,
    collection: str,
    token: str,
) -> None:
    """POST all records in a single class JSON file to the server."""
    records = _records_adapter.validate_json(
        await asyncio.to_thread(file_path.read_bytes)
    )
    if not records:
        return

    class_name = file_path.stem
    endpoint = f"{collection}/record/{class_name}"

    async with asyncio.TaskGroup() as tg:
        tasks = [
            tg.create_task(_post_record(client, endpoint, record, token))
            for record in records
        ]

    errors = [t.result() for t in tasks]
    n_ok = sum(1 for e in errors if e is None)
    print(f"{class_name}: {n_ok}/{len(records)} records posted successfully")
    for i, error in enumerate(errors):
        if error is not None:
            print(f"  Record {i + 1}: {error}")


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
    class_files = sorted(source.glob("*.json"), key=lambda f: f.stem)

    if not class_files:
        print(f"No JSON files found in {source}.")
        return

    # service_url always has a trailing slash as a Pydantic HttpUrl
    base = str(service_url)

    if dry_run:
        for file_path in class_files:
            records = _records_adapter.validate_json(
                await asyncio.to_thread(file_path.read_bytes)
            )
            if not records:
                continue
            class_name = file_path.stem
            print(
                f"{len(records)} {class_name} record(s)"
                f" → POST {base}{collection}/record/{class_name}"
            )
        return

    async with httpx.AsyncClient(
        base_url=base,
        limits=httpx.Limits(max_connections=50),
        timeout=httpx.Timeout(5.0, pool=None),
    ) as client:
        async with asyncio.TaskGroup() as tg:
            for file_path in class_files:
                tg.create_task(
                    _post_class_file(client, file_path, collection, token)
                )
