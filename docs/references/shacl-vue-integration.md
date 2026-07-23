# SHACL-vue editor integration decision

## Decision

Do not couple SHACL-vue to the public static site yet. First build a read-only,
separately deployed spike from the same Things v2 data. Add editing only after a
staging service can round-trip a record into a reviewable Git change without
semantic loss.

SHACL-vue is the proposed editor. No alternative backing data model is being
introduced. Things v2 remains the research-information model and the validated
JSON arrays remain its canonical repository serialization. SHACL-vue consumes
an RDF serialization because that is its interface contract; JSON-to-RDF and
RDF-to-JSON are adapter and round-trip concerns, not a second semantic model.

This keeps the current delivery architecture simple:

- Git and the validated source-scoped JSON arrays remain canonical.
- The public website remains a deterministic, read-only projection deployed by
  GitHub Actions.
- The SHACL-vue editor is a separate client and runtime trust boundary.
- Accepted edits enter the canonical repository through a pull request.

The decision was assessed against
[`orinoco/shacl-vue`](https://hub.psychoinformatics.de/orinoco/shacl-vue) at
commit `dbb9bfa3997881abb0dfc8ba1bbc572ddc39b8d0`. The project describes itself as
under continuous development and currently has no release tags, so any prototype
must pin a full commit rather than follow `main`.

## What is already available

The DataLad Concepts research-information schema publishes two of the required
SHACL-vue inputs:

- [annotated SHACL shapes](https://concepts.datalad.org/s/demo-research-information/unreleased.shacl.ttl)
- [OWL class hierarchy](https://concepts.datalad.org/s/demo-research-information/unreleased.owl.ttl)

Both URLs were reachable when this decision was written. The editor's identifier
property must be configured as
`https://concepts.datalad.org/s/things/v2/pid`.

SHACL-vue can be built as a standalone static Vue application. A deployment is
configured with JSON or YAML and can point to local or remote TTL files. This
makes a read-only GitHub Pages prototype possible without introducing a service.

## Missing pieces

### RDF data projection

The repository stores validated source-scoped JSON arrays, while the editor
takes the same Things v2 graph serialized as RDF/Turtle. A deterministic
serialization adapter is needed that:

- merges or preserves duplicate source records according to an explicit policy;
- emits named nodes using the existing Things v2 PIDs;
- preserves associations, identifiers, attributes, and CURIEs;
- records the source directory for later write-back; and
- has a regression test that compares JSON-to-RDF-to-JSON semantics.

The generated public-site merge is not an acceptable write target because it
has already applied precedence and union rules. This is a provenance limitation
of that projection, not evidence of an alternative model.

### Read/write service

SHACL-vue documents direct integration with `dump-things-server`. Its
`service_base_url` configuration distinguishes read and write collections, and
its endpoint templates fetch and submit Turtle records. The present local
service is used only for validation; there is no persistent, authenticated CON
collection to edit.

### Authentication and authorization

The documented upstream workflow uses a Forgejo-generated token supplied by the
user in SHACL-vue and forwarded to `dumpthings`. This repository and its review
workflow currently live on GitHub. Before enabling writes, maintainers must
choose either:

1. Operate the editor and data service behind Forgejo authentication, then export
   accepted changes to GitHub pull requests.
2. Implement and operate a different authentication bridge suitable for GitHub.

The first option is closer to the pre-existing Orinoco deployment pattern and is
the recommended starting point. Neither option belongs in a static GitHub Pages
deployment.

### Canonical write-back

A service record does not by itself identify which source-scoped JSON array it
should update. The write-back process must define:

- whether an edit updates an existing source record or creates a curated source;
- how conflicts with refreshed Zotero or current-site snapshots are represented;
- stable JSON formatting and class-based file placement;
- validation before a branch is pushed; and
- the identity recorded in the commit and pull request audit trail.

## Phased implementation

### Phase A: read-only spike

1. Implement a deterministic Things v2 JSON-to-Turtle export.
2. Pin the full SHACL-vue commit in a dedicated deployment directory or
   repository.
3. Configure `class_url`, `shapes_url`, `data_url`, and the Things v2 PID IRI.
4. Limit visible classes initially to person, organization, project, grant,
   publication, dataset, instrument, and publication venue.
5. Build the standalone application with `npm run build:app`.
6. Publish it as a separate CI artifact and optional preview URL, with all submit
   operations disabled.

The spike is successful only if all current records can be viewed and linked by
their existing PIDs. It is not a production editor.

### Phase B: disposable write staging

1. Deploy a schema-matched `dump-things-server` instance with separate public
   read and protected write collections.
2. Configure authentication, CORS, backups, and retention.
3. Point a non-public SHACL-vue deployment at that service.
4. Implement export from the staging collection into a new Git branch.
5. Generate a pull request containing source-scoped JSON changes and validation
   evidence.
6. Test create, update, reference, conflict, and rejection paths.

No staging edit should directly mutate `main` or the generated website.

### Phase C: maintained editor

Proceed only when the staging round trip meets all acceptance criteria. Pin a
reviewed SHACL-vue revision, define an upgrade cadence, monitor the service, and
document operator recovery procedures. Keep the public site operational when the
editor or service is unavailable.

## Acceptance criteria for write support

- A representative record survives JSON to RDF to editor to JSON without losing
  supported meaning.
- Existing PIDs and references remain stable.
- Every changed record passes the current Orinoco Things v2 validator.
- Source provenance and merge conflicts remain visible.
- Unauthorized clients cannot read protected collections or submit records.
- Browser-delivered configuration contains no reusable service credential.
- Every accepted edit is attributable and reviewable as a Git change.
- Service failure cannot block or corrupt the public static site deployment.

## Open decisions

1. Who will operate and back up the persistent `dumpthings` service?
2. Which Forgejo instance and groups should control read, submit, curate, and
   administrative permissions?
3. Should human edits enter a new `data/curated/` source, or update the original
   source-scoped record?
4. How should simultaneous source refreshes and editor changes be reconciled?
5. Is the RDF projection a merged read view, source-preserving named graphs, or
   both?
6. Which classes and fields need UI-specific SHACL annotations beyond the
   published Concepts shapes?

## References

- [SHACL-vue source on the Orinoco Forgejo](https://hub.psychoinformatics.de/orinoco/shacl-vue)
- [SHACL-vue application inputs](https://shacl-vue.psychoinformatics.de/app-inputs.html)
- [SHACL-vue application configuration](https://shacl-vue.psychoinformatics.de/app-configuration.html)
- [SHACL-vue deployment guidance](https://shacl-vue.psychoinformatics.de/app-deployment.html)
- [SHACL-vue dumpthings integration](https://shacl-vue.psychoinformatics.de/features-dumpthings.html)
- [SHACL-vue Forgejo authentication integration](https://shacl-vue.psychoinformatics.de/features-forgejo.html)
- [TRR379 SHACL-vue deployment example](https://hub.trr379.de/q04/annotate.trr379.de-demo)
