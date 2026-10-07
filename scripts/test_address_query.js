import { Database } from 'bun:sqlite';
const db = new Database('data/state/state.sqlite', { readonly: true });
const results = db.query(`
  SELECT 
    t.id, t.address, t.commune, t.parcel_number, t.property_type, t.nature,
    t.rooms, t.floor, t.unit_number, t.surface_m2, t.price_chf,
    t.zone_code, t.zone_name, t.building_year,
    e.heating_system, e.surface_official_m2, e.lien_extrait_rf, e.egrid
  FROM transactions t
  LEFT JOIN enrichments e ON t.id = e.transaction_id
  WHERE t.address IS NOT NULL AND length(t.address) > 3
  ORDER BY t.id DESC
  LIMIT 5
`).all();
console.log('Sample Matches:', JSON.stringify(results, null, 2));
db.close();
