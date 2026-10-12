import { describe, it, expect } from "bun:test";
import path from "path";

const projectRoot = path.resolve(__dirname, "..");
const indexHtmlPath = path.join(projectRoot, "index.html");
const mapBuilderPath = path.join(projectRoot, "src", "fao_transactions", "visualization", "map_builder.py");

describe("Cytria Top Bar & Mobile UI/UX Overhaul Integrity", () => {
  it("should verify D&V links are completely removed from the visible top bar in index.html", async () => {
    const html = await Bun.file(indexHtmlPath).text();
    const topBarMatch = html.match(/<header class="top-bar">([\s\S]*?)<\/header>/);
    expect(topBarMatch).toBeTruthy();
    const topBarHtml = topBarMatch![1];

    expect(topBarHtml.includes("Désormière &amp; Vanhalst")).toBe(false);
    expect(topBarHtml.includes("Désormière & Vanhalst")).toBe(false);
    expect(topBarHtml.includes("D&amp;V")).toBe(false);
    expect(topBarHtml.includes("D&V")).toBe(false);
  });

  it("should verify top-bar-tier-1 and top-bar-tier-2 do not have lateral scrolling overflow-x: auto", async () => {
    const html = await Bun.file(indexHtmlPath).text();
    expect(html.includes(".top-bar-tier-1 {\n      overflow-x: auto;")).toBe(false);
    expect(html.includes(".top-bar-tier-2 {\n      overflow-x: auto;")).toBe(false);
    expect(html.includes("overflow-x: auto !important;")).toBe(false);
  });

  it("should verify mobile sticky header, close button, and footer CTA exist in the sidebar", async () => {
    const html = await Bun.file(indexHtmlPath).text();
    expect(html.includes('class="sidebar-mobile-header"')).toBe(true);
    expect(html.includes('class="sidebar-mobile-close-btn"')).toBe(true);
    expect(html.includes('class="sidebar-mobile-reset-btn"')).toBe(true);
    expect(html.includes('class="sidebar-mobile-footer"')).toBe(true);
    expect(html.includes('class="sidebar-mobile-apply-btn"')).toBe(true);
  });

  it("should verify floating mobile bottom navigation bar exists with interactive buttons", async () => {
    const html = await Bun.file(indexHtmlPath).text();
    expect(html.includes('id="mobileBottomBar"')).toBe(true);
    expect(html.includes('id="btnMobMap"')).toBe(true);
    expect(html.includes('id="btnMobFilters"')).toBe(true);
    expect(html.includes('id="btnMobMarketToggle"')).toBe(true);
    expect(html.includes('id="btnMobReset"')).toBe(true);
  });

  it("should verify openDetail cleanly separates En Vente from Vendus denominations", async () => {
    const html = await Bun.file(indexHtmlPath).text();
    expect(html.includes("Mandat Actif en Commercialisation")).toBe(true);
    expect(html.includes("Disponible à l'achat (En cours de commercialisation)")).toBe(true);
    expect(html.includes("Propriétaire / Mandant")).toBe(true);
    expect(html.includes("Diffusion Mandat")).toBe(true);
    expect(html.includes("Données Foncières &amp; SITG") || html.includes("Données Foncières & SITG")).toBe(true);
  });

  it("should verify properties have pool metadata in DATA", async () => {
    const html = await Bun.file(indexHtmlPath).text();
    const dataMatch = html.match(/const DATA = (\[[\s\S]*?\]);/);
    expect(dataMatch).toBeTruthy();
    const data = JSON.parse(dataMatch![1]);
    
    const soldWithPool = data.filter((r: any) => r.has_pool === 1).length;
    expect(soldWithPool).toBe(468);
  });

  it("should verify essential mobile controller functions are defined in JavaScript", async () => {
    const html = await Bun.file(indexHtmlPath).text();
    expect(html.includes("function toggleMobileSidebar(")).toBe(true);
    expect(html.includes("function cycleMarketStatusMobile(")).toBe(true);
    expect(html.includes("function resetAllFilters(")).toBe(true);
  });

  it("should verify map_builder.py template preserves all UI/UX enhancements", async () => {
    const py = await Bun.file(mapBuilderPath).text();
    expect(py.includes('class="sidebar-mobile-header"')).toBe(true);
    expect(py.includes('id="mobileBottomBar"')).toBe(true);
    expect(py.includes("Mandat Actif en Commercialisation")).toBe(true);
    expect(py.includes("function cycleMarketStatusMobile")).toBe(true);
    expect(py.includes('id="btnFilterToggle"')).toBe(true);
    expect(py.includes('id="sidebarToggleFloatingBtn"')).toBe(true);
  });

  it("should verify show/hide filter panel toggle button exists with UI/UX optimization across mobile and responsive layouts", async () => {
    const html = await Bun.file(indexHtmlPath).text();
    expect(html.includes('id="btnFilterToggle"')).toBe(true);
    expect(html.includes('id="filterToggleStatusBadge"')).toBe(true);
    expect(html.includes('.filter-panel-toggle-btn {')).toBe(true);
    expect(html.includes('id="sidebarToggleFloatingBtn"')).toBe(true);
    expect(html.includes('function toggleSidebar(')).toBe(true);
    expect(html.includes('(Raccourci: Shift+F)')).toBe(true);
  });

  it("should verify responsive and mobile breakpoint synchronization in toggleSidebar", async () => {
    const html = await Bun.file(indexHtmlPath).text();
    expect(html.includes("window.innerWidth <= 820")).toBe(true);
    expect(html.includes("sidebar-is-collapsed")).toBe(true);
    expect(html.includes("filterToggleStatusBadge")).toBe(true);
    expect(html.includes("window._filterKeyShortcutBound")).toBe(true);
  });

  it("should verify .sidebar CSS integrity with proper z-index and background styling", async () => {
    const html = await Bun.file(indexHtmlPath).text();
    const sidebarCssMatch = html.match(/\.sidebar\s*\{([^}]*)\}/);
    expect(sidebarCssMatch).toBeTruthy();
    const sidebarCss = sidebarCssMatch![1];
    expect(sidebarCss.includes("z-index: 1000")).toBe(true);
    expect(sidebarCss.includes("background: var(--panel-bg)")).toBe(true);
    expect(sidebarCss.includes("display: flex")).toBe(true);
    expect(sidebarCss.includes("overflow-y: auto")).toBe(true);
  });

  it("should verify keyboard shortcut respects native browser Ctrl+F find without hijacking", async () => {
    const html = await Bun.file(indexHtmlPath).text();
    expect(html.includes("e.ctrlKey || e.metaKey || e.altKey")).toBe(true);
    expect(html.includes("e.shiftKey && (e.key === 'F' || e.key === 'f')")).toBe(true);
  });

  it("should verify inline script has valid JavaScript syntax with zero parser errors", async () => {
    const html = await Bun.file(indexHtmlPath).text();
    const scriptMatch = html.match(/<script(?![^>]*src=)[^>]*>([\s\S]*?)<\/script>/i);
    expect(scriptMatch).toBeTruthy();
    let parseError = null;
    try {
      new Function(scriptMatch![1]);
    } catch (e: any) {
      parseError = e.message;
    }
    expect(parseError).toBeNull();
  });
});
