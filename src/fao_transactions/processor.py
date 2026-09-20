"""Unified high-speed batch processor and exporter for Geneva property transactions."""

import sys
import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from concurrent.futures import ProcessPoolExecutor, as_completed
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
from fao_transactions.parser.pdf_parser import FaoPdfParser
from fao_transactions.parser.models import TransactionRecord
from fao_transactions.storage.db import Database
from fao_transactions.cadastre.sitg_client import SitgClient

console = Console(legacy_windows=False)


def _parse_single_file(pdf_path_str: str) -> List[Dict[str, Any]]:
    """Worker function for multiprocess PDF parsing."""
    try:
        p = FaoPdfParser()
        records = p.parse_pdf(Path(pdf_path_str))
        return [r.model_dump() for r in records]
    except Exception:
        return []


class UnifiedBatchProcessor:
    """Processes both Registre Foncier (art. 157 LaCC) and LDTR (art. 39 LDTR) notices."""

    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()
        self.exports_dir = Path(settings.storage.exports_dir)
        self.exports_dir.mkdir(parents=True, exist_ok=True)

    def parse_all_pdfs(
        self,
        rf_dir: Optional[Path] = None,
        ldtr_dir: Optional[Path] = None,
        workers: int = 4,
    ) -> List[TransactionRecord]:
        """Parse all PDFs across both archives using multiprocessing."""
        rf_folder = rf_dir or Path("data/raw/transactions")
        ldtr_folder = ldtr_dir or Path("data/raw/ldtr")

        rf_files = list(rf_folder.glob("*.pdf")) if rf_folder.exists() else []
        ldtr_files = list(ldtr_folder.glob("*.pdf")) if ldtr_folder.exists() else []
        all_files = rf_files + ldtr_files

        console.rule("[bold cyan]Batch Parsing Property Transaction PDFs[/bold cyan]")
        console.print(f"Registre Foncier archive: [bold]{len(rf_files)}[/bold] PDFs ({rf_folder})")
        console.print(f"LDTR Apartment archive:   [bold]{len(ldtr_files)}[/bold] PDFs ({ldtr_folder})")
        console.print(f"Total PDFs to process:    [bold]{len(all_files)}[/bold] files\n")

        if not all_files:
            console.print("[yellow]No PDF files found to parse.[/yellow]")
            return []

        start_time = time.time()
        file_paths = [str(f.resolve()) for f in all_files]
        all_records: List[TransactionRecord] = []

        console.print(f"Starting multiprocessing parser with [bold]{workers}[/bold] CPU workers...")
        with ProcessPoolExecutor(max_workers=workers) as executor:
            future_to_file = {executor.submit(_parse_single_file, path): path for path in file_paths}
            done_count = 0
            for future in as_completed(future_to_file):
                done_count += 1
                result_dicts = future.result()
                for d in result_dicts:
                    all_records.append(TransactionRecord(**d))

                if done_count % 1000 == 0 or done_count == len(all_files):
                    elapsed = time.time() - start_time
                    rate = done_count / elapsed if elapsed > 0 else 0
                    console.print(f"  Parsed {done_count}/{len(all_files)} files ({rate:.0f} files/sec)... Records found: {len(all_records)}")

        elapsed = time.time() - start_time
        console.print(f"\n[bold green][OK] Completed parsing {len(all_files)} files in {elapsed:.1f}s ({len(all_files)/elapsed:.0f} files/sec)![/bold green]")
        console.print(f"Total extracted transaction records: [bold cyan]{len(all_records)}[/bold cyan]\n")
        return all_records

    def save_to_database(self, records: List[TransactionRecord]) -> Dict[str, int]:
        """Save parsed records into SQLite database with hash deduplication."""
        console.rule("[bold cyan]Database Ingestion & Deduplication[/bold cyan]")
        inserted = 0
        duplicates = 0

        for r in records:
            res = self.db.insert_transaction_record(r)
            if res is not None:
                inserted += 1
            else:
                duplicates += 1

        console.print(f"[bold green][OK] Successfully ingested into SQLite:[/bold green] {self.db.db_path}")
        console.print(f"  - New unique transactions inserted: [bold green]{inserted}[/bold green]")
        console.print(f"  - Duplicates skipped: [yellow]{duplicates}[/yellow]\n")
        return {"inserted": inserted, "duplicates": duplicates}

    def export_data(self) -> Dict[str, str]:
        """Export all database records to CSV, Excel, and GeoJSON."""
        console.rule("[bold cyan]Exporting Unified Deliverables[/bold cyan]")

        with self.db.get_connection() as conn:
            query = """
                SELECT 
                    t.id,
                    t.source_category,
                    t.notice_date,
                    t.commune,
                    t.commune_section,
                    t.parcel_number,
                    t.transaction_type,
                    t.property_type,
                    t.nature,
                    t.address,
                    t.rooms,
                    t.floor,
                    t.unit_number,
                    t.case_number,
                    t.surface_m2,
                    t.seller,
                    t.buyer,
                    t.price_raw,
                    t.price_chf,
                    t.file_source,
                    t.transaction_hash,
                    e.egrid,
                    e.surface_official_m2,
                    e.centroid_wgs84_lon,
                    e.centroid_wgs84_lat,
                    e.centroid_lv95_e,
                    e.centroid_lv95_n
                FROM transactions t
                LEFT JOIN enrichments e ON t.id = e.transaction_id
                ORDER BY t.notice_date DESC, t.id DESC
            """
            df = pd.read_sql_query(query, conn)

        console.print(f"Total records in database: [bold]{len(df)}[/bold]")

        # 1. Export CSV
        csv_path = self.exports_dir / "geneva_property_transactions.csv"
        try:
            df.to_csv(csv_path, index=False, encoding="utf-8-sig")
            console.print(f"[bold green][OK] CSV Exported:[/bold green] {csv_path.name} ({len(df)} rows)")
        except PermissionError:
            csv_path = self.exports_dir / "geneva_property_transactions_geocoded.csv"
            df.to_csv(csv_path, index=False, encoding="utf-8-sig")
            console.print(f"[bold yellow][Notice] Original CSV was open in another app. Saved to:[/bold yellow] {csv_path.name}")

        # 2. Export Excel
        xlsx_path = self.exports_dir / "geneva_property_transactions.xlsx"
        try:
            df.to_excel(xlsx_path, index=False, engine="openpyxl")
            console.print(f"[bold green][OK] Excel Exported:[/bold green] {xlsx_path.name}")
        except PermissionError:
            xlsx_path = self.exports_dir / "geneva_property_transactions_geocoded.xlsx"
            df.to_excel(xlsx_path, index=False, engine="openpyxl")
            console.print(f"[bold yellow][Notice] Original Excel was open in another app. Saved to:[/bold yellow] {xlsx_path.name}")

        # 3. Export GeoJSON for records with coordinates
        geo_records = []
        for _, row in df.iterrows():
            lon = row["centroid_wgs84_lon"]
            lat = row["centroid_wgs84_lat"]
            if pd.notna(lon) and pd.notna(lat):
                props = {k: (None if pd.isna(v) else v) for k, v in row.items() if k not in ("centroid_wgs84_lon", "centroid_wgs84_lat")}
                geo_records.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(lon), float(lat)],
                    },
                    "properties": props,
                })

        geojson_path = self.exports_dir / "geneva_property_transactions.geojson"
        geojson_doc = {
            "type": "FeatureCollection",
            "name": "geneva_property_transactions",
            "features": geo_records,
        }
        geojson_path.write_text(json.dumps(geojson_doc, ensure_ascii=False, indent=2), encoding="utf-8")
        console.print(f"[bold green][OK] GeoJSON Exported:[/bold green] {geojson_path.name} ({len(geo_records)} georeferenced features)\n")

        return {
            "csv": str(csv_path),
            "xlsx": str(xlsx_path),
            "geojson": str(geojson_path),
        }
