#!/usr/bin/env python3
"""Inject Agency Duel feature into map_builder.py and build index.html."""

import re
from pathlib import Path

MAP_BUILDER = Path("src/fao_transactions/visualization/map_builder.py")
content = MAP_BUILDER.read_text(encoding="utf-8")

# 1. Inject CSS
CSS_TARGET = """    .agency-focus-banner .focus-banner-reset:hover {
      background: #ef4444;
      color: #fff;
    }

    /* Social Action Buttons */"""

CSS_REPLACEMENT = """    .agency-focus-banner .focus-banner-reset:hover {
      background: #ef4444;
      color: #fff;
    }

    /* Agency Duel Specific Styling */
    .agency-marker-pin.duel-a {
      border-color: #06b6d4 !important;
      background: rgba(8, 13, 17, 0.95);
      box-shadow: 0 0 16px rgba(6, 182, 212, 0.8) !important;
    }
    .agency-marker-pin.duel-a .pin-badge {
      background: #06b6d4 !important;
      color: #080d11 !important;
    }
    .agency-marker-pin.duel-b {
      border-color: #f59e0b !important;
      background: rgba(8, 13, 17, 0.95);
      box-shadow: 0 0 16px rgba(245, 158, 11, 0.8) !important;
    }
    .agency-marker-pin.duel-b .pin-badge {
      background: #f59e0b !important;
      color: #080d11 !important;
    }

    .duel-modal-window {
      background: var(--panel-bg);
      border: 1px solid rgba(6, 182, 212, 0.45);
      width: 95vw;
      max-width: 1220px;
      max-height: 88vh;
      height: 88vh;
      display: flex;
      flex-direction: column;
      box-shadow: 0 16px 48px rgba(0, 0, 0, 0.8), 0 0 24px rgba(6, 182, 212, 0.2);
      overflow: hidden;
    }
    .duel-header {
      padding: 14px 24px;
      background: var(--color-ink-950);
      border-bottom: 1px solid var(--panel-border);
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-shrink: 0;
    }
    .duel-header h2 {
      font-family: var(--font-brand);
      font-size: 16px;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: #38bdf8;
      margin: 0 0 2px 0;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .duel-header p {
      margin: 0;
      font-size: 11px;
      color: var(--color-sand-300);
    }
    .duel-selector-bar {
      padding: 12px 24px;
      background: rgba(8, 13, 17, 0.98);
      border-bottom: 1px solid var(--panel-border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      flex-wrap: wrap;
      flex-shrink: 0;
    }
    .duel-select-box {
      flex: 1;
      min-width: 260px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .duel-badge-tag {
      font-family: var(--font-mono);
      font-size: 10px;
      font-weight: 800;
      padding: 3px 8px;
      border-radius: 2px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      white-space: nowrap;
    }
    .duel-badge-a {
      background: rgba(6, 182, 212, 0.18);
      color: #38bdf8;
      border: 1px solid #06b6d4;
    }
    .duel-badge-b {
      background: rgba(245, 158, 11, 0.18);
      color: #fbbf24;
      border: 1px solid #f59e0b;
    }
    .duel-select-input {
      flex: 1;
      padding: 8px 12px;
      background: var(--color-ink-900);
      border: 1px solid var(--panel-border);
      color: var(--color-paper);
      font-family: var(--font-brand);
      font-size: 12px;
      font-weight: 600;
      outline: none;
      cursor: pointer;
    }
    .duel-select-input:focus {
      border-color: #06b6d4;
    }
    .duel-vs-badge {
      font-family: var(--font-brand);
      font-size: 13px;
      font-weight: 900;
      color: #e2e8f0;
      background: var(--color-ink-800);
      border: 1px solid rgba(255,255,255,0.12);
      padding: 4px 10px;
      border-radius: 4px;
      letter-spacing: 0.08em;
    }
    .duel-body {
      flex: 1;
      overflow-y: auto;
      padding: 20px 24px;
      background: var(--color-ink-900);
      display: flex;
      flex-direction: column;
      gap: 18px;
    }
    .duel-kpi-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;
    }
    .duel-kpi-table th {
      background: var(--color-ink-950);
      padding: 10px 14px;
      font-family: var(--font-mono);
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      border-bottom: 1px solid var(--panel-border);
    }
    .duel-kpi-table td {
      padding: 10px 14px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      vertical-align: middle;
    }
    .duel-kpi-table tr:hover td {
      background: rgba(255, 255, 255, 0.02);
    }
    .duel-val-a {
      text-align: right;
      color: #38bdf8;
      font-weight: 700;
      width: 38%;
    }
    .duel-metric-name {
      text-align: center;
      color: var(--color-sand-300);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      width: 24%;
      font-family: var(--font-mono);
    }
    .duel-val-b {
      text-align: left;
      color: #fbbf24;
      font-weight: 700;
      width: 38%;
    }
    .duel-winner-pill {
      display: inline-block;
      font-size: 9.5px;
      font-weight: 700;
      padding: 1px 6px;
      border-radius: 2px;
      margin-left: 6px;
      font-family: var(--font-mono);
    }
    .winner-a {
      background: rgba(6, 182, 212, 0.2);
      color: #38bdf8;
      border: 1px solid rgba(6, 182, 212, 0.4);
    }
    .winner-b {
      background: rgba(245, 158, 11, 0.2);
      color: #fbbf24;
      border: 1px solid rgba(245, 158, 11, 0.4);
    }

    /* Social Action Buttons */"""

