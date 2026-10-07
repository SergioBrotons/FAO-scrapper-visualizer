import { readFileSync } from "fs";

const filePath = "public/dv/index.html";
let html = readFileSync(filePath, "utf8");

// Pane 1 Rebuild
const oldPane1 = `<div class="wizard-pane active" id="wizardPane1">[\\s\\S]*?<!-- ================= PANE 2: SURFACES & TECHNIQUE ================= -->`;
const newPane1 = `<div class="wizard-pane active" id="wizardPane1">
          <div class="form-section-title">
            <svg class="mini-icon" width="20" height="20" viewBox="0 0 24 24"><polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/><line x1="9" y1="3" x2="9" y2="18"/><line x1="15" y1="6" x2="15" y2="21"/></svg>
            <span>Étape 01 · Identification du Mandant & Références Cadastrales (Slides 1, 2, 3)</span>
          </div>
          <div class="form-section-sub">
            Renseignez les données administratives officielles. Chaque champ est calibré pour s'intégrer harmonieusement dans les diapositives de couverture et les fiches administratives du document PPTX.
          </div>

          <!-- Card 1: Mandant & Couverture -->
          <div class="wizard-card">
            <div class="wizard-card-header">
              <span>1. Mandant & Titre de la Présentation (Slide 01)</span>
              <span style="font-size:11px; font-weight:700; color:var(--dv-teal); text-transform:none;">Couverture Prestige</span>
            </div>
            <div class="wizard-card-sub">Informations visibles sur la page de garde remise aux propriétaires.</div>

            <div class="form-grid-3">
              <div class="form-field">
                <label>Nom du Mandant / Propriétaire</label>
                <input type="text" id="wizOwner" value="Sergio Brotons Mas">
              </div>
              <div class="form-field">
                <label>Contact Client (Téléphone / E-mail)</label>
                <input type="text" id="wizClientContact" value="+41 78 000 00 00 · sergio.brotons@bluewin.ch">
              </div>
              <div class="form-field">
                <label>Type de Bien (Intitulé Couverture)</label>
                <input type="text" id="wizPropertyType" value="APPARTEMENT PPE CONTEMPORAIN AVEC JARDIN">
                <div class="char-meta">
                  <span class="char-hint">Titre principal couverture</span>
                  <span class="char-counter" id="cntPropertyType">0 / 60 car. max (Slide 1)</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Card 2: Cadastre & SITG -->
          <div class="wizard-card">
            <div class="wizard-card-header">
              <span>2. Références Cadastrales & Immeuble (Slide 02)</span>
              <span style="font-size:11px; font-weight:700; color:var(--dv-deep-green); text-transform:none;">Fiche Administrative</span>
            </div>
            <div class="wizard-card-sub">Identification officielle au Registre Foncier et géoportail de l'État de Genève.</div>

            <div class="form-grid-3">
              <div class="form-field">
                <label>Adresse du Bien</label>
                <input type="text" id="wizAddress" value="Chemin du Saut-du-Loup 18">
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

            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:10px; background:var(--dv-sand); padding:12px 18px; border-radius:6px;">
              <div style="font-size:12px; color:var(--dv-deep-green);">
                <strong>SITG Officiel :</strong> Vérification cadastrale instantanée sur le géoportail de l'État de Genève.
              </div>
              <div style="display:flex; gap:10px;">
                <a href="https://map.sitg.ge.ch/?center=2504600,1117200&scale=2500&mapresources=CADASTRE" target="_blank" rel="noopener" class="btn-action-secondary" style="font-size:11px; padding:6px 12px;">
                  <svg class="mini-icon" width="13" height="13" viewBox="0 0 24 24"><polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/><line x1="9" y1="3" x2="9" y2="18"/><line x1="15" y1="6" x2="15" y2="21"/></svg>
                  <span>Ouvrir SITG Cadastre</span>
                </a>
                <button class="btn-action-primary" style="font-size:11px; padding:6px 12px;" onclick="showToast('Données cadastrales synchronisées avec SITG et FAO.')">
                  <svg class="mini-icon" width="13" height="13" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
                  <span>Auto-remplir depuis le Système</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Card 3: Micro-secteur Slide 3 -->
          <div class="wizard-card">
            <div class="wizard-card-header">
              <span>3. Situation Géographique & Micro-Secteur (Slide 03)</span>
              <span style="font-size:11px; font-weight:700; color:var(--dv-teal); text-transform:none;">Synthèse Quartier</span>
            </div>
            <div class="wizard-card-sub">Une description concise soulignant l'attractivité immédiate et les commodités.</div>

            <div class="form-field">
              <label>Micro-localisation en une phrase clé (Slide 03)</label>
              <textarea id="wizMicroLocation" rows="2">Enclave résidentielle très calme et arborée, à 650 m de la gare CEVA Chêne-Bourg et des commerces.</textarea>
              <div class="char-meta">
                <span class="char-hint">Recommandation PPTX : 1 phrase percutante pour préserver l'impact visuel</span>
                <span class="char-counter" id="cntMicroLocation">0 / 140 car. max (Slide 3)</span>
              </div>
            </div>
          </div>
        </div>

        <!-- ================= PANE 2: SURFACES & TECHNIQUE ================= -->`;

