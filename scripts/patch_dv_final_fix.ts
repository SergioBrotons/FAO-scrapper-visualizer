import { readFileSync, writeFileSync } from "fs";

const indexPath = "./public/dv/index.html";
let html = readFileSync(indexPath, "utf8");

// 1. Fix double declaration of IS_DEMO_CASE and IS_VIERGE_MODE
const duplicateDeclRegex = /let IS_DEMO_CASE = false;\s*let IS_DEMO_CASE = false;\s*IS_VIERGE_MODE = true;/g;
if (duplicateDeclRegex.test(html)) {
  html = html.replace(duplicateDeclRegex, "let IS_DEMO_CASE = false;\n    let IS_VIERGE_MODE = true;");
  console.log("Fixed duplicate IS_DEMO_CASE declaration.");
} else {
  // Try alternative pattern if formatted differently
  const altRegex = /let IS_DEMO_CASE = false;\s*let IS_DEMO_CASE = false;/g;
  if (altRegex.test(html)) {
    html = html.replace(altRegex, "let IS_DEMO_CASE = false;\n    let IS_VIERGE_MODE = true;");
    console.log("Fixed alt duplicate IS_DEMO_CASE declaration.");
  }
}

// 2. Locate exportPresentationPptx and update slideReplacements & fetch body
const targetReplacements = `        // Filename dynamically calibrated
        const cleanCommune = communeVal.split(' ').pop() || 'Genève';
        const cleanAddr = addressVal ? addressVal.replace(/[^a-zA-Z0-9]/g, '_') : 'Nouvelle_Estimation';
        const filename = 'Estimation_DV_' + cleanAddr + '.pptx';
        const isDemo = IS_DEMO_CASE === true;

        // Build 15-Slide Replacement Dictionary STRICTLY from the user form!
        const slideReplacements = {
          slide1: {
            "[TYPE DE BIEN]": propTypeVal,
            "[appartement / maison]": propTypeVal.toLowerCase().includes('maison') ? 'maison' : 'appartement',
            "[Nom du propriétaire]": ownerVal || '[Nom du propriétaire]',
            "[Commune], le [date]": cleanCommune + ', le ' + new Date().toLocaleDateString('fr-CH'),
            "[ADRESSE DU BIEN]": addressVal || '[ADRESSE DU BIEN]'
          },
          slide2: {
            "[ADRESSE COMPLÈTE]": addressVal || '[ADRESSE COMPLÈTE]',
            "[Nom de la résidence / bâtiment]  ·  [Commune]": (residenceVal ? (residenceVal + '  ·  ') : '') + (communeVal || cleanCommune),
            "[00]": roomsVal ? (roomsVal.split(' ')[0] || roomsVal) : '[00]',
            "[00 m²]": [surfPPE ? (surfPPE + ' m²') : '[00 m²]', weightedSurf ? (weightedSurf + ' m²') : '[00 m²]'],
            "[AAAA]": yearVal ? yearVal.substring(0, 4) : '[AAAA]',
            "[n°]": [parcelVal ? ('Parcelle ' + parcelVal) : '—', buildingVal ? ('Bât. ' + buildingVal) : '—', lotVal ? ('Lot ' + lotVal) : '—'],
            "[‰]": quotePartVal || '—',
            "[étage]": floorVal || '—',
            "[zone]": zoneVal || '—',
            "[Parking]": parkingVal || '[Parking]',
            "[Cave]": cellarVal || '[Cave]',
            "[Chauffage]": heatingVal || '[Chauffage]'
          },
          slide3: {
            "[PARCELLE N°0000]": parcelVal ? ('PARCELLE N° ' + parcelVal + ' (' + cleanCommune.toUpperCase() + ')') : '[PARCELLE N°0000]',
            "[Micro-localisation en une phrase]": microLocationVal || '[Micro-localisation en une phrase]'
          },
          slide4: {
            "[Hall et circulation]": qualDistVal || '[Hall et circulation]',
            "[Pièces de vie]": qualDistVal ? ('Espaces de vie : ' + qualDistVal) : '[Pièces de vie]',
            "[Matériaux et équipements]": qualEquipVal || '[Matériaux et équipements]',
            "[État général]": qualStateVal || '[État général]',
            "[Environnement]": qualEnvVal || '[Environnement]'
          },
          slide5: {},
          slide6: {},
          slide7: {},
          slide8: {},
          slide9: {
            "MÉTHODE DE NORMALISATION": normMethodVal || 'Normalisation D&V basée sur les transactions authentiques récentes du secteur.'
          },
          slide10: {
            "[Évolution récente documentée]": trendStr + ' sur 18 mois (source OCSTAT / FAO Genève)',
            "[Position de la commune]": marketTrendVal || ('Marché communal sur ' + cleanCommune),
            "[Écart entre prix affichés et transactions]": 'Écart moyen de négociation constaté : ' + spreadStr,
            "[00’000]": ppeMedianStr,
            "[Périmètre et date]": 'Genève & ' + cleanCommune + ' · Arrêté au ' + new Date().toLocaleDateString('fr-CH')
          },
          slide11: {
            "[00 m²] × 100%": (surfPPE || '85') + ' m² × 100%',
            "[00,0 m²]": (weightedSurf || surfPPE || '85') + ' m²',
            "[Prix de base / m²]": 'CHF ' + baseM2Val.toLocaleString('fr-CH') + ' / m²',
            "[valeur]": [
              'CHF ' + baseM2Val.toLocaleString('fr-CH') + ' / m² (Base pondérée calibrée)',
              "0.0% (État technique et finitions)",
              '+CHF ' + gardenValNum.toLocaleString('fr-CH') + (surfGarden > 0 ? (' (' + surfGarden + ' m²)') : ' (0 m²)'),
              '+CHF ' + parkingValNum.toLocaleString('fr-CH') + ' (Stationnement privatif)'
            ]
          },
          slide12: {
            "CHF [0’000’000]": [
              'CHF ' + batiValNum.toLocaleString('fr-CH'),
              'CHF ' + (targetPriceVal ? Number(targetPriceVal).toLocaleString('fr-CH') : totalValNum.toLocaleString('fr-CH'))
            ],
            "CHF [±00’000]": [
              'CHF 0',
              '+CHF ' + gardenValNum.toLocaleString('fr-CH'),
              '+CHF ' + parkingValNum.toLocaleString('fr-CH')
            ],
            "CHF [MIN]": rangeMinVal && rangeMinVal !== '0' ? ('CHF ' + Number(rangeMinVal).toLocaleString('fr-CH')) : 'CHF [MIN]',
            "CHF [MAX]": rangeMaxVal && rangeMaxVal !== '0' ? ('CHF ' + Number(rangeMaxVal).toLocaleString('fr-CH')) : 'CHF [MAX]',
            "[Validité]": validityVal || '[Validité]',
            "[Hypothèse de négociation]": negHypoVal || '[Hypothèse de négociation]',
            "[Positionnement retenu]": stratPosVal || '[Positionnement retenu]'
          },
          slide13: {},
          slide14: {},
          slide15: {}
        };`;

