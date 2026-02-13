# con_site — Metadata from the Center for Open Neuroscience Website

## Source

Metadata was gathered from the official Center for Open Neuroscience (CON) website
and its source repository:

- **Website**: https://centerforopenneuroscience.org/
  - Pages scraped: main page (`/`), team page (`/whoweare`), projects page (`/projects`)
- **Source repository**: https://github.com/con/centerforopenneuroscience.org
  - Used to extract person identifiers (emails, GitHub usernames) from the HTML source

## Process

1. The dump-things-server was started locally and its OpenAPI schema was retrieved
   to understand all available data model classes and their field definitions.
2. Website content was fetched and parsed from the three main pages listed above.
3. Information was mapped to the most specific (lowest in the hierarchy) XYZ data
   model classes available.
4. Each record was validated against the dump-things-server's
   `/{collection}/validate/record/{class}` endpoint before being saved.
5. All 81 records passed validation with no discards.

## Result

| File                      | Class               | Records | Content                                                  |
|---------------------------|---------------------|---------|----------------------------------------------------------|
| `XYZOrganization.json`    | XYZOrganization     | 8       | CON and affiliated institutions                          |
| `XYZPerson.json`          | XYZPerson           | 31      | Centroids, collaborators, affiliated faculty, emeritus   |
| `XYZProject.json`         | XYZProject          | 22      | Software, standards, initiatives, education, community   |
| `XYZGrant.json`           | XYZGrant            | 3       | NIH grants (DANDI, EMBER, OpenNeuro)                     |
| `XYZPublication.json`     | XYZPublication      | 9       | Referenced papers (with DOIs)                            |
| `XYZPublicationVenue.json`| XYZPublicationVenue | 8       | Journals where CON-related work is published             |

## Strategies and Decisions

### PID assignment

Every record requires a `pid` (persistent, globally unique identifier). The
strategy varied by class:

- **XYZOrganization**: [ROR](https://ror.org/) identifiers (e.g.
  `https://ror.org/04tfhh831` for CON).
- **XYZPerson**: GitHub profile URLs (e.g. `https://github.com/yarikoptic`).
  ORCID identifiers were not listed on the website and were not looked up
  externally, so GitHub URLs were used as the most authoritative persistent
  identifier available from the source.
- **XYZProject**: Project homepage URLs (e.g. `https://datalad.org`,
  `https://github.com/con/duct`).
- **XYZGrant**: NIH Reporter URLs. Only one of the three (the DANDI grant) had a
  known real NIH Reporter URL; the other two use placeholder search paths (see
  known issues below).
- **XYZPublication**: DOI URLs (e.g. `https://doi.org/10.3389/fninf.2012.00022`).
- **XYZPublicationVenue**: Journal homepage URLs.

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

- The schema requires `at_location` to be a valid URI, not free text.
  The Wikidata entity URI for Hanover, NH (`https://www.wikidata.org/entity/Q131908`)
  was used for CON and Dartmouth College.

### Person coverage

All persons listed on the `/whoweare` page were included across all sections:
centroids (6), collaborators (7), affiliated faculty (4), and emeritus (14).
Descriptions were derived from the biographical blurbs on the website.

### Grant coverage

Only three grants with explicit grant numbers were identified on the
`/projects` page (DANDI, EMBER, OpenNeuro). The website mentions additional
funding sources (NSF, German BMBF for DataLad; NIH ReproNim for ReproMan and
HeuDiConv) but without specific grant numbers, so these were not included.

### Publication coverage

Nine publications were identified from explicit references on the website
(main page and project descriptions). All had DOIs which were used as both
`pid` and in the `identifiers` array.

### Inter-record relationships

Relationships between records were populated using PROV-O-based fields where
the `object` property references another record's PID:

- **XYZOrganization `part_of`**: CON is part of Dartmouth College (stated on
  the website).
- **XYZProject `associated_with`**: Projects were linked to persons explicitly
  named on the `/projects` and `/whoweare` pages (e.g., DataLad lists Hanke,
  Visconti di Oleggio Castello, Meyer, Poldrack, and Halchenko). 17 of 22
  projects have at least one association. Projects without named contributors
  on the website (con/duct, con/tinuous, pyout, NWB, distribits) have none.
- **XYZPublication `attributed_to`**: Publications were linked to their authors
  where those authors have records in `XYZPerson.json`. Only authors explicitly
  named on the website were included. All 9 publications have at least one
  attribution.
- **XYZGrant `attributed_to`**: Grants were linked to PIs and Co-Is named on
  the `/projects` page. Roles (PI, Co-I) are not included in the `attributed_to`
  objects because the `roles` field requires URIs/CURIEs rather than plain
  strings.

## Known Issues

- **No ROR ID for Harvard Medical School**: Harvard Medical School does not
  appear to have a ROR entry. Its homepage URL (`https://hms.harvard.edu`) is
  used as the PID instead of a ROR ID.
- **Placeholder grant PIDs**: The EMBER and OpenNeuro grant PIDs use fabricated
  NIH Reporter search paths (`x1x1x1x1x1`, `x2x2x2x2x2`) because the actual
  NIH Reporter URLs were not looked up. These should be replaced with the real
  NIH Reporter project detail URLs.
- **No ORCID identifiers**: Person records use GitHub profile URLs as PIDs.
  These could be enriched with ORCID identifiers (in the `identifiers` field)
  if looked up from an external source.
