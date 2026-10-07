"""SITG CAD_PISCINE Ingestion & Spatial Parcel Matcher.

Authoritative in-ground swimming pool register from the Canton of Geneva (SITG).
Ingests all official pool polygons, computes spatial centroids, and performs
spatial intersection joins with existing cadastral parcel polygons in SQLite.
"""

import sys
import os
import json
import sqlite3
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# Ensure stdout/stderr handles UTF-8 on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import httpx
from rich.console import Console
from rich.table import Table
from shapely.geometry import shape, Point
from shapely.strtree import STRtree

console = Console(highlight=False)
ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR / "data" / "state" / "state.sqlite"

SITG_PISCINE_URL = "https://vector.sitg.ge.ch/arcgis/rest/services/CAD_PISCINE/FeatureServer/0/query"
SITG_COMMUNE_URL = "https://vector.sitg.ge.ch/arcgis/rest/services/CAD_COMMUNE/FeatureServer/0/query"

# Fallback clean commune mapping by NO_COMM
COMMUNE_NAMES = {
    1: "Aire-la-Ville", 2: "Anières", 3: "Avully", 4: "Avusy", 5: "Bardonnex",
    6: "Bellevue", 7: "Bernex", 8: "Carouge", 9: "Cartigny", 10: "Céligny",
    11: "Chancy", 12: "Chêne-Bougeries", 13: "Chêne-Bourg", 14: "Choulex",
    15: "Collex-Bossy", 16: "Collonge-Bellerive", 17: "Cologny", 18: "Confignon",
    19: "Corsier", 20: "Dardagny", 21: "Genève-Cité", 22: "Genève-Eaux-Vives",
    23: "Genève-Petit-Saconnex", 24: "Genève-Plainpalais", 25: "Genthod",
    26: "Grand-Saconnex", 27: "Gy", 28: "Hermance", 29: "Jussy", 30: "Laconnex",
    31: "Lancy", 32: "Meinier", 33: "Meyrin", 34: "Onex", 35: "Perly-Certoux",
    36: "Plan-les-Ouates", 37: "Pregny-Chambésy", 38: "Presinge", 39: "Puplinge",
    40: "Russin", 41: "Satigny", 42: "Soral", 43: "Thônex", 44: "Troinex",
    45: "Vandœuvres", 46: "Vernier", 47: "Versoix", 48: "Veyrier"
}


def ensure_schema(conn: sqlite3.Connection):
    """Ensure geneva_pools table and enrichment pool columns exist."""
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS geneva_pools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT DEFAULT 'sitg_cadastre',
            objectid INTEGER UNIQUE NOT NULL,
            commune_code INTEGER,
            commune_name TEXT,
            mutation_num TEXT,
            mutation_date TEXT,
            surface_m2 REAL,
            perimeter_m REAL,
            confidence_score REAL DEFAULT 1.0,
            centroid_wgs84_lon REAL,
            centroid_wgs84_lat REAL,
            geom_geojson_wgs84 TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pools_commune_code ON geneva_pools(commune_code);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pools_commune_name ON geneva_pools(commune_name);")

    # Enrichments table columns
    cur.execute("PRAGMA table_info(enrichments);")
    existing_cols = {row[1] for row in cur.fetchall()}
    new_cols = {
        "has_pool": "INTEGER DEFAULT 0",
        "pool_count": "INTEGER DEFAULT 0",
        "pool_surface_m2": "REAL DEFAULT 0.0",
        "pool_status": "TEXT DEFAULT 'none'",
        "pool_details_json": "TEXT",
    }
    for col, col_type in new_cols.items():
        if col not in existing_cols:
            cur.execute(f"ALTER TABLE enrichments ADD COLUMN {col} {col_type};")

    conn.commit()


def fetch_commune_mapping() -> Dict[int, str]:
    """Fetch official commune names from SITG CAD_COMMUNE."""
    mapping = dict(COMMUNE_NAMES)
    try:
        r = httpx.get(
            SITG_COMMUNE_URL,
            params={"where": "1=1", "outFields": "NO_COMM,COMMUNE", "f": "json"},
            timeout=15.0
        )
        if r.status_code == 200:
            for feat in r.json().get("features", []):
                attrs = feat.get("attributes", {})
                no_comm = attrs.get("NO_COMM")
                name = attrs.get("COMMUNE")
                if no_comm and name:
                    mapping[int(no_comm)] = name
    except Exception as e:
        console.print(f"[dim yellow]Warning fetching commune names: {e}, using fallback map.[/dim yellow]")
    return mapping


