import { Database } from "bun:sqlite";
import { join } from "path";

export interface ToolDefinition {
  name: string;
  description: string;
  parameters: {
    type: "object";
    properties: Record<string, { type: string; description: string; enum?: string[] }>;
    required?: string[];
  };
}

export class CopilotToolsService {
  private db: Database;

  constructor(dbPath?: string) {
    const path = dbPath || join(process.cwd(), "data", "state", "state.sqlite");
    this.db = new Database(path);
  }

  // List of tool definitions for MiniMax / Anthropic Tool Calling
  public getToolDefinitions(): ToolDefinition[] {
    return [
      {
        name: "search_fao_comparables",
        description: "Recherche des transactions immobilières officielles réelles enregistrées au Registre Foncier (FAO Genève). Utiliser pour fournir des comparables de prix incontestables.",
        parameters: {
          type: "object",
          properties: {
            commune: { type: "string", description: "Nom de la commune genevoise (ex: Cologny, Vandoeuvres, Chêne-Bougeries, Troinex, Champel, Genève)" },
            property_type: { type: "string", description: "Type de bien ou nature (ex: Villa, Maison individuelle, Appartement PPE, Terrain, Parcelle)", enum: ["Villa", "Appartement", "Terrain", "Immeuble", "Tous"] },
            min_price: { type: "number", description: "Prix minimum en CHF" },
            max_price: { type: "number", description: "Prix maximum en CHF" },
            min_surface_m2: { type: "number", description: "Surface minimum en m²" },
            max_surface_m2: { type: "number", description: "Surface maximum en m²" },
            min_rooms: { type: "number", description: "Nombre de pièces minimum (décompte genevois : la cuisine compte pour 1 pièce)" },
            limit: { type: "number", description: "Nombre maximum de résultats à renvoyer (par défaut 5, max 12)" }
          }
        }
      },
      {
        name: "get_market_statistics",
        description: "Calcule les statistiques officielles de marché pour une commune ou un secteur (prix médian, prix moyen/m², volume total, nombre d'actes).",
        parameters: {
          type: "object",
          properties: {
            commune: { type: "string", description: "Commune genevoise concernée (ex: Cologny, Troinex, Veyrier, etc.)" },
            rive: { type: "string", description: "Rive du lac", enum: ["GAUCHE", "DROITE", "TOUTE"] },
            year: { type: "number", description: "Année d'analyse (ex: 2024, 2025, 2026)" }
          },
          required: ["commune"]
        }
      },
      {
        name: "get_parcel_neighbors",
        description: "Recherche les parcelles et adresses limitrophes autour d'une adresse ou d'un numéro de parcelle donné pour la prospection de voisinage (canvassing).",
        parameters: {
          type: "object",
          properties: {
            address_or_parcel: { type: "string", description: "Adresse (ex: 'Chemin de Conches 14') ou numéro de parcelle" },
            commune: { type: "string", description: "Commune genevoise" },
            radius_meters: { type: "number", description: "Rayon de voisinage en mètres (par défaut 250m)" }
          },
          required: ["address_or_parcel"]
        }
      },
      {
        name: "get_agency_bi_data",
        description: "Analyse les performances concurrentielles des 96 agences immobilières genevoises (volume vendu, prix médian, parts de marché, mandats récents, courtiers).",
        parameters: {
          type: "object",
          properties: {
            agency_name: { type: "string", description: "Nom ou fragment du nom de l'agence (ex: 'Désormière', 'BARNES', 'Cardis', 'SPG', 'Naef', 'Comptoir')" },
            commune: { type: "string", description: "Commune spécifique pour évaluer la part de marché locale" }
          }
        }
      },
      {
        name: "calculate_casatax_and_lcpur",
        description: "Simulateur fiscal genevois officiel : calcule l'économie d'acquisition Casatax (abattement droits d'enregistrement) et l'impôt sur les gains immobiliers (LCPur) selon la durée de détention.",
        parameters: {
          type: "object",
          properties: {
            price_chf: { type: "number", description: "Prix de vente envisagé en CHF" },
            holding_years: { type: "number", description: "Nombre d'années de détention par le vendeur" },
            is_primary_residence: { type: "boolean", description: "Si le bien est destiné à être la résidence principale de l'acheteur (condition Casatax)" }
          },
          required: ["price_chf", "holding_years"]
        }
      }
    ];
  }

