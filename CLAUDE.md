# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repo serves two purposes:

1. **Metadata gathering setup**: Provides a setup for AI coding agents and people to gather research metadata from CON (Center for Open Neuroscience) related websites, repositories, and registries. Candidate data is validated using the REST API of a dump-things-service instance. Humans give final confirmation and commit the validated metadata.
2. **CLI tool**: A Python CLI tool (`dump-research-info`) for dumping the gathered metadata in this repo to an [Orinoco dump-things-service](https://hub.psychoinformatics.de/orinoco/dump-things-service) instance.

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

These JSON arrays are the repository's reviewed metadata contract. Do not add a
parallel canonical model. Use the classes and relationships provided by the
research-information demonstrator and its DataLad Things v2 imports. If a real
schema gap is found, document it before introducing any local extension.

Source adapters must create deterministic candidate arrays, preserve stable
identifiers, reconcile duplicate entities, and validate every record before
replacing files under `data/`. A source README records acquisition and mapping
decisions. Prefer checked-in Pixi tasks and source-version records for
reproducible fetch, transform, and validation steps. Keep the repository as pure
Git unless that decision is explicitly revisited. See
`docs/references/ingestion-contract.md`.

Each JSON file contains an array of records conforming to `<ClassName>`.

#### `pool_psychoinformatics_de`

Records in `data/pool_psychoinformatics_de/` were downloaded directly from the
public REST API at `https://pool.psychoinformatics.de/api/` (collection:
`public`, endpoint: `GET /public/records/{ClassName}`). They were **not**
gathered by an AI agent analyzing source content — they are verbatim copies of
the records served by the API. Only a selected subset of available classes was
downloaded: those considered useful as a controlled vocabulary for building a
knowledge pool (`Rule`, `XYZPublicationVenue`, `XYZAgentRole`,
`XYZBibliographicType`, `XYZQuality`, `XYZTopic`, `Property`,
`XYZInstrument`, `AnnotationTag`, `XYZEntityRole`, `XYZInstrumentType`,
`XYZCompetitionType`, `XYZObjective`).

## Terminology

- **dump-things-server** and **dump-things-service** are used interchangeably. `dump-things-service` is the PyPI package name and the command to start the server; `dump-things-server` is the general name for the server/project.
- **data model**, **data class**, and **data model (class)** are used interchangeably. Generally, "data model" refers to the concept and "data class" refers to the implementation, but the distinction is not strict in this project.
- **data**, **metadata**, and **(meta)data** are used interchangeably. Whether a piece of data is "meta" is relative, and we don't make that distinction in this project.
- **this project** and **this repo** are used interchangeably, referring to the same thing from different perspectives.

## Instructions for Claude Code Agents

- By default, user-specified notes should be added to `CLAUDE.md`
  unless specified otherwise.

## Conventions

- **Commits**: conventional commits (`feat:`, `fix:`, `docs:`, `build:`)
- **Data README**: A `README.md` file should be maintained for each subdirectory of `data/`. It should provide an up-to-date summary of the gathered metadata within the subdirectory, including but not exclusive to the strategies used and decisions made in the process of gathering the metadata, a description of the gathered metadata, and known issues of the gathered metadata. The `README.md` should be checked and updated, if and only if appropriate, whenever the metadata within the subdirectory is updated.
- **README updates**: For each newly added Claude Code slash command, hatch command, or other tool in the project, add a description of it to the project's `README.md`.
- **Line length in text files**: When modifying or editing text files
  (e.g., markdown files), keep lines at a reasonable length for human
  readability. Break long lines into multiple shorter lines.
- **Pytest**: Organize related tests in classes and use parametrization.
