import { readFileSync } from 'fs';
import { readZipEntries } from '../src/fao_transactions/dv/dv_pptx_generator.ts';

const buf = readFileSync('Prompts/estimation/DV_Estimation_Template_Premium_FR.pptx');
const entries = readZipEntries(buf);

const s5Xml = entries.get('ppt/slides/slide5.xml')?.toString('utf8') || '';
console.log('--- SLIDE 5 XML (first 1000 chars) ---');
console.log(s5Xml.slice(0, 1000));

// Find pic elements
const pics = s5Xml.match(/<p:pic>[\s\S]*?<\/p:pic>/g) || [];
console.log('Slide 5 pics count:', pics.length);
if (pics.length > 0) {
  console.log('Sample pic element:');
  console.log(pics[0]);
}
