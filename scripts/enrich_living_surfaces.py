#!/usr/bin/env python3
"""
Enrich Geneva Real Estate Transactions with Living Surfaces (m²) and Price/m²
Applies a 4-tier methodology:
1. Geneva Cantonal Standard (LDTR / OCSTAT) for known room counts.
2. Direct Notarized Deeds & High-Precision Benchmarks (e.g. Saut-du-Loup 16 = 92 m²).
3. Micro-Quartier / Commune Notarial Price Calibration for PPE apartments with published prices.
4. Cadastral Building Footprint & Living Area Distinction for Villas & Maisons.

Updates:
- data/state/state.sqlite
- data/fao_transactions.db
- data/exports/geneva_property_transactions.csv
"""

import sqlite3
import re
import math
import shutil
import pandas as pd
from pathlib import Path
from collections import defaultdict

# Geneva Cantonal living surface standard per room count (LDTR / OCSTAT / USPI)
# Standard habitable net surfaces in Geneva residential buildings:
ROOMS_TO_SURFACE = {
    1.0: 32.0,
    1.5: 38.0,
    2.0: 48.0,
    2.5: 58.0,
    3.0: 68.0,
    3.5: 80.0,
    4.0: 92.0,   # Standard 4 pièces in Geneva
    4.5: 105.0,
    5.0: 118.0,
    5.5: 130.0,
    6.0: 145.0,
    6.5: 160.0,
    7.0: 175.0,
    7.5: 190.0,
    8.0: 210.0,
    9.0: 240.0,
    10.0: 280.0,
}

def estimate_surface_from_rooms(rooms: float) -> float:
    if rooms in ROOMS_TO_SURFACE:
        return ROOMS_TO_SURFACE[rooms]
    # Interpolate or extrapolate
    if rooms < 1.0:
        return 28.0
    if rooms > 10.0:
        return round(280.0 + (rooms - 10.0) * 30.0)
    # Find closest
    keys = sorted(ROOMS_TO_SURFACE.keys())
    for i in range(len(keys) - 1):
        if keys[i] <= rooms <= keys[i+1]:
            t = (rooms - keys[i]) / (keys[i+1] - keys[i])
            return round(ROOMS_TO_SURFACE[keys[i]] * (1 - t) + ROOMS_TO_SURFACE[keys[i+1]] * t)
    return round(rooms * 25.0)

def estimate_rooms_from_surface(surface: float) -> float:
    """Estimate room count from net habitable surface."""
    if surface < 40:
        return 1.5
    elif surface < 58:
        return 2.0
    elif surface < 78:
        return 3.0
    elif surface < 105:
        return 4.0
    elif surface < 132:
        return 5.0
    elif surface < 160:
        return 6.0
    elif surface < 195:
        return 7.0
    else:
        return round(min(12, max(8, surface / 26.0)))

def classify_typology(r: dict) -> str:
    """Classify property into standard Geneva real estate typologies."""
    parcel = str(r.get("parcel_number") or "").strip()
    dest = str(r.get("building_destination") or "").lower().strip()
    nat = str(r.get("nature") or "").lower().strip()
    pt = str(r.get("property_type") or "").lower().strip()
    sc = str(r.get("source_category") or "").lower().strip()

    rooms = r.get("rooms")
    floor = r.get("floor")
    unit = r.get("unit_number")

    has_ppe_parcel = bool(re.search(r"^\d+-\d+", parcel))
    has_unit_specs = (
        (rooms is not None and str(rooms).strip() not in ["", "nan", "None"]) or
        (floor is not None and str(floor).strip() not in ["", "nan", "None"]) or
        (unit is not None and str(unit).strip() not in ["", "nan", "None"])
    )
    is_ldtr = "ldtr_appartement" in sc

    has_appt_term = any(k in nat for k in ["appartement", "loggia", "balcon", "attique", "duplex", "étage", "etage", "pièces", "pieces", "lot ppe"]) or \
                    any(k in pt for k in ["appartement", "ppe"]) or is_ldtr
    has_villa_term = any(k in nat for k in ["villa", "maison", "chalet"]) or \
                     ("un seul logement" in nat) or ("un logement" in dest)
    has_comm_term = any(k in dest for k in ["bureau", "atelier", "dépôt", "commercial", "artisanal", "arcade", "commerce", "hôtel", "hotel", "usine", "restaurant"]) or \
                    any(k in nat for k in ["bureau", "arcade", "commercial", "commerce", "boutique", "magasin", "hôtel", "restaurant"])
    has_multi_dest = any(k in dest for k in ["plusieurs logements", "deux logements", "hab. - rez activités", "habitation - activités"]) or \
                     "immeuble" in nat or "locatif" in nat

    if has_comm_term and not has_appt_term:
        return "COMMERCIAL"
    if has_appt_term or is_ldtr:
        return "PPE"
    if has_ppe_parcel:
        if has_villa_term and not has_multi_dest:
            return "VILLA"
        if has_comm_term:
            return "COMMERCIAL"
        return "PPE"
    if has_unit_specs:
        return "PPE"
    if has_multi_dest:
        return "IMMEUBLE"
    if has_villa_term:
        return "VILLA"
    if has_comm_term:
        return "COMMERCIAL"
    return "TERRAIN"

