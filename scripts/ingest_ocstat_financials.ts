import { Database } from "bun:sqlite";
import { readFileSync, existsSync } from "fs";
import { join } from "path";

const ROOT_DIR = process.cwd();
const DB_PATH = join(ROOT_DIR, "data/state/state.sqlite");
const OCSTAT_JSON_PATH = join(ROOT_DIR, "data/reference/ocstat_communes_2025_2026.json");
const FINANCIAL_RULES_PATH = join(ROOT_DIR, "data/reference/financial_rules.json");

if (!existsSync(DB_PATH)) {
  console.error(`Database not found at: ${DB_PATH}`);
  process.exit(1);
}

const db = new Database(DB_PATH);
db.exec("PRAGMA foreign_keys = ON;");
db.exec("PRAGMA journal_mode = WAL;");

console.log("----------------------------------------------------------------");
console.log("   CYTRIA GENEVA REAL ESTATE INTELLIGENCE: OCSTAT & FINANCIALS  ");
console.log("----------------------------------------------------------------\n");

// 1. Initialize Tables
console.log("1. Initializing schema tables...");

db.exec(`
  CREATE TABLE IF NOT EXISTS ocstat_communal_benchmarks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    commune_code INTEGER UNIQUE NOT NULL,
    commune TEXT NOT NULL,
    canton TEXT DEFAULT 'GE',
    rive TEXT,
    annee INTEGER DEFAULT 2025,
    prix_median_m2_ppe REAL,
    prix_moyen_m2_ppe REAL,
    prix_median_m2_maison REAL,
    prix_moyen_m2_maison REAL,
    taux_vacance_officiel_pct REAL,
    tendance_annuelle_pct REAL,
    volume_total_chf REAL,
    nb_transactions_annuel INTEGER,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );

  CREATE INDEX IF NOT EXISTS idx_ocstat_commune ON ocstat_communal_benchmarks(commune);
  CREATE INDEX IF NOT EXISTS idx_ocstat_code ON ocstat_communal_benchmarks(commune_code);

  CREATE TABLE IF NOT EXISTS financial_benchmarks (
    year INTEGER PRIMARY KEY,
    casatax_threshold_chf REAL NOT NULL,
    casatax_rebate_mutation_chf REAL NOT NULL,
    casatax_cedule_rebate_pct REAL DEFAULT 0.50,
    taux_technique_finma_pct REAL DEFAULT 0.05,
    charges_entretien_pct REAL DEFAULT 0.01,
    amortissement_annuel_pct REAL DEFAULT 0.01,
    fonds_propres_min_pct REAL DEFAULT 0.20,
    fonds_propres_hard_cash_min_pct REAL DEFAULT 0.10,
    ratio_tenue_charge_max_pct REAL DEFAULT 0.3333,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS financial_intelligence (
    transaction_id INTEGER PRIMARY KEY,
    commune TEXT,
    notice_date TEXT,
    price_chf REAL,
    surface_m2 REAL,
    price_per_m2_real REAL,
    ocstat_median_m2 REAL,
    price_vs_ocstat_ratio REAL,
    price_vs_ocstat_pct REAL,
    is_casatax_eligible INTEGER DEFAULT 0,
    casatax_savings_chf REAL DEFAULT 0,
    casatax_cliff_flag INTEGER DEFAULT 0,
    equity_min_required_chf REAL,
    equity_hard_cash_min_chf REAL,
    loan_amount_chf REAL,
    theoretical_annual_charge_chf REAL,
    min_gross_annual_income_chf REAL,
    deal_type_signal TEXT,
    is_hoirie INTEGER DEFAULT 0,
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE
  );

  CREATE INDEX IF NOT EXISTS idx_fi_casatax ON financial_intelligence(is_casatax_eligible);
  CREATE INDEX IF NOT EXISTS idx_fi_cliff ON financial_intelligence(casatax_cliff_flag);
  CREATE INDEX IF NOT EXISTS idx_fi_signal ON financial_intelligence(deal_type_signal);
  CREATE INDEX IF NOT EXISTS idx_fi_commune ON financial_intelligence(commune);
`);

