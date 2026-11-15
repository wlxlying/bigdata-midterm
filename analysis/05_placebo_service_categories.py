# -*- coding: utf-8 -*-
"""Within-BaTiS placebo: compare SI2 (computer services) against other service items.

Rationale: BACI download is too slow to serve as the goods-side placebo. Instead we use
BaTiS's own other EBOPS categories as the comparison group. If the STRI-concentration
pattern appears for travel/transport (services not delivered digitally), then any
pattern found for SI2 is unlikely to be driven by digital policy.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np
import pandas as pd

for name in ("Microsoft YaHei", "SimHei"):
    try:
        font_manager.findfont(name, fallback_to_default=False)
        plt.rcParams["font.sans-serif"] = [name]
        break
    except Exception:
        continue
plt.rcParams["axes.unicode_minus"] = False

ROOT = Path(r"d:/HuaweiMoveData/Users/wlx/Desktop") / "\u6570\u636e\u9a71\u52a8" / "midterm_project"
RAW = ROOT / "data" / "raw"
INTEG = ROOT / "data" / "integrated"
VIS = ROOT / "visualization"

BATIS = RAW / "OECD-WTO_BATIS_BPM6_bulk.csv"
AGG = {"WL", "EU", "GEU", "ROW"}
# SI2 = computer services (digital); SC = transport, SD = travel (non-digital)
ITEMS = {"SI2": "\u8ba1\u7b97\u673a\u670d\u52a1", "SC": "\u8fd0\u8f93\u670d\u52a1", "SD": "\u65c5\u6e38\u670d\u52a1"}

frames = []
for chunk in pd.read_csv(
        BATIS,
        usecols=["Reporter", "type_Reporter", "Partner", "type_Partner", "Flow",
                 "Item_code", "Year", "Balanced_value"],
        chunksize=2_000_000,
        dtype={"Item_code": "string", "Flow": "string", "Year": "Int64",
               "type_Reporter": "string", "type_Partner": "string"}):
    sub = chunk[(chunk["Item_code"].isin(list(ITEMS)))
                & (chunk["Flow"] == "X")
                & (chunk["Year"] == 2024)
                & (chunk["type_Reporter"] == "c")
                & (chunk["type_Partner"] == "c")
                & (~chunk["Partner"].isin(AGG))]
    if not sub.empty:
        frames.append(sub)

df = pd.concat(frames, ignore_index=True)
df = df.rename(columns={"Reporter": "iso2", "Item_code": "item", "Balanced_value": "value"})
df = df[df["value"].notna()]
print("rows:", len(df), "items:", df["item"].value_counts().to_dict())


def conc(g):
    v = g["value"].values
    tot = v.sum()
    if tot <= 0:
        return np.nan
    s = v / tot
    return float((s ** 2).sum() * 10000)


res = df.groupby(["iso2", "item"]).apply(conc, include_groups=False).reset_index()
res.columns = ["iso2", "item", "hhi"]
piv = res.pivot(index="iso2", columns="item", values="hhi").dropna()
print("\ncountries with all three items:", len(piv))

panel = pd.read_csv(INTEG / "policy_trade_panel_106.csv", dtype={"iso2": str})
m = piv.merge(panel[["iso2", "stri2024"]], left_index=True, right_on="iso2", how="inner")
print("merged:", len(m))

print("\n=== placebo: correlation of STRI with HHI, by service item ===")
rows = []
for it, label in ITEMS.items():
    if it not in m.columns:
        continue
    s = m[["stri2024", it]].dropna()
    r = s.corr().iloc[0, 1]
    rows.append({"item": it, "label": label, "n": len(s), "r": round(float(r), 3)})
    print(f"  {label:8s} ({it}): r={r:+.3f}  n={len(s)}")

pl = pd.DataFrame(rows)
pl.to_csv(INTEG / "placebo_service_categories.csv", index=False, encoding="utf-8-sig")

# figure
fig, axes = plt.subplots(1, 3, figsize=(15, 5.2))
for ax, it in zip(axes, ["SI2", "SC", "SD"]):
    if it not in m.columns:
        ax.axis("off")
        continue
    s = m[["stri2024", it]].dropna()
    ax.scatter(s["stri2024"], s[it], s=26, alpha=0.5, c="#4C78A8", edgecolors="none")
    z = np.polyfit(s["stri2024"], s[it], 1)
    xs = np.linspace(s["stri2024"].min(), s["stri2024"].max(), 30)
    ax.plot(xs, np.polyval(z, xs), "--", color="#E45756", lw=1.8)
    r = s.corr().iloc[0, 1]
    ax.set_title(f"{ITEMS[it]}\uff08{it}\uff09 r={r:+.2f}", fontsize=11.5)
    ax.set_xlabel("\u6570\u5b57 STRI (2024)", fontsize=9.5)
    ax.set_ylabel("HHI", fontsize=9.5)
    ax.grid(alpha=0.28)
fig.suptitle("\u5b89\u6170\u5242\u68c0\u9a8c\uff1a\u82e5\u975e\u6570\u5b57\u670d\u52a1\u4e5f\u5448\u73b0\u540c\u6837\u6a21\u5f0f\uff0c\u5219 SI2 \u7684\u7ed3\u679c\u4e0d\u80fd\u5f52\u56e0\u4e8e\u6570\u5b57\u653f\u7b56\n"
         "\uff08BaTiS 2024\uff0c\u8ba1\u7b97\u673a\u670d\u52a1 vs \u8fd0\u8f93 vs \u65c5\u6e38\uff09", fontsize=12)
fig.tight_layout(rect=[0, 0, 1, 0.88])
fig.savefig(VIS / "fig7_placebo_services.png", dpi=160)
plt.close(fig)
print("\nfig7 saved")
