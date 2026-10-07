import { readFileSync, writeFileSync } from 'fs';
import { join } from 'path';

const htmlPath = join(process.cwd(), 'public', 'dv', 'index.html');
let html = readFileSync(htmlPath, 'utf8');

console.log('Revamping public/dv/index.html: Removing all baked-in ghost data, unifying form and PPTX export...');

// 1. Initialize IS_DEMO_CASE instead of IS_VIERGE_MODE
html = html.replace('let IS_VIERGE_MODE = false;', 'let IS_DEMO_CASE = false;\n    let IS_VIERGE_MODE = true;');

// 2. Clean up Step 1 inputs (Card 1: Mandant & Couverture)
html = html.replace(
  '<input type="text" id="wizOwner" value="Sergio Brotons Mas">',
  '<input type="text" id="wizOwner" placeholder="Ex: Jean Dupont (Nom du mandant)">'
);

html = html.replace(
  '<input type="text" id="wizClientContact" value="+41 78 000 00 00 · sergio.brotons@bluewin.ch">',
  '<input type="text" id="wizClientContact" placeholder="Ex: +41 79 000 00 00 · contact@client.ch">'
);

html = html.replace(
  '<input type="text" id="wizPropertyType" value="APPARTEMENT PPE CONTEMPORAIN AVEC JARDIN">',
  '<input type="text" id="wizPropertyType" placeholder="Ex: APPARTEMENT PPE CONTEMPORAIN">'
);

// Clean up Step 1 inputs (Card 2: Cadastre & SITG)
html = html.replace(
  '<input type="text" id="wizAddress" value="Chemin du Saut-du-Loup 18"',
  '<input type="text" id="wizAddress" value=""'
);

html = html.replace(
  '<input type="text" id="wizCommune" value="1225 Chêne-Bourg">',
  '<input type="text" id="wizCommune" placeholder="Ex: 1225 Chêne-Bourg ou 1214 Vernier">'
);

html = html.replace(
  '<input type="text" id="wizResidence" value="Résidence Les Jardins de la Seymaz">',
  '<input type="text" id="wizResidence" placeholder="Ex: Résidence du Parc (optionnel)">'
);

html = html.replace(
  '<input type="text" id="wizParcel" value="4643">',
  '<input type="text" id="wizParcel" placeholder="Ex: 4642 (auto SITG)">'
);

html = html.replace(
  '<input type="text" id="wizBuilding" value="Bât. 2921-2922">',
  '<input type="text" id="wizBuilding" placeholder="Ex: Bât. A">'
);

html = html.replace(
  '<input type="text" id="wizLotPPE" value="Lot 2.02 (Feuillet 4642-10)">',
  '<input type="text" id="wizLotPPE" placeholder="Ex: Lot 2.01 (Feuillet 104)">'
);

html = html.replace(
  '<input type="text" id="wizQuotePart" value="132.5‰">',
  '<input type="text" id="wizQuotePart" placeholder="Ex: 48 / 1000èmes">'
);

html = html.replace(
  '<input type="text" id="wizZone" value="Zone 5 (Villas et résidences de standing)">',
  '<input type="text" id="wizZone" placeholder="Ex: Zone 5 (Villas et résidences)">'
);

html = html.replace(
  '<input type="text" id="wizFloor" value="Rez-de-chaussée surélevé">',
  '<input type="text" id="wizFloor" placeholder="Ex: 2ème étage avec ascenseur">'
);

html = html.replace(
  '<input type="text" id="wizBuildingYear" value="2019 (Label Minergie GE-1672)">',
  '<input type="text" id="wizBuildingYear" placeholder="Ex: 2018 (auto SITG)">'
);

// Clean up Card 3: Micro-secteur Slide 3
html = html.replace(
  '<textarea id="wizMicroLocation" rows="3">Enclave résidentielle très calme et arborée, à 650 m de la gare CEVA Chêne-Bourg et des commerces.</textarea>',
  '<textarea id="wizMicroLocation" rows="3" placeholder="Ex: Enclave résidentielle paisible, à proximité immédiate des transports publics, écoles et commerces."></textarea>'
);

