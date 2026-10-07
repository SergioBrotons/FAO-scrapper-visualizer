import { readFileSync, existsSync } from 'fs';
import { readZipEntries } from '../src/fao_transactions/dv/dv_pptx_generator.ts';

const files = [
  'Prompts/estimation/DV_Estimation_Template_Premium_FR.pptx',
  'data/exports/Estimation_DV_Template_Vierge_Officiel.pptx',
  'data/exports/Estimation_Saut_du_Loup_18_Brotons_2026.pptx'
];

for (const fname of files) {
  if (!existsSync(fname)) {
    console.log(fname, 'NOT FOUND');
    continue;
  }
  const buf = readFileSync(fname);
  const entries = readZipEntries(buf);
  const media = Array.from(entries.keys()).filter(k => k.startsWith('ppt/media/'));
  let sautCount = 0;
  let placeholderCount = 0;

  for (let i = 1; i <= 15; i++) {
    const s = entries.get(`ppt/slides/slide${i}.xml`)?.toString('utf8') || '';
    const m1 = s.match(/Saut-du-Loup|Brotons/gi);
    if (m1) sautCount += m1.length;
    const m2 = s.match(/\[[A-Z0-9\s/éèêàâôûîç\.\'’_\-]+\]/g);
    if (m2) placeholderCount += m2.length;
  }

  console.log(`=== ${fname} === (${buf.length} bytes)`);
  console.log(`  Media files count: ${media.length}`, media.slice(0, 5));
  console.log(`  Saut-du-Loup / Brotons occurrences: ${sautCount}`);
  console.log(`  [PLACEHOLDER] occurrences: ${placeholderCount}`);

  // check media file sizes
  for (const m of media) {
    const mBuf = entries.get(m);
    console.log(`    ${m}: ${mBuf ? mBuf.length : 0} bytes`);
  }
}
