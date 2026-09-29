# Stage 4 — Parser, Extraction and Data Quality Audit

Goal: establish what fields are extracted, how, and how accurate they are.

## Build a field inventory

For every relevant extracted field record:

| Field | Source | Extraction method | Normalization | Validation | Failure risk |
|---|---|---|---|---|---|

Possible fields include:
- publication date
- transaction date
- price
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

## Classify extraction method

Examples:
- deterministic parser
- regex
- positional text
- table parser
- OCR
- heuristic
- fuzzy matching
- LLM
- lookup/enrichment
- manual entry

Do not equate “value produced” with “value correct”.

## Search specifically for edge cases

- multiple prices in one document
- multiple parcels
- multiple buyers/sellers
- ownership fractions
- PPE
- bundled transactions
- amendments/corrections
- CHF separators
- date ambiguity
- OCR digit errors
- missing fields
- unusual wording
- malformed PDFs

## Completeness funnel

Measure, where possible:

FAO listings
→ documents downloaded
→ valid documents
→ parsed documents
→ canonical transactions
→ cadastral matches
→ geocoded records
→ displayed records

Report counts and loss rates between stages.

## Temporal coverage

Measure:
- earliest transaction date
- latest transaction date
- earliest publication date
- latest publication date
- counts by month
- counts by municipality
- missing weeks/months
- suspicious drops/spikes

Do not assume gaps equal zero market activity.

## Cross-field validation

Check possible rules such as:
- price > 0
- plausible dates
- municipality/postal code consistency
- parcel belongs to municipality
- no impossible coordinates
- CHF/m² only with compatible price + area
- duplicate IDs
- duplicate hashes
- duplicate transaction signatures

Flag anomalies. Do not auto-correct.

## Required output

Create:

`docs/audit/fao/04_PARSER_AND_DATA_QUALITY.md`

Include:
1. field inventory
2. extraction risk by field
3. completeness funnel
4. temporal coverage
5. anomalies
6. cross-field validation
7. highest-risk parser assumptions
8. validation priorities

Update `00_AUDIT_INDEX.md`.
