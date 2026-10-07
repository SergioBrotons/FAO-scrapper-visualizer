import { deflateRawSync, inflateRawSync } from "zlib";
import { readFileSync, existsSync, mkdirSync } from "fs";
import { join } from "path";

/**
 * Slide replacement map: slideKey (e.g. 'slide1', 'slide2') => { [placeholder: string]: string | string[] }
 */
export interface SlideReplacements {
  [slideKey: string]: Record<string, string | string[]>;
}

export interface DVPptxExportOptions {
  templatePath?: string;
  outputPath?: string;
  slideReplacements?: SlideReplacements;
  images?: Record<string, string | Buffer | (string | Buffer)[]>;
  hideInternalInstructions?: boolean;
}

/**
 * Escape XML special characters while preserving Swiss curly quotes
 */
function escapeXml(unsafe: string): string {
  if (typeof unsafe !== "string") return String(unsafe);
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

/**
 * Pure TypeScript CRC-32 calculation for ZIP integrity
 */
function makeCrcTable(): Uint32Array {
  const table = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) {
      c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    }
    table[n] = c;
  }
  return table;
}

const CRC_TABLE = makeCrcTable();

function crc32(buf: Buffer): number {
  let crc = 0xffffffff;
  for (let i = 0; i < buf.length; i++) {
    crc = CRC_TABLE[(crc ^ buf[i]) & 0xff] ^ (crc >>> 8);
  }
  return (crc ^ 0xffffffff) >>> 0;
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

    // Central Directory header: 46 bytes + filename
    const cdHeader = Buffer.alloc(46);
    cdHeader.writeUInt32LE(0x02014b50, 0);   // sig
    cdHeader.writeUInt16LE(20, 4);            // version made by
    cdHeader.writeUInt16LE(20, 6);            // version needed
    cdHeader.writeUInt16LE(0, 8);             // flags
    cdHeader.writeUInt16LE(8, 10);            // method
    cdHeader.writeUInt16LE(0x4000, 12);       // modTime
    cdHeader.writeUInt16LE(0x5400, 14);       // modDate
    cdHeader.writeUInt32LE(entryCrc, 16);     // crc32
    cdHeader.writeUInt32LE(compressed.length, 20); // compSize
    cdHeader.writeUInt32LE(uncompressed.length, 24); // uncompSize
    cdHeader.writeUInt16LE(fnBuf.length, 28); // fnLen
    cdHeader.writeUInt16LE(0, 30);            // extraLen
    cdHeader.writeUInt16LE(0, 32);            // commentLen
    cdHeader.writeUInt16LE(0, 34);            // diskStart
    cdHeader.writeUInt16LE(0, 36);            // intAttr
    cdHeader.writeUInt32LE(0, 38);            // extAttr
    cdHeader.writeUInt32LE(currentOffset, 42);// localHeaderOffset

    cdChunks.push(cdHeader, fnBuf);

    currentOffset += localHeader.length + fnBuf.length + compressed.length;
  }

  const cdTotalSize = cdChunks.reduce((acc, c) => acc + c.length, 0);
  const cdOffset = currentOffset;

  // End of Central Directory: 22 bytes
  const eocd = Buffer.alloc(22);
  eocd.writeUInt32LE(0x06054b50, 0);          // sig
  eocd.writeUInt16LE(0, 4);                   // diskNum
  eocd.writeUInt16LE(0, 6);                   // cdDisk
  eocd.writeUInt16LE(entries.size, 8);        // cdEntriesDisk
  eocd.writeUInt16LE(entries.size, 10);       // cdEntriesTotal
  eocd.writeUInt32LE(cdTotalSize, 12);        // cdSize
  eocd.writeUInt32LE(cdOffset, 16);           // cdOffset
  eocd.writeUInt16LE(0, 20);                  // commentLen

  return Buffer.concat([...localChunks, ...cdChunks, eocd]);
}

