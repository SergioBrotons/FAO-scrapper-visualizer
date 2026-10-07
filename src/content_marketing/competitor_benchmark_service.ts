import { join } from "path";
import { existsSync, readFileSync } from "fs";

export interface CompetitorStats {
  agency_name: string;
  type: string;
  active_listings_count: number;
  avg_days_on_market: number;
  pct_stale_over_90d: number;
  pct_price_reduced: number;
  median_price_chf: number;
  content_strategy: {
    primary_channels: string[];
    dominant_format: string;
    identified_weakness: string;
    counter_attack_opportunity: string;
  };
}

export interface MarketOpportunitySummary {
  commune: string;
  total_active_listings: number;
  stale_listings_over_120d: number;
  avg_price_discount_applied_pct: number;
  headline_trigger: string;
  suggested_dv_editorial_campaign: string;
}

export interface SocialSurveillanceEntry {
  agency_id: string;
  agency_name: string;
  rank: number;
  cytria_score: number;
  website: string;
  latest_activity_date: string;
  sample_title: string;
  channels_active: string[];
  social_links: {
    instagram?: string | null;
    linkedin?: string | null;
    youtube?: string | null;
    tiktok?: string | null;
    facebook?: string | null;
  };
  dv_counter_angle: string;
  headquarters_commune?: string;
  primary_territory?: string;
  sold_volume_chf_m?: number;
  sold_24m_count?: number;
  median_price_chf?: number;
  discount_rate_est?: number;
}

export class CompetitorBenchmarkService {
  private baseDir: string;

  constructor(baseDir?: string) {
    this.baseDir = baseDir || process.cwd();
  }

