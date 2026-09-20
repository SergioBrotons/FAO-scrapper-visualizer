import sqlite3
import json
import os

db_path = 'data/fao_transactions.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Database: {db_path}")
    for t in tables:
        count = cursor.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
        print(f" - Table '{t}': {count} records")
        cursor.execute(f"PRAGMA table_info({t})")
        cols = [c[1] for c in cursor.fetchall()]
        print(f"   Columns: {', '.join(cols[:8])}...")
    conn.close()
else:
    print(f"No DB file at {db_path}")

exports_dir = 'data/exports'
print(f"\nExports files in {exports_dir}:")
for f in os.listdir(exports_dir):
    p = os.path.join(exports_dir, f)
    size_mb = os.path.getsize(p) / (1024 * 1024)
    print(f" - {f} ({size_mb:.2f} MB)")