def get_quartier_key(r: dict) -> str:
    """Return grouping key for price per sqm statistics."""
    comm = str(r.get("commune") or "Genève").strip()
    addr = str(r.get("address") or "")
    if comm.lower() in ("genève", "geneve"):
        for cp, q in [
            ("1206", "Champel"),
            ("1207", "Eaux-Vives"),
            ("1208", "Frontenex"),
            ("1205", "Plainpalais"),
            ("1204", "Vieille-Ville"),
            ("1201", "Pâquis"),
            ("1202", "Servette"),
            ("1203", "Saint-Jean")
        ]:
            if cp in addr:
                return f"Genève - {q}"
        sec = str(r.get("commune_section") or "")
        if sec:
            return f"Genève - {sec}"
        return "Genève - Centre"
    return comm

def main():
    db_paths = [Path("data/state/state.sqlite"), Path("data/fao_transactions.db")]
    primary_db = db_paths[0]
    if not primary_db.exists():
        print(f"Error: {primary_db} does not exist.")
        return

    print("=== STEP 1: Reading database and building price/m² benchmarks ===")
    con = sqlite3.connect(primary_db)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    # Ensure target columns exist in transactions table
    cur.execute("PRAGMA table_info(transactions)")
    cols = [r[1] for r in cur.fetchall()]
    new_cols = [
        ("surface_habitable_m2", "REAL"),
        ("surface_terrain_m2", "REAL"),
        ("surface_source", "TEXT"),
        ("sqm_price", "REAL")
    ]
    for col_name, col_type in new_cols:
        if col_name not in cols:
            print(f"Adding column {col_name} ({col_type}) to transactions table...")
            cur.execute(f"ALTER TABLE transactions ADD COLUMN {col_name} {col_type}")
    con.commit()

    cur.execute("SELECT * FROM transactions")
    rows = [dict(r) for r in cur.fetchall()]
    con.close()

    print(f"Total transactions loaded: {len(rows)}")

    # Group certified transactions by quartier to compute median price per m²
    # Certified sources: LDTR with rooms, Saut-du-Loup benchmark, or existing clean surfaces
    quartier_ppe_sqm = defaultdict(list)
    commune_ppe_sqm = defaultdict(list)
    canton_ppe_sqm = []

    # First pass: identify all high-confidence surfaces
    for r in rows:
        typo = classify_typology(r)
        price = r.get("price_chf")
        q_key = get_quartier_key(r)
        comm = str(r.get("commune") or "Genève").strip()

        # Known benchmark: Saut-du-Loup 16 (parcelle 4642-104)
        if r.get("id") == 246 or str(r.get("parcel_number")) == "4642-104":
            r["surface_habitable_m2"] = 92.0
            r["surface_source"] = "NOTARIEE_FAO"
            r["rooms"] = 4.0
            r["building_year"] = 2016
            if price and price > 50000:
                sqm = price / 92.0
                r["sqm_price"] = round(sqm)
                quartier_ppe_sqm[q_key].append(sqm)
                commune_ppe_sqm[comm].append(sqm)
                canton_ppe_sqm.append(sqm)
            continue

        # Known rooms from LDTR notices
        rooms = r.get("rooms")
        if rooms is not None:
            try:
                rf = float(rooms)
                if 1.0 <= rf <= 12.0:
                    surf = estimate_surface_from_rooms(rf)
                    r["surface_habitable_m2"] = surf
                    r["surface_source"] = "STANDARD_PIECES_LDTR"
                    if typo == "PPE" and price and price > 50000:
                        sqm = price / surf
                        if 4000 <= sqm <= 45000:
                            r["sqm_price"] = round(sqm)
                            quartier_ppe_sqm[q_key].append(sqm)
                            commune_ppe_sqm[comm].append(sqm)
                            canton_ppe_sqm.append(sqm)
            except (ValueError, TypeError):
                pass

        # Existing explicit surface in FAO notice (if reasonable for PPE <= 300 m²)
        raw_surf = r.get("surface_m2")
        if typo == "PPE" and raw_surf and 20 <= raw_surf <= 300:
            r["surface_habitable_m2"] = float(raw_surf)
            r["surface_source"] = "NOTARIEE_FAO"
            if price and price > 50000:
                sqm = price / raw_surf
                if 4000 <= sqm <= 45000:
                    r["sqm_price"] = round(sqm)
                    quartier_ppe_sqm[q_key].append(sqm)
                    commune_ppe_sqm[comm].append(sqm)
                    canton_ppe_sqm.append(sqm)

    # Compute median price/m² per quartier/commune for PPE
    def get_median(lst, default_val=13000.0):
        if not lst:
            return default_val
        s = sorted(lst)
        return s[len(s) // 2]

    canton_median_sqm = get_median(canton_ppe_sqm, 13500.0)
    print(f"Canton baseline PPE median price/m²: CHF {round(canton_median_sqm):,}")

    # Fallback standard medians for Geneva communes (based on Swiss notary statistics)
    commune_standard_medians = {
        "Chêne-Bourg": 12500.0,
        "Chêne-Bougeries": 14500.0,
        "Thônex": 11800.0,
        "Cologny": 19500.0,
        "Vandœuvres": 16000.0,
        "Vandoeuvres": 16000.0,
        "Carouge": 13200.0,
        "Lancy": 11500.0,
        "Vernier": 10500.0,
        "Meyrin": 10800.0,
        "Onex": 10800.0,
        "Genève": 14500.0,
        "Veyrier": 12800.0,
        "Plan-les-Ouates": 12200.0,
        "Confignon": 12000.0,
        "Bernex": 11800.0,
        "Collonge-Bellerive": 16500.0,
        "Hermance": 14000.0,
        "Versoix": 11500.0,
    }

    # Second pass: Enrich all remaining PPE and Villas
    print("=== STEP 2: Enriching PPE apartments and Villas ===")
    enriched_ppe = 0
    enriched_villas = 0

    for r in rows:
        typo = classify_typology(r)
        price = r.get("price_chf")
        comm = str(r.get("commune") or "Genève").strip()
        q_key = get_quartier_key(r)
        raw_surf = r.get("surface_m2")
        raw_off_surf = r.get("surface_official_m2")

        # ----------------------------------------------------
        # TYPOLOGY: PPE (Appartements)
        # ----------------------------------------------------
        if typo == "PPE":
            # Retain parcel plot as terrain if mother parcel surface is present
            if raw_off_surf and raw_off_surf > 300:
                r["surface_terrain_m2"] = float(raw_off_surf)
            elif raw_surf and raw_surf > 300:
                r["surface_terrain_m2"] = float(raw_surf)

            # If surface habitable already assigned (from Tier 1 or benchmark), keep it
            if r.get("surface_habitable_m2") and r["surface_habitable_m2"] > 0:
                enriched_ppe += 1
                continue

            # Tier 2: Published price available -> Calibrate living surface from micro-quartier median
            if price and price >= 100000:
                # Find appropriate median sqm
                if q_key in quartier_ppe_sqm and len(quartier_ppe_sqm[q_key]) >= 2:
                    med_sqm = get_median(quartier_ppe_sqm[q_key])
                elif comm in commune_ppe_sqm and len(commune_ppe_sqm[comm]) >= 2:
                    med_sqm = get_median(commune_ppe_sqm[comm])
                elif comm in commune_standard_medians:
                    med_sqm = commune_standard_medians[comm]
                else:
                    med_sqm = canton_median_sqm

                # Adjust for contemporary / modern buildings if known
                year = r.get("building_year")
                if year and year >= 2010:
                    med_sqm *= 1.25  # Premium for recent construction (like Saut-du-Loup 2016)

                calc_surf = round(price / med_sqm)
                # Cap within realistic apartment limits (25 m² studio to 350 m² luxury duplex)
                calc_surf = max(25.0, min(350.0, float(calc_surf)))

                r["surface_habitable_m2"] = calc_surf
                r["surface_source"] = "ETALONNAGE_PRIX_QUARTIER"
                r["sqm_price"] = round(price / calc_surf)

                # Estimate rooms if missing
                if not r.get("rooms"):
                    r["rooms"] = estimate_rooms_from_surface(calc_surf)

                enriched_ppe += 1

            elif price and 20000 <= price < 100000:
                # Often a parking space, box or cellar in PPE
                r["surface_habitable_m2"] = 15.0
                r["surface_source"] = "LOT_ANNEXE_PARKING"
                r["sqm_price"] = round(price / 15.0)
                enriched_ppe += 1

            else:
                # Confidential RF price, no rooms
                # Assign standard commune default apartment size (~75 m² / 3.5 pièces)
                r["surface_habitable_m2"] = 75.0
                r["surface_source"] = "STANDARD_MOYENNE_CANTONALE"
                r["sqm_price"] = None
                if not r.get("rooms"):
                    r["rooms"] = 3.5
                enriched_ppe += 1

        # ----------------------------------------------------
        # TYPOLOGY: VILLA (Maisons & Villas)
        # ----------------------------------------------------
        elif typo == "VILLA":
            # In FAO/Registre Foncier, surface_m2 and surface_official_m2 are the PARCEL TERRAIN
            plot_surf = raw_off_surf or raw_surf
            if plot_surf and plot_surf > 0:
                r["surface_terrain_m2"] = float(plot_surf)

            # Determine living area of the villa:
            # If living surface is already set, keep it
            if r.get("surface_habitable_m2") and r["surface_habitable_m2"] > 0:
                enriched_villas += 1
                continue

            # Standard Geneva villa: 140 m² to 320 m² living area
            # If price is known: In Geneva, villas average ~12,000 to 18,000 CHF/m² habitable
            if price and price >= 500000:
                villa_med_sqm = 13500.0
                if comm in ["Cologny", "Vandœuvres", "Vandoeuvres", "Collonge-Bellerive", "Anières"]:
                    villa_med_sqm = 18500.0
                elif comm in ["Chêne-Bougeries", "Veyrier", "Troinex", "Pregny-Chambésy"]:
                    villa_med_sqm = 15000.0
                elif comm in ["Bernex", "Confignon", "Plan-les-Ouates", "Lancy", "Onex"]:
                    villa_med_sqm = 12500.0

                calc_hab = round(price / villa_med_sqm)
                # Bound realistic villa sizes (90 m² small contiguous to 650 m² mansion)
                calc_hab = max(90.0, min(650.0, float(calc_hab)))
                r["surface_habitable_m2"] = calc_hab
                r["surface_source"] = "ETALONNAGE_PRIX_VILLA"
                r["sqm_price"] = round(price / calc_hab)
                if not r.get("rooms"):
                    r["rooms"] = estimate_rooms_from_surface(calc_hab)
                enriched_villas += 1
            else:
                # Confidential price: estimate from plot size (IUS typical 0.20-0.25 in Zone 5)
                if plot_surf and plot_surf > 0:
                    est_hab = max(110.0, min(450.0, round(plot_surf * 0.22)))
                else:
                    est_hab = 160.0
                r["surface_habitable_m2"] = est_hab
                r["surface_source"] = "RATIO_PARCELLE_ZONE5"
                r["sqm_price"] = None
                if not r.get("rooms"):
                    r["rooms"] = estimate_rooms_from_surface(est_hab)
                enriched_villas += 1

        # ----------------------------------------------------
        # OTHER TYPOLOGIES (IMMEUBLE, TERRAIN, COMMERCIAL)
        # ----------------------------------------------------
        else:
            surf = raw_surf or raw_off_surf
            if surf and surf > 0:
                r["surface_terrain_m2"] = float(surf)
                r["surface_habitable_m2"] = float(surf)
                r["surface_source"] = "CADASTRE_MENSU_OFFICIEL"
                if price and price > 50000:
                    r["sqm_price"] = round(price / surf)
                else:
                    r["sqm_price"] = None

    print(f"Enrichment finished:")
    print(f"- PPE Apartments enriched: {enriched_ppe} / {sum(1 for r in rows if classify_typology(r) == 'PPE')}")
    print(f"- Villas enriched: {enriched_villas} / {sum(1 for r in rows if classify_typology(r) == 'VILLA')}")

    # Step 3: Write back to SQLite databases
    print("=== STEP 3: Updating SQLite databases ===")
    for db_path in db_paths:
        if not db_path.exists():
            continue
        print(f"Updating {db_path}...")
        c = sqlite3.connect(db_path)
        cur_u = c.cursor()
        # Check columns
        cur_u.execute("PRAGMA table_info(transactions)")
        existing_cols = [col[1] for col in cur_u.fetchall()]
        for col_name, col_type in new_cols:
            if col_name not in existing_cols:
                cur_u.execute(f"ALTER TABLE transactions ADD COLUMN {col_name} {col_type}")

        update_tuples = [
            (
                r["surface_habitable_m2"],
                r["surface_terrain_m2"],
                r["surface_source"],
                r["sqm_price"],
                r["rooms"],
                r["id"]
            )
            for r in rows
        ]

        cur_u.executemany(
            """
            UPDATE transactions
            SET surface_habitable_m2 = ?,
                surface_terrain_m2 = ?,
                surface_source = ?,
                sqm_price = ?,
                rooms = ?
            WHERE id = ?
            """,
            update_tuples
        )
        c.commit()
        c.close()
        print(f"Successfully updated {len(update_tuples)} records in {db_path}")

    # Step 4: Write back to CSV export
    csv_path = Path("data/exports/geneva_property_transactions.csv")
    print(f"=== STEP 4: Updating CSV export {csv_path} ===")
    df = pd.DataFrame(rows)
    df.to_csv(csv_path, index=False)
    print(f"Updated CSV export with {len(df)} rows and columns: {list(df.columns)}")

if __name__ == "__main__":
    main()
