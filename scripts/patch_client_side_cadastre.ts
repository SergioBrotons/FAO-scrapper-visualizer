import { readFileSync } from "fs";

const indexPath = "./public/dv/index.html";
let html = readFileSync(indexPath, "utf8");

// 1. Update autocomplete input handler with client-side federal fallback
const targetAutocompleteBlock = `          // 1. Try server API
          try {
            const res = await fetch('/api/dv/address-autocomplete?q=' + encodeURIComponent(q));
            if (res.ok) {
              const json = await res.json();
              results = json.results || [];
            }
          } catch (err) {}

          // 2. Direct Swiss Federal RegBL / SITG GeoAdmin Client-Side API
          if (!results || results.length === 0) {
            try {
              const fedUrl = 'https://api3.geo.admin.ch/rest/services/api/SearchServer?type=locations&origins=address&searchText=' + encodeURIComponent(q);
              const fedRes = await fetch(fedUrl);
              if (fedRes.ok) {
                const fedJson = await fedRes.json();
                const fedItems = (fedJson.results || []).filter(r => {
                  const detail = (r.attrs?.detail || '').toLowerCase();
                  const label = (r.attrs?.label || '').toLowerCase();
                  return detail.includes(' ch ge') || detail.includes(' ge') || /12\\d\\d/.test(label);
                });

                if (fedItems.length > 0) {
                  const enriched = await Promise.all(fedItems.slice(0, 5).map(async f => {
                    const featId = f.attrs?.featureId;
                    if (!featId) return null;
                    try {
                      const dRes = await fetch('https://api3.geo.admin.ch/rest/services/ech/MapServer/ch.bfs.gebaeude_wohnungs_register/' + featId);
                      if (!dRes.ok) return null;
                      const dJson = await dRes.json();
                      const a = dJson.feature?.attributes || {};
                      
                      const heatingCode = a.gwaerzh1;
                      let heating = "Chauffage central standard";
                      if (heatingCode === 7520 || heatingCode === 7620) heating = "Chauffage à distance (CAD Genève / SIG)";
                      else if (heatingCode === 7530 || heatingCode === 7410) heating = "Pompe à chaleur (PAC)";
                      else if (heatingCode === 7511) heating = "Gaz naturel";
                      else if (heatingCode === 7501) heating = "Mazout (Fioul)";
                      else if (heatingCode === 7540) heating = "Solaire thermique";

                      const dwellingsCount = a.ganzwhg || 1;
                      const surfaces = Array.isArray(a.warea) ? a.warea.filter(Boolean) : [];
                      const roomsList = Array.isArray(a.wazim) ? a.wazim.filter(Boolean) : [];
                      const primarySurface = surfaces.length > 0 ? surfaces[0] : (a.garea ? Math.round(a.garea / Math.max(1, dwellingsCount)) : 85);
                      const primaryRooms = roomsList.length > 0 ? roomsList[0] : (primarySurface > 110 ? 5 : primarySurface > 75 ? 4 : 3);

                      const cleanAddr = a.strname_deinr || (f.attrs?.label || '').replace(/<[^>]+>/g, ' ').replace(/\\s+/g, ' ').trim();
                      const commune = a.ggdename || a.dplzname || "Genève";

                      return {
                        id: 'regbl_' + featId,
                        featureId: featId,
                        address: cleanAddr,
                        commune: (a.dplz4 ? (a.dplz4 + ' ') : '') + commune,
                        parcel_number: a.lparz || '—',
                        building_number: a.gebnr || '—',
                        building_year: a.gbauj || a.wbauj?.[0] || null,
                        rooms: primaryRooms,
                        surface_m2: primarySurface,
                        egrid: a.egrid || null,
                        egid: a.egid || null,
                        heating_system: heating,
                        zone: "Zone 5 (Villas et résidences de standing)",
                        property_type: dwellingsCount > 1 ? "APPARTEMENT PPE" : "VILLA / MAISON INDIVIDUELLE",
                        source: "RegBL / SITG Officiel"
                      };
                    } catch (e) {
                      return null;
                    }
                  }));
                  results = enriched.filter(Boolean);
                }
              }
            } catch (fedErr) {
              console.warn("Client-side federal lookup error:", fedErr);
            }
          }

          // 3. Fallback to local index
          if (!results || results.length === 0) {
            if (GENEVA_CADASTRE_INDEX.length > 0) {
              const lowerQ = q.toLowerCase();
              results = GENEVA_CADASTRE_INDEX.filter(item => 
                (item.address && item.address.toLowerCase().includes(lowerQ)) ||
                (item.parcel_number && item.parcel_number.toLowerCase().includes(lowerQ)) ||
                (item.commune && item.commune.toLowerCase().includes(lowerQ))
              ).slice(0, 15);
            }
          }`;

