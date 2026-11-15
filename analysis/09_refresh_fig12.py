# -*- coding: utf-8 -*-
"""Redraw the GDELT figure from the saved daily table and print report stats."""
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
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
VIS = ROOT / "visualization"
d = pd.read_csv(ROOT / "data" / "integrated" / "gdelt_india_daily.csv")
d["day"] = d["day"].astype(str)
days = list(d["day"])
start = datetime.strptime(days[0], "%Y%m%d")
end = datetime.strptime(days[-1], "%Y%m%d")
have = set(days)
missing = []
cur = start
while cur <= end:
    key = cur.strftime("%Y%m%d")
    if key not in have:
        missing.append(cur.strftime("%m-%d"))
    cur += timedelta(days=1)

labels = [x[4:6] + "-" + x[6:8] for x in days]
x = range(len(days))
fig, ax = plt.subplots(figsize=(10.4, 5.5))
ax.bar(list(x), d["in_geo"], color="#c5cdd6", width=0.72, label="\u884c\u52a8\u5730\u5728\u5370\u5ea6\u7684\u5168\u90e8\u4e8b\u4ef6")
ax2 = ax.twinx()
ax2.plot(list(x), d["mid"], color="#1f4e79", marker="o", lw=1.8, label="\u6570\u636e\u4fdd\u62a4\u7c7b\u94fe\u63a5")
ax2.plot(list(x), d["narrow"], color="#9c2f2f", marker="s", lw=1.8, label="\u6cd5\u6848\u4e13\u540d\u94fe\u63a5")
for mark, text in (("20230803", "\u63d0\u4ea4"), ("20230807", "\u4eba\u6c11\u9662"), ("20230809", "\u8054\u90a6\u9662")):
    i = days.index(mark)
    ax.axvline(i, color="#9c2f2f", ls="--", lw=0.7, alpha=0.65)
    ax.text(i, d["in_geo"].max() * 0.98, text, rotation=90, va="top", ha="right", fontsize=8, color="#9c2f2f")
ax.set_xticks(list(x))
ax.set_xticklabels(labels, rotation=45, ha="right")
ax.set_ylabel("\u4e8b\u4ef6\u6761\u6570")
ax2.set_ylabel("\u542b\u5173\u952e\u8bcd\u7684\u4e8b\u4ef6\u6761\u6570")
ax.set_title(
    "\u5370\u5ea6\u300a\u6570\u5b57\u4e2a\u4eba\u6570\u636e\u4fdd\u62a4\u6cd5\u300b\u901a\u8fc7\u90a3\u4e00\u5468\uff0c\u6570\u636e\u4fdd\u62a4\u62a5\u9053\u6709\u6ca1\u6709\u62ac\u5347\uff1f\n"
    "GDELT \u65e5\u6587\u4ef6 2023-07-22 \u81f3 2023-08-17\uff0c\u7f3a " + "\u3001".join(missing),
    fontsize=12,
)
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="upper left", frameon=False, fontsize=8)
fig.text(
    0.01, 0.005,
    "\u5355\u4f4d\uff1a\u4e8b\u4ef6\u6761\u6570\u3002\u6765\u6e90\uff1aGDELT 2.0 \u65e5\u5ea6\u4e8b\u4ef6\u5e93\u3002"
    "\u7b5b\u9009\uff1a\u884c\u52a8\u5730\u4e3a\u5370\u5ea6\uff0c\u6216\u53c2\u4e0e\u65b9\u4e3a IND\u3002"
    "\u4e13\u540d\u94fe\u63a5\u542b dpdp\u3001digital-personal\u3001personal-data-protection\uff1b"
    "\u6570\u636e\u4fdd\u62a4\u7c7b\u53e6\u542b data-protection\u3002\u7f3a\u65e5\u4e0d\u4ee5 0 \u586b\u5145\u3002",
    fontsize=7.2, color="#333333",
)
fig.tight_layout(rect=(0, 0.05, 1, 1))
fig.savefig(VIS / "fig12_gdelt_dpdp.png", dpi=160)
print("missing", missing)
print("narrow_sum", int(d["narrow"].sum()), "rows_sum", int(d["rows"].sum()))

raw = ROOT / "data" / "raw"
for child in sorted(raw.iterdir(), key=lambda p: p.name):
    if child.is_file():
        n = child.stat().st_size
    else:
        n = sum(f.stat().st_size for f in child.rglob("*") if f.is_file())
    print("SIZE", child.name, round(n / 1048576, 1))
pol = ROOT / "policy_raw"
print("POLICY_MB", round(sum(f.stat().st_size for f in pol.rglob("*") if f.is_file()) / 1048576, 1))

panel = pd.read_csv(ROOT / "data" / "integrated" / "analysis_panel_full.csv")
five = panel[panel["iso2"].isin(["US", "IE", "GB", "DE", "IN"])][
    ["iso2", "stri2014", "stri2024", "hhi14", "hhi24", "total14", "total24"]
]
print(five.to_string(index=False))

reg = pd.read_csv(ROOT / "data" / "integrated" / "regulatory_domain_index.csv")
reg24 = reg[reg["year"] == 2024]
m = reg24.merge(panel[["iso3", "hhi24"]], left_on="Country_code", right_on="iso3")
print("domain_overlap", len(m))
for col in ["DG.1", "DG.2", "DG.3", "DG.4", "DG.5", "reg_index_w"]:
    print(col, round(float(m[col].corr(m["hhi24"])), 3), "n", int(m[col].notna().sum()))

clean = ROOT / "data" / "cleaned"
for p in sorted(clean.glob("*.csv")):
    with p.open("rb") as fh:
        n = sum(1 for _ in fh) - 1
    print("CLEAN", p.name, n)
