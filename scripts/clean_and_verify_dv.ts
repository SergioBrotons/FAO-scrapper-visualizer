import { readFileSync, writeFileSync } from "fs";
import { join } from "path";

const filePath = join(process.cwd(), "public/dv/index.html");
let html = readFileSync(filePath, "utf-8");

console.log("Original file size:", html.length);

// 1. Check duplicate IDs
const duplicateIds = ["viewRadar", "viewMandates", "viewBuyers"];
duplicateIds.forEach(id => {
  const matches = html.match(new RegExp(`id=["']${id}["']`, "g"));
  console.log(`ID ${id} occurrences:`, matches ? matches.length : 0);
});

// 2. Remove the empty duplicate views at lines ~2548-2564
const emptyViewsRegex = /<!-- ================= VIEW 3: RADAR SECTEUR \(TERRITORY\) ================= -->[\s\S]*?<!-- ================= VIEW 5: ACTIVER MES ACHETEURS \(MATCH\) ================= -->[\s\S]*?<\/div>\s*<\/div>/;

if (emptyViewsRegex.test(html)) {
  console.log("Found empty duplicate views block! Removing...");
  html = html.replace(emptyViewsRegex, "");
}

// 3. Check where </main> is
// We need <main class="container"> to encompass: viewHub, viewValue, viewRadar, viewMandates, viewBuyers, and app-trust-footer!
// Let's check how many </main> tags there are
const mainCloses = html.match(/<\/main>/g);
console.log("Total </main> tags:", mainCloses ? mainCloses.length : 0);

// If there's an early </main> before viewRadar, let's fix it so all views are properly contained within one <main>
// Find the first </main> and check if viewRadar appears after it
const firstMainClose = html.indexOf("</main>");
const viewRadarPos = html.indexOf('id="viewRadar"');
console.log("firstMainClose pos:", firstMainClose, "viewRadarPos:", viewRadarPos);

if (firstMainClose !== -1 && viewRadarPos !== -1 && viewRadarPos > firstMainClose) {
  console.log("viewRadar is placed after the first </main>! Restructuring so all views are inside <main>...");
  // Remove the premature </main> and its misplaced footer
  // Let's find the trust-footer right before the first </main>
  const prematureCloseRegex = /<footer class="app-trust-footer">[\s\S]*?<\/footer>\s*<\/main>/;
  html = html.replace(prematureCloseRegex, "");
}

// 4. Ensure all 6 wizard panes and tabs exist
for (let i = 1; i <= 6; i++) {
  const hasPane = html.includes(`id="wizardPane${i}"`);
  const hasTab = html.includes(`id="wizardTab${i}"`);
  console.log(`Step ${i} -> wizardPane${i}: ${hasPane}, wizardTab${i}: ${hasTab}`);
}

writeFileSync(filePath, html, "utf-8");
console.log("Cleaned public/dv/index.html successfully!");
