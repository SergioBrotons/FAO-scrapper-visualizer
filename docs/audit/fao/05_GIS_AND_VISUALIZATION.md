# Stage 5 — GIS, Maps, Analytics and Visualization Accuracy Audit

**Target System**: Cytria — Geneva Real Estate & Land Intelligence Platform (`FAO-Scrapper-Visualizer`)  
**Date**: 2026-09-29  
**Audit Stage**: Stage 5 (GIS, Geocoding, Analytics & UI Metrics Audit)  
**Standard**: Strict Evidence-Based Audit (`00_README_FIRST.md`, `01_MASTER_INSTRUCTIONS.md`, `06_GIS_AND_VISUALIZATION_AUDIT.md`)  
**Status**: VERIFIED & DOCUMENTED  

---

## 1. Executive Summary

This stage evaluates the geographic geocoding engine ([`sitg_client.py`](file:///c:/Users/LocalUser/kDrive/DEV/Sbrot/Cytria_FAO_Scrapper_Intelligence_AGY/src/fao_transactions/cadastre/sitg_client.py), [`enricher.py`](file:///c:/Users/LocalUser/kDrive/DEV/Sbrot/Cytria_FAO_Scrapper_Intelligence_AGY/src/fao_transactions/cadastre/enricher.py)) and the visual intelligence application ([`map_builder.py`](file:///c:/Users/LocalUser/kDrive/DEV/Sbrot/Cytria_FAO_Scrapper_Intelligence_AGY/src/fao_transactions/visualization/map_builder.py), [`index.html`](file:///c:/Users/LocalUser/kDrive/DEV/Sbrot/Cytria_FAO_Scrapper_Intelligence_AGY/index.html)), measuring spatial precision, KPI calculation faithfulness, and visual presentation risks.

Key findings include:
1. **P0 10% Cantonal Volume Distortion in UI Banner**: Due to the decimal stripping defect in `parse_price` (ID 4837 inflated to CHF 1.875 billion), the master banner KPI displays **CHF 18.81 Billion**, of which **CHF 1.875 Billion (9.97%) is fictitious inflation from a single transaction**.
2. **False Precision via Centroid Stacking**: 87.7% of locations are matched via parcel centroid. In dense multi-family residential complexes, up to **53 distinct sales transactions over 3 years are stacked at the identical coordinate point**, giving a misleading visual impression of a single event unless clusters are expanded.
3. **Arbitrary Truncation of Price/m²**: [`map_builder.py:7087-7095`](file:///c:/Users/LocalUser/kDrive/DEV/Sbrot/Cytria_FAO_Scrapper_Intelligence_AGY/src/fao_transactions/visualization/map_builder.py#L7087-L7095) clamps price/m² between 1,500 and 80,000 CHF/m². Legitimate ultra-luxury transactions (e.g. Cologny > 80k CHF/m²) or discounted social/family mutations (< 1,500 CHF/m²) have their price/m² silently nullified.
4. **Hardcoded Property Override**: Production code contains a hardcoded override for record ID 246 / parcel `4642-104` (Saut-du-Loup 16), forcing living area to 92 m² and construction year to 2016.

---

## 2. Geographic Matching Methods & Spatial Accuracy

| Strategy Classification | Internal Match Tag | Count | Pct of DB | Precision | Failure Modes / Risks |
|---|---|---|---|---|---|
| **EXACT_CADASTRAL** | `matched_parcel` | 7,668 | 87.7% | High (Centroid of cadastral polygon) | Sub-parcels (e.g. `6089-104`) truncated to base plot `6089`. All apartments in a building share the same coordinate. |
| **EXACT_ADDRESS** | `matched_address` | 696 | 8.0% | Medium-High (Street entrance point) | LDTR notices without parcel numbers matched against `CAD_ADRESSE`. Multi-entrance parcels resolve to primary entrance. |
| **UNRESOLVED** | `not_found` | 378 | 4.3% | None (No coordinates assigned) | Omitted from map visualization. Includes unparseable parcel numbers or missing street addresses. |

### Spatial Coordinate Bounds Verification:
- Longitude range: `[5.95920, 6.30930]` (Valid Geneva Canton bounds: ~5.95 to 6.31).
- Latitude range: `[46.13197, 46.31649]` (Valid Geneva Canton bounds: ~46.13 to 46.32).
- Zero records fall outside the territory of the Republic and Canton of Geneva.

### False-Precision Risk (Coincident Coordinate Clusters):
Because 87.7% of transactions resolve to parcel centroids, multiple sales occurring in the same building plot over the 3-year audit window collapse to identical points:
- **(6.10562, 46.20523)**: **53 transactions stacked** (large residential building complex in Vernier/Lignon).
- **(6.14026, 46.21018)**: **50 transactions stacked** (multi-unit development in Geneva Plainpalais).
- **(6.16362, 46.17907)**: **40 transactions stacked** (Carouge multi-family parcel).

---

## 3. UI Analytics, KPIs and Calculations Trace

| UI Element | Source Query / Data Column | Population | Frontend Calculation | Faithfulness / Correctness | Confidence | Primary Risk |
|---|---|---|---|---|---|---|
| **Total Volume (Banner)** | `sum(price_chf)` in `rows` | 8,742 total (6,377 priced) | `sum(r.price_chf) / 1e9` | **FALSE (INFLATED)** | LOW | Inflated by 1.875 billion CHF due to ID 4837 decimal bug. |
| **Total Transactions (Banner)** | `len(rows)` | 8,742 rows | `len(rows)` | **APPROXIMATE** | MEDIUM | Counts database rows rather than unique economic transactions (41 multi-parcel notices produce multiple rows). |
| **Priced Sales (Banner)** | `count(price_chf > 0)` | 6,377 rows | `sum(1 for r if r.price_chf)` | **ACCURATE** | HIGH | Correctly identifies transactions with disclosed cash consideration. |
| **PPE Apartments Count** | `classify_typology(r) == 'PPE'` | 1,401 rows | Heuristic classification | **APPROXIMATE** | MEDIUM | Relies on keyword matching in notice text; misclassifies some mixed-use units. |
| **Villas / Houses Count** | `classify_typology(r) == 'VILLA'` | 1,120 rows | Heuristic classification | **ACCURATE** | HIGH | Matches "villa", "maison individuelle", "habitation à un seul logement". |
| **Rive Gauche / Rive Droite** | `classify_rive(r)` | 8,742 rows | Commune lookup + latitude threshold (`lat > 46.206`) | **ACCURATE** | HIGH | Faithful macro-zoning dividing canton along the Rhône/Lake. |
| **Price / m² (Map Cards & CMA)** | `price_chf / surface` | 3,857 rows | Clamped: `1500 <= sqm <= 80000` | **DISTORTED** | LOW | 519 PPE units distorted by plot land surfaces; extreme values silently discarded. |
| **Seller Mandate Radar Score** | `compute_mandate_score(r)` | 8,742 rows | Point-based keyword heuristic | **HEURISTIC** | MEDIUM | Rule-based algorithm based on succession/hoirie keywords; not ground-truth verified. |
| **Developer Opportunity Score**| `compute_development_potential(r)`| 8,742 rows | Zone 5 + plot area + building year | **HEURISTIC** | MEDIUM | Useful planning indicator, but assumes development feasibility without zoning law review. |
| **Agency League Table** | `GENEVA_AGENCIES_DATA` | 83 agencies | Hardcoded Python data dictionary | **SYNTHETIC / CURATED**| LOW | Static benchmark; not dynamically derived from verified FAO transaction matches. |

---

## 4. Visual Semantic Errors Identified

1. **Summing Fictitious Extreme Values**:
   Total volume in `index.html` is computed via plain addition `sum(price_chf)`. Because ID 4837 has an erroneous price of 1,875,000,000 CHF, the displayed volume of **18.81 Billion CHF** is 10% overstated.
2. **Hardcoded Overrides in Generic Pipeline**:
   Lines 7067–7075 of [`map_builder.py`](file:///c:/Users/LocalUser/kDrive/DEV/Sbrot/Cytria_FAO_Scrapper_Intelligence_AGY/src/fao_transactions/visualization/map_builder.py#L7067-L7075) explicitly inject hardcoded values for parcel `4642-104`:
   ```python
   if r.get("id") == 246 or (str(r.get("parcel_number")) == "4642-104"):
       surf_hab = 92.0
       r["surface_habitable_m2"] = 92.0
       r["building_year"] = 2016
       r["rooms"] = 4.0
   ```
   Injecting bespoke exceptions into visualization builders undermines trustworthiness across the remaining 8,741 records.
3. **Arbitrary Filtering of Outlier Unit Prices**:
   When calculating price per square meter, values under 1,500 CHF/m² or above 80,000 CHF/m² are set to `None`. This arbitrarily conceals real luxury transactions and subsidized social housing mutations from the user interface.

---

## 5. Filter Consistency Audit

The single-page application implements client-side filtering via JavaScript:
- **Cross-Filter Population**: All visual cards, map markers, and KPI charts share the central `filteredData` array in memory. When a commune or date filter is adjusted, the map markers and summary statistics update consistently.
- **Viewport Binding**: Viewport filtering is decoupled from aggregate KPI counters (banner counters show cantonal totals rather than viewport-bounded totals, which may confuse users expecting metrics to reflect the visible map area).

---

## 6. Recommendations

1. **Sanitize Cantonal Volume Aggregate**: Re-parse price values to eliminate the 1.875 billion CHF outlier before computing `__TOTAL_VOLUME__`.
2. **Eliminate Hardcoded Code Overrides**: Remove bespoke `if r.get("id") == 246` blocks from `map_builder.py`; fix data issues at the parser or database migration layer.
3. **Implement Spiderfier for Coincident Pins**: Use `OverlappingMarkerSpiderfier` in Leaflet to separate the up to 53 stacked transaction pins at parcel centroids.
4. **Display Data Lineage in Map Popups**: In transaction popups, explicitly label whether `surface_m2` is "Notarized FAO Notice", "SITG Cadastral Plot", or "Synthetic Estimate".

---

*Stage 5 GIS, Maps, Analytics and Visualization Accuracy Audit is complete. Proceed to Stage 6: Confidence Model and Validation Audit.*
