# CON source inventory and first vertical slice

Status: research snapshot and implementation recommendation  
Observed: 2026-07-22

This document executes the inventory/enrichment planning step from
`con-research-information-architecture.md`. It records what is currently
available, what can be imported automatically, what conflicts need review, and
which connected records should drive the first implementation slice.

## 1. Recommendation

Use **DataLad** for the first vertical slice:

```text
Center for Open Neuroscience
  -> Yaroslav O. Halchenko
  -> DataLad project
  -> DataLad software and resources
  -> NSF 1429999 and NSF 1912266
  -> DataLad JOSS publication
  -> dated evidence and impact observations
```

Use **DANDI** as the second slice. DANDI has a particularly clean NIH award
edge, but DataLad exercises more of the intended model at once: historical and
current funding, multiple organizations, project versus software identity,
publication ingestion, a data-distribution resource, contributor
relationships, prior-work reporting, and impact evidence.

## 2. Source inventory

### 2.1 Existing `con/dump-research-info` corpus

The repository currently exposes generated JSON collections under
`data/con_site`, not one authoritative YAML file per record. Its curated
record directory contains configuration but no curated records yet.

Current CON record counts:

| Record collection | Count |
|---|---:|
| Organizations | 8 |
| People | 33 |
| Projects | 22 |
| Grants | 3 |
| Publications | 11 |
| Publication venues | 2 |
| **Total** | **79** |

Useful source files:

