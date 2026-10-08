import { describe, it, expect } from "bun:test";
import { Database } from "bun:sqlite";

describe("Geolocation & Address Integrity Across Datasets", () => {
  it("index.html DATA array has 0 dummy placeholder addresses", async () => {
    const html = await Bun.file("index.html").text();
    const dataMatch = html.match(/const DATA = (\[[\s\S]*?\]);/);
    expect(dataMatch).toBeTruthy();

    const data = JSON.parse(dataMatch![1]);
    expect(data.length).toBeGreaterThan(8000);

    const dummyAddresses = data.filter((r: any) => r.address && r.address.includes("Avenue ou Chemin"));
    expect(dummyAddresses.length).toBe(0);
  });

  it("All properties in index.html are strictly within Geneva geographic boundary", async () => {
    const html = await Bun.file("index.html").text();
    const dataMatch = html.match(/const DATA = (\[[\s\S]*?\]);/);
    const data = JSON.parse(dataMatch![1]);

    const outOfBounds = data.filter((r: any) => {
      if (!r.lat || !r.lon) return false;
      return r.lat < 46.12 || r.lat > 46.37 || r.lon < 5.94 || r.lon > 6.33;
    });

    expect(outOfBounds.length).toBe(0);
  });

  it("Chêne-Bougeries properties are strictly located within Chêne-Bougeries bounds", async () => {
    const html = await Bun.file("index.html").text();
    const dataMatch = html.match(/const DATA = (\[[\s\S]*?\]);/);
    const data = JSON.parse(dataMatch![1]);

    const cheneProps = data.filter((r: any) => r.commune === "Chêne-Bougeries");
    expect(cheneProps.length).toBeGreaterThan(50);

    const misplacedAtLake = cheneProps.filter((r: any) => r.lat > 46.205 && r.lon < 6.165);
    expect(misplacedAtLake.length).toBe(0);
  });

  it("state.sqlite transactions and agency_sold_properties have 0 dummy placeholder addresses", () => {
    const db = new Database("data/state/state.sqlite", { readonly: true });

    const txDummies = db.query("SELECT count(*) as c FROM transactions WHERE address LIKE '%Avenue ou Chemin%'").get() as any;
    expect(txDummies.c).toBe(0);

    const agencyDummies = db.query("SELECT count(*) as c FROM agency_sold_properties WHERE address LIKE '%Avenue ou Chemin%'").get() as any;
    expect(agencyDummies.c).toBe(0);

    db.close();
  });

  it("All outer Geneva communes are 100% strictly assigned to their correct Rive", async () => {
    const html = await Bun.file("index.html").text();
    const dataMatch = html.match(/const DATA = (\[[\s\S]*?\]);/);
    const data = JSON.parse(dataMatch![1]);

    const RIVE_GAUCHE = [
      "Cologny", "Vandoeuvres", "Vandœuvres", "Collonge-Bellerive", "Corsier", "Anières", "Hermance",
      "Choulex", "Meinier", "Gy", "Jussy", "Presinge", "Puplinge", "Thônex", "Chêne-Bourg",
      "Chêne-Bougeries", "Veyrier", "Carouge", "Troinex", "Bardonnex", "Plan-les-Ouates",
      "Lancy", "Onex", "Confignon", "Bernex", "Perly-Certoux", "Soral", "Laconnex",
      "Avusy", "Avully", "Chancy", "Cartigny", "Aire-la-Ville",
      "Genève-Eaux-Vives", "Genève-Cité", "Genève-Plainpalais"
    ];

    const RIVE_DROITE = [
      "Pregny-Chambésy", "Chambésy", "Grand-Saconnex", "Le Grand-Saconnex", "Vernier",
      "Meyrin", "Bellevue", "Genthod", "Versoix", "Collex-Bossy", "Céligny", "Celigny",
      "Satigny", "Russin", "Dardagny", "Genève-Petit-Saconnex"
    ];

    for (const comm of RIVE_GAUCHE) {
      const records = data.filter((r: any) => r.commune === comm);
      const wrong = records.filter((r: any) => r.rive !== "GAUCHE");
      expect(wrong.length).toBe(0);
    }

    for (const comm of RIVE_DROITE) {
      const records = data.filter((r: any) => r.commune === comm);
      const wrong = records.filter((r: any) => r.rive !== "DROITE");
      expect(wrong.length).toBe(0);
    }
  });

  it("Ville de Genève properties with explicit postal codes are correctly classified by Rive", async () => {
    const html = await Bun.file("index.html").text();
    const dataMatch = html.match(/const DATA = (\[[\s\S]*?\]);/);
    const data = JSON.parse(dataMatch![1]);

    const genevaProps = data.filter((r: any) => (r.commune || "").toLowerCase() === "genève");

    for (const r of genevaProps) {
      const addr = r.address || "";
      if (/\b(1201|1202|1203|1209)\b/.test(addr)) {
        expect(r.rive).toBe("DROITE");
      }
      if (/\b(1204|1205|1206|1207|1208|1227)\b/.test(addr)) {
        expect(r.rive).toBe("GAUCHE");
      }
    }
  });

  it("Rive Gauche and Rive Droite polygons in index.html have clean separation and proper bounds", async () => {
    const html = await Bun.file("index.html").text();
    const rgMatch = html.match(/const RIVE_GAUCHE_COORDS = (\[[\s\S]*?\]);/);
    const rdMatch = html.match(/const RIVE_DROITE_COORDS = (\[[\s\S]*?\]);/);

    expect(rgMatch).toBeTruthy();
    expect(rdMatch).toBeTruthy();

    const rgCoords: Array<[number, number]> = JSON.parse(rgMatch![1]);
    const rdCoords: Array<[number, number]> = JSON.parse(rdMatch![1]);

    // Rive Droite polygon must NOT contain points on Rive Gauche inland/coast like Hermance/Jussy (lon > 6.25, lat < 46.31)
    const rdAtGaucheLand = rdCoords.filter(([lat, lon]) => lon > 6.25 && lat < 46.31);
    expect(rdAtGaucheLand.length).toBe(0);

    // Both polygons must close (start equals end)
    expect(rgCoords[0][0]).toBe(rgCoords[rgCoords.length - 1][0]);
    expect(rgCoords[0][1]).toBe(rgCoords[rgCoords.length - 1][1]);
    expect(rdCoords[0][0]).toBe(rdCoords[rdCoords.length - 1][0]);
    expect(rdCoords[0][1]).toBe(rdCoords[rdCoords.length - 1][1]);
  });

  it("Chemin de Conches properties strictly match the real street axis (not displaced onto Tornalettes)", async () => {
    const html = await Bun.file("index.html").text();
    const dataMatch = html.match(/const DATA = (\[[\s\S]*?\]);/);
    const data = JSON.parse(dataMatch![1]);

    const conchesProps = data.filter((r: any) => r.address && r.address.includes("Chemin de Conches"));
    expect(conchesProps.length).toBeGreaterThanOrEqual(3);

    for (const r of conchesProps) {
      // True Chemin de Conches is south of 46.184. Chemin des Tornalettes is around 46.1862+.
      expect(r.lat).toBeLessThan(46.1845);
      expect(r.lat).toBeGreaterThan(46.1750);
      expect(r.lon).toBeGreaterThan(6.1700);
      expect(r.lon).toBeLessThan(6.1780);
    }
  });
});
