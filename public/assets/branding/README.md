# Cytria Logo Kit 2.1

Approved smooth vector reconstruction. This release supersedes version 2.0 (retired palette) and version 1.0 (traced geometry).

**Regenerated 20 September 2026** from the repository masters at `apps/web/public/brand/`, which are canonical. Every asset in this kit now matches the live site.

Use `01_Master_SVG` for scalable artwork, `02_PNG` for transparent exports, `03_Social` for square avatars and banners, `04_Web` for icons, and `05_Guidelines` for the usage guide.

## Colours

| Role | HEX |
|---|---|
| Cytria Ink | `#080D11` |
| Cytria Gold — the single accent | `#C9A24D` |
| Cytria Canvas | `#FCFAF6` |
| White | `#FFFFFF` |

There is **no navy** and **no secondary accent colour** in the Cytria palette. Any asset carrying `#0D1B25` or `#CD9C44` is superseded.

## What changed in 2.1

- **Navy removed.** Every mark and wordmark body is now `#080D11` (ink). `cytria-logo-navy.svg` and `cytria-mark-navy.svg` were renamed to `-ink`.
- **Gold unified** from the retired `#CD9C44` to the approved `#C9A24D`.
- Stale duplicates removed, including `cytria-logo-on-light@2x - Copy.png`.
- `03_Social` profile avatars and banners rebuilt from the corrected masters.
- Superseded artwork moved to `03_Social/_superseded/` — never ship from that folder.

## Notes

All curved contours use the exact approved cubic paths. No font dependency or embedded bitmap in the master SVGs.

`-ink` is for pixels; `-black` is for print. They differ by 8/255 per channel. In both, the gold wedge matches the mark colour so the C reads closed. That is correct for one-colour output, not a defect.

PNG exports have finite resolution. Always use SVG for large-format work. Printer-specific CMYK conversion and proofing should be handled by the printer.

## Sources

- Repo masters: `apps/web/public/brand/`
- Regeneration script: `apps/web/scripts/brandbook/launch/sync-logo-kit.mjs`
- Full brand rules: `SSOT/00-BRAND-BOOK.md`
