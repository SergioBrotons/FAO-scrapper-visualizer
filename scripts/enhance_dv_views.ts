import { readFileSync, writeFileSync } from "fs";

const filePath = "public/dv/index.html";
let html = readFileSync(filePath, "utf8");

console.log("Original HTML length:", html.length);

// 1. Enlarge Container max-width
html = html.replace(/max-width:\s*1240px;/g, "max-width: 1420px;");

// 2. Enhance form inputs, textareas, labels and grids in CSS
const oldFormCss = `.form-grid-2 {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      margin-bottom: 16px;
    }
    .form-grid-3 {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
      margin-bottom: 16px;
    }
    .form-grid-4 {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 14px;
      margin-bottom: 16px;
    }
    @media (max-width: 860px) {
      .form-grid-2, .form-grid-3, .form-grid-4 {
        grid-template-columns: 1fr;
      }
    }

    .form-field {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    .form-field label {
      font-size: 11px;
      font-weight: 700;
      color: var(--dv-deep-green);
      letter-spacing: 0.02em;
    }
    .form-field input, .form-field select, .form-field textarea {
      padding: 10px 12px;
      border: 1px solid rgba(0, 147, 157, 0.25);
      border-radius: 6px;
      font-family: inherit;
      font-size: 13px;
      color: var(--dv-text-main);
      background: #FFFFFF;
      outline: none;
      transition: all 0.2s;
    }`;

const newFormCss = `.form-grid-2 {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 22px;
      margin-bottom: 22px;
    }
    .form-grid-3 {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 22px;
      margin-bottom: 22px;
    }
    .form-grid-4 {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 18px;
      margin-bottom: 22px;
    }
    @media (max-width: 960px) {
      .form-grid-2, .form-grid-3, .form-grid-4 {
        grid-template-columns: 1fr;
      }
    }

    .form-field {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .form-field label {
      font-size: 12px;
      font-weight: 700;
      color: var(--dv-deep-green);
      letter-spacing: 0.02em;
    }
    .form-field input, .form-field select {
      padding: 13px 16px;
      border: 1px solid rgba(0, 147, 157, 0.28);
      border-radius: 8px;
      font-family: inherit;
      font-size: 14px;
      color: var(--dv-text-main);
      background: #FFFFFF;
      outline: none;
      min-height: 48px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.02);
      transition: all 0.2s;
    }
    .form-field textarea {
      padding: 14px 16px;
      border: 1px solid rgba(0, 147, 157, 0.28);
      border-radius: 8px;
      font-family: inherit;
      font-size: 13.5px;
      color: var(--dv-text-main);
      background: #FFFFFF;
      outline: none;
      min-height: 120px;
      line-height: 1.6;
      box-shadow: 0 1px 3px rgba(0,0,0,0.02);
      transition: all 0.2s;
      resize: vertical;
    }`;

html = html.replace(oldFormCss, newFormCss);

// 3. Enhance Comparables Table spacing in CSS
const oldTableCss = `.comps-table th {
      background: rgba(0, 74, 79, 0.05);
      color: var(--dv-deep-green);
      font-weight: 700;
      padding: 10px 12px;
      border-bottom: 1px solid var(--dv-border);
    }
    .comps-table td {
      padding: 10px 12px;
      border-bottom: 1px solid rgba(0,0,0,0.05);
      color: var(--dv-text-main);
    }`;

const newTableCss = `.comps-table th {
      background: rgba(0, 74, 79, 0.06);
      color: var(--dv-deep-green);
      font-weight: 700;
      padding: 14px 16px;
      border-bottom: 1px solid var(--dv-border);
      font-size: 12.5px;
      letter-spacing: 0.02em;
    }
    .comps-table td {
      padding: 15px 16px;
      border-bottom: 1px solid rgba(0,0,0,0.05);
      color: var(--dv-text-main);
      font-size: 13.5px;
    }`;

html = html.replace(oldTableCss, newTableCss);

