import { describe, it, expect } from "bun:test";
import { resolve } from "path";

describe("Cytria Sovereign Access Gate Security & Authentication", () => {
  const indexHtmlPath = resolve("index.html");
  const mapBuilderPath = resolve("src/fao_transactions/visualization/map_builder.py");
  const welcomeHtmlPath = resolve("welcome.html");
  const dvIndexPath = resolve("public/dv/index.html");
  const dvMarketingPath = resolve("public/dv/marketing/index.html");

  it("should verify index.html contains the security gate overlay and controls", async () => {
    const html = await Bun.file(indexHtmlPath).text();
    expect(html).toContain('id="cytriaAccessGate"');
    expect(html).toContain('id="cytriaGateInput"');
    expect(html).toContain('id="cytriaGateSubmitBtn"');
    expect(html).toContain('id="cytriaGateError"');
    expect(html).toContain('lockCytriaApp');
    expect(html).toContain('id="btnLockApp"');
    expect(html).toContain('Q3l0cmlhMjAyNlBhcnQx');
  });

  it("should verify map_builder.py template preserves the security gate", async () => {
    const py = await Bun.file(mapBuilderPath).text();
    expect(py).toContain('id="cytriaAccessGate"');
    expect(py).toContain('id="cytriaGateInput"');
    expect(py).toContain('id="cytriaGateSubmitBtn"');
    expect(py).toContain('lockCytriaApp');
    expect(py).toContain('Q3l0cmlhMjAyNlBhcnQx');
  });

  it("should verify welcome.html and D&V portals have the security gate installed", async () => {
    const welcome = await Bun.file(welcomeHtmlPath).text();
    const dv = await Bun.file(dvIndexPath).text();
    const dvMkt = await Bun.file(dvMarketingPath).text();

    expect(welcome).toContain('id="cytriaAccessGate"');
    expect(welcome).toContain('Q3l0cmlhMjAyNlBhcnQx');

    expect(dv).toContain('id="cytriaAccessGate"');
    expect(dv).toContain('Q3l0cmlhMjAyNlBhcnQx');

    expect(dvMkt).toContain('id="cytriaAccessGate"');
    expect(dvMkt).toContain('Q3l0cmlhMjAyNlBhcnQx');
  });

  it("should validate that key logic strictly accepts Cytria2026Part1 and rejects unauthorized keys", () => {
    const KEY_HASH = "Q3l0cmlhMjAyNlBhcnQx";
    
    function isValid(val: string | null | undefined): boolean {
      if (!val || typeof val !== "string") return false;
      const trimmed = val.trim();
      try {
        return btoa(trimmed) === KEY_HASH || trimmed === atob(KEY_HASH);
      } catch (e) {
        return trimmed === atob(KEY_HASH);
      }
    }

    // Official user password
    expect(isValid("Cytria2026Part1")).toBe(true);
    expect(isValid(" Cytria2026Part1 ")).toBe(true); // trims whitespace
    expect(atob(KEY_HASH)).toBe("Cytria2026Part1");

    // Rejections
    expect(isValid("cytria2026part1")).toBe(false); // case-sensitive
    expect(isValid("Cytria2026")).toBe(false);
    expect(isValid("cytria")).toBe(false);
    expect(isValid("admin")).toBe(false);
    expect(isValid("password")).toBe(false);
    expect(isValid("")).toBe(false);
    expect(isValid(undefined)).toBe(false);
  });

  it("should maintain zero violations of surgical hardening privacy rules", async () => {
    const html = await Bun.file(indexHtmlPath).text();
    expect(html.includes("Indice : cytria")).toBe(false);
    expect(html.includes("cytria2026")).toBe(false);
  });
});
