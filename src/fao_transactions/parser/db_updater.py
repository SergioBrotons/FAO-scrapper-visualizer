import sqlite3
import re
import time
from fao_transactions.parser.pdf_parser import parse_price

def update_database_prices_and_parcels():
    conn = sqlite3.connect('data/state/state.sqlite')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, commune, parcel_number, price_raw, price_chf, raw_text FROM transactions WHERE raw_text IS NOT NULL")
    rows = cursor.fetchall()
    print(f"Scanning {len(rows)} database records...")

    price_pat = re.compile(r"(?:Prix(?:\s+total(?:\s+de\s+l['’]affaire)?)?|Prix\s+de\s+vente|Montant(?:\s+de\s+l['’]affaire)?|Valeur(?:\s+totale)?|contreprestation)\s*:\s*([^.;]+)", re.IGNORECASE)

    updated_prices = 0
    updated_parcels = 0
    updates = []

    for r in rows:
        t_id = r["id"]
        p_num = r["parcel_number"]
        p_raw = r["price_raw"]
        p_chf = r["price_chf"]
        text = r["raw_text"]

        new_p_raw = p_raw
        new_p_chf = p_chf
        new_p_num = p_num

        # Check price
        if p_chf is None:
            m = price_pat.search(text)
            if m:
                raw_str, val_chf = parse_price(m.group(1))
                if val_chf and val_chf > 0:
                    new_p_raw = raw_str
                    new_p_chf = val_chf
                    updated_prices += 1

        # Check parcel
        prop_parcel_match = re.search(
            r"(?:PPE|B-F|DDP|COP|parcelle(?:s)?)\s+[^,;]*?(?:,\s*)?(?:[0-9]{1,2}/)?([0-9]{1,6}(?:-[0-9]+)?)",
            text,
            re.IGNORECASE,
        )
        if prop_parcel_match:
            candidate = prop_parcel_match.group(1).replace(" ", "")
            if candidate != p_num:
                new_p_num = candidate
                updated_parcels += 1
        elif p_num in ("1", "2", "3", "4", "5"):
            slash_matches = re.finditer(r"\b([0-9]{1,2})/([0-9]+(?:\s*[-/]\s*[0-9]+)?)\b", text)
            for sm in slash_matches:
                prefix = sm.group(1)
                body = sm.group(2).replace(" ", "")
                if prefix in ("1", "2", "3", "4") and body in ("2", "3", "4", "5", "6", "1000"):
                    continue
                new_p_num = body
                updated_parcels += 1
                break

        if new_p_chf != p_chf or new_p_num != p_num:
            updates.append((new_p_raw, new_p_chf, new_p_num, t_id))

    print(f"Applying {len(updates)} updates (New prices: {updated_prices}, Fixed parcels: {updated_parcels})...")
    cursor.executemany("""
        UPDATE transactions SET
            price_raw = ?,
            price_chf = ?,
            parcel_number = ?
        WHERE id = ?
    """, updates)
    conn.commit()

    # Check COLCOMBET record specifically:
    cursor.execute("SELECT id, commune, parcel_number, price_chf, seller, buyer FROM transactions WHERE buyer LIKE '%COLCOMBET%'")
    print("COLCOMBET updated record:", cursor.fetchone())

    # Overall stats
    res = cursor.execute("""
        SELECT count(*), count(price_chf), sum(price_chf)
        FROM transactions
    """).fetchone()
    print(f"Final status: {res[0]} total transactions, {res[1]} with price, CHF {res[2]:,.2f} total volume.")
    conn.close()

if __name__ == '__main__':
    update_database_prices_and_parcels()
