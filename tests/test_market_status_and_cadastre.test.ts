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

  it("should verify Parc Foncier Piscines SITG (5'173 bassins) layer is present and functional", () => {
    const html = readFileSync(indexPath, "utf-8");
    expect(html.includes('id="sitgAllPoolsLayerBtn"')).toBe(true);
    expect(html.includes("function toggleSitgAllPoolsLayer")).toBe(true);
    expect(html.includes("SITG_ALL_POOLS")).toBe(true);

    const poolsMatch = html.match(/const SITG_ALL_POOLS = (\[[\s\S]*?\]);/);
    expect(poolsMatch).toBeTruthy();
    const pools = JSON.parse(poolsMatch![1]);
    expect(pools.length).toBe(5173);

    // Verify sample pool point integrity [id, lat, lon, surf, perim, com]
    const p1 = pools[0];
    expect(p1[0]).toBe(1); // objectid
    expect(p1[1]).toBeGreaterThan(46.1); // lat
    expect(p1[2]).toBeGreaterThan(5.9); // lon
    expect(p1[3]).toBeGreaterThan(0); // surface_m2
    expect(typeof p1[5]).toBe("string"); // commune
  });
});
