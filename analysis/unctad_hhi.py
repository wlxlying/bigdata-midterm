# -*- coding: utf-8 -*-
"""Compute HHI from UNCTAD bilateral services, locating the value column by position.

The value header contains a non-breaking space, so name-based selection is fragile;
we resolve the column index once and use usecols with integers.
"""
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(r"d:/HuaweiMoveData/Users/wlx/Desktop") / "\u6570\u636e\u9a71\u52a8" / "midterm_project"
RAW = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "cleaned"
CLEAN.mkdir(parents=True, exist_ok=True)
SRC = RAW / "UNCTAD_TradeServCatByPartner.csv"

CATS = ["SI2", "SI21", "SI22", "SI1", "SI3", "SH", "SH3", "SJ", "SG", "SC", "SD"]
YEARS = [2014, 2024]

cols = pd.read_csv(SRC, nrows=0).columns.tolist()
pos = {c: i for i, c in enumerate(cols)}
vcol = [c for c in cols if c.startswith("Millions of US$")][0]
print("value column:", repr(vcol))

use = [pos["Year"], pos["Economy"], pos["Partner"], pos["Flow"], pos["Category"], pos[vcol]]
print("usecols indices:", use)

acc = {}
rows = 0
t0 = time.time()
for i, ch in enumerate(pd.read_csv(SRC, usecols=use, chunksize=1_200_000,
                                   header=0, low_memory=False,
                                   encoding_errors="replace",
                                   names=["Year", "Economy", "Partner", "Flow", "Category", "value"],
                                   skiprows=1)):
    rows += len(ch)
    ch["Year"] = pd.to_numeric(ch["Year"], errors="coerce")
    ch["Flow"] = pd.to_numeric(ch["Flow"], errors="coerce")
    ch["value"] = pd.to_numeric(ch["value"], errors="coerce")
    sub = ch[ch["Year"].isin(YEARS) & ch["Category"].isin(CATS) & (ch["Flow"] == 2)]
    sub = sub[sub["value"].notna() & (sub["value"] > 0)]
    for (eco, cat, yr), g in sub.groupby(["Economy", "Category", "Year"]):
        key = (int(eco), str(cat), int(yr))
        d = acc.setdefault(key, {})
        for ptn, v in zip(g["Partner"], g["value"]):
            try:
                ptn = int(float(ptn))
            except (TypeError, ValueError):
                continue
            if ptn == 0:
                continue
            d[ptn] = d.get(ptn, 0.0) + float(v)
    if i % 3 == 0:
        print("  scanned %.1fM rows | %d cells | %.0fs"
              % (rows / 1e6, len(acc), time.time() - t0), flush=True)

print("total rows: %d | cells: %d" % (rows, len(acc)))

recs = []
for (eco, cat, yr), d in acc.items():
    vals = np.array([v for v in d.values() if v > 0])
    tot = vals.sum()
    if tot <= 0 or len(vals) < 5:
        continue
    s = vals / tot
    srt = np.sort(s)[::-1]
    recs.append({"m49": eco, "cat": cat, "year": yr,
                 "total_musd": float(tot), "n_partners": int(len(vals)),
                 "hhi": float((s ** 2).sum() * 10000),
                 "cr1": float(srt[0] * 100),
                 "cr5": float(srt[:5].sum() * 100)})

out = pd.DataFrame(recs)
out.to_csv(CLEAN / "unctad_hhi_by_category.csv", index=False, encoding="utf-8-sig")
print("\nHHI computed for %d economy-category-year cells" % len(out))

snap = out[out["year"] == 2024].groupby("cat").agg(
    n=("m49", "size"), hhi_mean=("hhi", "mean"), hhi_med=("hhi", "median"),
    tot_med=("total_musd", "median")).round(1)
print("\n2024 by category:")
print(snap.to_string())

print("\nSI2 top 15 (2024):")
print(out[(out["cat"] == "SI2") & (out["year"] == 2024)]
      .nlargest(15, "total_musd")[["m49", "total_musd", "hhi", "n_partners"]]
      .round(1).to_string(index=False))
