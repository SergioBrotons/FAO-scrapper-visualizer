import { readFileSync } from 'fs';
import { readZipEntries } from '../src/fao_transactions/dv/dv_pptx_generator.ts';

const buf = readFileSync('Prompts/estimation/DV_Estimation_Template_Premium_FR.pptx');
const entries = readZipEntries(buf);

for (const [k, v] of entries) {
  if (k.endsWith('.rels') || k.endsWith('.xml')) {
    const s = v.toString('utf8');
    if (s.includes('media/') || s.includes('image')) {
      const re = /media\/([^"'\s>]+)/g;
      let m;
      const found: string[] = [];
      while ((m = re.exec(s)) !== null) {
        found.push(m[1]);
      }
      if (found.length > 0) {
        console.log(`${k} -> ${found.join(', ')}`);
      }
    }
  }
}
