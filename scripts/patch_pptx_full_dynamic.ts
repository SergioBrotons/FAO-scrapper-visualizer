import { readFileSync, writeFileSync } from 'fs';
import { join } from 'path';

const htmlPath = join(process.cwd(), 'public', 'dv', 'index.html');
let html = readFileSync(htmlPath, 'utf8');

console.log('Applying comprehensive PPTX dynamic filling & UI enhancements to public/dv/index.html...');

// ==========================================
// 1. ADD CADASTRE UPLOAD DROPZONE IN STEP 3
// ==========================================
const oldUploadGridTarget = `<div class="upload-slide-card">
                <div class="upload-slide-title">Slide 01 &bull; Couverture Principale</div>`;

const newUploadCadastreCard = `<!-- Slide 3 Cadastre Plan -->
              <div class="upload-slide-card" style="border: 2px dashed var(--dv-teal); background: rgba(0, 147, 157, 0.03);">
                <div class="upload-slide-title" style="display:flex; justify-content:space-between; align-items:center;">
                  <span>Slide 03 &bull; Plan Cadastral SITG</span>
                  <a id="linkSitgCapture" href="https://map.sitg.ge.ch/?scale=2500&mapresources=CADASTRE" target="_blank" rel="noopener" style="font-size:10px; color:var(--dv-teal); font-weight:700; text-decoration:none;" title="Ouvrir le SITG pour capturer l'extrait">SITG &rarr;</a>
                </div>
                <div class="upload-dropzone" onclick="document.getElementById('fileCadastre').click()">
                  <input type="file" id="fileCadastre" accept="image/*" style="display:none;" onchange="handleImageUpload('cadastre', this)">
                  <div id="previewCadastre" class="dropzone-placeholder">
                    <svg class="mini-icon" width="22" height="22" viewBox="0 0 24 24"><polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/><line x1="9" y1="3" x2="9" y2="18"/><line x1="15" y1="6" x2="15" y2="21"/></svg>
                    <span>Extrait Cadastral & Situation</span>
                  </div>
                </div>
              </div>

              <div class="upload-slide-card">
                <div class="upload-slide-title">Slide 01 &bull; Couverture Principale</div>`;

if (!html.includes('fileCadastre') && html.includes(oldUploadGridTarget)) {
  html = html.replace(oldUploadGridTarget, newUploadCadastreCard);
  console.log('✓ Slide 03 Cadastre Upload Card added to Step 3');
} else {
  console.log('• Slide 03 Cadastre Upload Card already present or target not found');
}

// ==========================================
// 2. ENHANCE STEP 5 OCSTAT & GARDEN HTML
// ==========================================
// A. Replace static garden slider with dynamic responsive garden slider
const oldGardenSliderRegex = /<div class="form-field">\s*<label style="display:flex; justify-content:space-between;">\s*<span>Valorisation Jardin Privatif[^<]*<\/span>[\s\S]*?id="sliderGardenValue"[\s\S]*?<\/div>/;

const newGardenSliderHtml = `<div class="form-field">
                <label style="display:flex; justify-content:space-between; align-items:center;">
                  <span id="lblGardenTitle">Valorisation Jardin Privatif</span>
                  <strong id="labelGardenValue" style="color:var(--dv-teal); font-size:14px;">+CHF 0</strong>
                </label>
                <input type="range" min="0" max="400000" step="5000" id="sliderGardenValue" value="0" oninput="updateValuationFormula()">
                <span id="subGardenValue" style="font-size:11px; color:var(--dv-text-muted);">Calibré dynamiquement selon la surface privative de pleine terre</span>
              </div>`;

if (oldGardenSliderRegex.test(html)) {
  html = html.replace(oldGardenSliderRegex, newGardenSliderHtml);
  console.log('✓ Dynamic garden slider HTML updated in Step 5');
}

// B. Enhance Card 1 in Step 5 for OCSTAT official metrics
const oldOcstatCardRegex = /<!-- Card 1: OCSTAT Slide 10 -->[\s\S]*?<!-- Card 2: Interactive Sliders Slide 11 -->/;

