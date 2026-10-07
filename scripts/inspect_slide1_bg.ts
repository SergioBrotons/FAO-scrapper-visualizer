import { readFileSync } from 'fs';
import { readZipEntries } from '../src/fao_transactions/dv/dv_pptx_generator.ts';

const buf = readFileSync('Prompts/estimation/DV_Estimation_Template_Premium_FR.pptx');
const entries = readZipEntries(buf);

const s1Xml = entries.get('ppt/slides/slide1.xml')?.toString('utf8') || '';
console.log(s1Xml.slice(0, 1500));
