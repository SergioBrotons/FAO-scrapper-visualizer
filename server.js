// Local development server for Cytria Geneva Real Estate Visualizer
import { join } from "path";
import { existsSync, statSync, readFileSync } from "fs";
import { Database } from "bun:sqlite";
import { ValuationService } from "./src/fao_transactions/dossier/valuation_service.ts";

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
  return 8085;
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

    const targetPath = join(ROOT_DIR, cleanPath);

    if (existsSync(targetPath)) {
      const stats = statSync(targetPath);
      if (stats.isDirectory()) {
        const subIndex = join(targetPath, "index.html");
        if (existsSync(subIndex)) {
          return new Response(Bun.file(subIndex), {
            headers: { "Content-Type": "text/html; charset=utf-8" },
          });
        }
        return new Response("Forbidden", { status: 403 });
      }
      return new Response(Bun.file(targetPath));
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
        port,
        fetch: handleFetch,
      });

      console.log(`\n------------- CYTRIA INTELLIGENCE & SYNC SERVER -------------`);
      console.log(`Serving at: http://localhost:${server.port}/`);
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
