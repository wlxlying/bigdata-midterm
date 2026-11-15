# -*- coding: utf-8 -*-
from pathlib import Path
from docx import Document

path = Path(r"d:/HuaweiMoveData/Users/wlx/Desktop") / "\u6570\u636e\u9a71\u52a8" / (
    "\u4e2d\u671f\u5927\u4f5c\u4e1a_\u62a5\u544a_\u9b4f\u5170\u99a8241820216.docx"
)
doc = Document(str(path))
n = 0
for p in doc.paragraphs:
    if p.style.name.startswith("toc") or "\u6458\u8981" in p.text or p.style.name.lower().startswith("toc"):
        print(p.style.name, p.text[:80])
        n += 1
print("shown", n)
# also print paragraphs 8-20
for i, p in enumerate(doc.paragraphs[6:22], start=7):
    print(i, p.style.name, p.text[:70])
