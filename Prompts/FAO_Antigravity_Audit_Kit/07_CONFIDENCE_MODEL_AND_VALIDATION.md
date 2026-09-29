# Stage 6 — Confidence Model and Ground-Truth Validation

Goal: quantify trust without inventing a fake single confidence number.

## Audit current confidence handling

Find any existing:
- confidence field
- parser score
- geocoding score
- validation status
- verification flag
- source reliability indicator

Explain exactly how it is computed.

## Design a decomposable confidence model

Evaluate at least:

### Source confidence
Was an authoritative FAO source retained and validated?

### Extraction confidence
Was the field deterministically extracted or heuristically inferred?

### Identity confidence
Is the transaction uniquely identified?

### Geographic confidence
Is the location exact, normalized, fuzzy or approximate?

### Completeness confidence
Are important fields missing?

### Consistency confidence
Do related fields agree?

Suggested labels:
- VERIFIED
- HIGH
- MEDIUM
- LOW
- UNVERIFIED
- CONFLICT
- INCOMPLETE

Every label must be explainable.

Do not create arbitrary percentages unless statistically calibrated.

## Golden-sample validation

Create a stratified sample across:
- recent transactions
- older transactions
- several municipalities
- high price
- low price
- PPE/apartments
- houses
- land
- multi-parcel cases
- missing-field records
- low-confidence records

For each sampled case compare:

source FAO document
vs
raw extraction
vs
normalized database
vs
frontend display

Where enough evidence exists calculate field-level accuracy, e.g.:

- price accuracy
- date accuracy
- parcel accuracy
- address accuracy
- geolocation exactness
- property type accuracy

Keep measured accuracy separate from heuristic confidence.

## Required output

Create:

`docs/audit/fao/06_CONFIDENCE_AND_VALIDATION.md`

Include:
1. existing confidence mechanisms
2. proposed confidence dimensions
3. explainability rules
4. golden-sample method
5. sample results
6. field-level measured accuracy where possible
7. unresolved validation limits
8. UI recommendations for representing uncertainty

Update `00_AUDIT_INDEX.md`.
