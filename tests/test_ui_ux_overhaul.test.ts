import { describe, it, expect } from "bun:test";
import { resolve } from "path";

describe("Cytria Top Bar & Mobile UI/UX Overhaul Integrity", () => {
  const indexHtmlPath = resolve("index.html");
  const mapBuilderPath = resolve("src/fao_transactions/visualization/map_builder.py");

  it("should verify D&V links are completely removed from the visible top bar in index.html", async () => {
    const html = await Bun.file(indexHtmlPath).text();
    const utilitiesMatch = html.match(/<div class="top-bar-utilities">([\s\S]*?)<\/div>/);
    expect(utilitiesMatch).toBeTruthy();
    const utilitiesContent = utilitiesMatch![1];
    
    // Explicitly verify NO D&V links in the visible top-bar-utilities
    expect(utilitiesContent.includes('Portail D&amp;V')).toBe(false);
    expect(utilitiesContent.includes('Studio D&amp;V')).toBe(false);
    expect(utilitiesContent.includes('Marketing D&amp;V')).toBe(false);
    expect(utilitiesContent.includes('href="/dv/"')).toBe(false);
    expect(utilitiesContent.includes('href="/dv/?view=value"')).toBe(false);
    expect(utilitiesContent.includes('href="/dv/marketing/"')).toBe(false);
  });

  it("should verify top-bar-tier-1 and top-bar-tier-2 do not have lateral scrolling overflow-x: auto", async () => {
    const html = await Bun.file(indexHtmlPath).text();
    expect(html.includes(".top-bar-tier-1 {")).toBe(true);
    expect(html.includes(".top-bar-tier-2 {")).toBe(true);
    expect(html.includes("overflow: hidden; overflow-x: clip;")).toBe(true);
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
  });
});
