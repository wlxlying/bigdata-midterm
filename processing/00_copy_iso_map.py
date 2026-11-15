# -*- coding: utf-8 -*-
"""Backfill the ISO3->ISO2 map into data/integrated so downstream scripts find it."""
import shutil
from pathlib import Path

ROOT = Path(r"d:/HuaweiMoveData/Users/wlx/Desktop") / "\u6570\u636e\u9a71\u52a8" / "midterm_project"
src = ROOT / "data" / "cleaned"
dst = ROOT / "data" / "integrated"
tmpl = Path(r"d:/HuaweiMoveData/Users/wlx/Desktop") / "\u6570\u636e\u9a71\u52a8" / "\u6570\u636e\u4e0e\u6570\u636e\u8bf4\u660e" / "\u6dfb\u52a0_\u6570\u5b57\u8d38\u6613\u6d41\u91cf" / "_iso3_to_iso2.csv"

if tmpl.exists():
    shutil.copy2(tmpl, dst / "_iso3_to_iso2.csv")
    print("copied mapping ->", dst / "_iso3_to_iso2.csv")
else:
    print("mapping source missing:", tmpl)
