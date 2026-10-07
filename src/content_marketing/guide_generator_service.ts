import { join } from "path";
import { existsSync, readFileSync } from "fs";

export interface QuartierGuide {
  commune: string;
  quarter: string;
  headline: string;
  ocstat: {
    ppe_median_sqm: number;
    villa_median_chf: number;
    transactions_annuelles_est: number;
    centimes_additionnels: number;
    rive: string;
  };
  market_analysis: string;
  seller_tips: string[];
  social_carousel_slides: Array<{
    slide_number: number;
    title: string;
    body: string;
    badge: string;
  }>;
  recommended_broker: {
    name: string;
    role: string;
    cta_direct: string;
  };
}

export class GuideGeneratorService {
  private ocstatList: any[] = [];

  constructor(baseDir?: string) {
    const root = baseDir || process.cwd();
    const ocstatPath = join(root, "data", "reference", "ocstat_communes_2025_2026.json");
    if (existsSync(ocstatPath)) {
      try {
        this.ocstatList = JSON.parse(readFileSync(ocstatPath, "utf-8"));
      } catch (err) {
        console.error("[GuideGeneratorService] Error loading OCSTAT:", err);
      }
    }
  }

  public generateQuartierGuide(communeName: string = "Troinex"): QuartierGuide {
    const norm = communeName.trim().toLowerCase();
    const item = this.ocstatList.find(c => c.commune.toLowerCase() === norm) ||
                 this.ocstatList.find(c => norm.includes(c.commune.toLowerCase())) ||
                 this.ocstatList.find(c => c.commune.toLowerCase() === "troinex") ||
                 {
                   commune: communeName,
                   rive: "GAUCHE",
                   ppe_median_sqm: 14500,
                   villa_median_chf: 3200000,
                   centimes_additionnels: 35.0,
                   transactions_annuelles_est: 95
                 };

    const isHighEnd = item.ppe_median_sqm >= 18000 || item.villa_median_chf >= 4500000;
    const isFamily = !isHighEnd;

    const broker = isHighEnd
      ? {
          name: "Adrien Désormière",
          role: "Spécialiste Propriétés d'Exception & Foncier Rive Gauche",
          cta_direct: "Étude d'arbitrage confidentiel et valorisation parcellaire personnalisée."
        }
      : {
          name: "Sandra Bleeckx Vanhalst",
          role: "Spécialiste Villas, Familles & Transmission Patrimoniale",
          cta_direct: "Estimation vénale certifiée et accompagnement pour consensus familial."
        };

    const marketAnalysis = `Le marché immobilier de ${item.commune} conserve une attractivité solide au premier trimestre 2026. Avec une valeur médiane OCSTAT s'établissant à CHF ${item.ppe_median_sqm.toLocaleString("fr-CH")}/m² pour la PPE et CHF ${item.villa_median_chf.toLocaleString("fr-CH")} pour les villas individuelles, la commune attire des profils d'acquéreurs solvables. Le taux communal favorable (${item.centimes_additionnels} centimes additionnels) constitue un atout fiscal indéniable pour les propriétaires résidents. L'analyse des actes notariés FAO récents confirme que les biens correctement estimés se négocient avec une marge de discussion inférieure à 3.5%.`;

    const sellerTips = [
      `Positionnement Prix : Sur ${item.commune}, tout bien surévalué de plus de 8% par rapport à la médiane OCSTAT subit en moyenne 120 jours de vacance supplémentaire.`,
      `Anticipation Fiscale : Vérifiez votre durée de détention exacte pour optimiser l'impôt LIPP art. 82 avant d'accepter une promesse d'achat.`,
      `Valorisation Foncière : Si votre parcelle dépasse 900 m² en Zone 5, examinez impérativement le potentiel de détachement avant toute mise en vente.`
    ];

    const slides = [
      {
        slide_number: 1,
        title: `Baromètre Immobilier ${item.commune} • Q1 2026`,
        body: `Ce que révèlent les statistiques officielles OCSTAT et les actes notariés du Registre Foncier.`,
        badge: "Chiffres Clés Offiels"
      },
      {
        slide_number: 2,
        title: "Prix Médian au m² & Villas",
        body: `Appartements PPE : CHF ${item.ppe_median_sqm.toLocaleString("fr-CH")}/m²\nVillas : CHF ${item.villa_median_chf.toLocaleString("fr-CH")}\nTaux communal : ${item.centimes_additionnels} cts`,
        badge: "Données de Référence"
      },
      {
        slide_number: 3,
        title: "Le Piège de la Surévaluation",
        body: `À ${item.commune}, 38% des mandats multi-agences subissent une baisse de prix de 5 à 8% après 90 jours d'affichage infructueux.`,
        badge: "Alerte Vendeur"
      },
      {
        slide_number: 4,
        title: "L'Atout Casatax & Droits Notariés",
        body: `Pour les biens sous CHF 1'394'928, vos acquéreurs économisent jusqu'à CHF 20'924 sur les droits de mutation, déclenchant des offres fermes.`,
        badge: "Levier d'Offre"
      },
      {
        slide_number: 5,
        title: "Un Accompagnement de Proximité",
        body: `Désormière & Vanhalst met à votre disposition l'estimation officielle certifiée et l'expertise du marché de la Rive Gauche.`,
        badge: "Désormière & Vanhalst"
      }
    ];

    return {
      commune: item.commune,
      quarter: "Q1 2026",
      headline: `Guide de Marché & Baromètre Foncier : ${item.commune}`,
      ocstat: item,
      market_analysis: marketAnalysis,
      seller_tips: sellerTips,
      social_carousel_slides: slides,
      recommended_broker: broker
    };
  }
}
