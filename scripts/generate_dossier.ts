import { ValuationService } from "../src/fao_transactions/dossier/valuation_service.ts";
import { writeFileSync, mkdirSync } from "fs";
import { join } from "path";

const args = process.argv.slice(2);
const txId = parseInt(args[0] || "16928");

const service = new ValuationService();
const html = service.renderHtml(txId);
const data = service.getDossier(txId);

if (!data) {
  console.error(`Transaction #${txId} introuvable.`);
  process.exit(1);
}

const outDir = join(process.cwd(), "data/exports");
mkdirSync(outDir, { recursive: true });
const outFile = join(outDir, `dossier_avis_valeur_${txId}.html`);

writeFileSync(outFile, html, "utf-8");

console.log("----------------------------------------------------------------");
console.log(`   AVIS DE VALEUR NOTARIÉ & DOSSIER D'EXPERTISE : #${txId}`);
console.log("----------------------------------------------------------------");
console.log(`- Dossier ID :        ${data.meta.dossier_id}`);
console.log(`- Commune :           ${data.transaction.commune}`);
console.log(`- Prix notarié :      ${data.transaction.price_chf?.toLocaleString("fr-CH")} CHF`);
console.log(`- Médiane OCSTAT :    ${data.ocstat.prix_median_m2_ppe?.toLocaleString("fr-CH")} CHF/m²`);
console.log(`- Éligibilité CASATAX: ${data.financial.is_casatax_eligible ? "OUI" : "NON"} (Gain: ${data.financial.casatax_savings_chf?.toLocaleString("fr-CH")} CHF)`);
console.log(`- Salaire FINMA min:  ${data.financial.min_gross_annual_income_chf?.toLocaleString("fr-CH")} CHF/an`);
console.log(`- Comparables trouvés: ${data.comparables.length}`);
console.log(`\n[OK] Rapport imprimable A4 généré avec succès :\n-> ${outFile}\n`);
