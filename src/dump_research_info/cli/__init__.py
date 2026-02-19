# SPDX-FileCopyrightText: 2026-present Isaac To <candleindark@gmail.com>
#
# SPDX-License-Identifier: MIT
import asyncio
from pathlib import Path
from typing import Annotated

import typer

from dump_research_info.__about__ import __version__


def version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit()


app = typer.Typer()


@app.command()
def main(
    source: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=False,
            dir_okay=True,
            readable=True,
            resolve_path=True,
            help="Directory containing JSON files named after data model class names.",
        ),
    ],
    service_url: Annotated[
        str,
        typer.Argument(
            help="Base URL of the dump-things-server instance.",
        ),
    ],
    token: Annotated[
        str,
        typer.Option(
            "--token",
            "-t",
            envvar="DUMP_THINGS_TOKEN",
            help=(
                "Authentication token for the dump-things-server. "
                "Can also be set via the DUMP_THINGS_TOKEN environment variable."
            ),
        ),
    ],
    collection: Annotated[
        str,
        typer.Option(
            "--collection",
            "-c",
            envvar="DUMP_THINGS_COLLECTION",
            help=(
                "Name of the target collection on the server. "
                "Can also be set via the DUMP_THINGS_COLLECTION environment variable."
            ),
        ),
    ],
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            "-n",
            help=(
                "Print a summary of what would be posted (record counts per class "
                "and target URLs) without making any HTTP requests."
            ),
        ),
    ] = False,
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-V",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit.",
        ),
    ] = False,
) -> None:
    """Dump gathered research metadata to a dump-things-server instance."""
    from dump_research_info.dump import dump_records

    asyncio.run(
        dump_records(
            source=source,
            service_url=service_url,  # type: ignore[arg-type]
            token=token,
            collection=collection,
            dry_run=dry_run,
        )
    )
