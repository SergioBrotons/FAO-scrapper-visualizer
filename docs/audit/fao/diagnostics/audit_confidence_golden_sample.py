"""Stage 6 Confidence Model and Golden-Sample Validation Script.
Extracts stratified golden samples across 10 categories to assess field accuracy,
lineage completeness, and confidence dimensions.
"""

import sys
import json
import sqlite3
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def run_golden_sample_audit(db_path: Path):
    print(f"\n=======================================================", flush=True)
    print(f"STAGE 6 GOLDEN SAMPLE VALIDATION: {db_path}", flush=True)
    print(f"=======================================================", flush=True)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    queries = {
        "1. Recent Transaction (Sept 2026)": """
            SELECT t.id, t.notice_date, t.commune, t.parcel_number, t.property_type, t.price_chf, t.surface_m2, t.file_source, e.match_status, e.centroid_wgs84_lon, e.surface_official_m2
            FROM transactions t LEFT JOIN enrichments e ON t.id = e.transaction_id
            WHERE t.notice_date LIKE '%septembre 2026%' AND t.price_chf > 1000000
            ORDER BY t.id DESC LIMIT 1
        """,
        "2. Older Historical Transaction (2023/2024)": """
            SELECT t.id, t.notice_date, t.commune, t.parcel_number, t.property_type, t.price_chf, t.surface_m2, t.file_source, e.match_status, e.centroid_wgs84_lon, e.surface_official_m2
            FROM transactions t LEFT JOIN enrichments e ON t.id = e.transaction_id
            WHERE (t.notice_date LIKE '%2023%' OR t.notice_date LIKE '%2024%') AND t.price_chf > 0
            ORDER BY t.id ASC LIMIT 1
        """,
        "3. High-Value Institutional / Prime (> CHF 20M)": """
            SELECT t.id, t.notice_date, t.commune, t.parcel_number, t.property_type, t.price_chf, t.surface_m2, t.file_source, e.match_status, e.centroid_wgs84_lon, e.surface_official_m2
            FROM transactions t LEFT JOIN enrichments e ON t.id = e.transaction_id
            WHERE t.price_chf > 20000000 AND t.id != 4837
            ORDER BY t.price_chf DESC LIMIT 1
        """,
        "4. Low-Value / Parking Lot (< CHF 100k)": """
            SELECT t.id, t.notice_date, t.commune, t.parcel_number, t.property_type, t.price_chf, t.surface_m2, t.file_source, e.match_status, e.centroid_wgs84_lon, e.surface_official_m2
            FROM transactions t LEFT JOIN enrichments e ON t.id = e.transaction_id
            WHERE t.price_chf > 0 AND t.price_chf < 100000
            ORDER BY t.price_chf ASC LIMIT 1
        """,
        "5. PPE Apartment Unit": """
            SELECT t.id, t.notice_date, t.commune, t.parcel_number, t.property_type, t.price_chf, t.surface_m2, t.file_source, e.match_status, e.centroid_wgs84_lon, e.surface_official_m2
            FROM transactions t LEFT JOIN enrichments e ON t.id = e.transaction_id
            WHERE t.property_type = 'PPE' AND t.rooms IS NOT NULL
            ORDER BY t.id DESC LIMIT 1
        """,
        "6. Villa / Individual House": """
            SELECT t.id, t.notice_date, t.commune, t.parcel_number, t.property_type, t.price_chf, t.surface_m2, t.file_source, e.match_status, e.centroid_wgs84_lon, e.surface_official_m2
            FROM transactions t LEFT JOIN enrichments e ON t.id = e.transaction_id
            WHERE t.nature LIKE '%habitation à un seul logement%' OR t.nature LIKE '%villa%'
            ORDER BY t.id DESC LIMIT 1
        """,
        "7. Multi-Parcel Transfer": """
            SELECT t.id, t.notice_date, t.commune, t.parcel_number, t.property_type, t.price_chf, t.surface_m2, t.file_source, e.match_status, e.centroid_wgs84_lon, e.surface_official_m2
            FROM transactions t LEFT JOIN enrichments e ON t.id = e.transaction_id
            WHERE t.file_source IN (
                SELECT file_source FROM transactions GROUP BY file_source HAVING count(*) > 1
            )
            ORDER BY t.id DESC LIMIT 1
        """,
        "8. Address-Only Fallback Geocoding": """
            SELECT t.id, t.notice_date, t.commune, t.parcel_number, t.address, t.price_chf, t.file_source, e.match_status, e.centroid_wgs84_lon
            FROM transactions t JOIN enrichments e ON t.id = e.transaction_id
            WHERE e.match_status = 'matched_address'
            ORDER BY t.id DESC LIMIT 1
        """,
        "9. Unresolved Cadastral Match (not_found)": """
            SELECT t.id, t.notice_date, t.commune, t.parcel_number, t.address, t.price_chf, t.file_source, e.match_status, e.centroid_wgs84_lon
            FROM transactions t JOIN enrichments e ON t.id = e.transaction_id
            WHERE e.match_status = 'not_found'
            ORDER BY t.id DESC LIMIT 1
        """,
        "10. Unpriced Succession / Héritage": """
            SELECT t.id, t.notice_date, t.commune, t.parcel_number, t.transaction_type, t.price_chf, t.seller, t.buyer, t.file_source
            FROM transactions t
            WHERE t.transaction_type = 'Héritage'
            ORDER BY t.id DESC LIMIT 1
        """,
    }

    samples_out = {}
    for label, q in queries.items():
        c.execute(q)
        row = c.fetchone()
        if row:
            samples_out[label] = dict(row)
            print(f"\n[{label}]", flush=True)
            for k, v in dict(row).items():
                print(f"  {k:<20}: {v}", flush=True)
        else:
            print(f"\n[{label}]: No row returned!", flush=True)

    conn.close()

if __name__ == "__main__":
    run_golden_sample_audit(Path("data/state/state.sqlite"))
