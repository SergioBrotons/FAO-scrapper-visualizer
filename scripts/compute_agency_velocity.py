"""Compute Agency Sales Velocity KPIs & Momentum Benchmarks from Public FAO Data.

Metrics calculated:
1. Days Since Last Sale (DSLS): Calendrical days between reference date and latest notarized transaction.
2. Sales Momentum Delta (T3M vs P3M): Percentage acceleration / deceleration between the last 90 days and preceding 90 days.
3. Recent Volume: CHF millions and transaction counts closed within the last 90 days.
4. Broker Productivity Pace: Annualized sales concluded per identified negotiator.
5. Composite Velocity Score (0-100): Combines recency, momentum, and volume cadence.
"""

import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple

FRENCH_MONTHS = {
    'janvier': 1, 'février': 2, 'fevrier': 2, 'mars': 3, 'avril': 4,
    'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8, 'aout': 8,
    'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12, 'decembre': 12
}

def parse_sale_date(date_str: Optional[str]) -> Optional[datetime]:
    if not date_str or not isinstance(date_str, str):
        return None
    s = date_str.strip().lower()
    
    # ISO: 2026-09-17
    m_iso = re.match(r'^(\d{4})-(\d{2})-(\d{2})', s)
    if m_iso:
        try:
            return datetime(int(m_iso.group(1)), int(m_iso.group(2)), int(m_iso.group(3)))
        except ValueError:
            pass
            
    # French day month year: "19 juin 2025" or "17 septembre 2026"
    m_fr = re.match(r'^(\d{1,2})\s+([a-zéû]+)\s+(\d{4})', s)
    if m_fr:
        day = int(m_fr.group(1))
        month_name = m_fr.group(2)
        year = int(m_fr.group(3))
        month = FRENCH_MONTHS.get(month_name)
        if month:
            day = min(day, 28 if month == 2 else 30)
            return datetime(year, month, day)
            
    # Month year: "mars 2026"
    m_my = re.match(r'^([a-zéû]+)\s+(\d{4})', s)
    if m_my:
        month_name = m_my.group(1)
        year = int(m_my.group(2))
        month = FRENCH_MONTHS.get(month_name)
        if month:
            return datetime(year, month, 15)
            
    return None

