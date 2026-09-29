"""Stage 3 Database, Identity and Provenance Audit Diagnostic.
Queries SQLite databases to analyze canonical identities, duplicates, referential integrity, and lineage.
"""

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

def audit_database_lineage(db_path: Path):
    print(f"\n=======================================================", flush=True)
    print(f"DATABASE LINEAGE AUDIT: {db_path}", flush=True)
    print(f"=======================================================", flush=True)
    if not db_path.exists():
        print(f"Database {db_path} does not exist!", flush=True)
        return

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # 1. Foreign Key check
    c.execute("PRAGMA foreign_key_check")
    fk_violations = c.fetchall()
    print(f"Foreign Key Violations: {len(fk_violations)}", flush=True)
    if fk_violations:
        for fkv in fk_violations[:5]:
            print(f"  FK violation: table={fkv[0]}, rowid={fkv[1]}, target={fkv[2]}, fkid={fkv[3]}", flush=True)

    # 2. Check orphans in enrichments
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='enrichments'")
    has_enrich = bool(c.fetchone())
    if has_enrich:
        c.execute("""
            SELECT count(*) FROM enrichments e 
            LEFT JOIN transactions t ON e.transaction_id = t.id 
            WHERE t.id IS NULL
        """)
        orphan_enrichments = c.fetchone()[0]
        print(f"Orphan enrichments (no parent transaction): {orphan_enrichments}", flush=True)

        c.execute("""
            SELECT count(*) FROM transactions t 
            LEFT JOIN enrichments e ON t.id = e.transaction_id 
            WHERE e.id IS NULL
        """)
        unenriched_transactions = c.fetchone()[0]
        print(f"Transactions without enrichments row: {unenriched_transactions}", flush=True)

        c.execute("SELECT match_status, count(*) FROM enrichments GROUP BY match_status")
        match_stats = c.fetchall()
        print(f"Enrichment match statuses: {[dict(m) for m in match_stats]}", flush=True)

        c.execute("SELECT count(*) FROM enrichments WHERE centroid_wgs84_lon IS NOT NULL")
        geocoded_count = c.fetchone()[0]
        print(f"Geocoded enrichments (non-null coordinates): {geocoded_count}", flush=True)

    # 3. Duplicate checks in transactions
    c.execute("SELECT count(*) FROM transactions")
    total_tx = c.fetchone()[0]

    # Duplicate by parcel + notice_date + price
    c.execute("""
        SELECT commune, parcel_number, notice_date, price_chf, count(*) as cnt 
        FROM transactions 
        WHERE parcel_number IS NOT NULL AND notice_date IS NOT NULL AND price_chf IS NOT NULL
        GROUP BY commune, parcel_number, notice_date, price_chf 
        HAVING cnt > 1 
        ORDER BY cnt DESC
    """)
    dup_parcel_date_price = c.fetchall()
    print(f"Potential economic duplicates (same commune + parcel + date + price): {len(dup_parcel_date_price)} clusters", flush=True)
    if dup_parcel_date_price:
        for d in dup_parcel_date_price[:5]:
            print(f"  Cluster: {dict(d)}", flush=True)

    # Duplicate by address + notice_date + price
    c.execute("""
        SELECT commune, address, notice_date, price_chf, count(*) as cnt 
        FROM transactions 
        WHERE address IS NOT NULL AND notice_date IS NOT NULL AND price_chf IS NOT NULL
        GROUP BY commune, address, notice_date, price_chf 
        HAVING cnt > 1 
        ORDER BY cnt DESC
    """)
    dup_addr_date_price = c.fetchall()
    print(f"Potential address duplicates (same commune + address + date + price): {len(dup_addr_date_price)} clusters", flush=True)
    if dup_addr_date_price:
        for d in dup_addr_date_price[:5]:
            print(f"  Cluster: {dict(d)}", flush=True)

    # 4. Provenance coverage
    c.execute("SELECT count(*) FROM transactions WHERE file_source IS NOT NULL AND length(file_source) > 0")
    has_file_source = c.fetchone()[0]
    print(f"Provenance: Has file_source: {has_file_source} / {total_tx} ({has_file_source/total_tx*100:.1f}%)", flush=True)

    # Check if raw_text column exists
    c.execute("PRAGMA table_info(transactions)")
    cols = [r["name"] for r in c.fetchall()]
    if "raw_text" in cols:
        c.execute("SELECT count(*) FROM transactions WHERE raw_text IS NOT NULL AND length(raw_text) > 0")
        has_raw = c.fetchone()[0]
        print(f"Provenance: Has raw_text: {has_raw} / {total_tx} ({has_raw/total_tx*100:.1f}%)", flush=True)
    else:
        print("Provenance: raw_text column does NOT exist in transactions", flush=True)

    if "publication_id" in cols:
        c.execute("SELECT count(*) FROM transactions WHERE publication_id IS NOT NULL")
        has_pub = c.fetchone()[0]
        print(f"Provenance: Has publication_id: {has_pub} / {total_tx}", flush=True)
    else:
        print("Provenance: publication_id column does NOT exist", flush=True)

    if "case_number" in cols:
        c.execute("SELECT count(*) FROM transactions WHERE case_number IS NOT NULL AND length(case_number) > 0")
        has_case = c.fetchone()[0]
        print(f"Provenance: Has case_number: {has_case} / {total_tx} ({has_case/total_tx*100:.1f}%)", flush=True)

    # Sample transaction for full lineage tracing
    c.execute("""
        SELECT * FROM transactions 
        WHERE parcel_number IS NOT NULL AND price_chf IS NOT NULL AND address IS NOT NULL 
        ORDER BY id DESC LIMIT 2
    """)
    samples = c.fetchall()
    print("\nSample transactions for Lineage Tracing:", flush=True)
    for s in samples:
        d = dict(s)
        print(f"  ID: {d.get('id')}, Date: {d.get('notice_date')}, Commune: {d.get('commune')}, Parcel: {d.get('parcel_number')}, Price: {d.get('price_chf')}, Hash: {d.get('transaction_hash')[:16]}..., File: {d.get('file_source')}", flush=True)

    conn.close()

if __name__ == "__main__":
    audit_database_lineage(Path("data/state/state.sqlite"))
    audit_database_lineage(Path("data/fao_transactions.db"))
