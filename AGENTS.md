# Repository agent instructions

## Data and architecture

- Validated DataLad Concepts Things v2 JSON is the canonical
  research-information representation.
- Keep source observations separated under `data/<source>/`.
- Preserve snapshot, candidate, reconciliation, review, and promotion
  boundaries for programmatic ingestion.
- The repository remains pure Git unless a later reviewed decision introduces
  DataLad.
- The public website is a deterministic static projection. Generated pages are
  not canonical records.
- SHACL-vue is a future editor over the same Things v2 model, not an alternative
  data model.
- Use the Forgejo `orinoco` projects as toolchain references. Do not substitute
  the Codeberg `datalink` repositories.

## Review boundaries

- Treat `docs/agent-notes/` as historical research and planning material.
  Reconcile it with current implementation and primary sources before acting on
  it.
- Maintain current decisions and unresolved questions in
  `docs/reports/decisions-and-questions.md`.
- New Zotero writes require an approved entry in
  `inputs/zotero_centerforopenneuroscience/reviewed-additions.yaml`.
- Keep credentials outside the repository.

## Commit co-authorship

Every commit authored by Codex must include a `Co-Authored-By` trailer
identifying both the tool name and version and the underlying model name and
version:

```text
Co-Authored-By: <tool name> <tool version> / <model name> <model version> <codex@openai.com>
```

Discover both versions from the active tool and session. Do not guess.
