# FAO Real-Estate Intelligence System: Full Technical, Data Quality & Visualization Audit

You are acting as a **senior data engineer, software architect, data-quality auditor, GIS/data-visualization specialist, and adversarial reviewer**.

Your task is to perform a comprehensive audit of the existing FAO Geneva real-estate transaction intelligence application.

## Core principle

**DO NOT immediately refactor, rewrite, migrate, or “improve” the application.**

First understand the existing system completely.

Separate:

1. What you can verify directly from code/data
2. What appears correct but has not been independently verified
3. What is inferred
4. What is uncertain
5. What is demonstrably incorrect
6. What cannot currently be validated

The goal is not merely to determine whether the application runs.

The goal is to establish:

> **Can we trust the data shown by this application, how much can we trust it, and can we trace every displayed fact back to authoritative evidence?**

---

# 1. SYSTEM DISCOVERY

Inspect the entire repository/workspace before making recommendations.

Identify:

- application architecture
- scraper architecture
- Playwright/browser automation
- CAPTCHA/manual intervention workflow
- FAO source URLs/endpoints
- downloaded source files
- PDF acquisition process
- PDF parsing/extraction
- OCR if present
- normalization/transformation logic
- database
- schema
- migrations
- APIs
- backend services
- frontend
- maps
- charts
- filters
- statistics
- confidence calculations
- cadastral/geographic enrichment
- geocoding
- deduplication
- entity matching
- caching
- scheduled jobs
- logs
- retries
- error handling
- tests
- configuration files
- environment variables
- documentation

Produce an architecture map similar to:

FAO source  
→ transaction discovery  
→ CAPTCHA/session  
→ PDF/document download  
→ raw-document storage  
→ extraction  
→ normalization  
→ database  
→ cadastral/geographic enrichment  
→ API/query layer  
→ visualization  
→ user interpretation

For every stage identify:

- inputs
- outputs
- transformation
- possible failure modes
- whether failures are detected
- whether failures can silently contaminate downstream data

---

# 2. SCRAPER AUDIT

Review how the application discovers and downloads FAO transactions.

Determine:

### Coverage
- What FAO pages/date ranges are queried?
- Can pagination or navigation cause transactions to be missed?
- Can transactions appear later or be modified?
- Does the scraper know where collection started and stopped?
- Is there a persistent checkpoint?
- Can interrupted runs resume safely?
- Is historical coverage continuous?

### Rate limiting and anti-bot handling
- Does the scraper intentionally operate slowly?
- Are delays deterministic or randomized?
- What happens after CAPTCHA?
- Can a session expire without the system noticing?
- Could FAO return an error/login/CAPTCHA page that gets stored as if it were a valid document?

### Downloads
For every document download verify:

- HTTP/response success where available
- correct MIME/file type
- non-zero size
- valid PDF structure
- expected page count where possible
- filename/transaction association
- document hash
- duplicate detection

Identify any way that:

- transactions can be skipped
- the same transaction can be downloaded twice
- documents can be associated with the wrong transaction
- HTML error pages can masquerade as PDFs
- partial downloads can enter the database

---

# 3. SOURCE-TO-RECORD TRACEABILITY

This is critical.

Determine whether every database transaction can be traced to its source.

Ideally each record should retain:

- FAO transaction/publication identifier
- original source URL
- source publication date
- downloaded document filename
- immutable document hash
- extraction timestamp
- parser version
- raw extracted text or structured extraction
- normalized values
- provenance for enriched fields

Evaluate whether this is currently possible.

Perform sample lineage tests:

**UI record → API/database row → normalized record → extracted source → original FAO document**

Report any broken links in this chain.

---

# 4. PDF / DOCUMENT EXTRACTION AUDIT

Inspect the parser carefully.

Identify all fields being extracted, for example:

- publication date
- transaction date
- sale price
- municipality
- address
- parcel number
- cadastral references
- property type
- buyer
- seller
- ownership share
- surface
- PPE/lot
- building
- transaction type
- legal notes

For each field determine:

