"""Standalone interactive HTML map generator for Geneva Property Transactions with Cytria Brand Design, Smart Street View Detection, Seller Mandate Radar, and Land Development Opportunity Engine."""

import json
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

    /* Top Mode Switcher */
    .mode-switcher-container {
      display: flex;
      background: var(--color-ink-950);
      border: 1px solid var(--panel-border);
      padding: 3px;
      gap: 4px;
      pointer-events: auto;
    }

    .nav-mode-btn {
      background: transparent;
      border: 1px solid transparent;
      color: var(--color-sand-300);
      font-family: var(--font-brand);
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      padding: 7px 14px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      transition: all 0.2s ease;
    }

    .nav-mode-btn:hover {
      color: var(--color-paper);
      background: var(--color-ink-800);
    }

    .nav-mode-btn.active {
      background: var(--color-brand-500);
      color: var(--color-ink-950);
      border-color: var(--color-brand-400);
      font-weight: 800;
      box-shadow: 0 4px 12px rgba(201, 162, 77, 0.25);
    }

    .nav-mode-badge {
      font-family: var(--font-mono);
      font-size: 9px;
      font-weight: 700;
      padding: 2px 5px;
      background: var(--color-ink-900);
      color: var(--color-brand-300);
      border: 1px solid var(--panel-border-gold);
    }

    .nav-mode-btn.active .nav-mode-badge {
      background: var(--color-ink-950);
      color: var(--color-paper);
      border-color: var(--color-ink-950);
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
      top: 76px;
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
      top: 76px;
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
  </style>
</head>
<body>

  <!-- Map Container -->
  <div id="map"></div>

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

      <!-- Mode Switcher -->
      <div class="mode-switcher-container">
        <button type="button" class="nav-mode-btn active" id="modeBtnMarket" onclick="setAppMode('MARKET')">
          Marché & Prix
        </button>
        <button type="button" class="nav-mode-btn" id="modeBtnMandates" onclick="setAppMode('MANDATES')">
          Scanner Mandats <span class="nav-mode-badge" id="navBadgeMandates">__MANDATES_COUNT__</span>
        </button>
        <button type="button" class="nav-mode-btn" id="modeBtnDev" onclick="setAppMode('DEVELOPMENT')">
          Radar Promotion <span class="nav-mode-badge" id="navBadgeDev">__DEV_COUNT__</span>
        </button>
        <button type="button" class="nav-mode-btn" id="btnOpenLeagueTable" onclick="openLeagueModal()" style="border-color: var(--color-brand-400); color: var(--color-brand-300);">
          Palmarès Agences & Courtiers
        </button>
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
          <h2>Palmarès & Performance des Agences et Courtiers de Genève</h2>
          <p>Indice de performance Cytria (0-100) calibré sur les transactions officielles du Registre Foncier (FAO) et le track record vérifié.</p>
        </div>
        <div style="display:flex; align-items:center; gap: 14px;">
          <div class="league-tabs">
            <button type="button" class="league-tab-btn active" id="leagueTabAgencies" onclick="setLeagueTab('AGENCIES')">Classement Agences</button>
            <button type="button" class="league-tab-btn" id="leagueTabBrokers" onclick="setLeagueTab('BROKERS')">Top Courtiers Individuels</button>
          </div>
          <button class="modal-close-btn" id="leagueModalCloseBtn" onclick="closeLeagueModal()">&times;</button>
        </div>
      </div>
      <div class="league-body" id="leagueBodyContent">
        <!-- Injected via JavaScript -->
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

    // App Mode Switching Handler
    function setAppMode(mode) {
      appMode = mode;
      document.querySelectorAll('.nav-mode-btn').forEach(b => b.classList.remove('active'));

      const filterMarket = document.getElementById('filterGroupMarket');
      const filterMandates = document.getElementById('filterGroupMandates');
      const filterDev = document.getElementById('filterGroupDev');
      const bannerTitle = document.getElementById('sidebarBannerTitle');
      const bannerSub = document.getElementById('sidebarBannerSub');

      if (mode === 'MANDATES') {
        document.getElementById('modeBtnMandates').classList.add('active');
        filterMarket.style.display = 'none';
        filterMandates.style.display = 'block';
        filterDev.style.display = 'none';
        bannerTitle.textContent = 'Scanner de Mandats Vendeurs';
        bannerSub.textContent = 'Détection algorithmique des successions et hoiries à forte propension de vente';
      } else if (mode === 'DEVELOPMENT') {
        document.getElementById('modeBtnDev').classList.add('active');
        filterMarket.style.display = 'none';
        filterMandates.style.display = 'none';
        filterDev.style.display = 'block';
        bannerTitle.textContent = 'Radar Foncier & Promotion';
        bannerSub.textContent = 'Calcul de potentiel de densification Art. 59 LCI et pipeline de permis';
      } else {
        document.getElementById('modeBtnMarket').classList.add('active');
        filterMarket.style.display = 'block';
        filterMandates.style.display = 'none';
        filterDev.style.display = 'none';
        bannerTitle.textContent = 'Marché Immobilier Complet';
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
            <span class="row-value mono">${r.parcel_number}</span>
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
            <span class="row-value">${r.building_destination} ${r.building_floors ? '(' + r.building_floors + ' étages)' : ''}</span>
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
      const q = searchInput.value.toLowerCase().trim();
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

        // Global search query
        if (q) {
          const str = [
            (r.address||''), (r.commune||''), (r.buyer||''), (r.seller||''),
            (r.parcel_number||''), (r.egrid||''), (r.plq_name||''),
            (r.permit_number||''), (r.grand_projet_name||''), (r.nature||'')
          ].join(' ').toLowerCase();
          if (!str.includes(q)) return false;
        }

        return true;
      });

      createMarkers(filtered);
    }

    // League Table Ranking Modal Logic
    const LEAGUE_DATA = __LEAGUE_JSON__;
    let currentLeagueTab = 'AGENCIES';

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
      if (currentLeagueTab === 'AGENCIES') {
        const rows = LEAGUE_DATA.agencies.map(a => {
          const rankClass = a.rank === 1 ? 'top-1' : a.rank === 2 ? 'top-2' : a.rank === 3 ? 'top-3' : '';
          return `
            <tr>
              <td><span class="rank-pill ${rankClass}">#${a.rank}</span></td>
              <td>
                <strong style="color:var(--color-brand-300); font-size:13px;">${a.name}</strong><br>
                <span style="color:var(--color-sand-300); font-size:11px;">${a.address}</span>
                ${a.website ? `<br><a href="${a.website}" target="_blank" style="color:var(--color-brand-400); text-decoration:none; font-size:10px;">Visiter Site Web ↗</a>` : ''}
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
                <span style="color:var(--color-brand-300); font-weight:600; font-size:11px;">${a.primary_territory}</span>
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
              </tr>
            </thead>
            <tbody>
              ${rows}
            </tbody>
          </table>
        `;
      } else {
        const rows = LEAGUE_DATA.brokers.map(b => {
          const rankClass = b.rank === 1 ? 'top-1' : b.rank === 2 ? 'top-2' : b.rank === 3 ? 'top-3' : '';
          return `
            <tr>
              <td><span class="rank-pill ${rankClass}">#${b.rank}</span></td>
              <td>
                <strong style="color:var(--color-brand-300); font-size:13px;">${b.name}</strong><br>
                <span style="color:var(--color-sand-300); font-size:11px;">${b.role}</span>
              </td>
              <td>
                <span style="color:var(--color-paper); font-weight:600;">${b.agency_name}</span>
              </td>
              <td><span class="score-badge">${b.cytria_score} / 100</span></td>
              <td>
                <strong>${b.deals_count} transactions</strong><br>
                <span style="color:var(--color-sand-300); font-size:10px;">Spécialité : ${b.specialty}</span>
              </td>
              <td>
                <strong>${b.rating} / 5.0</strong><br>
                <span style="color:var(--color-sand-300); font-size:10px;">${b.reviews_count} avis vérifiés</span>
              </td>
              <td>
                <span style="color:var(--color-brand-300); font-weight:600; font-size:11px;">${(b.top_communes || []).join(', ')}</span>
              </td>
            </tr>
          `;
        }).join('');

        container.innerHTML = `
          <table class="league-table">
            <thead>
              <tr>
                <th>Rang</th>
                <th>Courtier / Agent</th>
                <th>Agence Affiliée</th>
                <th>Score Cytria</th>
                <th>Volume & Spécialité</th>
                <th>Avis Clients</th>
                <th>Communes de Prédilection</th>
              </tr>
            </thead>
            <tbody>
              ${rows}
            </tbody>
          </table>
        `;
      }
    }

    document.getElementById('leagueTableModal').addEventListener('click', (e) => {
      if (e.target.id === 'leagueTableModal') {
        closeLeagueModal();
      }
    });

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
    """Classify property into a clean institutional asset class."""
    dest = str(r.get("building_destination") or "").lower()
    nat = str(r.get("nature") or "").lower()
    pt = str(r.get("property_type") or "").lower()
    sc = str(r.get("source_category") or "").lower()

    if "plusieurs logements" in dest or "deux logements" in dest or "immeuble" in nat:
        return "IMMEUBLE"
    elif "un logement" in dest or "villa" in nat:
        return "VILLA"
    elif "appartement" in nat or "ppe" in pt or "ldtr_appartement" in sc:
        return "PPE"
    elif any(k in dest for k in ["activités", "bureau", "atelier", "dépôt", "commercial", "artisanal", "rez activités"]) or "commercial" in nat:
        return "COMMERCIAL"
    else:
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
        "IMMEUBLE": "Immeuble collectif",
        "VILLA": "Villa individuelle",
        "PPE": "Appartement / PPE",
        "COMMERCIAL": "Commercial & Mixte",
        "TERRAIN": "Terrain / Parcelle",
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

    html_content = (
        HTML_TEMPLATE
        .replace("__RECORDS_JSON__", records_json)
        .replace("__COMMUNES_JSON__", communes_json)
        .replace("__ZONES_JSON__", zones_json)
        .replace("__LEAGUE_JSON__", league_json)
        .replace("__TOTAL_ROWS__", f"{len(rows):,}")
        .replace("__TOTAL_VOLUME__", f"{total_volume/1e9:.2f}")
        .replace("__PRICED_COUNT__", f"{priced_count:,}")
        .replace("__MANDATES_COUNT__", f"{mandates_count:,}")
        .replace("__HOT_MANDATES_COUNT__", f"{hot_mandates_count:,}")
        .replace("__DEV_COUNT__", f"{dev_opportunities_count:,}")
    )

    out_file.write_text(html_content, encoding="utf-8")
    console.print(f"[bold green][OK] Cytria Interactive Map Generated:[/bold green] {out_file.resolve()} ({len(html_content)/1024:.1f} KB)\n")
    return out_file