const newOcstatCardHtml = `<!-- Card 1: OCSTAT Slide 10 -->
          <div class="wizard-card">
            <div class="wizard-card-header">
              <span>1. Baromètre Statistique Cantonal OCSTAT Genève (Slide 10)</span>
              <span class="pulse-validated-badge" style="background:var(--dv-sand);" id="badgeOcstatStatus">Indices Officiels Synchronisés</span>
            </div>
            <div class="wizard-card-sub">Données officielles OCSTAT & FAO arrêtées pour la commune sélectionnée. Remplies automatiquement, modifiables par le courtier.</div>

            <div class="form-grid-4" style="margin-bottom:12px;">
              <div class="form-field">
                <label>Prix Médian Commune (PPE / m²)</label>
                <div class="unit-input-wrap">
                  <input type="text" id="wizOcstatPpeMedian" value="16'000" oninput="updateOcstatNote()">
                  <span class="unit-tag">CHF/m²</span>
                </div>
              </div>
              <div class="form-field">
                <label>Prix Médian Canton (Genève / m²)</label>
                <div class="unit-input-wrap">
                  <input type="text" id="wizOcstatCantonMedian" value="14'200" oninput="updateOcstatNote()">
                  <span class="unit-tag">CHF/m²</span>
                </div>
              </div>
              <div class="form-field">
                <label>Tendance Marché (18 mois)</label>
                <input type="text" id="wizOcstatTrend" value="+2.4%" oninput="updateOcstatNote()">
              </div>
              <div class="form-field">
                <label>Marge de Négociation Moyenne</label>
                <input type="text" id="wizOcstatSpread" value="-3.2%" oninput="updateOcstatNote()">
              </div>
            </div>

            <div class="form-field">
              <label style="display:flex; justify-content:space-between;">
                <span>Synthèse Professionnelle & Analyse Marché du Courtier (Slide 10)</span>
                <button type="button" class="btn-action-secondary" style="font-size:10.5px; padding:2px 8px;" onclick="regenerateOcstatNote()">Générer Note Type</button>
              </label>
              <textarea id="wizMarketTrend" rows="3">+4.2% sur les appartements PPE récents en Rive Gauche sur les 18 derniers mois (OCSTAT Genève). Chêne-Bourg bénéficie d'une forte valorisation soutenue par l'attractivité du Léman Express.</textarea>
              <div class="char-meta">
                <span class="char-hint">Recommandation : 2 à 3 phrases claires pour le mandant</span>
                <span class="char-counter" id="cntMarketTrend">0 / 220 car. max (Slide 10)</span>
              </div>
            </div>
          </div>

          <!-- Card 2: Interactive Sliders Slide 11 -->`;

if (oldOcstatCardRegex.test(html)) {
  html = html.replace(oldOcstatCardRegex, newOcstatCardHtml);
  console.log('✓ OCSTAT Card 1 updated with automatic metrics in Step 5');
}

// ==========================================
// 3. JAVASCRIPT FUNCTIONS UPDATES
// ==========================================

// Let's replace the recalculateSurfaces, updateValuationFormula, handleImageUpload, and selectCadastreProperty logic
const oldRecalcSurfacesRegex = /function recalculateSurfaces\(\)[\s\S]*?function updateValuationFormula\(\)[\s\S]*?function syncRanges\(\)[\s\S]*?function handleImageUpload\(slot, input\)[\s\S]*?function renderWizardComps\(\)/;

