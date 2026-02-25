# pool_psychoinformatics_de

## Source

- **URL**: https://pool.psychoinformatics.de/api/
- **Collection**: `public`
- **Endpoint pattern**: `GET /public/records/{ClassName}`
- **Date downloaded**: 2026-02-24

## Description

Records in this directory were downloaded directly from the public REST API of
`pool.psychoinformatics.de`. They were **not** gathered or compiled by an AI
agent analyzing source content — they are verbatim copies of the records served
by the API.

This is a **selective subset** of the classes available from the source. The
specific classes were chosen to serve as a controlled vocabulary for building a
knowledge pool.

## Downloaded Classes

| File | Class | Records |
|------|-------|---------|
| `AnnotationTag.json` | `AnnotationTag` | 2 |
| `Property.json` | `Property` | 11 |
| `Rule.json` | `Rule` | 726 |
| `XYZAgentRole.json` | `XYZAgentRole` | 93 |
| `XYZBibliographicType.json` | `XYZBibliographicType` | 61 |
| `XYZCompetitionType.json` | `XYZCompetitionType` | 1 |
| `XYZEntityRole.json` | `XYZEntityRole` | 1 |
| `XYZInstrument.json` | `XYZInstrument` | 3 |
| `XYZInstrumentType.json` | `XYZInstrumentType` | 1 |
| `XYZObjective.json` | `XYZObjective` | 1 |
| `XYZPublicationVenue.json` | `XYZPublicationVenue` | 264 |
| `XYZQuality.json` | `XYZQuality` | 23 |
| `XYZTopic.json` | `XYZTopic` | 19 |

Total: 13 files, 1,206 records.

## Known Issues

- Some classes (e.g. `XYZEntityRole`, `XYZInstrumentType`,
  `XYZCompetitionType`, `XYZObjective`) have only 1 record, suggesting the
  controlled vocabulary for these categories is still sparse in the source.
