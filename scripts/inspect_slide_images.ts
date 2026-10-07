import { readFileSync } from 'fs';
import { readZipEntries } from '../src/fao_transactions/dv/dv_pptx_generator.ts';

const buf = readFileSync('Prompts/estimation/DV_Estimation_Template_Premium_FR.pptx');
const entries = readZipEntries(buf);

for (let i = 1; i <= 15; i++) {
  const relsXml = entries.get(`ppt/slides/_rels/slide${i}.xml.rels`)?.toString('utf8') || '';
  const imgMatches: string[] = [];
  const re = /Target="\.\.\/media\/([^"]+)"/g;
  let m;
  while ((m = re.exec(relsXml)) !== null) {
    imgMatches.push(m[1]);
  }
  if (imgMatches.length > 0) {
    console.log(`Slide ${i} images:`, imgMatches.join(', '));
  } else {
    console.log(`Slide ${i}: NO IMAGES`);
  }
}
