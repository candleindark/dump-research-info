# con_site — Metadata from the Center for Open Neuroscience Website

## Source

Metadata was gathered from the official Center for Open Neuroscience (CON) website
and its source repository:

- **Website**: https://centerforopenneuroscience.org/
  - Pages scraped: main page (`/`), team page (`/whoweare`), projects page
    (`/projects`)
- **Source repository**: https://github.com/con/centerforopenneuroscience.org
  - Used to extract person identifiers (emails, GitHub usernames) from the
    HTML source

## Process

1. The dump-things-server was started locally and its OpenAPI schema was
   retrieved to understand all available data model classes and their field
   definitions.
2. Website content was fetched and parsed from the three main pages listed
   above.
3. Information was mapped to the most specific (lowest in the hierarchy) XYZ
   data model classes available.
4. Each record was validated against the dump-things-server's
   `/{collection}/validate/record/{class}` endpoint before being saved.
5. Records were subsequently refined: PIDs were remapped to use the
   `xyzrins:` namespace, controlled-vocabulary pool records were
   deduplicated, and additional metadata (GitHub usernames, emails, roles,
   new persons and publications) was added.

## Result

| File                       | Class               | Records | Content                                                 |
|----------------------------|---------------------|---------|---------------------------------------------------------|
| `XYZOrganization.json`     | XYZOrganization     | 8       | CON and affiliated institutions                         |
| `XYZPerson.json`           | XYZPerson           | 33      | Centroids, collaborators, affiliated faculty, emeritus  |
| `XYZProject.json`          | XYZProject          | 22      | Software, standards, initiatives, education, community  |
| `XYZGrant.json`            | XYZGrant            | 3       | NIH grants (DANDI, EMBER, OpenNeuro)                    |
| `XYZPublication.json`      | XYZPublication      | 11      | Referenced papers (with DOIs or canonical URLs)         |
| `XYZPublicationVenue.json` | XYZPublicationVenue | 2       | Journals not already covered by the pool                |

**Total: 79 records.**

## Pool Deduplication

Records that are already present in
`data/pool_psychoinformatics_de/XYZPublicationVenue.json` are **not**
duplicated here. Those venues are referenced by their pool PIDs when needed.
The following 7 venues were removed from `data/con_site/` after the pool data
was added:

| Title                          | Pool PID         |
|--------------------------------|------------------|
| Frontiers in Neuroinformatics  | `ISSN:1662-5196` |
| Journal of Open Source Software| `ISSN:2475-9066` |
| Neuroinformatics               | `ISSN:1539-2791` |
| Scientific Data                | `ISSN:2052-4463` |
| Human Brain Mapping            | `ISSN:1065-9471` |
| F1000Research                  | `ISSN:2046-1402` |
| Cerebral Cortex                | `ISSN:1047-3211` |

Only two venues remain in `data/con_site/` because they are not in the pool:
Annual Review of Neuroscience and Journal of Machine Learning Research.

## Strategies and Decisions

### PID assignment

Every record requires a `pid` (persistent, globally unique identifier). The
strategy varied by class:

- **XYZOrganization**: [ROR](https://ror.org/) CURIEs (e.g. `ror:04tfhh831`
  for CON). Harvard Medical School has no ROR entry; it uses
  `xyzrins:organizations/hms`.
- **XYZPerson**: `xyzrins:persons/<given-name>-<family-name>` (lowercase,
  hyphen-separated). The former GitHub profile URL PID is now recorded as an
  `identifiers` entry with `creator: rrid:SCR_002630`.
- **XYZProject**: `xyzrins:projects/<short-name>` (lowercase, hyphens). The
  project homepage URL is stored in an `attributes` entry with
  `predicate: foaf:homepage`.
- **XYZGrant**: `xyzrins:grants/<short-name>`. The NIH Reporter URL is stored
  in an `attributes` entry with `predicate: foaf:homepage`. Only one of the
  three grants (DANDI) had a confirmed real NIH Reporter URL; the other two use
  placeholder search paths (see Known Issues).
- **XYZPublication**: DOI URLs (e.g.
  `https://doi.org/10.3389/fninf.2012.00022`). The HyperTools paper has no DOI;
  its canonical JMLR URL is used as `pid`.
- **XYZPublicationVenue**: ISSN-based PIDs (e.g. `ISSN:0147-006X`).

### Class selection

- XYZ subclasses were preferred over base classes throughout, per the schema
  instructions (e.g. `XYZPerson` over `Person`, `XYZProject` over `Project`).
- Software projects, data standards, initiatives, educational modules, and
  community events listed on the `/projects` page were all stored as
  `XYZProject`, since the website presents them uniformly and they all fit the
  project model.
- `distribits` (a community conference) was stored as `XYZProject` rather than
  `XYZActivity` because the website describes it as an ongoing community
  (project) rather than a single event.