if CSS_TARGET in content:
    content = content.replace(CSS_TARGET, CSS_REPLACEMENT, 1)
    print("[OK] CSS injected.")
else:
    print("[!] CSS_TARGET not found.")

# 2. Inject Duel Map Banner
BANNER_TARGET = """  <!-- Floating Agency & Agent Focus Banner -->
  <div id="agencyFocusBanner" class="agency-focus-banner" style="display:none;">
    <div class="focus-banner-content">
      <span class="focus-badge" id="focusBannerBadge">Agence Isolée</span>
      <span class="focus-title" id="focusBannerTitle"></span>
      <span class="focus-count" id="focusBannerCount"></span>
    </div>
    <button type="button" class="focus-banner-reset" onclick="renderAgenciesOnMap(null)" title="Voir tout le réseau (Réinitialiser le focus)">✕</button>
  </div>"""

BANNER_REPLACEMENT = """  <!-- Floating Agency & Agent Focus Banner -->
  <div id="agencyFocusBanner" class="agency-focus-banner" style="display:none;">
    <div class="focus-banner-content">
      <span class="focus-badge" id="focusBannerBadge">Agence Isolée</span>
      <span class="focus-title" id="focusBannerTitle"></span>
      <span class="focus-count" id="focusBannerCount"></span>
    </div>
    <button type="button" class="focus-banner-reset" onclick="renderAgenciesOnMap(null)" title="Voir tout le réseau (Réinitialiser le focus)">✕</button>
  </div>

  <!-- Floating Agency Duel Map Banner -->
  <div id="agencyDuelBanner" class="agency-focus-banner" style="display:none; border-color:#06b6d4; box-shadow:0 8px 32px rgba(0, 0, 0, 0.8), 0 0 20px rgba(6, 182, 212, 0.35);">
    <div class="focus-banner-content">
      <span class="focus-badge" style="background:rgba(6, 182, 212, 0.25); color:#38bdf8; border-color:#06b6d4;">⚔️ DUEL ACTIF</span>
      <span class="focus-title" id="duelBannerTitle" style="color:#ffffff;"></span>
      <span class="focus-count" id="duelBannerMeta" style="color:var(--color-sand-300);"></span>
    </div>
    <div style="display:flex; align-items:center; gap:6px; margin-left:8px;">
      <button type="button" class="btn-sm" onclick="openAgencyDuelModal()" style="background:var(--color-ink-800); border:1px solid #06b6d4; color:#38bdf8; padding:3px 8px; font-size:10px; cursor:pointer;">
        📊 Comparateur
      </button>
      <button type="button" class="focus-banner-reset" onclick="resetAgencyDuelMap()" title="Quitter le mode Duel">✕</button>
    </div>
  </div>"""

if BANNER_TARGET in content:
    content = content.replace(BANNER_TARGET, BANNER_REPLACEMENT, 1)
    print("[OK] Banner injected.")
else:
    print("[!] BANNER_TARGET not found.")

# 3. Inject Button in Agency BI Subtoolbar
SUBTOOLBAR_TARGET = """        <!-- 3. AGENCY BI Subtoolbar -->
        <div class="product-subtoolbar" id="subtoolbarAgencyBI" style="display: none;">
          <button type="button" class="subtool-btn active" id="agencyBtnMap" onclick="switchAgencyTool('MAP')">
            Carte des Agences <span class="subtool-badge" id="navBadgeAgencies">__AGENCIES_COUNT__</span>
          </button>
          <button type="button" class="subtool-btn" id="btnOpenLeagueTable" onclick="openLeagueModal()">
            Benchmark & Parts de Marché
          </button>
          <button type="button" class="subtool-btn" id="btnOpenMarketingModal" onclick="openMarketingModal()">
            Veille Marketing
          </button>
        </div>"""

SUBTOOLBAR_REPLACEMENT = """        <!-- 3. AGENCY BI Subtoolbar -->
        <div class="product-subtoolbar" id="subtoolbarAgencyBI" style="display: none;">
          <button type="button" class="subtool-btn active" id="agencyBtnMap" onclick="switchAgencyTool('MAP')">
            Carte des Agences <span class="subtool-badge" id="navBadgeAgencies">__AGENCIES_COUNT__</span>
          </button>
          <button type="button" class="subtool-btn" id="btnOpenAgencyDuel" onclick="openAgencyDuelModal()" style="border-color: rgba(6, 182, 212, 0.5); color: #38bdf8;">
            <span style="color:#06b6d4;">⚔️</span> Duel Face-à-Face
          </button>
          <button type="button" class="subtool-btn" id="btnOpenLeagueTable" onclick="openLeagueModal()">
            Benchmark & Parts de Marché
          </button>
          <button type="button" class="subtool-btn" id="btnOpenMarketingModal" onclick="openMarketingModal()">
            Veille Marketing
          </button>
        </div>"""

if SUBTOOLBAR_TARGET in content:
    content = content.replace(SUBTOOLBAR_TARGET, SUBTOOLBAR_REPLACEMENT, 1)
    print("[OK] Subtoolbar button injected.")
