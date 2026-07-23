# Legacy site asset policy

The legacy CON site contains locally hosted images that are part of its content
and presentation. The replacement must not depend on the continued operation of
the old domain, but mirroring an image does not by itself approve prominent or
current use.

## Preservation

`scripts/con_site_assets.py` extracts image references from the pinned source
inventory and fetches the exact blobs from the pinned
`con/centerforopenneuroscience.org` commit. The committed manifest records every
source path, source URL, reference variant, media type, byte count, SHA-256
digest, site path, and web path. CI verifies the inventory, manifest, and files
offline.

The mirrored files are byte-for-byte source artifacts. They are not optimized,
resized, recolored, or silently replaced with newer upstream branding.

## Display status

- `team/` portraits are preserved for migration, but current display should be
  confirmed with the represented person or the center's editorial owner.
- `3rd/` project and third-party marks are preserved for identification. Their
  current branding and trademark guidance should be reviewed before prominent
  display.
- `banners/` and `trifolds/` are legacy engagement artwork. They may be shown in
  historical or resource context while the linked handouts remain available.
- `contact/` contains the ROR mark used by the contact page.

The legacy footer states that website content is released under CC BY 3.0, but
third-party marks and portraits can carry separate rights. The manifest
therefore establishes provenance, not a blanket relicensing assertion.

## Commands

Refresh from the immutable upstream commit:

```bash
pixi run con-site-assets-fetch
```

Verify committed files without network access:

```bash
pixi run con-site-assets-check
```
