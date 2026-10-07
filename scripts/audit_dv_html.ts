import { readFileSync } from "fs";

const html = readFileSync("public/dv/index.html", "utf8");

// 1. Script syntax check
const scriptMatch = html.match(/<script>([\s\S]*?)<\/script>/);
if (!scriptMatch) {
  console.error("No script tag found!");
} else {
  try {
    new Function(scriptMatch[1]);
    console.log("Script syntax: OK!");
  } catch(e) {
    console.error("Script syntax ERROR:", e.message);
  }
}

// 2. getElementById check
const regex = /document\.getElementById\(['"]([^'"]+)['"]\)/g;
let match;
const ids = new Set<string>();
while ((match = regex.exec(html)) !== null) {
  ids.add(match[1]);
}

const missing: string[] = [];
for (const id of ids) {
  if (!html.includes(`id="${id}"`)) {
    missing.push(id);
  }
}

console.log("Total unique IDs queried in script:", ids.size);
console.log("Missing IDs count:", missing.length);
if (missing.length > 0) {
  console.log("Missing IDs:", missing);
}
