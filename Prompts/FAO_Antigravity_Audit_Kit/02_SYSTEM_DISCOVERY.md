# Stage 1 — System Discovery and Architecture

Goal: understand the system completely before judging or changing it.

## Tasks

Inspect the repository and identify:

- frontend framework
- backend/API
- scraper code
- Playwright/browser automation
- CAPTCHA/manual workflow
- FAO URL/page discovery
- PDF/document downloading
- raw document storage
- parser/extractor
- OCR, if any
- normalization logic
- database technology
- schema and migrations
- cadastral enrichment
- address/geolocation logic
- map implementation
- charts/KPIs
- filters
- scheduled jobs
- logging
- retries
- tests
- config/environment files
- caches
- generated artifacts

Trace the complete data flow:

FAO source
→ listing discovery
→ CAPTCHA/session
→ document acquisition
→ raw storage
→ extraction
→ normalization
→ canonical records
→ cadastral/geographic enrichment
→ API/query layer
→ frontend metrics/maps/tables

## For every stage document

- inputs
- outputs
- relevant code files
- relevant tables
- transformations
- validation
- error handling
- failure modes
- whether failures are visible or silent

## Required output

Create:

`docs/audit/fao/01_SYSTEM_ARCHITECTURE.md`

Include:

1. repository map
2. architecture overview
3. data-flow diagram in Mermaid if practical
4. major data entities
5. important entry points
6. current validation checkpoints
7. possible trust breaks
8. unknowns requiring later investigation

Update `00_AUDIT_INDEX.md`.

Stop after documenting the architecture. Do not refactor.
