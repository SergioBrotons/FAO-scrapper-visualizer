# Module 5 : Architecture d'Information & Roadmap Produit
## Plan de Fusion Unifié : Cadastre Officiel (FAO × SITG) & Intelligence Concurrentielle

---

## 🏛 1. Vision d'Architecture Unifiée (Master Architecture)

Actuellement, les deux briques technologiques sont structurées en deux répertoires complémentaires :
1. **`FAO-Scrapper-Visualizer`** : Moteur amont d'extraction légale (PDF de la FAO), géocodage cadastral officiel (SITG) et filtres d'opportunités foncières (Radar Hoiries & Développeurs).
2. **`Real-state-agencies-intelligence`** : Moteur aval de surveillance concurrentielle (83 agences, 93 courtiers), agrégation multi-portails en temps réel (Flatfox, Homegate, Immobilier.ch), déduplication spatiale et suivi des délistages/ventes présumées.

### L'Objectif de la Plateforme Unifiée :
Créer le premier **Système d'Exploitation Décisionnel Immobilier (Real Estate Intelligence OS)** dédié au canton de Genève, fusionnant la vérité officielle du sol (FAO/SITG) et la réalité commerciale des flux en ligne (Portails/Agences).

```
                               ┌─────────────────────────────────────────────────────────────┐
                               │                    DATA INGESTION LAYER                     │
                               └─────────────────────────────────────────────────────────────┘
                                        │                                       │
                    ┌───────────────────┴──────────────────┐                    │
                    ▼                                      ▼                    ▼
     [FAO & SITG OFFICIAL DATA]              [PUBLIC PORTALS STREAM]      [AGENCY ROSTER BASELINE]
    - FAO PDFs (LaCC art. 157 & LDTR)       - Flatfox REST API           - 83 Master Geneva Agencies
    - SITG Parcels & Cadastre               - SMG Homegate/ImmoScout     - 93 Verified Brokers
    - SITG PLQ & Planning Overlays          - Immobilier.ch Feeds        - Contact info & LinkedIn
                    │                                      │                    │
                    └───────────────────┬──────────────────┘                    │
                                        ▼                                       │
                               ┌────────────────────────────────────────────────▼┐
                               │       CROSS-REFERENCING & DEDUPLICATION CORE     │
                               │  - Spatial Fingerprinting (Haversine < 50m)     │
                               │  - Canonical Agency Mapping (Levenshtein)       │
                               │  - Status Transition Engine (Active -> Delisted)│
                               │  - Official Notary vs Portal Price Deviation    │
                               └─────────────────────────────────────────────────┘
                                                        │
                                                        ▼
                               ┌─────────────────────────────────────────────────┐
                               │         MASTER SQLITE / DUCKDB REPOSITORY       │
                               │  - unified_properties (Historical & Active)     │
                               │  - transactions_fao (8'700+ deeds)              │
                               │  - agencies_master & brokers_master             │
                               │  - coverage_matrix & territory_analytics        │
                               └─────────────────────────────────────────────────┘
                                                        │
                                                        ▼
                               ┌─────────────────────────────────────────────────┐
                               │            UNIFIED SWISS MODERN WEB UI          │
                               │  - Interactive Map (Leaflet + Swisstopo/Esri)   │
                               │  - 4 Operational Modes (Market/Mandate/Dev/Ag)  │
                               │  - Agency & Broker League Tables                │
                               │  - Multi-Portal Coverage Matrix                 │
                               │  - Live 'SCAN NOW' Trigger & PDF Export         │
                               └─────────────────────────────────────────────────┘
```

---

## 🗄 2. Schéma de Données Maître (Master Data Schema)

Pour fusionner les modèles des deux projets en un schéma unique et hautement performant :

