# dump-research-info

-----

This repository gathers and models research information related to the Center
for Open Neuroscience (CON). Git-tracked YAML under `metadata/` is the initial
authority for curated records. Source-scoped observations and legacy imports
remain under `data/`.

The model starts from the
[demo-research-information-schema](https://concepts.datalad.org/s/demo-research-information/unreleased.yaml)
and records demonstrated CON extensions separately. A future formal schema can
generate JSON Schema, linked-data exports, SHACL shapes, and `shacl-vue` forms.

The CLI can export reviewed records to
[Orinoco dump-things-service](https://hub.psychoinformatics.de/orinoco/dump-things-service).
The service is an optional validator, index, API, and future editing backend;
it is not the initial source of truth.

AI agents may gather observations and propose changes. Humans review and merge
canonical facts, relationships, and public narratives. Generated website,
grant, reporting, JSONL, and graph outputs are projections of the same records.

## Table of Contents

- [Server Configuration](#server-configuration)
- [Metadata Authority](#metadata-authority)
- [Commands and Tools](#commands-and-tools)
  - [CLI](#cli)
  - [Hatch Commands](#hatch-commands)
  - [Claude Code Slash Commands](#claude-code-slash-commands)
- [License](#license)

## Metadata Authority

The repository separates three concerns:

- `data/`: source-scoped JSON snapshots and earlier gathered records;
- `metadata/`: canonical YAML records, evidence, assertions, source policies,
  and the draft CON profile;
- generated projections: website pages, grant/report material, JSONL, and graph
  data, which must not become canonical input.

See [`metadata/README.md`](metadata/README.md) for record ownership, Zotero
collection policy, the DataLad fixture, and current review boundaries.

## Server Configuration

Tokens for accessing the dump-things-server instance for validating
gathered metadata are defined in `.dumpthings.yaml` in the `store/`
directory. The interpretation of the token modes is documented at
[christian-monch/dump-things-server#67 (comment)](https://github.com/christian-monch/dump-things-server/issues/67#issuecomment-2834900042)
and
[dump-things-service#118](https://hub.psychoinformatics.de/orinoco/dump-things-service/issues/118).

## Commands and Tools

### CLI

- **`dump-research-info`** — Main CLI entry point
  (also invocable via `python -m dump_research_info`).
  Used for dumping the gathered (meta)data in this repo
  to a dump-things-server instance.

### Hatch Commands

- **`hatch run dump-server:start`** — Start a local dump-things-server
  instance configured to serve the `store/` directory.
  The server listens on `localhost:8111` and allows CORS requests
  from `http://localhost:8000`.
  Used for validating gathered metadata against the
  demo-research-information-schema.
- **`hatch run tools:serve-frontend`** — Serve the frontend web UI
  from `_ext/pool.psychoinformatics.de-ui/dist/` on `http://localhost:8000`.
  Used for browsing and inspecting data in the dump-things-server instance.
- **`hatch run types:check`** — Run mypy type checking on the source
  and test packages.

### Claude Code Slash Commands

- **`/gather_metadata <source>`** — Gather metadata from a specified source.
  This command guides Claude Code through fetching information from
  the source, constructing records conforming to the
  demo-research-information-schema, validating each record against a
  running dump-things-server instance, and storing valid records as
  JSON files in `data/<source_name>/`.
- **`/start_frontend`** — Launch the local frontend web UI for the
  dump-things-server. This command handles cloning and building the
  frontend repo (if needed) and serving it on `http://localhost:8000`.

## License

`dump-research-info` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
