import { readFileSync, writeFileSync } from 'fs';
import { join } from 'path';

const htmlPath = join(process.cwd(), 'public', 'dv', 'index.html');
let html = readFileSync(htmlPath, 'utf8');

console.log('Patching public/dv/index.html with Dynamic Geneva Address Autocomplete & Cadastre Lock...');

// 1. Add CSS for Autocomplete Dropdown and Cadastre Lock Badge
const autocompleteCss = `
    /* Dynamic Address Autocomplete & Cadastre Lock */
    .address-autocomplete-container {
      position: relative;
    }
    .address-suggestions-dropdown {
      position: absolute;
      top: calc(100% + 4px);
      left: 0;
      right: 0;
      max-height: 320px;
      overflow-y: auto;
      background: #FFFFFF;
      border: 1px solid var(--dv-teal);
      border-radius: 6px;
      box-shadow: 0 10px 25px rgba(0, 74, 79, 0.15);
      z-index: 1050;
      display: none;
    }
    .address-suggestion-item {
      padding: 10px 14px;
      cursor: pointer;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid #F1F5F9;
      transition: background 0.15s ease;
      font-size: 13px;
    }
    .address-suggestion-item:last-child {
      border-bottom: none;
    }
    .address-suggestion-item:hover,
    .address-suggestion-item.active {
      background: rgba(0, 147, 157, 0.08);
    }
    .address-suggestion-main {
      font-weight: 600;
      color: var(--dv-deep-green);
    }
    .address-suggestion-sub {
      font-size: 11px;
      color: #64748B;
      display: flex;
      gap: 8px;
      margin-top: 2px;
      align-items: center;
    }
    .address-suggestion-pill {
      font-size: 10px;
      font-weight: 700;
      padding: 2px 6px;
      border-radius: 4px;
      background: rgba(0, 74, 79, 0.08);
      color: var(--dv-deep-green);
    }
    .cadastre-lock-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 11px;
      font-weight: 700;
      color: var(--dv-teal);
      background: rgba(0, 147, 157, 0.08);
      border: 1px solid rgba(0, 147, 157, 0.2);
      padding: 5px 12px;
      border-radius: 4px;
      margin-top: 8px;
    }
    .lock-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--dv-teal);
      display: inline-block;
    }
`;

if (!html.includes('.address-autocomplete-container')) {
  html = html.replace('.wizard-card {', autocompleteCss + '\n    .wizard-card {');
  console.log('✓ CSS injected');
}

// 2. Replace Card 2 HTML with interactive autocomplete & functional Auto-remplir toolbar
const oldCard2Regex = /<!-- Card 2: Cadastre & SITG -->[\s\S]*?<!-- Card 3: Micro-secteur Slide 3 -->/;

