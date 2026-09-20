import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1600, "height": 950})
        
        print("Navigating to http://localhost:8080/index.html ...")
        await page.goto("http://localhost:8080/index.html", timeout=30000)
        await page.wait_for_timeout(2000)

        # 1. Verify counts in LEAGUE_DATA
        counts = await page.evaluate("""() => {
            return {
                agencies: typeof LEAGUE_DATA !== 'undefined' ? LEAGUE_DATA.agencies.length : 0,
                brokers: typeof LEAGUE_DATA !== 'undefined' ? LEAGUE_DATA.brokers.length : 0,
                marketing_agencies: typeof MARKETING_BENCHMARK !== 'undefined' ? MARKETING_BENCHMARK.length : 0
            }
        }""")
        print(f"Counts: Agencies={counts['agencies']}, Brokers={counts['brokers']}, Marketing Agencies={counts['marketing_agencies']}")
        assert counts['agencies'] == 83, f"Expected 83 agencies, got {counts['agencies']}"
        assert counts['brokers'] == 93, f"Expected 93 brokers, got {counts['brokers']}"

        # Also check DOM counts
        dom_agency_count = await page.evaluate("() => document.getElementById('countAgencies').textContent")
        dom_broker_count = await page.evaluate("() => document.getElementById('countBrokers').textContent")
        print(f"DOM display: countAgencies={dom_agency_count}, countBrokers={dom_broker_count}")
        assert dom_agency_count == '83'
        assert dom_broker_count == '93'

        # 2. Test CMA Tool opening and closing
        print("Testing CMA Tool modal display...")
        cma_vis_before = await page.evaluate("() => document.getElementById('cmaModal').classList.contains('visible')")
        mkt_vis_before = await page.evaluate("() => document.getElementById('marketingModal').classList.contains('visible')")
        print(f"Initially: cmaModal visible={cma_vis_before}, marketingModal visible={mkt_vis_before}")
        assert not cma_vis_before and not mkt_vis_before

        # Open CMA Modal
        await page.evaluate("() => openCmaModal()")
        await page.wait_for_timeout(500)
        cma_vis_open = await page.evaluate("() => document.getElementById('cmaModal').classList.contains('visible')")
        mkt_vis_open = await page.evaluate("() => document.getElementById('marketingModal').classList.contains('visible')")
        print(f"After openCmaModal(): cmaModal visible={cma_vis_open}, marketingModal visible={mkt_vis_open}")
        assert cma_vis_open, "cmaModal should be visible"
        assert not mkt_vis_open, "marketingModal should NOT be visible when opening CMA"

        # Close CMA Modal
        await page.evaluate("() => closeCmaModal()")
        await page.wait_for_timeout(500)
        cma_vis_closed = await page.evaluate("() => document.getElementById('cmaModal').classList.contains('visible')")
        mkt_vis_closed = await page.evaluate("() => document.getElementById('marketingModal').classList.contains('visible')")
        print(f"After closeCmaModal(): cmaModal visible={cma_vis_closed}, marketingModal visible={mkt_vis_closed}")
        assert not cma_vis_closed and not mkt_vis_closed, "Both modals should be closed"

        # Open Marketing Modal
        await page.evaluate("() => openMarketingModal()")
        await page.wait_for_timeout(500)
        mkt_vis_open2 = await page.evaluate("() => document.getElementById('marketingModal').classList.contains('visible')")
        cma_vis_open2 = await page.evaluate("() => document.getElementById('cmaModal').classList.contains('visible')")
        print(f"After openMarketingModal(): marketingModal visible={mkt_vis_open2}, cmaModal visible={cma_vis_open2}")
        assert mkt_vis_open2, "marketingModal should be visible"
        assert not cma_vis_open2, "cmaModal should NOT be visible"

        # Close Marketing Modal
        await page.evaluate("() => closeMarketingModal()")
        await page.wait_for_timeout(500)
        assert not (await page.evaluate("() => document.getElementById('marketingModal').classList.contains('visible')"))

        # 3. Test Benchmark (League Table) Modal & Sorting
        print("Testing Benchmark League Table modal & sorting...")
        await page.evaluate("() => openLeagueModal()")
        await page.wait_for_timeout(500)
        
        # Test sorting by name A-Z
        await page.evaluate("""() => {
            const sel = document.getElementById('leagueSortSelect');
            sel.value = 'NAME_ASC';
            renderLeagueContent();
        }""")
        first_agency_asc = await page.evaluate("() => document.querySelector('#leagueBodyContent table tbody tr td:nth-child(2) strong').innerText")
        print(f"First agency (A-Z): {first_agency_asc}")
        
        # Test sorting by name Z-A
        await page.evaluate("""() => {
            const sel = document.getElementById('leagueSortSelect');
            sel.value = 'NAME_DESC';
            renderLeagueContent();
        }""")
        first_agency_desc = await page.evaluate("() => document.querySelector('#leagueBodyContent table tbody tr td:nth-child(2) strong').innerText")
        print(f"First agency (Z-A): {first_agency_desc}")
        assert first_agency_asc != first_agency_desc, "Sort A-Z vs Z-A should yield different first rows"

        # Test sorting by Volume High-Low
        await page.evaluate("""() => {
            const sel = document.getElementById('leagueSortSelect');
            sel.value = 'VOLUME_DESC';
            renderLeagueContent();
        }""")
        first_agency_vol = await page.evaluate("() => document.querySelector('#leagueBodyContent table tbody tr td:nth-child(2) strong').innerText")
        print(f"First agency by volume: {first_agency_vol}")

        # Switch to Courtiers tab
        await page.evaluate("() => setLeagueTab('BROKERS')")
        await page.wait_for_timeout(300)
        broker_count = await page.evaluate("() => document.querySelectorAll('#leagueBodyContent table tbody tr').length")
        print(f"Brokers rendered in table: {broker_count}")
        assert broker_count == 93, f"Expected 93 broker rows, got {broker_count}"

        # Test broker sorting
        await page.evaluate("""() => {
            const sel = document.getElementById('leagueSortSelect');
            sel.value = 'NAME_ASC';
            renderLeagueContent();
        }""")
        first_broker_asc = await page.evaluate("() => document.querySelector('#leagueBodyContent table tbody tr td:nth-child(2) strong').innerText")
        
        await page.evaluate("""() => {
            const sel = document.getElementById('leagueSortSelect');
            sel.value = 'NAME_DESC';
            renderLeagueContent();
        }""")
        first_broker_desc = await page.evaluate("() => document.querySelector('#leagueBodyContent table tbody tr td:nth-child(2) strong').innerText")
        print(f"First broker A-Z: {first_broker_asc}, Z-A: {first_broker_desc}")
        assert first_broker_asc != first_broker_desc

        await page.evaluate("() => closeLeagueModal()")

        # 4. Test Marketing Table Sorting (Recency, Name)
        print("Testing Marketing Table sorting...")
        await page.evaluate("() => openMarketingModal()")
        await page.wait_for_timeout(500)

        # Sort by date desc (plus récent)
        await page.evaluate("""() => {
            const sel = document.getElementById('marketingSortSelect');
            sel.value = 'DATE_DESC';
            renderMarketingContent();
        }""")
        first_mkt_date_desc = await page.evaluate("() => document.querySelector('#marketingBodyContent table tbody tr td:nth-child(3) div').innerText")
        
        # Sort by date asc (plus ancien)
        await page.evaluate("""() => {
            const sel = document.getElementById('marketingSortSelect');
            sel.value = 'DATE_ASC';
            renderMarketingContent();
        }""")
        first_mkt_date_asc = await page.evaluate("() => document.querySelector('#marketingBodyContent table tbody tr td:nth-child(3) div').innerText")
        print(f"Marketing sort DATE_DESC: {first_mkt_date_desc}, DATE_ASC: {first_mkt_date_asc}")
        assert first_mkt_date_desc != first_mkt_date_asc

        # Sort by name A-Z
        await page.evaluate("""() => {
            const sel = document.getElementById('marketingSortSelect');
            sel.value = 'NAME_ASC';
            renderMarketingContent();
        }""")
        first_mkt_name_asc = await page.evaluate("() => document.querySelector('#marketingBodyContent table tbody tr td:nth-child(2) div').innerText")
        print(f"Marketing sort NAME_ASC: {first_mkt_name_asc}")

        await page.evaluate("() => closeMarketingModal()")

        # 5. Test Agency and Broker filtering on map & sidebar
        print("Testing Agency and Broker filtering...")
        # Switch to Agency suite
        await page.evaluate("() => switchProductSuite('AGENCY_BI')")
        await page.wait_for_timeout(500)

        # Select an agency (Pilet & Renaud or SPG One)
        selected_agency_id = await page.evaluate("""() => {
            const select = document.getElementById('sidebarAgencySelect');
            // Select second option (first real agency)
            select.selectedIndex = 1;
            select.dispatchEvent(new Event('change'));
            return select.value;
        }""")
        await page.wait_for_timeout(500)
        print(f"Selected agency ID: {selected_agency_id}")

        broker_options = await page.evaluate("""() => {
            const brokerSelect = document.getElementById('sidebarBrokerSelect');
            return Array.from(brokerSelect.options).map(o => o.text);
        }""")
        print(f"Brokers dropdown for {selected_agency_id}: {broker_options}")
        assert len(broker_options) > 1, f"Expected brokers for {selected_agency_id}"

        # Check sold properties marker layer and stats
        stat_count_agency = await page.evaluate("() => document.getElementById('stat-count').textContent")
        cluster_count = await page.evaluate("() => markersCluster.getLayers().length")
        print(f"Agency stat-count: {stat_count_agency}, cluster markers: {cluster_count}")
        assert int(stat_count_agency) > 0, "Expected sold properties count > 0 for agency"
        assert cluster_count > 0, "Expected markers in cluster"

        # Select a specific broker
        broker_selected = await page.evaluate("""() => {
            const brokerSelect = document.getElementById('sidebarBrokerSelect');
            brokerSelect.selectedIndex = 1;
            brokerSelect.dispatchEvent(new Event('change'));
            return brokerSelect.value;
        }""")
        await page.wait_for_timeout(500)
        print(f"Selected broker: {broker_selected}")

        stat_count_broker = await page.evaluate("() => document.getElementById('stat-count').textContent")
        broker_cluster_count = await page.evaluate("() => markersCluster.getLayers().length")
        print(f"Broker stat-count: {stat_count_broker}, cluster markers: {broker_cluster_count}")
        assert int(stat_count_broker) > 0, "Expected sold properties for broker"
        assert broker_cluster_count > 0, "Expected markers in cluster for broker"

        print("ALL VERIFICATIONS PASSED 100% PERFECTLY!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
