"""SQLite database schema and operations for the property transactions pipeline."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fao_transactions.config import settings


class Database:
    """Manages SQLite state storage for publications, transactions, and cadastral enrichments."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path or settings.storage.database_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Return a new SQLite connection with foreign keys and dict-like rows enabled."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_db(self) -> None:
        """Create tables and indexes if they do not exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Publications table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS publications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    issue_id TEXT UNIQUE NOT NULL,
                    issue_date TEXT,
                    issue_no TEXT,
                    title TEXT,
                    url TEXT,
                    file_path TEXT,
                    sha256 TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    publication_id INTEGER,
                    transaction_hash TEXT UNIQUE NOT NULL,
                    source_category TEXT DEFAULT 'Registre_Foncier',
                    notice_date TEXT,
                    commune TEXT NOT NULL,
                    commune_section TEXT,
                    parcel_number TEXT,
                    transaction_type TEXT DEFAULT 'Vente',
                    property_type TEXT,
                    nature TEXT,
                    address TEXT,
                    rooms REAL,
                    floor TEXT,
                    unit_number TEXT,
                    case_number TEXT,
                    surface_m2 REAL,
                    seller TEXT,
                    buyer TEXT,
                    price_raw TEXT,
                    price_chf REAL,
                    file_source TEXT,
                    raw_text TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (publication_id) REFERENCES publications(id) ON DELETE SET NULL
                );
            """)

            # Automated migration for existing databases missing new columns
            cursor.execute("PRAGMA table_info(transactions);")
            existing_cols = {row["name"] for row in cursor.fetchall()}
            new_cols = {
                "source_category": "TEXT DEFAULT 'Registre_Foncier'",
                "transaction_type": "TEXT DEFAULT 'Vente'",
                "property_type": "TEXT",
                "address": "TEXT",
                "rooms": "REAL",
                "floor": "TEXT",
                "unit_number": "TEXT",
                "case_number": "TEXT",
                "file_source": "TEXT",
            }
            for col, col_type in new_cols.items():
                if col not in existing_cols:
                    cursor.execute(f"ALTER TABLE transactions ADD COLUMN {col} {col_type};")

            # Enrichments table (linked to SITG cadastre)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS enrichments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_id INTEGER UNIQUE NOT NULL,
                    egrid TEXT,
                    commune_official TEXT,
                    parcel_no_official TEXT,
                    surface_official_m2 REAL,
                    plan_rf TEXT,
                    price_per_m2 REAL,
                    lien_extrait_rf TEXT,
                    extrait_rdppf_url TEXT,
                    centroid_lv95_e REAL,
                    centroid_lv95_n REAL,
                    centroid_wgs84_lon REAL,
                    centroid_wgs84_lat REAL,
                    geom_geojson_lv95 TEXT,
                    geom_geojson_wgs84 TEXT,
                    match_status TEXT,
                    enriched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE
                );
            """)

            # Automated migration for enrichments table
            cursor.execute("PRAGMA table_info(enrichments);")
            existing_enrich_cols = {row["name"] for row in cursor.fetchall()}
            new_enrich_cols = {
                "zone_code": "TEXT",
                "zone_name": "TEXT",
                "building_destination": "TEXT",
                "building_period": "TEXT",
                "building_year": "INTEGER",
                "building_floors": "INTEGER",
            }
            for col, col_type in new_enrich_cols.items():
                if col not in existing_enrich_cols:
                    cursor.execute(f"ALTER TABLE enrichments ADD COLUMN {col} {col_type};")

            # Useful indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_trans_commune ON transactions(commune);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_trans_parcel ON transactions(parcel_number);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_trans_cat ON transactions(source_category);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_enrich_egrid ON enrichments(egrid);")
            conn.commit()

    def upsert_publication(
        self,
        issue_id: str,
        issue_date: Optional[str] = None,
        issue_no: Optional[str] = None,
        title: Optional[str] = None,
        url: Optional[str] = None,
        file_path: Optional[str] = None,
        sha256: Optional[str] = None,
        status: str = "pending",
    ) -> int:
        """Insert or update publication record."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO publications (issue_id, issue_date, issue_no, title, url, file_path, sha256, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(issue_id) DO UPDATE SET
                    issue_date=coalesce(excluded.issue_date, publications.issue_date),
                    issue_no=coalesce(excluded.issue_no, publications.issue_no),
                    title=coalesce(excluded.title, publications.title),
                    url=coalesce(excluded.url, publications.url),
                    file_path=coalesce(excluded.file_path, publications.file_path),
                    sha256=coalesce(excluded.sha256, publications.sha256),
                    status=excluded.status
                RETURNING id;
                """,
                (issue_id, issue_date, issue_no, title, url, file_path, sha256, status),
            )
            pub_id = cursor.fetchone()[0]
            conn.commit()
            return pub_id

    def insert_transaction(
        self,
        transaction_hash: str,
        commune: str,
        parcel_number: Optional[str] = None,
        source_category: str = "Registre_Foncier",
        publication_id: Optional[int] = None,
        notice_date: Optional[str] = None,
        commune_section: Optional[str] = None,
        transaction_type: Optional[str] = "Vente",
        property_type: Optional[str] = None,
        nature: Optional[str] = None,
        address: Optional[str] = None,
        rooms: Optional[float] = None,
        floor: Optional[str] = None,
        unit_number: Optional[str] = None,
        case_number: Optional[str] = None,
        surface_m2: Optional[float] = None,
        seller: Optional[str] = None,
        buyer: Optional[str] = None,
        price_raw: Optional[str] = None,
        price_chf: Optional[float] = None,
        file_source: Optional[str] = None,
        raw_text: Optional[str] = None,
    ) -> Optional[int]:
        """Insert a parsed transaction, ignoring duplicates by transaction_hash."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR IGNORE INTO transactions (
                    publication_id, transaction_hash, source_category, notice_date, commune,
                    commune_section, parcel_number, transaction_type, property_type, nature,
                    address, rooms, floor, unit_number, case_number, surface_m2,
                    seller, buyer, price_raw, price_chf, file_source, raw_text
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                RETURNING id;
                """,
                (
                    publication_id,
                    transaction_hash,
                    source_category,
                    notice_date,
                    commune,
                    commune_section,
                    parcel_number,
                    transaction_type,
                    property_type,
                    nature,
                    address,
                    rooms,
                    floor,
                    unit_number,
                    case_number,
                    surface_m2,
                    seller,
                    buyer,
                    price_raw,
                    price_chf,
                    file_source,
                    raw_text,
                ),
            )
            row = cursor.fetchone()
            conn.commit()
            return row[0] if row else None

    def insert_transaction_record(self, record: Any, publication_id: Optional[int] = None) -> Optional[int]:
        """Insert a TransactionRecord Pydantic model directly into SQLite."""
        return self.insert_transaction(
            transaction_hash=record.transaction_hash,
            commune=record.commune,
            parcel_number=record.parcel_number,
            source_category=record.source_category,
            publication_id=publication_id,
            notice_date=record.notice_date,
            commune_section=record.commune_section,
            transaction_type=record.transaction_type,
            property_type=record.property_type,
            nature=record.nature,
            address=record.address,
            rooms=record.rooms,
            floor=record.floor,
            unit_number=record.unit_number,
            case_number=record.case_number,
            surface_m2=record.surface_m2,
            seller=record.seller,
            buyer=record.buyer,
            price_raw=record.price_raw,
            price_chf=record.price_chf,
            file_source=record.file_source,
            raw_text=record.raw_text,
        )

    def upsert_enrichment(
        self,
        transaction_id: int,
        match_status: str,
        egrid: Optional[str] = None,
        commune_official: Optional[str] = None,
        parcel_no_official: Optional[str] = None,
        surface_official_m2: Optional[float] = None,
        plan_rf: Optional[str] = None,
        price_per_m2: Optional[float] = None,
        lien_extrait_rf: Optional[str] = None,
        extrait_rdppf_url: Optional[str] = None,
        centroid_lv95: Optional[tuple] = None,
        centroid_wgs84: Optional[tuple] = None,
        geom_lv95: Optional[Dict[str, Any]] = None,
        geom_wgs84: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Insert or update SITG enrichment for a transaction."""
        c_e = centroid_lv95[0] if centroid_lv95 else None
        c_n = centroid_lv95[1] if centroid_lv95 else None
        c_lon = centroid_wgs84[0] if centroid_wgs84 else None
        c_lat = centroid_wgs84[1] if centroid_wgs84 else None
        g_lv95_json = json.dumps(geom_lv95) if geom_lv95 else None
        g_wgs84_json = json.dumps(geom_wgs84) if geom_wgs84 else None

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO enrichments (
                    transaction_id, egrid, commune_official, parcel_no_official,
                    surface_official_m2, plan_rf, price_per_m2, lien_extrait_rf,
                    extrait_rdppf_url, centroid_lv95_e, centroid_lv95_n,
                    centroid_wgs84_lon, centroid_wgs84_lat, geom_geojson_lv95,
                    geom_geojson_wgs84, match_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(transaction_id) DO UPDATE SET
                    egrid=excluded.egrid,
                    commune_official=excluded.commune_official,
                    parcel_no_official=excluded.parcel_no_official,
                    surface_official_m2=excluded.surface_official_m2,
                    plan_rf=excluded.plan_rf,
                    price_per_m2=excluded.price_per_m2,
                    lien_extrait_rf=excluded.lien_extrait_rf,
                    extrait_rdppf_url=excluded.extrait_rdppf_url,
                    centroid_lv95_e=excluded.centroid_lv95_e,
                    centroid_lv95_n=excluded.centroid_lv95_n,
                    centroid_wgs84_lon=excluded.centroid_wgs84_lon,
                    centroid_wgs84_lat=excluded.centroid_wgs84_lat,
                    geom_geojson_lv95=excluded.geom_geojson_lv95,
                    geom_geojson_wgs84=excluded.geom_geojson_wgs84,
                    match_status=excluded.match_status,
                    enriched_at=CURRENT_TIMESTAMP
                RETURNING id;
                """,
                (
                    transaction_id,
                    egrid,
                    commune_official,
                    parcel_no_official,
                    surface_official_m2,
                    plan_rf,
                    price_per_m2,
                    lien_extrait_rf,
                    extrait_rdppf_url,
                    c_e,
                    c_n,
                    c_lon,
                    c_lat,
                    g_lv95_json,
                    g_wgs84_json,
                    match_status,
                ),
            )
            row = cursor.fetchone()
            conn.commit()
            return row[0]

    def get_all_transactions(self, enriched_only: bool = False) -> List[Dict[str, Any]]:
        """Retrieve transactions optionally joined with enrichments."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT 
                    t.id as transaction_id,
                    t.transaction_hash,
                    t.notice_date,
                    t.commune,
                    t.commune_section,
                    t.parcel_number,
                    t.nature,
                    t.surface_m2,
                    t.seller,
                    t.buyer,
                    t.price_raw,
                    t.price_chf,
                    t.raw_text,
                    e.egrid,
                    e.commune_official,
                    e.parcel_no_official,
                    e.surface_official_m2,
                    e.plan_rf,
                    e.price_per_m2,
                    e.lien_extrait_rf,
                    e.extrait_rdppf_url,
                    e.centroid_wgs84_lon,
                    e.centroid_wgs84_lat,
                    e.geom_geojson_wgs84,
                    e.geom_geojson_lv95,
                    e.match_status
                FROM transactions t
                LEFT JOIN enrichments e ON t.id = e.transaction_id
            """
            if enriched_only:
                query += " WHERE e.id IS NOT NULL"
            query += " ORDER BY t.id DESC;"
            cursor.execute(query)
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_unenriched_transactions(self) -> List[Dict[str, Any]]:
        """Retrieve transactions that have not yet been enriched by SITG."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.* FROM transactions t
                LEFT JOIN enrichments e ON t.id = e.transaction_id
                WHERE e.id IS NULL
                ORDER BY t.id ASC;
            """)
            return [dict(r) for r in cursor.fetchall()]