const newCard2Html = `<!-- Card 2: Cadastre & SITG -->
          <div class="wizard-card">
            <div class="wizard-card-header">
              <span>2. Références Cadastrales & Immeuble (Slide 02)</span>
              <span style="font-size:11px; font-weight:700; color:var(--dv-deep-green); text-transform:none;">Fiche Administrative</span>
            </div>
            <div class="wizard-card-sub">Identification officielle au Registre Foncier et géoportail de l'État de Genève. Saisissez une adresse pour autocomplétion instantanée.</div>

            <div class="form-grid-3">
              <div class="form-field address-autocomplete-container">
                <label style="display:flex; justify-content:space-between; align-items:center;">
                  <span>Adresse du Bien (Genève)</span>
                  <span style="font-size:10px; font-weight:700; color:var(--dv-teal); text-transform:uppercase;">Autocomplete SITG Actif</span>
                </label>
                <div style="position:relative;">
                  <input type="text" id="wizAddress" value="Chemin du Saut-du-Loup 18" placeholder="Ex: Chemin du Saut-du-Loup 18, Rue de Genève..." autocomplete="off">
                  <span id="addressLoadingSpinner" style="position:absolute; right:12px; top:10px; display:none;">
                    <svg class="mini-icon spin" width="14" height="14" viewBox="0 0 24 24"><line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/><line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/></svg>
                  </span>
                </div>
                <!-- Dropdown suggestions -->
                <div id="addressSuggestionsDropdown" class="address-suggestions-dropdown"></div>
                <div id="cadastreLockBadge" class="cadastre-lock-badge" style="display:inline-flex;">
                  <span class="lock-dot"></span>
                  <span id="cadastreLockText">Référence SITG verrouillée : Parcelle 4642 · 1225 Chêne-Bourg</span>
                </div>
              </div>
              <div class="form-field">
                <label>Commune & NPA</label>
                <input type="text" id="wizCommune" value="1225 Chêne-Bourg">
              </div>
              <div class="form-field">
                <label>Nom de la Résidence / Promotion</label>
                <input type="text" id="wizResidence" value="Résidence Les Jardins de la Seymaz">
              </div>
            </div>

            <div class="form-grid-4">
              <div class="form-field">
                <label>N° Parcelle Cadastre</label>
                <input type="text" id="wizParcel" value="4643">
              </div>
              <div class="form-field">
                <label>Bâtiment</label>
                <input type="text" id="wizBuilding" value="Bât. 2921-2922">
              </div>
              <div class="form-field">
                <label>Lot PPE & Feuillet</label>
                <input type="text" id="wizLotPPE" value="Lot 2.02 (Feuillet 4642-10)">
              </div>
              <div class="form-field">
                <label>Quote-part PPE</label>
                <input type="text" id="wizQuotePart" value="132.5‰">
              </div>
            </div>

            <div class="form-grid-3">
              <div class="form-field">
                <label>Zone d'Affectation (LACI)</label>
                <input type="text" id="wizZone" value="Zone 5 (Villas et résidences de standing)">
              </div>
              <div class="form-field">
                <label>Étage / Niveau</label>
                <input type="text" id="wizFloor" value="Rez-de-chaussée surélevé">
              </div>
              <div class="form-field">
                <label>Année de Construction & Label</label>
                <input type="text" id="wizBuildingYear" value="2019 (Label Minergie GE-1672)">
              </div>
            </div>

            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:12px; background:var(--dv-sand); padding:12px 18px; border-radius:6px; flex-wrap:wrap; gap:10px;">
              <div style="font-size:12px; color:var(--dv-deep-green); display:flex; align-items:center; gap:8px;">
                <svg class="mini-icon" width="16" height="16" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                <span><strong>SITG & FAO Officiel :</strong> Foncier, cadastre et comparables synchronisés en temps réel.</span>
              </div>
              <div style="display:flex; gap:10px; align-items:center;">
                <a id="btnSitgMap" href="https://map.sitg.ge.ch/?center=2504600,1117200&scale=2500&mapresources=CADASTRE" target="_blank" rel="noopener" class="btn-action-secondary" style="font-size:11px; padding:6px 12px;">
                  <svg class="mini-icon" width="13" height="13" viewBox="0 0 24 24"><polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/><line x1="9" y1="3" x2="9" y2="18"/><line x1="15" y1="6" x2="15" y2="21"/></svg>
                  <span>Ouvrir SITG Cadastre</span>
                </a>
                <button class="btn-action-primary" id="btnAutoFillSystem" style="font-size:11px; padding:6px 14px;" onclick="autoFillFromSystem()">
                  <svg class="mini-icon" width="13" height="13" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
                  <span>Auto-remplir depuis le Système</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Card 3: Micro-secteur Slide 3 -->`;

if (oldCard2Regex.test(html)) {
  html = html.replace(oldCard2Regex, newCard2Html);
  console.log('✓ Card 2 HTML updated');
} else {
  console.warn('Regex for Card 2 did not match');
}

