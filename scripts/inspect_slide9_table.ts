import { readZipEntries } from "../src/fao_transactions/dv/dv_pptx_generator";
import { readFileSync } from "fs";

const buf = readFileSync("Prompts/estimation/DV_Estimation_Template_Premium_FR.pptx");
const entries = readZipEntries(buf);
const s9 = entries.get("ppt/slides/slide9.xml")?.toString("utf8") || "";

const shapes = s9.match(/<p:sp>[\s\S]*?<\/p:sp>/g) || [];
console.log("Shapes in slide 9:", shapes.length);
shapes.forEach((sp, idx) => {
  const texts = (sp.match(/<a:t[^>]*>([^<]+)<\/a:t>/g) || []).map(t => t.replace(/<[^>]+>/g, ""));
  if (texts.length > 0) {
    console.log(`Shape ${idx}:`, texts.join(" ~ "));
  }
});
