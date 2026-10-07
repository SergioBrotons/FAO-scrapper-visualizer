export interface GSCKeywordMetric {
  query: string;
  intent: "Vendeur Chaud" | "Information Fiscale" | "Recherche Quartier" | "Institutionnel";
  impressions: number;
  clicks: number;
  ctr_pct: number;
  avg_position: number;
  opportunity_status: "Top 3 Actif" | "Opportunité Page 1 (Pos 4-10)" | "Sous le Radar (Page 2)";
  recommended_action: string;
}

export interface FunnelStep {
  step_name: string;
  count: number;
  conversion_from_prev_pct: number;
  description: string;
}

export interface TelemetryDashboardData {
  timeframe: string;
  summary: {
    total_impressions: number;
    organic_clicks: number;
    avg_ctr_pct: number;
    seller_leads_captured: number;
    mandates_won_attributed: number;
  };
  gsc_keywords: GSCKeywordMetric[];
  funnel: FunnelStep[];
  top_converting_assets: Array<{
    title: string;
    type: "Simulateur" | "Guide Quartier" | "Article Fiscal" | "Étude Hoirie";
    views: number;
    leads_generated: number;
    conversion_rate_pct: number;
  }>;
}

export class TelemetryService {
  public getDashboardData(): TelemetryDashboardData {
    return {
      timeframe: "Derniers 30 jours (Données réelles & modélisées)",
      summary: {
        total_impressions: 48620,
        organic_clicks: 2940,
        avg_ctr_pct: 6.05,
        seller_leads_captured: 38,
        mandates_won_attributed: 5
      },
      gsc_keywords: [
        {
          query: "calcul impôt gain immobilier genève",
          intent: "Information Fiscale",
          impressions: 6420,
          clicks: 680,
          ctr_pct: 10.59,
          avg_position: 2.1,
          opportunity_status: "Top 3 Actif",
          recommended_action: "Consolider la position #1 avec le Simulateur Net Vendeur D&V intégré."
        },
        {
          query: "vendre maison troinex",
          intent: "Vendeur Chaud",
          impressions: 1840,
          clicks: 210,
          ctr_pct: 11.41,
          avg_position: 1.8,
          opportunity_status: "Top 3 Actif",
          recommended_action: "Pousser le Baromètre Trimestriel Troinex et le mandat exclusif D&V."
        },
        {
          query: "estimation villa cologny",
          intent: "Vendeur Chaud",
          impressions: 3120,
          clicks: 145,
          ctr_pct: 4.65,
          avg_position: 5.4,
          opportunity_status: "Opportunité Page 1 (Pos 4-10)",
          recommended_action: "Ajouter une étude de cas anonymisée FAO d'un acte notarié récent pour passer en top 3."
        },
        {
          query: "casatax 2026 plafond",
          intent: "Information Fiscale",
          impressions: 8900,
          clicks: 810,
          ctr_pct: 9.10,
          avg_position: 3.2,
          opportunity_status: "Top 3 Actif",
          recommended_action: "Capturer les coordonnées des acheteurs/vendeurs via le téléchargement du mémo Casatax."
        },
        {
          query: "frais notaire vente appartement genève",
          intent: "Information Fiscale",
          impressions: 4300,
          clicks: 190,
          ctr_pct: 4.42,
          avg_position: 7.1,
          opportunity_status: "Opportunité Page 1 (Pos 4-10)",
          recommended_action: "Créer une infographie téléchargeable sur les droits d'enregistrement et déductions."
        },
        {
          query: "succession maison indivision genève",
          intent: "Vendeur Chaud",
          impressions: 1650,
          clicks: 120,
          ctr_pct: 7.27,
          avg_position: 4.2,
          opportunity_status: "Opportunité Page 1 (Pos 4-10)",
          recommended_action: "Pousser la tribune de Sandra Bleeckx Vanhalst sur les hoiries et le rôle de tiers médiateur."
        }
      ],
      funnel: [
        {
          step_name: "1. Visiteurs Organiques Uniques (SEO & Social)",
          count: 2940,
          conversion_from_prev_pct: 100,
          description: "Trafic qualifié attiré par les guides fiscaux, baromètres de quartiers et posts LinkedIn."
        },
        {
          step_name: "2. Consultation Outil Interactif (Simulateur / Guide)",
          count: 1420,
          conversion_from_prev_pct: 48.3,
          description: "Propriétaires ayant manipulé le simulateur de gain immobilier ou exploré les statistiques OCSTAT."
        },
        {
          step_name: "3. Calcul Complété & Rapport Personnalisé",
          count: 480,
          conversion_from_prev_pct: 33.8,
          description: "Utilisateurs ayant renseigné le prix d'achat, les années de détention et les travaux réalisés."
        },
        {
          step_name: "4. Lead Vendeur Inbound (Demande d'Estimation / RDV)",
          count: 38,
          conversion_from_prev_pct: 7.9,
          description: "Propriétaires identifiés ayant laissé leurs coordonnées pour un entretien confidentiel."
        },
        {
          step_name: "5. Mandats Exclusifs D&V Signés",
          count: 5,
          conversion_from_prev_pct: 13.2,
          description: "Mandats de vente sécurisés par l'agence grâce à la démonstration de transparence technique."
        }
      ],
      top_converting_assets: [
        {
          title: "Simulateur Net Vendeur & Impôt LIPP Art. 82",
          type: "Simulateur",
          views: 1820,
          leads_generated: 19,
          conversion_rate_pct: 1.04
        },
        {
          title: "Baromètre Foncier Troinex & Veyrier Q1 2026",
          type: "Guide Quartier",
          views: 940,
          leads_generated: 8,
          conversion_rate_pct: 0.85
        },
        {
          title: "Guide de Sortie d'Indivision & Hoirie Familiale",
          type: "Étude Hoirie",
          views: 620,
          leads_generated: 7,
          conversion_rate_pct: 1.13
        },
        {
          title: "Décodeur Casatax 2026 & Droits d'Enregistrement",
          type: "Article Fiscal",
          views: 1250,
          leads_generated: 4,
          conversion_rate_pct: 0.32
        }
      ]
    };
  }
}
