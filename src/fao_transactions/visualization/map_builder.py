"""Standalone interactive HTML map generator for Geneva Property Transactions with Cytria Brand Design, In-App 360° Modal, and 3-Phase Intelligence Enrichment."""

import json
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional

from rich.console import Console

from fao_transactions.config import settings

console = Console()


def build_interactive_map(
    db_path: Optional[str] = None,
    output_path: Optional[str] = None,
) -> Path:
    """Build a standalone, single-file interactive Leaflet/Swiss map styled with Cytria branding, in-app Street View modal, and full planning/visual enrichment."""
    console.rule("[bold #C9A24D]Building Cytria Geneva Real Estate Intelligence Map[/bold #C9A24D]")
    
    db_file = Path(db_path or settings.storage.database_path)
    out_file = Path(output_path or (Path(settings.storage.exports_dir) / "geneva_transactions_map.html"))
    out_file.parent.mkdir(parents=True, exist_ok=True)

    csv_file = Path(settings.storage.exports_dir) / "geneva_property_transactions.csv"
    if csv_file.exists():
        import pandas as pd
        console.print(f"[cyan]Loading fully enriched dataset from:[/cyan] {csv_file.name}")
        df = pd.read_csv(csv_file)
        df = df[df["centroid_wgs84_lon"].notna() & df["centroid_wgs84_lat"].notna()]
        df = df.rename(columns={
            "centroid_wgs84_lon": "lon",
            "centroid_wgs84_lat": "lat",
            "centroid_lv95_e": "lv95_e",
            "centroid_lv95_n": "lv95_n",
        })
        rows = [
            {k: (None if pd.isna(v) else v) for k, v in row.items()}
            for row in df.to_dict(orient="records")
        ]
    elif db_file.exists():
        with sqlite3.connect(db_file) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    t.id,
                    t.source_category,
                    t.notice_date,
                    t.commune,
                    t.parcel_number,
                    t.transaction_type,
                    t.property_type,
                    t.nature,
                    t.address,
                    t.rooms,
                    t.floor,
                    t.surface_m2,
                    t.seller,
                    t.buyer,
                    t.price_chf,
                    t.case_number,
                    e.egrid,
                    e.zone_code,
                    e.zone_name,
                    e.building_destination,
                    e.building_period,
                    e.building_year,
                    e.building_floors,
                    e.surface_official_m2,
                    round(e.centroid_wgs84_lon, 5) as lon,
                    round(e.centroid_wgs84_lat, 5) as lat,
                    round(e.centroid_lv95_e, 0) as lv95_e,
                    round(e.centroid_lv95_n, 0) as lv95_n
                FROM transactions t
                JOIN enrichments e ON t.id = e.transaction_id
                WHERE e.centroid_wgs84_lon IS NOT NULL
                ORDER BY t.notice_date DESC
            """)
            rows = [dict(r) for r in cursor.fetchall()]
    else:
        rows = []

    console.print(f"Loaded [bold]{len(rows)}[/bold] geocoded and enriched transactions.")

    # Distinct communes and zones for filters
    communes = sorted(list({r["commune"] for r in rows if r["commune"]}))
    zones = sorted(list({r["zone_code"] for r in rows if r["zone_code"]}))

    total_volume = sum(r["price_chf"] or 0 for r in rows)
    priced_count = sum(1 for r in rows if r["price_chf"])
    plq_count = sum(1 for r in rows if r.get("plq_number"))
    dev_count = sum(1 for r in rows if r.get("zone_dev_name"))
    permit_count = sum(1 for r in rows if r.get("permit_number"))

    records_json = json.dumps(rows, ensure_ascii=False)
    communes_json = json.dumps(communes, ensure_ascii=False)
    zones_json = json.dumps(zones, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CYTRIA — Intelligence Immobilière Genève (FAO × SITG)</title>
  
  <!-- Cytria Fonts: Hanken Grotesk, Inter, JetBrains Mono -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  
  <!-- Leaflet & MarkerCluster CSS -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
  <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css"/>
  <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css"/>

  <style>
    :root {{
      /* Cytria Official Brand System */
      --color-brand-50: #FBF7ED;
      --color-brand-100: #F5EACF;
      --color-brand-200: #EBD49A;
      --color-brand-300: #DEBC69;
      --color-brand-400: #D2AA4F;
      --color-brand-500: #C9A24D;
      --color-brand-600: #A77F22;
      --color-brand-700: #805E0D;

      --color-ink-950: #080D11;
      --color-ink-900: #0B1117;
      --color-ink-850: #101820;
      --color-ink-800: #17212A;
      --color-ink-700: #25313B;
      --color-ink-600: #3B4650;

      --color-night: #10141B;
      --color-paper: #F7F4EC;
      --color-sand-100: #F4F1EA;
      --color-sand-300: #DDD5C8;
      --color-neutral-400: #A8A29A;
      --color-muted-ink: #5A6068;

      --color-success: #2F6B57;
      --color-warning: #A46D13;
      --color-error: #B33A33;
      --color-info: #315E78;
      --color-purple: #8A4F7D;

      --panel-bg: rgba(16, 20, 27, 0.94);
      --panel-border: rgba(255, 255, 255, 0.12);
      --panel-border-gold: rgba(201, 162, 77, 0.35);

      --font-brand: "Hanken Grotesk", "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
      --font-mono: "JetBrains Mono", "SFMono-Regular", Consolas, monospace;

      --shadow-elevation: 0 20px 40px -15px rgba(0, 0, 0, 0.8), 0 0 1px 1px rgba(255, 255, 255, 0.08);
      --radius-strict: 0px;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: var(--font-brand);
      background: var(--color-ink-950);
      color: var(--color-paper);
      overflow: hidden;
      height: 100vh;
      width: 100vw;
      -webkit-font-smoothing: antialiased;
    }}

    #map {{
      height: 100vh;
      width: 100vw;
      z-index: 1;
      background: var(--color-ink-950);
    }}

    /* Top Bar HUD */
    .top-bar {{
      position: absolute;
      top: 16px;
      left: 16px;
      right: 16px;
      z-index: 1000;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      pointer-events: none;
    }}

    .hud-card {{
      background: var(--panel-bg);
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
      border: 1px solid var(--panel-border);
      border-radius: var(--radius-strict);
      padding: 12px 22px;
      box-shadow: var(--shadow-elevation);
      pointer-events: auto;
      display: flex;
      align-items: center;
      gap: 20px;
    }}

    .brand-group {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}

    .cytria-logo-svg {{
      height: 30px;
      width: auto;
      display: block;
    }}

    .brand-divider {{
      width: 1px;
      height: 28px;
      background: rgba(255, 255, 255, 0.15);
    }}

    .brand-meta {{
      display: flex;
      flex-direction: column;
      gap: 2px;
    }}

    .brand-meta-title {{
      font-weight: 700;
      font-size: 13px;
      letter-spacing: 0.04em;
      color: var(--color-paper);
      text-transform: uppercase;
    }}

    .brand-meta-sub {{
      font-size: 10px;
      letter-spacing: 0.08em;
      color: var(--color-brand-400);
      text-transform: uppercase;
      font-weight: 600;
    }}

    .badge-fao {{
      background: rgba(201, 162, 77, 0.12);
      border: 1px solid var(--panel-border-gold);
      color: var(--color-brand-400);
      font-family: var(--font-mono);
      font-size: 10px;
      font-weight: 700;
      padding: 3px 8px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }}

    .hud-stats {{
      display: flex;
      gap: 22px;
      font-size: 12px;
      border-left: 1px solid rgba(255, 255, 255, 0.12);
      padding-left: 20px;
    }}

    .stat-item {{
      display: flex;
      flex-direction: column;
    }}

    .stat-label {{
      color: var(--color-sand-300);
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-weight: 600;
    }}

    .stat-value {{
      font-family: var(--font-mono);
      font-weight: 700;
      font-size: 15px;
      color: var(--color-paper);
      letter-spacing: -0.02em;
    }}

    .stat-value.gold {{ color: var(--color-brand-400); }}
    .stat-value.emerald {{ color: #10b981; }}
    .stat-value.info {{ color: #38bdf8; }}

    /* Sidebar Controls */
    .sidebar {{
      position: absolute;
      top: 84px;
      left: 16px;
      bottom: 24px;
      width: 380px;
      z-index: 1000;
      background: var(--panel-bg);
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
      border: 1px solid var(--panel-border);
      border-radius: var(--radius-strict);
      padding: 22px;
      box-shadow: var(--shadow-elevation);
      display: flex;
      flex-direction: column;
      gap: 16px;
      overflow-y: auto;
      transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    /* Custom Scrollbars */
    .sidebar::-webkit-scrollbar, .detail-drawer::-webkit-scrollbar {{
      width: 5px;
    }}
    .sidebar::-webkit-scrollbar-track, .detail-drawer::-webkit-scrollbar-track {{
      background: rgba(0, 0, 0, 0.2);
    }}
    .sidebar::-webkit-scrollbar-thumb, .detail-drawer::-webkit-scrollbar-thumb {{
      background: rgba(201, 162, 77, 0.4);
    }}

    .filter-section-title {{
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      color: var(--color-brand-400);
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .filter-section-title::before {{
      content: "";
      display: inline-block;
      width: 4px;
      height: 4px;
      background: var(--color-brand-500);
    }}

    .search-box input {{
      width: 100%;
      background: var(--color-ink-900);
      border: 1px solid var(--panel-border);
      border-radius: var(--radius-strict);
      padding: 10px 14px;
      color: var(--color-paper);
      font-family: var(--font-brand);
      font-size: 13px;
      outline: none;
      transition: all 0.2s ease;
    }}

    .search-box input:focus {{
      border-color: var(--color-brand-500);
      background: var(--color-ink-850);
      box-shadow: 0 0 0 1px var(--color-brand-500);
    }}

    .select-control select {{
      width: 100%;
      background: var(--color-ink-900);
      border: 1px solid var(--panel-border);
      border-radius: var(--radius-strict);
      padding: 10px 14px;
      color: var(--color-paper);
      font-family: var(--font-brand);
      font-size: 13px;
      outline: none;
      cursor: pointer;
      transition: all 0.2s ease;
    }}

    .select-control select:focus {{
      border-color: var(--color-brand-500);
    }}

    .filter-pills {{
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
    }}

    .pill-btn {{
      background: var(--color-ink-900);
      border: 1px solid var(--panel-border);
      border-radius: var(--radius-strict);
      padding: 6px 11px;
      color: var(--color-sand-300);
      font-family: var(--font-brand);
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      cursor: pointer;
      transition: all 0.2s ease;
    }}

    .pill-btn:hover {{
      border-color: var(--color-brand-400);
      color: var(--color-paper);
    }}

    .pill-btn.active {{
      background: var(--color-brand-500);
      color: var(--color-ink-950);
      font-weight: 700;
      border-color: var(--color-brand-500);
    }}

    .toggle-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 12px;
      color: var(--color-paper);
      cursor: pointer;
      background: var(--color-ink-900);
      border: 1px solid var(--panel-border);
      padding: 9px 12px;
      margin-bottom: 4px;
    }}

    .toggle-row input {{
      cursor: pointer;
      width: 16px;
      height: 16px;
      accent-color: var(--color-brand-500);
    }}

    .reset-btn {{
      background: transparent;
      border: 1px solid rgba(179, 58, 51, 0.4);
      color: #e27d76;
      border-radius: var(--radius-strict);
      padding: 10px;
      font-family: var(--font-brand);
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      cursor: pointer;
      transition: all 0.2s ease;
      text-align: center;
    }}

    .reset-btn:hover {{
      background: var(--color-error);
      color: #fff;
      border-color: var(--color-error);
    }}

    /* Legend Box */
    .legend {{
      margin-top: auto;
      padding-top: 12px;
      border-top: 1px solid rgba(255, 255, 255, 0.1);
      font-size: 11px;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}

    .legend-item {{
      display: flex;
      align-items: center;
      gap: 10px;
      color: var(--color-sand-300);
    }}

    .legend-dot {{
      width: 10px;
      height: 10px;
      border-radius: var(--radius-strict);
      flex-shrink: 0;
    }}

    /* Detail Drawer */
    .detail-drawer {{
      position: absolute;
      top: 84px;
      right: 16px;
      width: 440px;
      max-height: calc(100vh - 120px);
      z-index: 1000;
      background: var(--panel-bg);
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
      border: 1px solid var(--panel-border);
      border-radius: var(--radius-strict);
      padding: 24px;
      box-shadow: var(--shadow-elevation);
      overflow-y: auto;
      display: none;
      flex-direction: column;
      gap: 16px;
    }}

    .detail-drawer.visible {{
      display: flex;
      animation: slideIn 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    @keyframes slideIn {{
      from {{ opacity: 0; transform: translateX(20px); }}
      to {{ opacity: 1; transform: translateX(0); }}
    }}

    .detail-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      padding-bottom: 14px;
    }}

    .detail-close {{
      background: transparent;
      border: 1px solid var(--panel-border);
      color: var(--color-sand-300);
      width: 28px;
      height: 28px;
      border-radius: var(--radius-strict);
      cursor: pointer;
      font-weight: 700;
      font-size: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s ease;
    }}

    .detail-close:hover {{
      border-color: var(--color-brand-400);
      color: var(--color-paper);
    }}

    .detail-price {{
      font-family: var(--font-mono);
      font-size: 26px;
      font-weight: 700;
      color: var(--color-brand-400);
      letter-spacing: -0.02em;
    }}

    .detail-badges {{
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
    }}

    .badge-tag {{
      font-size: 10px;
      font-weight: 700;
      padding: 4px 8px;
      border-radius: var(--radius-strict);
      background: var(--color-ink-800);
      border: 1px solid var(--panel-border);
      color: var(--color-paper);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}

    .badge-tag.plq {{
      background: rgba(138, 79, 125, 0.25);
      color: #d896c8;
      border-color: rgba(138, 79, 125, 0.5);
    }}

    .badge-tag.zonedev {{
      background: rgba(201, 162, 77, 0.2);
      color: var(--color-brand-300);
      border-color: var(--panel-border-gold);
    }}

    .badge-tag.permit {{
      background: rgba(47, 107, 87, 0.3);
      color: #6ee7b7;
      border-color: rgba(47, 107, 87, 0.6);
    }}

    .badge-tag.grandprojet {{
      background: rgba(49, 94, 120, 0.3);
      color: #7dd3fc;
      border-color: rgba(49, 94, 120, 0.5);
    }}

    /* Action Toolbar (Street View & SITG) */
    .action-toolbar {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }}

    .action-btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      padding: 11px 12px;
      border-radius: var(--radius-strict);
      font-family: var(--font-brand);
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      text-decoration: none;
      transition: all 0.2s ease;
      cursor: pointer;
    }}

    .action-btn.streetview {{
      background: var(--color-ink-900);
      border: 1px solid var(--panel-border-gold);
      color: var(--color-brand-300);
    }}
    .action-btn.streetview:hover {{
      background: rgba(201, 162, 77, 0.15);
      border-color: var(--color-brand-500);
      color: var(--color-paper);
    }}

    .action-btn.sitg {{
      background: var(--color-brand-500);
      border: 1px solid var(--color-brand-500);
      color: var(--color-ink-950);
      box-shadow: 0 4px 14px rgba(201, 162, 77, 0.25);
    }}
    .action-btn.sitg:hover {{
      background: var(--color-brand-400);
      box-shadow: 0 6px 20px rgba(201, 162, 77, 0.4);
    }}

    /* Intelligence Section */
    .intel-section {{
      background: var(--color-ink-900);
      border: 1px solid var(--panel-border);
      padding: 14px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}

    .intel-title {{
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--color-brand-400);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .intel-link {{
      color: var(--color-brand-300);
      text-decoration: underline;
      font-size: 10px;
      font-family: var(--font-brand);
      font-weight: 600;
    }}

    .detail-grid {{
      display: grid;
      grid-template-columns: 1fr;
      gap: 10px;
      background: var(--color-ink-900);
      border: 1px solid var(--panel-border);
      padding: 14px;
    }}

    .detail-row {{
      display: flex;
      flex-direction: column;
      gap: 2px;
      font-size: 13px;
    }}

    .detail-row .row-label {{
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--color-neutral-400);
      font-weight: 600;
    }}

    .detail-row .row-value {{
      font-weight: 500;
      color: var(--color-paper);
    }}

    .detail-row .row-value.mono {{
      font-family: var(--font-mono);
      color: var(--color-brand-200);
    }}

    /* Street View In-App Modal */
    .modal-overlay {{
      position: fixed;
      inset: 0;
      background: rgba(8, 13, 17, 0.88);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      z-index: 2000;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 24px;
    }}

    .modal-overlay.visible {{
      display: flex;
      animation: modalFadeIn 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    @keyframes modalFadeIn {{
      from {{ opacity: 0; transform: scale(0.98); }}
      to {{ opacity: 1; transform: scale(1); }}
    }}

    .modal-window {{
      width: 100%;
      max-width: 1050px;
      height: 80vh;
      background: var(--color-night);
      border: 1px solid var(--panel-border-gold);
      border-radius: var(--radius-strict);
      display: flex;
      flex-direction: column;
      box-shadow: 0 30px 60px -15px rgba(0, 0, 0, 0.95);
      overflow: hidden;
    }}

    .modal-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 14px 20px;
      background: var(--color-ink-900);
      border-bottom: 1px solid var(--panel-border);
    }}

    .modal-header-left {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .modal-title-box {{
      display: flex;
      flex-direction: column;
      gap: 2px;
    }}

    .modal-title {{
      font-size: 14px;
      font-weight: 700;
      color: var(--color-paper);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}

    .modal-subtitle {{
      font-size: 10px;
      font-weight: 600;
      color: var(--color-brand-400);
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}

    .modal-header-actions {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .modal-ext-link {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 12px;
      background: var(--color-ink-800);
      border: 1px solid var(--panel-border);
      color: var(--color-sand-300);
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      text-decoration: none;
      transition: all 0.2s ease;
    }}

    .modal-ext-link:hover {{
      border-color: var(--color-brand-400);
      color: var(--color-paper);
    }}

    .modal-close-btn {{
      background: transparent;
      border: 1px solid var(--panel-border);
      color: var(--color-sand-300);
      width: 32px;
      height: 32px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      font-size: 18px;
      font-weight: 700;
      transition: all 0.2s ease;
    }}

    .modal-close-btn:hover {{
      border-color: var(--color-brand-400);
      color: var(--color-paper);
    }}

    .modal-body {{
      flex: 1;
      width: 100%;
      height: 100%;
      position: relative;
      background: var(--color-ink-950);
    }}

    .modal-iframe {{
      width: 100%;
      height: 100%;
      border: none;
    }}

    /* Custom Leaflet Cluster Styling */
    .marker-cluster-small, .marker-cluster-medium, .marker-cluster-large {{
      background-color: rgba(16, 20, 27, 0.85) !important;
      backdrop-filter: blur(8px);
      border: 2px solid var(--color-brand-500) !important;
      border-radius: var(--radius-strict) !important;
    }}
    .marker-cluster div {{
      background-color: transparent !important;
      color: var(--color-paper) !important;
      font-weight: 700 !important;
      font-size: 12px !important;
      font-family: var(--font-mono) !important;
    }}

    /* Leaflet Controls Styling */
    .leaflet-control-layers {{
      background: var(--panel-bg) !important;
      border: 1px solid var(--panel-border) !important;
      border-radius: var(--radius-strict) !important;
      color: var(--color-paper) !important;
      font-family: var(--font-brand) !important;
      font-size: 12px !important;
      box-shadow: var(--shadow-elevation) !important;
    }}
    .leaflet-control-zoom a {{
      background: var(--panel-bg) !important;
      color: var(--color-paper) !important;
      border: 1px solid var(--panel-border) !important;
      border-radius: var(--radius-strict) !important;
    }}
  </style>
</head>
<body>

  <!-- Map Container -->
  <div id="map"></div>

  <!-- Top Bar HUD -->
  <div class="top-bar">
    <div class="hud-card">
      <div class="brand-group">
        <!-- Official Cytria Vector Logo -->
        <svg class="cytria-logo-svg" viewBox="606 188 836 309" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path fill="#F7F4EC" fill-rule="evenodd" d="M731.0,202.5 L757.0,202.5 L778.5,207.0 L745.0,250.5 L728.0,251.5 L709.0,258.5 L695.0,268.5 L687.5,276.0 L676.5,293.0 L670.5,311.0 L669.5,332.0 L674.5,351.0 L685.5,370.0 L697.0,381.5 L704.0,386.5 L721.0,394.5 L733.0,397.5 L755.0,397.5 L773.0,392.5 L791.0,382.5 L803.0,370.5 L856.5,371.0 L852.5,380.0 L842.5,396.0 L821.0,418.5 L808.0,427.5 L793.0,435.5 L779.0,440.5 L760.0,444.5 L739.0,445.5 L713.0,441.5 L693.0,434.5 L680.0,427.5 L667.0,418.5 L653.5,406.0 L644.5,395.0 L635.5,381.0 L624.5,353.0 L621.5,336.0 L621.5,313.0 L625.5,292.0 L636.5,265.0 L649.5,246.0 L666.0,229.5 L689.0,214.5 L710.0,206.5 L731.0,202.5 Z M1243.0,234.5 L1255.0,234.5 L1260.0,236.5 L1266.5,242.0 L1269.5,248.0 L1270.5,252.0 L1269.5,260.0 L1267.5,264.0 L1259.0,271.5 L1251.0,273.5 L1242.0,272.5 L1236.0,269.5 L1230.5,264.0 L1228.5,260.0 L1227.5,252.0 L1231.5,242.0 L1238.0,236.5 L1243.0,234.5 Z M1044.0,257.5 L1077.0,257.5 L1078.5,259.0 L1079.0,293.5 L1114.5,294.0 L1114.0,319.5 L1078.5,320.0 L1078.5,394.0 L1082.0,399.5 L1088.0,402.5 L1113.0,401.5 L1114.5,427.0 L1095.0,430.5 L1072.0,429.5 L1057.0,423.5 L1049.5,416.0 L1045.5,408.0 L1043.5,399.0 L1043.5,320.0 L1014.0,319.5 L966.5,421.0 L963.5,425.0 L950.5,453.0 L942.5,465.0 L933.0,474.5 L927.0,478.5 L917.0,482.5 L903.0,484.5 L876.0,483.5 L875.5,480.0 L882.5,456.0 L904.0,455.5 L913.0,451.5 L920.5,443.0 L930.5,424.0 L930.5,421.0 L871.5,294.0 L910.5,294.0 L934.5,351.0 L947.5,386.0 L949.0,386.5 L976.5,322.0 L986.5,295.0 L988.0,293.5 L1043.0,293.5 L1044.0,257.5 Z M1351.0,289.5 L1374.0,290.5 L1390.0,294.5 L1399.0,298.5 L1408.0,304.5 L1418.5,316.0 L1423.5,327.0 L1426.5,346.0 L1426.5,423.0 L1425.5,424.0 L1426.5,427.0 L1425.0,428.5 L1392.0,428.5 L1390.5,427.0 L1390.5,420.0 L1389.0,419.5 L1375.0,426.5 L1363.0,429.5 L1333.0,430.5 L1323.0,428.5 L1306.0,421.5 L1292.5,408.0 L1289.5,402.0 L1287.5,393.0 L1288.5,381.0 L1294.5,369.0 L1308.0,357.5 L1319.0,352.5 L1338.0,347.5 L1353.0,346.5 L1354.0,345.5 L1392.5,345.0 L1391.5,337.0 L1387.5,328.0 L1380.0,320.5 L1370.0,316.5 L1346.0,315.5 L1326.0,321.5 L1314.0,329.5 L1311.5,328.0 L1298.5,309.0 L1298.0,305.5 L1314.0,297.5 L1326.0,293.5 L1351.0,289.5 Z M1199.0,290.5 L1214.0,290.5 L1217.5,292.0 L1217.5,321.0 L1209.0,319.5 L1194.0,320.5 L1184.0,324.5 L1174.5,333.0 L1169.5,341.0 L1167.5,348.0 L1167.5,427.0 L1166.0,428.5 L1134.0,428.5 L1133.5,294.0 L1167.0,293.5 L1168.0,311.5 L1183.0,296.5 L1199.0,290.5 Z M1232.0,293.5 L1266.5,294.0 L1266.5,427.0 L1265.0,428.5 L1231.5,428.0 L1232.0,293.5 Z M1359.0,368.5 L1337.0,372.5 L1331.0,375.5 L1325.5,381.0 L1323.5,386.0 L1323.5,391.0 L1326.5,398.0 L1330.0,401.5 L1341.0,406.5 L1358.0,407.5 L1372.0,404.5 L1381.0,399.5 L1386.5,394.0 L1390.5,387.0 L1392.5,379.0 L1392.5,370.0 L1391.0,368.5 L1359.0,368.5 Z"/>
          <path fill="#C9A24D" fill-rule="evenodd" d="M790.0,210.5 L807.0,218.5 L819.0,226.5 L838.5,245.0 L853.5,268.0 L857.5,277.0 L858.0,281.5 L806.0,281.5 L786.0,261.5 L770.0,253.5 L759.5,251.0 L763.5,244.0 L790.0,210.5 Z"/>
        </svg>

        <div class="brand-divider"></div>

        <div class="brand-meta">
          <div class="brand-meta-title">Transactions Immobilières</div>
          <div class="brand-meta-sub">Canton de Genève</div>
        </div>

        <span class="badge-fao">FAO × SITG</span>
      </div>

      <div class="hud-stats">
        <div class="stat-item">
          <span class="stat-label">Transactions</span>
          <span class="stat-value" id="stat-count">{len(rows):,}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Volume Déclaré</span>
          <span class="stat-value emerald">CHF {total_volume/1e9:.2f} Mrd</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">En Zone Dév.</span>
          <span class="stat-value gold" id="stat-dev">{dev_count:,}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Avec PLQ</span>
          <span class="stat-value info" id="stat-plq">{plq_count:,}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Permis (APA)</span>
          <span class="stat-value emerald" id="stat-permit">{permit_count:,}</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Filter Sidebar -->
  <aside class="sidebar" id="sidebar">
    <div class="search-box">
      <div class="filter-section-title">Recherche instantanée</div>
      <input type="text" id="searchInput" placeholder="Adresse, acheteur, vendeur, PLQ, permis...">
    </div>

    <div>
      <div class="filter-section-title">Type de notice officielle</div>
      <div class="filter-pills">
        <button class="pill-btn active" data-source="ALL">Toutes</button>
        <button class="pill-btn" data-source="LDTR_Appartement">LDTR Appartements</button>
        <button class="pill-btn" data-source="Registre_Foncier">Registre Foncier</button>
      </div>
    </div>

    <div>
      <div class="filter-section-title">Filtres Urbanisme & Développement</div>
      <label class="toggle-row">
        <span>En Zone de Développement (LDTR/LGZD)</span>
        <input type="checkbox" id="onlyDevCheckbox">
      </label>
      <label class="toggle-row">
        <span>Avec Plan Localisé de Quartier (PLQ)</span>
        <input type="checkbox" id="onlyPlqCheckbox">
      </label>
      <label class="toggle-row">
        <span>Avec Permis de Construire (APA / Projet)</span>
        <input type="checkbox" id="onlyPermitCheckbox">
      </label>
    </div>

    <div>
      <div class="filter-section-title">Commune genevoise</div>
      <div class="select-control">
        <select id="communeSelect">
          <option value="ALL">Toutes les communes ({len(communes)})</option>
        </select>
      </div>
    </div>

    <div>
      <div class="filter-section-title">Zone d'affectation SITG</div>
      <div class="select-control">
        <select id="zoneSelect">
          <option value="ALL">Toutes les zones d'aménagement</option>
        </select>
      </div>
    </div>

    <div>
      <div class="filter-section-title">Époque de construction</div>
      <div class="select-control">
        <select id="buildingSelect">
          <option value="ALL">Toutes époques de construction</option>
          <option value="avant 1919">Bâtiments historiques (Avant 1919)</option>
          <option value="1919">1919 à 1960</option>
          <option value="1961">1961 à 1990</option>
          <option value="1991">1991 à 2015</option>
          <option value="2016">Récent (2016 à aujourd'hui)</option>
        </select>
      </div>
    </div>

    <div>
      <div class="filter-section-title">Filtre de prix</div>
      <label class="toggle-row">
        <span>Transactions avec prix publié uniquement</span>
        <input type="checkbox" id="onlyPricedCheckbox">
      </label>
    </div>

    <button class="reset-btn" id="resetBtn">Réinitialiser les filtres</button>

    <div class="legend">
      <div class="filter-section-title">Légende des marqueurs</div>
      <div class="legend-item"><div class="legend-dot" style="background:#C9A24D;"></div> Prix supérieur à CHF 3M (Gold)</div>
      <div class="legend-item"><div class="legend-dot" style="background:#315E78;"></div> LDTR Vente appartement</div>
      <div class="legend-item"><div class="legend-dot" style="background:#8A4F7D;"></div> Avec PLQ ou Zone de Dév.</div>
      <div class="legend-item"><div class="legend-dot" style="background:#A46D13;"></div> Zone 5 Villas & Terrains</div>
      <div class="legend-item"><div class="legend-dot" style="background:#2F6B57;"></div> Autre mutation Registre Foncier</div>
    </div>
  </aside>

  <!-- Detail Drawer -->
  <div class="detail-drawer" id="detailDrawer">
    <div class="detail-header">
      <div class="detail-price" id="detailPriceDisplay"></div>
      <button class="detail-close" id="detailClose">&times;</button>
    </div>
    <div id="detailContent"></div>
  </div>

  <!-- In-App Street View 360° Modal -->
  <div class="modal-overlay" id="streetViewModal">
    <div class="modal-window">
      <div class="modal-header">
        <div class="modal-header-left">
          <div class="modal-title-box">
            <div class="modal-title" id="modalTitle">Vue 360°</div>
            <div class="modal-subtitle">Panorama Street View &bull; Cytria Intelligence</div>
          </div>
        </div>
        <div class="modal-header-actions">
          <a href="#" id="modalExtLink" target="_blank" rel="noopener" class="modal-ext-link">
            Ouvrir dans Google Maps ↗
          </a>
          <button class="modal-close-btn" id="modalCloseBtn">&times;</button>
        </div>
      </div>
      <div class="modal-body">
        <iframe id="modalIframe" class="modal-iframe" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen src="about:blank"></iframe>
      </div>
    </div>
  </div>

  <!-- Leaflet & MarkerCluster JS -->
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
  <script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>

  <script>
    const DATA = {records_json};
    const COMMUNES = {communes_json};
    const ZONES = {zones_json};

    // Populate selects
    const communeSelect = document.getElementById('communeSelect');
    COMMUNES.forEach(c => {{
      const opt = document.createElement('option');
      opt.value = c;
      opt.textContent = c;
      communeSelect.appendChild(opt);
    }});

    const zoneSelect = document.getElementById('zoneSelect');
    ZONES.forEach(z => {{
      const opt = document.createElement('option');
      opt.value = z;
      opt.textContent = 'Zone ' + z;
      zoneSelect.appendChild(opt);
    }});

    // Initialize Map with Swisstopo & Esri basemaps
    const map = leafletMap();

    function leafletMap() {{
      const m = L.map('map', {{
        center: [46.2044, 6.1432], // Geneva center
        zoom: 12,
        minZoom: 10,
        maxZoom: 19,
        zoomControl: false
      }});

      L.control.zoom({{ position: 'bottomright' }}).addTo(m);

      const darkTiles = L.layerGroup([
        L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
          attribution: '&copy; Esri &mdash; Esri, DeLorme, NAVTEQ',
          maxZoom: 16
        }}),
        L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
          maxZoom: 16
        }})
      ]).addTo(m);

      const swissGrey = L.tileLayer('https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.pixelkarte-grau/default/current/3857/{{z}}/{{x}}/{{y}}.jpeg', {{
        attribution: '&copy; swisstopo',
        maxZoom: 19
      }});

      const swissImage = L.tileLayer('https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.swissimage/default/current/3857/{{z}}/{{x}}/{{y}}.jpeg', {{
        attribution: '&copy; swisstopo',
        maxZoom: 19
      }});

      const osmStandard = L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
        attribution: '&copy; OpenStreetMap contributors',
        maxZoom: 19
      }});

      L.control.layers({{
        "Carte Sombre (Cytria Dark)": darkTiles,
        "Plan Officiel Swisstopo": swissGrey,
        "Photo Aérienne Swisstopo": swissImage,
        "OpenStreetMap": osmStandard
      }}, null, {{ position: 'bottomleft' }}).addTo(m);

      return m;
    }}

    // Marker Clusters
    const clusterGroup = L.markerClusterGroup({{
      chunkedLoading: true,
      maxClusterRadius: 45,
      spiderfyOnMaxZoom: true,
      showCoverageOnHover: false
    }});
    map.addLayer(clusterGroup);

    function getMarkerColor(r) {{
      if (r.price_chf && r.price_chf >= 3000000) return '#C9A24D'; // Cytria Gold for >= 3M
      if (r.plq_number || r.zone_dev_name) return '#8A4F7D'; // Purple for PLQ / Zone Dev
      if (r.source_category === 'LDTR_Appartement') return '#315E78'; // Cytria Slate Blue
      if (r.zone_code === '5') return '#A46D13'; // Cytria Warm Ochre
      return '#2F6B57'; // Cytria Forest Green
    }}

    function createMarkers(records) {{
      clusterGroup.clearLayers();
      const markers = [];

      records.forEach(r => {{
        if (!r.lat || !r.lon) return;

        const color = getMarkerColor(r);
        const radius = r.price_chf ? 8 : 6;

        const marker = L.circleMarker([r.lat, r.lon], {{
          radius: radius,
          fillColor: color,
          color: '#F7F4EC',
          weight: 1.5,
          opacity: 0.9,
          fillOpacity: 0.85
        }});

        marker.on('click', () => openDetail(r));
        markers.push(marker);
      }});

      clusterGroup.addLayers(markers);
      document.getElementById('stat-count').textContent = records.length.toLocaleString('fr-CH');
    }}

    // Initial render
    createMarkers(DATA);

    // Detail Drawer
    const detailDrawer = document.getElementById('detailDrawer');
    const detailContent = document.getElementById('detailContent');
    const detailPriceDisplay = document.getElementById('detailPriceDisplay');

    document.getElementById('detailClose').addEventListener('click', () => {{
      detailDrawer.classList.remove('visible');
    }});

    function openDetail(r) {{
      detailPriceDisplay.innerHTML = r.price_chf 
        ? 'CHF ' + Math.round(r.price_chf).toLocaleString('fr-CH') 
        : '<span style="color:#A8A29A; font-size:15px; font-weight:500;">Prix non publié (Mutation RF)</span>';

      const sitgLink = (r.lv95_e && r.lv95_n) 
        ? (r.sitg_aerial_url || `https://map.sitg.ge.ch/?center=${{r.lv95_e}},${{r.lv95_n}}&scale=1000&mapresources=CADASTRE,ORTHOPHOTO_2023`)
        : null;

      const streetViewLink = (r.lat && r.lon)
        ? (r.streetview_url || `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${{r.lat}},${{r.lon}}`)
        : null;

      const escapedTitle = (r.address || (r.commune + ' Parcelle ' + (r.parcel_number || ''))).replace(/'/g, "\\'");

      detailContent.innerHTML = `
        <div class="detail-badges">
          <span class="badge-tag">${{r.source_category === 'LDTR_Appartement' ? 'Vente Appartement (LDTR)' : 'Registre Foncier'}}</span>
          ${{r.zone_code ? `<span class="badge-tag zone">${{r.zone_name || ('Zone ' + r.zone_code)}}</span>` : ''}}
          ${{r.plq_number ? `<span class="badge-tag plq">PLQ #${{r.plq_number}}</span>` : ''}}
          ${{r.zone_dev_name ? `<span class="badge-tag zonedev">${{r.zone_dev_code || 'Zone Dév.'}}</span>` : ''}}
          ${{r.permit_number ? `<span class="badge-tag permit">${{r.permit_number}}</span>` : ''}}
          ${{r.grand_projet_name ? `<span class="badge-tag grandprojet">${{r.grand_projet_name}}</span>` : ''}}
        </div>

        <!-- Action Toolbar (Street View Modal & SITG) -->
        <div class="action-toolbar">
          ${{r.lat && r.lon ? `
          <button type="button" class="action-btn streetview" onclick="openStreetViewModal('${{r.lat}}', '${{r.lon}}', '${{escapedTitle}}', '${{streetViewLink}}')">
            Street View 360° ⛶
          </button>` : ''}}
          ${{sitgLink ? `
          <a href="${{sitgLink}}" target="_blank" rel="noopener" class="action-btn sitg">
            SITG 5cm Aérien ↗
          </a>` : ''}}
        </div>

        <!-- Urban Planning & Development Intelligence -->
        ${{(r.plq_number || r.zone_dev_name || r.permit_number || r.grand_projet_name) ? `
        <div class="intel-section">
          <div class="intel-title">
            <span>Urbanisme & Projets Futurs</span>
            <span style="color:var(--color-sand-300); font-size:9px;">SITG OPEN DATA</span>
          </div>

          ${{r.plq_number ? `
          <div class="detail-row">
            <span class="row-label">Plan Localisé de Quartier (PLQ)</span>
            <span class="row-value">
              PLQ N° <strong>${{r.plq_number}}</strong> (${{r.plq_name || 'Geneve'}}) — ${{r.plq_status || 'En vigueur'}}
              ${{r.plq_plan_url ? `<br><a href="${{r.plq_plan_url}}" target="_blank" class="intel-link">Télécharger le Plan PLQ (PDF) ↗</a>` : ''}}
              ${{r.plq_reglement_url ? ` &bull; <a href="${{r.plq_reglement_url}}" target="_blank" class="intel-link">Règlement (PDF) ↗</a>` : ''}}
            </span>
          </div>` : ''}}

          ${{r.zone_dev_name ? `
          <div class="detail-row">
            <span class="row-label">Zone de Développement (LDTR/LGZD)</span>
            <span class="row-value">
              ${{r.zone_dev_name}} ${{r.zone_dev_restriction ? `— <em>${{r.zone_dev_restriction}}</em>` : ''}}
              ${{r.zone_dev_url ? `<br><a href="${{r.zone_dev_url}}" target="_blank" class="intel-link">Plan de zone légale (PDF) ↗</a>` : ''}}
            </span>
          </div>` : ''}}

          ${{r.permit_number ? `
          <div class="detail-row">
            <span class="row-label">Permis de Construire / Projet</span>
            <span class="row-value">
              <strong>${{r.permit_number}}</strong>: ${{r.permit_type || 'Projet'}} (${{r.permit_destination || 'Bâtiment'}})
              ${{r.permit_floors ? ` &bull; ${{r.permit_floors}} étages` : ''}}
              ${{r.permit_sad_url ? `<br><a href="${{r.permit_sad_url}}" target="_blank" class="intel-link">Consulter Dossier SAD Cantonal ↗</a>` : ''}}
            </span>
          </div>` : ''}}

          ${{r.grand_projet_name ? `
          <div class="detail-row">
            <span class="row-label">Périmètre Grand Projet Cantonal</span>
            <span class="row-value">
              ${{r.grand_projet_name}} (${{r.grand_projet_type || 'PDCn'}})
              ${{r.grand_projet_url ? `<br><a href="${{r.grand_projet_url}}" target="_blank" class="intel-link">Fiche Grand Projet (PDF) ↗</a>` : ''}}
            </span>
          </div>` : ''}}
        </div>` : ''}}

        <div class="detail-grid">
          <div class="detail-row">
            <span class="row-label">Commune & Adresse</span>
            <span class="row-value">${{r.address || (r.commune + ' (Parcelle ' + (r.parcel_number || 'N/A') + ')')}}</span>
          </div>

          ${{r.egrid ? `
          <div class="detail-row">
            <span class="row-label">Identifiant Fédéral EGRID</span>
            <span class="row-value mono">${{r.egrid}}</span>
          </div>` : ''}}

          ${{r.parcel_number ? `
          <div class="detail-row">
            <span class="row-label">Numéro de Parcelle</span>
            <span class="row-value mono">${{r.parcel_number}}</span>
          </div>` : ''}}

          ${{r.surface_m2 ? `
          <div class="detail-row">
            <span class="row-label">Surface & Pièces</span>
            <span class="row-value mono">${{r.surface_m2}} m² ${{r.rooms ? ' | ' + r.rooms + ' pièces' : ''}}</span>
          </div>` : ''}}

          ${{r.building_destination ? `
          <div class="detail-row">
            <span class="row-label">Destination bâtiment</span>
            <span class="row-value">${{r.building_destination}} ${{r.building_floors ? '(' + r.building_floors + ' étages)' : ''}}</span>
          </div>` : ''}}

          <div class="detail-row">
            <span class="row-label">Acquéreur (Acheteur)</span>
            <span class="row-value">${{r.buyer || 'Non précisé'}}</span>
          </div>

          <div class="detail-row">
            <span class="row-label">Aliénateur (Vendeur)</span>
            <span class="row-value">${{r.seller || 'Non précisé'}}</span>
          </div>

          <div class="detail-row">
            <span class="row-label">Date publication FAO</span>
            <span class="row-value mono">${{r.notice_date || 'N/A'}}</span>
          </div>
        </div>
      `;

      detailDrawer.classList.add('visible');
    }}

    // Street View In-App Modal Logic
    const streetViewModal = document.getElementById('streetViewModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalIframe = document.getElementById('modalIframe');
    const modalExtLink = document.getElementById('modalExtLink');
    const modalCloseBtn = document.getElementById('modalCloseBtn');

    function openStreetViewModal(lat, lon, title, extUrl) {{
      modalTitle.textContent = title || 'Vue Panoramique 360°';
      modalExtLink.href = extUrl || `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${{lat}},${{lon}}`;
      modalIframe.src = `https://maps.google.com/maps?q=&layer=c&cbll=${{lat}},${{lon}}&cbp=11,0,0,0,0&output=svembed`;
      streetViewModal.classList.add('visible');
    }}

    function closeStreetViewModal() {{
      streetViewModal.classList.remove('visible');
      modalIframe.src = 'about:blank';
    }}

    modalCloseBtn.addEventListener('click', closeStreetViewModal);
    streetViewModal.addEventListener('click', (e) => {{
      if (e.target === streetViewModal) {{
        closeStreetViewModal();
      }}
    }});

    document.addEventListener('keydown', (e) => {{
      if (e.key === 'Escape' && streetViewModal.classList.contains('visible')) {{
        closeStreetViewModal();
      }}
    }});

    // Filter Logic
    let currentSource = 'ALL';

    document.querySelectorAll('.pill-btn').forEach(btn => {{
      btn.addEventListener('click', (e) => {{
        document.querySelectorAll('.pill-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        currentSource = e.target.getAttribute('data-source');
        applyFilters();
      }});
    }});

    const searchInput = document.getElementById('searchInput');
    const buildingSelect = document.getElementById('buildingSelect');
    const onlyPricedCheckbox = document.getElementById('onlyPricedCheckbox');
    const onlyDevCheckbox = document.getElementById('onlyDevCheckbox');
    const onlyPlqCheckbox = document.getElementById('onlyPlqCheckbox');
    const onlyPermitCheckbox = document.getElementById('onlyPermitCheckbox');

    [searchInput, communeSelect, zoneSelect, buildingSelect, onlyPricedCheckbox, onlyDevCheckbox, onlyPlqCheckbox, onlyPermitCheckbox].forEach(el => {{
      el.addEventListener('input', applyFilters);
      el.addEventListener('change', applyFilters);
    }});

    document.getElementById('resetBtn').addEventListener('click', () => {{
      searchInput.value = '';
      communeSelect.value = 'ALL';
      zoneSelect.value = 'ALL';
      buildingSelect.value = 'ALL';
      onlyPricedCheckbox.checked = false;
      onlyDevCheckbox.checked = false;
      onlyPlqCheckbox.checked = false;
      onlyPermitCheckbox.checked = false;
      currentSource = 'ALL';
      document.querySelectorAll('.pill-btn').forEach(b => b.classList.remove('active'));
      document.querySelector('.pill-btn[data-source="ALL"]').classList.add('active');
      applyFilters();
    }});

    function applyFilters() {{
      const q = searchInput.value.toLowerCase().trim();
      const selComm = communeSelect.value;
      const selZone = zoneSelect.value;
      const selBuild = buildingSelect.value;
      const onlyPriced = onlyPricedCheckbox.checked;
      const onlyDev = onlyDevCheckbox.checked;
      const onlyPlq = onlyPlqCheckbox.checked;
      const onlyPermit = onlyPermitCheckbox.checked;

      const filtered = DATA.filter(r => {{
        if (currentSource !== 'ALL' && r.source_category !== currentSource) return false;
        if (selComm !== 'ALL' && r.commune !== selComm) return false;
        if (selZone !== 'ALL' && r.zone_code !== selZone) return false;
        if (onlyPriced && (!r.price_chf || r.price_chf <= 0)) return false;
        if (onlyDev && !r.zone_dev_name) return false;
        if (onlyPlq && !r.plq_number) return false;
        if (onlyPermit && !r.permit_number) return false;

        if (selBuild !== 'ALL') {{
          const bp = (r.building_period || '').toLowerCase();
          if (!bp.includes(selBuild.toLowerCase())) return false;
        }}

        if (q) {{
          const str = [(r.address||''), (r.commune||''), (r.buyer||''), (r.seller||''), (r.parcel_number||''), (r.egrid||''), (r.plq_name||''), (r.permit_number||''), (r.grand_projet_name||'')].join(' ').toLowerCase();
          if (!str.includes(q)) return false;
        }}

        return true;
      }});

      createMarkers(filtered);
    }}
  </script>
</body>
</html>
"""
    out_file.write_text(html_content, encoding="utf-8")
    console.print(f"[bold green][OK] Cytria Interactive Map with Street View Modal Generated:[/bold green] {out_file.resolve()} ({len(html_content)/1024:.1f} KB)\n")
    return out_file
