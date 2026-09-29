"""Check breakdown of the 65 files on disk not in DB."""
import sqlite3
from pathlib import Path

conn = sqlite3.connect('data/state/state.sqlite')
c = conn.cursor()
c.execute('SELECT LOWER(file_source) FROM transactions WHERE file_source IS NOT NULL')
db_files = set(r[0].strip() for r in c.fetchall() if r[0])

rf_files = set(f.name.lower() for f in Path('data/raw/transactions').glob('*.pdf'))
ldtr_files = set(f.name.lower() for f in Path('data/raw/ldtr').glob('*.pdf'))

missing_rf = rf_files - db_files
missing_ldtr = ldtr_files - db_files

print(f"Missing RF files: {len(missing_rf)}")
print(f"Missing LDTR files: {len(missing_ldtr)}")
print(f"Sample missing RF: {list(missing_rf)[:5]}")
print(f"Sample missing LDTR: {list(missing_ldtr)[:5]}")

# Also check how many records in DB share the same file_source (multi-record PDFs):
c.execute("SELECT file_source, count(*) as cnt FROM transactions GROUP BY file_source HAVING cnt > 1 ORDER BY cnt DESC LIMIT 10")
multi_records = c.fetchall()
print(f"\nTop PDFs with multiple transaction records: {multi_records}")
c.execute("SELECT count(*) FROM (SELECT file_source FROM transactions GROUP BY file_source HAVING count(*) > 1)")
multi_count = c.fetchone()[0]
print(f"Total PDFs that produced multiple records: {multi_count}")
