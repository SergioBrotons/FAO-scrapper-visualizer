from pathlib import Path

file_path = Path("src/fao_transactions/visualization/map_builder.py")
content = file_path.read_text(encoding="utf-8")

old_snippet = """        '<div style="font-size:11px; color:#94a3b8; line-height:1.5; margin-bottom:10px; background:rgba(0,229,255,0.06); padding:6px 8px; border-radius:4px; border:1px solid rgba(0,229,255,0.15);">' +
          '<div>&bull; Plan d\\'eau : <strong style="color:#38bdf8;">' + surf + ' m²</strong></div>' +
          '<div>&bull; Périmètre : <strong style="color:#e2e8f0;">' + perim + ' m</strong></div>' +
          '<div>&bull; Réf. Registre : <strong style="color:#cbd5e1;">SITG CAD_PISCINE #' + id + '</strong></div>' +
        '</div>' +
        '<div style="display:flex; gap:6px;">' +
          '<button type="button" onclick="openStreetViewModal(' + lat + ', ' + lon + ', \\'Piscine SITG #' + id + ' - ' + com + '\\', null, null, null, \\'sat\\')" style="flex:1; padding:5px 6px; font-size:10px; background:#0284c7; color:#fff; border:none; border-radius:3px; cursor:pointer; font-weight:700;">Satellite HD</button>' +
          '<button type="button" onclick="openStreetViewModal(' + lat + ', ' + lon + ', \\'Piscine SITG #' + id + ' - ' + com + '\\', null, null, null, \\'sitg\\')" style="flex:1; padding:5px 6px; font-size:10px; background:#0f766e; color:#fff; border:none; border-radius:3px; cursor:pointer; font-weight:700;">Cadastre SITG</button>' +
          '<button type="button" onclick="openStreetViewModal(' + lat + ', ' + lon + ', \\'Piscine SITG #' + id + ' - ' + com + '\\', null, null, null, \\'pano\\')" style="flex:1; padding:5px 6px; font-size:10px; background:#334155; color:#fff; border:none; border-radius:3px; cursor:pointer; font-weight:700;">360°</button>' +
        '</div>' +"""

new_snippet = """        '<div style="font-size:11px; color:#94a3b8; line-height:1.5; margin-bottom:10px; background:rgba(0,229,255,0.06); padding:6px 8px; border-radius:4px; border:1px solid rgba(0,229,255,0.15);">' +
          '<div>&bull; Plan d’eau : <strong style="color:#38bdf8;">' + surf + ' m²</strong></div>' +
          '<div>&bull; Périmètre : <strong style="color:#e2e8f0;">' + perim + ' m</strong></div>' +
          '<div>&bull; Réf. Registre : <strong style="color:#cbd5e1;">SITG CAD_PISCINE #' + id + '</strong></div>' +
        '</div>' +
        '<div style="display:flex; gap:6px;">' +
          '<button type="button" onclick="openStreetViewModal(' + lat + ', ' + lon + ', &quot;Piscine SITG #' + id + ' - ' + com + '&quot;, null, null, null, &quot;sat&quot;)" style="flex:1; padding:5px 6px; font-size:10px; background:#0284c7; color:#fff; border:none; border-radius:3px; cursor:pointer; font-weight:700;">Satellite HD</button>' +
          '<button type="button" onclick="openStreetViewModal(' + lat + ', ' + lon + ', &quot;Piscine SITG #' + id + ' - ' + com + '&quot;, null, null, null, &quot;sitg&quot;)" style="flex:1; padding:5px 6px; font-size:10px; background:#0f766e; color:#fff; border:none; border-radius:3px; cursor:pointer; font-weight:700;">Cadastre SITG</button>' +
          '<button type="button" onclick="openStreetViewModal(' + lat + ', ' + lon + ', &quot;Piscine SITG #' + id + ' - ' + com + '&quot;, null, null, null, &quot;pano&quot;)" style="flex:1; padding:5px 6px; font-size:10px; background:#334155; color:#fff; border:none; border-radius:3px; cursor:pointer; font-weight:700;">360°</button>' +
        '</div>' +"""

if old_snippet in content:
    content = content.replace(old_snippet, new_snippet, 1)
    file_path.write_text(content, encoding="utf-8")
    print("Fixed syntax in map_builder.py")
else:
    print("Old snippet not found directly, trying normalized...")
    # Try normalized CRLF
    old_crlf = old_snippet.replace("\n", "\r\n")
    new_crlf = new_snippet.replace("\n", "\r\n")
    if old_crlf in content:
        content = content.replace(old_crlf, new_crlf, 1)
        file_path.write_text(content, encoding="utf-8")
        print("Fixed CRLF syntax in map_builder.py")
    else:
        print("Failed to find snippet")
