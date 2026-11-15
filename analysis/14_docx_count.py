# -*- coding: utf-8 -*-
from pathlib import Path
from docx import Document

path = Path(r"d:/HuaweiMoveData/Users/wlx/Desktop") / "\u6570\u636e\u9a71\u52a8" / (
    "\u4e2d\u671f\u5927\u4f5c\u4e1a_\u62a5\u544a_\u9b4f\u5170\u99a8241820216.docx"
)
doc = Document(str(path))
texts = []
for p in doc.paragraphs:
    if p.text.strip():
        texts.append(p.text.strip())
body = "".join(texts)
print("paragraphs", len(texts))
print("chars", len(body))
print("---head---")
print(texts[0])
print(texts[4][:80] if len(texts) > 4 else "")
print("---tail---")
print(texts[-2][:120])
print("has_1710", any("1,710" in t or "1710" in t for t in texts))
print("has_gdelt", any("GDELT" in t for t in texts))
print("pics", sum(1 for rel in doc.part.rels.values() if "image" in rel.reltype))
