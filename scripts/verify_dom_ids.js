import { readFileSync } from 'fs';
const html = readFileSync('public/dv/index.html', 'utf8');

const requiredIds = [
  'wizAddress', 'addressSuggestionsDropdown', 'addressLoadingSpinner',
  'cadastreLockBadge', 'cadastreLockText', 'wizCommune', 'wizParcel',
  'wizBuilding', 'wizLotPPE', 'wizZone', 'wizBuildingYear', 'wizSurfPPE',
  'wizWeightedSurf', 'wizRooms', 'wizHeating', 'btnAutoFillSystem', 'btnSitgMap'
];

let allOk = true;
for (const id of requiredIds) {
  if (!html.includes(`id="${id}"`)) {
    console.error('MISSING ID:', id);
    allOk = false;
  } else {
    console.log(`✓ ID '${id}' is present`);
  }
}
if (allOk) {
  console.log('\nAll 17 critical DOM elements verified in public/dv/index.html!');
}