// Clean up Step 2 (Surfaces & Technique)
html = html.replace(
  '<input type="number" id="wizSurfPPE" value="73.0" step="0.5" oninput="recalculateSurfaces()">',
  '<input type="number" id="wizSurfPPE" value="" placeholder="Ex: 85.0" step="0.5" oninput="recalculateSurfaces()">'
);

html = html.replace(
  '<input type="number" id="wizSurfLoggia" value="11.0" step="0.5" oninput="recalculateSurfaces()">',
  '<input type="number" id="wizSurfLoggia" value="" placeholder="0" step="0.5" oninput="recalculateSurfaces()">'
);

html = html.replace(
  '<input type="number" id="wizSurfTerrace" value="42.0" step="0.5" oninput="recalculateSurfaces()">',
  '<input type="number" id="wizSurfTerrace" value="" placeholder="0" step="0.5" oninput="recalculateSurfaces()">'
);

html = html.replace(
  '<input type="number" id="wizSurfGarden" value="250" step="1" oninput="recalculateSurfaces()">',
  '<input type="number" id="wizSurfGarden" value="0" placeholder="0" step="1" oninput="recalculateSurfaces()">'
);

html = html.replace(
  '<input type="text" id="wizWeightedSurf" value="92.5" readonly>',
  '<input type="text" id="wizWeightedSurf" value="" placeholder="—" readonly>'
);

html = html.replace(
  '<input type="text" id="wizRooms" value="4 pièces (dont 2 chambres et 2 sanitaires)">',
  '<input type="text" id="wizRooms" placeholder="Ex: 4 pièces (dont 2 chambres)">'
);

html = html.replace(
  '<input type="text" id="wizParking" value="1 place couverte en sous-sol (n° 7)">',
  '<input type="text" id="wizParking" placeholder="Ex: 1 place couverte en sous-sol / box">'
);

html = html.replace(
  '<input type="text" id="wizCellar" value="1 cave privative sécurisée (lot C)">',
  '<input type="text" id="wizCellar" placeholder="Ex: 1 cave privative sécurisée">'
);

html = html.replace(
  '<input type="text" id="wizHeating" value="Pompe à chaleur (PAC) géothermique au sol">',
  '<input type="text" id="wizHeating" placeholder="Ex: Pompe à chaleur au sol / Chauffage à distance">'
);

html = html.replace(
  '<input type="text" id="wizVentilation" value="Double-flux Minergie + Panneaux solaires toiture">',
  '<input type="text" id="wizVentilation" placeholder="Ex: Double-flux / Panneaux solaires">'
);

html = html.replace(
  '<input type="text" id="wizChargesAnnual" value="CHF 559.-/mois (CHF 6\'708.-/an)">',
  '<input type="text" id="wizChargesAnnual" placeholder="Ex: CHF 480.-/mois (CHF 5\'760.-/an)">'
);

html = html.replace(
  '<input type="text" id="wizRenovFund" value="CHF 148\'000 (solde au 31.12.2025 · part lot: CHF 7\'104.-)">',
  '<input type="text" id="wizRenovFund" placeholder="Ex: CHF 120\'000 (solde au 31.12.2025)">'
);

// Clean up Step 3 (Quadrants Slide 4)
html = html.replace(
  '<textarea id="wizQualDist" rows="3">Entrée privative avec vestiaire intégré, dégagement fluide, double orientation Sud-Est et Nord sans surface perdue.</textarea>',
  '<textarea id="wizQualDist" rows="3" placeholder="Ex: Entrée privative avec vestiaire, dégagement fluide, double orientation sans surface perdue."></textarea>'
);

html = html.replace(
  '<textarea id="wizQualEquip" rows="3">Cuisine aménagée haut de gamme, parquet chêne massif brossé, stores à lamelles électriques, label Minergie GE-1672.</textarea>',
  '<textarea id="wizQualEquip" rows="3" placeholder="Ex: Cuisine agencée de standing, parquet chêne, stores électriques, finitions soignées."></textarea>'
);

html = html.replace(
  '<textarea id="wizQualState" rows="3">État irréprochable comme neuf, copropriété récente 2018 sous garantie décennale, aucun appel de fonds extraordinaire voté en AG.</textarea>',
  '<textarea id="wizQualState" rows="3" placeholder="Ex: État irréprochable comme neuf, copropriété saine, aucun travaux extraordinaires votés."></textarea>'
);

