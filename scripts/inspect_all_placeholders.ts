import { readZipEntries } from "../src/fao_transactions/dv/dv_pptx_generator";
import { readFileSync } from "fs";

const buf = readFileSync("Prompts/estimation/DV_Estimation_Template_Premium_FR.pptx");
const entries = readZipEntries(buf);

for (let i = 1; i <= 15; i++) {
  const xml = entries.get("ppt/slides/slide" + i + ".xml")?.toString("utf8") || "";
  const brackets = xml.match(/\[[^\]]+\]/g);
  console.log(`=== SLIDE ${i} BRACKETS ===`, brackets ? [...new Set(brackets)] : "none");
}