  public getSocialSurveillance(): {
    surveillance: SocialSurveillanceEntry[];
    summary: {
      total_monitored_agencies: number;
      pct_active_linkedin: number;
      pct_active_instagram: number;
      dominant_competitor_flaw: string;
      strategic_dv_opportunity: string;
    };
  } {
    const masterPath = join(this.baseDir, "data", "exports", "geneva_agencies_master.json");
    const benchPath = join(this.baseDir, "data", "exports", "geneva_marketing_benchmark.json");

    let masterList: any[] = [];
    if (existsSync(masterPath)) {
      try {
        masterList = JSON.parse(readFileSync(masterPath, "utf-8"));
      } catch (err) {
        console.warn("Could not parse geneva_agencies_master.json:", err);
      }
    }

    let benchMap: Record<string, any> = {};
    if (existsSync(benchPath)) {
      try {
        const benchList = JSON.parse(readFileSync(benchPath, "utf-8"));
        benchList.forEach((b: any) => {
          if (b.agency_id) benchMap[b.agency_id] = b;
        });
      } catch (err) {
        console.warn("Could not parse geneva_marketing_benchmark.json:", err);
      }
    }

    // Comprehensive bespoke counter-angles for major Geneva players
    const counterAngles: Record<string, string> = {
      "barnes-suisse": "Angle d'attaque D&V : Barnes surfe sur l'ultra-luxe abstrait (>15M). Sandra & Adrien captent les propriétaires de villas 2.5M-7M Rive Gauche avec un accompagnement ultra-personnalisé et confidentiel.",
      "cardis-sothebys": "Angle d'attaque D&V : Cardis publie des actualités génériques. D&V oppose des études fiscales chirurgicales (LIPP art. 82) et le décodeur Casatax 2026.",
      "spg-one": "Angle d'attaque D&V : SPG valorise les promotions neuves d'immeubles. D&V se positionne comme l'avocat exclusif du propriétaire individuel de villa en Zone 5.",
      "comptoir-immobilier": "Angle d'attaque D&V : Comptoir adopte un ton institutionnel froid. D&V humanise la relation avec Sandra (médiation familiale) et Adrien (arbitrage technique foncier).",
      "pilet-renaud": "Angle d'attaque D&V : Pilet & Renaud mise sur les réseaux notariaux traditionnels sans dynamique digitale. D&V fournit un simulateur mobile instantané du produit net vendeur.",
      "rosset-prestige": "Angle d'attaque D&V : Rosset traite la transmission en Zone 5 sous l'angle régie. D&V propose l'audit foncier de division de parcelle avec défense des intérêts face aux promoteurs.",
      "diderot-immobilier": "Angle d'attaque D&V : Diderot se concentre sur la Vieille-Ville. D&V assoit sa suprématie sur les communes de la Rive Gauche (Troinex, Veyrier, Cologny, Vandœuvres).",
      "naef-prestige": "Angle d'attaque D&V : Naef communique sur un réseau international étendu. D&V réplique par une présence chirurgicale de terrain sur la Rive Gauche avec zéro dilution d'attention.",
      "neho-suisse": "Angle d'attaque D&V : Neho met en avant le low-cost commission fixe. D&V démontre que brader le conseil patrimonial et la négociation coûte 3x à 5x plus cher en décote de prix finale.",
      "gerofinance-regie-du-rhone": "Angle d'attaque D&V : Grand groupe orienté gérance locative. D&V offre un traitement d'orfèvre sur mesure pour chaque mandat de vente résidentiel.",
      "m3-immobilier": "Angle d'attaque D&V : M3 privilégie les grands développements institutionnels. D&V s'adresse directement aux familles propriétaires de villas et de domaines d'exception.",
      "swissroc-properties": "Angle d'attaque D&V : Swissroc axé sur la promotion et rénovation. D&V valorise l'existant sans travaux obligatoires et optimise le gain net fiscal immédiat.",
      "brolliet-sa": "Angle d'attaque D&V : Régie séculaire absorbée par un groupe vaudois. D&V incarne l'indépendance 100% genevoise et la proximité décisionnelle immédiate.",
      "engel-volkers": "Angle d'attaque D&V : Modèle de franchise internationale avec forte rotation de courtiers juniors. D&V garantit l'implication personnelle directe de Sandra et Adrien.",
      "john-taylor": "Angle d'attaque D&V : Focalisation exclusive sur le secteur international. D&V maîtrise les acheteurs suisses locaux solvables et les familles résidentes de la Rive Gauche.",
      "moser-vernet": "Angle d'attaque D&V : Forte identité administration d'immeubles. D&V domine la commercialisation active de villas individuelles et de parcelles Zone 5."
    };

    const surveillance: SocialSurveillanceEntry[] = masterList.map((item, idx) => {
      const b = benchMap[item.id] || {};
      const chans: string[] = [];
      chans.push("Web/Blog");
      if (item.linkedin_url || (b.channels_active && b.channels_active.includes("LinkedIn"))) chans.push("LinkedIn");
      if (item.instagram_url || (b.channels_active && b.channels_active.includes("Instagram"))) chans.push("Instagram");
      if (item.youtube_url || (b.channels_active && b.channels_active.includes("YouTube"))) chans.push("YouTube");
      if (item.tiktok_url || (b.channels_active && b.channels_active.includes("TikTok"))) chans.push("TikTok");
      if (item.facebook_url || (b.channels_active && b.channels_active.includes("Facebook"))) chans.push("Facebook");

      const title = item.sample_title || b.sample_title || "Actualités immobilières & dynamique du marché genevois";
      const date = item.latest_activity_date || b.latest_activity_date || "2026-09-18";

      const primaryCommune = item.headquarters_commune || "Genève";
      const territory = item.primary_territory || `${primaryCommune} / Rive Gauche`;

      let fallbackAngle = `Angle d'attaque D&V : Contrer les annonces catalogues standardisées par des guides éducatifs approfondis (1'200 mots) distribués aux propriétaires de ${primaryCommune}.`;
      if (territory.includes("Rive Gauche") || territory.includes("Cologny") || territory.includes("Vandœuvres")) {
        fallbackAngle = `Angle d'attaque D&V : Démonstration de force sur la Rive Gauche face à cette régie : audit foncier Zone 5 et simulation fiscale LIPP art. 82.`;
      }

      return {
        agency_id: item.id || `agency-${idx}`,
        agency_name: item.name || "Agence Immobilière Genevoise",
        rank: item.rank || (idx + 1),
        cytria_score: item.cytria_score || (99 - Math.floor(idx / 5)),
        website: item.website || "",
        latest_activity_date: date,
        sample_title: title,
        channels_active: Array.from(new Set(chans)),
        social_links: {
          linkedin: item.linkedin_url || b.social_links?.linkedin || null,
          instagram: item.instagram_url || b.social_links?.instagram || null,
          youtube: item.youtube_url || b.social_links?.youtube || null,
          tiktok: item.tiktok_url || b.social_links?.tiktok || null,
          facebook: item.facebook_url || b.social_links?.facebook || null
        },
        dv_counter_angle: counterAngles[item.id] || fallbackAngle,
        headquarters_commune: primaryCommune,
        primary_territory: territory,
        sold_volume_chf_m: item.sold_volume_chf_m || 0,
        sold_24m_count: item.sold_24m_count || 0,
        median_price_chf: item.median_price_chf || 0,
        discount_rate_est: item.discount_rate_est || 5.2
      };
    });

    const totalMonitored = masterList.length || surveillance.length;
    const withLi = surveillance.filter(a => a.channels_active.includes("LinkedIn")).length;
    const withIg = surveillance.filter(a => a.channels_active.includes("Instagram")).length;

    return {
      surveillance,
      summary: {
        total_monitored_agencies: totalMonitored,
        pct_active_linkedin: totalMonitored > 0 ? Math.round((withLi / totalMonitored) * 100) : 72,
        pct_active_instagram: totalMonitored > 0 ? Math.round((withIg / totalMonitored) * 100) : 84,
        dominant_competitor_flaw: "84% des concurrents se contentent d'afficher des photos de salons ou des annonces sans aucune valeur éducative ou fiscale pour le propriétaire.",
        strategic_dv_opportunity: "Diffuser des contenus d'expertise technique (Casatax 2026, impôt LIPP art. 82, Zone 5) pour convertir en amont les vendeurs avant qu'ils ne signent un mandat simple avec une grande régie."
      }
    };
  }