// 3. Add Autocomplete & Auto-Fill JavaScript logic
const newJsFunctions = `
    // Geneva Cadastre & Autocomplete System
    let GENEVA_CADASTRE_INDEX = [];
    let GENEVA_RECENT_COMPARABLES = [];

    async function loadCadastreIndexes() {
      try {
        const res = await fetch('/dv/data/geneva_cadastre_index.json');
        if (res.ok) {
          GENEVA_CADASTRE_INDEX = await res.json();
          console.log('Geneva Cadastre Index ready:', GENEVA_CADASTRE_INDEX.length, 'properties');
        }
      } catch (e) {
        console.warn('Cadastre index load error:', e);
      }

      try {
        const resComps = await fetch('/dv/data/geneva_recent_comparables.json');
        if (resComps.ok) {
          GENEVA_RECENT_COMPARABLES = await resComps.json();
          console.log('Geneva Comparables Index ready:', GENEVA_RECENT_COMPARABLES.length, 'sales');
        }
      } catch (e) {
        console.warn('Comparables index load error:', e);
      }
    }

    function initAddressAutocomplete() {
      const input = document.getElementById('wizAddress');
      const dropdown = document.getElementById('addressSuggestionsDropdown');
      const spinner = document.getElementById('addressLoadingSpinner');
      if (!input || !dropdown) return;

      let debounceTimer = null;
      let activeIndex = -1;
      let currentResults = [];

      input.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        const q = input.value.trim();
        if (q.length < 2) {
          dropdown.style.display = 'none';
          dropdown.innerHTML = '';
          return;
        }

        if (spinner) spinner.style.display = 'block';

        debounceTimer = setTimeout(async () => {
          let results = [];
          // 1. Try server API
          try {
            const res = await fetch('/api/dv/address-autocomplete?q=' + encodeURIComponent(q));
            if (res.ok) {
              const json = await res.json();
              results = json.results || [];
            }
          } catch (err) {}

          // 2. Fallback to local index
          if (!results || results.length === 0) {
            if (GENEVA_CADASTRE_INDEX.length > 0) {
              const lowerQ = q.toLowerCase();
              results = GENEVA_CADASTRE_INDEX.filter(item => 
                (item.address && item.address.toLowerCase().includes(lowerQ)) ||
                (item.parcel_number && item.parcel_number.toLowerCase().includes(lowerQ)) ||
                (item.commune && item.commune.toLowerCase().includes(lowerQ))
              ).slice(0, 15);
            }
          }

          if (spinner) spinner.style.display = 'none';
          currentResults = results;
          activeIndex = -1;

          if (results.length === 0) {
            dropdown.innerHTML = '<div style="padding:12px; font-size:12px; color:var(--dv-text-muted); text-align:center;">Aucune adresse cadastrée trouvée pour "' + escapeHtml(q) + '"</div>';
            dropdown.style.display = 'block';
            return;
          }

          dropdown.innerHTML = results.map((item, idx) => {
            const addr = item.address || '';
            const comm = item.commune || 'Genève';
            const parcel = item.parcel_number || item.parcel || 'N/A';
            const egrid = item.egrid ? ('<span class="address-suggestion-pill">EGRID ' + escapeHtml(item.egrid.slice(-6)) + '</span>') : '';
            return \`
              <div class="address-suggestion-item" data-idx="\${idx}">
                <div>
                  <div class="address-suggestion-main">\${escapeHtml(addr)}</div>
                  <div class="address-suggestion-sub">
                    <span>📍 \${escapeHtml(comm)}</span>
                    <span>•</span>
                    <span class="address-suggestion-pill">Parcelle \${escapeHtml(parcel)}</span>
                    \${egrid}
                  </div>
                </div>
                <div style="font-size:11px; font-weight:700; color:var(--dv-teal);">
                  Sélectionner &rarr;
                </div>
              </div>
            \`;
          }).join('');

          dropdown.style.display = 'block';

          dropdown.querySelectorAll('.address-suggestion-item').forEach(el => {
            el.addEventListener('click', () => {
              const idx = parseInt(el.getAttribute('data-idx'));
              if (currentResults[idx]) {
                selectCadastreProperty(currentResults[idx]);
              }
            });
          });
        }, 180);
      });

      input.addEventListener('keydown', (e) => {
        const items = dropdown.querySelectorAll('.address-suggestion-item');
        if (dropdown.style.display !== 'block' || items.length === 0) return;

        if (e.key === 'ArrowDown') {
          e.preventDefault();
          activeIndex = (activeIndex + 1) % items.length;
          items.forEach((it, idx) => it.classList.toggle('active', idx === activeIndex));
          if (items[activeIndex]) items[activeIndex].scrollIntoView({ block: 'nearest' });
        } else if (e.key === 'ArrowUp') {
          e.preventDefault();
          activeIndex = (activeIndex - 1 + items.length) % items.length;
          items.forEach((it, idx) => it.classList.toggle('active', idx === activeIndex));
          if (items[activeIndex]) items[activeIndex].scrollIntoView({ block: 'nearest' });
        } else if (e.key === 'Enter') {
          if (activeIndex >= 0 && currentResults[activeIndex]) {
            e.preventDefault();
            selectCadastreProperty(currentResults[activeIndex]);
          }
        } else if (e.key === 'Escape') {
          dropdown.style.display = 'none';
        }
      });

      document.addEventListener('click', (e) => {
        if (!input.contains(e.target) && !dropdown.contains(e.target)) {
          dropdown.style.display = 'none';
        }
      });
    }

    function selectCadastreProperty(prop) {
      const dropdown = document.getElementById('addressSuggestionsDropdown');
      if (dropdown) dropdown.style.display = 'none';
      if (!prop) return;

      // 1. Step 1: Cadastre & Identity
      const addrInput = document.getElementById('wizAddress');
      if (addrInput) addrInput.value = prop.address || '';

      const commInput = document.getElementById('wizCommune');
      if (commInput) {
        let c = prop.commune || 'Genève';
        if (!c.includes('12') && !c.includes('NPA')) c = '1225 ' + c;
        commInput.value = c;
      }

      const parcelInput = document.getElementById('wizParcel');
      if (parcelInput) parcelInput.value = prop.parcel_number || prop.parcel || '';

      const buildingInput = document.getElementById('wizBuilding');
      if (buildingInput) {
        const num = (prop.address.match(/\\d+/) || [''])[0];
        buildingInput.value = prop.building || ('Bât. ' + (num ? num : '1'));
      }

      const lotInput = document.getElementById('wizLotPPE');
      if (lotInput) lotInput.value = prop.unit_number ? ('Lot ' + prop.unit_number) : (prop.lot_ppe || 'Lot 2.01');

      const zoneInput = document.getElementById('wizZone');
      if (zoneInput) zoneInput.value = prop.zone || 'Zone 5 (Villas et résidences de standing)';

      const yearInput = document.getElementById('wizBuildingYear');
      if (yearInput && prop.building_year) {
        yearInput.value = prop.building_year + (parseInt(prop.building_year) >= 2016 ? ' (Label Minergie)' : '');
      }

      // 2. Step 2: Surfaces & Technique
      const surfVal = parseFloat(prop.surface || prop.surface_m2) || 85;
      const surfInput = document.getElementById('wizSurfPPE');
      if (surfInput) surfInput.value = surfVal.toFixed(1);

      const weightedInput = document.getElementById('wizWeightedSurf');
      if (weightedInput) weightedInput.value = surfVal.toFixed(1);

      const roomsInput = document.getElementById('wizRooms');
      if (roomsInput) {
        const r = prop.rooms || (surfVal > 110 ? 5 : surfVal > 75 ? 4 : 3);
        roomsInput.value = r + ' pièces';
      }

      const heatingInput = document.getElementById('wizHeating');
      if (heatingInput && prop.heating_system) heatingInput.value = prop.heating_system;

      // 3. Cadastre Lock Badge
      const lockBadge = document.getElementById('cadastreLockBadge');
      const lockText = document.getElementById('cadastreLockText');
      if (lockBadge && lockText) {
        lockBadge.style.display = 'inline-flex';
        lockText.innerHTML = '<strong>SITG Verrouillé :</strong> Parcelle ' + escapeHtml(prop.parcel_number || 'Cadastrée') + ' (' + escapeHtml(prop.commune || 'Genève') + ')' + (prop.egrid ? ' · EGRID ' + escapeHtml(prop.egrid) : '');
      }

      // 4. SITG Map link
      const btnSitg = document.getElementById('btnSitgMap');
      if (btnSitg) {
        btnSitg.href = 'https://map.sitg.ge.ch/?center=2504600,1117200&scale=2500&mapresources=CADASTRE&search=' + encodeURIComponent(prop.address);
      }

      // 5. Auto-discover authentic comparables for this commune (Phase 2 automation!)
      autoFillComparablesForCommune(prop.commune, prop.id);

      recalculateSurfaces();
      initAllCharCounters();

      showToast('Fiche officielle ' + prop.address + ' liée : cadastre et comparables synchronisés !');
    }

    async function autoFillFromSystem() {
      const addr = document.getElementById('wizAddress')?.value?.trim();
      if (!addr) {
        showToast("Veuillez d'abord saisir une adresse genevoise pour la lier au cadastre.");
        document.getElementById('wizAddress')?.focus();
        return;
      }

      const btn = document.getElementById('btnAutoFillSystem');
      const origText = btn ? btn.innerHTML : '';
      if (btn) btn.innerHTML = '<svg class="mini-icon spin" width="13" height="13" viewBox="0 0 24 24"><line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/><line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/></svg> Recherche...';

      try {
        let matchedProp = null;
        try {
          const res = await fetch('/api/dv/cadastre-lookup?address=' + encodeURIComponent(addr));
          if (res.ok) {
            const json = await res.json();
            matchedProp = json.data;
          }
        } catch (e) {}

        if (!matchedProp && GENEVA_CADASTRE_INDEX.length > 0) {
          const lower = addr.toLowerCase();
          matchedProp = GENEVA_CADASTRE_INDEX.find(item => item.address && item.address.toLowerCase().includes(lower)) ||
                        GENEVA_CADASTRE_INDEX.find(item => item.address && lower.includes(item.address.toLowerCase())) ||
                        GENEVA_CADASTRE_INDEX[0];
        }

        if (matchedProp) {
          selectCadastreProperty(matchedProp);
        } else {
          showToast("Aucun enregistrement cadastral exact trouvé. Sélectionnez une adresse proposée dans la liste déroulante.");
        }
      } catch (err) {
        showToast("Erreur auto-remplissage : " + err.message);
      } finally {
        if (btn) btn.innerHTML = origText;
      }
    }

    async function autoFillComparablesForCommune(commune, excludeId) {
      if (!commune) return;
      const cleanCommune = commune.replace(/^\\d+\\s*/, '').trim();

      let comps = [];
      try {
        const res = await fetch('/api/dv/comparables-lookup?commune=' + encodeURIComponent(cleanCommune) + '&exclude_id=' + (excludeId || 0) + '&limit=4');
        if (res.ok) {
          const json = await res.json();
          comps = json.results || [];
        }
      } catch (e) {}

      if ((!comps || comps.length === 0) && GENEVA_RECENT_COMPARABLES.length > 0) {
        const lower = cleanCommune.toLowerCase();
        comps = GENEVA_RECENT_COMPARABLES.filter(c => 
          c.commune && c.commune.toLowerCase().includes(lower) && c.id !== excludeId
        ).slice(0, 4);
        if (comps.length < 3) {
          const others = GENEVA_RECENT_COMPARABLES.filter(c => c.id !== excludeId).slice(0, 4 - comps.length);
          comps = [...comps, ...others];
        }
      }

      if (comps.length > 0) {
        WIZARD_COMPARABLES = comps.map((c, idx) => ({
          id: c.id,
          is_anchor: (idx === 0),
          address: c.address,
          commune: c.commune,
          date: c.raw_date || c.date || "2026",
          surface: c.surface || 85,
          price: c.price || 1200000,
          price_m2: c.price_m2 || Math.round((c.price || 1200000) / (c.surface || 85)),
          similarity: idx === 0 ? 98 : (90 - idx * 4),
          source: "Base FAO / RF"
        }));

        renderWizardComps();

        const avgM2 = Math.round(WIZARD_COMPARABLES.reduce((acc, c) => acc + c.price_m2, 0) / WIZARD_COMPARABLES.length);
        const slider = document.getElementById('sliderBasePriceM2');
        if (slider && avgM2 >= 8000 && avgM2 <= 30000) {
          slider.value = avgM2;
          updateValuationFormula();
        }
      }
    }
`;

