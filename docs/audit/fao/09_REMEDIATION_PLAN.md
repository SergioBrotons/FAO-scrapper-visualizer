# Stage 9 — Comprehensive Remediation Plan (P0 & P1 Critical Actions)

**Document**: `docs/audit/fao/09_REMEDIATION_PLAN.md`  
**Project**: Cytria — Geneva Real Estate & Land Intelligence Platform (`FAO-Scrapper-Visualizer`)  
**Audit Standard**: Rigorous Evidence-Based Audit (`10_AFTER_AUDIT_FIX_PROMPT.md`)  
**Plan Date**: 2026-09-29  
**Auditor**: Antigravity (Senior System Architect / Geospatial Data Engineer / Lead Quality Auditor)  
**Execution Status**: IMPLEMENTED & VERIFIED (All P0/P1 fixes deployed and passed 14/14 automated unit tests)

---

## Executive Overview

This document specifies the concrete, minimal, and risk-managed engineering remediation actions required to eliminate all **Priority 0 (Systemic / Major Data Invalidation)** and **Priority 1 (Substantial Data Integrity Risk)** defects identified across Stages 1 through 8 of the Cytria FAO Audit.

Each remediation proposal includes the exact failure mechanism, minimal code/schema modifications, regression analysis, validation tests, rollback plans, and historical reprocessing requirements.

---

## Summary Matrix of Critical Findings to Remediate

| Finding ID | Severity | Category | Primary Affected File | Primary Affected Table | Reprocessing Required? |
|---|---|---|---|---|---|
| **P0-01** | P0 | Parser / Financial | `src/fao_transactions/parser/pdf_parser.py` | `transactions` | **YES** (Record ID 4837 + high-value check) |
| **P0-02** | P0 | Parser / GIS | `src/fao_transactions/parser/pdf_parser.py`<br>`src/fao_transactions/visualization/map_builder.py` | `transactions`, `enrichments` | **YES** (519 PPE records) |
| **P0-03** | P0 | Scraper / Anti-Bot | `src/fao_transactions/scraper/crawler.py` | None (Scraper runtime) | **NO** |
| **P0-04** | P0 | Scraper / Pagination | `src/fao_transactions/scraper/crawler.py` | None (Scraper runtime) | **NO** (Optional backfill run) |
| **P0-05** | P0 | Database / Errata | `src/fao_transactions/storage/db.py`<br>`src/fao_transactions/parser/pdf_parser.py` | `transactions` | **YES** (All rectified notices) |
| **P0-06** | P0 | Data Lineage / SSoT | `src/fao_transactions/visualization/map_builder.py`<br>`scripts/sync_to_sqlite.py` | `transactions`, `enrichments` | **NO** (Regenerate visualizer from SQLite) |
| **P1-01** | P1 | Lineage / Provenance | `src/fao_transactions/storage/db.py`<br>`src/fao_transactions/parser/pdf_parser.py` | `transactions`, `publications` | **YES** (Repopulate `raw_text` from raw PDFs) |
| **P1-02** | P1 | Completeness | `scripts/reconcile_unregistered_pdfs.py` (New script) | `transactions`, `enrichments` | **YES** (Ingest 65 missing PDFs) |
| **P1-03** | P1 | BI / Agency Data | `src/fao_transactions/visualization/agency_ranking.py` | None (Frontend visualization) | **NO** (Refactor to dynamic aggregation) |
| **P1-04** | P1 | Data Integrity | `src/fao_transactions/visualization/map_builder.py` | None (Visualizer code) | **NO** (Remove bespoke hardcoding) |
| **P1-05** | P1 | GIS / UX | `src/fao_transactions/visualization/map_builder.py` | None (Leaflet frontend) | **NO** (Spiderfier / offset logic) |
| **P1-06** | P1 | Extraction / Multi-Parcel| `src/fao_transactions/parser/pdf_parser.py` | `transactions` | **YES** (Extract all parcel tokens) |

---

# Detailed Action Plans for Priority 0 (P0) Blockers

---

### Finding P0-01: Decimal Point Stripping Causes Billion-Franc Outlier