const oldAutocompleteRegex = /\/\/ 1\. Try server API[\s\S]*?\/\/ 2\. Fallback to local index[\s\S]*?\}\s*\}\s*\}/;
if (oldAutocompleteRegex.test(html)) {
  html = html.replace(oldAutocompleteRegex, targetAutocompleteBlock);
  console.log("Updated autocomplete with client-side federal search.");
} else {
  console.warn("Could not find oldAutocompleteRegex");
}

// 2. Update autoFillFromSystem with client-side federal fallback
const targetAutoFillBlock = `        if (!matchedProp) {
          try {
            const fedRes = await fetch('https://api3.geo.admin.ch/rest/services/api/SearchServer?type=locations&origins=address&searchText=' + encodeURIComponent(addr));
            if (fedRes.ok) {
              const fedJson = await fedRes.json();
              const top = (fedJson.results || [])[0];
              const featId = top?.attrs?.featureId;
              if (featId) {
                const dRes = await fetch('https://api3.geo.admin.ch/rest/services/ech/MapServer/ch.bfs.gebaeude_wohnungs_register/' + featId);
                if (dRes.ok) {
                  const dJson = await dRes.json();
                  const a = dJson.feature?.attributes || {};
                  const heatingCode = a.gwaerzh1;
                  let heating = "Chauffage central standard";
                  if (heatingCode === 7520 || heatingCode === 7620) heating = "Chauffage à distance (CAD Genève / SIG)";
                  else if (heatingCode === 7530 || heatingCode === 7410) heating = "Pompe à chaleur (PAC)";
                  else if (heatingCode === 7511) heating = "Gaz naturel";
                  else if (heatingCode === 7501) heating = "Mazout (Fioul)";
                  else if (heatingCode === 7540) heating = "Solaire thermique";

                  const dwellingsCount = a.ganzwhg || 1;
                  const surfaces = Array.isArray(a.warea) ? a.warea.filter(Boolean) : [];
                  const roomsList = Array.isArray(a.wazim) ? a.wazim.filter(Boolean) : [];
                  const primarySurface = surfaces.length > 0 ? surfaces[0] : (a.garea ? Math.round(a.garea / Math.max(1, dwellingsCount)) : 85);
                  const primaryRooms = roomsList.length > 0 ? roomsList[0] : (primarySurface > 110 ? 5 : primarySurface > 75 ? 4 : 3);

                  matchedProp = {
                    id: 'regbl_' + featId,
                    featureId: featId,
                    address: a.strname_deinr || (top.attrs?.label || '').replace(/<[^>]+>/g, ' ').replace(/\\s+/g, ' ').trim(),
                    commune: (a.dplz4 ? (a.dplz4 + ' ') : '') + (a.ggdename || a.dplzname || "Genève"),
                    parcel_number: a.lparz || '—',
                    building_number: a.gebnr || '—',
                    building_year: a.gbauj || a.wbauj?.[0] || null,
                    rooms: primaryRooms,
                    surface_m2: primarySurface,
                    egrid: a.egrid || null,
                    egid: a.egid || null,
                    heating_system: heating,
                    zone: "Zone 5 (Villas et résidences de standing)",
                    property_type: dwellingsCount > 1 ? "APPARTEMENT PPE" : "VILLA / MAISON INDIVIDUELLE",
                    source: "RegBL / SITG Officiel"
                  };
                }
              }
            }
          } catch (fedErr) {
            console.warn("Client-side federal lookup error:", fedErr);
          }
        }

        if (!matchedProp && GENEVA_CADASTRE_INDEX.length > 0) {`;

const oldAutoFillRegex = /if \(!matchedProp && GENEVA_CADASTRE_INDEX\.length > 0\) \{/;
if (oldAutoFillRegex.test(html)) {
  html = html.replace(oldAutoFillRegex, targetAutoFillBlock);
  console.log("Updated autoFillFromSystem with client-side federal fallback.");
} else {
  console.warn("Could not find oldAutoFillRegex");
}

await Bun.write(indexPath, html);
console.log("Successfully wrote updated index.html with client-side federal resolvers!");
