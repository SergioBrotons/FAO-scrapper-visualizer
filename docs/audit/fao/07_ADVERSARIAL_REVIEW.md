# Stage 7 — Adversarial / 10th-Man Review

**Target System**: Cytria — Geneva Real Estate & Land Intelligence Platform (`FAO-Scrapper-Visualizer`)  
**Date**: 2026-09-29  
**Audit Stage**: Stage 7 (Adversarial Robustness & Skeptical Senior Review)  
**Standard**: Strict Evidence-Based Audit (`00_README_FIRST.md`, `01_MASTER_INSTRUCTIONS.md`, `08_ADVERSARIAL_REVIEW.md`)  
**Status**: VERIFIED & DOCUMENTED  

---

## 1. Executive Summary

This adversarial review assumes the persona of a skeptical senior architect tasked with answering the challenge:  
> *“The application looks visually stunning and commercially convincing, but can its data be trusted in high-stakes institutional real-estate underwriting?”*

The investigation substantiates significant portions of that skeptical claim. While the system undeniably possesses a legitimate repository of **8,756 genuine cantonal PDFs** covering 36 months of real market transactions across all 46 Geneva communes, **the application layer presents several critical metrics that are demonstrably corrupted, synthetically altered, or visually overstated**:
- The total cantonal transaction volume of **18.81 Billion CHF** displayed in the master banner is distorted by nearly **2 Billion CHF (9.97%)** due to a single decimal-point parsing bug on an apartment in Geneva (`ID 4837`).
- More than **500 apartment records** display distorted price/m² metrics because the platform assigned whole-building land plots (up to 3,400 m²) to individual apartment units, and then labeled the resulting figures as notarized deed surfaces (`"NOTARIEE_FAO"`).
- The Agency League Table and broker ranking system—presented as official transaction intelligence—relies on **hardcoded static Python dictionaries** rather than dynamic transaction attribution.
- Production map builder code contains **hardcoded bespoke overrides** for specific properties (e.g. Saut-du-Loup 16).

---

## 2. Adversarial Hypotheses & Evidence Matrix

| # | Skeptical Hypothesis | Evidence FOR (Skeptical Proof) | Evidence AGAINST (Counter-Evidence) | Status | Severity |
|---|---|---|---|---|---|
| **H1** | **Cantonal total market volume in the UI banner is substantially overstated.** | `ID 4837` (apartment with loggia) has an extracted price of **CHF 1,875,000,000** due to decimal stripping in `parse_price`. This single error inflates cantonal volume from CHF 16.93B to CHF 18.81B (9.97% of total volume). | 6,376 of the 6,377 priced transactions are genuine prices; 99.5% of standard-format prices are accurately captured. | **CONFIRMED** | **P0** |
| **H2** | **Visualized Price/m² metrics are contaminated by cadastral land plot collisions.** | 519 PPE apartment records inherit whole-building cadastral land plots > 500 m² (up to 3,400 m²), producing unit prices of 200–500 CHF/m². `map_builder.py` defaults unpopulated surfaces to `"NOTARIEE_FAO"`, misleading users. | For single-family villas and land plots, SITG cadastral surfaces match notarized deed areas faithfully. | **CONFIRMED** | **P0** |
| **H3** | **Unattended scraper runs silently abort during anti-bot challenges without acquiring data.** | `is_blocked()` timeout in `browser.py:182-194` logs a warning and returns cleanly without raising an error. The scraper detects 0 links on the challenge page, logs "No more notices found", and exits with status 0. | When executed interactively with a visible browser by a human operator, challenges are solved and notices download. | **CONFIRMED** | **P0** |
| **H4** | **Database records cannot be audited against raw source texts due to severed lineage.** | In `state.sqlite`, 8,728 of 8,742 transactions have `raw_text = NULL` (99.8% missing). In `fao_transactions.db`, the column does not exist. `publications` has 0 rows. | 8,756 original notice PDFs remain intact on disk in `data/raw/` and can be inspected or re-parsed offline. | **CONFIRMED** | **P1** |
| **H5** | **Database synchronization scripts destroy relational integrity through full-table replacement.** | `scripts/sync_to_sqlite.py:23` executes `df_txs.to_sql('transactions', conn, if_exists='replace')`, dropping primary keys, unique constraints, and foreign key definitions. | The raw CSV contains full record rows, and `state.sqlite` currently passes `PRAGMA foreign_key_check`. | **CONFIRMED** | **P0** |
| **H6** | **The platform suffers from municipal or territorial selection bias.** | 378 transactions are ungeocoded (`not_found`), and historical parcel 8 in Carouge failed to match SITG. | Transactions are actively present across all 46 Geneva communes in proportion to population (Genève 2,024, Vernier 541, Lancy 448). | **DISPROVEN** | — |
| **H7** | **Agency League Tables and broker rankings are synthetically fabricated rather than computed.** | `GENEVA_AGENCIES_DATA` in `agency_ranking.py` is a 1,260-line hardcoded static Python dictionary of 83 agencies, ratings, and estimated discount rates. | Real transaction links exist in `agency_sold_properties` for 2,183 sales reconciled against agencies. | **CONFIRMED** | **P1** |
| **H8** | **Production visualization code includes hardcoded property overrides.** | Lines 7067–7075 of `map_builder.py` explicitly hardcode surface (92 m²), year (2016), rooms (4), and source (`"NOTARIEE_FAO"`) for parcel `4642-104`. | The remaining 8,741 records are evaluated via automated functions. | **CONFIRMED** | **P1** |
| **H9** | **Cantonal errata and rectification notices produce duplicate transaction entries.** | LDTR notice `VA_15296.pdf` and rectification notice `VA_15296_-_RECTIFICATIF.pdf` generated two independent rows (IDs 16417 and 16418) for the exact same apartment. | `transaction_hash UNIQUE` prevents exact-string duplicates; multi-row clusters for parcel `2563-20` were proven to be legitimate share transfers. | **CONFIRMED** | **P1** |
| **H10** | **The production database contains mock test artifacts.** | Transaction `id=8145` with hash `'test_hash_1'` is present in both production SQLite databases. | It represents only 1 record out of 8,742 total rows. | **CONFIRMED** | **P2** |

