# Stage 2 — Scraper and Acquisition Audit

Goal: determine whether the FAO acquisition process is complete, repeatable and auditable.

## Inspect

- listing discovery
- pagination
- date-range handling
- browser state
- CAPTCHA workflow
- session expiry
- rate limiting
- request pacing
- retries
- checkpoints
- resumability
- document naming
- document validation
- duplicate handling
- run logs

## Answer

### Coverage
- What exact periods/pages are requested?
- Can pages or transactions be skipped?
- Can a resumed run create gaps?
- Is there a persistent cursor/checkpoint?
- Can revised or late-published transactions be detected?

### CAPTCHA/session
- What happens after CAPTCHA?
- Can expiry happen silently?
- Could a CAPTCHA/error page be accepted as valid content?

### Downloads
Check whether the system validates:
- response status
- content type
- file signature
- non-zero size
- PDF validity
- expected identifier
- hash
- duplicate content
- partial downloads

### Idempotency
Determine whether rerunning the same period:
- duplicates rows
- updates records
- skips correctly
- corrupts state
- creates conflicting documents

## Measure actual acquisition state where possible

Produce counts such as:
- listings discovered
- documents requested
- documents downloaded
- failed downloads
- invalid documents
- duplicates
- parse-ready documents

Identify unexplained gaps.

## Required output

Create:

`docs/audit/fao/02_SCRAPER_AUDIT.md`

Use this table for findings:

| ID | Severity | Finding | Evidence | Consequence | Recommendation |
|---|---|---|---|---|---|

Also create diagnostic scripts/queries only if necessary under:
- `docs/audit/fao/diagnostics/`
- `docs/audit/fao/queries/`

Update `00_AUDIT_INDEX.md`.

Do not change scraper production behavior yet.
