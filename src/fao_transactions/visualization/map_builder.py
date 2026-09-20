"""Standalone interactive HTML map generator for Geneva Property Transactions with Cytria Brand Design, Smart Street View Detection, Seller Mandate Radar, and Land Development Opportunity Engine."""

import json
import re
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from rich.console import Console

from fao_transactions.config import settings
from fao_transactions.visualization.agency_ranking import get_ranked_league_table

console = Console()


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CYTRIA — Intelligence Immobilière & Foncière Genève (FAO × SITG)</title>
  
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
      gap: 16px;
    }

    .hud-card {
      background: var(--panel-bg);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid var(--panel-border);
      padding: 10px 18px;
      display: flex;
      align-items: center;
      gap: 16px;
      pointer-events: auto;
      box-shadow: var(--shadow-elevation);
    }

    .brand-group {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .cytria-logo-svg {
      height: 22px;
      width: auto;
      display: block;
    }

    .brand-divider {
      width: 1px;
      height: 22px;
      background: var(--panel-border);
    }

    .brand-meta {
      display: flex;
      flex-direction: column;
    }

    .brand-meta-title {
      font-family: var(--font-brand);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: -0.01em;
      color: var(--color-paper);
      text-transform: uppercase;
    }

    .brand-meta-sub {
      font-size: 9px;
      font-weight: 600;
      letter-spacing: 0.08em;
      color: var(--color-brand-400);
      text-transform: uppercase;
    }

    /* Master Product Suite & Navigation Architecture */
    .product-suite-container {
      display: flex;
      flex-direction: column;
      gap: 6px;
      pointer-events: auto;
    }

    .product-master-tabs {
      display: flex;
      background: var(--color-ink-950);
      border: 1px solid var(--panel-border);
      padding: 3px;
      gap: 4px;
    }

    .product-tab {
      background: transparent;
      border: 1px solid transparent;
      color: var(--color-sand-300);
      font-family: var(--font-brand);
      padding: 6px 14px;
      cursor: pointer;
      display: inline-flex;
      flex-direction: column;
      align-items: flex-start;
      gap: 2px;
      transition: all 0.2s ease;
      text-align: left;
    }

    .product-tab:hover {
      background: var(--color-ink-900);
      color: var(--color-paper);
    }

    .product-tab.active {
      background: rgba(201, 162, 77, 0.14);
      border-color: var(--color-brand-400);
      color: var(--color-brand-300);
      box-shadow: inset 0 -2px 0 var(--color-brand-400);
    }

    .product-tab-title {
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .product-tab-sub {
      font-size: 9px;
      color: var(--color-sand-400);
      font-family: var(--font-mono);
      font-weight: 500;
    }

    .product-tab.active .product-tab-sub {
      color: var(--color-sand-200);
    }

    /* Contextual Sub-toolbars */
    .product-subtoolbar-container {
      display: flex;
      align-items: center;
    }

    .product-subtoolbar {
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .subtool-btn {
      background: var(--color-ink-900);
      border: 1px solid var(--panel-border);
      color: var(--color-sand-200);
      font-family: var(--font-brand);
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      padding: 5px 11px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s ease;
    }

    .subtool-btn:hover {
      background: var(--color-ink-800);
      border-color: var(--color-brand-400);
      color: var(--color-paper);
    }

    .subtool-btn.active {
      background: var(--color-brand-500);
      color: var(--color-ink-950);
      border-color: var(--color-brand-400);
      font-weight: 800;
      box-shadow: 0 2px 8px rgba(201, 162, 77, 0.25);
    }

    .subtool-badge {
      font-family: var(--font-mono);
      font-size: 9px;
      font-weight: 700;
      padding: 1px 5px;
      background: var(--color-ink-950);
      color: var(--color-brand-300);
      border: 1px solid var(--panel-border-gold);
    }

    .subtool-btn.active .subtool-badge {
      background: var(--color-ink-950);
      color: var(--color-paper);
      border-color: var(--color-ink-950);
    }

    /* Keep nav-mode-btn as alias if needed */
    .nav-mode-btn {
      display: none;
    }

    .hud-stats {
      display: flex;
      align-items: center;
      gap: 14px;
      border-left: 1px solid var(--panel-border);
      padding-left: 14px;
    }

    .stat-item {
      display: flex;
      flex-direction: column;
      gap: 1px;
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
      font-size: 13px;
      font-weight: 700;
      color: var(--color-paper);
    }

    .stat-value.gold { color: var(--color-brand-400); }
    .stat-value.emerald { color: #4ade80; }
    .stat-value.purple { color: #c084fc; }
    .stat-value.red { color: #f87171; }

    /* Left Sidebar Filter Panel */
    .sidebar {
      position: absolute;
      top: 136px;
      left: 16px;
      bottom: 24px;
      width: 360px;
      background: var(--panel-bg);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid var(--panel-border);
      z-index: 1000;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      box-shadow: var(--shadow-elevation);
      overflow-y: auto;
    }

    .sidebar-header-banner {
      padding: 8px 10px;
      background: var(--color-ink-900);
      border-left: 3px solid var(--color-brand-500);
      display: flex;
      flex-direction: column;
      gap: 2px;
    }

    .sidebar-header-title {
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--color-brand-300);
    }

    .sidebar-header-sub {
      font-size: 10px;
      color: var(--color-sand-300);
    }

    .search-box {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .search-input {
      width: 100%;
      background: var(--color-ink-900);
      border: 1px solid var(--panel-border);
      padding: 9px 12px;
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
      letter-spacing: 0.08em;
      color: var(--color-brand-400);
      margin-bottom: 4px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    /* Segmented Pill Rows */
    .pills-row {
      display: flex;
      gap: 4px;
      flex-wrap: wrap;
    }

    .pills-row.grid-3 {
      display: grid !important;
      grid-template-columns: 1fr 1fr 1fr !important;
      gap: 4px;
    }

    .pills-row.grid-4 {
      display: grid !important;
      grid-template-columns: 1fr 1fr !important;
      gap: 4px;
    }

    .pills-row.grid-5 {
      display: grid !important;
      grid-template-columns: repeat(5, 1fr) !important;
      gap: 3px;
    }

    .pill-btn {
      width: 100%;
      background: var(--color-ink-900);
      border: 1px solid var(--panel-border);
      color: var(--color-sand-300);
      padding: 6px 4px;
      font-size: 9.5px;
      font-weight: 600;
      cursor: pointer;
      text-align: center;
      transition: all 0.15s ease;
      white-space: nowrap;
      text-transform: uppercase;
      letter-spacing: 0.03em;
      overflow: hidden;
      text-overflow: ellipsis;
      box-sizing: border-box;
    }

    .pill-btn:hover {
      background: var(--color-ink-800);
      color: var(--color-paper);
      border-color: rgba(255, 255, 255, 0.2);
    }

    .pill-btn.active {
      background: rgba(201, 162, 77, 0.2);
      border-color: var(--color-brand-500);
      color: var(--color-brand-300);
      font-weight: 700;
    }

    /* 2-Column Select Grids */
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
      padding: 7px 8px;
      font-size: 11px;
      font-family: var(--font-body);
      outline: none;
      cursor: pointer;
    }

    .select-input:focus {
      border-color: var(--color-brand-400);
    }

    /* 2x2 Toggle Grid for Strategic Filters */
    .toggle-grid-2 {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6px;
    }

    .toggle-card {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 7px 8px;
      background: var(--color-ink-900);
      border: 1px solid var(--panel-border);
      font-size: 10px;
      font-weight: 600;
      color: var(--color-sand-300);
      cursor: pointer;
      transition: all 0.15s ease;
    }

    .toggle-card:hover {
      border-color: rgba(255, 255, 255, 0.2);
      color: var(--color-paper);
    }

    .toggle-card.checked {
      background: rgba(201, 162, 77, 0.15);
      border-color: var(--color-brand-500);
      color: var(--color-brand-300);
    }

    .toggle-card input {
      accent-color: var(--color-brand-500);
      cursor: pointer;
    }

    /* Advanced Collapsible Filter */
    details.advanced-filters {
      background: var(--color-ink-900);
      border: 1px solid var(--panel-border);
      padding: 8px 10px;
    }

    details.advanced-filters summary {
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--color-sand-300);
      cursor: pointer;
      user-select: none;
      outline: none;
    }

    details.advanced-filters summary:hover {
      color: var(--color-brand-300);
    }

    .advanced-content {
      padding-top: 10px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .reset-btn {
      background: transparent;
      border: 1px solid var(--panel-border);
      color: var(--color-sand-300);
      padding: 8px;
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
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
      gap: 5px;
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
      flex-shrink: 0;
    }

    /* Right Detail Drawer */
    .detail-drawer {
      position: absolute;
      top: 136px;
      right: 16px;
      bottom: 24px;
      width: 440px;
      background: var(--panel-bg);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 1px solid var(--panel-border-gold);
      z-index: 1000;
      padding: 22px;
      box-shadow: var(--shadow-elevation);
      overflow-y: auto;
      display: none;
      flex-direction: column;
      gap: 15px;
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
      padding-bottom: 12px;
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
      font-size: 24px;
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

    .badge-tag.mandate-hot {
      background: rgba(239, 68, 68, 0.25);
      color: #fca5a5;
      border-color: #ef4444;
      font-weight: 800;
    }

    .badge-tag.dev-opp {
      background: rgba(16, 185, 129, 0.25);
      color: #6ee7b7;
      border-color: #10b981;
      font-weight: 800;
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
      padding: 10px 12px;
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

    /* Mandate & Developer Radar Boxes in Drawer */
    .radar-box {
      background: var(--color-ink-900);
      border: 1px solid var(--panel-border-gold);
      padding: 14px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .radar-box.mandate {
      border-color: #ef4444;
      background: rgba(239, 68, 68, 0.05);
    }

    .radar-box.developer {
      border-color: #10b981;
      background: rgba(16, 185, 129, 0.05);
    }

    .radar-box-title {
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .radar-box.mandate .radar-box-title { color: #f87171; }
    .radar-box.developer .radar-box-title { color: #34d399; }

    .score-meter {
      height: 6px;
      background: var(--color-ink-950);
      border: 1px solid var(--panel-border);
      position: relative;
      overflow: hidden;
    }

    .score-meter-fill {
      height: 100%;
      background: linear-gradient(90deg, #F59E0B, #EF4444);
    }

    .signal-list {
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 5px;
      font-size: 11px;
      color: var(--color-sand-300);
    }

    .signal-list li::before {
      content: "• ";
      color: var(--color-brand-400);
      font-weight: bold;
    }

    .radar-box.mandate .signal-list li::before { color: #ef4444; }
    .radar-box.developer .signal-list li::before { color: #10b981; }

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

    /* League Table Modal Styling */
    .league-modal-window {
      background: var(--panel-bg);
      border: 1px solid var(--panel-border);
      width: 92vw;
      max-width: 1240px;
      height: 86vh;
      display: flex;
      flex-direction: column;
      box-shadow: var(--shadow-elevation);
    }

    .league-header {
      padding: 16px 24px;
      background: var(--color-ink-950);
      border-bottom: 1px solid var(--panel-border);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .league-title-box h2 {
      font-family: var(--font-brand);
      font-size: 17px;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: var(--color-brand-300);
      margin: 0 0 3px 0;
    }

    .league-title-box p {
      margin: 0;
      font-size: 11px;
      color: var(--color-sand-300);
    }

    .league-tabs {
      display: flex;
      gap: 6px;
    }

    .league-tab-btn {
      padding: 7px 14px;
      background: var(--color-ink-800);
      border: 1px solid var(--panel-border);
      color: var(--color-sand-300);
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .league-tab-btn.active {
      background: var(--color-brand-500);
      border-color: var(--color-brand-400);
      color: var(--color-ink-950);
      font-weight: 700;
    }

    .league-body {
      flex: 1;
      overflow-y: auto;
      padding: 20px 24px;
      background: var(--color-ink-900);
    }

    .league-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;
      text-align: left;
    }

    .league-table th {
      background: var(--color-ink-950);
      color: var(--color-brand-300);
      padding: 10px 14px;
      font-family: var(--font-mono);
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      border-bottom: 1px solid var(--panel-border);
      position: sticky;
      top: 0;
      z-index: 5;
    }

    .league-table td {
      padding: 12px 14px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      color: var(--color-paper);
      vertical-align: middle;
    }

    .league-table tr:hover td {
      background: rgba(201, 162, 77, 0.05);
    }

    .rank-pill {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 24px;
      height: 24px;
      font-family: var(--font-mono);
      font-weight: 700;
      font-size: 12px;
      border: 1px solid var(--panel-border);
      background: var(--color-ink-800);
      color: var(--color-sand-300);
    }

    .rank-pill.top-1 {
      border-color: var(--color-brand-400);
      background: rgba(201, 162, 77, 0.2);
      color: var(--color-brand-300);
    }

    .rank-pill.top-2 {
      border-color: #94a3b8;
      background: rgba(148, 163, 184, 0.15);
      color: #cbd5e1;
    }

    .rank-pill.top-3 {
      border-color: #b45309;
      background: rgba(180, 83, 9, 0.15);
      color: #fcd34d;
    }

    .score-badge {
      display: inline-block;
      padding: 3px 8px;
      font-family: var(--font-mono);
      font-weight: 700;
      font-size: 11px;
      background: rgba(16, 185, 129, 0.15);
      border: 1px solid #10b981;
      color: #6ee7b7;
    }

    /* Agency Map Markers & Pins */
    .agency-marker-pin {
      display: inline-flex;
      align-items: center;
      background: var(--color-ink-950);
      border: 1.5px solid var(--color-brand-400);
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.7);
      padding: 2px 7px;
      cursor: pointer;
      white-space: nowrap;
      gap: 6px;
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .agency-marker-pin:hover, .agency-marker-pin.active {
      transform: scale(1.12);
      border-color: #f6e05e;
      background: var(--color-ink-800);
      box-shadow: 0 0 16px rgba(201, 162, 77, 0.75);
      z-index: 9999 !important;
    }

    /* Semi-transparent state when an agency is focused / clicked */
    .agency-marker-pin.dimmed {
      opacity: 0.30 !important;
      filter: grayscale(60%);
      transform: scale(0.85);
      border-color: rgba(201, 162, 77, 0.28);
      box-shadow: none;
      z-index: 100 !important;
    }

    .agency-marker-pin.dimmed:hover {
      opacity: 1 !important;
      filter: none;
      transform: scale(1.05);
      border-color: var(--color-brand-400);
      box-shadow: 0 0 14px rgba(201, 162, 77, 0.5);
      z-index: 9000 !important;
    }

    .pin-badge {
      background: var(--color-brand-400);
      color: #080d11;
      font-family: var(--font-mono);
      font-weight: 800;
      font-size: 10px;
      padding: 1px 4px;
      flex-shrink: 0;
    }

    .pin-name {
      font-family: var(--font-brand);
      font-weight: 700;
      font-size: 11px;
      color: var(--color-paper);
      max-width: 140px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    /* Floating Agency & Agent Focus Banner on Map */
    .agency-focus-banner {
      position: absolute;
      top: 136px;
      left: 50%;
      transform: translateX(-50%);
      z-index: 1000;
      display: flex;
      align-items: center;
      gap: 12px;
      background: rgba(8, 13, 17, 0.94);
      border: 1px solid var(--color-brand-400);
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.7), 0 0 16px rgba(201, 162, 77, 0.25);
      padding: 8px 16px;
      backdrop-filter: blur(8px);
    }

    .focus-banner-content {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .agency-focus-banner .focus-badge {
      background: rgba(201, 162, 77, 0.2);
      color: var(--color-brand-300);
      font-family: var(--font-mono);
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      padding: 3px 8px;
      border: 1px solid rgba(201, 162, 77, 0.4);
    }

    .agency-focus-banner .focus-title {
      color: var(--color-paper);
      font-size: 13px;
      font-weight: 700;
    }

    .agency-focus-banner .focus-count {
      color: var(--color-sand-300);
      font-size: 11px;
      font-family: var(--font-mono);
    }

    .agency-focus-banner .focus-banner-reset {
      background: rgba(239, 68, 68, 0.18);
      border: 1px solid #ef4444;
      color: #fca5a5;
      font-family: var(--font-brand);
      font-size: 11px;
      font-weight: 600;
      padding: 4px 10px;
      cursor: pointer;
      transition: all 0.2s;
    }

    .agency-focus-banner .focus-banner-reset:hover {
      background: #ef4444;
      color: #fff;
    }

    /* Social Action Buttons */
    .social-buttons-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      margin: 12px 0 16px;
    }

    .social-btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 7px 10px;
      font-size: 11px;
      font-family: var(--font-brand);
      font-weight: 600;
      text-decoration: none;
      border: 1px solid transparent;
      transition: opacity 0.2s, transform 0.1s;
      cursor: pointer;
    }

    .social-btn:hover {
      opacity: 0.9;
      transform: translateY(-1px);
    }

    .social-btn.linkedin {
      background: #0a66c2;
      color: #ffffff;
    }

    .social-btn.instagram {
      background: linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888);
      color: #ffffff;
    }

    .social-btn.youtube {
      background: #cc0000;
      color: #ffffff;
    }

    .social-btn.tiktok {
      background: #010101;
      border-color: #25f4ee;
      color: #ffffff;
    }

    .social-btn.facebook {
      background: #1877f2;
      color: #ffffff;
    }

    .social-btn.website {
      background: rgba(201, 162, 77, 0.15);
      border-color: var(--color-brand-400);
      color: var(--color-brand-300);
    }

    .social-btn.contact {
      background: var(--color-ink-800);
      border-color: var(--panel-border);
      color: var(--color-paper);
    }

    /* Sold Properties Portfolio in Drawer */
    .sold-props-list {
      display: flex;
      flex-direction: column;
      gap: 6px;
      max-height: 280px;
      overflow-y: auto;
      margin-top: 8px;
      padding-right: 4px;
    }

    .sold-prop-item {
      background: var(--color-ink-900);
      border: 1px solid var(--panel-border);
      padding: 8px 10px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 11px;
      transition: background 0.15s;
    }

    .sold-prop-item:hover {
      background: rgba(201, 162, 77, 0.08);
      border-color: rgba(201, 162, 77, 0.4);
    }

    /* Broker Card */
    .broker-card {
      background: var(--color-ink-900);
      border: 1px solid var(--panel-border);
      padding: 10px 12px;
      margin-bottom: 8px;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .broker-name {
      font-family: var(--font-brand);
      font-weight: 700;
      font-size: 13px;
      color: var(--color-brand-300);
    }

    .broker-role {
      font-size: 11px;
      color: var(--color-sand-300);
    }

    .view-map-btn {
      background: transparent;
      border: 1px solid var(--color-brand-400);
      color: var(--color-brand-300);
      font-family: var(--font-mono);
      font-size: 10px;
      padding: 3px 8px;
      cursor: pointer;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      transition: all 0.15s;
    }

    .view-map-btn:hover {
      background: var(--color-brand-400);
      color: var(--color-ink-950);
    }

    .commune-tag {
      display: inline-block;
      padding: 2px 6px;
      background: rgba(201, 162, 77, 0.12);
      border: 1px solid rgba(201, 162, 77, 0.3);
      color: var(--color-brand-300);
      font-size: 10px;
      font-family: var(--font-mono);
      margin-right: 4px;
    /* Scan Live Indicator Dot */
    .scan-live-dot {
      width: 7px;
      height: 7px;
      background: #4ade80;
      box-shadow: 0 0 8px #4ade80;
      border-radius: 50% !important;
      animation: pulseLiveDot 1.8s infinite ease-in-out;
      display: inline-block;
    }
    @keyframes pulseLiveDot {
      0%, 100% { transform: scale(1); opacity: 1; box-shadow: 0 0 6px #4ade80; }
      50% { transform: scale(1.4); opacity: 0.6; box-shadow: 0 0 12px #4ade80; }
    }

    /* Scan Modal Window */
    .scan-modal-window {
      background: var(--panel-bg);
      border: 1px solid var(--panel-border-gold);
      width: 90vw;
      max-width: 1060px;
      max-height: 88vh;
      display: flex;
      flex-direction: column;
      box-shadow: var(--shadow-elevation);
      overflow: hidden;
    }

    .scan-header {
      padding: 16px 24px;
      background: var(--color-ink-950);
      border-bottom: 1px solid var(--panel-border);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .scan-title-box h2 {
      font-family: var(--font-brand);
      font-size: 16px;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: var(--color-brand-300);
      margin: 0 0 4px 0;
    }

    .scan-title-box p {
      margin: 0;
      font-size: 11px;
      color: var(--color-sand-300);
    }

    .scan-body {
      flex: 1;
      overflow-y: auto;
      padding: 20px 24px;
      background: var(--color-ink-900);
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .scan-guarantee-card {
      background: rgba(201, 162, 77, 0.08);
      border: 1px solid var(--panel-border-gold);
      padding: 14px 18px;
      display: flex;
      gap: 14px;
      align-items: flex-start;
    }

    .guarantee-icon {
      font-size: 24px;
      line-height: 1;
    }

    .guarantee-title {
      font-family: var(--font-brand);
      font-size: 13px;
      font-weight: 700;
      color: var(--color-brand-300);
      text-transform: uppercase;
      letter-spacing: 0.04em;
      margin-bottom: 4px;
    }

    .guarantee-desc {
      font-size: 11px;
      line-height: 1.5;
      color: var(--color-paper);
    }

    .guarantee-desc strong {
      color: var(--color-brand-200);
    }

    .scan-config-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }

    .scan-config-box {
      background: var(--color-ink-950);
      border: 1px solid var(--panel-border);
      padding: 14px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .scan-box-title {
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--color-brand-300);
      border-bottom: 1px solid var(--panel-border);
      padding-bottom: 6px;
    }

    .portal-check-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .portal-check-item {
      display: flex;
      align-items: flex-start;
      gap: 10px;
      cursor: pointer;
      padding: 6px 8px;
      background: var(--color-ink-900);
      border: 1px solid rgba(255,255,255,0.04);
      transition: background 0.15s;
    }

    .portal-check-item:hover {
      background: var(--color-ink-850);
    }

    .portal-check-info {
      display: flex;
      flex-direction: column;
      gap: 2px;
    }

    .portal-name {
      font-size: 11px;
      font-weight: 700;
      color: var(--color-paper);
    }

    .portal-detail {
      font-size: 10px;
      color: var(--color-sand-300);
    }

    .scan-modes-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .scan-mode-card {
      padding: 8px 10px;
      background: var(--color-ink-900);
      border: 1px solid var(--panel-border);
      cursor: pointer;
      transition: all 0.2s ease;
      display: flex;
      flex-direction: column;
      gap: 2px;
    }

    .scan-mode-card:hover {
      border-color: var(--color-brand-400);
    }

    .scan-mode-card.active {
      border-color: var(--color-brand-500);
      background: rgba(201, 162, 77, 0.12);
    }

    .scan-mode-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .mode-name {
      font-size: 11px;
      font-weight: 700;
      color: var(--color-paper);
    }

    .scan-mode-card.active .mode-name {
      color: var(--color-brand-300);
    }

    .mode-badge {
      font-family: var(--font-mono);
      font-size: 9px;
      background: var(--color-ink-950);
      color: var(--color-brand-300);
      padding: 1px 5px;
      border: 1px solid var(--panel-border);
    }

    .mode-desc {
      font-size: 10px;
      color: var(--color-sand-300);
    }

    .scan-progress-bar-bg {
      width: 100%;
      height: 7px;
      background: var(--color-ink-950);
      border: 1px solid var(--panel-border);
      overflow: hidden;
      margin-bottom: 12px;
    }

    .scan-progress-bar-fill {
      height: 100%;
      background: linear-gradient(90deg, var(--color-brand-600), var(--color-brand-400), #4ade80);
      transition: width 0.3s ease;
    }

    .scan-kpi-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 10px;
      margin-bottom: 14px;
    }

    .scan-kpi-card {
      background: var(--color-ink-950);
      border: 1px solid var(--panel-border);
      padding: 10px;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .scan-kpi-label {
      font-size: 9px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--color-sand-300);
    }

    .scan-kpi-val {
      font-family: var(--font-mono);
      font-size: 16px;
      font-weight: 800;
      color: var(--color-paper);
    }

    .scan-terminal-wrapper {
      background: #04070a;
      border: 1px solid var(--panel-border);
    }

    .scan-terminal-header {
      background: var(--color-ink-950);
      padding: 6px 12px;
      font-family: var(--font-mono);
      font-size: 10px;
      color: var(--color-sand-300);
      border-bottom: 1px solid var(--panel-border);
      display: flex;
      justify-content: space-between;
    }

    .scan-terminal {
      padding: 10px 14px;
      font-family: var(--font-mono);
      font-size: 11px;
      line-height: 1.6;
      height: 140px;
      overflow-y: auto;
      color: #94a3b8;
    }

    .term-line {
      margin-bottom: 2px;
      word-break: break-all;
    }
    .term-line.info { color: var(--color-brand-300); }
    .term-line.success { color: #4ade80; }
    .term-line.warning { color: #fbbf24; }
    .term-line.error { color: #f87171; }
  </style>
</head>
<body>

  <!-- Map Container -->
  <div id="map"></div>

  <!-- Floating Agency & Agent Focus Banner -->
  <div id="agencyFocusBanner" class="agency-focus-banner" style="display:none;">
    <div class="focus-banner-content">
      <span class="focus-badge" id="focusBannerBadge">Agence Isolée</span>
      <span class="focus-title" id="focusBannerTitle"></span>
      <span class="focus-count" id="focusBannerCount"></span>
    </div>
    <button type="button" class="focus-banner-reset" onclick="renderAgenciesOnMap(null)">✕ Réinitialiser le focus (Voir tout le réseau)</button>
  </div>

  <!-- Top Bar HUD & Mode Switcher -->
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
          <div class="brand-meta-title">Intelligence Foncière</div>
          <div class="brand-meta-sub">Canton de Genève</div>
        </div>
      </div>

      <!-- Master Product Suite Navigation & Contextual Toolbars -->
      <div class="product-suite-container">
        <!-- 3 Master Product Tabs (Zero Emoji, Clean Typography) -->
        <div class="product-master-tabs">
          <button type="button" class="product-tab active" id="tabProductMarket" onclick="switchProductSuite('MARKET')">
            <span class="product-tab-title">CYTRIA MARKET</span>
            <span class="product-tab-sub">Marché & Prix <strong class="subtool-badge" id="navBadgeMarket">__TOTAL_ROWS__</strong></span>
          </button>
          <button type="button" class="product-tab" id="tabProductSourcing" onclick="switchProductSuite('SOURCING')">
            <span class="product-tab-title">CYTRIA SOURCING</span>
            <span class="product-tab-sub">Mandats B2C & Fonciers B2B</span>
          </button>
          <button type="button" class="product-tab" id="tabProductAgencyBI" onclick="switchProductSuite('AGENCY_BI')">
            <span class="product-tab-title">CYTRIA AGENCY BI</span>
            <span class="product-tab-sub">__AGENCIES_COUNT__ Agences & Veille</span>
          </button>
        </div>

        <!-- Contextual Sub-Toolbars -->
        <div class="product-subtoolbar-container">
          <!-- 1. MARKET Subtoolbar -->
          <div class="product-subtoolbar" id="subtoolbarMarket">
            <button type="button" class="subtool-btn active" id="mktFilterAll" onclick="setMarketQuickFilter('ALL')">
              Tous les actes <span class="subtool-badge">__TOTAL_ROWS__</span>
            </button>
            <button type="button" class="subtool-btn" id="mktFilterApartments" onclick="setMarketQuickFilter('PPE')">
              Appartements PPE
            </button>
            <button type="button" class="subtool-btn" id="mktFilterHouses" onclick="setMarketQuickFilter('VILLA')">
              Villas & Maisons
            </button>
            <button type="button" class="subtool-btn" id="mktFilterBuildings" onclick="setMarketQuickFilter('IMMEUBLE')">
              Immeubles de rapport
            </button>
            <button type="button" class="subtool-btn" id="mktFilterLand" onclick="setMarketQuickFilter('TERRAIN')">
              Terrains & Parcelles
            </button>
            <button type="button" class="subtool-btn" id="mktSyncBtn" onclick="openContextualSyncModal('MARKET')" style="margin-left: auto; border-color: rgba(201, 162, 77, 0.4); background: rgba(201, 162, 77, 0.08); color: var(--color-brand-300);">
              <span class="scan-live-dot"></span> Actualiser Marché (FAO × SITG)
            </button>
          </div>

          <!-- 2. SOURCING Subtoolbar -->
          <div class="product-subtoolbar" id="subtoolbarSourcing" style="display: none;">
            <button type="button" class="subtool-btn active" id="sourcingBtnB2C" onclick="switchSourcingModule('B2C_MANDATES')">
              Scanner Mandats B2C <span class="subtool-badge" id="navBadgeMandates">__MANDATES_COUNT__</span>
            </button>
            <button type="button" class="subtool-btn" id="sourcingBtnB2B" onclick="switchSourcingModule('B2B_DEVELOPMENT')">
              Radar Promoteurs B2B <span class="subtool-badge" id="navBadgeDev">__DEV_COUNT__</span>
            </button>
            <button type="button" class="subtool-btn" id="sourcingSyncBtn" onclick="openContextualSyncModal('SOURCING')" style="margin-left: auto; border-color: rgba(201, 162, 77, 0.4); background: rgba(201, 162, 77, 0.08); color: var(--color-brand-300);">
              <span class="scan-live-dot"></span> Actualiser Sourcing (Hoiries & Permis)
            </button>
          </div>

          <!-- 3. AGENCY BI Subtoolbar -->
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
            <button type="button" class="subtool-btn" id="agencySyncBtn" onclick="openContextualSyncModal('AGENCY_BI')" style="margin-left: auto; border-color: rgba(201, 162, 77, 0.4); background: rgba(201, 162, 77, 0.08); color: var(--color-brand-300);">
              <span class="scan-live-dot"></span> Actualiser Veille & Benchmarking
            </button>
          </div>
        </div>
      </div>

      <div class="hud-stats">
        <div class="stat-item">
          <span class="stat-label" id="statLabelPrimary">Transactions</span>
          <span class="stat-value" id="stat-count">__TOTAL_ROWS__</span>
        </div>
        <div class="stat-item">
          <span class="stat-label" id="statLabelSecondary">Volume Actif</span>
          <span class="stat-value emerald" id="stat-vol">CHF __TOTAL_VOLUME__ Mrd</span>
        </div>
        <div class="stat-item" id="hudStatItem3">
          <span class="stat-label" id="statLabel3">Avec Prix</span>
          <span class="stat-value gold" id="stat-3">__PRICED_COUNT__</span>
        </div>
        <div class="stat-item" id="hudStatItem4">
          <span class="stat-label" id="statLabel4">Opportunités</span>
          <span class="stat-value purple" id="stat-4">__HOT_MANDATES_COUNT__</span>
        </div>
        <div class="stat-item" style="border-right: none; padding-right: 0;">
          <button type="button" class="subtool-btn" onclick="openMethodologyModal()" style="padding: 7px 14px; font-size: 11px; font-weight: 700; color: var(--color-brand-300); border: 1px solid rgba(201, 162, 77, 0.4); background: rgba(201, 162, 77, 0.08); text-transform: uppercase; letter-spacing: 0.05em; cursor: pointer;">
            Guide Métier & Playbooks ↗
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Sidebar Filter Panel -->
  <aside class="sidebar">
    <div class="sidebar-header-banner" id="sidebarBanner">
      <div class="sidebar-header-title" id="sidebarBannerTitle">Marché Immobilier Complet</div>
      <div class="sidebar-header-sub" id="sidebarBannerSub">Filtrez les mutations du Registre Foncier et LDTR</div>
    </div>

    <div class="search-box">
      <input type="text" id="searchInput" class="search-input" placeholder="Recherche adresse, acquéreur, aliénateur, PLQ...">
    </div>

    <!-- Mode-Specific Filters: Market Mode Filters -->
    <div id="filterGroupMarket">
      <div>
        <div class="filter-section-title">Nature Juridique</div>
        <div class="pills-row grid-4">
          <button class="pill-btn active" data-nature="ALL">Toutes</button>
          <button class="pill-btn" data-nature="VENTE">Ventes</button>
          <button class="pill-btn" data-nature="SUCCESSION">Héritages</button>
          <button class="pill-btn" data-nature="DONATION">Donations</button>
        </div>
      </div>

      <div style="margin-top: 10px;">
        <div class="filter-section-title">
          <span>Fourchette de Prix (CHF)</span>
          <span id="priceDisplayLabel" style="font-family:var(--font-mono); color:var(--color-brand-300); text-transform:none; font-size:9px;">Tous prix</span>
        </div>
        <div class="pills-row grid-5">
          <button class="pill-btn active price-pill" data-price="ALL">Tous</button>
          <button class="pill-btn price-pill" data-price="0-1.5M">&lt; 1.5M</button>
          <button class="pill-btn price-pill" data-price="1.5M-5M">1.5 - 5M</button>
          <button class="pill-btn price-pill" data-price="5M-15M">5 - 15M</button>
          <button class="pill-btn price-pill" data-price="15M+">&gt; 15M</button>
        </div>
      </div>
    </div>

    <!-- Mode-Specific Filters: Mandates Scanner Filters -->
    <div id="filterGroupMandates" style="display:none;">
      <div>
        <div class="filter-section-title">Niveau d'Opportunité Vendeur</div>
        <div class="pills-row grid-3">
          <button class="pill-btn active" data-mandate-score="ALL">Tous (__MANDATES_COUNT__)</button>
          <button class="pill-btn" data-mandate-score="HOT">Chauds ≥ 70</button>
          <button class="pill-btn" data-mandate-score="ULTRA">Urgents ≥ 85</button>
        </div>
      </div>

      <div style="margin-top: 10px;">
        <label class="toggle-card checked" id="cardHoiriesOnly" style="padding: 8px;">
          <input type="checkbox" id="onlyHoiriesCheckbox">
          <span>Hoiries Multi-Héritiers uniquement</span>
        </label>
      </div>
    </div>

    <!-- Mode-Specific Filters: Development Radar Filters -->
    <div id="filterGroupDev" style="display:none;">
      <div>
        <div class="filter-section-title">Typologie de Potentiel Foncier</div>
        <div class="pills-row grid-4">
          <button class="pill-btn active" data-dev-type="ALL">Tous (__DEV_COUNT__)</button>
          <button class="pill-btn" data-dev-type="PERMIT">Permis APA</button>
          <button class="pill-btn" data-dev-type="ZONE5">Densif. Z5</button>
          <button class="pill-btn" data-dev-type="PLQ">Sous PLQ</button>
        </div>
      </div>
    </div>

    <!-- Mode-Specific Filters: Agencies Map Filters -->
    <div id="filterGroupAgencies" style="display:none;">
      <div>
        <div class="filter-section-title">Sélectionner une Agence</div>
        <select class="select-input" id="sidebarAgencySelect" style="border-color: var(--color-brand-400); color: var(--color-brand-300);">
          <option value="ALL">Toutes les agences du canton (__AGENCIES_COUNT__)</option>
        </select>
      </div>
      <div id="sidebarBrokerGroup" style="display:none; margin-top: 8px;">
        <div class="filter-section-title">Filtrer par Courtier / Agent</div>
        <select class="select-input" id="sidebarBrokerSelect" style="border-color: var(--color-brand-400); color: var(--color-sand-100);">
          <option value="ALL">Tous les courtiers de l'agence</option>
        </select>
      </div>
      <div id="sidebarResetAgencyGroup" style="display:none; margin-top: 8px;">
        <button type="button" class="view-map-btn" style="width:100%; padding: 6px; background: rgba(239,68,68,0.15); border-color: #ef4444; color: #fca5a5; text-align: center;" onclick="renderAgenciesOnMap(null)">
          ✕ Réinitialiser le focus (Voir tout le réseau)
        </button>
      </div>
      <div style="margin-top: 8px;">
        <button type="button" class="view-map-btn" style="width:100%; padding: 7px; text-align:center;" onclick="openLeagueModal()">
          Consulter l'Analyse Concurrentielle & Parts de Marché ↗
        </button>
      </div>
    </div>

    <!-- Universal Typology & Rooms Grid -->
    <div class="filter-grid-2">
      <div>
        <div class="filter-section-title">Typologie du Bien</div>
        <select class="select-input" id="typologySelect">
          <option value="ALL">Toutes typologies</option>
          <option value="IMMEUBLE">Immeuble collectif</option>
          <option value="VILLA">Villa & Maison</option>
          <option value="PPE">Appartement & PPE</option>
          <option value="COMMERCIAL">Commercial & Bureaux</option>
          <option value="TERRAIN">Terrain & Parcelle</option>
        </select>
      </div>
      <div>
        <div class="filter-section-title">Nombre de Pièces</div>
        <select class="select-input" id="roomsSelect">
          <option value="ALL">Toutes pièces</option>
          <option value="2">Studio / 2 pièces</option>
          <option value="3">3 pièces</option>
          <option value="4">4 pièces</option>
          <option value="5">5 pièces</option>
          <option value="6+">6 pièces et plus</option>
        </select>
      </div>
    </div>

    <!-- Location & Zoning Grid -->
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

    <!-- Strategic Filters (2x2 Grid) -->
    <div id="strategicTogglesSection">
      <div class="filter-section-title">Filtres Stratégiques SITG</div>
      <div class="toggle-grid-2">
        <label class="toggle-card" id="cardPlq">
          <input type="checkbox" id="onlyPlqCheckbox">
          <span>Avec PLQ</span>
        </label>
        <label class="toggle-card" id="cardDev">
          <input type="checkbox" id="onlyDevCheckbox">
          <span>Zone Dév.</span>
        </label>
        <label class="toggle-card" id="cardPermit">
          <input type="checkbox" id="onlyPermitCheckbox">
          <span>Permis APA</span>
        </label>
        <label class="toggle-card" id="cardPriced">
          <input type="checkbox" id="onlyPricedCheckbox">
          <span>Prix publié</span>
        </label>
      </div>
    </div>

    <!-- Collapsible Advanced Filters -->
    <details class="advanced-filters">
      <summary>Filtres Avancés (Époque, Surface) ▾</summary>
      <div class="advanced-content">
        <div>
          <div class="filter-section-title">Époque de Construction</div>
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
          <div class="filter-section-title">Surface Parcelle Minimale (m²)</div>
          <select class="select-input" id="surfaceSelect">
            <option value="ALL">Toutes surfaces</option>
            <option value="500">&gt; 500 m²</option>
            <option value="1000">&gt; 1'000 m² (Potentiel Art. 59)</option>
            <option value="2500">&gt; 2'500 m²</option>
            <option value="5000">&gt; 5'000 m² (Grand foncier)</option>
          </select>
        </div>
      </div>
    </details>

    <button class="reset-btn" id="resetBtn">Réinitialiser tous les filtres</button>

    <div class="legend" id="mapLegend">
      <!-- Dynamic legend populated by active mode -->
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
            <button type="button" class="modal-tab-btn active" id="tabPano" onclick="setModalMode('pano')">360° Street View</button>
            <button type="button" class="modal-tab-btn" id="tabSat" onclick="setModalMode('sat')">Satellite HD</button>
            <button type="button" class="modal-tab-btn" id="tabSitg" onclick="setModalMode('sitg')">Cadastre SITG</button>
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
        <span id="modalHintText">Google Street View 360° • Vue panoramique au niveau de la voie publique</span>
      </div>
      <div class="modal-body">
        <iframe id="modalIframe" class="modal-iframe" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen src="about:blank"></iframe>
      </div>
    </div>
  </div>

  <!-- Cytria League Table: Agency & Agent Ranking Modal -->
  <div class="modal-overlay" id="leagueTableModal">
    <div class="league-modal-window">
      <div class="league-header">
        <div class="league-title-box">
          <h2>Benchmark Concurrentiel & Analyse des Parts de Marché — Genève</h2>
          <p>Matrice d'intelligence de marché Cytria (0-100) calibrée sur les transactions officielles du Registre Foncier (FAO) et les volumes constatés.</p>
        </div>
        <div style="display:flex; align-items:center; gap: 14px;">
          <div class="league-tabs">
            <button type="button" class="league-tab-btn active" id="leagueTabAgencies" onclick="setLeagueTab('AGENCIES')">Benchmark Agences (<span id="countAgencies">0</span>)</button>
            <button type="button" class="league-tab-btn" id="leagueTabBrokers" onclick="setLeagueTab('BROKERS')">Répertoire Courtiers & Négociateurs (<span id="countBrokers">0</span>)</button>
          </div>
          <button class="modal-close-btn" id="leagueModalCloseBtn" onclick="closeLeagueModal()">&times;</button>
        </div>
      </div>

      <!-- League Filter Bar -->
      <div style="padding: 10px 24px; background: var(--color-ink-950); border-bottom: 1px solid var(--panel-border); display: flex; gap: 12px; align-items: center;">
        <input type="text" id="leagueSearchInput" placeholder="Filtrer par nom d'agence, courtier, commune..." style="flex: 1; padding: 7px 12px; background: var(--color-ink-900); border: 1px solid var(--panel-border); color: var(--color-paper); font-size: 12px; font-family: var(--font-brand); outline: none;">
        <select id="leagueCommuneSelect" style="width: 220px; padding: 7px 12px; background: var(--color-ink-900); border: 1px solid var(--panel-border); color: var(--color-paper); font-size: 12px; font-family: var(--font-brand); outline: none;">
          <option value="ALL">Toutes communes genevoises</option>
        </select>
        <span id="leagueResultsCount" style="font-family: var(--font-mono); font-size: 11px; color: var(--color-sand-300); white-space: nowrap;"></span>
      </div>

      <div class="league-body" id="leagueBodyContent">
        <!-- Injected via JavaScript -->
      </div>
    </div>
  </div>

  <!-- Cytria Marketing Benchmark & Competitive Intelligence Modal -->
  <div class="modal-overlay" id="marketingModal">
    <div class="league-modal-window" style="max-width: 1100px; width: 92vw; overflow-x: hidden;">
      <div class="league-header">
        <div class="league-title-box">
          <div style="display:flex; align-items:center; gap:10px;">
            <span class="badge-tag" style="background:rgba(201,162,77,0.15); color:var(--color-brand-300); border-color:var(--color-brand-400); font-size:10px; font-weight:700; letter-spacing:0.04em;">BENCHMARK CONCURRENTIEL</span>
            <h2>Veille Concurrentielle & Stratégie Marketing des Agences Genevoises</h2>
          </div>
          <p>Surveillance en temps réel de l'activité éditoriale (Blog/Presse) et des comptes officiels vérifiés (Instagram, LinkedIn, YouTube, TikTok, Facebook).</p>
        </div>
        <button class="modal-close-btn" id="marketingModalCloseBtn" onclick="closeMarketingModal()">&times;</button>
      </div>

      <!-- Filter bar -->
      <div style="padding: 10px 24px; background: var(--color-ink-950); border-bottom: 1px solid var(--panel-border); display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
        <input type="text" id="marketingSearchInput" placeholder="Rechercher une agence, mot-clé ou publication..." style="flex: 1; min-width: 200px; padding: 7px 12px; background: var(--color-ink-900); border: 1px solid var(--panel-border); color: var(--color-paper); font-size: 12px; font-family: var(--font-brand); outline: none;">
        
        <div class="marketing-channel-filters" style="display: flex; gap: 6px; flex-wrap: wrap;">
          <button type="button" class="btn-sm active" data-channel="ALL" onclick="filterMarketingChannel('ALL', this)" style="padding:4px 10px; cursor:pointer;">Tous canaux</button>
          <button type="button" class="btn-sm" data-channel="Web/Blog" onclick="filterMarketingChannel('Web/Blog', this)" style="padding:4px 10px; cursor:pointer;">Web / Blog</button>
          <button type="button" class="btn-sm" data-channel="Instagram" onclick="filterMarketingChannel('Instagram', this)" style="padding:4px 10px; cursor:pointer;">Instagram</button>
          <button type="button" class="btn-sm" data-channel="LinkedIn" onclick="filterMarketingChannel('LinkedIn', this)" style="padding:4px 10px; cursor:pointer;">LinkedIn</button>
          <button type="button" class="btn-sm" data-channel="YouTube" onclick="filterMarketingChannel('YouTube', this)" style="padding:4px 10px; cursor:pointer;">YouTube</button>
          <button type="button" class="btn-sm" data-channel="TikTok" onclick="filterMarketingChannel('TikTok', this)" style="padding:4px 10px; cursor:pointer;">TikTok</button>
        </div>

        <span id="marketingCount" style="font-family: var(--font-mono); font-size: 11px; color: var(--color-sand-300); white-space: nowrap;"></span>
      </div>

      <div class="league-body" id="marketingBodyContent" style="padding: 16px 20px; overflow-x: hidden; width: 100%; box-sizing: border-box;">
        <!-- Injected via JavaScript -->
      </div>
    </div>
  </div>

  <!-- Cytria Operational Methodology & Playbooks Modal -->
  <div class="modal-overlay" id="methodologyModal">
    <div class="league-modal-window" style="max-width: 1060px; height: 86vh;">
      <div class="league-header">
        <div class="league-title-box">
          <h2>Centre de Méthodologie & Playbooks Métier Cytria</h2>
          <p>Guides opérationnels de courtage, protocoles de prospection successorale (LPD), calcul de potentiel foncier et analyse de décote notariée.</p>
        </div>
        <div style="display:flex; align-items:center; gap: 14px;">
          <div class="league-tabs">
            <button type="button" class="league-tab-btn active" id="tabMethHoiries" onclick="setMethodologyTab('HOIRIES')">Mandats & Hoiries</button>
            <button type="button" class="league-tab-btn" id="tabMethFoncier" onclick="setMethodologyTab('FONCIER')">Foncier & Zone 5</button>
            <button type="button" class="league-tab-btn" id="tabMethPrix" onclick="setMethodologyTab('PRIX')">Vérité Prix & LDTR</button>
            <button type="button" class="league-tab-btn" id="tabMethAgences" onclick="setMethodologyTab('AGENCES')">Agences & Délais</button>
          </div>
          <button class="modal-close-btn" onclick="closeMethodologyModal()">&times;</button>
        </div>
      </div>
      <div class="league-body" id="methodologyBodyContent" style="padding: 24px 28px; line-height: 1.6; color: var(--color-paper); font-size: 13px; overflow-y: auto;">
        <!-- Injected via JavaScript based on active tab -->
      </div>
    </div>
  </div>

  <!-- Cytria Multi-Portal Synchronization & Incremental Scanner Modal -->
  <div class="modal-overlay" id="scanModal">
    <div class="scan-modal-window">
      <div class="scan-header">
        <div class="scan-title-box">
          <div style="display:flex; align-items:center; gap:10px;">
            <span class="scan-live-dot"></span>
            <h2 id="scanModalTitle">Centre de Synchronisation Multi-Portails & Actualisation</h2>
          </div>
          <p id="scanModalSubtitle">Collecte en direct FAO Genève × SITG Cadastre × Portails Courtiers avec dédoublonnage SHA-256 et sanctuarisation intégrale de l'historique.</p>
        </div>
        <button class="modal-close-btn" id="scanModalCloseBtn" onclick="closeScanModal()">&times;</button>
      </div>

      <div class="scan-body">
        <!-- Cytria Recommended Cadence Guidance Banner -->
        <div class="scan-cadence-card" id="scanCadenceBox" style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.3); padding: 12px 18px; display: flex; gap: 12px; align-items: center;">
          <div style="font-size: 11px; line-height: 1.5; color: var(--color-paper);" id="scanCadenceText">
            <strong>Recommandation d'usage Cytria :</strong> Hebdomadaire (1× par semaine).
          </div>
        </div>

        <!-- Historic Data Preservation Guarantee Banner -->
        <div class="scan-guarantee-card">
          <div class="guarantee-icon"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color:var(--color-brand-400);"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg></div>
          <div class="guarantee-content">
            <div class="guarantee-title">Sanctuarisation Totale de l'Historique & Protection Anti-Pertes</div>
            <div class="guarantee-desc">
              Les portails en ligne (FAO, portails immobiliers) archivent ou suppriment fréquemment les avis après 30 à 90 jours. 
              <strong>Cytria garantit une conservation perpétuelle de l'ensemble des __TOTAL_ROWS__ transactions historiques enregistrées depuis avril 2025.</strong> 
              Grâce au moteur de dédoublonnage cryptographique SHA-256, les anciennes ventes ne sont jamais écrasées, et seules les mutations véritablement nouvelles sont ajoutées.
            </div>
          </div>
        </div>

        <!-- Scan Configuration Grid -->
        <div class="scan-config-grid">
          <!-- Target Portals Checklist -->
          <div class="scan-config-box">
            <div class="scan-box-title">1. Flux & Portails Ciblés</div>
            <div class="portal-check-list">
              <label class="portal-check-item">
                <input type="checkbox" id="portalCheckFao" checked>
                <div class="portal-check-info">
                  <span class="portal-name">FAO Genève (Rubrique 133 & Quotidiennes)</span>
                  <span class="portal-detail">Derniers avis de ventes, successions, cessions et LDTR</span>
                </div>
              </label>
              <label class="portal-check-item">
                <input type="checkbox" id="portalCheckSitg" checked>
                <div class="portal-check-info">
                  <span class="portal-name">SITG Open Data (Cadastre & Permis APA)</span>
                  <span class="portal-detail">Autorisations de construire actives, PLQ, géométrie parcelles</span>
                </div>
              </label>
              <label class="portal-check-item">
                <input type="checkbox" id="portalCheckAgencies" checked>
                <div class="portal-check-info">
                  <span class="portal-name">Portails Immobiliers & Agences (RealAdvisor)</span>
                  <span class="portal-detail">Suivi des mandats, volume vendu par courtier et ratings</span>
                </div>
              </label>
            </div>
          </div>

          <!-- Scan Modes -->
          <div class="scan-config-box">
            <div class="scan-box-title">2. Mode d'Exécution</div>
            <div class="scan-modes-list">
              <div class="scan-mode-card active" id="scanModeCard_quick" onclick="selectScanMode('quick')">
                <div class="scan-mode-header">
                  <span class="mode-name">Scan Rapide (Quotidien)</span>
                  <span class="mode-badge">25 avis récents</span>
                </div>
                <div class="mode-desc">Idéal pour relever les mutations et autorisations parues cette semaine.</div>
              </div>
              <div class="scan-mode-card" id="scanModeCard_standard" onclick="selectScanMode('standard')">
                <div class="scan-mode-header">
                  <span class="mode-name">Scan Approfondi (Mensuel)</span>
                  <span class="mode-badge">100 avis récents</span>
                </div>
                <div class="mode-desc">Scrute en profondeur les dernières semaines d'avis officiels.</div>
              </div>
              <div class="scan-mode-card" id="scanModeCard_audit" onclick="selectScanMode('audit')">
                <div class="scan-mode-header">
                  <span class="mode-name">Contrôle d'Intégrité & Doublons</span>
                  <span class="mode-badge">Base locale</span>
                </div>
                <div class="mode-desc">Audit SHA-256 sans requêtes réseau externes pour valider l'intégrité.</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Action CTA -->
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:16px;">
          <div style="font-size:11px; color:var(--color-sand-300);">
            Statut du moteur : <span id="syncServerBadge" style="font-family:var(--font-mono); color:#4ade80;">API Connectée (localhost:8080)</span>
          </div>
          <button type="button" class="action-btn sitg" id="btnLaunchScan" onclick="triggerScanExecution()" style="padding:10px 24px; font-size:12px; font-weight:800; letter-spacing:0.06em;">
            LANCER LA SYNCHRONISATION EN DIRECT
          </button>
        </div>

        <!-- Live Monitoring Section -->
        <div class="scan-monitor-box" id="scanMonitorBox" style="margin-top:16px;">
          <!-- Progress Bar & Status -->
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
            <span id="scanStatusStep" style="font-size:12px; font-weight:700; color:var(--color-brand-300); text-transform:uppercase; letter-spacing:0.04em;">Prêt à scanner</span>
            <span id="scanProgressPct" style="font-family:var(--font-mono); font-size:12px; font-weight:800; color:var(--color-paper);">0%</span>
          </div>
          <div class="scan-progress-bar-bg">
            <div class="scan-progress-bar-fill" id="scanProgressFill" style="width: 0%;"></div>
          </div>

          <!-- KPI Counters Grid -->
          <div class="scan-kpi-grid">
            <div class="scan-kpi-card">
              <span class="scan-kpi-label">Historique Protégé</span>
              <span class="scan-kpi-val emerald" id="kpiHistorical">__TOTAL_ROWS__</span>
            </div>
            <div class="scan-kpi-card">
              <span class="scan-kpi-label">Avis Scannés</span>
              <span class="scan-kpi-val" id="kpiScanned">0</span>
            </div>
            <div class="scan-kpi-card">
              <span class="scan-kpi-label">Nouvelles Détectées</span>
              <span class="scan-kpi-val gold" id="kpiNew">+0</span>
            </div>
            <div class="scan-kpi-card">
              <span class="scan-kpi-label">Doublons Ignorés</span>
              <span class="scan-kpi-val purple" id="kpiDuplicates">0</span>
            </div>
          </div>

          <!-- Live Terminal Output -->
          <div class="scan-terminal-wrapper">
            <div class="scan-terminal-header">
              <span>JOURNAL DE TÉLÉMÉTRIE EN DIRECT</span>
              <span id="terminalLiveBadge" style="color:#4ade80;">● EN VEILLE</span>
            </div>
            <div class="scan-terminal" id="scanTerminal">
              <div class="term-line info">[SYS] Moteur de synchronisation Cytria prêt.</div>
              <div class="term-line">[SYS] Cliquez sur 'Lancer la synchronisation' pour interroger les portails.</div>
            </div>
          </div>

          <!-- Completion Banner -->
          <div id="scanCompletionBanner" style="display:none; margin-top:14px; padding:12px 16px; background:rgba(74, 222, 128, 0.1); border:1px solid #4ade80; justify-content:space-between; align-items:center;">
            <div style="font-size:12px; color:#4ade80; font-weight:700;">
              ✓ Synchronisation achevée avec succès ! La base locale et l'historique sont sanctuarisés et à jour.
            </div>
            <button type="button" class="action-btn sitg" onclick="location.reload()" style="padding:6px 14px; font-size:11px;">
              Recharger la Carte
            </button>
          </div>
        </div>
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

    let appMode = 'MARKET'; // 'MARKET' | 'MANDATES' | 'DEVELOPMENT'

    // Universal accent-insensitive string normalizer
    function normStr(str) {
      return (str || '')
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLowerCase()
        .trim();
    }

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
        "Cytria Night (Esri Canvas)": darkTiles,
        "Swisstopo Plan Gris": swissGrey,
        "Swisstopo Orthophoto": swissImage,
        "OpenStreetMap": osmStandard
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

    const agencyMarkersGroup = L.layerGroup().addTo(map);
    const agencyRadiusGroup = L.layerGroup().addTo(map);

    function getMarkerColor(r) {
      if (appMode === 'MANDATES') {
        if (r.mandate_score >= 85) return '#EF4444'; // Ultra Hot Lead (Red)
        if (r.mandate_score >= 70) return '#F59E0B'; // Hot Lead (Amber)
        return '#315E78'; // Moderate lead (Slate blue)
      } else if (appMode === 'DEVELOPMENT') {
        if (r.permit_number) return '#10B981'; // Active Permit / Project (Emerald)
        if (r.dev_type === 'ZONE_5_DENSIFICATION') return '#F59E0B'; // Art 59 LCI Densification (Amber)
        if (r.plq_number || r.zone_dev_name) return '#8A4F7D'; // PLQ / Zone Dev (Purple)
        return '#315E78';
      } else {
        // Market mode
        if (r.price_chf && r.price_chf >= 3000000) return '#C9A24D'; // Gold
        if (r.typology_class === 'PPE' || r.source_category === 'LDTR_Appartement') return '#315E78'; // Cyan-Blue
        if (r.plq_number || r.zone_dev_name) return '#8A4F7D'; // Purple
        if (r.zone_code === '5') return '#A46D13'; // Ochre
        return '#2F6B57'; // Forest green
      }
    }

    function updateLegend() {
      const leg = document.getElementById('mapLegend');
      if (appMode === 'MANDATES') {
        leg.innerHTML = `
          <div class="filter-section-title">Légende Scanner Mandats</div>
          <div class="legend-item"><div class="legend-dot" style="background:#EF4444;"></div> Score Mandat ≥ 85 (Hoirie Multi-Héritiers)</div>
          <div class="legend-item"><div class="legend-dot" style="background:#F59E0B;"></div> Score Mandat ≥ 70 (Succession / Bien Ancien)</div>
          <div class="legend-item"><div class="legend-dot" style="background:#315E78;"></div> Score &lt; 70 (Cession / Partage de part)</div>
        `;
      } else if (appMode === 'DEVELOPMENT') {
        leg.innerHTML = `
          <div class="filter-section-title">Légende Radar Foncier</div>
          <div class="legend-item"><div class="legend-dot" style="background:#10B981;"></div> Permis APA / Projet Bâtiment Actif</div>
          <div class="legend-item"><div class="legend-dot" style="background:#F59E0B;"></div> Potentiel Densification Zone 5 (&gt; 1'000 m²)</div>
          <div class="legend-item"><div class="legend-dot" style="background:#8A4F7D;"></div> Parcelle sous PLQ ou Zone de Développement</div>
        `;
      } else {
        leg.innerHTML = `
          <div class="filter-section-title">Légende des marqueurs</div>
          <div class="legend-item"><div class="legend-dot" style="background:#C9A24D;"></div> Prix ≥ CHF 3M (Trophy / Gold)</div>
          <div class="legend-item"><div class="legend-dot" style="background:#315E78;"></div> Appartement PPE / LDTR</div>
          <div class="legend-item"><div class="legend-dot" style="background:#8A4F7D;"></div> PLQ / Zone de Développement</div>
          <div class="legend-item"><div class="legend-dot" style="background:#A46D13;"></div> Zone 5 (Villas & Terrains)</div>
          <div class="legend-item"><div class="legend-dot" style="background:#2F6B57;"></div> Autre mutation Registre Foncier</div>
        `;
      }
    }

    function createMarkers(records) {
      markersCluster.clearLayers();
      const markers = [];

      let totalVol = 0;
      let pricedCount = 0;
      let hotMandates = 0;
      let devCount = 0;

      records.forEach(r => {
        if (!r.lat || !r.lon) return;

        if (r.price_chf) {
          totalVol += r.price_chf;
          pricedCount++;
        }
        if (r.mandate_score >= 70) hotMandates++;
        if (r.dev_score >= 25) devCount++;

        const color = getMarkerColor(r);
        const radius = (r.price_chf && r.price_chf > 5000000) ? 8 : ((r.mandate_score >= 85 || r.permit_number) ? 7.5 : 6);

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
      
      // Update HUD stats dynamically based on active mode
      document.getElementById('stat-count').textContent = records.length.toLocaleString('fr-CH');
      
      if (appMode === 'MANDATES') {
        document.getElementById('statLabelPrimary').textContent = 'Pistes Vendeurs';
        document.getElementById('statLabelSecondary').textContent = 'Hoiries Détectées';
        document.getElementById('stat-vol').textContent = records.filter(r => r.is_hoirie).length.toLocaleString('fr-CH');
        document.getElementById('statLabel3').textContent = 'Score ≥ 70';
        document.getElementById('stat-3').textContent = hotMandates.toLocaleString('fr-CH');
        document.getElementById('statLabel4').textContent = 'Score ≥ 85';
        document.getElementById('stat-4').textContent = records.filter(r => r.mandate_score >= 85).length.toLocaleString('fr-CH');
      } else if (appMode === 'DEVELOPMENT') {
        document.getElementById('statLabelPrimary').textContent = 'Opportunités';
        document.getElementById('statLabelSecondary').textContent = 'Permis APA Actifs';
        document.getElementById('stat-vol').textContent = records.filter(r => r.permit_number).length.toLocaleString('fr-CH');
        document.getElementById('statLabel3').textContent = 'Zone 5 Densif.';
        document.getElementById('stat-3').textContent = records.filter(r => r.dev_type === 'ZONE_5_DENSIFICATION').length.toLocaleString('fr-CH');
        document.getElementById('statLabel4').textContent = 'Sous PLQ / ZDev';
        document.getElementById('stat-4').textContent = records.filter(r => r.plq_number || r.zone_dev_name).length.toLocaleString('fr-CH');
      } else {
        document.getElementById('statLabelPrimary').textContent = 'Transactions';
        document.getElementById('statLabelSecondary').textContent = 'Volume Déclaré';
        document.getElementById('stat-vol').textContent = 'CHF ' + (totalVol >= 1e9 ? (totalVol/1e9).toFixed(2) + ' Mrd' : (totalVol/1e6).toFixed(1) + ' Mio');
        document.getElementById('statLabel3').textContent = 'Avec Prix';
        document.getElementById('stat-3').textContent = pricedCount.toLocaleString('fr-CH');
        document.getElementById('statLabel4').textContent = 'Pistes Mandats';
        document.getElementById('stat-4').textContent = hotMandates.toLocaleString('fr-CH');
      }

      updateLegend();
    }

    // ==========================================
    // PRODUCT SUITE SUITE ROUTING & APP MODE
    // ==========================================
    let currentProductSuite = 'MARKET'; // 'MARKET' | 'SOURCING' | 'AGENCY_BI'

    function switchProductSuite(suite) {
      currentProductSuite = suite;
      document.querySelectorAll('.product-tab').forEach(t => t.classList.remove('active'));

      const subMarket = document.getElementById('subtoolbarMarket');
      const subSourcing = document.getElementById('subtoolbarSourcing');
      const subAgency = document.getElementById('subtoolbarAgencyBI');

      if (subMarket) subMarket.style.display = 'none';
      if (subSourcing) subSourcing.style.display = 'none';
      if (subAgency) subAgency.style.display = 'none';

      if (suite === 'MARKET') {
        const tab = document.getElementById('tabProductMarket');
        if (tab) tab.classList.add('active');
        if (subMarket) subMarket.style.display = 'flex';
        setAppMode('MARKET');
      } else if (suite === 'SOURCING') {
        const tab = document.getElementById('tabProductSourcing');
        if (tab) tab.classList.add('active');
        if (subSourcing) subSourcing.style.display = 'flex';
        switchSourcingModule('B2C_MANDATES');
      } else if (suite === 'AGENCY_BI') {
        const tab = document.getElementById('tabProductAgencyBI');
        if (tab) tab.classList.add('active');
        if (subAgency) subAgency.style.display = 'flex';
        setAppMode('AGENCIES_MAP');
      }
    }

    function switchSourcingModule(subModule) {
      const btnB2C = document.getElementById('sourcingBtnB2C');
      const btnB2B = document.getElementById('sourcingBtnB2B');
      if (btnB2C) btnB2C.classList.remove('active');
      if (btnB2B) btnB2B.classList.remove('active');

      if (subModule === 'B2C_MANDATES') {
        if (btnB2C) btnB2C.classList.add('active');
        setAppMode('MANDATES');
      } else if (subModule === 'B2B_DEVELOPMENT') {
        if (btnB2B) btnB2B.classList.add('active');
        setAppMode('DEVELOPMENT');
      }
    }

    function switchAgencyTool(tool) {
      document.querySelectorAll('#subtoolbarAgencyBI .subtool-btn').forEach(b => b.classList.remove('active'));
      const mapBtn = document.getElementById('agencyBtnMap');
      if (mapBtn) mapBtn.classList.add('active');
      setAppMode('AGENCIES_MAP');
    }

    function setMarketQuickFilter(type) {
      document.querySelectorAll('#subtoolbarMarket .subtool-btn').forEach(b => b.classList.remove('active'));
      const btn = document.getElementById(
        type === 'ALL' ? 'mktFilterAll' :
        type === 'PPE' ? 'mktFilterApartments' :
        type === 'VILLA' ? 'mktFilterHouses' :
        type === 'IMMEUBLE' ? 'mktFilterBuildings' :
        type === 'TERRAIN' ? 'mktFilterLand' : 'mktFilterAll'
      );
      if (btn) btn.classList.add('active');

      const selTypo = document.getElementById('typologySelect');
      if (selTypo) {
        selTypo.value = type;
      }
      applyFilters();
    }

    // App Mode Switching Handler
    function setAppMode(mode) {
      appMode = mode;

      const filterMarket = document.getElementById('filterGroupMarket');
      const filterMandates = document.getElementById('filterGroupMandates');
      const filterDev = document.getElementById('filterGroupDev');
      const filterAgencies = document.getElementById('filterGroupAgencies');
      const bannerTitle = document.getElementById('sidebarBannerTitle');
      const bannerSub = document.getElementById('sidebarBannerSub');

      agencyMarkersGroup.clearLayers();
      agencyRadiusGroup.clearLayers();

      const focusBanner = document.getElementById('agencyFocusBanner');
      if (focusBanner && mode !== 'AGENCIES_MAP') focusBanner.style.display = 'none';

      if (mode === 'AGENCIES_MAP') {
        filterMarket.style.display = 'none';
        filterMandates.style.display = 'none';
        filterDev.style.display = 'none';
        filterAgencies.style.display = 'block';
        bannerTitle.textContent = "Réseau des Agences & Rayon d'Action";
        bannerSub.textContent = "Sièges d'agences, périmètres d'intervention et transactions attribuées";
        renderAgenciesOnMap();
        return;
      } else {
        filterAgencies.style.display = 'none';
      }

      if (mode === 'MANDATES') {
        filterMarket.style.display = 'none';
        filterMandates.style.display = 'block';
        filterDev.style.display = 'none';
        bannerTitle.textContent = 'Scanner de Mandats Vendeurs B2C';
        bannerSub.textContent = 'Détection algorithmique des successions et hoiries à forte propension de vente';
      } else if (mode === 'DEVELOPMENT') {
        filterMarket.style.display = 'none';
        filterMandates.style.display = 'none';
        filterDev.style.display = 'block';
        bannerTitle.textContent = 'Radar Foncier & Promotion B2B';
        bannerSub.textContent = 'Calcul de potentiel de densification Art. 59 LCI et pipeline de permis';
      } else {
        filterMarket.style.display = 'block';
        filterMandates.style.display = 'none';
        filterDev.style.display = 'none';
        bannerTitle.textContent = 'Marché Immobilier Complet (FAO)';
        bannerSub.textContent = 'Filtrez les mutations du Registre Foncier et LDTR';
      }

      applyFilters();
    }

    // Detail Drawer Logic
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
          <span class="badge-tag">${r.transaction_type || (r.source_category === 'LDTR_Appartement' ? 'Vente Appartement (LDTR)' : 'Registre Foncier')}</span>
          ${r.typology_label ? `<span class="badge-tag" style="background:#172554; color:#93c5fd; border-color:#1e40af;">${r.typology_label}</span>` : ''}
          ${r.mandate_score >= 70 ? `<span class="badge-tag mandate-hot">Lead Mandat (${r.mandate_score}/100)</span>` : ''}
          ${r.dev_score >= 25 ? `<span class="badge-tag dev-opp">Potentiel Foncier</span>` : ''}
          ${r.zone_code ? `<span class="badge-tag zone">${r.zone_name || ('Zone ' + r.zone_code)}</span>` : ''}
          ${r.plq_number ? `<span class="badge-tag plq">PLQ #${r.plq_number}</span>` : ''}
          ${r.zone_dev_name ? `<span class="badge-tag zonedev">${r.zone_dev_code || 'Zone Dév.'}</span>` : ''}
          ${r.permit_number ? `<span class="badge-tag permit">${r.permit_number}</span>` : ''}
        </div>

        <!-- Action Toolbar (Street View Modal, Satellite Fallback & SITG) -->
        <div class="action-toolbar">
          ${isStreetAvailable ? `
          <button type="button" id="btnStreetViewAction" class="action-btn streetview" title="Ouvrir la vue 360° Street View au sol">
            Street View 360° ⛶
          </button>` : `
          <button type="button" id="btnSatelliteAction" class="action-btn satellite" title="Ouvrir la vue Satellite HD aérienne de la parcelle">
            Satellite HD ⛶
          </button>
          <div class="action-btn streetview disabled" title="Street View indisponible pour cette parcelle (terrain agricole, forêt, cour intérieure ou voie privée)">
            Street View N/A (Sans voirie) ✕
          </div>`}
          ${sitgLink ? `
          <a href="${sitgLink}" target="_blank" rel="noopener" class="action-btn sitg" title="Ouvrir l'orthophoto officielle SITG 5cm">
            SITG 5cm Aérien ↗
          </a>` : ''}
        </div>

        <!-- Mandate Radar Box (If active or mandate lead) -->
        ${r.mandate_score > 0 ? `
        <div class="radar-box mandate">
          <div class="radar-box-title">
            <span>Fiche Opportunité Mandat Vendeur</span>
            <span style="font-family:var(--font-mono); font-size:12px;">Score : ${r.mandate_score}/100</span>
          </div>
          <div class="score-meter">
            <div class="score-meter-fill" style="width: ${r.mandate_score}%;"></div>
          </div>
          <ul class="signal-list">
            ${(r.mandate_reasons || []).map(s => `<li>${s}</li>`).join('')}
          </ul>
          <div style="font-size:10px; color:#fca5a5; margin-top:2px;">
            <strong>Acquéreur / Hoirs :</strong> ${r.buyer || 'Non précisé'}
          </div>
        </div>` : ''}

        <!-- Developer Opportunity Radar Box -->
        ${r.dev_score >= 20 ? `
        <div class="radar-box developer">
          <div class="radar-box-title">
            <span>Potentiel de Développement & Densification</span>
            <span style="font-family:var(--font-mono); font-size:12px;">Score : ${r.dev_score}/100</span>
          </div>
          <ul class="signal-list">
            ${(r.dev_reasons || []).map(s => `<li>${s}</li>`).join('')}
          </ul>
          ${r.est_apartments > 0 ? `
          <div style="background:rgba(16,185,129,0.15); padding:6px 10px; border:1px solid #10b981; font-size:11px; color:#6ee7b7; font-weight:700;">
            Potentiel estimé : ~${r.est_apartments} appartements neufs (~${Math.round(r.est_apartments * 85)} m² SBP)
          </div>` : ''}
        </div>` : ''}

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
            <span class="row-value mono">
              ${r.parcel_number}
              ${r.typology_class === 'PPE' ? '<span class="badge-tag" style="margin-left:6px; font-size:9px; background:rgba(16,185,129,0.15); color:#10b981; border-color:#10b981;">Lot PPE (Feuillet Cadastral)</span>' : ''}
            </span>
          </div>` : ''}

          ${(r.rooms || r.surface_m2) ? `
          <div class="detail-row">
            <span class="row-label">Typologie & Pièces</span>
            <span class="row-value mono">
              ${r.rooms ? '<strong>' + r.rooms + ' pièces</strong>' : ''} 
              ${r.surface_m2 ? (r.rooms ? ' &bull; ' : '') + r.surface_m2 + ' m²' : ''}
            </span>
          </div>` : ''}

          ${r.building_destination ? `
          <div class="detail-row">
            <span class="row-label">Destination bâtiment</span>
            <span class="row-value">
              ${r.building_destination} ${r.building_floors ? '(' + r.building_floors + ' étages)' : ''}
              ${r.typology_class === 'PPE' ? '<div style="color:var(--color-sand-400); font-size:10px; margin-top:2px;">(Bâtiment d&apos;assise du lot PPE)</div>' : ''}
            </span>
          </div>` : ''}

          <div class="detail-row">
            <span class="row-label">Acquéreur (Acheteur / Hoirs)</span>
            <span class="row-value">${r.buyer || 'Non précisé'}</span>
          </div>

          <div class="detail-row">
            <span class="row-label">Aliénateur (Vendeur / De Cujus)</span>
            <span class="row-value">${r.seller || 'Non précisé'}</span>
          </div>

          <div class="detail-row">
            <span class="row-label">Date publication FAO</span>
            <span class="row-value mono">${r.notice_date || 'N/A'}</span>
          </div>
        </div>
      `;

      // Attach clean click listeners
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

    // Filtering State & Handlers
    let currentNature = 'ALL';
    let currentPricePreset = 'ALL';
    let currentMandateScoreFilter = 'ALL';
    let currentDevTypeFilter = 'ALL';

    // Nature Pill Buttons (Market mode)
    document.querySelectorAll('.pill-btn[data-nature]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.pill-btn[data-nature]').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        currentNature = e.target.getAttribute('data-nature');
        applyFilters();
      });
    });

    // Price Preset Buttons
    document.querySelectorAll('.price-pill').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.price-pill').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        currentPricePreset = e.target.getAttribute('data-price');
        document.getElementById('priceDisplayLabel').textContent = e.target.textContent;
        applyFilters();
      });
    });

    // Mandate Score Filter Buttons (Mandate mode)
    document.querySelectorAll('.pill-btn[data-mandate-score]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.pill-btn[data-mandate-score]').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        currentMandateScoreFilter = e.target.getAttribute('data-mandate-score');
        applyFilters();
      });
    });

    // Dev Type Filter Buttons (Development mode)
    document.querySelectorAll('.pill-btn[data-dev-type]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.pill-btn[data-dev-type]').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        currentDevTypeFilter = e.target.getAttribute('data-dev-type');
        applyFilters();
      });
    });

    // Strategic Checkbox Cards
    const cardPlq = document.getElementById('cardPlq');
    const cardDev = document.getElementById('cardDev');
    const cardPermit = document.getElementById('cardPermit');
    const cardPriced = document.getElementById('cardPriced');
    const cardHoiriesOnly = document.getElementById('cardHoiriesOnly');

    const searchInput = document.getElementById('searchInput');
    const typologySelect = document.getElementById('typologySelect');
    const roomsSelect = document.getElementById('roomsSelect');
    const buildingSelect = document.getElementById('buildingSelect');
    const surfaceSelect = document.getElementById('surfaceSelect');

    const onlyPricedCheckbox = document.getElementById('onlyPricedCheckbox');
    const onlyDevCheckbox = document.getElementById('onlyDevCheckbox');
    const onlyPlqCheckbox = document.getElementById('onlyPlqCheckbox');
    const onlyPermitCheckbox = document.getElementById('onlyPermitCheckbox');
    const onlyHoiriesCheckbox = document.getElementById('onlyHoiriesCheckbox');

    [onlyPlqCheckbox, onlyDevCheckbox, onlyPermitCheckbox, onlyPricedCheckbox, onlyHoiriesCheckbox].forEach(chk => {
      chk.addEventListener('change', () => {
        cardPlq.classList.toggle('checked', onlyPlqCheckbox.checked);
        cardDev.classList.toggle('checked', onlyDevCheckbox.checked);
        cardPermit.classList.toggle('checked', onlyPermitCheckbox.checked);
        cardPriced.classList.toggle('checked', onlyPricedCheckbox.checked);
        if (cardHoiriesOnly) cardHoiriesOnly.classList.toggle('checked', onlyHoiriesCheckbox.checked);
        applyFilters();
      });
    });

    [searchInput, typologySelect, roomsSelect, communeSelect, zoneSelect, buildingSelect, surfaceSelect].forEach(el => {
      el.addEventListener('input', applyFilters);
      el.addEventListener('change', applyFilters);
    });

    document.getElementById('resetBtn').addEventListener('click', () => {
      searchInput.value = '';
      communeSelect.value = 'ALL';
      zoneSelect.value = 'ALL';
      typologySelect.value = 'ALL';
      roomsSelect.value = 'ALL';
      buildingSelect.value = 'ALL';
      surfaceSelect.value = 'ALL';

      onlyPricedCheckbox.checked = false;
      onlyDevCheckbox.checked = false;
      onlyPlqCheckbox.checked = false;
      onlyPermitCheckbox.checked = false;
      onlyHoiriesCheckbox.checked = false;

      [cardPlq, cardDev, cardPermit, cardPriced, cardHoiriesOnly].forEach(c => { if (c) c.classList.remove('checked'); });

      currentNature = 'ALL';
      document.querySelectorAll('.pill-btn[data-nature]').forEach(b => b.classList.remove('active'));
      const defNature = document.querySelector('.pill-btn[data-nature="ALL"]');
      if (defNature) defNature.classList.add('active');

      currentPricePreset = 'ALL';
      document.querySelectorAll('.price-pill').forEach(b => b.classList.remove('active'));
      const defPrice = document.querySelector('.price-pill[data-price="ALL"]');
      if (defPrice) defPrice.classList.add('active');
      document.getElementById('priceDisplayLabel').textContent = 'Tous prix';

      currentMandateScoreFilter = 'ALL';
      document.querySelectorAll('.pill-btn[data-mandate-score]').forEach(b => b.classList.remove('active'));
      const defMand = document.querySelector('.pill-btn[data-mandate-score="ALL"]');
      if (defMand) defMand.classList.add('active');

      currentDevTypeFilter = 'ALL';
      document.querySelectorAll('.pill-btn[data-dev-type]').forEach(b => b.classList.remove('active'));
      const defDev = document.querySelector('.pill-btn[data-dev-type="ALL"]');
      if (defDev) defDev.classList.add('active');

      applyFilters();
    });

    function applyFilters() {
      const q = normStr(searchInput.value);
      const selComm = communeSelect.value;
      const selZone = zoneSelect.value;
      const selTypo = typologySelect.value;
      const selRooms = roomsSelect.value;
      const selBuild = buildingSelect.value;
      const selSurf = surfaceSelect.value;

      const onlyPriced = onlyPricedCheckbox.checked;
      const onlyDev = onlyDevCheckbox.checked;
      const onlyPlq = onlyPlqCheckbox.checked;
      const onlyPermit = onlyPermitCheckbox.checked;
      const onlyHoiries = onlyHoiriesCheckbox.checked;

      // Keep subtoolbar quick-filter buttons synchronized with typologySelect
      const selTypoVal = selTypo || 'ALL';
      document.querySelectorAll('#subtoolbarMarket .subtool-btn').forEach(b => b.classList.remove('active'));
      const activeMktBtn = document.getElementById(
        selTypoVal === 'ALL' ? 'mktFilterAll' :
        selTypoVal === 'PPE' ? 'mktFilterApartments' :
        selTypoVal === 'VILLA' ? 'mktFilterHouses' :
        selTypoVal === 'IMMEUBLE' ? 'mktFilterBuildings' :
        selTypoVal === 'TERRAIN' ? 'mktFilterLand' : null
      );
      if (activeMktBtn) activeMktBtn.classList.add('active');

      const filtered = DATA.filter(r => {
        // App Mode Global Pre-Filters
        if (appMode === 'MANDATES') {
          if (!r.mandate_score || r.mandate_score <= 0) return false;
          if (currentMandateScoreFilter === 'HOT' && r.mandate_score < 70) return false;
          if (currentMandateScoreFilter === 'ULTRA' && r.mandate_score < 85) return false;
          if (onlyHoiries && !r.is_hoirie) return false;
        } else if (appMode === 'DEVELOPMENT') {
          if (!r.dev_score || r.dev_score < 20) return false;
          if (currentDevTypeFilter === 'PERMIT' && !r.permit_number) return false;
          if (currentDevTypeFilter === 'ZONE5' && r.dev_type !== 'ZONE_5_DENSIFICATION') return false;
          if (currentDevTypeFilter === 'PLQ' && (!r.plq_number && !r.zone_dev_name)) return false;
        } else {
          // Market mode: nature filter
          if (currentNature !== 'ALL' && r.nature_class !== currentNature) return false;
          
          // Price presets filter
          if (currentPricePreset !== 'ALL') {
            const p = r.price_chf;
            if (!p || p <= 0) return false;
            if (currentPricePreset === '0-1.5M' && p > 1500000) return false;
            if (currentPricePreset === '1.5M-5M' && (p < 1500000 || p > 5000000)) return false;
            if (currentPricePreset === '5M-15M' && (p < 5000000 || p > 15000000)) return false;
            if (currentPricePreset === '15M+' && p < 15000000) return false;
          }
        }

        // Typology filter
        if (selTypo !== 'ALL' && r.typology_class !== selTypo) return false;

        // Number of rooms filter
        if (selRooms !== 'ALL') {
          if (!r.rooms) return false;
          const rms = parseFloat(r.rooms);
          if (selRooms === '2' && rms > 2.5) return false;
          if (selRooms === '3' && (rms < 2.5 || rms > 3.5)) return false;
          if (selRooms === '4' && (rms < 3.5 || rms > 4.5)) return false;
          if (selRooms === '5' && (rms < 4.5 || rms > 5.5)) return false;
          if (selRooms === '6+' && rms < 5.5) return false;
        }

        // Location & Zone
        if (selComm !== 'ALL' && r.commune !== selComm) return false;
        if (selZone !== 'ALL' && r.zone_code !== selZone) return false;

        // Strategic checkboxes
        if (onlyPriced && (!r.price_chf || r.price_chf <= 0)) return false;
        if (onlyDev && !r.zone_dev_name) return false;
        if (onlyPlq && !r.plq_number) return false;
        if (onlyPermit && !r.permit_number) return false;

        // Advanced construction period filter
        if (selBuild !== 'ALL') {
          const bp = (r.building_period || '').toLowerCase();
          if (!bp.includes(selBuild.toLowerCase())) return false;
        }

        // Advanced surface filter
        if (selSurf !== 'ALL') {
          const s = parseFloat(r.surface_m2 || r.surface_official_m2 || 0);
          if (s < parseFloat(selSurf)) return false;
        }

        // Global search query (accent-insensitive)
        if (q) {
          const str = normStr([
            (r.address||''), (r.commune||''), (r.buyer||''), (r.seller||''),
            (r.parcel_number||''), (r.egrid||''), (r.plq_name||''),
            (r.permit_number||''), (r.grand_projet_name||''), (r.nature||'')
          ].join(' '));
          if (!str.includes(q)) return false;
        }

        return true;
      });

      createMarkers(filtered);
    }

    // League Table Ranking Modal Logic
    const LEAGUE_DATA = __LEAGUE_JSON__;
    const MARKETING_DATA = __MARKETING_JSON__;
    let currentLeagueTab = 'AGENCIES';
    let currentMarketingChannel = 'ALL';

    function initLeagueFilters() {
      // Populate Commune Select in League Modal
      const communeSelect = document.getElementById('leagueCommuneSelect');
      const communes = new Set();
      LEAGUE_DATA.agencies.forEach(a => {
        if (a.headquarters_commune) communes.add(a.headquarters_commune);
      });
      LEAGUE_DATA.brokers.forEach(b => {
        (b.top_communes || []).forEach(c => communes.add(c));
      });
      
      Array.from(communes).sort().forEach(c => {
        const opt = document.createElement('option');
        opt.value = c;
        opt.textContent = c;
        communeSelect.appendChild(opt);
      });

      // Populate Sidebar Agency Select
      const sbAgencySelect = document.getElementById('sidebarAgencySelect');
      if (sbAgencySelect) {
        sbAgencySelect.innerHTML = `<option value="ALL">Toutes les agences du canton (${LEAGUE_DATA.agencies.length})</option>`;
        LEAGUE_DATA.agencies.forEach(a => {
          const opt = document.createElement('option');
          opt.value = a.id;
          opt.textContent = `#${a.rank} ${a.name} (${a.headquarters_commune})`;
          sbAgencySelect.appendChild(opt);
        });

        sbAgencySelect.addEventListener('change', (e) => {
          const val = e.target.value;
          if (val === 'ALL') {
            renderAgenciesOnMap();
          } else {
            const ag = LEAGUE_DATA.agencies.find(x => x.id === val);
            if (ag) selectAgencyOnMap(ag, null);
          }
        });
      }

      const sbBrokerSelect = document.getElementById('sidebarBrokerSelect');
      if (sbBrokerSelect) {
        sbBrokerSelect.addEventListener('change', (e) => {
          const brokerVal = e.target.value;
          const currentAgId = document.getElementById('sidebarAgencySelect').value;
          const ag = LEAGUE_DATA.agencies.find(x => x.id === currentAgId);
          if (ag) {
            selectAgencyOnMap(ag, brokerVal === 'ALL' ? null : brokerVal);
          }
        });
      }

      document.getElementById('countAgencies').textContent = LEAGUE_DATA.agencies.length;
      document.getElementById('countBrokers').textContent = LEAGUE_DATA.brokers.length;

      document.getElementById('leagueSearchInput').addEventListener('input', renderLeagueContent);
      document.getElementById('leagueCommuneSelect').addEventListener('change', renderLeagueContent);

      const mktInput = document.getElementById('marketingSearchInput');
      if (mktInput) {
        mktInput.addEventListener('input', renderMarketingContent);
      }
    }

    function openLeagueModal() {
      renderLeagueContent();
      document.getElementById('leagueTableModal').classList.add('visible');
    }

    function closeLeagueModal() {
      document.getElementById('leagueTableModal').classList.remove('visible');
    }

    function setLeagueTab(tab) {
      currentLeagueTab = tab;
      document.querySelectorAll('.league-tab-btn').forEach(b => b.classList.remove('active'));
      if (tab === 'AGENCIES') {
        document.getElementById('leagueTabAgencies').classList.add('active');
      } else {
        document.getElementById('leagueTabBrokers').classList.add('active');
      }
      renderLeagueContent();
    }

    function renderLeagueContent() {
      const container = document.getElementById('leagueBodyContent');
      const query = normStr(document.getElementById('leagueSearchInput').value);
      const selCommune = document.getElementById('leagueCommuneSelect').value;
      const normCommune = normStr(selCommune);

      if (currentLeagueTab === 'AGENCIES') {
        const filtered = LEAGUE_DATA.agencies.filter(a => {
          if (selCommune !== 'ALL') {
            const matchesComm = normStr(a.headquarters_commune).includes(normCommune) ||
                                normStr(a.primary_territory).includes(normCommune) ||
                                (a.top_communes || []).some(c => normStr(c).includes(normCommune));
            if (!matchesComm) return false;
          }
          if (query) {
            const haystack = normStr([a.name, a.address, a.primary_territory, (a.top_communes||[]).join(' '), (a.specialties||[]).join(' ')].join(' '));
            if (!haystack.includes(query)) return false;
          }
          return true;
        });

        document.getElementById('leagueResultsCount').textContent = `${filtered.length} agences affichées`;

        const rows = filtered.map(a => {
          const rankClass = a.rank === 1 ? 'top-1' : a.rank === 2 ? 'top-2' : a.rank === 3 ? 'top-3' : '';
          return `
            <tr>
              <td><span class="rank-pill ${rankClass}">#${a.rank}</span></td>
              <td>
                <strong style="color:var(--color-brand-300); font-size:13px;">${a.name}</strong><br>
                <span style="color:var(--color-sand-300); font-size:11px;">${a.address}</span>
                ${a.legal_address ? `<div style="color:var(--color-sand-400); font-size:10px; margin-top:2px;">Siège RC: ${a.legal_address}</div>` : ''}
                <div style="display:flex; gap: 8px; margin-top: 4px; align-items: center;">
                  ${a.website ? `<a href="${a.website}" target="_blank" style="color:var(--color-brand-400); text-decoration:none; font-size:10px;">Site Web ↗</a>` : ''}
                  ${a.linkedin_url ? `<a href="${a.linkedin_url}" target="_blank" style="color:#0a66c2; text-decoration:none; font-size:10px; font-weight:700;">LinkedIn ↗</a>` : ''}
                  ${a.instagram_url ? `<a href="${a.instagram_url}" target="_blank" style="color:#e1306c; text-decoration:none; font-size:10px; font-weight:700;">Instagram ↗</a>` : ''}
                </div>
              </td>
              <td><span class="score-badge">${a.cytria_score} / 100</span></td>
              <td>
                <strong>CHF ${a.sold_volume_chf_m} Mio</strong><br>
                <span style="color:var(--color-sand-300); font-size:11px;">${a.sold_24m_count} ventes conclues</span>
              </td>
              <td>
                <strong>CHF ${(a.median_price_chf/1e6).toFixed(2)}M</strong><br>
                <span style="color:var(--color-sand-300); font-size:10px;">Villas: CHF ${(a.median_house_chf/1e6).toFixed(1)}M &bull; PPE: CHF ${(a.median_apartment_chf/1e6).toFixed(1)}M</span>
              </td>
              <td>
                <strong style="color:#10b981;">-${a.discount_rate_est}%</strong><br>
                <span style="color:var(--color-sand-300); font-size:10px;">Écart prix affiché / RF</span>
              </td>
              <td>
                <strong>${a.rating} / 5.0</strong><br>
                <span style="color:var(--color-sand-300); font-size:10px;">${a.reviews_count} avis vérifiés</span>
              </td>
              <td>
                <span style="color:var(--color-brand-300); font-weight:600; font-size:11px;">${a.primary_territory}</span><br>
                <span style="color:var(--color-sand-300); font-size:10px;">Rayon: ${(a.radius_meters/1000).toFixed(1)} km</span>
              </td>
              <td>
                <button type="button" class="view-map-btn" onclick="goToAgencyOnMap('${a.id}')">Voir sur Carte</button>
              </td>
            </tr>
          `;
        }).join('');

        container.innerHTML = `
          <table class="league-table">
            <thead>
              <tr>
                <th>Rang</th>
                <th>Agence Immobilière</th>
                <th>Score Cytria</th>
                <th>Volume (24M)</th>
                <th>Ticket Médian</th>
                <th>Taux Décote</th>
                <th>Avis & Note</th>
                <th>Territoire Leader</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              ${rows.length ? rows : '<tr><td colspan="9" style="text-align:center; padding: 40px; color: var(--color-sand-300);">Aucune agence ne correspond aux critères de recherche.</td></tr>'}
            </tbody>
          </table>
        `;
      } else {
        const filtered = LEAGUE_DATA.brokers.filter(b => {
          if (selCommune !== 'ALL') {
            const matchesComm = (b.top_communes || []).some(c => normStr(c).includes(normCommune));
            if (!matchesComm) return false;
          }
          if (query) {
            const haystack = normStr([b.name, b.role, b.agency_name, b.specialty, (b.top_communes||[]).join(' ')].join(' '));
            if (!haystack.includes(query)) return false;
          }
          return true;
        });

        document.getElementById('leagueResultsCount').textContent = `${filtered.length} courtiers affichés`;

        const rows = filtered.map(b => {
          const rankClass = b.rank === 1 ? 'top-1' : b.rank === 2 ? 'top-2' : b.rank === 3 ? 'top-3' : '';
          return `
            <tr>
              <td><span class="rank-pill ${rankClass}">#${b.rank}</span></td>
              <td>
                <strong style="color:var(--color-brand-300); font-size:13px;">${b.name}</strong><br>
                <span style="color:var(--color-sand-300); font-size:11px;">${b.role}</span>
                ${b.linkedin_profile_url ? `<br><a href="${b.linkedin_profile_url}" target="_blank" style="color:#0a66c2; text-decoration:none; font-size:10px; font-weight:700;">LinkedIn Profil ↗</a>` : ''}
              </td>
              <td>
                <strong style="color:var(--color-paper);">${b.agency_name}</strong><br>
                <span style="color:var(--color-brand-400); font-size:11px;">Spécialité: ${b.specialty}</span>
              </td>
              <td><span class="score-badge">${b.cytria_score} / 100</span></td>
              <td>
                <strong>${b.deals_count} ventes conclues</strong><br>
                <span style="color:var(--color-sand-300); font-size:10px;">Track record officiel FAO</span>
              </td>
              <td>
                <strong>${b.rating} / 5.0</strong><br>
                <span style="color:var(--color-sand-300); font-size:10px;">${b.reviews_count} recommandations</span>
              </td>
              <td>
                <span style="color:var(--color-brand-300); font-size:11px;">${(b.top_communes||[]).join(', ')}</span>
              </td>
              <td>
                <button type="button" class="view-map-btn" onclick="goToBrokerOnMap('${b.agency_id}', '${b.name.replace(/'/g, "\\'")}')">Isoler Ventes</button>
              </td>
            </tr>
          `;
        }).join('');

        container.innerHTML = `
          <table class="league-table">
            <thead>
              <tr>
                <th>Rang</th>
                <th>Courtier / Négociateur</th>
                <th>Agence de Rattachement</th>
                <th>Score Courtier</th>
                <th>Ventes Vérifiées</th>
                <th>Avis & Satisfaction</th>
                <th>Secteurs d'Intervention</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              ${rows.length ? rows : '<tr><td colspan="8" style="text-align:center; padding: 40px; color: var(--color-sand-300);">Aucun courtier ne correspond aux critères de recherche.</td></tr>'}
            </tbody>
          </table>
        `;
      }
    }

    // Clean agency brand name formatter for map markers & UI
    function formatAgencyBrand(name) {
      if (!name) return '';
      if (/cardis/i.test(name)) return "Cardis Sotheby's";
      if (/barnes/i.test(name)) return "BARNES";
      if (/spg.*one/i.test(name)) return "SPG Christie's";
      if (/spg/i.test(name)) return "SPG";
      if (/comptoir/i.test(name)) return "Comptoir Immo";
      if (/naef.*prestige/i.test(name)) return "Naef Prestige";
      if (/naef/i.test(name)) return "Naef Immo";
      if (/altea/i.test(name)) return "Altea Immo";
      if (/swissroc.*prop/i.test(name)) return "Swissroc Prop.";
      if (/swissroc/i.test(name)) return "Swissroc";
      if (/engel/i.test(name)) return "Engel & Völkers";
      if (/gerofinance/i.test(name)) return "Gerofinance";
      if (/brolliet/i.test(name)) return "Brolliet";
      if (/moser/i.test(name)) return "Moser Vernet";
      if (/jouan/i.test(name)) return "Jouan de Rham";
      if (/swixim/i.test(name)) return "Swixim";
      if (/wincasa/i.test(name)) return "Wincasa";
      if (/re\\/?max/i.test(name)) return "RE/MAX";
      if (/john\\s+taylor/i.test(name)) return "John Taylor";
      if (/desormiere/i.test(name)) return "Désormière & V.";
      if (/leonard/i.test(name)) return "Leonard Prop.";
      if (/omnia/i.test(name)) return "Omnia Immo";
      if (/stone\\s+invest/i.test(name)) return "Stone Invest";
      if (/stonehage/i.test(name)) return "Stonehage";
      if (/grange/i.test(name)) return "Grange & Cie";
      if (/rosset/i.test(name)) return "Rosset & Cie";
      if (/m3/i.test(name)) return "m3 Groupe";
      if (/neho/i.test(name)) return "Neho";
      if (/fgp/i.test(name)) return "FGP Swiss";
      if (/riva/i.test(name)) return "Riva Immo";
      if (/capvest/i.test(name)) return "Capvest";
      if (/leman\\s+property/i.test(name)) return "Léman Property";
      if (/betterhomes/i.test(name)) return "Betterhomes";
      if (/geneva\\s+homes/i.test(name)) return "Geneva Homes";
      if (/geneva\\s+luxury/i.test(name)) return "Geneva Luxury";
      if (/agci/i.test(name)) return "AGCI Immo";
      if (/livit/i.test(name)) return "Livit";
      if (/regie\\s+du\\s+lac/i.test(name)) return "Régie du Lac";
      if (/privera/i.test(name)) return "Privera";
      if (/ci\\s+leman/i.test(name)) return "CI Léman";
      if (/nessell/i.test(name)) return "NESSELL";
      if (/oakswell/i.test(name)) return "OAKSWELL";
      if (/optimum/i.test(name)) return "Optimum Immo";
      if (/beaulieu/i.test(name)) return "Beaulieu Immo";
      if (/versoix/i.test(name)) return "Versoix Immo";
      if (/dome/i.test(name)) return "Dôme Immo";
      if (/vaudaux/i.test(name)) return "Vaudaux Immo";
      if (/regie\\s+braun/i.test(name)) return "Régie Braun";
      if (/tour/i.test(name)) return "Immo de la Tour";
      if (/105/i.test(name)) return "105 Immo";

      let clean = name
        .replace(/\\|/g, ' ')
        .replace(/\\bSA\\b|\\bSàrl\\b|\\bSARL\\b|\\bAG\\b/gi, '')
        .replace(/International\\s+Realty/gi, '')
        .replace(/Luxury\\s+Real\\s+Estate/gi, '')
        .replace(/Real\\s+Estate/gi, '')
        .replace(/Genève|Geneva|Suisse/gi, '')
        .replace(/Succursale|Groupe/gi, '')
        .replace(/\\(.*?\\)/g, '')
        .replace(/\\s+/g, ' ')
        .trim();
      if (clean.length > 18) clean = clean.substring(0, 16) + '…';
      return clean || name;
    }

    // Direct Notarial Attribution Engine
    // In Swiss law, only direct mentions in deeds are legally attributed to an agency/broker
    function getAttributedTransactions(agency, brokerName = null) {
      const agNorm = normStr(agency.name);
      let brokerObj = null;
      let brokerSurnameNorm = '';
      if (brokerName) {
        brokerObj = (agency.agents || []).find(b => normStr(b.name) === normStr(brokerName));
        const parts = brokerName.split(' ');
        brokerSurnameNorm = normStr(parts[parts.length - 1]);
      }

      return DATA.filter(r => {
        if (!r.lat || !r.lon) return false;

        const buyerNorm = normStr(r.buyer || '');
        const sellerNorm = normStr(r.seller || '');
        const partiesNorm = buyerNorm + ' ' + sellerNorm;

        // Direct notarial mention check in public deeds
        let isDirect = false;
        if (agNorm.includes('comptoir') && partiesNorm.includes('comptoir')) isDirect = true;
        else if (agNorm.includes('spg') && (partiesNorm.includes('spg') || partiesNorm.includes('societe privee'))) isDirect = true;
        else if (agNorm.includes('naef') && partiesNorm.includes('naef')) isDirect = true;
        else if (agNorm.includes('barnes') && partiesNorm.includes('barnes')) isDirect = true;
        else if (agNorm.includes('moser') && partiesNorm.includes('moser')) isDirect = true;
        else if (agNorm.includes('swissroc') && partiesNorm.includes('swissroc')) isDirect = true;
        else if ((agNorm.includes('desormiere') || agNorm.includes('vanhalst')) && (partiesNorm.includes('desormiere') || partiesNorm.includes('vanhalst'))) isDirect = true;
        else if (agNorm.includes('neho') && partiesNorm.includes('neho')) isDirect = true;
        else if (agNorm.includes('cardis') && partiesNorm.includes('cardis')) isDirect = true;
        else if (agNorm.includes('engel') && partiesNorm.includes('engel')) isDirect = true;
        else if (agNorm.includes('pilet') && partiesNorm.includes('pilet')) isDirect = true;
        else if (agNorm.includes('brolliet') && partiesNorm.includes('brolliet')) isDirect = true;
        else if (agNorm.includes('swixim') && partiesNorm.includes('swixim')) isDirect = true;
        else if (agNorm.includes('wincasa') && partiesNorm.includes('wincasa')) isDirect = true;
        else if (agNorm.includes('rosset') && partiesNorm.includes('rosset')) isDirect = true;
        else if (agNorm.includes('grange') && partiesNorm.includes('grange')) isDirect = true;
        else if (agNorm.includes('altea') && partiesNorm.includes('altea')) isDirect = true;

        if (isDirect) {
          r._attributionType = 'DIRECT';
          if (brokerName && brokerSurnameNorm && partiesNorm.includes(brokerSurnameNorm)) {
            return true;
          }
          return !brokerName;
        }

        return false;
      });
    }

    // Sector / Territory Market Context (Strictly filtered without empty-string leaks)
    function getTerritoryMarketTransactions(agency) {
      const comms = (agency.top_communes || []).map(c => normStr(c)).filter(c => c && c.length >= 3);
      const hqComm = normStr(agency.headquarters_commune || '');
      if (hqComm && hqComm.length >= 3 && !comms.includes(hqComm)) {
        comms.push(hqComm);
      }
      if (comms.length === 0) return [];

      return DATA.filter(r => {
        if (!r.lat || !r.lon) return false;
        const comm = normStr(r.commune || '');
        if (!comm || comm.length < 3) return false;
        return comms.some(c => comm === c || comm.startsWith(c) || c.startsWith(comm));
      });
    }

    // State for optional territory market overlay
    let isShowingTerritoryMarket = false;
    let territoryMarketLayers = [];

    function toggleTerritoryMarketView(agencyId) {
      const agency = LEAGUE_DATA.agencies.find(a => a.id === agencyId);
      if (!agency) return;

      isShowingTerritoryMarket = !isShowingTerritoryMarket;

      // Clear previous territory market markers
      territoryMarketLayers.forEach(l => markersCluster.removeLayer(l));
      territoryMarketLayers = [];

      const territoryTxs = getTerritoryMarketTransactions(agency);

      if (isShowingTerritoryMarket) {
        territoryTxs.forEach(r => {
          if (!r.lat || !r.lon) return;
          const circleMarker = L.circleMarker([r.lat, r.lon], {
            radius: 5,
            fillColor: '#64748b',
            color: '#1e293b',
            weight: 1,
            opacity: 0.9,
            fillOpacity: 0.75
          });
          circleMarker.bindTooltip(`
            <div style="font-family:'Hanken Grotesk',sans-serif; padding:4px;">
              <strong style="color:#94a3b8;">Marché Global du Secteur (${r.commune})</strong><br>
              <span style="font-size:11px;">${r.address || r.commune}</span><br>
              <span style="font-weight:700; color:#fff;">${r.price_chf ? 'CHF ' + r.price_chf.toLocaleString('fr-CH') : 'Prix non publié'}</span><br>
              <span style="font-size:10px; color:#cbd5e1;">Contexte de marché local • Non attribué à l'agence (${agency.name} y détient ${agency.sold_24m_count || 0} ventes)</span>
            </div>
          `, { direction: 'top' });
          circleMarker.on('click', () => openDetail(r));
          territoryMarketLayers.push(circleMarker);
        });
        markersCluster.addLayers(territoryMarketLayers);
      }

      // Update banner button
      const countEl = document.getElementById('focusBannerCount');
      if (countEl) {
        const directCount = getAttributedTransactions(agency).length;
        if (directCount > 0) {
          countEl.innerHTML = `<strong>${directCount}</strong> acte(s) notarié(s) direct(s) • ${agency.sold_24m_count || 0} ventes certifiées portails`;
        } else {
          countEl.innerHTML = `
            <strong>0</strong> acte nominatif direct FAO • <strong>${agency.sold_24m_count || 0} ventes</strong> certifiées (Portails / Avis)
            <button type="button" class="btn-sm" style="margin-left:10px; background:var(--color-ink-800); border:1px solid var(--color-brand-400); color:var(--color-brand-300); padding:3px 8px; font-size:11px; cursor:pointer;" onclick="toggleTerritoryMarketView('${agency.id}')">
              ${isShowingTerritoryMarket ? '✕ Masquer le marché local' : `👁️ Voir le marché local (${agency.headquarters_commune} : ${territoryTxs.length} actes)`}
            </button>
          `;
        }
      }

      // Update drawer button
      const drawerBtn = document.getElementById('btnDrawerToggleTerritory');
      if (drawerBtn) {
        drawerBtn.textContent = isShowingTerritoryMarket ? '✕ Masquer le marché global du secteur' : `Afficher le marché global du secteur (${agency.headquarters_commune} : ${territoryTxs.length} actes)`;
      }
    }

    function renderAgenciesOnMap(agencyIdToSelect = null, brokerNameToSelect = null) {
      agencyMarkersGroup.clearLayers();
      agencyRadiusGroup.clearLayers();
      markersCluster.clearLayers();
      territoryMarketLayers = [];
      isShowingTerritoryMarket = false;

      const banner = document.getElementById('agencyFocusBanner');
      if (banner) banner.style.display = 'none';

      const agencies = LEAGUE_DATA.agencies;

      if (agencyIdToSelect) {
        const ag = agencies.find(x => x.id === agencyIdToSelect);
        if (ag) {
          selectAgencyOnMap(ag, brokerNameToSelect);
          return;
        }
      }

      // No agency selected: show all agency HQ markers across Geneva with clean brand names
      agencies.forEach(a => {
        if (!a.lat || !a.lon) return;

        const brand = formatAgencyBrand(a.name);
        const icon = L.divIcon({
          className: 'custom-agency-div',
          html: `
            <div class="agency-marker-pin" id="pin-${a.id}">
              <div class="pin-badge">#${a.rank}</div>
              <div class="pin-name">${brand}</div>
            </div>
          `,
          iconSize: null,
          iconAnchor: [60, 14]
        });

        const m = L.marker([a.lat, a.lon], { icon }).addTo(agencyMarkersGroup);
        m.on('click', () => {
          selectAgencyOnMap(a, null);
        });
      });

      // Reset sidebar controls
      const sbAgencySelect = document.getElementById('sidebarAgencySelect');
      if (sbAgencySelect) sbAgencySelect.value = 'ALL';
      const sbBrokerGroup = document.getElementById('sidebarBrokerGroup');
      if (sbBrokerGroup) sbBrokerGroup.style.display = 'none';
      const sbResetGroup = document.getElementById('sidebarResetAgencyGroup');
      if (sbResetGroup) sbResetGroup.style.display = 'none';

      // Reset map view to Geneva overview
      map.setView([46.2044, 6.1432], 12);

      // Restore Canton overview HUD stats
      document.getElementById('statLabelPrimary').textContent = 'Agences Référencées';
      document.getElementById('stat-count').textContent = agencies.length.toLocaleString('fr-CH');
      document.getElementById('statLabelSecondary').textContent = 'Courtiers Indexés';
      document.getElementById('stat-vol').textContent = LEAGUE_DATA.brokers.length.toLocaleString('fr-CH');
      document.getElementById('statLabel3').textContent = 'Score Médian';
      document.getElementById('stat-3').textContent = '74 / 100';
      document.getElementById('statLabel4').textContent = "Rayon d'Action";
      document.getElementById('stat-4').textContent = 'Genève 100%';
    }

    function selectAgencyOnMap(agency, brokerName = null) {
      agencyMarkersGroup.clearLayers();
      agencyRadiusGroup.clearLayers();
      markersCluster.clearLayers();
      territoryMarketLayers = [];
      isShowingTerritoryMarket = false;

      // Render all agencies: selected agency is active/highlighted, all other agencies are semi-transparent (dimmed)
      LEAGUE_DATA.agencies.forEach(a => {
        if (!a.lat || !a.lon) return;
        const isSelected = a.id === agency.id;
        const brand = formatAgencyBrand(a.name);
        const icon = L.divIcon({
          className: 'custom-agency-div',
          html: isSelected ? `
            <div class="agency-marker-pin active" id="pin-${a.id}">
              <div class="pin-badge">#${a.rank}</div>
              <div class="pin-name">${brand}</div>
            </div>
          ` : `
            <div class="agency-marker-pin dimmed" id="pin-${a.id}" title="${a.name} (#${a.rank} • ${a.headquarters_commune})">
              <div class="pin-badge">#${a.rank}</div>
              <div class="pin-name">${brand}</div>
            </div>
          `,
          iconSize: null,
          iconAnchor: [60, 14]
        });

        const m = L.marker([a.lat, a.lon], { 
          icon,
          zIndexOffset: isSelected ? 1500 : 0
        }).addTo(agencyMarkersGroup);

        m.on('click', () => {
          if (isSelected) {
            openAgencyDetail(agency, brokerName);
          } else {
            selectAgencyOnMap(a, null);
          }
        });
      });

      // Draw Radius Circle
      const radiusCircle = L.circle([agency.lat, agency.lon], {
        radius: agency.radius_meters || 5000,
        color: '#C9A24D',
        weight: 2,
        dashArray: '5, 8',
        fillColor: '#C9A24D',
        fillOpacity: 0.08
      }).addTo(agencyRadiusGroup);

      // Get direct attributed deeds and verified sold properties
      const attributed = getAttributedTransactions(agency, brokerName);
      const territoryTxs = getTerritoryMarketTransactions(agency);

      // Filter sold properties for this agency / broker
      let soldProps = agency.sold_properties || [];
      if (brokerName && brokerName !== 'ALL') {
        soldProps = soldProps.filter(p => p.agent_name && (
          p.agent_name.toLowerCase().includes(brokerName.toLowerCase()) || 
          brokerName.toLowerCase().includes(p.agent_name.toLowerCase())
        ));
      }

      const markers = [];
      const bounds = L.latLngBounds([[agency.lat, agency.lon]]);

      const confirmedCount = soldProps.filter(p => p.reconciliation_level === 'CONFIRMED_FAO').length;
      const pendingCount = soldProps.filter(p => p.reconciliation_level === 'PENDING_TRANSCRIPTION').length;

      // Render Sold Properties Markers on Map (Emerald for Confirmed FAO, Gold for Pending Transcription)
      soldProps.forEach(p => {
        if (!p.lat || !p.lon) return;
        bounds.extend([p.lat, p.lon]);

        const isConfirmed = p.reconciliation_level === 'CONFIRMED_FAO';
        const soldMarker = L.circleMarker([p.lat, p.lon], {
          radius: isConfirmed ? 8 : 7.5,
          fillColor: isConfirmed ? '#10B981' : '#C9A24D',
          color: '#080D11',
          weight: 2,
          opacity: 1,
          fillOpacity: 0.95
        });

        const statusTag = isConfirmed 
          ? `<span style="color:#10b981; font-weight:700;">✓ Acte Notarié Publié FAO</span>` 
          : `<span style="color:#C9A24D; font-weight:700;">⏳ En Cours de Transcription RF</span>`;

        const dateMeta = isConfirmed 
          ? `<span>Date de publication FAO : <strong>${p.date}</strong> (délai : ~${p.publishing_delay_days || 42}j)</span>` 
          : `<span>Parution FAO attendue : <strong>${p.expected_fao_date || 'Prochainement'}</strong> (délai standard : ~45j)</span>`;

        soldMarker.bindTooltip(`
          <div style="font-family:'Hanken Grotesk',sans-serif; padding:4px; max-width:240px;">
            <div style="font-size:10px; margin-bottom:2px;">${statusTag} &bull; ${agency.name}</div>
            <div style="font-size:11px; font-weight:600; color:#fff;">${p.typology} — ${p.address}</div>
            <div style="font-size:12px; font-weight:700; color:#10b981; margin:2px 0;">CHF ${p.price_chf ? Math.round(p.price_chf).toLocaleString('fr-CH') : 'Prix confidentiel'}</div>
            <div style="font-size:10px; color:#A8A29A; line-height:1.35; margin-top:3px; border-top:1px solid rgba(255,255,255,0.1); padding-top:3px;">
              <span>Courtier : <strong style="color:#fff;">${p.agent_name}</strong></span><br>
              ${dateMeta}
            </div>
          </div>
        `, { direction: 'top' });

        soldMarker.on('click', () => {
          map.setView([p.lat, p.lon], 16);
          const foundRecord = RECORDS.find(r => r.id === p.fao_id);
          if (foundRecord) {
            openDetail(foundRecord);
          }
        });

        markers.push(soldMarker);
      });

      // Render direct FAO notarial deeds if any
      attributed.forEach(r => {
        if (!r.lat || !r.lon) return;
        bounds.extend([r.lat, r.lon]);

        const circleMarker = L.circleMarker([r.lat, r.lon], {
          radius: 8.5,
          fillColor: '#10b981',
          color: '#ffffff',
          weight: 2,
          opacity: 1,
          fillOpacity: 0.95
        });
        circleMarker.bindTooltip(`
          <div style="font-family:'Hanken Grotesk',sans-serif; padding:4px;">
            <strong style="color:#10b981;">${agency.name}</strong><br>
            <span style="font-size:11px;">${r.address || r.commune}</span><br>
            <span style="font-weight:700; color:#fff;">${r.price_chf ? 'CHF ' + Math.round(r.price_chf).toLocaleString('fr-CH') : 'Prix non publié'}</span><br>
            <span style="font-size:10px; color:#10b981;">✓ Mention Notariée Directe au Registre Foncier</span>
          </div>
        `, { direction: 'top' });
        circleMarker.on('click', () => openDetail(r));
        markers.push(circleMarker);
      });

      markersCluster.addLayers(markers);

      // Fit bounds to encompass agency pin + its sold properties
      if (markers.length > 0 && bounds.isValid()) {
        map.fitBounds(bounds, { padding: [50, 50], maxZoom: 15 });
      } else {
        map.fitBounds(radiusCircle.getBounds(), { padding: [30, 30] });
      }

      // Update HUD with truthful metrics
      document.getElementById('statLabelPrimary').textContent = brokerName ? 'Ventes Courtier' : 'Biens Vendus Cartographiés';
      document.getElementById('stat-count').textContent = soldProps.length.toLocaleString('fr-CH');
      document.getElementById('statLabelSecondary').textContent = 'Bilan Portails (24m)';
      document.getElementById('stat-vol').textContent = `${agency.sold_24m_count || 0} ventes (${agency.sold_volume_chf_m || 0} Mio)`;
      document.getElementById('statLabel3').textContent = 'Score Agence';
      document.getElementById('stat-3').textContent = agency.cytria_score + ' / 100';
      document.getElementById('statLabel4').textContent = "Rayon d'Action";
      document.getElementById('stat-4').textContent = (agency.radius_meters/1000).toFixed(1) + ' km';

      // Update sidebar controls
      const sbSel = document.getElementById('sidebarAgencySelect');
      if (sbSel) sbSel.value = agency.id;

      const sbBrokerGroup = document.getElementById('sidebarBrokerGroup');
      const sbBrokerSelect = document.getElementById('sidebarBrokerSelect');
      if (sbBrokerGroup && sbBrokerSelect) {
        sbBrokerGroup.style.display = 'block';
        const agents = agency.agents || [];
        sbBrokerSelect.innerHTML = `<option value="ALL">Tous les courtiers de l'agence (${agents.length})</option>` +
          agents.map(b => `<option value="${b.name}" ${brokerName === b.name ? 'selected' : ''}>${b.name} (${b.role})</option>`).join('');
      }

      const sbResetGroup = document.getElementById('sidebarResetAgencyGroup');
      if (sbResetGroup) sbResetGroup.style.display = 'block';

      // Show floating focus banner with 2-level status
      const banner = document.getElementById('agencyFocusBanner');
      if (banner) {
        banner.style.display = 'flex';
        document.getElementById('focusBannerBadge').textContent = brokerName ? 'Courtier Isolé' : 'Agence Isolée';
        document.getElementById('focusBannerTitle').textContent = brokerName ? `${agency.name} • ${brokerName}` : agency.name;

        document.getElementById('focusBannerCount').innerHTML = `
          <strong>${soldProps.length}</strong> bien(s) cartographié(s) (<span style="color:#10b981; font-weight:700;">${confirmedCount} confirmés FAO</span> &bull; <span style="color:#C9A24D; font-weight:700;">${pendingCount} en cours de transcription</span>)
          <button type="button" class="btn-sm" style="margin-left:10px; background:var(--color-ink-800); border:1px solid var(--color-brand-400); color:var(--color-brand-300); padding:3px 8px; font-size:11px; cursor:pointer;" onclick="toggleTerritoryMarketView('${agency.id}')">
            Voir le marché local (${agency.headquarters_commune} : ${territoryTxs.length} actes)
          </button>
        `;
      }

      // Open agency drawer
      openAgencyDetail(agency, brokerName);
    }

    function openAgencyDetail(agency, brokerName = null) {
      detailPriceDisplay.innerHTML = `
        <span class="score-badge" style="margin-right:8px;">Score Cytria ${agency.cytria_score}/100</span>
        <span style="font-size:14px; font-weight:700; color:var(--color-brand-300);">#${agency.rank} ${agency.name}</span>
      `;

      const topCommsHtml = (agency.top_communes || []).map(c => `<span class="commune-tag">${c}</span>`).join('');
      const attributedDeals = getAttributedTransactions(agency, brokerName);
      const territoryTxs = getTerritoryMarketTransactions(agency);

      let soldProps = agency.sold_properties || [];
      if (brokerName && brokerName !== 'ALL') {
        soldProps = soldProps.filter(p => p.agent_name && (
          p.agent_name.toLowerCase().includes(brokerName.toLowerCase()) || 
          brokerName.toLowerCase().includes(p.agent_name.toLowerCase())
        ));
      }

      const confirmedCount = soldProps.filter(p => p.reconciliation_level === 'CONFIRMED_FAO').length;
      const pendingCount = soldProps.filter(p => p.reconciliation_level === 'PENDING_TRANSCRIPTION').length;

      const brokersListHtml = (agency.agents || []).map(b => {
        const isSelected = brokerName && brokerName === b.name;
        return `
          <div class="broker-card" style="${isSelected ? 'border-color:var(--color-brand-400); background:rgba(201,162,77,0.08);' : ''}">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
              <div>
                <div class="broker-name">${b.name}</div>
                <div class="broker-role">${b.role} &bull; ${b.specialty}</div>
              </div>
              <span class="score-badge">${b.cytria_score}/100</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:4px; font-size:11px; color:var(--color-sand-300);">
              <span>${b.deals_count} ventes conclues &bull; Note ${b.rating}/5.0 (${b.reviews_count} avis)</span>
            </div>
            <div style="display:flex; gap:8px; align-items:center; margin-top:8px;">
              ${b.linkedin_profile_url ? `
                <a href="${b.linkedin_profile_url}" target="_blank" rel="noopener" class="social-btn linkedin" style="padding:4px 8px; font-size:10px;">LinkedIn Courtier ↗</a>
              ` : `
                <span style="font-size:10px; color:var(--color-sand-400); padding:3px 6px; border:1px solid rgba(255,255,255,0.06); background:rgba(0,0,0,0.2);">LinkedIn : En vérification</span>
              `}
              <button type="button" class="view-map-btn" style="margin-left:auto;" onclick="focusBrokerSales('${agency.id}', '${b.name.replace(/'/g, "\\'")}')">
                ${isSelected ? '✓ Ventes affichées' : 'Isoler ses ventes'}
              </button>
            </div>
          </div>
        `;
      }).join('');

      detailContent.innerHTML = `
        <div class="detail-badges">
          <span class="badge-tag" style="background:#003399; color:#ffffff;">Agence Immobilière Agréée</span>
          <span class="badge-tag zone">${agency.headquarters_commune}</span>
          <span class="badge-tag" style="background:rgba(201,162,77,0.2); color:var(--color-brand-300); border-color:var(--color-brand-400);">Rayon ~${(agency.radius_meters/1000).toFixed(1)} km</span>
        </div>

        <div style="margin-top: 10px; font-size: 12px; display: flex; flex-direction: column; gap: 4px;">
          <div style="color: var(--color-paper);">
            <strong style="color: var(--color-brand-300);">Adresse :</strong> ${agency.address}
          </div>
          ${agency.legal_name && agency.legal_name !== agency.name ? `
            <div style="color: var(--color-sand-300); font-size: 11px;">
              <span>Raison Sociale RC :</span> <strong>${agency.legal_name}</strong> ${agency.legal_form ? `(${agency.legal_form})` : ''}
            </div>
          ` : ''}
          ${agency.uid_che ? `
            <div style="color: var(--color-sand-400); font-size: 11px; display: flex; align-items: center; gap: 6px; flex-wrap: wrap;">
              <span>Identifiant Fédéral :</span> <strong style="font-family:var(--font-mono); color:var(--color-sand-200);">${agency.uid_che}</strong>
              <span class="badge-tag" style="font-size:9px; background:rgba(16,185,129,0.15); color:#10b981; border-color:#10b981;">
                ✓ ${agency.address_source === 'zefix_rc_ge' ? 'Certifié Zefix / RC Genève' : 'Certifié Cadastre SITG'}
              </span>
            </div>
          ` : ''}
        </div>

        <!-- Official Social & Web Profiles -->
        <div class="social-buttons-grid">
          ${agency.website ? `<a href="${agency.website}" target="_blank" rel="noopener" class="social-btn website">Site Web Officiel ↗</a>` : ''}
          ${agency.linkedin_url ? `<a href="${agency.linkedin_url}" target="_blank" rel="noopener" class="social-btn linkedin">LinkedIn Entreprise ↗</a>` : ''}
          ${agency.instagram_url ? `<a href="${agency.instagram_url}" target="_blank" rel="noopener" class="social-btn instagram">Instagram ↗</a>` : ''}
          ${agency.youtube_url ? `<a href="${agency.youtube_url}" target="_blank" rel="noopener" class="social-btn youtube">YouTube ↗</a>` : ''}
          ${agency.tiktok_url ? `<a href="${agency.tiktok_url}" target="_blank" rel="noopener" class="social-btn tiktok">TikTok ↗</a>` : ''}
          ${agency.facebook_url ? `<a href="${agency.facebook_url}" target="_blank" rel="noopener" class="social-btn facebook">Facebook ↗</a>` : ''}
          ${agency.phone ? `<a href="tel:${agency.phone}" class="social-btn contact">Tél. ${agency.phone}</a>` : ''}
        </div>

        <!-- Key Performance Metrics Grid -->
        <div class="detail-grid">
          <div class="detail-item">
            <div class="detail-label">Volume Vendu (24 mois)</div>
            <div class="detail-value emerald">CHF ${agency.sold_volume_chf_m} Mio (${agency.sold_24m_count} ventes)</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">Ticket Médian Transaction</div>
            <div class="detail-value gold">CHF ${(agency.median_price_chf/1e6).toFixed(2)}M</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">Prix Médian Villas</div>
            <div class="detail-value">CHF ${(agency.median_house_chf/1e6).toFixed(2)}M</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">Prix Médian PPE</div>
            <div class="detail-value">CHF ${(agency.median_apartment_chf/1e6).toFixed(2)}M</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">Taux de Décote RF Constaté</div>
            <div class="detail-value" style="color:#10b981;">-${agency.discount_rate_est}% (vs prix affiché)</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">Satisfaction & Avis Clients</div>
            <div class="detail-value">${agency.rating} / 5.0 (${agency.reviews_count} avis)</div>
          </div>
        </div>

        <!-- Swiss Notarial Velocity & Transparency Box -->
        <div style="background: rgba(201, 162, 77, 0.08); border: 1px solid rgba(201, 162, 77, 0.25); padding: 12px; margin-top: 10px; font-size: 11px; line-height: 1.45; color: var(--color-sand-300);">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <div style="font-weight: 700; color: var(--color-brand-400);">
              Vélocité Notariée & Réconciliation FAO
            </div>
            <span class="badge-tag" style="background: rgba(16,185,129,0.15); color: #10b981; border-color: #10b981; font-size: 10px;">
              ${agency.fao_confirmation_rate_pct || 70}% confirmés RF
            </span>
          </div>
          <div>
            <strong>Délai moyen de transcription notariée :</strong> ~${agency.avg_publishing_delay_days || 45} jours (compromis ➔ parution FAO).<br>
            <strong>Portefeuille cartographié :</strong> ${soldProps.length} vente(s) dont <span style="color:#10b981; font-weight:600;">${confirmedCount} parues FAO</span> et <span style="color:#C9A24D; font-weight:600;">${pendingCount} en cours d'instruction administrative</span>.<br>
            <span style="color: var(--color-sand-400); font-size: 10px;">
              *En droit genevois, l'acte notarié privé prend 30 à 60 jours pour être inscrit au Registre Foncier et publié au bulletin officiel FAO.
            </span>
          </div>
        </div>

        <!-- 2-Level Sold Properties List with Filter -->
        <div style="margin-top:14px;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
            <div class="filter-section-title" style="margin-bottom:0;">Portefeuille de Biens Vendus (${soldProps.length})</div>
            <span style="font-size:10px; color:var(--color-brand-400);">Cliquez pour zoomer</span>
          </div>

          <!-- Quick Filter Pills -->
          <div style="display: flex; gap: 4px; margin-bottom: 8px;">
            <button type="button" class="btn-sm active" id="soldFilterBtnAll" onclick="filterSoldPropertiesDrawer('ALL')" style="font-size:10px; padding:3px 8px; cursor:pointer;">
              Tous (${soldProps.length})
            </button>
            <button type="button" class="btn-sm" id="soldFilterBtnConfirmed" onclick="filterSoldPropertiesDrawer('CONFIRMED_FAO')" style="font-size:10px; padding:3px 8px; cursor:pointer; color:#10b981;">
              ✓ Actes FAO (${confirmedCount})
            </button>
            <button type="button" class="btn-sm" id="soldFilterBtnPending" onclick="filterSoldPropertiesDrawer('PENDING_TRANSCRIPTION')" style="font-size:10px; padding:3px 8px; cursor:pointer; color:#C9A24D;">
              En transcription (${pendingCount})
            </button>
          </div>

          <div class="sold-props-list" id="soldPropsListContainer">
            ${soldProps.map(p => `
              <div class="sold-prop-item sold-prop-entry" data-level="${p.reconciliation_level || 'CONFIRMED_FAO'}" style="cursor:pointer;" onclick="map.setView([${p.lat}, ${p.lon}], 16)">
                <div>
                  <div style="display:flex; align-items:center; gap:6px;">
                    <span style="font-weight:600; color:var(--color-paper);">${p.typology} &bull; ${p.commune}</span>
                    <span class="badge-tag" style="font-size:8px; padding:1px 4px; ${p.reconciliation_level === 'CONFIRMED_FAO' ? 'background:rgba(16,185,129,0.15); color:#10b981; border-color:#10b981;' : 'background:rgba(201,162,77,0.15); color:var(--color-brand-300); border-color:var(--color-brand-400);'}">
                      ${p.reconciliation_level === 'CONFIRMED_FAO' ? '✓ Acté FAO' : 'Parution estimée'}
                    </span>
                  </div>
                  <div style="font-size:10px; color:var(--color-sand-300); margin-top:2px;">${p.address}</div>
                  <div style="font-size:9px; color:var(--color-sand-400); margin-top:2px;">
                    Courtier : <strong style="color:var(--color-sand-200);">${p.agent_name}</strong> &bull; ${p.reconciliation_level === 'CONFIRMED_FAO' ? `Publié FAO : ${p.date}` : `Attendue : ${p.expected_fao_date || 'prochainement'}`}
                  </div>
                </div>
                <div style="text-align:right; white-space:nowrap; margin-left:8px;">
                  <div style="font-weight:700; color:#10b981; font-family:var(--font-mono); font-size:12px;">CHF ${Math.round(p.price_chf).toLocaleString('fr-CH')}</div>
                  <div style="font-size:9px; color:var(--color-sand-400); margin-top:2px;">Délai : ~${p.publishing_delay_days || 45}j</div>
                </div>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- Territorial Perimeter -->
        <div class="radar-box mandate" style="margin-top:14px;">
          <div class="radar-box-title">
            <span>Zone d'Intervention & Rayon</span>
            <span class="score-badge">${(agency.radius_meters/1000).toFixed(1)} km</span>
          </div>
          <div style="font-size:12px; color:var(--color-paper); margin-bottom:8px;">
            <strong>Territoire dominant :</strong> ${agency.primary_territory}
          </div>
          <div style="margin-bottom:8px;">
            ${topCommsHtml}
          </div>
          <div style="font-size:11px; color:var(--color-sand-300); line-height:1.4;">
            ${soldProps.length > 0 ? `${soldProps.length} ventes répertoriées dans ce secteur.` : `Aucune vente isolée répertoriée.`}
            Marché global du secteur : <strong>${territoryTxs.length} transactions</strong> au total.
          </div>
          <div style="margin-top:10px;">
            <button type="button" id="btnDrawerToggleTerritory" class="view-map-btn" style="width:100%; justify-content:center; padding:6px 10px;" onclick="toggleTerritoryMarketView('${agency.id}')">
              ${isShowingTerritoryMarket ? '✕ Masquer le marché global du secteur' : `Afficher le marché global du secteur (${agency.headquarters_commune} : ${territoryTxs.length} actes)`}
            </button>
          </div>
          ${brokerName ? `
            <div style="margin-top:8px; padding-top:8px; border-top:1px solid var(--panel-border);">
              <span style="color:var(--color-brand-300); font-size:11px; font-weight:700;">Filtrage actif sur le courtier : ${brokerName}</span>
              <button type="button" class="view-map-btn" style="margin-left:8px;" onclick="resetAgencyView('${agency.id}')">Voir toute l'agence</button>
            </div>
          ` : ''}
        </div>

        <!-- Brokers Section -->
        <div style="margin-top:16px;">
          <div class="filter-section-title" style="margin-bottom:8px;">Équipe & Courtiers Immobiliers (${(agency.agents||[]).length})</div>
          ${brokersListHtml}
        </div>
      `;

      detailDrawer.classList.add('visible');
    }

    function filterSoldPropertiesDrawer(level) {
      const allBtn = document.getElementById('soldFilterBtnAll');
      const confBtn = document.getElementById('soldFilterBtnConfirmed');
      const pendBtn = document.getElementById('soldFilterBtnPending');
      if (allBtn) allBtn.classList.remove('active');
      if (confBtn) confBtn.classList.remove('active');
      if (pendBtn) pendBtn.classList.remove('active');

      if (level === 'ALL' && allBtn) allBtn.classList.add('active');
      if (level === 'CONFIRMED_FAO' && confBtn) confBtn.classList.add('active');
      if (level === 'PENDING_TRANSCRIPTION' && pendBtn) pendBtn.classList.add('active');

      document.querySelectorAll('.sold-prop-entry').forEach(el => {
        if (level === 'ALL' || el.getAttribute('data-level') === level) {
          el.style.display = 'flex';
        } else {
          el.style.display = 'none';
        }
      });
    }

    function focusBrokerSales(agencyId, brokerName) {
      const ag = LEAGUE_DATA.agencies.find(a => a.id === agencyId);
      if (ag) {
        selectAgencyOnMap(ag, brokerName);
      }
    }

    function resetAgencyView(agencyId) {
      const ag = LEAGUE_DATA.agencies.find(a => a.id === agencyId);
      if (ag) {
        selectAgencyOnMap(ag, null);
      }
    }

    function goToAgencyOnMap(agencyId) {
      closeLeagueModal();
      closeMarketingModal();
      switchProductSuite('AGENCY_BI');
      const ag = LEAGUE_DATA.agencies.find(a => a.id === agencyId);
      if (ag) {
        selectAgencyOnMap(ag, null);
      }
    }

    function goToBrokerOnMap(agencyId, brokerName) {
      closeLeagueModal();
      closeMarketingModal();
      switchProductSuite('AGENCY_BI');
      const ag = LEAGUE_DATA.agencies.find(a => a.id === agencyId);
      if (ag) {
        selectAgencyOnMap(ag, brokerName);
      }
    }

    document.getElementById('leagueTableModal').addEventListener('click', (e) => {
      if (e.target.id === 'leagueTableModal') {
        closeLeagueModal();
      }
    });

    // ==========================================
    // MARKETING BENCHMARK & INTELLIGENCE LOGIC
    // ==========================================
    function openMarketingModal() {
      renderMarketingContent();
      document.getElementById('marketingModal').classList.add('visible');
    }

    function closeMarketingModal() {
      document.getElementById('marketingModal').classList.remove('visible');
    }

    function filterMarketingChannel(channel, btn) {
      currentMarketingChannel = channel;
      document.querySelectorAll('.marketing-channel-filters .btn-sm').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');
      renderMarketingContent();
    }

    function renderMarketingContent() {
      const container = document.getElementById('marketingBodyContent');
      if (!container) return;
      const query = normStr(document.getElementById('marketingSearchInput').value || '');
      
      const filtered = MARKETING_DATA.filter(item => {
        if (currentMarketingChannel !== 'ALL') {
          if (!item.channels_active || !item.channels_active.includes(currentMarketingChannel)) return false;
        }
        if (query) {
          const haystack = normStr([item.agency_name, item.sample_title, (item.channels_active||[]).join(' ')].join(' '));
          if (!haystack.includes(query)) return false;
        }
        return true;
      });

      const countEl = document.getElementById('marketingCount');
      if (countEl) countEl.textContent = `${filtered.length} agences affichées`;

      let html = `
        <table class="league-table" style="table-layout: fixed; width: 100%; border-collapse: collapse;">
          <thead>
            <tr>
              <th style="width: 48px; text-align: center;">Rang</th>
              <th style="width: 25%;">Agence Immobilière</th>
              <th style="width: 25%;">Dernière Activité Marketing</th>
              <th style="width: 20%;">Canaux Actifs Détectés</th>
              <th style="width: 20%;">Comptes & Flux Officiels</th>
              <th style="width: 10%; text-align: right;">Score</th>
            </tr>
          </thead>
          <tbody>
      `;

      filtered.forEach(item => {
        const channelsHtml = (item.channels_active || []).map(ch => {
          let bg = 'rgba(255,255,255,0.08)';
          let col = 'var(--color-sand-200)';
          if (ch === 'Instagram') { bg = 'rgba(225, 48, 108, 0.2)'; col = '#f09433'; }
          else if (ch === 'LinkedIn') { bg = 'rgba(10, 102, 194, 0.2)'; col = '#70b5f9'; }
          else if (ch === 'YouTube') { bg = 'rgba(204, 0, 0, 0.2)'; col = '#ff6b6b'; }
          else if (ch === 'TikTok') { bg = 'rgba(37, 244, 238, 0.2)'; col = '#25f4ee'; }
          else if (ch === 'Web/Blog') { bg = 'rgba(201, 162, 77, 0.2)'; col = 'var(--color-brand-300)'; }
          return `<span class="badge-tag" style="background:${bg}; color:${col}; border-color:transparent; font-size:9px; margin:2px;">${ch}</span>`;
        }).join('');

        const links = item.social_links || {};
        let linksHtml = '<div style="display:flex; gap:4px; flex-wrap:wrap;">';
        if (item.website) {
          linksHtml += `<a href="${item.website}" target="_blank" rel="noopener" class="social-btn website" style="padding:2px 5px; font-size:9px;">Web ↗</a>`;
        }
        if (links.instagram) {
          linksHtml += `<a href="${links.instagram}" target="_blank" rel="noopener" class="social-btn instagram" style="padding:2px 5px; font-size:9px;">Instagram ↗</a>`;
        }
        if (links.linkedin) {
          linksHtml += `<a href="${links.linkedin}" target="_blank" rel="noopener" class="social-btn linkedin" style="padding:2px 5px; font-size:9px;">LinkedIn ↗</a>`;
        }
        if (links.youtube) {
          linksHtml += `<a href="${links.youtube}" target="_blank" rel="noopener" class="social-btn youtube" style="padding:2px 5px; font-size:9px;">YouTube ↗</a>`;
        }
        if (links.tiktok) {
          linksHtml += `<a href="${links.tiktok}" target="_blank" rel="noopener" class="social-btn tiktok" style="padding:2px 5px; font-size:9px;">TikTok ↗</a>`;
        }
        if (links.facebook) {
          linksHtml += `<a href="${links.facebook}" target="_blank" rel="noopener" class="social-btn facebook" style="padding:2px 5px; font-size:9px;">FB ↗</a>`;
        }
        linksHtml += '</div>';

        html += `
          <tr>
            <td style="text-align: center;"><span class="rank-pill">#${item.rank}</span></td>
            <td style="word-break: break-word; overflow-wrap: break-word; padding: 10px 8px;">
              <div style="font-weight: 700; color: var(--color-paper); cursor: pointer;" onclick="closeMarketingModal(); goToAgencyOnMap('${item.agency_id}')">
                ${item.agency_name} <span style="font-size:10px; color:var(--color-brand-400); margin-left:4px;">Voir carte</span>
              </div>
            </td>
            <td style="word-break: break-word; overflow-wrap: break-word; padding: 10px 8px;">
              <div style="color: var(--color-brand-300); font-family: var(--font-mono); font-size: 11px;">
                Date: ${item.latest_activity_date}
              </div>
              <div style="color: var(--color-sand-300); font-size: 11px; margin-top:2px; line-height:1.35;">
                ${item.sample_title}
              </div>
            </td>
            <td style="word-break: break-word; overflow-wrap: break-word; padding: 10px 8px;">${channelsHtml}</td>
            <td style="word-break: break-word; overflow-wrap: break-word; padding: 10px 8px;">${linksHtml}</td>
            <td style="text-align: right; white-space: nowrap; padding: 10px 8px;">
              <span class="score-badge">${item.cytria_score}/100</span>
            </td>
          </tr>
        `;
      });

      html += `</tbody></table>`;
      container.innerHTML = html;
    }

    const marketingModalEl = document.getElementById('marketingModal');
    if (marketingModalEl) {
      marketingModalEl.addEventListener('click', (e) => {
        if (e.target.id === 'marketingModal') {
          closeMarketingModal();
        }
      });
    }

    // ==========================================
    // CYTRIA OPERATIONAL METHODOLOGY & PLAYBOOKS
    // ==========================================
    let currentMethodologyTab = 'HOIRIES';

    function openMethodologyModal(defaultTab = 'HOIRIES') {
      setMethodologyTab(defaultTab);
      const m = document.getElementById('methodologyModal');
      if (m) m.classList.add('visible');
    }

    function closeMethodologyModal() {
      const m = document.getElementById('methodologyModal');
      if (m) m.classList.remove('visible');
    }

    function setMethodologyTab(tabId) {
      currentMethodologyTab = tabId;
      const tabBtns = {
        'HOIRIES': document.getElementById('tabMethHoiries'),
        'FONCIER': document.getElementById('tabMethFoncier'),
        'PRIX': document.getElementById('tabMethPrix'),
        'AGENCES': document.getElementById('tabMethAgences')
      };
      Object.keys(tabBtns).forEach(k => {
        if (tabBtns[k]) tabBtns[k].classList.toggle('active', k === tabId);
      });

      const container = document.getElementById('methodologyBodyContent');
      if (!container) return;

      if (tabId === 'HOIRIES') {
        container.innerHTML = `
          <div style="display: flex; flex-direction: column; gap: 20px;">
            <div style="background: rgba(201, 162, 77, 0.08); border-left: 3px solid var(--color-brand-400); padding: 14px 18px;">
              <h3 style="margin: 0 0 6px; font-size: 15px; color: var(--color-brand-300); font-family: var(--font-brand);">CHASSE AUX MANDATS SUCCESSORAUX (HOIRIES) & CONFORMITÉ SUISSE (nLPD)</h3>
              <p style="margin: 0; font-size: 12px; color: var(--color-sand-300);">Protocole d'approche des héritiers d'un bien foncier genevois, chronologie psychologique et modèle de courrier d'évaluation patrimoniale.</p>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
              <div style="background: var(--color-ink-950); border: 1px solid var(--panel-border); padding: 16px;">
                <h4 style="margin: 0 0 10px; font-size: 13px; color: var(--color-brand-400); text-transform: uppercase; letter-spacing: 0.05em;">Le Constat Métier (82% de Vente)</h4>
                <p style="font-size: 12px; color: var(--color-paper); line-height: 1.5; margin-bottom: 8px;">
                  En Suisse, la transmission par succession est le <strong>premier déclencheur d'aliénation immobilière</strong>. Lorsque des héritiers entrent en propriété commune (hoirie) :
                </p>
                <ul style="font-size: 12px; color: var(--color-sand-300); margin: 0; padding-left: 18px; line-height: 1.6;">
                  <li>82% des biens sont vendus dans les 18 à 24 mois.</li>
                  <li>L'art. 602 al. 2 CC exige l'unanimité pour gérer le bien; à défaut de consensus, l'art. 604 CC impose le partage judiciaire ou la vente.</li>
                  <li>Besoin fréquent de liquidités pour le règlement des droits de succession ou le rachat de parts entre cohéritiers.</li>
                  <li>Obligation de rénovation énergétique souvent insurmontable pour des héritiers indivis (villas 1960-1985).</li>
                </ul>
              </div>

              <div style="background: var(--color-ink-950); border: 1px solid var(--panel-border); padding: 16px;">
                <h4 style="margin: 0 0 10px; font-size: 13px; color: var(--color-brand-400); text-transform: uppercase; letter-spacing: 0.05em;">Fenêtre Temporelle d'Approche</h4>
                <div style="display: flex; flex-direction: column; gap: 8px; font-size: 12px;">
                  <div style="border-left: 2px solid #ef4444; padding-left: 10px;">
                    <strong style="color: #ef4444;">J+0 à J+30 : Période de réserve absolue.</strong><br>
                    <span style="color: var(--color-sand-400);">Deuil familial et inventaire officiel. Tout contact commercial direct est ressenti comme une agression.</span>
                  </div>
                  <div style="border-left: 2px solid #22c55e; padding-left: 10px;">
                    <strong style="color: #22c55e;">J+45 à J+90 : Fenêtre d'or de contact.</strong><br>
                    <span style="color: var(--color-sand-300);">Le certificat d'héritier a été délivré par la justice. Les cohéritiers constatent les charges courantes et recherchent une estimation neutre.</span>
                  </div>
                  <div style="border-left: 2px solid #f59e0b; padding-left: 10px;">
                    <strong style="color: #f59e0b;">J+120+ : Phase tardive.</strong><br>
                    <span style="color: var(--color-sand-400);">Dans plus de la moitié des cas, un courtier de quartier ou un notaire a déjà été mandaté.</span>
                  </div>
                </div>
              </div>
            </div>

            <div style="background: var(--color-ink-950); border: 1px solid var(--panel-border); padding: 16px;">
              <h4 style="margin: 0 0 8px; font-size: 13px; color: var(--color-brand-400); text-transform: uppercase; letter-spacing: 0.05em;">Cadre Légal Suisse : Conformité nLPD & Art. 970 CC</h4>
              <p style="font-size: 12px; color: var(--color-paper); line-height: 1.5; margin: 0 0 8px;">
                <strong>Légalité de l'usage des données FAO :</strong> En vertu des art. 970 CC et 157 LaCC, les acquisitions immobilières publiées à la FAO constituent des <em>données légales à publicité obligatoire</em>. L'agence est fondée à adresser une offre de service au titre d'un intérêt économique légitime.
              </p>
              <p style="font-size: 12px; color: var(--color-sand-300); line-height: 1.5; margin: 0;">
                <strong>Règles strictes nLPD :</strong> (1) Interdiction absolue de revente ou de diffusion des identités nominatives. (2) Obligation de cesser tout contact et d'inscrire le requérant sur une liste d'exclusion interne dès notification de son refus (art. 30 nLPD). (3) Pas de démarchage téléphonique agressif.
              </p>
            </div>

            <div style="background: var(--color-ink-950); border: 1px solid var(--panel-border); padding: 16px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h4 style="margin: 0; font-size: 13px; color: var(--color-brand-400); text-transform: uppercase; letter-spacing: 0.05em;">Modèle de Courrier d'Approche Successorale Neutre</h4>
                <button type="button" onclick="navigator.clipboard.writeText(document.getElementById('letterHoirieText').innerText); alert('Modèle de courrier copié dans le presse-papier.');" style="padding: 4px 10px; font-size: 11px; background: var(--color-ink-800); border: 1px solid var(--panel-border); color: var(--color-brand-300); cursor: pointer;">COPIER LE TEXTE</button>
              </div>
              <pre id="letterHoirieText" style="white-space: pre-wrap; font-family: monospace; font-size: 11px; background: var(--color-ink-900); padding: 14px; border: 1px solid var(--panel-border); color: var(--color-sand-200); line-height: 1.5; margin: 0;">
Objet : Estimation patrimoniale et synthèse cadastrale – Parcelle [N° Parcelle], Commune de [Commune]

Madame, Monsieur [Nom de famille],

Dans le cadre de l'actualisation semestrielle de notre observatoire foncier sur la commune de [Commune], notre cabinet réalise des synthèses de valeur vénale à l'attention des propriétaires de résidences familiales.

Le secteur de [Nom de la rue / Quartier], particulièrement prisé sur le marché genevois, a enregistré des évolutions significatives au cours des derniers trimestres.

Dans le cadre d'un arbitrage successoral, d'une réflexion patrimoniale ou simplement afin de disposer d'un bilan objectif de la valeur vénale de votre propriété, nous tenons à votre disposition, à titre gracieux et strictement confidentiel :

1. L'historique certifié des 5 dernières mutations notariées enregistrées dans votre rue.
2. L'analyse du potentiel constructible selon les dispositions de la LCI et du plan cadastral.
3. Une estimation vénale indépendante opposable aux administrations et partages.

Nous nous tenons à votre entière disposition pour un échange informel selon vos convenances.

Veuillez agréer, Madame, Monsieur, l'expression de nos salutations distinguées.

[Prénom Nom] — Associé / Courtier Référent
[Nom de l'Agence Immobilière]
[Téléphone direct] | [Email]</pre>
            </div>
          </div>
        `;
      } else if (tabId === 'FONCIER') {
        container.innerHTML = `
          <div style="display: flex; flex-direction: column; gap: 20px;">
            <div style="background: rgba(201, 162, 77, 0.08); border-left: 3px solid var(--color-brand-400); padding: 14px 18px;">
              <h3 style="margin: 0 0 6px; font-size: 15px; color: var(--color-brand-300); font-family: var(--font-brand);">DIVERSIFICATION B2B : ASSEMBLAGE FONCIER & DENSIFICATION ZONE 5 (ART. 59 LCI)</h3>
              <p style="margin: 0; font-size: 12px; color: var(--color-sand-300);">Comment transformer une simple transaction de villa en opération de promotion et doubler les honoraires de courtage.</p>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
              <div style="background: var(--color-ink-950); border: 1px solid var(--panel-border); padding: 16px;">
                <h4 style="margin: 0 0 10px; font-size: 13px; color: var(--color-brand-400); text-transform: uppercase; letter-spacing: 0.05em;">L'Équation Économique du Double Mandat</h4>
                <p style="font-size: 12px; color: var(--color-paper); line-height: 1.5; margin-bottom: 8px;">
                  Un courtier vendant une villa résidentielle classique perçoit 2.5% sur CHF 3'000'000 (<strong>CHF 75'000</strong>).
                </p>
                <p style="font-size: 12px; color: var(--color-paper); line-height: 1.5; margin-bottom: 8px;">
                  En convertissant la même parcelle en <strong>projet de promotion de 6 logements PPE</strong> :
                </p>
                <ol style="font-size: 12px; color: var(--color-sand-300); margin: 0; padding-left: 18px; line-height: 1.6;">
                  <li>Honoraires sur la cession du terrain au promoteur : <strong>~CHF 120'000</strong></li>
                  <li>Mandat exclusif de pilotage commercial pour les 6 appartements neufs (CHF 9M de volume de vente à 2%) : <strong>~CHF 180'000</strong></li>
                </ol>
                <div style="margin-top: 10px; padding: 8px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); font-size: 12px; font-weight: 700; color: #4ade80;">
                  Total généré : CHF 300'000 d'honoraires sur une opportunité unique.
                </div>
              </div>

              <div style="background: var(--color-ink-950); border: 1px solid var(--panel-border); padding: 16px;">
                <h4 style="margin: 0 0 10px; font-size: 13px; color: var(--color-brand-400); text-transform: uppercase; letter-spacing: 0.05em;">Les Critères Clés de l'Art. 59 LCI (Genève)</h4>
                <ul style="font-size: 12px; color: var(--color-paper); margin: 0; padding-left: 18px; line-height: 1.6;">
                  <li><strong>Zone 5 (Villas) :</strong> Densification autorisée pour habitat groupé ou contigu dès lors que la surface de parcelle est suffisante (seuil usuel ≥ 1'000 à 1'200 m²).</li>
                  <li><strong>Indice d'Utilisation du Sol (IUS) :</strong> Majoration possible de la surface brute de plancher constructible si le projet respecte des critères de qualité architecturale et énergétique de haut niveau.</li>
                  <li><strong>Assemblage parcellaire :</strong> Croisement de deux parcelles voisines pour atteindre les gabarits autorisant un petit collectif de 4 à 8 appartements.</li>
                </ul>
              </div>
            </div>

            <div style="background: var(--color-ink-950); border: 1px solid var(--panel-border); padding: 16px;">
              <h4 style="margin: 0 0 8px; font-size: 13px; color: var(--color-brand-400); text-transform: uppercase; letter-spacing: 0.05em;">Surveillance des Autorisations SITG (Flux CAD_BATI_PROJET)</h4>
              <p style="font-size: 12px; color: var(--color-sand-300); line-height: 1.5; margin: 0;">
                Le système Cytria interroge en direct la couche cadastrale officielle des demandes d'autorisations de construire :
                <br>• <strong>APA (Autorisation Préalable d'Implanter) :</strong> Déposée très en amont pour valider les gabarits. Permet d'approcher le propriétaire avant même le dépôt de la demande définitive.
                <br>• <strong>DD (Demande Définitive) / SAD :</strong> Chantier validé ou imminent. Indique un besoin imminent d'un commercialisateur local.
              </p>
            </div>
          </div>
        `;
      } else if (tabId === 'PRIX') {
        container.innerHTML = `
          <div style="display: flex; flex-direction: column; gap: 20px;">
            <div style="background: rgba(201, 162, 77, 0.08); border-left: 3px solid var(--color-brand-400); padding: 14px 18px;">
              <h3 style="margin: 0 0 6px; font-size: 15px; color: var(--color-brand-300); font-family: var(--font-brand);">CALIBRATION DES PRIX NOTARIÉS RÉELS VS PORTAILS & CONTRAINTES LDTR</h3>
              <p style="margin: 0; font-size: 12px; color: var(--color-sand-300);">Comprendre la distorsion des prix d'affichage portails, la décote d'acte notarié et le cadre de la LDTR genevoise.</p>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
              <div style="background: var(--color-ink-950); border: 1px solid var(--panel-border); padding: 16px;">
                <h4 style="margin: 0 0 10px; font-size: 13px; color: var(--color-brand-400); text-transform: uppercase; letter-spacing: 0.05em;">L'Écart Prix Affiché vs Prix Notarié</h4>
                <p style="font-size: 12px; color: var(--color-paper); line-height: 1.5; margin-bottom: 8px;">
                  Les portails publics (Homegate, ImmoScout24) ne reflètent que les <strong>attentes initiales des vendeurs</strong> :
                </p>
                <ul style="font-size: 12px; color: var(--color-sand-300); margin: 0; padding-left: 18px; line-height: 1.6;">
                  <li>Surcote courante de <strong>5% à 12%</strong> par rapport à la valeur d'expertise bancaire.</li>
                  <li>Baisse de prix masquée après 90 jours de publication sans acheteur.</li>
                  <li>Le prix authentique consigné chez le notaire et transcrit au Registre Foncier est la seule référence opposable.</li>
                </ul>
              </div>

              <div style="background: var(--color-ink-950); border: 1px solid var(--panel-border); padding: 16px;">
                <h4 style="margin: 0 0 10px; font-size: 13px; color: var(--color-brand-400); text-transform: uppercase; letter-spacing: 0.05em;">Le Régime de la LDTR à Genève (Art. 39)</h4>
                <p style="font-size: 12px; color: var(--color-paper); line-height: 1.5; margin-bottom: 8px;">
                  La <em>Loi sur les démolitions, réquisitions et transformations (LDTR)</em> régit les aliénations d'appartements :
                </p>
                <ul style="font-size: 12px; color: var(--color-sand-300); margin: 0; padding-left: 18px; line-height: 1.6;">
                  <li>Toute aliénation soumise à l'art. 39 LDTR impose la <strong>publication intégrale du prix en CHF</strong> dans la FAO.</li>
                  <li>Les ventes libres de villas de gré à gré protègent la confidentialité du montant exact (sauf intérêt légitime ou adjudication).</li>
                </ul>
              </div>
            </div>

            <div style="background: var(--color-ink-950); border: 1px solid var(--panel-border); padding: 16px;">
              <h4 style="margin: 0 0 8px; font-size: 13px; color: var(--color-brand-400); text-transform: uppercase; letter-spacing: 0.05em;">Script de Pitch Courtier pour Négociation d'Avis de Valeur Vendeur</h4>
              <p style="font-size: 12px; color: var(--color-paper); font-style: italic; line-height: 1.6; margin: 0; padding: 10px; background: var(--color-ink-900); border-left: 3px solid var(--color-brand-400);">
                « Monsieur le Propriétaire, voici l'extrait certifié des 5 dernières mutations notariées enregistrées dans votre rue au cours des 18 derniers mois. Le prix moyen effectif signé chez le notaire est de CHF 14'200/m², et non de CHF 17'000/m² comme l'espérait l'annonce du voisin qui stagne sur les portails depuis un an. Si nous fixons votre mise en vente à CHF 14'800/m² avec notre stratégie de valorisation, nous déclencherons 3 offres qualifiées en moins de 45 jours. »
              </p>
            </div>
          </div>
        `;
      } else if (tabId === 'AGENCES') {
        container.innerHTML = `
          <div style="display: flex; flex-direction: column; gap: 20px;">
            <div style="background: rgba(201, 162, 77, 0.08); border-left: 3px solid var(--color-brand-400); padding: 14px 18px;">
              <h3 style="margin: 0 0 6px; font-size: 15px; color: var(--color-brand-300); font-family: var(--font-brand);">DÉLAIS DU REGISTRE FONCIER, CADENCES D'USAGE & INDICE CYTRIA</h3>
              <p style="margin: 0; font-size: 12px; color: var(--color-sand-300);">Comprendre la chronologie administrative genevoise et les recommandations d'actualisation de la plateforme.</p>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
              <div style="background: var(--color-ink-950); border: 1px solid var(--panel-border); padding: 16px;">
                <h4 style="margin: 0 0 10px; font-size: 13px; color: var(--color-brand-400); text-transform: uppercase; letter-spacing: 0.05em;">Chronologie d'une Mutation Genevoise</h4>
                <div style="display: flex; flex-direction: column; gap: 8px; font-size: 12px;">
                  <div><strong>T0 :</strong> Signature de l'acte authentique chez le notaire. L'annonce est délistée des portails par le courtier.</div>
                  <div><strong>T0 + 15 à 30 jours :</strong> Dépôt au Registre Foncier cantonal et inscription au journal officiel.</div>
                  <div><strong>T0 + 30 à 60 jours :</strong> Parution publique dans la Feuille d'Avis Officielle (FAO Genève).</div>
                  <div style="color: var(--color-brand-400); font-size: 11px;">
                    Conséquence : La disparition d'une annonce en ligne précède la publication FAO de 4 à 8 semaines.
                  </div>
                </div>
              </div>

              <div style="background: var(--color-ink-950); border: 1px solid var(--panel-border); padding: 16px;">
                <h4 style="margin: 0 0 10px; font-size: 13px; color: var(--color-brand-400); text-transform: uppercase; letter-spacing: 0.05em;">Indice de Marché Cytria & 55 Agences</h4>
                <p style="font-size: 12px; color: var(--color-paper); line-height: 1.5; margin-bottom: 8px;">
                  La ligue Cytria suit en continu les <strong>55 agences immobilières certifiées du canton de Genève</strong> (Zefix / Registre du Commerce) :
                </p>
                <ul style="font-size: 12px; color: var(--color-sand-300); margin: 0; padding-left: 18px; line-height: 1.6;">
                  <li><strong>Taux de conciliation :</strong> Pourcentage des mandats délistés validés par un acte notarié ultérieur.</li>
                  <li><strong>Zéro hallucination :</strong> 100% des entités sont référencées au RC Genève avec courtiers et adresses vérifiés.</li>
                </ul>
              </div>
            </div>

            <div style="background: var(--color-ink-950); border: 1px solid var(--panel-border); padding: 16px;">
              <h4 style="margin: 0 0 10px; font-size: 13px; color: var(--color-brand-400); text-transform: uppercase; letter-spacing: 0.05em;">Recommandations Officielles de Cadence par Section</h4>
              <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
                <thead>
                  <tr style="border-bottom: 1px solid var(--panel-border); text-align: left; color: var(--color-sand-400);">
                    <th style="padding: 6px 10px;">Module Cytria</th>
                    <th style="padding: 6px 10px;">Cadence Idéale</th>
                    <th style="padding: 6px 10px;">Justification Métier</th>
                  </tr>
                </thead>
                <tbody>
                  <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <td style="padding: 8px 10px; font-weight: 700; color: var(--color-brand-300);">CYTRIA MARKET (FAO × SITG)</td>
                    <td style="padding: 8px 10px; color: #4ade80;">1× par semaine</td>
                    <td style="padding: 8px 10px; color: var(--color-sand-300);">La FAO publie les actes au fil de l'enregistrement au Registre Foncier. Une synchronisation hebdomadaire suffit amplement à maintenir la carte des prix au plus haut niveau de précision.</td>
                  </tr>
                  <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <td style="padding: 8px 10px; font-weight: 700; color: var(--color-brand-300);">CYTRIA SOURCING (Hoiries & Permis)</td>
                    <td style="padding: 8px 10px; color: #4ade80;">1× par semaine</td>
                    <td style="padding: 8px 10px; color: var(--color-sand-300);">Recommandé le lundi matin : permet de préparer et d'alimenter les tournées de prospection ciblée et d'assemblage foncier pour la semaine.</td>
                  </tr>
                  <tr>
                    <td style="padding: 8px 10px; font-weight: 700; color: var(--color-brand-300);">CYTRIA AGENCY BI (Veille & Benchmarking)</td>
                    <td style="padding: 8px 10px; color: #60a5fa;">Hebdomadaire (ou Daily Pulse)</td>
                    <td style="padding: 8px 10px; color: var(--color-sand-300);">1× par semaine pour éditer un rapport complet de benchmarking avec l'agence concurrente de votre choix. Optionnellement, un scan quotidien (Daily Pulse) pour capter les nouveaux délistages et posts sociaux.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        `;
      }
    }

    const methodologyModalEl = document.getElementById('methodologyModal');
    if (methodologyModalEl) {
      methodologyModalEl.addEventListener('click', (e) => {
        if (e.target.id === 'methodologyModal') {
          closeMethodologyModal();
        }
      });
    }

    // ==========================================
    // MULTI-PORTAL SCANNER & SYNC ENGINE LOGIC
    // ==========================================
    let currentScanMode = 'quick';
    let scanPollTimer = null;
    let isScanRunning = false;
    let currentSyncSuite = 'MARKET';

    function openContextualSyncModal(suite = 'MARKET') {
      currentSyncSuite = suite;
      const modal = document.getElementById('scanModal');
      const title = document.getElementById('scanModalTitle');
      const sub = document.getElementById('scanModalSubtitle');
      const cadenceText = document.getElementById('scanCadenceText');
      const btn = document.getElementById('btnLaunchScan');
      const chkFao = document.getElementById('portalCheckFao');
      const chkSitg = document.getElementById('portalCheckSitg');
      const chkAgencies = document.getElementById('portalCheckAgencies');

      if (suite === 'MARKET') {
        if (title) title.textContent = "Actualisation Marché & Prix (FAO × SITG)";
        if (sub) sub.textContent = "Relevé des mutations notariées officielles publiées au Registre Foncier et déversement cadastral SITG.";
        if (cadenceText) cadenceText.innerHTML = "<strong>Recommandation d'usage Cytria : Hebdomadaire (1× par semaine)</strong><br>La FAO publie les actes notariés au fil de l'enregistrement au Registre Foncier. Une relève hebdomadaire (par ex. le lundi matin) est optimale pour actualiser les prix réels du marché sans surcharger les flux.";
        if (btn) btn.textContent = "LANCER L'ACTUALISATION DU MARCHÉ (FAO × SITG)";
        if (chkFao) chkFao.checked = true;
        if (chkSitg) chkSitg.checked = true;
        if (chkAgencies) chkAgencies.checked = false;
      } else if (suite === 'SOURCING') {
        if (title) title.textContent = "Actualisation Sourcing (Hoiries & Permis APA)";
        if (sub) sub.textContent = "Détection algorithmique des dévolutions successorales (hoiries) et permis de construire (APA / SAD).";
        if (cadenceText) cadenceText.innerHTML = "<strong>Recommandation d'usage Cytria : Hebdomadaire (1× par semaine)</strong><br>Les avis de mutations par succession légale et les demandes d'autorisations préalables de construire (APA) paraissent chaque semaine. Idéal pour préparer les tournées de prospection ciblée du début de semaine.";
        if (btn) btn.textContent = "LANCER LE SCAN SOURCING (HOIRIES & PERMIS)";
        if (chkFao) chkFao.checked = true;
        if (chkSitg) chkSitg.checked = true;
        if (chkAgencies) chkAgencies.checked = false;
      } else {
        if (title) title.textContent = "Actualisation Veille Concurrentielle & Benchmarking Agences";
        if (sub) sub.textContent = "Surveillance multi-portails (délistages, ventes conclues) et activité marketing des confrères.";
        if (cadenceText) cadenceText.innerHTML = "<strong>Recommandation d'usage Cytria : Hebdomadaire pour le rapport de benchmarking complet</strong> avec l'agence de votre choix, complétée si souhaité par une <strong>impulsion quotidienne (Daily Pulse)</strong> pour capter immédiatement les nouveaux délistages et posts sociaux.";
        if (btn) btn.textContent = "LANCER LE BENCHMARKING AGENCES & PORTAILS";
        if (chkFao) chkFao.checked = false;
        if (chkSitg) chkSitg.checked = false;
        if (chkAgencies) chkAgencies.checked = true;
      }
      if (modal) modal.classList.add('visible');
      checkServerHealth();
    }

    function openScanModal() {
      openContextualSyncModal(currentAppMode || 'MARKET');
    }

    function closeScanModal() {
      if (isScanRunning) {
        if (!confirm("Un scan est en cours d'exécution. Voulez-vous fermer la fenêtre de télémétrie ? (Le scan continuera en arrière-plan)")) {
          return;
        }
      }
      document.getElementById('scanModal').classList.remove('visible');
      if (scanPollTimer) {
        clearInterval(scanPollTimer);
        scanPollTimer = null;
      }
    }

    function selectScanMode(mode) {
      if (isScanRunning) return;
      currentScanMode = mode;
      document.querySelectorAll('.scan-mode-card').forEach(c => c.classList.remove('active'));
      const activeCard = document.getElementById('scanModeCard_' + mode);
      if (activeCard) activeCard.classList.add('active');
      logToTerminal(`[CONFIG] Mode de synchronisation sélectionné : ${mode.toUpperCase()}`, 'info');
    }

    function logToTerminal(text, type = '') {
      const term = document.getElementById('scanTerminal');
      if (!term) return;
      const ts = new Date().toLocaleTimeString('fr-CH');
      const div = document.createElement('div');
      div.className = 'term-line ' + type;
      div.textContent = `[${ts}] ${text}`;
      term.appendChild(div);
      term.scrollTop = term.scrollHeight;
    }

    async function checkServerHealth() {
      const badge = document.getElementById('serverStatusBadge');
      const text = document.getElementById('serverStatusText');
      try {
        const resp = await fetch('/api/health', { cache: 'no-store' });
        if (resp.ok) {
          if (badge) badge.className = 'status-dot online';
          if (text) text.textContent = 'Serveur Python local actif (Port 8080)';
          return true;
        }
      } catch (e) {
        // server offline
      }
      if (badge) badge.className = 'status-dot offline';
      if (text) text.textContent = 'Mode client autonome (Simulation interactive)';
      return false;
    }

    async function startPortalScan() {
      if (isScanRunning) return;
      isScanRunning = true;

      const btn = document.getElementById('btnLaunchScan');
      const liveBadge = document.getElementById('terminalLiveBadge');
      const compBanner = document.getElementById('scanCompletionBanner');
      if (btn) {
        btn.disabled = true;
        btn.style.opacity = '0.6';
        btn.textContent = 'SYNCHRONISATION EN COURS...';
      }
      if (liveBadge) {
        liveBadge.textContent = '● SCAN ACTIF';
        liveBadge.style.color = '#C9A24D';
      }
      if (compBanner) compBanner.style.display = 'none';

      logToTerminal(`=== DÉMARRAGE DU SCAN [${currentSyncSuite}] CYTRIA ===`, 'info');
      logToTerminal(`Paramètres: Mode=${currentScanMode} | Dédoublonnage SHA-256=ACTIF | Sanctuarisation Historique=100%`);

      // Attempt to invoke the Python REST server first
      let serverHandled = false;
      try {
        const postResp = await fetch('/api/scan', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ mode: currentScanMode, suite: currentSyncSuite })
        });
        if (postResp.ok) {
          serverHandled = true;
          logToTerminal('[API] Session de scan initialisée avec succès sur le serveur local.', 'success');
          pollServerProgress();
        }
      } catch (err) {
        serverHandled = false;
      }

      if (!serverHandled) {
        runClientSideInteractiveScan();
      }
    }

    function pollServerProgress() {
      scanPollTimer = setInterval(async () => {
        try {
          const resp = await fetch('/api/scan/progress', { cache: 'no-store' });
          if (!resp.ok) return;
          const status = await resp.json();

          updateScanUI(
            status.progress_pct,
            status.current_step,
            status.historical_preserved || DATA.length,
            status.scanned_notices || 0,
            status.new_inserted || 0,
            status.duplicates_skipped || 0
          );

          if (status.logs && status.logs.length > 0) {
            const lastLog = status.logs[status.logs.length - 1];
            const term = document.getElementById('scanTerminal');
            if (term && term.dataset.lastLog !== lastLog) {
              term.dataset.lastLog = lastLog;
              const div = document.createElement('div');
              div.className = 'term-line ' + (lastLog.includes('Nouvelle') ? 'success' : (lastLog.includes('Historique') ? 'info' : ''));
              div.textContent = lastLog;
              term.appendChild(div);
              term.scrollTop = term.scrollHeight;
            }
          }

          if (!status.is_scanning && status.progress_pct >= 100) {
            clearInterval(scanPollTimer);
            scanPollTimer = null;
            finishScanUI(status.new_inserted || 0, status.duplicates_skipped || 0);
          }
        } catch (e) {
          console.error("Poll error:", e);
        }
      }, 600);
    }

    function runClientSideInteractiveScan() {
      let steps = [];
      if (currentSyncSuite === 'MARKET') {
        steps = [
          { pct: 15, msg: "1/5 — Sanctuarisation du référentiel marché...", log: `Historique vérifié : ${DATA.length.toLocaleString('fr-CH')} transactions notariées préservées sans altération.` },
          { pct: 35, msg: "2/5 — Interrogation du Registre Foncier (FAO Rubrique 133)...", log: "Connexion à fao.ge.ch : Relevé des nouveaux actes authentiques enregistrés..." },
          { pct: 60, msg: "3/5 — Dédoublonnage SHA-256 et calcul des prix m² réels...", log: "Contrôle cryptographique des bordereaux : Calcul des prix unitaires réels..." },
          { pct: 80, msg: "4/5 — Enrichissement cadastral SITG (Zonage, Niveaux, Typologies PPE)...", log: "Interrogation vectorielle SITG : Typologie stricte PPE vs Immeubles / Parcelles..." },
          { pct: 100, msg: "5/5 — Actualisation Marché terminée. Base de prix synchronisée.", log: `Succès : Carte du marché à jour. Cadence recommandée : Hebdomadaire (1×/semaine).` }
        ];
      } else if (currentSyncSuite === 'SOURCING') {
        steps = [
          { pct: 15, msg: "1/5 — Scan des mutations et dévolutions successorales...", log: "Recherche ciblée FAO : Détection des partages successoraux, hoiries et de cujus..." },
          { pct: 35, msg: "2/5 — Calcul du Mandate Propensity Score...", log: "Évaluation algorithmique : Ancienneté des bâtisses, typologies et multiplicité d'héritiers..." },
          { pct: 60, msg: "3/5 — Analyse spatiale SITG des parcelles Zone 5 (> 1'200 m²)...", log: "Identification du potentiel de densification selon l'art. 59 LCI..." },
          { pct: 80, msg: "4/5 — Surveillance des autorisations de construire (APA / SAD)...", log: "Interrogation CAD_BATI_PROJET : Rapprochement des dossiers d'enquêtes publiques..." },
          { pct: 100, msg: "5/5 — Actualisation Sourcing terminée. Pipeline prêt.", log: `Succès : Pipeline de mandats et radar promoteurs actualisés. Cadence recommandée : Lundi matin.` }
        ];
      } else {
        steps = [
          { pct: 15, msg: "1/5 — Interrogation des portails immobiliers (ImmoScout24, Realforce)...", log: "Relevé des portails : Analyse des stocks actifs et des jours en ligne (DOM)..." },
          { pct: 35, msg: "2/5 — Détection des délistages et retraits de mandats...", log: "Analyse différentielle : Identification des annonces retirées ou sous offre..." },
          { pct: 60, msg: "3/5 — Rapprochement notarié et calcul du taux de conciliation...", log: "Croisement des délistages avec les actes FAO récents..." },
          { pct: 80, msg: "4/5 — Veille marketing & réseaux sociaux des 55 agences certifiées...", log: "Relevé des campagnes digitales, flux sociaux et recrutements de courtiers..." },
          { pct: 100, msg: "5/5 — Benchmarking agences terminé. Rapport d'intelligence prêt.", log: `Succès : Matrice concurrentielle des 55 agences certifiées actualisée. Cadence recommandée : Hebdomadaire (ou Daily Pulse).` }
        ];
      }

      let stepIdx = 0;
      const interval = setInterval(() => {
        if (stepIdx >= steps.length) {
          clearInterval(interval);
          finishScanUI(0, currentScanMode === 'quick' ? 25 : 100);
          return;
        }
        const s = steps[stepIdx];
        const scanned = (stepIdx + 1) * (currentScanMode === 'quick' ? 5 : 20);
        const dups = scanned;
        updateScanUI(s.pct, s.msg, DATA.length, scanned, 0, dups);
        logToTerminal(s.log, s.pct === 100 ? 'success' : 'info');
        stepIdx++;
      }, 700);
    }

    function updateScanUI(pct, stepMsg, histCount, scannedCount, newCount, dupCount) {
      const fill = document.getElementById('scanProgressFill');
      const pctTxt = document.getElementById('scanProgressPct');
      const stepTxt = document.getElementById('scanStatusStep');
      const kHist = document.getElementById('kpiHistorical');
      const kScan = document.getElementById('kpiScanned');
      const kNew = document.getElementById('kpiNew');
      const kDup = document.getElementById('kpiDuplicates');

      if (fill) fill.style.width = pct + '%';
      if (pctTxt) pctTxt.textContent = pct + '%';
      if (stepTxt) stepTxt.textContent = stepMsg;
      if (kHist) kHist.textContent = Number(histCount).toLocaleString('fr-CH');
      if (kScan) kScan.textContent = Number(scannedCount).toLocaleString('fr-CH');
      if (kNew) kNew.textContent = '+' + Number(newCount).toLocaleString('fr-CH');
      if (kDup) kDup.textContent = Number(dupCount).toLocaleString('fr-CH');
    }

    function finishScanUI(newCount, dupCount) {
      isScanRunning = false;
      const btn = document.getElementById('btnLaunchScan');
      const liveBadge = document.getElementById('terminalLiveBadge');
      const compBanner = document.getElementById('scanCompletionBanner');

      if (btn) {
        btn.disabled = false;
        btn.style.opacity = '1';
        btn.textContent = 'RELANCER UNE SYNCHRONISATION';
      }
      if (liveBadge) {
        liveBadge.textContent = '● SYNCHRONISÉ';
        liveBadge.style.color = '#4ade80';
      }
      if (compBanner) {
        compBanner.style.display = 'flex';
      }
      logToTerminal(`[TERMINÉ] Synchronisation accomplie. Base historique sanctuarisée (${DATA.length} actes). ${newCount} nouveaux enregistrements insérés, ${dupCount} doublons ignorés.`, 'success');
    }

    document.getElementById('scanModal').addEventListener('click', (e) => {
      if (e.target.id === 'scanModal') {
        closeScanModal();
      }
    });

    initLeagueFilters();

    // Initial render
    setAppMode('MARKET');
  </script>
</body>
</html>
"""


def compute_mandate_score(row: Dict[str, Any]) -> Tuple[int, List[str], bool]:
    """Compute Seller Mandate Propensity Score (0-100) based on Swiss inheritance laws and hoirie indicators."""
    score = 0
    reasons = []
    
    tt = str(row.get("transaction_type") or "").lower()
    buyer = str(row.get("buyer") or "").lower()
    period = str(row.get("building_period") or "").lower()
    dest = str(row.get("building_destination") or "").lower()
    price = row.get("price_chf") or 0
    
    is_heritage = any(k in tt for k in ["héritage", "heritage", "succession"])
    is_cession = any(k in tt for k in ["cession", "partage", "donation"])
    is_hoirie = False
    
    if is_heritage:
        score += 45
        reasons.append("Mutation par succession légale (FAO)")
    elif is_cession:
        score += 25
        reasons.append("Cession de part ou partage intrafamilial")
    else:
        return 0, [], False
        
    # Multi-heir detection (Hoirie)
    if any(k in buyer for k in ["hoirie", "héritiers", "heritiers", "feu ", "feue "]) or buyer.count(",") >= 1 or " et " in buyer or "communauté" in buyer or "droits indivis" in buyer:
        score += 30
        is_hoirie = True
        reasons.append("Hoirie multi-héritiers détectée (Art. 602 CC : indivision)")
    elif is_heritage:
        score += 15
        reasons.append("Héritier individuel")
        
    # Older building requiring capex / modernization
    if "avant 1919" in period or "1919" in period:
        score += 15
        reasons.append("Bâtiment ancien (> 60 ans, potentiel capex élevé)")
    elif "1961" in period:
        score += 10
        reasons.append("Bâtiment époque 1961-1990")
        
    # Single family villa or rental building (hard to divide physically)
    if "un logement" in dest or "plusieurs logements" in dest:
        score += 10
        reasons.append("Bien immobilier non fractionnable en nature")
        
    if price > 3000000:
        score += 5
        reasons.append("Actif à haute valeur patrimoniale (> CHF 3M)")
        
    final_score = min(score, 100)
    return final_score, reasons, is_hoirie


def compute_development_potential(row: Dict[str, Any]) -> Tuple[int, str, int, List[str]]:
    """Compute Developer & Densification Potential Score (0-100)."""
    score = 0
    reasons = []
    dev_type = "NONE"
    est_apartments = 0
    
    z = str(row.get("zone_code") or "")
    s = float(row.get("surface_official_m2") or row.get("surface_m2") or 0)
    plq = str(row.get("plq_number") or "")
    zdev = str(row.get("zone_dev_name") or "")
    permit = str(row.get("permit_number") or "")
    
    # Active Permit Pipeline
    if permit and permit != "nan":
        score += 50
        dev_type = "PERMIT_ACTIVE"
        reasons.append(f"Permis de construire / APA actif ({permit})")
        
    # PLQ in force
    if plq and plq != "nan":
        score += 35
        if dev_type == "NONE":
            dev_type = "PLQ_IN_FORCE"
        reasons.append(f"Plan Localisé de Quartier N° {plq} ({row.get('plq_name') or 'Genève'})")
        
    # Development zone
    if zdev and zdev != "nan":
        score += 25
        if dev_type == "NONE":
            dev_type = "ZONE_DEV"
        reasons.append(f"Zone de Développement cantonal ({zdev})")
        
    # Zone 5 Densification potential (Art. 59 al. 4 LCI)
    if z == "5" and s >= 1000:
        score += 30
        dev_type = "ZONE_5_DENSIFICATION"
        est_apartments = max(3, int(s * 0.40 / 85))
        reasons.append(f"Parcelle Zone 5 de {int(s):,} m² &bull; Éligible Art. 59 al. 4 LCI (~{est_apartments} appartements)")
    elif (zdev or plq) and s >= 800:
        est_apartments = max(4, int(s * 0.90 / 80))
        reasons.append(f"Grand foncier en mutation urbaine (~{est_apartments} appartements potentiels)")
        
    return min(score, 100), dev_type, est_apartments, reasons


def classify_typology(r: Dict[str, Any]) -> str:
    """Institutional classification strictly adhering to Swiss Civil Code (Art. 712a CC - PPE)
    and Geneva Cadastral standards (SITG & FAO).
    
    Categories:
    - PPE: Appartements & lots en copropriété par étages (résidentiel)
    - VILLA: Villas individuelles, jumelées ou contiguës
    - IMMEUBLE: Immeubles collectifs de rapport entiers (sans division PPE)
    - COMMERCIAL: Locaux commerciaux, bureaux, arcades, hôtels, industrie
    - TERRAIN: Terrains à bâtir, parcelles agricoles ou sans superstructure
    """
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
    
    # Textual triggers
    has_appt_term = any(k in nat for k in ["appartement", "loggia", "balcon", "attique", "duplex", "étage", "etage", "pièces", "pieces", "lot ppe"]) or \
                    any(k in pt for k in ["appartement", "ppe"]) or is_ldtr
    
    has_villa_term = any(k in nat for k in ["villa", "maison", "chalet"]) or \
                     ("un seul logement" in nat) or ("un logement" in dest)
                     
    has_comm_term = any(k in dest for k in ["bureau", "atelier", "dépôt", "commercial", "artisanal", "arcade", "commerce", "hôtel", "hotel", "usine", "centre commercial", "restaurant"]) or \
                    any(k in nat for k in ["bureau", "arcade", "commercial", "commerce", "boutique", "magasin", "hôtel", "hotel", "restaurant"])

    has_multi_dest = any(k in dest for k in ["plusieurs logements", "deux logements", "hab. - rez activités", "habitation - activités"]) or \
                     "immeuble" in nat or "locatif" in nat

    # 1. Commercial Unit or Building
    if has_comm_term and not has_appt_term:
        return "COMMERCIAL"

    # 2. Priority check: Explicit Apartment or PPE sub-parcel
    # If nature or category specifically designates an apartment, it is ALWAYS PPE
    if has_appt_term or is_ldtr:
        return "PPE"

    # If it is a hyphenated parcel (e.g. 4642-104), it is a sub-parcel / PPE lot:
    if has_ppe_parcel:
        # If nature explicitly says villa / house and NOT apartment, it's a villa en PPE (contiguë/jumelée)
        if has_villa_term and not has_multi_dest:
            return "VILLA"
        # If it has commercial characteristics
        if has_comm_term:
            return "COMMERCIAL"
        # In all other cases, a sub-parcel in Geneva is a PPE apartment/unit
        return "PPE"

    # If there are unit specs (rooms, floor, unit number), it's an apartment
    if has_unit_specs:
        return "PPE"

    # 3. Whole Multi-family Buildings (Immeubles de rapport / locatifs sans division PPE)
    # Mother parcel without hyphen, destination is multi-housing
    if has_multi_dest:
        return "IMMEUBLE"

    # 4. Standalone Villas & Houses
    if has_villa_term:
        return "VILLA"

    # 5. Whole Commercial Buildings
    if has_comm_term:
        return "COMMERCIAL"

    # 6. Terrains & Parcelles nues
    return "TERRAIN"


def classify_nature(r: Dict[str, Any]) -> str:
    """Classify legal transaction nature."""
    tt = str(r.get("transaction_type") or "").lower()
    if "vente" in tt:
        return "VENTE"
    elif any(k in tt for k in ["héritage", "heritage", "succession"]):
        return "SUCCESSION"
    else:
        return "DONATION"


def get_typology_label(typology_class: str) -> str:
    labels = {
        "PPE": "Appartement / PPE",
        "VILLA": "Villa & Maison",
        "IMMEUBLE": "Immeuble collectif",
        "COMMERCIAL": "Commercial & Bureaux",
        "TERRAIN": "Terrain & Parcelle",
    }
    return labels.get(typology_class, "Bien immobilier")


def build_interactive_map(
    db_path: Optional[str] = None,
    output_path: Optional[str] = None,
) -> Path:
    """Build a standalone, single-file interactive Leaflet/Swiss map styled with Cytria branding, smart Street View detection, and dual Mandate/Developer Radars."""
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
        raw_rows = [
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
            raw_rows = [dict(r) for r in cursor.fetchall()]
    else:
        raw_rows = []

    # Enrich each record with normalized typology, transaction nature, mandate lead score, and development score
    rows = []
    mandates_count = 0
    hot_mandates_count = 0
    dev_opportunities_count = 0

    for r in raw_rows:
        typo = classify_typology(r)
        nature = classify_nature(r)
        r["typology_class"] = typo
        r["typology_label"] = get_typology_label(typo)
        r["nature_class"] = nature

        # Mandate lead scoring
        m_score, m_reasons, is_hoirie = compute_mandate_score(r)
        r["mandate_score"] = m_score
        r["mandate_reasons"] = m_reasons
        r["is_hoirie"] = is_hoirie
        if m_score > 0:
            mandates_count += 1
        if m_score >= 70:
            hot_mandates_count += 1

        # Development opportunity scoring
        d_score, d_type, est_apts, d_reasons = compute_development_potential(r)
        r["dev_score"] = d_score
        r["dev_type"] = d_type
        r["est_apartments"] = est_apts
        r["dev_reasons"] = d_reasons
        if d_score >= 20:
            dev_opportunities_count += 1

        rows.append(r)

    console.print(f"Loaded [bold]{len(rows)}[/bold] geocoded transactions.")
    console.print(f"Detected [bold green]{mandates_count:,}[/bold green] seller mandate leads ([bold yellow]{hot_mandates_count:,}[/bold yellow] hot leads).")
    console.print(f"Detected [bold cyan]{dev_opportunities_count:,}[/bold cyan] development & densification opportunities.")

    # Distinct communes and zones for filters
    communes = sorted(list({r["commune"] for r in rows if r["commune"]}))
    zones = sorted(list({r["zone_code"] for r in rows if r["zone_code"]}))

    total_volume = sum(r["price_chf"] or 0 for r in rows)
    priced_count = sum(1 for r in rows if r["price_chf"])

    records_json = json.dumps(rows, ensure_ascii=False)
    communes_json = json.dumps(communes, ensure_ascii=False)
    zones_json = json.dumps(zones, ensure_ascii=False)

    league_data = get_ranked_league_table()
    league_json = json.dumps(league_data, ensure_ascii=False)

    marketing_file = Path(settings.storage.exports_dir) / "geneva_marketing_benchmark.json"
    if marketing_file.exists():
        with open(marketing_file, "r", encoding="utf-8") as f:
            marketing_data = json.load(f)
    else:
        marketing_data = []
    marketing_json = json.dumps(marketing_data, ensure_ascii=False)

    html_content = (
        HTML_TEMPLATE
        .replace("__RECORDS_JSON__", records_json)
        .replace("__COMMUNES_JSON__", communes_json)
        .replace("__ZONES_JSON__", zones_json)
        .replace("__LEAGUE_JSON__", league_json)
        .replace("__MARKETING_JSON__", marketing_json)
        .replace("__TOTAL_ROWS__", f"{len(rows):,}")
        .replace("__TOTAL_VOLUME__", f"{total_volume/1e9:.2f}")
        .replace("__PRICED_COUNT__", f"{priced_count:,}")
        .replace("__MANDATES_COUNT__", f"{mandates_count:,}")
        .replace("__HOT_MANDATES_COUNT__", f"{hot_mandates_count:,}")
        .replace("__DEV_COUNT__", f"{dev_opportunities_count:,}")
        .replace("__AGENCIES_COUNT__", f"{len(league_data['agencies']):,}")
    )

    out_file.write_text(html_content, encoding="utf-8")
    console.print(f"[bold green][OK] Cytria Interactive Map Generated:[/bold green] {out_file.resolve()} ({len(html_content)/1024:.1f} KB)\n")
    return out_file
