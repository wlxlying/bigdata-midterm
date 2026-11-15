# -*- coding: utf-8 -*-
"""Step 2: extract top-5 exporters' bilateral SI2 panel from BaTiS and compute concentration."""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(r"d:/HuaweiMoveData/Users/wlx/Desktop") / "\u6570\u636e\u9a71\u52a8" / "midterm_project"
RAW = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "cleaned"
INTEG = ROOT / "data" / "integrated"
for d in (CLEAN, INTEG):
    d.mkdir(parents=True, exist_ok=True)

BATIS = RAW / "OECD-WTO_BATIS_BPM6_bulk.csv"
EXPORTERS = ["US", "IE", "GB", "DE", "IN"]
AGG = {"WL", "EU", "GEU", "ROW"}

frames = []
scanned = 0
for chunk in pd.read_csv(
        BATIS,
        usecols=["Reporter", "type_Reporter", "Partner", "type_Partner", "Flow",
                 "Item_code", "Year", "Reported_value", "Final_value_methodology",
                 "Balanced_value"],
        chunksize=2_000_000,
        dtype={"Item_code": "string", "Flow": "string", "Year": "Int64",
               "type_Reporter": "string", "type_Partner": "string"}):
    scanned += len(chunk)
    sub = chunk[(chunk["Item_code"] == "SI2")
                & (chunk["Flow"] == "X")
                & (chunk["type_Reporter"] == "c")
                & (chunk["type_Partner"] == "c")
                & (chunk["Reporter"].isin(EXPORTERS))
                & (~chunk["Partner"].isin(AGG))
                & (chunk["Year"].between(2014, 2024))]
    if not sub.empty:
        frames.append(sub)
    if scanned % 10_000_000 < 2_000_000:
        print("scanned", scanned // 1_000_000, "M rows | kept", sum(len(f) for f in frames), flush=True)

df = pd.concat(frames, ignore_index=True)
print("\ntotal kept rows:", len(df))
print("exporters:", sorted(df["Reporter"].unique()))
print("years:", int(df["Year"].min()), "-", int(df["Year"].max()))
print("partners:", df["Partner"].nunique())

df = df.rename(columns={"Reporter": "exporter", "Partner": "partner", "Year": "year",
                        "Balanced_value": "value", "Reported_value": "reported"})
df = df[df["value"].notna()]

clean = df[["exporter", "partner", "year", "value", "reported", "Final_value_methodology"]].copy()
clean["reported"] = clean["reported"].notna()
clean.to_parquet(CLEAN / "batis_si2_top5_bilateral.parquet", index=False)
clean.to_csv(CLEAN / "batis_si2_top5_bilateral.csv", index=False, encoding="utf-8-sig")
print("saved clean panel:", len(clean), "rows")


def concentration(g):
    v = g["value"].values
    tot = v.sum()
    if tot <= 0:
        return pd.Series({"total": 0, "n_partners": 0, "hhi": None, "cr1": None, "cr5": None})
    shares = v / tot
    srt = sorted(shares, reverse=True)
    return pd.Series({
        "total": tot,
        "n_partners": int((v > 0).sum()),
        "hhi": float((shares ** 2).sum() * 10000),
        "cr1": float(srt[0] * 100),
        "cr5": float(sum(srt[:5]) * 100),
    })


con = clean.groupby(["exporter", "year"]).apply(concentration, include_groups=False).reset_index()
con.to_csv(INTEG / "concentration_top5.csv", index=False, encoding="utf-8-sig")

print("\n=== HHI / CR by exporter-year ===")
pv = con.pivot(index="year", columns="exporter", values="hhi").round(0)
print(pv.to_string())

print("\n=== 2024 snapshot ===")
snap = con[con["year"] == 2024][["exporter", "total", "n_partners", "hhi", "cr1", "cr5"]]
print(snap.round(1).to_string(index=False))

print("\n=== HHI change 2014 -> 2024 ===")
for ex in EXPORTERS:
    s = con[con["exporter"] == ex].set_index("year")["hhi"]
    if 2014 in s.index and 2024 in s.index:
        print(f"  {ex}: 2014={s[2014]:.0f}  2024={s[2024]:.0f}  delta={s[2024]-s[2014]:+.0f}")

json.dump({"exporters": EXPORTERS, "years": [2014, 2024], "rows": len(clean)},
          open(INTEG / "panel_meta.json", "w", encoding="utf-8"), indent=2)
print("\nDONE")
