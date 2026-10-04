# Rapport d'Audit & Durcissement Chirurgical (Surgical Hardening Report)
**Projet :** Cytria Real Estate Intelligence (Genève)  
**Date d'exécution :** 4 Octobre 2026  
**Branche Git :** `fix/surgical-security-data-hardening`  
**Environnement d'exécution :** Windows x64 / Bun v1.1.30 / SQLite 3 (Strict Read-Only)  
**Auditeur :** Senior Software Security Engineer & Swiss Real Estate Domain Specialist  

---

## 1. Synthèse Exécutive et Tableau de Classification

Toutes les investigations ont été conduites sous la contrainte absolue de **non-régression**, d'**absence de refactorisation architecturale** et d'**interdiction formelle de modification de la base de données de production** (`data/state/state.sqlite` maintenue en lecture seule stricte).

| ID | Domaine / Risque | Statut | Fichiers Impactés | Résumé de l'Action & Preuve |
|---|---|---|---|---|
| **SEC-01** | Exposition nominative des personnes physiques (nLPD suisse) & contournement par mot de passe "Vault" | **FIXED** | `src/fao_transactions/visualization/map_builder.py`<br>`index.html`<br>`server.js`<br>`src/fao_transactions/dossier/valuation_service.ts` | Anonymisation systématique à la source (`D*** J*** (Personne physique)`) des vendeurs et acquéreurs physiques. Suppression définitive du mot de passe maître en clair (`cytria`, `cytria2026`), des paramètres d'escalade d'URL (`?vault=`) et du stockage de session. Conservation intacte des personnes morales inscrites au RC. |
| **SEC-02** | Téléchargement non authentifié de fichiers sensibles (.sqlite, .env, .git, code source) via le serveur web | **FIXED** | `server.js` | Filtrage de sécurité strict sur le routeur statique. Renvoie systématiquement `403 Forbidden` pour les requêtes ciblant `data/state/*`, `*.sqlite`, `*.db`, `.env*`, `.git*`, `package.json`, scripts sources (`.ts`, `.py`, `.bat`, etc.) et exports CSV bruts. |
| **SEC-03** | Risque d'injection SQL et non-application de la lecture seule SQLite sur le serveur | **FIXED** | `server.js`<br>`src/fao_transactions/dossier/valuation_service.ts` | Toutes les instanciations de base SQLite sont verrouillées avec `{ readonly: true }`. Toutes les requêtes dynamiques (`/api/developer/radar`, `/api/intelligence/transactions`) sont paramétrées avec des placeholders `?`. |
| **DATA-01** | Plafond CASATAX et barème des droits d'enregistrement obsolètes (valeurs 2024/anciennes) | **FIXED** | `data/reference/financial_rules.json`<br>`src/fao_transactions/dossier/valuation_service.ts` | Mise à jour du plafond légal cantonal à **CHF 1'394'928** (en vigueur depuis le 1er mars 2026, communiqué officiel du Conseil d'État) et de l'abattement maximal à **CHF 20'924**. Intégration de l'historique officiel (2024: 1'359'903 CHF; 2025: 1'374'396 CHF; 2026: 1'394'928 CHF). Qualification de l'éligibilité comme conditionnelle au respect de l'affectation en résidence principale. |
| **DATA-02** | Fabrication artificielle de dates et fausse activité pour les agences à 0 transaction (Vélocité) | **FIXED** | `src/fao_transactions/visualization/agency_velocity.py` | Suppression de la valeur factice `Mars 2026` et du délai arbitraire de 180 jours. Pour toute agence sans vente enregistrée, assignation de `dsls = None`, `latest_date_fr = "Aucune vente enregistrée"` et statut `INACTIVE` (`#94a3b8`). |
| **LEGAL-01** | Allégations de certification juridique trompeuses ("Avis Notarié", "Certifié Registre Foncier art. 157") | **FIXED** | `src/fao_transactions/dossier/valuation_service.ts`<br>`src/fao_transactions/visualization/map_builder.py`<br>`index.html` | Remplacement des mentions d'expertise judiciaire ou notariée par **"Rapport d'Analyse Comparative de Marché (CMA)"**. Neutralisation des formules d'homologation légale par la mention officielle exacte : avis indicatifs publiés à la FAO en application de l'art. 157 LaCC. |
| **DATA-03** | Période d'observation erronée affichée ("24 mois" au lieu des ~17.3 mois observés) | **FIXED** | `src/fao_transactions/visualization/map_builder.py` | Qualification temporelle exacte de l'échantillon d'analyse. |
| **DATA-04** | Intégrité des données d'origine et préservation de la base SQLite de référence | **ALREADY SAFE** | `data/state/state.sqlite` | 8'970 transactions vérifiées, 6'535 transactions avec prix > 0 CHF, volume cantonal de CHF 17'466'487'594.03. Aucun enregistrement d'essai injecté (0 enregistrement test). |
| **DATA-05** | Erreur décimale de parsing des montants suisses (P0-01) et surface parcellaire PPE (P0-02) | **ALREADY SAFE** | `tests/test_remediation_fixes.py`<br>`tests/test_surgical_hardening.test.ts` | Vérifié sur le cas critique ID 4837 : montant authentique de CHF 1'875'000.00 préservé (aucun arrondi erroné à 1.88 CHF). Préservation de la dissociation entre parcelle globale et lot PPE. |

