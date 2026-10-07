import { resolve } from "path";

const GATE_CSS = `
    /* Cytria Sovereign Access Gate Overlay */
    .cytria-access-gate {
      position: fixed;
      inset: 0;
      width: 100vw;
      height: 100vh;
      background: radial-gradient(circle at 50% 38%, #0e1620 0%, #06090d 100%);
      z-index: 9999999;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px;
      box-sizing: border-box;
      opacity: 1;
      transition: opacity 0.35s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .cytria-access-gate.unlocked {
      opacity: 0;
      pointer-events: none;
    }
    .cytria-gate-card {
      width: 100%;
      max-width: 440px;
      background: rgba(11, 17, 23, 0.96);
      border: 1px solid rgba(201, 162, 77, 0.4);
      box-shadow: 0 30px 80px rgba(0, 0, 0, 0.95), 0 0 50px rgba(201, 162, 77, 0.12);
      padding: 36px 32px 30px;
      box-sizing: border-box;
      text-align: center;
      position: relative;
    }
    .cytria-gate-badge {
      display: inline-block;
      font-family: var(--font-mono, 'JetBrains Mono', monospace);
      font-size: 9.5px;
      font-weight: 700;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: #C9A24D;
      background: rgba(201, 162, 77, 0.12);
      border: 1px solid rgba(201, 162, 77, 0.3);
      padding: 4px 10px;
      margin-bottom: 20px;
    }
    .cytria-gate-logo {
      margin-bottom: 16px;
    }
    .cytria-gate-logo-svg {
      height: 24px;
      max-width: 100%;
    }
    .cytria-gate-title {
      font-family: var(--font-brand, 'Hanken Grotesk', sans-serif);
      font-size: 19px;
      font-weight: 800;
      letter-spacing: 0.02em;
      color: #FFFFFF;
      margin-bottom: 8px;
      text-transform: uppercase;
    }
    .cytria-gate-desc {
      font-family: var(--font-body, 'Inter', sans-serif);
      font-size: 11.5px;
      color: #8F9CAE;
      line-height: 1.55;
      margin-bottom: 24px;
    }
    .cytria-gate-form {
      display: flex;
      flex-direction: column;
      gap: 12px;
      width: 100%;
    }
    .cytria-gate-input-box {
      width: 100%;
    }
    .cytria-gate-input {
      width: 100%;
      background: #080D11;
      border: 1px solid rgba(255, 255, 255, 0.14);
      color: #FFFFFF;
      padding: 12px 14px;
      font-size: 13px;
      font-family: var(--font-mono, monospace);
      box-sizing: border-box;
      outline: none;
      transition: all 0.2s ease;
    }
    .cytria-gate-input:focus {
      border-color: #C9A24D;
      box-shadow: 0 0 15px rgba(201, 162, 77, 0.3);
    }
    .cytria-gate-btn {
      width: 100%;
      background: #C9A24D;
      border: 1px solid #D2AA4F;
      color: #080D11;
      font-family: var(--font-brand, sans-serif);
      font-size: 11.5px;
      font-weight: 700;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      padding: 12px 16px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      transition: all 0.2s ease;
      box-shadow: 0 4px 16px rgba(201, 162, 77, 0.25);
    }
    .cytria-gate-btn:hover {
      background: #DEBC69;
      transform: translateY(-1px);
      box-shadow: 0 6px 22px rgba(201, 162, 77, 0.4);
    }
    .cytria-gate-error {
      font-family: var(--font-mono, monospace);
      font-size: 10.5px;
      color: #EF4444;
      background: rgba(239, 68, 68, 0.1);
      border: 1px solid rgba(239, 68, 68, 0.25);
      padding: 6px 10px;
      display: none;
      text-align: left;
    }
    .cytria-gate-error.visible {
      display: block;
    }
    .cytria-gate-footer {
      margin-top: 22px;
      font-size: 10px;
      color: #637381;
      line-height: 1.4;
      border-top: 1px solid rgba(255, 255, 255, 0.06);
      padding-top: 14px;
    }
`;