console.log("   [OK] Tables and indexes created successfully.\n");

// 2. Ingest OCSTAT Benchmarks
console.log("2. Ingesting OCSTAT 45 Geneva Communes...");
const ocstatData = JSON.parse(readFileSync(OCSTAT_JSON_PATH, "utf-8"));

const insertOcstatStmt = db.prepare(`
  INSERT INTO ocstat_communal_benchmarks (
    commune_code, commune, canton, rive, annee,
    prix_median_m2_ppe, prix_moyen_m2_ppe,
    prix_median_m2_maison, prix_moyen_m2_maison,
    taux_vacance_officiel_pct, tendance_annuelle_pct,
    volume_total_chf, nb_transactions_annuel, updated_at
  ) VALUES (
    $commune_code, $commune, $canton, $rive, $annee,
    $prix_median_m2_ppe, $prix_moyen_m2_ppe,
    $prix_median_m2_maison, $prix_moyen_m2_maison,
    $taux_vacance_officiel_pct, $tendance_annuelle_pct,
    $volume_total_chf, $nb_transactions_annuel, CURRENT_TIMESTAMP
  )
  ON CONFLICT(commune_code) DO UPDATE SET
    commune=excluded.commune,
    prix_median_m2_ppe=excluded.prix_median_m2_ppe,
    prix_moyen_m2_ppe=excluded.prix_moyen_m2_ppe,
    prix_median_m2_maison=excluded.prix_median_m2_maison,
    prix_moyen_m2_maison=excluded.prix_moyen_m2_maison,
    taux_vacance_officiel_pct=excluded.taux_vacance_officiel_pct,
    tendance_annuelle_pct=excluded.tendance_annuelle_pct,
    volume_total_chf=excluded.volume_total_chf,
    nb_transactions_annuel=excluded.nb_transactions_annuel,
    updated_at=CURRENT_TIMESTAMP;
`);

const insertAllOcstat = db.transaction((rows: any[]) => {
  for (const row of rows) {
    insertOcstatStmt.run({
      $commune_code: row.commune_code,
      $commune: row.commune,
      $canton: row.canton || "GE",
      $rive: row.rive || "Gauche",
      $annee: row.annee || 2025,
      $prix_median_m2_ppe: row.prix_median_m2_ppe,
      $prix_moyen_m2_ppe: row.prix_moyen_m2_ppe,
      $prix_median_m2_maison: row.prix_median_m2_maison,
      $prix_moyen_m2_maison: row.prix_moyen_m2_maison,
      $taux_vacance_officiel_pct: row.taux_vacance_officiel_pct,
      $tendance_annuelle_pct: row.tendance_annuelle_pct,
      $volume_total_chf: row.volume_total_chf,
      $nb_transactions_annuel: row.nb_transactions_annuel,
    });
  }
});

insertAllOcstat(ocstatData);
console.log(`   [OK] Ingested ${ocstatData.length} Geneva communes.\n`);

// 3. Ingest Financial Benchmarks
console.log("3. Ingesting Financial Benchmarks (CASATAX & FINMA rules)...");
const finRules = JSON.parse(readFileSync(FINANCIAL_RULES_PATH, "utf-8"));
const annualSchedules = finRules.casatax.annual_schedules;