html = html.replace(new RegExp(oldPane1), newPane1);

// Pane 2 Rebuild
const oldPane2 = `<div class="wizard-pane" id="wizardPane2">[\\s\\S]*?<!-- ================= PANE 3: VISITE & PHOTOS ================= -->`;
const newPane2 = `<div class="wizard-pane" id="wizardPane2">
          <div class="form-section-title">
            <svg class="mini-icon" width="20" height="20" viewBox="0 0 24 24"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M3 9h18"/><path d="M9 21V9"/></svg>
            <span>Étape 02 · Fiche Technique, Surfaces Pondérées & Équipements (Slide 2)</span>
          </div>
          <div class="form-section-sub">
            Le calcul de surface pondérée applique la règle D&V : 100% PPE + 50% Loggia fermée + 33% Terrasse dallée. Le jardin privatif de pleine terre de 250 m² est valorisé séparément pour garantir une parfaite équité comparative.
          </div>

          <!-- Card 1: Surfaces -->
          <div class="wizard-card">
            <div class="wizard-card-header">
              <span>1. Surfaces & Pondérations Réglementaires D&V</span>
              <span style="font-size:11px; font-weight:700; color:var(--dv-teal); text-transform:none;">Pondération 92.5 m²</span>
            </div>
            <div class="wizard-card-sub">Saisissez les métrés officiels. La surface pondérée est recalculée en temps réel.</div>

            <div class="form-grid-4">
              <div class="form-field">
                <label>Surface PPE Intérieure (100%)</label>
                <div class="unit-input-wrap">
                  <input type="number" step="0.5" id="wizSurfPPE" value="73.0" oninput="recalculateSurfaces()">
                  <span class="unit-tag">m²</span>
                </div>
              </div>
              <div class="form-field">
                <label>Loggia Fermée / Véranda (50%)</label>
                <div class="unit-input-wrap">
                  <input type="number" step="0.5" id="wizSurfLoggia" value="11.0" oninput="recalculateSurfaces()">
                  <span class="unit-tag">m²</span>
                </div>
              </div>
              <div class="form-field">
                <label>Terrasse Dallée (33%)</label>
                <div class="unit-input-wrap">
                  <input type="number" step="0.5" id="wizSurfTerrace" value="42.0" oninput="recalculateSurfaces()">
                  <span class="unit-tag">m²</span>
                </div>
              </div>
              <div class="form-field">
                <label>Surface Pondérée Retenue</label>
                <div class="unit-input-wrap">
                  <input type="text" id="wizWeightedSurf" value="92.5" readonly style="background:#F8FAFC; font-weight:800; color:var(--dv-teal); font-size:15px;">
                  <span class="unit-tag">m²</span>
                </div>
              </div>
            </div>

            <div class="form-grid-3">
              <div class="form-field">
                <label>Surface Jardin Privatif (Pleine Terre)</label>
                <div class="unit-input-wrap">
                  <input type="number" step="10" id="wizSurfGarden" value="250" oninput="updateValuationFormula()">
                  <span class="unit-tag">m²</span>
                </div>
              </div>
              <div class="form-field">
                <label>Nombre de Pièces</label>
                <input type="text" id="wizRooms" value="4 pièces (dont 2 chambres et 2 sanitaires)">
              </div>
              <div class="form-field">
                <label>Stationnement & Box</label>
                <input type="text" id="wizParking" value="1 place couverte en sous-sol (n° 7)">
              </div>
            </div>
          </div>

          <!-- Card 2: Equipements -->
          <div class="wizard-card">
            <div class="wizard-card-header">
              <span>2. Équipements Techniques & Dépendances</span>
              <span style="font-size:11px; font-weight:700; color:var(--dv-deep-green); text-transform:none;">Fiche Technique</span>
            </div>
            <div class="wizard-card-sub">Prestations de standing et caractéristiques thermiques du bâtiment.</div>

            <div class="form-grid-3">
              <div class="form-field">
                <label>Cave Privative</label>
                <input type="text" id="wizCellar" value="1 cave privative sécurisée (lot C)">
              </div>
              <div class="form-field">
                <label>Système de Chauffage</label>
                <input type="text" id="wizHeating" value="Pompe à chaleur (PAC) géothermique au sol">
              </div>
              <div class="form-field">
                <label>Ventilation & Solaire</label>
                <input type="text" id="wizVentilation" value="Double-flux Minergie + Panneaux solaires toiture">
              </div>
            </div>

            <div class="form-grid-2">
              <div class="form-field">
                <label>Charges de Copropriété Mensuelles / Annuelles</label>
                <input type="text" id="wizChargesAnnual" value="CHF 559.-/mois (CHF 6'708.-/an)">
              </div>
              <div class="form-field">
                <label>Fonds de Rénovation de la Copropriété</label>
                <input type="text" id="wizRenovFund" value="CHF 148'000 (solde au 31.12.2025 · part lot: CHF 7'104.-)">
              </div>
            </div>
          </div>
        </div>

        <!-- ================= PANE 3: VISITE & PHOTOS ================= -->`;

