import sys
from pathlib import Path

target_file = Path("src/fao_transactions/visualization/map_builder.py")
content = target_file.read_text(encoding="utf-8")

# Check if already injected
if "btnCopilotToggle" in content:
    print("Already injected into map_builder.py")
    sys.exit(0)

# 1. CSS
css_snippet = """
    /* Cytria AI Copilot Drawer (MiniMax M3) */
    .copilot-drawer {
      position: fixed;
      top: 104px;
      right: 14px;
      width: 440px;
      max-width: calc(100vw - 28px);
      height: calc(100vh - 120px);
      background: rgba(11, 17, 23, 0.95);
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
      border: 1px solid var(--panel-border-gold);
      box-shadow: 0 25px 60px rgba(0, 0, 0, 0.75), 0 0 20px rgba(201, 162, 77, 0.15);
      z-index: 1050;
      display: flex;
      flex-direction: column;
      transform: translateX(115%);
      transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      pointer-events: auto;
    }
    .copilot-drawer.active {
      transform: translateX(0);
    }
    .copilot-header {
      padding: 12px 16px;
      border-bottom: 1px solid var(--panel-border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: rgba(8, 13, 17, 0.7);
    }
    .copilot-avatar {
      width: 28px;
      height: 28px;
      background: linear-gradient(135deg, #A77F22 0%, #C9A24D 100%);
      color: #080D11;
      font-weight: 900;
      font-size: 11px;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 0 10px rgba(201, 162, 77, 0.4);
    }
    .copilot-icon-btn {
      background: transparent;
      border: 1px solid var(--panel-border);
      color: var(--color-sand-300);
      width: 26px;
      height: 26px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      font-size: 12px;
      transition: all 0.15s ease;
    }
    .copilot-icon-btn:hover {
      background: rgba(255, 255, 255, 0.1);
      color: #fff;
      border-color: var(--color-brand-400);
    }
    .copilot-chips {
      padding: 10px 14px;
      display: flex;
      gap: 6px;
      overflow-x: auto;
      scrollbar-width: none;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      background: rgba(8, 13, 17, 0.3);
    }
    .copilot-chips::-webkit-scrollbar { display: none; }
    .copilot-chip {
      background: rgba(201, 162, 77, 0.08);
      border: 1px solid rgba(201, 162, 77, 0.25);
      color: var(--color-sand-200);
      font-size: 10px;
      padding: 4px 9px;
      white-space: nowrap;
      cursor: pointer;
      font-family: var(--font-body);
      transition: all 0.15s ease;
    }
    .copilot-chip:hover {
      background: rgba(201, 162, 77, 0.2);
      border-color: var(--color-brand-400);
      color: #fff;
    }
    .copilot-messages {
      flex: 1;
      padding: 16px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 12px;
      font-size: 12.5px;
      line-height: 1.55;
    }
    .copilot-bubble {
      padding: 12px 14px;
      max-width: 92%;
      word-break: break-word;
    }
    .copilot-bubble.user {
      align-self: flex-end;
      background: rgba(201, 162, 77, 0.18);
      border: 1px solid rgba(201, 162, 77, 0.4);
      color: var(--color-paper);
    }
    .copilot-bubble.bot {
      align-self: flex-start;
      background: rgba(16, 24, 32, 0.85);
      border: 1px solid var(--panel-border);
      color: var(--color-sand-100);
    }
    .copilot-bubble.bot .bubble-header {
      font-size: 9px;
      font-weight: 800;
      letter-spacing: 0.08em;
      color: var(--color-brand-400);
      margin-bottom: 6px;
      text-transform: uppercase;
      font-family: var(--font-mono);
    }
    .copilot-input-area {
      padding: 12px 14px;
      border-top: 1px solid var(--panel-border);
      display: flex;
      gap: 8px;
      background: rgba(8, 13, 17, 0.8);
    }
    .copilot-input-area input {
      flex: 1;
      background: var(--color-ink-950);
      border: 1px solid var(--panel-border);
      color: var(--color-paper);
      padding: 8px 12px;
      font-size: 12px;
      font-family: var(--font-body);
      outline: none;
      transition: border-color 0.2s ease;
    }
    .copilot-input-area input:focus {
      border-color: var(--color-brand-400);
      box-shadow: 0 0 10px rgba(201, 162, 77, 0.2);
    }
    .copilot-input-area button {
      background: var(--color-brand-500);
      border: 1px solid var(--color-brand-400);
      color: var(--color-ink-950);
      padding: 0 14px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.15s ease;
    }
    .copilot-input-area button:hover {
      background: var(--color-brand-400);
      color: #000;
    }
"""

css_anchor = "from { opacity: 0; transform: scale(0.98); }\n      to { opacity: 1; transform: scale(1); }\n    }"
if css_anchor not in content:
    css_anchor = "from { opacity: 0; transform: scale(0.98); }\r\n      to { opacity: 1; transform: scale(1); }\r\n    }"