const insertFinStmt = db.prepare(`
  INSERT INTO financial_benchmarks (
    year, casatax_threshold_chf, casatax_rebate_mutation_chf,
    casatax_cedule_rebate_pct, taux_technique_finma_pct,
    charges_entretien_pct, amortissement_annuel_pct,
    fonds_propres_min_pct, fonds_propres_hard_cash_min_pct,
    ratio_tenue_charge_max_pct, updated_at
  ) VALUES (
    $year, $casatax_threshold_chf, $casatax_rebate_mutation_chf,
    $casatax_cedule_rebate_pct, $taux_technique_finma_pct,
    $charges_entretien_pct, $amortissement_annuel_pct,
    $fonds_propres_min_pct, $fonds_propres_hard_cash_min_pct,
    $ratio_tenue_charge_max_pct, CURRENT_TIMESTAMP
  )
  ON CONFLICT(year) DO UPDATE SET
    casatax_threshold_chf=excluded.casatax_threshold_chf,
    casatax_rebate_mutation_chf=excluded.casatax_rebate_mutation_chf,
    updated_at=CURRENT_TIMESTAMP;
`);

for (const [yearStr, sched] of Object.entries(annualSchedules) as [string, any][]) {
  const y = parseInt(yearStr);
  insertFinStmt.run({
    $year: y,
    $casatax_threshold_chf: sched.ceiling_price_chf,
    $casatax_rebate_mutation_chf: sched.max_rebate_mutation_chf,
    $casatax_cedule_rebate_pct: sched.cedule_rebate_pct || 0.50,
    $taux_technique_finma_pct: finRules.mortgage_affordability_finma.tenue_de_charge.theoretical_interest_rate_pct,
    $charges_entretien_pct: finRules.mortgage_affordability_finma.tenue_de_charge.maintenance_charges_pct,
    $amortissement_annuel_pct: finRules.mortgage_affordability_finma.tenue_de_charge.mandatory_amortization_annual_pct,
    $fonds_propres_min_pct: finRules.mortgage_affordability_finma.equity_requirements.min_equity_pct,
    $fonds_propres_hard_cash_min_pct: finRules.mortgage_affordability_finma.equity_requirements.min_hard_cash_pct,
    $ratio_tenue_charge_max_pct: finRules.mortgage_affordability_finma.tenue_de_charge.max_debt_to_income_ratio_pct,
  });
}
console.log("   [OK] Ingested CASATAX 2024, 2025, 2026 rules.\n");

// 4. Enrich All Transactions with OCSTAT & Financial Intelligence
console.log("4. Computing Financial & OCSTAT Intelligence on all transactions...");

// Preload communal benchmarks map for O(1) lookups
const communalMap = new Map<string, any>();
const allCommunes = db.query("SELECT * FROM ocstat_communal_benchmarks").all() as any[];
for (const c of allCommunes) {
  communalMap.set(c.commune.toLowerCase().trim(), c);
}

// Preload financial benchmark (default to 2025/2026)
const currentRules = db.query("SELECT * FROM financial_benchmarks ORDER BY year DESC LIMIT 1").get() as any;

// Fetch all transactions joined with enrichments
const query = `
  SELECT 
    t.id, t.commune, t.notice_date, t.property_type, t.nature,
    t.surface_m2, t.price_chf, t.seller, t.buyer, t.raw_text,
    e.surface_official_m2, e.price_per_m2
  FROM transactions t
  LEFT JOIN enrichments e ON t.id = e.transaction_id
  WHERE t.price_chf IS NOT NULL AND t.price_chf > 0
`;

const transactions = db.query(query).all() as any[];
console.log(`   Found ${transactions.length} monetized transactions to evaluate.`);

