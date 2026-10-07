import { readFileSync } from 'fs';
import { readZipEntries } from '../src/fao_transactions/dv/dv_pptx_generator.ts';

const buf = readFileSync('Prompts/estimation/DV_Estimation_Template_Premium_FR.pptx');
const entries = readZipEntries(buf);

const s1Xml = entries.get('ppt/slides/slide1.xml')?.toString('utf8') || '';
const s1Rels = entries.get('ppt/slides/_rels/slide1.xml.rels')?.toString('utf8') || '';

console.log('--- SLIDE 1 RELS ---');
console.log(s1Rels);

console.log('--- SLIDE 1 PICS ---');
const re = /<p:pic>[\s\S]*?<\/p:pic>/g;
let m;
while ((m = re.exec(s1Xml)) !== null) {
  console.log(m[0].slice(0, 300));
}
