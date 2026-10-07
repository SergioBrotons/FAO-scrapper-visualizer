import sys
import re

file_path = "public/dv/index.html"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

print("File size before:", len(content))

# 1. Update CSS container max-width to 1420px for spacious layout
content = content.replace("max-width: 1240px;", "max-width: 1420px;")

# Check where viewHub starts and where it ends
hub_idx = content.find('<div id="viewHub">')
val_idx = content.find('<div id="viewValue"')

print("hub_idx:", hub_idx, "val_idx:", val_idx)