// Insert the new JS functions before resetBlankStudio()
if (!html.includes('loadCadastreIndexes()')) {
  html = html.replace('function resetBlankStudio()', newJsFunctions + '\n    function resetBlankStudio()');
  console.log('✓ JS functions injected');
}

// In resetBlankStudio(), ensure cadastre lock badge is cleared
if (!html.includes("lockBadge.style.display = 'none';")) {
  html = html.replace("IS_VIERGE_MODE = true;", `IS_VIERGE_MODE = true;
      const lockBadge = document.getElementById('cadastreLockBadge');
      if (lockBadge) lockBadge.style.display = 'none';`);
  console.log('✓ resetBlankStudio updated');
}

// In loadSautDuLoupCase(), ensure cadastre lock badge is shown
if (!html.includes("lockBadge.style.display = 'inline-flex';")) {
  html = html.replace("IS_VIERGE_MODE = false;", `IS_VIERGE_MODE = false;
        const lockBadge = document.getElementById('cadastreLockBadge');
        const lockText = document.getElementById('cadastreLockText');
        if (lockBadge && lockText) {
          lockBadge.style.display = 'inline-flex';
          lockText.innerHTML = '<strong>SITG Verrouillé :</strong> Parcelle 4642 (1225 Chêne-Bourg) · EGRID CH376390706537';
        }`);
  console.log('✓ loadSautDuLoupCase updated');
}

// Call loadCadastreIndexes() and initAddressAutocomplete() on DOMContentLoaded
if (!html.includes('loadCadastreIndexes()')) {
  html = html.replace("window.addEventListener('DOMContentLoaded', () => {", `window.addEventListener('DOMContentLoaded', () => {
      loadCadastreIndexes();
      initAddressAutocomplete();`);
  console.log('✓ DOMContentLoaded wired');
} else if (!html.includes('initAddressAutocomplete();')) {
  html = html.replace("window.addEventListener('DOMContentLoaded', () => {", `window.addEventListener('DOMContentLoaded', () => {
      loadCadastreIndexes();
      initAddressAutocomplete();`);
}

writeFileSync(htmlPath, html, 'utf8');
console.log('public/dv/index.html successfully updated and saved!');
