# CON canonical metadata

This directory is the initial Git-native authority for modeled Center for Open
Neuroscience information. It is deliberately independent of a running service.

## Boundaries

- One YAML file represents one canonical entity or contextual relationship.
- `records/` stores draft or accepted entities and relationships.
- `evidence/sources/` stores dated source observations and import policies.
- `evidence/assertions/` attaches evidence to individual claim paths.
- `schema/` describes the draft CON profile and controlled values.
- Derived joins, JSONL, graph data, pages, and prose must be generated outside
  this authority tree.
- The current profile is intentionally lightweight. It records demonstrated
  needs before a formal LinkML/SHACL schema is generated.

## Review states

Fixture records are `draft`, and gathered assertions are `proposed` unless a
specific conflict is recorded. This is not a claim that an agent can approve
CON roles, credit, funding relationships, or public narrative.

Assertions identify semantic predicates rather than JSON locations. Repeatable
properties use qualifiers such as an identifier scheme. Time intervals are
represented by separate start and end assertions so each value can have its
own source, confidence, and review state.

## Reproducible execution

- Pixi is the intended environment and task manager.
- External acquisition, normalization, enrichment, and projection commands
  should be recorded with `datalad run` and explicit inputs and outputs.
- Human edits to canonical YAML remain ordinary reviewed Git changes.
- Credentials, API keys, and private source material must never be recorded in
  DataLad command provenance or committed outputs.

## Zotero policy

The public CON Zotero group is the maintained intake source for research
outputs. The initial policy is:

- include `Articles`;
- include `Datasets`;
- include `Zenodo/OSF DOIs`;
- include `Software`;
- exclude `External` because it does not represent CON output;
- send unfiled items to review rather than public projections;
- classify by Zotero item type, not by collection name;
- merge exact identifier duplicates while preserving every Zotero observation;
- represent deletions as source tombstones, never automatic canonical deletes.

## First fixtures

The first connected slice models CON, Yaroslav Halchenko, DataLad and DataGit,
two NSF awards, the DataLad software, its JOSS publication, documentation, and
a data-distribution resource. DataLad is modeled as both a project and a linked
software product because their dates, participants, releases, licenses, and
funding semantics differ.

DANDI is the planned second slice.

## Known review items

- ROR identifies CON correctly but currently resolves its location to Hanover,
  Massachusetts; the CON site publishes Hanover, New Hampshire.
- Zotero contains two records for DataLad publication DOI
  `10.21105/joss.03262`.
- The BMBF DataLad awards still need issuing-agency observations.
- A maintainer policy for accepting assertions is not yet defined.
- Confidential grant and progress-report sources need a private storage policy.
