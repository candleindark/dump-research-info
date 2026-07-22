# Reference Documents

This directory contains reference documentation for external systems
and workflows that interact with the dump-things ecosystem — in
particular, how knowledge pool data flows into websites.

## Documents

### [TRR379 Contributors & Projects Workflow](trr379-contributors-projects-workflow.md)

Documents the Forgejo Actions workflow in
[`q04/www.trr379.de`](https://hub.trr379.de/q04/www.trr379.de)
that generates contributor and project pages for the
[TRR379 website](https://www.trr379.de).  This is the original
approach: a single monolithic workflow clones the
[`pool-publication-page`](https://hub.trr379.de/q02/pool-publication-page)
code repo, fetches records from the TRR379 pool via `dtc`, enriches
them through a pipeline of custom Python filters and `qrg`
commands (including ROR-based site inference), and writes Hugo
Markdown pages using bespoke Python formatter scripts.

### [Psychoinformatics Website-from-Model Workflows](pimde-www-from-model-workflow.md)

Documents the refactored approach in
[`www/www-from-model`](https://hub.psychoinformatics.de/www/www-from-model)
that generates the **entire** Psychoinformatics group website from
the knowledge pool — not just people and projects, but also the
frontpage, topics, and objectives.  Key differences from the TRR379
approach: no external code repo (Jinja2 templates replace custom
Python scripts), five independent workflows (one per content type)
instead of one monolith, reusable composite actions for setup and
commit, and a strict "no manual content edits" policy.  Also covers
planned work on portrait images and person-page enrichment.

## External references

- [Developer onboarding notes for www-from-model (HedgeDoc)](https://hedgedoc.psychoinformatics.de/GbtN4IvTTLaGDUJN6rkU-A)
  — Stephan Heunis's notes covering local development setup,
  step-by-step pipeline walkthrough with full example records
  (including inlined JSON), `qrg` command semantics, and a design
  sketch for the portrait-image feature. Contains a clarification
  from Michal Szczepanik on the `-p delegated_by` inlining behavior.
- [dump-things-server](https://hub.psychoinformatics.de/datalink/dump-things-server)
  — the knowledge pool server that both workflows query
- [dump-things-pyclient (`dtc`)](https://hub.psychoinformatics.de/datalink/dump-things-pyclient)
  — CLI client for the pool API
- [query-rse-group (`qrg`)](https://hub.psychoinformatics.de/datalink/query-rse-group)
  — CLI toolkit for filtering, inlining, and rendering pool records
- [demo-research-information-schema](https://concepts.datalad.org/s/demo-research-information/unreleased.yaml)
  ([docs](https://concepts.datalad.org/s/demo-research-information/unreleased/))
  — the data model that all records conform to
