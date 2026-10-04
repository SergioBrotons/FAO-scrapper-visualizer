# Cytria — Agency Head-to-Head & Live Portfolio Intelligence Engine
## Architectural Design, Data Engineering & Implementation Plan

---

### Executive Summary

To elevate Cytria from a transaction visualizer into a **Market Intelligence & Competitive Reconnaissance Platform**, we propose a two-pillar expansion:

1. **Module A — Agency Duel (Head-to-Head Benchmarking & Turf Overlap)**:
   - Side-by-side comparative UI allowing the user to select **Agency A (Cyan)** vs **Agency B (Gold)**.
   - Dual-radius spatial overlays, territorial market share heatmaps, velocity (Days-to-Deed), and market conquest indicators.
2. **Module B — Live Active Listings & Multi-Mandate Collision Engine**:
   - Continuous ingestion of active market listings (Immobilier.ch, Homegate, ImmoScout24, Agency websites).
   - **Multi-Agency Mandate Collision Detection**: Algorithmic deduplication to identify when the **exact same property** is marketed concurrently by multiple competing agencies.
   - **Price War & Spread Tracking**: Highlighting price discrepancies (e.g., Agency A listing at CHF 3.4M while Agency B lists at CHF 3.15M) and tracking price cuts over time.

---

## 1. Feature 1: Agency Head-to-Head Benchmark ("Agency Duel")

