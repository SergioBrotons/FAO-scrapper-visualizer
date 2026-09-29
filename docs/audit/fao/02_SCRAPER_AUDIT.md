# Stage 2 — Scraper and Acquisition Audit

**Target System**: Cytria — Geneva Real Estate & Land Intelligence Platform (`FAO-Scrapper-Visualizer`)  
**Date**: 2026-09-29  
**Audit Stage**: Stage 2 (Scraper, Browser Automation & Acquisition Pipeline)  
**Standard**: Strict Evidence-Based Audit (`00_README_FIRST.md`, `01_MASTER_INSTRUCTIONS.md`, `03_SCRAPER_AUDIT.md`)  
**Status**: VERIFIED & DOCUMENTED  

---

## 1. Executive Summary

This stage audits the acquisition subsystem responsible for discovering, fetching, and validating official Geneva real-estate transactions from the Canton of Geneva's portal (`https://fao.ge.ch`).

The audit reveals that while the scraper employs thoughtful anti-detection practices (headed Playwright execution, random safety pacing between 2.5s and 4.5s, persistent Chromium browser profiles, and magic-byte PDF validation), the acquisition engine suffers from **severe structural blind spots**:
1. **Silent Anti-Bot Abort**: If Cloudflare blocks the search listing page, the scraper encounters 0 links and exits cleanly with return code 0, silently reporting that no new documents exist.
2. **Blind Stop Condition Gaps**: The incremental mode halts the scraper after 3 consecutive already-archived notices on page 0. Any backfilled, out-of-order, or retroactively published notices on deeper pages are permanently skipped.
3. **Rectification Errata Price Blindness**: When an official cantonal rectification notice (*avis rectificatif*) is detected, the database update logic only updates `seller` and `buyer`. Official corrections to transaction price, parcel number, or surface area are completely discarded.
4. **65 Unaccounted PDF Files on Disk**: Diagnostic metadata analysis reveals that 65 downloaded PDF notices on disk (60 Registre Foncier, 5 LDTR) do not exist in the database.
5. **Absence of Persistent Checkpoint Tracking**: The system lacks a cursor or state table; all deduplication and progress relies on in-memory sets compiled from disk and SQLite at the start of each run.

---

## 2. Findings Log