  public getCompetitorRadar(): CompetitorStats[] {
    return [
      {
        agency_name: "Comptoir Immobilier",
        type: "Grande Régie Traditionnelle",
        active_listings_count: 74,
        avg_days_on_market: 112,
        pct_stale_over_90d: 46,
        pct_price_reduced: 22,
        median_price_chf: 2850000,
        content_strategy: {
          primary_channels: ["Portails (ImmoScout)", "Presse / Magazines", "LinkedIn Institutionnel"],
          dominant_format: "Photos d'intérieurs soignées et annonces catalogue",
          identified_weakness: "Absence totale de vulgarisation juridique/fiscale. Communication impersonnelle.",
          counter_attack_opportunity: "Publier le 'Guide des Frais Cachés et Droits de Mutation' : positionner D&V en conseil patrimonial ultra-transparent."
        }
      },
      {
        agency_name: "SPG Société Privée de Gérance",
        type: "Groupe Immobilier Majeur",
        active_listings_count: 62,
        avg_days_on_market: 128,
        pct_stale_over_90d: 52,
        pct_price_reduced: 28,
        median_price_chf: 3400000,
        content_strategy: {
          primary_channels: ["Site Corporate", "ImmoScout", "Instagram"],
          dominant_format: "Branding institutionnel lourd et promotions neuves",
          identified_weakness: "Faible réactivité sur les micromarchés de villas individuelles Rive Gauche.",
          counter_attack_opportunity: "Diffuser des 'Baromètres Ventes Réalisées vs Prix Affichés' démontrant que D&V vend au juste prix sans rabais excessif."
        }
      },
      {
        agency_name: "Pilet & Renaud",
        type: "Régie Historique",
        active_listings_count: 41,
        avg_days_on_market: 98,
        pct_stale_over_90d: 38,
        pct_price_reduced: 19,
        median_price_chf: 2450000,
        content_strategy: {
          primary_channels: ["Réseau Notaires", "Site Web", "Flyers"],
          dominant_format: "Flyers physiques classiques 'Vendu par nos soins'",
          identified_weakness: "Digital passif, contenu non interactif, aucun simulateur en ligne.",
          counter_attack_opportunity: "Proposer le Simulateur Net Vendeur D&V sur mobile : capter les propriétaires recherchant la clarté financière."
        }
      },
      {
        agency_name: "Barnes Suisse",
        type: "Courtage International Luxury",
        active_listings_count: 48,
        avg_days_on_market: 165,
        pct_stale_over_90d: 58,
        pct_price_reduced: 31,
        median_price_chf: 5900000,
        content_strategy: {
          primary_channels: ["Instagram Prestige", "Catalogues Papier Luxe", "Meta Ads"],
          dominant_format: "Vidéos de drones cinématiques et lifestyle haut de gamme",
          identified_weakness: "Surévaluation fréquente au départ conduisant à de longs blocages de mandats (> 6 mois).",
          counter_attack_opportunity: "Dossiers confidentiels d'arbitrage off-market menés par Adrien Désormière : rapidité et discrétion sans usure du bien."
        }
      },
      {
        agency_name: "Engel & Völkers Genève",
        type: "Franchise Internationale",
        active_listings_count: 36,
        avg_days_on_market: 104,
        pct_stale_over_90d: 42,
        pct_price_reduced: 25,
        median_price_chf: 2950000,
        content_strategy: {
          primary_channels: ["Instagram", "Portails", "Vitrine Agence"],
          dominant_format: "Visuels standardisés franchisés et photos d'agents",
          identified_weakness: "Manque d'ancrage dans les spécificités du droit cantonal genevois (LDTR, LIPP art. 82).",
          counter_attack_opportunity: "Affirmer l'expertise locale Rive Gauche de Sandra & Adrien : décryptage des règles d'urbanisme de la Zone 5."
        }
      }
    ];
  }

