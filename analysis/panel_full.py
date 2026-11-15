# -*- coding: utf-8 -*-
"""Build a full country-year panel (2014-2024) of SI2 export concentration.

Needed for two-way fixed effects, event study, and the HHI decomposition:
the earlier analysis only had 2014 and 2024 cross-sections.

Also computes the two margins of HHI:
    HHI = (1/N) * (1 + CV^2)
so ln(HHI) = -ln(N) + ln(1 + CV^2)
  - extensive margin: N   (how many markets served)
  - intensive margin: CV  (how unevenly sales spread across them)
"""
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(r"d:/HuaweiMoveData/Users/wlx/Desktop") / "\u6570\u636e\u9a71\u52a8" / "midterm_project"
RAW = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "cleaned"
INTEG = ROOT / "data" / "integrated"
CLEAN.mkdir(parents=True, exist_ok=True)

SRC = RAW / "OECD-WTO_BATIS_BPM6_bulk.csv"
YEARS = list(range(2014, 2025))
AGG_P = {"WL", "EU", "GEU", "ROW"}

acc = {}
rows = 0
t0 = time.time()
for i, ch in enumerate(pd.read_csv(
        SRC,
        usecols=["Reporter", "type_Reporter", "Partner", "type_Partner", "Flow",
                 "Item_code", "Year", "Balanced_value"],
        chunksize=1_500_000,
        dtype={"Item_code": "string", "Flow": "string", "Year": "Int64",
               "type_Reporter": "string", "type_Partner": "string"})):
    rows += len(ch)
    sub = ch[(ch["Item_code"] == "SI2") & (ch["Flow"] == "X")
             & (ch["type_Reporter"] == "c") & (ch["type_Partner"] == "c")
             & (ch["Year"].isin(YEARS)) & (~ch["Partner"].isin(AGG_P))]
    if not sub.empty:
        sub = sub[sub["Balanced_value"].notna()]
        for (rep, yr), g in sub.groupby(["Reporter", "Year"]):
            key = (str(rep), int(yr))
            d = acc.setdefault(key, {})
            for ptn, v in zip(g["Partner"], g["Balanced_value"]):
                d[str(ptn)] = d.get(str(ptn), 0.0) + float(v)
    if i % 4 == 0:
        print("  scanned %.1fM | cells %d | %.0fs"
              % (rows / 1e6, len(acc), time.time() - t0), flush=True)

print("total rows %d | reporter-year cells %d" % (rows, len(acc)))

recs = []
for (rep, yr), d in acc.items():
    v = np.array([x for x in d.values() if x > 0])
    if len(v) < 5:
        continue
    tot = v.sum()
    if tot <= 0:
        continue
    s = v / tot
    n = len(v)
    cv = float(np.std(s, ddof=0) / np.mean(s)) if np.mean(s) > 0 else np.nan
    hhi = float((s ** 2).sum() * 10000)
    srt = np.sort(s)[::-1]
    recs.append({
        "iso2": rep, "year": yr, "total_musd": float(tot),
        "n_partners": n, "cv": cv, "hhi": hhi,
        "cr1": float(srt[0] * 100), "cr5": float(srt[:5].sum() * 100),
        # shares for the decomposition (share of HHI explained by 1/N)
        "ln_hhi": np.log(hhi) if hhi > 0 else np.nan,
        "ln_n": np.log(n),
        "ln_cv_term": np.log(1 + cv ** 2) if cv == cv else np.nan,
    })

df = pd.DataFrame(recs)
df.to_csv(CLEAN / "batis_hhi_panel_2014_2024.csv", index=False, encoding="utf-8-sig")

print("\npanel: %d country-year rows | %d countries | %d-%d"
      % (len(df), df["iso2"].nunique(), df["year"].min(), df["year"].max()))
print("years covered: %s" % sorted(df["year"].unique()))

# verify the decomposition identity
chk = df.dropna(subset=["ln_hhi", "ln_n", "ln_cv_term"]).copy()
chk["recon"] = -chk["ln_n"] + chk["ln_cv_term"]
err = (chk["recon"] - chk["ln_hhi"]).abs()
print("\ndecomposition check: max abs error = %.6f (should be ~0)" % err.max())

print("\nper-year summary:")
print(df.groupby("year").agg(n=("iso2", "size"), hhi_med=("hhi", "median"),
                             partners_med=("n_partners", "median"),
                             cv_med=("cv", "median")).round(2).to_string())
