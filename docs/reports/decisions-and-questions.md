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
| D005 | Current-site editorial content is seeded once, then manually curated. | A source refresh must not overwrite intentional copy edits. | A reviewed bidirectional editorial workflow is implemented. |
| D006 | Pull request previews use artifact-only privileged deployment. | Fork code must not execute with a write-capable token. | GitHub Pages gains native safe fork previews. |
| D007 | SHACL-vue is the future editor UI over the same Things v2 model and a separate runtime trust boundary. | Editing requires an RDF serialization adapter, persistence, authentication, and reviewed Git write-back. | The staging service and lossless round trip exist. |

## Recommended defaults being implemented

| ID | Default | Impact if changed |
|---|---|---|
| R001 | Deploy first at the GitHub project URL. | A custom root domain changes generated base paths and cutover/redirect planning. |
| R002 | Use source-specific scalar authority, with explicit per-conflict exceptions. | Silent class-level precedence can publish known typos or poor display labels. |
| R003 | Treat imported current-site images as approved presentation assets, mapped reviewably to Things v2 entity PIDs. | A future depiction model can absorb these mappings without rewriting entity identity. |
| R004 | Accept only high-confidence project relationships with direct authoritative evidence. | Lower-confidence agent inferences remain review items rather than assertions. |

## Open questions

| ID | Question | Recommendation | Blocks |
|---|---|---|---|
| Q001 | Who can enable upstream Pages and workflow write permissions? | A maintainer performs the documented one-time bootstrap after merge. | Public upstream deployment and previews. |
| Q002 | When should `centerforopenneuroscience.org` move to the generated site? | Run at the project URL first, audit redirects/accessibility, then schedule cutover. | Custom-domain production only. |
| Q003 | Who approves changes to principles, biographies, and support acknowledgements? | Use CODEOWNERS or explicit review by a small editorial group. | Governance, not implementation. |
| Q005 | Should manually curated edits update a source record or enter `data/curated/`? | Use a separate curated source so source refreshes remain reproducible. | Future SHACL-vue write-back. |
| Q006 | Which source is authoritative when a project affiliation or contributor role changes? | Prefer evidence maintained by the represented project, with the CON site as presentation evidence. This does not mean the Psychoinformatics site or Michael Hanke's lab generally. | Automated relationship refresh. |

## Current review queues

| Queue | Current size | Next action |
|---|---:|---|
| Scalar merge conflicts | 13 | Resolve in explicit merge policy and enforce in CI. |
| Current-site field-level review | 106 | Separate identity links from narrative/editorial links. |
| Current-site imported images | 105 | Keep the approved PID mapping aligned with the pinned inventory. |
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

- **D008 - Fail closed on scalar conflicts.** `site/merge-policy.yaml` must exactly match the current non-empty scalar disagreements for the same class, PID, and field. New conflicts and stale decisions both fail the build. This is not a claim that every content or modeling decision is complete.
- **D009 - Keep curation separate from ingestion.** Agent-reviewed assertions live in `data/curated_relationships/`; generated current-site and Zotero sources remain untouched and refreshable.
- **D010 - Use existing Things v2 extension points.** Project links use validated `dlthings:AttributeSpecification` records with `schema:funding`, `schema:subjectOf`, and `dcterms:relation` predicates.
- **D011 - Keep Zotero authoritative for publications.** A publication found online but absent from group 6197458 is queued for Zotero rather than duplicated in a competing source.
- **D012 - Review project-centered graph slices.** Deterministic outgoing traversals run to depth two, assert required targets, and are checked for staleness in CI.
- **D013 - Model the two primary DataLad NSF awards.** NSF 1429999 and 1912266 are represented as grants using current NSF API records and linked to DataLad.

### Questions added

- **Q007 - Additional DataLad funding:** Should BMBF 01GQ1905 and 01GQ1411, NIH 1P41EB019936-01A1, EU 945539 and 826421, and DFG SFB1451-INF become full grant entities now, or wait for a general grant-source ETL?
- **Q008 - DANDI publication:** Resolved 2026-07-23. DOI `10.7554/eLife.78362` is approved for the Zotero `External` collection because the paper does not list CON as an affiliation.
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

## Implementation checkpoint: current-site assets

### Decisions added

- **D017 - Import with provenance.** Every image referenced by the pinned current-site inventory is copied byte-for-byte from the pinned source commit with a SHA-256 manifest.
- **D018 - Keep builds independent of the current deployment.** The static site artifact contains the complete imported asset set, and CI verifies it offline.
- **D021 - Continue the current display approval.** Existing public display and explicit owner approval cover all 105 imported assets for now. Any repository developer can revise approval or PID mappings through review.
- **D022 - Map display separately from entity identity.** `site/entity-assets.yaml` maps the current roster and projects to local images, ordering, and roster groups without creating an alternative research-information model.

### Resolved questions

- **Q013 - Portrait review:** Resolved. The repository owner approved the 33 current-site portraits; developers with repository access may update the mapping.
- **Q014 - Project logo review:** Resolved. The current-site project logos are approved. "Project logo" means the graphic identifying the represented project, not branding copied from the Psychoinformatics site.

### Current review facts

- 105 unique source assets are imported: 61 project/organization logos, 33 portraits, 6 handout previews, 4 banners, and 1 contact logo.
- The imported asset set is 3,775,586 bytes and has no unmatched source reference.
- CI can verify inventory coverage and byte-level integrity without network access.

## Implementation checkpoint: engagement media

### Decisions added

- **D019 - Display resource previews from the build.** The six handout images linked by the engagement page use imported, base-path-aware assets with explicit alternative text and lazy loading.
- **D020 - Display approved portraits and project logos.** The current roster and project records use the reviewed PID mapping and local build paths.
- **D023 - Model broadly, stage presentation deliberately.** All sufficiently evidenced people can be modeled. The current-site roster is ordered and labeled first for initial display; additional entities can be introduced or toggled without deleting their records.
- **D024 - Research sources before generalizing ETL.** Parallel agent research maps authoritative sources, identifiers, candidate entities, and unknowns first. Deterministic adapters remain the maintenance target after source-specific evidence is understood.
- **D025 - Use the GitHub project URL first.** Custom-domain cutover remains a later deployment task.
- **D026 - Gate Zotero writes with review records.** A repository editor must approve DOI metadata, target collection, evidence, and rationale before the write command can add an item.

### Current review facts

- The engagement page renders 6 local handout previews and contains no current-site runtime image dependency.
- Editorial asset URLs use the same configurable base path as pull-request previews and the main deployment.
- The current inventory maps 33 roster entries and 23 project entries; 33 portraits and 19 project logos are available for entity pages.

## Current research questions

1. Which source-specific batches should be promoted first after the current-site and Zotero baselines: NIH/NSF grants, ORCID/ROR identities, DANDI datasets, or repository/software metadata?
2. How should current, historical, collaborator, project-contributor, and publication-author roles be time-qualified without collapsing them into employment?
3. Which evidence threshold distinguishes a direct CON project from a partner or ecosystem project?
4. Should grant continuations, supplements, subprojects, and parent awards be separate entities or qualified identifiers on one grant?
5. Should dataset concepts, immutable versions, and file-level assets be separate modeled entities?
6. Which relationships need typed classes rather than pragmatic `dlthings:AttributeSpecification` predicates?
7. Should source and approval provenance be displayed field-by-field or remain available in machine-readable reports?
