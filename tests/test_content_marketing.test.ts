import { describe, expect, test } from "bun:test";
import { AgencyConfigService } from "../src/content_marketing/agency_config_service.ts";
import { FiscalSimulationService } from "../src/content_marketing/fiscal_simulation_service.ts";
import { CompetitorBenchmarkService } from "../src/content_marketing/competitor_benchmark_service.ts";
import { TelemetryService } from "../src/content_marketing/telemetry_service.ts";
import { GuideGeneratorService } from "../src/content_marketing/guide_generator_service.ts";
import { FunnelContentService } from "../src/content_marketing/funnel_content_service.ts";

describe("Cytria Content Marketing & Seller Acquisition Engine", () => {
  const agencyService = new AgencyConfigService();
  const fiscalService = new FiscalSimulationService();
  const competitorService = new CompetitorBenchmarkService();
  const telemetryService = new TelemetryService();
  const guideService = new GuideGeneratorService();
  const funnelService = new FunnelContentService();

  test("AgencyConfigService loads D&V brand profile correctly", () => {
    const profile = agencyService.getProfile("desormiere_vanhalst");
    expect(profile.agency_id).toBe("desormiere_vanhalst");
    expect(profile.name).toBe("Désormière & Vanhalst");
    expect(profile.brand.primary_color).toBe("#00939D");
    expect(profile.brand.secondary_prestige).toBe("#004A4F");
    expect(profile.personas.length).toBeGreaterThanOrEqual(2);
    expect(profile.territory.focus_communes).toContain("Troinex");
  });

  test("AgencyConfigService lists white-label profiles", () => {
    const profiles = agencyService.listProfiles();
    expect(profiles.length).toBeGreaterThanOrEqual(2);
    expect(profiles.some(p => p.agency_id === "desormiere_vanhalst")).toBe(true);
    expect(profiles.some(p => p.agency_id === "template_white_label")).toBe(true);
  });

  test("FiscalSimulationService calculates LIPP Art. 82 brackets and net proceeds", () => {
    // 12 years held: 10% tax bracket
    const sim12 = fiscalService.simulate({
      selling_price_chf: 2450000,
      acquisition_price_chf: 1600000,
      years_held: 12,
      renovations_invested_chf: 180000
    });

    expect(sim12.applicable_tax_rate_pct).toBe(10);
    expect(sim12.gross_capital_gain_chf).toBe(850000);
    expect(sim12.taxable_capital_gain_chf).toBeLessThan(850000);
    expect(sim12.estimated_net_seller_proceeds_chf).toBeGreaterThan(2000000);
    expect(sim12.casatax.is_eligible).toBe(false); // 2.45M > 1.39M

    // 26 years held: 2% tax bracket floor (Loi 13414 dès 2025)
    const sim26 = fiscalService.simulate({
      selling_price_chf: 3000000,
      acquisition_price_chf: 1000000,
      years_held: 26,
      renovations_invested_chf: 200000
    });

    expect(sim26.applicable_tax_rate_pct).toBe(2);
    expect(sim26.cantonal_capital_gain_tax_chf).toBe(33560);
    expect(sim26.inbound_angles.title).toContain("Taux Plancher IBGI");

    // Under Casatax ceiling (e.g. 1.2M)
    const simCasa = fiscalService.simulate({
      selling_price_chf: 1200000,
      acquisition_price_chf: 900000,
      years_held: 6,
      renovations_invested_chf: 50000
    });

    expect(simCasa.casatax.is_eligible).toBe(true);
    expect(simCasa.applicable_tax_rate_pct).toBe(15);
  });

  test("CompetitorBenchmarkService provides radar data and stale listing triggers", () => {
    const radar = competitorService.getCompetitorRadar();
    expect(radar.length).toBeGreaterThanOrEqual(4);
    expect(radar.some(c => c.agency_name === "Comptoir Immobilier")).toBe(true);

    const stale = competitorService.getStaleMandateOpportunities();
    expect(stale.length).toBeGreaterThanOrEqual(3);
    expect(stale.some(s => s.commune === "Troinex")).toBe(true);
  });

  test("TelemetryService reports GSC keywords and full conversion funnel", () => {
    const data = telemetryService.getDashboardData();
    expect(data.summary.total_impressions).toBeGreaterThan(10000);
    expect(data.gsc_keywords.length).toBeGreaterThanOrEqual(5);
    expect(data.funnel.length).toBe(5);
    expect(data.funnel[4].step_name).toContain("Mandats Exclusifs");
  });

  test("GuideGeneratorService compiles official OCSTAT data and 5 social slides", () => {
    const guide = guideService.generateQuartierGuide("Troinex");
    expect(guide.commune).toBe("Troinex");
    expect(guide.ocstat.ppe_median_sqm).toBeGreaterThan(0);
    expect(guide.social_carousel_slides.length).toBe(5);
    expect(guide.recommended_broker.name).toBe("Sandra Bleeckx Vanhalst");
  });

  test("FunnelContentService provides TOFU, MOFU, BOFU suggestions with live Cytria metrics", () => {
    const result = funnelService.getFunnelSuggestions({ commune: "Troinex" });
    expect(result.commune).toBe("Troinex");
    expect(result.ppe_median_sqm).toBeGreaterThan(0);
    expect(result.suggestions.length).toBeGreaterThanOrEqual(5);

    const stages = result.suggestions.map(s => s.stage);
    expect(stages).toContain("TOFU");
    expect(stages).toContain("MOFU");
    expect(stages).toContain("BOFU");

    const hoirieIdea = result.suggestions.find(s => s.id === "tofu_succession_famille");
    expect(hoirieIdea?.target_persona).toBe("Sandra Bleeckx Vanhalst");
    expect(hoirieIdea?.data_anchor).toContain("successions familiales");
  });

  test("FunnelContentService generates complete 1'200+ word inbound guide with real FAO comparables", () => {
    const fullGuide = funnelService.generateFullGuide("tofu_succession_famille", "Troinex");
    expect(fullGuide.title).toContain("Sortie d'Indivision & Succession");
    expect(fullGuide.author.name).toBe("Sandra Bleeckx Vanhalst");
    expect(fullGuide.key_metrics.length).toBeGreaterThanOrEqual(3);
    expect(fullGuide.recent_fao_transactions.length).toBeGreaterThanOrEqual(1);
    expect(fullGuide.chapters.length).toBeGreaterThanOrEqual(3);
    expect(fullGuide.common_pitfalls.length).toBeGreaterThanOrEqual(3);
    expect(fullGuide.final_call_to_action.contact_email).toContain("@desormiere-vanhalst.ch");
  });

  test("CompetitorBenchmarkService loads real Geneva social surveillance and counter angles", () => {
    const social = competitorService.getSocialSurveillance();
    expect(social.summary.total_monitored_agencies).toBeGreaterThanOrEqual(10);
    expect(social.surveillance.length).toBeGreaterThanOrEqual(10);
    expect(social.surveillance.some(s => s.agency_id === "barnes-suisse")).toBe(true);
    expect(social.surveillance.some(s => s.channels_active.includes("LinkedIn"))).toBe(true);
    expect(social.summary.dominant_competitor_flaw.length).toBeGreaterThan(20);
    expect(social.summary.strategic_dv_opportunity.length).toBeGreaterThan(20);
  });
});

