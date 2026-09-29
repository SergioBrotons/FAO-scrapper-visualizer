# Stage 3 — Database, Identity and Provenance Audit

Goal: determine whether database records represent the source faithfully and can be traced back.

## Inspect the schema

For every important table document:
- purpose
- primary key
- foreign keys
- uniqueness rules
- nullable fields
- indexes
- cardinality
- source/provenance fields

## Determine canonical identities

Answer:
- What defines one transaction?
- What defines one document?
- What defines one parcel?
- What defines one property?
- What defines one party/person/entity?
- Can one FAO transaction generate several database rows?
- Can multiple FAO publications refer to the same economic transaction?

## Duplicate risk

Test for possible duplicates by:
- FAO identifier
- source URL
- document hash
- transaction date + price + address
- parcel + date
- document filename
- import/run ID

Do not delete duplicates. Report them.

## Referential integrity

Look for:
- orphan records
- broken foreign keys
- inconsistent municipality relationships
- missing source links
- unresolved parcel relations
- malformed IDs

## Source lineage

For sampled UI records, attempt:

UI value
→ API/query
→ database row
→ normalized extraction
→ raw extraction
→ source FAO document

For every link mark:
- VERIFIED
- PARTIAL
- BROKEN
- NOT IMPLEMENTED

## Provenance expectations

Assess whether important records retain:
- FAO/publication identifier
- source URL
- publication date
- original document filename
- document hash
- extraction timestamp
- parser version
- raw text/structured extraction
- normalization provenance
- enrichment provenance

## Required output

Create:

`docs/audit/fao/03_DATABASE_AND_LINEAGE.md`

Include:
1. schema summary
2. canonical identity assessment
3. duplicate analysis
4. referential-integrity findings
5. provenance coverage
6. lineage tests
7. P0/P1 issues
8. recommended schema/provenance improvements

Update `00_AUDIT_INDEX.md`.

Do not migrate the database.