// 4. Check if additional CSS for Territory, Mandate, Match views is present
const additionalCss = `
    /* Filter Chips Bar */
    .filter-chips-bar {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-bottom: 20px;
      align-items: center;
    }
    .filter-chip {
      background: #FFFFFF;
      border: 1px solid var(--dv-border);
      border-radius: 20px;
      padding: 6px 14px;
      font-size: 12px;
      font-weight: 600;
      color: var(--dv-text-main);
      cursor: pointer;
      transition: all 0.2s;
    }
    .filter-chip:hover {
      background: rgba(0, 147, 157, 0.06);
      border-color: var(--dv-teal);
    }
    .filter-chip.active {
      background: var(--dv-deep-green);
      color: #FFFFFF;
      border-color: var(--dv-deep-green);
      box-shadow: 0 2px 8px rgba(0, 74, 79, 0.2);
    }

    /* Competitor Alert Ribbon */
    .competitor-alert-ribbon {
      background: #FFFDF8;
      border: 1px solid rgba(158, 64, 0, 0.25);
      border-left: 5px solid var(--dv-brown-warm);
      border-radius: 8px;
      padding: 16px 20px;
      margin-bottom: 24px;
      box-shadow: var(--dv-shadow);
    }
    .ribbon-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
    }
    .ribbon-title {
      font-size: 13px;
      font-weight: 800;
      color: var(--dv-brown-warm);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .ribbon-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 12px;
    }
    .ribbon-item {
      background: #FFFFFF;
      border: 1px solid rgba(158, 64, 0, 0.15);
      border-radius: 6px;
      padding: 12px 14px;
      font-size: 12px;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .ribbon-item-badge {
      display: inline-block;
      font-size: 10px;
      font-weight: 800;
      text-transform: uppercase;
      padding: 2px 6px;
      border-radius: 4px;
      width: fit-content;
    }
    .badge-stale {
      background: rgba(158, 64, 0, 0.12);
      color: var(--dv-brown-warm);
    }
    .badge-drop {
      background: rgba(220, 38, 38, 0.1);
      color: #DC2626;
    }
    .badge-new {
      background: rgba(0, 147, 157, 0.1);
      color: var(--dv-teal);
    }

    /* Architecture Security Banner */
    .privacy-architecture-card {
      background: linear-gradient(135deg, #00363A 0%, #004A4F 100%);
      color: #FFFFFF;
      border-radius: 8px;
      padding: 22px 28px;
      margin: 32px 0 20px;
      box-shadow: var(--dv-shadow);
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      align-items: center;
    }
    @media (max-width: 900px) {
      .privacy-architecture-card {
        grid-template-columns: 1fr;
      }
    }
    .privacy-col h4 {
      font-size: 14px;
      font-weight: 700;
      color: var(--dv-light-teal);
      margin-bottom: 6px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .privacy-col p {
      font-size: 12px;
      color: rgba(255, 255, 255, 0.85);
      line-height: 1.5;
    }

    /* Web Leads Card */
    .lead-card {
      background: #FFFFFF;
      border: 1px solid var(--dv-border);
      border-radius: 8px;
      padding: 18px 20px;
      margin-bottom: 14px;
      box-shadow: var(--dv-shadow);
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 14px;
    }
    .lead-score-pill {
      font-size: 11px;
      font-weight: 800;
      color: var(--dv-teal);
      background: rgba(0, 147, 157, 0.1);
      padding: 4px 10px;
      border-radius: 12px;
    }
`;

if (!html.includes(".filter-chips-bar")) {
  html = html.replace("</style>", additionalCss + "\n  </style>");
}

// 5. Build HTML Markup for the missing views:
// viewRadar (TERRITORY)
// viewMandates (MANDATE)
// viewBuyers (MATCH)
// and close </main> properly!

