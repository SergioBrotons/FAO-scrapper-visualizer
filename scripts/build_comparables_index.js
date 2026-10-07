import { Database } from 'bun:sqlite';

const db = new Database('data/state/state.sqlite', { readonly: true });
const comps = db.query(`
  SELECT 
    t.id,
    t.address,
    t.commune,
    t.notice_date as raw_date,
    t.parcel_number,
    COALESCE(t.surface_m2, e.surface_official_m2, 85) as surface,
    t.price_chf as price,
    ROUND(t.price_chf / COALESCE(t.surface_m2, e.surface_official_m2, 85)) as price_m2,
    t.property_type,
    t.nature,
    e.egrid
  FROM transactions t
  LEFT JOIN enrichments e ON t.id = e.transaction_id
  WHERE t.address IS NOT NULL 
    AND t.price_chf > 200000
    AND length(trim(t.address)) > 3
  ORDER BY t.notice_date DESC
  LIMIT 500
`).all();

console.log('Total recent comparables indexed:', comps.length);
await Bun.write('public/dv/data/geneva_recent_comparables.json', JSON.stringify(comps));
console.log('Saved to public/dv/data/geneva_recent_comparables.json');
db.close();