html = html.replace(
  '<textarea id="wizQualEnv" rows="3">Calme absolu, absence de vis-à-vis gênant, voie sans issue résidentielle très préservée à 650 m de la gare CEVA.</textarea>',
  '<textarea id="wizQualEnv" rows="3" placeholder="Ex: Environnement calme et résidentiel, sans vis-à-vis gênant, proximité des commodités."></textarea>'
);

// Clean up Step 4 (Slide 9 Normalisation)
html = html.replace(
  '<textarea id="wizNormMethod" rows="2">Normalisation D&V : Référence ancre = Saut-du-Loup 16 (17’609 CHF/m²). Base prudentielle retenue à 16’000 CHF/m² pour tenir compte de la surface pondérée.</textarea>',
  '<textarea id="wizNormMethod" rows="2" placeholder="Ex: Normalisation D&V basée sur les transactions authentiques récentes du secteur avec ajustement prudentiel."></textarea>'
);

// Clean up Step 6 (Stratégie Slide 12, 13, 14, 15)
html = html.replace(
  '<input type="number" id="wizRangeMin" value="1750000" oninput="syncRanges()">',
  '<input type="number" id="wizRangeMin" value="" placeholder="Ex: 1450000" oninput="syncRanges()">'
);

html = html.replace(
  '<input type="number" id="wizTargetPrice" value="1780000" oninput="syncRanges()">',
  '<input type="number" id="wizTargetPrice" value="" placeholder="Ex: 1490000" oninput="syncRanges()">'
);

html = html.replace(
  '<input type="number" id="wizRangeMax" value="1790000" oninput="syncRanges()">',
  '<input type="number" id="wizRangeMax" value="" placeholder="Ex: 1520000" oninput="syncRanges()">'
);

html = html.replace(
  '<input type="text" id="wizNegHypo" value="Hypothèse de négociation : 1.5% à 2.0% avec prix d\'appel recommandé à CHF 1\'790\'000.">',
  '<input type="text" id="wizNegHypo" placeholder="Ex: Marge de négociation prévisible : 1.5% à 2.5%">'
);

html = html.replace(
  '<input type="text" id="wizStratPos" value="Préservation du seuil psychologique de 1.8M CHF avec justification directe par l\'acte du n° 16.">',
  '<input type="text" id="wizStratPos" placeholder="Ex: Positionnement sous le seuil psychologique de...">'
);

html = html.replace(
  '<input type="text" id="wizLippText" value="Acquis en 2019 (Détention > 7 ans). Taux d\'imposition LIPP : 20%. Réduction à 15% dès 8 ans. Consulter votre notaire pour optimiser le calcul du remploi (art. 84 LIPP).">',
  '<input type="text" id="wizLippText" placeholder="Ex: Taux d\'imposition LIPP selon durée de détention. Consulter votre notaire pour le calcul du remploi.">'
);

html = html.replace(
  '<input type="text" id="wizMandateText" value="Mandat exclusif responsable D&V à 3.0% HT incluant reportage professionnel HDR, filtrage de solvabilité et visites accompagnées.">',
  '<input type="text" id="wizMandateText" placeholder="Ex: Mandat exclusif responsable D&V à 3.0% HT incluant reportage professionnel et visites qualifiées.">'
);

html = html.replace(
  '<input type="text" id="wizValidity" value="Validité : 6 mois (Février 2026 – Août 2026)">',
  '<input type="text" id="wizValidity" placeholder="Ex: Validité : 6 mois">'
);

html = html.replace(
  '<input type="text" id="wizNextStep" value="Échange stratégique et fixation de la date de démarrage de la commercialisation">',
  '<input type="text" id="wizNextStep" placeholder="Ex: Échange stratégique et fixation du calendrier de commercialisation">'
);

html = html.replace(
  '<textarea id="wizConclusionText" rows="3">Cette estimation actualisée intègre la réalité du marché au 26 février 2026 pour vous assurer une valorisation irréfutable.</textarea>',
  '<textarea id="wizConclusionText" rows="3" placeholder="Ex: Cette estimation actualisée intègre la réalité du marché notarié genevois pour assurer un positionnement optimal."></textarea>'
);

