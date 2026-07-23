# Current-site imported asset policy

The current CON site contains images that are part of its published content and
presentation. The metadata-driven replacement must not depend on the continued
operation of that deployment. The existing public display provides the initial
approval basis, and the repository owner explicitly approved these files for
continued display on 2026-07-23.

## Preservation

`scripts/con_site_assets.py` extracts image references from the pinned source
inventory and fetches the exact blobs from the pinned
`con/centerforopenneuroscience.org` commit. The committed manifest records every
source path, source URL, reference variant, media type, byte count, SHA-256
digest, site path, and web path. CI verifies the inventory, manifest, and files
offline.

The imported files are byte-for-byte source artifacts. They are not optimized,
resized, recolored, or silently replaced with newer upstream branding.

## Display status

- `team/` portraits are approved for the current roster projection.
- `3rd/` project logos are approved wherever the corresponding project is
  displayed.
- `banners/` and `trifolds/` are approved in their existing engagement and
  resource context.
- `contact/` contains the ROR logo used by the contact page.

Here, "logo" means a graphic used to identify a represented project or
organization. It does not refer to additional branding imported from the
Psychoinformatics site or Michael Hanke's lab.

The current-site footer states that website content is released under CC BY
3.0, but logos and portraits can carry separate rights. This note records that
general caveat; it does not override the current display approval. A repository
editor can update `site/entity-assets.yaml` through normal review if an image
should be replaced or withdrawn.

The files are committed under `site/assets/current-site/`. "Committed" means
they are copied into every built site artifact and served from the generated
site. The browser does not fetch them from the current CON domain at runtime.

## Commands

Refresh from the immutable current-site source commit:

```bash
pixi run con-site-assets-fetch
```

Verify committed files without network access:

```bash
pixi run con-site-assets-check
```