else:
    print("[!] SUBTOOLBAR_TARGET not found.")

# 4. Inject Duel Modal Window HTML
MODAL_TARGET = """      <div class="league-body" id="leagueBodyContent">
        <!-- Injected via JavaScript -->
      </div>
    </div>
  </div>"""

MODAL_REPLACEMENT = """      <div class="league-body" id="leagueBodyContent">
        <!-- Injected via JavaScript -->
      </div>
    </div>
  </div>

  <!-- Cytria Agency Duel: Head-to-Head & Turf Conflict Modal -->
  <div class="modal-overlay" id="agencyDuelModal">
    <div class="duel-modal-window">
      <div class="duel-header">
        <div>
          <h2>⚔️ Duel d'Agences — Comparateur Face-à-Face & Conflit Territorial</h2>
          <p>Analyse comparative bilatérale des parts de marché, de la vélocité et du chevauchement géographique (Genève)</p>
        </div>
        <button class="modal-close-btn" onclick="closeAgencyDuelModal()">&times;</button>
      </div>

      <div class="duel-selector-bar">
        <div class="duel-select-box">
          <span class="duel-badge-tag duel-badge-a">Agence A</span>
          <select id="duelSelectAgencyA" class="duel-select-input" onchange="renderAgencyDuelContent()">
          </select>
        </div>

        <div class="duel-vs-badge">VS</div>

        <div class="duel-select-box">
          <span class="duel-badge-tag duel-badge-b">Agence B</span>
          <select id="duelSelectAgencyB" class="duel-select-input" onchange="renderAgencyDuelContent()">
          </select>
        </div>

        <div>
          <button type="button" class="btn-sm" onclick="projectDuelToMap()" style="padding: 8px 16px; background: rgba(6, 182, 212, 0.2); border: 1px solid #06b6d4; color: #38bdf8; font-weight: 700; cursor: pointer; display: flex; align-items: center; gap: 6px; white-space: nowrap;">
            📍 Projeter le Duel sur la Carte
          </button>
        </div>
      </div>

      <div class="duel-body" id="duelBodyContent">
        <!-- Rendered via JavaScript -->
      </div>
    </div>
  </div>"""

if MODAL_TARGET in content:
    content = content.replace(MODAL_TARGET, MODAL_REPLACEMENT, 1)
    print("[OK] Modal HTML injected.")
else:
    print("[!] MODAL_TARGET not found.")

# 5. Inject Duel Action in League Table Row and Agency Detail Drawer
LEAGUE_ROW_TARGET = """              <td>
                <span style="color:var(--color-brand-300); font-weight:600; font-size:11px;">${a.primary_territory}</span><br>
                <span style="color:var(--color-sand-300); font-size:10px;">Rayon: ${(a.radius_meters/1000).toFixed(1)} km</span>
              </td>
              <td>
                <button type="button" class="view-map-btn" onclick="goToAgencyOnMap('${a.id}')">Voir sur Carte</button>
              </td>"""

LEAGUE_ROW_REPLACEMENT = """              <td>
                <span style="color:var(--color-brand-300); font-weight:600; font-size:11px;">${a.primary_territory}</span><br>
                <span style="color:var(--color-sand-300); font-size:10px;">Rayon: ${(a.radius_meters/1000).toFixed(1)} km</span>
              </td>
              <td>
                <div style="display:flex; gap:6px; flex-wrap:nowrap;">
                  <button type="button" class="view-map-btn" onclick="goToAgencyOnMap('${a.id}')">Carte</button>
                  <button type="button" class="view-map-btn" style="border-color:#06b6d4; color:#38bdf8;" onclick="openAgencyDuelModal('${a.id}')" title="Comparer en face-à-face">⚔️ Duel</button>
                </div>
              </td>"""

if LEAGUE_ROW_TARGET in content:
    content = content.replace(LEAGUE_ROW_TARGET, LEAGUE_ROW_REPLACEMENT, 1)
    print("[OK] League table row duel button injected.")
else:
    print("[!] LEAGUE_ROW_TARGET not found.")

# Agency Detail Drawer Header Duel Button
DRAWER_TARGET = """      detailPriceDisplay.innerHTML = `
        <span class="score-badge" style="margin-right:8px;">Score Cytria ${agency.cytria_score}/100</span>
        <span style="font-size:14px; font-weight:700; color:var(--color-brand-300);">#${agency.rank} ${agency.name}</span>
      `;"""

DRAWER_REPLACEMENT = """      detailPriceDisplay.innerHTML = `
        <div style="display:flex; align-items:center; justify-content:space-between; width:100%; gap:8px;">
          <div>
            <span class="score-badge" style="margin-right:8px;">Score Cytria ${agency.cytria_score}/100</span>
            <span style="font-size:14px; font-weight:700; color:var(--color-brand-300);">#${agency.rank} ${agency.name}</span>
          </div>
          <button type="button" class="view-map-btn" style="border-color:#06b6d4; color:#38bdf8; padding:3px 8px; font-size:10px; white-space:nowrap;" onclick="openAgencyDuelModal('${agency.id}')">
            ⚔️ Duel Face-à-Face
          </button>
        </div>
      `;"""

