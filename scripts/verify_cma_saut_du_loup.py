import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1600, "height": 950})

        print("Navigating to http://localhost:8080/index.html ...")
        await page.goto("http://localhost:8080/index.html", timeout=30000)
        await page.wait_for_timeout(2000)

        # 1. Open CMA Modal
        print("Opening CMA modal...")
        await page.evaluate("() => openCmaModal()")
        await page.wait_for_timeout(600)

        # 2. Check target inputs
        addr_val = await page.evaluate("() => document.getElementById('cmaAddressInput').value")
        print(f"Address input: {addr_val}")

        # Set surface to 90 m2 and run analysis
        await page.evaluate("""() => {
            document.getElementById('cmaAddressInput').value = 'Chemin du Saut-du-Loup 18, 1225 Chêne-Bourg';
            document.getElementById('cmaSurfaceInput').value = 90;
            document.getElementById('cmaTypologySelect').value = 'PPE';
            runComparativeAnalysis();
        }""")
        await page.wait_for_timeout(500)

        # 3. Verify resolved Quartier
        quartier_text = await page.evaluate("""() => {
            const els = document.querySelectorAll('#cmaResultsArea div');
            for (const el of els) {
                if (el.innerText && el.innerText.includes('Chêne-Bourg')) return el.innerText;
            }
            return '';
        }""")
        print(f"Quartier block contains: {quartier_text[:100]}")
        assert 'Chêne-Bourg' in quartier_text, "Target quartier must be Chêne-Bourg"
        assert 'Genthod' not in quartier_text, "Target quartier must NOT be Genthod"

        # 4. Verify Same-Residence banner
        raw_residence_banner = await page.evaluate("""() => {
            const b = document.querySelector('#cmaResultsArea');
            return b ? b.innerText : '';
        }""")
        import re
        clean_residence_banner = re.sub(r'[\s\u202f\xa0]+', ' ', raw_residence_banner)
        print("Cleaned banner text sample:", clean_residence_banner[:250])
        assert 'MÊME RÉSIDENCE' in clean_residence_banner or 'même résidence' in clean_residence_banner.lower(), "Must contain in-residence benchmark"
        assert '1 620 000' in clean_residence_banner or '1620000' in clean_residence_banner, "Must reference Saut-du-Loup 16 price of CHF 1'620'000"
        assert '17 609' in clean_residence_banner or '17609' in clean_residence_banner, "Must reference Saut-du-Loup 16 unit price (~17'609 CHF/m²)"

        # 5. Verify 3 KPI Cards for 90 m2
        val_med = await page.evaluate("""() => {
            const cards = document.querySelectorAll('#cmaResultsArea div');
            for (const c of cards) {
                if (c.innerText && c.innerText.includes('VALEUR VÉNALE MÉDIANE')) return c.innerText;
            }
            return '';
        }""")
        clean_val_med = re.sub(r'[\s\u202f\xa0]+', ' ', val_med)
        print(f"Median Valuation Card:\n{clean_val_med}")
        assert '1 585 000' in clean_val_med or '1585000' in clean_val_med, f"Expected ~1'585'000 CHF for 90 m², got: {clean_val_med}"

        # 6. Test 70 m2 and 110 m2 consistency
        await page.evaluate("""() => {
            document.getElementById('cmaSurfaceInput').value = 70;
            runComparativeAnalysis();
        }""")
        await page.wait_for_timeout(300)
        val_70 = await page.evaluate("""() => {
            const cards = document.querySelectorAll('#cmaResultsArea div');
            for (const c of cards) {
                if (c.innerText && c.innerText.includes('VALEUR VÉNALE MÉDIANE')) return c.innerText;
            }
            return '';
        }""")
        clean_val_70 = re.sub(r'[\s\u202f\xa0]+', ' ', val_70)
        print(f"70 m² Valuation: {clean_val_70}")
        assert '1 233 000' in clean_val_70 or '1233000' in clean_val_70

        await page.evaluate("""() => {
            document.getElementById('cmaSurfaceInput').value = 110;
            runComparativeAnalysis();
        }""")
        await page.wait_for_timeout(300)
        val_110 = await page.evaluate("""() => {
            const cards = document.querySelectorAll('#cmaResultsArea div');
            for (const c of cards) {
                if (c.innerText && c.innerText.includes('VALEUR VÉNALE MÉDIANE')) return c.innerText;
            }
            return '';
        }""")
        clean_val_110 = re.sub(r'[\s\u202f\xa0]+', ' ', val_110)
        print(f"110 m² Valuation: {clean_val_110}")
        assert '1 937 000' in clean_val_110 or '1937000' in clean_val_110

        # Reset to 90 m2
        await page.evaluate("""() => {
            document.getElementById('cmaSurfaceInput').value = 90;
            runComparativeAnalysis();
        }""")
        await page.wait_for_timeout(300)

        # 7. Verify Comparables Table columns & data
        rows_data = await page.evaluate("""() => {
            const rows = Array.from(document.querySelectorAll('#cmaResultsArea table tbody tr'));
            return rows.map(r => {
                const cols = Array.from(r.querySelectorAll('td')).map(td => td.innerText.trim());
                return cols;
            });
        }""")
        print(f"Comparables count: {len(rows_data)}")
        assert len(rows_data) > 0, "Expected at least 1 comparable row"
        
        # Check first row (Saut-du-Loup 16)
        first_row = [re.sub(r'[\s\u202f\xa0]+', ' ', c) for c in rows_data[0]]
        print(f"First comparable row: {first_row}")
        assert '0 m' in first_row[0] or 'Même résidence' in first_row[0]
        assert '16' in first_row[2] or 'Saut-du-Loup' in first_row[2]
        assert '1 620 000' in first_row[4]
        assert '92 m²' in first_row[5]
        assert '17 609' in first_row[6]

        print("ALL SAUT-DU-LOUP CMA VERIFICATIONS PASSED 100% PERFECTLY!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
