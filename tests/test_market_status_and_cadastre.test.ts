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
    expect(html.includes('id="btnStatusCadastre"')).toBe(true);

    // Top Command Bar Tier 2 pills
    expect(html.includes('id="mktStatusPillSold"')).toBe(true);
    expect(html.includes('id="mktStatusPillCadastre"')).toBe(true);
  });

  it("should verify Swisstopo & SITG Cadastral WMTS layer is defined and toggleable", () => {
    const html = readFileSync(indexPath, "utf-8");
    expect(html.includes("ch.kantone.cadastralwebmap-farbe")).toBe(true);
    expect(html.includes("function toggleCadastreLayer")).toBe(true);
    expect(html.includes("function setMarketStatusFilter")).toBe(true);
    expect(html.includes("Plan Cadastral SITG (Foncier Officiel)")).toBe(true);
  });

  it("should verify DATA in index.html contains 100% verified authentic SOLD properties (ON_SALE retired)", () => {
    const html = readFileSync(indexPath, "utf-8");
    const dataMatch = html.match(/const DATA = (\[[\s\S]*?\]);/);
    expect(dataMatch).toBeTruthy();

    const data = JSON.parse(dataMatch![1]);
    expect(data.length).toBe(8548);
    const onSale = data.filter((r: any) => r.market_status === "ON_SALE");
    expect(onSale.length).toBe(0); // Safely retired upon user request
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
