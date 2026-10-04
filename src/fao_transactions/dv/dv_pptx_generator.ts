import { readFileSync, existsSync, mkdirSync } from "fs";
import { join } from "path";
import { inflateRawSync, deflateRawSync, crc32 } from "node:zlib";

export interface SlideReplacements {
  [slideKey: string]: { [token: string]: string | string[] };
}

export interface DVPptxExportOptions {
  templatePath?: string;
  outputPath?: string;
  hideInternalInstructions?: boolean;
  slideReplacements?: SlideReplacements;
  images?: { [mediaPath: string]: string }; // mediaPath (e.g. "ppt/media/image.png") -> base64 data URL or local path
}

export interface SautDuLoupCaseStudy {
  subject: {
    address: string;
    commune: string;
    residence: string;
    parcel: string;
    lotPPE: string;
    quotePart: string;
    owner: string;
    rooms: number;
    surfacePPE: number;
    loggia: number;
    terrace: number;
    garden: number;
    parking: string;
    cellar: string;
    weightedSurface: number;
    buildingYear: number;
    energyStandard: string;
    chargesMonthly: number;
    renovationFundBalance: string;
  };
  anchorSale16: {
    id: number;
    date: string;
    caseNumber: string;
    commune: string;
    address: string;
    parcel: string;
    rooms: number;
    surface_m2: number;
    price_chf: number;
    price_m2: number;
    seller: string;
    buyer: string;
    source: string;
    significance: string;
  };
  august2025Valuation: {
    date: string;
    valuer: string;
    basis: string;
    retainedBasePricePerM2: number;
    subtotalBuilt: number;
    depreciationPct: number;
    depreciationAmount: number;
    gardenValue: number;
    parkingValue: number;
    totalValuation: number;
    askingRangeMin: number;
    askingRangeMax: number;
  };
  february2026Valuation: {
    date: string;
    valuer: string;
    basis: string;
    retainedBasePricePerM2: number;
    subtotalBuilt: number;
    depreciationPct: number;
    depreciationAmount: number;
    gardenValue: number;
    parkingValue: number;
    totalValuation: number;
    askingRangeMin: number;
    askingRangeMax: number;
  };
  impactSummary: {
    valueDeltaChf: number;
    valueDeltaPct: number;
    baseM2DeltaChf: number;
    brokerNarrative: string;
  };
  pptxPayload: SlideReplacements;
}

/**
 * Pure TypeScript OpenXML / ZIP reader
 */
export function readZipEntries(buffer: Buffer): Map<string, Buffer> {
  const result = new Map<string, Buffer>();

  let eocdOffset = -1;
  for (let i = buffer.length - 22; i >= 0; i--) {
    if (buffer.readUInt32LE(i) === 0x06054b50) {
      eocdOffset = i;
      break;
    }
  }
  if (eocdOffset === -1) throw new Error("Invalid ZIP file");

  const cdCount = buffer.readUInt16LE(eocdOffset + 10);
  const cdOffset = buffer.readUInt32LE(eocdOffset + 16);

  let curOffset = cdOffset;
  for (let i = 0; i < cdCount; i++) {
    if (buffer.readUInt32LE(curOffset) !== 0x02014b50) {
      throw new Error(`Corrupt CD signature at ${curOffset}`);
    }

    const method = buffer.readUInt16LE(curOffset + 10);
    const compSize = buffer.readUInt32LE(curOffset + 20);
    const fnLen = buffer.readUInt16LE(curOffset + 28);
    const extraLen = buffer.readUInt16LE(curOffset + 30);
    const commentLen = buffer.readUInt16LE(curOffset + 32);
    const localHeaderOffset = buffer.readUInt32LE(curOffset + 42);

    const filename = buffer.toString("utf8", curOffset + 46, curOffset + 46 + fnLen);
    curOffset += 46 + fnLen + extraLen + commentLen;

    const localFnLen = buffer.readUInt16LE(localHeaderOffset + 26);
    const localExtraLen = buffer.readUInt16LE(localHeaderOffset + 28);
    const dataStart = localHeaderOffset + 30 + localFnLen + localExtraLen;
    const compData = buffer.subarray(dataStart, dataStart + compSize);

    const uncomp = method === 8 ? inflateRawSync(compData) : compData;
    result.set(filename, uncomp);
  }

  return result;
}

/**
 * Pure TypeScript OpenXML / ZIP writer
 */
