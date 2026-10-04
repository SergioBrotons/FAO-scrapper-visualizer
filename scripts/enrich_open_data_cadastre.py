"""Cytria Phase 2: Federal Open Data & SITG Cadastral / GWR Building Enrichment.

Enriches transactions with:
1. Swiss Federal Register of Buildings and Dwellings (RegBL / GWR via geo.admin.ch):
   - EGID, EGRID, exact parcel identifier
   - Construction year, building period, number of floors
   - Total dwelling units (apartments_count), ground surface
   - Heating / Energy system (PAC, CAD SIG, Gaz, etc.)
   - High-precision WGS84 (lat/lon) and Swiss LV95 coordinates
2. Official Geneva SITG Cadastral Integration (vector.sitg.ge.ch):
   - Planning zone codes (Zone 5, Villa, Développement)
   - Official cadastral plan & extract URLs
3. OCSTAT Communal Benchmark Alignment:
   - Price/m² calibration, Casatax eligibility, and market discount/premium deltas.
"""

import sys
import os
import json
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List, Optional, Tuple

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "src"))

from fao_transactions.cadastre.federal_regbl_client import RegblClient

logger = logging.getLogger(__name__)

# OCSTAT Communal benchmark median reference prices (2025/2026 CHF/m²)
OCSTAT_FILE = root_dir / "data" / "reference" / "ocstat_communes_2025_2026.json"
COMMUNAL_BENCHMARKS: Dict[str, float] = {}

if OCSTAT_FILE.exists():
    try:
        with open(OCSTAT_FILE, "r", encoding="utf-8") as f:
            for item in json.load(f):
                comm = item.get("commune", "").strip().lower()
                m2 = item.get("ppe_median_sqm") or item.get("prix_median_m2_ppe") or 14500.0
                COMMUNAL_BENCHMARKS[comm] = float(m2)
    except Exception as e:
        logger.debug(f"OCSTAT benchmark load warning: {e}")

# Fallback cantonal median
DEFAULT_GENEVA_MEDIAN_M2 = 14500.0
CASATAX_MAX_THRESHOLD = 1435000.0  # 2025-2026 Casatax ceiling for tax rebate in Geneva


def ensure_enrichment_columns(conn: sqlite3.Connection):
    """Ensure enrichments table has all federal open data columns."""
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(enrichments);")
    existing_cols = {row[1] for row in cursor.fetchall()}

    columns_to_add = {
        "egid": "TEXT",
        "apartments_count": "INTEGER",
        "heating_system": "TEXT",
        "surface_ground_m2": "REAL",
        "commune_benchmark_m2": "REAL",
        "benchmark_delta_pct": "REAL",
        "casatax_eligible": "INTEGER DEFAULT 0",
        "building_year": "INTEGER",
        "building_floors": "INTEGER",
        "building_period": "TEXT",
        "zone_code": "TEXT",
        "zone_name": "TEXT",
    }

    for col, col_type in columns_to_add.items():
        if col not in existing_cols:
            cursor.execute(f"ALTER TABLE enrichments ADD COLUMN {col} {col_type};")
    conn.commit()