def fetch_all_sitg_pools() -> List[Dict[str, Any]]:
    """Fetch all official swimming pool features from SITG REST in WGS84 GeoJSON."""
    console.print("[cyan]Fetching official pool polygons from SITG CAD_PISCINE FeatureServer...[/cyan]")
    features: List[Dict[str, Any]] = []
    batch_size = 4000
    offset = 0

    client = httpx.Client(timeout=45.0)
    while True:
        params = {
            "where": "1=1",
            "outFields": "*",
            "f": "geojson",
            "outSR": 4326,
            "resultOffset": offset,
            "resultRecordCount": batch_size,
        }
        res = client.get(SITG_PISCINE_URL, params=params)
        res.raise_for_status()
        data = res.json()
        batch_features = data.get("features", [])
        if not batch_features:
            break
        features.extend(batch_features)
        console.print(f"  -> Fetched batch of [bold]{len(batch_features)}[/bold] pools (total so far: {len(features)})")
        if len(batch_features) < batch_size:
            break
        offset += batch_size

    console.print(f"[bold green]Successfully retrieved {len(features)} total pools from SITG.[/bold green]")
    return features


def sync_pools_to_database(conn: sqlite3.Connection, features: List[Dict[str, Any]], commune_map: Dict[int, str]) -> List[Tuple[Any, Dict[str, Any]]]:
    """
    Save pools into geneva_pools table and prepare Shapely geometries.
    Returns list of (shapely_geometry, pool_metadata_dict).
    """
    cur = conn.cursor()
    pool_records = []
    shapely_pool_list = []

    for f in features:
        props = f.get("properties", {})
        geom_json = f.get("geometry", {})
        if not geom_json or not geom_json.get("coordinates"):
            continue

        obj_id = props.get("OBJECTID")
        mut_com = props.get("MUTCOM")
        commune_name = commune_map.get(int(mut_com), f"Commune #{mut_com}") if mut_com else None
        mut_num = str(props.get("MUTNUM") or "")

        # Format mutation date if epoch
        datedt_val = props.get("DATEDT")
        mut_date_str = None
        if datedt_val:
            try:
                # SITG returns epoch timestamp in milliseconds
                dt = datetime.datetime.fromtimestamp(datedt_val / 1000.0, tz=datetime.timezone.utc)
                mut_date_str = dt.strftime("%Y-%m-%d")
            except Exception:
                mut_date_str = str(datedt_val)

        surf_m2 = props.get("Shape__Area") or 0.0
        perim_m = props.get("Shape__Length") or 0.0

        # Compute centroid using Shapely
        try:
            poly_geom = shape(geom_json)
            centroid = poly_geom.centroid
            lon, lat = centroid.x, centroid.y
        except Exception:
            continue

        pool_records.append((
            "sitg_cadastre",
            obj_id,
            mut_com,
            commune_name,
            mut_num,
            mut_date_str,
            round(surf_m2, 2),
            round(perim_m, 2),
            1.0,
            round(lon, 6),
            round(lat, 6),
            json.dumps(geom_json)
        ))

        meta = {
            "objectid": obj_id,
            "commune_code": mut_com,
            "commune_name": commune_name,
            "mutation_num": mut_num,
            "mutation_date": mut_date_str,
            "surface_m2": round(surf_m2, 1),
            "lon": round(lon, 6),
            "lat": round(lat, 6)
        }
        shapely_pool_list.append((poly_geom, meta))

    cur.executemany("""
        INSERT INTO geneva_pools (
            source, objectid, commune_code, commune_name, mutation_num,
            mutation_date, surface_m2, perimeter_m, confidence_score,
            centroid_wgs84_lon, centroid_wgs84_lat, geom_geojson_wgs84
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(objectid) DO UPDATE SET
            commune_code = excluded.commune_code,
            commune_name = excluded.commune_name,
            mutation_num = excluded.mutation_num,
            mutation_date = excluded.mutation_date,
            surface_m2 = excluded.surface_m2,
            perimeter_m = excluded.perimeter_m,
            centroid_wgs84_lon = excluded.centroid_wgs84_lon,
            centroid_wgs84_lat = excluded.centroid_wgs84_lat,
            geom_geojson_wgs84 = excluded.geom_geojson_wgs84;
    """, pool_records)

    conn.commit()
    console.print(f"[bold green]Stored {len(pool_records)} swimming pools in table geneva_pools.[/bold green]")
    return shapely_pool_list


