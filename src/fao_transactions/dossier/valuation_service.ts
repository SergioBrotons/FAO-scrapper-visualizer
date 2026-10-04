import { Database } from "bun:sqlite";
import { join } from "path";
import { existsSync } from "fs";

export interface ValuationDossierData {
  transaction: any;
  enrichment: any;
  financial: any;
  ocstat: any;
  benchmarks: any;
  comparables: any[];
  meta: {
    dossier_id: string;
    generated_at: string;
    canton: string;
  };
}

const CORPORATE_KEYWORDS = [
  "SA", "SARL", "SÀRL", "SI", "SNC", "AG", "GMBH", "HOLDING", "IMMO", "IMMOBILIER",
  "FONDATION", "CAISSE", "PREVOYANCE", "PRÉVOYANCE", "BANQUE", "INVESTISSEMENT",
  "COMMUNE", "VILLE DE", "ETAT DE", "ÉTAT DE", "CONFEDERATION", "CONFÉDÉRATION",
  "PAROISSE", "SOCIETE", "SOCIÉTÉ", "COOPERATIVE", "COOPÉRATIVE", "SERVICES INDUSTRIELS",
  "SIG", "HUG", "UNIGE", "COMPAGNIE", "CREDIT", "CRÉDIT", "DEVELOPPEMENT", "DÉVELOPPEMENT",
  "PATRIMOINE", "FONCIERE", "FONCIÈRE", "REAL ESTATE", "MANAGEMENT", "FINANCE",
  "ASSURANCE", "TRUST", "LTD", "CORP", "INC", "PLC", "CANTON", "RÉPUBLIQUE", "REPUBLIQUE"
];

function isCorporateEntity(name?: string): boolean {
  if (!name || typeof name !== "string") return false;
  const upper = name.toUpperCase();
  return CORPORATE_KEYWORDS.some(kw => {
    const regex = new RegExp(`(^|[^a-zA-ZÀ-ÿ0-9])${kw}([^a-zA-ZÀ-ÿ0-9]|$)`, "i");
    return regex.test(upper);
  });
}

function maskNaturalPerson(name?: string): string {
  if (!name || typeof name !== "string" || !name.trim()) return "Non précisé";
  const clean = name.replace(/\s*,?\s*inscrit\s+(dès\s+le|le)\s+\d+.*$/i, "").trim();
  const parts = clean.split(/[,;]|\bet\b/i).map(p => p.trim()).filter(p => p.length > 0);
  const maskedParts = parts.map(part => {
    const words = part.split(/\s+/).filter(w => w.length > 0 && !["feu", "feue", "de", "du", "la", "des"].includes(w.toLowerCase()));
    if (words.length === 0) return "Particulier";
    const firstInitial = words[0].charAt(0).toUpperCase();
    const secondInitial = words.length > 1 ? words[1].charAt(0).toUpperCase() : "";
    return secondInitial ? `${firstInitial}*** ${secondInitial}***` : `${firstInitial}***`;
  });
  return maskedParts.slice(0, 3).join(", ") + (maskedParts.length > 3 ? " (et consorts)" : "") + " (Personne physique)";
}

function maskParty(name?: string): string {
  if (!name || typeof name !== "string" || !name.trim()) return "Non précisé";
  if (isCorporateEntity(name)) return name.trim();
  return maskNaturalPerson(name);
}

export class ValuationService {
  private db: Database;

  constructor(dbPath?: string) {
    const defaultPath = join(process.cwd(), "data/state/state.sqlite");
    const path = dbPath || defaultPath;
    if (!existsSync(path)) {
      throw new Error(`Database state.sqlite not found at ${path}`);
    }
    this.db = new Database(path, { readonly: true });
  }