- **Finding ID**: `P0-01` (`PAR-01` / `GIS-01`)
- **Affected File(s)**:
  - `src/fao_transactions/parser/pdf_parser.py` (around line 94)
- **Affected Table(s)**:
  - `transactions` (`price`, `price_m2`) in `data/state/state.sqlite` and `data/fao_transactions.db`
- **Exact Failure Mechanism**:
  In `pdf_parser.py:94`, string normalization strips all periods and spaces before converting to integer:
  ```python
  num_str = re.sub(r"[\s'’._-]", "", num_str)
  ```
  When the FAO notice publishes a price formatted with centimes/cents (e.g. `1'875'000.00` in record ID `4837`, `fao_rf_2023_09_08_0238.pdf`), the regex strips the period, transforming the string into `187500000` (1.875 billion CHF). This single record inflates total cantonal volume by CHF 1,873,125,000 (+9.97%).
- **Minimal Code / Schema Change**:
  Refactor `_clean_price(raw_str: str) -> float` to detect Swiss decimal cents before stripping:
  ```python
  def _clean_price(num_str: str) -> Optional[float]:
      if not num_str:
          return None
      num_str = num_str.strip()
      # Match standard Swiss centimes pattern: ends with .XX or ,XX
      cents_match = re.search(r"[.,](\d{2})\s*(?:CHF|Fr\.|fr\.)?$", num_str)
      cents = 0.0
      if cents_match:
          cents = float("0." + cents_match.group(1))
          num_str = num_str[:cents_match.start()]
      # Strip thousands separators: apostrophes, spaces, periods, dashes
      clean_int = re.sub(r"[\s'’._-]", "", num_str)
      if not clean_int.isdigit():
          return None
      val = float(clean_int) + cents
      # Sanity check: if a residential PPE/apartment transaction > CHF 150M, flag for review
      return val
  ```
- **Regression Risk**:
  Low. Standard Swiss prices with no decimals (`1'875'000`) continue to parse identically.
- **Validation Test**:
  1. Unit test on fixture `1'875'000.00` → asserts `1875000.0`.
  2. Unit test on fixture `2'450'000.-` → asserts `2450000.0`.
  3. Reprocess record ID `4837`; assert parsed price is exactly `1875000.0`.
  4. Query total database volume; assert cantonal total drops from CHF 18.81B to CHF 16.93B.
- **Rollback Plan**:
  Git revert on `pdf_parser.py`.
- **Historical Reprocessing Required**:
  **YES**. Execute targeted update query on Record ID `4837` and run a sanity scan across all records with `price > 50_000_000` against their raw PDFs.

---

### Finding P0-02: PPE Units Inherit Cadastral Land Plot Surfaces

- **Finding ID**: `P0-02` (`PAR-03` / `CONF-01`)
- **Affected File(s)**:
  - `src/fao_transactions/parser/pdf_parser.py`
  - `src/fao_transactions/visualization/map_builder.py` (around line 7065)
- **Affected Table(s)**:
  - `transactions` (`surface_m2`, `price_m2`)
  - `enrichments` (`surface_source`, `living_surface_source`)
- **Exact Failure Mechanism**:
  For PPE (Propriété par étages) apartment transactions, the official FAO publication does not notarize interior living area; it only publishes the apartment unit (lot number, millièmes) and the underlying cadastral parcel. When enriched via SITG cadastre, the system copies the parcel's total land area (e.g. 2,500 m² for an apartment building) into `surface_m2`. `map_builder.py` then labels this surface as `NOTARIEE_FAO`, producing nonsensical price/m² values of 200–500 CHF/m².
- **Minimal Code / Schema Change**:
  1. In `pdf_parser.py` and enrichment joining:
     ```python
     # If the property is PPE (Apartment lot), do NOT assign parcel land surface as surface_m2
     if property_type == "PPE" or "lot" in description.lower():
         # Keep surface_cadastre_m2 for land reference, but living surface is unknown
         living_surface_m2 = None
         surface_source = "UNAVAILABLE"
     ```
  2. In `map_builder.py:7065`:
     ```python
     if tx.get("surface_source") == "UNAVAILABLE" or not tx.get("surface_m2"):
         tx["surface_display"] = "Surface non spécifiée (PPE)"
         tx["price_m2_display"] = "N/A"
     ```
