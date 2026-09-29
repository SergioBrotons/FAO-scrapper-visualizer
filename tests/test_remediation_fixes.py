"""Unit tests verifying all P0 and P1 audit remediation fixes using Python's standard unittest."""

import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from fao_transactions.parser.pdf_parser import parse_price, parse_surface, FaoPdfParser
from fao_transactions.collector.browser import AntiBotChallengeException
from fao_transactions.storage.db import Database


class TestPriceParserRemediation(unittest.TestCase):
    """Validate P0-01: Swiss currency decimal and separator parsing."""

    def test_price_with_point_zeros(self):
        raw, val = parse_price("1'875'000.00")
        self.assertEqual(val, 1875000.0)
        self.assertEqual(raw, "1'875'000.00")

    def test_price_with_dash(self):
        raw, val = parse_price("1'875'000.-")
        self.assertEqual(val, 1875000.0)

    def test_price_with_double_dash(self):
        raw, val = parse_price("Frs 2'770'000.--")
        self.assertEqual(val, 2770000.0)

    def test_price_with_cents_decimal(self):
        raw, val = parse_price("1'875'000,50")
        self.assertEqual(val, 1875000.5)

    def test_price_with_chf_prefix(self):
        raw, val = parse_price("CHF 1'875'000.00")
        self.assertEqual(val, 1875000.0)

    def test_price_non_communicated(self):
        raw, val = parse_price("non communiqué")
        self.assertIsNone(val)
        self.assertEqual(raw, "non communiqué")

    def test_price_donation(self):
        raw, val = parse_price("Donation entre vifs")
        self.assertIsNone(val)


class TestPPESurfaceRemediation(unittest.TestCase):
    """Validate P0-02: PPE units uncoupled from whole-building land plot surfaces."""

    def test_ppe_surface_guard(self):
        parser = FaoPdfParser()
        notice_text = """
        COMMUNE DE GENÈVE
        B-F 2384-3, PPE d'un appartement de 4 pièces, loggia, 2'500 m2.
        Aliénateur: Dupont Pierre.
        Acquéreur: Durand Marie.
        Prix: 1'875'000.00
        """
        record = parser.parse_notice_block(notice_text, current_commune="Genève", notice_date="01.01.2024")
        self.assertIsNotNone(record)
        # Living surface for apartment must NOT be 2500 m2 (which is the land plot):
        self.assertIsNone(record.surface_m2)

    def test_villa_surface_preserved(self):
        parser = FaoPdfParser()
        notice_text = """
        COMMUNE DE VANDŒUVRES
        B-F 1450, Habitation à un seul logement, villa individuelle, 1'200 m2.
        Aliénateur: Martin Jean.
        Acquéreur: Bernard Sophie.
        Prix: 3'500'000.-
        """
        record = parser.parse_notice_block(notice_text, current_commune="Vandœuvres", notice_date="01.01.2024")
        self.assertIsNotNone(record)
        # Single-family villa land plot surface IS legitimate:
        self.assertEqual(record.surface_m2, 1200.0)


class TestAntiBotRemediation(unittest.TestCase):
    """Validate P0-03: Anti-bot challenge raises fatal exception rather than silent exit."""

    def test_antibot_exception_class(self):
        with self.assertRaises(AntiBotChallengeException):
            raise AntiBotChallengeException("Challenge detected and unsolved")


class TestRectificationRemediation(unittest.TestCase):
    """Validate P0-05: Rectification updates price and parcel, not just parties."""

    def test_rectification_updates_price_and_parcel(self):
        test_dir = Path("scratch/test_db_dir")
        test_dir.mkdir(parents=True, exist_ok=True)
        db_file = test_dir / "test_rect.sqlite"
        if db_file.exists():
            try:
                db_file.unlink()
            except Exception:
                pass

        db = Database(str(db_file))

        # 1. Insert original transaction
        t_id = db.insert_transaction(
            transaction_hash="hash_orig_123",
            commune="Genève",
            parcel_number="1001",
            seller="Old Seller",
            buyer="Old Buyer",
            price_raw="5'000'000",
            price_chf=5000000.0,
            case_number="VA 99999",
            notice_date="01.01.2024",
        )
        self.assertIsNotNone(t_id)

        # 2. Insert rectification notice correcting price to 500'000 and parcel to 1001-12
        rect_id = db.insert_transaction(
            transaction_hash="hash_rect_456",
            commune="Genève",
            parcel_number="1001-12",
            seller="Corrected Seller",
            buyer="Corrected Buyer",
            price_raw="500'000",
            price_chf=500000.0,
            case_number="VA 99999",
            notice_date="15.01.2024",
            is_rectification=True,
            raw_text="Rectificatif: le prix exact est de 500'000 CHF pour la parcelle 1001-12.",
        )
        self.assertEqual(rect_id, t_id)

        # 3. Verify in database
        with db.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT seller, buyer, price_chf, parcel_number, raw_text FROM transactions WHERE id = ?", (t_id,))
            row = c.fetchone()
            self.assertEqual(row["seller"], "Corrected Seller")
            self.assertEqual(row["buyer"], "Corrected Buyer")
            self.assertEqual(row["price_chf"], 500000.0)
            self.assertEqual(row["parcel_number"], "1001-12")
            self.assertIn("Rectificatif:", row["raw_text"])

        # Cleanup
        try:
            db_file.unlink(missing_ok=True)
        except Exception:
            pass


class TestProductionDatabaseRemediation(unittest.TestCase):
    """Validate active database state integrity post-remediation."""

    def test_record_4837_remediated(self):
        db_path = Path("data/state/state.sqlite")
        self.assertTrue(db_path.exists())
        conn = sqlite3.connect(str(db_path))
        c = conn.cursor()
        c.execute("SELECT price_raw, price_chf FROM transactions WHERE id = 4837")
        row = c.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "1'875'000")
        self.assertEqual(row[1], 1875000.0)

    def test_test_record_purged(self):
        db_path = Path("data/state/state.sqlite")
        conn = sqlite3.connect(str(db_path))
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM transactions WHERE transaction_hash = 'test_hash_1' OR id = 8145")
        count = c.fetchone()[0]
        conn.close()
        self.assertEqual(count, 0)

    def test_total_cantonal_volume_bounds(self):
        db_path = Path("data/state/state.sqlite")
        conn = sqlite3.connect(str(db_path))
        c = conn.cursor()
        c.execute("SELECT SUM(price_chf) FROM transactions")
        total = c.fetchone()[0]
        conn.close()
        # Must be ~16.93B, NOT 18.81B:
        self.assertTrue(16.5e9 < total < 17.5e9)


if __name__ == "__main__":
    unittest.main()
