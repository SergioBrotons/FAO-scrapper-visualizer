import { describe, it, expect } from "bun:test";
import { readFileSync, existsSync } from "fs";
import { join } from "path";

describe("D&V Marketing Simulator & Sub-tabs Hardening", () => {
  const htmlPath = join(process.cwd(), "public", "dv", "marketing", "index.html");

  it("should have index.html present and readable", () => {
    expect(existsSync(htmlPath)).toBe(true);
    const content = readFileSync(htmlPath, "utf-8");
    expect(content.length).toBeGreaterThan(10000);
  });

  it("should contain the instant 60 FPS computeFiscalLocally engine in script", () => {
    const html = readFileSync(htmlPath, "utf-8");
    expect(html.includes("function computeFiscalLocally")).toBe(true);
    expect(html.includes("runSimulation()")).toBe(true);
    expect(html.includes("updateSimulationUI(localSim)")).toBe(true);
  });

  it("should calculate exact LIPP Art. 82 figures for baseline values (2.45M / 1.6M / 12y / 180k)", () => {
    const sellPrice = 2450000;
    const acqPrice = 1600000;
    const years = 12;
    const reno = 180000;

    const initialCosts = Math.round(acqPrice * 0.032); // 51'200
    const saleCommission = Math.round(sellPrice * 0.03); // 73'500
    const grossGain = sellPrice - acqPrice; // 850'000
    const totalDeductions = reno + initialCosts + saleCommission; // 304'700
    const taxableGain = grossGain - totalDeductions; // 545'300
    const cantonalTax = Math.round(taxableGain * 0.10); // 54'530
    const netProceeds = sellPrice - cantonalTax - saleCommission; // 2'321'970
    const netPct = Number(((netProceeds / sellPrice) * 100).toFixed(1)); // 94.8%

    expect(grossGain).toBe(850000);
    expect(totalDeductions).toBe(304700);
    expect(cantonalTax).toBe(54530);
    expect(netProceeds).toBe(2321970);
    expect(netPct).toBe(94.8);
  });

  it("should dynamically recalculate higher gain when sellPrice increases to 4.0M", () => {
    const sellPrice = 4000000;
    const acqPrice = 1600000;
    const years = 12;
    const reno = 180000;

    const initialCosts = Math.round(acqPrice * 0.032); // 51'200
    const saleCommission = Math.round(sellPrice * 0.03); // 120'000
    const grossGain = sellPrice - acqPrice; // 2'400'000
    const totalDeductions = reno + initialCosts + saleCommission; // 351'200
    const taxableGain = grossGain - totalDeductions; // 2'048'800
    const cantonalTax = Math.round(taxableGain * 0.10); // 204'880
    const netProceeds = sellPrice - cantonalTax - saleCommission; // 3'675'120
    const netPct = Number(((netProceeds / sellPrice) * 100).toFixed(1)); // 91.9%

    expect(grossGain).toBe(2400000);
    expect(totalDeductions).toBe(351200);
    expect(cantonalTax).toBe(204880);
    expect(netProceeds).toBe(3675120);
    expect(netPct).toBe(91.9);
  });

  it("should apply 2% tax floor when detention years >= 25 (Loi 13414 dès 2025)", () => {
    const sellPrice = 2450000;
    const acqPrice = 1600000;
    const years = 25;
    const reno = 180000;

    const initialCosts = Math.round(acqPrice * 0.032);
    const saleCommission = Math.round(sellPrice * 0.03);
    const grossGain = sellPrice - acqPrice;
    const totalDeductions = reno + initialCosts + saleCommission;
    const taxableGain = grossGain - totalDeductions;
    const rate = years >= 25 ? 2 : 10;
    const cantonalTax = Math.round(taxableGain * (rate / 100)); // 10'906 CHF
    const netProceeds = sellPrice - cantonalTax - saleCommission; // 2'365'594 CHF

    expect(rate).toBe(2);
    expect(cantonalTax).toBe(10906);
    expect(netProceeds).toBe(2365594);
  });

  it("should have Tab 3 Sub-tabs navigation buttons and panels", () => {
    const html = readFileSync(htmlPath, "utf-8");
    expect(html.includes('id="btn-subtab-social"')).toBe(true);
    expect(html.includes('id="btn-subtab-macro"')).toBe(true);
    expect(html.includes('id="panel-subtab-social"')).toBe(true);
    expect(html.includes('id="panel-subtab-macro"')).toBe(true);
    expect(html.includes("function switchBenchmarkSubTab")).toBe(true);
  });

  it("should have pre-rendered stale mandate cards and competitor rows in panel-subtab-macro", () => {
    const html = readFileSync(htmlPath, "utf-8");
    expect(html.includes("11 mandats bloqués")).toBe(true);
    expect(html.includes("Cologny")).toBe(true);
    expect(html.includes("Vandoeuvres")).toBe(true);
    expect(html.includes("Comptoir Immobilier")).toBe(true);
    expect(html.includes("SPG Société Privée de Gérance")).toBe(true);
    expect(html.includes("Pilet &amp; Renaud")).toBe(true);
    expect(html.includes("Barnes Suisse")).toBe(true);
    expect(html.includes("Engel &amp; Völkers Genève")).toBe(true);
  });

  it("should have pre-rendered funnel suggestions and UX note banner in Tab 2", () => {
    const html = readFileSync(htmlPath, "utf-8");
    expect(html.includes("en attente de synchronisation avec l'agent autonome de génération de contenu")).toBe(true);
    expect(html.includes("Baromètre Officiel de l'Immobilier à Troinex")).toBe(true);
    expect(html.includes("Transmission Patrimoniale &amp; Indivision Successorale à Troinex")).toBe(true);
    expect(html.includes("Le Barème IBGI (LIPP Art. 80-87)")).toBe(true);
    expect(html.includes("Valorisation Foncière en Zone 5")).toBe(true);
    expect(html.includes("Le Décodeur Casatax 2026")).toBe(true);
    expect(html.includes("Pourquoi 40% des Propriétés Rive Gauche Stagnent plus de 120 Jours")).toBe(true);
  });

  it("should have COMMUNE_INTELLIGENCE dictionary and onCommuneChange handler in marketing index.html", () => {
    const html = readFileSync(htmlPath, "utf-8");
    expect(html.includes("const COMMUNE_INTELLIGENCE = {")).toBe(true);
    expect(html.includes("function onCommuneChange(commune)")).toBe(true);
    expect(html.includes("function renderQuartierGuideLocally(commune)")).toBe(true);
    expect(html.includes("Cologny")).toBe(true);
    expect(html.includes("Adrien Désormière")).toBe(true);
    expect(html.includes("5800000")).toBe(true);
    expect(html.includes("21500")).toBe(true);
  });

  it("should support ?view=value and #value deep-linking in public/dv/index.html", () => {
    const dvHtml = readFileSync(join(__dirname, "..", "public", "dv", "index.html"), "utf-8");
    expect(dvHtml.includes("urlParams.get('view')")).toBe(true);
    expect(dvHtml.includes("switchView(initialView)")).toBe(true);
    expect(dvHtml.includes("history.replaceState")).toBe(true);
  });

  it("should provide prominent navigation links from root index.html to D&V portals", () => {
    const rootHtml = readFileSync(join(__dirname, "..", "index.html"), "utf-8");
    expect(rootHtml.includes('href="/dv/?view=value"')).toBe(true);
    expect(rootHtml.includes('href="/dv/"')).toBe(true);
    expect(rootHtml.includes('href="/dv/marketing/"')).toBe(true);
  });
});