### Extraction method

Is it obtained through:

- deterministic parsing
- regex
- text positioning
- table parsing
- OCR
- heuristic logic
- LLM inference
- lookup/enrichment
- manual entry

### Error susceptibility

Identify risks such as:

- OCR digit confusion
- thousands separator issues
- decimal separator issues
- CHF parsing errors
- dates swapped
- multiple prices in one document
- multiple parcels
- multiple buyers/sellers
- ownership fractions
- PPE transactions
- bundled transactions
- duplicate documents
- corrected publications
- missing fields
- unusual legal wording

Do not assume that a parser returning a value means that value is correct.

---

# 5. DATABASE AUDIT

Inspect the entire database model.

For each important table document:

- purpose
- primary key
- foreign keys
- uniqueness rules
- indexes
- nullability
- expected cardinality

Look specifically for:

### Duplicate risks

Could one transaction exist:

- twice under different IDs?
- once per parcel rather than once per transaction?
- once per owner?
- once per document?
- once per scraping run?

### Identity

Determine what the system treats as the canonical identity of a transaction.

Assess whether that identity is robust.

### Referential integrity

Check for:

- orphan rows
- missing relationships
- invalid foreign keys
- duplicate canonical identifiers
- inconsistent municipality/address/parcel relationships

### Field semantics

Determine whether apparently similar concepts have been incorrectly conflated, e.g.:

- publication date vs sale date
- asking price vs transaction price
- parcel area vs habitable area
- property address vs owner address
- transaction count vs parcel count

---

# 6. DATA COMPLETENESS AUDIT

Measure completeness rather than merely inspecting code.

Calculate, where possible:

- transactions discovered
- documents downloaded
- documents successfully parsed
- database records created
- records mapped to parcels
- records geocoded
- records visible in the application

Create a funnel such as:

FAO listings found: N  
↓  
Documents downloaded: N  
↓  
Valid documents: N  
↓  
Parsed successfully: N  
↓  
Canonical transactions: N  
↓  
Cadastral matches: N  
↓  
Geographically mapped: N  
↓  
Displayed: N

Calculate loss percentages between every stage.

Flag unexplained losses.

---

# 7. TEMPORAL COVERAGE

Determine exactly which periods are represented.

Produce:

- first transaction date
- last transaction date
- first publication date
- last publication date
- transaction count by month
- transaction count by municipality
- missing days/weeks/months
- suspicious sudden drops or spikes

Distinguish between:

**true market behavior** and **collection/data-quality problems**.

Never assume a gap means no transactions occurred.

---

# 8. CADASTRE / ADDRESS / GEOLOCATION AUDIT

Audit geographic enrichment separately from FAO extraction.

For every mapping mechanism determine whether it uses:

- official cadastral identifiers
- parcel IDs
- addresses
- coordinates
- fuzzy matching
- geocoder results
- manual mappings

Classify geographic matches as:

- exact cadastral match
- exact address match
- normalized-address match
- fuzzy match
- municipality-only match
- inferred approximate location
- unresolved

A point appearing on a map must **not automatically imply exact geographic certainty**.

Check for:

- duplicated addresses
- street-number mismatch
- municipality mismatch
- parcel mismatch
- coordinates outside the Canton of Geneva
- impossible coordinates
- centroid use disguised as exact address position

---

# 9. VISUALIZATION ACCURACY

Audit the frontend from a data semantics perspective, not only visually.

For every:

- KPI
- chart
- map
- marker
- tooltip
- filter
- table
- average
- median
- €/m² or CHF/m² metric
- trend
- ranking
- percentage

trace the value back to its database query or calculation.

Verify:

### Aggregation correctness

Check for common analytical errors:

- COUNT(rows) when rows are parcels but UI says transactions
- AVG(price) where weighted calculations are needed
- average instead of median
- duplicated transactions affecting totals
- null values treated as zero
- filtered and unfiltered denominators mixed
- grouped sales counted multiple times
- surface mismatch producing invalid CHF/m²
- outliers dominating results