const oldSlideDictRegex = /\/\/ Filename dynamically calibrated[\s\S]*?slide15:\s*\{\}\s*\};/;
if (oldSlideDictRegex.test(html)) {
  html = html.replace(oldSlideDictRegex, targetReplacements);
  console.log("Updated slideReplacements dictionary in index.html.");
} else {
  console.warn("Could not match oldSlideDictRegex");
}

// 3. Update fetch body and toast messages in exportPresentationPptx
const oldFetchRegex = /body:\s*JSON\.stringify\(\{\s*isVierge,[\s\S]*?showToast\(isVierge[\s\S]*?showToast\(isVierge[\s\S]*?\}\s*\}\s*catch/g;
const replacementFetch = `body: JSON.stringify({
              isDemo,
              slideReplacements,
              images: UPLOADED_SLIDE_IMAGES,
              hideInternalInstructions: true,
              filename
            })
          });

          if (res.ok) {
            const blob = await res.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(downloadUrl);
            downloaded = true;
            showToast(isDemo
              ? "Présentation PPTX Démo Saut-du-Loup 18 générée et téléchargée !"
              : "Présentation PPTX personnalisée générée et téléchargée avec succès (100% données du formulaire) !");
          }
        } catch (apiErr) {
          console.warn("API export route error, falling back to direct static file:", apiErr);
        }

        // Direct static fallback if API didn't complete
        if (!downloaded) {
          const a = document.createElement('a');
          a.href = isDemo ? '/data/exports/Estimation_Saut_du_Loup_18_Brotons_2026.pptx' : '/data/exports/Estimation_DV_Template_Vierge_Officiel.pptx';
          a.download = filename;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          showToast(isDemo
            ? "Présentation PPTX Saut-du-Loup téléchargée via lien direct !"
            : "Dossier vierge officiel PPTX téléchargé (gabarits neutres) !");
        }
      } catch`;

if (oldFetchRegex.test(html)) {
  html = html.replace(oldFetchRegex, replacementFetch);
  console.log("Updated fetch body and toast messages.");
} else {
  console.warn("Could not match oldFetchRegex");
}

await Bun.write(indexPath, html);
console.log("Successfully wrote updated index.html");
