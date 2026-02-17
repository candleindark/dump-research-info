# SPDX-FileCopyrightText: 2026-present Isaac To <candleindark@gmail.com>
#
# SPDX-License-Identifier: MIT
import typer

from dump_research_info.__about__ import __version__


def version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit()


app = typer.Typer()


@app.callback(invoke_without_command=True)
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    typer.echo("Hello world!")
