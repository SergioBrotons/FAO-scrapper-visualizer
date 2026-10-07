import { join } from "path";
import { existsSync, readFileSync } from "fs";

export interface FiscalSimulationParams {
  selling_price_chf: number;
  acquisition_price_chf: number;
  years_held: number;
  commune?: string; // e.g. Cologny, Troinex, Vandoeuvres
  renovations_invested_chf?: number; // Impenses apportant une plus-value
  notary_and_acquisition_costs_chf?: number; // Frais d'acquisition initiaux
  agency_commission_pct?: number; // Honoraires de vente usuels (ex: 3%)
}

export interface FiscalBracket {
  years_held_max: number;
  rate_pct: number;
  label: string;
}

export interface FiscalSimulationResult {
  selling_price_chf: number;
  acquisition_price_chf: number;
  years_held: number;
  
  // Breakdown
  gross_capital_gain_chf: number;
  total_deductions_chf: number;
  deductions_breakdown: {
    renovations_chf: number;
    initial_acquisition_costs_chf: number;
    estimated_sale_fees_chf: number;
  };
  taxable_capital_gain_chf: number;
  
  // Tax outcome
  applicable_tax_rate_pct: number;
  bracket_label: string;
  next_bracket_years?: number;
  next_bracket_rate_pct?: number;
  tax_saving_if_waiting_chf?: number;
  cantonal_capital_gain_tax_chf: number;
  
  // Casatax 2026 Analysis for Buyer Demand
  casatax: {
    is_eligible: boolean;
    ceiling_2026_chf: number;
    buyer_max_rebate_chf: number;
    difference_to_ceiling_chf: number;
    market_sweet_spot_advice: string;
  };

  // Final Net Proceed
  estimated_net_seller_proceeds_chf: number;
  net_percentage_of_sale: number;

  // Inbound Marketing Hooks
  inbound_angles: {
    title: string;
    hook_sentence: string;
    actionable_cta: string;
    persona_recommendation: string;
  };
}

export class FiscalSimulationService {
  private rules: any;

  constructor(baseDir?: string) {
    const root = baseDir || process.cwd();
    const rulesPath = join(root, "data", "reference", "financial_rules.json");
    if (existsSync(rulesPath)) {
      try {
        this.rules = JSON.parse(readFileSync(rulesPath, "utf-8"));
      } catch (err) {
        console.error("[FiscalSimulationService] Failed to load financial_rules.json:", err);
      }
    }
  }

