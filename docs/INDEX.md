# CYTRIA Geneva Real Estate Business Intelligence Suite
## Le Système d'Intelligence Foncière & Immobilière de Référence (FAO × SITG × Portails)

---

## 🎯 Vision & Proposition de Valeur pour une Agence Immobilière

À Genève, le marché immobilier est l'un des plus fermés, opaques et réglementés au monde. Les grandes régies historiques (Comptoir Immobilier, Naef, Brolliet, Gerofinance, Moser Vernet) détiennent des décennies d'antériorité et des parcs sous gestion qui leur apportent un flux naturel de mandats.

Pour une **agence boutique, un courtier indépendant ou une structure en développement**, attendre que les vendeurs appellent ou se contenter de scraper des annonces publiques déjà en ligne est une stratégie vouée à l'échec : lorsqu'un bien apparaît sur Homegate ou ImmoScout24, le mandat est **déjà signé**, les honoraires sont attribués, et le courtier arrive trop tard.

Le système **CYTRIA (FAO × SITG)** renverse cette asymétrie d'information :
1. **Découverte Amont (Pré-mandat)** : Détecte les successions (*hoiries*), partages et mutations légales des semaines avant que le bien n'arrive sur le marché.
2. **Radar Développeurs & Terrains** : Identifie les réserves foncières et les parcelles en Zone 5 avec potentiel de densification ou sous PLQ pour apporter des opérations clés en main à des promoteurs.
3. **Vérité des Prix Notariés** : S'appuie sur les prix déclarés au Registre Foncier (art. 157 LaCC) et sous LDTR (art. 39) plutôt que sur les prix d'affichage sur-évalués des portails.
4. **Cartographie Concurrentielle** : Mesure l'emprise territoriale des agences concurrentes pour conquérir les micro-marchés délaissés.

---

## 📚 Sommaire de la Suite Documentaire

Cette documentation est organisée en 5 modules stratégiques et opérationnels, conçus pour servir de manuel d'utilisation, de base de connaissances métier et de cadre d'architecture logicielle :

```
docs/FAO_BI_GUIDE/
├── INDEX.md                                  # Le présent document d'orientation
├── 01_HOW_TO_AGENCY_BI_MANUAL.md             # Guide pratique des workflows de prospection et de courtage
├── 02_GENEVA_CADASTRE_LEGAL_GLOSSARY.md      # Dictionnaire exhaustif juridique, cadastral & foncier genevois
├── 03_FACTORS_AND_METRICS_ANALYSIS_GUIDE.md  # Analyse détaillée de chaque facteur de donnée et son impact métier
├── 04_STRATEGIC_PLAYBOOK_SCRIPTS_FAQ.md      # Scripts de prise de contact, conformité suisse LPD et FAQ
└── 05_INFORMATION_ARCHITECTURE_ROADMAP.md    # Architecture d'information, schéma de données et roadmap produit
```

---

## 🗺 Résumé des 5 Modules

### 1. [01_HOW_TO_AGENCY_BI_MANUAL.md](file:///c:/Users/AI-Mini-PC/DEV/Real-state-agencies-intelligence/docs/FAO_BI_GUIDE/01_HOW_TO_AGENCY_BI_MANUAL.md)
*Le manuel opérationnel du courtier.*
- **Workflow 1 : La Chasse aux Mandats Successoraux (Radar Hoiries)** — Comment identifier les héritiers et décrocher l'exclusivité avant la mise en vente.
- **Workflow 2 : L'Assemblage Foncier & Surcharge Promoteur (Radar Zone 5 & PLQ)** — Calculer la valeur résiduelle du sol et monter des tours de table promoteurs.
- **Workflow 3 : L'Avis de Valeur Imparable (Calibration Prix Notariés)** — Désarmer les prétentions irréalistes des vendeurs grâce aux statistiques officielles du Registre Foncier.
- **Workflow 4 : Le Farming Territorial Intelligent** — Quadriller un quartier (Cologny, Conches, Florissant) et anticiper les rotations de propriétaires.
- **Workflow 5 : Veille Concurrentielle & Angles Morts** — Analyser la part de marché des 80 agences genevoises et identifier les faiblesses des concurrents.

### 2. [02_GENEVA_CADASTRE_LEGAL_GLOSSARY.md](file:///c:/Users/AI-Mini-PC/DEV/Real-state-agencies-intelligence/docs/FAO_BI_GUIDE/02_GENEVA_CADASTRE_LEGAL_GLOSSARY.md)
*Le glossaire de référence du droit et du cadastre genevois.*
- **Organismes & Sources** : FAO, Registre Foncier, Notariat latin, SITG, DALE / OAC, DDP, PPE.
- **Lois Cantonales Spécifiques** : LDTR (art. 39 et aliénation), LaCC (art. 157), LGZD (Zones de développement), LDFR (Droit foncier rural), LCI (Constructions).
- **Zonage & Aménagement** : Zones 1 à 5, Zone foraine agricole, PLQ (Plan Localisé de Quartier), Dénonciation / Droit de préemption communal et cantonal.
- **Systèmes de Coordonnées** : LV95 (MN95 / CH1903+) vs WGS84, EGRID fédéral.

### 3. [03_FACTORS_AND_METRICS_ANALYSIS_GUIDE.md](file:///c:/Users/AI-Mini-PC/DEV/Real-state-agencies-intelligence/docs/FAO_BI_GUIDE/03_FACTORS_AND_METRICS_ANALYSIS_GUIDE.md)
*Le décryptage de chaque facteur de donnée et sa rentabilité pour l'agence.*
- Analyse systématique de plus de 45 colonnes de données (Avis FAO, Registre foncier, Enrichissement cadastral SITG, Overlays d'urbanisme, Algorithmes de scoring).
- Pour chaque donnée : **Origine technique**, **Méthode d'extraction**, et surtout **Signification Commerciale & Cas d'Usage pour l'Agence**.

### 4. [04_STRATEGIC_PLAYBOOK_SCRIPTS_FAQ.md](file:///c:/Users/AI-Mini-PC/DEV/Real-state-agencies-intelligence/docs/FAO_BI_GUIDE/04_STRATEGIC_PLAYBOOK_SCRIPTS_FAQ.md)
*Boîte à outils de conversion, conformité juridique et FAQ.*
- **Scripts d'approche** : Courriers et appels téléphoniques sur-mesure pour hoiries, propriétaires en zone de densification et copropriétaires PPE.
- **Cadre Légal Suisse** : Respect de la nouvelle Loi fédérale sur la protection des données (nLPD), légitimité de consultation du Registre Foncier public.
- **FAQ Métier** : Plus de 20 questions/réponses concrètes sur les limites, les pièges à éviter et l'exploitation quotidienne de l'outil.

### 5. [05_INFORMATION_ARCHITECTURE_ROADMAP.md](file:///c:/Users/AI-Mini-PC/DEV/Real-state-agencies-intelligence/docs/FAO_BI_GUIDE/05_INFORMATION_ARCHITECTURE_ROADMAP.md)
*Cadre d'évolution logicielle et architecture d'information.*
- Comment fusionner `FAO-Scrapper-Visualizer` et `Real-state-agencies-intelligence` en une plateforme unique unifiée.
- Modèle de données maître, architecture multi-couches, UX mobile pour courtiers en déplacement et intégration CRM (OnOffice, Fluxaro, Hubspot).