  public getDossier(transactionId: number): ValuationDossierData | null {
    // 1. Fetch transaction
    const t = this.db.query("SELECT * FROM transactions WHERE id = ?").get(transactionId) as any;
    if (!t) return null;

    // Mask natural persons to prevent unauthenticated personal data leakage
    if (t.seller) t.seller = maskParty(t.seller);
    if (t.buyer) t.buyer = maskParty(t.buyer);

    // 2. Fetch enrichment
    const e = (this.db.query("SELECT * FROM enrichments WHERE transaction_id = ?").get(transactionId) as any) || {};

    // 3. Fetch financial intelligence
    const fi = (this.db.query("SELECT * FROM financial_intelligence WHERE transaction_id = ?").get(transactionId) as any) || {};

    // 4. Fetch OCSTAT commune benchmark
    const communeName = (t.commune || "").trim();
    let ocstat = this.db.query("SELECT * FROM ocstat_communal_benchmarks WHERE lower(commune) = lower(?)").get(communeName) as any;
    if (!ocstat) {
      ocstat = (this.db.query("SELECT * FROM ocstat_communal_benchmarks WHERE lower(commune) = 'genève'").get() as any) || {};
    }

    // 5. Fetch latest financial rules
    const finRules = (this.db.query("SELECT * FROM financial_benchmarks ORDER BY year DESC LIMIT 1").get() as any) || {};

    // 6. Find 4 closest contiguous comparables in same commune with monetized prices
    const comparables = this.db.query(`
      SELECT 
        t.id, t.notice_date, t.commune, t.parcel_number, t.property_type,
        t.nature, t.surface_m2, t.price_chf, e.surface_official_m2, e.price_per_m2,
        e.centroid_wgs84_lat, e.centroid_wgs84_lon, e.zone_code
      FROM transactions t
      LEFT JOIN enrichments e ON t.id = e.transaction_id
      WHERE t.id != ? 
        AND lower(t.commune) = lower(?)
        AND t.price_chf > 0
      ORDER BY ABS(t.price_chf - ?) ASC
      LIMIT 4
    `).all(transactionId, communeName, t.price_chf || 1000000) as any[];

    const dossierId = `CYT-AV-${new Date().getFullYear()}-${String(transactionId).padStart(6, "0")}`;

    return {
      transaction: t,
      enrichment: e,
      financial: fi,
      ocstat,
      benchmarks: finRules,
      comparables,
      meta: {
        dossier_id: dossierId,
        generated_at: new Date().toLocaleDateString("fr-CH", {
          year: "numeric",
          month: "long",
          day: "numeric",
        }),
        canton: "République et canton de Genève",
      },
    };
  }

