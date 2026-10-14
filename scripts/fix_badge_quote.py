from pathlib import Path

target_file = Path("src/fao_transactions/visualization/map_builder.py")
content = target_file.read_text(encoding="utf-8")

lines = content.splitlines(keepends=True)
fixed = []
count = 0
for line in lines:
    if "isSitgAllPoolsActive ?" in line:
        line = '      badge.textContent = isSitgAllPoolsActive ? "ACTIF (5\'173)" : "5\'173";\n'
        count += 1
    fixed.append(line)

target_file.write_text("".join(fixed), encoding="utf-8")
print(f"Fixed {count} lines in map_builder.py")