html = html.replace(new RegExp(oldPane2), newPane2);

// Pane 3 Rebuild
const oldPane3 = `<div class="wizard-pane" id="wizardPane3">[\\s\\S]*?<!-- ================= PANE 4: COMPARABLES NOTARIÉS ================= -->`;
const newPane3 = `<div class="wizard-pane" id="wizardPane3">
          <div class="form-section-title">
            <svg class="mini-icon" width="20" height="20" viewBox="0 0 24 24"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
            <span>Étape 03 · Visite Qualificative & Photos par Slide (Slides 1, 4, 5, 6, 7)</span>
          </div>
          <div class="form-section-sub">
            Téléchargez les photos spécifiques qui s'insèreront directement dans les gabarits d'images de vos diapositives PPTX, et personnalisez les observations professionnelles de votre visite sur place.
          </div>

          <!-- Card 1: Phototheque -->
          <div class="wizard-card">
            <div class="wizard-card-header">
              <span>1. Photothèque Haute Définition par Diapositive</span>
              <span style="font-size:11px; font-weight:700; color:var(--dv-teal); text-transform:none;">4 Emplacements PPTX</span>
            </div>
            <div class="wizard-card-sub">Cliquez sur une zone pour charger vos propres photographies ou laissez les visuels de référence.</div>

            <div class="pptx-slides-upload-grid" style="margin-bottom:12px;">
              <!-- Slide 1 Cover -->
              <div class="upload-slide-card">
                <div class="upload-slide-title">Slide 01 &bull; Couverture Principale</div>
                <div class="upload-dropzone" onclick="document.getElementById('fileCover').click()">
                  <input type="file" id="fileCover" accept="image/*" style="display:none;" onchange="handleImageUpload('cover', this)">
                  <div id="previewCover" class="dropzone-placeholder">
                    <svg class="mini-icon" width="22" height="22" viewBox="0 0 24 24"><rect width="18" height="18" x="3" y="3" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/></svg>
                    <span>Façade & Accueil Résidence</span>
                  </div>
                </div>
              </div>

              <!-- Slide 5 Interior -->
              <div class="upload-slide-card">
                <div class="upload-slide-title">Slide 05 &bull; Reportage Intérieur</div>
                <div class="upload-dropzone" onclick="document.getElementById('fileInterior').click()">
                  <input type="file" id="fileInterior" accept="image/*" style="display:none;" onchange="handleImageUpload('interior', this)">
                  <div id="previewInterior" class="dropzone-placeholder">
                    <svg class="mini-icon" width="22" height="22" viewBox="0 0 24 24"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
                    <span>Séjour / Cuisine Ouverte</span>
                  </div>
                </div>
              </div>

              <!-- Slide 6 Exterior -->
              <div class="upload-slide-card">
                <div class="upload-slide-title">Slide 06 &bull; Jardin & Extérieurs</div>
                <div class="upload-dropzone" onclick="document.getElementById('fileExterior').click()">
                  <input type="file" id="fileExterior" accept="image/*" style="display:none;" onchange="handleImageUpload('exterior', this)">
                  <div id="previewExterior" class="dropzone-placeholder">
                    <svg class="mini-icon" width="22" height="22" viewBox="0 0 24 24"><polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/><line x1="9" y1="3" x2="9" y2="18"/><line x1="15" y1="6" x2="15" y2="21"/></svg>
                    <span>Jardin Privatif 250 m² & Terrasse</span>
                  </div>
                </div>
              </div>

              <!-- Slide 7 Plan -->
              <div class="upload-slide-card">
                <div class="upload-slide-title">Slide 07 &bull; Plan Architecte</div>
                <div class="upload-dropzone" onclick="document.getElementById('filePlan').click()">
                  <input type="file" id="filePlan" accept="image/*" style="display:none;" onchange="handleImageUpload('plan', this)">
                  <div id="previewPlan" class="dropzone-placeholder">
                    <svg class="mini-icon" width="22" height="22" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                    <span>Plan PPE de Masse Lot 2.02</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Card 2: Appréciations Slide 4 -->
          <div class="wizard-card">
            <div class="wizard-card-header">
              <span>2. Diagnostics Qualitatifs de la Visite (Slide 04)</span>
              <span style="font-size:11px; font-weight:700; color:var(--dv-teal); text-transform:none;">Grille d'Évaluation Terrain</span>
            </div>
            <div class="wizard-card-sub">Textes intégrés dans les 4 quadrants d'analyse de la diapositive 4.</div>

            <div class="form-grid-2">
              <div class="form-field">
                <label>Distribution & Circulation (Slide 04)</label>
                <textarea id="wizQualDist" rows="3">Entrée privative avec vestiaire intégré, dégagement fluide, double orientation Sud-Est et Nord sans surface perdue.</textarea>
                <div class="char-meta">
                  <span class="char-hint">Quadrant 1 : Organisation spatiale</span>
                  <span class="char-counter" id="cntQualDist">0 / 150 car. max (Slide 4)</span>
                </div>
              </div>
              <div class="form-field">
                <label>Matériaux & Équipements de Standing (Slide 04)</label>
                <textarea id="wizQualEquip" rows="3">Cuisine aménagée haut de gamme, parquet chêne massif brossé, stores à lamelles électriques, label Minergie GE-1672.</textarea>
                <div class="char-meta">
                  <span class="char-hint">Quadrant 2 : Finitions & technique</span>
                  <span class="char-counter" id="cntQualEquip">0 / 150 car. max (Slide 4)</span>
                </div>
              </div>
            </div>

            <div class="form-grid-2">
              <div class="form-field">
                <label>État Général & Entretien (Slide 04)</label>
                <textarea id="wizQualState" rows="3">État irréprochable comme neuf, copropriété récente 2018 sous garantie décennale, aucun appel de fonds extraordinaire voté en AG.</textarea>
                <div class="char-meta">
                  <span class="char-hint">Quadrant 3 : Vétusté & copropriété</span>
                  <span class="char-counter" id="cntQualState">0 / 150 car. max (Slide 4)</span>
                </div>
              </div>
              <div class="form-field">
                <label>Environnement & Nuisances (Slide 04)</label>
                <textarea id="wizQualEnv" rows="3">Calme absolu, absence de vis-à-vis gênant, voie sans issue résidentielle très préservée à 650 m de la gare CEVA.</textarea>
                <div class="char-meta">
                  <span class="char-hint">Quadrant 4 : Environnement immédiat</span>
                  <span class="char-counter" id="cntQualEnv">0 / 150 car. max (Slide 4)</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ================= PANE 4: COMPARABLES NOTARIÉS ================= -->`;

