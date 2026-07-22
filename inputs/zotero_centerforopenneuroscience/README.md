# CON Zotero snapshots

`snapshot.json` is generated from the public Zotero API by:

```sh
pixi run zotero-fetch
```

It records the collection definitions, all top-level items, retrieval time, API
URLs, and Zotero library versions needed to interpret a transform. It is not a
validated research-information file and must never be loaded by
`dump-research-info`.
