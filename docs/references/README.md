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

### [Psychoinformatics Website-from-Model Workflow](psychoinformatics-de.md)

Current-state description of the pipeline in
[`www/www-from-model`](https://hub.psychoinformatics.de/www/www-from-model)
that generates the **entire** Psychoinformatics group website
([www.psychoinformatics.de](https://www.psychoinformatics.de) and
its [draft mirror](https://www-draft.psychoinformatics.de)) from the
knowledge pool. Key features vs. the TRR379 approach: no external
code repo (Jinja2 templates replace custom Python scripts), one
consolidated `update-from-pool.yaml` workflow with a step per class,
reusable composite actions pulled from
[`orinoco/flow`](https://hub.psychoinformatics.de/orinoco/flow), a
strict "no manual content edits" policy, and coverage of eight
content classes (persons, projects, objectives, topics, publications,
instruments, datasets, plus a homepage). Also covers depiction
registration via git-annex and the navigation graph rendered from
`static/graph.json`. Includes a comparison table showing the
evolution from TRR379 (v1) through an intermediate v2 layout to
the current pipeline.

#### [Psychoinformatics Website-from-Model Workflows — earlier snapshot](pimde-www-from-model-workflow.md)

Kept as a historical reference: the v2 layout with five separate
per-class workflows using `qrg`, before consolidation into a single
workflow and the addition of depictions/graph. Superseded by
`psychoinformatics-de.md` above.

## External references

- [Developer onboarding notes for www-from-model (HedgeDoc)](https://hedgedoc.psychoinformatics.de/GbtN4IvTTLaGDUJN6rkU-A)
  — Stephan Heunis's notes covering local development setup,
  step-by-step pipeline walkthrough with full example records
  (including inlined JSON), `qrg` command semantics, and a design
  sketch for the portrait-image feature. Contains a clarification
  from Michal Szczepanik on the `-p delegated_by` inlining behavior.
- [dump-things-server](https://hub.psychoinformatics.de/datalink/dump-things-server)
  — the knowledge pool server that all workflows query
- [orinoco/flow](https://hub.psychoinformatics.de/orinoco/flow)
  — "FLOW" toolkit; provides the `prep-metadata-query` and
  `deposit-changes` composite Forgejo Actions reused across sites
- [orinoco/query-things (`qri`)](https://hub.psychoinformatics.de/orinoco/query-things)
  — CLI toolkit for filtering, inlining, and rendering pool records
  (used by the current `www-from-model` pipeline)
- [orinoco/dump-things-pyclient (`dtc`)](https://hub.psychoinformatics.de/orinoco/dump-things-pyclient)
  — CLI client for the pool API (used by the current `www-from-model`
  pipeline)
- [datalink/dump-things-pyclient (`dtc`)](https://hub.psychoinformatics.de/datalink/dump-things-pyclient)
  and [datalink/query-rse-group (`qrg`)](https://hub.psychoinformatics.de/datalink/query-rse-group)
  — the equivalents used by the TRR379 workflow and the earlier
  v2 pim.de layout
- [orinoco/knowledge-enrichment](https://hub.psychoinformatics.de/orinoco/knowledge-enrichment)
  — provides `tools/get-depiction-urls.py`, downloaded on demand by
  the depiction-registration workflow
- [orinoco/things-graph-renderer](https://hub.psychoinformatics.de/orinoco/things-graph-renderer)
  — client-side navigation-graph renderer loaded by the site
- [demo-research-information-schema](https://concepts.datalad.org/s/demo-research-information/unreleased.yaml)
  ([docs](https://concepts.datalad.org/s/demo-research-information/unreleased/))
  — the data model that all records conform to
- [psychoinformatics-de/datalad-concepts](https://github.com/psychoinformatics-de/datalad-concepts)
  ([rendered at `concepts.datalad.org`](https://concepts.datalad.org))
  — LinkML source for the schemas served by the pool
