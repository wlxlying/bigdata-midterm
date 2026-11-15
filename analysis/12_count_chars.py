# -*- coding: utf-8 -*-
import json
from pathlib import Path

here = Path(__file__).resolve().parent

def load(name):
    raw = (here / name).read_bytes()
    for enc in ("utf-8", "utf-8-sig", "gb18030"):
        try:
            return json.loads(raw.decode(enc))
        except Exception:
            continue
    raise SystemExit(name)

blocks = []
for name in ("report_blocks_a.json", "report_blocks_b.json", "report_blocks_c.json"):
    blocks.extend(load(name))
prose = []
for b in blocks:
    if b["t"] == "p":
        prose.append(b["s"])
    elif b["t"] in ("h1", "h2"):
        prose.append(b["s"])
text = "".join(prose)
print("prose_chars", len(text))
print("paragraphs", sum(1 for b in blocks if b["t"] == "p"))
print("sample", text[200:260])