### 1.1 Visual & Spatial Experience
- **Dual Selector in Top Navigation Bar**:
  - Primary Agency (e.g., *BARNES Suisse*) [Accent: Cyan `#06b6d4`]
  - Benchmark Competitor (e.g., *Cardis Sotheby's*) [Accent: Gold `#f59e0b`]
- **Map Dual Layer**:
  - **Color-Coded Markers**: Cyan dots (Agency A) vs Gold dots (Agency B).
  - **Shared Turf Halo (Intersection)**: A highlighted spatial polygon/circle where both agencies compete directly.
  - **Territory Invasion Indicators**: Highlighting when Agency A sells a property within Agency B's historical core stronghold.

### 1.2 Comparative KPI Scorecard (Side-by-Side Modal / Split Drawer)

| Metric | Agency A (e.g., BARNES) | Agency B (e.g., Cardis) | Advantage / Delta |
| :--- | :---: | :---: | :---: |
| **Total 24M Volume** | CHF 210.0 Mio | CHF 185.0 Mio | **+13.5% (Agency A)** |
| **Total Deals Closed** | 52 sales | 45 sales | **+7 deals (Agency A)** |
| **Median House Price** | CHF 6.80 Mio | CHF 7.50 Mio | **+10.3% (Agency B - Ultra Luxury)** |
| **Median Apt / PPE Price** | CHF 2.30 Mio | CHF 2.40 Mio | **+4.3% (Agency B)** |
| **Velocity (DOM to Notary)** | 114 days | 98 days | **+16 days faster (Agency B)** |
| **Avg. Negotiation Spread** | -5.8% | -4.2% | **Agency B holds price firmer** |
| **Dominant Core Commune** | Cologny (28% share) | Cologny (22% share) | **Agency A leads by 6%** |
| **Turf Overlap Index** | **64.2% Geographic Overlap** | | High Direct Rivalry |

---

## 2. Feature 2: Live Active Listings & Multi-Mandate Collision Engine

### 2.1 The Market Opportunity
In Geneva's high-value residential market, sellers frequently grant **simple (non-exclusive) mandates** to 2, 3, or even 4 agencies simultaneously, or switch agencies after 6 months of stagnation.

This engine uncovers:
1. **Multi-Agency Mandates**: The same villa marketed by Naef, SPG, and Barnes at the same time.
2. **Price Asymmetry**: Agency A advertising at CHF 4'200'000 while Agency B dropped it to CHF 3'950'000 (creating massive leverage for buyers and revealing seller urgency).
3. **Ghost Listings**: Properties marked as "Active" on an agency site that were already legally sold at the Land Registry 3 months ago.

### 2.2 Matching & Deduplication Algorithm (Collision Engine)

Because Swiss portals hide exact parcel numbers and street numbers on luxury villas, the algorithm performs **Multi-Factor Fingerprinting**:

```python
def compute_listing_fingerprint(listing):
    """
    Generate deterministic & fuzzy hash for multi-agency collision detection.
    """
    return {
        "commune_norm": normalize_commune(listing["commune"]),
        "typology": listing["typology"],  # VILLA | PPE | TERRAIN
        "rooms_bucket": round(float(listing.get("rooms", 0)) * 2) / 2,  # 7.5 rooms
        "surface_bucket": round(float(listing.get("surface_habitable_m2", 0)) / 10) * 10, # ~320m2
        "land_bucket": round(float(listing.get("surface_terrain_m2", 0)) / 50) * 50, # ~1500m2
        "geo_cluster": geohash_encode(listing["lat"], listing["lon"], precision=6)
    }
```

---

## 3. Database Schema Extensions (`state.sqlite`)

### 3.1 New Table: `active_listings`
```sql
CREATE TABLE IF NOT EXISTS active_listings (
    id TEXT PRIMARY KEY,               -- e.g. "immob_129481" or "homeg_84920"
    portal_source TEXT NOT NULL,       -- "immobilier.ch", "homegate", "agency_direct"
    agency_id TEXT REFERENCES agencies(id),
    agency_raw_name TEXT,
    broker_name TEXT,
    title TEXT,
    address_display TEXT,
    commune TEXT NOT NULL,
    lat REAL,
    lon REAL,
    typology TEXT NOT NULL,            -- "PPE", "VILLA", "IMMEUBLE", "TERRAIN"
    rooms REAL,
    surface_habitable_m2 REAL,
    surface_terrain_m2 REAL,
    price_asking_chf REAL,
    initial_price_chf REAL,
    price_drops_count INTEGER DEFAULT 0,
    first_seen_date TEXT NOT NULL,
    last_seen_date TEXT NOT NULL,
    days_on_market INTEGER,
    status TEXT DEFAULT 'ACTIVE',       -- 'ACTIVE', 'PRICE_REDUCED', 'UNDER_OFFER', 'SOLD'
    matched_collision_id TEXT,         -- Foreign key to active_market_collisions
    matched_fao_id INTEGER REFERENCES transactions(id)
);
```

### 3.2 New Table: `active_market_collisions` (Multi-Mandate Tracking)
```sql
CREATE TABLE IF NOT EXISTS active_market_collisions (
    collision_id TEXT PRIMARY KEY,
    commune TEXT NOT NULL,
    typology TEXT NOT NULL,
    estimated_address TEXT,
    agency_count INTEGER NOT NULL,      -- e.g. 3 agencies marketing the same property
    agencies_involved JSON NOT NULL,    -- ["barnes-suisse", "cardis-sothebys", "spg-one"]
    min_price_chf REAL NOT NULL,
    max_price_chf REAL NOT NULL,
    price_spread_chf REAL NOT NULL,     -- e.g. CHF 250'000
    price_spread_pct REAL NOT NULL,     -- e.g. 7.14%
    listings_json JSON NOT NULL,
    detected_at TEXT NOT NULL
);
```

---

## 4. Implementation Phasing & Roadmap

### Phase 1: Dual Agency Head-to-Head UI (1–2 Days)
- Add **"VS Compare Competitor"** selector in HUD and Agency Drawer.
- Dual-color map overlays (Agency A: Cyan, Agency B: Amber).
- Render **Agency Duel Scorecard** with turf conquest metrics.

### Phase 2: Portal Scraper & Active Listings Pipeline (3–5 Days)
- Build portal connectors for Geneva active market listings (`src/fao_transactions/collector/portal_crawler.py`).
- Daily ingestion of active listings with commune-level geocoding and price history.

### Phase 3: Multi-Mandate Collision & Price Spread Engine (2–3 Days)
- Deploy fuzzy fingerprint matcher (`src/fao_transactions/intelligence/collision_engine.py`).
- Add **"Multi-Mandates & Price Wars"** radar tab to the visualizer.
- Cross-reference active listings with closed FAO deeds for empirical discount analysis.