### Table : `properties_master`
```sql
CREATE TABLE IF NOT EXISTS properties_master (
    fingerprint TEXT PRIMARY KEY,               -- Hash unique SHA256 (commune|type|surface|rooms|price|geo)
    parcel_number TEXT,                         -- Numéro de parcelle cadastrale SITG (ex: 2428)
    commune TEXT NOT NULL,                      -- Commune genevoise (ex: Cologny)
    address TEXT,                               -- Adresse postale normalisée
    lat REAL, lon REAL,                         -- Coordonnées WGS84
    lv95_e REAL, lv95_n REAL,                   -- Coordonnées suisses officielles MN95
    property_type TEXT,                         -- HOUSE | APARTMENT | BUILDING | LAND
    nature TEXT,                                -- Villa, attique, duplex, immeuble
    rooms REAL,
    living_surface_m2 REAL,
    land_surface_m2 REAL,
    
    -- Prix & Dynamique
    current_asking_price_chf REAL,              -- Dernier prix affiché sur portail
    initial_asking_price_chf REAL,              -- Premier prix observé
    price_change_pct REAL,                      -- Pourcentage de baisse/hausse
    fao_official_price_chf REAL,                -- Prix notarié réel enregistré à la FAO
    price_delta_pct REAL,                       -- Écart (%) entre prix demandé et prix notarié final
    
    -- Statut & Cycle de vie
    status TEXT,                                -- ACTIVE | PRICE_REDUCED | DELISTED_INFERRED_SOLD | FAO_CONFIRMED_SOLD
    first_seen TEXT,
    last_seen TEXT,
    days_on_market INTEGER,
    
    -- Attribution Commerciale
    primary_agency_id TEXT,                     -- Identifiant canonique (ex: barnes-suisse)
    primary_agency_name TEXT,
    primary_agent_name TEXT,
    portals_seen TEXT,                          -- Liste JSON des portails (ex: ["FLATFOX", "HOMEGATE"])
    is_incremental_active INTEGER,              -- 1 si nouveau mandat absent de RealAdvisor
    
    -- Urbanisme & Opportunités
    zone_code TEXT,                             -- Zone 1 à 5, Zone de développement
    is_hoirie INTEGER,                          -- 1 si succession / partage
    mandate_score INTEGER,                      -- Score d'opportunité vendeur (0-100)
    dev_score INTEGER,                          -- Score d'opportunité promoteur (0-100)
    dev_type TEXT,                              -- ZONE_5_DENSIFICATION | PLQ_DEVELOPMENT | PERMIT_ACTIVE
    plq_number TEXT,
    permit_number TEXT,
    
    data_json TEXT                              -- Payload JSON complet pour extensions futures
);
```

---

## 🎨 3. Expérience Utilisateur (UX) & Navigation Unifiée

L'application unifiée disposera d'une barre de navigation supérieure à deux niveaux :

### Niveau 1 : Le Mode Opérationnel (Filtrage Stratégique)
- **`MARKET (Marché)`** : Visualisation des prix réels notariés, cote au m² et tendances par commune.
- **`MANDATES (Prospection)`** : Radar des successions, hoiries et passoires thermiques à forte probabilité de vente.
- **`DEVELOPMENT (Foncier)`** : Radar des terrains divisibles en Zone 5, parcelles sous PLQ et permis de construire.
- **`COMPETITIVE (Concurrence)`** : Cartographie des 83 agences, parts de marché et rayons d'action.

### Niveau 2 : La Vue de Restitution
- **`CARTE (Map View)`** : Plein écran Leaflet avec couches activables (Swisstopo gris, Orthophoto satellite, Cadastre parcellaire, Marqueurs groupés).
- **`PALMARÈS (League Table)`** : Tableau de bord des agences et courtiers classés par Score Cytria.
- **`MATRICE (Coverage)`** : Tableau comparatif des portails (RealAdvisor vs Homegate/Flatfox).
- **`PIPELINE (Cards)`** : Grille de cartes détaillées avec historique de prix et boutons d'action.

---

## 🚀 4. Roadmap de Développement en 4 Phases

### Phase 1 : Consolidation & Synchronisation des Données (Actuelle)
- [x] Compilation du cadastre de 83 agences genevoises et 93 courtiers d'élite.
- [x] Ingestion en temps réel via l'API Flatfox sans blocage anti-bot.
- [x] Algorithme de réconciliation historique (préservation des biens délistés et détection des baisses de prix).
- [x] Bouton interactif "SCAN NOW / ACTUALISER" avec notification toast.

### Phase 2 : Fusion Cartographique & Moteur Spatial Unique (Mois 1)
- [ ] Réunir le visualisateur Leaflet de `FAO-Scrapper-Visualizer` et le moteur d'agences dans une unique base de code.
- [ ] Permettre d'afficher simultanément sur la même carte :
  1. Les cercles territoriaux des agences concurrentes.
  2. Les mandats portails actifs avec badge d'agence.
  3. Les parcelles notariées de la FAO avec prix certifiés.
- [ ] Clic sur une agence $\rightarrow$ filtre instantanément tous ses mandats actifs et ses ventes notariées passées sur la carte.

### Phase 3 : Notifications Automatisées & Intégration CRM (Mois 2)
- [ ] Mettre en place un webhook d'alerte quotidienne (Telegram / Slack / Email) dès qu'une publication FAO obtient un `mandate_score >= 85` (Succession d'une villa en Zone 5).
- [ ] Connecteur d'export en 1 clic vers les CRM immobiliers suisses :
  - **OnOffice**
  - **Fluxaro**
  - **HubSpot Real Estate**
- [ ] Générateur automatique de dossiers PDF d'estimation préalable au format corporate de l'agence.

### Phase 4 : Calculateur Automatisé de Valeur Résiduelle Foncière (Mois 3)
- [ ] Module intégré permettant au courtier de cliquer sur n'importe quelle parcelle en Zone 5 pour calculer automatiquement :
  $$\text{Valeur Résiduelle du Sol} = \text{Chiffre d'Affaires Prévisionnel du Projet} - (\text{Coûts de Construction CFC 2} + \text{Frais Financiers} + \text{Marge Promoteur 15\%})$$
- [ ] Permet au courtier d'arriver devant le promoteur avec le bilan financier complet de l'opération pré-chiffré.
