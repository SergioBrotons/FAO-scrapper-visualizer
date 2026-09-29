# FAO Antigravity Audit Kit

Purpose: audit the existing FAO Geneva real-estate scraper application end-to-end before making major changes.

## How to use this kit in Antigravity

1. Copy this entire folder into the repository, preferably under:
   `docs/audit/antigravity-kit/`

2. Open Antigravity at the repository root.

3. Start with `01_MASTER_INSTRUCTIONS.md`.

4. Then execute the prompts strictly in numerical order:
   - `02_SYSTEM_DISCOVERY.md`
   - `03_SCRAPER_AUDIT.md`
   - `04_DATABASE_AND_LINEAGE_AUDIT.md`
   - `05_PARSER_AND_DATA_QUALITY_AUDIT.md`
   - `06_GIS_AND_VISUALIZATION_AUDIT.md`
   - `07_CONFIDENCE_MODEL_AND_VALIDATION.md`
   - `08_ADVERSARIAL_REVIEW.md`
   - `09_FINAL_SYNTHESIS.md`

5. Do not paste every file into one prompt. Give Antigravity one file at a time.

6. After each step, require Antigravity to:
   - write findings to the requested audit file,
   - cite exact source files/functions/tables where possible,
   - distinguish verified facts from assumptions,
   - avoid destructive changes,
   - stop after completing that stage.

7. If Antigravity tries to refactor before completing the audit, instruct it:
   `Audit first. Do not modify production logic yet. Continue with the current audit stage only.`

## Intended output folder

Antigravity should create and maintain:

`docs/audit/fao/`

with:

- `00_AUDIT_INDEX.md`
- `01_SYSTEM_ARCHITECTURE.md`
- `02_SCRAPER_AUDIT.md`
- `03_DATABASE_AND_LINEAGE.md`
- `04_PARSER_AND_DATA_QUALITY.md`
- `05_GIS_AND_VISUALIZATION.md`
- `06_CONFIDENCE_AND_VALIDATION.md`
- `07_ADVERSARIAL_REVIEW.md`
- `08_FINAL_AUDIT.md`
- `evidence/`
- `queries/`
- `diagnostics/`

## Operating rule

The audit is about trustworthiness, not merely whether the application runs.

The central question is:

> Can every important value shown in the application be traced to authoritative source evidence, and how much confidence should a user place in it?
