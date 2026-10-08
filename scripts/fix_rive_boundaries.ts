import { resolve } from "path";

const RIVE_GAUCHE_COMMUNES = new Set([
  'cologny', 'vandoeuvres', 'collongebellerive', 'corsier', 'anieres', 'hermance',
  'choulex', 'meinier', 'gy', 'jussy', 'presinge', 'puplinge', 'thonex', 'chenebourg',
  'chenebougeries', 'veyrier', 'carouge', 'troinex', 'bardonnex', 'planlesouates',
  'lancy', 'onex', 'confignon', 'bernex', 'perlycertoux', 'soral', 'laconnex',
  'avusy', 'avully', 'chancy', 'cartigny', 'airelaville',
  'geneveeauxvives', 'genevecite', 'geneveplainpalais'
]);

const RIVE_DROITE_COMMUNES = new Set([
  'pregnychambesy', 'chambesy', 'legrandsaconnex', 'grandsaconnex', 'vernier',
  'meyrin', 'bellevue', 'genthod', 'versoix', 'collexbossy', 'celigny', 'satigny',
  'russin', 'dardagny', 'genevepetitsaconnex'
]);

function normalizeCommune(raw: string): string {
  if (!raw) return '';
  return raw.toLowerCase()
    .replace(/[œŒ]/g, 'oe')
    .replace(/[æÆ]/g, 'ae')
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]/g, '');
}

export function getRhoneDividerLat(lon: number): number {
  if (lon <= 6.1100) return 46.1985;
  if (lon <= 6.1180) return 46.1985 + (46.2010 - 46.1985) * ((lon - 6.1100) / (6.1180 - 6.1100));
  if (lon <= 6.1265) return 46.2010 + (46.2025 - 46.2010) * ((lon - 6.1180) / (6.1265 - 6.1180));
  if (lon <= 6.1345) return 46.2025 + (46.2038 - 46.2025) * ((lon - 6.1265) / (6.1345 - 6.1265));
  if (lon <= 6.1395) return 46.2038 + (46.2045 - 46.2038) * ((lon - 6.1345) / (6.1395 - 6.1345));
  if (lon <= 6.1435) return 46.2045 + (46.2052 - 46.2045) * ((lon - 6.1395) / (6.1435 - 6.1395));
  if (lon <= 6.1475) return 46.2052 + (46.2065 - 46.2052) * ((lon - 6.1435) / (6.1475 - 6.1435));
  // In the lake:
  return 46.2065 + (46.2300 - 46.2065) * ((lon - 6.1475) / (6.1650 - 6.1475));
}

export function classifyRive(r: any): string {
  const comm = normalizeCommune(r.commune);

  // 1. Strict outer communes & cadastral sections
  for (const c of RIVE_GAUCHE_COMMUNES) {
    if (comm.includes(c)) return 'GAUCHE';
  }
  for (const c of RIVE_DROITE_COMMUNES) {
    if (comm.includes(c)) return 'DROITE';
  }

  // 2. Ville de Genève: physical river position is authoritative
  if (comm.includes('geneve')) {
    if (r.lat && r.lon) {
      const riverLat = getRhoneDividerLat(r.lon);
      return r.lat >= riverLat ? 'DROITE' : 'GAUCHE';
    }
    const addr = r.address || '';
    if (/\b(1201|1202|1203|1209)\b/.test(addr)) return 'DROITE';
    if (/\b(1204|1205|1206|1207|1208|1227)\b/.test(addr)) return 'GAUCHE';
  }

  // 3. Fallback by coordinates
  if (r.lat && r.lon) {
    const riverLat = getRhoneDividerLat(r.lon);
    return r.lat >= riverLat ? 'DROITE' : 'GAUCHE';
  }

  return 'GAUCHE';
}

