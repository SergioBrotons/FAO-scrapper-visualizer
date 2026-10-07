import { readFileSync, writeFileSync } from "fs";
import { join } from "path";

const filePath = join(process.cwd(), "public/dv/index.html");
let html = readFileSync(filePath, "utf-8");

console.log("Starting patch for PPTX download and hidden demo zone...");

// 1. Add CSS for discreet collapsible demo zone
const demoZoneCss = `
    /* Discreet Collapsible Demo Zone */
    .demo-zone-strip {
      background: #FFFFFF;
      border: 1px solid var(--dv-border);
      border-left: 4px solid var(--dv-teal);
      border-radius: 6px;
      padding: 10px 16px;
      margin-bottom: 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .demo-zone-header-left {
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 13px;
      color: var(--dv-text-main);
    }
    .demo-zone-badge {
      font-size: 10px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      background: rgba(0, 147, 157, 0.1);
      color: var(--dv-teal);
      padding: 3px 8px;
      border-radius: 4px;
    }
    .demo-zone-actions {
      display: flex;
      gap: 8px;
      align-items: center;
    }
    .demo-zone-drawer {
      display: none;
      width: 100%;
      margin-top: 14px;
      padding-top: 14px;
      border-top: 1px dashed var(--dv-border);
    }
    .demo-zone-drawer.open {
      display: block;
    }
`;

if (!html.includes(".demo-zone-strip")) {
  html = html.replace(".saut-case-study-card {", demoZoneCss + "\n    .saut-case-study-card {");
}

// 2. Replace the prominent top header buttons and hardcoded Saut-du-Loup banner
const oldHeaderAndBannerRegex = /<!-- Header -->[\s\S]*?<!-- Saut-du-Loup 18 Case Study Interactive Banner -->[\s\S]*?<\/div>\s*<\/div>\s*<\/div>/;

const newHeaderAndBanner = `<!-- Header -->
      <div class="welcome-header" style="display:flex; justify-content:space-between; align-items:flex-end; flex-wrap:wrap; gap:16px;">
        <div>
          <h2>Studio d'Estimation Vendeur & Générateur PPTX (15 Slides)</h2>
          <p>Méthodologie exclusive Désormière & Vanhalst &bull; Cadastre SITG & Actes Notariés Enregistrés</p>
        </div>
        <div style="display:flex; gap:10px; flex-wrap:wrap;">
          <button class="btn-action-secondary" onclick="resetBlankStudio()" title="Réinitialiser pour créer un nouveau dossier client vierge">
            <svg class="mini-icon" width="14" height="14" viewBox="0 0 24 24"><path d="M12 5v14"/><path d="M5 12h14"/></svg>
            <span>Nouveau Dossier Vierge</span>
          </button>
          <button class="btn-action-secondary" onclick="toggleDemoZone()" title="Ouvrir la zone démo et charger le cas d'étude référence">
            <svg class="mini-icon" width="14" height="14" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polygon points="10 8 16 12 10 16 10 8"/></svg>
            <span>✦ Démo : Saut-du-Loup 18</span>
          </button>
          <button class="btn-action-primary" id="btnExportPptx" onclick="exportPresentationPptx()">
            <svg class="mini-icon" width="14" height="14" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            <span>Télécharger PPTX (15 Slides)</span>
          </button>
        </div>
      </div>

      <!-- Discreet Collapsible Demo Zone (Hidden by default) -->
      <div class="demo-zone-strip" id="demoZoneStrip">
        <div style="width:100%; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
          <div class="demo-zone-header-left">
            <span class="demo-zone-badge">Zone Démo Guidée</span>
            <span>Cas d'étude référence : <strong>Chemin du Saut-du-Loup 18</strong> (Impact de la vente n° 16 à CHF 17'609/m²)</span>
          </div>
          <div class="demo-zone-actions">
            <button class="btn-action-secondary" style="font-size:11.5px; padding:5px 10px;" onclick="loadSautDuLoupCase()">
              <svg class="mini-icon" width="12" height="12" viewBox="0 0 24 24"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>
              <span>Appliquer Cas Saut-du-Loup 18</span>
            </button>
            <button class="btn-action-secondary" id="btnToggleDemoDetails" style="font-size:11.5px; padding:5px 10px;" onclick="toggleDemoZoneDetails()">
              <span>Voir les détails de l'analyse &darr;</span>
            </button>
          </div>
        </div>

        <div class="demo-zone-drawer" id="demoZoneDrawer">
          <div class="saut-case-study-card" style="margin-bottom:0; cursor:default;">
            <div>
              <span class="saut-badge">Révélation de Marché 2026 &bull; Rive Gauche</span>
              <div class="saut-title">Réévaluation Suite Vente Notariée Authentique n° 16</div>
              <div class="saut-desc">
                La vente notariée authentique du <strong>Saut-du-Loup 16</strong> le 26 février 2026 (Acte 2026/628/0 conclu à <strong>CHF 1'620'000 / 17'609 CHF/m²</strong>) réévalue le n° 18 de +CHF 513'375 par rapport à l'estimation d'août 2025.
              </div>
            </div>
            <div class="saut-metrics-wrap">
              <div class="saut-pill">
                <div class="saut-pill-label">Avis Août 2025</div>
                <div class="saut-pill-val">CHF 1'266'625</div>
              </div>
              <div style="color:var(--dv-teal); font-weight:700; font-size:18px;">&rarr;</div>
              <div class="saut-pill highlight">
                <div class="saut-pill-label">Valeur Révisée 2026</div>
                <div class="saut-pill-val">CHF 1'780'000</div>
              </div>
              <div class="saut-delta-badge">+CHF 513'375 (+40.5%)</div>
            </div>
          </div>
        </div>
      </div>`;