// 3. Make selectCadastreProperty CLEAN PREVIOUS SPECIFICS
const oldSelectPropertyBlock = /function selectCadastreProperty\(prop\) \{[\s\S]*?\/\/ 1\. Step 1: Cadastre & Identity/;
const newSelectPropertyBlock = `function selectCadastreProperty(prop) {
      IS_DEMO_CASE = false;
      const dropdown = document.getElementById('addressSuggestionsDropdown');
      if (dropdown) dropdown.style.display = 'none';
      if (!prop) return;

      // Reset specific building name & notes so ghost data never carries over!
      const resInput = document.getElementById('wizResidence');
      if (resInput) resInput.value = prop.residence || '';

      const microInput = document.getElementById('wizMicroLocation');
      if (microInput) microInput.value = '';

      // 1. Step 1: Cadastre & Identity`;

if (oldSelectPropertyBlock.test(html)) {
  html = html.replace(oldSelectPropertyBlock, newSelectPropertyBlock);
  console.log('✓ selectCadastreProperty updated with clean reset');
}

// 4. Update loadSautDuLoupCase to set IS_DEMO_CASE = true
if (html.includes('IS_VIERGE_MODE = false;')) {
  html = html.replace('IS_VIERGE_MODE = false;', 'IS_DEMO_CASE = true;\n        IS_VIERGE_MODE = false;');
  console.log('✓ loadSautDuLoupCase sets IS_DEMO_CASE = true');
}

// 5. Update resetBlankStudio to set IS_DEMO_CASE = false
if (html.includes('IS_VIERGE_MODE = true;')) {
  html = html.replace('IS_VIERGE_MODE = true;', 'IS_DEMO_CASE = false;\n      IS_VIERGE_MODE = true;');
  console.log('✓ resetBlankStudio sets IS_DEMO_CASE = false');
}

// 6. OVERHAUL exportPresentationPptx: ALWAYS BUILD FROM THE LIVE FORM!
const oldExportFunctionRegex = /async function exportPresentationPptx\(\) \{[\s\S]*?const res = await fetch\('\/api\/dv\/export-pptx'/;

const newExportFunctionJs = `async function exportPresentationPptx() {
      const btns = [document.getElementById('btnExportPptx'), document.getElementById('btnWizExportPptx')].filter(Boolean);
      const originalTexts = btns.map(b => b.innerHTML);
      try {
        btns.forEach(b => {
          b.disabled = true;
          b.innerHTML = '<svg class="mini-icon spin" width="14" height="14" viewBox="0 0 24 24"><line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/><line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/></svg> <span>Génération PPTX...</span>';
        });

        // The form is the SINGLE SOURCE OF TRUTH (SSOT)!
        const addressVal = document.getElementById('wizAddress')?.value?.trim() || '';
        const communeVal = document.getElementById('wizCommune')?.value?.trim() || '';
        const ownerVal = document.getElementById('wizOwner')?.value?.trim() || '';
        const propTypeVal = document.getElementById('wizPropertyType')?.value?.trim() || 'APPARTEMENT PPE CONTEMPORAIN';
        const residenceVal = document.getElementById('wizResidence')?.value?.trim() || '';
        const parcelVal = document.getElementById('wizParcel')?.value?.trim() || '';
        const buildingVal = document.getElementById('wizBuilding')?.value?.trim() || '';
        const lotVal = document.getElementById('wizLotPPE')?.value?.trim() || '';
        const quotePartVal = document.getElementById('wizQuotePart')?.value?.trim() || '';
        const zoneVal = document.getElementById('wizZone')?.value?.trim() || '';
        const floorVal = document.getElementById('wizFloor')?.value?.trim() || '';
        const yearVal = document.getElementById('wizBuildingYear')?.value?.trim() || '';
        const microLocationVal = document.getElementById('wizMicroLocation')?.value?.trim() || '';

        const surfPPE = document.getElementById('wizSurfPPE')?.value?.trim() || '';
        const surfLoggia = parseFloat(document.getElementById('wizSurfLoggia')?.value) || 0;
        const surfTerrace = parseFloat(document.getElementById('wizSurfTerrace')?.value) || 0;
        const surfGarden = parseFloat(document.getElementById('wizSurfGarden')?.value) || 0;
        const weightedSurf = document.getElementById('wizWeightedSurf')?.value?.trim() || surfPPE;
        const roomsVal = document.getElementById('wizRooms')?.value?.trim() || '';
        const parkingVal = document.getElementById('wizParking')?.value?.trim() || '';
        const cellarVal = document.getElementById('wizCellar')?.value?.trim() || '';
        const heatingVal = document.getElementById('wizHeating')?.value?.trim() || '';
        const chargesVal = document.getElementById('wizChargesAnnual')?.value?.trim() || '';
        const renovVal = document.getElementById('wizRenovFund')?.value?.trim() || '';

        const qualDistVal = document.getElementById('wizQualDist')?.value?.trim() || '';
        const qualEquipVal = document.getElementById('wizQualEquip')?.value?.trim() || '';
        const qualStateVal = document.getElementById('wizQualState')?.value?.trim() || '';
        const qualEnvVal = document.getElementById('wizQualEnv')?.value?.trim() || '';

        const normMethodVal = document.getElementById('wizNormMethod')?.value?.trim() || '';
        const ppeMedianStr = document.getElementById('wizOcstatPpeMedian')?.value?.trim() || '15\\\'500';
        const cantonMedianStr = document.getElementById('wizOcstatCantonMedian')?.value?.trim() || '14\\\'200';
        const trendStr = document.getElementById('wizOcstatTrend')?.value?.trim() || '+2.4%';
        const spreadStr = document.getElementById('wizOcstatSpread')?.value?.trim() || '-3.2%';
        const marketTrendVal = document.getElementById('wizMarketTrend')?.value?.trim() || '';

        const baseM2Val = parseFloat(document.getElementById('sliderBasePriceM2')?.value) || 15000;
        let gardenValNum = parseFloat(document.getElementById('sliderGardenValue')?.value) || 0;
        if (surfGarden === 0) gardenValNum = 0;
        const parkingValNum = parseFloat(document.getElementById('sliderParkingValue')?.value) || 0;
        const weightedNum = parseFloat(weightedSurf) || parseFloat(surfPPE) || 85;
        const batiValNum = Math.round(weightedNum * baseM2Val);
        const totalValNum = batiValNum + gardenValNum + parkingValNum;

        const targetPriceVal = document.getElementById('wizTargetPrice')?.value?.trim() || String(totalValNum);
        const rangeMinVal = document.getElementById('wizRangeMin')?.value?.trim() || '';
        const rangeMaxVal = document.getElementById('wizRangeMax')?.value?.trim() || '';
        const negHypoVal = document.getElementById('wizNegHypo')?.value?.trim() || '';
        const stratPosVal = document.getElementById('wizStratPos')?.value?.trim() || '';
        const lippVal = document.getElementById('wizLippText')?.value?.trim() || '';
        const mandateVal = document.getElementById('wizMandateText')?.value?.trim() || '';
        const validityVal = document.getElementById('wizValidity')?.value?.trim() || '';
        const nextStepVal = document.getElementById('wizNextStep')?.value?.trim() || '';
        const conclusionVal = document.getElementById('wizConclusionText')?.value?.trim() || '';

        // Filename dynamically calibrated
        const cleanCommune = communeVal.split(' ').pop() || 'Genève';
        const cleanAddr = addressVal ? addressVal.replace(/[^a-zA-Z0-9]/g, '_') : 'Nouvelle_Estimation';
        const filename = 'Estimation_DV_' + cleanAddr + '.pptx';

        // Build 15-Slide Replacement Dictionary STRICTLY from the user form!
        const slideReplacements = {
          slide1: {
            "[TYPE DE BIEN]": propTypeVal,
            "[Nom du propriétaire]": ownerVal || '[Nom du propriétaire]',
            "[Commune], le [date]": cleanCommune + ', le ' + new Date().toLocaleDateString('fr-CH'),
            "[ADRESSE DU BIEN]": addressVal || '[ADRESSE DU BIEN]'
          },
          slide2: {
            "[ADRESSE COMPLÈTE]": addressVal || '[ADRESSE COMPLÈTE]',
            "[Nom de la résidence / bâtiment]  ·  [Commune]": (residenceVal ? (residenceVal + ' · ') : '') + (communeVal || cleanCommune),
            "[00] PIÈCES": roomsVal ? (roomsVal.split(' ')[0] || roomsVal) : '[00]',
            "[00 m²] SURFACE PPE": surfPPE ? (surfPPE + ' m²') : '[00 m²]',
            "[00 m²] SURFACE PONDÉRÉE": weightedSurf ? (weightedSurf + ' m²') : '[00 m²]',
            "[AAAA] CONSTRUCTION": yearVal ? yearVal.substring(0, 4) : '[AAAA]',
            "Parcelle [n°]": parcelVal ? ('Parcelle ' + parcelVal) : 'Parcelle [n°]',
            "Bâtiment [n°]": buildingVal || 'Bâtiment [n°]',
            "Lot PPE [n°]": lotVal ? ('Lot ' + lotVal) : 'Lot PPE [n°]',
            "Quote-part [‰]": quotePartVal || 'Quote-part [‰]',
            "Étage [étage]": floorVal || 'Étage [étage]',
            "Zone [zone]": zoneVal || 'Zone [zone]',
            "[Parking]": parkingVal || '[Parking]',
            "[Cave]": cellarVal || '[Cave]',
            "[Chauffage]": heatingVal || '[Chauffage]'
          },
          slide3: {
            "[PARCELLE N°0000]": parcelVal ? ('PARCELLE N° ' + parcelVal + ' (' + cleanCommune.toUpperCase() + ')') : '[PARCELLE N°0000]',
            "[Micro-localisation en une phrase]": microLocationVal || '[Micro-localisation en une phrase]'
          },
          slide4: {
            "[Distribution & circulation]": qualDistVal || '[Distribution & circulation]',
            "[Matériaux & équipements]": qualEquipVal || '[Matériaux & équipements]',
            "[État & entretien]": qualStateVal || '[État & entretien]',
            "[Environnement & nuisances]": qualEnvVal || '[Environnement & nuisances]'
          },
          slide5: {},
          slide6: {},
          slide7: {},
          slide8: {},
          slide9: {
            "MÉTHODE DE NORMALISATION": normMethodVal || 'Normalisation D&V basée sur les transactions authentiques récentes du secteur.'
          },
          slide10: {
            "[Évolution récente documentée]": trendStr + ' sur 18 mois (source OCSTAT / FAO Genève)',
            "[Position de la commune]": marketTrendVal || ('Marché communal sur ' + cleanCommune),
            "[Écart entre prix affichés et transactions]": 'Écart moyen de négociation constaté : ' + spreadStr,
            "CHF [00’000]": 'CHF ' + ppeMedianStr,
            "[00’000]": cantonMedianStr,
            "[Périmètre et date]": 'Genève & ' + cleanCommune + ' · Arrêté au ' + new Date().toLocaleDateString('fr-CH')
          },
          slide11: {
            "[00 m²] × 100%": (surfPPE || '85') + ' m² × 100%',
            "[00,0 m²]": (weightedSurf || surfPPE || '85') + ' m²',
            "[Prix de base / m²]": 'CHF ' + baseM2Val.toLocaleString('fr-CH') + ' / m²',
            "[valeur]": [
              'CHF ' + baseM2Val.toLocaleString('fr-CH') + ' / m² (Base pondérée calibrée)',
              "0.0% (État technique et finitions)",
              '+CHF ' + gardenValNum.toLocaleString('fr-CH') + (surfGarden > 0 ? (' (' + surfGarden + ' m²)') : ' (0 m²)'),
              '+CHF ' + parkingValNum.toLocaleString('fr-CH') + ' (Stationnement privatif)'
            ]
          },
          slide12: {
            "CHF [0’000’000]": [
              'CHF ' + batiValNum.toLocaleString('fr-CH'),
              'CHF ' + (targetPriceVal ? Number(targetPriceVal).toLocaleString('fr-CH') : totalValNum.toLocaleString('fr-CH'))
            ],
            "CHF [±00’000]": [
              'CHF 0',
              '+CHF ' + gardenValNum.toLocaleString('fr-CH'),
              '+CHF ' + parkingValNum.toLocaleString('fr-CH')
            ]
          },
          slide13: {},
          slide14: {},
          slide15: {}
        };

        // Exterior spaces on Slide 2
        let extUsage = [];
        if (surfGarden > 0) extUsage.push('Jardin privatif ~' + surfGarden + ' m²');
        if (surfTerrace > 0) extUsage.push('Terrasse ' + surfTerrace + ' m²');
        if (surfLoggia > 0) extUsage.push('Loggia ' + surfLoggia + ' m²');
        if (extUsage.length > 0) {
          slideReplacements.slide2["[Jardin / droit d’usage]"] = extUsage.join(' + ');
        }

        if (chargesVal || renovVal) {
          slideReplacements.slide2["[Charges / fonds]"] = (chargesVal || '') + (chargesVal && renovVal ? ' · ' : '') + (renovVal || '');
        }

        // Slide 9 Comparables Table
        if (Array.isArray(WIZARD_COMPARABLES) && WIZARD_COMPARABLES.length > 0) {
          slideReplacements.slide9["[JJ.MM.AA]"] = WIZARD_COMPARABLES.map(c => c.date || '—');
          slideReplacements.slide9["[Adresse / promotion]"] = WIZARD_COMPARABLES.map(c => c.address || '—');
          slideReplacements.slide9["[PPE]"] = WIZARD_COMPARABLES.map(c => c.commune ? ('PPE ' + c.commune) : 'PPE');
          slideReplacements.slide9["[00 m²]"] = WIZARD_COMPARABLES.map(c => (c.surface ? (c.surface + ' m²') : '—'));
          slideReplacements.slide9["[Jardin / balcon]"] = WIZARD_COMPARABLES.map(c => c.ext || 'Balcon / Extérieur');
          slideReplacements.slide9["CHF [0’000’000]"] = WIZARD_COMPARABLES.map(c => ('CHF ' + Number(c.price || 0).toLocaleString('fr-CH')));
          slideReplacements.slide9["[00’000]"] = WIZARD_COMPARABLES.map(c => (c.price_m2 ? Number(c.price_m2).toLocaleString('fr-CH') : '—'));
          slideReplacements.slide9["[FAO / D&V]"] = WIZARD_COMPARABLES.map(c => c.source || 'Base FAO / RF');
        }

        // Slide 11 sub-surfaces
        if (surfLoggia > 0 || surfTerrace > 0) {
          slideReplacements.slide11["[00 m²] × [00%]"] = [
            surfLoggia > 0 ? (surfLoggia + ' m² × 50%') : '',
            surfTerrace > 0 ? (surfTerrace + ' m² × 33%') : ''
          ].filter(Boolean);
        }

        // Slide 12 ranges
        if (rangeMinVal && rangeMinVal !== '0') slideReplacements.slide12["CHF [MIN]"] = 'CHF ' + Number(rangeMinVal).toLocaleString('fr-CH');
        if (rangeMaxVal && rangeMaxVal !== '0') slideReplacements.slide12["CHF [MAX]"] = 'CHF ' + Number(rangeMaxVal).toLocaleString('fr-CH');

        // Slides 13, 14, 15
        if (lippVal) slideReplacements.slide13["[Conseil professionnel requis]"] = lippVal;
        if (mandateVal) slideReplacements.slide14["[Pourquoi cette formule correspond au projet]"] = mandateVal;
        if (conclusionVal) slideReplacements.slide15["[Phrase de conclusion courte et personnalisée]"] = conclusionVal;
        if (nextStepVal) slideReplacements.slide15["[PROCHAINE ÉTAPE]"] = nextStepVal;

        let downloaded = false;
        try {
          const res = await fetch('/api/dv/export-pptx'`;

if (oldExportFunctionRegex.test(html)) {
  html = html.replace(oldExportFunctionRegex, newExportFunctionJs);
  console.log('✓ exportPresentationPptx completely rewritten as SSOT');
} else {
  console.warn('Regex for exportPresentationPptx did not match');
}

// 7. Remove any remnant of the old if (isVierge) / else block inside exportPresentationPptx
// Let's check if there is any trailing Saut du Loup block
const oldElseSautDuLoupRegex = /\/\/ SAUT-DU-LOUP Reference Case Study Replacements[\s\S]*?slide15: \{[\s\S]*?\}\s*\}\s*;/;
if (oldElseSautDuLoupRegex.test(html)) {
  html = html.replace(oldElseSautDuLoupRegex, '');
  console.log('✓ Old else Saut du Loup static block purged from export');
}

writeFileSync(htmlPath, html, 'utf8');
console.log('public/dv/index.html successfully updated and saved!');