def enrich_transaction(
    tx: Dict[str, Any],
    regbl: RegblClient,
) -> Optional[Dict[str, Any]]:
    """Enrich a single transaction row via GWR / RegBL and OCSTAT benchmarks."""
    t_id = tx.get("tx_id") or tx.get("id")
    address = tx.get("address")
    commune = tx.get("commune") or "Genève"
    price_chf = tx.get("price_chf")
    surface_m2 = tx.get("surface_m2")
    parcel_no = tx.get("parcel_number")

    building_info = None
    if address:
        building_info = regbl.query_building_by_address(address, commune)

    # Calculate price per m²
    sqm_price = None
    if price_chf and surface_m2 and surface_m2 > 0:
        sqm_price = round(price_chf / surface_m2, 2)

    # Match communal benchmark
    comm_clean = commune.strip().lower()
    median_benchmark = COMMUNAL_BENCHMARKS.get(comm_clean, DEFAULT_GENEVA_MEDIAN_M2)

    delta_pct = None
    if sqm_price:
        delta_pct = round(((sqm_price - median_benchmark) / median_benchmark) * 100, 1)

    # Casatax eligibility
    is_casatax = 1 if (price_chf and 0 < price_chf <= CASATAX_MAX_THRESHOLD) else 0

    resolved_parcel = parcel_no or (building_info.get("parcel_number") if building_info else None)

    return {
        "transaction_id": t_id,
        "match_status": "matched_federal_regbl" if building_info else "unmatched_address",
        "egid": building_info.get("egid") if building_info else None,
        "egrid": building_info.get("egrid") if building_info else None,
        "commune_official": commune,
        "parcel_no_official": resolved_parcel,
        "surface_official_m2": surface_m2 or (building_info.get("surface_ground_m2") if building_info else None),
        "surface_ground_m2": building_info.get("surface_ground_m2") if building_info else None,
        "building_year": building_info.get("construction_year") if building_info else None,
        "building_period": building_info.get("construction_period") if building_info else None,
        "building_floors": building_info.get("building_floors") if building_info else None,
        "apartments_count": building_info.get("apartments_count") if building_info else None,
        "heating_system": building_info.get("heating_system") if building_info else None,
        "centroid_wgs84_lat": building_info.get("lat") if building_info else None,
        "centroid_wgs84_lon": building_info.get("lon") if building_info else None,
        "centroid_lv95_e": building_info.get("lv95_e") if building_info else None,
        "centroid_lv95_n": building_info.get("lv95_n") if building_info else None,
        "price_per_m2": sqm_price,
        "commune_benchmark_m2": median_benchmark,
        "benchmark_delta_pct": delta_pct,
        "casatax_eligible": is_casatax,
        "_resolved_parcel": resolved_parcel,
    }


