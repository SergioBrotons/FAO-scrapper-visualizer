"""Stage 4 Parser, Extraction and Data Quality Diagnostic Script.
Queries data/state/state.sqlite to compute completeness funnel, temporal coverage,
cross-field validation, and edge case metrics.
"""

import sys
import re
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

FRENCH_MONTHS = {
    "janvier": "01", "février": "02", "fevrier": "02", "mars": "03",
    "avril": "04", "mai": "05", "juin": "06", "juillet": "07",
    "août": "08", "aout": "08", "septembre": "09", "octobre": "10",
    "novembre": "11", "décembre": "12", "decembre": "12"
}

def parse_french_date_to_iso(date_str):
    if not date_str:
        return None
    # match e.g. "25 septembre 2026" or "1er avril 2025"
    m = re.search(r"(\d{1,2}|1er)\s+([a-zéû]+)\s+(\d{4})", date_str.lower())
    if m:
        day_str = m.group(1).replace("1er", "1")
        month_name = m.group(2)
        year_str = m.group(3)
        month_num = FRENCH_MONTHS.get(month_name)
        if month_num:
            return f"{year_str}-{month_num}-{int(day_str):02d}"
    # match e.g. "25.09.2026"
    m2 = re.search(r"(\d{1,2})[./-](\d{1,2})[./-](\d{4})", date_str)
    if m2:
        return f"{m2.group(3)}-{int(m2.group(2)):02d}-{int(m2.group(1)):02d}"
    return None