content = content.replace(css_anchor, css_anchor + "\n" + css_snippet, 1)

# 2. Trigger Button in Utilities
btn_snippet = """        <button type="button" class="subtool-btn utility-btn" id="btnCopilotToggle" onclick="toggleCopilotDrawer()" title="Ouvrir le Copilote IA (MiniMax M3)" style="display:inline-flex; align-items:center; gap:6px; background:linear-gradient(135deg, rgba(201,162,77,0.28) 0%, rgba(201,162,77,0.1) 100%) !important; border-color:var(--color-brand-400) !important; color:#fff !important; font-weight:700 !important; box-shadow:0 0 10px rgba(201,162,77,0.2);">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
          <span>Copilote IA</span>
          <span class="subtool-badge" style="background:#C9A24D; color:#080D11; font-weight:800; font-size:8px;">M3</span>
        </button>
"""
btn_anchor = '<button type="button" class="subtool-btn utility-btn" id="hudOpenCmaBtn"'
content = content.replace(btn_anchor, btn_snippet + "        " + btn_anchor, 1)

# 3. Drawer HTML markup before Leaflet script
drawer_html = """
  <!-- Cytria AI Copilot Drawer (MiniMax M3) -->
  <div id="copilotDrawer" class="copilot-drawer">
    <div class="copilot-header">
      <div style="display:flex; align-items:center; gap:10px;">
        <div class="copilot-avatar">M3</div>
        <div>
          <div style="font-weight:700; font-size:12px; letter-spacing:0.04em; text-transform:uppercase;">CYTRIA COPILOT</div>
          <div id="copilotPersonaBadge" style="font-size:9px; color:var(--color-brand-400); font-family:var(--font-mono);">MODE MARCHÉ (FAO × SITG)</div>
        </div>
      </div>
      <div style="display:flex; align-items:center; gap:6px;">
        <button class="copilot-icon-btn" onclick="clearCopilotHistory()" title="Effacer l'historique">↺</button>
        <button class="copilot-icon-btn" onclick="toggleCopilotDrawer()" title="Fermer">✕</button>
      </div>
    </div>

    <div class="copilot-chips" id="copilotChips">
      <button class="copilot-chip" onclick="askCopilot('Quels sont les comparables récents de villas à Cologny ?')">📍 Comparables Cologny</button>
      <button class="copilot-chip" onclick="askCopilot('Prix médian et volume à Vandoeuvres en 2025-2026')">📊 Médiane Vandoeuvres</button>
      <button class="copilot-chip" onclick="askCopilot('Qui sont les voisins de la parcelle 1677 à Cologny ?')">🎯 Voisins Parcelle 1677</button>
      <button class="copilot-chip" onclick="askCopilot('Simulation Casatax pour un bien à 1\\\'400\\\'000 CHF avec 6 ans de détention')">💰 Casatax & LCPur</button>
    </div>

    <div class="copilot-messages" id="copilotMessages">
      <div class="copilot-bubble bot">
        <div class="bubble-header">CYTRIA COPILOT • MINIMAX M3</div>
        <div class="bubble-content">Bonjour. Je suis votre copilote foncier pour le Canton de Genève. Posez-moi une question sur une transaction, une parcelle, un secteur ou une simulation fiscale. Mes réponses pilotent directement la carte.</div>
      </div>
    </div>

    <div class="copilot-input-area">
      <input type="text" id="copilotInput" placeholder="Posez une question foncière ou notariée..." onkeydown="if(event.key==='Enter') sendCopilotMessage()" />
      <button id="copilotSendBtn" onclick="sendCopilotMessage()" title="Envoyer">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
      </button>
    </div>
  </div>
"""
drawer_anchor = '<!-- Leaflet & MarkerCluster JS -->'
content = content.replace(drawer_anchor, drawer_html + "\n  " + drawer_anchor, 1)

