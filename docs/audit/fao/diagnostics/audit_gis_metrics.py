"""Stage 5 GIS, Maps, Analytics and Visualization Diagnostic Script."""

import sys
import json
import sqlite3
import csv
from pathlib import Path
from collections import Counter

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def audit_gis_and_kpis(db_path: Path, csv_path: Path):
    print(f"\n=======================================================", flush=True)
    print(f"STAGE 5 GIS & VISUALIZATION AUDIT", flush=True)
    print(f"=======================================================", flush=True)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # 1. Volume Distortion Check
    c.execute("SELECT sum(price_chf), count(*), sum(case when price_chf > 0 then 1 else 0 end) FROM transactions")
    vol_db, total_db, priced_db = c.fetchone()
    print(f"Database Total Volume: CHF {vol_db:,.0f} across {priced_db} priced / {total_db} total", flush=True)

    c.execute("SELECT sum(price_chf) FROM transactions WHERE id != 4837")
    vol_db_clean = c.fetchone()[0]
    print(f"Database Total Volume without ID 4837: CHF {vol_db_clean:,.0f}", flush=True)
    distortion = vol_db - vol_db_clean
    print(f"Distortion from single ID 4837: CHF {distortion:,.0f} ({distortion/vol_db*100:.2f}% of cantonal volume!)", flush=True)

    # 2. Geographic Matching Methods Breakdown
    c.execute("""
        SELECT e.match_status, count(*) as cnt 
        FROM enrichments e 
        GROUP BY e.match_status
    """)
    match_modes = c.fetchall()
    print("\n--- Geographic Matching Strategy Breakdown ---", flush=True)
    for m in match_modes:
        print(f"  {m['match_status']:<20}: {m['cnt']:>5} records ({m['cnt']/total_db*100:.1f}%)", flush=True)

    # 3. Coordinate Bounds and Precision
    c.execute("""
        SELECT min(centroid_wgs84_lon), max(centroid_wgs84_lon),
               min(centroid_wgs84_lat), max(centroid_wgs84_lat)
        FROM enrichments
        WHERE centroid_wgs84_lon IS NOT NULL
    """)
    min_lon, max_lon, min_lat, max_lat = c.fetchone()
    print(f"\nCoordinate Bounds: Lon [{min_lon:.5f}, {max_lon:.5f}], Lat [{min_lat:.5f}, {max_lat:.5f}]", flush=True)

    # 4. Duplicate / Collapsed Coordinates (False Precision Risk)
    c.execute("""
        SELECT round(centroid_wgs84_lon, 5) as lon, round(centroid_wgs84_lat, 5) as lat, count(*) as cnt 
        FROM enrichments 
        WHERE centroid_wgs84_lon IS NOT NULL 
        GROUP BY round(centroid_wgs84_lon, 5), round(centroid_wgs84_lat, 5) 
        HAVING cnt > 1 
        ORDER BY cnt DESC LIMIT 10
    """)
    coord_clusters = c.fetchall()
    print(f"\nTop Coincident Coordinate Clusters (Multiple distinct sales stacked at identical lat/lon):", flush=True)
    for cl in coord_clusters:
        print(f"  Coordinates ({cl['lon']}, {cl['lat']}): {cl['cnt']} stacked transactions", flush=True)

    # 5. CSV vs Database Population in Visualizer
    if csv_path.exists():
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = list(csv.DictReader(f))
        print(f"\n--- Visualizer Deliverable CSV Comparison ---", flush=True)
        print(f"  CSV Total Rows: {len(reader)}", flush=True)
        geocoded = sum(1 for r in reader if r.get("centroid_wgs84_lon"))
        print(f"  CSV Geocoded Rows (with lon): {geocoded}", flush=True)
        priced = sum(1 for r in reader if r.get("price_chf") and float(r.get("price_chf") or 0) > 0)
        vol_csv = sum(float(r.get("price_chf") or 0) for r in reader if r.get("price_chf"))
        print(f"  CSV Priced Rows: {priced}", flush=True)
        print(f"  CSV Total Volume: CHF {vol_csv:,.0f}", flush=True)

    conn.close()

if __name__ == "__main__":
    audit_gis_and_kpis(Path("data/state/state.sqlite"), Path("data/exports/geneva_property_transactions.csv"))