const GATE_HTML = `
  <!-- ========================================== -->
  <!-- CYTRIA SOVEREIGN ACCESS GATE (RESTRICTED)  -->
  <!-- ========================================== -->
  <div id="cytriaAccessGate" class="cytria-access-gate" style="display:none;">
    <div class="cytria-gate-card">
      <div class="cytria-gate-badge">GENÈVE · ACCÈS RESTREINT</div>
      <div class="cytria-gate-logo">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="606 188 836 310" class="cytria-gate-logo-svg" role="img" aria-label="Cytria"><path fill="#FFFFFF" fill-rule="evenodd" d="M778.5 207 C767 203.8 755.5 202.5 744 202.5 C676.35 202.5 621.5 256.9 621.5 324 C621.5 391.1 676.35 445.5 744 445.5 C794.5 445.5 837.9 414.8 856.5 371 L803 371 C789 388.2 768.1 398 744 398 C702.86 398 669.5 364.86 669.5 324 C669.5 283.14 702.86 250 744 250 L745 250 Z"/><path fill="#FFFFFF" fill-rule="evenodd" d="M871.5 294 L910.5 294 L948 387 L987.5 294 L1044 294 L1044 258 L1078.5 258 L1078.5 294 L1114.5 294 L1114.5 320 L1078.5 320 L1078.5 390 C1078.5 399.2 1083.3 403 1092.5 403 C1099.5 403 1105.8 402.4 1113 401.5 L1114.5 427 C1107.5 429.3 1099.2 430.5 1090 430.5 C1058.5 430.5 1043.5 420.8 1043.5 395 L1043.5 320 L1014 320 L953 448 C940 475.4 927 484.5 902 484.5 C892 484.5 883.5 484 876 483.5 L882.5 456 L901 456 C914 456 922.5 441.5 930.5 422 Z"/><path fill="#FFFFFF" fill-rule="evenodd" d="M1134 294 L1167.5 294 L1167.5 312 C1178 297.5 1191 290.5 1207 290.5 C1211 290.5 1214.5 291 1217.5 292 L1217.5 321 C1213.5 320 1209 319.5 1204.5 319.5 C1180 319.5 1167.5 333.5 1167.5 358 L1167.5 428.5 L1134 428.5 Z"/><path fill="#FFFFFF" fill-rule="evenodd" d="M1232 294 L1266.5 294 L1266.5 428.5 L1232 428.5 Z M1249 234.5 C1260.9 234.5 1270.5 243.2 1270.5 254 C1270.5 264.8 1260.9 273.5 1249 273.5 C1237.1 273.5 1227.5 264.8 1227.5 254 C1227.5 243.2 1237.1 234.5 1249 234.5 Z"/><path fill="#FFFFFF" fill-rule="evenodd" d="M1298 306 C1314 295.5 1335 289.5 1357 289.5 C1403 289.5 1426.5 309 1426.5 347 L1426.5 428.5 L1391 428.5 L1391 419 C1380 427.5 1364.5 431 1346 431 C1309 431 1287.5 415.8 1287.5 390 C1287.5 361.5 1318 345.5 1357 345.5 L1392.5 345.5 C1392.5 325.5 1380.5 315.5 1358.5 315.5 C1341.5 315.5 1326 320 1314 330 Z M1359 368.5 C1335.5 368.5 1323.5 376 1323.5 388.5 C1323.5 400.2 1334.3 407.5 1350 407.5 C1375 407.5 1392.5 395.8 1392.5 375 L1392.5 368.5 Z"/><path fill="#C9A24D" fill-rule="evenodd" d="M790 210.5 C821.5 223.5 846.3 249 858 281.5 L806 281.5 C795.2 266.5 778.8 255.2 759.5 251 Z"/></svg>
      </div>
      <h2 class="cytria-gate-title">Accès Restreint</h2>
      <p class="cytria-gate-desc">
        Plateforme confidentielle d'intelligence foncière et notariale FAO × SITG Genève. Veuillez renseigner votre clé d'habilitation autorisée.
      </p>
      <form class="cytria-gate-form" onsubmit="handleCytriaGateSubmit(event); return false;">
        <div class="cytria-gate-input-box">
          <input type="password" id="cytriaGateInput" class="cytria-gate-input" placeholder="Clé d'accès confidentielle..." autocomplete="current-password" required />
        </div>
        <button type="submit" id="cytriaGateSubmitBtn" class="cytria-gate-btn">
          <span>Déverrouiller l'accès</span>
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
        </button>
        <div id="cytriaGateError" class="cytria-gate-error">
          Clé d'habilitation incorrecte. Veuillez vérifier la clé d'accès.
        </div>
      </form>
      <div class="cytria-gate-footer">
        Diffusion soumise à accord de confidentialité · République et Canton de Genève
      </div>
    </div>
  </div>
`;