  // Execute a tool by name with arguments
  public executeTool(name: string, args: any): any {
    switch (name) {
      case "search_fao_comparables":
        return this.searchComparables(args);
      case "get_market_statistics":
        return this.getMarketStatistics(args);
      case "get_parcel_neighbors":
        return this.getParcelNeighbors(args);
      case "get_agency_bi_data":
        return this.getAgencyBiData(args);
      case "calculate_casatax_and_lcpur":
        return this.calculateTaxes(args);
      default:
        throw new Error(`Outil inconnu : ${name}`);
    }
  }

  private searchComparables(args: {
    commune?: string;
    property_type?: string;
    min_price?: number;
    max_price?: number;
    min_surface_m2?: number;
    max_surface_m2?: number;
    min_rooms?: number;
    limit?: number;
  }) {
    let sql = `
      SELECT t.id, t.notice_date, t.commune, t.parcel_number, t.address, t.property_type,
             t.nature, t.rooms, t.surface_m2, t.price_chf, t.zone_name,
             t.centroid_wgs84_lat, t.centroid_wgs84_lon,
             e.price_per_m2, e.surface_official_m2
      FROM transactions t
      LEFT JOIN enrichments e ON e.transaction_id = t.id
      WHERE t.price_chf > 50000
    `;
    const params: any[] = [];

    if (args.commune) {
      sql += ` AND LOWER(t.commune) LIKE LOWER(?)`;
      params.push(`%${args.commune.trim()}%`);
    }

    if (args.property_type && args.property_type !== "Tous") {
      if (args.property_type === "Villa") {
        sql += ` AND (LOWER(t.nature) LIKE '%villa%' OR LOWER(t.property_type) LIKE '%villa%' OR LOWER(t.nature) LIKE '%maison%')`;
      } else if (args.property_type === "Appartement") {
        sql += ` AND (LOWER(t.nature) LIKE '%ppe%' OR LOWER(t.nature) LIKE '%appartement%' OR LOWER(t.property_type) LIKE '%appartement%')`;
      } else if (args.property_type === "Terrain") {
        sql += ` AND (LOWER(t.nature) LIKE '%terrain%' OR LOWER(t.nature) LIKE '%parcelle%')`;
      }
    }

    if (args.min_price) {
      sql += ` AND t.price_chf >= ?`;
      params.push(args.min_price);
    }
    if (args.max_price) {
      sql += ` AND t.price_chf <= ?`;
      params.push(args.max_price);
    }
    if (args.min_surface_m2) {
      sql += ` AND (t.surface_m2 >= ? OR e.surface_official_m2 >= ?)`;
      params.push(args.min_surface_m2, args.min_surface_m2);
    }
    if (args.max_surface_m2) {
      sql += ` AND (t.surface_m2 <= ? OR e.surface_official_m2 <= ?)`;
      params.push(args.max_surface_m2, args.max_surface_m2);
    }
    if (args.min_rooms) {
      sql += ` AND t.rooms >= ?`;
      params.push(args.min_rooms);
    }

    sql += ` ORDER BY t.notice_date DESC, t.price_chf DESC LIMIT ?`;
    params.push(Math.min(args.limit || 5, 12));

    const rows = this.db.query(sql).all(...params);
    return {
      count: rows.length,
      comparables: rows.map((r: any) => ({
        id: r.id,
        date_acte: r.notice_date,
        commune: r.commune,
        parcelle: r.parcel_number,
        adresse: r.address || "Adresse au Registre Foncier",
        type: r.nature || r.property_type,
        pieces: r.rooms,
        surface_m2: r.surface_m2 || r.surface_official_m2,
        prix_chf: r.price_chf,
        prix_m2: r.price_per_m2 ? Math.round(r.price_per_m2) : null,
        zone: r.zone_name,
        coordonnees: r.centroid_wgs84_lat ? { lat: r.centroid_wgs84_lat, lon: r.centroid_wgs84_lon } : null
      }))
    };
  }

