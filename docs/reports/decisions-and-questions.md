# CON metadata site decisions and questions

This report is the review surface for implementation choices, unresolved policy,
and external actions. It should be updated whenever a decision changes.

## Settled decisions

| ID | Decision | Reason | Revisit when |
|---|---|---|---|
| D001 | Validated Things v2 JSON remains canonical for research entities. | Preserves upstream compatibility and existing validation. | The upstream schema contract changes. |
| D002 | The repository remains pure Git. | Current data volume does not require annexed storage. | Large binary assets or provenance requirements justify DataLad. |
| D003 | Source snapshots, candidates, resolutions, and promoted records remain distinct. | Keeps deterministic extraction separate from reviewed assertions. | Never collapse without equivalent provenance. |
| D004 | Editorial content is versioned YAML outside Things v2. | Principles, engagement guidance, contact text, and licensing are not research entities. | A compatible upstream editorial schema exists. |
| D005 | Legacy editorial content is seeded once, then manually curated. | A live-site refresh must not overwrite intentional copy edits. | A reviewed bidirectional editorial workflow is implemented. |
| D006 | Pull request previews use artifact-only privileged deployment. | Fork code must not execute with a write-capable token. | GitHub Pages gains native safe fork previews. |
| D007 | SHACL-vue is a separate future editor trust boundary. | Editing requires RDF, persistence, authentication, and reviewed Git write-back. | The staging service and round trip exist. |

## Recommended defaults being implemented

| ID | Default | Impact if changed |
|---|---|---|
| R001 | Deploy first at the GitHub project URL. | A custom root domain changes generated base paths and cutover/redirect planning. |
| R002 | Use source-specific scalar authority, with explicit per-conflict exceptions. | Silent class-level precedence can publish known typos or poor display labels. |
| R003 | Treat images as presentation assets, not embedded Things v2 values by default. | A future depiction model can reference curated local assets without rewriting entity identity. |
| R004 | Accept only high-confidence project relationships with direct authoritative evidence. | Lower-confidence agent inferences remain review items rather than assertions. |

## Open questions

| ID | Question | Recommendation | Blocks |
|---|---|---|---|
| Q001 | Who can enable upstream Pages and workflow write permissions? | A maintainer performs the documented one-time bootstrap after merge. | Public upstream deployment and previews. |
| Q002 | When should `centerforopenneuroscience.org` move to the generated site? | Run at the project URL first, audit redirects/accessibility, then schedule cutover. | Custom-domain production only. |
| Q003 | Who approves changes to principles, biographies, and support acknowledgements? | Use CODEOWNERS or explicit review by a small editorial group. | Governance, not implementation. |
| Q004 | Which of the 103 legacy images may be retained, and under what licenses? | Copy only selected logos/headshots after attribution and consent review. | Local image migration. |
| Q005 | Should manually curated edits update a source record or enter `data/curated/`? | Use a separate curated source so source refreshes remain reproducible. | Future SHACL-vue write-back. |
| Q006 | Which source is authoritative when a project affiliation or contributor role changes? | Prefer the project-maintained source, with the CON site as presentation evidence. | Automated relationship refresh. |

## Current review queues

| Queue | Current size | Next action |
|---|---:|---|
| Scalar merge conflicts | 13 | Resolve in explicit merge policy and enforce in CI. |
| Current-site field-level review | 106 | Separate identity links from narrative/editorial links. |
| Legacy local images | 103 | Establish selection, license, and storage policy. |
| Zotero creator occurrences | 1,930 | Resolve high-confidence ORCID/name matches through reviewed mappings. |
| Zotero tags | 49 | Map to existing topics or retain as source annotations. |
| Zotero venues without ISSNs | 42 | Resolve through authoritative journal metadata. |

## Review checklist

- Confirm D004 and D005: editorial YAML is acceptable alongside Things v2 JSON.
- Confirm R001: use the GitHub project URL for the first deployment.
- Assign an owner for Q001 and Q003.
- Decide whether `data/curated/` is the preferred future human-edit source.