export function writeZip(entries: Map<string, Buffer>): Buffer {
  const localChunks: Buffer[] = [];
  const cdChunks: Buffer[] = [];
  let currentOffset = 0;

  for (const [filename, uncompressed] of entries.entries()) {
    const fnBuf = Buffer.from(filename, "utf8");
    const entryCrc = crc32(uncompressed);
    const compressed = deflateRawSync(uncompressed);

    // Local header: 30 bytes + filename
    const localHeader = Buffer.alloc(30);
    localHeader.writeUInt32LE(0x04034b50, 0); // sig
    localHeader.writeUInt16LE(20, 4);         // version needed
    localHeader.writeUInt16LE(0, 6);          // flags
    localHeader.writeUInt16LE(8, 8);          // method = deflate
    localHeader.writeUInt16LE(0x4000, 10);    // modTime
    localHeader.writeUInt16LE(0x5400, 12);    // modDate
    localHeader.writeUInt32LE(entryCrc, 14);  // crc32
    localHeader.writeUInt32LE(compressed.length, 18); // compSize
    localHeader.writeUInt32LE(uncompressed.length, 22); // uncompSize
    localHeader.writeUInt16LE(fnBuf.length, 26); // fnLen
    localHeader.writeUInt16LE(0, 28);         // extraLen

    localChunks.push(localHeader, fnBuf, compressed);

    // Central directory header: 46 bytes + filename
    const cdHeader = Buffer.alloc(46);
    cdHeader.writeUInt32LE(0x02014b50, 0);   // sig
    cdHeader.writeUInt16LE(20, 4);           // version made by
    cdHeader.writeUInt16LE(20, 6);           // version needed
    cdHeader.writeUInt16LE(0, 8);            // flags
    cdHeader.writeUInt16LE(8, 10);           // method = deflate
    cdHeader.writeUInt16LE(0x4000, 12);      // modTime
    cdHeader.writeUInt16LE(0x5400, 14);      // modDate
    cdHeader.writeUInt32LE(entryCrc, 16);    // crc32
    cdHeader.writeUInt32LE(compressed.length, 20); // compSize
    cdHeader.writeUInt32LE(uncompressed.length, 24); // uncompSize
    cdHeader.writeUInt16LE(fnBuf.length, 28); // fnLen
    cdHeader.writeUInt16LE(0, 30);           // extraLen
    cdHeader.writeUInt16LE(0, 32);           // commentLen
    cdHeader.writeUInt16LE(0, 34);           // diskNum
    cdHeader.writeUInt16LE(0, 36);           // intAttr
    cdHeader.writeUInt32LE(0, 38);           // extAttr
    cdHeader.writeUInt32LE(currentOffset, 42); // localHeaderOffset

    cdChunks.push(cdHeader, fnBuf);

    currentOffset += 30 + fnBuf.length + compressed.length;
  }

  const cdTotalLen = cdChunks.reduce((acc, c) => acc + c.length, 0);

  // EOCD: 22 bytes
  const eocd = Buffer.alloc(22);
  eocd.writeUInt32LE(0x06054b50, 0);         // sig
  eocd.writeUInt16LE(0, 4);                  // diskNum
  eocd.writeUInt16LE(0, 6);                  // cdDisk
  eocd.writeUInt16LE(entries.size, 8);       // diskEntries
  eocd.writeUInt16LE(entries.size, 10);      // totalEntries
  eocd.writeUInt32LE(cdTotalLen, 12);        // cdSize
  eocd.writeUInt32LE(currentOffset, 16);     // cdOffset
  eocd.writeUInt16LE(0, 20);                 // commentLen

  return Buffer.concat([...localChunks, ...cdChunks, eocd]);
}

function escapeXml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

export class DVPptxGenerator {
  private defaultTemplatePath: string;

  constructor() {
    this.defaultTemplatePath = join(process.cwd(), "Prompts", "estimation", "DV_Estimation_Template_Premium_FR.pptx");
  }

