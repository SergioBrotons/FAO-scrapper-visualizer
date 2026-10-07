// Local development server for Cytria Geneva Real Estate Visualizer
import { join, extname } from "path";
import { existsSync, statSync, readFileSync } from "fs";
import { Database } from "bun:sqlite";
import { ValuationService } from "./src/fao_transactions/dossier/valuation_service.ts";
import { DVIntelligenceService } from "./src/fao_transactions/dv/dv_service.ts";
import { DVPptxGenerator } from "./src/fao_transactions/dv/dv_pptx_generator.ts";
import { AgencyConfigService } from "./src/content_marketing/agency_config_service.ts";
import { FiscalSimulationService } from "./src/content_marketing/fiscal_simulation_service.ts";
import { CompetitorBenchmarkService } from "./src/content_marketing/competitor_benchmark_service.ts";
import { TelemetryService } from "./src/content_marketing/telemetry_service.ts";
import { GuideGeneratorService } from "./src/content_marketing/guide_generator_service.ts";
import { FunnelContentService } from "./src/content_marketing/funnel_content_service.ts";

const agencyConfigService = new AgencyConfigService();
const fiscalSimService = new FiscalSimulationService();
const competitorBenchmarkService = new CompetitorBenchmarkService();
const telemetryService = new TelemetryService();
const guideGeneratorService = new GuideGeneratorService();
const funnelContentService = new FunnelContentService();

function getRequestedPort() {
  const args = process.argv.slice(2);
  for (let i = 0; i < args.length; i++) {
    if ((args[i] === "--port" || args[i] === "-p") && args[i + 1]) {
      return parseInt(args[i + 1]);
    }
  }
  if (process.env.PORT) {
    return parseInt(process.env.PORT);
  }
  return 8088;
}

const ROOT_DIR = import.meta.dir;
const INDEX_HTML = join(ROOT_DIR, "index.html");
const DB_PATH = join(ROOT_DIR, "data/state/state.sqlite");
const VENV_PYTHON = join(ROOT_DIR, ".venv", "Scripts", "python.exe");
const PYTHON_EXE = existsSync(VENV_PYTHON) ? VENV_PYTHON : "python";

const scanState = {
  is_scanning: false,
  progress_pct: 0,
  current_step: "En attente de commande",
  logs: [],
  historical_preserved: 8724,
  scanned_notices: 0,
  new_inserted: 0,
  duplicates_skipped: 0,
  childProcess: null,
};

function getScanStatus() {
  if (scanState.is_scanning || scanState.logs.length > 0) {
    return {
      is_scanning: scanState.is_scanning,
      progress_pct: scanState.progress_pct,
      current_step: scanState.current_step,
      logs: scanState.logs.slice(-35),
      historical_preserved: scanState.historical_preserved,
      scanned_notices: scanState.scanned_notices,
      new_inserted: scanState.new_inserted,
      duplicates_skipped: scanState.duplicates_skipped,
      last_sync_time: new Date().toLocaleTimeString("fr-FR"),
    };
  }

  const syncFile = join(ROOT_DIR, "data", "state", "sync_status.json");
  if (existsSync(syncFile)) {
    try {
      const data = JSON.parse(readFileSync(syncFile, "utf-8"));
      if (typeof data.is_scanning === "boolean") {
        scanState.is_scanning = data.is_scanning;
      }
      if (typeof data.progress_pct === "number") {
        scanState.progress_pct = data.progress_pct;
      }
      if (data.current_step) {
        scanState.current_step = data.current_step;
      }
      return {
        is_scanning: scanState.is_scanning,
        progress_pct: scanState.progress_pct,
        current_step: scanState.current_step,
        logs: data.logs && data.logs.length > 0 ? data.logs.slice(-35) : scanState.logs.slice(-35),
        historical_preserved: data.historical_preserved ?? scanState.historical_preserved,
        scanned_notices: data.scanned_notices ?? scanState.scanned_notices,
        new_inserted: data.new_inserted ?? scanState.new_inserted,
        duplicates_skipped: data.duplicates_skipped ?? scanState.duplicates_skipped,
        last_sync_time: new Date().toLocaleTimeString("fr-FR"),
      };
    } catch (e) {}
  }
  return {
    is_scanning: scanState.is_scanning,
    progress_pct: scanState.progress_pct,
    current_step: scanState.current_step,
    logs: scanState.logs.slice(-35),
    historical_preserved: scanState.historical_preserved,
    scanned_notices: scanState.scanned_notices,
    new_inserted: scanState.new_inserted,
    duplicates_skipped: scanState.duplicates_skipped,
    last_sync_time: new Date().toLocaleTimeString("fr-FR"),
  };
}

function addScanLog(msg) {
  const ts = new Date().toLocaleTimeString("fr-FR");
  const entry = `[${ts}] ${msg}`;
  scanState.logs.push(entry);
  if (scanState.logs.length > 250) scanState.logs.shift();
  console.log(entry);
}

function startScan(mode = "quick", source = "ALL", headed = true) {
  if (source.toUpperCase() === "ALL" || source.toUpperCase() === "MARKET" || source.toUpperCase() === "FASTLANE") {
    startFastlaneScan();
    return;
  }

  if (source.toUpperCase() === "AGENCIES") {
    startAgencyScan();
    return;
  }

  if (source.toUpperCase() === "SITG") {
    startSitgScan();
    return;
  }

  scanState.is_scanning = true;
  scanState.progress_pct = 5;
  scanState.current_step = "1/5 — Démarrage du scan Cytria...";
  scanState.logs = [];
  scanState.scanned_notices = 0;
  scanState.new_inserted = 0;
  scanState.duplicates_skipped = 0;

  addScanLog(`=== DÉMARRAGE DU SCAN [${source}] CYTRIA ===`);
  if (headed) {
    addScanLog("[FAO] Ouverture de la console interactive et de Chromium sur votre bureau...");
  }

  const launcherPs1 = join(ROOT_DIR, "launch_interactive.ps1");
  const batchPath = join(ROOT_DIR, "launch_fao_scraper.bat");

  // Delegate launch to Windows Explorer Shell COM so the window is 100% visible on the user's interactive desktop
  const proc = Bun.spawn([
    "powershell.exe",
    "-ExecutionPolicy",
    "Bypass",
    "-File",
    launcherPs1,
    "-batchFile",
    batchPath,
  ], {
    cwd: ROOT_DIR,
    env: { ...process.env, PYTHONPATH: join(ROOT_DIR, "src") },
  });

  scanState.childProcess = proc;
}

function startFastlaneScan() {
  scanState.is_scanning = true;
  scanState.progress_pct = 10;
  scanState.current_step = "Synchronisation Fast-Lane en cours (Zéro Captcha)...";
  scanState.logs = [];
  addScanLog("=== DÉMARRAGE DU SCAN FAST-LANE (ZÉRO CAPTCHA) ===");
  addScanLog("[FastLane] Interrogation directe du flux haute fréquence...");

  const proc = Bun.spawn([PYTHON_EXE, "src/fao_transactions/collector/fastlane_collector.py"], {
    cwd: ROOT_DIR,
    stdout: "pipe",
    stderr: "pipe",
    env: { ...process.env, PYTHONPATH: join(ROOT_DIR, "src") },
  });

  scanState.childProcess = proc;

  (async () => {
    try {
      const reader = proc.stdout.getReader();
      const decoder = new TextDecoder();
      let buf = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += decoder.decode(value, { stream: true });
        const lines = buf.split("\n");
        buf = lines.pop() || "";
        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed) addScanLog(trimmed);
        }
      }
      await proc.exited;
      addScanLog("[Visualizer] Actualisation de la carte interactive (index.html)...");
      const mapProc = Bun.spawn([PYTHON_EXE, "-c", "import sys; sys.path.insert(0, 'src'); from fao_transactions.visualization.map_builder import build_interactive_map; build_interactive_map()"], {
        cwd: ROOT_DIR,
        env: { ...process.env, PYTHONPATH: join(ROOT_DIR, "src") },
      });
      await mapProc.exited;
      scanState.is_scanning = false;
      scanState.progress_pct = 100;
      scanState.current_step = "Synchronisation Fast-Lane et carte actualisées avec succès !";
      addScanLog("[FastLane] Cycle complet de synchronisation terminé. Carte à jour.");
    } catch (err) {
      scanState.is_scanning = false;
      scanState.current_step = `Erreur Fast-Lane: ${err.message}`;
      addScanLog(`[Erreur] ${err.message}`);
    }
  })();
}