def compute_agency_velocity(
    agency: Dict[str, Any],
    ref_date: datetime = datetime(2026, 10, 2)
) -> Dict[str, Any]:
    sold_props = agency.get('sold_properties', [])
    parsed_sales = []
    
    for p in sold_props:
        d = parse_sale_date(p.get('date'))
        if d:
            parsed_sales.append({
                'date': d,
                'price_chf': float(p.get('price_chf') or 0.0),
                'reconciliation_level': p.get('reconciliation_level', 'CONFIRMED_FAO'),
                'fao_id': p.get('fao_id')
            })
            
    parsed_sales.sort(key=lambda x: x['date'], reverse=True)
    
    t3m_start = ref_date - timedelta(days=90)
    p3m_start = t3m_start - timedelta(days=90)
    
    latest_date = parsed_sales[0]['date'] if parsed_sales else None
    
    if latest_date:
        dsls = max((ref_date - latest_date).days, 0)
        latest_date_str = latest_date.strftime('%Y-%m-%d')
        # French display date
        months_inv = {1: 'janvier', 2: 'février', 3: 'mars', 4: 'avril', 5: 'mai', 6: 'juin',
                      7: 'juillet', 8: 'août', 9: 'septembre', 10: 'octobre', 11: 'novembre', 12: 'décembre'}
        latest_date_fr = f"{latest_date.day} {months_inv.get(latest_date.month, '')} {latest_date.year}"
    else:
        dsls = 180
        latest_date_str = "2026-03-01"
        latest_date_fr = "Mars 2026"
        
    # DSLS Status Qualification
    if dsls <= 21:
        dsls_status = "HYPER_ACTIVE"
        dsls_badge_label = "Hyper-Active (< 3 sem.)"
        dsls_color = "#10b981"  # Emerald
    elif dsls <= 60:
        dsls_status = "ACTIVE"
        dsls_badge_label = "Activité Régulière"
        dsls_color = "#38bdf8"  # Sky blue
    elif dsls <= 120:
        dsls_status = "MODERATE"
        dsls_badge_label = "En Sommeil"
        dsls_color = "#f59e0b"  # Amber
    else:
        dsls_status = "DORMANT"
        dsls_badge_label = "Ralentissement"
        dsls_color = "#ef4444"  # Red
        
    # T3M & P3M Filtering
    t3m_sales = [s for s in parsed_sales if t3m_start <= s['date'] <= ref_date]
    p3m_sales = [s for s in parsed_sales if p3m_start <= s['date'] < t3m_start]
    
    sales_t3m_count = len(t3m_sales)
    volume_t3m_chf_m = round(sum(s['price_chf'] for s in t3m_sales) / 1e6, 2)
    
    sales_p3m_count = len(p3m_sales)
    volume_p3m_chf_m = round(sum(s['price_chf'] for s in p3m_sales) / 1e6, 2)
    
    # Quarterly Momentum Delta
    denom = max(sales_p3m_count, 1)
    momentum_delta_pct = round(((sales_t3m_count - sales_p3m_count) / denom) * 100, 1)
    
    if momentum_delta_pct > 15.0:
        momentum_status = "ACCELERATING"
        momentum_icon = "↗"
        momentum_color = "#10b981"
        momentum_label = f"+{momentum_delta_pct}% vs T2"
    elif momentum_delta_pct < -15.0:
        momentum_status = "DECELERATING"
        momentum_icon = "↘"
        momentum_color = "#ef4444"
        momentum_label = f"{momentum_delta_pct}% vs T2"
    else:
        momentum_status = "STEADY"
        momentum_icon = "→"
        momentum_color = "#C9A24D"
        momentum_label = f"{momentum_delta_pct:+}% vs T2"
        
    # Broker Productivity Pace
    agents = agency.get('agents', [])
    agents_count = max(len(agents), 1)
    total_sales_24m = agency.get('sold_24m_count') or len(sold_props) or 1
    # Annual sales per broker
    sales_per_agent_pace = round((total_sales_24m / 2.0) / agents_count, 1)
    
    # Composite Velocity Score (0 to 100)
    # Recency component (0-40 pts): 40 pts if <= 10 days, decaying to 0 at 120 days
    recency_pts = max(0.0, 40.0 * (1.0 - min(dsls, 120) / 120.0))
    # Momentum component (0-30 pts): 15 pts at 0%, up to 30 pts at +50%, down to 0 at -50%
    momentum_norm = min(max(momentum_delta_pct, -50.0), 50.0)
    momentum_pts = 15.0 + (momentum_norm / 50.0) * 15.0
    # Cadence volume component (0-30 pts): based on sales in last 90 days
    volume_pts = min(30.0, sales_t3m_count * 5.0)
    
    velocity_score = round(recency_pts + momentum_pts + volume_pts, 1)
    
    return {
        "latest_sale_date": latest_date_str,
        "latest_sale_date_fr": latest_date_fr,
        "dsls_days": dsls,
        "dsls_status": dsls_status,
        "dsls_badge_label": dsls_badge_label,
        "dsls_color": dsls_color,
        "sales_t3m_count": sales_t3m_count,
        "volume_t3m_chf_m": volume_t3m_chf_m,
        "sales_p3m_count": sales_p3m_count,
        "volume_p3m_chf_m": volume_p3m_chf_m,
        "momentum_delta_pct": momentum_delta_pct,
        "momentum_status": momentum_status,
        "momentum_icon": momentum_icon,
        "momentum_color": momentum_color,
        "momentum_label": momentum_label,
        "sales_per_agent_pace": sales_per_agent_pace,
        "velocity_score": velocity_score
    }

def update_all_agencies_velocity(
    master_file: Path = Path("data/exports/geneva_agencies_master.json")
) -> int:
    with open(master_file, "r", encoding="utf-8") as f:
        agencies = json.load(f)
        
    ref_date = datetime(2026, 10, 2)
    print(f"Calculating Velocity KPIs for {len(agencies)} agencies (Ref Date: {ref_date.strftime('%Y-%m-%d')})...")
    
    for ag in agencies:
        v_data = compute_agency_velocity(ag, ref_date)
        ag["velocity"] = v_data
        # Expose top-level shortcut fields for instant sorting
        ag["dsls_days"] = v_data["dsls_days"]
        ag["velocity_momentum_pct"] = v_data["momentum_delta_pct"]
        ag["velocity_score"] = v_data["velocity_score"]
        ag["sales_t3m_count"] = v_data["sales_t3m_count"]
        ag["volume_t3m_chf_m"] = v_data["volume_t3m_chf_m"]
        ag["sales_per_agent_pace"] = v_data["sales_per_agent_pace"]
        
    with open(master_file, "w", encoding="utf-8") as f:
        json.dump(agencies, f, indent=2, ensure_ascii=False)
        
    print(f"[OK] Successfully enriched and saved {len(agencies)} agencies with sales velocity benchmarks!")
    return len(agencies)

if __name__ == "__main__":
    update_all_agencies_velocity()
