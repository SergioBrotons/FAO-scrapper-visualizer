"""Standalone interactive HTML map generator for Geneva Property Transactions with Cytria Brand Design, Smart Street View Detection, and 3-Phase Intelligence Enrichment."""

import json
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional

from rich.console import Console

from fao_transactions.config import settings

console = Console()


HTML_TEMPLATE = """<!DOCTYPE html>
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
    :root {
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
      --color-muted-ink: #6B7280;

      --font-brand: 'Hanken Grotesk', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      --font-body: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;

      --panel-bg: rgba(16, 20, 27, 0.94);
      --panel-border: rgba(255, 255, 255, 0.08);
      --panel-border-gold: rgba(201, 162, 77, 0.35);
      
      --radius-strict: 0px;
      --shadow-elevation: 0 20px 40px -10px rgba(0, 0, 0, 0.7);
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      border-radius: var(--radius-strict) !important;
    }

    body, html {
      height: 100%;
      width: 100%;
      font-family: var(--font-body);
      background-color: var(--color-ink-950);
      color: var(--color-paper);
      overflow: hidden;
      -webkit-font-smoothing: antialiased;
    }

    #map {
      height: 100%;
      width: 100%;
      background: var(--color-ink-950);
      z-index: 1;
    }

    /* Top Bar HUD */
    .top-bar {
      position: absolute;
      top: 16px;
      left: 16px;
      right: 16px;
      z-index: 1000;
      display: flex;
      justify-content: space-between;
      align-items: center;
      pointer-events: none;
    }

    .hud-card {
      background: var(--panel-bg);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid var(--panel-border);
      padding: 12px 20px;
      display: flex;
      align-items: center;
      gap: 20px;
      pointer-events: auto;
      box-shadow: var(--shadow-elevation);
    }

    .brand-group {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .cytria-logo-svg {
      height: 24px;
      width: auto;
      display: block;
    }

    .brand-divider {
      width: 1px;
      height: 24px;
      background: var(--panel-border);
    }

    .brand-meta {
      display: flex;
      flex-direction: column;
    }

    .brand-meta-title {
      font-family: var(--font-brand);
      font-size: 13px;
      font-weight: 700;
      letter-spacing: -0.01em;
      color: var(--color-paper);
      text-transform: uppercase;
    }

    .brand-meta-sub {
      font-size: 10px;
      font-weight: 500;
      letter-spacing: 0.08em;
      color: var(--color-brand-400);
      text-transform: uppercase;
    }

    .badge-fao {
      background: var(--color-ink-800);
      border: 1px solid var(--panel-border-gold);
      color: var(--color-brand-300);
      font-family: var(--font-mono);
      font-size: 10px;
      font-weight: 600;
      padding: 3px 7px;
      letter-spacing: 0.05em;
    }

    .hud-stats {
      display: flex;
      align-items: center;
      gap: 18px;
      border-left: 1px solid var(--panel-border);
      padding-left: 18px;
    }

    .stat-item {
      display: flex;
      flex-direction: column;
      gap: 2px;
    }

    .stat-label {
      font-size: 9px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--color-sand-300);
      font-weight: 600;
    }

    .stat-value {
      font-family: var(--font-mono);
      font-size: 14px;
      font-weight: 700;
      color: var(--color-paper);
    }

    .stat-value.gold { color: var(--color-brand-400); }
    .stat-value.emerald { color: #4ade80; }
    .stat-value.purple { color: #c084fc; }

    /* Left Sidebar Filter Panel */
    .sidebar {
      position: absolute;
      top: 80px;
      left: 16px;
      bottom: 24px;
      width: 340px;
      background: var(--panel-bg);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid var(--panel-border);
      z-index: 1000;
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      box-shadow: var(--shadow-elevation);
      overflow-y: auto;
    }

    .search-box {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .search-input {
      width: 100%;
      background: var(--color-ink-900);
      border: 1px solid var(--panel-border);
      padding: 10px 14px;
      color: var(--color-paper);
      font-family: var(--font-body);
      font-size: 12px;
      outline: none;
      transition: all 0.2s ease;
    }

    .search-input:focus {
      border-color: var(--color-brand-400);
      box-shadow: 0 0 0 1px var(--color-brand-400);
    }

    .filter-section-title {
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--color-brand-400);
      margin-bottom: 6px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .pills-grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 4px;
    }

    .pill-btn {
      background: var(--color-ink-900);
      border: 1px solid var(--panel-border);
      color: var(--color-sand-300);
      padding: 8px 12px;
      font-size: 11px;
      font-weight: 500;
      cursor: pointer;
      text-align: left;
      transition: all 0.15s ease;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .pill-btn:hover {
      background: var(--color-ink-800);
      color: var(--color-paper);
      border-color: rgba(255, 255, 255, 0.2);
    }

    .pill-btn.active {
      background: rgba(201, 162, 77, 0.15);
      border-color: var(--color-brand-500);
      color: var(--color-brand-300);
      font-weight: 700;
    }

    .filter-grid-2 {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }

    .select-input {
      width: 100%;
      background: var(--color-ink-900);
      border: 1px solid var(--panel-border);
      color: var(--color-paper);
      padding: 8px 10px;
      font-size: 11px;
      font-family: var(--font-body);
      outline: none;
      cursor: pointer;
    }

    .select-input:focus {
      border-color: var(--color-brand-400);
    }

    .toggle-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 8px 10px;
      background: var(--color-ink-900);
      border: 1px solid var(--panel-border);
      font-size: 11px;
      color: var(--color-sand-300);
      cursor: pointer;
      margin-bottom: 4px;
    }

    .toggle-row:hover {
      border-color: rgba(255, 255, 255, 0.2);
    }

    .toggle-row input {
      accent-color: var(--color-brand-500);
      cursor: pointer;
    }

    .reset-btn {
      background: transparent;
      border: 1px solid var(--panel-border);
      color: var(--color-sand-300);
      padding: 9px;
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      cursor: pointer;
      transition: all 0.2s ease;
      margin-top: auto;
    }

    .reset-btn:hover {
      background: var(--color-ink-800);
      color: var(--color-paper);
      border-color: var(--color-brand-400);
    }

    .legend {
      background: var(--color-ink-900);
      border: 1px solid var(--panel-border);
      padding: 10px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      font-size: 10px;
    }

    .legend-item {
      display: flex;
      align-items: center;
      gap: 8px;
      color: var(--color-sand-300);
    }

    .legend-dot {
      width: 10px;
      height: 10px;
    }

    /* Right Detail Drawer */
    .detail-drawer {
      position: absolute;
      top: 80px;
      right: 16px;
      bottom: 24px;
      width: 420px;
      background: var(--panel-bg);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 1px solid var(--panel-border-gold);
      z-index: 1000;
      padding: 24px;
      box-shadow: var(--shadow-elevation);
      overflow-y: auto;
      display: none;
      flex-direction: column;
      gap: 16px;
    }

    .detail-drawer.visible {
      display: flex;
      animation: slideIn 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }

    @keyframes slideIn {
      from { opacity: 0; transform: translateX(20px); }
      to { opacity: 1; transform: translateX(0); }
    }

    .detail-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      padding-bottom: 14px;
    }

    .detail-close {
      background: transparent;
      border: 1px solid var(--panel-border);
      color: var(--color-sand-300);
      width: 28px;
      height: 28px;
      cursor: pointer;
      font-weight: 700;
      font-size: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s ease;
    }

    .detail-close:hover {
      border-color: var(--color-brand-400);
      color: var(--color-paper);
    }

    .detail-price {
      font-family: var(--font-mono);
      font-size: 26px;
      font-weight: 700;
      color: var(--color-brand-400);
      letter-spacing: -0.02em;
    }

    .detail-badges {
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
    }

    .badge-tag {
      font-size: 10px;
      font-weight: 700;
      padding: 4px 8px;
      background: var(--color-ink-800);
      border: 1px solid var(--panel-border);
      color: var(--color-paper);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .badge-tag.plq {
      background: rgba(138, 79, 125, 0.25);
      color: #d896c8;
      border-color: rgba(138, 79, 125, 0.5);
    }

    .badge-tag.zonedev {
      background: rgba(201, 162, 77, 0.2);
      color: var(--color-brand-300);
      border-color: var(--panel-border-gold);
    }

    .badge-tag.permit {
      background: rgba(47, 107, 87, 0.3);
      color: #6ee7b7;
      border-color: rgba(47, 107, 87, 0.6);
    }

    .badge-tag.grandprojet {
      background: rgba(49, 94, 120, 0.3);
      color: #7dd3fc;
      border-color: rgba(49, 94, 120, 0.5);
    }

    /* Action Toolbar (Street View & SITG) */
    .action-toolbar {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }

    .action-btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      padding: 11px 12px;
      font-family: var(--font-brand);
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      text-decoration: none;
      transition: all 0.2s ease;
      cursor: pointer;
    }

    .action-btn.streetview {
      background: var(--color-ink-900);
      border: 1px solid var(--panel-border-gold);
      color: var(--color-brand-300);
    }
    .action-btn.streetview:hover {
      background: rgba(201, 162, 77, 0.15);
      border-color: var(--color-brand-500);
      color: var(--color-paper);
    }

    .action-btn.satellite {
      background: var(--color-ink-900);
      border: 1px solid #315E78;
      color: #7dd3fc;
    }
    .action-btn.satellite:hover {
      background: rgba(49, 94, 120, 0.25);
      border-color: #38bdf8;
      color: #ffffff;
    }

    .action-btn.streetview.disabled {
      background: var(--color-ink-950);
      border: 1px dashed rgba(255, 255, 255, 0.15);
      color: var(--color-muted-ink);
      cursor: not-allowed;
      opacity: 0.7;
      grid-column: 1 / -1;
      justify-content: center;
      padding: 8px 12px;
      font-size: 10px;
    }

    .action-btn.sitg {
      background: var(--color-brand-500);
      border: 1px solid var(--color-brand-500);
      color: var(--color-ink-950);
      box-shadow: 0 4px 14px rgba(201, 162, 77, 0.25);
    }
    .action-btn.sitg:hover {
      background: var(--color-brand-400);
      box-shadow: 0 6px 20px rgba(201, 162, 77, 0.4);
    }

    /* Intelligence Section */
    .intel-section {
      background: var(--color-ink-900);
      border: 1px solid var(--panel-border);
      padding: 14px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .intel-title {
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--color-brand-400);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .intel-link {
      color: var(--color-brand-300);
      text-decoration: underline;
      font-size: 10px;
      font-family: var(--font-brand);
      font-weight: 600;
    }

    .detail-grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 10px;
      background: var(--color-ink-900);
      border: 1px solid var(--panel-border);
      padding: 14px;
    }

    .detail-row {
      display: flex;
      flex-direction: column;
      gap: 2px;
      font-size: 13px;
    }

    .detail-row .row-label {
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--color-sand-300);
      font-weight: 600;
    }

    .detail-row .row-value {
      font-weight: 500;
      color: var(--color-paper);
    }

    .detail-row .row-value.mono {
      font-family: var(--font-mono);
      color: var(--color-brand-200);
    }

    /* Street View In-App Modal */
    .modal-overlay {
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
    }

    .modal-overlay.visible {
      display: flex;
      animation: modalFadeIn 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }

    @keyframes modalFadeIn {
      from { opacity: 0; transform: scale(0.98); }
      to { opacity: 1; transform: scale(1); }
    }

    .modal-window {
      width: 100%;
      max-width: 1080px;
      height: 84vh;
      background: var(--color-night);
      border: 1px solid var(--panel-border-gold);
      display: flex;
      flex-direction: column;
      box-shadow: 0 30px 60px -15px rgba(0, 0, 0, 0.95);
      overflow: hidden;
    }

    .modal-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 20px;
      background: var(--color-ink-900);
      border-bottom: 1px solid var(--panel-border);
      flex-wrap: wrap;
      gap: 12px;
    }

    .modal-header-left {
      display: flex;
      align-items: center;
      gap: 14px;
      flex-wrap: wrap;
    }

    .modal-title-box {
      display: flex;
      flex-direction: column;
      gap: 2px;
    }

    .modal-title {
      font-size: 13px;
      font-weight: 700;
      color: var(--color-paper);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }

    .modal-subtitle {
      font-size: 10px;
      font-weight: 600;
      color: var(--color-brand-400);
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    .modal-mode-tabs {
      display: flex;
      gap: 6px;
      background: var(--color-ink-950);
      border: 1px solid var(--panel-border);
      padding: 3px;
    }

    .modal-tab-btn {
      background: transparent;
      border: 1px solid transparent;
      color: var(--color-sand-300);
      font-family: var(--font-brand);
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      padding: 5px 10px;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .modal-tab-btn:hover {
      color: var(--color-paper);
    }

    .modal-tab-btn.active {
      background: var(--color-brand-500);
      color: var(--color-ink-950);
      font-weight: 700;
    }

    .modal-header-actions {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .modal-ext-link {
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
    }

    .modal-ext-link:hover {
      border-color: var(--color-brand-400);
      color: var(--color-paper);
    }

    .modal-close-btn {
      background: transparent;
      border: 1px solid var(--panel-border);
      color: var(--color-sand-300);
      width: 30px;
      height: 30px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      font-size: 18px;
      font-weight: 700;
      transition: all 0.2s ease;
    }

    .modal-close-btn:hover {
      border-color: var(--color-brand-400);
      color: var(--color-paper);
    }

    .modal-hint-bar {
      padding: 6px 20px;
      background: var(--color-ink-950);
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
      font-size: 11px;
      color: var(--color-sand-300);
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .modal-hint-bar strong {
      color: var(--color-brand-300);
    }

    .modal-body {
      flex: 1;
      width: 100%;
      height: 100%;
      position: relative;
      background: var(--color-ink-950);
    }

    .modal-iframe {
      width: 100%;
      height: 100%;
      border: none;
    }

    /* Custom Leaflet Cluster Styling */
    .marker-cluster-small, .marker-cluster-medium, .marker-cluster-large {
      background-color: rgba(16, 20, 27, 0.85) !important;
      backdrop-filter: blur(8px);
      border: 2px solid var(--color-brand-500) !important;
    }
    .marker-cluster div {
      background-color: transparent !important;
      color: var(--color-paper) !important;
      font-weight: 700 !important;
      font-size: 12px !important;
      font-family: var(--font-mono) !important;
    }

    /* Leaflet Controls Styling */
    .leaflet-control-layers {
      background: var(--panel-bg) !important;
      border: 1px solid var(--panel-border) !important;
      color: var(--color-paper) !important;
      font-family: var(--font-brand) !important;
      font-size: 12px !important;
      box-shadow: var(--shadow-elevation) !important;
    }
    .leaflet-control-zoom a {
      background: var(--panel-bg) !important;
      color: var(--color-paper) !important;
      border: 1px solid var(--panel-border) !important;
    }
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
          <span class="stat-value" id="stat-count">__TOTAL_ROWS__</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Volume Déclaré</span>
          <span class="stat-value emerald">CHF __TOTAL_VOLUME__ Mrd</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Avec Prix Publié</span>
          <span class="stat-value gold">__PRICED_COUNT__</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">PLQ Actifs</span>
          <span class="stat-value purple">__PLQ_COUNT__</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Zone Dév. (LGZD)</span>
          <span class="stat-value gold">__DEV_COUNT__</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Permis / Projets</span>
          <span class="stat-value emerald">__PERMIT_COUNT__</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Sidebar Filter Panel -->
  <aside class="sidebar">
    <div class="search-box">
      <input type="text" id="searchInput" class="search-input" placeholder="Recherche adresse, acquéreur, aliénateur, PLQ...">
    </div>

    <div>
      <div class="filter-section-title">Source Juridique</div>
      <div class="pills-grid">
        <button class="pill-btn active" data-source="ALL">Toutes (__TOTAL_ROWS__)</button>
        <button class="pill-btn" data-source="LDTR_Appartement">Appartements LDTR</button>
        <button class="pill-btn" data-source="Registre_Foncier">Registre Foncier</button>
      </div>
    </div>

    <div class="filter-grid-2">
      <div>
        <div class="filter-section-title">Commune</div>
        <select class="select-input" id="communeSelect">
          <option value="ALL">Toutes les communes</option>
        </select>
      </div>
      <div>
        <div class="filter-section-title">Zone d'Affectation</div>
        <select class="select-input" id="zoneSelect">
          <option value="ALL">Toutes les zones</option>
        </select>
      </div>
    </div>

    <div>
      <div class="filter-section-title">Filtres Stratégiques & Urbanisme</div>
      <label class="toggle-row">
        <span>⚡ Avec PLQ (Plan Localisé de Quartier)</span>
        <input type="checkbox" id="onlyPlqCheckbox">
      </label>
      <label class="toggle-row">
        <span>🏗️ En Zone de Développement (LGZD)</span>
        <input type="checkbox" id="onlyDevCheckbox">
      </label>
      <label class="toggle-row">
        <span>📋 Avec Permis / Projet Bâtiment</span>
        <input type="checkbox" id="onlyPermitCheckbox">
      </label>
    </div>

    <div class="filter-grid-2">
      <div>
        <div class="filter-section-title">Époque Construction</div>
        <select class="select-input" id="buildingSelect">
          <option value="ALL">Toutes époques de construction</option>
          <option value="avant 1919">Bâtiments historiques (Avant 1919)</option>
          <option value="1919">1919 à 1960</option>
          <option value="1961">1961 à 1990</option>
          <option value="1991">1991 à 2015</option>
          <option value="2016">Récent (2016 à aujourd'hui)</option>
        </select>
      </div>
      <div>
        <div class="filter-section-title">Prix Publié</div>
        <label class="toggle-row" style="margin-top: 4px;">
          <span>Uniquement avec prix</span>
          <input type="checkbox" id="onlyPricedCheckbox">
        </label>
      </div>
    </div>

    <button class="reset-btn" id="resetBtn">Réinitialiser les filtres</button>

    <div class="legend">
      <div class="filter-section-title">Légende des marqueurs</div>
      <div class="legend-item"><div class="legend-dot" style="background:#C9A24D;"></div> Prix ≥ CHF 3M (Gold)</div>
      <div class="legend-item"><div class="legend-dot" style="background:#315E78;"></div> Appartement LDTR</div>
      <div class="legend-item"><div class="legend-dot" style="background:#8A4F7D;"></div> PLQ / Zone de Développement</div>
      <div class="legend-item"><div class="legend-dot" style="background:#A46D13;"></div> Zone 5 (Villas & Terrains)</div>
      <div class="legend-item"><div class="legend-dot" style="background:#2F6B57;"></div> Registre Foncier (Autre)</div>
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

  <!-- In-App Street View & Aerial Multi-Mode Modal -->
  <div class="modal-overlay" id="streetViewModal">
    <div class="modal-window">
      <div class="modal-header">
        <div class="modal-header-left">
          <div class="modal-title-box">
            <div class="modal-title" id="modalTitle">Inspection Visuelle</div>
            <div class="modal-subtitle">Panorama Street View &bull; Cytria Intelligence</div>
          </div>
          <div class="modal-mode-tabs">
            <button type="button" class="modal-tab-btn active" id="tabPano" onclick="setModalMode('pano')">📸 360° Street View</button>
            <button type="button" class="modal-tab-btn" id="tabSat" onclick="setModalMode('sat')">🛰️ Satellite HD</button>
            <button type="button" class="modal-tab-btn" id="tabSitg" onclick="setModalMode('sitg')">🇨🇭 Cadastre SITG</button>
          </div>
        </div>
        <div class="modal-header-actions">
          <a href="#" id="modalExtLink" target="_blank" rel="noopener" class="modal-ext-link">
            Ouvrir dans Google Maps ↗
          </a>
          <button class="modal-close-btn" id="modalCloseBtn">&times;</button>
        </div>
      </div>
      <div class="modal-hint-bar" id="modalHintBar">
        <span>💡</span>
        <span id="modalHintText">Google Street View 360° • Vue panoramique au niveau de la voie publique</span>
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
    const DATA = __RECORDS_JSON__;
    const COMMUNES = __COMMUNES_JSON__;
    const ZONES = __ZONES_JSON__;

    // Helper: Determine if Street View coverage is available upfront
    function hasStreetViewCoverage(r) {
      if (!r || !r.lat || !r.lon) return false;
      if (!r.address) return false;
      const addr = r.address.toLowerCase().trim();
      if (addr.startsWith('parcelle') || addr.startsWith('terrain') || addr.startsWith('champ') || addr === '-' || addr.includes('inconnu') || addr.includes('non spécifiée') || addr.includes('non bâti')) {
        return false;
      }
      if ((r.zone_code === '6' || r.zone_code === '6A' || r.zone_code === 'F') && !r.building_destination && !r.permit_number) {
        return false;
      }
      return true;
    }

    // Populate selects
    const communeSelect = document.getElementById('communeSelect');
    COMMUNES.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c;
      opt.textContent = c;
      communeSelect.appendChild(opt);
    });

    const zoneSelect = document.getElementById('zoneSelect');
    ZONES.forEach(z => {
      const opt = document.createElement('option');
      opt.value = z;
      opt.textContent = 'Zone ' + z;
      zoneSelect.appendChild(opt);
    });

    // Initialize Map with Swisstopo & Esri basemaps
    const map = leafletMap();

    function leafletMap() {
      const m = L.map('map', {
        center: [46.2044, 6.1432], // Geneva center
        zoom: 12,
        minZoom: 10,
        maxZoom: 19,
        zoomControl: false
      });

      L.control.zoom({ position: 'bottomright' }).addTo(m);

      const darkTiles = L.layerGroup([
        L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
          attribution: '&copy; Esri &mdash; Esri, DeLorme, NAVTEQ',
          maxZoom: 16
        }),
        L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}', {
          maxZoom: 16
        })
      ]).addTo(m);

      const swissGrey = L.tileLayer('https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.pixelkarte-grau/default/current/3857/{z}/{x}/{y}.jpeg', {
        attribution: '&copy; swisstopo',
        maxZoom: 19
      });

      const swissImage = L.tileLayer('https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.swissimage/default/current/3857/{z}/{x}/{y}.jpeg', {
        attribution: '&copy; swisstopo',
        maxZoom: 19
      });

      const osmStandard = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        maxZoom: 19
      });

      const baseMaps = {
        "🌙 Cytria Night (Esri Canvas)": darkTiles,
        "🇨🇭 Swisstopo Plan Gris": swissGrey,
        "🛰️ Swisstopo Orthophoto": swissImage,
        "🗺️ OpenStreetMap": osmStandard
      };

      L.control.layers(baseMaps, null, { position: 'topright' }).addTo(m);

      return m;
    }

    let markersCluster = L.markerClusterGroup({
      chunkedLoading: true,
      maxClusterRadius: 40,
      spiderfyOnMaxZoom: true,
      showCoverageOnHover: false
    });
    map.addLayer(markersCluster);

    function getMarkerColor(r) {
      if (r.price_chf && r.price_chf >= 3000000) return '#C9A24D'; // Gold
      if (r.source_category === 'LDTR_Appartement') return '#315E78'; // Cyan-Blue
      if (r.plq_number || r.zone_dev_name) return '#8A4F7D'; // Purple
      if (r.zone_code === '5') return '#A46D13'; // Ochre
      return '#2F6B57'; // Forest green
    }

    function createMarkers(records) {
      markersCluster.clearLayers();
      const markers = [];

      records.forEach(r => {
        if (!r.lat || !r.lon) return;

        const color = getMarkerColor(r);
        const radius = (r.price_chf && r.price_chf > 5000000) ? 8 : 6;

        const marker = L.circleMarker([r.lat, r.lon], {
          radius: radius,
          fillColor: color,
          color: '#F7F4EC',
          weight: 1.2,
          opacity: 0.9,
          fillOpacity: 0.85
        });

        marker.on('click', () => openDetail(r));
        markers.push(marker);
      });

      markersCluster.addLayers(markers);
      document.getElementById('stat-count').textContent = records.length.toLocaleString('fr-CH');
    }

    // Initial render
    createMarkers(DATA);

    // Detail Drawer
    const detailDrawer = document.getElementById('detailDrawer');
    const detailContent = document.getElementById('detailContent');
    const detailPriceDisplay = document.getElementById('detailPriceDisplay');

    document.getElementById('detailClose').addEventListener('click', () => {
      detailDrawer.classList.remove('visible');
    });

    function openDetail(r) {
      detailPriceDisplay.innerHTML = r.price_chf 
        ? 'CHF ' + Math.round(r.price_chf).toLocaleString('fr-CH') 
        : '<span style="color:#A8A29A; font-size:15px; font-weight:500;">Prix non publié (Mutation RF)</span>';

      const sitgLink = (r.lv95_e && r.lv95_n) 
        ? (r.sitg_aerial_url || `https://map.sitg.ge.ch/?center=${r.lv95_e},${r.lv95_n}&scale=1000&mapresources=CADASTRE,ORTHOPHOTO_2023`)
        : null;

      const streetViewLink = (r.lat && r.lon)
        ? (r.streetview_url || `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${r.lat},${r.lon}`)
        : null;

      const isStreetAvailable = hasStreetViewCoverage(r);
      const displayTitle = r.address || (r.commune + ' (Parcelle ' + (r.parcel_number || 'N/A') + ')');

      detailContent.innerHTML = `
        <div class="detail-badges">
          <span class="badge-tag">${r.source_category === 'LDTR_Appartement' ? 'Vente Appartement (LDTR)' : 'Registre Foncier'}</span>
          ${r.zone_code ? `<span class="badge-tag zone">${r.zone_name || ('Zone ' + r.zone_code)}</span>` : ''}
          ${r.plq_number ? `<span class="badge-tag plq">PLQ #${r.plq_number}</span>` : ''}
          ${r.zone_dev_name ? `<span class="badge-tag zonedev">${r.zone_dev_code || 'Zone Dév.'}</span>` : ''}
          ${r.permit_number ? `<span class="badge-tag permit">${r.permit_number}</span>` : ''}
          ${r.grand_projet_name ? `<span class="badge-tag grandprojet">${r.grand_projet_name}</span>` : ''}
        </div>

        <!-- Action Toolbar (Street View Modal, Satellite Fallback & SITG) -->
        <div class="action-toolbar">
          ${isStreetAvailable ? `
          <button type="button" id="btnStreetViewAction" class="action-btn streetview" title="Ouvrir la vue 360° Street View au sol">
            Street View 360° ⛶
          </button>` : `
          <button type="button" id="btnSatelliteAction" class="action-btn satellite" title="Ouvrir la vue Satellite HD aérienne de la parcelle">
            🛰️ Satellite HD ⛶
          </button>
          <div class="action-btn streetview disabled" title="Street View indisponible pour cette parcelle (terrain agricole, forêt, cour intérieure ou voie privée)">
            Street View N/A (Sans voirie) ✕
          </div>`}
          ${sitgLink ? `
          <a href="${sitgLink}" target="_blank" rel="noopener" class="action-btn sitg" title="Ouvrir l'orthophoto officielle SITG 5cm">
            SITG 5cm Aérien ↗
          </a>` : ''}
        </div>

        <!-- Urban Planning & Development Intelligence -->
        ${(r.plq_number || r.zone_dev_name || r.permit_number || r.grand_projet_name) ? `
        <div class="intel-section">
          <div class="intel-title">
            <span>Urbanisme & Projets Futurs</span>
            <span style="color:var(--color-sand-300); font-size:9px;">SITG OPEN DATA</span>
          </div>

          ${r.plq_number ? `
          <div class="detail-row">
            <span class="row-label">Plan Localisé de Quartier (PLQ)</span>
            <span class="row-value">
              PLQ N° <strong>${r.plq_number}</strong> (${r.plq_name || 'Geneve'}) — ${r.plq_status || 'En vigueur'}
              ${r.plq_plan_url ? `<br><a href="${r.plq_plan_url}" target="_blank" class="intel-link">Télécharger le Plan PLQ (PDF) ↗</a>` : ''}
              ${r.plq_reglement_url ? ` &bull; <a href="${r.plq_reglement_url}" target="_blank" class="intel-link">Règlement (PDF) ↗</a>` : ''}
            </span>
          </div>` : ''}

          ${r.zone_dev_name ? `
          <div class="detail-row">
            <span class="row-label">Zone de Développement (LDTR/LGZD)</span>
            <span class="row-value">
              ${r.zone_dev_name} ${r.zone_dev_restriction ? `— <em>${r.zone_dev_restriction}</em>` : ''}
              ${r.zone_dev_url ? `<br><a href="${r.zone_dev_url}" target="_blank" class="intel-link">Plan de zone légale (PDF) ↗</a>` : ''}
            </span>
          </div>` : ''}

          ${r.permit_number ? `
          <div class="detail-row">
            <span class="row-label">Permis de Construire / Projet</span>
            <span class="row-value">
              <strong>${r.permit_number}</strong>: ${r.permit_type || 'Projet'} (${r.permit_destination || 'Bâtiment'})
              ${r.permit_floors ? ` &bull; ${r.permit_floors} étages` : ''}
              ${r.permit_sad_url ? `<br><a href="${r.permit_sad_url}" target="_blank" class="intel-link">Consulter Dossier SAD Cantonal ↗</a>` : ''}
            </span>
          </div>` : ''}

          ${r.grand_projet_name ? `
          <div class="detail-row">
            <span class="row-label">Périmètre Grand Projet Cantonal</span>
            <span class="row-value">
              ${r.grand_projet_name} (${r.grand_projet_type || 'PDCn'})
              ${r.grand_projet_url ? `<br><a href="${r.grand_projet_url}" target="_blank" class="intel-link">Fiche Grand Projet (PDF) ↗</a>` : ''}
            </span>
          </div>` : ''}
        </div>` : ''}

        <div class="detail-grid">
          <div class="detail-row">
            <span class="row-label">Commune & Adresse</span>
            <span class="row-value">${displayTitle}</span>
          </div>

          ${r.egrid ? `
          <div class="detail-row">
            <span class="row-label">Identifiant Fédéral EGRID</span>
            <span class="row-value mono">${r.egrid}</span>
          </div>` : ''}

          ${r.parcel_number ? `
          <div class="detail-row">
            <span class="row-label">Numéro de Parcelle</span>
            <span class="row-value mono">${r.parcel_number}</span>
          </div>` : ''}

          ${r.surface_m2 ? `
          <div class="detail-row">
            <span class="row-label">Surface & Pièces</span>
            <span class="row-value mono">${r.surface_m2} m² ${r.rooms ? ' | ' + r.rooms + ' pièces' : ''}</span>
          </div>` : ''}

          ${r.building_destination ? `
          <div class="detail-row">
            <span class="row-label">Destination bâtiment</span>
            <span class="row-value">${r.building_destination} ${r.building_floors ? '(' + r.building_floors + ' étages)' : ''}</span>
          </div>` : ''}

          <div class="detail-row">
            <span class="row-label">Acquéreur (Acheteur)</span>
            <span class="row-value">${r.buyer || 'Non précisé'}</span>
          </div>

          <div class="detail-row">
            <span class="row-label">Aliénateur (Vendeur)</span>
            <span class="row-value">${r.seller || 'Non précisé'}</span>
          </div>

          <div class="detail-row">
            <span class="row-label">Date publication FAO</span>
            <span class="row-value mono">${r.notice_date || 'N/A'}</span>
          </div>
        </div>
      `;

      // Attach clean click listeners to avoid string quote parsing issues
      const btnStreet = document.getElementById('btnStreetViewAction');
      if (btnStreet) {
        btnStreet.onclick = () => {
          openStreetViewModal(r.lat, r.lon, displayTitle, streetViewLink, r.lv95_e, r.lv95_n, 'pano');
        };
      }

      const btnSat = document.getElementById('btnSatelliteAction');
      if (btnSat) {
        btnSat.onclick = () => {
          openStreetViewModal(r.lat, r.lon, displayTitle, streetViewLink, r.lv95_e, r.lv95_n, 'sat');
        };
      }

      detailDrawer.classList.add('visible');
    }

    // Street View & Aerial In-App Modal Logic
    const streetViewModal = document.getElementById('streetViewModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalIframe = document.getElementById('modalIframe');
    const modalExtLink = document.getElementById('modalExtLink');
    const modalCloseBtn = document.getElementById('modalCloseBtn');
    const modalHintText = document.getElementById('modalHintText');

    let currentModalLat = null;
    let currentModalLon = null;
    let currentModalLv95E = null;
    let currentModalLv95N = null;
    let currentModalTitle = '';

    function openStreetViewModal(lat, lon, title, extUrl, lv95_e, lv95_n, defaultMode = 'pano') {
      currentModalLat = lat;
      currentModalLon = lon;
      currentModalLv95E = lv95_e;
      currentModalLv95N = lv95_n;
      currentModalTitle = title || 'Inspection Visuelle';

      modalTitle.textContent = currentModalTitle;
      
      setModalMode(defaultMode);
      streetViewModal.classList.add('visible');
    }

    function setModalMode(mode) {
      document.querySelectorAll('.modal-tab-btn').forEach(b => b.classList.remove('active'));
      
      if (mode === 'pano') {
        document.getElementById('tabPano').classList.add('active');
        modalIframe.src = `https://maps.google.com/maps?q=&layer=c&cbll=${currentModalLat},${currentModalLon}&cbp=11,0,0,0,0&output=svembed`;
        modalExtLink.href = `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${currentModalLat},${currentModalLon}`;
        modalExtLink.textContent = 'Ouvrir Street View 360° ↗';
        modalHintText.innerHTML = 'Google Street View 360° • Vue panoramique au sol (Utilisez les onglets ci-dessus si la voie est privée ou agricole)';
      } else if (mode === 'sat') {
        document.getElementById('tabSat').classList.add('active');
        modalIframe.src = `https://maps.google.com/maps?q=${currentModalLat},${currentModalLon}&t=k&z=19&output=embed`;
        modalExtLink.href = `https://www.google.com/maps/@${currentModalLat},${currentModalLon},19z/data=!3m1!1e3`;
        modalExtLink.textContent = 'Ouvrir Satellite dans Google Maps ↗';
        modalHintText.innerHTML = 'Google Satellite HD • Imagerie aérienne haute résolution (Zoom 19 &bull; Couverture 100% Genève)';
      } else if (mode === 'sitg') {
        document.getElementById('tabSitg').classList.add('active');
        const sitgUrl = `https://map.sitg.ge.ch/?center=${currentModalLv95E || '2500000'},${currentModalLv95N || '1118000'}&scale=1000&mapresources=CADASTRE,ORTHOPHOTO_2023`;
        modalIframe.src = sitgUrl;
        modalExtLink.href = sitgUrl;
        modalExtLink.textContent = 'Ouvrir dans le Géoportail SITG ↗';
        modalHintText.innerHTML = 'Cadastre SITG Genève • Orthophoto officielle 5cm & Registre Foncier Cantonal (LV95)';
      }
    }

    function closeStreetViewModal() {
      streetViewModal.classList.remove('visible');
      modalIframe.src = 'about:blank';
    }

    modalCloseBtn.addEventListener('click', closeStreetViewModal);
    streetViewModal.addEventListener('click', (e) => {
      if (e.target === streetViewModal) {
        closeStreetViewModal();
      }
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && streetViewModal.classList.contains('visible')) {
        closeStreetViewModal();
      }
    });

    // Filter Logic
    let currentSource = 'ALL';

    document.querySelectorAll('.pill-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.pill-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        currentSource = e.target.getAttribute('data-source');
        applyFilters();
      });
    });

    const searchInput = document.getElementById('searchInput');
    const buildingSelect = document.getElementById('buildingSelect');
    const onlyPricedCheckbox = document.getElementById('onlyPricedCheckbox');
    const onlyDevCheckbox = document.getElementById('onlyDevCheckbox');
    const onlyPlqCheckbox = document.getElementById('onlyPlqCheckbox');
    const onlyPermitCheckbox = document.getElementById('onlyPermitCheckbox');

    [searchInput, communeSelect, zoneSelect, buildingSelect, onlyPricedCheckbox, onlyDevCheckbox, onlyPlqCheckbox, onlyPermitCheckbox].forEach(el => {
      el.addEventListener('input', applyFilters);
      el.addEventListener('change', applyFilters);
    });

    document.getElementById('resetBtn').addEventListener('click', () => {
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
    });

    function applyFilters() {
      const q = searchInput.value.toLowerCase().trim();
      const selComm = communeSelect.value;
      const selZone = zoneSelect.value;
      const selBuild = buildingSelect.value;
      const onlyPriced = onlyPricedCheckbox.checked;
      const onlyDev = onlyDevCheckbox.checked;
      const onlyPlq = onlyPlqCheckbox.checked;
      const onlyPermit = onlyPermitCheckbox.checked;

      const filtered = DATA.filter(r => {
        if (currentSource !== 'ALL' && r.source_category !== currentSource) return false;
        if (selComm !== 'ALL' && r.commune !== selComm) return false;
        if (selZone !== 'ALL' && r.zone_code !== selZone) return false;
        if (onlyPriced && (!r.price_chf || r.price_chf <= 0)) return false;
        if (onlyDev && !r.zone_dev_name) return false;
        if (onlyPlq && !r.plq_number) return false;
        if (onlyPermit && !r.permit_number) return false;

        if (selBuild !== 'ALL') {
          const bp = (r.building_period || '').toLowerCase();
          if (!bp.includes(selBuild.toLowerCase())) return false;
        }

        if (q) {
          const str = [(r.address||''), (r.commune||''), (r.buyer||''), (r.seller||''), (r.parcel_number||''), (r.egrid||''), (r.plq_name||''), (r.permit_number||''), (r.grand_projet_name||'')].join(' ').toLowerCase();
          if (!str.includes(q)) return false;
        }

        return true;
      });

      createMarkers(filtered);
    }
  </script>
</body>
</html>
"""


