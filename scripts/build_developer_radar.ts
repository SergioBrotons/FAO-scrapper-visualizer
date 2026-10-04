import { Database } from "bun:sqlite";
import { join } from "path";
import { existsSync } from "fs";

const DB_PATH = join(process.cwd(), "data/state/state.sqlite");
if (!existsSync(DB_PATH)) {
  console.error("Database state.sqlite not found.");
  process.exit(1);
}

const db = new Database(DB_PATH);
db.exec("PRAGMA foreign_keys = ON;");
db.exec("PRAGMA journal_mode = WAL;");

console.log("----------------------------------------------------------------");
console.log("   RADAR DÉVELOPPEURS & DROITS À BÂTIR (ZONE 5 & PLQ GENÈVE)   ");
console.log("----------------------------------------------------------------\n");

// 1. Initialize Developer Intelligence Table
db.exec(`
  CREATE TABLE IF NOT EXISTS developer_intelligence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER,
    commune TEXT NOT NULL,
    parcel_number TEXT,
    egrid TEXT,
    surface_m2 REAL,
    zone_code TEXT,
    zone_name TEXT,
    has_plq INTEGER DEFAULT 0,
    ius_standard REAL DEFAULT 0.20,
    ius_densified REAL DEFAULT 0.40,
    max_buildable_floor_area_m2 REAL,
    residual_rights_m2 REAL,
    estimated_exit_price_m2 REAL,
    gross_developer_potential_chf REAL,
    is_hoirie INTEGER DEFAULT 0,
    priority_score REAL DEFAULT 50.0,
    centroid_lat REAL,
    centroid_lon REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );

  CREATE INDEX IF NOT EXISTS idx_dev_commune ON developer_intelligence(commune);
  CREATE INDEX IF NOT EXISTS idx_dev_zone ON developer_intelligence(zone_code);
  CREATE INDEX IF NOT EXISTS idx_dev_hoirie ON developer_intelligence(is_hoirie);
  CREATE INDEX IF NOT EXISTS idx_dev_score ON developer_intelligence(priority_score);
`);

console.log("1. Initialized table 'developer_intelligence'.");

// 2. Preload OCSTAT benchmark map
const communalMap = new Map<string, any>();
const allCommunes = db.query("SELECT * FROM ocstat_communal_benchmarks").all() as any[];
for (const c of allCommunes) {
  communalMap.set(c.commune.toLowerCase().trim(), c);
}

// 3. Query candidates for densification
// Target: Parcels with zone_code = '5' (or residential) with surface >= 700 m2
const query = `
  SELECT 
    t.id as transaction_id, t.commune, t.parcel_number, t.surface_m2 as t_surface,
    e.surface_official_m2, e.zone_code, e.zone_name, e.egrid, e.extrait_rdppf_url,
    e.centroid_wgs84_lat, e.centroid_wgs84_lon,
    fi.is_hoirie, fi.price_chf
  FROM transactions t
  LEFT JOIN enrichments e ON t.id = e.transaction_id
  LEFT JOIN financial_intelligence fi ON t.id = fi.transaction_id
  WHERE (e.zone_code = '5' OR e.zone_name LIKE '%villa%' OR e.zone_name LIKE '%développement%' OR e.zone_code IS NULL)
    AND (COALESCE(e.surface_official_m2, t.surface_m2, 0) >= 700)
`;

const candidates = db.query(query).all() as any[];
console.log(`2. Found ${candidates.length} candidate parcels for land development analysis.`);

db.exec("DELETE FROM developer_intelligence;");

const insertDevStmt = db.prepare(`
  INSERT INTO developer_intelligence (
    transaction_id, commune, parcel_number, egrid, surface_m2,
    zone_code, zone_name, has_plq, ius_standard, ius_densified,
    max_buildable_floor_area_m2, residual_rights_m2, estimated_exit_price_m2,
    gross_developer_potential_chf, is_hoirie, priority_score,
    centroid_lat, centroid_lon, created_at
  ) VALUES (
    $transaction_id, $commune, $parcel_number, $egrid, $surface_m2,
    $zone_code, $zone_name, $has_plq, $ius_standard, $ius_densified,
    $max_buildable_floor_area_m2, $residual_rights_m2, $estimated_exit_price_m2,
    $gross_developer_potential_chf, $is_hoirie, $priority_score,
    $centroid_lat, $centroid_lon, CURRENT_TIMESTAMP
  );
`);