const viewsMarkup = `
    <!-- ================= VIEW 3: ANALYSER MON SECTEUR (TERRITORY) ================= -->
    <div id="viewRadar" style="display: none;">
      <div class="welcome-header" style="display:flex; justify-content:space-between; align-items:flex-end; flex-wrap:wrap; gap:16px;">
        <div>
          <h2>Veille de Secteur & Intelligence Foncière Rive Gauche</h2>
          <p>Transactions notariées officielles (RF / FAO) & Surveillance active des mandats concurrents</p>
        </div>
        <div style="display:flex; gap:10px;">
          <button class="btn-action-primary" onclick="loadRadarView()">
            <svg class="mini-icon" width="14" height="14" viewBox="0 0 24 24"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M16 21h5v-5"/></svg>
            <span>Actualiser les Signaux</span>
          </button>
        </div>
      </div>

      <!-- Territory Commune Filter Chips -->
      <div class="filter-chips-bar" id="communeFilterBar">
        <span style="font-size:12px; font-weight:700; color:var(--dv-deep-green); margin-right:4px;">Commune :</span>
        <button class="filter-chip active" onclick="filterTerritory('all', this)">Toutes les communes (8)</button>
        <button class="filter-chip" onclick="filterTerritory('Chêne-Bourg', this)">Chêne-Bourg</button>
        <button class="filter-chip" onclick="filterTerritory('Veyrier', this)">Veyrier</button>
        <button class="filter-chip" onclick="filterTerritory('Troinex', this)">Troinex</button>
        <button class="filter-chip" onclick="filterTerritory('Chêne-Bougeries', this)">Chêne-Bougeries</button>
        <button class="filter-chip" onclick="filterTerritory('Cologny', this)">Cologny</button>
        <button class="filter-chip" onclick="filterTerritory('Collonge-Bellerive', this)">Collonge-Bellerive</button>
        <button class="filter-chip" onclick="filterTerritory('Vandœuvres', this)">Vandœuvres</button>
      </div>

      <!-- Live Competitor Property Alerts Ribbon -->
      <div class="competitor-alert-ribbon">
        <div class="ribbon-header">
          <div class="ribbon-title">
            <svg class="mini-icon" width="16" height="16" viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
            <span>Alertes Propriétés Concurrentes Détectées en Vente sur le Secteur</span>
          </div>
          <span style="font-size:11px; font-weight:700; color:var(--dv-brown-warm);">Surveillance automatique 24/7</span>
        </div>
        <div class="ribbon-grid">
          <div class="ribbon-item">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span class="ribbon-item-badge badge-stale">⏳ Mandat en Souffrance (82j)</span>
              <strong style="color:var(--dv-deep-green);">CHF 2'150'000</strong>
            </div>
            <div style="font-weight:700; color:var(--dv-text-main); margin-top:2px;">Chemin des Prés 14, Chêne-Bourg</div>
            <div style="color:var(--dv-text-muted); font-size:11px;">Agence : <strong>John Taylor Geneva</strong> &bull; Attique 5p 130 m²</div>
            <div style="color:var(--dv-brown-warm); font-size:11px; margin-top:4px;">
              <strong>Opportunité D&V :</strong> Bloqué depuis 82 jours sans transaction. L'acte récent du Saut-du-Loup 16 à CHF 17'609/m² fournit l'argument idéal pour démarcher le propriétaire avec une valorisation factuelle.
            </div>
          </div>

          <div class="ribbon-item">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span class="ribbon-item-badge badge-drop">📉 Baisse de Prix (-5.5%)</span>
              <strong style="color:var(--dv-deep-green);">CHF 2'740'000</strong>
            </div>
            <div style="font-weight:700; color:var(--dv-text-main); margin-top:2px;">Route de Vessy 42, Veyrier</div>
            <div style="color:var(--dv-text-muted); font-size:11px;">Agence : <strong>Barnes Immobilier</strong> &bull; Villa 7p 210 m²</div>
            <div style="color:#B91C1C; font-size:11px; margin-top:4px;">
              <strong>Alerte :</strong> Réduction de CHF 160'000 après 60j d'affichage initial à 2.9M. Signal d'ajustement sur les villas familiales de Veyrier.
            </div>
          </div>

          <div class="ribbon-item">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span class="ribbon-item-badge badge-new">⚡ Nouveau Mandat Concurrent</span>
              <strong style="color:var(--dv-deep-green);">CHF 3'400'000</strong>
            </div>
            <div style="font-weight:700; color:var(--dv-text-main); margin-top:2px;">Chemin de Chambésy 8, Troinex</div>
            <div style="color:var(--dv-text-muted); font-size:11px;">Agence : <strong>Naef Prestige Knight Frank</strong> &bull; Villa d'architecte 250 m²</div>
            <div style="color:var(--dv-teal); font-size:11px; margin-top:4px;">
              <strong>Action D&V :</strong> Rapprocher immédiatement avec notre portefeuille de 3 acquéreurs qualifiés Troinex en attente sur ce budget.
            </div>
          </div>
        </div>
      </div>

      <!-- Radar Dynamic Content Container -->
      <div id="radarContainer"></div>
    </div>

    <!-- ================= VIEW 4: REVOIR MES MANDATS (MANDATE) ================= -->
    <div id="viewMandates" style="display: none;">
      <div class="welcome-header" style="display:flex; justify-content:space-between; align-items:flex-end; flex-wrap:wrap; gap:16px;">
        <div>
          <h2>Gestion du Portefeuille Agence & Diagnostic Commercial</h2>
          <p>Mandats internes sous gestion &bull; Réajustements stratégiques basés sur les actes notariés récents</p>
        </div>
        <div style="display:flex; gap:10px;">
          <button class="btn-action-primary" onclick="showToast('Synchronisation avec votre CRM d\\'agence (Whise / Apimo) effectuée !')">
            <svg class="mini-icon" width="14" height="14" viewBox="0 0 24 24"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M16 21h5v-5"/></svg>
            <span>Synchroniser CRM Agence</span>
          </button>
        </div>
      </div>

      <!-- CRM Connector Architecture Explanation -->
      <div style="background:#FFFFFF; border:1px solid var(--dv-border); border-left:5px solid var(--dv-teal); border-radius:8px; padding:18px 22px; margin-bottom:24px; box-shadow:var(--dv-shadow);">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
          <div>
            <div style="font-size:11px; font-weight:800; color:var(--dv-teal); text-transform:uppercase; letter-spacing:0.06em;">
              🟢 CONNECTEUR CRM AGENCE ACTIF (Whise / Apimo / SweepBright API v3)
            </div>
            <h3 style="font-family:'Cormorant Garamond', Georgia, serif; font-size:21px; color:var(--dv-deep-green); margin-top:2px;">
              Portefeuille Privé Désormière & Vanhalst enrichi par Cytria Intelligence
            </h3>
            <p style="font-size:12px; color:var(--dv-text-muted); margin-top:4px; max-width:920px;">
              Vos mandats de vente, contacts propriétaires et honoraires proviennent directement de votre CRM d'agence privé. Cytria n'altère aucune donnée commerciale : le système croise vos mandats avec les dernières ventes notariées (FAO) et le cadastre genevois (SITG) pour identifier les ajustements de prix nécessaires avant que les mandats ne deviennent stagnants.
            </p>
          </div>
          <div style="text-align:right;">
            <div style="font-size:11px; color:var(--dv-text-muted);">Dernier sync : Aujourd'hui à 18:45</div>
            <div style="font-size:13px; font-weight:700; color:var(--dv-deep-green);">8 mandats actifs sous gestion</div>
          </div>
        </div>
      </div>

      <!-- Incoming Website Leads Section -->
      <div style="margin-bottom:28px;">
        <div class="section-title" style="display:flex; justify-content:space-between; align-items:center;">
          <span>Formulaires Web D&V — Demandes d'Estimation en Ligne (Site Web)</span>
          <span style="font-size:11px; font-weight:700; color:var(--dv-teal); text-transform:none;">2 nouvelles demandes qualifiées</span>
        </div>

        <div class="lead-card">
          <div>
            <div style="display:flex; align-items:center; gap:8px;">
              <span class="lead-score-pill">Priorité Maximale &bull; Score 94%</span>
              <span style="font-size:11px; color:var(--dv-text-muted);">Reçue il y a 3 heures</span>
            </div>
            <h4 style="font-size:16px; font-weight:700; color:var(--dv-deep-green); margin-top:6px;">
              M. et Mme François Dumont &bull; Chemin de la Blonde 9, 1253 Vandœuvres
            </h4>
            <div style="font-size:12px; color:var(--dv-text-muted); margin-top:2px;">
              Typologie déclarée : <strong>Villa individuelle 240 m² sur parcelle 1'450 m²</strong> &bull; Tél: +41 79 450 12 88
            </div>
            <div style="background:rgba(0,147,157,0.06); padding:8px 12px; border-radius:4px; font-size:11px; margin-top:8px; color:var(--dv-deep-green);">
              <strong>Analyse Cytria :</strong> Parcelle 5821 vérifiée au SITG en zone 5. Aucun mandat concurrent repéré. Propriétaire unique depuis 18 ans. Estimation recommandée : ~CHF 3.8M – 4.2M.
            </div>
          </div>
          <div>
            <button class="btn-action-primary" onclick="switchView('value'); showToast('Dossier M. Dumont chargé dans le Studio d\\'estimation !');">
              <svg class="mini-icon" width="13" height="13" viewBox="0 0 24 24"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/></svg>
              <span>Créer l'Estimation (1-Click)</span>
            </button>
          </div>
        </div>

        <div class="lead-card">
          <div>
            <div style="display:flex; align-items:center; gap:8px;">
              <span class="lead-score-pill" style="color:var(--dv-brown-warm); background:rgba(158,64,0,0.1);">Priorité Forte &bull; Score 89%</span>
              <span style="font-size:11px; color:var(--dv-text-muted);">Reçue hier</span>
            </div>
            <h4 style="font-size:16px; font-weight:700; color:var(--dv-deep-green); margin-top:6px;">
              Dr. Philippe Mercier &bull; Route de Veyrier 118, 1255 Veyrier
            </h4>
            <div style="font-size:12px; color:var(--dv-text-muted); margin-top:2px;">
              Typologie déclarée : <strong>Appartement attique 5p Minergie 115 m² avec terrasse 60 m²</strong> &bull; Email: p.mercier@bluewin.ch
            </div>
            <div style="background:rgba(158,64,0,0.06); padding:8px 12px; border-radius:4px; font-size:11px; margin-top:8px; color:var(--dv-brown-warm);">
              <strong>Analyse Cytria :</strong> Hoirie récente enregistrée au Registre Foncier (art. 602 CC). Bien exempt de charges hypothécaires lourdes. Forte motivation à la vente.
            </div>
          </div>
          <div>
            <button class="btn-action-primary" onclick="switchView('value'); showToast('Dossier Dr. Mercier chargé dans le Studio d\\'estimation !');">
              <svg class="mini-icon" width="13" height="13" viewBox="0 0 24 24"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/></svg>
              <span>Créer l'Estimation (1-Click)</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Active Mandates List -->
      <div class="section-title">Mandats en Cours & Diagnostics de Positionnement Prix</div>
      <div id="mandatesListContainer" style="display:flex; flex-direction:column; gap:16px;"></div>
    </div>

    <!-- ================= VIEW 5: ACTIVER MES ACHETEURS (MATCH) ================= -->
    <div id="viewBuyers" style="display: none;">
      <div class="welcome-header" style="display:flex; justify-content:space-between; align-items:flex-end; flex-wrap:wrap; gap:16px;">
        <div>
          <h2>Moteur de Matching Acquéreurs Privés & Opportunités de Secteur</h2>
          <p>Croisement en circuit fermé entre acheteurs qualifiés CRM et parutions cadastrales récentes</p>
        </div>
        <div style="display:flex; gap:10px;">
          <button class="btn-action-primary" onclick="showToast('Rapprochement algorithmique acheteurs mis à jour !')">
            <svg class="mini-icon" width="14" height="14" viewBox="0 0 24 24"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
            <span>Relancer les Correspondances</span>
          </button>
        </div>
      </div>

      <!-- Private Matching Architecture Explanation -->
      <div style="background:#FFFFFF; border:1px solid var(--dv-border); border-left:5px solid var(--dv-deep-green); border-radius:8px; padding:18px 22px; margin-bottom:24px; box-shadow:var(--dv-shadow);">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
          <div>
            <div style="font-size:11px; font-weight:800; color:var(--dv-deep-green); text-transform:uppercase; letter-spacing:0.06em;">
              🔒 CLOISONNEMENT STRICT DU FICHIER ACQUÉREURS (Conformité nLPD)
            </div>
            <h3 style="font-family:'Cormorant Garamond', Georgia, serif; font-size:21px; color:var(--dv-deep-green); margin-top:2px;">
              Recherche Inverse & Correspondances Immédiates
            </h3>
            <p style="font-size:12px; color:var(--dv-text-muted); margin-top:4px; max-width:920px;">
              Les profils financiers et les critères de recherche de vos acquéreurs restent strictement cantonnés dans votre espace d'agence. Cytria applique un modèle d'appariement local pour détecter en temps réel les biens qui répondent exactement aux budgets de vos clients, vous permettant de déclencher des propositions off-market exclusives avant toute publication publique.
            </p>
          </div>
          <div style="text-align:right;">
            <div style="font-size:11px; color:var(--dv-text-muted);">Base acquéreurs : 142 profils actifs</div>
            <div style="font-size:13px; font-weight:700; color:var(--dv-teal);">9 correspondances haute probabilité</div>
          </div>
        </div>
      </div>

      <!-- Buyers List -->
      <div id="buyersListContainer" style="display:flex; flex-direction:column; gap:16px;"></div>
    </div>

    <!-- ================= ARCHITECTURE PRIVÉE + PUBLIQUE (nLPD GUARANTEE) ================= -->
    <div class="privacy-architecture-card">
      <div class="privacy-col">
        <h4>
          <svg class="mini-icon" width="16" height="16" viewBox="0 0 24 24"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
          <span>Portefeuille Privé Agence (CRM Whise / Apimo)</span>
        </h4>
        <p>
          Vos mandats exclusifs, données clients, évaluations internes et notes de négociation restent sous votre contrôle exclusif. Aucune donnée nominative n'est divulguée, assurant la conformité intégrale avec la nouvelle Loi fédérale sur la protection des données (nLPD).
        </p>
      </div>
      <div class="privacy-col">
        <h4>
          <svg class="mini-icon" width="16" height="16" viewBox="0 0 24 24"><path d="M12 2H2v10l9.29 9.29c.94.94 2.48.94 3.42 0l6.58-6.58c.94-.94.94-2.48 0-3.42L12 2Z"/><path d="M7 7h.01"/></svg>
          <span>Cadastre Officiel & Transactions FAO</span>
        </h4>
        <p>
          Cytria enrichit vos dossiers en interrogeant directement le cadastre genevois SITG et les transactions publiées à la Feuille d'Avis Officielle. Vous disposez ainsi des prix réels notariés pour prouver indiscutablement la valeur de vos estimations.
        </p>
      </div>
    </div>
  </main>
`;