/**
 * High-performance, pure TypeScript PPTX Generator for Désormière & Vanhalst.
 */
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
            const tokenVariants = [
              token,
              token.replace(/'/g, "’"),
              token.replace(/’/g, "'"),
              token.replace(/&/g, "&amp;"),
              token.replace(/&amp;/g, "&")
            ];

            const uniqueVariants = [...new Set(tokenVariants)];
            if (Array.isArray(value)) {
              for (const val of value) {
                const escapedVal = escapeXml(val);
                for (const t of uniqueVariants) {
                  if (xml.includes(t)) {
                    xml = xml.replace(t, escapedVal);
                    break;
                  }
                }
              }
            } else {
              const escapedVal = escapeXml(value);
              for (const t of uniqueVariants) {
                if (xml.includes(t)) {
                  xml = xml.replaceAll(t, escapedVal);
                }
              }
            }
          }
        }

        // Clean up reviewer instructions if requested
        if (options.hideInternalInstructions !== false) {
          xml = xml.replace(/INTERNE · MASQUER AVANT EXPORT/g, "");
          xml = xml.replace(/SOURCE À AJOUTER[^<]*/g, "");
          xml = xml.replace(/PHOTO COMPARABLE\s*Capture datée/g, "");
        }

        entries.set(slideFile, Buffer.from(xml, "utf8"));
      }
    }

    // 2. Media / Image Replacements with Friendly Aliasing
    const images = options.images || {};
    const mediaTargets: Record<string, string | Buffer> = {};

    function resolveImageBuf(src: string | Buffer | null | undefined): Buffer | null {
      if (!src) return null;
      if (Buffer.isBuffer(src)) return src;
      if (typeof src === "string") {
        if (src.startsWith("data:image")) {
          const base64Data = src.replace(/^data:image\/[^;]+;base64,/, "");
          return Buffer.from(base64Data, "base64");
        } else if (existsSync(src)) {
          return readFileSync(src);
        }
      }
      return null;
    }

    // Cover photo -> Slide 1 full cover (image.png) and Slide 4 property overview (image.jpeg)
    if (images.cover) {
      const coverVal = Array.isArray(images.cover) ? images.cover[0] : images.cover;
      mediaTargets["ppt/media/image.png"] = coverVal;
      mediaTargets["ppt/media/image.jpeg"] = coverVal;
    }

    // Interior photos -> Slide 5 (image2.jpeg ... image6.jpeg)
    if (images.interior) {
      const interiorList = Array.isArray(images.interior) ? images.interior : [images.interior];
      const interiorMedia = [
        "ppt/media/image2.jpeg",
        "ppt/media/image3.jpeg",
        "ppt/media/image4.jpeg",
        "ppt/media/image5.jpeg",
        "ppt/media/image6.jpeg"
      ];
      interiorList.forEach((img, idx) => {
        if (idx < interiorMedia.length && img) {
          mediaTargets[interiorMedia[idx]] = img;
        }
      });
    }

    // Exterior photos -> Slide 6 (image7.jpeg ... image10.jpeg)
    if (images.exterior) {
      const exteriorList = Array.isArray(images.exterior) ? images.exterior : [images.exterior];
      const exteriorMedia = [
        "ppt/media/image7.jpeg",
        "ppt/media/image8.jpeg",
        "ppt/media/image9.jpeg",
        "ppt/media/image10.jpeg"
      ];
      exteriorList.forEach((img, idx) => {
        if (idx < exteriorMedia.length && img) {
          mediaTargets[exteriorMedia[idx]] = img;
        }
      });
    }

    // Direct / raw media paths
    for (const [key, val] of Object.entries(images)) {
      if (key.startsWith("ppt/media/")) {
        mediaTargets[key] = Array.isArray(val) ? val[0] : val;
      }
    }

    // Apply all standard media replacements
    for (const [targetMedia, source] of Object.entries(mediaTargets)) {
      if (source && entries.has(targetMedia)) {
        const imageBuf = resolveImageBuf(source);
        if (imageBuf) {
          entries.set(targetMedia, imageBuf);
        }
      }
    }

    // Cadastre / Situation Map on Slide 3 (Plan Cadastral)
    const cadastreImg = images.cadastre || images.planCadastre || images.plan;
    if (cadastreImg) {
      const cadastreVal = Array.isArray(cadastreImg) ? cadastreImg[0] : cadastreImg;
      const cadastreBuf = resolveImageBuf(cadastreVal);
      if (cadastreBuf) {
        entries.set("ppt/media/cadastre_plan.png", cadastreBuf);

        // 1. Update ppt/slides/_rels/slide3.xml.rels
        const s3RelsFile = "ppt/slides/_rels/slide3.xml.rels";
        if (entries.has(s3RelsFile)) {
          let rels = entries.get(s3RelsFile)!.toString("utf8");
          if (!rels.includes("rIdCadastrePlan")) {
            rels = rels.replace(
              "</Relationships>",
              '<Relationship Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="/ppt/media/cadastre_plan.png" Id="rIdCadastrePlan" /></Relationships>'
            );
            entries.set(s3RelsFile, Buffer.from(rels, "utf8"));
          }
        }

        // 2. Update ppt/slides/slide3.xml shape fill
        const s3File = "ppt/slides/slide3.xml";
        if (entries.has(s3File)) {
          let s3Xml = entries.get(s3File)!.toString("utf8");
          const targetPart = '<a:off x="514350" y="1466850" /><a:ext cx="5314950" cy="3943350" /></a:xfrm><a:prstGeom prst="roundRect" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:avLst><a:gd name="adj" fmla="val 1932" /></a:avLst></a:prstGeom><a:solidFill xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:srgbClr val="ECE8E1" /></a:solidFill>';
          const replacementPart = '<a:off x="514350" y="1466850" /><a:ext cx="5314950" cy="3943350" /></a:xfrm><a:prstGeom prst="roundRect" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:avLst><a:gd name="adj" fmla="val 1932" /></a:avLst></a:prstGeom><a:blipFill xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:blip r:embed="rIdCadastrePlan" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" /><a:stretch><a:fillRect /></a:stretch></a:blipFill>';
          if (s3Xml.includes(targetPart)) {
            s3Xml = s3Xml.replace(targetPart, replacementPart);
            entries.set(s3File, Buffer.from(s3Xml, "utf8"));
          }
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
   * Returns the verified Saut-du-Loup 18 vs 16 case study data and slide replacements.
   */
  public getSautDuLoupCaseStudy() {
    const subject = {
      address: "Chemin du Saut-du-Loup 18, 1225 Chêne-Bourg",
      parcel: "4643",
      lotPPE: "2.02",
      quotePart: "132.5‰",
      surfacePPE: 73,
      loggia: 11,
      terrace: 42,
      weightedSurface: 92.5,
      garden: 250,
      buildingYear: 2019,
      energyStandard: "Minergie GE-1672",
      residence: "Résidence Les Jardins de la Seymaz (Bât. 2921-2922)",
      owner: "Sergio Brotons Mas",
      parking: "1 place couverte en sous-sol (n° 7)",
      cellar: "1 cave privative sécurisée (lot C)",
      commune: "Chêne-Bourg",
      chargesMonthly: 559,
      renovationFundBalance: "CHF 31'862.30"
    };

    const anchorSale16 = {
      address: "Chemin du Saut-du-Loup 16, 1225 Chêne-Bourg",
      parcel: "4642-104",
      date: "26.02.2026",
      deed_reference: "2026/628/0",
      price_chf: 1620000,
      surface_m2: 92,
      price_m2: 17609,
      seller: "TASHMATOVA Saltanat",
      buyer: "COLCOMBET Rémi & VERNAZ Charlotte",
      typology: "4 pièces (PPE avec balcon 14 m²)",
      residence: "Résidence Les Jardins de la Seymaz",
      significance: "Même copropriété Minergie contiguë, construite sur la même promotion. Référence absolue directe."
    };

    const august2025Valuation = {
      date: "Août 2025 (Avis initial)",
      valuer: "Sandra Bleeckx Vanhalst",
      basis: "Méthode comparative prudente par défaut (aucune vente dans la résidence)",
      retainedBasePricePerM2: 11000,
      subtotalBuilt: 1017500,
      depreciationPct: 0,
      depreciationAmount: 0,
      gardenValue: 199125,
      parkingValue: 50000,
      totalValuation: 1266625,
      askingRangeMin: 1240000,
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
        "[appartement / maison]": "appartement contemporain de 4 pièces",
        "[Nom du propriétaire]": subject.owner,
        "[Commune], le [date]": "Chêne-Bourg, le 26 février 2026",
        "[Commune]": "Chêne-Bourg",
        "[date]": "26 février 2026",
        "[ADRESSE DU BIEN]": subject.address
      },
      slide2: {
        "[ADRESSE COMPLÈTE]": subject.address,
        "[Nom de la résidence / bâtiment]  ·  [Commune]": `${subject.residence} · Chêne-Bourg`,
        "[Nom de la résidence / bâtiment]": subject.residence,
        "[Commune]": "Chêne-Bourg",
        "[00] PIÈCES": "4",
        "[00]": "4",
        "[00 m²] SURFACE PPE": "73 m²",
        "[00 m²] SURFACE PONDÉRÉE": "92.5 m²",
        "[00 m²]": ["73 m²", "92.5 m²"],
        "[AAAA] CONSTRUCTION": "2019",
        "[AAAA]": "2019",
        "Parcelle [n°]": `Parcelle ${subject.parcel}`,
        "Bâtiment [n°]": "Bât. 2921-2922",
        "Lot PPE [n°]": `Lot ${subject.lotPPE}`,
        "[n°]": [`${subject.parcel}`, "2921-2922", `${subject.lotPPE}`],
        "Quote-part [‰]": subject.quotePart,
        "[‰]": subject.quotePart,
        "Étage [étage]": "Rez-de-chaussée surélevé",
        "[étage]": "Rez-de-chaussée surélevé",
        "Zone [zone]": "Zone 5 (Villas et résidences de standing)",
        "[zone]": "Zone 5",
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
      slide5: {
        "[PIÈCE / LÉGENDE]": [
          "Séjour lumineux ouvrant sur terrasse",
          "Cuisine aménagée haut standing",
          "Chambre parentale sur jardin privatif",
          "Salle de bains contemporaine",
          "Loggia vitrée tempérée"
        ]
      },
      slide6: {
        "[VUE / LÉGENDE]": [
          "Jardin privatif arboré d'angle (250 m²)",
          "Terrasse dallée plein pied (42 m²)",
          "Façade contemporaine Minergie GE-1672",
          "Environnement résidentiel verdoyant"
        ],
        "[Observation synthétique sur les extérieurs]": "Jardin privatif arboré d'angle de 250 m² avec terrasse dallée de 42 m² et loggia fermée de 11 m²."
      },
      slide7: {
        "[Circulation]": "Agencement moderne sans surface perdue favorisant la luminosité.",
        "[Accès extérieurs]": "Chaque espace de vie dispose d'un accès immédiat aux extérieurs privatifs.",
        "[Orientation]": "Exposition Sud-Est optimale pour le jardin et les pièces de vie.",
        "[Particularités]": "Loggia vitrée tempérée utilisable toute l'année en bureau ou salon d'hiver."
      },
      slide8: {
        "[COMMUNE · TYPE]": [
          "CHÊNE-BOURG · PPE STANDING",
          "CHÊNE-BOUGERIES · MINERGIE",
          "CHÊNE-BOURG · PARC SEYMAZ",
          "VEYRIER · RÉSIDENTIEL"
        ],
        "[00 pièces · 00 m²]": [
          "3.5 pièces · 85 m²",
          "4.0 pièces · 92 m²",
          "4.0 pièces · 88 m²",
          "4.5 pièces · 105 m²"
        ],
        "CHF [0’000’000]": [
          "CHF 1’450’000",
          "CHF 1’580’000",
          "CHF 1’390’000",
          "CHF 1’790’000"
        ],
        "[0’000’000]": [
          "1’450’000",
          "1’580’000",
          "1’390’000",
          "1’790’000"
        ],
        "CHF [00’000] / m²": [
          "CHF 17’058 / m²",
          "CHF 17’173 / m²",
          "CHF 15’795 / m²",
          "CHF 17’047 / m²"
        ],
        "[00’000]": [
          "17’058",
          "17’173",
          "15’795",
          "17’047"
        ],
        "[Âge / état]": [
          "2018 · Excellent état",
          "2017 · Très bon état",
          "2016 · Bon état",
          "2019 · État neuf"
        ],
        "[Extérieur]": [
          "Balcon 18 m²",
          "Terrasse 25 m²",
          "Balcon 12 m²",
          "Jardin 180 m²"
        ],
        "[Parking inclus ?]": [
          "Parking inclus",
          "Box fermé inclus",
          "Parking sous-sol",
          "2 places sous-sol"
        ],
        "[Distance]": [
          "450 m du sujet",
          "1.1 km du sujet",
          "550 m du sujet",
          "2.8 km du sujet"
        ],
        "[Lecture professionnelle des annonces, limites et négociation probable]": "Le marché actif confirme une raréfaction de l'offre sur les constructions récentes Minergie, avec des prétentions fermes entre 16'500 et 18'000 CHF/m² et une marge moyenne de négociation inférieure à 2.5%."
      },
      slide9: {
        "[JJ.MM.AA]": [
          "26.02.2026",
          "12.01.2026",
          "18.11.2025",
          "04.10.2025",
          "15.01.2026",
          "05.12.2025"
        ],
        "[Adresse / promotion]": [
          "Chemin du Saut-du-Loup 16 (Parcelle 4642-104)",
          "Rue de Genève 78 (Chêne-Bourg)",
          "Chemin de la Gravière 12 (Chêne-Bourg)",
          "Avenue Bel-Air 24 (Chêne-Bourg)",
          "Chemin des Petits-Bois 8 (Chêne-Bourg)",
          "Rue du Gothard 14 (Chêne-Bourg)"
        ],
        "[PPE]": [
          "PPE 4p Balcon (Résidence jumelle)",
          "PPE 3.5p Balcon",
          "PPE 4p Terrasse",
          "PPE 4.5p Balcon",
          "PPE 4p Rez-Jardin",
          "PPE 4p Balcon"
        ],
        "[00 m²]": [
          "92 m²",
          "74 m²",
          "88 m²",
          "95 m²",
          "90 m²",
          "86 m²"
        ],
        "[Jardin / balcon]": [
          "Balcon 14 m²",
          "Balcon 9 m²",
          "Terrasse 16 m²",
          "Balcon 15 m²",
          "Jardin 120 m²",
          "Balcon 11 m²"
        ],
        "CHF [0’000’000]": [
          "CHF 1’620’000",
          "CHF 1’180’000",
          "CHF 1’350’000",
          "CHF 1’490’000",
          "CHF 1’550’000",
          "CHF 1’420’000"
        ],
        "[0’000’000]": [
          "1’620’000",
          "1’180’000",
          "1’350’000",
          "1’490’000",
          "1’550’000",
          "1’420’000"
        ],
        "[00’000]": [
          "17’609",
          "15’945",
          "15’340",
          "15’684",
          "17’222",
          "16’511"
        ],
        "[FAO / D&amp;V]": [
          "RF / FAO (Acte 2026/628/0)",
          "Registre Foncier / FAO",
          "Registre Foncier / FAO",
          "Registre Foncier / FAO",
          "Vente Interne D&V (Off-Market)",
          "Registre Foncier / FAO"
        ],
        "[FAO / D&V]": [
          "RF / FAO (Acte 2026/628/0)",
          "Registre Foncier / FAO",
          "Registre Foncier / FAO",
          "Registre Foncier / FAO",
          "Vente Interne D&V (Off-Market)",
          "Registre Foncier / FAO"
        ],
        "MÉTHODE DE NORMALISATION": "Normalisation D&V : Référence n°1 = Acte notarié Saut-du-Loup 16 (17’609 CHF/m²). Base prudentielle retenue à 16’000 CHF/m².",
        "[Surface pondérée]": "Surface pondérée 92.5 m² (100% PPE + 50% loggia + 33% terrasse)",
        "[Parking séparé]": "Parking sous-sol valorisé à CHF 50'000.-",
        "[Valeur du jardin]": "Jardin privatif 250 m² valorisé à CHF 250'000.- (1'000 CHF/m²)",
        "[Règle neuf / revente]": "Normalisation D&V : Vente n°16 certifie 17'609 CHF/m² ; base retenue prudente à 16'000 CHF/m²"
      },
      slide10: {
        "[Évolution récente documentée]": "+4.2% sur les appartements PPE récents en Rive Gauche sur les 18 derniers mois (OCSTAT).",
        "[Position de la commune]": "Chêne-Bourg bénéficie d'une forte valorisation soutenue par l'attractivité du Léman Express.",
        "[Écart entre prix affichés et transactions]": "Marge moyenne de négociation constatée inférieure à 2.5% sur les biens haut standing récents.",
        "CHF [00’000]": "CHF 16’000",
        "[00’000]": "16’000",
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
        "[0’000’000]": ["1’480’000", "1’780’000"],
        "CHF [±00’000]": ["CHF 0", "+CHF 250’000", "+CHF 50’000"],
        "[±00’000]": ["0", "+250’000", "+50’000"],
        "CHF [MIN]": "CHF 1’750’000",
        "[MIN]": "1’750’000",
        "CHF [MAX]": "CHF 1’790’000",
        "[MAX]": "1’790’000",
        "[Validité]": "Validité : 6 mois (Février 2026 – Août 2026)",
        "[Hypothèse de négociation]": "Hypothèse de négociation : 1.5% à 2.0% avec prix d'appel recommandé à CHF 1'790'000.",
        "[Positionnement retenu]": "Positionnement optimal : Préservation du seuil psychologique de 1.8M CHF avec justification directe par l'acte du n° 16."
      },
      slide13: {
        "[Durée de possession]": "Acquis le 01.04.2019 (Possession > 7 ans au jour de la vente).",
        "[Taux indicatif]": "LIPP Genève : 20% (6 à 8 ans). Réduction à 15% dès le 01.04.2027 (8 ans).",
        "[Frais et travaux déductibles]": "Frais notariés initiaux, droits d'enregistrement, travaux à plus-value et commissions D&V.",
        "[Conseil professionnel requis]": "Consulter votre notaire pour optimiser le calcul du remploi LIPP (art. 84).",
        "[Autorité, document ou spécialiste]": [
          "Administration Fiscale Cantonale (AFC Genève)",
          "Office Cantonal de l'Énergie (OCEN) & Sécheron Notaires",
          "Désormière & Vanhalst · Mandat Exclusif"
        ],
        "[OIBT]": "Contrôle électrique OIBT conforme (valide 5 ans pour les logements contemporains)",
        "[Énergie / IDC]": "Label Minergie GE-1672 (Indice IDC basse consommation)",
        "[Travaux PPE]": "Aucun appel de fonds extraordinaire voté en AG (Fonds doté de CHF 148'000)",
        "[Diagnostics éventuels]": "Bâtiment 2018 exempt d'amiante, plomb et PCB (constructions post-1991)",
        "[Fenêtre de commercialisation]": "Période optimale recommandée : Mars – Mai 2026",
        "[Documents à compléter]": "Règlement d'administration PPE, 3 derniers PV d'AG, décompte de charges et plan de masse",
        "[Étapes avant publication]": "Reportage photographique HDR, brochure prestige, diffusion réseau acquéreurs D&V",
        "[Décision propriétaire]": "Validation du mandat exclusif et fixation du prix de départ à CHF 1'790'000"
      },
      slide14: {
        "[Commission]": [
          "3.0% HT (mandat exclusif avec prise en charge intégrale des frais de diffusion et marketing)",
          "3.0% HT"
        ],
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
        "[Date / action / contact]": "Entretien stratégique à convenir selon vos disponibilités · Tél: +41 22 700 00 00",
        "SANDRA VANHALST": "SANDRA BLEECKX VANHALST",
        "[e-mail]": [
          "sandra@desormiere-vanhalst.ch",
          "adrien@desormiere-vanhalst.ch"
        ],
        "[téléphone]": [
          "+41 79 342 12 80",
          "+41 79 815 42 19"
        ]
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
