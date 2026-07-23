# CON research-information source landscape

Status: initial agent-assisted survey, 2026-07-23.

This report guides content expansion before general-purpose ETL is designed. It
is a discovery and review queue, not a set of canonical assertions. Every
promoted fact still needs source-specific extraction, Things v2 modeling,
reconciliation, and review.

## Confirmed operating approach

- Model every person, organization, project, grant, publication, dataset, and
  software entity for which useful evidence can be retained.
- Initially order and label the public people view according to the 33-entry
  current-site roster. Do not delete broader modeled people merely because they
  are not in that display snapshot.
- Preserve distinctions among center membership, employment, project
  participation, authorship, maintenance, and historical affiliation.
- Use deterministic extraction where a source has stable identifiers and a
  usable API. Use agents and people for discovery, ambiguous identity,
  relationship interpretation, narrative synthesis, and review.
- Require human review before writing new items to Zotero or classifying them
  as internal or external.

## Priority source matrix

| Priority | Source | Primary contribution | Stable identifiers / access |
|---|---|---|---|
| P0 | Current CON site and pinned source repository | Initial roster, role buckets, projects, descriptions, affiliations, links, media | Git commit, URLs, ORCID, GitHub, grant and DOI links |
| P0 | Zotero group 6197458 | Reviewed publication and dataset bibliography | Zotero item/collection keys, DOI; Web API v3 |
| P0 | ORCID | Person identity, aliases, public works and affiliations | ORCID iD; public API |
| P0 | ROR | Organization identity, aliases, location and hierarchy | ROR ID; REST API |
| P0 | Crossref and DataCite | DOI metadata, authors, funders, related outputs, versions | DOI; REST APIs |
| P0 | NIH RePORTER and NSF Award Search | Award identity, title, abstract, investigators, recipient, dates and amount | Grant/application numbers; APIs and exports |
| P0 | DANDI | Dandisets, versions, contributors, funding, related works and NWB-derived metadata | Dandiset ID, version, DOI, asset UUID; REST API |
| P1 | GitHub and Orinoco Forgejo | Repository identity, releases, citation files, maintainers, source evidence | Repository URL, release/tag/commit; REST APIs |
| P1 | Zenodo | Software/data releases, creators, ORCID, grants and related identifiers | Concept/version DOI; REST API |
| P1 | PubMed/PMC | Biomedical publication identity and publisher-supplied affiliations | PMID, PMCID, DOI; E-utilities |
| P1 | OpenNeuro | BIDS datasets, snapshots, authors and version DOIs | Accession, snapshot, DOI; GraphQL and Git/DataLad access |
| P1 | CORDIS and UKRI Gateway to Research | EU and UK grants, participants, outputs and deliverables | Project/award IDs; APIs and bulk data |
| P2 | OpenAlex | Candidate discovery across authors, works, institutions and funders | OpenAlex IDs, linked ORCID/ROR/DOI; API |
| P2 | DataLad Registry, Catalog and MetaLad | Dataset identity, metadata extraction, provenance and discoverability | Dataset UUID, Git URL and revision; APIs/tools |
| P2 | Software Heritage | Exact archived code identity and preservation | SWHID; API |

Primary references:

