import { readFileSync, writeFileSync } from "fs";

const filePath = "public/dv/index.html";
let html = readFileSync(filePath, "utf8");

// CSS for character counters and tabulated cards
const newCss = `
    /* Tabulated Wizard Cards */
    .wizard-card {
      background: #FFFFFF;
      border: 1px solid var(--dv-border);
      border-radius: 8px;
      padding: 24px 28px;
      margin-bottom: 22px;
      box-shadow: 0 2px 10px rgba(0, 74, 79, 0.04);
    }
    .wizard-card-header {
      font-family: 'Cormorant Garamond', Georgia, serif;
      font-size: 21px;
      font-weight: 700;
      color: var(--dv-deep-green);
      margin-bottom: 4px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .wizard-card-sub {
      font-size: 12px;
      color: var(--dv-text-muted);
      margin-bottom: 18px;
    }

    /* Character Counter & PPTX Space Recommendation */
    .char-meta {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 5px;
      font-size: 11px;
    }
    .char-hint {
      color: var(--dv-text-muted);
      display: flex;
      align-items: center;
      gap: 4px;
    }
    .char-counter {
      font-weight: 700;
      color: var(--dv-teal);
      background: rgba(0, 147, 157, 0.08);
      padding: 2px 7px;
      border-radius: 4px;
    }
    .char-counter.warning {
      color: var(--dv-brown-warm);
      background: rgba(158, 64, 0, 0.1);
    }
    .char-counter.danger {
      color: #DC2626;
      background: rgba(220, 38, 38, 0.1);
      font-weight: 800;
    }

    /* Spacious Inputs */
    .form-field {
      display: flex;
      flex-direction: column;
      gap: 7px;
    }
    .form-field label {
      font-size: 12px;
      font-weight: 700;
      color: var(--dv-deep-green);
      letter-spacing: 0.01em;
    }
    .form-field input, .form-field select {
      height: 48px;
      padding: 12px 16px;
      border: 1px solid rgba(0, 147, 157, 0.28);
      border-radius: 8px;
      font-family: inherit;
      font-size: 14px;
      color: var(--dv-text-main);
      background: #FFFFFF;
      outline: none;
      box-shadow: 0 1px 3px rgba(0,0,0,0.02);
      transition: all 0.2s;
    }
    .form-field textarea {
      padding: 14px 16px;
      border: 1px solid rgba(0, 147, 157, 0.28);
      border-radius: 8px;
      font-family: inherit;
      font-size: 13.5px;
      color: var(--dv-text-main);
      background: #FFFFFF;
      outline: none;
      min-height: 115px;
      line-height: 1.6;
      box-shadow: 0 1px 3px rgba(0,0,0,0.02);
      transition: all 0.2s;
      resize: vertical;
    }
    .form-field input:focus, .form-field select:focus, .form-field textarea:focus {
      border-color: var(--dv-teal);
      box-shadow: 0 0 0 3px rgba(0, 147, 157, 0.15);
    }
`;

if (!html.includes(".wizard-card")) {
  html = html.replace("</style>", newCss + "\n  </style>");
}

// Ensure container max-width is 1420px
html = html.replace(/max-width:\s*1240px;/g, "max-width: 1420px;");

// Update character counting script in JS
const charCounterScript = `
    // PPTX Character Limitation & Recommendation Bindings
    function bindCharCounter(inputId, counterId, maxLen, slideNum) {
      const input = document.getElementById(inputId);
      const counter = document.getElementById(counterId);
      if (!input || !counter) return;

      function update() {
        const len = (input.value || '').length;
        counter.textContent = len + ' / ' + maxLen + ' car. max (Slide ' + slideNum + ')';
        if (len > maxLen) {
          counter.className = 'char-counter danger';
          counter.title = 'Attention: Ce texte risque de déborder de l\\'encadré PowerPoint sur la diapositive ' + slideNum;
        } else if (len > maxLen * 0.88) {
          counter.className = 'char-counter warning';
          counter.title = 'Volume textuel approchant la limite optimale de la diapositive ' + slideNum;
        } else {
          counter.className = 'char-counter';
          counter.title = 'Taille optimale pour la mise en page de la diapositive ' + slideNum;
        }
      }

      input.addEventListener('input', update);
      update();
    }

    function initAllCharCounters() {
      bindCharCounter('wizPropertyType', 'cntPropertyType', 60, 1);
      bindCharCounter('wizMicroLocation', 'cntMicroLocation', 140, 3);
      bindCharCounter('wizQualDist', 'cntQualDist', 150, 4);
      bindCharCounter('wizQualEquip', 'cntQualEquip', 150, 4);
      bindCharCounter('wizQualState', 'cntQualState', 150, 4);
      bindCharCounter('wizQualEnv', 'cntQualEnv', 150, 4);
      bindCharCounter('wizNormMethod', 'cntNormMethod', 180, 9);
      bindCharCounter('wizMarketTrend', 'cntMarketTrend', 150, 10);
      bindCharCounter('wizNegHypo', 'cntNegHypo', 150, 12);
      bindCharCounter('wizStratPos', 'cntStratPos', 160, 12);
      bindCharCounter('wizLippText', 'cntLippText', 160, 13);
      bindCharCounter('wizMandateText', 'cntMandateText', 160, 14);
      bindCharCounter('wizConclusionText', 'cntConclusionText', 160, 15);
    }
`;

if (!html.includes("function bindCharCounter")) {
  html = html.replace("window.addEventListener('DOMContentLoaded', () => {", charCounterScript + "\n    window.addEventListener('DOMContentLoaded', () => {\n      initAllCharCounters();");
}

await Bun.write(filePath, html);
console.log("Applied CSS and JS counter bindings!");