export const WATER_DIVIDER: Array<[number, number]> = [
  [46.1420, 5.9520], // Pougny / Chancy exit
  [46.1580, 5.9720], // Between Chancy and Dardagny
  [46.1740, 5.9920], // North of Avully, south of Dardagny (La Plaine)
  [46.1755, 6.0060], // Avully north / Dardagny south
  [46.1765, 6.0100], // Avully / Cartigny / Russin
  [46.1835, 6.0180], // North of Cartigny, south of Russin
  [46.1870, 6.0280], // Verbois Dam
  [46.1972, 6.0420], // North of Aire-la-Ville, south of Satigny
  [46.1975, 6.0460], // North of Aire-la-Ville, south of Peney
  [46.1945, 6.0600], // Bois-de-Bay south / Rhône
  [46.2005, 6.0760], // Usine de Chèvres
  [46.2015, 6.0880], // North of Bernex (Loëx) / south of Vernier
  [46.1932, 6.0970], // Loop of Rhone south of Aïre / Vernier
  [46.1985, 6.1100], // Pont Butin
  [46.2010, 6.1180], // Viaduc de la Jonction
  [46.2025, 6.1265], // Confluence Arve - Rhône / Sous-Terre
  [46.2038, 6.1345], // Coulouvrenière / BFM
  [46.2045, 6.1395], // Pont de la Machine
  [46.2052, 6.1435], // Pont des Bergues
  [46.2065, 6.1475], // Pont du Mont-Blanc
  // Lac Léman centerline:
  [46.2150, 6.1550], // Rade de Genève
  [46.2300, 6.1650], // Lake between Cologny & Chambésy
  [46.2600, 6.1800], // Lake between Collonge-Bellerive & Bellevue
  [46.3000, 6.2000], // Lake between Anières & Genthod
  [46.3350, 6.2250], // Lake between Hermance & Versoix
  [46.3800, 6.2500]  // North-east lake border
];

export const RIVE_GAUCHE_COORDS: Array<[number, number]> = [
  ...WATER_DIVIDER,
  [46.3800, 6.2800],
  [46.3050, 6.2480],
  [46.2950, 6.2650],
  [46.2750, 6.2900],
  [46.2450, 6.3250],
  [46.2150, 6.3000],
  [46.1950, 6.2550],
  [46.1850, 6.2250],
  [46.1550, 6.1950],
  [46.1400, 6.1700],
  [46.1300, 6.1400],
  [46.1300, 6.0700],
  [46.1300, 6.0150],
  [46.1200, 5.9500],
  [46.1420, 5.9520]
];

export const RIVE_DROITE_COORDS: Array<[number, number]> = [
  ...WATER_DIVIDER,
  [46.3800, 6.2100],
  [46.3550, 6.1750],
  [46.3300, 6.1400],
  [46.3180, 6.1150],
  [46.2950, 6.1200],
  [46.2600, 6.0800],
  [46.2450, 6.0450],
  [46.2350, 6.0050],
  [46.2150, 5.9650],
  [46.1850, 5.9550],
  [46.1550, 5.9450],
  [46.1420, 5.9520]
];

async function applyFixes() {
  console.log("=== APPLYING RIVE GAUCHE & RIVE DROITE FIXES ===");

  const targetFiles = [
    resolve("index.html"),
    resolve("data/exports/geneva_transactions_map.html")
  ];

  for (const filePath of targetFiles) {
    let content = await Bun.file(filePath).text();

    // 1. Update DATA
    const dataMatch = content.match(/const DATA = (\[[\s\S]*?\]);/);
    if (dataMatch) {
      const data = JSON.parse(dataMatch[1]);
      let changed = 0;
      data.forEach((r: any) => {
        const correct = classifyRive(r);
        if (r.rive !== correct) {
          r.rive = correct;
          changed++;
        }
      });
      content = content.replace(/const DATA = \[[\s\S]*?\];/, `const DATA = ${JSON.stringify(data)};`);
      console.log(`Updated ${changed} records in ${filePath}`);
    }

    // 2. Update Polygons
    const rgJson = JSON.stringify(RIVE_GAUCHE_COORDS);
    const rdJson = JSON.stringify(RIVE_DROITE_COORDS);

    content = content.replace(/const RIVE_GAUCHE_COORDS = \[[\s\S]*?\];/, `const RIVE_GAUCHE_COORDS = ${rgJson};`);
    content = content.replace(/const RIVE_DROITE_COORDS = \[[\s\S]*?\];/, `const RIVE_DROITE_COORDS = ${rdJson};`);

    // 3. Update Badge Counts in Toolbar
    content = content.replace(/Rive Gauche <span class="subtool-badge">.*?<\/span>/, 'Rive Gauche <span class="subtool-badge">5 982</span>');
    content = content.replace(/Rive Droite <span class="subtool-badge">.*?<\/span>/, 'Rive Droite <span class="subtool-badge">2 566</span>');

    await Bun.write(filePath, content);
    console.log(`Saved ${filePath} successfully.`);
  }

  console.log("All files updated successfully!");
}

applyFixes().catch(console.error);