const insertFiStmt = db.prepare(`
  INSERT INTO financial_intelligence (
    transaction_id, commune, notice_date, price_chf, surface_m2,
    price_per_m2_real, ocstat_median_m2, price_vs_ocstat_ratio,
    price_vs_ocstat_pct, is_casatax_eligible, casatax_savings_chf,
    casatax_cliff_flag, equity_min_required_chf, equity_hard_cash_min_chf,
    loan_amount_chf, theoretical_annual_charge_chf, min_gross_annual_income_chf,
    deal_type_signal, is_hoirie, computed_at
  ) VALUES (
    $transaction_id, $commune, $notice_date, $price_chf, $surface_m2,
    $price_per_m2_real, $ocstat_median_m2, $price_vs_ocstat_ratio,
    $price_vs_ocstat_pct, $is_casatax_eligible, $casatax_savings_chf,
    $casatax_cliff_flag, $equity_min_required_chf, $equity_hard_cash_min_chf,
    $loan_amount_chf, $theoretical_annual_charge_chf, $min_gross_annual_income_chf,
    $deal_type_signal, $is_hoirie, CURRENT_TIMESTAMP
  )
  ON CONFLICT(transaction_id) DO UPDATE SET
    price_chf=excluded.price_chf,
    price_per_m2_real=excluded.price_per_m2_real,
    ocstat_median_m2=excluded.ocstat_median_m2,
    price_vs_ocstat_ratio=excluded.price_vs_ocstat_ratio,
    price_vs_ocstat_pct=excluded.price_vs_ocstat_pct,
    is_casatax_eligible=excluded.is_casatax_eligible,
    casatax_savings_chf=excluded.casatax_savings_chf,
    casatax_cliff_flag=excluded.casatax_cliff_flag,
    equity_min_required_chf=excluded.equity_min_required_chf,
    equity_hard_cash_min_chf=excluded.equity_hard_cash_min_chf,
    loan_amount_chf=excluded.loan_amount_chf,
    theoretical_annual_charge_chf=excluded.theoretical_annual_charge_chf,
    min_gross_annual_income_chf=excluded.min_gross_annual_income_chf,
    deal_type_signal=excluded.deal_type_signal,
    is_hoirie=excluded.is_hoirie,
    computed_at=CURRENT_TIMESTAMP;
`);

let casataxEligibleCount = 0;
let casataxCliffCount = 0;
let undervaluedCount = 0;
let hoirieCount = 0;

