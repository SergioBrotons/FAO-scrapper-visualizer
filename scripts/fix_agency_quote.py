from pathlib import Path

target_file = Path("src/fao_transactions/visualization/map_builder.py")
content = target_file.read_text(encoding="utf-8")

old_str = "par ${r.agency_name || 'l\\'agence mandataire'}"
new_str = 'par ${r.agency_name || "l\'agence mandataire"}'

if old_str in content:
    content = content.replace(old_str, new_str, 1)
    target_file.write_text(content, encoding="utf-8")
    print("Fixed line 4945 in map_builder.py")
else:
    print("Not found directly, searching...")
    lines = content.splitlines(keepends=True)
    fixed = []
    c = 0
    for line in lines:
        if "l\\'agence mandataire" in line or "l'agence mandataire" in line:
            line = line.replace("'l\\'agence mandataire'", '"l\'agence mandataire"')
            line = line.replace("'l'agence mandataire'", '"l\'agence mandataire"')
            c += 1
        fixed.append(line)
    target_file.write_text("".join(fixed), encoding="utf-8")
    print(f"Fixed {c} lines in map_builder.py")