html = html.replace(new RegExp(oldPane3), newPane3);

// Pane 4 Rebuild
const oldPane4 = `<div class="wizard-pane" id="wizardPane4">[\\s\\S]*?<!-- ================= PANE 5: METHODE D&V & INDICES OCSTAT ================= -->`;
const newPane4 = `<div class="wizard-pane" id="wizardPane4">
          <div class="form-section-title">
            <svg class="mini-icon" width="20" height="20" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
            <span>Étape 04 · Panel Comparables Notariés & Normalisation (Slides 8, 9)</span>
          </div>
          <div class="form-section-sub">
            Gérez le panel des transactions officielles retenues pour étayer l'estimation. Chaque vente est documentée avec son acte notarié, sa date d'enregistrement et son niveau de similitude.
          </div>

          <!-- Card 1: Anchor Sale 16 -->
          <div class="wizard-card" style="border: 2px solid var(--dv-teal); background: rgba(0, 147, 157, 0.04);">
            <div class="wizard-card-header">
              <span style="display:flex; align-items:center; gap:8px;">
                <span class="saut-badge" style="margin:0;">⭐ VENTE ANCRE DE RÉFÉRENCE ABSOLUE</span>
                <span style="font-size:18px;">Chemin du Saut-du-Loup 16</span>
              </span>
              <span style="font-size:20px; font-weight:800; color:var(--dv-teal);">CHF 1'620'000 (17'609 CHF/m²)</span>
            </div>
            <div class="wizard-card-sub" style="margin-bottom:8px; color:var(--dv-deep-green);">
              Même résidence Minergie contiguë, même promoteur, construite dans le même ensemble. Acte notarié <strong>2026/628/0</strong> du <strong>26 février 2026</strong> (Feuillet 4642-104).
            </div>
            <div style="font-size:12px; color:#475569; line-height:1.5;">
              Vendeur: <strong>TASHMATOVA Saltanat</strong> &bull; Acquéreurs: <strong>COLCOMBET Rémi & VERNAZ Charlotte</strong> &bull; Surface: <strong>92 m²</strong> avec balcon 14 m². Cette vente authentique établit la cote irréfutable des logements contemporains du quartier.
            </div>
          </div>

          <!-- Card 2: Panel Comparables Table -->
          <div class="wizard-card">
            <div class="wizard-card-header">
              <span>Panel des Ventes Notariées Récentes Retenues (Slide 09)</span>
              <span style="font-size:11px; font-weight:700; color:var(--dv-teal); text-transform:none;" id="wizardCompsAvgLabel">Moyenne panel : CHF 16'144 / m²</span>
            </div>
            <div class="wizard-card-sub">Tableau synchronisé directement dans les 6 lignes de comparables de la diapositive 9 du PPTX.</div>

            <div class="comps-table-wrap">
              <table class="comps-table">
                <thead>
                  <tr>
                    <th>Statut / Source Officielle</th>
                    <th>Adresse & Commune</th>
                    <th>Date Acte</th>
                    <th>Surface</th>
                    <th>Prix Acté (CHF)</th>
                    <th>Prix / m²</th>
                    <th>Similitude</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody id="wizardCompsTbody">
                  <!-- Injected by JavaScript -->
                </tbody>
              </table>
            </div>

            <div style="display:flex; justify-content:flex-end; gap:10px; margin-top:14px;">
              <button class="btn-action-secondary" onclick="addManualComparablePrompt()">
                <svg class="mini-icon" width="13" height="13" viewBox="0 0 24 24"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                <span>+ Saisie Vente Interne D&V (Off-Market)</span>
              </button>
              <button class="btn-action-primary" onclick="addFaoComparablePrompt()">
                <svg class="mini-icon" width="13" height="13" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
                <span>+ Ajouter depuis la Base Notariée FAO</span>
              </button>
            </div>
          </div>

          <!-- Card 3: Normalisation Slide 9 -->
          <div class="wizard-card">
            <div class="wizard-card-header">
              <span>Méthode de Normalisation Comparative (Slide 09 Encadré Bas)</span>
              <span style="font-size:11px; font-weight:700; color:var(--dv-teal); text-transform:none;">Rigueur Démonstrative</span>
            </div>
            <div class="wizard-card-sub">Justification du passage des transactions observées au prix de base retenu.</div>

            <div class="form-field">
              <label>Synthèse de normalisation méthodologique (Slide 09)</label>
              <textarea id="wizNormMethod" rows="2">Normalisation D&V : Référence ancre = Saut-du-Loup 16 (17’609 CHF/m²). Base prudentielle retenue à 16’000 CHF/m² pour tenir compte de la surface pondérée.</textarea>
              <div class="char-meta">
                <span class="char-hint">Recommandation PPTX : 2 à 3 lignes pour un affichage limpide sans chevauchement</span>
                <span class="char-counter" id="cntNormMethod">0 / 180 car. max (Slide 9)</span>
              </div>
            </div>
          </div>
        </div>

        <!-- ================= PANE 5: METHODE D&V & INDICES OCSTAT ================= -->`;

