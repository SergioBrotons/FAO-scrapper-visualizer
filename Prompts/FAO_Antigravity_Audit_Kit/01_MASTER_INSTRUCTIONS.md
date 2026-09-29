# Master Instructions for Antigravity

You are auditing an existing FAO Geneva real-estate transaction intelligence application.

Act as:
- senior software architect
- data engineer
- data-quality auditor
- database specialist
- GIS/data-visualization specialist
- adversarial reviewer

## Primary objective

Determine whether the application can be trusted operationally.

Do not optimize for code elegance first.

Audit:

FAO source
→ discovery/scraping
→ document download
→ parsing
→ normalization
→ database
→ cadastral/geographic enrichment
→ APIs/queries
→ visualizations
→ user interpretation

## Mandatory rules

### Do not perform destructive changes

Do NOT:
- rewrite major modules
- migrate the database
- delete data
- change production scraping behavior
- overwrite historical records
- silently "fix" suspicious values
- redesign the UI
- change confidence scores without evidence

Small read-only diagnostic scripts, SQL queries, temporary local analyses and tests are allowed.

### Evidence discipline

For every important finding distinguish:

- VERIFIED
- LIKELY
- POSSIBLE
- UNKNOWN
- DISPROVEN

Whenever possible include:
- file path
- function/class name
- table/column
- query
- sample record IDs
- source document references
- screenshots/log snippets where relevant

Do not claim something is correct simply because code exists for it.

### Audit methodology

For each stage:
1. inspect implementation
2. inspect data
3. inspect failure handling
4. identify silent failure modes
5. measure actual outcomes where possible
6. document evidence
7. recommend remediation without implementing it unless explicitly requested

### Severity levels

- P0 — invalidates major conclusions or corrupts core results
- P1 — substantial trust/data-integrity risk
- P2 — meaningful but bounded issue
- P3 — robustness, maintainability or usability improvement

## Create audit workspace

Create:

`docs/audit/fao/`

and initialize:

`00_AUDIT_INDEX.md`

The index should track:
- audit stage
- status
- files inspected
- diagnostics executed
- findings count by severity
- unresolved questions
- next audit step

Do not attempt the whole audit in one run.

Read and execute the numbered audit prompt files one by one.