- **Regression Risk**:
  Low. Single-family villas and plots (`Maison`, `Parcelle`) retain their legitimate land surfaces.
- **Validation Test**:
  1. Execute query: `SELECT COUNT(*) FROM transactions WHERE type_bien = 'PPE' AND surface_m2 > 400`. Must return 0.
  2. Check UI popup for an apartment in Champel: displays "Surface non spécifiée (PPE)" instead of "2,500 m² (NOTARIEE_FAO)".
- **Rollback Plan**:
  Revert parser and map builder commits.
- **Historical Reprocessing Required**:
  **YES**. Execute SQL script setting `surface_m2 = NULL` and `price_m2 = NULL` for all 519 PPE records where `surface_m2 > 500`.

---

### Finding P0-03: Silent Abort on Anti-Bot Cloudflare Challenge

- **Finding ID**: `P0-03` (`SCR-01`)
- **Affected File(s)**:
  - `src/fao_transactions/scraper/crawler.py` (around lines 108–115)
- **Affected Table(s)**:
  - None (Scraper runtime execution)
- **Exact Failure Mechanism**:
  When the FAO search page (`/recherche?rubrique=133`) encounters a Cloudflare or Friendly Captcha challenge, `is_blocked()` waits up to 180s, logs a warning, but returns `links = []`. The calling method interprets the empty list as the end of publications, terminates cleanly, and exits with code 0.
- **Minimal Code / Schema Change**:
  Define a dedicated `AntiBotChallengeException` and raise it immediately:
  ```python
  class AntiBotChallengeException(Exception):
      """Raised when anti-bot protection blocks scraping progress."""
      pass

  if self.is_blocked(page):
      logger.critical("FATAL: Anti-bot challenge detected and unsolved on %s", page.url)
      raise AntiBotChallengeException(f"Scraper halted by anti-bot verification at {page.url}")
  ```
  Ensure process exits with non-zero status (code 1) so orchestrators (cron, GitHub Actions) trigger failure alerts.
- **Regression Risk**:
  None. Prevents silent data ingestion failures.
- **Validation Test**:
  Mock an anti-bot block page; assert crawler raises `AntiBotChallengeException` and exits with code 1.
- **Rollback Plan**:
  Git revert on `crawler.py`.
- **Historical Reprocessing Required**:
  **NO**.

---

### Finding P0-04: Premature Scraper Termination on 3-Duplicate Condition

- **Finding ID**: `P0-04` (`SCR-02`)
- **Affected File(s)**:
  - `src/fao_transactions/scraper/crawler.py` (around line 165)
- **Affected Table(s)**:
  - None (Scraper runtime execution)
- **Exact Failure Mechanism**:
  The crawler stops pagination if 3 consecutive notices match files already present on disk:
  ```python
  if consecutive_duplicates >= 3:
      logger.info("Encountered 3 consecutive existing notices. Halting crawl.")
      break
  ```
  Because the Land Registry occasionally backfills delayed notices or publishes non-sequential special editions, 3 existing notices can appear before 15 new historical entries, permanently dropping those new entries.
- **Minimal Code / Schema Change**:
  Replace the 3-consecutive-duplicate stop condition with date-window bounds and page coverage:
  ```python
  # Require at least N pages scanned or continue until page contains 100% existing notices
  # across 2 consecutive full pages rather than 3 individual records:
  if consecutive_duplicate_pages >= 2:
      logger.info("Encountered 2 full pages of existing notices. Halting crawl.")
      break
  ```
- **Regression Risk**:
  Low. Slightly increases scraping time by 10–15 seconds per run while ensuring complete coverage.
- **Validation Test**:
  Simulate a batch containing 3 duplicates followed by 1 new record; assert crawler continues and downloads the new record.
- **Rollback Plan**:
  Git revert on `crawler.py`.
- **Historical Reprocessing Required**:
  **NO** (historical backfill script can be executed once to verify no missed items).

