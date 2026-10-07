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

  it("should verify map_builder.py HTML_TEMPLATE includes the Tri-State controls and Cadastre layer", () => {
    expect(existsSync(mapBuilderPath)).toBe(true);
    const py = readFileSync(mapBuilderPath, "utf-8");

    expect(py.includes('id="marketStatusSelector"')).toBe(true);
    expect(py.includes('id="btnStatusSold"')).toBe(true);
    expect(py.includes('id="btnStatusOnSale"')).toBe(true);
    expect(py.includes('id="btnStatusCadastre"')).toBe(true);
    expect(py.includes('id="mktStatusPillSold"')).toBe(true);
    expect(py.includes('id="mktStatusPillOnSale"')).toBe(true);
    expect(py.includes('id="mktStatusPillCadastre"')).toBe(true);
    expect(py.includes("ch.kantone.cadastralwebmap-farbe")).toBe(true);
    expect(py.includes("function toggleCadastreLayer")).toBe(true);
    expect(py.includes("function setMarketStatusFilter")).toBe(true);
  });
});
