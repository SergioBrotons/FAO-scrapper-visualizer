import { describe, it, expect } from "bun:test";
import { readFileSync, existsSync } from "fs";
import { join } from "path";

describe("Cytria Tri-State Market Status & Cadastre Filter Integration", () => {
  const indexPath = join(process.cwd(), "index.html");
  const mapBuilderPath = join(process.cwd(), "src", "fao_transactions", "visualization", "map_builder.py");

  it("should verify index.html exists and contains the Tri-State Segmented Control", () => {
    expect(existsSync(indexPath)).toBe(true);
    const html = readFileSync(indexPath, "utf-8");

    // Sidebar controls
    expect(html.includes('id="marketStatusSelector"')).toBe(true);
    expect(html.includes('id="btnStatusSold"')).toBe(true);
    expect(html.includes('id="btnStatusOnSale"')).toBe(true);
    expect(html.includes('id="btnStatusCadastre"')).toBe(true);

    // Top Command Bar Tier 2 pills
    expect(html.includes('id="mktStatusPillSold"')).toBe(true);
    expect(html.includes('id="mktStatusPillOnSale"')).toBe(true);
    expect(html.includes('id="mktStatusPillCadastre"')).toBe(true);
  });

  it("should verify Swisstopo & SITG Cadastral WMTS layer is defined and toggleable", () => {
    const html = readFileSync(indexPath, "utf-8");
    expect(html.includes("ch.kantone.cadastralwebmap-farbe")).toBe(true);
    expect(html.includes("function toggleCadastreLayer")).toBe(true);
    expect(html.includes("function setMarketStatusFilter")).toBe(true);
    expect(html.includes("Plan Cadastral SITG (Foncier Officiel)")).toBe(true);
  });

  it("should verify DATA in index.html contains both SOLD and ON_SALE properties", () => {
    const html = readFileSync(indexPath, "utf-8");
    expect(html.includes('"market_status":"ON_SALE"') || html.includes('"market_status": "ON_SALE"')).toBe(true);
    expect(html.includes('BARNES Suisse SA - Genève')).toBe(true);
  });

  it("should verify all ON_SALE properties in index.html have actionable live ad and verification links", () => {
    const html = readFileSync(indexPath, "utf-8");
    const dataMatch = html.match(/const DATA = (\[[\s\S]*?\]);/);
    expect(dataMatch).toBeTruthy();

    const data = JSON.parse(dataMatch![1]);
    const onSale = data.filter((r: any) => r.market_status === "ON_SALE");
    expect(onSale.length).toBeGreaterThan(500);

    for (const r of onSale) {
      expect(r.listing_url).toBeTruthy();
      expect(r.listing_url.startsWith("http")).toBe(true);
      expect(r.portal_url).toBeTruthy();
      expect(r.portal_url.includes("immoscout24.ch")).toBe(true);
      expect(r.verify_url).toBeTruthy();
      expect(r.verify_url.includes("google.com/search")).toBe(true);
    }
  });

  it("should verify openDetail and map_builder template contain the live ad action button and verification gateways", () => {
    const html = readFileSync(indexPath, "utf-8");
    expect(html.includes('action-btn live-ad')).toBe(true);
    expect(html.includes("Annonce en Direct")).toBe(true);
    expect(html.includes("Vérification de l'annonce en direct")).toBe(true);

    const py = readFileSync(mapBuilderPath, "utf-8");
    expect(py.includes('action-btn live-ad')).toBe(true);
    expect(py.includes("Annonce en Direct")).toBe(true);
  });
});
