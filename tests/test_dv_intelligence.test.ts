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

  it("should retrieve territorial watch data with recent sales and competitor mandates", () => {
    const watch = service.getTerritorialWatch({ limit: 20 });
    expect(watch).toBeDefined();
    expect(watch.recent_sales.length).toBeGreaterThan(0);
    expect(watch.competitor_mandates.length).toBeGreaterThan(0);
    expect(watch.stats.sales_count).toBeGreaterThan(0);
    expect(watch.stats.competitor_deals_count).toBeGreaterThan(0);
    expect(typeof watch.stats.stale_mandates_count).toBe("number");
    expect(typeof watch.stats.top_active_competitor).toBe("string");

    // Check sales structure
    const firstSale = watch.recent_sales[0];
    expect(firstSale.id).toBeDefined();
    expect(firstSale.commune).toBeDefined();
    expect(firstSale.address).toBeDefined();
    expect(firstSale.price_chf).toBeGreaterThanOrEqual(1200000);

    // Check competitor mandate structure
    const firstMandate = watch.competitor_mandates[0];
    expect(firstMandate.agency_name).toBeDefined();
    expect(firstMandate.status_badge).toBeDefined();
    expect(firstMandate.strategic_action).toBeDefined();
  });

  it("should generate neighbor effect canvassing data and courtesy letter", () => {
    const watch = service.getTerritorialWatch({ limit: 5 });
    const saleId = watch.recent_sales[0].id;
    const neighborData = service.getNeighborsForSale(saleId);

    expect(neighborData).toBeDefined();
    expect(neighborData!.sale.id).toBe(saleId);
    expect(neighborData!.neighbors.length).toBeGreaterThan(0);
    expect(neighborData!.neighbors.length).toBeLessThanOrEqual(5);

    // Courtesy letter verification
    expect(neighborData!.courtesy_letter_text).toContain("DÉSORMIÈRE & VANHALST");
    expect(neighborData!.courtesy_letter_text).toContain("Sandra Bleeckx Vanhalst & Adrien Désormière");
  });

  it("should verify server.js registers all required DV endpoints", () => {
    const serverCode = fs.readFileSync(path.resolve("server.js"), "utf8");
    expect(serverCode.includes("/api/dv/opportunities")).toBe(true);
    expect(serverCode.includes("/api/dv/cma")).toBe(true);
    expect(serverCode.includes("/api/dv/watch")).toBe(true);
    expect(serverCode.includes("/api/dv/neighbors")).toBe(true);
    expect(serverCode.includes("/api/dv/search")).toBe(true);
    expect(serverCode.includes("/api/dv/valuation-studio")).toBe(true);
    expect(serverCode.includes("/api/dv/saut-du-loup-case")).toBe(true);
    expect(serverCode.includes("/api/dv/export-pptx")).toBe(true);
  });

  it("should verify property search, valuation studio, and agency portfolio review", () => {
    // 1. Search properties
    const searchRes = service.searchProperties("Veyrier", 5);
    expect(searchRes.length).toBeGreaterThan(0);
    expect(searchRes[0].address).toBeDefined();

    // 2. Valuation studio
    const studio = service.getValuationStudio(searchRes[0].id);
    expect(studio).toBeDefined();
    expect(studio.target.address).toBeDefined();
    expect(studio.comparables.length).toBeGreaterThanOrEqual(3);
    expect(studio.valuation_baseline.base_price_chf).toBeGreaterThan(0);
    expect(studio.expert_checklist.length).toBe(4);

    // 3. Portfolio & Buyers
    const portfolio = service.getAgencyPortfolioReview();
    expect(portfolio.mandates.length).toBeGreaterThan(0);
    expect(portfolio.buyers.length).toBeGreaterThan(0);
    expect(portfolio.weekly_pulse.sales_this_week).toBeGreaterThan(0);
  });

  it("should verify public/dv/index.html includes Executive Hub, 3-Step Valuation Studio, and actions", () => {
    const indexPath = path.resolve("public/dv/index.html");
    const html = fs.readFileSync(indexPath, "utf8");

    // Views & navigation
    expect(html.includes("viewHub")).toBe(true);
    expect(html.includes("viewValue")).toBe(true);
    expect(html.includes("viewRadar")).toBe(true);
    expect(html.includes("viewMandates")).toBe(true);
    expect(html.includes("viewBuyers")).toBe(true);
    expect(html.includes("switchView")).toBe(true);

    // Executive Greeting & 4 Tiles
    expect(html.includes("greetingTitle")).toBe(true);
    expect(html.includes("Bonjour, Sandra")).toBe(true);
    expect(html.includes("Préparer une estimation")).toBe(true);
    expect(html.includes("Analyser mon secteur")).toBe(true);
    expect(html.includes("Revoir mes mandats")).toBe(true);
    expect(html.includes("Activer mes acheteurs")).toBe(true);

    // Valuation Studio & Saut-du-Loup Banner
    expect(html.includes("studioAddressInput")).toBe(true);
    expect(html.includes("calculateDynamicValuation")).toBe(true);
    expect(html.includes("updateAdjustment")).toBe(true);
    expect(html.includes("sautDuLoupBanner")).toBe(true);
    expect(html.includes("loadSautDuLoupCase")).toBe(true);

    // PPTX Generator Studio
    expect(html.includes("btnExportPptx")).toBe(true);
    expect(html.includes("exportPresentationPptx")).toBe(true);
    expect(html.includes("handleImageUpload")).toBe(true);
    expect(html.includes("fileCover")).toBe(true);
    expect(html.includes("fileInterior")).toBe(true);
    expect(html.includes("fileExterior")).toBe(true);
    expect(html.includes("filePlan")).toBe(true);

    // Neighbor modal & actions
    expect(html.includes("neighborModal")).toBe(true);
    expect(html.includes("openNeighborModal")).toBe(true);
    expect(html.includes("copyNeighborLetter")).toBe(true);
    expect(html.includes("printNeighborLetter")).toBe(true);
  });

  it("should calculate and document the Saut-du-Loup 18 vs 16 valuation delta (+513k CHF)", () => {
    const { DVPptxGenerator } = require("../src/fao_transactions/dv/dv_pptx_generator");
    const generator = new DVPptxGenerator();
    const caseStudy = generator.getSautDuLoupCaseStudy();

    // Subject property verified facts
    expect(caseStudy.subject.address).toBe("Chemin du Saut-du-Loup 18, 1225 Chêne-Bourg");
    expect(caseStudy.subject.parcel).toBe("4643");
    expect(caseStudy.subject.surfacePPE).toBe(73);
    expect(caseStudy.subject.weightedSurface).toBe(92.5);
    expect(caseStudy.subject.garden).toBe(250);

    // Anchor sale 16 verified facts (Deed 2026/628/0)
    expect(caseStudy.anchorSale16.address).toBe("Chemin du Saut-du-Loup 16, 1225 Chêne-Bourg");
    expect(caseStudy.anchorSale16.parcel).toBe("4642-104");
    expect(caseStudy.anchorSale16.price_chf).toBe(1620000);
    expect(caseStudy.anchorSale16.price_m2).toBe(17609);

    // August 2025 vs February 2026 delta
    expect(caseStudy.august2025Valuation.totalValuation).toBe(1266625);
    expect(caseStudy.february2026Valuation.totalValuation).toBe(1780000);
    expect(caseStudy.impactSummary.valueDeltaChf).toBe(513375);
    expect(caseStudy.impactSummary.valueDeltaPct).toBeGreaterThan(40);
  });

  it("should generate tailored D&V PPTX presentation with 15 slides and verified tokens", async () => {
    const { DVPptxGenerator, readZipEntries } = require("../src/fao_transactions/dv/dv_pptx_generator");
    const generator = new DVPptxGenerator();
    const caseStudy = generator.getSautDuLoupCaseStudy();

    const outputPath = path.resolve("data/exports/test_valuation_pptx.pptx");
    const res = await generator.generatePptx({
      outputPath,
      slideReplacements: caseStudy.pptxPayload,
      hideInternalInstructions: true
    });

    expect(res.success).toBe(true);
    expect(fs.existsSync(outputPath)).toBe(true);
    const fileBuf = fs.readFileSync(outputPath);
    expect(fileBuf.length).toBeGreaterThan(5000000); // Master template ~5.8 MB

    const entries = readZipEntries(fileBuf);
    expect(entries.size).toBe(90);

    // Verify all 15 slides exist
    for (let i = 1; i <= 15; i++) {
      expect(entries.has(`ppt/slides/slide${i}.xml`)).toBe(true);
    }

    // Slide 1: Owner & Address
    const s1 = entries.get("ppt/slides/slide1.xml")!.toString("utf8");
    expect(s1.includes("Sergio Brotons Mas")).toBe(true);
    expect(s1.includes("Saut-du-Loup 18")).toBe(true);

    // Slide 9: Anchor Comparable Saut-du-Loup 16
    const s9 = entries.get("ppt/slides/slide9.xml")!.toString("utf8");
    expect(s9.includes("Saut-du-Loup 16")).toBe(true);
    expect(s9.includes("1'620'000") || s9.includes("1’620’000")).toBe(true);

    // Slide 11: Base rate & Breakdown
    const s11 = entries.get("ppt/slides/slide11.xml")!.toString("utf8");
    expect(s11.includes("16’000") || s11.includes("16'000")).toBe(true);
    expect(s11.includes("92.5 m²")).toBe(true);

    // Slide 12: Total & Asking Range
    const s12 = entries.get("ppt/slides/slide12.xml")!.toString("utf8");
    expect(s12.includes("1’780’000") || s12.includes("1'780'000")).toBe(true);
    expect(s12.includes("1’750’000") || s12.includes("1'750'000")).toBe(true);
    expect(s12.includes("1’790’000") || s12.includes("1'790'000")).toBe(true);
  });

  it("should support custom image replacements across PPTX slides", async () => {
    const { DVPptxGenerator, readZipEntries } = require("../src/fao_transactions/dv/dv_pptx_generator");
    const generator = new DVPptxGenerator();
    const caseStudy = generator.getSautDuLoupCaseStudy();

    const dummyPng = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==";
    const outputPath = path.resolve("data/exports/test_image_replace.pptx");

    const res = await generator.generatePptx({
      outputPath,
      slideReplacements: caseStudy.pptxPayload,
      images: {
        "ppt/media/image.png": dummyPng
      }
    });

    expect(res.success).toBe(true);
    const entries = readZipEntries(fs.readFileSync(outputPath));
    const replaced = entries.get("ppt/media/image.png");
    expect(replaced).toBeDefined();
    expect(replaced!.length).toBe(70); // 1x1 test png size
  });
});
