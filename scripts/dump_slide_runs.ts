import { readZipEntries } from "../src/fao_transactions/dv/dv_pptx_generator";
import { readFileSync } from "fs";

const buf = readFileSync("Prompts/estimation/DV_Estimation_Template_Premium_FR.pptx");
const entries = readZipEntries(buf);

function dumpSlide(num: number) {
  const xml = entries.get("ppt/slides/slide" + num + ".xml")?.toString("utf8") || "";
  // Strip XML tags to see text runs
  const textRuns = (xml.match(/<a:t[^>]*>([^<]+)<\/a:t>/g) || []).map(t => t.replace(/<[^>]+>/g, ""));
  console.log(`\n=================== SLIDE ${num} TEXT ===================`);
  console.log(textRuns.join(" | "));
}

dumpSlide(8);
dumpSlide(9);
dumpSlide(13);
dumpSlide(15);