---

## 3. Strongest Reasons NOT to Trust the System (The Skeptic's Case)

1. **Catastrophic Outlier Propagation**: The fact that a single apartment with a loggia could enter the database as a **1.875 Billion CHF sale** and propagate unflagged into the master executive dashboard proves that the system lacks automated sanity checks and outlier gates.
2. **False Surface Attribution**: Labeling cadastral land plot surfaces (e.g. a 2,500 m² plot) as a `"NOTARIEE_FAO"` living area on an apartment unit directly breaches data integrity and would cause an institutional real-estate analyst to make catastrophic valuation errors.
3. **Destructive Overwrite Pattern**: A platform where running an operational script (`sync_to_sqlite.py`) replaces the entire primary database table via `if_exists='replace'` from an unvalidated CSV file cannot guarantee long-term data consistency.
4. **Synthetic Marketing Layer**: Presenting static hardcoded agency profiles and broker market shares as dynamic intelligence undermines professional credibility.

---

## 4. Strongest Reasons TO Trust the System (The Defender's Case)

1. **Genuine Primary Document Foundation**: The underlying corpus is authentic. 8,756 genuine cantonal PDFs are physically present on disk, spanning exactly 36 months of real-world Geneva property transfers without synthetic document generation.
2. **Deterministic Extraction Baseline**: For 99.5% of standard-format notices, party names, registry case numbers, and transaction prices are extracted faithfully from cantonal texts.
3. **Official SITG Integration**: The integration with the State of Geneva's official cadastral FeatureServers (`vector.sitg.ge.ch`) is real and authoritative. 95.7% of transactions resolve to genuine cadastral polygons, federal EGRIDs, and cantonal planning zones.
4. **Complete Cantonal Scope**: All 46 communes of Geneva are represented without geographic blind spots or municipal favoritism.

---

## 5. Unresolved Questions Requiring Post-Audit Resolution

1. **Volume of Decimally Inflated Transactions**: Beyond ID 4837, how many other notices have had prices inflated by `.00` centime stripping?
2. **Reconciliation Depth of Agency BI**: Exactly how many of the 2,183 records in `agency_sold_properties` represent verified notary deed matches vs fuzzy address heuristics?
3. **Historical Rectification Scope**: How many official errata currently exist in the archive that failed to update their original target records?

---

*Stage 7 Adversarial / 10th-Man Review is complete. Proceed to Stage 8: Final Audit Synthesis and Prioritized Remediation Roadmap.*