html = html.replace(new RegExp(oldPane4), newPane4);

// Pane 5 Rebuild
const oldPane5 = `<div class="wizard-pane" id="wizardPane5">[\\s\\S]*?<!-- ================= PANE 6: STRATEGIE & EXPORT PPTX ================= -->`;
const newPane5 = `<div class="wizard-pane" id="wizardPane5">
          <div class="form-section-title">
            <svg class="mini-icon" width="20" height="20" viewBox="0 0 24 24"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>
            <span>Étape 05 · Méthodologie Décomposée D&V & Indices OCSTAT (Slides 10, 11, 12)</span>
          </div>
          <div class="form-section-sub">
            Décomposition rigoureuse en 3 composantes distinctes : Bâti pondéré + Valeur foncière du jardin privatif + Valeur vénale du stationnement couvert en sous-sol.
          </div>

          <!-- Card 1: OCSTAT Slide 10 -->
          <div class="wizard-card">
            <div class="wizard-card-header">
              <span>1. Baromètre Statistique Cantonal OCSTAT Genève (Slide 10)</span>
              <span class="pulse-validated-badge" style="background:var(--dv-sand);">Indices Officiels</span>
            </div>
            <div class="wizard-card-sub">Indices de marché cantonaux consolidant la dynamique haussière en Rive Gauche.</div>

            <div class="form-field">
              <label>Tendance de Marché Documentée (Slide 10)</label>
              <textarea id="wizMarketTrend" rows="2">+4.2% sur les appartements PPE récents en Rive Gauche sur les 18 derniers mois (OCSTAT Genève). Chêne-Bourg bénéficie d'une forte valorisation soutenue par l'attractivité du Léman Express.</textarea>
              <div class="char-meta">
                <span class="char-hint">Tendance macro-économique cantonale (Slide 10)</span>
                <span class="char-counter" id="cntMarketTrend">0 / 150 car. max (Slide 10)</span>
              </div>
            </div>
          </div>

          <!-- Card 2: Interactive Sliders Slide 11 -->
          <div class="wizard-card">
            <div class="wizard-card-header">
              <span>2. Décomposition Analytique en 3 Composantes (Slide 11)</span>
              <span style="font-size:11px; font-weight:700; color:var(--dv-teal); text-transform:none;">Simulateur Paramétrique</span>
            </div>
            <div class="wizard-card-sub">Ajustez les curseurs ci-dessous : la valeur vénale totale et les diapositives se recalculent instantanément.</div>

            <div class="form-grid-3">
              <div class="form-field">
                <label style="display:flex; justify-content:space-between;">
                  <span>Prix de Base Bâti Pondéré</span>
                  <strong id="labelBasePriceM2" style="color:var(--dv-teal); font-size:14px;">CHF 16'000 / m²</strong>
                </label>
                <input type="range" min="12000" max="20000" step="250" id="sliderBasePriceM2" value="16000" oninput="updateValuationFormula()">
                <span style="font-size:11px; color:var(--dv-text-muted);">Calibré sur acte n° 16 à 17'609 CHF/m² avec marge prudentielle</span>
              </div>

              <div class="form-field">
                <label style="display:flex; justify-content:space-between;">
                  <span>Valorisation Jardin Privatif (250 m²)</span>
                  <strong id="labelGardenValue" style="color:var(--dv-teal); font-size:14px;">+CHF 250'000</strong>
                </label>
                <input type="range" min="100000" max="400000" step="10000" id="sliderGardenValue" value="250000" oninput="updateValuationFormula()">
                <span style="font-size:11px; color:var(--dv-text-muted);">Base 1'000 CHF/m² pour jouissance exclusive de pleine terre</span>
              </div>

              <div class="form-field">
                <label style="display:flex; justify-content:space-between;">
                  <span>Valeur Parking & Cave Privative</span>
                  <strong id="labelParkingValue" style="color:var(--dv-teal); font-size:14px;">+CHF 50'000</strong>
                </label>
                <input type="range" min="30000" max="80000" step="5000" id="sliderParkingValue" value="50000" oninput="updateValuationFormula()">
                <span style="font-size:11px; color:var(--dv-text-muted);">Valeur vénale certifiée standard PPE Chêne-Bourg</span>
              </div>
            </div>

            <!-- Live Result Box -->
            <div class="live-val-card" style="margin-top:16px;">
              <div class="live-val-left">
                <div class="live-val-title">Valeur Vénale Centrale Certifiée D&V</div>
                <div class="live-val-price" id="wizLiveValDisplay">CHF 1'780'000</div>
                <div class="live-val-sub" id="wizLiveRangeDisplay">Fourchette de commercialisation recommandée : CHF 1'750'000 – CHF 1'790'000</div>
              </div>
              <div class="live-val-breakdown">
                <div class="breakdown-pill">
                  <span>Bâti Pondéré (92.5 m²)</span>
                  <strong id="pillBuiltVal">CHF 1'480'000</strong>
                </div>
                <div class="breakdown-pill">
                  <span>Jardin Privatif</span>
                  <strong id="pillGardenVal">CHF 250'000</strong>
                </div>
                <div class="breakdown-pill">
                  <span>Parking Couvert</span>
                  <strong id="pillParkingVal">CHF 50'000</strong>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ================= PANE 6: STRATEGIE & EXPORT PPTX ================= -->`;