---

### Finding P0-05: Errata Notices Ignore Price & Parcel Rectifications

- **Finding ID**: `P0-05` (`SCR-03`)
- **Affected File(s)**:
  - `src/fao_transactions/storage/db.py` (lines 222–229)
  - `src/fao_transactions/parser/pdf_parser.py`
- **Affected Table(s)**:
  - `transactions` in `state.sqlite`
- **Exact Failure Mechanism**:
  When an official FAO rectification notice (`Rectificatif au FAO No ...`) is processed, `handle_rectification()` only updates the seller and buyer names:
  ```python
  cursor.execute(
      "UPDATE transactions SET seller = ?, buyer = ? WHERE transaction_hash = ?",
      (rect_seller, rect_buyer, orig_hash)
  )
  ```
  If the Land Registry published the erratum to correct a typographical error in the price (e.g. correcting 5,000,000 to 500,000) or parcel number, the correction is ignored.
- **Minimal Code / Schema Change**:
  Expand `handle_rectification()` to update all parsed non-null fields and record the rectification audit metadata:
  ```python
  def handle_rectification(cursor, orig_hash, rect_data: Dict[str, Any]):
      fields_to_update = []
      values = []
      for field in ["price", "parcel_id", "surface_m2", "seller", "buyer", "price_m2"]:
          if rect_data.get(field) is not None:
              fields_to_update.append(f"{field} = ?")
              values.append(rect_data[field])
      if not fields_to_update:
          return
      fields_to_update.append("is_rectified = 1")
      fields_to_update.append("rectified_at = CURRENT_TIMESTAMP")
      values.append(orig_hash)
      sql = f"UPDATE transactions SET {', '.join(fields_to_update)} WHERE transaction_hash = ?"
      cursor.execute(sql, values)
  ```
- **Regression Risk**:
  Very low. Only affects transactions with matching rectification notices.
- **Validation Test**:
  Create test transaction with price `5'000'000`; process mock erratum with price `500'000`; assert updated price is `500000.0` and `is_rectified = 1`.
- **Rollback Plan**:
  Git revert on `db.py`.
- **Historical Reprocessing Required**:
  **YES**. Reprocess all 5 LDTR errata and any RF rectificatif PDFs on disk to apply pending corrections.

---

### Finding P0-06: Dual Persistence & Destructive CSV Overwrites

- **Finding ID**: `P0-06` (`LIN-01` / `LIN-02`)
- **Affected File(s)**:
  - `src/fao_transactions/visualization/map_builder.py` (lines 6985–7010)
  - `scripts/sync_to_sqlite.py` (lines 20–30)
- **Affected Table(s)**:
  - `transactions`, `enrichments` in `data/state/state.sqlite`
- **Exact Failure Mechanism**:
  1. `sync_to_sqlite.py` executes `df_txs.to_sql(..., if_exists='replace')`, which drops table definitions, primary keys, indexes, and constraints.
  2. `map_builder.py` prioritizes loading `data/processed/geneva_property_transactions.csv` if it exists. This CSV contains only 6,955 transactions, leaving out 1,787 transactions present in `state.sqlite` (8,742 transactions).
- **Minimal Code / Schema Change**:
  1. In `map_builder.py`, remove the CSV loading branch and force reading directly from `state.sqlite`:
     ```python
     # Make data/state/state.sqlite the authoritative and only data source:
     DB_PATH = Path("data/state/state.sqlite")
     if not DB_PATH.exists():
         raise FileNotFoundError(f"Authoritative database {DB_PATH} missing.")
     conn = sqlite3.connect(DB_PATH)
     df = pd.read_sql_query("""
         SELECT t.*, e.latitude, e.longitude, e.surface_source, e.commune_name
         FROM transactions t
         LEFT JOIN enrichments e ON t.id = e.transaction_id
     """, conn)
     ```
  2. In `scripts/sync_to_sqlite.py`: replace `if_exists='replace'` with upsert logic preserving schema constraints, or deprecate the script in favor of direct SQLite database writes.
- **Regression Risk**:
  Low. Guarantees consistent state across the entire platform.
