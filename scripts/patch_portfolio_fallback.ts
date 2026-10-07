import { readFileSync, writeFileSync } from "fs";
import { join } from "path";

const filePath = join(process.cwd(), "public/dv/index.html");
let html = readFileSync(filePath, "utf-8");

const fallbackPortfolioCode = `
    const FALLBACK_PORTFOLIO_DATA = {
      mandates: [
        {
          id: "mandat_1",
          address: "Chemin des Gravières 12",
          commune: "Chêne-Bourg",
          broker: "Sandra Bleeckx Vanhalst",
          current_price: 1850000,
          current_price_display: "CHF 1'850'000",
          days_on_market: 74,
          status: "À Réajuster (Mandat Stagnant)",
          status_color: "#9E4000",
          suggested_adjustment_pct: -5.5,
          recommended_action: "Organiser un point vendeur : présenter l'acte notarié récent du Saut-du-Loup 16 à CHF 17'609/m² pour acter un réalignement de prix réaliste."
        },
        {
          id: "mandat_2",
          address: "Route de Veyrier 44",
          commune: "Veyrier",
          broker: "Adrien Désormière",
          current_price: 2650000,
          current_price_display: "CHF 2'650'000",
          days_on_market: 42,
          status: "Actif Normal",
          status_color: "#00939D",
          suggested_adjustment_pct: 0,
          recommended_action: "Poursuivre la commercialisation ciblée sur le réseau privé D&V. Bonne dynamique de demandes acquéreurs."
        },
        {
          id: "mandat_3",
          address: "Chemin de Grange-Canal 8",
          commune: "Chêne-Bougeries",
          broker: "Sandra Bleeckx Vanhalst",
          current_price: 3200000,
          current_price_display: "CHF 3'200'000",
          days_on_market: 88,
          status: "À Réajuster (Mandat Stagnant)",
          status_color: "#9E4000",
          suggested_adjustment_pct: -6.0,
          recommended_action: "Mandat bloqué depuis près de 3 mois. Positionner le bien sous le seuil psychologique de CHF 3.0M pour capter les acquéreurs qualifiés."
        },
        {
          id: "mandat_4",
          address: "Chemin de Sous-Balme 15",
          commune: "Troinex",
          broker: "Adrien Désormière",
          current_price: 3950000,
          current_price_display: "CHF 3'950'000",
          days_on_market: 28,
          status: "Actif Normal",
          status_color: "#00939D",
          suggested_adjustment_pct: 0,
          recommended_action: "Offre d'achat en cours d'analyse juridique et financière par l'acquéreur."
        }
      ],
      buyers: [
        {
          id: "BUYER_DV_01",
          client_name: "Famille M. de V. (Acquéreur Privé)",
          broker: "Sandra Bleeckx Vanhalst",
          budget_chf: 3800000,
          budget_display: "CHF 3'500'000 – 4'000'000",
          target_communes: ["Troinex", "Veyrier", "Chêne-Bougeries"],
          criteria: "Villa contemporaine ou Minergie, 7+ pièces, jardin > 800 m², calme résidentiel",
          match_count: 3,
          top_match: "Parcelle Zone 5 Troinex (art. 602 CC Hoirie) — Score 95%"
        },
        {
          id: "BUYER_DV_02",
          client_name: "M. & Mme K. (Retour Expatriation Londres)",
          broker: "Adrien Désormière",
          budget_chf: 5200000,
          budget_display: "CHF 4'500'000 – 5'500'000",
          target_communes: ["Cologny", "Vandœuvres"],
          criteria: "Prestige, vue lac ou dégagée, terrain piscinable, discrétion totale",
          match_count: 2,
          top_match: "Propriété de caractère Vandœuvres — Score 91%"
        },
        {
          id: "BUYER_DV_03",
          client_name: "Investisseur Privé Genevois",
          broker: "Adrien Désormière",
          budget_chf: 2900000,
          budget_display: "CHF 2'500'000 – 3'200'000",
          target_communes: ["Chêne-Bougeries", "Chêne-Bourg"],
          criteria: "Terrain avec potentiel de détachement/division (Zone 5, IUS 0.20+)",
          match_count: 4,
          top_match: "Parcelle 1'140 m² Zone 5 Chêne-Bougeries — Score 88%"
        },
        {
          id: "BUYER_DV_04",
          client_name: "Dr. & Mme S. (Famille Médicale)",
          broker: "Sandra Bleeckx Vanhalst",
          budget_chf: 2200000,
          budget_display: "CHF 1'900'000 – 2'300'000",
          target_communes: ["Chêne-Bourg", "Thônex"],
          criteria: "Attique ou RDC avec jardin PPE, 4-5 pièces, standing contemporain",
          match_count: 2,
          top_match: "Chemin du Saut-du-Loup 18 (Bâtiment 2018) — Score 98%"
        }
      ],
      weekly_pulse: {
        sales_this_week: 4,
        active_competitor_listings: 12,
        stale_reviews_recommended: 2,
        exclusive_opps: 3
      }
    };
`;

// Insert FALLBACK_PORTFOLIO_DATA before loadPortfolioView
if (!html.includes("FALLBACK_PORTFOLIO_DATA")) {
  html = html.replace("async function loadPortfolioView() {", fallbackPortfolioCode + "\n    async function loadPortfolioView() {");
}

// Ensure loadPortfolioView sets fallback immediately then updates if fetch succeeds
const newLoadPortfolioView = `async function loadPortfolioView() {
      if (!PORTFOLIO_DATA) {
        PORTFOLIO_DATA = FALLBACK_PORTFOLIO_DATA;
        renderMandatesAndBuyers();
      }
      try {
        const res = await fetch('/api/dv/portfolio');
        if (res.ok) {
          const data = await res.json();
          if (data.status === 'ok') {
            PORTFOLIO_DATA = data;
            document.getElementById('pulseSales').textContent = data.weekly_pulse.sales_this_week;
            document.getElementById('pulseCompetitors').textContent = data.weekly_pulse.active_competitor_listings;
            document.getElementById('pulseStale').textContent = data.weekly_pulse.stale_reviews_recommended;
            document.getElementById('pulseOpps').textContent = data.weekly_pulse.exclusive_opps;
            renderMandatesAndBuyers();
          }
        }
      } catch (e) {
        console.warn("Portfolio fetch fallback:", e);
      }
    }`;

const oldLoadPortfolioViewRegex = /async function loadPortfolioView\(\) \{[\s\S]*?renderMandatesAndBuyers\(\);\s*\}\s*\}\s*catch\s*\(e\)\s*\{[\s\S]*?\}\s*\}/;
html = html.replace(oldLoadPortfolioViewRegex, newLoadPortfolioView);

writeFileSync(filePath, html, "utf-8");
console.log("Successfully patched portfolio fallback data!");
