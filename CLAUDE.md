# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repo serves two purposes:

1. **Metadata gathering setup**: Provides a setup for AI coding agents to gather research metadata from CON (Center for Open Neuroscience) related websites and repositories. AI agents are responsible for validating gathered data using the REST API of a dump-things-server instance. Humans give final confirmation and commit the gathered metadata.
2. **CLI tool**: A Python CLI tool (`dump-research-info`) for dumping the gathered metadata in this repo to a [dump-things-server](https://hub.psychoinformatics.de/datalink/dump-things-server) instance.

Data must conform to the data models defined in or referenced by the [demo-research-information-schema](https://concepts.datalad.org/s/demo-research-information/unreleased.yaml) ([docs](https://concepts.datalad.org/s/demo-research-information/unreleased/)). The relevant data model classes are also available through the OpenAPI documentation of a dump-things-server instance's REST API.

## Build & Development Commands

- **Install**: `pip install -e .` (or use `hatch`)
- **Run CLI**: `dump-research-info` or `python -m dump_research_info`
- **Type check**: `hatch run types:check`
- **Build**: `hatch build`

## Architecture

- **Build system**: Hatchling (configured in `pyproject.toml`)
- **CLI framework**: Click
- **Python**: >= 3.11

### Source Layout

- `src/dump_research_info/` — main package (src layout)
  - `cli/__init__.py` — Click command group entry point (`dump_research_info`)
  - `__about__.py` — version (dynamic, read by Hatch)
  - `__main__.py` — enables `python -m` invocation
- `tests/` — test package
- `data/` — gathered metadata storage (JSON files organized by source)
- `store/` — data store for the dump-things-server instance used for validation; contains both configuration and data records, but only the configuration files (`.dumpthings.yaml`) are tracked by git

### Data Organization

Metadata is stored as JSON files at `data/<source_name>/<ClassName>.json`:
- `<source_name>` — a name given to the source from which the metadata is gathered
- `<ClassName>` — the name of a class defined or referenced in `demo-research-information-schema` that the contained records must conform to

Each JSON file contains an array of records conforming to `<ClassName>`.

## Terminology

- **dump-things-server** and **dump-things-service** are used interchangeably. `dump-things-service` is the PyPI package name and the command to start the server; `dump-things-server` is the general name for the server/project.
- **data model**, **data class**, and **data model (class)** are used interchangeably. Generally, "data model" refers to the concept and "data class" refers to the implementation, but the distinction is not strict in this project.

## Conventions

- **Commits**: conventional commits (`feat:`, `fix:`, `docs:`, `build:`)
- **Data README**: A `README.md` file should be maintained for each subdirectory of `data/`. It should provide an up-to-date summary of the gathered metadata within the subdirectory, including but not exclusive to the strategies used and decisions made in the process of gathering the metadata and a description of the gathered data. The `README.md` should be checked and updated, if and only if appropriate, whenever the metadata within the subdirectory is updated.