---

## 2. Analyse Détaillée des Interventions Chirurgicales

### SEC-01 : Conformité nLPD Suisse et Neutralisation du Contournement Client
- **Vulnérabilité Constatée :** Dans la version d'origine, le client web recevait les identités complètes des vendeurs et acquéreurs particuliers dans le blob JSON `DATA` injecté dans `index.html`. L'anonymisation n'était qu'un masquage d'affichage dans le navigateur, facilement contournable par l'URL `?vault=cytria` ou la saisie du mot de passe maître en clair dans le code source `cytria`.
- **Correction Appliquée :**
  1. `src/fao_transactions/visualization/map_builder.py` (lignes 72-132, 175-185, 3315-3340) : Les fonctions `is_corporate_entity_py` et `mask_party_py` anonymisent les personnes physiques **avant** l'injection dans le HTML : `DUPONT Jean` -> `D*** J*** (Personne physique)`. Les personnes morales (SA, SARL, SI, Banques, Communes) conservent leur raison sociale du Registre du Commerce.
  2. `index.html` : L'intégralité du tableau `DATA` (8'548 actes) a été régénéré avec masquage irréversible (13'513 occurrences nominatives neutralisées).
  3. Le dialogue modal de mot de passe a été remplacé par un volet d'information didactique sur la conformité nLPD. Tout mot de passe maître et tout écouteur d'escalade d'URL (`?vault=`, `?key=`, `?auth=`) ont été purgés.
  4. `server.js` (lignes 605-620) et `src/fao_transactions/dossier/valuation_service.ts` (lignes 55-80, 130-145) : L'API JSON `/api/intelligence/transactions` omet les champs nominatifs bruts, et `/api/dossier/valuation` applique `maskParty` aux parties de l'acte.

### SEC-02 & SEC-03 : Verrouillage du Serveur HTTP et Injection SQL
- **Vulnérabilités Constatées :**
  - `server.js` servait directement n'importe quel fichier de l'arborescence du projet, autorisant le téléchargement direct de `data/state/state.sqlite`, `.env`, et des codes sources de l'application.
  - La route `/api/developer/radar` concaténait la valeur `commune` directement dans la clause SQL, exposant la base SQLite à des injections de requêtes.
  - Les instances de `Database(DB_PATH)` n'étaient pas explicitement ouvertes en mode lecture seule.
- **Correction Appliquée :**
  1. Blocage systématique au début du gestionnaire statique de `server.js` (lignes 722-742) :
     ```javascript
     if (
       lowerPath.includes(".sqlite") ||
       lowerPath.includes(".db") ||
       lowerPath.includes(".env") ||
       lowerPath.startsWith(".git") ||
       lowerPath.startsWith(".venv") ||
       lowerPath.startsWith("data/state") ||
       lowerPath.endsWith(".csv") ||
       lowerPath.endsWith(".xlsx") ||
       lowerPath.endsWith(".py") ||
       lowerPath.endsWith(".ts") ||
       lowerPath.endsWith(".bat") ||
       lowerPath.endsWith(".ps1") ||
       lowerPath.endsWith(".sh") ||
       lowerPath === "pyproject.toml" ||
       lowerPath === "package.json"
     ) {
       return new Response("Forbidden", { status: 403 });
     }
     ```
  2. Paramétrage intégral des requêtes SQL (`q += " AND lower(commune) = lower(?)"; params.push(commune.trim());`).
  3. Verrouillage systématique de toutes les ouvertures de base : `new Database(DB_PATH, { readonly: true })`.

### DATA-01 : Barèmes Légaux CASATAX et Droits d'Enregistrement
- **Anomalie Constatée :** Les fichiers de règles et scripts de valorisation utilisaient des plafonds dépassés ou approximatifs (1'446'000 CHF ou 1'465'000 CHF), et ne documentaient pas les évolutions annuelles indexées par l'Office Cantonal de la Statistique (OCSTAT).
- **Correction Appliquée :**
  1. `data/reference/financial_rules.json` :
     - Plafond 2026 : **CHF 1'394'928**
     - Réduction maximale des droits de mutation (art. 8A LDE) : **CHF 20'924**
     - Réduction des émoluments du registre foncier pour la cédule hypothécaire : 50%
     - Ajout de la table chronologique légale :
       - 2024 : 1'359'903 CHF (abattement max 20'398 CHF)
       - 2025 : 1'374'396 CHF (abattement max 20'616 CHF)
       - 2026 : 1'394'928 CHF (abattement max 20'924 CHF)
  2. `src/fao_transactions/dossier/valuation_service.ts` :
     - Utilisation de la constante officielle `1394928` pour l'exercice 2026.
     - Précision légale stipulant que le bénéfice de CASATAX est légalement soumis à l'engagement de l'acquéreur d'affecter le bien à sa résidence principale pendant une durée continue de 2 ans.

### DATA-02 : Fiabilité de la Vélocité des Agences
- **Anomalie Constatée :** Lorsqu'une agence répertoriée ne présentait aucune vente réconciliée, `compute_agency_velocity` assignait une fausse date `"Mars 2026"` et un indicateur arbitraire de 180 jours (`dsls = 180`).
- **Correction Appliquée :**
  - `src/fao_transactions/visualization/agency_velocity.py` (lignes 86-96) :
    ```python
    if latest_date:
        dsls = max((ref_date - latest_date).days, 0)
        # ... formatage date réelle ...
    else:
        dsls = None
        latest_date_str = None
        latest_date_fr = "Aucune vente enregistrée"

    if dsls is None:
        dsls_status = "INACTIVE"
        dsls_badge_label = "Aucune vente enregistrée"
        dsls_color = "#94a3b8"
    ```

### LEGAL-01 : Conformité Réglementaire des Rapports de Valorisation
- **Anomalie Constatée :** L'outil générait des rapports sous le libellé "Avis de Valeur Notarié & Dossier d'Expertise" et citait l'article 157 LaCC sous la forme d'une prétendue "Certification : Registre Foncier (art. 157 LaCC)". Or, seul un notaire ou un expert immobilier assermenté peut délivrer un avis de valeur notarié. L'art. 157 LaCC régit uniquement la publication des transferts dans la FAO par le département cantonal.
- **Correction Appliquée :**
  - Remplacement systématique du titre par **"Rapport d'Analyse Comparative de Marché (CMA)"**.
  - Remplacement de la certification par **"Source des transferts : Publications officielles FAO (art. 157 LaCC) • Traitement analytique indicatif Cytria"**.
  - Remplacement du tampon d'homologation par la mention standardisée d'évaluation statistique de marché.

---

## 3. Preuves de Validation et Non-Régression

La suite complète de tests de non-régression (`tests/test_surgical_hardening.test.ts`) a été exécutée avec succès via le moteur natif de Bun :
```bash
bun test tests/test_surgical_hardening.test.ts
```
**Résultat :** 18 tests exécutés, 18 réussis, 0 échec, 59 assertions validées en 199 ms.
