import { resolve } from "path";

async function run() {
  console.log("Starting comprehensive UI/UX overhaul...");

  const mapBuilderPath = resolve("src/fao_transactions/visualization/map_builder.py");
  const indexHtmlPath = resolve("index.html");

  const sidebarHeaderMarkup = `
    <!-- Sticky Mobile Header -->
    <div class="sidebar-mobile-header">
      <div class="sidebar-mobile-title">Filtres de Recherche</div>
      <div class="sidebar-mobile-actions">
        <button type="button" class="sidebar-mobile-reset-btn" onclick="resetAllFilters()">Effacer</button>
        <button type="button" class="sidebar-mobile-close-btn" onclick="toggleMobileSidebar(false)" aria-label="Fermer les filtres">&times;</button>
      </div>
    </div>
  `;

  const sidebarFooterMarkup = `
    <!-- Sticky Mobile Footer CTA -->
    <div class="sidebar-mobile-footer">
      <button type="button" class="sidebar-mobile-apply-btn" onclick="toggleMobileSidebar(false)">
        <span>Afficher les résultats</span>
        <span id="mobileSidebarResultCount" class="sidebar-mobile-badge">8'548</span>
      </button>
    </div>
  `;

  const mobileJsFunctions = `
  /* --- MOBILE CONTROLLER FUNCTIONS --- */
  function toggleMobileSidebar(forceState) {
    const sidebar = document.querySelector('.sidebar');
    const backdrop = document.getElementById('mobileSidebarBackdrop');
    if (!sidebar) return;
    const shouldOpen = forceState !== undefined ? forceState : !sidebar.classList.contains('mobile-open');
    sidebar.classList.toggle('mobile-open', shouldOpen);
    if (backdrop) {
      backdrop.classList.toggle('visible', shouldOpen);
      backdrop.style.display = shouldOpen ? 'block' : 'none';
    }
    const mobBtn = document.getElementById('btnMobFilters');
    if (mobBtn) mobBtn.classList.toggle('active', shouldOpen);
  }

  function cycleMarketStatusMobile() {
    const order = ['SOLD', 'ON_SALE', 'CADASTRE'];
    const nextIdx = (order.indexOf(currentMarketStatus) + 1) % order.length;
    setMarketStatusFilter(order[nextIdx]);
    const dot = document.getElementById('mobStatusDot');
    const label = document.getElementById('mobStatusLabel');
    if (dot && label) {
      dot.className = 'status-indicator-dot ' + (order[nextIdx] === 'SOLD' ? 'sold' : order[nextIdx] === 'ON_SALE' ? 'on-sale' : 'cadastre');
      label.textContent = order[nextIdx] === 'SOLD' ? 'Vendus' : order[nextIdx] === 'ON_SALE' ? 'En Vente' : 'Cadastre';
    }
  }

  function resetAllFilters() {
    if (typeof currentMarketStatus !== 'undefined') setMarketStatusFilter('SOLD');
    if (typeof currentRiveFilter !== 'undefined') setRiveFilter('ALL');
    if (typeof isPoolFilterActive !== 'undefined' && isPoolFilterActive) togglePoolFilter();
    if (typeof isSqmPriceLayerActive !== 'undefined' && isSqmPriceLayerActive) toggleSqmPriceLayer();
    const sInp = document.getElementById('searchInput');
    if (sInp) sInp.value = '';
    const cSel = document.getElementById('communeSelect');
    if (cSel) cSel.value = 'ALL';
    const zSel = document.getElementById('zoneSelect');
    if (zSel) zSel.value = 'ALL';
    const rSel = document.getElementById('roomsSelect');
    if (rSel) rSel.value = 'ALL';
    const bSel = document.getElementById('buildingSelect');
    if (bSel) bSel.value = 'ALL';
    const sfSel = document.getElementById('surfaceSelect');
    if (sfSel) sfSel.value = 'ALL';
    ['onlyPlqCheckbox', 'onlyDevCheckbox', 'onlyPermitCheckbox', 'onlyPricedCheckbox'].forEach(id => {
      const cb = document.getElementById(id);
      if (cb) cb.checked = false;
    });
    document.querySelectorAll('.pill-btn').forEach(btn => {
      const isDefault = btn.dataset.nature === 'ALL' || btn.dataset.price === 'ALL' || btn.dataset.typology === 'ALL';
      btn.classList.toggle('active', isDefault);
    });
    if (typeof applyFilters === 'function') applyFilters();
  }
`;

  async function patch(filePath: string) {
    console.log(`Patching ${filePath}...`);
    let text = await Bun.file(filePath).text();

    // 1. Inject sidebar header if not present
    if (!text.includes('class="sidebar-mobile-header"')) {
      text = text.replace('<aside class="sidebar">', `<aside class="sidebar">\n${sidebarHeaderMarkup}`);
      console.log(`  Injected sidebar-mobile-header`);
    }

    // 2. Inject sidebar footer if not present
    if (!text.includes('class="sidebar-mobile-footer"')) {
      text = text.replace('</aside>', `${sidebarFooterMarkup}\n  </aside>`);
      console.log(`  Injected sidebar-mobile-footer`);
    }

    // 3. Inject mobile controller functions before the last </script>
    if (!text.includes('function toggleMobileSidebar(')) {
      const lastScriptIdx = text.lastIndexOf('</script>');
      if (lastScriptIdx !== -1) {
        text = text.slice(0, lastScriptIdx) + `\n${mobileJsFunctions}\n` + text.slice(lastScriptIdx);
        console.log(`  Injected mobile JS controller functions`);
      }
    }

    await Bun.write(filePath, text);
  }

  await patch(mapBuilderPath);
  await patch(indexHtmlPath);

  console.log("Overhaul patching complete!");
}

run().catch(err => {
  console.error("Error:", err);
  process.exit(1);
});