// Insert viewsMarkup right before the modals (before <!-- Modal for Neighbor Effect Letters -->)
const modalMarker = "<!-- Modal for Neighbor Effect Letters -->";
if (html.includes(modalMarker)) {
  html = html.replace(modalMarker, viewsMarkup + "\n\n  " + modalMarker);
} else {
  // If not found, insert before toast
  html = html.replace("<!-- Toast -->", viewsMarkup + "\n\n  <!-- Toast -->");
}

// 6. Update Territory filtering function in script
const filterScript = `
    let ACTIVE_COMMUNE_FILTER = 'all';

    function filterTerritory(commune, btn) {
      ACTIVE_COMMUNE_FILTER = commune;
      const chips = document.querySelectorAll('#communeFilterBar .filter-chip');
      chips.forEach(c => c.classList.remove('active'));
      if (btn) btn.classList.add('active');

      const container = document.getElementById('radarContainer');
      if (container && window.LAST_RADAR_DATA) {
        renderRadarInContainer(container, window.LAST_RADAR_DATA);
      }
    }
`;

if (!html.includes("function filterTerritory")) {
  html = html.replace("async function loadRadarView()", filterScript + "\n    async function loadRadarView()");
}

// 7. Update renderRadarInContainer to support the commune filter
const oldRenderRadar = `function renderRadarInContainer(container, data) {`;
const newRenderRadar = `function renderRadarInContainer(container, data) {
      window.LAST_RADAR_DATA = data;
      const filter = ACTIVE_COMMUNE_FILTER;
      const filteredSales = (filter === 'all') 
        ? data.recent_sales 
        : data.recent_sales.filter(s => s.commune && s.commune.toLowerCase().includes(filter.toLowerCase()));
      const filteredCompetitors = (filter === 'all') 
        ? data.competitor_mandates 
        : data.competitor_mandates.filter(m => m.commune && m.commune.toLowerCase().includes(filter.toLowerCase()));
`;

