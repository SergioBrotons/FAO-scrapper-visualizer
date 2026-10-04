"""OCSTAT and Financial Benchmarks ingestion and enrichment pipeline."""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import sqlite3

from fao_transactions.config import settings
from fao_transactions.storage.db import Database


class OcstatFinancialIngester:
    """Loads official OCSTAT communal data and computes financial underwriting metrics."""

    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()
        self.root_dir = Path(__file__).resolve().parent.parent.parent.parent
        self.ocstat_file = self.root_dir / "data" / "reference" / "ocstat_communes_2025_2026.json"
        self.financial_rules_file = self.root_dir / "data" / "reference" / "financial_rules.json"

    def ingest_all(self) -> Dict[str, Any]:
        """Ingests reference benchmarks and enriches all transactions in state.sqlite."""
        self._load_ocstat_benchmarks()
        self._load_financial_benchmarks()
        summary = self._compute_financial_intelligence()
        return summary

    def _load_ocstat_benchmarks(self) -> None:
        if not self.ocstat_file.exists():
            return
        with open(self.ocstat_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            for row in data:
                cursor.execute("""
                    INSERT INTO ocstat_communal_benchmarks (
                        commune_code, commune, canton, rive, annee,
                        prix_median_m2_ppe, prix_moyen_m2_ppe,
                        prix_median_m2_maison, prix_moyen_m2_maison,
                        taux_vacance_officiel_pct, tendance_annuelle_pct,
                        volume_total_chf, nb_transactions_annuel, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(commune_code) DO UPDATE SET
                        commune=excluded.commune,
                        prix_median_m2_ppe=excluded.prix_median_m2_ppe,
                        prix_moyen_m2_ppe=excluded.prix_moyen_m2_ppe,
                        prix_median_m2_maison=excluded.prix_median_m2_maison,
                        prix_moyen_m2_maison=excluded.prix_moyen_m2_maison,
                        taux_vacance_officiel_pct=excluded.taux_vacance_officiel_pct,
                        tendance_annuelle_pct=excluded.tendance_annuelle_pct,
                        volume_total_chf=excluded.volume_total_chf,
                        nb_transactions_annuel=excluded.nb_transactions_annuel,
                        updated_at=CURRENT_TIMESTAMP;
                """, (
                    row["commune_code"], row["commune"], row.get("canton", "GE"),
                    row.get("rive", "Gauche"), row.get("annee", 2025),
                    row.get("prix_median_m2_ppe"), row.get("prix_moyen_m2_ppe"),
                    row.get("prix_median_m2_maison"), row.get("prix_moyen_m2_maison"),
                    row.get("taux_vacance_officiel_pct"), row.get("tendance_annuelle_pct"),
                    row.get("volume_total_chf"), row.get("nb_transactions_annuel")
                ))
            conn.commit()

    def _load_financial_benchmarks(self) -> None:
        if not self.financial_rules_file.exists():
            return
        with open(self.financial_rules_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        schedules = data.get("casatax", {}).get("annual_schedules", {})
        finma = data.get("mortgage_affordability_finma", {})
        tenue = finma.get("tenue_de_charge", {})
        equity = finma.get("equity_requirements", {})

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            for year_str, sched in schedules.items():
                cursor.execute("""
                    INSERT INTO financial_benchmarks (
                        year, casatax_threshold_chf, casatax_rebate_mutation_chf,
                        casatax_cedule_rebate_pct, taux_technique_finma_pct,
                        charges_entretien_pct, amortissement_annuel_pct,
                        fonds_propres_min_pct, fonds_propres_hard_cash_min_pct,
                        ratio_tenue_charge_max_pct, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(year) DO UPDATE SET
                        casatax_threshold_chf=excluded.casatax_threshold_chf,
                        casatax_rebate_mutation_chf=excluded.casatax_rebate_mutation_chf,
                        updated_at=CURRENT_TIMESTAMP;
                """, (
                    int(year_str), sched["ceiling_price_chf"], sched["max_rebate_mutation_chf"],
                    sched.get("cedule_rebate_pct", 0.50),
                    tenue.get("theoretical_interest_rate_pct", 0.05),
                    tenue.get("maintenance_charges_pct", 0.01),
                    tenue.get("mandatory_amortization_annual_pct", 0.01),
                    equity.get("min_equity_pct", 0.20),
                    equity.get("min_hard_cash_pct", 0.10),
                    tenue.get("max_debt_to_income_ratio_pct", 0.3333)
                ))
            conn.commit()

    def _compute_financial_intelligence(self) -> Dict[str, Any]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            # Fetch commune benchmarks map
            cursor.execute("SELECT * FROM ocstat_communal_benchmarks")
            communes = {r["commune"].lower().strip(): dict(r) for r in cursor.fetchall()}

            # Latest financial benchmark
            cursor.execute("SELECT * FROM financial_benchmarks ORDER BY year DESC LIMIT 1")
            rules = dict(cursor.fetchone())

            cursor.execute("""
                SELECT 
                    t.id, t.commune, t.notice_date, t.property_type, t.nature,
                    t.surface_m2, t.price_chf, t.seller, t.buyer, t.raw_text,
                    e.surface_official_m2, e.price_per_m2
                FROM transactions t
                LEFT JOIN enrichments e ON t.id = e.transaction_id
                WHERE t.price_chf IS NOT NULL AND t.price_chf > 0
            """)
            transactions = cursor.fetchall()

            for t in transactions:
                raw_text = (t["raw_text"] or "").lower()
                seller = (t["seller"] or "").lower()
                is_hoirie = 1 if ("hoirie" in raw_text or "hoirie" in seller or "succession" in raw_text) else 0

                c_key = (t["commune"] or "").lower().strip()
                ocstat = communes.get(c_key, communes.get("genève", {}))

                price_chf = t["price_chf"]
                surface = t["surface_official_m2"] or t["surface_m2"] or 0
                real_m2 = (t["price_per_m2"] or (price_chf / surface)) if surface > 0 else None

                is_ppe = ("ppe" in (t["property_type"] or "").lower()) or ("ppe" in (t["nature"] or "").lower())
                ocstat_median_m2 = ocstat.get("prix_median_m2_ppe" if is_ppe else "prix_median_m2_maison", 13800.0)

                price_vs_ratio = None
                price_vs_pct = None
                if real_m2 and ocstat_median_m2 and real_m2 > 500:
                    price_vs_ratio = round(real_m2 / ocstat_median_m2, 3)
                    price_vs_pct = round(((real_m2 - ocstat_median_m2) / ocstat_median_m2) * 100, 1)

                is_casatax = 1 if (price_chf <= rules["casatax_threshold_chf"]) else 0
                is_cliff = 1 if (not is_casatax and price_chf <= (rules["casatax_threshold_chf"] * 1.05)) else 0

                casatax_savings = 0
                if is_casatax:
                    rebate = min(price_chf * 0.03, rules["casatax_rebate_mutation_chf"])
                    cedule_rebate = min(price_chf * 0.80 * 0.0136 * 0.50, 3000.0)
                    casatax_savings = round(rebate + cedule_rebate)

                min_equity = round(price_chf * rules["fonds_propres_min_pct"])
                hard_cash = round(price_chf * rules["fonds_propres_hard_cash_min_pct"])
                loan_amt = round(price_chf * (1 - rules["fonds_propres_min_pct"]))
                annual_rate = rules["taux_technique_finma_pct"] + rules["charges_entretien_pct"] + rules["amortissement_annuel_pct"]
                annual_charge = round(loan_amt * annual_rate)
                min_income = round(annual_charge / rules["ratio_tenue_charge_max_pct"])

                deal_signal = "PRIX_MARCHE"
                if is_hoirie:
                    deal_signal = "HOIRIE_SOURCING"
                elif is_cliff:
                    deal_signal = "CASATAX_CLIFF"
                elif price_vs_pct is not None and price_vs_pct <= -15:
                    deal_signal = "OPPORTUNITE_DECOTEE"
                elif price_vs_pct is not None and price_vs_pct >= 25:
                    deal_signal = "SURCOTE_PREMIUM"

                cursor.execute("""
                    INSERT INTO financial_intelligence (
                        transaction_id, commune, notice_date, price_chf, surface_m2,
                        price_per_m2_real, ocstat_median_m2, price_vs_ocstat_ratio,
                        price_vs_ocstat_pct, is_casatax_eligible, casatax_savings_chf,
                        casatax_cliff_flag, equity_min_required_chf, equity_hard_cash_min_chf,
                        loan_amount_chf, theoretical_annual_charge_chf, min_gross_annual_income_chf,
                        deal_type_signal, is_hoirie, computed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(transaction_id) DO UPDATE SET
                        price_chf=excluded.price_chf,
                        price_per_m2_real=excluded.price_per_m2_real,
                        ocstat_median_m2=excluded.ocstat_median_m2,
                        price_vs_ocstat_ratio=excluded.price_vs_ocstat_ratio,
                        price_vs_ocstat_pct=excluded.price_vs_ocstat_pct,
                        is_casatax_eligible=excluded.is_casatax_eligible,
                        casatax_savings_chf=excluded.casatax_savings_chf,
                        casatax_cliff_flag=excluded.casatax_cliff_flag,
                        equity_min_required_chf=excluded.equity_min_required_chf,
                        equity_hard_cash_min_chf=excluded.equity_hard_cash_min_chf,
                        loan_amount_chf=excluded.loan_amount_chf,
                        theoretical_annual_charge_chf=excluded.theoretical_annual_charge_chf,
                        min_gross_annual_income_chf=excluded.min_gross_annual_income_chf,
                        deal_type_signal=excluded.deal_type_signal,
                        is_hoirie=excluded.is_hoirie,
                        computed_at=CURRENT_TIMESTAMP;
                """, (
                    t["id"], t["commune"], t["notice_date"], price_chf, surface,
                    round(real_m2) if real_m2 else None, ocstat_median_m2,
                    price_vs_ratio, price_vs_pct, is_casatax, casatax_savings,
                    is_cliff, min_equity, hard_cash, loan_amt, annual_charge,
                    min_income, deal_signal, is_hoirie
                ))
            conn.commit()

        return self.db.get_intelligence_summary()