- [CON projects](https://centerforopenneuroscience.org/projects)
- [CON people](https://centerforopenneuroscience.org/whoweare)
- [ORCID public API](https://info.orcid.org/what-is-orcid/services/public-api/)
- [ROR REST API](https://ror.readme.io/docs/rest-api)
- [Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/)
- [DataCite REST API](https://support.datacite.org/docs/api)
- [NIH RePORTER API](https://api.reporter.nih.gov/)
- [NSF Award Search](https://www.nsf.gov/funding/award-search)
- [DANDI REST API](https://docs.dandiarchive.org/api/rest-api/)
- [OpenNeuro API](https://docs.openneuro.org/api.html)
- [Zotero Web API v3](https://www.zotero.org/support/dev/web_api/v3/)

## People and organizations

The current display baseline is 33 people: 7 Centroids, 8 Collaborators, 4
Affiliated Faculty, and 14 Emeritus. These labels are a source-site snapshot,
not a verified employment ontology.

High-value enrichment sources include the CON roster's ORCID links,
institutional profiles, project team pages, publication affiliations, and ROR.
The DANDI and NWB team pages are especially useful because they distinguish
current and former members and technical, governance, liaison, and investigator
roles.

Immediate identity candidates include Benjamin Dichter, Oliver Rübel, Ryan Ly,
Lydia Ng, Kristofer Bouchard, Roni Choudhury, Jacob Nesbitt, Michael
VanDenburgh, Daniel Chiquito, Michael Grauer, and Bhavya Kandimalla. Their
project participation must not be promoted as CON employment without separate
evidence.

Known temporal/status conflicts include John Wodder being listed as CON
Emeritus while appearing as a current DANDI developer, and Cody Baker and
Horea-Ioan Ioanas having current/former distinctions across CON, DANDI, and
employer sources. These are reasons to model qualified roles, not to select one
unqualified status.

## Projects, grants, and organizations

### Near-term grant batches

| Ecosystem | Award candidates | Authoritative source |
|---|---|---|
| DANDI | NIH `1R24MH117295` and continuations | NIH RePORTER |
| EMBER | NIH `1R24MH136632-01` | NIH RePORTER |
| OpenNeuro | NIH `5R24MH117179-07` | NIH RePORTER |
| ReproNim | NIH `1P41EB019936-01A1` | NIH RePORTER |
| NWB | NIH `1R24MH116922-01`, `5U24NS120057`, `1R44MH115731` | NIH RePORTER and NWB grants page |
| DataLad/DataGit | NSF `1429999`, `1912266`; BMBF `01GQ1411`, `01GQ1905` | NSF, BMBF/GSI, DataLad acknowledgements |
| DataLad ecosystem | EU `945539`, `826421`; DFG `431549029`, `512007073` | CORDIS, GEPRIS/project pages, DataLad acknowledgements |

Grant recipient, PI institution, CON affiliation, project leadership, and
software maintenance are separate relationships. NIH continuation and
application numbers should retain both the core award identity and the complete
application identifier.

### Project classification queue

Use evidence-backed categories rather than ownership assumptions:

- Direct or center-led candidates: DataLad, DataLad Registry, Open Brain
  Consent, and explicitly CON-maintained repositories.
- Partner or co-led candidates: DANDI, OpenNeuro, ReproNim, BIDS, NWB, and
  projects for which CON names a concrete contribution.
- Ecosystem candidates: standards, archives, funders, datasets, publications,
  software dependencies, and partner institutions.
- Hold candidates: title/name similarity or contributor activity without an
  explicit project relationship.

"Upstream project source" means evidence maintained by the represented project
or its funder/publisher. It does not mean importing Psychoinformatics branding
or treating Michael Hanke's lab as generally authoritative for CON content.

## Publications

Publication discovery should begin with the Zotero group, current CON project
and person pages, exact DOIs, ORCIDs, and affiliation searches. Crossref and
OpenAlex improve recall; publisher pages and PubMed provide stronger
classification evidence.

High-value candidates to compare against Zotero include:

| Work | DOI | Initial review class |
|---|---|---|
| NeuroConv | `10.25080/cehj4257` | Internal candidate; explicit CON affiliations reported |
| Neuroimaging article reexecution and reproduction assessment system | `10.3389/fninf.2024.1376022` | Internal candidate; explicit CON affiliation |
| HeuDiConv | `10.21105/joss.05839` | Internal candidate |
| DataLad | `10.21105/joss.03262` | Internal candidate |
| Open Brain Consent | `10.1002/hbm.25351` | CON initiative; review author-affiliation semantics |
| Microscopy-BIDS | `10.3389/fnins.2022.871228` | CON-affiliated/community-standard candidate |
| OpenNeuro resource | `10.7554/eLife.71774` | External collaboration candidate |
| Neurodata Without Borders ecosystem | `10.7554/eLife.78362` | External; explicitly reviewed 2026-07-23 |
| Eye-Tracking-BIDS preprint | `10.64898/2026.02.03.703514` | Hold until version/status review |

Internal, External, Historical-related, and Hold are editorial classifications.
They are not inferred from coauthor names alone.

## Datasets, software, and standards

The first DANDI dataset candidates should exercise concept/version distinctions:

| Candidate | Stable identity |
|---|---|
| Allen Institute Visual Coding - Optical Physiology | DANDI `000728`, version DOI `10.48324/dandi.000728/0.240827.1809` |
| IBL Brain Wide Map | DANDI `000409`, version DOI `10.48324/dandi.000409/0.260309.1324` |
| MICrONS Two Photon Functional Imaging | DANDI `000402` |
| Drosophila locomotion dynamics | DANDI `000727`, version DOI `10.48324/dandi.000727/0.240106.0043` |

Candidate software and standards include PyNWB, MatNWB, HDMF, NWB Schema,
NWB extensions, DANDI CLI and Schema, NeuroConv, NWB Inspector, NWB GUIDE,
Neurosift, DataLad Catalog, DataLad MetaLad, BIDS, and Open Brain Consent.
Repository ownership, commit activity, scientific authorship, and institutional
affiliation must remain separate assertions.

## Recommended implementation sequence

1. Complete the current-site and Zotero baselines and review their unresolved
   identity queues.
2. Add ORCID/ROR enrichment as candidate generation with explicit identity
   mappings.
3. Add NIH and NSF award adapters for already identified exact award numbers.
4. Add DANDI Dandiset/version candidates for a small reviewed sample.
5. Add repository and release metadata through GitHub, Forgejo, Zenodo, and
   citation files.
6. Reassess common extraction interfaces only after these source-specific
   batches expose their real differences.

## Questions for review

1. What evidence is sufficient to assert current CON membership rather than
   project contribution or publication authorship?
2. Should role and affiliation assertions carry `validFrom`, `validTo`, source,
   retrieval date, and approval state?
3. Which projects are direct CON projects, partner projects, or ecosystem
   context?
4. Should parent awards, continuations, supplements, cores, and subawards be
   separate grant entities?
5. Should a dataset concept, published version, draft, and file asset be
   separate Things v2 entities?
6. Which identifier wins for a software version: concept DOI, version DOI, Git
   tag, commit, package version, or SWHID?
7. Which source wins when a funder, DOI registry, repository, project page, and
   institutional profile disagree?
8. Must every displayed field expose source and approval provenance, or is a
   record-level provenance panel sufficient?
9. How should retractions, renamed organizations, deleted repositories, changed
   affiliations, and withdrawn datasets be represented?
10. Which source-specific batch should follow the current baseline?
