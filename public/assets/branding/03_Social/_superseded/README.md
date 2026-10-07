# Superseded assets — do not use

Files here are retained for audit only. They are **not** approved for publication.

## Quarantined 2026-09-20

| File | Why |
|---|---|
| `Enrico_Impact_resultats.png` | Carried the claim *"Des résultats mesurables"*. No approved source for it exists in `apps/web/data/claims-registry.ts` or `SSOT/17-PRIVACY-LEGAL-CLAIMS`. It was meant to be replaced by `enrico_fr_linkedin_1584x396.png`, but was still sitting in `Banners/` next to the corrected file — one click from a launch post. |

## Flagged, NOT moved — awaiting a decision

These remain in `Banners/`. They were not relocated because it has not been confirmed which is current.

- `enrico_en.png` (17 Sep 11:41) and `enrico_fr.png` (17 Sep 11:42) — superseded in practice by `enrico_fr_linkedin_1584x396.png` (17 Sep 14:48), but the EN counterpart of that corrected file has not been identified.
- `linkedin.png`, `linkedin2.png`, `linkedinEn.png`, `linkedinEn2.png` (all 16 Sep 12:28) — an earlier banner set predating the corrected exports.

## Current approved banner sources

The banners shipped on the site are **generated, not hand-exported**:

```
apps/web/public/brand/social/linkedin-banner-en.png   (1584x396)
apps/web/public/brand/social/linkedin-banner-fr.png   (1584x396)
apps/web/public/images/social-card-en.png             (1200x630)
apps/web/public/images/social-card-fr.png             (1200x630)
apps/web/public/images/social-card.png                (1200x630, EN fallback)
```

Regenerate with `node apps/web/scripts/generate-social-cards.mjs`.