const runEnrichment = db.transaction((rows: any[]) => {
  for (const t of rows) {
    const rawText = (t.raw_text || "").toLowerCase();
    const seller = (t.seller || "").toLowerCase();
    const isHoirie = (rawText.includes("hoirie") || seller.includes("hoirie") || rawText.includes("succession")) ? 1 : 0;
    if (isHoirie) hoirieCount++;

    const communeKey = (t.commune || "").toLowerCase().trim();
    const ocstat = communalMap.get(communeKey) || communalMap.get("genève");

    const priceChf = t.price_chf;
    const surface = t.surface_official_m2 || t.surface_m2 || 0;
    const realPriceM2 = (surface > 0) ? (t.price_per_m2 || (priceChf / surface)) : null;

    // Detect typology (PPE vs House)
    const isPPE = (t.property_type && t.property_type.includes("PPE")) || (t.nature && t.nature.includes("PPE"));
    const ocstatMedianM2 = isPPE ? ocstat.prix_median_m2_ppe : ocstat.prix_median_m2_maison;

    let priceVsOcstatRatio: number | null = null;
    let priceVsOcstatPct: number | null = null;
    if (realPriceM2 && ocstatMedianM2 && realPriceM2 > 500) {
      priceVsOcstatRatio = Number((realPriceM2 / ocstatMedianM2).toFixed(3));
      priceVsOcstatPct = Number((((realPriceM2 - ocstatMedianM2) / ocstatMedianM2) * 100).toFixed(1));
    }

    // CASATAX evaluation
    const casataxCeiling = currentRules.casatax_threshold_chf;
    const isCasatax = (priceChf <= casataxCeiling) ? 1 : 0;
    if (isCasatax) casataxEligibleCount++;

    // Casatax Cliff: between threshold and threshold + 5%
    const isCliff = (!isCasatax && priceChf <= (casataxCeiling * 1.05)) ? 1 : 0;
    if (isCliff) casataxCliffCount++;

    // Total cash savings under CASATAX:
    // 1. Direct rebate on mutation tax (max ~20'903 CHF)
    // 2. 50% discount on mortgage deed constitution (~1'800 - 2'500 CHF)
    let casataxSavings = 0;
    if (isCasatax) {
      const standardMutationTax = priceChf * 0.03;
      const rebate = Math.min(standardMutationTax, currentRules.casatax_rebate_mutation_chf);
      const ceduleSavings = Math.min(priceChf * 0.80 * 0.0136 * 0.50, 3000);
      casataxSavings = Math.round(rebate + ceduleSavings);
    }

    // FINMA Affordability Underwriting
    const minEquity = Math.round(priceChf * currentRules.fonds_propres_min_pct);
    const hardCash = Math.round(priceChf * currentRules.fonds_propres_hard_cash_min_pct);
    const loanAmount = Math.round(priceChf * (1 - currentRules.fonds_propres_min_pct));

    // Annual theoretical debt service:
    // Interest (5%) + Maintenance (1%) + Amortization to 2/3 (1%) = 7%
    const annualRate = currentRules.taux_technique_finma_pct + currentRules.charges_entretien_pct + currentRules.amortissement_annuel_pct;
    const theoreticalAnnualCharge = Math.round(loanAmount * annualRate);
    const minGrossIncome = Math.round(theoreticalAnnualCharge / currentRules.ratio_tenue_charge_max_pct);

    // Deal Type Classification
    let dealSignal = "PRIX_MARCHE";
    if (isHoirie) {
      dealSignal = "HOIRIE_SOURCING";
    } else if (isCliff) {
      dealSignal = "CASATAX_CLIFF";
    } else if (priceVsOcstatPct !== null && priceVsOcstatPct <= -15) {
      dealSignal = "OPPORTUNITE_DECOTEE";
      undervaluedCount++;
    } else if (priceVsOcstatPct !== null && priceVsOcstatPct >= 25) {
      dealSignal = "SURCOTE_PREMIUM";
    }

    insertFiStmt.run({
      $transaction_id: t.id,
      $commune: t.commune,
      $notice_date: t.notice_date,
      $price_chf: priceChf,
      $surface_m2: surface,
      $price_per_m2_real: realPriceM2 ? Math.round(realPriceM2) : null,
      $ocstat_median_m2: ocstatMedianM2,
      $price_vs_ocstat_ratio: priceVsOcstatRatio,
      $price_vs_ocstat_pct: priceVsOcstatPct,
      $is_casatax_eligible: isCasatax,
      $casatax_savings_chf: casataxSavings,
      $casatax_cliff_flag: isCliff,
      $equity_min_required_chf: minEquity,
      $equity_hard_cash_min_chf: hardCash,
      $loan_amount_chf: loanAmount,
      $theoretical_annual_charge_chf: theoreticalAnnualCharge,
      $min_gross_annual_income_chf: minGrossIncome,
      $deal_type_signal: dealSignal,
      $is_hoirie: isHoirie,
    });
  }
});

runEnrichment(transactions);

console.log("   [OK] Computed intelligence for all transactions!");
console.log(`        - CASATAX Eligible (< CHF ${currentRules.casatax_threshold_chf.toLocaleString()}): ${casataxEligibleCount} transactions`);
console.log(`        - CASATAX Cliff Deals (Target for re-negotiation): ${casataxCliffCount} transactions`);
console.log(`        - Undervalued Deals (> 15% below OCSTAT): ${undervaluedCount} transactions`);
console.log(`        - Hoirie / Succession Mandates: ${hoirieCount} transactions\n`);

// 5. Verification Check
const sample = db.query(`
  SELECT 
    t.id, fi.commune, fi.price_chf, fi.price_per_m2_real, fi.ocstat_median_m2,
    fi.price_vs_ocstat_pct, fi.is_casatax_eligible, fi.casatax_savings_chf,
    fi.min_gross_annual_income_chf, fi.deal_type_signal
  FROM financial_intelligence fi
  JOIN transactions t ON fi.transaction_id = t.id
  ORDER BY fi.transaction_id DESC
  LIMIT 5
`).all();

console.log("5. Sample Enriched Intelligence Rows:");
console.table(sample);

db.close();
console.log("Ingestion & Enrichment Pipeline finished successfully!\n");