const newSurfacesAndFormulaJs = `function recalculateSurfaces() {
      const ppe = parseFloat(document.getElementById('wizSurfPPE')?.value) || 0;
      const loggia = parseFloat(document.getElementById('wizSurfLoggia')?.value) || 0;
      const terrace = parseFloat(document.getElementById('wizSurfTerrace')?.value) || 0;
      const garden = parseFloat(document.getElementById('wizSurfGarden')?.value) || 0;

      // Standard Swiss PPE Pondération: 100% PPE + 50% Loggia + 33% Terrasse
      const weighted = ppe + (loggia * 0.5) + (terrace * 0.33);
      const roundedWeighted = Math.round(weighted * 10) / 10;

      const weightedField = document.getElementById('wizWeightedSurf');
      if (weightedField) {
        weightedField.value = roundedWeighted.toFixed(1);
      }

      // Dynamic Garden Slider calibration
      const gardenSlider = document.getElementById('sliderGardenValue');
      const lblTitle = document.getElementById('lblGardenTitle');
      const subGarden = document.getElementById('subGardenValue');

      if (gardenSlider) {
        if (garden === 0) {
          gardenSlider.value = 0;
          gardenSlider.disabled = true;
          if (lblTitle) lblTitle.textContent = "Valorisation Jardin Privatif (0 m²)";
          if (subGarden) subGarden.textContent = "0 m² · Aucun jardin privatif rattaché au lot (CHF 0)";
        } else {
          gardenSlider.disabled = false;
          gardenSlider.max = Math.max(300000, Math.round(garden * 2000));
          if (lblTitle) lblTitle.textContent = "Valorisation Jardin Privatif (" + garden + " m²)";
          if (gardenSlider.value === "0" || gardenSlider.value === "") {
            gardenSlider.value = Math.round(garden * 1000);
          }
          if (subGarden) subGarden.textContent = "Base calculée sur " + garden + " m² de jouissance exclusive de pleine terre";
        }
      }

      updateValuationFormula();
    }

    // Valuation Formula & Interactive Sliders (Step 5)
    function updateValuationFormula() {
      const baseM2 = parseFloat(document.getElementById('sliderBasePriceM2')?.value) || 16000;
      const gardenSurf = parseFloat(document.getElementById('wizSurfGarden')?.value) || 0;
      let gardenVal = parseFloat(document.getElementById('sliderGardenValue')?.value) || 0;
      if (gardenSurf === 0) gardenVal = 0;

      const parkingVal = parseFloat(document.getElementById('sliderParkingValue')?.value) || 0;
      const weightedSurf = parseFloat(document.getElementById('wizWeightedSurf')?.value) || 85;

      const batiVal = Math.round(weightedSurf * baseM2);
      const totalVal = batiVal + gardenVal + parkingVal;

      // Recommended commercial range: -1.7% / +1.0% (calibrated on psychology)
      const rangeMin = Math.round((totalVal * 0.983) / 10000) * 10000;
      const rangeMax = Math.round((totalVal * 1.01) / 10000) * 10000;

      // Update Slider Label Displays
      const lblBase = document.getElementById('labelBasePriceM2');
      if (lblBase) lblBase.textContent = 'CHF ' + baseM2.toLocaleString('fr-CH') + ' / m²';

      const lblGarden = document.getElementById('labelGardenValue');
      if (lblGarden) {
        if (gardenSurf > 0 && gardenVal > 0) {
          const ratePerM2 = Math.round(gardenVal / gardenSurf);
          lblGarden.textContent = '+CHF ' + gardenVal.toLocaleString('fr-CH') + ' (~' + ratePerM2 + ' CHF/m²)';
        } else {
          lblGarden.textContent = '+CHF 0';
        }
      }

      const lblParking = document.getElementById('labelParkingValue');
      if (lblParking) lblParking.textContent = '+CHF ' + parkingVal.toLocaleString('fr-CH');

      // Update Live Result Cards
      const livePrice = document.getElementById('wizLiveValDisplay');
      if (livePrice) livePrice.textContent = 'CHF ' + totalVal.toLocaleString('fr-CH');

      const liveRange = document.getElementById('wizLiveRangeDisplay');
      if (liveRange) {
        liveRange.textContent = 'Fourchette de commercialisation recommandée : CHF ' +
          rangeMin.toLocaleString('fr-CH') + ' – CHF ' + rangeMax.toLocaleString('fr-CH');
      }

      // Breakdown Pills
      const pillBuilt = document.getElementById('pillBuiltVal');
      if (pillBuilt) pillBuilt.textContent = 'CHF ' + batiVal.toLocaleString('fr-CH');

      const pillGarden = document.getElementById('pillGardenVal');
      if (pillGarden) pillGarden.textContent = '+CHF ' + gardenVal.toLocaleString('fr-CH');

      const pillParking = document.getElementById('pillParkingVal');
      if (pillParking) pillParking.textContent = '+CHF ' + parkingVal.toLocaleString('fr-CH');

      // Step 6 Inputs Sync
      const inTarget = document.getElementById('wizTargetPrice');
      if (inTarget) inTarget.value = totalVal;

      const inMin = document.getElementById('wizRangeMin');
      if (inMin) inMin.value = rangeMin;

      const inMax = document.getElementById('wizRangeMax');
      if (inMax) inMax.value = rangeMax;
    }

    // Manual Sync when editing Step 6 Range inputs directly
    function syncRanges() {
      const target = parseFloat(document.getElementById('wizTargetPrice')?.value) || 0;
      const min = parseFloat(document.getElementById('wizRangeMin')?.value) || 0;
      const max = parseFloat(document.getElementById('wizRangeMax')?.value) || 0;

      const livePrice = document.getElementById('wizLiveValDisplay');
      if (livePrice && target > 0) livePrice.textContent = 'CHF ' + target.toLocaleString('fr-CH');

      const liveRange = document.getElementById('wizLiveRangeDisplay');
      if (liveRange && min > 0 && max > 0) {
        liveRange.textContent = 'Fourchette de commercialisation recommandée : CHF ' +
          min.toLocaleString('fr-CH') + ' – CHF ' + max.toLocaleString('fr-CH');
      }
    }

    // Image Upload Handler (Slide 1, 3, 4, 5, 6, 7)
    function handleImageUpload(slot, input) {
      if (!input || !input.files || !input.files[0]) return;
      const file = input.files[0];
      const reader = new FileReader();

      reader.onload = function(e) {
        const base64Data = e.target.result;
        UPLOADED_SLIDE_IMAGES[slot] = base64Data;

        // Capitalize slot name for preview ID
        const capSlot = slot.charAt(0).toUpperCase() + slot.slice(1);
        const previewEl = document.getElementById('preview' + capSlot);
        if (previewEl) {
          previewEl.innerHTML = '<img src="' + base64Data + '" style="width:100%; height:100%; object-fit:cover; border-radius:6px;" alt="' + slot + '">';
        }
        showToast("Photo " + slot + " chargée et calibrée pour la présentation PowerPoint !");
      };

      reader.readAsDataURL(file);
    }

    // OCSTAT Dynamic Helper
    function updateOcstatNote() {
      const comm = (document.getElementById('wizCommune')?.value || 'Genève').replace(/^\\d+\\s*/, '').trim();
      const ppeMedian = document.getElementById('wizOcstatPpeMedian')?.value || "15'000";
      const cantonMedian = document.getElementById('wizOcstatCantonMedian')?.value || "14'200";
      const trend = document.getElementById('wizOcstatTrend')?.value || "+2.4%";
      const spread = document.getElementById('wizOcstatSpread')?.value || "-3.2%";

      const text = "Le baromètre officiel OCSTAT et l'historique des actes notariés FAO sur " + comm +
        " enregistrent une médiane PPE de CHF " + ppeMedian + " / m² (contre CHF " + cantonMedian + " à l'échelle cantonale). " +
        "La dynamique à 18 mois s'établit à " + trend + " avec un écart de négociation moyen contenu à " + spread + ".";

      const txtEl = document.getElementById('wizMarketTrend');
      if (txtEl && (!txtEl.value || txtEl.value.includes("baromètre officiel OCSTAT"))) {
        txtEl.value = text;
      }
      initAllCharCounters();
    }

    function regenerateOcstatNote() {
      const comm = (document.getElementById('wizCommune')?.value || 'Genève').replace(/^\\d+\\s*/, '').trim();
      const ppeMedian = document.getElementById('wizOcstatPpeMedian')?.value || "15'000";
      const cantonMedian = document.getElementById('wizOcstatCantonMedian')?.value || "14'200";
      const trend = document.getElementById('wizOcstatTrend')?.value || "+2.4%";
      const spread = document.getElementById('wizOcstatSpread')?.value || "-3.2%";

      const text = "Le baromètre statistique officiel OCSTAT et les actes notariés FAO récents sur la commune de " + comm +
        " démontrent un marché de propriétaires-occupants résilient. Valeur médiane PPE : CHF " + ppeMedian + "/m² (canton : CHF " + cantonMedian + "/m²). " +
        "Tendance 18 mois : " + trend + " avec marge de négociation moyenne de " + spread + ".";

      const txtEl = document.getElementById('wizMarketTrend');
      if (txtEl) txtEl.value = text;
      initAllCharCounters();
      showToast("Note OCSTAT mise à jour avec les indices de " + comm);
    }

    function renderWizardComps()`;

