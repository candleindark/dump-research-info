Gather metadata from: $ARGUMENTS

## Goal
Gather metadata from the source specified by the provided arguments.

## Reference materials

Before starting, familiarise yourself with the following reference sources:

1. **Reference JSONL** — fetch and inspect
   `https://raw.githubusercontent.com/con/visidata-demos/refs/heads/master/psychoinformatics-1/data.jsonl`
   early to understand correct field-formatting patterns used in real records.

2. **Pool controlled vocabulary** — read the files in `data/pool_psychoinformatics_de/`
   before writing any record. The pool contains authoritative controlled-vocabulary
   records (roles, topics, qualities, bibliographic types, etc.) and records for
   entities (venues, instruments, …) that may already exist. Use pool PIDs when
   referencing these entities rather than creating duplicates.

## Context and requirements

### Data model
The gathered metadata must conform to the data models (classes) defined in or
referenced by the
[demo-research-information-schema](https://concepts.datalad.org/s/demo-research-information/unreleased.yaml).
The classes are also described by the OpenAPI documentation of the running
dump-things-server instance at `http://localhost:8111/openapi.json`.

### General notes
- Gathered metadata must be constructed from information obtained from the
  provided source. If a piece of metadata is derived from an AI system's
  memory (e.g., a PID or an ORCID), it must be verified against an
  authoritative external source before use.
- Prefer subclass records over superclass records. For example, use `XYZPerson`
  rather than `Person`, and `XYZProject` rather than `Project`.
- When relationships between entities can be identified from the source (a person
  is associated with a project, a publication is attributed to a person, an
  organisation is part of another), capture them using the appropriate fields
  (`associated_with`, `attributed_to`, `part_of`). The `object` property must
  reference the `pid` of the related record.

### Pool deduplication
Before creating a record for any entity, check whether a record with the same
identity already exists in `data/pool_psychoinformatics_de/`. If it does, **do
not create a duplicate** — reference the pool record's `pid` in relationship
fields instead. Classes most likely to overlap with the pool: `XYZPublicationVenue`,
`XYZAgentRole`, `XYZBibliographicType`, `XYZTopic`, `XYZQuality`, `Rule`,
`Property`, `AnnotationTag`, `XYZEntityRole`, `XYZInstrumentType`.

### PID assignment conventions
Assign PIDs according to the following class-specific rules:

| Class | PID format |
|---|---|
| `XYZPerson` | `xyzrins:persons/<given>-<family>` (all lowercase, hyphen-separated) |
| `XYZOrganization` | `ror:<id>` CURIE when a ROR entry exists; otherwise `xyzrins:organizations/<short-name>` |
| `XYZProject` | `xyzrins:projects/<short-name>` (lowercase, hyphens) |
| `XYZGrant` | `xyzrins:grants/<short-name>` (lowercase, hyphens) |
| `XYZPublication` | DOI URL `https://doi.org/<doi>` when a DOI exists; otherwise canonical URL |
| `XYZPublicationVenue` | `ISSN:<print-issn>` |

For projects and grants, the homepage URL is **not** the `pid` — it goes in an
`attributes` entry with `predicate: foaf:homepage` (see field patterns below).

### Schema_type rule
**Every dict nested inside an array field must carry a `schema_type` key.**
Correct values for commonly used array fields:

| Array field | `schema_type` of each element |
|---|---|
| `associated_with` | `dlthings:Association` |
| `attributed_to` | `dlthings:Attribution` |
| `attributes` | `dlthings:AttributeSpecification` |
| `identifiers` — generic | `dlthings:Identifier` |
| `identifiers` — DOI | `dlthings:DOI` |
| `identifiers` — ORCID | `xyzri:ORCID` |

### Common field patterns

```json
// GitHub username in identifiers  (rrid:SCR_002630 = GitHub)
{"schema_type": "dlthings:Identifier", "creator": "rrid:SCR_002630", "notation": "<github-username>"}

// ORCID in identifiers  (ror:04fa4r544 = ORCID registry)
{"schema_type": "xyzri:ORCID", "creator": "ror:04fa4r544", "notation": "0000-0000-0000-0000"}

// Email address in attributes
{"schema_type": "dlthings:AttributeSpecification", "predicate": "vcard:Email", "value": "<email>"}

// Homepage URL in attributes  (use for projects, grants, persons, etc.)
{"schema_type": "dlthings:AttributeSpecification", "predicate": "foaf:homepage", "value": "<url>"}

// associated_with entry  (roles array is required)
{"schema_type": "dlthings:Association", "object": "<pid>", "roles": ["<role-pid>"]}

// attributed_to entry  (roles array is required)
{"schema_type": "dlthings:Attribution", "object": "<pid>", "roles": ["<role-pid>"]}
```

### Roles vocabulary
Role PIDs must be taken from `data/pool_psychoinformatics_de/XYZAgentRole.json`.
Consult that file for the full list. Commonly used roles:

| PID | Label |
|---|---|
| `obo:NCIT_C19924` | Principal investigator (PI) |
| `marcrel:led` | Lead |
| `marcrel:cre` | Creator |
| `marcrel:ctb` | Contributor |
| `marcrel:rtm` | Research team member (Co-I) |
| `marcrel:pdr` | Project director |
| `marcrel:rth` | Research team head |
| `marcrel:aut` | Author (generic, when position is unknown) |
| `obo:MS_1002034` | First author |
| `obo:MS_1002035` | Senior author |
| `obo:MS_1002036` | Co-author |

More broadly, `data/pool_psychoinformatics_de/` contains the full controlled
vocabulary. Before using any coded value in a record (role, topic, quality,
bibliographic type, entity role, instrument type, etc.), look up the correct
PID in the relevant pool file (`XYZTopic.json`, `XYZQuality.json`,
`XYZBibliographicType.json`, `XYZEntityRole.json`, `XYZInstrumentType.json`,
`XYZObjective.json`, `Rule.json`, `Property.json`, `AnnotationTag.json`, …).

## Steps

### 1. Ensure the dump-things-server is running
Send a GET request to `http://localhost:8111/server`. If the response is not
200, start the server:
```
hatch run dump-server:start
```
(This command is blocking; run it in a separate terminal.) Verify it is running
before proceeding.

### 2. Familiarise yourself with reference materials
- Fetch and skim the reference JSONL (see Reference materials above) to
  understand field-formatting patterns.
- Read the relevant files in `data/pool_psychoinformatics_de/` to know which
  entities and vocabulary terms already have pool PIDs.

### 3. Gather records in the recommended order
Gather records in this order so that PIDs referenced by later records are
established first:
1. `XYZPerson`
2. `XYZOrganization`
3. `XYZProject` and `XYZGrant`
4. `XYZPublicationVenue`
5. `XYZPublication`

### 4. Validate and save each record
For each gathered record, validate it against the dump-things-server:
- **Endpoint**: `POST http://localhost:8111/research_info/validate/record/<ClassName>`
- **Header**: `X-DumpThings-Token: write_collection_token`
- **Body**: the JSON record
- **Success**: HTTP 200 with response body `true`

If the record is invalid, adjust it using information from the source and retry.
Use progressively more careful reasoning on each attempt. After 3 failed
attempts, discard the record and move on.

Once valid, append it to `data/<source_name>/<ClassName>.json` (create the file
if it does not exist).

### 5. Post-gathering review

#### a. Source review for completeness and correctness
Re-examine the source to check whether the gathered records completely and
accurately capture all relevant information. Specifically look for:
- Persons, projects, grants, or publications mentioned in the source but not yet
  recorded.
- Relationships (associations, attributions, memberships) that were missed.
- Records that misrepresent what the source says.

Add or correct records as needed. Re-run server validation (step 4) for any
added or modified records before proceeding.

#### b. Cross-reference check
Scan every `object` value across all `associated_with`, `attributed_to`, and
`part_of` fields in all gathered files. Verify that each referenced PID is
present either in `data/<source_name>/` or in `data/pool_psychoinformatics_de/`.
Resolve any dangling references (add the missing record or correct the PID)
before finishing.

### 6. Write the source README
Create (or update) `data/<source_name>/README.md` documenting:
- The source and the specific pages, endpoints, or files consulted.
- The process followed.
- A result table: file name, class name, record count, brief content description.
- Strategies and decisions made (PID assignment choices, class selection
  rationale, pool deduplication decisions, coverage scope).
- Known issues (missing identifiers, placeholder PIDs, incomplete coverage, etc.).