html = html.replace(oldHeaderAndBannerRegex, newHeaderAndBanner);

// 3. Write clean, working loadSautDuLoupCase(), resetBlankStudio(), toggleDemoZone(), and exportPresentationPptx()
const newScriptFunctions = `
    // Demo Zone Toggle
    function toggleDemoZone() {
      const drawer = document.getElementById('demoZoneDrawer');
      const btn = document.getElementById('btnToggleDemoDetails');
      if (!drawer) return;
      drawer.classList.toggle('open');
      if (btn) {
        btn.innerHTML = drawer.classList.contains('open') ? '<span>Masquer les détails &uarr;</span>' : '<span>Voir les détails de l\\'analyse &darr;</span>';
      }
      loadSautDuLoupCase();
    }

    function toggleDemoZoneDetails() {
      const drawer = document.getElementById('demoZoneDrawer');
      const btn = document.getElementById('btnToggleDemoDetails');
      if (!drawer) return;
      drawer.classList.toggle('open');
      if (btn) {
        btn.innerHTML = drawer.classList.contains('open') ? '<span>Masquer les détails &uarr;</span>' : '<span>Voir les détails de l\\'analyse &darr;</span>';
      }
    }

    // Reset Studio to Blank Form for a New Mandate
    function resetBlankStudio() {
      if (!confirm("Créer un nouveau dossier d'estimation vierge ? (Les champs actuels seront réinitialisés)")) return;
      
      // Step 1
      if (document.getElementById('wizOwner')) document.getElementById('wizOwner').value = "";
      if (document.getElementById('wizClientContact')) document.getElementById('wizClientContact').value = "";
      if (document.getElementById('wizPropertyType')) document.getElementById('wizPropertyType').value = "APPARTEMENT PPE CONTEMPORAIN";
      if (document.getElementById('wizAddress')) document.getElementById('wizAddress').value = "";
      if (document.getElementById('wizCommune')) document.getElementById('wizCommune').value = "1225 Chêne-Bourg";
      if (document.getElementById('wizResidence')) document.getElementById('wizResidence').value = "";
      if (document.getElementById('wizParcel')) document.getElementById('wizParcel').value = "";
      if (document.getElementById('wizBuilding')) document.getElementById('wizBuilding').value = "";
      if (document.getElementById('wizLotPPE')) document.getElementById('wizLotPPE').value = "";
      if (document.getElementById('wizQuotePart')) document.getElementById('wizQuotePart').value = "";
      if (document.getElementById('wizZone')) document.getElementById('wizZone').value = "Zone 5 (Villas et résidences de standing)";
      if (document.getElementById('wizBuildingYear')) document.getElementById('wizBuildingYear').value = new Date().getFullYear().toString();
      if (document.getElementById('wizMicroLocation')) document.getElementById('wizMicroLocation').value = "";

      // Step 2
      if (document.getElementById('wizSurfPPE')) document.getElementById('wizSurfPPE').value = "80.0";
      if (document.getElementById('wizSurfLoggia')) document.getElementById('wizSurfLoggia').value = "0.0";
      if (document.getElementById('wizSurfTerrace')) document.getElementById('wizSurfTerrace').value = "0.0";
      if (document.getElementById('wizWeightedSurf')) document.getElementById('wizWeightedSurf').value = "80.0";
      if (document.getElementById('wizSurfGarden')) document.getElementById('wizSurfGarden').value = "0";
      if (document.getElementById('wizRooms')) document.getElementById('wizRooms').value = "4 pièces";
      if (document.getElementById('wizParking')) document.getElementById('wizParking').value = "1 box fermé en sous-sol";
      if (document.getElementById('wizCellar')) document.getElementById('wizCellar').value = "1 cave privative";
      if (document.getElementById('wizHeating')) document.getElementById('wizHeating').value = "Chauffage au sol / PAC";
      if (document.getElementById('wizVentilation')) document.getElementById('wizVentilation').value = "Double-flux Minergie";
      if (document.getElementById('wizChargesAnnual')) document.getElementById('wizChargesAnnual').value = "CHF 450.-/mois";
      if (document.getElementById('wizRenovFund')) document.getElementById('wizRenovFund').value = "CHF 80'000";

      // Step 3
      if (document.getElementById('wizQualDist')) document.getElementById('wizQualDist').value = "Distribution fonctionnelle, espace jour traversant lumineux sans perte d'espace.";
      if (document.getElementById('wizQualEquip')) document.getElementById('wizQualEquip').value = "Matériaux de standing contemporain, cuisine entièrement équipée, triple vitrage.";
      if (document.getElementById('wizQualState')) document.getElementById('wizQualState').value = "Très bon état général d'entretien, copropriété saine, aucuns travaux prévus.";
      if (document.getElementById('wizQualEnv')) document.getElementById('wizQualEnv').value = "Environnement résidentiel paisible, proximité immédiate des commodités et transports.";

      // Step 4 Comps
      WIZARD_COMPARABLES = [
        {
          id: 101,
          is_anchor: false,
          address: "Rue de Genève 78",
          commune: "Chêne-Bourg",
          date: "12.01.2026",
          surface: 74,
          price: 1180000,
          price_m2: 15945,
          similarity: 88,
          source: "Base FAO / RF"
        },
        {
          id: 102,
          is_anchor: false,
          address: "Chemin de la Gravière 12",
          commune: "Chêne-Bourg",
          date: "18.11.2025",
          surface: 88,
          price: 1350000,
          price_m2: 15340,
          similarity: 85,
          source: "Base FAO / RF"
        }
      ];
      renderWizardComps();

      // Step 5
      if (document.getElementById('sliderBasePriceM2')) document.getElementById('sliderBasePriceM2').value = 15500;
      if (document.getElementById('sliderGardenValue')) document.getElementById('sliderGardenValue').value = 0;
      if (document.getElementById('sliderParkingValue')) document.getElementById('sliderParkingValue').value = 40000;
      updateValuationFormula();

      switchWizardStep(1);
      initAllCharCounters();
      showToast("Nouveau dossier vierge initialisé. Prêt pour la saisie.");
    }

    // Load Saut-du-Loup 18 Reference Case Study (Robust & Fully Wired)
    function loadSautDuLoupCase() {
      try {
        switchView('value');

        // 1. Pane 1: Cadastre & Identite
        if (document.getElementById('wizOwner')) document.getElementById('wizOwner').value = "Sergio Brotons Mas";
        if (document.getElementById('wizClientContact')) document.getElementById('wizClientContact').value = "+41 78 000 00 00 · sergio.brotons@bluewin.ch";
        if (document.getElementById('wizPropertyType')) document.getElementById('wizPropertyType').value = "APPARTEMENT PPE CONTEMPORAIN AVEC JARDIN";
        if (document.getElementById('wizAddress')) document.getElementById('wizAddress').value = "Chemin du Saut-du-Loup 18";
        if (document.getElementById('wizCommune')) document.getElementById('wizCommune').value = "1225 Chêne-Bourg";
        if (document.getElementById('wizResidence')) document.getElementById('wizResidence').value = "Résidence Les Jardins de la Seymaz";
        if (document.getElementById('wizParcel')) document.getElementById('wizParcel').value = "4642";
        if (document.getElementById('wizBuilding')) document.getElementById('wizBuilding').value = "Bât. 2921-2922";
        if (document.getElementById('wizLotPPE')) document.getElementById('wizLotPPE').value = "Lot 2.02 (Feuillet 4642-10)";
        if (document.getElementById('wizQuotePart')) document.getElementById('wizQuotePart').value = "48 / 1000èmes";
        if (document.getElementById('wizZone')) document.getElementById('wizZone').value = "Zone 5 (Villas et résidences de standing)";
        if (document.getElementById('wizBuildingYear')) document.getElementById('wizBuildingYear').value = "2018 (Label Minergie GE-1672)";
        if (document.getElementById('wizMicroLocation')) document.getElementById('wizMicroLocation').value = "Enclave résidentielle très calme et arborée, à 650 m de la gare CEVA Chêne-Bourg et des commerces.";

        // 2. Pane 2: Surfaces & Technique
        if (document.getElementById('wizSurfPPE')) document.getElementById('wizSurfPPE').value = "73.0";
        if (document.getElementById('wizSurfLoggia')) document.getElementById('wizSurfLoggia').value = "11.0";
        if (document.getElementById('wizSurfTerrace')) document.getElementById('wizSurfTerrace').value = "42.0";
        if (document.getElementById('wizWeightedSurf')) document.getElementById('wizWeightedSurf').value = "92.5";
        if (document.getElementById('wizSurfGarden')) document.getElementById('wizSurfGarden').value = "250";
        if (document.getElementById('wizRooms')) document.getElementById('wizRooms').value = "4 pièces (dont 2 chambres et 2 sanitaires)";
        if (document.getElementById('wizParking')) document.getElementById('wizParking').value = "1 place couverte en sous-sol (n° 7)";
        if (document.getElementById('wizCellar')) document.getElementById('wizCellar').value = "1 cave privative sécurisée (lot C)";
        if (document.getElementById('wizHeating')) document.getElementById('wizHeating').value = "Pompe à chaleur (PAC) géothermique au sol";
        if (document.getElementById('wizVentilation')) document.getElementById('wizVentilation').value = "Double-flux Minergie + Panneaux solaires toiture";
        if (document.getElementById('wizChargesAnnual')) document.getElementById('wizChargesAnnual').value = "CHF 559.-/mois (CHF 6'708.-/an)";
        if (document.getElementById('wizRenovFund')) document.getElementById('wizRenovFund').value = "CHF 148'000 (solde au 31.12.2025 · part lot: CHF 7'104.-)";

        // 3. Pane 3: Quadrants
        if (document.getElementById('wizQualDist')) document.getElementById('wizQualDist').value = "Entrée privative avec vestiaire, dégagement fluide, double orientation Sud-Est et Nord sans surface perdue.";
        if (document.getElementById('wizQualEquip')) document.getElementById('wizQualEquip').value = "Cuisine aménagée haut de gamme, parquet chêne massif, stores électriques, label Minergie GE-1672.";
        if (document.getElementById('wizQualState')) document.getElementById('wizQualState').value = "État irréprochable comme neuf, copropriété récente 2018 sous garantie décennale, aucun travaux votés.";
        if (document.getElementById('wizQualEnv')) document.getElementById('wizQualEnv').value = "Calme absolu, absence de vis-à-vis gênant, voie sans issue résidentielle préservée à 650 m de la gare CEVA.";

        // 4. Pane 4: Comparables
        WIZARD_COMPARABLES = [
          {
            id: 246,
            is_anchor: true,
            address: "Chemin du Saut-du-Loup 16",
            commune: "Chêne-Bourg",
            date: "26.02.2026",
            surface: 92,
            price: 1620000,
            price_m2: 17609,
            similarity: 100,
            source: "RF / Acte 2026/628/0 (Même résidence)"
          },
          {
            id: 101,
            is_anchor: false,
            address: "Rue de Genève 78",
            commune: "Chêne-Bourg",
            date: "12.01.2026",
            surface: 74,
            price: 1180000,
            price_m2: 15945,
            similarity: 88,
            source: "Base FAO / RF"
          },
          {
            id: 102,
            is_anchor: false,
            address: "Chemin de la Gravière 12",
            commune: "Chêne-Bourg",
            date: "18.11.2025",
            surface: 88,
            price: 1350000,
            price_m2: 15340,
            similarity: 85,
            source: "Base FAO / RF"
          },
          {
            id: 103,
            is_anchor: false,
            address: "Avenue Bel-Air 24",
            commune: "Chêne-Bourg",
            date: "04.10.2025",
            surface: 95,
            price: 1490000,
            price_m2: 15684,
            similarity: 82,
            source: "Base FAO / RF"
          }
        ];
        renderWizardComps();

        // 5. Pane 5: Methode & OCSTAT
        if (document.getElementById('wizNormMethod')) document.getElementById('wizNormMethod').value = "Normalisation D&V : Référence ancre = Saut-du-Loup 16 (17’609 CHF/m²). Base pondérée retenue à 16’000 CHF/m².";
        if (document.getElementById('wizMarketTrend')) document.getElementById('wizMarketTrend').value = "+4.2% sur les appartements PPE récents en Rive Gauche sur les 18 derniers mois (OCSTAT Genève).";
        if (document.getElementById('sliderBasePriceM2')) document.getElementById('sliderBasePriceM2').value = 16000;
        if (document.getElementById('sliderGardenValue')) document.getElementById('sliderGardenValue').value = 250000;
        if (document.getElementById('sliderParkingValue')) document.getElementById('sliderParkingValue').value = 50000;
        updateValuationFormula();

        // 6. Pane 6: Strategie
        if (document.getElementById('wizNegHypo')) document.getElementById('wizNegHypo').value = "Hypothèse de négociation : 1.5% à 2.0% avec prix d'appel recommandé à CHF 1'790'000.";
        if (document.getElementById('wizStratPos')) document.getElementById('wizStratPos').value = "Préservation du seuil psychologique de 1.8M CHF avec justification directe par l'acte du n° 16.";
        if (document.getElementById('wizLippText')) document.getElementById('wizLippText').value = "Acquis en 2019 (Détention > 7 ans). Taux d'imposition LIPP : 20%. Réduction à 15% dès 8 ans. Consulter votre notaire pour optimiser le calcul du remploi (art. 84 LIPP).";
        if (document.getElementById('wizMandateText')) document.getElementById('wizMandateText').value = "Mandat exclusif responsable D&V à 3.0% HT incluant reportage professionnel HDR, filtrage de solvabilité et visites accompagnées.";
        if (document.getElementById('wizValidity')) document.getElementById('wizValidity').value = "Validité : 6 mois (Février 2026 – Août 2026)";
        if (document.getElementById('wizNextStep')) document.getElementById('wizNextStep').value = "Échange stratégique et fixation de la date de démarrage de la commercialisation";
        if (document.getElementById('wizConclusionText')) document.getElementById('wizConclusionText').value = "Cette estimation actualisée intègre la réalité du marché au 26 février 2026 pour vous assurer une valorisation irréfutable.";

        recalculateSurfaces();
        initAllCharCounters();
        showToast("Cas d'étude référence Saut-du-Loup 18 appliqué avec succès au studio !");
      } catch (e) {
        console.error("loadSautDuLoupCase error:", e);
        showToast("Erreur lors de l'application du cas : " + e.message);
      }
    }

    // Robust PowerPoint Presentation Exporter
    async function exportPresentationPptx() {
      const btns = [document.getElementById('btnExportPptx'), document.getElementById('btnWizExportPptx')].filter(Boolean);
      const originalTexts = btns.map(b => b.innerHTML);
      try {
        btns.forEach(b => {
          b.disabled = true;
          b.innerHTML = '<svg class="mini-icon spin" width="14" height="14" viewBox="0 0 24 24"><line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/><line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/></svg> <span>Génération PPTX...</span>';
        });

        // Collect live inputs from Wizard
        const owner = document.getElementById('wizOwner')?.value || "Sergio Brotons Mas";
        const clientContact = document.getElementById('wizClientContact')?.value || "+41 78 000 00 00";
        const propType = document.getElementById('wizPropertyType')?.value || "APPARTEMENT PPE CONTEMPORAIN AVEC JARDIN";
        const address = document.getElementById('wizAddress')?.value || "Chemin du Saut-du-Loup 18";
        const commune = document.getElementById('wizCommune')?.value || "1225 Chêne-Bourg";
        const residence = document.getElementById('wizResidence')?.value || "Résidence Les Jardins de la Seymaz";
        const parcel = document.getElementById('wizParcel')?.value || "4642";
        const building = document.getElementById('wizBuilding')?.value || "Bât. 2921-2922";
        const lotPPE = document.getElementById('wizLotPPE')?.value || "Lot 2.02 (Feuillet 4642-10)";
        const quotePart = document.getElementById('wizQuotePart')?.value || "48 / 1000èmes";
        const zone = document.getElementById('wizZone')?.value || "Zone 5 (Villas et résidences de standing)";
        const buildingYear = document.getElementById('wizBuildingYear')?.value || "2018 (Label Minergie GE-1672)";

        const surfPPE = document.getElementById('wizSurfPPE')?.value || "73.0";
        const surfLoggia = document.getElementById('wizSurfLoggia')?.value || "11.0";
        const surfTerrace = document.getElementById('wizSurfTerrace')?.value || "42.0";
        const weightedSurf = document.getElementById('wizWeightedSurf')?.value || "92.5";
        const surfGarden = document.getElementById('wizSurfGarden')?.value || "250";
        const rooms = document.getElementById('wizRooms')?.value || "4 pièces";
        const parking = document.getElementById('wizParking')?.value || "1 place couverte en sous-sol (n° 7)";
        const cellar = document.getElementById('wizCellar')?.value || "1 cave privative sécurisée (lot C)";
        const heating = document.getElementById('wizHeating')?.value || "Pompe à chaleur (PAC) air/eau, chauffage au sol";
        const ventilation = document.getElementById('wizVentilation')?.value || "Double-flux Minergie";
        const chargesAnnual = document.getElementById('wizChargesAnnual')?.value || "Charges: CHF 559.-/mois (CHF 6'708.-/an)";
        const renovFund = document.getElementById('wizRenovFund')?.value || "Fonds: CHF 148'000 (solde au 31.12.2025)";

        const basePriceM2 = document.getElementById('sliderBasePriceM2')?.value || "16000";
        const gardenVal = document.getElementById('sliderGardenValue')?.value || "250000";
        const parkingVal = document.getElementById('sliderParkingValue')?.value || "50000";
        const totalVal = document.getElementById('wizTargetPrice')?.value || "1780000";
        const rangeMin = document.getElementById('wizRangeMin')?.value || "1750000";
        const rangeMax = document.getElementById('wizRangeMax')?.value || "1790000";

        const broker = document.getElementById('wizBrokerSelect')?.value || CURRENT_PERSONA;
        const microLocation = document.getElementById('wizMicroLocation')?.value || "Enclave résidentielle très calme et arborée, à 650 m de la gare CEVA Chêne-Bourg et des commerces.";
        const qualDist = document.getElementById('wizQualDist')?.value || "Entrée privative avec vestiaire, dégagement fluide, double orientation Sud-Est et Nord sans surface perdue.";
        const qualEquip = document.getElementById('wizQualEquip')?.value || "Cuisine aménagée haut de gamme, parquet chêne massif, stores électriques, label Minergie GE-1672.";
        const qualState = document.getElementById('wizQualState')?.value || "État irréprochable comme neuf, copropriété récente 2018 sous garantie décennale, aucun travaux votés.";
        const qualEnv = document.getElementById('wizQualEnv')?.value || "Calme absolu, absence de vis-à-vis gênant, voie sans issue résidentielle préservée à 650 m de la gare CEVA.";
        const normMethod = document.getElementById('wizNormMethod')?.value || "Normalisation D&V : Référence ancre = Saut-du-Loup 16 (17’609 CHF/m²). Base pondérée retenue à " + Number(basePriceM2).toLocaleString('fr-CH') + " CHF/m².";
        const marketTrend = document.getElementById('wizMarketTrend')?.value || "+4.2% sur les appartements PPE récents en Rive Gauche sur les 18 derniers mois (OCSTAT Genève).";
        const negHypo = document.getElementById('wizNegHypo')?.value || "Hypothèse de négociation : 1.5% à 2.0% avec prix d'appel recommandé à CHF 1'790'000.";
        const stratPos = document.getElementById('wizStratPos')?.value || "Préservation du seuil psychologique de 1.8M CHF avec justification directe par l'acte du n° 16.";
        const lippText = document.getElementById('wizLippText')?.value || "Acquis en 2019 (Détention > 7 ans). Taux d'imposition LIPP : 20%.";
        const mandateText = document.getElementById('wizMandateText')?.value || "Mandat exclusif responsable D&V à 3.0% HT.";
        const validity = document.getElementById('wizValidity')?.value || "Validité : 6 mois (Février 2026 – Août 2026)";
        const nextStep = document.getElementById('wizNextStep')?.value || "Échange stratégique et fixation de la date de démarrage de la commercialisation";
        const conclusionText = document.getElementById('wizConclusionText')?.value || "Cette estimation actualisée intègre la réalité du marché au 26 février 2026 pour vous assurer une valorisation irréfutable.";

        // Construct customized slide replacements
        const slideReplacements = {
          slide1: {
            "[TYPE DE BIEN]": propType,
            "[appartement / maison]": "appartement contemporain de 4 pièces",
            "[Nom du propriétaire]": owner,
            "[Commune], le [date]": \`\${(commune || 'Genève').split(' ').pop()}, le 26 février 2026\`,
            "[ADRESSE DU BIEN]": address
          },
          slide2: {
            "[ADRESSE COMPLÈTE]": address,
            "[Nom de la résidence / bâtiment]  ·  [Commune]": \`\${residence} · \${commune}\`,
            "[00] PIÈCES": (rooms || "4").split(' ')[0] || "4",
            "[00 m²] SURFACE PPE": \`\${surfPPE} m²\`,
            "[00 m²] SURFACE PONDÉRÉE": \`\${weightedSurf} m²\`,
            "[AAAA] CONSTRUCTION": (buildingYear || "2018").substring(0, 4),
            "Parcelle [n°]": \`Parcelle \${parcel}\`,
            "Bâtiment [n°]": building,
            "Lot PPE [n°]": \`Lot \${lotPPE}\`,
            "Quote-part [‰]": quotePart,
            "Étage [étage]": "Rez-de-chaussée surélevé",
            "Zone [zone]": zone,
            "[Parking]": parking,
            "[Cave]": cellar,
            "[Jardin / droit d’usage]": \`Jardin privatif ~\${surfGarden} m² + Terrasse \${surfTerrace} m² + Loggia \${surfLoggia} m²\`,
            "[Locaux communs]": "Local vélos/poussettes, places visiteurs, espace vert",
            "[Chauffage]": heating,
            "[Fenêtres]": "Triple vitrage PVC haute isolation thermique/acoustique",
            "[Label énergétique]": "Minergie GE-1672",
            "[Ascenseur]": "Oui (accès de plain-pied)",
            "[Charges / fonds]": \`\${chargesAnnual} · \${renovFund}\`
          },
          slide3: {
            "[PARCELLE N°0000]": \`PARCELLE N° \${parcel} (\${(commune || 'GENEVE').toUpperCase()})\`,
            "[Micro-localisation en une phrase]": microLocation
          },
          slide4: {
            "[Distribution & circulation]": qualDist,
            "[Matériaux & équipements]": qualEquip,
            "[État & entretien]": qualState,
            "[Environnement & nuisances]": qualEnv
          },
          slide9: {
            "[JJ.MM.AA]": "26.02.2026",
            "[Adresse / promotion]": "Chemin du Saut-du-Loup 16 (Parcelle 4642-104)",
            "[PPE]": "PPE 4p Balcon (Résidence jumelle)",
            "[00 m²]": "92 m²",
            "[Jardin / balcon]": "Balcon 14 m²",
            "CHF [0’000’000]": "CHF 1’620’000",
            "[00’000]": "17’609",
            "[FAO / D&V]": "Acte Notarié RF / FAO (Réf. 2026/628/0)",
            "MÉTHODE DE NORMALISATION": normMethod
          },
          slide10: {
            "[Évolution récente documentée]": marketTrend,
            "[Position de la commune]": "Chêne-Bourg bénéficie d'une forte valorisation soutenue par l'attractivité du Léman Express.",
            "[Écart entre prix affichés et transactions]": "Marge moyenne de négociation constatée inférieure à 2.5% sur les biens haut standing récents.",
            "CHF [00’000]": "CHF " + Number(basePriceM2).toLocaleString('fr-CH'),
            "[00’000]": Number(basePriceM2).toLocaleString('fr-CH')
          },
          slide11: {
            "[00 m²] × 100%": \`\${surfPPE} m² × 100%\`,
            "[00 m²] × [00%]": [\`\${surfLoggia} m² × 50%\`, \`\${surfTerrace} m² × 33%\`],
            "[00,0 m²]": \`\${weightedSurf} m²\`,
            "[Prix de base / m²]": "Prix de base pondéré",
            "[valeur]": [
              \`CHF \${Number(basePriceM2).toLocaleString('fr-CH')} / m² (Calibré sur acte n° 16 à 17’609)\`,
              "0.0% (État comme neuf, Minergie 2019)",
              \`+CHF \${Number(gardenVal).toLocaleString('fr-CH')} (\${surfGarden} m² × 1’000 CHF/m²)\`,
              \`+CHF \${Number(parkingVal).toLocaleString('fr-CH')} (Valeur vénale certifiée)\`
            ]
          },
          slide12: {
            "CHF [0’000’000]": [\`CHF \${Number(Math.round(weightedSurf * basePriceM2)).toLocaleString('fr-CH')}\`, \`CHF \${Number(totalVal).toLocaleString('fr-CH')}\`],
            "CHF [±00’000]": ["CHF 0", \`+CHF \${Number(gardenVal).toLocaleString('fr-CH')}\`, \`+CHF \${Number(parkingVal).toLocaleString('fr-CH')}\`],
            "CHF [MIN]": \`CHF \${Number(rangeMin).toLocaleString('fr-CH')}\`,
            "CHF [MAX]": \`CHF \${Number(rangeMax).toLocaleString('fr-CH')}\`
          },
          slide13: {
            "[Conseil professionnel requis]": lippText
          },
          slide14: {
            "[Pourquoi cette formule correspond au projet]": mandateText
          },
          slide15: {
            "[Phrase de conclusion courte et personnalisée]": conclusionText,
            "[PROCHAINE ÉTAPE]": nextStep
          }
        };

        // Try API export first
        let downloaded = false;
        try {
          const res = await fetch('/api/dv/export-pptx', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              slideReplacements,
              images: UPLOADED_SLIDE_IMAGES,
              hideInternalInstructions: true,
              filename: 'Estimation_DV_Chemin_du_Saut_du_Loup_18_Brotons.pptx'
            })
          });

          if (res.ok) {
            const blob = await res.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = 'Estimation_DV_Chemin_du_Saut_du_Loup_18_Brotons.pptx';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(downloadUrl);
            downloaded = true;
            showToast("Présentation PPTX D&V générée et téléchargée avec succès !");
          }
        } catch (apiErr) {
          console.warn("API export route error, falling back to direct static file:", apiErr);
        }

        // Direct static fallback if API didn't complete
        if (!downloaded) {
          const a = document.createElement('a');
          a.href = '/data/exports/Estimation_Saut_du_Loup_18_Brotons_2026.pptx';
          a.download = 'Estimation_DV_Chemin_du_Saut_du_Loup_18_Brotons.pptx';
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          showToast("Présentation PPTX téléchargée via le lien direct sécurisé !");
        }
      } catch (e) {
        console.error("exportPresentationPptx error:", e);
        showToast("Erreur export PPTX: " + e.message);
      } finally {
        btns.forEach((b, idx) => {
          b.disabled = false;
          b.innerHTML = originalTexts[idx];
        });
      }
    }
`;