### Filter consistency

Test whether changing:

- municipality
- date
- property type
- transaction category
- price range
- map viewport

causes every KPI/chart/table to use the same population.

Identify any component that silently uses a different query/filter scope.

---

# 10. DATA CONFIDENCE MODEL

Design or audit an explicit confidence model.

Do NOT create a single arbitrary confidence percentage.

Confidence should be decomposable.

For each transaction consider dimensions such as:

### Source confidence
Was the original authoritative FAO source retained and validated?

### Extraction confidence
Were required fields deterministically extracted?

### Identity confidence
Is transaction identity unambiguous?

### Geographic confidence
Was the location linked through exact cadastral identifiers or approximated?

### Completeness confidence
Are important fields missing?

### Consistency confidence
Do related fields agree with one another?

Suggested statuses:

- VERIFIED
- HIGH
- MEDIUM
- LOW
- UNVERIFIED
- CONFLICT
- INCOMPLETE

Every confidence classification must have an explainable reason.

Example:

Confidence: HIGH

Reasons:
- authoritative FAO PDF retained
- document hash verified
- price deterministically parsed
- transaction ID unique
- parcel ID exact cadastral match

Limitation:
- habitable surface unavailable

Avoid black-box scoring unless every component and weight is documented.

---

# 11. CROSS-FIELD VALIDATION

Implement or identify possible consistency checks.

Examples:

- publication date cannot precede transaction date by impossible intervals
- prices must be positive
- parcel surface cannot be negative
- coordinates must fall in plausible geographic bounds
- municipality and postal code should agree
- cadastral parcel should belong to stated municipality
- CHF/m² should not be calculated without compatible price and surface fields
- duplicate transaction IDs should trigger alerts
- document hash duplicates should be investigated
- transactions sharing identical price/date/address should be checked for duplicates

Flag anomalies rather than automatically “correcting” them.

---

# 12. GOLDEN-SAMPLE VALIDATION

Create a validation methodology.

Select a stratified sample, for example:

- recent transactions
- old transactions
- high-value transactions
- low-value transactions
- several municipalities
- apartments/PPE
- houses
- land
- complex multi-parcel transactions
- records with missing fields
- records with low confidence

For each sample manually compare:

FAO source document  
vs  
extracted values  
vs  
database  
vs  
frontend display

Calculate field-level accuracy where possible.

Examples:

price: 49/50 correct = 98%  
publication date: 50/50 = 100%  
parcel: 46/50 = 92%  
address: 44/50 = 88%  
geolocation: 40/50 exact = 80%

Clearly distinguish a measured accuracy rate from a confidence heuristic.

---

# 13. ADVERSARIAL / 10TH-MAN REVIEW

After completing the normal audit, deliberately try to prove the system unreliable.

Assume another engineer says:

> “The application looks convincing but the data cannot be trusted.”

Try to substantiate that claim.

Search specifically for:

- silent data loss
- accidental duplicates
- stale records
- incorrect joins
- incorrect aggregation
- parser edge cases
- visualization mistakes
- false geographic precision
- records without provenance
- scraper interruptions
- schema assumptions
- historical gaps
- survivorship bias
- selection bias

Document every credible failure mechanism.

Then assess whether the evidence actually supports it.

---

# 14. AUTOMATED TESTS

Review existing tests.

Identify missing tests for:

### Scraping
- pagination
- retries
- CAPTCHA/session expiry
- failed downloads
- duplicate documents
- resumability

### Parsing
- representative documents
- unusual document layouts
- multiple parcels
- ownership fractions
- missing fields
- malformed PDFs

### Database
- uniqueness
- referential integrity
- duplicate prevention
- idempotent imports

### Analytics
- aggregation
- filters
- date periods
- median/average calculations
- CHF/m²

### Geography
- exact/fuzzy matches
- invalid coordinates
- unresolved parcels

### Frontend
- displayed values equal API/database calculations

Do not write all tests yet.

First provide the proposed test matrix.

---

# 15. OBSERVABILITY

