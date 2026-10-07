import { Database } from 'bun:sqlite';
import { existsSync } from 'fs';

const DB_PATH = 'data/state/state.sqlite';
const db = new Database(DB_PATH, { readonly: true });

function searchAddresses(q) {
  const cleanQ = q.trim();
  const term = `%${cleanQ}%`;
  const startTerm = `${cleanQ}%`;
  const sql = `
    SELECT 
      t.id,
      t.address,
      t.commune,
      t.parcel_number,
      t.property_type,
      t.nature,
      t.building_year,
      t.rooms,
      COALESCE(t.surface_m2, e.surface_official_m2) as surface_m2,
      e.egrid,
      e.heating_system,
      e.zone_name
    FROM transactions t
    LEFT JOIN enrichments e ON t.id = e.transaction_id
    WHERE t.address IS NOT NULL 
      AND (
        t.address LIKE ? 
        OR t.parcel_number LIKE ? 
        OR t.commune LIKE ?
      )
    GROUP BY t.address, t.commune
    ORDER BY 
      CASE WHEN t.address LIKE ? THEN 1 ELSE 2 END,
      t.notice_date DESC
    LIMIT 12;
  `;
  return db.query(sql).all(term, term, term, startTerm);
}

function lookupCadastre(id, address) {
  let row = null;
  if (id) {
    row = db.query(`
      SELECT t.*, e.heating_system, e.surface_official_m2, e.lien_extrait_rf, e.egrid, e.zone_name as sitg_zone
      FROM transactions t
      LEFT JOIN enrichments e ON t.id = e.transaction_id
      WHERE t.id = ?
    `).get(id);
  } else if (address) {
    row = db.query(`
      SELECT t.*, e.heating_system, e.surface_official_m2, e.lien_extrait_rf, e.egrid, e.zone_name as sitg_zone
      FROM transactions t
      LEFT JOIN enrichments e ON t.id = e.transaction_id
      WHERE t.address LIKE ?
      ORDER BY t.notice_date DESC LIMIT 1
    `).get(`%${address.trim()}%`);
  }
  return row;
}

function findComparables(commune, excludeId) {
  return db.query(`
    SELECT 
      t.id,
      t.address,
      t.commune,
      t.notice_date as date,
      COALESCE(t.surface_m2, e.surface_official_m2, 85) as surface,
      t.price_chf as price,
      ROUND(t.price_chf / COALESCE(t.surface_m2, e.surface_official_m2, 85)) as price_m2
    FROM transactions t
    LEFT JOIN enrichments e ON t.id = e.transaction_id
    WHERE t.commune = ? 
      AND t.price_chf > 300000 
      AND t.id != ?
      AND t.address IS NOT NULL
    ORDER BY t.notice_date DESC
    LIMIT 5
  `).all(commune, excludeId || 0);
}

console.log('--- Search Saut-du-Loup ---');
console.log(searchAddresses('Saut-du-Loup'));

console.log('--- Search Bel-Air ---');
console.log(searchAddresses('Bel-Air'));

console.log('--- Lookup Cadastre 17178 ---');
const cad = lookupCadastre(17178);
console.log(cad);

console.log('--- Comparables Chêne-Bourg ---');
console.log(findComparables('Chêne-Bourg', 0));

db.close();
