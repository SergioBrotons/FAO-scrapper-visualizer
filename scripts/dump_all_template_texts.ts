import { readFileSync } from 'fs';
import { readZipEntries } from '../src/fao_transactions/dv/dv_pptx_generator.ts';

const buf = readFileSync('Prompts/estimation/DV_Estimation_Template_Premium_FR.pptx');
const entries = readZipEntries(buf);

for (let i = 1; i <= 15; i++) {
  const xml = entries.get(`ppt/slides/slide${i}.xml`)?.toString('utf8') || '';
  const re = /<a:t[^>]*>([^<]+)<\/a:t>/g;
  let m;
  const ts: string[] = [];
  while ((m = re.exec(xml)) !== null) {
    if (m[1].trim()) ts.push(m[1].trim());
  }
  console.log(`\n=== SLIDE ${i} (${ts.length} texts) ===`);
  console.log(ts.join(' | '));
}
