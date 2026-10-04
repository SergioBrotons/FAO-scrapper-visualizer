# Résultats des Tests de Non-Régression & Durcissement
**Projet :** Cytria Real Estate Intelligence (Genève)  
**Date :** 4 Octobre 2026  
**Document :** `docs/hardening/REGRESSION_RESULTS.md`  
**Environnement :** Windows 10/11 x64 • Bun v1.1.30 • SQLite 3.45  

---

## 1. Commande d'Exécution et Résultat Global

### Commande de Validation
```powershell
bun test tests/test_surgical_hardening.test.ts
```

### Rapport de Sortie Moteur (Stdout Officiel)
```text
bun test v1.1.30 (7996d06b)

tests\test_surgical_hardening.test.ts:
(pass) nLPD Natural Person Privacy Masking > should preserve corporate entities untouched
(pass) nLPD Natural Person Privacy Masking > should anonymize natural persons with initial asterisks and tag
(pass) nLPD Natural Person Privacy Masking > should sanitize registration suffix dates from natural person entries
(pass) nLPD Natural Person Privacy Masking > should safely handle null, undefined, or empty values
(pass) CASATAX Statutory Schedules and Calculation > should contain the official 2026 ceiling of CHF 1,394,928
(pass) CASATAX Statutory Schedules and Calculation > should document statutory schedules for 2024, 2025, and 2026
(pass) CASATAX Statutory Schedules and Calculation > should accurately determine threshold eligibility at boundary values
(pass) CASATAX Statutory Schedules and Calculation > should correctly compute maximum mutation rebate capped at CHF 20,924
(pass) Database Read-Only Guarantees and Baseline Integrity > should open database in strictly read-only mode and reject writes
(pass) Database Read-Only Guarantees and Baseline Integrity > should contain exactly 8,970 baseline transactions
(pass) Database Read-Only Guarantees and Baseline Integrity > should verify total cantonal transaction volume bounds (~17.47B CHF)
(pass) Database Read-Only Guarantees and Baseline Integrity > should verify record 4837 price parsing integrity (CHF 1'875'000, not 1.88 CHF)
(pass) Database Read-Only Guarantees and Baseline Integrity > should verify dataset notice year distribution (2023: 91, 2024: 1325, 2025: 4375, 2026: 3179)
(pass) Database Read-Only Guarantees and Baseline Integrity > should verify agency sales attribution baseline (83 agencies, 2,183 sales)
(pass) index.html Static Client Privacy & Integrity > should contain masked natural persons and zero plaintext master unlock bypasses
(pass) Valuation Service Compliance and Provenance > should have removed misleading judicial/notarial certification claims from valuation_service.ts
(pass) Agency Velocity Inactivity and Date Reliability > should have removed fabricated 'Mars 2026' sale dates for agencies with 0 sales
(pass) Server Route Security and Prohibited Paths > should strictly disallow direct downloads of sensitive databases, env files, and source code

 18 pass
 0 fail
 59 expect() calls
Ran 18 tests across 1 files. [199.00ms]
```

---

## 2. Détail des Jeux d'Essai Synthétiques et Cas Limites

### Module 1 : Anonymisation des Personnes Physiques (nLPD)
| Cas d'Essai / Fixture | Type | Résultat Attendu | Résultat Obtenu | Statut |
|---|---|---|---|---|
| `UBS FUND MANAGEMENT (SWITZERLAND) AG` | Personne Morale | Inchangé | Inchangé | **PASS** |
| `IMMEUBLE RIVE GAUCHE SA` | Personne Morale | Inchangé | Inchangé | **PASS** |
| `SOCIETE IMMOBILIERE SAINT-JEAN SI` | Personne Morale | Inchangé | Inchangé | **PASS** |
| `COMMUNE DE COLLONGE-BELLERIVE` | Entité Publique | Inchangé | Inchangé | **PASS** |
| `CAISSE DE PREVOYANCE DU PERSONNEL` | Institution | Inchangé | Inchangé | **PASS** |
| `BERNARD IMMOBILIER SARL` | Personne Morale | Inchangé | Inchangé | **PASS** |
| `DUPONT Jean` | Personne Physique | `D*** J*** (Personne physique)` | `D*** J*** (Personne physique)` | **PASS** |
| `DE ROTHSCHILD Benjamin` | Particule nobiliaire | `R*** B*** (Personne physique)` | `R*** B*** (Personne physique)` | **PASS** |
| `M. et Mme MARTIN Pierre et Sophie` | Consorts / Époux | Anonymisation multi-parties | `M***, M*** M***, S*** (Personne physique)` | **PASS** |
| `MUELLER Hans, inscrit le 15.03.2023` | Mention registre foncier | Suppression du suffixe légal | `M*** H*** (Personne physique)` | **PASS** |
| `""` / `null` / `undefined` | Cas limite vide | `"Non précisé"` | `"Non précisé"` | **PASS** |

