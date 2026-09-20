import asyncio
import re
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1800, "height": 1000})

        print("Navigating to http://localhost:8080/index.html ...")
        await page.goto("http://localhost:8080/index.html", timeout=30000)
        await page.wait_for_timeout(2000)

        # Open CMA Modal
        await page.evaluate("() => openCmaModal()")
        await page.wait_for_timeout(600)

        # Run analysis for Saut-du-Loup 18 (95 m2)
        await page.evaluate("""() => {
            document.getElementById('cmaAddressInput').value = 'Chemin du Saut-du-Loup 18, 1225 Chêne-Bourg';
            document.getElementById('cmaSurfaceInput').value = 95;
            document.getElementById('cmaTypologySelect').value = 'PPE';
            runComparativeAnalysis();
        }""")
        await page.wait_for_timeout(800)

        # Extract all rows from table
        rows_data = await page.evaluate("""() => {
            const rows = Array.from(document.querySelectorAll('#cmaResultsArea table tbody tr'));
            return rows.map(r => {
                const cols = Array.from(r.querySelectorAll('td')).map(td => td.innerText.trim());
                return cols;
            });
        }""")

        print(f"\nTotal rows in CMA table: {len(rows_data)}")
        print("-" * 120)
        print(f"{'Dist':<15} | {'Date':<15} | {'Address / Parcelle':<40} | {'Prix':<18} | {'Surface':<20} | {'Prix/m²':<18}")
        print("-" * 120)
        for r in rows_data:
            dist = re.sub(r'\s+', ' ', r[0])
            dt = re.sub(r'\s+', ' ', r[1])
            addr = re.sub(r'\s+', ' ', r[2])[:38]
            price = re.sub(r'\s+', ' ', r[4])
            surf = re.sub(r'\s+', ' ', r[5])
            unit_p = re.sub(r'\s+', ' ', r[6])
            print(f"{dist:<15} | {dt:<15} | {addr:<40} | {price:<18} | {surf:<20} | {unit_p:<18}")

        # Capture screenshot of the CMA modal
        await page.screenshot(path="cma_enriched_surfaces.png")
        print("\nScreenshot saved to cma_enriched_surfaces.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
