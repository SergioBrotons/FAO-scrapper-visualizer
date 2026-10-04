# Module d'Intelligence Foncière Dédié : Désormière & Vanhalst

**Destinataires :** Sandra Bleeckx Vanhalst & Adrien Désormière  
**Agence :** Désormière & Vanhalst — Rive Gauche Genève  
**Territoire d'Observation :** Troinex, Veyrier, Chêne-Bougeries, Plan-les-Ouates, Cologny, Vandœuvres, Collonge-Bellerive, Thônex, Chêne-Bourg  
**URL d'Accès :** `http://localhost:8088/dv` (ou `http://localhost:8088/desormiere-vanhalst`)  
**Statut Technique :** Isolé, non-intrusif (« Separated but Not Breaking »), 100% conforme à la charte graphique officielle.

---

## 1. Respect Strict du Brandbook Officiel

Le portail et les dossiers d'estimation ont été construits en respectant scrupuleusement la charte graphique extraite de `docs/brandbook d&v/Charte_graphique_DV (2).docx` :

- **Couleur Principale :** `#00939D` (Turquoise DV • RGB 0 · 147 · 157 | Pantone #3541c) — Utilisée pour les boutons principaux, les badges d'opportunité et les puces actives.
- **Couleur Secondaire Prestige :** `#004A4F` (Vert Profond • RGB 0 · 74 · 79) — Couleur de référence de la gamme *« DV Signature »*, bandeau d'en-tête et badges de priorité haute.
- **Accent au Survol :** `#17DAE8` (Turquoise Lumineux • RGB 23 · 218 · 232) — Utilisé pour le survol dynamique des boutons et les indicateurs interactifs.
- **Fond de Page & Surfaces :** `#F6F3F3` (Sable chaud) avec cartes blanches contrastées `#FFFFFF` pour une ergonomie claire, luxueuse et familière.
- **Typographie :**
  - Titres et élégance éditoriale : *Cormorant Garamond* (Georgia / Serif).
  - Données et interface : *Plus Jakarta Sans* (moderne, aérée et ultra-lisible).
- **Logos Intégrés :** Emploi des fichiers officiels situés dans `public/dv/assets/` (`DandV Logo right text clear.png`, `DV logo rond signature.png`, etc.).

---

## 2. Détection de Signaux & Scoring d'Opportunités

Le service `src/fao_transactions/dv/dv_service.ts` interroge la base foncière genevoise (`data/state/state.sqlite` en lecture seule stricte) et calcule un **Score d'Urgence Foncière (0-99)** combinant 4 signaux objectifs :

1. **Signal Hoirie / Succession (+35 pts) :**  
   Détection des indivisions successorales (art. 602 al. 2 CC) dans les avis officiels du Registre Foncier (héritages, dévolutions entre plusieurs cohéritiers). Dès 18 à 24 mois sans arbitrage, la nécessité de partage financier ou le risque d'action en partage (art. 604 CC) active une forte propension à la vente.
2. **Signal Division Parcellaire / Développeur (+25 pts) :**  
   Détection des parcelles surdimensionnées ($\ge 950\text{ m}^2$) situées en **Zone 5 (Villas)** bénéficiant d'un potentiel de surdensification, de détachement de parcelle ou de construction d'une seconde villa (IUS standard 0.20 pouvant atteindre 0.40).
3. **Signal Détention Longue / Vintage (+15 pts) :**  
   Propriétés acquises il y a plus de 20 ans par des propriétaires historiques, garantissant une exonération substantielle de l'impôt sur les gains immobiliers (LIPP art. 82) et une probabilité de changement de cycle de vie (enfants ayant quitté le foyer / downsizing).
4. **Signal Prestige DV Signature (+15 pts) :**  
   Biens situés à Cologny, Vandœuvres ou Collonge-Bellerive, ou transactions excédant 3 millions de CHF.

### Répartition des Rôles (Personas)
- **Sandra Bleeckx Vanhalst :** Spécialiste Villas & Hoiries familiales. Angle d'approche axé sur l'accompagnement humain, discret et l'estimation officielle pour faciliter l'entente successorale.
- **Adrien Désormière :** Spécialiste Villas Haut de Gamme, Terrains et Développements. Angle d'approche axé sur l'étude de faisabilité foncière, le détachement de parcelle et la vente de gré à gré à un promoteur.

---

## 3. Fonctionnalités Prêtes à l'Emploi

1. **Le Feed d'Opportunités (Notion / CRM Luxury) :**
   - Cartes récapitulatives avec adresse, commune, numéro de parcelle officiel, surface, affectation de zone et propriétaires cédants/acquéreurs anonymisés (conformité nLPD).
   - Angle d'approche pré-rédigé pour chaque opportunité.
2. **Action 1-Clic « Fiche Mandat CMA » :**
   - Ouvre une fiche synthétique au format A4/Web aux couleurs D&V (`/api/dv/cma?id=...`).
   - Intègre les 3 transactions comparables récentes de la même commune, la médiane au m² OCSTAT et la fourchette recommandée (P25 - Médiane - P75). Bouton d'impression instantanée pour rendez-vous vendeur.
3. **Action 1-Clic « Cadastre SITG » :**
   - Lien direct vers le guichet cartographique officiel du SITG pour visualiser les limites de parcelles et les plans de zones.
4. **Action 1-Clic « Copier l'Angle d'Approche » :**
   - Copie instantanée dans le presse-papier d'un texte prêt à l'envoi pour prise de contact téléphonique ou courrier adressé.

---

## 4. Points d'Accès API et Architecture

| Endpoint | Méthode | Rôle |
|---|---|---|
| `/dv` ou `/desormiere-vanhalst` | `GET` | Interface utilisateur principale Désormière & Vanhalst. |
| `/api/dv/opportunities` | `GET` | Renvoie la liste JSON filtrée (`?commune=Troinex&signal=hoirie&limit=50`) avec KPIs. |
| `/api/dv/cma?id=16945` | `GET` | Génère la fiche CMA imprimable aux couleurs D&V. |
| `/public/dv/assets/*` | `GET` | Logos et assets de marque protégés. |

---

## 5. Validation Automatisée

La suite de tests `tests/test_dv_intelligence.test.ts` confirme le fonctionnement :
- **8 tests unitaires dédiés**, 100% passés en 434 ms.
- Aucune régression sur le visualiseur cantonal Cytria (`tests/test_surgical_hardening.test.ts` : 18/18 passés).
- Base SQLite `state.sqlite` intacte (strictement 0 écriture).