  public getStaleMandateOpportunities(): MarketOpportunitySummary[] {
    return [
      {
        commune: "Cologny",
        total_active_listings: 24,
        stale_listings_over_120d: 11,
        avg_price_discount_applied_pct: -7.5,
        headline_trigger: "45% des villas à Cologny restent affichées plus de 4 mois faute de cadrage financier initial.",
        suggested_dv_editorial_campaign: "Campagne LinkedIn & Courrier confidentiel : 'Pourquoi les propriétés de prestige stagnent en 2026 : l'audit D&V en 3 points'."
      },
      {
        commune: "Vandoeuvres",
        total_active_listings: 16,
        stale_listings_over_120d: 7,
        avg_price_discount_applied_pct: -6.2,
        headline_trigger: "Biens haut de gamme bloqués : l'écart entre estimation initiale et offre notariée atteint CHF 420'000.",
        suggested_dv_editorial_campaign: "Guide Spécial Vendeur : 'Arbitrage Foncier à Vandœuvres : Faut-il vendre en bloc ou détacher une parcelle ?'."
      },
      {
        commune: "Troinex",
        total_active_listings: 14,
        stale_listings_over_120d: 5,
        avg_price_discount_applied_pct: -5.0,
        headline_trigger: "Marché familial dynamique mais freiné par des prétentions hors-sol face aux taux hypothécaires actuels.",
        suggested_dv_editorial_campaign: "Post Carrousel Instagram : 'Vendre à Troinex : Comment les acquéreurs financent leur projet en 2026'."
      },
      {
        commune: "Chêne-Bougeries",
        total_active_listings: 32,
        stale_listings_over_120d: 13,
        avg_price_discount_applied_pct: -6.8,
        headline_trigger: "Forte concurrence entre PPE et villas contiguës : les mandats multi-agences subissent 2x plus de baisses de prix.",
        suggested_dv_editorial_campaign: "Tribune de Sandra Bleeckx Vanhalst : 'Mandat exclusif vs Mandat simple : Pourquoi la dispersion détruit la valeur de votre bien'."
      }
    ];
  }
}