  public simulate(params: FiscalSimulationParams): FiscalSimulationResult {
    const sellPrice = Math.max(0, Number(params.selling_price_chf) || 0);
    const acqPrice = Math.max(0, Number(params.acquisition_price_chf) || 0);
    const years = Math.max(0, Number(params.years_held) || 0);
    const reno = Math.max(0, Number(params.renovations_invested_chf) || 0);
    
    // Default initial costs: 3.2% if not specified
    const initialCosts = params.notary_and_acquisition_costs_chf !== undefined
      ? Math.max(0, Number(params.notary_and_acquisition_costs_chf))
      : Math.round(acqPrice * 0.032);

    const commPct = params.agency_commission_pct !== undefined ? params.agency_commission_pct : 3.0;
    const saleCommission = Math.round(sellPrice * (commPct / 100));

    // Gross Capital Gain
    const grossGain = Math.max(0, sellPrice - acqPrice);

    // Total Legal Deductions (impenses + acquisition costs + sale fees)
    const totalDeductions = reno + initialCosts + saleCommission;
    const taxableGain = Math.max(0, grossGain - totalDeductions);

    // IBGI (LIPP Art. 80-87 / LCP art. 84) Brackets
    const brackets: FiscalBracket[] = this.rules?.impot_gains_immobiliers?.brackets || [
      { years_held_max: 2, rate_pct: 50, label: "< 2 ans (spéculatif)" },
      { years_held_max: 3, rate_pct: 40, label: "2 à 3 ans" },
      { years_held_max: 4, rate_pct: 30, label: "3 à 4 ans" },
      { years_held_max: 5, rate_pct: 20, label: "4 à 5 ans" },
      { years_held_max: 10, rate_pct: 15, label: "5 à 10 ans" },
      { years_held_max: 25, rate_pct: 10, label: "10 à 25 ans" },
      { years_held_max: 999, rate_pct: 2, label: "≥ 25 ans (taux plancher 2% dès 2025)" },
    ];

    let currentRate = 50;
    let currentLabel = "< 2 ans";
    let nextYears: number | undefined;
    let nextRate: number | undefined;

    for (let i = 0; i < brackets.length; i++) {
      if (years < brackets[i].years_held_max) {
        currentRate = brackets[i].rate_pct;
        currentLabel = brackets[i].label;
        if (i + 1 < brackets.length) {
          nextYears = brackets[i].years_held_max;
          nextRate = brackets[i + 1].rate_pct;
        }
        break;
      }
    }

    const cantonalTax = Math.round(taxableGain * (currentRate / 100));

    let taxSavingIfWaiting = 0;
    if (nextRate !== undefined && nextRate < currentRate) {
      const prospectiveTax = Math.round(taxableGain * (nextRate / 100));
      taxSavingIfWaiting = Math.max(0, cantonalTax - prospectiveTax);
    }

    // Casatax 2026 Analysis
    const casataxCeiling = this.rules?.casatax?.threshold_chf || 1394928;
    const casataxRebate = this.rules?.casatax?.tax_reduction_chf || 20924;
    const isCasataxEligible = sellPrice > 0 && sellPrice <= casataxCeiling;
    const diffCeiling = sellPrice - casataxCeiling;

    let casataxAdvice = "";
    if (isCasataxEligible) {
      casataxAdvice = `Votre bien est sous le plafond Casatax 2026 (CHF ${casataxCeiling.toLocaleString("fr-CH")}). Vos acquéreurs bénéficieront d'un abattement fiscal immédiat de CHF ${casataxRebate.toLocaleString("fr-CH")} et 50% sur la cédule hypothécaire, maximisant votre bassin d'acheteurs finançables.`;
    } else if (diffCeiling <= 80000) {
      casataxAdvice = `Votre prix dépasse le plafond Casatax de seulement CHF ${Math.round(diffCeiling).toLocaleString("fr-CH")}. Une négociation stratégique juste sous CHF ${casataxCeiling.toLocaleString("fr-CH")} ferait économiser CHF ${casataxRebate.toLocaleString("fr-CH")} à l'acheteur, déclenchant des offres fermes sans délai.`;
    } else {
      casataxAdvice = `Bien positionné au-delà du seuil Casatax (marché intermédiaire ou haut de gamme). L'argumentaire doit cibler des acquéreurs à fort apport personnel ou investisseurs patrimoniaux.`;
    }

    // Net Seller Proceeds
    const netProceeds = sellPrice - cantonalTax - saleCommission;
    const netPct = sellPrice > 0 ? Number(((netProceeds / sellPrice) * 100).toFixed(1)) : 0;

    // Tailored Inbound Angle
    let inboundTitle = "";
    let hookSentence = "";
    let actionableCta = "";
    let personaRec = "";

    const commune = (params.commune || "").trim();
    const isUltraPrestige = commune.toLowerCase().includes("cologny") || commune.toLowerCase().includes("vandoeuvres") || sellPrice >= 4500000;

    if (isUltraPrestige) {
      personaRec = "Adrien Désormière";
      const communeLabel = commune || "Rive Gauche";
      if (years >= 25) {
        inboundTitle = `Taux Plancher IBGI de 2% à ${communeLabel} (Détention ≥ 25 ans, Loi 13414 dès 2025)`;
        hookSentence = `Détention ≥ 25 ans : votre gain sur cette propriété de ${communeLabel} bénéficie du taux cantonal plancher de 2% (art. 84 LIPP).`;
        actionableCta = "Consulter Adrien Désormière pour sécuriser une valorisation patrimoniale confidentielle et orchestrer une diffusion off-market.";
      } else if (taxSavingIfWaiting > 15000 && nextYears) {
        inboundTitle = `Optimisation Fiscale ${communeLabel} : Économisez CHF ${taxSavingIfWaiting.toLocaleString("fr-CH")} en ajustant le calendrier`;
        hookSentence = `En signant l'acte authentique après le cap des ${nextYears} ans de détention, votre taux d'impôt chute de ${currentRate}% à ${nextRate}%.`;
        actionableCta = "Consulter Adrien Désormière pour synchroniser le calendrier d'arbitrage et le transfert de propriété à l'optimum fiscal.";
      } else {
        inboundTitle = `Valorisation d'Exception & Arbitrage Foncier à ${communeLabel}`;
        hookSentence = `Sur un prix net estimé à CHF ${sellPrice.toLocaleString("fr-CH")}, votre produit net en mains s'élève à CHF ${netProceeds.toLocaleString("fr-CH")} (${netPct}%).`;
        actionableCta = "Contacter Adrien Désormière pour une analyse de faisabilité foncière et mobiliser le réseau d'acquéreurs off-market qualifiés.";
      }
    } else {
      personaRec = "Sandra Bleeckx Vanhalst";
      const communeLabel = commune || "Rive Gauche";
      if (years >= 25) {
        inboundTitle = `Taux Plancher IBGI de 2% à ${communeLabel} (Détention ≥ 25 ans, Loi 13414 dès 2025)`;
        hookSentence = `Félicitations : vous avez franchi le cap des 25 ans de détention. Votre gain bénéficie du taux cantonal plancher de 2% (art. 84 LIPP).`;
        actionableCta = "Consulter Sandra Bleeckx Vanhalst pour sécuriser une estimation confidentielle et préparer un arbitrage patrimonial familial.";
      } else if (taxSavingIfWaiting > 15000 && nextYears) {
        inboundTitle = `Optimisation Fiscale : Économisez CHF ${taxSavingIfWaiting.toLocaleString("fr-CH")} en ajustant le calendrier`;
        hookSentence = `En signant l'acte authentique après le cap des ${nextYears} ans de détention, votre taux d'impôt chute de ${currentRate}% à ${nextRate}%.`;
        actionableCta = "Consulter Sandra Bleeckx Vanhalst pour caler la promesse de vente et le transfert de propriété à la date fiscale optimale.";
      } else {
        inboundTitle = `Valorisation & Arbitrage Foncier à ${communeLabel}`;
        hookSentence = `Sur un prix net estimé à CHF ${sellPrice.toLocaleString("fr-CH")}, votre produit net en mains s'élève à CHF ${netProceeds.toLocaleString("fr-CH")} (${netPct}%).`;
        actionableCta = `Consulter Sandra Bleeckx Vanhalst pour une estimation vénale rigoureuse basée sur les actes récents de ${communeLabel}.`;
      }
    }

    return {
      selling_price_chf: sellPrice,
      acquisition_price_chf: acqPrice,
      years_held: years,
      gross_capital_gain_chf: grossGain,
      total_deductions_chf: totalDeductions,
      deductions_breakdown: {
        renovations_chf: reno,
        initial_acquisition_costs_chf: initialCosts,
        estimated_sale_fees_chf: saleCommission
      },
      taxable_capital_gain_chf: taxableGain,
      applicable_tax_rate_pct: currentRate,
      bracket_label: currentLabel,
      next_bracket_years: nextYears,
      next_bracket_rate_pct: nextRate,
      tax_saving_if_waiting_chf: taxSavingIfWaiting,
      cantonal_capital_gain_tax_chf: cantonalTax,
      casatax: {
        is_eligible: isCasataxEligible,
        ceiling_2026_chf: casataxCeiling,
        buyer_max_rebate_chf: casataxRebate,
        difference_to_ceiling_chf: diffCeiling,
        market_sweet_spot_advice: casataxAdvice
      },
      estimated_net_seller_proceeds_chf: netProceeds,
      net_percentage_of_sale: netPct,
      inbound_angles: {
        title: inboundTitle,
        hook_sentence: hookSentence,
        actionable_cta: actionableCta,
        persona_recommendation: personaRec
      }
    };
  }
}
