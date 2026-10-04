import { describe, it, expect } from "bun:test";
import { DVIntelligenceService } from "../src/fao_transactions/dv/dv_service";
import path from "path";
import fs from "fs";

describe("Désormière & Vanhalst Real Estate Intelligence Service", () => {
  const service = new DVIntelligenceService();

  it("should initialize and return target Rive Gauche communes", () => {
    const communes = service.getTerritoryCommunes();
    expect(communes).toContain("Troinex");
    expect(communes).toContain("Veyrier");
    expect(communes).toContain("Chêne-Bougeries");
    expect(communes).toContain("Cologny");
    expect(communes).toContain("Collonge-Bellerive");
    expect(communes).toContain("Plan-les-Ouates");
  });

  it("should compute territory summary stats with active hoirie and division leads", () => {
    const stats = service.getSummaryStats();
    expect(stats.total_territory_leads).toBeGreaterThan(50);
    expect(stats.hoiries_count).toBeGreaterThan(5);
    expect(stats.divisions_count).toBeGreaterThan(5);
    expect(stats.prestige_count).toBeGreaterThan(10);
    expect(typeof stats.top_commune).toBe("string");
  });

  it("should return prioritized opportunities with valid score and signals", () => {
    const opps = service.getOpportunities({ limit: 20 });
    expect(opps.length).toBeGreaterThan(0);
    expect(opps.length).toBeLessThanOrEqual(20);

    const first = opps[0];
    expect(first.opportunity_score).toBeGreaterThanOrEqual(40);
    expect(first.opportunity_score).toBeLessThanOrEqual(99);
    expect(["URGENT", "QUALIFIE", "VEILLE"]).toContain(first.priority_tier);
    expect(first.signals.length).toBeGreaterThan(0);
    expect(["Sandra Bleeckx Vanhalst", "Adrien Désormière"]).toContain(first.target_broker);
    expect(first.recommended_pitch.length).toBeGreaterThan(10);
    expect(first.estimated_market_value_chf).toBeGreaterThan(0);
  });

  it("should strictly filter by specific commune (e.g. Troinex)", () => {
    const troinexOpps = service.getOpportunities({ commune: "Troinex", limit: 30 });
    expect(troinexOpps.length).toBeGreaterThan(0);
    for (const o of troinexOpps) {
      expect(o.commune.toLowerCase()).toBe("troinex");
    }
  });

  it("should filter by signal: hoiries only", () => {
    const hoirieOpps = service.getOpportunities({ signal: "hoirie", limit: 30 });
    expect(hoirieOpps.length).toBeGreaterThan(0);
    for (const o of hoirieOpps) {
      const hasHoirie = o.signals.some(s => s.code === "HOIRIE");
      expect(hasHoirie).toBe(true);
    }
  });

  it("should filter by signal: divisions only", () => {
    const divOpps = service.getOpportunities({ signal: "division", limit: 30 });
    expect(divOpps.length).toBeGreaterThan(0);
    for (const o of divOpps) {
      const hasDiv = o.signals.some(s => s.code === "DIVISION");
      expect(hasDiv).toBe(true);
      expect(o.surface_m2).toBeGreaterThanOrEqual(950);
    }
  });

  it("should generate branded D&V CMA HTML with nLPD masked parties", () => {
    // Transaction 16945 in Chêne-Bougeries
    const html = service.getCmaHtml(16945);
    expect(html).not.toBeNull();
    if (html) {
      expect(html.includes("Désormière & Vanhalst")).toBe(true);
      expect(html.includes("#00939D")).toBe(true); // Turquoise DV
      expect(html.includes("#004A4F")).toBe(true); // Vert profond
      expect(html.includes("Chêne-Bougeries")).toBe(true);
      expect(html.includes("Personne physique")).toBe(true); // nLPD compliance
    }
  });

  it("should verify public/dv assets and index.html exist and adhere to Brandbook", () => {
    const indexPath = path.resolve("public/dv/index.html");
    expect(fs.existsSync(indexPath)).toBe(true);
    const html = fs.readFileSync(indexPath, "utf8");

    // Colors from brandbook
    expect(html.includes("#00939D")).toBe(true);
    expect(html.includes("#004A4F")).toBe(true);
    expect(html.includes("#17DAE8")).toBe(true);
    expect(html.includes("#F6F3F3")).toBe(true);

    // Personas
    expect(html.includes("Sandra Bleeckx")).toBe(true);
    expect(html.includes("Adrien Désormière")).toBe(true);

    // Assets
    const logoPath = path.resolve("public/dv/assets/DandV Logo right text clear.png");
    expect(fs.existsSync(logoPath)).toBe(true);
  });
});
