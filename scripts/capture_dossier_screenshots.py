import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1600, "height": 1100})
        await page.goto("http://localhost:8080/index.html", timeout=30000)
        await page.wait_for_timeout(2000)

        # Open CMA and Dossier for Saut-du-Loup 18
        print("Opening CMA and Dossier modal...")
        await page.evaluate("""() => {
            document.getElementById('cmaAddressInput').value = 'Chemin du Saut-du-Loup 18, 1225 Chêne-Bourg';
            document.getElementById('cmaSurfaceInput').value = 90;
            document.getElementById('cmaTypologySelect').value = 'PPE';
            runComparativeAnalysis();
            openCmaDossierModal();
        }""")
        await page.wait_for_timeout(1000)

        # Check modal visibility
        is_visible = await page.evaluate("() => document.getElementById('cmaDossierModal').classList.contains('visible')")
        print(f"cmaDossierModal visible: {is_visible}")

        # Screenshot Page 1
        await page.screenshot(path=r"C:\Users\AI-Mini-PC\.gemini\antigravity-ide\brain\6170bb8a-e7e1-46fd-b87d-0f7dabde8adf\dossier_page_1_swiss_grid.png")
        print("Page 1 saved.")

        # Scroll modal body down to show Page 2
        await page.evaluate("""() => {
            const b = document.querySelector('#cmaDossierModal .league-body');
            if (b) b.scrollTop = 1050;
        }""")
        await page.wait_for_timeout(800)

        # Screenshot Page 2
        await page.screenshot(path=r"C:\Users\AI-Mini-PC\.gemini\antigravity-ide\brain\6170bb8a-e7e1-46fd-b87d-0f7dabde8adf\dossier_page_2_swiss_grid.png")
        print("Page 2 saved.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
