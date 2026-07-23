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

## Implementation checkpoint: Zotero creator identities

### Decisions added

- **D014 - Resolve aliases explicitly, never fuzzily.** Zotero creator variants map to existing person or organization PIDs only through the reviewed YAML file; fuzzy matching is limited to candidate discovery and never runs during ingestion.
- **D015 - Make promotion reproducible and fail stale CI.** Candidate generation, semantic promotion, and promoted-data comparison are separate Pixi tasks. CI regenerates candidates offline and fails if committed Zotero records differ.
- **D016 - Leave external coauthors unresolved by default.** The repository does not create person entities merely to eliminate a reconciliation count; identity records require a defined scope and sufficient evidence.

### Questions added

- **Q011 - Person scope:** Should future person modeling include every publication coauthor, only CON contributors and project investigators, or an intermediate evidence-based subset?
- **Q012 - Identity source:** Should ORCID become a separate person-enrichment ETL before expanding beyond the current CON roster?

### Current review facts

- 28 normalized aliases across 15 modeled people resolve 110 Zotero creator occurrences.
- The unresolved queue is now 1,817 occurrences across 1,221 names; the remaining high-similarity candidates were reviewed as different people.
- DataLad slice: 32 nodes and 73 edges, including 15 people.
- DANDI slice: 16 nodes and 26 edges, including 4 people.
- Validation: 1,445 of 1,445 Things v2 records valid after promotion.

## Implementation checkpoint: legacy assets

### Decisions added

- **D017 - Preserve before selecting.** Every image referenced by the pinned legacy inventory is mirrored byte-for-byte from the pinned source commit with a SHA-256 manifest; preservation does not imply approval for current prominent display.
- **D018 - Keep builds independent of the old domain.** The static site artifact contains the complete mirrored asset set, and CI verifies it offline.

### Questions added

- **Q013 - Portrait review:** Who is the editorial owner for confirming which of the 33 legacy team portraits remain current and approved for display?
- **Q014 - Brand review:** Should legacy third-party marks be shown as a historical project index, or replaced selectively with current upstream brand assets and explicit trademark notes?

### Current review facts

- 105 unique source assets are preserved: 61 project/third-party marks, 33 portraits, 6 handout previews, 4 banners, and 1 contact mark.
- The mirrored asset set is 3,775,586 bytes and has no unmatched source reference.
- CI can verify inventory coverage and byte-level integrity without network access.

## Implementation checkpoint: engagement media

### Decisions added

- **D019 - Display the low-risk resource previews now.** The six handout images already linked by the engagement page use mirrored, base-path-aware assets with explicit alternative text and lazy loading.
- **D020 - Withhold portraits and project marks by default.** Preserved portraits and third-party marks remain available to editors but are not automatically introduced into the replacement design before Q013 and Q014 are resolved.

### Current review facts

- The engagement page renders 6 local handout previews and contains no legacy-domain handout image dependency.
- Editorial asset URLs use the same configurable base path as pull-request previews and the main deployment.
