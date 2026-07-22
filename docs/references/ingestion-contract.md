# CON research-information ingestion contract

## Objective

Maintain reusable, modeled information about the Center for Open Neuroscience
(CON) in the repository's existing validated JSON format. Website pages, grant
material, reports, APIs, and linked-data exports are projections of these
records rather than separate sources of truth.

The target is not a pixel-for-pixel recreation of the current website. It is a
maintainable body of research information that can support a replacement site
and other CON work.

## Normative model and storage contract

The accepted record model is the
[research-information demonstrator](https://concepts.datalad.org/s/demo-research-information/unreleased/),
which imports the foundational [Things v2 schema](https://concepts.datalad.org/s/things/v2/).
The repository's configured record store points at the same schema.

The only reviewed ingestion targets are:

```text
data/<source_name>/<ClassName>.json
```

Each target file:

- is a JSON array;
- is named for an exact class exposed by the configured schema;
- contains only records validated as that class;
- is deterministically ordered to keep refresh diffs reviewable; and
- is accompanied by a source README describing retrieval and modeling.

The file name selects the top-level class for the REST endpoint. Nested values
use `schema_type` whenever the schema requires a concrete class. There is no
parallel CON-specific entity schema. New local schema work requires a
documented blocker in the upstream model first.

## Target classes

| Information | Target class | Main sources |
| --- | --- | --- |
| People | `XYZPerson` | current CON site, ORCID, project repositories |
| Organizations | `XYZOrganization` | current CON site, ROR, funders |
| Projects | `XYZProject` | current CON site, repositories, funder records |
| Grants and awards | `XYZGrant` | current CON site, NSF, NIH RePORTER |
| Scholarly outputs | `XYZPublication` | Zotero, Crossref, DataCite |
| Publication venues | `XYZPublicationVenue` | Zotero, Crossref |
| Datasets | `XYZDataset` | Zotero, DataCite, DANDI |
| Software and operational tools | `XYZInstrument` | Zotero, repositories, package registries |
| First-class documents that are not publications | `XYZDocument` | current CON site, Zotero after enrichment |
| Topics and classifications | `XYZTopic` and existing vocabulary classes | source tags plus reviewed vocabulary mappings |

Schema-native structure is preferred throughout:

- `about` connects records to topics;
- `associated_with` and `attributed_to` carry qualified agent relationships;
- `relations` plus `characterized_by` and `Statement` express other qualified
  Thing-to-Thing relationships;
- `attributes` carries values that do not have their own persistent identity;
- the imported PROV classes represent generation, derivation, revision, and
  other provenance when that provenance is part of the modeled information.

## Pipeline

1. **Acquire** a versioned source snapshot or API response. Record its URL,
   retrieval time, source version or ETag, and command.
2. **Normalize** source fields without deciding identity from display text.
3. **Classify** each item into an exact schema class and controlled `kind`.
4. **Reconcile** identifiers and duplicates across both the source and existing
   repository records.
5. **Render** deterministic candidate JSON arrays in a temporary location.
6. **Validate** every candidate against the configured dump-things-service
   collection and perform cross-reference checks.
7. **Review** the proposed diff, including additions, removals, conflicts, and
   low-confidence mappings.
8. **Promote** accepted arrays into `data/<source_name>/` and commit the source
   README and provenance together with them.
9. **Project** the accepted records into website pages and other products.

Pixi should pin the commands and dependencies. `datalad run` should record the
acquisition, transformation, and validation commands and their declared inputs
and outputs. Large or frequently refreshed raw snapshots can be annexed; they
must not become a second hand-edited metadata authority.

## Identity and reconciliation

Identity is global even though files are grouped by source. The same real-world
thing must not receive a source-specific `pid` in each directory.

Preferred persistent identifiers are:

- DOI URL for DOI-bearing publications, datasets, and software;
- ORCID URL for people;
- ROR URL for organizations;
- authoritative award URL for grants;
- authoritative archive or repository URL for projects, datasets, and software;
- stable source-item URL only when no stronger identifier exists.

DOIs are normalized by removing resolver prefixes and a leading `doi:`, then
lowercasing the DOI before constructing its canonical URL. Equivalent external
identifiers remain in `identifiers`. Titles and names are evidence for matching,
not identifiers by themselves.

Reconciliation order:

1. exact normalized persistent identifier;
2. exact source identifier already attached to a record;
3. high-confidence composite match appropriate to the class;
4. manual review.

The current CLI loads one source directory without merging it with others.
Cross-source merge or selection is therefore a required ingestion-stage step,
not behavior that can be assumed from the loader.

## Zotero policy

Source: [CON Zotero group library](https://www.zotero.org/groups/6197458/centerforopenneuroscience/library)

- Include `Articles`, `Datasets`, `Zenodo/OSF DOIs`, and `Software`.
- Exclude `External`.
- Send unfiled items to review rather than publishing them automatically.
- Collapse duplicate DOI items to one entity while retaining all Zotero item
  keys as source identifiers.
- Map publication-like item types to `XYZPublication` and an existing
  `XYZBibliographicType` value.
- Map datasets to `XYZDataset`.
- Map software to `XYZInstrument` with kind `obo:IAO_0000010` (`Software`).
- Classify generic Zotero `document` items using collection context and
  Crossref/DataCite resource type. Use `XYZDocument` only when the item is truly
  a document rather than a weakly typed publication, dataset, or software item.
- Preserve creator order and roles when the schema representation permits it;
  flag lossy cases for review.

The source-specific baseline and refresh notes are in
[`data/zotero_centerforopenneuroscience/README.md`](../../data/zotero_centerforopenneuroscience/README.md).

## Source sequence

1. Zotero publications, datasets, and software, because the library is curated
   and refreshable.
2. Current CON site, to capture all presently published people, organizations,
   projects, grants, descriptions, links, and images.
3. DataLad as the first end-to-end project slice, joining repository, grant,
   people, software, and publication records.
4. DANDI as the second slice, adding NIH and dataset-registry ingestion.
5. Remaining CON projects and external registries.

## Validation and review gates

A source refresh is ready to promote only when:

- each file parses as a JSON array;
- every record validates against the class named by the file;
- every referenced PID is either present in the target collection or supplied
  by the same reviewed load set;
- duplicate canonical identifiers are resolved;
- removals are explicitly explained rather than inferred from a transient
  source failure;
- source README and acquisition provenance are updated; and
- a person approves the resulting diff.

Future `shacl-vue` editing should operate against the same schema and produce
the same record shapes. It should not introduce a second authoring model.

## Open decisions and recommended defaults

1. **Schema pinning:** keep `unreleased` while matching the existing validator,
   but pin a resolved schema artifact before unattended refreshes begin.
2. **Raw snapshots:** store refresh inputs with DataLad/git-annex so records can
   be reproduced after upstream APIs change.
3. **Conflicts:** make refreshes propose diffs; never let an adapter silently
   replace a reviewed field. Resolve conflicts field by field during review.
4. **Ambiguous Zotero documents:** use registry metadata plus collection context,
   with manual review as the fallback.
5. **Cross-source loading:** add an explicit reconcile/build command before any
   command that loads all sources into one collection.

## References

- [DataLad Concepts: Things v2](https://concepts.datalad.org/s/things/v2/)
- [DataLad Concepts: research-information demonstrator](https://concepts.datalad.org/s/demo-research-information/unreleased/)
- [Resolved LinkML schema](https://concepts.datalad.org/s/demo-research-information/unreleased.yaml)
- [Orinoco dump-things-service](https://hub.psychoinformatics.de/orinoco/dump-things-service)
- [CON metadata issue #18](https://github.com/con/dump-research-info/issues/18)
- [TRR379 contributor/project workflow](https://github.com/con/dump-research-info/blob/HEAD/docs/references/trr379-contributors-projects-workflow.md)
- [Psychoinformatics VisiData demonstration](https://github.com/con/visidata-demos/tree/master/psychoinformatics-1)
- [CON Zotero library](https://www.zotero.org/groups/6197458/centerforopenneuroscience/library)