if (oldRecalcSurfacesRegex.test(html)) {
  html = html.replace(oldRecalcSurfacesRegex, newSurfacesAndFormulaJs);
  console.log('✓ Surfaces, garden slider logic, and OCSTAT helpers updated');
} else {
  console.warn('Regex for surfaces and formula JS did not match');
}

// ==========================================
// 4. FETCH OCSTAT IN selectCadastreProperty
// ==========================================
const oldSelectCadastreRegex = /autoFillComparablesForCommune\(prop\.commune, prop\.id\);[\s\S]*?recalculateSurfaces\(\);/;

const newSelectCadastreAddition = `autoFillComparablesForCommune(prop.commune, prop.id);

      // Auto-fetch OCSTAT cantonal benchmarks for this commune
      autoFillOcstatForCommune(prop.commune);

      // Update SITG capture link
      const sitgLink = document.getElementById('linkSitgCapture');
      if (sitgLink && prop.parcel_number) {
        sitgLink.href = 'https://map.sitg.ge.ch/?scale=2500&mapresources=CADASTRE&search=' + encodeURIComponent(prop.address || prop.parcel_number);
      }

      recalculateSurfaces();`;

if (oldSelectCadastreRegex.test(html)) {
  html = html.replace(oldSelectCadastreRegex, newSelectCadastreAddition);
  console.log('✓ selectCadastreProperty updated with OCSTAT benchmark trigger');
}