html = html.replace(oldRenderRadar, newRenderRadar);

// Also replace data.recent_sales with filteredSales and data.competitor_mandates with filteredCompetitors
html = html.replace("data.recent_sales.map(s => `", "filteredSales.map(s => `");
html = html.replace("data.competitor_mandates.map(m => `", "filteredCompetitors.map(m => `");

// 8. Update exportPresentationPptx to dynamically pass all active comparables from WIZARD_COMPARABLES
const oldSlide9Replacements = `slide9: {
            "[JJ.MM.AA]": "26.02.2026",
            "[Adresse / promotion]": "Chemin du Saut-du-Loup 16 (Parcelle 4642-104)",
            "[PPE]": "PPE 4p Balcon (Résidence jumelle)",
            "[00 m²]": "92 m²",
            "[Jardin / balcon]": "Balcon 14 m²",
            "CHF [0’000’000]": "CHF 1’620’000",
            "[00’000]": "17’609",
            "[FAO / D&V]": "Acte Notarié RF / FAO (Réf. 2026/628/0)",
            "MÉTHODE DE NORMALISATION": \`Normalisation D&V : Référence n°1 = Acte notarié Saut-du-Loup 16 (17’609 CHF/m²). Base prudentielle retenue à \${Number(basePriceM2).toLocaleString('fr-CH')} CHF/m\`
          }`;