const GATE_JS_FUNCTIONS = `
  /* --- CYTRIA ACCESS GATE SECURITY CONTROLLER --- */
  var CYTRIA_KEY_HASH = 'Q3l0cmlhMjAyNlBhcnQx'; // base64 representation of target key
  var CYTRIA_AUTH_TOKEN = 'cytria_auth';

  function isCytriaKeyValid(val) {
    if (!val || typeof val !== 'string') return false;
    var trimmed = val.trim();
    try {
      return btoa(trimmed) === CYTRIA_KEY_HASH || trimmed === atob(CYTRIA_KEY_HASH);
    } catch (e) {
      return trimmed === atob(CYTRIA_KEY_HASH);
    }
  }

  function unlockCytriaApp() {
    try {
      localStorage.setItem(CYTRIA_AUTH_TOKEN, 'granted');
      sessionStorage.setItem(CYTRIA_AUTH_TOKEN, 'granted');
    } catch (e) {}
    var gate = document.getElementById('cytriaAccessGate');
    if (gate) {
      gate.classList.add('unlocked');
      setTimeout(function() { gate.style.display = 'none'; }, 360);
    }
  }

  function lockCytriaApp() {
    try {
      localStorage.removeItem(CYTRIA_AUTH_TOKEN);
      sessionStorage.removeItem(CYTRIA_AUTH_TOKEN);
    } catch (e) {}
    var gate = document.getElementById('cytriaAccessGate');
    if (gate) {
      gate.classList.remove('unlocked');
      gate.style.display = 'flex';
      var inp = document.getElementById('cytriaGateInput');
      if (inp) {
        inp.value = '';
        setTimeout(function() { inp.focus(); }, 100);
      }
    }
  }

  function handleCytriaGateSubmit(e) {
    if (e && e.preventDefault) e.preventDefault();
    var inp = document.getElementById('cytriaGateInput');
    var err = document.getElementById('cytriaGateError');
    var val = inp ? inp.value : '';

    if (isCytriaKeyValid(val)) {
      if (err) err.classList.remove('visible');
      unlockCytriaApp();
    } else {
      if (err) err.classList.add('visible');
      if (inp) {
        inp.style.borderColor = '#EF4444';
        setTimeout(function() { inp.style.borderColor = ''; }, 1200);
        inp.focus();
        inp.select();
      }
    }
  }

  function initCytriaGate() {
    // 1. Check query params & URL hash
    try {
      var params = new URLSearchParams(window.location.search);
      var queryKey = params.get('key') || params.get('pwd') || params.get('pass') || params.get('auth');
      var hashKey = (window.location.hash || '').replace(/^#/, '');

      if (isCytriaKeyValid(queryKey) || isCytriaKeyValid(hashKey)) {
        unlockCytriaApp();
        if (queryKey) {
          params.delete('key');
          params.delete('pwd');
          params.delete('pass');
          params.delete('auth');
          var qs = params.toString() ? '?' + params.toString() : '';
          var cleanUrl = window.location.pathname + qs + (hashKey && !isCytriaKeyValid(hashKey) ? window.location.hash : '');
          window.history.replaceState({}, document.title, cleanUrl);
        }
        return;
      }
    } catch (e) {}

    // 2. Check persistent browser storage
    try {
      if (localStorage.getItem(CYTRIA_AUTH_TOKEN) === 'granted' || sessionStorage.getItem(CYTRIA_AUTH_TOKEN) === 'granted') {
        unlockCytriaApp();
        return;
      }
    } catch (e) {}

    // 3. Otherwise reveal access gate overlay
    var gate = document.getElementById('cytriaAccessGate');
    if (gate) {
      gate.style.display = 'flex';
      var inp = document.getElementById('cytriaGateInput');
      if (inp) setTimeout(function() { inp.focus(); }, 150);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCytriaGate);
  } else {
    initCytriaGate();
  }
`;

