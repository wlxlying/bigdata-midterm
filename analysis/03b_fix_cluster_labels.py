# -*- coding: utf-8 -*-
"""Fix cluster labelling: assign four distinct names based on actual cluster means."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

INTEG = (Path(r"d:/HuaweiMoveData/Users/wlx/Desktop") / "\u6570\u636e\u9a71\u52a8"
         / "midterm_project" / "data" / "integrated")

p = pd.read_csv(INTEG / "policy_trade_panel_106.csv", dtype={"iso2": str})

prof = p.groupby("cluster").agg(
    n=("iso2", "size"), hhi=("hhi24", "mean"), stri=("stri2024", "mean"),
    tot=("total24", "median")).round(1)
print("== raw profile ==")
print(prof.to_string())

hhi_med = p["hhi24"].median()
stri_med = p["stri2024"].median()
tot_med = p["total24"].median()
print(f"\nmedians: hhi={hhi_med:.0f} stri={stri_med:.3f} total={tot_med:.1f}")

names = {}
for c, r in prof.iterrows():
    hi_h = r["hhi"] > hhi_med
    hi_s = r["stri"] > stri_med
    tiny = r["tot"] < tot_med / 10
    if tiny:
        names[c] = "D \u5fae\u578b\u7ecf\u6d4e\u4f53-\u6781\u9ad8\u96c6\u4e2d"
    elif hi_h and hi_s:
        names[c] = "A \u9ad8\u9650\u5236-\u9ad8\u96c6\u4e2d"
    elif hi_h:
        names[c] = "B \u4f4e\u9650\u5236-\u9ad8\u96c6\u4e2d"
    elif hi_s:
        names[c] = "C \u9ad8\u9650\u5236-\u4f4e\u96c6\u4e2d"
    else:
        names[c] = "E \u4f4e\u9650\u5236-\u4f4e\u96c6\u4e2d"

p["cluster_label"] = p["cluster"].map(names)
print("\n== label mapping ==")
for c, nm in names.items():
    print(f"  cluster {c} -> {nm}  (n={prof.loc[c,'n']}, hhi={prof.loc[c,'hhi']:.0f}, "
          f"stri={prof.loc[c,'stri']:.3f}, total_med={prof.loc[c,'tot']:.1f})")

print("\n== final label counts ==")
print(p["cluster_label"].value_counts().sort_index().to_string())

print("\n== five countries ==")
print(p[p["iso2"].isin(["US", "IE", "GB", "DE", "IN"])][
    ["iso2", "hhi24", "stri2024", "total24", "cluster_label"]
].round(3).to_string(index=False))

p.to_csv(INTEG / "policy_trade_panel_106.csv", index=False, encoding="utf-8-sig")

prof2 = p.groupby("cluster_label").agg(
    n=("iso2", "size"), hhi_mean=("hhi24", "mean"),
    stri_mean=("stri2024", "mean"), cr5_mean=("cr524", "mean"),
    total_median=("total24", "median")).round(1).sort_index()
prof2.to_csv(INTEG / "cluster_profile.csv", encoding="utf-8-sig")
print("\n== cluster profile ==")
print(prof2.to_string())