def perform_parcel_spatial_join(conn: sqlite3.Connection, shapely_pools: List[Tuple[Any, Dict[str, Any]]]):
    """
    Perform spatial join between cadastral parcel polygons and swimming pool polygons.
    Updates enrichments table with pool count, total surface, status, and metadata JSON.
    """
    console.print("[cyan]Building R-tree spatial index (STRtree) for instant pool queries...[/cyan]")
    geoms = [p[0] for p in shapely_pools]
    metas = [p[1] for p in shapely_pools]
    tree = STRtree(geoms)

    cur = conn.cursor()
    # Reset existing pool flags
    cur.execute("""
        UPDATE enrichments
        SET has_pool = 0, pool_count = 0, pool_surface_m2 = 0.0, pool_status = 'none', pool_details_json = NULL;
    """)
    conn.commit()

    # Load all parcel polygons from enrichments
    cur.execute("""
        SELECT e.transaction_id, e.geom_geojson_wgs84, e.commune_official, e.parcel_no_official
        FROM enrichments e
        WHERE e.geom_geojson_wgs84 IS NOT NULL;
    """)
    parcel_rows = cur.fetchall()
    console.print(f"[cyan]Evaluating spatial intersections for [bold]{len(parcel_rows)}[/bold] cadastral parcels...[/cyan]")

    matched_parcels = 0
    total_pool_surface = 0.0
    updates = []

    for tid, geom_str, comm, p_no in parcel_rows:
        try:
            parcel_json = json.loads(geom_str)
            parcel_geom = shape(parcel_json)
        except Exception:
            continue

        # Fast R-tree bbox candidate filter
        candidate_idxs = tree.query(parcel_geom)
        if len(candidate_idxs) == 0:
            continue

        intersecting_pools = []
        for idx in candidate_idxs:
            pool_geom = geoms[idx]
            # Spatial intersection check (or pool centroid inside parcel)
            if parcel_geom.intersects(pool_geom):
                intersecting_pools.append(metas[idx])

        if intersecting_pools:
            matched_parcels += 1
            pool_count = len(intersecting_pools)
            tot_surf = round(sum(p["surface_m2"] for p in intersecting_pools), 1)
            total_pool_surface += tot_surf
            details_json = json.dumps(intersecting_pools, ensure_ascii=False)

            updates.append((1, pool_count, tot_surf, "registered", details_json, tid))

    console.print(f"  -> Found [bold green]{matched_parcels}[/bold green] parcels containing official swimming pools!")

    # Batch update enrichments table
    cur.executemany("""
        UPDATE enrichments
        SET has_pool = ?, pool_count = ?, pool_surface_m2 = ?, pool_status = ?, pool_details_json = ?
        WHERE transaction_id = ?;
    """, updates)
    conn.commit()

    # Print summary statistics table
    table = Table(title="Geneva Swimming Pool Intelligence Overview")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="bold green")

    table.add_row("Total Cantonal In-Ground Pools (SITG)", f"{len(shapely_pools):,}")
    table.add_row("Properties/Transactions with Pools", f"{matched_parcels:,}")
    table.add_row("Total Matched Pool Basin Surface", f"{total_pool_surface:,.1f} m2")
    table.add_row("Average Pool Surface", f"{(total_pool_surface / max(matched_parcels, 1)):.1f} m2")

    console.print(table)

    # Top communes with pools in portfolio
    cur.execute("""
        SELECT e.commune_official, COUNT(*) as cnt, ROUND(AVG(e.pool_surface_m2), 1) as avg_m2, SUM(e.pool_count) as pools
        FROM enrichments e
        WHERE e.has_pool = 1
        GROUP BY e.commune_official
        ORDER BY cnt DESC
        LIMIT 10;
    """)
    commune_stats = cur.fetchall()

    comm_table = Table(title="Top 10 Communes with Pools in Cytria Transactions")
    comm_table.add_column("Commune", style="yellow")
    comm_table.add_column("Transactions with Pools", style="green")
    comm_table.add_column("Total Basins", style="cyan")
    comm_table.add_column("Avg Basin Size (m2)", style="magenta")

    for row in commune_stats:
        comm_table.add_row(str(row[0] or "Inconnu"), str(row[1]), str(row[3]), f"{row[2]} m2")

    console.print(comm_table)


def run_pool_ingestion():
    console.rule("[bold #00939D]Cytria x SITG Cadastre Swimming Pool Ingestion Engine[/bold #00939D]")
    if not DB_PATH.exists():
        console.print(f"[red]Database not found at {DB_PATH}[/red]")
        sys.exit(1)

    conn = sqlite3.connect(str(DB_PATH))
    try:
        ensure_schema(conn)
        commune_map = fetch_commune_mapping()
        features = fetch_all_sitg_pools()
        shapely_pools = sync_pools_to_database(conn, features, commune_map)
        perform_parcel_spatial_join(conn, shapely_pools)
        console.print("\n[bold green][OK] Pool Intelligence ingestion and parcel join complete![/bold green]\n")
    finally:
        conn.close()


if __name__ == "__main__":
    run_pool_ingestion()