if DRAWER_TARGET in content:
    content = content.replace(DRAWER_TARGET, DRAWER_REPLACEMENT, 1)
    print("[OK] Drawer duel button injected.")
else:
    print("[!] DRAWER_TARGET not found.")

# 6. Inject Duel JS Functions
JS_TARGET = """    document.getElementById('leagueTableModal').addEventListener('click', (e) => {
      if (e.target.id === 'leagueTableModal') {
        closeLeagueModal();
      }
    });

    // ==========================================
    // MARKETING BENCHMARK & INTELLIGENCE LOGIC
    // ==========================================
    function openMarketingModal() {"""

JS_REPLACEMENT = """    document.getElementById('leagueTableModal').addEventListener('click', (e) => {
      if (e.target.id === 'leagueTableModal') {
        closeLeagueModal();
      }
    });

    // ==========================================
    // AGENCY DUEL (HEAD-TO-HEAD COMPARISON)
    // ==========================================
    let currentDuelAgencyAId = null;
    let currentDuelAgencyBId = null;
    let isDuelMapActive = false;

    function initAgencyDuelSelectors(preselectA = null, preselectB = null) {
      const selA = document.getElementById('duelSelectAgencyA');
      const selB = document.getElementById('duelSelectAgencyB');
      if (!selA || !selB || !LEAGUE_DATA.agencies) return;

      const agencies = LEAGUE_DATA.agencies;
      const opts = agencies.map(a => `<option value="${a.id}">#${a.rank} ${a.name} (${a.headquarters_commune})</option>`).join('');

      selA.innerHTML = opts;
      selB.innerHTML = opts;

      // Defaults: Top 1 (BARNES) vs Top 2 (Cardis) or aliases
      const defaultA = preselectA || currentDuelAgencyAId || (agencies[0] ? agencies[0].id : null);
      let defaultB = preselectB || currentDuelAgencyBId || (agencies[1] ? agencies[1].id : (agencies[0] ? agencies[0].id : null));
      if (defaultA && defaultB && defaultA === defaultB && agencies.length > 1) {
        defaultB = agencies[1].id;
      }

      if (defaultA) selA.value = defaultA;
      if (defaultB) selB.value = defaultB;

      currentDuelAgencyAId = selA.value;
      currentDuelAgencyBId = selB.value;
    }

    function openAgencyDuelModal(preselectA = null, preselectB = null) {
      initAgencyDuelSelectors(preselectA, preselectB);
      renderAgencyDuelContent();
      document.getElementById('agencyDuelModal').classList.add('visible');
    }

    function closeAgencyDuelModal() {
      document.getElementById('agencyDuelModal').classList.remove('visible');
    }

    function calculateHaversineKm(lat1, lon1, lat2, lon2) {
      const r = 6371.0;
      const dlat = (lat2 - lat1) * Math.PI / 180;
      const dlon = (lon2 - lon1) * Math.PI / 180;
      const a = Math.sin(dlat / 2)**2 + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dlon / 2)**2;
      const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
      return r * c;
    }

    function renderAgencyDuelContent() {
      const selA = document.getElementById('duelSelectAgencyA');
      const selB = document.getElementById('duelSelectAgencyB');
      const container = document.getElementById('duelBodyContent');
      if (!selA || !selB || !container) return;

      currentDuelAgencyAId = selA.value;
      currentDuelAgencyBId = selB.value;

      const agA = LEAGUE_DATA.agencies.find(a => a.id === currentDuelAgencyAId);
      const agB = LEAGUE_DATA.agencies.find(a => a.id === currentDuelAgencyBId);

      if (!agA || !agB) {
        container.innerHTML = '<div style="color:var(--color-sand-300); text-align:center; padding:40px;">Veuillez sélectionner deux agences valides.</div>';
        return;
      }

      // Distance calculation
      const distKm = (agA.lat && agA.lon && agB.lat && agB.lon) 
        ? calculateHaversineKm(agA.lat, agA.lon, agB.lat, agB.lon).toFixed(2) 
        : '—';

      // Territorial Overlap calculation
      const commsA = (agA.top_communes || []).map(c => c.trim());
      const commsB = (agB.top_communes || []).map(c => c.trim());
      const sharedComms = commsA.filter(c => commsB.includes(c));
      const allCommsSet = new Set([...commsA, ...commsB]);
      const overlapPct = allCommsSet.size > 0 ? ((sharedComms.length / allCommsSet.size) * 100).toFixed(1) : 0;
      const rivalryLevel = overlapPct >= 50 ? 'EXTRÊME' : (overlapPct >= 25 ? 'FORTE' : 'MODÉRÉE');
      const rivalryColor = overlapPct >= 50 ? '#ef4444' : (overlapPct >= 25 ? '#f59e0b' : '#10b981');

      // Velocity data
      const vA = agA.velocity || {
        velocity_score: agA.velocity_score || 80,
        dsls_days: agA.dsls_days !== undefined ? agA.dsls_days : 15,
        dsls_badge_label: "Actif",
        dsls_color: "#10b981",
        momentum_label: "+0% vs T2",
        momentum_color: "#C9A24D",
        sales_t3m_count: agA.sales_t3m_count || 4,
        volume_t3m_chf_m: agA.volume_t3m_chf_m || "12.0",
        sales_per_agent_pace: agA.sales_per_agent_pace || 5.0,
        latest_sale_date_fr: "Septembre 2026"
      };

      const vB = agB.velocity || {
        velocity_score: agB.velocity_score || 80,
        dsls_days: agB.dsls_days !== undefined ? agB.dsls_days : 15,
        dsls_badge_label: "Actif",
        dsls_color: "#10b981",
        momentum_label: "+0% vs T2",
        momentum_color: "#C9A24D",
        sales_t3m_count: agB.sales_t3m_count || 4,
        volume_t3m_chf_m: agB.volume_t3m_chf_m || "12.0",
        sales_per_agent_pace: agB.sales_per_agent_pace || 5.0,
        latest_sale_date_fr: "Septembre 2026"
      };

      // Advantage helpers
      const volDiff = (agA.sold_volume_chf_m || 0) - (agB.sold_volume_chf_m || 0);
      const dealsDiff = (agA.sold_24m_count || 0) - (agB.sold_24m_count || 0);
      const scoreDiff = (agA.cytria_score || 0) - (agB.cytria_score || 0);
      const veloDiff = (vA.velocity_score || 0) - (vB.velocity_score || 0);
      const dslsAdvantage = (vA.dsls_days || 0) <= (vB.dsls_days || 0) ? 'A' : 'B';

      container.innerHTML = `
        <!-- Rivalry & Overlap Highlight Card -->
        <div style="background: rgba(8, 13, 17, 0.85); border: 1px solid var(--panel-border); padding: 16px 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
          <div style="display: flex; align-items: center; gap: 14px;">
            <div style="text-align: center; padding-right: 14px; border-right: 1px solid var(--panel-border);">
              <div style="font-size: 22px; font-weight: 800; color: ${rivalryColor}; font-family: var(--font-mono);">${overlapPct}%</div>
              <div style="font-size: 9px; color: var(--color-sand-400); text-transform: uppercase; letter-spacing: 0.05em;">Chevauchement</div>
            </div>
            <div>
              <div style="display: flex; align-items: center; gap: 8px;">
                <span class="badge-tag" style="background:${rivalryColor}22; color:${rivalryColor}; border-color:${rivalryColor}; font-size:10px; font-weight:800;">
                  Rivalité Territoriale ${rivalryLevel}
                </span>
                <span style="font-size: 11px; color: var(--color-sand-300);">
                  Distance entre sièges : <strong>${distKm} km</strong>
                </span>
              </div>
              <div style="margin-top: 6px; font-size: 11px; color: var(--color-sand-300);">
                Communes en confrontation directe (${sharedComms.length}) :
                <span style="color: var(--color-brand-300); font-weight: 600;">
                  ${sharedComms.length > 0 ? sharedComms.join(', ') : 'Aucune commune en commun (rayons disjoints)'}
                </span>
              </div>
            </div>
          </div>

          <div style="text-align: right;">
            <button type="button" class="btn-sm" onclick="projectDuelToMap()" style="padding: 7px 14px; background: rgba(6, 182, 212, 0.15); border: 1px solid #06b6d4; color: #38bdf8; font-size: 11px; font-weight: 700; cursor: pointer;">
              🗺️ Projeter les 2 Réseaux sur la Carte
            </button>
          </div>
        </div>

        <!-- Comparative Metrics Table -->
        <div style="background: var(--color-ink-950); border: 1px solid var(--panel-border); overflow-x: auto;">
          <table class="duel-kpi-table">
            <thead>
              <tr>
                <th style="text-align: right; color: #38bdf8; width: 38%; font-size: 12px;">#${agA.rank} ${agA.name}</th>
                <th style="text-align: center; color: var(--color-sand-400); width: 24%;">Métrique / Indicateur</th>
                <th style="text-align: left; color: #fbbf24; width: 38%; font-size: 12px;">#${agB.rank} ${agB.name}</th>
              </tr>
            </thead>
            <tbody>
              <!-- Score Cytria -->
              <tr>
                <td class="duel-val-a">
                  <span class="score-badge" style="background:rgba(6,182,212,0.18); border-color:#06b6d4; color:#38bdf8;">${agA.cytria_score} / 100</span>
                  ${scoreDiff > 0 ? `<span class="duel-winner-pill winner-a">+${scoreDiff} pts</span>` : ''}
                </td>
                <td class="duel-metric-name">Score Global Cytria</td>
                <td class="duel-val-b">
                  <span class="score-badge" style="background:rgba(245,158,11,0.18); border-color:#f59e0b; color:#fbbf24;">${agB.cytria_score} / 100</span>
                  ${scoreDiff < 0 ? `<span class="duel-winner-pill winner-b">+${Math.abs(scoreDiff)} pts</span>` : ''}
                </td>
              </tr>

              <!-- Velocity Score -->
              <tr>
                <td class="duel-val-a">
                  <strong>${vA.velocity_score} / 100</strong>
                  ${veloDiff > 0 ? `<span class="duel-winner-pill winner-a">+${veloDiff.toFixed(1)} pts</span>` : ''}
                </td>
                <td class="duel-metric-name">⚡ Score de Vélocité</td>
                <td class="duel-val-b">
                  <strong>${vB.velocity_score} / 100</strong>
                  ${veloDiff < 0 ? `<span class="duel-winner-pill winner-b">+${Math.abs(veloDiff).toFixed(1)} pts</span>` : ''}
                </td>
              </tr>

              <!-- DSLS (Days Since Last Sale) -->
              <tr>
                <td class="duel-val-a">
                  <span style="color:${vA.dsls_color || '#10b981'}; font-weight:700;">${vA.dsls_days} jours</span>
                  <div style="font-size:10px; color:var(--color-sand-400);">${vA.dsls_badge_label} (${vA.latest_sale_date_fr})</div>
                  ${dslsAdvantage === 'A' && vA.dsls_days !== vB.dsls_days ? `<span class="duel-winner-pill winner-a">${vB.dsls_days - vA.dsls_days}j plus récent</span>` : ''}
                </td>
                <td class="duel-metric-name">Récence Dernier Acte (DSLS)</td>
                <td class="duel-val-b">
                  <span style="color:${vB.dsls_color || '#10b981'}; font-weight:700;">${vB.dsls_days} jours</span>
                  <div style="font-size:10px; color:var(--color-sand-400);">${vB.dsls_badge_label} (${vB.latest_sale_date_fr})</div>
                  ${dslsAdvantage === 'B' && vA.dsls_days !== vB.dsls_days ? `<span class="duel-winner-pill winner-b">${vA.dsls_days - vB.dsls_days}j plus récent</span>` : ''}
                </td>
              </tr>

              <!-- Quarterly Momentum Delta -->
              <tr>
                <td class="duel-val-a">
                  <span style="color:${vA.momentum_color || '#C9A24D'};">${vA.momentum_label || '+0%'}</span>
                </td>
                <td class="duel-metric-name">Dynamisme T3M (Momentum)</td>
                <td class="duel-val-b">
                  <span style="color:${vB.momentum_color || '#C9A24D'};">${vB.momentum_label || '+0%'}</span>
                </td>
              </tr>

              <!-- Volume 24M -->
              <tr>
                <td class="duel-val-a">
                  <strong>CHF ${agA.sold_volume_chf_m} Mio</strong>
                  ${volDiff > 0 ? `<span class="duel-winner-pill winner-a">+${volDiff.toFixed(1)}M</span>` : ''}
                </td>
                <td class="duel-metric-name">Volume Notarié 24 Mois</td>
                <td class="duel-val-b">
                  <strong>CHF ${agB.sold_volume_chf_m} Mio</strong>
                  ${volDiff < 0 ? `<span class="duel-winner-pill winner-b">+${Math.abs(volDiff).toFixed(1)}M</span>` : ''}
                </td>
              </tr>

              <!-- Deals 24M -->
              <tr>
                <td class="duel-val-a">
                  <strong>${agA.sold_24m_count} ventes</strong>
                  ${dealsDiff > 0 ? `<span class="duel-winner-pill winner-a">+${dealsDiff} ventes</span>` : ''}
                </td>
                <td class="duel-metric-name">Actes Notariés Conclus</td>
                <td class="duel-val-b">
                  <strong>${agB.sold_24m_count} ventes</strong>
                  ${dealsDiff < 0 ? `<span class="duel-winner-pill winner-b">+${Math.abs(dealsDiff)} ventes</span>` : ''}
                </td>
              </tr>

              <!-- Recent 90 Days Liquid Cadence -->
              <tr>
                <td class="duel-val-a">
                  <strong>${vA.sales_t3m_count} ventes</strong> (CHF ${vA.volume_t3m_chf_m}M)
                </td>
                <td class="duel-metric-name">Flux Liquide 90 Jours</td>
                <td class="duel-val-b">
                  <strong>${vB.sales_t3m_count} ventes</strong> (CHF ${vB.volume_t3m_chf_m}M)
                </td>
              </tr>

              <!-- Sales per Broker Pace -->
              <tr>
                <td class="duel-val-a">
                  <strong>${vA.sales_per_agent_pace} / an</strong>
                  <div style="font-size:10px; color:var(--color-sand-400);">${(agA.agents||[]).length} courtier(s) déclarés</div>
                </td>
                <td class="duel-metric-name">Débit Négociateurs (v/an/ag)</td>
                <td class="duel-val-b">
                  <strong>${vB.sales_per_agent_pace} / an</strong>
                  <div style="font-size:10px; color:var(--color-sand-400);">${(agB.agents||[]).length} courtier(s) déclarés</div>
                </td>
              </tr>

              <!-- Ticket Median -->
              <tr>
                <td class="duel-val-a">
                  <strong>CHF ${(agA.median_price_chf/1e6).toFixed(2)}M</strong>
                </td>
                <td class="duel-metric-name">Ticket Médian Transaction</td>
                <td class="duel-val-b">
                  <strong>CHF ${(agB.median_price_chf/1e6).toFixed(2)}M</strong>
                </td>
              </tr>

              <!-- Median House & PPE -->
              <tr>
                <td class="duel-val-a">
                  <div>Villas: <strong>CHF ${(agA.median_house_chf/1e6).toFixed(2)}M</strong></div>
                  <div style="font-size:11px; color:var(--color-sand-400);">PPE: CHF ${(agA.median_apartment_chf/1e6).toFixed(2)}M</div>
                </td>
                <td class="duel-metric-name">Prix Médian par Typologie</td>
                <td class="duel-val-b">
                  <div>Villas: <strong>CHF ${(agB.median_house_chf/1e6).toFixed(2)}M</strong></div>
                  <div style="font-size:11px; color:var(--color-sand-400);">PPE: CHF ${(agB.median_apartment_chf/1e6).toFixed(2)}M</div>
                </td>
              </tr>

              <!-- Discount Rate -->
              <tr>
                <td class="duel-val-a">
                  <span style="color:#10b981; font-weight:700;">-${agA.discount_rate_est}%</span>
                </td>
                <td class="duel-metric-name">Décote Moyenne Constatée</td>
                <td class="duel-val-b">
                  <span style="color:#10b981; font-weight:700;">-${agB.discount_rate_est}%</span>
                </td>
              </tr>

              <!-- Client Rating -->
              <tr>
                <td class="duel-val-a">
                  <strong>${agA.rating} / 5.0</strong> (${agA.reviews_count} avis)
                </td>
                <td class="duel-metric-name">Satisfaction Clientèle</td>
                <td class="duel-val-b">
                  <strong>${agB.rating} / 5.0</strong> (${agB.reviews_count} avis)
                </td>
              </tr>

              <!-- Primary Territory -->
              <tr>
                <td class="duel-val-a">
                  <div>${agA.primary_territory}</div>
                  <div style="font-size:10px; color:var(--color-sand-400);">Siège: ${agA.headquarters_commune} (~${(agA.radius_meters/1000).toFixed(1)} km)</div>
                </td>
                <td class="duel-metric-name">Territoire Principal & Rayon</td>
                <td class="duel-val-b">
                  <div>${agB.primary_territory}</div>
                  <div style="font-size:10px; color:var(--color-sand-400);">Siège: ${agB.headquarters_commune} (~${(agB.radius_meters/1000).toFixed(1)} km)</div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      `;
    }

    function projectDuelToMap() {
      closeAgencyDuelModal();
      renderAgencyDuelOnMap(currentDuelAgencyAId, currentDuelAgencyBId);
    }

    function renderAgencyDuelOnMap(agencyAId, agencyBId) {
      if (!LEAGUE_DATA.agencies) return;
      const agA = LEAGUE_DATA.agencies.find(a => a.id === agencyAId);
      const agB = LEAGUE_DATA.agencies.find(a => a.id === agencyBId);
      if (!agA || !agB) return;

      switchProductSuite('AGENCY_BI');
      isDuelMapActive = true;

      // Clear layers
      agencyMarkersGroup.clearLayers();
      agencyRadiusGroup.clearLayers();
      markersCluster.clearLayers();
      territoryMarketLayers = [];
      isShowingTerritoryMarket = false;

      const bounds = L.latLngBounds();

      // Render Agency A HQ (Cyan)
      if (agA.lat && agA.lon) {
        bounds.extend([agA.lat, agA.lon]);
        const iconA = L.divIcon({
          className: 'custom-agency-div',
          html: `
            <div class="agency-marker-pin duel-a" id="pin-${agA.id}">
              <div class="pin-badge" style="background:#06b6d4 !important; color:#080d11 !important;">#${agA.rank} A</div>
              <div class="pin-name" style="color:#e0f2fe;">${formatAgencyBrand(agA.name)}</div>
            </div>
          `,
          iconSize: null,
          iconAnchor: [60, 14]
        });
        const mA = L.marker([agA.lat, agA.lon], { icon: iconA, zIndexOffset: 2000 }).addTo(agencyMarkersGroup);
        mA.on('click', () => openAgencyDuelModal(agA.id, agB.id));

        // Radius circle A (Cyan)
        L.circle([agA.lat, agA.lon], {
          radius: agA.radius_meters || 5000,
          color: '#06b6d4',
          weight: 2,
          dashArray: '6, 6',
          fillColor: '#06b6d4',
          fillOpacity: 0.08
        }).addTo(agencyRadiusGroup);
      }

      // Render Agency B HQ (Amber/Gold)
      if (agB.lat && agB.lon) {
        bounds.extend([agB.lat, agB.lon]);
        const iconB = L.divIcon({
          className: 'custom-agency-div',
          html: `
            <div class="agency-marker-pin duel-b" id="pin-${agB.id}">
              <div class="pin-badge" style="background:#f59e0b !important; color:#080d11 !important;">#${agB.rank} B</div>
              <div class="pin-name" style="color:#fef3c7;">${formatAgencyBrand(agB.name)}</div>
            </div>
          `,
          iconSize: null,
          iconAnchor: [60, 14]
        });
        const mB = L.marker([agB.lat, agB.lon], { icon: iconB, zIndexOffset: 2000 }).addTo(agencyMarkersGroup);
        mB.on('click', () => openAgencyDuelModal(agA.id, agB.id));

        // Radius circle B (Amber/Gold)
        L.circle([agB.lat, agB.lon], {
          radius: agB.radius_meters || 5000,
          color: '#f59e0b',
          weight: 2,
          dashArray: '6, 6',
          fillColor: '#f59e0b',
          fillOpacity: 0.08
        }).addTo(agencyRadiusGroup);
      }

      // Sold properties for Agency A (Cyan dots)
      const markers = [];
      (agA.sold_properties || []).forEach(p => {
        if (!p.lat || !p.lon) return;
        bounds.extend([p.lat, p.lon]);
        const markerA = L.circleMarker([p.lat, p.lon], {
          radius: 7.5,
          fillColor: '#06b6d4',
          color: '#080d11',
          weight: 2,
          opacity: 1,
          fillOpacity: 0.95
        });
        markerA.bindTooltip(`
          <div style="font-family:'Hanken Grotesk',sans-serif; padding:4px;">
            <div style="color:#06b6d4; font-weight:700; font-size:10px;">[AGENCE A] ${agA.name}</div>
            <div style="color:#fff; font-size:11px; font-weight:600;">${p.typology} — ${p.address}</div>
            <div style="color:#38bdf8; font-weight:700; font-size:12px;">CHF ${p.price_chf ? Math.round(p.price_chf).toLocaleString('fr-CH') : 'Prix confidentiel'}</div>
          </div>
        `, { direction: 'top' });
        markers.push(markerA);
      });

      // Sold properties for Agency B (Amber dots)
      (agB.sold_properties || []).forEach(p => {
        if (!p.lat || !p.lon) return;
        bounds.extend([p.lat, p.lon]);
        const markerB = L.circleMarker([p.lat, p.lon], {
          radius: 7.5,
          fillColor: '#f59e0b',
          color: '#080d11',
          weight: 2,
          opacity: 1,
          fillOpacity: 0.95
        });
        markerB.bindTooltip(`
          <div style="font-family:'Hanken Grotesk',sans-serif; padding:4px;">
            <div style="color:#f59e0b; font-weight:700; font-size:10px;">[AGENCE B] ${agB.name}</div>
            <div style="color:#fff; font-size:11px; font-weight:600;">${p.typology} — ${p.address}</div>
            <div style="color:#fbbf24; font-weight:700; font-size:12px;">CHF ${p.price_chf ? Math.round(p.price_chf).toLocaleString('fr-CH') : 'Prix confidentiel'}</div>
          </div>
        `, { direction: 'top' });
        markers.push(markerB);
      });

      markersCluster.addLayers(markers);

      if (bounds.isValid()) {
        map.fitBounds(bounds, { padding: [50, 50], maxZoom: 14 });
      }

      // Show floating duel banner
      const banner = document.getElementById('agencyDuelBanner');
      if (banner) {
        banner.style.display = 'flex';
        document.getElementById('duelBannerTitle').innerHTML = `
          <span style="color:#38bdf8; font-weight:700;">${formatAgencyBrand(agA.name)}</span>
          <span style="color:var(--color-sand-400); margin:0 4px;">VS</span>
          <span style="color:#fbbf24; font-weight:700;">${formatAgencyBrand(agB.name)}</span>
        `;
        document.getElementById('duelBannerMeta').innerHTML = `
          ${(agA.sold_properties||[]).length} ventes (A) &bull; ${(agB.sold_properties||[]).length} ventes (B)
        `;
      }

      // Hide normal focus banner
      const normBanner = document.getElementById('agencyFocusBanner');
      if (normBanner) normBanner.style.display = 'none';
    }

    function resetAgencyDuelMap() {
      isDuelMapActive = false;
      const banner = document.getElementById('agencyDuelBanner');
      if (banner) banner.style.display = 'none';
      renderAgenciesOnMap(null);
    }

    const duelModalEl = document.getElementById('agencyDuelModal');
    if (duelModalEl) {
      duelModalEl.addEventListener('click', (e) => {
        if (e.target.id === 'agencyDuelModal') {
          closeAgencyDuelModal();
        }
      });
    }

    // ==========================================
    // MARKETING BENCHMARK & INTELLIGENCE LOGIC
    // ==========================================
    function openMarketingModal() {"""

