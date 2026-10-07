import { Database } from 'bun:sqlite';
const db = new Database('data/state/state.sqlite', { readonly: true });
const tables = db.query("SELECT name FROM sqlite_master WHERE type='table'").all();
console.log('Tables:', tables.map(t => t.name));
for (const t of tables) {
  const count = db.query(`SELECT count(*) as c FROM "${t.name}"`).get();
  const cols = db.query(`PRAGMA table_info("${t.name}")`).all();
  console.log(`\nTable ${t.name} (${count.c} rows):`);
  console.log(cols.map(c => c.name).join(', '));
}
db.close();
