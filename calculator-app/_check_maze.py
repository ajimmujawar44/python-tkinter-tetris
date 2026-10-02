from pathlib import Path
import re

text = Path("pacman.py").read_text(encoding="utf-8")
block = text.split("MAZE = [", 1)[1].split("]", 1)[0]
rows = re.findall(r'"([^"]*)"', block)
for row in rows:
    print(len(row), row)
print("unique", set(map(len, rows)))
