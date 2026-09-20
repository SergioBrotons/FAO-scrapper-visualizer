# Geneva Property Transactions Pipeline

Automated pipeline for collecting and enriching official Geneva real-estate transaction notices from FAO (Feuille d'avis officielle de la République et canton de Genève) and linking them with SITG (Système d'Information du Territoire à Genève) cadastral geodata.

## Features
- **Headed Playwright Automation**: Respectful navigation with persistent browser session and manual CAPTCHA solving.
- **Deterministic PDF Parser**: Extracts transaction records, parcels, parties, monetary values, and surfaces.
- **SITG Cadastral Enrichment**: Links FAO notices directly to official Swiss cadastral parcels (`CAD_PARCELLE_MENSU`), historical parcels, DDPs, PPE units, buildings, and addresses.
- **Geographic Exports & Map**: Outputs to CSV, Excel, GeoJSON, and GeoPackage with EPSG:2056 and EPSG:4326 geometries.

## Usage
```powershell
# Discover FAO structure & test access
python -m fao_transactions discover
```
