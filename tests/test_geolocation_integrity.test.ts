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
      return r.lat < 46.12 || r.lat > 46.36 || r.lon < 5.95 || r.lon > 6.32;
    });

    expect(outOfBounds.length).toBe(0);
  });

  it("Chêne-Bougeries properties are strictly located within Chêne-Bougeries bounds", async () => {
    const html = await Bun.file("index.html").text();
    const dataMatch = html.match(/const DATA = (\[[\s\S]*?\]);/);
    const data = JSON.parse(dataMatch![1]);

    const cheneProps = data.filter((r: any) => r.commune === "Chêne-Bougeries");
    expect(cheneProps.length).toBeGreaterThan(50);

    // Chêne-Bougeries bounding box: lat ~ 46.18 - 46.21, lon ~ 6.17 - 6.20
    // Baby-Plage / Eaux-Vives lake is at lat: 46.208+, lon: 6.160-6.162 (West of 6.165)
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
});
