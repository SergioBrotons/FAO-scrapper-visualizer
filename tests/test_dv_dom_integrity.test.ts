import { describe, it, expect } from "bun:test";
import fs from "fs";
import path from "path";

describe("D&V 5-Screen Portal & 6-Step Valuation Wizard UI Integrity", () => {
  const htmlPath = path.resolve("public/dv/index.html");
  const html = fs.readFileSync(htmlPath, "utf8");

  it("should verify public/dv/index.html has zero missing document.getElementById references", () => {
    const regex = /document\.getElementById\(['"]([^'"]+)['"]\)/g;
    let match;
    const ids = new Set<string>();

    while ((match = regex.exec(html)) !== null) {
      ids.add(match[1]);
    }

    const missing: string[] = [];
    for (const id of ids) {
      if (!html.includes(`id="${id}"`)) {
        missing.push(id);
      }
    }

    expect(missing).toEqual([]);
    expect(ids.size).toBeGreaterThan(30);
  });

  it("should verify all HTML inline event handlers map to declared JavaScript functions", () => {
    const scriptMatch = html.match(/<script>([\s\S]*?)<\/script>/);
    expect(scriptMatch).toBeTruthy();
    const script = scriptMatch![1];

    const declaredFunctions = new Set<string>();
    const declRegex = /function\s+([a-zA-Z0-9_$]+)\s*\(/g;
    let m;
    while ((m = declRegex.exec(script)) !== null) {
      declaredFunctions.add(m[1]);
    }

    const htmlHandlerRegex = /on[a-z]+\s*=\s*['"]([a-zA-Z0-9_$]+)\s*\(/g;
    const missingHandlers: string[] = [];
    while ((m = htmlHandlerRegex.exec(html)) !== null) {
      const fnName = m[1];
      if (!declaredFunctions.has(fnName)) {
        missingHandlers.push(fnName);
      }
    }

    expect(missingHandlers).toEqual([]);
  });

  it("should verify all 5 distinct screens/views exist in navigation and DOM", () => {
    // 5 Navigation Tabs
    expect(html.includes(`id="tabHubBtn"`)).toBe(true);
    expect(html.includes(`id="tabValueBtn"`)).toBe(true);
    expect(html.includes(`id="tabRadarBtn"`)).toBe(true);
    expect(html.includes(`id="tabMandatesBtn"`)).toBe(true);
    expect(html.includes(`id="tabBuyersBtn"`)).toBe(true);

    // 5 Screen Views
    expect(html.includes(`id="viewHub"`)).toBe(true);
    expect(html.includes(`id="viewValue"`)).toBe(true);
    expect(html.includes(`id="viewRadar"`)).toBe(true);
    expect(html.includes(`id="viewMandates"`)).toBe(true);
    expect(html.includes(`id="viewBuyers"`)).toBe(true);
  });

  it("should verify the Valuation Studio has the full 6-Step guided wizard & PPTX generator", () => {
    // Case study banner and demo zone
    expect(html.includes(`id="sautDuLoupBanner"`)).toBe(true);
    expect(html.includes(`id="demoZoneStrip"`)).toBe(true);

    // 6 Wizard Step Tabs
    for (let i = 1; i <= 6; i++) {
      expect(html.includes(`id="wizardTab${i}"`)).toBe(true);
      expect(html.includes(`id="wizardPane${i}"`)).toBe(true);
    }

    // Step 1: Cadastre & Dynamic Autocomplete
    expect(html.includes(`id="wizAddress"`)).toBe(true);
    expect(html.includes(`id="addressSuggestionsDropdown"`)).toBe(true);
    expect(html.includes(`id="addressLoadingSpinner"`)).toBe(true);
    expect(html.includes(`id="cadastreLockBadge"`)).toBe(true);
    expect(html.includes(`id="btnAutoFillSystem"`)).toBe(true);
    expect(html.includes(`id="btnSitgMap"`)).toBe(true);
    expect(html.includes(`id="wizCommune"`)).toBe(true);
    expect(html.includes(`id="wizParcel"`)).toBe(true);
    expect(html.includes(`id="wizBuilding"`)).toBe(true);
    expect(html.includes(`id="wizLotPPE"`)).toBe(true);
    expect(html.includes(`id="wizZone"`)).toBe(true);
    expect(html.includes(`id="wizBuildingYear"`)).toBe(true);

    // Step 2: Surfaces & Technique
    expect(html.includes(`id="wizSurfPPE"`)).toBe(true);
    expect(html.includes(`id="wizSurfLoggia"`)).toBe(true);
    expect(html.includes(`id="wizSurfTerrace"`)).toBe(true);
    expect(html.includes(`id="wizWeightedSurf"`)).toBe(true);
    expect(html.includes(`id="wizSurfGarden"`)).toBe(true);
    expect(html.includes(`id="wizRooms"`)).toBe(true);
    expect(html.includes(`id="wizParking"`)).toBe(true);
    expect(html.includes(`id="wizCellar"`)).toBe(true);
    expect(html.includes(`id="wizHeating"`)).toBe(true);

    // Step 3: Photos & Dropzones
    expect(html.includes(`id="fileCover"`)).toBe(true);
    expect(html.includes(`id="previewCover"`)).toBe(true);
    expect(html.includes(`id="fileInterior"`)).toBe(true);
    expect(html.includes(`id="previewInterior"`)).toBe(true);
    expect(html.includes(`id="fileExterior"`)).toBe(true);
    expect(html.includes(`id="previewExterior"`)).toBe(true);
    expect(html.includes(`id="filePlan"`)).toBe(true);
    expect(html.includes(`id="previewPlan"`)).toBe(true);

    // Step 4: Comparables
    expect(html.includes(`id="wizardCompsTbody"`)).toBe(true);
    expect(html.includes(`id="wizNormMethod"`)).toBe(true);

    // Step 5: Méthode & Indices OCSTAT
    expect(html.includes(`id="sliderBasePriceM2"`)).toBe(true);
    expect(html.includes(`id="sliderGardenValue"`)).toBe(true);
    expect(html.includes(`id="sliderParkingValue"`)).toBe(true);
    expect(html.includes(`id="wizOcstatPpeMedian"`)).toBe(true);
    expect(html.includes(`id="wizOcstatCantonMedian"`)).toBe(true);
    expect(html.includes(`id="wizOcstatTrend"`)).toBe(true);
    expect(html.includes(`id="wizOcstatSpread"`)).toBe(true);
    expect(html.includes(`id="wizMarketTrend"`)).toBe(true);

    // Step 6: Stratégie & Export PPTX
    expect(html.includes(`id="wizTargetPrice"`)).toBe(true);
    expect(html.includes(`id="wizRangeMin"`)).toBe(true);
    expect(html.includes(`id="wizRangeMax"`)).toBe(true);
    expect(html.includes(`id="btnExportPptx"`)).toBe(true);
    expect(html.includes(`id="btnWizExportPptx"`)).toBe(true);

    // Direct precompiled PPTX download fallback link
    expect(html.includes("Estimation_Saut_du_Loup_18_Brotons_2026.pptx")).toBe(true);

    // Modals
    expect(html.includes(`id="neighborModal"`)).toBe(true);
    expect(html.includes(`id="cmaModal"`)).toBe(true);
  });

  it("should verify essential JS functions are defined", () => {
    expect(html.includes("function switchView(")).toBe(true);
    expect(html.includes("function switchWizardStep(")).toBe(true);
    expect(html.includes("function loadSautDuLoupCase()")).toBe(true);
    expect(html.includes("function resetBlankStudio()")).toBe(true);
    expect(html.includes("function toggleDemoZone()")).toBe(true);
    expect(html.includes("function exportPresentationPptx()")).toBe(true);
    expect(html.includes("function recalculateSurfaces()")).toBe(true);
    expect(html.includes("function updateValuationFormula()")).toBe(true);
    expect(html.includes("function handleImageUpload(")).toBe(true);
    expect(html.includes("function initAddressAutocomplete()")).toBe(true);
    expect(html.includes("function selectCadastreProperty(")).toBe(true);
    expect(html.includes("function autoFillFromSystem()")).toBe(true);
  });
});
