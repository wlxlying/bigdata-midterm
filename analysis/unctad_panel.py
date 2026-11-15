# -*- coding: utf-8 -*-
"""Build the UNCTAD country-year panel (2014-2024) for the main analysis.

UNCTAD is the chosen caliber: reported values, 111 EBOPS categories, and the
partner-count sensitivity coefficient (0.38) closest to the theoretical value.

Outputs one row per exporter-year-category with HHI, CR5, N, CV and the
two-margin decomposition terms.
"""
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(r"d:/HuaweiMoveData/Users/wlx/Desktop") / "\u6570\u636e\u9a71\u52a8" / "midterm_project"
RAW = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "cleaned"
INTEG = ROOT / "data" / "integrated"
CLEAN.mkdir(parents=True, exist_ok=True)

SRC = RAW / "UNCTAD_TradeServCatByPartner.csv"
YEARS = list(range(2014, 2025))
CATS = ["SI2", "SI21", "SI22", "SI1", "SI3", "SH", "SH3", "SJ", "SG", "SC", "SD"]

M49 = {4: "AFG", 8: "ALB", 12: "DZA", 24: "AGO", 32: "ARG", 36: "AUS", 40: "AUT",
       48: "BHR", 50: "BGD", 56: "BEL", 76: "BRA", 100: "BGR", 124: "CAN",
       152: "CHL", 156: "CHN", 170: "COL", 188: "CRI", 191: "HRV", 196: "CYP",
       203: "CZE", 208: "DNK", 233: "EST", 246: "FIN", 250: "FRA", 276: "DEU",
       300: "GRC", 344: "HKG", 348: "HUN", 352: "ISL", 356: "IND", 360: "IDN",
       372: "IRL", 376: "ISR", 380: "ITA", 392: "JPN", 398: "KAZ", 410: "KOR",
       428: "LVA", 440: "LTU", 442: "LUX", 458: "MYS", 470: "MLT", 484: "MEX",
       499: "MNE", 528: "NLD", 554: "NZL", 578: "NOR", 616: "POL", 620: "PRT",
       642: "ROU", 643: "RUS", 688: "SRB", 702: "SGP", 703: "SVK", 705: "SVN",
       724: "ESP", 752: "SWE", 756: "CHE", 792: "TUR", 826: "GBR", 840: "USA",
       858: "URY", 70: "BIH", 807: "MKD", 784: "ARE", 788: "TUN", 818: "EGY",
       784: "ARE", 600: "PRY", 604: "PER", 608: "PHL", 634: "QAT", 682: "SAU",
       702: "SGP", 704: "VNM", 710: "ZAF", 364: "IRN", 368: "IRQ", 400: "JOR",
       422: "LBN", 504: "MAR", 566: "NGA", 586: "PAK", 643: "RUS", 804: "UKR"}

cols = pd.read_csv(SRC, nrows=0).columns.tolist()
vcol = [c for c in cols if c.startswith("Millions of US$")][0]
pos = {c: i for i, c in enumerate(cols)}
use = [pos["Year"], pos["Economy"], pos["Partner"], pos["Flow"], pos["Category"], pos[vcol]]

acc = {}
rows = 0
t0 = time.time()
for i, ch in enumerate(pd.read_csv(
        SRC, usecols=use, chunksize=1_200_000, header=0, low_memory=False,
        encoding_errors="replace",
        names=["Year", "Economy", "Partner", "Flow", "Category", "value"],
        skiprows=1)):
    rows += len(ch)
    ch["Year"] = pd.to_numeric(ch["Year"], errors="coerce")
    ch["Flow"] = pd.to_numeric(ch["Flow"], errors="coerce")
    ch["value"] = pd.to_numeric(ch["value"], errors="coerce")
    sub = ch[ch["Year"].isin(YEARS) & ch["Category"].isin(CATS) & (ch["Flow"] == 2)]
    sub = sub[sub["value"].notna() & (sub["value"] > 0)]
    for (eco, ptn, cat, yr), g in sub.groupby(
            ["Economy", "Partner", "Category", "Year"]):
        try:
            eco, ptn, yr = int(float(eco)), int(float(ptn)), int(float(yr))
        except (TypeError, ValueError):
            continue
        if ptn == 0:
            continue
        key = (eco, str(cat), yr)
        d = acc.setdefault(key, {})
        d[ptn] = d.get(ptn, 0.0) + float(g["value"].sum())
    if i % 3 == 0:
        print("  scanned %.1fM | cells %d | %.0fs"
              % (rows / 1e6, len(acc), time.time() - t0), flush=True)

print("total rows %d | cells %d" % (rows, len(acc)))

recs = []
for (eco, cat, yr), d in acc.items():
    v = np.array([x for x in d.values() if x > 0])
    if len(v) < 5:
        continue
    tot = v.sum()
    if tot <= 0:
        continue
    s = v / tot
    n = len(v)
    cv = float(np.std(s, ddof=0) / np.mean(s))
    hhi_share = float((s ** 2).sum())
    srt = np.sort(s)[::-1]
    recs.append({
        "iso3": M49.get(eco), "m49": eco, "year": yr, "cat": cat,
        "total_musd": float(tot), "n_partners": n, "cv": cv,
        "hhi": hhi_share * 10000,
        "cr1": float(srt[0] * 100), "cr5": float(srt[:5].sum() * 100),
        "ln_hhi": float(np.log(hhi_share)),
        "ln_n": float(np.log(n)),
        "ln_cv_term": float(np.log(1 + cv ** 2)),
    })

df = pd.DataFrame(recs)
df.to_csv(CLEAN / "unctad_panel_2014_2024.csv", index=False, encoding="utf-8-sig")

print("\npanel: %d rows | %d countries with ISO3 | %d-%d"
      % (len(df), df["iso3"].notna().sum(), df["year"].min(), df["year"].max()))
print("by category:")
print(df.groupby("cat").agg(rows=("iso3", "size"), countries=("iso3", "nunique"),
                            hhi_med=("hhi", "median"),
                            n_med=("n_partners", "median")).round(1).to_string())

chk = df[df["iso3"].notna()].dropna(subset=["ln_hhi", "ln_n", "ln_cv_term"])
err = ((-chk["ln_n"] + chk["ln_cv_term"]) - chk["ln_hhi"]).abs()
print("\ndecomposition identity: max error = %.10f" % err.max())

base = chk[chk["cat"] == "SI2"]
print("\nSI2 panel: %d rows, %d countries, %d years"
      % (len(base), base["iso3"].nunique(), base["year"].nunique()))
print(base.groupby("year").agg(n=("iso3", "size"), hhi_med=("hhi", "median"),
                               n_med=("n_partners", "median")).round(1).to_string())
