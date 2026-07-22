# dump-research-info

-----

This repository gathers modeled research information about the Center for Open
Neuroscience (CON) and provides a tool to load it into an
[Orinoco dump-things-service](https://hub.psychoinformatics.de/orinoco/dump-things-service)
instance.

The reviewed metadata contract is the existing source-scoped JSON layout:
`data/<source_name>/<ClassName>.json`. Each file is a JSON array whose records
conform to the named class in the
[research-information demonstrator schema](https://concepts.datalad.org/s/demo-research-information/unreleased/).
That schema uses the foundational [DataLad Things v2](https://concepts.datalad.org/s/things/v2/)
model. The tracked JSON files are the ingestion targets; a parallel local entity
schema is not maintained.

AI agents and people may gather, reconcile, and improve candidate records, but
only records validated against the configured dump-things collection are
promoted into `data/`. The same modeled records can later drive the CON website,
grant applications, reports, APIs, JSONL exports, and other projections.

## Table of Contents

- [Server Configuration](#server-configuration)
- [Metadata and Ingestion Contract](#metadata-and-ingestion-contract)
- [Commands and Tools](#commands-and-tools)
  - [CLI](#cli)
  - [Hatch Commands](#hatch-commands)
  - [Claude Code Slash Commands](#claude-code-slash-commands)
- [License](#license)

## Metadata and Ingestion Contract

- A source has one directory under `data/` and a README that documents its
  origin, inclusion policy, retrieval date, and modeling decisions.
- A file stem is an exact schema class name, such as `XYZPerson`,
  `XYZProject`, `XYZDataset`, or `XYZPublication`.
- Top-level records follow the existing endpoint convention: the file name
  selects the class. Nested polymorphic values include `schema_type` where the
  schema requires it.
- Stable external identifiers are reused as `pid` values whenever possible.
  Source-local identifiers are retained as additional identifiers rather than
  creating a second identity for the same thing.
- Source refreshes produce reviewable diffs. They do not blindly overwrite
  curated records, and duplicate entities are reconciled before loading.
- Acquisition and transformation use checked-in Pixi tasks and versioned source
  metadata. The repository remains pure Git for now.

The detailed target-class mapping, identity rules, validation gate, source
sequence, and open decisions are in
[`docs/references/ingestion-contract.md`](docs/references/ingestion-contract.md).

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
