import { join } from "path";
import { writeFileSync } from "fs";
import { CompetitorBenchmarkService } from "../src/content_marketing/competitor_benchmark_service.ts";

const svc = new CompetitorBenchmarkService();
const data = svc.getSocialSurveillance();

const outPath = join(import.meta.dir, "..", "public", "dv", "marketing", "surveillance_data.js");
const content = `// Auto-generated 96-agency Geneva intelligence dataset\nwindow.INITIAL_SURVEILLANCE_DATA = ${JSON.stringify(data)};\n`;
writeFileSync(outPath, content, "utf-8");
console.log(`Successfully generated ${outPath} with ${data.surveillance.length} agencies.`);
