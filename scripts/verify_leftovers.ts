import { DVPptxGenerator, readZipEntries } from "../src/fao_transactions/dv/dv_pptx_generator";
import { readFileSync } from "fs";

const generator = new DVPptxGenerator();
const caseStudy = generator.getSautDuLoupCaseStudy();

// Test generation buffer
const buffer = generator.generatePptxBuffer({
  slideReplacements: caseStudy.pptxPayload,
  hideInternalInstructions: true
});

const entries = readZipEntries(buffer);

console.log("=== CHECKING FOR LEFTOVER BRACKETS IN GENERATED PPTX ===");
let totalLeftovers = 0;
for (let i = 1; i <= 15; i++) {
  const xml = entries.get("ppt/slides/slide" + i + ".xml")?.toString("utf8") || "";
  const brackets = xml.match(/\[[^\]]+\]/g);
  if (brackets && brackets.length > 0) {
    const unique = [...new Set(brackets)];
    console.log(`Slide ${i} leftovers (${brackets.length}):`, unique);
    totalLeftovers += brackets.length;
  } else {
    console.log(`Slide ${i}: PERFECT (0 leftovers)`);
  }
}
console.log(`Total leftover placeholders: ${totalLeftovers}`);