def build_interactive_map(
    db_path: Optional[str] = None,
    output_path: Optional[str] = None,
) -> Path:
    """Build a standalone, single-file interactive Leaflet/Swiss map styled with Cytria branding, smart Street View detection, and full planning/visual enrichment."""
    console.rule("[bold #C9A24D]Building Cytria Geneva Real Estate Intelligence Map[/bold #C9A24D]")
    
    db_file = Path(db_path or settings.storage.database_path)
    out_file = Path(output_path or (Path(settings.storage.exports_dir) / "geneva_transactions_map.html"))
    out_file.parent.mkdir(parents=True, exist_ok=True)

    csv_file = Path(settings.storage.exports_dir) / "geneva_property_transactions.csv"
    if csv_file.exists():
        import pandas as pd
        console.print(f"[cyan]Loading fully enriched dataset from:[/cyan] {csv_file.name}")
        df = pd.read_csv(csv_file, low_memory=False)
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

    html_content = (
        HTML_TEMPLATE
        .replace("__RECORDS_JSON__", records_json)
        .replace("__COMMUNES_JSON__", communes_json)
        .replace("__ZONES_JSON__", zones_json)
        .replace("__TOTAL_ROWS__", f"{len(rows):,}")
        .replace("__TOTAL_VOLUME__", f"{total_volume/1e9:.2f}")
        .replace("__PRICED_COUNT__", f"{priced_count:,}")
        .replace("__PLQ_COUNT__", f"{plq_count:,}")
        .replace("__DEV_COUNT__", f"{dev_count:,}")
        .replace("__PERMIT_COUNT__", f"{permit_count:,}")
    )

    out_file.write_text(html_content, encoding="utf-8")
    console.print(f"[bold green][OK] Cytria Interactive Map Generated:[/bold green] {out_file.resolve()} ({len(html_content)/1024:.1f} KB)\n")
    return out_file