const LOCK_BTN = `
        <button type="button" class="subtool-btn utility-btn" id="btnLockApp" onclick="lockCytriaApp()" title="Verrouiller la session" style="display:inline-flex; align-items:center; gap:5px; border-color:rgba(201,162,77,0.35);">
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="3" y="11" width="18" height="11" rx="0" ry="0"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg> Verrouiller
        </button>`;

async function patchFile(filePath: string) {
  console.log(`Patching ${filePath}...`);
  const file = Bun.file(filePath);
  let text = await file.text();

  // Clean any old cytriaAccessGate if already there to ensure clean idempotency
  if (text.includes('id="cytriaAccessGate"')) {
    console.log(`  Cleaning previous gate insertion...`);
    // Remove previous CSS
    text = text.replace(/\/\* Cytria Sovereign Access Gate Overlay \*\/[\s\S]*?\.cytria-gate-footer\s*\{[\s\S]*?\}/, '');
    // Remove previous HTML
    text = text.replace(/<!-- =+ -->\s*<!-- CYTRIA SOVEREIGN ACCESS GATE \(RESTRICTED\) -->[\s\S]*?<\/div>\s*<\/div>/, '');
    // Remove previous JS
    text = text.replace(/\/\* --- CYTRIA ACCESS GATE SECURITY CONTROLLER --- \*\/[\s\S]*?initCytriaGate\(\);\s*\}\s*/, '');
    text = text.replace(/\/\* --- CYTRIA ACCESS GATE SECURITY CONTROLLER --- \*\/[\s\S]*?\)\(\);/, '');
  }

  // 1. Inject CSS before the LAST </style>
  const lastStyleIdx = text.lastIndexOf("</style>");
  if (lastStyleIdx !== -1) {
    text = text.slice(0, lastStyleIdx) + `${GATE_CSS}\n  ` + text.slice(lastStyleIdx);
  }

  // 2. Inject HTML right after <body...>
  const bodyMatch = text.match(/<body[^>]*>/);
  if (bodyMatch && bodyMatch.index !== undefined) {
    const insertIdx = bodyMatch.index + bodyMatch[0].length;
    text = text.slice(0, insertIdx) + `\n${GATE_HTML}\n` + text.slice(insertIdx);
  }

  // 3. Inject Lock Button into top-bar-utilities if present
  if (text.includes('id="btnVaultToggle"') && !text.includes('id="btnLockApp"')) {
    text = text.replace(/(<button[^>]+id="btnVaultToggle"[^>]*>[\s\S]*?<\/button>)/, `$1\n${LOCK_BTN}`);
  }

  // 4. Inject JS: Find the LAST </script> before the closing </body>
  const lastScriptIdx = text.lastIndexOf("</script>");
  if (lastScriptIdx !== -1) {
    text = text.slice(0, lastScriptIdx) + `\n${GATE_JS_FUNCTIONS}\n` + text.slice(lastScriptIdx);
  } else {
    // If no script tag exists, append one before the last </body>
    const lastBodyIdx = text.lastIndexOf("</body>");
    if (lastBodyIdx !== -1) {
      text = text.slice(0, lastBodyIdx) + `<script>\n${GATE_JS_FUNCTIONS}\n</script>\n` + text.slice(lastBodyIdx);
    }
  }

  await Bun.write(filePath, text);
  console.log(`  Successfully patched ${filePath}`);
}

async function main() {
  await patchFile(resolve("index.html"));
  await patchFile(resolve("src/fao_transactions/visualization/map_builder.py"));
  await patchFile(resolve("welcome.html"));
  await patchFile(resolve("public/dv/index.html"));
  await patchFile(resolve("public/dv/marketing/index.html"));
  console.log("All files patched successfully!");
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
