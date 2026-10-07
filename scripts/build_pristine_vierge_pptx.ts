import { readFileSync, existsSync } from 'fs';
import { join } from 'path';
import { readZipEntries, writeZip } from '../src/fao_transactions/dv/dv_pptx_generator.ts';

const rootDir = process.cwd();
const templatePath = join(rootDir, 'Prompts', 'estimation', 'DV_Estimation_Template_Premium_FR.pptx');
const outputPath = join(rootDir, 'data', 'exports', 'Estimation_DV_Template_Vierge_Officiel.pptx');

const coverPlaceholderPath = join(rootDir, 'public', 'dv', 'assets', 'dv_cover_placeholder.jpg');
const photoPlaceholderPath = join(rootDir, 'public', 'dv', 'assets', 'dv_photo_placeholder.jpg');

console.log('Building Pristine Blank Template PPTX...');
const rawTemplate = readFileSync(templatePath);
const entries = readZipEntries(rawTemplate);

// 1. Clean XML text across all slides
for (let i = 1; i <= 15; i++) {
  const slideFile = `ppt/slides/slide${i}.xml`;
  if (entries.has(slideFile)) {
    let xml = entries.get(slideFile)!.toString('utf8');

    // Remove internal reviewer banners and helper instructions
    xml = xml.replace(/INTERNE · MASQUER AVANT EXPORT/g, '');
    xml = xml.replace(/SOURCE À AJOUTER[^<]*/g, '');
    xml = xml.replace(/Photo exemple · à remplacer/g, '');
    xml = xml.replace(/PHOTO COMPARABLE\s*Capture datée/g, '[PHOTO COMPARABLE]');

    entries.set(slideFile, Buffer.from(xml, 'utf8'));
  }
}

// 2. Replace Property Photos with Elegant Placeholders
const coverPlaceholderBuf = readFileSync(coverPlaceholderPath);
const photoPlaceholderBuf = readFileSync(photoPlaceholderPath);

// Replace slide 1 cover photo (image.png was 4.9MB house photo)
if (entries.has('ppt/media/image.png')) {
  console.log('Replacing Slide 1 cover photo with D&V Cover Placeholder...');
  entries.set('ppt/media/image.png', coverPlaceholderBuf);
}

// Replace interior and exterior property photos (image.jpeg to image10.jpeg)
for (let j = 1; j <= 10; j++) {
  const name = j === 1 ? 'ppt/media/image.jpeg' : `ppt/media/image${j}.jpeg`;
  if (entries.has(name)) {
    console.log(`Replacing ${name} with D&V Photo Placeholder...`);
    entries.set(name, photoPlaceholderBuf);
  }
}

// 3. Write modified presentation
const outputZip = writeZip(entries);
await Bun.write(outputPath, outputZip);
console.log(`Pristine Blank Template PPTX generated successfully: ${outputPath} (${outputZip.length} bytes)`);
