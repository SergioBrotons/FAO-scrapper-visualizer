import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1000})

        print("Navigating to http://localhost:8080/index.html ...")
        await page.goto("http://localhost:8080/index.html", timeout=30000)
        await page.wait_for_timeout(2000)

        # 1. Total DATA in JavaScript memory
        data_stats = await page.evaluate("""() => {
            const typologies = {};
            const rives = {};
            DATA.forEach(r => {
                typologies[r.typology_class] = (typologies[r.typology_class] || 0) + 1;
                rives[r.rive] = (rives[r.rive] || 0) + 1;
            });
            return {
                total: DATA.length,
                typologies: typologies,
                rives: rives
            };
        }""")
        print(f"Total Geocoded Transactions in DATA: {data_stats['total']}")
        print(f"Typologies breakdown: {data_stats['typologies']}")
        print(f"Rives breakdown: {data_stats['rives']}")

        # Helper to get HUD stat count
        async def get_hud_count():
            raw = await page.evaluate("() => document.getElementById('stat-count').textContent")
            return int(raw.replace('\u202f', '').replace('\xa0', '').replace(' ', '').replace("'", ''))

        # Helper to get markers count
        async def get_markers_count():
            return await page.evaluate("() => markersCluster.getLayers().length")

        # 2. Test Market Quick Filter: ALL
        await page.evaluate("() => setMarketQuickFilter('ALL')")
        hud_all = await get_hud_count()
        markers_all = await get_markers_count()
        print(f"\n[Test ALL]: HUD Count = {hud_all} | Markers = {markers_all} (Expected: {data_stats['total']})")
        assert hud_all == data_stats['total']
        assert markers_all == data_stats['total']

        # 3. Test Market Quick Filter: PPE (Appartements)
        await page.evaluate("() => setMarketQuickFilter('PPE')")
        hud_ppe = await get_hud_count()
        markers_ppe = await get_markers_count()
        expected_ppe = data_stats['typologies'].get('PPE', 0)
        print(f"[Test PPE]: HUD Count = {hud_ppe} | Markers = {markers_ppe} (Expected: {expected_ppe})")
        assert hud_ppe == expected_ppe
        assert markers_ppe == expected_ppe

        # 4. Test Market Quick Filter: VILLA (Maisons)
        await page.evaluate("() => setMarketQuickFilter('VILLA')")
        hud_villa = await get_hud_count()
        markers_villa = await get_markers_count()
        expected_villa = data_stats['typologies'].get('VILLA', 0)
        print(f"[Test VILLA]: HUD Count = {hud_villa} | Markers = {markers_villa} (Expected: {expected_villa})")
        assert hud_villa == expected_villa
        assert markers_villa == expected_villa

        # 5. Test Market Quick Filter: IMMEUBLE
        await page.evaluate("() => setMarketQuickFilter('IMMEUBLE')")
        hud_imm = await get_hud_count()
        markers_imm = await get_markers_count()
        expected_imm = data_stats['typologies'].get('IMMEUBLE', 0)
        print(f"[Test IMMEUBLE]: HUD Count = {hud_imm} | Markers = {markers_imm} (Expected: {expected_imm})")
        assert hud_imm == expected_imm
        assert markers_imm == expected_imm

        # 6. Test Market Quick Filter: TERRAIN
        await page.evaluate("() => setMarketQuickFilter('TERRAIN')")
        hud_ter = await get_hud_count()
        markers_ter = await get_markers_count()
        expected_ter = data_stats['typologies'].get('TERRAIN', 0)
        print(f"[Test TERRAIN]: HUD Count = {hud_ter} | Markers = {markers_ter} (Expected: {expected_ter})")
        assert hud_ter == expected_ter
        assert markers_ter == expected_ter

        # 7. Test RIVE Filters: RIVE GAUCHE & RIVE DROITE
        await page.evaluate("""() => {
            setMarketQuickFilter('ALL');
            setRiveFilter('GAUCHE');
        }""")
        hud_rg = await get_hud_count()
        markers_rg = await get_markers_count()
        expected_rg = data_stats['rives'].get('GAUCHE', 0)
        print(f"[Test RIVE GAUCHE]: HUD Count = {hud_rg} | Markers = {markers_rg} (Expected: {expected_rg})")
        assert hud_rg == expected_rg
        assert markers_rg == expected_rg

        await page.evaluate("() => setRiveFilter('DROITE')")
        hud_rd = await get_hud_count()
        markers_rd = await get_markers_count()
        expected_rd = data_stats['rives'].get('DROITE', 0)
        print(f"[Test RIVE DROITE]: HUD Count = {hud_rd} | Markers = {markers_rd} (Expected: {expected_rd})")
        assert hud_rd == expected_rd
        assert markers_rd == expected_rd

        # 8. Test Combined Filter: PPE + RIVE GAUCHE
        await page.evaluate("""() => {
            setMarketQuickFilter('PPE');
            setRiveFilter('GAUCHE');
        }""")
        hud_comb = await get_hud_count()
        markers_comb = await get_markers_count()
        expected_comb = await page.evaluate("() => DATA.filter(r => r.typology_class === 'PPE' && r.rive === 'GAUCHE').length")
        print(f"[Test COMBINED PPE + RIVE GAUCHE]: HUD Count = {hud_comb} | Markers = {markers_comb} (Expected: {expected_comb})")
        assert hud_comb == expected_comb
        assert markers_comb == expected_comb

        # 9. Test Combined Filter: VILLA + RIVE GAUCHE
        await page.evaluate("""() => {
            setMarketQuickFilter('VILLA');
            setRiveFilter('GAUCHE');
        }""")
        hud_villa_rg = await get_hud_count()
        markers_villa_rg = await get_markers_count()
        expected_villa_rg = await page.evaluate("() => DATA.filter(r => r.typology_class === 'VILLA' && r.rive === 'GAUCHE').length")
        print(f"[Test COMBINED VILLA + RIVE GAUCHE]: HUD Count = {hud_villa_rg} | Markers = {markers_villa_rg} (Expected: {expected_villa_rg})")
        assert hud_villa_rg == expected_villa_rg
        assert markers_villa_rg == expected_villa_rg

        # 10. Check UI Button Active State Consistency
        active_btn_id = await page.evaluate("""() => {
            const active = document.querySelector('#subtoolbarMarket .mkt-typo-btn.active');
            return active ? active.id : null;
        }""")
        print(f"[UI State]: Active button = {active_btn_id} (Expected: mktFilterHouses)")
        assert active_btn_id == 'mktFilterHouses'

        # Reset to ALL and RIVE ALL
        await page.evaluate("""() => {
            setMarketQuickFilter('ALL');
            setRiveFilter('ALL');
        }""")
        reset_count = await get_hud_count()
        assert reset_count == data_stats['total']
        print(f"\n[Reset ALL]: HUD Count reset successfully to {reset_count}")

        print("\n==========================================================================")
        print("ALL CATEGORY VISUALIZATION FILTERS TESTED & VERIFIED 100% ACCURATE!")
        print("==========================================================================")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
