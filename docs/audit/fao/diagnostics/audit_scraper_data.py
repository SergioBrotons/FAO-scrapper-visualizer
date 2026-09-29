"""Diagnostic script for Stage 2 Scraper and Acquisition Audit.
Audits the raw PDF files, SQLite databases, and acquisition state using metadata only.
Does NOT open files to prevent blocking on cloud-dehydrated files.
"""

import os
import sys
import json
import sqlite3
from pathlib import Path
from collections import Counter

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def audit_database(db_path: Path):
    print(f"\n=======================================================", flush=True)
    print(f"Auditing Database: {db_path}", flush=True)
    print(f"=======================================================", flush=True)
    if not db_path.exists():
        print(f"Database {db_path} does not exist!", flush=True)
        return set()

    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()

    c.execute("SELECT count(*) FROM transactions")
    total_tx = c.fetchone()[0]
    print(f"Total transactions: {total_tx}", flush=True)

    c.execute("SELECT length(transaction_hash), count(*) FROM transactions GROUP BY length(transaction_hash)")
    hash_lens = c.fetchall()
    print(f"Transaction hash lengths and counts: {hash_lens}", flush=True)

    c.execute("SELECT count(DISTINCT transaction_hash) FROM transactions")
    dist_hashes = c.fetchone()[0]
    print(f"Unique transaction hashes: {dist_hashes} (Duplicates: {total_tx - dist_hashes})", flush=True)

    c.execute("SELECT source_category, count(*) FROM transactions GROUP BY source_category")
    cats = c.fetchall()
    print(f"By source_category: {cats}", flush=True)

    c.execute("SELECT count(DISTINCT file_source) FROM transactions WHERE file_source IS NOT NULL")
    dist_files = c.fetchone()[0]
    print(f"Distinct file_source entries: {dist_files}", flush=True)

    c.execute("SELECT count(*) FROM transactions WHERE file_source IS NULL")
    null_files = c.fetchone()[0]
    print(f"Transactions with NULL file_source: {null_files}", flush=True)

    c.execute("SELECT LOWER(file_source) FROM transactions WHERE file_source IS NOT NULL")
    db_file_sources = set(r[0].strip() for r in c.fetchall() if r[0])

    # Date range and formatting check
    c.execute("SELECT min(notice_date), max(notice_date) FROM transactions WHERE notice_date IS NOT NULL")
    date_range = c.fetchone()
    print(f"Notice date min/max (lexical): {date_range}", flush=True)

    # Check publications table if present
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='publications'")
    if c.fetchone():
        c.execute("SELECT count(*) FROM publications")
        pub_count = c.fetchone()[0]
        print(f"Publications table rows: {pub_count}", flush=True)
    else:
        print("Publications table: DOES NOT EXIST", flush=True)

    conn.close()
    return db_file_sources

def audit_directory_files(dir_path: Path):
    print(f"\n=======================================================", flush=True)
    print(f"Auditing Directory Files: {dir_path}", flush=True)
    print(f"=======================================================", flush=True)
    if not dir_path.exists():
        print(f"Directory {dir_path} does not exist!", flush=True)
        return set()

    files = set()
    for entry in os.scandir(dir_path):
        if entry.is_file() and entry.name.lower().endswith(".pdf"):
            files.add(entry.name.lower())

    print(f"Total PDF files on disk: {len(files)}", flush=True)
    return files

def compare_disk_vs_db(db_files: set, rf_files: set, ldtr_files: set):
    print(f"\n=======================================================", flush=True)
    print(f"Comparing Disk vs Database Files", flush=True)
    print(f"=======================================================", flush=True)
    all_disk_files = rf_files | ldtr_files
    print(f"Total disk files across RF and LDTR: {len(all_disk_files)}", flush=True)
    print(f"Total distinct file sources in DB: {len(db_files)}", flush=True)

    disk_not_in_db = all_disk_files - db_files
    print(f"Files on disk but NOT recorded in DB: {len(disk_not_in_db)}", flush=True)
    if disk_not_in_db:
        print(f"  Missing files sample: {sorted(list(disk_not_in_db))[:15]}", flush=True)

    db_not_on_disk = db_files - all_disk_files
    print(f"Files in DB but NOT found on disk: {len(db_not_on_disk)}", flush=True)
    if db_not_on_disk:
        print(f"  Ghost files in DB: {sorted(list(db_not_on_disk))[:15]}", flush=True)

if __name__ == "__main__":
    db_files = audit_database(Path("data/state/state.sqlite"))
    audit_database(Path("data/fao_transactions.db"))
    rf_files = audit_directory_files(Path("data/raw/transactions"))
    ldtr_files = audit_directory_files(Path("data/raw/ldtr"))
    compare_disk_vs_db(db_files, rf_files, ldtr_files)
