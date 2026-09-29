# Stage 3 — Database, Identity and Provenance Audit

**Target System**: Cytria — Geneva Real Estate & Land Intelligence Platform (`FAO-Scrapper-Visualizer`)  
**Date**: 2026-09-29  
**Audit Stage**: Stage 3 (Database Schema, Entity Identity & Data Lineage Audit)  
**Standard**: Strict Evidence-Based Audit (`00_README_FIRST.md`, `01_MASTER_INSTRUCTIONS.md`, `04_DATABASE_AND_LINEAGE_AUDIT.md`)  
**Status**: VERIFIED & DOCUMENTED  

---

## 1. Executive Summary

This stage evaluates the integrity of the data layer, inspecting table schemas, canonical entity definitions, duplicate risks, referential integrity, and end-to-end data lineage from the user interface back to original legal source documents.

The audit establishes that while basic relational integrity between `transactions` and `enrichments` is structurally sound (0 orphan enrichments in `state.sqlite`), the database and provenance architecture suffers from **systemic lineage breaks**:
1. **Severed Raw Lineage (99.8% Missing)**: Only 14 out of 8,742 transactions in `data/state/state.sqlite` have `raw_text` populated (0.2%). In `data/fao_transactions.db`, the `raw_text` column does not exist at all.
2. **Severed Publication Provenance**: The `publications` table contains 0 rows across both databases, and 100% of transaction rows have `publication_id = NULL`. Original gazette issue numbers, issue dates, and source URLs are completely absent from database records.
3. **Confirmed Rectification Duplication**: Audit diagnostics identified duplicated transactions caused by LDTR rectification notices (e.g. `VA_15296.pdf` and `VA_15296_-_RECTIFICATIF.pdf` creating dual records IDs 16417 and 16418 for the same apartment with different case numbers).
4. **CSV Authority Inversion**: In production, the single-page application and core visualization scripts bypass the SQLite database entirely whenever `geneva_property_transactions.csv` is present on disk.

---

## 2. Table Schema & Cardinality Summary

### Primary Database: `data/state/state.sqlite` (22.6 MB)

| Table | Purpose | Primary Key | Foreign Keys | Uniqueness Constraints | Indexes | Row Count | Provenance Fields |
|---|---|---|---|---|---|---|---|
| **`publications`** | Intended parent table for FAO gazette issues | `id` (INTEGER AUTO) | None | `issue_id UNIQUE` | Implicit PK/Unique | **0 rows** (EMPTY) | `issue_id`, `url`, `file_path`, `sha256` |
| **`transactions`** | Core real-estate transaction records | `id` (INTEGER AUTO) | `publication_id -> publications.id` | `transaction_hash UNIQUE` | `idx_trans_commune`, `idx_trans_parcel`, `idx_trans_cat`, `idx_transactions_hash` | **8,742 rows** | `file_source` (8,741/8,742), `case_number` (8,689/8,742), `raw_text` (14/8,742) |
| **`enrichments`** | Official SITG cadastral & planning geodata | `id` (INTEGER AUTO) | `transaction_id -> transactions.id` (ON DELETE CASCADE) | `transaction_id UNIQUE` | `idx_enrich_egrid` | **8,742 rows** | `egrid`, `plan_rf`, `lien_extrait_rf`, `extrait_rdppf_url`, `match_status`, `enriched_at` |
| **`agencies`** | Real estate agency directory & KPI benchmarks | `id` (TEXT) | None | `id` | `idx_ag_id`, `idx_ag_rank` | **83 rows** | Synthetically curated / hardcoded in Python |
| **`agency_sold_properties`** | Transaction-to-agency reconciliation | Rowid | `agency_id -> agencies.id` | None | `idx_sp_agency`, `idx_sp_fao` | **2,183 rows** | `fao_id`, `reconciliation_level`, `expected_fao_date` |
| **`brokers`** | Individual agent/broker directory | Rowid | `agency_id -> agencies.id` | None | `idx_br_agency`, `idx_br_name` | **93 rows** | Synthetically curated / LinkedIn directory |

---

## 3. Canonical Identity Assessment