def run_parser_quality_audit(db_path: Path):
    print(f"\n=======================================================", flush=True)
    print(f"STAGE 4 DATA QUALITY AUDIT: {db_path}", flush=True)
    print(f"=======================================================", flush=True)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT count(*) FROM transactions")
    total_tx = c.fetchone()[0]
    print(f"Total Transactions in DB: {total_tx}", flush=True)

    # 1. Null Rates per Field
    c.execute("PRAGMA table_info(transactions)")
    cols = [r["name"] for r in c.fetchall()]
    print("\n--- Field Completeness & Null Rates ---", flush=True)
    for col in cols:
        c.execute(f"SELECT count(*) FROM transactions WHERE {col} IS NULL OR {col} = ''")
        null_cnt = c.fetchone()[0]
        pop_cnt = total_tx - null_cnt
        pop_pct = pop_cnt / total_tx * 100
        print(f"  {col:<24} populated: {pop_cnt:>5} ({pop_pct:>5.1f}%) | null: {null_cnt:>5}", flush=True)

    # 2. Price Distribution & Anomalies
    print("\n--- Price CHF Distribution & Anomalies ---", flush=True)
    c.execute("SELECT count(*) FROM transactions WHERE price_chf IS NOT NULL AND price_chf > 0")
    priced_cnt = c.fetchone()[0]
    c.execute("SELECT count(*) FROM transactions WHERE price_chf = 0")
    zero_price_cnt = c.fetchone()[0]
    c.execute("SELECT count(*) FROM transactions WHERE price_chf < 0")
    neg_price_cnt = c.fetchone()[0]
    c.execute("SELECT count(*) FROM transactions WHERE price_chf IS NULL")
    null_price_cnt = c.fetchone()[0]
    c.execute("SELECT min(price_chf), max(price_chf), avg(price_chf) FROM transactions WHERE price_chf > 0")
    p_min, p_max, p_avg = c.fetchone()
    print(f"  Priced (>0): {priced_cnt} ({priced_cnt/total_tx*100:.1f}%)", flush=True)
    print(f"  Zero Price (=0): {zero_price_cnt}", flush=True)
    print(f"  Negative Price (<0): {neg_price_cnt}", flush=True)
    print(f"  Null Price: {null_price_cnt} ({null_price_cnt/total_tx*100:.1f}%)", flush=True)
    print(f"  Min Price: CHF {p_min:,.0f} | Max Price: CHF {p_max:,.0f} | Avg Price: CHF {p_avg:,.0f}", flush=True)

    # Micro-transactions (< 10,000 CHF)
    c.execute("SELECT count(*) FROM transactions WHERE price_chf > 0 AND price_chf < 10000")
    micro_prices = c.fetchone()[0]
    print(f"  Micro-prices (< CHF 10,000): {micro_prices} records (e.g. garage co-ownership, symbolic transfers)", flush=True)

    # Mega-transactions (> 100M CHF)
    c.execute("SELECT id, commune, parcel_number, price_chf, seller, buyer FROM transactions WHERE price_chf > 100000000 ORDER BY price_chf DESC LIMIT 5")
    mega_prices = c.fetchall()
    print(f"  Mega-prices (> CHF 100M): {len(mega_prices)} records. Top 3:", flush=True)
    for m in mega_prices[:3]:
        print(f"    - ID {m['id']}: {m['commune']} P.{m['parcel_number']} -> CHF {m['price_chf']:,.0f}", flush=True)

    # 3. Surface Analysis & Discrepancies
    print("\n--- Surface m² Analysis ---", flush=True)
    c.execute("SELECT count(*) FROM transactions WHERE surface_m2 IS NOT NULL AND surface_m2 > 0")
    tx_surf_cnt = c.fetchone()[0]
    c.execute("SELECT count(*) FROM enrichments WHERE surface_official_m2 IS NOT NULL AND surface_official_m2 > 0")
    cad_surf_cnt = c.fetchone()[0]
    print(f"  Transactions with surface_m2 from notice: {tx_surf_cnt} ({tx_surf_cnt/total_tx*100:.1f}%)", flush=True)
    print(f"  Enrichments with surface_official_m2 from SITG: {cad_surf_cnt} ({cad_surf_cnt/total_tx*100:.1f}%)", flush=True)

    # Check PPE with giant parcel land surfaces
    c.execute("""
        SELECT count(*) FROM transactions t 
        JOIN enrichments e ON t.id = e.transaction_id 
        WHERE t.property_type = 'PPE' AND e.surface_official_m2 > 500
    """)
    ppe_giant_cadastral = c.fetchone()[0]
    print(f"  PPE apartments where SITG parcel surface > 500 m² (Plot land surface collision): {ppe_giant_cadastral}", flush=True)

    # 4. Temporal Coverage & Month Distribution
    print("\n--- Temporal Coverage & Normalized Monthly Trends ---", flush=True)
    c.execute("SELECT id, notice_date FROM transactions WHERE notice_date IS NOT NULL")
    dates = c.fetchall()

    year_months = Counter()
    unparsed_dates = []
    iso_dates = []

    for d in dates:
        raw_d = d["notice_date"]
        iso_d = parse_french_date_to_iso(raw_d)
        if iso_d:
            iso_dates.append(iso_d)
            ym = iso_d[:7] # YYYY-MM
            year_months[ym] += 1
        else:
            unparsed_dates.append((d["id"], raw_d))

    iso_dates.sort()
    print(f"  Earliest ISO Notice Date: {iso_dates[0] if iso_dates else 'N/A'}", flush=True)
    print(f"  Latest ISO Notice Date:   {iso_dates[-1] if iso_dates else 'N/A'}", flush=True)
    print(f"  Unparseable dates: {len(unparsed_dates)}", flush=True)
    if unparsed_dates:
        print(f"    Sample unparsed: {unparsed_dates[:3]}", flush=True)

    print("\n  Monthly Distribution (Sorted Chronologically):", flush=True)
    for ym in sorted(year_months.keys()):
        bar = "█" * (year_months[ym] // 50)
        print(f"    {ym}: {year_months[ym]:>4} notices {bar}", flush=True)

    # 5. Geographic Distribution by Commune
    print("\n--- Top Communes Distribution ---", flush=True)
    c.execute("SELECT commune, count(*) as cnt FROM transactions GROUP BY commune ORDER BY cnt DESC LIMIT 10")
    communes = c.fetchall()
    for cm in communes:
        print(f"  {cm['commune']:<24}: {cm['cnt']:>5} transactions", flush=True)

    # 6. Transaction Typology Breakdown
    print("\n--- Transaction & Property Types ---", flush=True)
    c.execute("SELECT transaction_type, count(*) as cnt FROM transactions GROUP BY transaction_type ORDER BY cnt DESC")
    for row in c.fetchall():
        print(f"  Type: {str(row['transaction_type']):<20}: {row['cnt']:>5}", flush=True)

    c.execute("SELECT property_type, count(*) as cnt FROM transactions GROUP BY property_type ORDER BY cnt DESC")
    print("  Property Types:", flush=True)
    for row in c.fetchall():
        print(f"    {str(row['property_type']):<20}: {row['cnt']:>5}", flush=True)

    conn.close()

if __name__ == "__main__":
    run_parser_quality_audit(Path("data/state/state.sqlite"))
