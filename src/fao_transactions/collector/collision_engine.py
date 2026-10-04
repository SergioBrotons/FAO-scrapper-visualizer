"""Multi-Agency Mandate Collision & Price Spread Detection Engine.

Analyzes active property listings across portals (Immobilier.ch, Homegate, ImmoScout24)
and agency websites to detect when the exact same property is marketed concurrently
by multiple competing brokers/agencies (simple mandates), tracking price wars and spreads.
"""

import math
import re
from typing import Dict, List, Any, Optional, Tuple


def normalize_string(text: str) -> str:
    """Normalize string for fuzzy comparison."""
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r'[àáâãäå]', 'a', text)
    text = re.sub(r'[èéêë]', 'e', text)
    text = re.sub(r'[ìíîï]', 'i', text)
    text = re.sub(r'[òóôõö]', 'o', text)
    text = re.sub(r'[ùúûü]', 'u', text)
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def compute_listing_similarity(l1: Dict[str, Any], l2: Dict[str, Any]) -> Tuple[float, List[str]]:
    """
    Score similarity (0 to 100) between two active listings to detect multi-mandates.
    """
    reasons = []
    score = 0.0

    # 1. Commune must match exactly
    c1 = normalize_string(l1.get("commune", ""))
    c2 = normalize_string(l2.get("commune", ""))
    if not c1 or not c2 or c1 != c2:
        return 0.0, []
    score += 25
    reasons.append(f"Même commune ({l1.get('commune')})")

    # 2. Typology class match
    t1 = l1.get("typology", "").upper()
    t2 = l2.get("typology", "").upper()
    if t1 and t2 and t1 == t2:
        score += 20
        reasons.append(f"Même typologie ({t1})")
    elif t1 != t2:
        return 0.0, []

    # 3. Room count match (tolerance: +/- 0.5 room)
    r1 = float(l1.get("rooms") or 0)
    r2 = float(l2.get("rooms") or 0)
    if r1 > 0 and r2 > 0:
        if abs(r1 - r2) <= 0.5:
            score += 20
            reasons.append(f"Nombre de pièces concordant ({r1} vs {r2} pièces)")
        else:
            return 0.0, []

    # 4. Living surface match (tolerance: +/- 8%)
    s1 = float(l1.get("surface_habitable_m2") or 0)
    s2 = float(l2.get("surface_habitable_m2") or 0)
    if s1 > 0 and s2 > 0:
        pct_diff = abs(s1 - s2) / max(s1, s2)
        if pct_diff <= 0.08:
            score += 25
            reasons.append(f"Surface habitable quasi-identique (~{round((s1+s2)/2)} m²)")
        elif pct_diff > 0.15:
            return 0.0, []

    # 5. Land surface match for villas (tolerance: +/- 10%)
    l_s1 = float(l1.get("surface_terrain_m2") or 0)
    l_s2 = float(l2.get("surface_terrain_m2") or 0)
    if l_s1 > 0 and l_s2 > 0:
        l_pct_diff = abs(l_s1 - l_s2) / max(l_s1, l_s2)
        if l_pct_diff <= 0.10:
            score += 10
            reasons.append(f"Parcelle terrain concordante (~{round((l_s1+l_s2)/2)} m²)")

    return score, reasons


def detect_multi_mandate_collisions(listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Cluster active listings into multi-mandate collisions where 2+ distinct agencies market the same asset.
    """
    collisions = []
    visited_ids = set()

    for i in range(len(listings)):
        l1 = listings[i]
        id1 = l1.get("id")
        if id1 in visited_ids:
            continue

        cluster = [l1]
        agencies_in_cluster = {l1.get("agency_id") or l1.get("agency_raw_name")}

        for j in range(i + 1, len(listings)):
            l2 = listings[j]
            id2 = l2.get("id")
            if id2 in visited_ids:
                continue

            # Must be from different agencies to constitute a multi-mandate collision
            ag2 = l2.get("agency_id") or l2.get("agency_raw_name")
            if ag2 in agencies_in_cluster:
                continue

            sim_score, reasons = compute_listing_similarity(l1, l2)
            if sim_score >= 80:
                cluster.append(l2)
                agencies_in_cluster.add(ag2)
                visited_ids.add(id2)

        if len(cluster) >= 2:
            visited_ids.add(id1)
            prices = [float(item["price_asking_chf"]) for item in cluster if item.get("price_asking_chf")]
            min_p = min(prices) if prices else 0
            max_p = max(prices) if prices else 0
            spread_chf = max_p - min_p
            spread_pct = (spread_chf / min_p * 100.0) if min_p > 0 else 0.0

            collisions.append({
                "collision_id": f"col_{cluster[0].get('commune', 'ge')}_{int(min_p)}_{len(cluster)}",
                "commune": cluster[0].get("commune"),
                "typology": cluster[0].get("typology"),
                "estimated_address": cluster[0].get("address_display") or cluster[0].get("commune"),
                "agency_count": len(agencies_in_cluster),
                "agencies_involved": list(agencies_in_cluster),
                "min_price_chf": min_p,
                "max_price_chf": max_p,
                "price_spread_chf": spread_chf,
                "price_spread_pct": round(spread_pct, 2),
                "listings": cluster,
                "collision_label": f"🚨 Mandat Multiple ({len(agencies_in_cluster)} agences)" if spread_chf == 0 else f"🔥 Guerre des Prix (Écart: CHF {spread_chf:,.0f} / {spread_pct:.1f}%)"
            })

    return sorted(collisions, key=lambda c: c["price_spread_chf"], reverse=True)
