"""High-speed batch cadastral enricher using official Geneva SITG REST service."""

import sys
import re
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from rich.console import Console
from rich.table import Table

from fao_transactions.config import settings
from fao_transactions.storage.db import Database
from fao_transactions.cadastre.sitg_client import SitgClient
from fao_transactions.cadastre.coordinate_transform import lv95_to_wgs84

console = Console(legacy_windows=False)


def extract_base_parcel(parcel_str: Optional[str]) -> Optional[str]:
    """Extract base numerical parcel number (e.g. '6089-104' -> '6089', '47/6928' -> '6928')."""
    if not parcel_str:
        return None
    cleaned = parcel_str.strip()
    # If contains slash '47/6928'
    if "/" in cleaned:
        cleaned = cleaned.split("/")[-1].strip()
    # If contains dash or hyphen '6089-104'
    if "-" in cleaned:
        cleaned = cleaned.split("-")[0].strip()
    if cleaned.isdigit():
        return cleaned
    match = re.search(r"\b([0-9]{1,6})\b", cleaned)
    return match.group(1) if match else cleaned


def parse_address_parts(addr_str: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """Extract street name and street number from an address string."""
    if not addr_str:
        return None, None
    cleaned = addr_str.strip().lstrip("0123456789, -–—")
    # Match number at end or start
    num_match = re.search(r"\b([0-9]{1,4}[A-Za-z]?)\b", addr_str)
    num = num_match.group(1) if num_match else None

    # Strip zip code e.g. 1205, 1227
    street_clean = re.sub(r"\b12[0-9]{2}\b.*$", "", addr_str).strip()
    # Strip street number
    if num:
        street_clean = re.sub(rf"\b{re.escape(num)}\b", "", street_clean).strip(" ,-–—")

    # Clean street words
    street_clean = re.sub(r"^(?:Route|Rue|Chemin|Avenue|Boulevard|Place|Quai|Allée|Esplanade|Promenade)\s+(?:de\s+la\s+|du\s+|de\s+|d['’]|des\s+)?", "", street_clean, flags=re.IGNORECASE).strip()
    return street_clean, num


class CadastralEnricher:
    """Enriches database transactions with official SITG cadastre geometries and coordinates."""

    def __init__(self, db: Optional[Database] = None, sitg: Optional[SitgClient] = None):
        self.db = db or Database()
        self.sitg = sitg or SitgClient()
        self.parcel_cache: Dict[str, Optional[Dict[str, Any]]] = {}
        self.address_cache: Dict[str, Optional[Dict[str, Any]]] = {}

    def lookup_parcel(self, commune: str, parcel: str, section: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Query SITG CAD_PARCELLE_MENSU with in-memory caching."""
        base_p = extract_base_parcel(parcel)
        if not base_p:
            return None

        cache_key = f"{commune.lower()}_{section or ''}_{base_p}"
        if cache_key in self.parcel_cache:
            return self.parcel_cache[cache_key]

        res = self.sitg.query_parcel(commune=commune, parcel_number=base_p, section=section)
        self.parcel_cache[cache_key] = res
        return res

    def lookup_address(self, commune: str, address_str: str) -> Optional[Dict[str, Any]]:
        """Query SITG CAD_ADRESSE with in-memory caching."""
        if not address_str:
            return None

        cache_key = f"{commune.lower()}_{address_str.lower().strip()}"
        if cache_key in self.address_cache:
            return self.address_cache[cache_key]

        street, num = parse_address_parts(address_str)
        where_clauses = [f"(COMMUNE='{commune}' OR UPPER(COMMUNE)='{commune.upper()}')"]
        if street and len(street) >= 3:
            safe_st = street.replace("'", "''")
            where_clauses.append(f"ADRESSE LIKE '%{safe_st}%'")
        if num:
            where_clauses.append(f"NO_ADRESSE LIKE '{num}%'")

        where = " AND ".join(where_clauses)
        features = self.sitg._query_layer(settings.sitg.layers.addresses, where, return_geometry=True)
        if features:
            f = features[0]
            # Attributes from CAD_ADRESSE
            attr = f.get("properties", {})
            x = attr.get("Y")  # In SITG Y is Easting (2.5M)
            y = attr.get("X")  # In SITG X is Northing (1.1M)
            if x and y:
                lon, lat = lv95_to_wgs84(float(x), float(y))
                f["centroid_lv95"] = (float(x), float(y))
                f["centroid_wgs84"] = (lon, lat)
            self.address_cache[cache_key] = f
            return f

        self.address_cache[cache_key] = None
        return None

    def enrich_all(self, workers: int = 8) -> Dict[str, Any]:
        """Fetch all unenriched transactions from database and enrich concurrently."""
        console.rule("[bold cyan]SITG Cadastral Geocoding & Parcel Enrichment[/bold cyan]")

        with self.db.get_connection() as conn:
            query = """
                SELECT id, source_category, commune, commune_section, parcel_number, address 
                FROM transactions
                WHERE id NOT IN (SELECT transaction_id FROM enrichments)
                ORDER BY id ASC;
            """
            rows = conn.execute(query).fetchall()

        console.print(f"Total transactions to enrich: [bold]{len(rows)}[/bold]")
        if not rows:
            console.print("[green]All transactions are already enriched![/green]")
            return {"total": 0, "enriched": 0}

        start_time = time.time()
        matched_parcels = 0
        matched_addresses = 0
        not_found = 0

        def process_row(row: Any) -> Tuple[int, Optional[Dict[str, Any]], str]:
            t_id = row["id"]
            cat = row["source_category"]
            comm = row["commune"]
            sec = row["commune_section"]
            p_num = row["parcel_number"]
            addr = row["address"]

            # 1. First priority: direct parcel lookup if parcel_number is present
            if p_num:
                feat = self.lookup_parcel(commune=comm, parcel=p_num, section=sec)
                if feat:
                    return (t_id, feat, "matched_parcel")

            # 2. Second priority: address lookup (for LDTR or when parcel lookup yielded no match)
            if addr:
                feat = self.lookup_address(commune=comm, address_str=addr)
                if feat:
                    return (t_id, feat, "matched_address")

            return (t_id, None, "not_found")

        console.print(f"Querying SITG REST endpoints with [bold]{workers}[/bold] concurrent workers...")
        enrichment_records: List[Dict[str, Any]] = []

        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_id = {executor.submit(process_row, row): row["id"] for row in rows}
            done_count = 0

            for future in as_completed(future_to_id):
                done_count += 1
                t_id, feat, status = future.result()

                rec = {
                    "transaction_id": t_id,
                    "match_status": status,
                    "egrid": None,
                    "commune_official": None,
                    "parcel_no_official": None,
                    "surface_official_m2": None,
                    "plan_rf": None,
                    "price_per_m2": None,
                    "lien_extrait_rf": None,
                    "extrait_rdppf_url": None,
                    "centroid_lv95_e": None,
                    "centroid_lv95_n": None,
                    "centroid_wgs84_lon": None,
                    "centroid_wgs84_lat": None,
                    "geom_geojson_wgs84": None,
                }

                if feat:
                    props = feat.get("properties", {})
                    c_lv95 = feat.get("centroid_lv95")
                    c_wgs = feat.get("centroid_wgs84")

                    rec["egrid"] = props.get("EGRID")
                    rec["commune_official"] = props.get("COMMUNE")
                    rec["parcel_no_official"] = str(props.get("NO_PARCELLE") or "")
                    rec["surface_official_m2"] = props.get("SURFACE") or props.get("SUPERFICIE")
                    rec["plan_rf"] = props.get("PLAN_RF")
                    rec["lien_extrait_rf"] = props.get("LIEN_WWW")
                    rec["extrait_rdppf_url"] = props.get("EXTRAIT_RDPPF_PDF")

                    if c_lv95:
                        rec["centroid_lv95_e"] = c_lv95[0]
                        rec["centroid_lv95_n"] = c_lv95[1]
                    if c_wgs:
                        rec["centroid_wgs84_lon"] = c_wgs[0]
                        rec["centroid_wgs84_lat"] = c_wgs[1]

                    geom_4326 = feat.get("geometry_4326") or feat.get("geometry")
                    if geom_4326:
                        rec["geom_geojson_wgs84"] = json.dumps(geom_4326)

                    if status == "matched_parcel":
                        matched_parcels += 1
                    else:
                        matched_addresses += 1
                else:
                    not_found += 1

                enrichment_records.append(rec)

                if done_count % 1000 == 0 or done_count == len(rows):
                    elapsed = time.time() - start_time
                    console.print(f"  Processed {done_count}/{len(rows)} ({done_count/elapsed:.0f} req/sec)... Matched: {matched_parcels + matched_addresses}")

        # Batch insert into enrichments table
        console.print(f"\n[cyan]Saving {len(enrichment_records)} enrichment records to SQLite...[/cyan]")
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(
                """
                INSERT OR REPLACE INTO enrichments (
                    transaction_id, egrid, commune_official, parcel_no_official,
                    surface_official_m2, plan_rf, price_per_m2, lien_extrait_rf,
                    extrait_rdppf_url, centroid_lv95_e, centroid_lv95_n,
                    centroid_wgs84_lon, centroid_wgs84_lat, geom_geojson_wgs84,
                    match_status
                ) VALUES (
                    :transaction_id, :egrid, :commune_official, :parcel_no_official,
                    :surface_official_m2, :plan_rf, :price_per_m2, :lien_extrait_rf,
                    :extrait_rdppf_url, :centroid_lv95_e, :centroid_lv95_n,
                    :centroid_wgs84_lon, :centroid_wgs84_lat, :geom_geojson_wgs84,
                    :match_status
                );
                """,
                enrichment_records,
            )
            conn.commit()

        elapsed = time.time() - start_time
        console.print(f"[bold green][OK] Cadastral enrichment complete in {elapsed:.1f}s![/bold green]")
        table = Table(title="SITG Enrichment Summary")
        table.add_column("Category", style="cyan")
        table.add_column("Count", style="bold")
        table.add_row("Matched by Cadastral Parcel", f"[green]{matched_parcels}[/green]")
        table.add_row("Matched by Official Address", f"[green]{matched_addresses}[/green]")
        table.add_row("Total Geocoded Transactions", f"[bold green]{matched_parcels + matched_addresses}[/bold green]")
        table.add_row("Unmatched / Historical", f"[dim]{not_found}[/dim]")
        console.print(table)

        return {
            "total": len(rows),
            "matched_parcels": matched_parcels,
            "matched_addresses": matched_addresses,
            "geocoded_total": matched_parcels + matched_addresses,
            "not_found": not_found,
        }