html = html.replace(new RegExp(oldPane5), newPane5);

// Pane 6 Rebuild
const oldPane6 = `<div class="wizard-pane" id="wizardPane6">[\\s\\S]*?<!-- Wizard Navigation Footer -->`;
const newPane6 = `<div class="wizard-pane" id="wizardPane6">
          <div class="form-section-title">
            <svg class="mini-icon" width="20" height="20" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            <span>Étape 06 · Stratégie Commerciale, Fiscalité LIPP & Exportation PPTX (Slides 12 à 15)</span>
          </div>
          <div class="form-section-sub">
            Définissez les paramètres finaux de mise en vente, la fiscalité immobilière cantonale, les termes du mandat exclusif et générez la présentation PowerPoint complète de 15 diapositives.
          </div>

          <!-- Card 1: Fourchettes Slide 12 -->
          <div class="wizard-card">
            <div class="wizard-card-header">
              <span>1. Fourchettes de Commercialisation & Prix d'Appel (Slide 12)</span>
              <span style="font-size:11px; font-weight:700; color:var(--dv-teal); text-transform:none;">Stratégie d'Affichage</span>
            </div>
            <div class="wizard-card-sub">Positionnement calibré sous le seuil psychologique de CHF 1'800'000.</div>

            <div class="form-grid-3">
              <div class="form-field">
                <label>Fourchette Basse de Négociation</label>
                <div class="unit-input-wrap">
                  <input type="number" id="wizRangeMin" value="1750000" oninput="syncRanges()">
                  <span class="unit-tag">CHF</span>
                </div>
              </div>
              <div class="form-field">
                <label>Prix de Mise en Vente Recommandé</label>
                <div class="unit-input-wrap">
                  <input type="number" id="wizTargetPrice" value="1780000" oninput="syncRanges()">
                  <span class="unit-tag">CHF</span>
                </div>
              </div>
              <div class="form-field">
                <label>Fourchette Haute (Plafond Psychologique)</label>
                <div class="unit-input-wrap">
                  <input type="number" id="wizRangeMax" value="1790000" oninput="syncRanges()">
                  <span class="unit-tag">CHF</span>
                </div>
              </div>
            </div>

            <div class="form-grid-2" style="margin-top:14px;">
              <div class="form-field">
                <label>Hypothèse de Négociation (Slide 12)</label>
                <input type="text" id="wizNegHypo" value="Hypothèse de négociation : 1.5% à 2.0% avec prix d'appel recommandé à CHF 1'790'000.">
                <div class="char-meta">
                  <span class="char-hint">Marge de négociation (Slide 12)</span>
                  <span class="char-counter" id="cntNegHypo">0 / 150 car. max (Slide 12)</span>
                </div>
              </div>
              <div class="form-field">
                <label>Positionnement Stratégique Retenu (Slide 12)</label>
                <input type="text" id="wizStratPos" value="Préservation du seuil psychologique de 1.8M CHF avec justification directe par l'acte du n° 16.">
                <div class="char-meta">
                  <span class="char-hint">Argument clé de positionnement (Slide 12)</span>
                  <span class="char-counter" id="cntStratPos">0 / 160 car. max (Slide 12)</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Card 2: LIPP & Mandat Slides 13, 14, 15 -->
          <div class="wizard-card">
            <div class="wizard-card-header">
              <span>2. Fiscalité LIPP, Mandat Exclusif & Conclusion (Slides 13, 14, 15)</span>
              <span style="font-size:11px; font-weight:700; color:var(--dv-deep-green); text-transform:none;">Accompagnement & Déontologie</span>
            </div>
            <div class="wizard-card-sub">Informations fiscales cantonales genevoises et conditions d'honoraires de l'agence.</div>

            <div class="form-grid-2">
              <div class="form-field">
                <label>Fiscalité Immobilière Cantonale (LIPP Genève - Slide 13)</label>
                <textarea id="wizLippText" rows="3">Acquis en 2019 (Détention > 7 ans). Taux d'imposition sur le gain immobilier (art. 82 LIPP) : 20%. Réduction à 15% dès 8 ans. Consulter votre notaire pour optimiser le calcul du remploi (art. 84 LIPP).</textarea>
                <div class="char-meta">
                  <span class="char-hint">Conseil fiscal cantonal (Slide 13)</span>
                  <span class="char-counter" id="cntLippText">0 / 160 car. max (Slide 13)</span>
                </div>
              </div>
              <div class="form-field">
                <label>Mandat & Engagement d'Exclusivité (Slide 14)</label>
                <textarea id="wizMandateText" rows="3">Mandat exclusif responsable D&V à 3.0% HT. Prise en charge intégrale des frais de diffusion, reportage professionnel HDR, filtrage de solvabilité et visites accompagnées.</textarea>
                <div class="char-meta">
                  <span class="char-hint">Engagement d'agence (Slide 14)</span>
                  <span class="char-counter" id="cntMandateText">0 / 160 car. max (Slide 14)</span>
                </div>
              </div>
            </div>

            <div class="form-grid-3" style="margin-top:14px;">
              <div class="form-field">
                <label>Courtier Référent en Charge</label>
                <select id="wizBrokerSelect">
                  <option value="Sandra Bleeckx Vanhalst" selected>Sandra Bleeckx Vanhalst (Associée Gérante)</option>
                  <option value="Adrien Désormière">Adrien Désormière (Associé Gérant)</option>
                  <option value="Sandra Bleeckx Vanhalst & Adrien Désormière">Sandra Bleeckx & Adrien Désormière (Binôme)</option>
                </select>
              </div>
              <div class="form-field">
                <label>Validité de l'Offre d'Estimation</label>
                <input type="text" id="wizValidity" value="Validité : 6 mois (Février 2026 – Août 2026)">
              </div>
              <div class="form-field">
                <label>Prochaine Étape Recommandée (Slide 15)</label>
                <input type="text" id="wizNextStep" value="Échange stratégique et fixation de la date de démarrage de la commercialisation">
              </div>
            </div>

            <div class="form-field" style="margin-top:14px;">
              <label>Phrase de Conclusion Personnalisée (Slide 15)</label>
              <textarea id="wizConclusionText" rows="2">Cette estimation actualisée intègre la réalité du marché au 26 février 2026 pour vous assurer une valorisation irréfutable.</textarea>
              <div class="char-meta">
                <span class="char-hint">Mot de clôture signé par les associés (Slide 15)</span>
                <span class="char-counter" id="cntConclusionText">0 / 160 car. max (Slide 15)</span>
              </div>
            </div>
          </div>

          <!-- Card 3: Big Export CTA Box -->
          <div class="wizard-card" style="background:linear-gradient(135deg, rgba(0,147,157,0.06) 0%, rgba(0,74,79,0.08) 100%); border:2px solid var(--dv-teal); text-align:center; padding:32px 24px;">
            <h3 style="font-family:'Cormorant Garamond', Georgia, serif; font-size:26px; font-weight:700; color:var(--dv-deep-green); margin-bottom:8px;">
              Votre Présentation PowerPoint Modifiable (15 Slides) est Prête
            </h3>
            <p style="font-size:13px; color:var(--dv-text-muted); max-width:680px; margin:0 auto 22px auto; line-height:1.5;">
              Le document contiendra l'intégralité des 15 diapositives personnalisées d'après les données ci-dessus, avec les comparables notariés, les visuels insérés, les calculs de pondération et zéro mention interne. Ouvrable et éditable dans PowerPoint et Keynote.
            </p>
            <div style="display:flex; justify-content:center; gap:16px; flex-wrap:wrap;">
              <button class="btn-action-primary" id="btnWizExportPptx" style="padding:14px 28px; font-size:14.5px;" onclick="exportPresentationPptx()">
                <svg class="mini-icon" width="18" height="18" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                <span>Générer & Télécharger la Présentation PPTX (15 Slides)</span>
              </button>
              <a href="/data/exports/Estimation_Saut_du_Loup_18_Brotons_2026.pptx" download="Estimation_DV_Chemin_du_Saut_du_Loup_18_Brotons.pptx" class="btn-action-secondary" style="padding:14px 22px; font-size:13.5px; text-decoration:none;">
                <svg class="mini-icon" width="16" height="16" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                <span>Téléchargement Direct du Cas Référence</span>
              </a>
            </div>
          </div>
        </div>

        <!-- Wizard Navigation Footer -->`;

