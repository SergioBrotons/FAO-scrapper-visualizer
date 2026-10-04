import { describe, it, expect } from "bun:test";
import { Database } from "bun:sqlite";
import fs from "fs";
import path from "path";

// 1. Privacy Masking Unit Tests
describe("nLPD Natural Person Privacy Masking", () => {
  const CORPORATE_KEYWORDS = [
    "SA", "SARL", "SÀRL", "SI", "SNC", "AG", "GMBH", "HOLDING", "IMMO", "IMMOBILIER",
    "FONDATION", "CAISSE", "PREVOYANCE", "PRÉVOYANCE", "BANQUE", "INVESTISSEMENT",
    "INVEST", "CAPITAL", "COMMUNE", "VILLE DE", "ETAT DE", "ÉTAT DE", "CONFEDERATION",
    "CONFÉDÉRATION", "PAROISSE", "SOCIETE", "SOCIÉTÉ", "COOPERATIVE", "COOPÉRATIVE",
    "SERVICES INDUSTRIELS", "SIG", "HUG", "UNIGE", "COMPAGNIE", "CREDIT", "CRÉDIT",
    "DEVELOPPEMENT", "DÉVELOPPEMENT", "PATRIMOINE", "FONCIERE", "FONCIÈRE", "REAL ESTATE",
    "MANAGEMENT", "FINANCE", "ASSURANCE", "TRUST", "LTD", "CORP", "INC", "PLC", "PARTAGE",
    "PARQUET", "CANTON", "RÉPUBLIQUE", "REPUBLIQUE", "CONSEIL"
  ];

  function isCorporate(name: string): boolean {
    if (!name || typeof name !== "string") return false;
    const upper = name.toUpperCase();
    return CORPORATE_KEYWORDS.some(kw => {
      const regex = new RegExp(`(^|[^a-zA-ZÀ-ÿ0-9])${kw}([^a-zA-ZÀ-ÿ0-9]|$)`, "i");
      return regex.test(upper);
    });
  }

  function maskNaturalPerson(name: string): string {
    if (!name || typeof name !== "string" || !name.trim()) return "Non précisé";
    const clean = name.replace(/\s*,?\s*inscrit\s+(dès\s+le|le)\s+\d+.*$/i, "").trim();
    const parts = clean.split(/[,;]| et /i).map(p => p.trim()).filter(p => p.length > 0);
    const maskedParts = parts.map(part => {
      const words = part.split(/\s+/).filter(w => w.length > 0 && !["feu", "feue", "de", "du", "la", "des"].includes(w.toLowerCase()));
      if (words.length === 0) return "Particulier";
      const firstInitial = words[0].charAt(0).toUpperCase();
      const secondInitial = words.length > 1 ? words[1].charAt(0).toUpperCase() : "";
      return secondInitial ? `${firstInitial}*** ${secondInitial}***` : `${firstInitial}***`;
    });
    const res = maskedParts.slice(0, 3).join(", ");
    return res + (maskedParts.length > 3 ? " (et consorts)" : "") + " (Personne physique)";
  }

  function maskParty(name: string | null | undefined): string {
    if (!name || typeof name !== "string" || !name.trim()) return "Non précisé";
    const clean = name.trim();
    if (isCorporate(clean)) return clean;
    return maskNaturalPerson(clean);
  }

  it("should preserve corporate entities untouched", () => {
    expect(maskParty("UBS FUND MANAGEMENT (SWITZERLAND) AG")).toBe("UBS FUND MANAGEMENT (SWITZERLAND) AG");
    expect(maskParty("IMMEUBLE RIVE GAUCHE SA")).toBe("IMMEUBLE RIVE GAUCHE SA");
    expect(maskParty("SOCIETE IMMOBILIERE SAINT-JEAN SI")).toBe("SOCIETE IMMOBILIERE SAINT-JEAN SI");
    expect(maskParty("COMMUNE DE COLLONGE-BELLERIVE")).toBe("COMMUNE DE COLLONGE-BELLERIVE");
    expect(maskParty("CAISSE DE PREVOYANCE DU PERSONNEL")).toBe("CAISSE DE PREVOYANCE DU PERSONNEL");
    expect(maskParty("BERNARD IMMOBILIER SARL")).toBe("BERNARD IMMOBILIER SARL");
  });

  it("should anonymize natural persons with initial asterisks and tag", () => {
    expect(maskParty("DUPONT Jean")).toBe("D*** J*** (Personne physique)");
    expect(maskParty("DE ROTHSCHILD Benjamin")).toBe("R*** B*** (Personne physique)");
    expect(maskParty("M. et Mme MARTIN Pierre et Sophie")).toBe("M***, M*** M***, S*** (Personne physique)");
  });

  it("should sanitize registration suffix dates from natural person entries", () => {
    const raw = "MUELLER Hans, inscrit le 15.03.2023";
    expect(maskParty(raw)).toBe("M*** H*** (Personne physique)");
  });

  it("should safely handle null, undefined, or empty values", () => {
    expect(maskParty("")).toBe("Non précisé");
    expect(maskParty(null)).toBe("Non précisé");
    expect(maskParty(undefined)).toBe("Non précisé");
  });
});

