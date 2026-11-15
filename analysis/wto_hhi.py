# -*- coding: utf-8 -*-
"""Bring WTO annual services into the analysis as a third independent source.

WTO annual is the *unbalanced* series that BaTiS is built from. Comparing the two
isolates how much of the concentration measure is an artefact of BaTiS balancing
rather than observed trade.

Also computes HHI under three partner-set definitions, turning the earlier
caliber discrepancy into a formal documented comparison.
"""
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(r"d:/HuaweiMoveData/Users/wlx/Desktop") / "\u6570\u636e\u9a71\u52a8" / "midterm_project"
RAW = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "cleaned"
CLEAN.mkdir(parents=True, exist_ok=True)

SRC = RAW / "WTO_services_annual.csv"
print("file MB: %.1f" % (SRC.stat().st_size / 1048576))

TARGET_YEAR = 2024
TARGETS = ["SI2", "SI1", "SI3", "SH", "SJ", "SG", "SC", "SD"]

acc = {}
rows = 0
t0 = time.time()
for i, ch in enumerate(pd.read_csv(
        SRC,
        usecols=["ReporterISO3A", "PartnerISO3A", "ProductCode", "Year", "Value"],
        chunksize=1_500_000, low_memory=False, encoding_errors="replace")):
    rows += len(ch)
    ch["Year"] = pd.to_numeric(ch["Year"], errors="coerce")
    sub = ch[(ch["Year"] == TARGET_YEAR) & (ch["ProductCode"].isin(TARGETS))].copy()
    if sub.empty:
        if i % 3 == 0:
            print("  scanned %.1fM | %.0fs" % (rows / 1e6, time.time() - t0), flush=True)
        continue
    sub["Value"] = pd.to_numeric(sub["Value"], errors="coerce")
    sub = sub[sub["Value"].notna() & (sub["Value"] > 0)]
    for (rep, ptn, prod), g in sub.groupby(["ReporterISO3A", "PartnerISO3A", "ProductCode"]):
        if pd.isna(rep) or pd.isna(ptn):
            continue
        rep, ptn = str(rep), str(ptn)
        if ptn in ("WLD", "W", "-", ""):
            continue
        key = (rep, str(prod))
        d = acc.setdefault(key, {})
        d[ptn] = d.get(ptn, 0.0) + float(g["Value"].sum())
    if i % 3 == 0:
        print("  scanned %.1fM | %d cells | %.0fs"
              % (rows / 1e6, len(acc), time.time() - t0), flush=True)

print("total rows %d | reporter-product cells %d" % (rows, len(acc)))


def hhi(v):
    s = v / v.sum()
    return float((s ** 2).sum() * 10000)


recs = []
for (rep, prod), d in acc.items():
    vals = np.array([x for x in d.values() if x > 0])
    if len(vals) < 3:
        continue
    tot = vals.sum()
    keep = vals[vals / tot >= 0.001]
    top20 = np.sort(vals)[::-1][:20]
    recs.append({
        "iso3": rep, "cat": prod, "year": TARGET_YEAR,
        "total_musd": float(tot), "n_partners": int(len(vals)),
        "hhi_all": hhi(vals),
        "hhi_sig": hhi(keep) if len(keep) >= 3 else np.nan,
        "hhi_top20": hhi(top20) if len(top20) >= 5 else np.nan,
    })

d = pd.DataFrame(recs)
d.to_csv(CLEAN / "wto_hhi_2024.csv", index=False, encoding="utf-8-sig")
print("\ncells computed: %d" % len(d))
print("\nby category:")
print(d.groupby("cat").agg(n=("iso3", "size"), hhi_all=("hhi_all", "median"),
                           hhi_sig=("hhi_sig", "median"),
                           hhi_top20=("hhi_top20", "median"),
                           partners=("n_partners", "median")).round(1).to_string())

print("\nSI2 top 15, three HHI definitions:")
print(d[d["cat"] == "SI2"].nlargest(15, "total_musd")[
    ["iso3", "total_musd", "n_partners", "hhi_all", "hhi_sig", "hhi_top20"]]
      .round(1).to_string(index=False))
