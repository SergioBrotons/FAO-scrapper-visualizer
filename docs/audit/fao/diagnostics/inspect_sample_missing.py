import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from fao_transactions.parser.pdf_parser import FaoPdfParser, is_real_estate_transaction

files = [
    Path('data/raw/transactions/notice_3137b42a-9305-4b28-b0d6-267778e96db9.pdf'),
    Path('data/raw/transactions/notice_de2fb4ce-a5d9-485c-9a26-eaf7ea1412fa.pdf'),
    Path('data/raw/transactions/notice_cafa9eb5-85d2-4fa4-98d7-41589bfcf179.pdf'),
]

parser = FaoPdfParser()

for p in files:
    if not p.exists():
        print(f"File {p} does not exist!")
        continue
    print(f"\n--- Checking {p.name} ({p.stat().st_size} bytes) ---")
    try:
        text = parser.extract_text_pymupdf(p)
        print(f"Length of text: {len(text)}")
        print(f"Is real estate transaction: {is_real_estate_transaction(text)}")
        records = parser.parse_pdf(p)
        print(f"Parsed records count: {len(records)}")
        print("Text snippet (first 300 chars):")
        print(text[:300].strip())
    except Exception as e:
        print(f"Error reading/parsing: {e}")