### Module 2 : Barème Légal CASATAX (Exercice 2026)
| Prix du Bien Testé | Seuil Légal (Plafond) | Éligibilité Théorique | Abattement Droits de Mutation (1.5%) | Statut |
|---|---|---|---|---|
| **CHF 1'300'000** | CHF 1'394'928 | Éligible (`true`) | CHF 19'500.00 | **PASS** |
| **CHF 1'394'928** (Borne exacte) | CHF 1'394'928 | Éligible (`true`) | CHF 20'923.92 (Plafond CHF 20'924) | **PASS** |
| **CHF 1'394'929** (Borne + 1 CHF) | CHF 1'394'928 | Non éligible (`false`) | CHF 0.00 | **PASS** |
| **CHF 1'450'000** | CHF 1'394'928 | Non éligible (`false`) | CHF 0.00 | **PASS** |

### Module 3 : Intégrité et Verrouillage de la Base SQLite `data/state/state.sqlite`
- **Tentative d'écriture SQL en mode `{ readonly: true }` :**  
  Requête : `CREATE TABLE IF NOT EXISTS test_fail (id INTEGER PRIMARY KEY)`  
  Résultat : Rejet immédiat avec exception levée (`SQLiteError: attempt to write a readonly database`). **PASS**
- **Comptage des Actes Authentiques de la Base de Référence :**  
  Nombre total de transactions : **8'970**.  
  Enregistrements de test résiduels : **0**. **PASS**
- **Volume Cantonal Cumulé (> 0 CHF) :**  
  Montant cumulé : **CHF 17'466'487'594.03** (compris dans l'intervalle cible de validation [17.4 Md - 17.5 Md CHF]). **PASS**
- **Vérification de la Non-Régression du Bug Décimal (Acte ID 4837) :**  
  Montant vérifié : **CHF 1'875'000.00** (strictement conforme, aucune régression à 1.88 CHF). **PASS**
- **Répartition Chronologique des Dates d'Avis Officielles :**  
  - 2023 : 91 actes  
  - 2024 : 1'325 actes  
  - 2025 : 4'375 actes  
  - 2026 : 3'179 actes  
  Total : **8'970 actes**. **PASS**
- **Référentiel des Ventes d'Agences :**  
  Agences analysées : **83**.  
  Ventes réconciliées : **2'183**. **PASS**

### Module 4 : Sécurité du Serveur HTTP & Protection des Fichiers Privés
| Route HTTP Testée | Règle de Filtrage | Code Statut HTTP | Résultat |
|---|---|---|---|
| `GET /data/state/state.sqlite` | `lowerPath.startsWith("data/state")` | **403 Forbidden** | **PASS** |
| `GET /.env` | `lowerPath.includes(".env")` | **403 Forbidden** | **PASS** |
| `GET /.git/config` | `lowerPath.startsWith(".git")` | **403 Forbidden** | **PASS** |
| `GET /package.json` | `lowerPath === "package.json"` | **403 Forbidden** | **PASS** |
| `GET /src/fao_transactions/server.py`| `lowerPath.endsWith(".py")` | **403 Forbidden** | **PASS** |
| `GET /data/exports/geneva_property_transactions.csv` | `lowerPath.endsWith(".csv")` | **403 Forbidden** | **PASS** |

### Module 5 : Intégrité du Client Web `index.html`
- Nombre d'occurrences d'anonymisation nLPD injectées dans le code source : **13'513**.
- Détection du mot de passe maître en clair (`Indice : cytria`, `cytria2026`) : **0 occurrence (complètement purgé)**.
- Remplacement du dialogue de mot de passe par le volet de conformité nLPD : **Vérifié et conforme**.