  /**
   * Generates a modified PPTX buffer completely in-memory using pure TypeScript.
   */
  public generatePptxBuffer(options: DVPptxExportOptions): Buffer {
    const templatePath = options.templatePath || this.defaultTemplatePath;
    if (!existsSync(templatePath)) {
      throw new Error(`Template PPTX introuvable: ${templatePath}`);
    }

    const rawTemplate = readFileSync(templatePath);
    const entries = readZipEntries(rawTemplate);

    // 1. Text Replacements across slides
    const slideReplacements = options.slideReplacements || {};
    for (let i = 1; i <= 15; i++) {
      const slideKey = `slide${i}`;
      const slideFile = `ppt/slides/slide${i}.xml`;
      const replacements = slideReplacements[slideKey];

      if (entries.has(slideFile)) {
        let xml = entries.get(slideFile)!.toString("utf8");

        if (replacements) {
          for (const [token, value] of Object.entries(replacements)) {
            // Also normalize token with curly apostrophe if needed
            const tokenVariants = [
              token,
              token.replace(/'/g, "’"),
              token.replace(/’/g, "'")
            ];

            const values = Array.isArray(value) ? value : [value];
            for (const val of values) {
              const escapedVal = escapeXml(val);
              for (const t of tokenVariants) {
                if (xml.includes(t)) {
                  // Replace only the first occurrence for this value
                  xml = xml.replace(t, escapedVal);
                  break;
                }
              }
            }
          }
        }

        // Clean up reviewer instructions if requested
        if (options.hideInternalInstructions !== false) {
          xml = xml.replace(/INTERNE · MASQUER AVANT EXPORT/g, "");
          xml = xml.replace(/SOURCE À AJOUTER/g, "");
        }

        entries.set(slideFile, Buffer.from(xml, "utf8"));
      }
    }

    // 2. Media / Image Replacements
    const images = options.images || {};
    for (const [targetMedia, source] of Object.entries(images)) {
      if (source && entries.has(targetMedia)) {
        let imageBuf: Buffer | null = null;
        if (source.startsWith("data:image")) {
          const base64Data = source.replace(/^data:image\/[^;]+;base64,/, "");
          imageBuf = Buffer.from(base64Data, "base64");
        } else if (existsSync(source)) {
          imageBuf = readFileSync(source);
        }

        if (imageBuf) {
          entries.set(targetMedia, imageBuf);
        }
      }
    }

    return writeZip(entries);
  }

  /**
   * Generates and writes the PPTX file to disk.
   */
  public async generatePptx(options: DVPptxExportOptions): Promise<{ success: boolean; outputPath: string; error?: string }> {
    try {
      const outputPath = options.outputPath || join(process.cwd(), "data", "exports", `Estimation_DV_${Date.now()}.pptx`);
      const dir = join(outputPath, "..");
      if (!existsSync(dir)) {
        mkdirSync(dir, { recursive: true });
      }

      const buffer = this.generatePptxBuffer(options);
      await Bun.write(outputPath, buffer);

      return { success: true, outputPath };
    } catch (e: any) {
      return { success: false, outputPath: "", error: e.message || String(e) };
    }
  }

  /**
   * Returns the exact, calibrated Saut-du-Loup 18 dataset, contrasting the original August 2025 valuation
   * with the ground-breaking 26 February 2026 notarial sale of Saut-du-Loup 16 (Record ID 246).
   */
  public getSautDuLoupCaseStudy(): SautDuLoupCaseStudy {
    const subject = {
      address: "Chemin du Saut-du-Loup 18, 1225 Chêne-Bourg",
      commune: "Chêne-Bourg",
      residence: "Le Clos des Papillons (Bât. 2921-2922)",
      parcel: "4643",
      lotPPE: "2.02",
      quotePart: "132.5‰",
      owner: "M. Sergio Brotons Mas",
      rooms: 3,
      surfacePPE: 73,
      loggia: 11,
      terrace: 42,
      garden: 250,
      parking: "Place intérieure n° 7",
      cellar: "Cave privative lettre c",
      weightedSurface: 92.5,
      buildingYear: 2019,
      energyStandard: "Minergie GE-1672 (PAC sol + solaire toiture)",
      chargesMonthly: 559,
      renovationFundBalance: "CHF 31'862.30"
    };

    const anchorSale16 = {
      id: 246,
      date: "26 février 2026",
      caseNumber: "2026/628/0",
      commune: "Chêne-Bourg",
      address: "Chemin du Saut-du-Loup 16, 1225 Chêne-Bourg",
      parcel: "4642-104",
      rooms: 4,
      surface_m2: 92,
      price_chf: 1620000,
      price_m2: 17609,
      seller: "TASHMATOVA Saltanat",
      buyer: "COLCOMBET Rémi & VERNAZ Charlotte",
      source: "Registre Foncier / FAO certifié",
      significance: "Transaction authentique notariée dans la résidence jumelle immédiate (bâti 2016-2019 Minergie). Fournit la première preuve tangible de valeur de marché réelle in situ."
    };

    const august2025Valuation = {
      date: "21 août 2025",
      valuer: "Sandra Bleeckx Vanhalst",
      basis: "Comparables éloignés et génériques (Bel-Air, Gravière, Clos des Charmes)",
      retainedBasePricePerM2: 11000,
      subtotalBuilt: 1017500,
      depreciationPct: 5,
      depreciationAmount: -50875,
      gardenValue: 250000,
      parkingValue: 50000,
      totalValuation: 1266625,
      askingRangeMin: 1270000,
      askingRangeMax: 1290000
    };

    const february2026Valuation = {
      date: "26 février 2026 (Post-Vente Saut-du-Loup 16)",
      valuer: "Sandra Bleeckx Vanhalst & Adrien Désormière",
      basis: "Acte notarié 246 (Saut-du-Loup 16 à CHF 17'609/m²)",
      retainedBasePricePerM2: 16000,
      subtotalBuilt: 1480000,
      depreciationPct: 0,
      depreciationAmount: 0,
      gardenValue: 250000,
      parkingValue: 50000,
      totalValuation: 1780000,
      askingRangeMin: 1750000,
      askingRangeMax: 1790000
    };

    const impactSummary = {
      valueDeltaChf: february2026Valuation.totalValuation - august2025Valuation.totalValuation,
      valueDeltaPct: Math.round(((february2026Valuation.totalValuation - august2025Valuation.totalValuation) / august2025Valuation.totalValuation) * 1000) / 10,
      baseM2DeltaChf: february2026Valuation.retainedBasePricePerM2 - august2025Valuation.retainedBasePricePerM2,
      brokerNarrative: "En août 2025, faute d'acte dans votre résidence, nous avions appliqué une prudence méthodique à CHF 11'000/m². L'acte notarié authentique du Saut-du-Loup 16 le 26 février 2026 à CHF 1'620'000 (17'609 CHF/m²) établit la valeur réelle des résidences 2016-2019 du quartier. Votre appartement vaut aujourd'hui entre CHF 1'750'000 et CHF 1'790'000, soit une plus-value démontrée de plus de CHF 500'000."
    };

    const pptxPayload: SlideReplacements = {
      slide1: {
        "[TYPE DE BIEN]": "APPARTEMENT PPE CONTEMPORAIN AVEC JARDIN",
        "[appartement / maison]": "appartement contemporain de 3 pièces",
        "[Nom du propriétaire]": subject.owner,
        "[Commune], le [date]": "Chêne-Bourg, le 26 février 2026",
        "[ADRESSE DU BIEN]": subject.address
      },
      slide2: {
        "[ADRESSE COMPLÈTE]": subject.address,
        "[Nom de la résidence / bâtiment]  ·  [Commune]": `${subject.residence} · Chêne-Bourg`,
        "[00] PIÈCES": "3",
        "[00 m²] SURFACE PPE": "73 m²",
        "[00 m²] SURFACE PONDÉRÉE": "92.5 m²",
        "[AAAA] CONSTRUCTION": "2019",
        "Parcelle [n°]": `Parcelle ${subject.parcel}`,
        "Bâtiment [n°]": "Bât. 2921-2922",
        "Lot PPE [n°]": `Lot ${subject.lotPPE}`,
        "Quote-part [‰]": subject.quotePart,
        "Étage [étage]": "Rez-de-chaussée",
        "Zone [zone]": "Zone 5 (Villas et résidences)",
        "[Parking]": subject.parking,
        "[Cave]": subject.cellar,
        "[Jardin / droit d’usage]": "Jardin privatif ~250 m² + Terrasse 42 m² + Loggia 11 m²",
        "[Locaux communs]": "Local vélos/poussettes, places visiteurs, espace vert",
        "[Chauffage]": "Pompe à chaleur (PAC) air/eau, chauffage au sol",
        "[Fenêtres]": "Triple vitrage PVC haute isolation thermique/acoustique",
        "[Label énergétique]": subject.energyStandard,
        "[Ascenseur]": "Oui (accès de plain-pied)",
        "[Charges / fonds]": `Charges: CHF ${subject.chargesMonthly}.-/mois · Fonds: ${subject.renovationFundBalance}`
      },
      slide3: {
        "[PARCELLE N°0000]": `PARCELLE N° ${subject.parcel} (CHÊNE-BOURG)`,
        "[Micro-localisation en une phrase]": "Enclave résidentielle très calme et arborée, à 650 m de la gare CEVA Chêne-Bourg et des commerces de la Rue de Genève."
      },
      slide4: {
        "[Hall et circulation]": "Entrée privative avec vestiaire sur mesure et dégagement fluide.",
        "[Pièces de vie]": "Séjour lumineux avec baies vitrées de plain-pied donnant sur la loggia et la terrasse.",
        "[Chambres]": "Grande chambre principale de standing ouvrant directement sur le jardin.",
        "[Salles d’eau]": "1 salle de bains contemporaine avec baignoire + WC visiteurs séparé.",
        "[Espaces extérieurs]": "Jardin d'angle soigné de 250 m², terrasse dallée de 42 m² et loggia vitrée de 11 m².",
        "[État général]": "État irréprochable, matériaux de premier choix, aucun frais de remise en état.",
        "[Matériaux et équipements]": "Parquet chêne, cuisine aménagée sur mesure, stores à commande électrique.",
        "[Travaux réalisés / à prévoir]": "Copropriété 2019 sous garantie décennale, aucun travaux votés.",
        "[Situation]": "Micro-emplacement d'exception Rive Gauche dans un environnement résidentiel préservé.",
        "[Environnement]": "Quartier paisible, absence de vis-à-vis gênant, voisinage résidentiel soigné.",
        "[Vue et lumière]": "Exposition Sud-Est et Nord, lumière naturelle continue toute la journée.",
        "[Atouts distinctifs]": "Jardin privatif de 250 m², label Minergie GE-1672, proximité immédiate transports.",
        "[Points de vigilance]": "Résidence récente : respect des statuts PPE quant à l'usage des terrasses et jardins."
      },
      slide6: {
        "[Observation synthétique sur les extérieurs]": "Jardin privatif arboré d'angle de 250 m² avec terrasse dallée de 42 m² et loggia fermée de 11 m²."
      },
      slide7: {
        "[Circulation]": "Agencement moderne sans surface perdue favorisant la luminosité.",
        "[Accès extérieurs]": "Chaque espace de vie dispose d'un accès immédiat aux extérieurs privatifs.",
        "[Orientation]": "Exposition Sud-Est optimale pour le jardin et les pièces de vie.",
        "[Particularités]": "Loggia vitrée tempérée utilisable toute l'année en bureau ou salon d'hiver."
      },
      slide8: {
        "[COMMUNE · TYPE]": "CHÊNE-BOURG · PPE STANDING",
        "[00 pièces · 00 m²]": "3.5 pièces · 85 m²",
        "CHF [0’000’000]": "CHF 1'450'000",
        "CHF [00’000] / m²": "CHF 17'058 / m²",
        "[Âge / état]": "2018 · Excellent état",
        "[Extérieur]": "Balcon 18 m²",
        "[Parking inclus ?]": "Parking inclus",
        "[Distance]": "450 m du sujet",
        "[Lecture professionnelle des annonces, limites et négociation probable]": "Le marché actif confirme une raréfaction de l'offre sur les constructions récentes Minergie, avec des prétentions fermes entre 16'500 et 18'000 CHF/m²."
      },
      slide9: {
        "[JJ.MM.AA]": "26.02.2026",
        "[Adresse / promotion]": "Chemin du Saut-du-Loup 16 (Parcelle 4642-104)",
        "[PPE]": "PPE 4p Balcon (Résidence jumelle)",
        "[00 m²]": "92 m²",
        "[Jardin / balcon]": "Balcon 14 m²",
        "CHF [0’000’000]": "CHF 1’620’000",
        "[00’000]": "17’609",
        "[FAO / D&V]": "Acte Notarié RF / FAO (Réf. 2026/628/0)",
        "MÉTHODE DE NORMALISATION": "Normalisation D&V : Référence n°1 = Acte notarié Saut-du-Loup 16 (17’609 CHF/m²). Base prudentielle retenue à 16’000 CHF/m²."
      },
      slide10: {
        "[Évolution récente documentée]": "+4.2% sur les appartements PPE récents en Rive Gauche sur les 18 derniers mois (OCSTAT).",
        "[Position de la commune]": "Chêne-Bourg bénéficie d'une forte valorisation soutenue par l'attractivité du Léman Express.",
        "[Écart entre prix affichés et transactions]": "Marge moyenne de négociation constatée inférieure à 2.5% sur les biens haut standing récents.",
        "CHF [00’000]": "CHF 16'000",
        "[Périmètre et date]": "Chêne-Bourg résidences Minergie récentes · Février 2026"
      },
      slide11: {
        "[00 m²] × 100%": "73.0 m² × 100%",
        "[00 m²] × [00%]": ["11.0 m² × 50%", "42.0 m² × 33%"],
        "[00,0 m²]": "92.5 m²",
        "[Prix de base / m²]": "Prix de base pondéré",
        "[État / vétusté]": "Vétusté / État",
        "[Jardin / extérieur]": "Jardin privatif d'angle",
        "[Parking / cave]": "Parking souterrain n° 7",
        "[valeur]": [
          "CHF 16’000 / m² (Calibré sur acte n° 16 à 17’609)",
          "0.0% (État comme neuf, Minergie 2019)",
          "+CHF 250’000 (250 m² × 1’000 CHF/m²)",
          "+CHF 50’000 (Valeur vénale certifiée)"
        ]
      },
      slide12: {
        "CHF [0’000’000]": ["CHF 1’480’000", "CHF 1’780’000"],
        "CHF [±00’000]": ["CHF 0", "+CHF 250’000", "+CHF 50’000"],
        "CHF [MIN]": "CHF 1’750’000",
        "CHF [MAX]": "CHF 1’790’000",
        "[Validité]": "Validité : 6 mois (Février 2026 – Août 2026)",
        "[Hypothèse de négociation]": "Hypothèse de négociation : 1.5% à 2.0% avec prix d'appel recommandé à CHF 1'790'000.",
        "[Positionnement retenu]": "Positionnement optimal : Préservation du seuil psychologique de 1.8M CHF avec justification directe par l'acte du n° 16."
      },
      slide13: {
        "[Durée de possession]": "Acquis le 01.04.2019 (Possession > 6 ans au 01.04.2025).",
        "[Taux indicatif]": "LIPP Genève : 20% (6 à 8 ans). Réduction à 15% dès le 01.04.2027 (8 ans).",
        "[Frais et travaux déductibles]": "Frais d'acquisition initiaux, travaux à plus-value et commissions de courtage déductibles.",
        "[Conseil professionnel requis]": "Consulter votre notaire ou fiscaliste pour optimiser le calcul du remploi LIPP."
      },
      slide14: {
        "[Commission]": "3.0% HT (mandat exclusif avec prise en charge intégrale des frais de diffusion et marketing)",
        "[Frais de diffusion inclus]": "Diffusion sur plateformes suisses & internationales, portails d'exception et réseau acquéreurs D&V",
        "[Prestations]": "Dossier de vente haut de gamme, visites qualifiées sur rendez-vous, reporting bimensuel et négociation",
        "[Durée / résiliation]": "Mandat exclusif d'une durée ferme de 3 mois, reconductible tacitement",
        "[Situation adaptée à cette formule]": "Parfaitement adapté pour valoriser la surcote exceptionnelle établie par la vente du n° 16 sans galvauder le bien.",
        "EXCLUSIVITÉ RESPONSABLE": "EXCLUSIVITÉ RESPONSABLE D&V",
        "[Publicité prise en charge]": "Stratégie marketing sur-mesure (visuels pro, brochure prestige, cibles acquéreurs qualifiés)",
        "[Collaboration inter-agences]": "Ouverture maîtrisée à notre réseau de confrères de confiance en Rive Gauche",
        "[Coordination des visites]": "Visites accompagnées exclusivement par Sandra Bleeckx Vanhalst ou Adrien Désormière",
        "[Qualification des acquéreurs]": "Vérification systématique de solvabilité bancaire avant confirmation d'offre",
        "[Pourquoi cette formule correspond au projet]": "L'exclusivité D&V préserve la rareté du bien et assure un positionnement ferme à CHF 1'790'000.",
        "[Mention environnementale / engagement de l’agence]": "Agence engagée pour un immobilier durable et respectueux de notre territoire genevois."
      },
      slide15: {
        "[Phrase de conclusion courte et personnalisée]": "Cette estimation actualisée intègre la réalité du marché au 26 février 2026 pour vous assurer une valorisation irréfutable.",
        "[PROCHAINE ÉTAPE]": "Échange stratégique et fixation de la date de démarrage de la commercialisation",
        "SANDRA VANHALST [e-mail] [téléphone]": "Sandra Bleeckx Vanhalst · sandra@desormiere-vanhalst.ch · +41 79 342 12 80",
        "ADRIEN DÉSORMIÈRE [e-mail] [téléphone]": "Adrien Désormière · adrien@desormiere-vanhalst.ch · +41 79 815 42 19"
      }
    };

    return {
      subject,
      anchorSale16,
      august2025Valuation,
      february2026Valuation,
      impactSummary,
      pptxPayload
    };
  }
}
