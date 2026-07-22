# Static site projection

This directory contains the presentation layer for the CON metadata website.
It has no independent content database. `scripts/build_site.py` reads the
validated JSON arrays under `data/`, reconciles records by class and PID, and
writes a deployable static site under `build/site/`.

## Build and preview

```sh
pixi run site-build
pixi run site-serve
```

The local site is then available at http://localhost:8000/.

For hosting below a path, call the builder directly:

```sh
pixi run python scripts/build_site.py --base-path /dump-research-info/
```

## Merge policy

- `con_site` is preferred for CON narratives, people, organizations, projects,
  and grants.
- `zotero_centerforopenneuroscience` is preferred for publications and
  datasets.
- `pool_psychoinformatics_de` is preferred for shared controlled vocabulary.
- Lists are unioned deterministically.
- Conflicting scalar values select the preferred source and are written to
  `build/site-merge-report.json` for agent or human review.
- Every contributing source remains visible on detail pages.

This merge is a website projection. It does not rewrite or silently curate the
source JSON files.

## SHACL-vue boundary

The public site is intentionally read-only and static. A future SHACL-vue
editor can use the same LinkML-derived SHACL, OWL class hierarchy, and modeled
records, but it also needs authenticated write APIs, token handling, a curation
workflow, and deployment-specific configuration. It should be deployed as an
editing surface rather than embedded into this public build until those pieces
are available.
