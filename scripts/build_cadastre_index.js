import { Database } from 'bun:sqlite';
import { mkdirSync } from 'fs';

const db = new Database('data/state/state.sqlite', { readonly: true });
const rows = db.query(`
  SELECT 
    t.id,
    t.address,
    t.commune,
    t.parcel_number,
    t.property_type,
    t.nature,
    t.rooms,
    t.floor,
    t.unit_number,
    t.building_year,
    COALESCE(t.surface_m2, e.surface_official_m2) as surface,
    e.heating_system,
    e.egrid,
    COALESCE(e.zone_name, t.zone_name, 'Zone 5') as zone
  FROM transactions t
  LEFT JOIN enrichments e ON t.id = e.transaction_id
  WHERE t.address IS NOT NULL AND length(trim(t.address)) > 3
  GROUP BY t.address, t.commune
  ORDER BY t.notice_date DESC
`).all();

console.log('Total unique Geneva addresses:', rows.length);
mkdirSync('public/dv/data', { recursive: true });
await Bun.write('public/dv/data/geneva_cadastre_index.json', JSON.stringify(rows));
console.log('Saved to public/dv/data/geneva_cadastre_index.json');
db.close();