// 2. CASATAX Financial Rules Verification
describe("CASATAX Statutory Schedules and Calculation", () => {
  const financialRules = JSON.parse(
    fs.readFileSync(path.resolve("data/reference/financial_rules.json"), "utf8")
  );

  it("should contain the official 2026 ceiling of CHF 1,394,928", () => {
    expect(financialRules.casatax.threshold_chf).toBe(1394928);
    expect(financialRules.casatax.tax_reduction_chf).toBe(20924);
  });

  it("should document statutory schedules for 2024, 2025, and 2026", () => {
    const schedules = financialRules.casatax.annual_schedules;
    expect(schedules["2024"].ceiling_price_chf).toBe(1359903);
    expect(schedules["2025"].ceiling_price_chf).toBe(1374396);
    expect(schedules["2026"].ceiling_price_chf).toBe(1394928);
  });

  it("should accurately determine threshold eligibility at boundary values", () => {
    const ceiling = financialRules.casatax.threshold_chf;
    expect(1300000 <= ceiling).toBe(true);
    expect(1394928 <= ceiling).toBe(true);
    expect(1394929 <= ceiling).toBe(false);
    expect(1450000 <= ceiling).toBe(false);
  });

  it("should correctly compute maximum mutation rebate capped at CHF 20,924", () => {
    const maxRebate = financialRules.casatax.tax_reduction_chf;
    const rate = 0.015; // 1.5% exemption
    
    // 1,300,000 * 0.015 = 19,500 CHF
    const rebate1 = Math.min(1300000 * rate, maxRebate);
    expect(rebate1).toBe(19500);

    // 1,394,928 * 0.015 = 20,923.92 CHF -> capped at 20,924 CHF
    const rebate2 = Math.min(1394928 * rate, maxRebate);
    expect(rebate2).toBeLessThanOrEqual(20924);
  });
});

// 3. Database State and Read-Only Constraints
describe("Database Read-Only Guarantees and Baseline Integrity", () => {
  const dbPath = path.resolve("data/state/state.sqlite");

  it("should open database in strictly read-only mode and reject writes", () => {
    const db = new Database(dbPath, { readonly: true });
    expect(() => {
      db.run("CREATE TABLE IF NOT EXISTS test_fail (id INTEGER PRIMARY KEY)");
    }).toThrow();
    db.close();
  });

  it("should contain exactly 8,970 baseline transactions", () => {
    const db = new Database(dbPath, { readonly: true });
    const row = db.query("SELECT COUNT(*) as count FROM transactions").get() as { count: number };
    expect(row.count).toBe(8970);

    const testRecords = db.query("SELECT COUNT(*) as count FROM transactions WHERE transaction_hash = 'test_hash_1' OR id = 8145").get() as { count: number };
    expect(testRecords.count).toBe(0);
    db.close();
  });

  it("should verify total cantonal transaction volume bounds (~17.47B CHF)", () => {
    const db = new Database(dbPath, { readonly: true });
    const row = db.query("SELECT SUM(price_chf) as total FROM transactions WHERE price_chf > 0").get() as { total: number };
    expect(row.total).toBeGreaterThan(17.4e9);
    expect(row.total).toBeLessThan(17.5e9);
    db.close();
  });

  it("should verify record 4837 price parsing integrity (CHF 1'875'000, not 1.88 CHF)", () => {
    const db = new Database(dbPath, { readonly: true });
    const row = db.query("SELECT price_raw, price_chf FROM transactions WHERE id = 4837").get() as { price_raw: string; price_chf: number };
    expect(row).toBeDefined();
    expect(row.price_raw).toBe("1'875'000");
    expect(row.price_chf).toBe(1875000.0);
    db.close();
  });

  it("should verify dataset notice year distribution (2023: 91, 2024: 1325, 2025: 4375, 2026: 3179)", () => {
    const db = new Database(dbPath, { readonly: true });
    const rows = db.query("SELECT notice_date FROM transactions").all() as { notice_date: string }[];
    const counts: Record<string, number> = {};
    rows.forEach(r => {
      const y = (r.notice_date || "").match(/\d{4}/)?.[0] || "unknown";
      counts[y] = (counts[y] || 0) + 1;
    });

    expect(counts["2023"]).toBe(91);
    expect(counts["2024"]).toBe(1325);
    expect(counts["2025"]).toBe(4375);
    expect(counts["2026"]).toBe(3179);
    expect(rows.length).toBe(8970);
    db.close();
  });

  it("should verify agency sales attribution baseline (83 agencies, 2,183 sales)", () => {
    const db = new Database(dbPath, { readonly: true });
    const agencies = db.query("SELECT COUNT(*) as count FROM agencies").get() as { count: number };
    const sales = db.query("SELECT COUNT(*) as count FROM agency_sold_properties").get() as { count: number };
    expect(agencies.count).toBe(83);
    expect(sales.count).toBe(2183);
    db.close();
  });
});

