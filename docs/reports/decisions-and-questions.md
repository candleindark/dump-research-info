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

## Implementation checkpoint: curated relationships

### Decisions added

- **D008 - Fail closed on scalar conflicts.** `site/merge-policy.yaml` must exactly match the conflicts observed across source records. New conflicts and stale decisions both fail the build.
- **D009 - Keep curation separate from ingestion.** Agent-reviewed assertions live in `data/curated_relationships/`; generated legacy-site and Zotero sources remain untouched and refreshable.
- **D010 - Use existing Things v2 extension points.** Project links use validated `dlthings:AttributeSpecification` records with `schema:funding`, `schema:subjectOf`, and `dcterms:relation` predicates.
- **D011 - Keep Zotero authoritative for publications.** A publication found online but absent from group 6197458 is queued for Zotero rather than duplicated in a competing source.
- **D012 - Review project-centered graph slices.** Deterministic outgoing traversals run to depth two, assert required targets, and are checked for staleness in CI.
- **D013 - Model the two primary DataLad NSF awards.** NSF 1429999 and 1912266 are represented as grants using current NSF API records and linked to DataLad.

### Questions added

- **Q007 - Additional DataLad funding:** Should BMBF 01GQ1905 and 01GQ1411, NIH 1P41EB019936-01A1, EU 945539 and 826421, and DFG SFB1451-INF become full grant entities now, or wait for a general grant-source ETL?
- **Q008 - DANDI publication:** Add DOI `10.7554/eLife.78362` to Zotero group 6197458 so the next refresh turns the existing project link into an internal publication entity.
- **Q009 - Predicate vocabulary:** Retain the pragmatic schema.org/Dublin Core predicates, or introduce more specific relationship classes when upstream Things v2 provides them?
- **Q010 - Assertion authoring:** Keep the small curated JSON overlays directly reviewable, or generate them from a dedicated YAML assertion file once the relationship set grows?

### Current review facts

- DataLad slice: 29 nodes, 65 edges, 2 grants, 3 publications, 1 instrument, and no missing external candidate.
- DANDI slice: 15 nodes, 22 edges, 1 grant, 1 publication, and 1 publication queued for Zotero.
- Validation: 1,445 of 1,445 Things v2 records valid.
- Site merge: 13 reviewed source conflicts resolved; 0 conflicts remain in rendered data.