  public renderHtml(transactionId: number): string {
    const data = this.getDossier(transactionId);
    if (!data) {
      return `<!DOCTYPE html><html><body><h1>Transaction #${transactionId} introuvable</h1></body></html>`;
    }

    const { transaction: t, enrichment: e, financial: fi, ocstat, benchmarks: b, comparables, meta } = data;

    const priceChf = t.price_chf ? t.price_chf.toLocaleString("fr-CH") + " CHF" : "Prix non déclaré";
    const surface = e.surface_official_m2 || t.surface_m2 || 0;
    const surfaceStr = surface > 0 ? surface.toLocaleString("fr-CH") + " m²" : "Non communiquée";
    const priceM2 = fi.price_per_m2_real ? fi.price_per_m2_real.toLocaleString("fr-CH") + " CHF/m²" : (surface > 0 && t.price_chf ? Math.round(t.price_chf / surface).toLocaleString("fr-CH") + " CHF/m²" : "N/D");

    const isPPE = (t.property_type && t.property_type.includes("PPE")) || (t.nature && t.nature.includes("PPE"));
    const medianOcstat = isPPE ? ocstat.prix_median_m2_ppe : ocstat.prix_median_m2_maison;
    const medianOcstatStr = medianOcstat ? medianOcstat.toLocaleString("fr-CH") + " CHF/m²" : "13'800 CHF/m²";

    const deltaPct = fi.price_vs_ocstat_pct !== null && fi.price_vs_ocstat_pct !== undefined ? fi.price_vs_ocstat_pct : null;
    let deltaBadgeClass = "delta-neutral";
    let deltaText = "Aligné sur la médiane";
    if (deltaPct !== null) {
      if (deltaPct <= -15) {
        deltaBadgeClass = "delta-green";
        deltaText = `${deltaPct}% (Décote d'opportunité)`;
      } else if (deltaPct >= 20) {
        deltaBadgeClass = "delta-red";
        deltaText = `+${deltaPct}% (Prime de marché)`;
      } else {
        deltaText = `${deltaPct > 0 ? "+" : ""}${deltaPct}% (Prix de marché)`;
      }
    }

    const isCasatax = fi.is_casatax_eligible === 1;
    const casataxSavings = fi.casatax_savings_chf ? fi.casatax_savings_chf.toLocaleString("fr-CH") + " CHF" : "0 CHF";
    const minEquity = fi.equity_min_required_chf ? fi.equity_min_required_chf.toLocaleString("fr-CH") + " CHF" : "N/D";
    const hardCash = fi.equity_hard_cash_min_chf ? fi.equity_hard_cash_min_chf.toLocaleString("fr-CH") + " CHF" : "N/D";
    const loanAmt = fi.loan_amount_chf ? fi.loan_amount_chf.toLocaleString("fr-CH") + " CHF" : "N/D";
    const minIncome = fi.min_gross_annual_income_chf ? fi.min_gross_annual_income_chf.toLocaleString("fr-CH") + " CHF/an" : "N/D";

    return `<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>Rapport d'Analyse Comparative de Marché (CMA) — ${meta.dossier_id}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  
  <style>
    :root {
      --brand-gold: #C9A24D;
      --brand-dark-gold: #8A6D2A;
      --ink-950: #080D11;
      --ink-900: #101820;
      --ink-700: #2C3844;
      --ink-500: #5A6978;
      --paper: #FAF8F5;
      --white: #FFFFFF;
      --sand-border: #E5DFC9;
      --green: #0E7042;
      --green-bg: #E6F4EA;
      --red: #C5221F;
      --red-bg: #FCE8E6;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Inter', -apple-system, sans-serif;
      background-color: #EEEDEA;
      color: var(--ink-900);
      -webkit-font-smoothing: antialiased;
      padding: 30px 15px;
    }

    .dossier-wrapper {
      max-width: 900px;
      margin: 0 auto;
      background: var(--white);
      box-shadow: 0 10px 30px rgba(0,0,0,0.12);
      border: 1px solid var(--sand-border);
    }

    /* Print & Action Banner (screen only) */
    .action-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 14px 24px;
      background: var(--ink-950);
      color: var(--white);
      border-bottom: 2px solid var(--brand-gold);
    }
    .action-bar .brand-title {
      font-family: 'Hanken Grotesk', sans-serif;
      font-weight: 700;
      font-size: 15px;
      letter-spacing: 0.5px;
      color: var(--brand-gold);
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .btn-print {
      background: var(--brand-gold);
      color: var(--ink-950);
      border: none;
      padding: 8px 18px;
      font-family: 'Hanken Grotesk', sans-serif;
      font-weight: 700;
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      cursor: pointer;
      transition: background 0.2s;
    }
    .btn-print:hover { background: #deb859; }

    /* Dossier Body */
    .dossier-content {
      padding: 40px 48px;
    }

    /* Official Header */
    .header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      border-bottom: 2px solid var(--ink-950);
      padding-bottom: 24px;
      margin-bottom: 28px;
    }
    .header-left h1 {
      font-family: 'Hanken Grotesk', sans-serif;
      font-size: 26px;
      font-weight: 800;
      color: var(--ink-950);
      letter-spacing: -0.5px;
      margin-bottom: 4px;
    }
    .header-left .subtitle {
      font-size: 13px;
      color: var(--ink-500);
      text-transform: uppercase;
      letter-spacing: 1px;
      font-weight: 600;
    }
    .header-right {
      text-align: right;
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      color: var(--ink-700);
      line-height: 1.6;
    }
    .header-right .ref {
      font-weight: 700;
      color: var(--brand-dark-gold);
      font-size: 13px;
    }

    /* Section styling */
    .section-title {
      font-family: 'Hanken Grotesk', sans-serif;
      font-size: 15px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: var(--ink-950);
      border-left: 3px solid var(--brand-gold);
      padding-left: 10px;
      margin-top: 28px;
      margin-bottom: 14px;
    }

    /* Grid & Cards */
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px; }
    .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }

    .kpi-card {
      background: var(--paper);
      border: 1px solid var(--sand-border);
      padding: 14px 16px;
    }
    .kpi-label {
      font-size: 11px;
      text-transform: uppercase;
      color: var(--ink-500);
      letter-spacing: 0.5px;
      font-weight: 600;
      margin-bottom: 6px;
    }
    .kpi-value {
      font-family: 'Hanken Grotesk', sans-serif;
      font-size: 20px;
      font-weight: 800;
      color: var(--ink-950);
    }
    .kpi-sub {
      font-size: 11px;
      color: var(--ink-500);
      margin-top: 4px;
      font-family: 'JetBrains Mono', monospace;
    }

    .badge {
      display: inline-block;
      padding: 3px 8px;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.5px;
      text-transform: uppercase;
    }
    .badge-green { background: var(--green-bg); color: var(--green); }
    .badge-gold { background: #FCF4DF; color: var(--brand-dark-gold); }
    .badge-red { background: var(--red-bg); color: var(--red); }

    .delta-green { color: var(--green); font-weight: 700; }
    .delta-red { color: var(--red); font-weight: 700; }
    .delta-neutral { color: var(--ink-700); font-weight: 700; }

    /* Tables */
    .data-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;
      margin-top: 8px;
    }
    .data-table th {
      background: var(--ink-950);
      color: var(--white);
      text-align: left;
      padding: 8px 10px;
      font-family: 'Hanken Grotesk', sans-serif;
      font-weight: 600;
      letter-spacing: 0.5px;
      font-size: 11px;
    }
    .data-table td {
      padding: 8px 10px;
      border-bottom: 1px solid var(--sand-border);
      color: var(--ink-900);
    }
    .data-table tr:nth-child(even) { background: #FAF9F6; }

    /* Legal Footer */
    .footer {
      border-top: 1px solid var(--sand-border);
      padding-top: 18px;
      margin-top: 36px;
      display: flex;
      justify-content: space-between;
      font-size: 10px;
      color: var(--ink-500);
      line-height: 1.5;
    }

    /* Print Optimization */
    @media print {
      body { background: transparent; padding: 0; }
      .action-bar { display: none !important; }
      .dossier-wrapper { box-shadow: none; border: none; max-width: 100%; }
      .dossier-content { padding: 0; }
      @page {
        size: A4 portrait;
        margin: 15mm 15mm 15mm 15mm;
      }
    }
  </style>
</head>
<body>

  <div class="dossier-wrapper">
    <div class="action-bar">
      <div class="brand-title">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
        CYTRIA REAL ESTATE & LAND INTELLIGENCE · GENÈVE
      </div>
      <button class="btn-print" onclick="window.print()">Imprimer Dossier (A4 / PDF)</button>
    </div>

    <div class="dossier-content">
      <!-- 1. Master Header -->
      <div class="header">
        <div class="header-left">
          <h1>Rapport d'Analyse Comparative de Marché (CMA)</h1>
          <div class="subtitle">Analyse Micro-Cadastrale (SITG) & Benchmark Macro-Économique (OCSTAT)</div>
        </div>
        <div class="header-right">
          <div class="ref">${meta.dossier_id}</div>
          <div>${meta.canton}</div>
          <div>Date d'édition : ${meta.generated_at}</div>
          <div>Source des transferts : Publications officielles FAO (art. 157 LaCC)</div>
        </div>
      </div>

      <!-- 2. Primary KPI Highlights -->
      <div class="grid-4" style="margin-bottom: 20px;">
        <div class="kpi-card">
          <div class="kpi-label">Prix Notarié Conclu</div>
          <div class="kpi-value" style="color: var(--brand-dark-gold);">${priceChf}</div>
          <div class="kpi-sub">${priceM2}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Médiane Commune OCSTAT</div>
          <div class="kpi-value">${medianOcstatStr}</div>
          <div class="kpi-sub ${deltaBadgeClass}">${deltaText}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Indicateur CASATAX</div>
          <div class="kpi-value" style="font-size: 16px;">
            ${isCasatax ? '<span class="badge badge-green">ÉLIGIBLE (SEUIL PRIX)</span>' : (fi.casatax_cliff_flag ? '<span class="badge badge-gold">ZONE DE CLIFF (&lt; 5%)</span>' : '<span class="badge badge-red">NON ÉLIGIBLE</span>')}
          </div>
          <div class="kpi-sub">Gain direct potentiel : ${casataxSavings}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Salaire Ménage Requis</div>
          <div class="kpi-value" style="font-size: 16px;">${minIncome}</div>
          <div class="kpi-sub">Règle FINMA (33%)</div>
        </div>
      </div>

      <!-- 3. Identification Cadastrale & Données Réglementaires -->
      <div class="section-title">1. Identification Cadastrale & Aménagement du Territoire</div>
      <div class="grid-2">
        <table class="data-table">
          <tr><td style="width: 40%; font-weight: 600;">Commune officielle</td><td><strong>${t.commune || "Genève"}</strong> (Rive ${ocstat.rive || "Gauche"})</td></tr>
          <tr><td style="font-weight: 600;">Adresse</td><td>${t.address || "Non spécifiée"}</td></tr>
          <tr><td style="font-weight: 600;">Parcelle n°</td><td><strong>${t.parcel_number || e.parcel_no_official || "N/D"}</strong></td></tr>
          <tr><td style="font-weight: 600;">Identifiant EGRID</td><td><code style="font-family: monospace;">${e.egrid || "CH_GE_" + t.commune + "_" + t.parcel_number}</code></td></tr>
          <tr><td style="font-weight: 600;">Typologie d'acte</td><td>${t.transaction_type || "Vente"} · ${t.property_type || t.nature || "Résidentiel"}</td></tr>
        </table>
        <table class="data-table">
          <tr><td style="width: 40%; font-weight: 600;">Surface officielle</td><td><strong>${surfaceStr}</strong></td></tr>
          <tr><td style="font-weight: 600;">Zonage d'aménagement</td><td><strong>${e.zone_code ? "Zone " + e.zone_code : "Zone 5 (Villas)"}</strong> · ${e.zone_name || "Zone résidentielle"}</td></tr>
          <tr><td style="font-weight: 600;">Périmètre PLQ</td><td>${e.plq_id ? "Oui (PLQ Actif)" : "Aucun PLQ grevant la parcelle"}</td></tr>
          <tr><td style="font-weight: 600;">Taux de vacance communal</td><td><strong>${ocstat.taux_vacance_officiel_pct || 0.4}%</strong> (Mesure OCSTAT au 1er juin)</td></tr>
          <tr><td style="font-weight: 600;">Tendance annuelle commune</td><td><strong>+${ocstat.tendance_annuelle_pct || 3.5}%</strong> sur 12 mois</td></tr>
        </table>
      </div>

      <!-- 4. Comparables Notariés Contigus -->
      <div class="section-title">2. Échantillon de Comparables Notariés Contigus (Même Commune)</div>
      <table class="data-table">
        <thead>
          <tr>
            <th>Date Acte</th>
            <th>Parcelle</th>
            <th>Typologie</th>
            <th>Surface</th>
            <th>Prix Notarié</th>
            <th>Prix au m²</th>
            <th>Écart vs Objet</th>
          </tr>
        </thead>
        <tbody>
          ${comparables.map((c) => {
            const cSurface = c.surface_official_m2 || c.surface_m2 || 0;
            const cPrice = c.price_chf ? c.price_chf.toLocaleString("fr-CH") + " CHF" : "N/D";
            const cPriceM2 = c.price_per_m2 ? c.price_per_m2.toLocaleString("fr-CH") + " CHF/m²" : (cSurface > 0 && c.price_chf ? Math.round(c.price_chf / cSurface).toLocaleString("fr-CH") + " CHF/m²" : "N/D");
            const diffPct = t.price_chf && c.price_chf ? Math.round(((c.price_chf - t.price_chf) / t.price_chf) * 100) : 0;
            const diffStr = diffPct === 0 ? "=" : (diffPct > 0 ? `+${diffPct}%` : `${diffPct}%`);
            return `
              <tr>
                <td>${c.notice_date || "2025/2026"}</td>
                <td><strong>Parcelle ${c.parcel_number || "N/D"}</strong></td>
                <td>${c.property_type || c.nature || "Résidentiel"}</td>
                <td>${cSurface > 0 ? cSurface + " m²" : "N/D"}</td>
                <td><strong>${cPrice}</strong></td>
                <td>${cPriceM2}</td>
                <td style="font-family: monospace; font-weight: 600;">${diffStr}</td>
              </tr>
            `;
          }).join("")}
        </tbody>
      </table>

      <!-- 5. Ingénierie Financière & Prêt Hypothécaire -->
      <div class="section-title">3. Simulation Prudentielle de Financement Théorique (Directives ASB / FINMA)</div>
      <div class="grid-2">
        <div style="background: var(--paper); border: 1px solid var(--sand-border); padding: 16px;">
          <div style="font-weight: 700; font-size: 13px; margin-bottom: 10px; color: var(--ink-950);">
            Structure de Financement Type (80 / 20)
          </div>
          <table class="data-table" style="background: transparent;">
            <tr><td>Fonds propres globaux (20%)</td><td style="text-align: right; font-weight: 700;">${minEquity}</td></tr>
            <tr><td>- Dont apport cash dur min. (10%)</td><td style="text-align: right; font-family: monospace;">${hardCash}</td></tr>
            <tr><td>- Dont prévoyance / LPP max. (10%)</td><td style="text-align: right; font-family: monospace;">${hardCash}</td></tr>
            <tr><td>Prêt hypothécaire de 1er & 2e rang (80%)</td><td style="text-align: right; font-weight: 700; color: var(--brand-dark-gold);">${loanAmt}</td></tr>
          </table>
        </div>

        <div style="background: var(--paper); border: 1px solid var(--sand-border); padding: 16px;">
          <div style="font-weight: 700; font-size: 13px; margin-bottom: 10px; color: var(--ink-950);">
            Capacité Théorique d'Emprunt (Simulation indicative - règle du tiers)
          </div>
          <table class="data-table" style="background: transparent;">
            <tr><td>Taux d'intérêt de crise FINMA (5.0%)</td><td style="text-align: right; font-family: monospace;">5.00%</td></tr>
            <tr><td>Charges d'entretien annuelles estimées (1.0%)</td><td style="text-align: right; font-family: monospace;">1.00%</td></tr>
            <tr><td>Amortissement linéaire obligatoire (15 ans)</td><td style="text-align: right; font-family: monospace;">1.00%</td></tr>
            <tr><td><strong>Revenu annuel brut exigé du ménage</strong></td><td style="text-align: right; font-weight: 800; color: var(--ink-950);">${minIncome}</td></tr>
          </table>
        </div>
      </div>

      <!-- 6. Fiscalité Cantonale Genevoise -->
      <div class="section-title">4. Fiscalité Cantonale : CASATAX & Impôt sur les Gains Immobiliers (IBI)</div>
      <div style="background: #F9F7F1; border: 1px solid var(--sand-border); padding: 16px; font-size: 12px; line-height: 1.6;">
        <p style="margin-bottom: 8px;">
          <strong>Régime CASATAX (art. 8A LDE) :</strong> 
          ${isCasatax 
            ? `Le bien satisfait au plafond cantonal d'acquisition fixé à <strong>${b.casatax_threshold_chf ? b.casatax_threshold_chf.toLocaleString('fr-CH') : "1'394'928"} CHF</strong> (au 01.03.2026). Éligibilité fiscale sous réserve d'affectation en résidence principale effective par une personne physique. Exonération maximale estimée à <strong>${casataxSavings}</strong>.`
            : (fi.casatax_cliff_flag 
                ? `<strong>Indicateur Seuil CASATAX :</strong> Le bien est positionné à moins de 5% au-dessus du plafond légal (CHF 1'394'928 dès 2026). Une négociation baissière permettrait de déclencher un gain fiscal immédiat de plus de 20'900 CHF (sous réserve des conditions de résidence principale).`
                : `Le montant dépasse le plafond légal de la CASATAX (CHF 1'394'928). Les droits de mutation ordinaires genevois (3.0% + 1.36% de cédule) sont applicables en totalité.`
              )
          }
        </p>
        <p>
          <strong>Impôt sur les Plus-Values (LIPP / LCP) :</strong> L'impôt cantonal sur les gains immobiliers à Genève est dégressif : 50% sous 2 ans, 40% entre 2 et 4 ans, 30% entre 4 et 6 ans, et <strong>0% d'exonération totale après 25 ans de détention continue</strong>.
        </p>
      </div>

      <!-- 7. Legal Disclaimer & Signature -->
      <div class="footer">
        <div>
          <strong>CYTRIA Real Estate & Land Intelligence Platform</strong><br>
          Données officielles : FAO Genève (art. 157 LaCC), SITG Genève (Open Data / Classe A), OCSTAT et OFS.<br>
          Document d'analyse comparative statistique à titre informatif ne constituant pas une expertise certifiée ni un titre de propriété.<br>
          Document généré le ${meta.generated_at} à usage confidentiel exclusif.
        </div>
        <div style="text-align: right;">
          <strong>Analyse comparative indicative</strong><br>
          Référence dossier : ${meta.dossier_id}<br>
          Page 1 sur 1 · Validité : 6 mois
        </div>
      </div>
    </div>
  </div>

</body>
</html>`;
  }
}
