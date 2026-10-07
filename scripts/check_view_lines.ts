import { readFileSync } from "fs";
import { join } from "path";

const s = readFileSync(join(process.cwd(), "public/dv/index.html"), "utf-8");
["viewHub", "viewValue", "viewRadar", "viewMandates", "viewBuyers"].forEach(id => {
  let idx = 0;
  const positions: number[] = [];
  while ((idx = s.indexOf(`id="${id}"`, idx)) !== -1) {
    const line = s.slice(0, idx).split("\n").length;
    positions.push(line);
    idx += 10;
  }
  console.log(`id="${id}" found at line(s):`, positions);
});