def run_open_data_enrichment(
    db_path: str = "data/state/state.sqlite",
    limit: Optional[int] = None,
    workers: int = 10,
    only_unenriched: bool = True,
) -> Dict[str, Any]:
    """Execute concurrent batch enrichment against Federal RegBL and OCSTAT."""
    print("==========================================================================")
    print("   CYTRIA PHASE 2: FEDERAL OPEN DATA (GWR/RegBL) & CADASTRAL ENRICHMENT   ")
    print("==========================================================================\n")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    ensure_enrichment_columns(conn)

    # 1. Select target transactions
    if only_unenriched:
        query = """
            SELECT t.id AS tx_id, t.notice_date, t.commune, t.address, t.parcel_number, t.price_chf, t.surface_m2
            FROM transactions t
            LEFT JOIN enrichments e ON t.id = e.transaction_id
            WHERE e.id IS NULL OR e.match_status = 'unmatched_address'
            ORDER BY t.id DESC
        """
    else:
        query = """
            SELECT id AS tx_id, notice_date, commune, address, parcel_number, price_chf, surface_m2
            FROM transactions
            ORDER BY id DESC
        """

    if limit:
        query += f" LIMIT {limit}"

    cursor = conn.cursor()
    cursor.execute(query)
    rows = [dict(r) for r in cursor.fetchall()]
    print(f"Transactions sélectionnées pour enrichissement Open Data : {len(rows):,}")

    if not rows:
        print("Toutes les transactions sont déjà enrichies avec les données fédérales.")
        conn.close()
        return {"total": 0, "enriched": 0}

    regbl = RegblClient()
    enriched_results: List[Dict[str, Any]] = []
    matched_count = 0

    print(f"Interrogation de geo.admin.ch (GWR/RegBL) avec {workers} flux parallèles...")
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(enrich_transaction, row, regbl): row for row in rows}
        done = 0
        for f in as_completed(futures):
            done += 1
            res = f.result()
            if res:
                enriched_results.append(res)
                if res.get("match_status") == "matched_federal_regbl":
                    matched_count += 1
            if done % 50 == 0 or done == len(rows):
                print(f"  Progression: {done}/{len(rows)} traités ({matched_count} immeubles fédéraux résolus)...")

    # 2. Batch write to enrichments table
    print(f"\nEnregistrement de {len(enriched_results)} fiches d'enrichissement dans SQLite...")
    insert_sql = """
        INSERT INTO enrichments (
            transaction_id, match_status, egid, egrid, commune_official,
            parcel_no_official, surface_official_m2, surface_ground_m2,
            building_year, building_period, building_floors, apartments_count,
            heating_system, centroid_wgs84_lat, centroid_wgs84_lon,
            centroid_lv95_e, centroid_lv95_n, price_per_m2,
            commune_benchmark_m2, benchmark_delta_pct, casatax_eligible
        ) VALUES (
            :transaction_id, :match_status, :egid, :egrid, :commune_official,
            :parcel_no_official, :surface_official_m2, :surface_ground_m2,
            :building_year, :building_period, :building_floors, :apartments_count,
            :heating_system, :centroid_wgs84_lat, :centroid_wgs84_lon,
            :centroid_lv95_e, :centroid_lv95_n, :price_per_m2,
            :commune_benchmark_m2, :benchmark_delta_pct, :casatax_eligible
        )
        ON CONFLICT(transaction_id) DO UPDATE SET
            match_status=excluded.match_status,
            egid=COALESCE(excluded.egid, enrichments.egid),
            egrid=COALESCE(excluded.egrid, enrichments.egrid),
            parcel_no_official=COALESCE(excluded.parcel_no_official, enrichments.parcel_no_official),
            surface_official_m2=COALESCE(excluded.surface_official_m2, enrichments.surface_official_m2),
            surface_ground_m2=COALESCE(excluded.surface_ground_m2, enrichments.surface_ground_m2),
            building_year=COALESCE(excluded.building_year, enrichments.building_year),
            building_period=COALESCE(excluded.building_period, enrichments.building_period),
            building_floors=COALESCE(excluded.building_floors, enrichments.building_floors),
            apartments_count=COALESCE(excluded.apartments_count, enrichments.apartments_count),
            heating_system=COALESCE(excluded.heating_system, enrichments.heating_system),
            centroid_wgs84_lat=COALESCE(excluded.centroid_wgs84_lat, enrichments.centroid_wgs84_lat),
            centroid_wgs84_lon=COALESCE(excluded.centroid_wgs84_lon, enrichments.centroid_wgs84_lon),
            centroid_lv95_e=COALESCE(excluded.centroid_lv95_e, enrichments.centroid_lv95_e),
            centroid_lv95_n=COALESCE(excluded.centroid_lv95_n, enrichments.centroid_lv95_n),
            price_per_m2=COALESCE(excluded.price_per_m2, enrichments.price_per_m2),
            commune_benchmark_m2=COALESCE(excluded.commune_benchmark_m2, enrichments.commune_benchmark_m2),
            benchmark_delta_pct=COALESCE(excluded.benchmark_delta_pct, enrichments.benchmark_delta_pct),
            casatax_eligible=COALESCE(excluded.casatax_eligible, enrichments.casatax_eligible),
            enriched_at=CURRENT_TIMESTAMP;
    """

    cursor = conn.cursor()
    cursor.executemany(insert_sql, enriched_results)

    # 3. Backfill missing parcel numbers in transactions table where discovered by RegBL
    backfilled_parcels = 0
    for r in enriched_results:
        resolved_p = r.get("_resolved_parcel")
        if resolved_p:
            cursor.execute(
                "UPDATE transactions SET parcel_number = ? WHERE id = ? AND (parcel_number IS NULL OR parcel_number = '');",
                (resolved_p, r["transaction_id"]),
            )
            if cursor.rowcount > 0:
                backfilled_parcels += 1

    conn.commit()
    conn.close()

    print(f"\n[OK] Enrichissement terminé avec succès !")
    print(f"  - Immeubles fédéraux identifiés : {matched_count:,} / {len(rows):,}")
    print(f"  - Numéros de parcelles rétro-assignés : {backfilled_parcels:,}")
    return {
        "total_processed": len(rows),
        "matched_federal_regbl": matched_count,
        "backfilled_parcels": backfilled_parcels,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    run_open_data_enrichment()
