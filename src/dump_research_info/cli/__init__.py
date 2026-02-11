# SPDX-FileCopyrightText: 2026-present Isaac To <candleindark@gmail.com>
#
# SPDX-License-Identifier: MIT
import click

from dump_research_info.__about__ import __version__


@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="dump-research-info")
def dump_research_info():
    click.echo("Hello world!")