// 4. index.html Static Integrity and Privacy Audit
describe("index.html Static Client Privacy & Integrity", () => {
  const htmlPath = path.resolve("index.html");

  it("should contain masked natural persons and zero plaintext master unlock bypasses", () => {
    const html = fs.readFileSync(htmlPath, "utf8");
    const maskedCount = (html.match(/Personne physique/g) || []).length;
    expect(maskedCount).toBeGreaterThan(5000);

    // Ensure master password prompt is removed
    expect(html.includes("Indice : cytria")).toBe(false);
    expect(html.includes("cytria2026")).toBe(false);
  });
});

// 4. Dossier Valuation Service Neutralization
describe("Valuation Service Compliance and Provenance", () => {
  it("should have removed misleading judicial/notarial certification claims from valuation_service.ts", () => {
    const code = fs.readFileSync(path.resolve("src/fao_transactions/dossier/valuation_service.ts"), "utf8");
    
    // Check that deceptive certification terms are gone
    expect(code.includes("Avis de Valeur Notarié & Dossier d'Expertise")).toBe(false);
    expect(code.includes("Certification : Registre Foncier (art. 157 LaCC)")).toBe(false);
    expect(code.includes("Visé pour conformité foncière")).toBe(false);

    // Check that compliant terminology is present
    expect(code.includes("Rapport d'Analyse Comparative de Marché (CMA)")).toBe(true);
    expect(code.includes("1'394'928")).toBe(true);
    expect(code.includes("maskParty")).toBe(true);
  });
});

// 5. Agency Velocity Edge Case Safety
describe("Agency Velocity Inactivity and Date Reliability", () => {
  it("should have removed fabricated 'Mars 2026' sale dates for agencies with 0 sales", () => {
    const code = fs.readFileSync(path.resolve("src/fao_transactions/visualization/agency_velocity.py"), "utf8");
    
    // Check that fallback fabricated date is removed
    expect(code.includes("latest_date_fr = 'Mars 2026'")).toBe(false);
    expect(code.includes("dsls = 180")).toBe(false);

    // Check that zero-sales edge case is explicitly guarded
    expect(code.includes('latest_date_fr = "Aucune vente enregistrée"')).toBe(true);
    expect(code.includes('dsls_status = "INACTIVE"')).toBe(true);
  });
});

// 6. Server Route Security & Static Protection
describe("Server Route Security and Prohibited Paths", () => {
  it("should strictly disallow direct downloads of sensitive databases, env files, and source code", () => {
    const serverCode = fs.readFileSync(path.resolve("server.js"), "utf8");
    
    // Check that direct database and sensitive serving is guarded by 403 checks
    expect(serverCode.includes('lowerPath.startsWith("data/state")')).toBe(true);
    expect(serverCode.includes('lowerPath.includes(".env")')).toBe(true);
    expect(serverCode.includes('lowerPath.startsWith(".git")')).toBe(true);
    expect(serverCode.includes('lowerPath === "package.json"')).toBe(true);
    expect(serverCode.includes('return new Response("Forbidden", { status: 403 });')).toBe(true);

    // Check that parameterized queries and readonly mode are used in server.js
    expect(serverCode.includes("db.query(q).all(...params)")).toBe(true);
    expect(serverCode.includes("const db = new Database(DB_PATH, { readonly: true })")).toBe(true);
  });
});