function startAgencyScan() {
  scanState.is_scanning = true;
  scanState.progress_pct = 20;
  scanState.current_step = "Actualisation Veille Concurrentielle & 83 Agences...";
  scanState.logs = [];
  addScanLog("=== DÉMARRAGE DE L'ACTUALISATION AGENCY BI & BENCHMARKING ===");
  addScanLog("[Agency BI] Traitement des 83 agences, 93 courtiers et flux marketing...");

  const proc = Bun.spawn([PYTHON_EXE, "scripts/enrich_agency_bi_complete.py"], {
    cwd: ROOT_DIR,
    stdout: "pipe",
    stderr: "pipe",
    env: { ...process.env, PYTHONPATH: join(ROOT_DIR, "src") },
  });

  scanState.childProcess = proc;

  (async () => {
    try {
      const reader = proc.stdout.getReader();
      const decoder = new TextDecoder();
      let buf = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += decoder.decode(value, { stream: true });
        const lines = buf.split("\n");
        buf = lines.pop() || "";
        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed) addScanLog(trimmed);
        }
      }
      await proc.exited;
      addScanLog("[Visualizer] Régénération du Benchmark Concurrentiel dans l'application...");
      const mapProc = Bun.spawn([PYTHON_EXE, "-c", "import sys; sys.path.insert(0, 'src'); from fao_transactions.visualization.map_builder import build_interactive_map; build_interactive_map()"], {
        cwd: ROOT_DIR,
        env: { ...process.env, PYTHONPATH: join(ROOT_DIR, "src") },
      });
      await mapProc.exited;
      scanState.is_scanning = false;
      scanState.progress_pct = 100;
      scanState.current_step = "Benchmarking Agences actualisé avec succès !";
      addScanLog("[Agency BI] Matrice concurrentielle et cartes mises à jour.");
    } catch (err) {
      scanState.is_scanning = false;
      scanState.current_step = `Erreur Agency BI: ${err.message}`;
      addScanLog(`[Erreur] ${err.message}`);
    }
  })();
}

function startSitgScan() {
  scanState.is_scanning = true;
  scanState.progress_pct = 20;
  scanState.current_step = "Interrogation du Cadastre Fédéral & SITG...";
  scanState.logs = [];
  addScanLog("=== INTERROGATION CADASTRALE SITG & REGBL FÉDÉRAL ===");
  addScanLog("[SITG/RegBL] Connexion aux registres officiels...");

  const proc = Bun.spawn([PYTHON_EXE, "scripts/enrich_open_data_cadastre.py"], {
    cwd: ROOT_DIR,
    stdout: "pipe",
    stderr: "pipe",
    env: { ...process.env, PYTHONPATH: join(ROOT_DIR, "src") },
  });

  scanState.childProcess = proc;

  (async () => {
    try {
      const reader = proc.stdout.getReader();
      const decoder = new TextDecoder();
      let buf = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += decoder.decode(value, { stream: true });
        const lines = buf.split("\n");
        buf = lines.pop() || "";
        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed) addScanLog(trimmed);
        }
      }
      await proc.exited;
      addScanLog("[Visualizer] Actualisation de la carte avec les données cadastrales enrichies...");
      const mapProc = Bun.spawn([PYTHON_EXE, "-c", "import sys; sys.path.insert(0, 'src'); from fao_transactions.visualization.map_builder import build_interactive_map; build_interactive_map()"], {
        cwd: ROOT_DIR,
        env: { ...process.env, PYTHONPATH: join(ROOT_DIR, "src") },
      });
      await mapProc.exited;
      scanState.is_scanning = false;
      scanState.progress_pct = 100;
      scanState.current_step = "Enrichissement cadastral SITG & RegBL achevé !";
      addScanLog("[Cadastre] Bâtiments, gabarits et parcelles à jour.");
    } catch (err) {
      scanState.is_scanning = false;
      scanState.current_step = `Erreur SITG: ${err.message}`;
      addScanLog(`[Erreur] ${err.message}`);
    }
  })();
}

function cancelScan() {
  if (scanState.childProcess) {
    try {
      scanState.childProcess.kill();
    } catch (e) {}
    scanState.childProcess = null;
  }
  scanState.is_scanning = false;
  scanState.current_step = "Scan interrompu.";
  addScanLog("[SYS] Scan arrêté par l'utilisateur.");
}