| ID | Severity | Finding | Evidence | Consequence | Recommendation |
|---|---|---|---|---|---|
| **SCR-01** | **P0** | Silent termination on anti-bot challenge on listing discovery | [`transaction_batch.py:161-163`](file:///c:/Users/LocalUser/kDrive/DEV/Sbrot/Cytria_FAO_Scrapper_Intelligence_AGY/src/fao_transactions/collector/transaction_batch.py#L161-L163), [`browser.py:182-194`](file:///c:/Users/LocalUser/kDrive/DEV/Sbrot/Cytria_FAO_Scrapper_Intelligence_AGY/src/fao_transactions/collector/browser.py#L182-L194) | When Cloudflare or Friendly Captcha blocks the search URL, 0 links are found; scraper logs "No more notices found. Stopping." and terminates cleanly without an alert or retry. | Raise explicit `CaptchaChallengeTimeoutError` when challenge is unresolved; do not treat blocked pages as empty result sets. |
| **SCR-02** | **P0** | Incremental 3-duplicate stop condition creates permanent gaps | [`transaction_batch.py:185-193`](file:///c:/Users/LocalUser/kDrive/DEV/Sbrot/Cytria_FAO_Scrapper_Intelligence_AGY/src/fao_transactions/collector/transaction_batch.py#L185-L193) | Any notice published with a slight delay, out of order, or backfilled behind 3 already-known notices is permanently ignored and never acquired. | Replace consecutive-duplicate break with date-range-bounded scans or crawl deeper (at least N full pages) before stopping. |
| **SCR-03** | **P0** | Rectification errata ignores price, parcel, and surface corrections | [`db.py:215-230`](file:///c:/Users/LocalUser/kDrive/DEV/Sbrot/Cytria_FAO_Scrapper_Intelligence_AGY/src/fao_transactions/storage/db.py#L215-L230) | When FAO publishes an official rectification notice correcting a misprinted transaction price or parcel, only `seller` and `buyer` are updated. Erroneous prices remain uncorrected. | Update all extractable fields (`price_chf`, `parcel_number`, `surface_m2`) when handling valid rectification records. |
| **SCR-04** | **P1** | Lack of persistent scraper run checkpoints and cursors | [`transaction_batch.py:123-131`](file:///c:/Users/LocalUser/kDrive/DEV/Sbrot/Cytria_FAO_Scrapper_Intelligence_AGY/src/fao_transactions/collector/transaction_batch.py#L123-L131) | Scraper reconstructs known state in-memory from filesystem and DB on every run. If interrupted, there is no record of where the scan left off. | Create a persistent `scraper_runs` table tracking `run_id`, `start_time`, `end_time`, `max_page_scanned`, `status`, and `notices_fetched`. |
| **SCR-05** | **P1** | Empty `publications` table severs provenance lineage | [`db.py:34-46`](file:///c:/Users/LocalUser/kDrive/DEV/Sbrot/Cytria_FAO_Scrapper_Intelligence_AGY/src/fao_transactions/storage/db.py#L34-L46), Verified query count = 0 | Transactions cannot be traced back to the specific FAO gazette issue date, URL, or publication number where they originally appeared. | Populate `publications` table during acquisition and enforce foreign key linkage with `transactions.publication_id`. |
| **SCR-06** | **P1** | 65 downloaded PDF notices on disk are absent from the database | Diagnostic output: 8,755 disk PDFs vs 8,690 distinct DB file sources (60 RF, 5 LDTR) | 65 transaction notices were downloaded over network but never ingested into SQLite or failed extraction silently. | Run an automated audit and ingestion pass on the 65 missing PDFs; log and categorize unparseable documents. |
| **SCR-07** | **P1** | Download stream lacks HTTP status code and content checksum validation | [`transaction_batch.py:210-213`](file:///c:/Users/LocalUser/kDrive/DEV/Sbrot/Cytria_FAO_Scrapper_Intelligence_AGY/src/fao_transactions/collector/transaction_batch.py#L210-L213), [`downloader.py:70-74`](file:///c:/Users/LocalUser/kDrive/DEV/Sbrot/Cytria_FAO_Scrapper_Intelligence_AGY/src/fao_transactions/collector/downloader.py#L70-L74) | Browser download stream does not capture HTTP response codes (403, 500) or verify SHA-256 integrity of the received document file. | Record HTTP status, response headers, and document SHA-256 hash immediately upon saving the raw file. |
| **SCR-08** | **P2** | Cloud storage dehydration blocks file reads synchronously | Windows attribute `FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS` (0x400000) on `data/raw/` | If files are offloaded by kDrive on-demand sync, standard Python `open()` blocks synchronously waiting for cloud hydration, causing processes to hang. | Ensure local pinning of data directories or handle dehydrated file attributes explicitly with non-blocking I/O. |
| **SCR-09** | **P2** | Non-chronological date sorting in database queries | [`db.py:314`](file:///c:/Users/LocalUser/kDrive/DEV/Sbrot/Cytria_FAO_Scrapper_Intelligence_AGY/src/fao_transactions/storage/db.py#L314), [`models.py:28`](file:///c:/Users/LocalUser/kDrive/DEV/Sbrot/Cytria_FAO_Scrapper_Intelligence_AGY/src/fao_transactions/parser/models.py#L28) | Dates are stored as un-normalized French strings (`'9 septembre 2026'`). SQL `ORDER BY notice_date` performs alphabetical sort rather than chronological order. | Add an ISO-8601 normalized column `notice_date_iso` (`YYYY-MM-DD`) and index it for chronological queries. |
| **SCR-10** | **P3** | Ephemeral in-memory logging in background synchronization engine | [`sync_engine.py:63, 84-91`](file:///c:/Users/LocalUser/kDrive/DEV/Sbrot/Cytria_FAO_Scrapper_Intelligence_AGY/src/fao_transactions/collector/sync_engine.py#L63) | Telemetry logs are kept in a Python list truncated to 200 items. Historical run logs are lost upon process restart. | Persist synchronization logs to a rolling log file on disk or SQLite table. |

---

## 3. Detailed Subsystem Analysis

### 3.1 Coverage & Discovery Mechanism
The scraper targets two main document categories:
1. **Registre Foncier Notices (Art. 157 LaCC)**:
   - Target URL: `https://fao.ge.ch/recherche?rubrique=133`
   - Pagination: `&page={page_idx}`
   - Selector: `a[href*='/avis/']`
   - Notice download endpoint: `https://fao.ge.ch/avis-download/{uuid}`
2. **LDTR Apartment Notices (Art. 39 LDTR)**:
   - Acquired via batch archives (`data/raw/ldtr/VA_*.pdf`).
3. **Daily Gazette Editions ("La Quotidienne")**:
   - Target URL: `https://fao.ge.ch/quotidiennes`
   - Selector: `a[href*='dwnlquotidienne']`

#### Coverage Analysis & Gaps:
- **No Temporal Parameters**: The query URL `fao.ge.ch/recherche?rubrique=133` contains no date filters (`date_from`, `date_to`). The crawler relies purely on pagination order.
- **Vulnerability to Out-of-Order Publications**: The stop condition halts scraping when 3 consecutive notices match existing files:
  ```python
  if self.stop_on_duplicate_count and consecutive_duplicates >= self.stop_on_duplicate_count:
      should_stop_incremental = True
      break
  ```
  If the Canton publishes an older transaction or backdates an announcement behind 3 already-scraped items, it will **never be downloaded**.

---

### 3.2 Browser Automation & Anti-Bot Defense
- **Browser**: Managed via Playwright Chromium with persistent user profile in `data/browser_profile/` ([`browser.py:43-88`](file:///c:/Users/LocalUser/kDrive/DEV/Sbrot/Cytria_FAO_Scrapper_Intelligence_AGY/src/fao_transactions/collector/browser.py#L43-L88)).
- **Channel**: Defaults to local Google Chrome (`channel="chrome"`), falling back to bundled Chromium.
- **Process Lock Cleanup**: Features automated killing of orphaned Chrome processes locking `SingletonLock` on Windows.
- **Anti-Bot Inspection (`is_blocked`)**:
  - Checks current URL for `/captcha`.
  - Searches page title and content for keywords: `cloudflare`, `turnstile`, `just a moment`, `vérification`, `friendly captcha`, `my-widget-mount`, `frc-captcha`, `robot`, `access denied`.
- **Friendly Captcha Auto-Activation**:
  - Attempts to click `button.frc-button` automatically.
- **Interactive Prompt**:
  - If terminal has a TTY (`sys.stdin.isatty()`), prompts user: `input(">>> Press [ENTER] ...")`.
  - Polls for 180 seconds via `wait_until_unblocked()`.

#### Anti-Bot Failure Mode:
- In headless mode or background execution (e.g., when launched by the background scheduler in `server.py`), no TTY exists. If Friendly Captcha requires manual interaction or Cloudflare presents a Turnstile challenge, `wait_until_unblocked()` exhausts its 180-second timeout, logs a timeout warning, and returns **without throwing an error**.
- The calling loop then evaluates `a[href*='/avis/']` on the blocked challenge page, finds 0 links, and concludes that the archive is completely up-to-date.

---

### 3.3 Download Validation Architecture
When downloading notices ([`transaction_batch.py:53-88, 202-238`](file:///c:/Users/LocalUser/kDrive/DEV/Sbrot/Cytria_FAO_Scrapper_Intelligence_AGY/src/fao_transactions/collector/transaction_batch.py#L53-L88)):
- **Status Code Validation**: NOT IMPLEMENTED. Playwright `expect_download()` captures the stream without providing HTTP response headers.
- **Content-Type Validation**: NOT IMPLEMENTED.
- **File Signature Validation**: IMPLEMENTED. Checks `header.startswith(b"%PDF-")`.
- **File Size Validation**: IMPLEMENTED. Rejects files < 500 bytes.
- **Text & PDF Integrity Validation**: IMPLEMENTED. Uses `pymupdf.open()` and verifies that text can be extracted. Inspects extracted text for Cloudflare challenge markers.
- **Expected Identifier Validation**: NOT IMPLEMENTED. The notice PDF does not contain the URL UUID in its printed body.
- **File Checksum / Hash Validation**: NOT IMPLEMENTED upon download. File hash is not computed or recorded in the publications table.

---

### 3.4 Actual Acquisition State & Document Inventory

| Metric | Registre Foncier (RF) | LDTR Apartments | Quotidiennes | Total |
|---|---|---|---|---|
| **Raw Documents on Disk** | 8,112 PDFs | 643 PDFs | 1 PDF | **8,756 PDFs** |
| **Documents Registered in `state.sqlite`** | 8,104 records | 638 records | 0 records | **8,742 records** |
| **Documents Registered in `fao_transactions.db`** | 8,090 records | 638 records | 0 records | **8,728 records** |
| **Unregistered Documents on Disk** | 60 PDFs | 5 PDFs | 1 PDF | **66 PDFs** |
| **Corrupted / < 500B Files** | 0 | 0 | 0 | **0** |
| **PDFs Producing Multiple Records** | 41 PDFs | 0 | 0 | **41 PDFs** (max 5 records/PDF) |
| **Publications Table Count** | — | — | — | **0 rows** |

#### Analysis of the 65 Missing Documents:
- **5 LDTR Missing Files**: 4 of the 5 files are explicit rectification notices (`va_15760_-_rectificatif.pdf`, `va_15501_-_rectificatif.pdf`, `va_15736_-_rectificatif.pdf`, `va_15204_-_rectificatif.pdf`). Because `db.py` updates existing rows during rectifications without updating `file_source`, these 4 PDFs are permanently detached from database provenance.
- **60 RF Missing Files**: Includes notices like `notice_3137b42a-9305-4b28-b0d6-267778e96db9.pdf` which were downloaded during search sweeps but either failed parsing silently or represented administrative notices rejected by the parser's exclusion filter.

---

## 4. Idempotency & Resumption Assessment

1. **Rerunning on an existing dataset**:
   - Correctly skips already downloaded PDFs based on filename presence in `known_sources`.
   - SQLite enforces `transaction_hash UNIQUE`, preventing duplicate transaction rows when parsed.
2. **Failure during batch download**:
   - If a download crashes mid-run, partially downloaded files are not left behind (Playwright atomic save).
   - However, because no persistent run cursor exists, restarting the scraper immediately evaluates the 3-duplicate rule; if the first 3 notices on page 0 are already present, the run terminates immediately, leaving any remaining notices on that page uncollected.
3. **Rectification handling**:
   - Partially idempotent: Updates `seller`, `buyer`, and appends to `raw_text`.
   - Defective: Does NOT update `price_chf`, `parcel_number`, or `surface_m2`.

---

## 5. Summary of Stage 2

The acquisition layer successfully downloaded 8,756 authentic notice PDFs through headed Playwright automation. However, its operational reliability is compromised by silent termination on anti-bot challenges, premature incremental stopping, lack of persistent run checkpoints, severed publication lineage, and incomplete rectification handling.

*Stage 2 Scraper and Acquisition Audit is complete. Proceed to Stage 3: Database and Lineage Audit.*