html = html.replace(new RegExp(oldPane6), newPane6);

// Update exportPresentationPptx to pass all newly defined fields
const oldExportCall = `const broker = document.getElementById('wizBrokerSelect')?.value || CURRENT_PERSONA;

        // Construct customized slide replacements
        const slideReplacements = {`;

const newExportCall = `const broker = document.getElementById('wizBrokerSelect')?.value || CURRENT_PERSONA;
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
            "[Commune], le [date]": \`\${commune.split(' ').pop()}, le 26 février 2026\`,
            "[ADRESSE DU BIEN]": address
          },
          slide2: {
            "[ADRESSE COMPLÈTE]": address,
            "[Nom de la résidence / bâtiment]  ·  [Commune]": \`\${residence} · \${commune}\`,
            "[00] PIÈCES": rooms.split(' ')[0] || "4",
            "[00 m²] SURFACE PPE": \`\${surfPPE} m²\`,
            "[00 m²] SURFACE PONDÉRÉE": \`\${weightedSurf} m²\`,
            "[AAAA] CONSTRUCTION": buildingYear.substring(0, 4),
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
            "[Charges / fonds]": \`Charges: \${chargesAnnual} · Fonds: \${renovFund}\`
          },
          slide3: {
            "[PARCELLE N°0000]": \`PARCELLE N° \${parcel} (\${commune.toUpperCase()})\`,
            "[Micro-localisation en une phrase]": microLocation
          },
          slide4: {
            "[Distribution & circulation]": qualDist,
            "[Matériaux & équipements]": qualEquip,
            "[État & entretien]": qualState,
            "[Environnement & nuisances]": qualEnv
          },
          slide10: {
            "[Évolution récente documentée]": marketTrend,
            "[Position de la commune]": "Chêne-Bourg bénéficie d'une forte valorisation soutenue par l'attractivité du Léman Express.",
            "[Écart entre prix affichés et transactions]": "Marge moyenne de négociation constatée inférieure à 2.5% sur les biens haut standing récents.",
            "CHF [00’000]": "CHF " + Number(basePriceM2).toLocaleString('fr-CH'),
            "[00’000]": Number(basePriceM2).toLocaleString('fr-CH')
          },
          slide12: {
            "CHF [0’000’000]": [\`CHF \${Number(Math.round(weightedSurf * basePriceM2)).toLocaleString('fr-CH')}\`, \`CHF \${Number(totalVal).toLocaleString('fr-CH')}\`],
            "CHF [±00’000]": ["CHF 0", \`+CHF \${Number(gardenVal).toLocaleString('fr-CH')}\`, \`+CHF \${Number(parkingVal).toLocaleString('fr-CH')}\`],
            "CHF [MIN]": \`CHF \${Number(rangeMin).toLocaleString('fr-CH')}\`,
            "CHF [MAX]": \`CHF \${Number(rangeMax).toLocaleString('fr-CH')}\`,
            "[Hypothèse de négociation]": negHypo,
            "[Positionnement retenu]": stratPos,
            "[Validité]": validity
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
          },`;

html = html.replace(oldExportCall, newExportCall);

await Bun.write(filePath, html);
console.log("Successfully rebuilt wizard panes with tabulated cards and character limitation meta!");