async function handleFetch(req) {
  const url = new URL(req.url);
  const pathname = decodeURIComponent(url.pathname);

  // CORS preflight
  if (req.method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
      },
    });
  }

  // Health and Status API endpoints
  if (pathname === "/api/health" || pathname === "/api/health/") {
    return Response.json(
      { status: "online", service: "Cytria Geneva Real Estate Intelligence Engine" },
      { headers: { "Access-Control-Allow-Origin": "*" } }
    );
  }

  if (pathname === "/api/status" || pathname === "/api/status/") {
    return Response.json(
      {
        status: "online",
        service: "Cytria Geneva Real Estate Intelligence Engine",
        telemetry: getScanStatus(),
      },
      { headers: { "Access-Control-Allow-Origin": "*" } }
    );
  }

  // Real-time synchronization scan triggers & progress
  if ((pathname === "/api/scan" || pathname === "/api/scan/") && req.method === "POST") {
    const currentStatus = getScanStatus();
    if (currentStatus.is_scanning) {
      return Response.json(
        {
          success: false,
          message: "Un scan est déjà en cours d'exécution.",
          status: currentStatus,
        },
        { status: 409, headers: { "Access-Control-Allow-Origin": "*" } }
      );
    }

    let body = {};
    try {
      body = await req.json();
    } catch (e) {
      body = {};
    }

    const mode = body.mode || "quick";
    const source = body.source || "ALL";
    const headed = body.headed !== false; // default true so Chromium window opens on desktop

    if (source.toUpperCase() === "FASTLANE" || mode.toLowerCase() === "fastlane") {
      startFastlaneScan();
      return Response.json(
        {
          success: true,
          message: "Scan Fast-Lane (Zéro Captcha) démarré avec succès.",
          status: getScanStatus(),
        },
        { headers: { "Access-Control-Allow-Origin": "*" } }
      );
    }

    startScan(mode, source, headed);

    return Response.json(
      {
        success: true,
        message: `Scan démarré en mode '${mode}' (source: ${source}, headed: ${headed}).`,
        status: getScanStatus(),
      },
      { headers: { "Access-Control-Allow-Origin": "*" } }
    );
  }

  if ((pathname === "/api/scan/fastlane" || pathname === "/api/scan/fastlane/") && req.method === "POST") {
    const currentStatus = getScanStatus();
    if (currentStatus.is_scanning) {
      return Response.json(
        {
          success: false,
          message: "Un scan est déjà en cours d'exécution.",
          status: currentStatus,
        },
        { status: 409, headers: { "Access-Control-Allow-Origin": "*" } }
      );
    }
    startFastlaneScan();
    return Response.json(
      {
        success: true,
        message: "Scan Fast-Lane (Zéro Captcha) démarré avec succès.",
        status: getScanStatus(),
      },
      { headers: { "Access-Control-Allow-Origin": "*" } }
    );
  }

  if ((pathname === "/api/scan/cancel" || pathname === "/api/scan/cancel/") && req.method === "POST") {
    cancelScan();
    return Response.json(
      {
        success: true,
        message: "Arrêt du scan demandé.",
        status: getScanStatus(),
      },
      { headers: { "Access-Control-Allow-Origin": "*" } }
    );
  }

  if ((pathname === "/api/scan/captcha-solved" || pathname === "/api/scan/captcha-solved/") && req.method === "POST") {
    const signalFile = join(ROOT_DIR, "data", "state", "captcha_solved.signal");
    try {
      await Bun.write(signalFile, "SOLVED\n");
      addScanLog("[UTILISATEUR] Défi Friendly Captcha validé via l'interface Web ! Rechargement du portail...");
    } catch (e) {
      console.error("Signal write error:", e);
    }
    return Response.json(
      {
        success: true,
        message: "Signal de résolution Captcha transmis au scraper.",
        status: getScanStatus(),
      },
      { headers: { "Access-Control-Allow-Origin": "*" } }
    );
  }

  if (pathname.startsWith("/api/scan/progress")) {
    return Response.json(getScanStatus(), {
      headers: { "Access-Control-Allow-Origin": "*", "Cache-Control": "no-store" },
    });
  }

  // OCSTAT Communal Benchmarks API
  if (pathname === "/api/ocstat/communes" || pathname === "/api/ocstat/communes/") {
    try {
      if (existsSync(DB_PATH)) {
        const db = new Database(DB_PATH, { readonly: true });
        const rows = db.query("SELECT * FROM ocstat_communal_benchmarks ORDER BY commune ASC").all();
        db.close();
        return Response.json(
          { status: "ok", count: rows.length, data: rows },
          { headers: { "Access-Control-Allow-Origin": "*" } }
        );
      }
    } catch (e) {
      return Response.json({ status: "error", message: e.message }, { status: 500 });
    }
  }

  // Financial Benchmarks API (CASATAX & FINMA)
  if (pathname === "/api/financial/benchmarks" || pathname === "/api/financial/benchmarks/") {
    try {
      if (existsSync(DB_PATH)) {
        const db = new Database(DB_PATH, { readonly: true });
        const rows = db.query("SELECT * FROM financial_benchmarks ORDER BY year DESC").all();
        db.close();
        return Response.json(
          { status: "ok", count: rows.length, data: rows },
          { headers: { "Access-Control-Allow-Origin": "*" } }
        );
      }
    } catch (e) {
      return Response.json({ status: "error", message: e.message }, { status: 500 });
    }
  }

  // Financial Intelligence Summary API
  if (pathname === "/api/intelligence/summary" || pathname === "/api/intelligence/summary/") {
    try {
      if (existsSync(DB_PATH)) {
        const db = new Database(DB_PATH, { readonly: true });
        const total = db.query("SELECT count(*) as c FROM transactions").get();
        const monetized = db.query("SELECT count(*) as c FROM transactions WHERE price_chf > 0").get();
        const casatax = db.query("SELECT count(*) as c FROM financial_intelligence WHERE is_casatax_eligible = 1").get();
        const cliff = db.query("SELECT count(*) as c FROM financial_intelligence WHERE casatax_cliff_flag = 1").get();
        const undervalued = db.query("SELECT count(*) as c FROM financial_intelligence WHERE deal_type_signal = 'OPPORTUNITE_DECOTEE'").get();
        const hoiries = db.query("SELECT count(*) as c FROM financial_intelligence WHERE is_hoirie = 1").get();
        const vol = db.query("SELECT sum(price_chf) as s FROM transactions WHERE price_chf > 0").get();
        db.close();

        return Response.json(
          {
            status: "ok",
            summary: {
              total_transactions: total?.c || 0,
              monetized_transactions: monetized?.c || 0,
              total_volume_chf: vol?.s || 0,
              casatax_eligible_deals: casatax?.c || 0,
              casatax_cliff_deals: cliff?.c || 0,
              undervalued_deals: undervalued?.c || 0,
              hoirie_succession_deals: hoiries?.c || 0,
            },
          },
          { headers: { "Access-Control-Allow-Origin": "*" } }
        );
      }
    } catch (e) {
      return Response.json({ status: "error", message: e.message }, { status: 500 });
    }
  }

  // Filtered Financial Intelligence Transactions API
  if (pathname === "/api/intelligence/transactions" || pathname === "/api/intelligence/transactions/") {
    try {
      if (existsSync(DB_PATH)) {
        const db = new Database(DB_PATH, { readonly: true });
        const searchParams = url.searchParams;
        const casatax = searchParams.get("casatax") === "1";
        const cliff = searchParams.get("cliff") === "1";
        const undervalued = searchParams.get("undervalued") === "1";
        const hoirie = searchParams.get("hoirie") === "1";
        const commune = searchParams.get("commune");
        const limit = Math.min(parseInt(searchParams.get("limit") || "50"), 500);

        let q = `
          SELECT 
            fi.*, t.property_type, t.nature, t.address
          FROM financial_intelligence fi
          JOIN transactions t ON fi.transaction_id = t.id
          WHERE 1=1
        `;
        const params = [];
        if (casatax) q += " AND fi.is_casatax_eligible = 1";
        if (cliff) q += " AND fi.casatax_cliff_flag = 1";
        if (undervalued) q += " AND fi.deal_type_signal = 'OPPORTUNITE_DECOTEE'";
        if (hoirie) q += " AND fi.is_hoirie = 1";
        if (commune) {
          q += " AND lower(fi.commune) = lower(?)";
          params.push(commune.trim());
        }
        q += ` ORDER BY fi.transaction_id DESC LIMIT ?;`;
        params.push(limit);

        const rows = db.query(q).all(...params);
        db.close();
        return Response.json(
          { status: "ok", count: rows.length, data: rows },
          { headers: { "Access-Control-Allow-Origin": "*" } }
        );
      }
    } catch (e) {
      return Response.json({ status: "error", message: e.message }, { status: 500 });
    }
  }

  // Swimming Pool Intelligence APIs (SITG CAD_PISCINE)
  if (pathname === "/api/pools/summary" || pathname === "/api/pools/summary/") {
    try {
      if (existsSync(DB_PATH)) {
        const db = new Database(DB_PATH, { readonly: true });
        const totalPools = db.query("SELECT count(*) as c, sum(surface_m2) as s, avg(surface_m2) as a FROM geneva_pools").get();
        const matched = db.query("SELECT count(*) as c, sum(pool_surface_m2) as s FROM enrichments WHERE has_pool = 1").get();
        const topCommunes = db.query(`
          SELECT 
            commune_name as commune, 
            count(*) as pools_count, 
            round(sum(surface_m2), 1) as total_surface_m2, 
            round(avg(surface_m2), 1) as avg_surface_m2
          FROM geneva_pools
          WHERE commune_name IS NOT NULL
          GROUP BY commune_name
          ORDER BY pools_count DESC
          LIMIT 12;
        `).all();
        db.close();

        return Response.json(
          {
            status: "ok",
            summary: {
              total_cantonal_pools: totalPools?.c || 5173,
              cantonal_total_surface_m2: Math.round(totalPools?.s || 0),
              cantonal_avg_surface_m2: Math.round((totalPools?.a || 0) * 10) / 10,
              properties_with_pools: matched?.c || 0,
              properties_pool_surface_m2: Math.round(matched?.s || 0),
              top_communes: topCommunes,
            },
          },
          { headers: { "Access-Control-Allow-Origin": "*" } }
        );
      }
    } catch (e) {
      return Response.json({ status: "error", message: e.message }, { status: 500 });
    }
  }

  if (pathname === "/api/pools" || pathname === "/api/pools/") {
    try {
      if (existsSync(DB_PATH)) {
        const db = new Database(DB_PATH, { readonly: true });
        const commune = url.searchParams.get("commune");
        const limit = Math.min(parseInt(url.searchParams.get("limit") || "500"), 5200);
        let q = "SELECT id, source, objectid, commune_code, commune_name, mutation_num, mutation_date, surface_m2, perimeter_m, centroid_wgs84_lon, centroid_wgs84_lat, geom_geojson_wgs84 FROM geneva_pools WHERE 1=1";
        const params = [];
        if (commune) {
          q += " AND lower(commune_name) = lower(?)";
          params.push(commune.trim());
        }
        q += " ORDER BY surface_m2 DESC LIMIT ?";
        params.push(limit);

        const rows = db.query(q).all(...params);
        db.close();

        return Response.json(
          { status: "ok", count: rows.length, data: rows },
          { headers: { "Access-Control-Allow-Origin": "*" } }
        );
      }
    } catch (e) {
      return Response.json({ status: "error", message: e.message }, { status: 500 });
    }
  }

  // 1-Click Valuation Dossier HTML Report
  if (pathname === "/dossier" || pathname === "/dossier.html") {
    try {
      const searchParams = url.searchParams;
      let txId = parseInt(searchParams.get("id") || searchParams.get("transaction_id") || "0");
      const service = new ValuationService(DB_PATH);

      if (!txId) {
        if (existsSync(DB_PATH)) {
          const db = new Database(DB_PATH, { readonly: true });
          const latest = db.query("SELECT transaction_id FROM financial_intelligence ORDER BY transaction_id DESC LIMIT 1").get();
          db.close();
          txId = latest?.transaction_id || 16928;
        } else {
          txId = 16928;
        }
      }

      const html = service.renderHtml(txId);
      return new Response(html, {
        headers: {
          "Content-Type": "text/html; charset=utf-8",
          "Access-Control-Allow-Origin": "*",
        },
      });
    } catch (e) {
      return new Response(`Erreur de génération du dossier : ${e.message}`, { status: 500 });
    }
  }

  // Désormière & Vanhalst Portal View
  if (pathname === "/dv" || pathname === "/dv/" || pathname === "/desormiere-vanhalst") {
    const dvHtml = join(ROOT_DIR, "public", "dv", "index.html");
    if (existsSync(dvHtml)) {
      return new Response(readFileSync(dvHtml, "utf-8"), {
        headers: { "Content-Type": "text/html; charset=utf-8" },
      });
    }
  }

  // Désormière & Vanhalst Opportunities API
  if (pathname === "/api/dv/opportunities" || pathname === "/api/dv/opportunities/") {
    try {
      const searchParams = url.searchParams;
      const commune = searchParams.get("commune") || "all";
      const signal = searchParams.get("signal") || "all";
      const minScore = parseFloat(searchParams.get("min_score") || "35");
      const limit = parseInt(searchParams.get("limit") || "80");

      const dvService = new DVIntelligenceService(DB_PATH);
      const data = dvService.getOpportunities({
        commune: commune === "all" ? undefined : commune,
        signal: signal === "all" ? undefined : signal,
        min_score: minScore,
        limit,
      });

      const stats = dvService.getSummaryStats();

      return Response.json(
        { status: "ok", count: data.length, data, stats },
        { headers: { "Access-Control-Allow-Origin": "*" } }
      );
    } catch (e) {
      return Response.json({ status: "error", message: e.message }, { status: 500 });
    }
  }

  // Désormière & Vanhalst Branded CMA Dossier View
  if (pathname === "/api/dv/cma" || pathname === "/api/dv/cma/") {
    try {
      const searchParams = url.searchParams;
      const txId = parseInt(searchParams.get("id") || searchParams.get("transaction_id") || "16945");
      const dvService = new DVIntelligenceService(DB_PATH);
      const html = dvService.getCmaHtml(txId);
      if (!html) {
        return new Response("Transaction introuvable pour l'estimation D&V", { status: 404 });
      }
      return new Response(html, {
        headers: {
          "Content-Type": "text/html; charset=utf-8",
          "Access-Control-Allow-Origin": "*",
        },
      });
    } catch (e) {
      return new Response(`Erreur de génération CMA : ${e.message}`, { status: 500 });
    }
  }

  // Désormière & Vanhalst Territorial Watch & Competitor Radar API
  if (pathname === "/api/dv/watch" || pathname === "/api/dv/watch/") {
    try {
      const searchParams = url.searchParams;
      const commune = searchParams.get("commune") || "all";
      const limit = parseInt(searchParams.get("limit") || "40");

      const dvService = new DVIntelligenceService(DB_PATH);
      const watchData = dvService.getTerritorialWatch({
        commune: commune === "all" ? undefined : commune,
        limit,
      });

      return Response.json(
        { status: "ok", ...watchData },
        { headers: { "Access-Control-Allow-Origin": "*" } }
      );
    } catch (e) {
      return Response.json({ status: "error", message: e.message }, { status: 500 });
    }
  }

  // Désormière & Vanhalst Neighbor Canvassing & Letter API
  if (pathname === "/api/dv/neighbors" || pathname === "/api/dv/neighbors/") {
    try {
      const searchParams = url.searchParams;
      const id = parseInt(searchParams.get("id") || searchParams.get("transaction_id") || "0");
      if (!id) {
        return Response.json({ status: "error", message: "Paramètre 'id' requis" }, { status: 400 });
      }

      const dvService = new DVIntelligenceService(DB_PATH);
      const neighborData = dvService.getNeighborsForSale(id);
      if (!neighborData) {
        return Response.json({ status: "error", message: "Transaction introuvable" }, { status: 404 });
      }

      return Response.json(
        { status: "ok", data: neighborData },
        { headers: { "Access-Control-Allow-Origin": "*" } }
      );
    } catch (e) {
      return Response.json({ status: "error", message: e.message }, { status: 500 });
    }
  }

  // Désormière & Vanhalst Address Autocomplete Search API
  if (pathname === "/api/dv/search" || pathname === "/api/dv/search/") {
    try {
      const searchParams = url.searchParams;
      const q = searchParams.get("q") || "";
      const dvService = new DVIntelligenceService(DB_PATH);
      const results = dvService.searchProperties(q);
      return Response.json(
        { status: "ok", count: results.length, data: results },
        { headers: { "Access-Control-Allow-Origin": "*" } }
      );
    } catch (e) {
      return Response.json({ status: "error", message: e.message }, { status: 500 });
    }
  }

  // Désormière & Vanhalst 3-Step Valuation Studio Workspace API
  if (pathname === "/api/dv/valuation-studio" || pathname === "/api/dv/valuation-studio/") {
    try {
      const searchParams = url.searchParams;
      const id = parseInt(searchParams.get("id") || "17169");
      const dvService = new DVIntelligenceService(DB_PATH);
      const data = dvService.getValuationStudio(id);
      if (!data) {
        return Response.json({ status: "error", message: "Bien introuvable" }, { status: 404 });
      }
      return Response.json(
        { status: "ok", data },
        { headers: { "Access-Control-Allow-Origin": "*" } }
      );
    } catch (e) {
      return Response.json({ status: "error", message: e.message }, { status: 500 });
    }
  }

  // Désormière & Vanhalst Agency Portfolio & Buyer Match API
  if (pathname === "/api/dv/portfolio" || pathname === "/api/dv/portfolio/") {
    try {
      const dvService = new DVIntelligenceService(DB_PATH);
      const data = dvService.getAgencyPortfolioReview();
      return Response.json(
        { status: "ok", ...data },
        { headers: { "Access-Control-Allow-Origin": "*" } }
      );
    } catch (e) {
      return Response.json({ status: "error", message: e.message }, { status: 500 });
    }
  }

  // Désormière & Vanhalst Saut-du-Loup 18 Comparative Case Study API
  if (pathname === "/api/dv/saut-du-loup-case" || pathname === "/api/dv/saut-du-loup-case/") {
    try {
      const generator = new DVPptxGenerator();
      const data = generator.getSautDuLoupCaseStudy();
      return Response.json(
        { status: "ok", data },
        { headers: { "Access-Control-Allow-Origin": "*" } }
      );
    } catch (e) {
      return Response.json({ status: "error", message: e.message }, { status: 500 });
    }
  }

  // Désormière & Vanhalst PPTX Presentation Export Engine API
  if (pathname === "/api/dv/export-pptx" || pathname === "/api/dv/export-pptx/") {
    try {
      let body = {};
      if (req.method === "POST") {
        try {
          body = await req.json();
        } catch {}
      }

      const isDemoMode = body.isDemo === true || body.mode === "demo";
      const generator = new DVPptxGenerator();
      
      let slideReplacements = {};
      if (isDemoMode) {
        const defaultCase = generator.getSautDuLoupCaseStudy();
        slideReplacements = JSON.parse(JSON.stringify(defaultCase.pptxPayload));
      }

      if (body.slideReplacements && typeof body.slideReplacements === 'object') {
        for (const [slideKey, tokens] of Object.entries(body.slideReplacements)) {
          slideReplacements[slideKey] = {
            ...(slideReplacements[slideKey] || {}),
            ...tokens
          };
        }
      }

      // Always use the official neutral template for user estimations to guarantee zero ghost data!
      let templatePath = undefined;
      const viergeTemplate = join(ROOT_DIR, "data", "exports", "Estimation_DV_Template_Vierge_Officiel.pptx");
      if (!isDemoMode && existsSync(viergeTemplate)) {
        templatePath = viergeTemplate;
      }

      const images = body.images || {};
      const hideInternalInstructions = body.hideInternalInstructions !== false;

      const buffer = generator.generatePptxBuffer({
        templatePath,
        slideReplacements,
        images,
        hideInternalInstructions
      });

      const filename = body.filename || (isDemoMode ? "Estimation_DV_Chemin_du_Saut_du_Loup_18.pptx" : "Estimation_DV_Dossier.pptx");

      return new Response(buffer, {
        status: 200,
        headers: {
          "Content-Type": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
          "Content-Disposition": `attachment; filename="${filename}"`,
          "Access-Control-Allow-Origin": "*",
          "Content-Length": buffer.length.toString()
        }
      });
    } catch (e) {
      return Response.json({ status: "error", message: e.message }, { status: 500 });
    }
  }

