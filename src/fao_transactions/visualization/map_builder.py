"""Standalone interactive HTML map generator for Geneva Property Transactions."""

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
    """Build a standalone, single-file interactive Leaflet/Swiss map containing all enriched transactions."""
    console.rule("[bold cyan]Building Interactive Geneva Real Estate Map[/bold cyan]")
    
    db_file = Path(db_path or settings.storage.database_path)
    out_file = Path(output_path or (Path(settings.storage.exports_dir) / "geneva_transactions_map.html"))
    out_file.parent.mkdir(parents=True, exist_ok=True)

    if db_file.exists():
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
        # Fallback to loading directly from CSV export (for fresh clones from GitHub)
        csv_file = Path(settings.storage.exports_dir) / "geneva_property_transactions.csv"
        if csv_file.exists():
            import pandas as pd
            console.print(f"[cyan]SQLite database not found. Loading from CSV deliverable:[/cyan] {csv_file.name}")
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
        else:
            rows = []

    console.print(f"Loaded [bold]{len(rows)}[/bold] geocoded transactions from SQLite.")

    # Distinct communes and zones for filters
    communes = sorted(list({r["commune"] for r in rows if r["commune"]}))
    zones = sorted(list({r["zone_code"] for r in rows if r["zone_code"]}))

    total_volume = sum(r["price_chf"] or 0 for r in rows)
    priced_count = sum(1 for r in rows if r["price_chf"])

    records_json = json.dumps(rows, ensure_ascii=False)
    communes_json = json.dumps(communes, ensure_ascii=False)
    zones_json = json.dumps(zones, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Genève Immobilier — Carte Interactive des Transactions FAO & SITG</title>
  
  <!-- Google Fonts: Inter -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  
  <!-- Leaflet & MarkerCluster CSS -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
  <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css"/>
  <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css"/>

  <style>
    :root {{
      --bg-dark: #0f172a;
      --panel-bg: rgba(15, 23, 42, 0.85);
      --panel-border: rgba(255, 255, 255, 0.1);
      --accent-blue: #38bdf8;
      --accent-emerald: #10b981;
      --accent-purple: #a855f7;
      --accent-amber: #f59e0b;
      --accent-rose: #f43f5e;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --radius-lg: 16px;
      --radius-md: 10px;
      --shadow-elevation: 0 20px 40px -15px rgba(0, 0, 0, 0.6), 0 0 1px 1px rgba(255, 255, 255, 0.08);
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background: var(--bg-dark);
      color: var(--text-main);
      overflow: hidden;
      height: 100vh;
      width: 100vw;
    }}

    #map {{
      height: 100vh;
      width: 100vw;
      z-index: 1;
      background: #090d16;
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
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid var(--panel-border);
      border-radius: var(--radius-lg);
      padding: 12px 20px;
      box-shadow: var(--shadow-elevation);
      pointer-events: auto;
      display: flex;
      align-items: center;
      gap: 16px;
    }}

    .brand-title {{
      font-weight: 800;
      font-size: 16px;
      letter-spacing: -0.02em;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .brand-title span.badge {{
      background: linear-gradient(135deg, #0284c7, #0369a1);
      color: #fff;
      font-size: 10px;
      font-weight: 700;
      padding: 2px 7px;
      border-radius: 6px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}

    .hud-stats {{
      display: flex;
      gap: 20px;
      font-size: 12px;
      border-left: 1px solid rgba(255, 255, 255, 0.1);
      padding-left: 16px;
    }}

    .stat-item {{
      display: flex;
      flex-direction: column;
    }}

    .stat-label {{
      color: var(--text-muted);
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}

    .stat-value {{
      font-weight: 700;
      font-size: 14px;
      color: var(--accent-blue);
    }}

    .stat-value.emerald {{ color: var(--accent-emerald); }}
    .stat-value.amber {{ color: var(--accent-amber); }}

    /* Sidebar Controls */
    .sidebar {{
      position: absolute;
      top: 80px;
      left: 16px;
      bottom: 24px;
      width: 360px;
      z-index: 1000;
      background: var(--panel-bg);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid var(--panel-border);
      border-radius: var(--radius-lg);
      padding: 20px;
      box-shadow: var(--shadow-elevation);
      display: flex;
      flex-direction: column;
      gap: 16px;
      overflow-y: auto;
      transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    .filter-section-title {{
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--accent-blue);
      margin-bottom: 8px;
    }}

    .search-box input {{
      width: 100%;
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: var(--radius-md);
      padding: 10px 14px;
      color: #fff;
      font-size: 13px;
      outline: none;
      transition: all 0.2s ease;
    }}

    .search-box input:focus {{
      border-color: var(--accent-blue);
      background: rgba(255, 255, 255, 0.1);
      box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2);
    }}

    .select-control select {{
      width: 100%;
      background: #1e293b;
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: var(--radius-md);
      padding: 10px 14px;
      color: #fff;
      font-size: 13px;
      outline: none;
      cursor: pointer;
    }}

    .filter-pills {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }}

    .pill-btn {{
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 20px;
      padding: 6px 12px;
      color: var(--text-muted);
      font-size: 12px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
    }}

    .pill-btn.active {{
      background: var(--accent-blue);
      color: #0f172a;
      font-weight: 700;
      border-color: var(--accent-blue);
    }}

    .toggle-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 13px;
      cursor: pointer;
    }}

    .toggle-row input {{
      cursor: pointer;
      width: 16px;
      height: 16px;
      accent-color: var(--accent-blue);
    }}

    .reset-btn {{
      background: rgba(244, 63, 94, 0.15);
      border: 1px solid rgba(244, 63, 94, 0.3);
      color: var(--accent-rose);
      border-radius: var(--radius-md);
      padding: 10px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
      text-align: center;
    }}

    .reset-btn:hover {{
      background: var(--accent-rose);
      color: #fff;
    }}

    /* Legend Box */
    .legend {{
      margin-top: auto;
      padding-top: 14px;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      font-size: 11px;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}

    .legend-item {{
      display: flex;
      align-items: center;
      gap: 8px;
      color: var(--text-muted);
    }}

    .legend-dot {{
      width: 10px;
      height: 10px;
      border-radius: 50%;
    }}

    /* Detail Drawer */
    .detail-drawer {{
      position: absolute;
      top: 80px;
      right: 16px;
      width: 380px;
      max-height: calc(100vh - 120px);
      z-index: 1000;
      background: var(--panel-bg);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 1px solid var(--panel-border);
      border-radius: var(--radius-lg);
      padding: 24px;
      box-shadow: var(--shadow-elevation);
      overflow-y: auto;
      display: none;
      flex-direction: column;
      gap: 16px;
    }}

    .detail-drawer.visible {{
      display: flex;
      animation: slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    @keyframes slideIn {{
      from {{ opacity: 0; transform: translateY(20px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    .detail-close {{
      align-self: flex-end;
      background: rgba(255, 255, 255, 0.08);
      border: none;
      color: var(--text-muted);
      width: 28px;
      height: 28px;
      border-radius: 50%;
      cursor: pointer;
      font-weight: 700;
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    .detail-price {{
      font-size: 26px;
      font-weight: 800;
      color: var(--accent-emerald);
      letter-spacing: -0.02em;
    }}

    .detail-badges {{
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
    }}

    .badge-tag {{
      font-size: 11px;
      font-weight: 600;
      padding: 4px 8px;
      border-radius: 6px;
      background: rgba(255, 255, 255, 0.08);
      color: var(--text-main);
    }}

    .badge-tag.zone {{
      background: rgba(168, 85, 247, 0.2);
      color: #c084fc;
      border: 1px solid rgba(168, 85, 247, 0.3);
    }}

    .badge-tag.building {{
      background: rgba(56, 189, 248, 0.15);
      color: #7dd3fc;
      border: 1px solid rgba(56, 189, 248, 0.3);
    }}

    .detail-row {{
      display: flex;
      flex-direction: column;
      gap: 2px;
      font-size: 13px;
    }}

    .detail-row .row-label {{
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
    }}

    .detail-row .row-value {{
      font-weight: 500;
      color: #fff;
    }}

    .sitg-btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      background: linear-gradient(135deg, #0284c7, #2563eb);
      color: #fff;
      padding: 12px 18px;
      border-radius: var(--radius-md);
      font-size: 13px;
      font-weight: 600;
      text-decoration: none;
      margin-top: 8px;
      transition: all 0.2s ease;
      box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }}

    .sitg-btn:hover {{
      transform: translateY(-1px);
      box-shadow: 0 6px 16px rgba(37, 99, 235, 0.5);
    }}

    /* Custom Leaflet Cluster Styling */
    .marker-cluster-small, .marker-cluster-medium, .marker-cluster-large {{
      background-color: rgba(15, 23, 42, 0.75) !important;
      backdrop-filter: blur(8px);
      border: 2px solid var(--accent-blue);
    }}
    .marker-cluster div {{
      background-color: transparent !important;
      color: #fff !important;
      font-weight: 700 !important;
      font-size: 12px !important;
      font-family: 'Inter', sans-serif !important;
    }}
  </style>
</head>
<body>

  <!-- Map Container -->
  <div id="map"></div>

  <!-- Top Bar HUD -->
  <div class="top-bar">
    <div class="hud-card">
      <div class="brand-title">
        Genève Immobilier
        <span class="badge">FAO & SITG</span>
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
          <span class="stat-label">Avec Prix</span>
          <span class="stat-value amber">{priced_count}</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Filter Sidebar -->
  <aside class="sidebar" id="sidebar">
    <div class="search-box">
      <div class="filter-section-title">Recherche instantanée</div>
      <input type="text" id="searchInput" placeholder="Adresse, acheteur, vendeur, parcelle...">
    </div>

    <div>
      <div class="filter-section-title">Type de notice</div>
      <div class="filter-pills">
        <button class="pill-btn active" data-source="ALL">Toutes</button>
        <button class="pill-btn" data-source="LDTR_Appartement">LDTR Appartements</button>
        <button class="pill-btn" data-source="Registre_Foncier">Registre Foncier</button>
      </div>
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
        <span>Transactions avec prix uniquement</span>
        <input type="checkbox" id="onlyPricedCheckbox">
      </label>
    </div>

    <button class="reset-btn" id="resetBtn">Réinitialiser les filtres</button>

    <div class="legend">
      <div class="filter-section-title">Légende des points</div>
      <div class="legend-item"><div class="legend-dot" style="background:#10b981;"></div> Prix supérieur à CHF 3M</div>
      <div class="legend-item"><div class="legend-dot" style="background:#38bdf8;"></div> LDTR Vente appartement</div>
      <div class="legend-item"><div class="legend-dot" style="background:#a855f7;"></div> Zone 5 Villas & Terrains</div>
      <div class="legend-item"><div class="legend-dot" style="background:#f59e0b;"></div> Autre mutation Registre Foncier</div>
    </div>
  </aside>

  <!-- Detail Drawer -->
  <div class="detail-drawer" id="detailDrawer">
    <button class="detail-close" id="detailClose">&times;</button>
    <div id="detailContent"></div>
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

    // Initialize Map with Swisstopo & Carto basemaps
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
        L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {{
          attribution: '&copy; Esri &mdash; Esri, DeLorme, NAVTEQ',
          maxZoom: 16
        }}),
        L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}', {{
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
        "Carte Sombre": darkTiles,
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
      if (r.price_chf && r.price_chf >= 3000000) return '#10b981'; // Green high price
      if (r.source_category === 'LDTR_Appartement') return '#38bdf8'; // Blue LDTR
      if (r.zone_code === '5') return '#a855f7'; // Purple Zone 5
      return '#f59e0b'; // Amber
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
          color: '#fff',
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
    document.getElementById('detailClose').addEventListener('click', () => {{
      detailDrawer.classList.remove('visible');
    }});

    function openDetail(r) {{
      const formattedPrice = r.price_chf 
        ? 'CHF ' + Math.round(r.price_chf).toLocaleString('fr-CH') 
        : '<span style="color:#94a3b8; font-size:16px;">Prix non publié (Mutation RF)</span>';

      const sitgLink = (r.lv95_e && r.lv95_n) 
        ? `https://map.sitg.ge.ch/?center=${{r.lv95_e}},${{r.lv95_n}}&scale=2500&mapresources=CADASTRE` 
        : null;

      detailContent.innerHTML = `
        <div class="detail-price">${{formattedPrice}}</div>
        <div class="detail-badges">
          <span class="badge-tag">${{r.source_category === 'LDTR_Appartement' ? 'Vente Appartement (LDTR)' : 'Registre Foncier'}}</span>
          ${{r.zone_code ? `<span class="badge-tag zone">${{r.zone_name || ('Zone ' + r.zone_code)}}</span>` : ''}}
          ${{r.building_period ? `<span class="badge-tag building">${{r.building_period}}</span>` : ''}}
        </div>

        <div class="detail-row">
          <span class="row-label">Commune & Adresse</span>
          <span class="row-value">${{r.address || (r.commune + ' (Parcelle ' + (r.parcel_number || 'N/A') + ')')}}</span>
        </div>

        ${{r.surface_m2 ? `
        <div class="detail-row">
          <span class="row-label">Surface & Pièces</span>
          <span class="row-value">${{r.surface_m2}} m² ${{r.rooms ? ' | ' + r.rooms + ' pièces' : ''}}</span>
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
          <span class="row-value">${{r.notice_date || 'N/A'}}</span>
        </div>

        ${{sitgLink ? `
        <a href="${{sitgLink}}" target="_blank" rel="noopener" class="sitg-btn">
          Voir sur le Géoportail SITG &rarr;
        </a>` : ''}}
      `;

      detailDrawer.classList.add('visible');
    }}

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

    [searchInput, communeSelect, zoneSelect, buildingSelect, onlyPricedCheckbox].forEach(el => {{
      el.addEventListener('input', applyFilters);
      el.addEventListener('change', applyFilters);
    }});

    document.getElementById('resetBtn').addEventListener('click', () => {{
      searchInput.value = '';
      communeSelect.value = 'ALL';
      zoneSelect.value = 'ALL';
      buildingSelect.value = 'ALL';
      onlyPricedCheckbox.checked = false;
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

      const filtered = DATA.filter(r => {{
        if (currentSource !== 'ALL' && r.source_category !== currentSource) return false;
        if (selComm !== 'ALL' && r.commune !== selComm) return false;
        if (selZone !== 'ALL' && r.zone_code !== selZone) return false;
        if (onlyPriced && (!r.price_chf || r.price_chf <= 0)) return false;

        if (selBuild !== 'ALL') {{
          const bp = (r.building_period || '').toLowerCase();
          if (!bp.includes(selBuild.toLowerCase())) return false;
        }}

        if (q) {{
          const str = [(r.address||''), (r.commune||''), (r.buyer||''), (r.seller||''), (r.parcel_number||'')].join(' ').toLowerCase();
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
    console.print(f"[bold green][OK] Interactive Map Generated:[/bold green] {out_file.resolve()} ({len(html_content)/1024:.1f} KB)\n")
    return out_file