  private getMarketStatistics(args: { commune: string; rive?: string; year?: number }) {
    let sql = `
      SELECT COUNT(*) as total_sales,
             AVG(t.price_chf) as avg_price,
             MIN(t.price_chf) as min_price,
             MAX(t.price_chf) as max_price,
             AVG(e.price_per_m2) as avg_price_m2
      FROM transactions t
      LEFT JOIN enrichments e ON e.transaction_id = t.id
      WHERE LOWER(t.commune) LIKE LOWER(?) AND t.price_chf > 50000
    `;
    const params: any[] = [`%${args.commune.trim()}%`];

    if (args.year) {
      sql += ` AND t.notice_date LIKE ?`;
      params.push(`${args.year}%`);
    }

    const stat: any = this.db.query(sql).get(...params);

    // Compute median price
    const medianPriceRow: any = this.db.query(`
      SELECT price_chf FROM transactions
      WHERE LOWER(commune) LIKE LOWER(?) AND price_chf > 50000
      ORDER BY price_chf LIMIT 1 OFFSET (
        SELECT COUNT(*) / 2 FROM transactions WHERE LOWER(commune) LIKE LOWER(?) AND price_chf > 50000
      )
    `).get(`%${args.commune.trim()}%`, `%${args.commune.trim()}%`);

    return {
      commune: args.commune,
      total_actes_analyses: stat.total_sales || 0,
      prix_median_chf: medianPriceRow ? medianPriceRow.price_chf : null,
      prix_moyen_chf: stat.avg_price ? Math.round(stat.avg_price) : null,
      prix_moyen_m2: stat.avg_price_m2 ? Math.round(stat.avg_price_m2) : null,
      fourchette_prix_chf: {
        minimum: stat.min_price || 0,
        maximum: stat.max_price || 0
      }
    };
  }

  private getParcelNeighbors(args: { address_or_parcel: string; commune?: string; radius_meters?: number }) {
    // Look up target transaction or coordinate
    let sql = `
      SELECT id, commune, parcel_number, address, centroid_wgs84_lat, centroid_wgs84_lon, surface_m2, price_chf, notice_date
      FROM transactions
      WHERE (LOWER(address) LIKE LOWER(?) OR parcel_number = ?)
    `;
    const params: any[] = [`%${args.address_or_parcel.trim()}%`, args.address_or_parcel.trim()];
    if (args.commune) {
      sql += ` AND LOWER(commune) LIKE LOWER(?)`;
      params.push(`%${args.commune.trim()}%`);
    }
    sql += ` LIMIT 1`;

    const target: any = this.db.query(sql).get(...params);
    if (!target || !target.centroid_wgs84_lat) {
      return {
        found_target: false,
        message: `Parcelle ou adresse '${args.address_or_parcel}' non localisée avec certitude dans la base. Indiquez la commune ou vérifiez l'orthographe.`
      };
    }

    // Spatial bounding box approx (1 degree lat ~= 111km, 1 degree lon ~= 77km at 46°N)
    const radiusM = args.radius_meters || 250;
    const deltaLat = radiusM / 111000;
    const deltaLon = radiusM / 77000;

    const neighborsSql = `
      SELECT id, commune, parcel_number, address, surface_m2, price_chf, notice_date,
             centroid_wgs84_lat, centroid_wgs84_lon
      FROM transactions
      WHERE id != ?
        AND centroid_wgs84_lat BETWEEN ? AND ?
        AND centroid_wgs84_lon BETWEEN ? AND ?
      ORDER BY notice_date DESC
      LIMIT 8
    `;

    const neighbors = this.db.query(neighborsSql).all(
      target.id,
      target.centroid_wgs84_lat - deltaLat,
      target.centroid_wgs84_lat + deltaLat,
      target.centroid_wgs84_lon - deltaLon,
      target.centroid_wgs84_lon + deltaLon
    );

    return {
      found_target: true,
      parcelle_cible: {
        id: target.id,
        commune: target.commune,
        parcelle: target.parcel_number,
        adresse: target.address,
        derniere_vente_chf: target.price_chf,
        date_acte: target.notice_date,
        coordonnees: { lat: target.centroid_wgs84_lat, lon: target.centroid_wgs84_lon }
      },
      rayon_prospection_m: radiusM,
      nombre_voisins_identifies: neighbors.length,
      voisins_limitrophes: neighbors.map((n: any) => ({
        id: n.id,
        parcelle: n.parcel_number,
        adresse: n.address || "Adresse au cadastre SITG",
        derniere_mutation_connue: n.notice_date,
        montant_precedent_chf: n.price_chf,
        coordonnees: { lat: n.centroid_wgs84_lat, lon: n.centroid_wgs84_lon }
      }))
    };
  }