| Entity | Canonical Definition in Cytria | Formal Legal / Cadastral Definition | System Divergence / Vulnerability |
|---|---|---|---|
| **Transaction** | Unique combination of `source_category`, `commune`, `case_number`, `address`, `parties`, and `price` (hashed into SHA-256 `transaction_hash`). | A notarized legal act registered at the Registre Foncier (art. 157 LaCC) or authorized under LDTR (art. 39). | If one notarized deed transfers 3 separate parcels, the parser creates 3 separate `TransactionRecord` rows with identical case numbers and prices. |
| **Document** | A single PDF notice on FAO identified by UUID (`notice_{uuid}.pdf`) or LDTR notice (`VA_{id}.pdf`). | An official electronic publication issue or extract from the Cantonal Official Gazette. | 41 PDF documents produced between 2 and 5 database records each. No document-level hash is recorded in `transactions`. |
| **Parcel** | Commune + parcel number string (e.g. `'4642'` or `'6089-104'`). | A legally delimited real property unit recorded on the cadastral plan, identified by an official federal `EGRID` (`CH...`). | Sub-parcel notations for PPE apartments (`-104`) are truncated to base parcel numbers for SITG queries, causing parcel land areas to be conflated with apartment units. |
| **Property Asset** | Classified by `property_type` (`PPE`, `Bien-fonds`, `DDP`, `Copropriété`). | Object of real-estate ownership under the Swiss Civil Code (CC art. 655). | Free-text notice parsing frequently leaves `property_type` as NULL or misclassified until downstream heuristic scripts run. |
| **Party / Person** | Raw string in `seller` or `buyer` column. | Natural person, legal entity, or undivided estate (*hoirie* / *consorts*). | No entity resolution or deduplication exists. An entity appearing as "SPC SA" and "SPC SOCIETE DE PARTICIPATION ET DE CONTROLE SA" are treated as unrelated strings. |

---

## 4. Duplicate Risk Analysis

Diagnostic queries executed on `data/state/state.sqlite` revealed the following duplicate patterns:

### 1. Re-ingested Rectification Errata Duplicates (VERIFIED)
- **Concrete Evidence**:
  - `ID 16417`: `'appartement n° 4.04 de 4 pièces au 1er étage'`, Parties: `Mme Francesca PAPARO` -> `PASCHA S.A.`, Price: `CHF 319,090`, Case: `VA 15291`, File: `VA_15296.pdf`.
  - `ID 16418`: `'appartement n° 4.04 de 4 pièces au 1er étage'`, Parties: `Mme Francesca PAPARO` -> `PASCHA S.A.`, Price: `CHF 319,090`, Case: `VA 15296`, File: `VA_15296_-_RECTIFICATIF.pdf`.
- **Finding**: When an erratum is published under LDTR, minor variations in extracted case numbers cause the parser to generate two independent database records for the identical economic transaction.

### 2. Multi-Share Legitimate Transfers (VERIFIED)
- 20 clusters of identical parcel + date + price were examined (e.g., parcel `2563-20` on `13 février 2026` with price `CHF 100`).
- **Finding**: Detailed inspection confirmed these are **distinct legal transactions** transferring fractional co-ownership shares in an underground garage facility (*Villereuse*) with distinct case numbers (`2026/8928/0`, `2024/13002/0`). These are not software duplicates.

### 3. Hash Implementation Conflict (VERIFIED)
- `models.py:35-46` computes 64-char SHA-256 hashes (`norm_commune + norm_case + norm_addr + ...`).
- `sync_engine.py:26-32` computes a 16-char truncated hash (`commune | parcel | date | price | ...`).
- **Finding**: While 8,741 records in SQLite use the 64-character hash, the existence of a competing hash calculation in `sync_engine.py` creates a permanent risk of deduplication failure during background sync.

---

## 5. Referential Integrity & Schema Health

| Diagnostic Check | Primary DB (`state.sqlite`) | Secondary DB (`fao_transactions.db`) | Status |
|---|---|---|---|
| **`PRAGMA foreign_key_check`** | 0 violations | 0 violations | **HEALTHY** |
| **Orphan `enrichments` records** | 0 orphan records | N/A (no enrichments table) | **HEALTHY** |
| **Transactions without enrichment** | 0 unlinked transactions | N/A | **HEALTHY** |
| **Geocoded Enrichments** | 8,364 / 8,742 (95.7%) | 8,350 / 8,728 (95.7%) | **VERIFIED** |
| **Ungeocoded (`not_found`)** | 378 / 8,742 (4.3%) | 378 / 8,728 (4.3%) | **VERIFIED** |
| **Test Artifact in Production** | `id=8145`, hash=`'test_hash_1'` | `id=8145`, hash=`'test_hash_1'` | **POLLUTED** |
| **Row Count Discrepancy** | **8,742 rows** | **8,728 rows** (14 fewer) | **DESYNCHRONIZED** |

---

## 6. End-to-End Source Lineage Tracing

A full trace was attempted from the visualizer UI down to the official FAO document for sample transaction **ID 16947**:

```
[1] UI Display (index.html / map card)
    └── Values: "Pregny-Chambésy", Parcelle 37, CHF 1'320'000, 25 septembre 2026
    └── Link Status: VERIFIED (Rendered from inline DATA constant)

[2] Query / API Layer (server.py / map_builder.py)
    └── map_builder.py queries CSV first, falling back to SQLite
    └── Link Status: PARTIAL (Bypasses SQLite database whenever CSV is present)

[3] Database Row (transactions table)
    └── Row: id=16947, commune='Pregny-Chambésy', parcel_number='37', price_chf=1320000.0,
             file_source='notice_71646949-2753-42bb-a3c0-87c31f361e55.pdf', publication_id=NULL
    └── Link Status: VERIFIED

[4] Database Row (enrichments table)
    └── Row: transaction_id=16947, egrid='CH447043812836', lon=6.14321, lat=46.23412,
             zone_code='5', surface_official_m2=1240.0, match_status='matched_parcel'
    └── Link Status: VERIFIED

[5] Raw Extracted Text (raw_text column)
    └── Value: NULL (Only 14 of 8,742 rows have raw_text stored)
    └── Link Status: BROKEN (Original text extraction is missing in DB)

[6] Raw Source Document (data/raw/transactions/)
    └── File: data/raw/transactions/notice_71646949-2753-42bb-a3c0-87c31f361e55.pdf
    └── Link Status: VERIFIED (File exists on disk, size 837 KB)

[7] Authoritative Cantonal Publication (FAO Portal)
    └── URL: https://fao.ge.ch/avis/71646949-2753-42bb-a3c0-87c31f361e55
    └── Link Status: PARTIAL (UUID is derivable from filename, but no URL or gazette issue is in DB)
```

---

## 7. Provenance Matrix Evaluation

| Provenance Attribute | Status | Coverage | Location |
|---|---|---|---|
| **FAO Publication Issue Number** | **NOT IMPLEMENTED** | 0% (0 / 8,742) | Expected in `publications.issue_no` (table empty) |
| **Source Portal URL** | **NOT IMPLEMENTED** | 0% (0 / 8,742) | Expected in `publications.url` |
| **Notice Date** | **VERIFIED** | 100% (8,742 / 8,742) | `transactions.notice_date` |
| **Original Notice Filename** | **VERIFIED** | 100% (8,741 / 8,742) | `transactions.file_source` |
| **Source Document Checksum (SHA-256)**| **NOT IMPLEMENTED** | 0% (0 / 8,742) | Expected in `publications.sha256` |
| **Registry Case Number** | **VERIFIED** | 99.4% (8,689 / 8,742) | `transactions.case_number` |
| **Raw Unparsed Text** | **BROKEN** | 0.2% (14 / 8,742) | `transactions.raw_text` (NULL on 8,728 rows) |
| **Extraction Timestamp** | **PARTIAL** | 100% | `transactions.created_at` (DB insertion timestamp) |
| **Parser Version** | **NOT IMPLEMENTED** | 0% | No schema field |
| **Enrichment Provenance & Match Mode** | **VERIFIED** | 100% (8,742 / 8,742) | `enrichments.match_status`, `enriched_at` |

---

## 8. Prioritized Issues

1. **[P0 - LIN-01] Destructive Full-Table CSV Overwrite (`sync_to_sqlite.py`)**:
   [`scripts/sync_to_sqlite.py`](file:///c:/Users/LocalUser/kDrive/DEV/Sbrot/Cytria_FAO_Scrapper_Intelligence_AGY/scripts/sync_to_sqlite.py#L23) executes `df_txs.to_sql('transactions', conn, if_exists='replace')`, dropping primary keys, unique constraints, and foreign key definitions.
2. **[P0 - LIN-02] 99.8% Loss of Raw Text Extraction in Database**:
   `raw_text` is NULL for 8,728 transactions. Verification of extracted values against original wording requires reading external PDF files on disk rather than querying the database.
3. **[P1 - LIN-03] Complete Severance of Publication Metadata**:
   The `publications` table is completely unpopulated, destroying provenance to official FAO publication issues, bulletin dates, and web URLs.
4. **[P1 - LIN-04] Rectification-Induced Transaction Duplication**:
   Errata notices published as separate documents create duplicate transaction entries when extracted case numbers vary slightly.
5. **[P2 - LIN-05] Test Record Artifact in Production Database**:
   Mock record `id=8145` with `transaction_hash='test_hash_1'` is present in production tables.

---

## 9. Recommendations

1. **Populate `raw_text`**: Run an offline backfill script using the existing 8,756 PDFs to populate `raw_text` across all 8,742 database records.
2. **Deprecate Destructive CSV Overwrites**: Prohibit `if_exists='replace'` in `sync_to_sqlite.py`. Establish SQLite as the single authoritative source of truth.
3. **Establish Publication Issue Provenance**: Update the scraper to populate `publications` with gazette issue dates, URLs, and file hashes, linking transactions via `publication_id`.
4. **Normalize Dates to ISO-8601**: Add an indexed `notice_date_iso` column (`YYYY-MM-DD`) to enable correct chronological ordering.

---

*Stage 3 Database, Identity and Provenance Audit is complete. Proceed to Stage 4: Parser and Data Quality Audit.*