# 4. JS controller before </script>
js_controller = """
  // ==========================================
  // CYTRIA AI COPILOT CONTROLLER (MINIMAX M3)
  // ==========================================
  let copilotConversation = [];

  function toggleCopilotDrawer() {
    const drawer = document.getElementById('copilotDrawer');
    if (!drawer) return;
    const isActive = drawer.classList.toggle('active');
    const toggleBtn = document.getElementById('btnCopilotToggle');
    if (toggleBtn) {
      toggleBtn.classList.toggle('active', isActive);
    }
    if (isActive) {
      updateCopilotPersonaBadge();
      const input = document.getElementById('copilotInput');
      if (input) setTimeout(() => input.focus(), 250);
    }
  }

  function updateCopilotPersonaBadge() {
    const badge = document.getElementById('copilotPersonaBadge');
    if (!badge) return;
    const suite = typeof currentProductSuite !== 'undefined' ? currentProductSuite : 'MARKET';
    if (suite === 'MARKET') badge.textContent = 'MODE MARCHÉ & PRIX (FAO × SITG)';
    else if (suite === 'SOURCING') badge.textContent = 'MODE SOURCING & PROSPECTION';
    else if (suite === 'AGENCY_BI') badge.textContent = 'MODE BENCHMARK 96 AGENCES';
  }

  function clearCopilotHistory() {
    copilotConversation = [];
    const container = document.getElementById('copilotMessages');
    if (container) {
      container.innerHTML = `
        <div class="copilot-bubble bot">
          <div class="bubble-header">CYTRIA COPILOT • MINIMAX M3</div>
          <div class="bubble-content">Historique réinitialisé. En quoi puis-je vous éclairer sur le foncier genevois ?</div>
        </div>
      `;
    }
  }

  function askCopilot(question) {
    const drawer = document.getElementById('copilotDrawer');
    if (drawer && !drawer.classList.contains('active')) {
      toggleCopilotDrawer();
    }
    const input = document.getElementById('copilotInput');
    if (input) {
      input.value = question;
      sendCopilotMessage();
    }
  }

  async function sendCopilotMessage() {
    const input = document.getElementById('copilotInput');
    const sendBtn = document.getElementById('copilotSendBtn');
    const container = document.getElementById('copilotMessages');
    if (!input || !container) return;

    const userText = input.value.trim();
    if (!userText) return;

    input.value = '';
    input.disabled = true;
    if (sendBtn) sendBtn.disabled = true;

    // Append user bubble
    const userDiv = document.createElement('div');
    userDiv.className = 'copilot-bubble user';
    userDiv.textContent = userText;
    container.appendChild(userDiv);

    // Append loading bot bubble
    const botDiv = document.createElement('div');
    botDiv.className = 'copilot-bubble bot';
    botDiv.innerHTML = `
      <div class="bubble-header">CYTRIA COPILOT • RECHERCHE...</div>
      <div class="bubble-content"><span class="scan-live-dot" style="display:inline-block; margin-right:6px;"></span> Interrogation de la base FAO et calcul en cours...</div>
    `;
    container.appendChild(botDiv);
    container.scrollTop = container.scrollHeight;

    copilotConversation.push({ role: 'user', content: userText });

    try {
      const activeSuite = typeof currentProductSuite !== 'undefined' ? currentProductSuite : 'MARKET';
      const mapCenter = (typeof map !== 'undefined' && map.getCenter) ? [map.getCenter().lat, map.getCenter().lng] : [46.2044, 6.1432];
      const mapZoom = (typeof map !== 'undefined' && map.getZoom) ? map.getZoom() : 12;

      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: copilotConversation,
          active_suite: activeSuite,
          map_context: { center: mapCenter, zoom: mapZoom }
        })
      });

      if (!res.ok) throw new Error('HTTP ' + res.status);
      const data = await res.json();

      botDiv.innerHTML = `
        <div class="bubble-header">${data.model_used || 'CYTRIA COPILOT • MINIMAX M3'}</div>
        <div class="bubble-content">${formatMarkdownSimple(data.reply)}</div>
      `;

      copilotConversation.push({ role: 'assistant', content: data.reply });

      // Execute map actions if returned
      if (data.map_actions && Array.isArray(data.map_actions)) {
        for (const action of data.map_actions) {
          if (action.type === 'FLY_TO' && action.payload && typeof map !== 'undefined') {
            map.flyTo([action.payload.lat, action.payload.lon], action.payload.zoom || 16, {
              animate: true,
              duration: 1.5
            });
          }
        }
      }

    } catch (err) {
      botDiv.innerHTML = `
        <div class="bubble-header" style="color:#ef4444;">ERREUR COPILOTE</div>
        <div class="bubble-content" style="color:#fca5a5;">Impossible de contacter le copilote (${err.message}). Vérifiez que le serveur local est actif.</div>
      `;
    } finally {
      input.disabled = false;
      if (sendBtn) sendBtn.disabled = false;
      input.focus();
      container.scrollTop = container.scrollHeight;
    }
  }

  function formatMarkdownSimple(text) {
    if (!text) return '';
    let out = text
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/### (.*)/g, '<div style="font-weight:800; font-size:13px; color:#C9A24D; margin:6px 0 4px 0;">$1</div>')
      .replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>')
      .replace(/\\*(.*?)\\*/g, '<em>$1</em>')
      .replace(/- (.*)/g, '<div style="margin-left:8px; display:flex; gap:6px;"><span style="color:#C9A24D;">•</span><span>$1</span></div>')
      .replace(/\\n\\n/g, '<div style="height:6px;"></div>')
      .replace(/\\n/g, '<br/>');
    return out;
  }
"""

script_end_anchor = "if (typeof applyFilters === 'function') applyFilters();\n  }"
if script_end_anchor not in content:
    script_end_anchor = "if (typeof applyFilters === 'function') applyFilters();\r\n  }"

content = content.replace(script_end_anchor, script_end_anchor + "\n" + js_controller, 1)

target_file.write_text(content, encoding="utf-8")
print("Successfully injected Copilot UI into map_builder.py")