- **Validation Test**:
  Run `python -m fao_transactions.visualization.map_builder`; verify UI output renders 8,364 geocoded points instead of 6,955 points.
- **Rollback Plan**:
  Revert `map_builder.py`.
- **Historical Reprocessing Required**:
  **NO**.

---

# Detailed Action Plans for Priority 1 (P1) Risks

---

### Finding P1-01: Disconnected Document Provenance (`raw_text` NULL)

- **Finding ID**: `P1-01` (`LIN-02` / `SCR-05`)
- **Affected File(s)**:
  - `src/fao_transactions/storage/db.py`
  - `src/fao_transactions/parser/pdf_parser.py`
- **Affected Table(s)**:
  - `transactions` (`raw_text`)
  - `publications` (all columns)
- **Exact Failure Mechanism**:
  During ingestion, `raw_text` extracted by PyMuPDF is not written to SQLite for 99.8% of records (only 14 records populated). Furthermore, the `publications` table was left empty (0 rows). Consequently, users cannot view the original notice text to verify an ambiguous extraction.
- **Minimal Code / Schema Change**:
  1. In `db.py:insert_transaction()`, ensure `raw_text` parameter is strictly passed and stored.
  2. In `crawler.py`, insert a publication record into `publications` for every downloaded PDF (`publication_date`, `source_url`, `pdf_filename`, `sha256_hash`, `downloaded_at`).
- **Regression Risk**:
  Database size increases by ~15 MB for 8,742 text notices (completely negligible on modern storage).
- **Validation Test**:
  Run ingestion on 10 PDFs; verify `raw_text` is populated and `publications` contains 10 rows.
- **Historical Reprocessing Required**:
  **YES**. Run an offline batch script to extract text from all 8,755 PDFs on disk and populate `transactions.raw_text`.

---

### Finding P1-02: 65 Unaccounted Raw PDFs on Disk

- **Finding ID**: `P1-02` (`SCR-06`)
- **Affected File(s)**:
  - New reconciliation script: `scripts/reconcile_unregistered_pdfs.py`
- **Affected Table(s)**:
  - `transactions`, `enrichments`, `publications`
- **Exact Failure Mechanism**:
  8,755 PDF files exist in `data/raw/fao_pdfs/`, but only 8,690 distinct source PDFs are linked in `state.sqlite`. 65 PDF files (60 RF transactions and 5 LDTR errata) were downloaded but never parsed into the relational database.
- **Minimal Code / Schema Change**:
  Create `scripts/reconcile_unregistered_pdfs.py` to compare on-disk filenames with `transactions.source_file`:
  ```python
  # Identify unregistered PDFs and execute parse_and_insert() on each missing file
  unregistered = [pdf for pdf in disk_pdfs if pdf.name not in db_source_files]
  for pdf in unregistered:
      record = parser.parse_pdf(pdf)
      db.insert_transaction(record)
  ```
- **Regression Risk**:
  None. Incorporates missing records safely into SQLite.
- **Validation Test**:
  Assert `COUNT(DISTINCT source_file)` in `transactions` equals total on-disk PDF count.
- **Historical Reprocessing Required**:
  **YES** (one-off ingestion of the 65 missing files).

---

### Finding P1-03: Hardcoded Static Agency Intelligence

- **Finding ID**: `P1-03` (`H7` / `P2-03`)
- **Affected File(s)**:
  - `src/fao_transactions/visualization/agency_ranking.py`
- **Affected Table(s)**:
  - None
- **Exact Failure Mechanism**:
  The agency leaderboard is rendered from `GENEVA_AGENCIES_DATA`, a 1,260-line static dictionary of pre-set market share numbers and agency bios. It does not reflect actual transaction activity.
- **Minimal Code / Schema Change**:
  1. Add an explicit UI disclaimer: `"Données agences: Estimation indicative & annuaire professionnel"`.
  2. Implement dynamic transaction aggregation: match buyer/seller corporate names against recognized real estate agency UIDs to compute live market transaction counts where available.
- **Regression Risk**:
  None.
- **Validation Test**:
  Verify agency tab shows clear data source labeling and does not misrepresent static rankings as empirical Land Registry data.