Determine whether failures are measurable.

Check for:

- structured logs
- scraper run IDs
- run start/end times
- pages attempted
- documents attempted
- documents downloaded
- parse successes/failures
- retry counts
- validation failures
- database inserts/updates/skips
- duplicate detection
- geocoding failures

Propose a run-level audit record such as:

run_id  
started_at  
completed_at  
source_period  
pages_seen  
transactions_discovered  
documents_downloaded  
downloads_failed  
documents_parsed  
parse_failed  
records_inserted  
records_updated  
records_skipped  
duplicates_detected  
validation_errors

---

# 16. DO NOT HIDE UNCERTAINTY

Whenever the system cannot know something confidently, the UI should represent that uncertainty.

Look for places where the application currently presents:

- inferred values as known facts
- fuzzy map matches as exact coordinates
- incomplete datasets as complete market statistics
- extrapolation as observation

Identify these explicitly.

---

# 17. REQUIRED OUTPUT

Create:

`docs/audit/FAO_SYSTEM_AUDIT.md`

Structure it as:

## 1. Executive summary

Briefly answer:

- Is the pipeline structurally sound?
- Is current data trustworthy?
- What can already be trusted?
- What requires validation?
- What are the largest risks?

Do NOT provide a false binary “good/bad” verdict.

---

## 2. System architecture

Include the complete pipeline and data flow.

---

## 3. Scraper audit

Finding | Severity | Evidence | Consequence | Recommendation

---

## 4. Parser audit

Field | Extraction method | Reliability | Known risks | Validation status

---

## 5. Database audit

Include schema/identity/integrity issues.

---

## 6. Data completeness

Include measurable funnel numbers.

---

## 7. Historical coverage

Include missing periods and anomalies.

---

## 8. Geographic/cadastral accuracy

Separate exact, inferred and unresolved locations.

---

## 9. Visualization audit

For every major KPI/chart/map/table:

UI element | Source query | Calculation | Correct? | Risk

---

## 10. Confidence model

Describe current confidence handling and proposed model.

---

## 11. Validation results

Include manually verified samples if the source documents are locally available.

---

## 12. Critical findings

Use severity:

- P0 — invalidates major conclusions
- P1 — substantial data integrity risk
- P2 — meaningful issue
- P3 — improvement / robustness

---

## 13. Trust matrix

Create a matrix such as:

| Data element | Provenance | Extraction | Validation | Confidence |
|---|---|---|---|---|
| Sale price | FAO PDF | deterministic | sample verified | HIGH |
| Address | FAO + parser | heuristic | partial | MEDIUM |
| Exact map location | cadastre | exact/fuzzy | mixed | VARIABLE |

---

## 14. Recommended remediation plan

Separate into:

### Phase A — Trust blockers
Problems that must be resolved before using the data for decisions.

### Phase B — Validation
Actions needed to quantify accuracy.

### Phase C — Robustness
Tests, observability, idempotency, provenance.

### Phase D — Product improvements
Confidence indicators, UI wording, filters, analytics.

---

# 18. IMPORTANT OPERATING RULES

During this first audit:

- DO NOT rewrite major modules.
- DO NOT migrate the database.
- DO NOT delete records.
- DO NOT normalize historical data automatically.
- DO NOT silently correct suspicious values.
- DO NOT alter production data.
- DO NOT change scraping behavior.

Small scripts or SQL queries used solely for analysis are permitted.

If you find an apparent bug, document it first.

If you need to modify anything to prove a hypothesis, create a minimal isolated test or diagnostic script.

---

# 19. FINAL QUESTION TO ANSWER

Conclude the report by answering:

> **If a real-estate professional used this application today to identify market activity, properties, transactions, or potential seller opportunities, which information could they rely on confidently, which information should they treat cautiously, and what must be validated before it is used operationally?**

Support the answer with evidence from the repository and data.

Start by inspecting the repository structure, database/schema, application entry points, scraper, parser, API/data layer and visualization code.

Do not make modifications until the audit map is complete.