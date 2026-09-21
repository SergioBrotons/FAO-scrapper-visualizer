import asyncio
import re
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1600, "height": 950})

        print("1. Navigating to http://localhost:8080/index.html#cma ...")
        await page.goto("http://localhost:8080/index.html#cma", timeout=30000)
        await page.wait_for_timeout(1500)

        # Ensure CMA modal is open and analyze Saut-du-Loup 18 (90 m2, PPE)
        print("2. Configuring CMA for Saut-du-Loup 18, 90 m2...")
        await page.evaluate("""() => {
            document.getElementById('cmaAddressInput').value = 'Chemin du Saut-du-Loup 18, 1225 Chêne-Bourg';
            document.getElementById('cmaSurfaceInput').value = 90;
            document.getElementById('cmaTypologySelect').value = 'PPE';
            runComparativeAnalysis();
        }""")
        await page.wait_for_timeout(500)

        # Check that the dossier generator button is present in CMA results
        dossier_btn = await page.query_selector("button:has-text('GÉNÉRER LE DOSSIER D\\'AVIS DE VALEUR')")
        assert dossier_btn is not None, "Button 'GÉNÉRER LE DOSSIER D'AVIS DE VALEUR ↗' must exist"
        print("Dossier generator button found in CMA results.")

        # Click the dossier button to open the modal
        print("3. Opening Dossier modal via button...")
        await dossier_btn.click()
        await page.wait_for_timeout(600)

        # Verify dossier modal visibility
        is_visible = await page.evaluate("() => document.getElementById('cmaDossierModal').classList.contains('visible')")
        assert is_visible, "cmaDossierModal must have 'visible' class"
        print("cmaDossierModal is visible.")

        # Check Page 1 Content
        printable_html = await page.evaluate("() => document.getElementById('cmaDossierPrintable').innerText")
        clean_text = re.sub(r'[\s\u202f\xa0]+', ' ', printable_html)
        print("Sample printable text:", clean_text[:250])

        assert "DOSSIER D'AVIS DE VALEUR NOTARIÉ" in clean_text.upper(), "Must contain title"
        assert "CYT-CMA-2026-" in clean_text, "Must contain official dossier reference number"
        assert "Saut-du-Loup 18" in clean_text, "Must contain target address"
        assert "1 585 000" in clean_text or "1585000" in clean_text, "Must contain median valuation ~CHF 1'585'000"
        assert "17 609" in clean_text or "17609" in clean_text, "Must contain unit valuation CHF 17'609 / m²"
        assert "Saut-du-Loup 16" in clean_text, "Must cite same-residence benchmark Saut-du-Loup 16"
        print("Page 1 assertions verified successfully.")

        # Check Page 2 Content (Preuves notariées contiguës & Cadre légal)
        assert "4. ACTES NOTARIÉS COMPARABLES CONTIGUS" in clean_text.upper(), "Must have Section 4"
        assert "157" in clean_text and "LACC" in clean_text.upper(), "Must cite Art. 157 LaCC"
        assert "NLPD" in clean_text.upper() or "PROTECTION DES DONNÉES" in clean_text.upper(), "Must have nLPD compliance note"
        assert "LDTR" in clean_text.upper(), "Must cite LDTR regulations"
        assert "VALIDITÉ INDICATIVE" in clean_text.upper() or "90 JOURS" in clean_text.upper(), "Must cite 90 days validity"
        assert "SIGNATURE DU COURTIER" in clean_text.upper(), "Must have broker signature block"
        print("Page 2 assertions verified successfully.")

        # 4. Test Agency Customizer / White-Labeling
        print("4. Testing Agency Branding Customizer...")
        await page.evaluate("""() => {
            toggleAgencyBrandingEditor();
            document.getElementById('dossierAgencyName').value = 'Brotons Real Estate Geneva';
            document.getElementById('dossierBrokerName').value = 'Sergio Brotons & Associés';
            document.getElementById('dossierContactInfo').value = '+41 22 700 88 99 • sb@brotons-realestate.ch';
            saveAgencyBranding();
        }""")
        await page.wait_for_timeout(400)

        updated_text = await page.evaluate("() => document.getElementById('cmaDossierPrintable').innerText")
        assert "Brotons Real Estate Geneva" in updated_text, "Custom agency branding must be reflected in dossier"
        assert "Sergio Brotons & Associés" in updated_text, "Custom broker branding must be reflected in dossier"
        print("Agency branding customization verified.")

        # 5. Test Deep Link #dossier
        print("5. Testing direct deep link #dossier...")
        await page.goto("http://localhost:8080/index.html#dossier", timeout=30000)
        await page.wait_for_timeout(1000)
        deep_visible = await page.evaluate("() => document.getElementById('cmaDossierModal').classList.contains('visible')")
        assert deep_visible, "#dossier deep link must open cmaDossierModal directly"
        print("Deep link #dossier verified.")

        print("ALL CMA DOSSIER VERIFICATIONS PASSED!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