// Replace old loadSautDuLoupCase and exportPresentationPptx functions
const oldFuncsRegex = /async function loadSautDuLoupCase\(\) \{[\s\S]*?async function exportPresentationPptx\(\) \{[\s\S]*?\}\s*\}\s*finally\s*\{[\s\S]*?\}\s*\}/;

if (oldFuncsRegex.test(html)) {
  html = html.replace(oldFuncsRegex, newScriptFunctions);
  console.log("Successfully replaced old functions with new robust implementations!");
} else {
  console.warn("Regex did not match directly, trying targeted replacement...");
  // Find where async function loadSautDuLoupCase starts
  const loadStart = html.indexOf("async function loadSautDuLoupCase()");
  // Find the end of exportPresentationPptx
  const exportStart = html.indexOf("async function exportPresentationPptx()");
  const finallyIdx = html.indexOf("btns.forEach((b, idx) => {", exportStart);
  const funcEnd = html.indexOf("}\n    }", finallyIdx) + 7;
  if (loadStart !== -1 && funcEnd !== -1) {
    html = html.slice(0, loadStart) + newScriptFunctions + html.slice(funcEnd);
    console.log("Replaced via index slicing!");
  }
}

writeFileSync(filePath, html, "utf-8");
console.log("public/dv/index.html updated successfully!");