// Add autoFillOcstatForCommune function right before resetBlankStudio()
const newOcstatFetchJs = `
    async function autoFillOcstatForCommune(commune) {
      if (!commune) return;
      const cleanCommune = commune.replace(/^\\d+\\s*/, '').trim();
      try {
        const res = await fetch('/api/dv/ocstat-benchmark?commune=' + encodeURIComponent(cleanCommune));
        if (res.ok) {
          const json = await res.json();
          if (json.status === 'ok') {
            const inPpe = document.getElementById('wizOcstatPpeMedian');
            if (inPpe && json.ppe_median_sqm) inPpe.value = Number(json.ppe_median_sqm).toLocaleString('fr-CH');

            const inCanton = document.getElementById('wizOcstatCantonMedian');
            if (inCanton && json.canton_median_sqm) inCanton.value = Number(json.canton_median_sqm).toLocaleString('fr-CH');

            const inTrend = document.getElementById('wizOcstatTrend');
            if (inTrend && json.trend_18m_pct) inTrend.value = json.trend_18m_pct;

            const inSpread = document.getElementById('wizOcstatSpread');
            if (inSpread && json.spread_discount_pct) inSpread.value = json.spread_discount_pct + '%';

            const inNotes = document.getElementById('wizMarketTrend');
            if (inNotes && json.suggested_notes) inNotes.value = json.suggested_notes;

            initAllCharCounters();
          }
        }
      } catch (e) {
        console.warn('OCSTAT fetch error:', e);
      }
    }
`;

if (!html.includes('autoFillOcstatForCommune(')) {
  html = html.replace('function resetBlankStudio()', newOcstatFetchJs + '\n    function resetBlankStudio()');
  console.log('✓ autoFillOcstatForCommune injected');
}

// In resetBlankStudio(), ensure previewCadastre is also cleared
if (html.includes("{ id: 'previewPlan', label: 'Plan PPE de Masse' }") && !html.includes("previewCadastre")) {
  html = html.replace(
    "{ id: 'previewPlan', label: 'Plan PPE de Masse' }",
    "{ id: 'previewCadastre', label: 'Extrait Cadastral & Situation' },\n        { id: 'previewPlan', label: 'Plan PPE de Masse' }"
  );
  console.log('✓ previewCadastre added to resetBlankStudio');
}

