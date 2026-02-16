# dump-research-info

-----

This repo provides a setup to gather research information related to 
Center for Open Neuroscience (CON) as (meta)data and a tool to dump the gathered 
(meta)data to an instance of [dump-things-server](https://hub.psychoinformatics.de/datalink/dump-things-server).
The (meta)data gathered must conform to the data models defined in the 
[demo-research-information-schema](https://concepts.datalad.org/s/demo-research-information/unreleased.yaml),
which is documented at [DataLad Concepts](https://concepts.datalad.org/s/demo-research-information/unreleased/),
and the dump-things-server instance receives the (meta)data in a collection that must
conform to the data models defined in the 
[demo-research-information-schema](https://concepts.datalad.org/s/demo-research-information/unreleased.yaml)
as well.

The setup is done in a way to facilitate AI coding agents, such as Claude Code, to gather
the (meta)data from various sources, such as CON related websites and project repositories,
and to validate the gathered (meta)data against the target data models through the
REST API of a dump-things-server instance. Once any gathered (meta)data is validated,
it will be added to this repository. The tool provided in this repository can be used
for dumping all the gathered (meta)data in this repo to a dump-things-server instance.

The gathered (meta)data are stored in separate JSON files each named with the name of
a model (or class) in the demo-research-information-schema, and the files are stored
in a subdirectory named after the source of the (meta)data. All (meta)data records of
a particular class from a particular source are stored in the file named after the class
in the subdirectory named after the source. All subdirectories are stored in the 
`data` directory in this repository.

## Table of Contents

- [Server Configuration](#server-configuration)
- [Commands and Tools](#commands-and-tools)
  - [CLI](#cli)
  - [Hatch Commands](#hatch-commands)
  - [Claude Code Slash Commands](#claude-code-slash-commands)
- [License](#license)

## Server Configuration

Tokens for accessing the dump-things-server instance for validating
gathered metadata are defined in `.dumpthings.yaml` in the `store/`
directory. The interpretation of the token modes is documented at
[christian-monch/dump-things-server#67 (comment)](https://github.com/christian-monch/dump-things-server/issues/67#issuecomment-2834900042)
and
[dump-things-server#118](https://hub.psychoinformatics.de/datalink/dump-things-server/issues/118).

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