if JS_TARGET in content:
    content = content.replace(JS_TARGET, JS_REPLACEMENT, 1)
    print("[OK] JS functions injected.")
else:
    print("[!] JS_TARGET not found.")

# 7. Inject Deep-linking support in handleExternalRouting
ROUTING_TARGET = """      } else if (target === 'agences' || target === 'benchmark' || target === 'parts-de-marche' || target === 'bi') {
        switchProductSuite('AGENCY_BI');
        openLeagueModal();
      } else if (target === 'sourcing') {"""

ROUTING_REPLACEMENT = """      } else if (target === 'agences' || target === 'benchmark' || target === 'parts-de-marche' || target === 'bi') {
        switchProductSuite('AGENCY_BI');
        openLeagueModal();
      } else if (target === 'duel' || target === 'face-a-face' || target === 'comparateur') {
        switchProductSuite('AGENCY_BI');
        const agA = params.get('a');
        const agB = params.get('b');
        openAgencyDuelModal(agA, agB);
      } else if (target === 'sourcing') {"""

if ROUTING_TARGET in content:
    content = content.replace(ROUTING_TARGET, ROUTING_REPLACEMENT, 1)
    print("[OK] Routing injected.")
else:
    print("[!] ROUTING_TARGET not found.")

MAP_BUILDER.write_text(content, encoding="utf-8")
print("[OK] map_builder.py saved successfully!")
