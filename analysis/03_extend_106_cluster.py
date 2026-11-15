# -*- coding: utf-8 -*-
"""Step 3: extend concentration to all economies with STRI, merge policy, cluster."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

ROOT = Path(r"d:/HuaweiMoveData/Users/wlx/Desktop") / "\u6570\u636e\u9a71\u52a8" / "midterm_project"
RAW = ROOT / "data" / "raw"
INTEG = ROOT / "data" / "integrated"

# ---------- 1. STRI ----------
stri = pd.read_csv(RAW / "oecd_digital_stri.csv")
s24 = stri[(stri["MEASURE"] == "STRI") & (stri["TIME_PERIOD"] == 2024)][["REF_AREA", "OBS_VALUE"]]
s24 = s24.rename(columns={"REF_AREA": "iso3", "OBS_VALUE": "stri2024"})
s14 = stri[(stri["MEASURE"] == "STRI") & (stri["TIME_PERIOD"] == 2014)][["REF_AREA", "OBS_VALUE"]]
s14 = s14.rename(columns={"REF_AREA": "iso3", "OBS_VALUE": "stri2014"})
stri_w = s24.merge(s14, on="iso3", how="outer")
stri_w["stri_change"] = stri_w["stri2024"] - stri_w["stri2014"]
print("STRI countries:", len(stri_w))

# ---------- 2. ISO3 -> ISO2 ----------
iso = pd.read_csv(INTEG / "_iso3_to_iso2.csv" if (INTEG / "_iso3_to_iso2.csv").exists()
                  else ROOT / "data" / "cleaned" / "_iso3_to_iso2.csv", dtype=str)
mapping = dict(zip(iso["iso3"], iso["iso2"]))
mapping.update({"CIV": "CI", "VNM": "VN", "XKV": "XK"})
stri_w["iso2"] = stri_w["iso3"].map(mapping)

# ---------- 3. Concentration for ALL reporters, 2024 & 2014 ----------
BATIS = RAW / "OECD-WTO_BATIS_BPM6_bulk.csv"
AGG = {"WL", "EU", "GEU", "ROW"}
frames = []
for chunk in pd.read_csv(
        BATIS,
        usecols=["Reporter", "type_Reporter", "Partner", "type_Partner", "Flow",
                 "Item_code", "Year", "Balanced_value"],
        chunksize=2_000_000,
        dtype={"Item_code": "string", "Flow": "string", "Year": "Int64",
               "type_Reporter": "string", "type_Partner": "string"}):
    sub = chunk[(chunk["Item_code"] == "SI2")
                & (chunk["Flow"] == "X")
                & (chunk["type_Reporter"] == "c")
                & (chunk["type_Partner"] == "c")
                & (chunk["Year"].isin([2014, 2024]))
                & (~chunk["Partner"].isin(AGG))]
    if not sub.empty:
        frames.append(sub)

df = pd.concat(frames, ignore_index=True)
df = df.rename(columns={"Reporter": "iso2", "Partner": "partner", "Year": "year",
                        "Balanced_value": "value"})
df = df[df["value"].notna()]
print("bilateral rows:", len(df), "reporters:", df["iso2"].nunique())


def conc(g):
    v = g["value"].values
    tot = v.sum()
    if tot <= 0:
        return pd.Series({"total": 0.0, "n_partners": 0, "hhi": np.nan, "cr5": np.nan})
    s = v / tot
    srt = np.sort(s)[::-1]
    return pd.Series({
        "total": float(tot),
        "n_partners": int((v > 0).sum()),
        "hhi": float((s ** 2).sum() * 10000),
        "cr5": float(srt[:5].sum() * 100),
    })


con = df.groupby(["iso2", "year"]).apply(conc, include_groups=False).reset_index()
wide = con.pivot(index="iso2", columns="year", values=["hhi", "total", "n_partners", "cr5"])
wide.columns = [f"{a}{str(b)[-2:]}" for a, b in wide.columns]
wide = wide.reset_index()
for c in ["hhi14", "hhi24", "total24", "n_partners24", "cr524"]:
    if c not in wide.columns:
        wide[c] = np.nan
wide["hhi_delta"] = wide["hhi24"] - wide["hhi14"]

# ---------- 4. merge ----------
m = wide.merge(stri_w[["iso2", "stri2024", "stri2014", "stri_change"]], on="iso2", how="inner")
m = m.dropna(subset=["hhi24", "stri2024"])
m = m[m["total24"] > 0]
print("merged with STRI:", len(m))

# ---------- 5. cluster ----------
feat = ["hhi24", "stri2024", "cr524"]
X = m[feat].copy()
X["hhi24"] = np.log1p(X["hhi24"])
X = StandardScaler().fit_transform(X)
km = KMeans(n_clusters=4, random_state=42, n_init=20)
m["cluster"] = km.fit_predict(X)

label_map = {}
for c in sorted(m["cluster"].unique()):
    sub = m[m["cluster"] == c]
    hs, ss = sub["hhi24"].mean(), sub["stri2024"].mean()
    if hs > m["hhi24"].median() and ss > m["stri2024"].median():
        label_map[c] = "A \u9ad8\u9650\u5236-\u9ad8\u96c6\u4e2d"
    elif hs > m["hhi24"].median():
        label_map[c] = "B \u4f4e\u9650\u5236-\u9ad8\u96c6\u4e2d"
    elif ss > m["stri2024"].median():
        label_map[c] = "C \u9ad8\u9650\u5236-\u4f4e\u96c6\u4e2d"
    else:
        label_map[c] = "D \u4f4e\u9650\u5236-\u4f4e\u96c6\u4e2d"
m["cluster_label"] = m["cluster"].map(label_map)

print("\n=== cluster profile ===")
prof = m.groupby("cluster_label").agg(
    n=("iso2", "size"),
    hhi_mean=("hhi24", "mean"),
    stri_mean=("stri2024", "mean"),
    cr5_mean=("cr524", "mean"),
    total_median=("total24", "median"),
).round(1).sort_index()
print(prof.to_string())

print("\n=== correlations (n=%d) ===" % len(m))
for a, b in [("stri2024", "hhi24"), ("stri2014", "hhi14"),
             ("stri_change", "hhi_delta"), ("total24", "hhi24")]:
    if a in m and b in m:
        sub = m[[a, b]].dropna()
        print(f"  {a:12s} vs {b:10s}  r={sub.corr().iloc[0,1]:+.3f}  n={len(sub)}")

m.to_csv(INTEG / "policy_trade_panel_106.csv", index=False, encoding="utf-8-sig")
prof.to_csv(INTEG / "cluster_profile.csv", encoding="utf-8-sig")

print("\n=== top-5 in context ===")
t5 = m[m["iso2"].isin(["US", "IE", "GB", "DE", "IN"])][
    ["iso2", "hhi24", "hhi14", "hhi_delta", "stri2024", "stri_change", "cluster_label"]]
print(t5.round(3).to_string(index=False))
print("\nDONE ->", INTEG)