// ==========================================
// 5. EXHAUSTIVE 15-SLIDE MAPPING IN exportPresentationPptx()
// ==========================================
// Replace the `if (isVierge) { ... }` block in `exportPresentationPptx` with a rich 15-slide mapper!
const oldExportViergeRegex = /if \(isVierge\) \{[\s\S]*?\/\/ SAUT-DU-LOUP Reference Case Study Replacements/;

const newExportViergeJs = `if (isVierge) {
          // Dynamic User Studio Replacements covering all 15 Slides
          slideReplacements = {
            slide1: {},
            slide2: {},
            slide3: {},
            slide4: {},
            slide5: {},
            slide6: {},
            slide7: {},
            slide8: {},
            slide9: {},
            slide10: {},
            slide11: {},
            slide12: {},
            slide13: {},
            slide14: {},
            slide15: {}
          };

          const owner = document.getElementById('wizOwner')?.value?.trim();
          if (owner) slideReplacements.slide1["[Nom du propriétaire]"] = owner;

          const propType = document.getElementById('wizPropertyType')?.value?.trim();
          if (propType) slideReplacements.slide1["[TYPE DE BIEN]"] = propType;

          const address = addressVal;
          if (address) {
            slideReplacements.slide1["[ADRESSE DU BIEN]"] = address;
            slideReplacements.slide2["[ADRESSE COMPLÈTE]"] = address;
            filename = 'Estimation_DV_' + address.replace(/[^a-zA-Z0-9]/g, '_') + '.pptx';
          }

          const commune = document.getElementById('wizCommune')?.value?.trim();
          if (commune) {
            const cleanCommune = commune.split(' ').pop();
            slideReplacements.slide1["[Commune], le [date]"] = cleanCommune + ', le ' + new Date().toLocaleDateString('fr-CH');
          }

          const residence = document.getElementById('wizResidence')?.value?.trim();
          if (residence) slideReplacements.slide2["[Nom de la résidence / bâtiment]  ·  [Commune]"] = residence + ' · ' + (commune || '');

          const rooms = document.getElementById('wizRooms')?.value?.trim();
          if (rooms) slideReplacements.slide2["[00] PIÈCES"] = rooms.split(' ')[0] || rooms;

          const surfPPE = document.getElementById('wizSurfPPE')?.value?.trim();
          if (surfPPE && surfPPE !== "0") slideReplacements.slide2["[00 m²] SURFACE PPE"] = surfPPE + ' m²';

          const weightedSurf = document.getElementById('wizWeightedSurf')?.value?.trim();
          if (weightedSurf && weightedSurf !== "0") slideReplacements.slide2["[00 m²] SURFACE PONDÉRÉE"] = weightedSurf + ' m²';

          const buildingYear = document.getElementById('wizBuildingYear')?.value?.trim();
          if (buildingYear) slideReplacements.slide2["[AAAA] CONSTRUCTION"] = buildingYear.substring(0, 4);

          const parcel = document.getElementById('wizParcel')?.value?.trim();
          if (parcel) {
            slideReplacements.slide2["Parcelle [n°]"] = 'Parcelle ' + parcel;
            slideReplacements.slide3["[PARCELLE N°0000]"] = 'PARCELLE N° ' + parcel + ' (' + (commune || 'GENÈVE').toUpperCase() + ')';
          }

          const building = document.getElementById('wizBuilding')?.value?.trim();
          if (building) slideReplacements.slide2["Bâtiment [n°]"] = building;

          const lotPPE = document.getElementById('wizLotPPE')?.value?.trim();
          if (lotPPE) slideReplacements.slide2["Lot PPE [n°]"] = 'Lot ' + lotPPE;

          const quotePart = document.getElementById('wizQuotePart')?.value?.trim();
          if (quotePart) slideReplacements.slide2["Quote-part [‰]"] = quotePart;

          const zone = document.getElementById('wizZone')?.value?.trim();
          if (zone) slideReplacements.slide2["Zone [zone]"] = zone;

          const parking = document.getElementById('wizParking')?.value?.trim();
          if (parking) slideReplacements.slide2["[Parking]"] = parking;

          const cellar = document.getElementById('wizCellar')?.value?.trim();
          if (cellar) slideReplacements.slide2["[Cave]"] = cellar;

          const surfGarden = parseFloat(document.getElementById('wizSurfGarden')?.value) || 0;
          const surfTerrace = parseFloat(document.getElementById('wizSurfTerrace')?.value) || 0;
          const surfLoggia = parseFloat(document.getElementById('wizSurfLoggia')?.value) || 0;
          let extUsage = [];
          if (surfGarden > 0) extUsage.push("Jardin privatif ~" + surfGarden + " m²");
          if (surfTerrace > 0) extUsage.push("Terrasse " + surfTerrace + " m²");
          if (surfLoggia > 0) extUsage.push("Loggia " + surfLoggia + " m²");
          if (extUsage.length > 0) {
            slideReplacements.slide2["[Jardin / droit d’usage]"] = extUsage.join(" + ");
          }

          const heating = document.getElementById('wizHeating')?.value?.trim();
          if (heating) slideReplacements.slide2["[Chauffage]"] = heating;

          const charges = document.getElementById('wizChargesAnnual')?.value?.trim();
          const renov = document.getElementById('wizRenovFund')?.value?.trim();
          if (charges || renov) {
            slideReplacements.slide2["[Charges / fonds]"] = (charges || '') + (charges && renov ? ' · ' : '') + (renov || '');
          }

          // Slide 3 Micro-localisation
          const microLocation = document.getElementById('wizMicroLocation')?.value?.trim();
          if (microLocation) slideReplacements.slide3["[Micro-localisation en une phrase]"] = microLocation;

          // Slide 4 Quadrants
          const qualDist = document.getElementById('wizQualDist')?.value?.trim();
          if (qualDist) slideReplacements.slide4["[Distribution & circulation]"] = qualDist;

          const qualEquip = document.getElementById('wizQualEquip')?.value?.trim();
          if (qualEquip) slideReplacements.slide4["[Matériaux & équipements]"] = qualEquip;

          const qualState = document.getElementById('wizQualState')?.value?.trim();
          if (qualState) slideReplacements.slide4["[État & entretien]"] = qualState;

          const qualEnv = document.getElementById('wizQualEnv')?.value?.trim();
          if (qualEnv) slideReplacements.slide4["[Environnement & nuisances]"] = qualEnv;

          // Slide 9 Comparables Table & Method
          const normMethod = document.getElementById('wizNormMethod')?.value?.trim();
          if (normMethod) slideReplacements.slide9["MÉTHODE DE NORMALISATION"] = normMethod;

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

          // Slide 10 OCSTAT Barometer
          const ppeMedianStr = document.getElementById('wizOcstatPpeMedian')?.value?.trim() || "15'500";
          const cantonMedianStr = document.getElementById('wizOcstatCantonMedian')?.value?.trim() || "14'200";
          const trendStr = document.getElementById('wizOcstatTrend')?.value?.trim() || "+2.4%";
          const spreadStr = document.getElementById('wizOcstatSpread')?.value?.trim() || "-3.2%";
          const marketTrend = document.getElementById('wizMarketTrend')?.value?.trim();

          slideReplacements.slide10["[Évolution récente documentée]"] = trendStr + " sur 18 mois (source OCSTAT / FAO Genève)";
          slideReplacements.slide10["[Position de la commune]"] = marketTrend || ("Marché communal dynamique sur " + (commune || 'Genève'));
          slideReplacements.slide10["[Écart entre prix affichés et transactions]"] = "Écart moyen de négociation constaté : " + spreadStr;
          slideReplacements.slide10["CHF [00’000]"] = "CHF " + ppeMedianStr;
          slideReplacements.slide10["[00’000]"] = cantonMedianStr;
          slideReplacements.slide10["[Périmètre et date]"] = "Genève & " + (commune || 'Commune') + " · Données arrêtées au " + new Date().toLocaleDateString('fr-CH');

          // Slide 11 Analytical Breakdown Formula
          const baseM2Val = parseFloat(document.getElementById('sliderBasePriceM2')?.value) || 15000;
          let gardenValNum = parseFloat(document.getElementById('sliderGardenValue')?.value) || 0;
          if (surfGarden === 0) gardenValNum = 0;
          const parkingValNum = parseFloat(document.getElementById('sliderParkingValue')?.value) || 0;
          const weightedNum = parseFloat(weightedSurf) || 85;
          const batiValNum = Math.round(weightedNum * baseM2Val);
          const totalValNum = batiValNum + gardenValNum + parkingValNum;

          slideReplacements.slide11["[00 m²] × 100%"] = (surfPPE || '85') + " m² × 100%";
          if (surfLoggia > 0 || surfTerrace > 0) {
            slideReplacements.slide11["[00 m²] × [00%]"] = [
              surfLoggia > 0 ? (surfLoggia + " m² × 50%") : "",
              surfTerrace > 0 ? (surfTerrace + " m² × 33%") : ""
            ].filter(Boolean);
          }
          slideReplacements.slide11["[00,0 m²]"] = (weightedSurf || '85') + " m²";
          slideReplacements.slide11["[Prix de base / m²]"] = "CHF " + baseM2Val.toLocaleString('fr-CH') + " / m²";
          slideReplacements.slide11["[valeur]"] = [
            "CHF " + baseM2Val.toLocaleString('fr-CH') + " / m² (Base pondérée calibrée)",
            "0.0% (État d'entretien et finitions)",
            "+CHF " + gardenValNum.toLocaleString('fr-CH') + (surfGarden > 0 ? (" (" + surfGarden + " m²)") : " (0 m²)"),
            "+CHF " + parkingValNum.toLocaleString('fr-CH') + " (Stationnement privatif)"
          ];

          // Slide 12 Synthesis & Recommendations
          slideReplacements.slide12["CHF [0’000’000]"] = [
            "CHF " + batiValNum.toLocaleString('fr-CH'),
            "CHF " + totalValNum.toLocaleString('fr-CH')
          ];
          slideReplacements.slide12["CHF [±00’000]"] = [
            "CHF 0",
            "+CHF " + gardenValNum.toLocaleString('fr-CH'),
            "+CHF " + parkingValNum.toLocaleString('fr-CH')
          ];

          const targetPrice = document.getElementById('wizTargetPrice')?.value?.trim();
          const rangeMin = document.getElementById('wizRangeMin')?.value?.trim();
          const rangeMax = document.getElementById('wizRangeMax')?.value?.trim();

          if (rangeMin && rangeMin !== "0") slideReplacements.slide12["CHF [MIN]"] = 'CHF ' + Number(rangeMin).toLocaleString('fr-CH');
          if (rangeMax && rangeMax !== "0") slideReplacements.slide12["CHF [MAX]"] = 'CHF ' + Number(rangeMax).toLocaleString('fr-CH');

          // Slide 13 Fiscalité LIPP
          const lippText = document.getElementById('wizLippText')?.value?.trim();
          if (lippText) slideReplacements.slide13["[Conseil professionnel requis]"] = lippText;

          // Slide 14 Mandat
          const mandateText = document.getElementById('wizMandateText')?.value?.trim();
          if (mandateText) slideReplacements.slide14["[Pourquoi cette formule correspond au projet]"] = mandateText;

          // Slide 15 Conclusion & Contact
          const conclusionText = document.getElementById('wizConclusionText')?.value?.trim();
          if (conclusionText) slideReplacements.slide15["[Phrase de conclusion courte et personnalisée]"] = conclusionText;

          const nextStep = document.getElementById('wizNextStep')?.value?.trim();
          if (nextStep) slideReplacements.slide15["[PROCHAINE ÉTAPE]"] = nextStep;
        } else {
          // SAUT-DU-LOUP Reference Case Study Replacements`;

if (oldExportViergeRegex.test(html)) {
  html = html.replace(oldExportViergeRegex, newExportViergeJs);
  console.log('✓ Exhaustive 15-Slide export mapping updated');
} else {
  console.warn('Regex for exportPresentationPptx vierge block did not match');
}

writeFileSync(htmlPath, html, 'utf8');
console.log('Successfully wrote and saved updated public/dv/index.html');