  private getAgencyBiData(args: { agency_name?: string; commune?: string }) {
    if (args.agency_name) {
      const agency: any = this.db.query(`
        SELECT * FROM agencies WHERE LOWER(name) LIKE LOWER(?) LIMIT 1
      `).get(`%${args.agency_name.trim()}%`);

      if (!agency) {
        return { found: false, message: `Aucune agence trouvée pour '${args.agency_name}'.` };
      }

      // Fetch brokers
      const brokers = this.db.query(`
        SELECT name, role, rank, deals_count, specialty FROM brokers WHERE agency_id = ? LIMIT 6
      `).all(agency.id);

      // Fetch recent sold properties
      const recentSales = this.db.query(`
        SELECT fao_id, date, typology, commune, address, price_chf FROM agency_sold_properties
        WHERE agency_id = ? ORDER BY date DESC LIMIT 5
      `).all(agency.id);

      return {
        found: true,
        nom: agency.name,
        rang_cantonal: agency.rank,
        score_cytria: agency.cytria_score,
        communes_phares: agency.top_communes ? JSON.parse(agency.top_communes) : [],
        volume_24m_chf: `${agency.sold_volume_chf_m}M CHF`,
        nombre_ventes_24m: agency.sold_24m_count,
        prix_median_chf: agency.median_price_chf,
        courtiers_repertories: brokers,
        dernieres_ventes_reconciliees: recentSales
      };
    }

    // Default: Top 5 agencies in Geneva
    const topAgencies = this.db.query(`
      SELECT rank, name, cytria_score, sold_24m_count, sold_volume_chf_m, median_price_chf, top_communes
      FROM agencies ORDER BY rank ASC LIMIT 5
    `).all();

    return {
      top_5_agences_geneve: topAgencies.map((a: any) => ({
        rang: a.rank,
        nom: a.name,
        score: a.cytria_score,
        ventes_24m: a.sold_24m_count,
        volume_m_chf: a.sold_volume_chf_m,
        prix_median_chf: a.median_price_chf
      }))
    };
  }

  private calculateTaxes(args: { price_chf: number; holding_years: number; is_primary_residence?: boolean }) {
    const price = args.price_chf;
    const years = args.holding_years;

    // Casatax calculation (Geneva Canton abatement)
    // Abatement threshold for 2026 is approx CHF 1'425'000 on main residences
    const casataxEligible = (args.is_primary_residence !== false) && (price <= 1450000);
    const standardMutationRights = Math.round(price * 0.03); // 3% typical
    const casataxAbatement = casataxEligible ? Math.min(standardMutationRights, 20689) : 0;
    const finalMutationRights = standardMutationRights - casataxAbatement;

    // LCPur (Tax on Real Estate Capital Gains in Geneva)
    // Decreasing scale based on holding years:
    // < 2 years: 50%
    // 2-4 years: 40%
    // 4-6 years: 30%
    // 6-8 years: 20%
    // 8-10 years: 15%
    // 10-25 years: -1% per year from 15% down to 0% after 25 years
    let lcPurRate = 0;
    if (years < 2) lcPurRate = 0.50;
    else if (years < 4) lcPurRate = 0.40;
    else if (years < 6) lcPurRate = 0.30;
    else if (years < 8) lcPurRate = 0.20;
    else if (years < 10) lcPurRate = 0.15;
    else if (years < 25) lcPurRate = Math.max(0, 0.15 - (years - 10) * 0.01);
    else lcPurRate = 0.0;

    return {
      prix_vente_chf: price,
      annees_detention: years,
      simulation_casatax: {
        eligible: casataxEligible,
        droits_mutation_standard_chf: standardMutationRights,
        economie_casatax_chf: casataxAbatement,
        droits_mutation_nets_chf: finalMutationRights,
        remarque: casataxEligible
          ? "Acquisition éligible Casatax : abattement direct sur les droits d'enregistrement."
          : "Plafond Casatax dépassé ou non éligible (barème plein applicable)."
      },
      simulation_lcpur_plus_value: {
        taux_imposition_applicable: `${Math.round(lcPurRate * 100)}%`,
        explication: years >= 25
          ? "Exonération totale de l'impôt sur la plus-value LCPur (>25 ans de détention)."
          : `Taux cantonal dégressif de ${Math.round(lcPurRate * 100)}% après ${years} an(s) de détention.`
      }
    };
  }
}
