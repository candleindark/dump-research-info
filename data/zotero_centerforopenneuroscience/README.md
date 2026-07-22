# Center for Open Neuroscience Zotero library

## Source

- Library: https://www.zotero.org/groups/6197458/centerforopenneuroscience/library
- Zotero group ID: `6197458`
- API root: https://api.zotero.org/groups/6197458
- Access: public, read-only ingestion

This directory is reserved for validated JSON arrays generated from the CON
Zotero group. It does not yet contain promoted records.

## Inclusion policy

Include items assigned to these collections:

- `Articles`
- `Datasets`
- `Zenodo/OSF DOIs`
- `Software`

Exclude `External`. Treat unfiled items as review candidates rather than
automatic additions. Attachments and notes are supporting source material, not
independent research-information records unless a reviewer promotes one as a
first-class document.

## Baseline inventory

The public API was inspected on 2026-07-22 at library version `216`:

- 193 active top-level items;
- 244 active records including 38 attachments and 13 notes;
- 9 deleted records reported by the API;
- 128 top-level items in `Articles`;
- 49 in excluded `External`;
- 4 in `Datasets`;
- 3 in `Zenodo/OSF DOIs`;
- 0 in `Software`; and
- 9 unfiled top-level items.

The baseline contains eight normalized DOI collision groups spanning 17 items.
An importer must reconcile these before emitting target arrays.

## Target mapping

| Zotero information | Target |
| --- | --- |
| Journal article, conference paper, preprint, book section, report, thesis | `XYZPublication.json` |
| Dataset or registry-classified dataset | `XYZDataset.json` |
| Computer program or registry-classified software | `XYZInstrument.json`, kind `obo:IAO_0000010` |
| Genuinely generic document | `XYZDocument.json` |
| Publication venue referenced by accepted publications | `XYZPublicationVenue.json` |
| Creators not already represented | `XYZPerson.json` or `XYZOrganization.json` after reconciliation |

Generic Zotero `document` items require enrichment from Crossref or DataCite
and collection context before class assignment.

## Refresh contract

The planned adapter will:

1. fetch collection and item data with Zotero API version headers recorded;
2. exclude deleted, child, and `External` records from automatic publication;
3. normalize DOI, ISBN, PMID, PMCID, ORCID, and URL identifiers;
4. enrich DOI records with Crossref or DataCite where needed for classification;
5. reconcile against existing records by canonical identifier;
6. render stable, sorted candidate arrays;
7. validate candidates against the configured research-information collection;
8. present additions, changes, removals, collisions, and uncertain mappings for
   human review; and
9. update this directory only after approval.

Acquisition and transformation should run through Pixi and be recorded with
`datalad run`. Zotero item keys and the library version must remain available as
source identifiers/provenance even when a DOI becomes the entity `pid`.