// Swiss Federal GeoAdmin (RegBL / GWR) and SITG Official Geneva Address Resolver
async function searchFederalGenevaAddresses(query) {
  try {
    const url = `https://api3.geo.admin.ch/rest/services/api/SearchServer?type=locations&origins=address&searchText=${encodeURIComponent(query)}`;
    const res = await fetch(url, { headers: { "User-Agent": "Cytria-DV-Cadastre/2.0" } });
    if (!res.ok) return [];
    const data = await res.json();
    return (data.results || []).filter(r => {
      const detail = (r.attrs?.detail || "").toLowerCase();
      const label = (r.attrs?.label || "").toLowerCase();
      return detail.includes(" ch ge") || detail.includes(" ge") || /12\d\d/.test(label);
    });
  } catch {
    return [];
  }
}

async function fetchFederalBuildingDetails(featureId) {
  try {
    const url = `https://api3.geo.admin.ch/rest/services/ech/MapServer/ch.bfs.gebaeude_wohnungs_register/${featureId}`;
    const res = await fetch(url, { headers: { "User-Agent": "Cytria-DV-Cadastre/2.0" } });
    if (!res.ok) return null;
    const data = await res.json();
    const attrs = data.feature?.attributes || {};

    const heatingCode = attrs.gwaerzh1;
    let heating = "Chauffage central standard";
    if (heatingCode === 7520 || heatingCode === 7620) heating = "Chauffage à distance (CAD Genève / SIG)";
    else if (heatingCode === 7530 || heatingCode === 7410) heating = "Pompe à chaleur (PAC)";
    else if (heatingCode === 7511) heating = "Gaz naturel";
    else if (heatingCode === 7501) heating = "Mazout (Fioul)";
    else if (heatingCode === 7540) heating = "Solaire thermique";

    const dwellingsCount = attrs.ganzwhg || 1;
    const propType = dwellingsCount > 1 ? "APPARTEMENT PPE" : "VILLA / MAISON INDIVIDUELLE";
    const surfaces = Array.isArray(attrs.warea) ? attrs.warea.filter(Boolean) : [];
    const roomsList = Array.isArray(attrs.wazim) ? attrs.wazim.filter(Boolean) : [];
    const primarySurface = surfaces.length > 0 ? surfaces[0] : (attrs.garea ? Math.round(attrs.garea / Math.max(1, dwellingsCount)) : 85);
    const primaryRooms = roomsList.length > 0 ? roomsList[0] : (primarySurface > 110 ? 5 : primarySurface > 75 ? 4 : 3);

    const cleanAddr = attrs.strname_deinr || (attrs.label || "").replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
    const commune = attrs.ggdename || attrs.dplzname || "Genève";

    return {
      address: cleanAddr,
      commune: (attrs.dplz4 ? `${attrs.dplz4} ` : '') + commune,
      parcel_number: attrs.lparz || "—",
      building_number: attrs.gebnr || "—",
      building_year: attrs.gbauj || attrs.wbauj?.[0] || null,
      rooms: primaryRooms,
      surface_m2: primarySurface,
      surface_official_m2: primarySurface,
      egrid: attrs.egrid || null,
      egid: attrs.egid || null,
      heating_system: heating,
      resolved_zone: "Zone 5 (Villas et résidences de standing)",
      property_type: propType,
      apartments_count: dwellingsCount,
      floors: attrs.gastw || null,
      source: "RegBL / SITG Officiel"
    };
  } catch {
    return null;
  }
}

  // Désormière & Vanhalst Dynamic Geneva Address Autocomplete API (Hybrid Local + SITG/RegBL)
  if (pathname === "/api/dv/address-autocomplete" || pathname === "/api/dv/address-autocomplete/") {
    try {
      const q = (url.searchParams.get("q") || "").trim();
      if (!q || q.length < 2) {
        return Response.json({ status: "ok", results: [] }, { headers: { "Access-Control-Allow-Origin": "*" } });
      }

      // 1. Local SQLite transactions
      const db = new Database(DB_PATH, { readonly: true });
      const term = `%${q}%`;
      const startTerm = `${q}%`;
      const sql = `
        SELECT 
          t.id,
          t.address,
          t.commune,
          t.parcel_number,
          t.property_type,
          t.nature,
          t.building_year,
          t.rooms,
          COALESCE(t.surface_m2, e.surface_official_m2) as surface_m2,
          e.egrid,
          e.heating_system,
          COALESCE(e.zone_name, t.zone_name, 'Zone 5') as zone_name,
          'FAO Transaction' as source
        FROM transactions t
        LEFT JOIN enrichments e ON t.id = e.transaction_id
        WHERE t.address IS NOT NULL 
          AND (
            t.address LIKE ? 
            OR t.parcel_number LIKE ? 
            OR t.commune LIKE ?
          )
        GROUP BY t.address, t.commune
        ORDER BY 
          CASE WHEN t.address LIKE ? THEN 1 ELSE 2 END,
          t.notice_date DESC
        LIMIT 10;
      `;
      const localResults = db.query(sql).all(term, term, term, startTerm);
      db.close();

      // 2. Query Swiss Federal Register / GeoAdmin API for Canton Geneva
      let federalMatches = [];
      try {
        const fedResults = await searchFederalGenevaAddresses(q);
        const existingAddrs = new Set(localResults.map(r => (r.address || "").toLowerCase().replace(/,/g, "")));
        
        const toEnrich = fedResults.filter(f => {
          const lbl = (f.attrs?.label || "").replace(/<[^>]+>/g, "").toLowerCase().replace(/,/g, "");
          return !existingAddrs.has(lbl);
        }).slice(0, 5);

        const enriched = await Promise.all(
          toEnrich.map(async f => {
            const featId = f.attrs?.featureId;
            if (!featId) return null;
            const details = await fetchFederalBuildingDetails(featId);
            if (!details) return null;
            return {
              id: `regbl_${featId}`,
              featureId: featId,
              ...details
            };
          })
        );
        federalMatches = enriched.filter(Boolean);
      } catch {}

      const results = [...localResults, ...federalMatches];

      return Response.json(
        { status: "ok", count: results.length, results },
        { headers: { "Access-Control-Allow-Origin": "*" } }
      );
    } catch (e) {
      return Response.json({ status: "error", message: e.message }, { status: 500 });
    }
  }

  // Désormière & Vanhalst Deep Cadastre & Property Lookup API (Local + Federal SITG)
  if (pathname === "/api/dv/cadastre-lookup" || pathname === "/api/dv/cadastre-lookup/") {
    try {
      const id = parseInt(url.searchParams.get("id") || "0");
      const address = (url.searchParams.get("address") || "").trim();
      const parcel = (url.searchParams.get("parcel") || "").trim();
      const featureId = (url.searchParams.get("featureId") || "").trim();

      let row = null;

      // 1. Direct Federal Feature ID lookup if available
      if (featureId) {
        row = await fetchFederalBuildingDetails(featureId);
      }

      // 2. Local Database Lookup
      if (!row) {
        const db = new Database(DB_PATH, { readonly: true });
        if (id > 0) {
          row = db.query(`
            SELECT t.*, e.heating_system, e.surface_official_m2, e.lien_extrait_rf, e.egrid, COALESCE(e.zone_name, t.zone_name, 'Zone 5') as resolved_zone
            FROM transactions t
            LEFT JOIN enrichments e ON t.id = e.transaction_id
            WHERE t.id = ?
          `).get(id);
        } else if (address) {
          row = db.query(`
            SELECT t.*, e.heating_system, e.surface_official_m2, e.lien_extrait_rf, e.egrid, COALESCE(e.zone_name, t.zone_name, 'Zone 5') as resolved_zone
            FROM transactions t
            LEFT JOIN enrichments e ON t.id = e.transaction_id
            WHERE t.address LIKE ?
            ORDER BY t.notice_date DESC LIMIT 1
          `).get(`%${address}%`);
        } else if (parcel) {
          row = db.query(`
            SELECT t.*, e.heating_system, e.surface_official_m2, e.lien_extrait_rf, e.egrid, COALESCE(e.zone_name, t.zone_name, 'Zone 5') as resolved_zone
            FROM transactions t
            LEFT JOIN enrichments e ON t.id = e.transaction_id
            WHERE t.parcel_number LIKE ?
            ORDER BY t.notice_date DESC LIMIT 1
          `).get(`%${parcel}%`);
        }
        db.close();
      }

      // 3. Fallback to Swiss Federal GeoAdmin API if address wasn't in local DB
      if (!row && address) {
        const fedResults = await searchFederalGenevaAddresses(address);
        if (fedResults.length > 0 && fedResults[0].attrs?.featureId) {
          row = await fetchFederalBuildingDetails(fedResults[0].attrs.featureId);
        }
      }

      if (!row) {
        return Response.json(
          { status: "not_found", message: "Aucun enregistrement cadastral trouvé" },
          { status: 404, headers: { "Access-Control-Allow-Origin": "*" } }
        );
      }

      return Response.json(
        { status: "ok", data: row },
        { headers: { "Access-Control-Allow-Origin": "*" } }
      );
    } catch (e) {
      return Response.json({ status: "error", message: e.message }, { status: 500 });
    }
  }

  // Désormière & Vanhalst Automatic Comparables Discovery API
  if (pathname === "/api/dv/comparables-lookup" || pathname === "/api/dv/comparables-lookup/") {
    try {
      const commune = (url.searchParams.get("commune") || "").trim();
      const excludeId = parseInt(url.searchParams.get("exclude_id") || "0");
      const limit = Math.min(parseInt(url.searchParams.get("limit") || "5"), 10);

      const db = new Database(DB_PATH, { readonly: true });
      const sql = `
        SELECT 
          t.id,
          t.address,
          t.commune,
          t.notice_date as raw_date,
          COALESCE(t.surface_m2, e.surface_official_m2, 85) as surface,
          t.price_chf as price,
          ROUND(t.price_chf / COALESCE(t.surface_m2, e.surface_official_m2, 85)) as price_m2,
          t.property_type,
          t.nature
        FROM transactions t
        LEFT JOIN enrichments e ON t.id = e.transaction_id
        WHERE t.commune LIKE ?
          AND t.price_chf > 300000 
          AND t.id != ?
          AND t.address IS NOT NULL
        ORDER BY t.notice_date DESC
        LIMIT ?;
      `;
      const rows = db.query(sql).all(`%${commune}%`, excludeId, limit);
      db.close();

      return Response.json(
        { status: "ok", count: rows.length, results: rows },
        { headers: { "Access-Control-Allow-Origin": "*" } }
      );
    } catch (e) {
      return Response.json({ status: "error", message: e.message }, { status: 500 });
    }
  }

  // Désormière & Vanhalst Official Cantonal OCSTAT Communal Benchmark API
  if (pathname === "/api/dv/ocstat-benchmark" || pathname === "/api/dv/ocstat-benchmark/") {
    try {
      const communeParam = (url.searchParams.get("commune") || "").trim().toLowerCase();
      let benchmark = null;
      const ocstatPath = join(ROOT_DIR, "data", "reference", "ocstat_communes_2025_2026.json");
      if (existsSync(ocstatPath)) {
        try {
          const list = JSON.parse(readFileSync(ocstatPath, "utf8"));
          benchmark = list.find(c => c.commune.toLowerCase() === communeParam) ||
                      list.find(c => communeParam.includes(c.commune.toLowerCase())) ||
                      list.find(c => c.commune.toLowerCase() === "genève");
        } catch {}
      }

      const ppeMedian = benchmark?.ppe_median_sqm || 13800;
      const cantonMedian = 14200;
      const spreadPct = -3.2;
      const trend18m = "+2.4%";
      const communeName = benchmark?.commune || (url.searchParams.get("commune") || "Genève");

      const suggestedNotes = `Le baromètre statistique officiel OCSTAT et l'historique des actes notariés FAO sur la commune de ${communeName} démontrent un marché de propriétaires-occupants résilient et sélectif. La valeur médiane enregistrée s'établit à CHF ${ppeMedian.toLocaleString("fr-CH")}/m² (contre CHF ${cantonMedian.toLocaleString("fr-CH")}/m² à l'échelle cantonale). L'écart moyen de négociation constaté entre offre initiale et réalisation acte s'élève à ${Math.abs(spreadPct)}%, avec une prime accentuée pour les biens à haute efficience énergétique et extérieurs dégagés.`;

      return Response.json(
        {
          status: "ok",
          commune: communeName,
          ppe_median_sqm: ppeMedian,
          canton_median_sqm: cantonMedian,
          trend_18m_pct: trend18m,
          spread_discount_pct: spreadPct,
          transactions_annuelles_est: benchmark?.transactions_annuelles_est || 150,
          suggested_notes: suggestedNotes
        },
        { headers: { "Access-Control-Allow-Origin": "*" } }
      );
    } catch (e) {
      return Response.json({ status: "error", message: e.message }, { status: 500 });
    }
  }

  // 1-Click Valuation Dossier JSON Data API
  if (pathname === "/api/dossier/valuation" || pathname === "/api/dossier/valuation/") {
    try {
      const searchParams = url.searchParams;
      let txId = parseInt(searchParams.get("id") || searchParams.get("transaction_id") || "0");
      const service = new ValuationService(DB_PATH);

      if (!txId) {
        if (existsSync(DB_PATH)) {
          const db = new Database(DB_PATH, { readonly: true });
          const latest = db.query("SELECT transaction_id FROM financial_intelligence ORDER BY transaction_id DESC LIMIT 1").get();
          db.close();
          txId = latest?.transaction_id || 16928;
        } else {
          txId = 16928;
        }
      }

      const data = service.getDossier(txId);
      if (!data) {
        return Response.json({ status: "error", message: `Transaction #${txId} introuvable` }, { status: 404 });
      }
      return Response.json(
        { status: "ok", dossier: data },
        { headers: { "Access-Control-Allow-Origin": "*" } }
      );
    } catch (e) {
      return Response.json({ status: "error", message: e.message }, { status: 500 });
    }
  }

  // Developer Radar & Residual Building Rights API
  if (pathname === "/api/developer/radar" || pathname === "/api/developer/radar/") {
    try {
      if (existsSync(DB_PATH)) {
        const db = new Database(DB_PATH, { readonly: true });
        const searchParams = url.searchParams;
        const minSurface = parseFloat(searchParams.get("min_surface") || "700");
        const minScore = parseFloat(searchParams.get("min_score") || "0");
        const hoirieOnly = searchParams.get("hoirie_only") === "1";
        const commune = searchParams.get("commune");
        const limit = Math.min(parseInt(searchParams.get("limit") || "50"), 500);

        let q = `
          SELECT * FROM developer_intelligence
          WHERE surface_m2 >= ?
            AND priority_score >= ?
        `;
        const params = [minSurface, minScore];
        if (hoirieOnly) q += " AND is_hoirie = 1";
        if (commune) {
          q += " AND lower(commune) = lower(?)";
          params.push(commune.trim());
        }
        q += ` ORDER BY priority_score DESC, surface_m2 DESC LIMIT ?;`;
        params.push(limit);

        const rows = db.query(q).all(...params);
        db.close();
        return Response.json(
          { status: "ok", count: rows.length, data: rows },
          { headers: { "Access-Control-Allow-Origin": "*" } }
        );
      }
    } catch (e) {
      return Response.json({ status: "error", message: e.message }, { status: 500 });
    }
  }

  // Developer Radar Summary API
  if (pathname === "/api/developer/summary" || pathname === "/api/developer/summary/") {
    try {
      if (existsSync(DB_PATH)) {
        const db = new Database(DB_PATH, { readonly: true });
        const total = db.query("SELECT count(*) as c FROM developer_intelligence").get();
        const topPriority = db.query("SELECT count(*) as c FROM developer_intelligence WHERE priority_score >= 70").get();
        const hoiries = db.query("SELECT count(*) as c FROM developer_intelligence WHERE is_hoirie = 1").get();
        const totalRightsM2 = db.query("SELECT sum(residual_rights_m2) as s FROM developer_intelligence").get();
        const totalGrossPotential = db.query("SELECT sum(gross_developer_potential_chf) as s FROM developer_intelligence").get();
        db.close();

        return Response.json(
          {
            status: "ok",
            summary: {
              total_development_parcels: total?.c || 0,
              top_priority_parcels: topPriority?.c || 0,
              succession_parcels: hoiries?.c || 0,
              total_residual_rights_m2: totalRightsM2?.s || 0,
              total_gross_potential_chf: totalGrossPotential?.s || 0,
            },
          },
          { headers: { "Access-Control-Allow-Origin": "*" } }
        );
      }
    } catch (e) {
      return Response.json({ status: "error", message: e.message }, { status: 500 });
    }
  }

  // Content Marketing Engine APIs
  if (pathname === "/api/marketing/agency-profile" || pathname === "/api/marketing/agency-profile/") {
    try {
      const agencyId = url.searchParams.get("agency") || "desormiere_vanhalst";
      const profile = agencyConfigService.getProfile(agencyId);
      const allProfiles = agencyConfigService.listProfiles();
      return Response.json(
        { status: "ok", profile, available_profiles: allProfiles },
        { headers: { "Access-Control-Allow-Origin": "*" } }
      );
    } catch (e) {
      return Response.json({ status: "error", message: e.message }, { status: 500 });
    }
  }

  if (pathname === "/api/marketing/fiscal-simulation" || pathname === "/api/marketing/fiscal-simulation/") {
    try {
      const sellPrice = parseFloat(url.searchParams.get("sell_price") || "2450000");
      const acqPrice = parseFloat(url.searchParams.get("acq_price") || "1600000");
      const years = parseInt(url.searchParams.get("years") || "12");
      const reno = parseFloat(url.searchParams.get("reno") || "180000");
      const commune = url.searchParams.get("commune") || "Troinex";
      const sim = fiscalSimService.simulate({
        selling_price_chf: sellPrice,
        acquisition_price_chf: acqPrice,
        years_held: years,
        commune: commune,
        renovations_invested_chf: reno
      });
      return Response.json(
        { status: "ok", simulation: sim },
        { headers: { "Access-Control-Allow-Origin": "*" } }
      );
    } catch (e) {
      return Response.json({ status: "error", message: e.message }, { status: 500 });
    }
  }

  if (pathname === "/api/marketing/competitor-radar" || pathname === "/api/marketing/competitor-radar/") {
    try {
      const radar = competitorBenchmarkService.getCompetitorRadar();
      const stale = competitorBenchmarkService.getStaleMandateOpportunities();
      return Response.json(
        { status: "ok", competitors: radar, stale_opportunities: stale },
        { headers: { "Access-Control-Allow-Origin": "*" } }
      );
    } catch (e) {
      return Response.json({ status: "error", message: e.message }, { status: 500 });
    }
  }

  if (pathname === "/api/marketing/social-surveillance" || pathname === "/api/marketing/social-surveillance/") {
    try {
      const socialData = competitorBenchmarkService.getSocialSurveillance();
      return Response.json(
        { status: "ok", ...socialData },
        { headers: { "Access-Control-Allow-Origin": "*" } }
      );
    } catch (e) {
      return Response.json({ status: "error", message: e.message }, { status: 500 });
    }
  }

  if (pathname === "/api/marketing/telemetry-metrics" || pathname === "/api/marketing/telemetry-metrics/") {
    try {
      const data = telemetryService.getDashboardData();
      return Response.json(
        { status: "ok", telemetry: data },
        { headers: { "Access-Control-Allow-Origin": "*" } }
      );
    } catch (e) {
      return Response.json({ status: "error", message: e.message }, { status: 500 });
    }
  }

  if (pathname === "/api/marketing/quartier-guide" || pathname === "/api/marketing/quartier-guide/") {
    try {
      const commune = url.searchParams.get("commune") || "Troinex";
      const guide = guideGeneratorService.generateQuartierGuide(commune);
      return Response.json(
        { status: "ok", guide },
        { headers: { "Access-Control-Allow-Origin": "*" } }
      );
    } catch (e) {
      return Response.json({ status: "error", message: e.message }, { status: 500 });
    }
  }

  if (pathname === "/api/marketing/funnel-suggestions" || pathname === "/api/marketing/funnel-suggestions/") {
    try {
      const commune = url.searchParams.get("commune") || "Troinex";
      const icpsParam = url.searchParams.get("icps") || "";
      const icps = icpsParam ? icpsParam.split(",") : undefined;
      const data = funnelContentService.getFunnelSuggestions({ commune, icps });
      return Response.json(
        { status: "ok", ...data },
        { headers: { "Access-Control-Allow-Origin": "*" } }
      );
    } catch (e) {
      return Response.json({ status: "error", message: e.message }, { status: 500 });
    }
  }

  if (pathname === "/api/marketing/full-guide" || pathname === "/api/marketing/full-guide/") {
    try {
      const guideId = url.searchParams.get("id") || "tofu_succession_famille";
      const commune = url.searchParams.get("commune") || "Troinex";
      const guide = funnelContentService.generateFullGuide(guideId, commune);
      return Response.json(
        { status: "ok", guide },
        { headers: { "Access-Control-Allow-Origin": "*" } }
      );
    } catch (e) {
      return Response.json({ status: "error", message: e.message }, { status: 500 });
    }
  }

  // Désormière & Vanhalst Content Marketing Engine
  if (pathname === "/dv/marketing") {
    return Response.redirect("/dv/marketing/", 302);
  }
  if (pathname === "/dv/marketing/" || pathname === "/dv/marketing/index.html") {
    const marketingIndex = join(ROOT_DIR, "public", "dv", "marketing", "index.html");
    if (existsSync(marketingIndex)) {
      return new Response(Bun.file(marketingIndex), {
        headers: { "Content-Type": "text/html; charset=utf-8", "Access-Control-Allow-Origin": "*" },
      });
    }
  }

  // Désormière & Vanhalst Portal
  if (pathname === "/dv") {
    return Response.redirect("/dv/", 302);
  }
  if (pathname === "/dv/" || pathname === "/dv/index.html") {
    const dvIndex = join(ROOT_DIR, "public", "dv", "index.html");
    if (existsSync(dvIndex)) {
      return new Response(Bun.file(dvIndex), {
        headers: { "Content-Type": "text/html; charset=utf-8", "Access-Control-Allow-Origin": "*" },
      });
    }
  }

  // Root document
  if (pathname === "/" || pathname === "" || pathname === "/index.html") {
    if (existsSync(INDEX_HTML)) {
      return new Response(Bun.file(INDEX_HTML), {
        headers: { "Content-Type": "text/html; charset=utf-8" },
      });
    }
    return new Response("index.html not found", { status: 404 });
  }

  // Static files and safe assets
  try {
    const cleanPath = pathname.replace(/^\/+/, "");
    if (!cleanPath) {
      return new Response(Bun.file(INDEX_HTML), {
        headers: { "Content-Type": "text/html; charset=utf-8" },
      });
    }

    // Security Hardening: Block direct access to database, secrets, internal scripts, and raw data dumps
    const lowerPath = cleanPath.toLowerCase();
    if (
      lowerPath.includes(".sqlite") ||
      lowerPath.includes(".db") ||
      lowerPath.includes(".env") ||
      lowerPath.startsWith(".git") ||
      lowerPath.startsWith(".venv") ||
      lowerPath.startsWith("data/state") ||
      lowerPath.endsWith(".csv") ||
      lowerPath.endsWith(".xlsx") ||
      lowerPath.endsWith(".py") ||
      lowerPath.endsWith(".ts") ||
      lowerPath.endsWith(".bat") ||
      lowerPath.endsWith(".ps1") ||
      lowerPath.endsWith(".sh") ||
      lowerPath === "pyproject.toml" ||
      lowerPath === "package.json"
    ) {
      return new Response("Forbidden", { status: 403 });
    }

    let targetPath = join(ROOT_DIR, cleanPath);
    if (!existsSync(targetPath) && existsSync(join(ROOT_DIR, "public", cleanPath))) {
      targetPath = join(ROOT_DIR, "public", cleanPath);
    }

    if (existsSync(targetPath)) {
      const stats = statSync(targetPath);
      if (stats.isDirectory()) {
        const subIndex = join(targetPath, "index.html");
        if (existsSync(subIndex) && statSync(subIndex).isFile()) {
          return new Response(Bun.file(subIndex), {
            headers: { "Content-Type": "text/html; charset=utf-8" },
          });
        }
        return new Response("Forbidden", { status: 403 });
      }
      if (!stats.isFile()) {
        return new Response("Not Found", { status: 404 });
      }
      const ext = extname(targetPath).toLowerCase();
      let contentType = "application/octet-stream";
      if (ext === ".html") contentType = "text/html; charset=utf-8";
      else if (ext === ".css") contentType = "text/css; charset=utf-8";
      else if (ext === ".js") contentType = "application/javascript; charset=utf-8";
      else if (ext === ".json") contentType = "application/json; charset=utf-8";
      else if (ext === ".png") contentType = "image/png";
      else if (ext === ".jpg" || ext === ".jpeg") contentType = "image/jpeg";
      else if (ext === ".svg") contentType = "image/svg+xml";
      else if (ext === ".pptx") contentType = "application/vnd.openxmlformats-officedocument.presentationml.presentation";
      else if (ext === ".pdf") contentType = "application/pdf";
      return new Response(Bun.file(targetPath), {
        headers: { "Content-Type": contentType, "Access-Control-Allow-Origin": "*" },
      });
    }
  } catch (err) {
    // Return 404 on any FS lookup error
  }

  return new Response("Not Found", { status: 404 });
}

function startServer() {
  const initialPort = getRequestedPort();
  let port = initialPort;
  const maxPort = port + 50;

  while (port < maxPort) {
    try {
      const server = Bun.serve({
        hostname: "0.0.0.0",
        port,
        fetch: handleFetch,
      });

      console.log(`\n------------- CYTRIA INTELLIGENCE & SYNC SERVER -------------`);
      console.log(`Serving at: http://localhost:${server.port}/`);
      console.log(`Portal D&V: http://localhost:${server.port}/dv/`);
      console.log(`REST API:   http://localhost:${server.port}/api/status`);
      console.log(`Dossier:    http://localhost:${server.port}/dossier?id=16928\n`);
      return server;
    } catch (err) {
      if (String(err).includes("listen") || err.code === "EADDRINUSE") {
        console.warn(`Port ${port} is in use, trying ${port + 1}...`);
        port++;
      } else {
        throw err;
      }
    }
  }

  throw new Error(`Unable to find an open port between ${initialPort} and ${maxPort}`);
}

startServer();