const newSlide9Replacements = `slide9: {
            "[JJ.MM.AA]": WIZARD_COMPARABLES.map(c => c.date || "26.02.2026"),
            "[Adresse / promotion]": WIZARD_COMPARABLES.map(c => c.address + (c.is_anchor ? " (Parcelle 4642-104)" : "")),
            "[PPE]": WIZARD_COMPARABLES.map(c => c.is_anchor ? "PPE 4p Balcon (Résidence jumelle)" : "PPE " + (c.surface > 80 ? "4p" : "3p")),
            "[00 m²]": WIZARD_COMPARABLES.map(c => c.surface + " m²"),
            "[Jardin / balcon]": WIZARD_COMPARABLES.map(c => c.is_anchor ? "Balcon 14 m²" : "Balcon / Loggia"),
            "CHF [0’000’000]": WIZARD_COMPARABLES.map(c => "CHF " + Number(c.price).toLocaleString('fr-CH')),
            "[00’000]": WIZARD_COMPARABLES.map(c => Number(c.price_m2).toLocaleString('fr-CH')),
            "[FAO / D&V]": WIZARD_COMPARABLES.map(c => c.source || "Base FAO / RF"),
            "[Principe général]": "Les transactions notariées du même quartier constituent la référence juridique absolue.",
            "[Critère 1 : localisation / micro-secteur]": "Micro-secteur homogène : Chêne-Bourg Rive Gauche, proximité immédiate gare CEVA.",
            "[Critère 2 : typologie / surface / standing]": "Logements récents (2016-2020), normes Minergie, typologie familiale de 3 à 5 pièces.",
            "[Critère 3 : date de transaction]": "Actes notariés enregistrés entre fin 2025 et début 2026 au Registre Foncier.",
            "MÉTHODE DE NORMALISATION": "Normalisation D&V : Référence ancre = Saut-du-Loup 16 (17’609 CHF/m²). Base pondérée retenue à " + Number(basePriceM2).toLocaleString('fr-CH') + " CHF/m²."
          }`;

html = html.replace(oldSlide9Replacements, newSlide9Replacements);

await Bun.write(filePath, html);
console.log("Successfully enhanced public/dv/index.html! New length:", html.length);