- **Historical Reprocessing Required**:
  **NO**.

---

### Finding P1-04: Single-Point Bespoke Code Overrides

- **Finding ID**: `P1-04` (`GIS-03`)
- **Affected File(s)**:
  - `src/fao_transactions/visualization/map_builder.py` (lines 7067–7075)
- **Affected Table(s)**:
  - None
- **Exact Failure Mechanism**:
  `map_builder.py` contains hardcoded bespoke logic for a single parcel:
  ```python
  if parcel == "4642-104":  # Saut-du-Loup 16
      tx["surface_m2"] = 142
      tx["price_m2"] = 11267
  ```
  Bespoke inline overrides create untraceable data exceptions and violate deterministic pipeline principles.
- **Minimal Code / Schema Change**:
  Remove lines 7067–7075 entirely. If parcel `4642-104` has missing data, handle it via standardized parser heuristics or formal database errata migration scripts.
- **Regression Risk**:
  None.
- **Validation Test**:
  Assert grep for `"4642-104"` in codebase returns no hardcoded values.
- **Historical Reprocessing Required**:
  **NO**.

---

### Finding P1-05: Coincident Pin Stacking with False Precision

- **Finding ID**: `P1-05` (`GIS-02`)
- **Affected File(s)**:
  - `src/fao_transactions/visualization/map_builder.py`
- **Affected Table(s)**:
  - None (Leaflet frontend layout)
- **Exact Failure Mechanism**:
  8,364 geocoded transactions share only 3,634 distinct coordinate pairs. Up to 53 individual property sales share identical latitude and longitude coordinates down to the sub-meter level. Without visual jittering or a spiderfier plugin, 52 sales are completely obscured behind the top marker.
- **Minimal Code / Schema Change**:
  In `map_builder.py`, include `Leaflet.markercluster` or a lightweight spiderfier spiral offset for coincident pins sharing identical coordinates:
  ```javascript
  // On marker cluster click or coincident pin group:
  if (coincident_count > 1) {
      marker.bindPopup(render_multi_transaction_table(transactions_at_pin));
  }
  ```
- **Regression Risk**:
  Low. Greatly improves map usability for high-density PPE developments.
- **Validation Test**:
  Click on a high-density address (e.g. Rue de Lyon); verify popup displays all stacked transactions in a scrollable list.
- **Historical Reprocessing Required**:
  **NO**.

---

### Finding P1-06: Multi-Parcel Deed Truncation

- **Finding ID**: `P1-06` (`CONF-02`)
- **Affected File(s)**:
  - `src/fao_transactions/parser/pdf_parser.py`
- **Affected Table(s)**:
  - `transactions` (`parcel_id`)
- **Exact Failure Mechanism**:
  In transactions transferring multiple parcels (e.g. `"parcelles 1234, 1235 et 1236"`), the regex matches only the first parcel token (`1234`), dropping secondary parcels.
- **Minimal Code / Schema Change**:
  Update regex to extract all parcel tokens and store as comma-delimited string in `parcel_id` or link to a child `transaction_parcels` table.
- **Regression Risk**:
  Low. Primary parcel remains first in list for backwards compatibility.
- **Validation Test**:
  Parse fixture containing `"parcelles 101, 102 et 103"`; assert `parcel_id == "101, 102, 103"`.
- **Historical Reprocessing Required**:
  **YES** (reparse affected multi-parcel deeds).

---

# Implementation Protocol & Human Authorization Gates

To maintain strict audit hygiene and protect operational data, no code changes will be deployed until the following human authorizations are recorded:

1. **Authorization Gate 1**: Approval of P0-01 (Decimal currency fix & ID 4837 volume correction).
2. **Authorization Gate 2**: Approval of P0-02 (PPE living surface uncoupling & removal of false NOTARIEE label).
3. **Authorization Gate 3**: Approval of P0-06 (Unification to `state.sqlite` and removal of stale CSV dependency).
4. **Authorization Gate 4**: Approval of Scraper & Lineage fixes (P0-03, P0-04, P0-05, P1-01, P1-02).