- [organizations](https://raw.githubusercontent.com/con/dump-research-info/main/data/con_site/XYZOrganization.json)
- [people](https://raw.githubusercontent.com/con/dump-research-info/main/data/con_site/XYZPerson.json)
- [projects](https://raw.githubusercontent.com/con/dump-research-info/main/data/con_site/XYZProject.json)
- [grants](https://raw.githubusercontent.com/con/dump-research-info/main/data/con_site/XYZGrant.json)
- [publications](https://raw.githubusercontent.com/con/dump-research-info/main/data/con_site/XYZPublication.json)

Observed structural limitations:

- File membership supplies the record class; individual records generally do
  not declare `schema_type`.
- Many project and grant records lack dates and status.
- Relationships are present, but their evidence, validity, and review state
  are not represented.
- Published site URLs are commonly stored in `about`, but the page location is
  not sufficient claim-level provenance.
- Local `xyzrins:` identifiers need stable CON mappings.
- The 11 publication records are a small selected set rather than the complete
  publication/output inventory.

### 2.2 Current live website

The [live CON site](https://centerforopenneuroscience.org/) remains the source
for editorial descriptions, role labels, contact links, grouping, principles,
featured ordering, images, support acknowledgements, and other presentation
content.

Previously inventoried live content includes:

- 6 principles;
- 33 person profiles and portraits;
- 22 featured projects/resources spanning several entity types;
- 39 collaborating projects/tools and 2 partner organizations;
- engagement resources and banners;
- NSF, NIH, and CCN support references;
- homepage references and testimonial material.

This content should be preserved as dated observations before editorial or
structural changes are proposed.

### 2.3 CON Zotero group

The [Center for Open Neuroscience Zotero group](https://www.zotero.org/groups/6197458/centerforopenneuroscience/library)
is public and can be read without an API key.

Snapshot:

| Metric | Count/value |
|---|---:|
| Group item count, including deleted records | 253 |
| Active records | 244 |
| Active top-level records | 193 |
| Active child attachments | 38 |
| Active child notes | 13 |
| Deleted top-level records | 8 |
| Deleted child attachments | 1 |
| Collections | 5 |
| `Last-Modified-Version` watermark | 216 |

The [top-level items API](https://api.zotero.org/groups/6197458/items/top?format=json&limit=100)
provides the candidate output records. The [all-items API](https://api.zotero.org/groups/6197458/items?format=json&limit=100)
also includes notes and attachments.

#### Item types

| Zotero type | Count | Proposed CON class |
|---|---:|---|
| `journalArticle` | 119 | Publication |
| `document` | 44 | Document, pending subtype review |
| `conferencePaper` | 11 | Publication |
| `preprint` | 5 | Publication |
| `bookSection` | 4 | Publication |
| `computerProgram` | 4 | Software |
| `dataset` | 4 | Dataset |
| `report` | 1 | Publication/report |
| `thesis` | 1 | Publication/thesis |
| **Total** | **193** | |

Type-first classification yields 141 publications, 44 documents, 4 software
records, and 4 datasets. Zotero collections should remain secondary curation
metadata rather than determine the entity class.

#### Collections

Every active top-level item is in exactly one collection or is unfiled.

| Collection | Count |
|---|---:|
| Articles | 128 |
| External | 49 |
| Datasets | 4 |
| Zenodo/OSF DOIs | 3 |
| Software | 0 |
| Unfiled | 9 |

The empty Software collection despite four `computerProgram` records, and the
meaning of External versus Articles, need curation-policy clarification.

#### Identifier and date coverage

| Identifier field | Count | Coverage |
|---|---:|---:|
| DOI | 141 | 73.06% |
| URL | 139 | 72.02% |
| ISBN | 5 | 2.59% |
| PMID | 4 | 2.07% |
| PMCID | 2 | 1.04% |

All top-level records have a parseable four-digit year. Dates range from 1992
through 2026: 6 records from the 1990s, 14 from the 2000s, 79 from the 2010s,
and 94 from 2020 through 2026.

#### Duplicate and review findings

There are eight duplicate DOI groups containing 17 Zotero records:

| DOI | Zotero keys |
|---|---|
| `10.1038/s41597-025-05543-2` | `7PWG497Y`, `VYEFN2PE` |
| `10.1038/sdata.2016.44` | `4IBTF6HG`, `9KS9CGNB` |
| `10.1101/2021.02.25.21252472` | `VWFN4ZUS`, `NTH9GIBW` |
| `10.1145/3701716.3715483` | `EJV44RBA`, `FURW46DX`, `V2CAAUMU` |
| `10.21105/joss.03262` | `M7WZZRWV`, `H8IFRMC4` |
| `10.21105/joss.05839` | `XHF43I5N`, `W9MC83Q7` |
| `10.3389/fninf.2024.1376022` | `5IQ9JI6W`, `W5M5BMYG` |
| `10.48550/arxiv.2309.05768` | `65GF4WEG`, `A8MQ2A7G` |

There are also 15 normalized-title collision groups. Some are duplicates;
others may be legitimate relationships such as preprint/published work or
article/dataset pairs. DOI equality can be merged automatically into one
candidate entity with multiple source observations. Title-only collisions
require review.

The importer must tolerate duplicate and deleted source records even if the
Zotero library is later cleaned.

### 2.4 Authoritative registries and project sources

Use Zotero to determine that an output is curated for CON. Use issuing
registries for identifier-bound bibliographic facts and funding agencies for
award facts.

Primary sources for the first slice:

- [ROR record `04tfhh831`](https://ror.org/04tfhh831)
- [CON people page](https://centerforopenneuroscience.org/whoweare)
- [CON projects page](https://centerforopenneuroscience.org/projects)
- [DataLad project information](https://project.datalad.org/)
- [DataLad funding acknowledgements](https://handbook.datalad.org/en/latest/acknowledgements.html)
- [NSF award `1912266`](https://www.nsf.gov/awardsearch/showAward?AWD_ID=1912266)
- [NSF award `1429999`](https://www.nsf.gov/awardsearch/showAward?AWD_ID=1429999)
- [DataLad JOSS article](https://doi.org/10.21105/joss.03262)
- [Zotero item `M7WZZRWV`](https://api.zotero.org/groups/6197458/items/M7WZZRWV?v=3)
- [Zotero item `H8IFRMC4`](https://api.zotero.org/groups/6197458/items/H8IFRMC4?v=3)

## 3. Verified first-slice facts

### Organization

The ROR API identifies [`https://ror.org/04tfhh831`](https://ror.org/04tfhh831)
as the active facility **Center for Open Neuroscience**, acronym **CON**, with
the CON website and a `related` relationship to Dartmouth College
(`ror:049s0rh22`). This validates the identifier used by the seed corpus.

There is a source conflict: the ROR record currently resolves its location to
Hanover, Massachusetts, while CON's public address is in Hanover, New
Hampshire. Preserve both observations, use the intentionally published CON
address for the canonical public record, and submit or request a ROR correction
separately.

### Person

The seed corpus and live site identify Yaroslav O. Halchenko as CON's Founding
Director and a DataLad lead.

Identifiers:

- proposed local ID: `con:person/yaroslav-halchenko`;
- legacy ID: `xyzrins:persons/yaroslav-halchenko`;
- ORCID: [`0000-0003-3456-2493`](https://orcid.org/0000-0003-3456-2493);
- GitHub: [`yarikoptic`](https://github.com/yarikoptic).

### DataLad project and software

The seed corpus identifies `xyzrins:projects/datalad` and associates Halchenko
with a lead role. The live CON site and DataLad project site describe DataLad as
a CON-associated project with collaboration involving Forschungszentrum
Jülich.

Model DataLad as two linked entities:

- `con:project/datalad`: the funded development, collaboration, and community
  endeavor;
- `con:software/datalad`: the versioned software product produced by that
  endeavor.

This avoids forcing grant periods, project participants, software versions,
licenses, and release identifiers onto one overloaded record.

### NSF funding

The official NSF API reports:

| Award | Recipient | PI | Period | Obligated amount | Relationship |
|---|---|---|---|---:|---|
| `1912266` | Dartmouth College | Yaroslav Halchenko | 2019-12-01 to 2023-11-30 | USD 649,643 | Explicit DataLad proposal |
| `1429999` | Dartmouth College | Yaroslav Halchenko | 2014-09-01 to 2018-08-31 | USD 690,400 | DataGit predecessor leading to DataLad |

The corresponding BMBF awards `01GQ1905` and `01GQ1411` are documented by
DataLad's acknowledgements. Their official recipient, amount, and period should
remain candidate assertions until verified from an issuing-agency source.

The correct graph is not "CON received the NSF awards." It is:

```text
NSF award -> awarded to Dartmouth College
NSF award -> PI Yaroslav Halchenko
NSF award -> supports DataLad/DataGit project
Yaroslav Halchenko -> has role in CON
DataLad -> associated with CON
```

### Publication

Crossref resolves [`10.21105/joss.03262`](https://doi.org/10.21105/joss.03262)
to **DataLad: distributed system for joint management of code, data, and their
relationship**, published 2021-07-01. Crossref also supplies ORCIDs for many
authors, including Halchenko.

The Zotero group contains two duplicate observations for this DOI:
`M7WZZRWV` and `H8IFRMC4`. The ETL should create one canonical publication
candidate linked to both evidence observations. Crossref returns no work for
`10.21105/joss.03834`; any DataLad page presenting that value should be treated
as a source typo, not as a second publication.

### Resource and impact evidence

Candidate resource records include:

- the DataLad software repositories and releases;
- `datasets.datalad.org` as a data-distribution resource;
- DataLad documentation and handbook as educational/document outputs;
- RRID records where verified;
- dated usage, catalog-size, release, citation, and adoption observations.

Do not store changing scale statements as timeless descriptions. Represent
counts, versions, and adoption claims as dated measurements with sources.

The Dartmouth Brain Imaging Center is a plausible facility record, but its
strongest documented chain is indirect through ReproIn/HeuDiConv and BIDS
DataLad datasets. Keep DBIC out of the first canonical DataLad claim graph
unless a human confirms the direct relationship; it can still be represented
as a separate CON facility in the wider corpus.

## 4. Proposed fixture records

The first repository fixture should contain at least:

```text
metadata/records/organizations/center-for-open-neuroscience.yaml
metadata/records/organizations/dartmouth-college.yaml
metadata/records/organizations/forschungszentrum-juelich.yaml
metadata/records/people/yaroslav-halchenko.yaml
metadata/records/projects/datalad.yaml
metadata/records/projects/datagit.yaml
metadata/records/software/datalad.yaml
metadata/records/grants/nsf-1912266.yaml
metadata/records/grants/nsf-1429999.yaml
metadata/records/publications/doi-10.21105-joss.03262.yaml
metadata/records/resources/datasets-datalad-org.yaml
metadata/records/documents/datalad-handbook.yaml
metadata/records/relationships/*.yaml
metadata/evidence/sources/*.yaml
metadata/evidence/assertions/*.yaml
```

BMBF awards should be added as provisional records only if the profile supports
`review_status: candidate`; otherwise defer them until official lookup is
complete.

## 5. Required projection tests

One correction to any fixture record must propagate to all relevant outputs.

Generate:

1. A CON organization page showing DataLad as an associated endeavor, not as an
   owned legal unit.
2. A person page showing Halchenko's current CON role separately from dated
   award/project roles.
3. A DataLad project page that links funding, people, organizations, software,
   publications, documentation, and resources.
4. A software page that can carry releases, license, repositories, citation,
   and current version independently of the project.
5. An NSF prior-support evidence packet based on awards `1429999` and
   `1912266`.
6. A publication view sourced from one canonical DOI record despite two Zotero
   observations.
7. A provenance view showing the live site, Zotero, Crossref, NSF, ROR, and
   DataLad sources behind each accepted claim.
8. A maintenance report showing the ROR location conflict, Zotero duplicate,
   unverified BMBF fields, and stale/undated claims.
9. Normalized JSONL and graph exports with no presentation-only `x_*` fields in
   the canonical YAML.

## 6. Zotero ETL contract

### Initial import

1. Fetch all pages of `/items/top` and `/collections` using API version 3.
2. Optionally fetch `/items` to preserve notes and attachment relationships.
3. Store raw source observations with group ID, item key, item version,
   collection membership, retrieval time, and source-library version.
4. Classify by Zotero item type, then apply collection-based inclusion rules.
5. Normalize persistent identifiers.
6. Collapse exact identifier matches into one candidate entity while preserving
   every source observation.
7. Send title-only matches, author identity matches, preprint/version relations,
   and CON-credit claims to review.

### Incremental maintenance

For a committed watermark `v`, use Zotero's version endpoints and `since=v`.
Fetch changed keys and upsert only newer object versions. Advance the watermark
only after every page, observation, candidate, and tombstone is durably
committed.

Deletion rules:

- A Zotero item with `deleted: 1` creates a source tombstone.
- The item leaves current Zotero-derived projections.
- Its canonical CON record is not deleted automatically.
- A reviewer decides whether the CON entity is archived, retained from other
  evidence, or removed from public projections.

The implementation should follow Zotero's [syncing guide](https://www.zotero.org/support/dev/web_api/v3/syncing)
and [pagination/version behavior](https://www.zotero.org/support/dev/web_api/v3/basics).

## 7. Review queue

### Source conflicts

- ROR location says Hanover, Massachusetts; the live CON address says Hanover,
  New Hampshire.
- One secondary DataLad resource page reports the invalid DOI
  `10.21105/joss.03834`; Crossref and JOSS support `10.21105/joss.03262`.

### Zotero curation

- Resolve eight duplicate DOI groups.
- Review seven or more title collisions that may represent versions or related
  output types rather than duplicates.
- Clarify the meaning of Articles and External.
- Classify 44 generic `document` items.
- Classify 9 unfiled items.
- Decide whether to populate the empty Software collection.
- Preserve nine source tombstones.

### Model/review decisions

- DataLad is the first slice and DANDI is the second.
- The draft uses the `con:` identifier namespace.
- DataLad's project and software are separate linked entities.
- NSF awards are attributed to Dartmouth, with CON represented through
  project/person associations rather than as recipient.
- Zotero's External collection is excluded; all named collections are eligible,
  and unfiled items enter review.
- Select the maintainers who may promote candidate assertions to accepted.
- Decide where confidential grant and progress-report source documents live.

## 8. DANDI second slice

DANDI should follow immediately because it tests a different shape:

```text
CON and participating organizations
  -> Yaroslav Halchenko and Satrajit Ghosh
  -> DANDI platform/archive
  -> NIH R24MH117295
  -> DANDI software, datasets, standards, and documentation
  -> dated archive-scale and reuse observations
```

Authoritative evidence already supports NIH award `R24MH117295`, with a period
of performance from 2019-08-01 through 2029-04-30, and the DANDI site identifies
the BRAIN Initiative and AWS Open Data support. See the [HHS TAGGS award
record](https://taggs.hhs.gov/Detail/AwardDetail?arg_AwardNum=R24MH117295&arg_ProgOfficeCode=134),
[DANDI project site](https://about.dandiarchive.org/), and [DANDI
documentation](https://docs.dandiarchive.org/introduction/).

This second slice will test an active award, a service/platform, large numbers
of versioned datasets, standards such as NWB and BIDS, infrastructure support,
and time-varying impact evidence.

## 9. Immediate next action

Create the repository skeleton and these DataLad fixture records in
`con/dump-research-info`. The fixtures must be real records with real evidence,
not illustrative placeholders. Only after the connected graph validates should
the remaining 79 seed records and eligible Zotero items be migrated in bulk.
