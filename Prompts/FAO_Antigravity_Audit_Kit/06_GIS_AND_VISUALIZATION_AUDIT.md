# Stage 5 — GIS, Maps, Analytics and Visualization Accuracy Audit

Goal: verify that maps, KPIs, charts, filters and tables represent the underlying data correctly.

## Geographic audit

Determine how locations are assigned:
- exact cadastral identifier
- official parcel coordinates
- exact address match
- normalized address
- fuzzy match
- geocoder
- municipality centroid
- inferred/approximate point

Classify every mapping strategy using:

- EXACT_CADASTRAL
- EXACT_ADDRESS
- NORMALIZED_ADDRESS
- FUZZY
- MUNICIPALITY_ONLY
- APPROXIMATE
- UNRESOLVED

Check for:
- wrong municipality
- wrong street number
- ambiguous addresses
- invalid coordinates
- points outside plausible Geneva bounds
- centroids presented as exact locations
- duplicate coordinates for unrelated records

## Visualization audit

Inventory every:
- KPI
- chart
- map layer
- marker
- tooltip
- table
- ranking
- filter
- average
- median
- CHF/m² metric
- trend
- percentage

For each trace:

UI component
→ frontend calculation
→ API endpoint/query
→ database fields

## Look for semantic errors

Examples:
- counting rows instead of transactions
- counting parcels as sales
- duplicate transactions inflating totals
- AVG where MEDIAN is intended
- null treated as zero
- wrong denominator
- mixed filtered/unfiltered populations
- grouped sales counted multiple times
- invalid surface used for CHF/m²
- map point implies false precision

## Filter consistency

Test whether all relevant views use the same filtered population when changing:
- date
- municipality
- property type
- transaction category
- price range
- map viewport

## Required output

Create:

`docs/audit/fao/05_GIS_AND_VISUALIZATION.md`

Include this table:

| UI element | Source query | Population | Calculation | Correct? | Confidence | Risk |
|---|---|---|---|---|---|---|

Also include:
1. geographic matching methods
2. false-precision risks
3. KPI correctness
4. chart correctness
5. filter consistency
6. map accuracy
7. unresolved discrepancies

Update `00_AUDIT_INDEX.md`.

Do not redesign the frontend.