let devOpportunitiesCount = 0;
let topPriorityCount = 0;

const runDevIngestion = db.transaction((rows: any[]) => {
  for (const row of rows) {
    const surface = row.surface_official_m2 || row.t_surface || 0;
    if (surface < 700) continue;

    const communeKey = (row.commune || "").toLowerCase().trim();
    const ocstat = communalMap.get(communeKey) || communalMap.get("genève");

    // Standard Zone 5 rules:
    // Standard IUS = 0.20
    // Densified IUS under art. 59 al. 4 LCI (Habitat groupé / PPE) = 0.40
    const iusStd = 0.20;
    const iusDensified = 0.40;

    const standardBuildableM2 = Math.round(surface * iusStd);
    const maxBuildableM2 = Math.round(surface * iusDensified);
    const residualRightsM2 = maxBuildableM2 - standardBuildableM2;

    const exitPriceM2 = ocstat?.prix_median_m2_ppe || 13500;
    const grossPotentialChf = Math.round(maxBuildableM2 * exitPriceM2);

    const hasPlq = (row.extrait_rdppf_url && row.extrait_rdppf_url.includes("plq")) ? 1 : 0;
    const isHoirie = row.is_hoirie === 1 ? 1 : 0;

    // Developer Priority Scoring (0 - 100):
    // + 30 pts for Hoirie / Succession (active sale propensity)
    // + 25 pts for Surface >= 1500 m2 (ideal size for promoter project)
    // + 20 pts for High OCSTAT commune (> 14'000 CHF/m2)
    // + 15 pts for PLQ presence
    // + 10 pts for Surface >= 2500 m2
    let score = 30.0;
    if (isHoirie) score += 30.0;
    if (surface >= 1500) score += 20.0;
    if (surface >= 2500) score += 10.0;
    if (exitPriceM2 >= 14000) score += 15.0;
    if (hasPlq) score += 15.0;
    score = Math.min(score, 100.0);

    if (score >= 70.0) topPriorityCount++;
    devOpportunitiesCount++;

    insertDevStmt.run({
      $transaction_id: row.transaction_id,
      $commune: row.commune,
      $parcel_number: row.parcel_number,
      $egrid: row.egrid,
      $surface_m2: surface,
      $zone_code: row.zone_code || "5",
      $zone_name: row.zone_name || "Zone 5 (Villas)",
      $has_plq: hasPlq,
      $ius_standard: iusStd,
      $ius_densified: iusDensified,
      $max_buildable_floor_area_m2: maxBuildableM2,
      $residual_rights_m2: residualRightsM2,
      $estimated_exit_price_m2: exitPriceM2,
      $gross_developer_potential_chf: grossPotentialChf,
      $is_hoirie: isHoirie,
      $priority_score: score,
      $centroid_lat: row.centroid_wgs84_lat,
      $centroid_lon: row.centroid_wgs84_lon,
    });
  }
});

runDevIngestion(candidates);

console.log(`3. Evaluated & Ingested ${devOpportunitiesCount} development parcels.`);
console.log(`   - Top Priority Opportunities (Score >= 70) : ${topPriorityCount}`);

const top5 = db.query(`
  SELECT 
    commune, parcel_number, surface_m2, residual_rights_m2,
    estimated_exit_price_m2, gross_developer_potential_chf,
    is_hoirie, priority_score
  FROM developer_intelligence
  ORDER BY priority_score DESC, surface_m2 DESC
  LIMIT 5
`).all();

console.log("\n4. Top 5 Developer Opportunities:");
console.table(top5);

db.close();
console.log("\n[OK] Developer Radar Engine successfully executed!\n");