### Location encoding

- The schema requires `at_location` to be a valid URI, not free text. The
  Wikidata entity URI for Hanover, NH
  (`https://www.wikidata.org/entity/Q131908`) was used for CON and Dartmouth
  College.

### Person coverage

All persons listed on the `/whoweare` page were included across all sections:
centroids (6), collaborators (7), affiliated faculty (4), and emeritus (14).
Two additional persons not listed on `/whoweare` were added because they are
PIs of CON-affiliated grants or archives:

- **Russell Poldrack** (`xyzrins:persons/russell-poldrack`): PI of the
  OpenNeuro archive (Stanford University).
- **Brock Wester** (`xyzrins:persons/brock-wester`): PI of the EMBER archive
  (Johns Hopkins University Applied Physics Laboratory).

Descriptions were derived from the biographical blurbs on the website.

### Person identifiers and contact information

- **GitHub usernames** are recorded as `identifiers` entries with
  `creator: rrid:SCR_002630` and `schema_type: dlthings:Identifier`.
- **ORCID identifiers** are recorded as `identifiers` entries with
  `creator: ror:04fa4r544` and `schema_type: xyzri:ORCID`. ORCIDs were only
  added for persons where they were explicitly available (Russell Poldrack,
  Brock Wester); they were not looked up externally for existing members.
- **Email addresses** are recorded as `attributes` entries with
  `predicate: vcard:Email` and `schema_type: dlthings:AttributeSpecification`.
  Emails were extracted from the CON website source repository. Four members
  (franco-pestilli, vanessa-sochat, nikolaas-oosterhof, benjamin-poldrack) do
  not have emails listed on the website.

### Grant coverage

Only three grants with explicit grant numbers were identified on the
`/projects` page (DANDI, EMBER, OpenNeuro). The website mentions additional
funding sources (NSF, German BMBF for DataLad; NIH ReproNim for ReproMan and
HeuDiConv) but without specific grant numbers, so these were not included.

### Publication coverage

Eleven publications are included: nine identified from explicit references on
the website, plus two added during refinement:

- **HyperTools** ("Heusser et al. 2018 JMLR"): published in JMLR, vol. 18.
  No DOI available; canonical JMLR URL used as `pid`.
- **SuperEEG** ("Owen et al. 2020 Cerebral Cortex"):
  `https://doi.org/10.1093/cercor/bhaa115`.

### Inter-record relationships

Relationships between records were populated using PROV-O-based fields where
the `object` property references another record's PID:

- **XYZOrganization `part_of`**: CON is part of Dartmouth College (stated on
  the website).
- **XYZProject `associated_with`**: Projects were linked to persons explicitly
  named on the `/projects` and `/whoweare` pages. Each entry includes
  `schema_type: dlthings:Association` and a `roles` array using pool PIDs from
  `XYZAgentRole`:
  - `obo:NCIT_C19924` (PI) for explicitly named PIs.
  - `marcrel:led` (Lead) for project creators and leads.
  - `marcrel:cre` (Creator) for co-developers of smaller tools.
  - `marcrel:ctb` (Contributor) for named contributors.
  - `marcrel:rtm` (Research team member) for Co-Is.
  17 of 22 projects have at least one association. Projects without named
  contributors on the website (con/duct, con/tinuous, pyout, NWB, distribits)
  have none.
- **XYZPublication `attributed_to`**: Publications were linked to their authors
  where those authors have records in `XYZPerson.json`. Each entry includes
  `schema_type: dlthings:Attribution` and a `roles` array: `obo:MS_1002034`
  (first author), `obo:MS_1002035` (senior author), or `obo:MS_1002036`
  (co-author), assigned based on author-order information visible from the CON
  website. All 11 publications have at least one attribution.
- **XYZGrant `attributed_to`**: Grants were linked to PIs and Co-Is named on
  the `/projects` page. Each entry includes `schema_type: dlthings:Attribution`
  and `roles`: `obo:NCIT_C19924` (PI) or `marcrel:rtm` (Co-I).

## Known Issues

- **No ROR ID for Harvard Medical School**: Harvard Medical School does not
  appear to have a ROR entry. The identifier `xyzrins:organizations/hms` is
  used instead.
- **Placeholder grant PIDs for EMBER and OpenNeuro**: The `attributes`
  homepage URLs for the EMBER and OpenNeuro grants use fabricated NIH Reporter
  search paths (`x1x1x1x1x1`, `x2x2x2x2x2`) because the actual NIH Reporter
  URLs were not confirmed. These should be replaced with the real NIH Reporter
  project detail URLs.
- **Partial ORCID coverage**: ORCID identifiers are only present for Russell
  Poldrack and Brock Wester. Other persons' ORCIDs were not looked up from
  external sources.
