# CON research-information architecture and implementation plan

Status: working decision document  
Last updated: 2026-07-22

This is the master plan for replacing the hand-maintained Center for Open
Neuroscience (CON) website with a modeled research-information system. It
consolidates the repository and service investigation in
`orinoco-con-website-plan.md` and the migration/model analysis in
`con-metadata-model-gap.md`.

## 1. North star

Build one reusable CON knowledge base, with the public website as one
projection of it.

The current [CON website](https://centerforopenneuroscience.org) is a valuable
migration source and evidence source. It is not the target information
architecture and need not be reproduced page-for-page.

The same modeled information should support:

- the public CON website;
- project, software, dataset, publication, and collaborator catalogs;
- grant planning and evidence packets;
- NIH and NSF application components;
- bios, biosketch support, CV fragments, and contributor profiles;
- progress reports and prior-work summaries;
- facilities, resources, and institutional-capability descriptions;
- impact and broader-impacts reports;
- graph, JSONL, JSON-LD/RDF, and other machine-readable exports;
- a future schema-driven editor based on `shacl-vue`.

The durable rule is:

> Store entities, facts, relationships, and evidence. Derive joins, summaries,
> pages, and application prose as reviewable projections.

## 2. Decisions already made

| Topic | Decision |
|---|---|
| Reference ecosystem | Use the Forgejo `orinoco` repositories, not the Codeberg `datalink` fork |
| Initial authority | A Git repository containing one YAML file per canonical record |
| Pipeline interchange | Generate JSONL; do not make JSONL the hand-edited authority |
| Initial editing | Manual and agent-assisted pull requests |
| Later editing | Add SHACL validation and `shacl-vue` after the model stabilizes |
| Migration scope | Preserve everything useful from the current live site, including currently published contact details |
| Historical scope | Retain historical people, roles, projects, and claims where evidence is available |
| Website strategy | Treat the website as a static projection, not as a runtime client of the metadata API |
| External enrichment | Additive, attributable candidate observations; never silent overwrites |
| Derived data | Inverse joins and presentation fields are generated, never canonical facts |
| Publication/output intake | Use the public CON Zotero group as the maintained curated feed; merge changes into canonical YAML through review |

## 3. Reference system and component map

### Primary references

- Planning issue: [`con/dump-research-info#18`](https://github.com/con/dump-research-info/issues/18)
- Process example: [TRR379 contributors/projects workflow](https://github.com/con/dump-research-info/blob/HEAD/docs/references/trr379-contributors-projects-workflow.md)
- Earlier exploration: [Psychoinformatics VisiData demo](https://github.com/con/visidata-demos/tree/master/psychoinformatics-1)
- Target design pattern: [Psychoinformatics website](https://www.psychoinformatics.de)
- CON output feed: [Center for Open Neuroscience Zotero group](https://www.zotero.org/groups/6197458/centerforopenneuroscience/library)
- Current audit and prototype choice: `con-source-inventory-and-first-slice.md`

### Current Orinoco services

- Pool API: [pool.psychoinformatics.de/api](https://pool.psychoinformatics.de/api)
- Pool editor: [pool.psychoinformatics.de/ui](https://pool.psychoinformatics.de/ui/)
- Service source: [`orinoco/dump-things-service`](https://hub.psychoinformatics.de/orinoco/dump-things-service)

The running service is useful as a reference and may later support editing or
indexing. It is not required for the first Git-native implementation.

### Reusable Forgejo components

| Component | Adopt now | Role for CON |
|---|---:|---|
| [`orinoco/flow`](https://hub.psychoinformatics.de/orinoco/flow) | Partly | Reuse Forgejo workflow mechanics and commit-only-if-changed behavior |
| [`orinoco/query-things`](https://hub.psychoinformatics.de/orinoco/query-things) | As a pattern | Reuse record resolution, filtering, link injection, and rendering ideas; adapt input to local YAML/JSONL |
| [`www/www-from-model`](https://hub.psychoinformatics.de/www/www-from-model) | As the main site reference | Reuse the separation between metadata, normalized view models, Hugo content, navigation, and presentation |
| [`orinoco/dump-things-service`](https://hub.psychoinformatics.de/orinoco/dump-things-service) | Later if needed | Optional index, API, incoming/curated workflow, audit log, and editor backend |
| [`orinoco/shacl-vue`](https://hub.psychoinformatics.de/orinoco/shacl-vue) | Later | Generate forms and viewers from stabilized SHACL shapes |
| [`orinoco/datalad-concepts`](https://hub.psychoinformatics.de/orinoco/datalad-concepts) | Evaluate during formalization | Possible route from modeled concepts to validation and linked-data representations |

## 4. Information layers

The system needs four distinct layers. Collapsing these layers would make both
maintenance and grant reuse unreliable.

| Layer | Stored content | Example |
|---|---|---|
| Entity facts | Canonical, queryable values and explicit links | A person's ORCID or a project's start date |
| Evidence observations | Sources and observations supporting or disputing a field | An ORCID response retrieved on a date |
| Claims | Reviewed interpretations supported by facts/evidence | CON has expertise in reproducible neuroimaging |
| Narratives/projections | Audience-specific generated outputs | A project page, biosketch paragraph, or facilities section |

Canonical entity files should remain readable and compatible with later
Things/SHACL import. Claim-level evidence belongs in a separate layer so an
entity does not become an unmanageable collection of source captures.

### 4.1 Canonical entity record

```yaml
pid: con:person/yarik-halchenko
schema_type: XYZPerson
name: Yaroslav Halchenko
identifiers:
  - type: ORCID
    value: https://orcid.org/...
roles:
  - organization: con:organization/center-for-open-neuroscience
    role: director
    valid_from: null
    valid_until: null
visibility: public
```

### 4.2 Evidence assertion

Assertions identify a subject and field path rather than duplicating the whole
entity record.

```yaml
id: con:assertion/person-yarik-role-director
subject: con:person/yarik-halchenko
path: /roles/0/role
observed_value: director
source:
  uri: https://centerforopenneuroscience.org/people/
  type: con_live_site
  retrieved_at: 2026-07-22
  source_modified_at: null
method: page_extraction
confidence: high
review_status: accepted
valid_from: null
valid_until: null
supersedes: null
```

Evidence and confidence are different. An authoritative source can be stale;
a self-reported statement can be current and accurate.

### 4.3 Generated narrative manifest

Every grant-facing or report-facing generated artifact should be able to state
which records and assertions produced it.

```yaml
projection: nih-facilities-v1
generated_at: 2026-07-22T00:00:00Z
generated_from:
  - con:organization/center-for-open-neuroscience
  - con:facility/example-compute-resource
  - con:assertion/example-resource-capacity
human_review: pending
```

## 5. Initial model scope

The existing `demo-research-information/unreleased` model is a useful starting
point, not a frozen contract. Start with its types and introduce new types only
when a real CON record or required projection demonstrates a gap.

### Entity classes

- `Organization` and organizational units
- `Person`
- `Project`
- `Grant` or `Award`, modeled independently from projects
- `Publication`
- `Dataset`
- `Software`, workflow, platform, and instrument
- `Document`, protocol, standard, and educational resource
- `Activity` and event
- `Facility` and research resource
- `Topic`, method, objective, and principle/concept
- `Depiction`, file, and other media
- first-class relationships when role, context, dates, or evidence matter
- impact observations and outcome measures

### Relationship requirements

Relationships must carry context rather than becoming unqualified lists. A
person may be a contributor to one project, an advisor to another, and a
coauthor of an output.

Minimum relationship properties are:

- subject, predicate, and object;
- role and project context where applicable;
- start and end dates;
- evidence and review status;
- active/historical status;
- publication visibility.

### Time-dependent information

Roles, affiliations, memberships, project status, funding, resource
availability, contact details, software versions, and impact metrics must
support validity or measurement dates. Avoid timeless claims such as "highly
cited"; store the metric, source, and measurement date instead.

## 6. Repository layout

```text
con-knowledge/
  metadata/
    records/
      organizations/
      people/
      projects/
      grants/
      publications/
      datasets/
      software/
      documents/
      activities/
      facilities/
      concepts/
      media/
      relationships/
      impacts/
    evidence/
      assertions/
      sources/
      captures/
    site/
      navigation.yaml
      featured.yaml
      redirects.yaml
    schema/
      profile.yaml
      vocabularies.yaml
      visibility.yaml
  assets/
  projections/
    templates/
      website/
      grants/
      reports/
      profiles/
    generated/
  site/
    layouts/
    static/
    content/                 # generated
  build/
    records.jsonl            # generated
    assertions.jsonl         # generated
    graph.json               # generated
    manifests/               # generated
```

Editing rules:

- Humans and agents edit `metadata/records`, `metadata/evidence`, controlled
  site configuration, projection templates, and presentation files.
- Builds own `projections/generated`, `site/content`, and `build`.
- Large captures or media can move to Git-annex only when ordinary Git becomes
  impractical.
- Generated fields such as `x_associated_projects` and `x_site` never flow back
  into canonical entity records.

## 7. Identifier policy

Recommended namespace:

```text
con: https://centerforopenneuroscience.org/id/
```

Examples:

```text
con:person/yarik-halchenko
con:project/datalad
con:grant/nih-...
```

External identifiers such as ORCID, ROR, DOI, PMID, PMCID, repository URL,
award number, and SWHID remain typed identifiers on the record. Existing
`xyzrins:` identifiers should be retained as legacy mappings rather than used
as the new canonical namespace.

## 8. Adapt the TRR379 workflow, do not copy its deployment assumptions

The [TRR379 workflow](https://github.com/con/dump-research-info/blob/HEAD/docs/references/trr379-contributors-projects-workflow.md)
has the right transformation pattern:

```text
fetch -> inline links -> derive inverse relationships -> enrich -> format -> commit
```

For CON, adapt it to:

```text
load canonical YAML
  -> validate stable IDs and record shape
  -> resolve local links
  -> derive inverse relationships
  -> combine accepted evidence
  -> optionally produce enrichment proposals
  -> emit normalized JSONL and graph views
  -> render one or more projections
  -> build and publish the static site
```

| TRR379 behavior | CON adaptation |
|---|---|
| Fetch authoritative records from the pool API | Read authoritative YAML from the checked-out repository |
| Resolve every link through HTTP | Resolve local PIDs; support remote resolution only as an optional adapter |
| Derive `x_*` joins for formatters | Keep equivalent fields in transient projection view models |
| Enrich affiliations from ROR | Produce sourced candidate assertions and a review queue |
| Emit Hugo page bundles | Retain, while allowing grant/report/profile templates too |
| Commit changed generated content | Reuse the commit-only-if-changed pattern from Orinoco FLOW |
| Require service tokens for builds | Use repository permissions until a service solves a demonstrated need |

This preserves the reusable pipeline while avoiding a premature Git/API
two-way synchronization problem.

## 9. Online enrichment and review policy

### Source priority

1. CON-authored or author-approved sources, supplied grant/report documents,
   and official CON repositories.
2. Official registries and issuing agencies: ORCID, ROR, Crossref, DataCite,
   PubMed, NIH, NSF, UKRI, and CORDIS.
3. Official institutional, project, publisher, repository, standard, and event
   pages.
4. Discovery indexes such as OpenAlex, Wikidata, Git hosting search, and web
   search.
5. Agent inference, which may only propose candidate assertions.

Useful primary interfaces include the [ORCID public API](https://info.orcid.org/what-is-orcid/services/public-api/),
[ROR API](https://ror.readme.io/docs/rest-api), [Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/),
[DataCite REST API](https://support.datacite.org/docs/api), [NCBI
E-utilities](https://www.ncbi.nlm.nih.gov/home/develop/api/), [NIH RePORTER
API](https://api.reporter.nih.gov/), and [NSF award API](https://resources.research.gov/common/webapi/awardapisearch-v1.htm).

For software and datasets, prefer exact repository and identifier metadata,
including [`CITATION.cff`](https://github.com/citation-file-format/citation-file-format),
[CodeMeta](https://codemeta.github.io/), [DataCite's schema](https://schema.datacite.org/),
and [SPDX identifiers](https://spdx.dev/learn/overview/).

### Zotero publication and output feed

The public CON Zotero group is a maintained intake source for research outputs.
Its [top-level item API](https://api.zotero.org/groups/6197458/items/top?v=3&limit=100)
is publicly readable and currently includes publications, software, and other
output types. Therefore, Zotero items must be classified into the broader
research-output model rather than mapped indiscriminately to `Publication`.

```text
CON Zotero group
  -> retrieve changed top-level items and collection metadata
  -> classify publication/software/dataset/document/other output
  -> normalize DOI, PMID/PMCID, ISBN, repository, and other identifiers
  -> match canonical CON records
  -> enrich exact identifiers from issuing registries
  -> emit additions, updates, conflicts, and possible removals for review
  -> merge accepted YAML changes
  -> regenerate website, grant, report, and machine-readable projections
```

Operational policy:

- Perform one complete initial import with pagination.
- Record the Zotero group ID, item key, item version, collection membership,
  tags, source URL, and retrieval timestamp on each observation.
- Use Zotero's library version and incremental `since`/conditional-request
  support for routine polling, with occasional complete reconciliation.
- Treat Zotero collection membership as a CON-curated inclusion signal, not as
  unquestionable bibliographic authority.
- Prefer DOI, PMID/PMCID, ISBN, or repository identifiers for matching; send
  title/creator/date-only matches to review.
- Resolve exact identifiers against Crossref, DataCite, PubMed, or the relevant
  issuing source while preserving Zotero's original observation.
- Do not automatically delete a canonical output when an item disappears from
  Zotero. Create a removal or archival proposal for review.
- Ignore child attachments and notes as independent publications by default;
  retain useful ones as evidence or related documents.
- Run the importer on a scheduled Forgejo action and by manual dispatch. A
  change should produce a reviewable branch or pull request; no change should
  be a no-op.

This makes routine publication maintenance a Zotero curation task while keeping
the Git history, evidence trail, and downstream builds reproducible. Zotero's
[Web API documentation](https://www.zotero.org/support/dev/web_api/v3/basics)
defines public-library reads, pagination, versioning, and incremental requests.

### Safe automation

- Validate and normalize exact persistent identifiers.
- Retrieve metadata for known DOI, PMID, ORCID, ROR, award, and repository IDs.
- Detect duplicates that share a persistent identifier.
- Import observations into a proposal/review branch.
- Flag broken links, stale observations, conflicts, and missing evidence.
- Suggest related outputs, people, projects, and grants.

### Human approval required

- Name-only identity matches.
- Current role, affiliation, membership, or project-status changes.
- Claims of CON authorship, leadership, participation, funding, or impact.
- Deletion or replacement of canonical descriptions.
- Publication of contact details not already intentionally public.
- Agent-generated summaries used as factual or grant-facing prose.

### Conflict handling

1. Preserve all observations.
2. Keep the current canonical value until review.
3. Create a conflict item showing field-specific sources.
4. Record the accepted resolution and reviewer.
5. Never interpret an empty upstream field as a deletion request.

The evidence model should remain compatible in spirit with [PROV-O](https://www.w3.org/TR/prov-o/).
Formal validation can later use [SHACL](https://www.w3.org/TR/shacl/).

## 10. Projection catalog

| Projection | Inputs | Output |
|---|---|---|
| Public website | Public entities, accepted claims, site configuration | Hugo pages, navigation, graph/search data, redirects |
| Person profile | Person, roles, projects, selected outputs | Website profile or internal directory card |
| Project portfolio | Projects, participants, outputs, grants, status | Public catalog and internal portfolio table |
| Grant prior-work packet | Relevant projects, outputs, contributions, evidence | Reviewed Markdown evidence list and citations |
| NIH biosketch support | Person, qualifications, contributions, selected outputs | Draft-support material, not a silently final biosketch |
| Facilities/resources | Facilities, capacity, availability, staff, project relevance | Funder-specific draft sections |
| NSF broader impacts | Activities, outputs, adoption, outcomes, measures | Evidence table and narrative draft |
| Progress report | Award period, milestones, activities, outputs, outcomes | RPPR/report-ready evidence packet |
| Funding attribution | Awards, projects, outputs, acknowledgements | Verified attribution lists and missing-attribution report |
| Staleness report | Assertions, evidence dates, validity periods | Maintenance/review queue |

Impact should be represented as an evidence chain rather than a single prose
field:

```text
activity -> immediate output -> adoption/use -> measured outcome -> significance
```

## 11. Current migration baseline

The existing `con/dump-research-info` material contains 79 CON records:

- 8 organizations;
- 33 people;
- 22 projects;
- 3 grants;
- 11 publications;
- 2 venues.

The live-site inventory adds or clarifies:

- 6 principles;
- 33 people and portraits across current and historical groupings;
- 22 featured projects/resources of several distinct types;
- 39 collaborating projects/tools and 2 partner organizations;
- engagement text, brochures/resources, and banners;
- current NSF, NIH, and CCN support references;
- homepage references and testimonial material.

This material should first be captured without loss, then decomposed into
reusable entities, relationships, claims, and site configuration. Existing
prose may be retained as a sourced editorial statement while better structured
facts are developed beneath it.

## 12. Execution plan

### Step 1: settle authority, identity, and privacy boundaries

Status: in progress.

Deliverables:

- approve the `con:` namespace;
- define public, internal, restricted, and generated visibility values;
- define reviewer/approver roles;
- decide where confidential grant source material lives;
- document Git as the sole initial authority.

Completion test: every future record and assertion has an unambiguous owner,
identifier, visibility, and review path.

### Step 2: create the minimal schema and repository skeleton

Status: pending.

Deliverables:

- directories from Section 6;
- lightweight YAML profiles for entity and assertion records;
- controlled vocabularies for type, role, status, evidence method, confidence,
  review status, and visibility;
- fixture records for one organization, person, project, grant, output,
  facility, relationship, and assertion.

Completion test: the fixture graph can represent one realistic CON vertical
slice without adding website-only fields to canonical records.

### Step 3: ingest the current CON corpus and live site

Status: pending.

Deliverables:

- import the 79 existing CON records;
- capture every live-site section and published asset;
- preserve source URL, retrieval date, original wording, and legacy identifier;
- split heterogeneous "project" entries into appropriate entity classes;
- create a migration report for omissions, duplicates, and conflicts.

Completion test: every meaningful fact or editorial statement on the live site
has a record, evidence assertion, site setting, or explicit exclusion reason.

### Step 4: enrich exact identifiers and create the review queue

Status: pending.

Deliverables:

- resolve exact ORCID, ROR, DOI, PMID/PMCID, repository, and award identifiers;
- import and incrementally synchronize the CON Zotero output feed;
- import official registry observations with retrieval metadata;
- propose, but do not auto-accept, ambiguous associations;
- report conflicts, stale claims, missing IDs, and unsupported claims.

Completion test: exact-ID facts are traceable and all uncertain matches are
visible to a reviewer.

### Step 5: build a multi-projection vertical slice

Status: pending.

Use one connected subset containing at least one person, project, grant,
software/dataset/publication output, facility/resource, and impact observation.

Generate:

- a person page;
- a project page;
- a project/contributor relationship view;
- a grant prior-work evidence packet;
- a facilities/resources draft;
- JSONL and graph exports;
- a staleness/unsupported-claim report;
- manifests identifying the inputs to each generated artifact.

Completion test: a single factual correction changes all relevant outputs and
does not require hand-editing generated prose or page metadata.

### Step 6: build the complete website projection

Status: pending.

Deliverables:

- information architecture based on modeled entities rather than legacy pages;
- Hugo/Jinja formatters and normalized view models;
- generated navigation, related-content links, search/graph data, and redirects;
- complete public content and assets;
- accessibility, responsive behavior, and deployment workflow.

Completion test: the generated site covers all approved live-site information
and provides useful model-driven discovery that the current site cannot.

### Step 7: add grant and reporting projections

Status: pending.

Prioritize:

- prior work and selected contributions;
- facilities and other resources;
- funding and output attribution;
- NIH biosketch support;
- NSF intellectual-merit and broader-impacts evidence;
- progress-report accomplishments and products;
- reusable bios and organization capability statements.

Completion test: each output is generated from accepted assertions, includes a
machine-readable manifest, and has an explicit human-review status.

### Step 8: governance and recurring maintenance

Status: pending.

Deliverables:

- review roles and pull-request rules;
- source-specific refresh schedules;
- conflict and correction workflow;
- archival rules for historical records;
- release/version policy for schemas and projections;
- scheduled Forgejo actions after manual runs are stable.

Completion test: updates are ordinary reviewed data changes, not periodic site
rewrites.

### Step 9: formal schema and `shacl-vue`

Status: later.

Deliverables:

- formal schema/profile derived from demonstrated record needs;
- JSON Schema and/or LinkML validation;
- RDF/JSON-LD and SHACL exports;
- `shacl-vue` forms for selected record classes;
- staging branch or incoming collection with review before canonical merge.

Completion test: nontechnical editing improves without creating a second,
conflicting source of truth.

## 13. Decision register and clarifications

These questions are intentionally recorded as work proceeds. Recommended
defaults allow Steps 2 and 3 to start without waiting on every answer.

| ID | Question | Recommended default | Blocking |
|---|---|---|---:|
| D1 | Approve `https://centerforopenneuroscience.org/id/` as the `con:` namespace? | Yes; retain old IDs as mappings | Yes for stable fixtures |
| D2 | Who may accept or reject candidate assertions? | Repository maintainers initially; add per-domain reviewers later | Yes before bulk enrichment merges |
| D3 | Where should confidential funded/unfunded proposal and report documents live? | Private sibling repository; public repo stores only permitted assertions and source pointers | Yes before private sources are ingested |
| D4 | Should each generated grant/report artifact carry an exact input manifest? | Yes | No |
| D5 | How strong must impact evidence be for grant-facing use? | Require a source and named reviewer; require a dated measure when the claim is quantitative | No |
| D6 | Preserve the public category label "Centroids"? | Preserve during migration; reconsider in the new website information architecture | No |
| D7 | Import the 39 collaborating projects/tools as full lightweight records? | Yes, with type, canonical URL, relationship to CON, and evidence | No |
| D8 | May agents rewrite current prose during migration? | Preserve original prose first; propose editorial revisions separately | No |
| D9 | Which first vertical slice? | DataLad first; DANDI second, as detailed in `con-source-inventory-and-first-slice.md` | Decided |
| D10 | Portable for other groups or CON-only? | Keep CON records local but make schema profiles, assertions, and projection templates portable | No |
| D11 | How should new publications and outputs enter the system? | Curate them in the CON Zotero group; scheduled ETL proposes reviewed YAML updates | Decided |
| D12 | Which repository should hold the initial authority and implementation? | Extend `con/dump-research-info` directly | Decided |
| D13 | Which Zotero collections are eligible? | Include all named collections except External; send unfiled items to review | Decided |

Published email addresses requested for migration can be retained with explicit
`visibility: public` and live-site provenance. Do not infer, scrape, or publish
additional personal contact information merely because it is discoverable.

## 14. Immediate next work product

After D1, D3, and D9 are settled, create the repository skeleton and the
connected fixture records from Step 2. That vertical slice should be kept small
enough to change the model cheaply, but rich enough to exercise evidence,
historical roles, grants, outputs, facilities, impact, website rendering, and a
grant-oriented projection.

No production service or `shacl-vue` deployment is needed before this slice
demonstrates that the model answers real CON questions.
