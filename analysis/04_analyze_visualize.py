# -*- coding: utf-8 -*-
"""Step 4: size-stratified analysis + six core visualizations."""
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
INTEG = ROOT / "data" / "integrated"
VIS = ROOT / "visualization"
VIS.mkdir(parents=True, exist_ok=True)

panel = pd.read_csv(INTEG / "policy_trade_panel_106.csv", dtype={"iso2": str})
con5 = pd.read_csv(INTEG / "concentration_top5.csv", dtype={"exporter": str})
pol = pd.read_csv(INTEG / "policy_dimension_scores.csv", index_col=0)
bilateral = pd.read_parquet(ROOT / "data" / "cleaned" / "batis_si2_top5_bilateral.parquet")

FIVE = ["US", "IE", "GB", "DE", "IN"]
CN = {"US": "\u7f8e\u56fd", "IE": "\u7231\u5c14\u5170", "GB": "\u82f1\u56fd",
      "DE": "\u5fb7\u56fd", "IN": "\u5370\u5ea6"}

# ---------- size strata ----------
panel["size_tier"] = pd.qcut(panel["total24"], 3,
                             labels=["\u5c0f\u578b\uff08\u4e0b1/3\uff09",
                                     "\u4e2d\u578b\uff08\u4e2d1/3\uff09",
                                     "\u5927\u578b\uff08\u4e0a1/3\uff09"])
print("=== size strata ===")
st = panel.groupby("size_tier", observed=True).agg(
    n=("iso2", "size"),
    total_median=("total24", "median"),
    hhi_mean=("hhi24", "mean"),
    stri_mean=("stri2024", "mean"),
).round(1)
print(st.to_string())

print("\n=== partial correlation within size tier ===")
for tier, g in panel.groupby("size_tier", observed=True):
    r = g[["stri2024", "hhi24"]].dropna().corr().iloc[0, 1]
    print(f"  {tier}: r={r:+.3f}  n={len(g)}")

# residualise HHI on log size, then correlate with STRI
x = np.log1p(panel["total24"])
y = panel["hhi24"]
mask = x.notna() & y.notna()
beta = np.polyfit(x[mask], y[mask], 1)
panel.loc[mask, "hhi_resid"] = y[mask] - np.polyval(beta, x[mask])
sub = panel[["stri2024", "hhi_resid"]].dropna()
print(f"\n=== size-adjusted correlation (HHI residual vs STRI) ===")
print(f"  r={sub.corr().iloc[0,1]:+.3f}  n={len(sub)}")
print(f"  HHI = {beta[0]:.1f} * log(total) + {beta[1]:.1f}")

panel.to_csv(INTEG / "policy_trade_panel_106.csv", index=False, encoding="utf-8-sig")

# ================= FIGURE 1: five-country HHI comparison =================
fig, ax = plt.subplots(figsize=(9.5, 5.2))
snap = con5[con5["year"] == 2024].sort_values("hhi")
bars = ax.barh([CN[e] for e in snap["exporter"]], snap["hhi"],
               color=["#4C78A8" if e not in ("IN",) else "#E45756" for e in snap["exporter"]])
for b, (_, r) in zip(bars, snap.iterrows()):
    ax.text(b.get_width() + 15, b.get_y() + b.get_height() / 2,
            f"HHI {r['hhi']:.0f}\n\u524d\u4e94\u4f19\u4f34 {r['cr5']:.0f}%",
            va="center", fontsize=8.5)
ax.set_xlabel("HHI \u51fa\u53e3\u5e02\u573a\u96c6\u4e2d\u5ea6\uff08\u8d8a\u9ad8\u8d8a\u96c6\u4e2d\uff09")
ax.set_title("\u4e94\u5927\u51fa\u53e3\u56fd\u7684\u8ba1\u7b97\u673a\u670d\u52a1\u51fa\u53e3\u96c6\u4e2d\u5ea6\u76f8\u5dee\u591a\u5c11\u500d\uff1f\n\uff082024 \u5e74\uff0cBaTiS SI2 \u53cc\u8fb9\u5e73\u8861\u503c\uff09", fontsize=11)
ax.set_xlim(0, 1050)
ax.grid(axis="x", alpha=0.3)
fig.tight_layout()
fig.savefig(VIS / "fig1_hhi_by_country.png", dpi=160)
plt.close(fig)
print("\nfig1 done")

# ================= FIGURE 2: scatter STRI x HHI (106 countries) =================
fig, ax = plt.subplots(figsize=(9.8, 6.4))
ax.scatter(panel["stri2024"], panel["hhi24"], s=34, alpha=0.55,
           c="#4C78A8", edgecolors="none", label="\u5176\u4ed6\u7ecf\u6d4e\u4f53")
f5 = panel[panel["iso2"].isin(FIVE)]
ax.scatter(f5["stri2024"], f5["hhi24"], s=150, c="#E45756",
           edgecolors="white", linewidths=1.6, zorder=5, label="\u524d\u4e94\u5927\u51fa\u53e3\u56fd")
for _, r in f5.iterrows():
    ax.annotate(CN[r["iso2"]], (r["stri2024"], r["hhi24"]),
                xytext=(8, 7), textcoords="offset points", fontsize=9.5,
                color="#B22222", fontweight="bold")
# trend line
s = panel[["stri2024", "hhi24"]].dropna()
z = np.polyfit(s["stri2024"], s["hhi24"], 1)
xs = np.linspace(s["stri2024"].min(), s["stri2024"].max(), 50)
ax.plot(xs, np.polyval(z, xs), "--", color="#888888", lw=1.4,
        label=f"\u7ebf\u6027\u62df\u5408 r={s.corr().iloc[0,1]:+.2f}")
ax.set_xlabel("\u6570\u5b57 STRI\uff082024\uff0c\u8d8a\u9ad8\u9650\u5236\u8d8a\u4e25\uff09")
ax.set_ylabel("\u51fa\u53e3\u5e02\u573a HHI")
ax.set_title("\u653f\u7b56\u8d8a\u4e25\u7684\u56fd\u5bb6\uff0c\u8ba1\u7b97\u673a\u670d\u52a1\u51fa\u53e3\u771f\u7684\u66f4\u96c6\u4e2d\u5417\uff1f\n\uff08106 \u4e2a\u7ecf\u6d4e\u4f53\uff0c2024 \u5e74\uff09", fontsize=11.5)
ax.legend(fontsize=9, loc="upper right")
ax.grid(alpha=0.28)
fig.tight_layout()
fig.savefig(VIS / "fig2_stri_vs_hhi.png", dpi=160)
plt.close(fig)
print("fig2 done")

# ================= FIGURE 3: HHI trajectory 2014-2024 =================
fig, ax = plt.subplots(figsize=(10, 5.6))
colors5 = {"US": "#4C78A8", "IE": "#54A24B", "GB": "#F58518",
           "DE": "#72B7B2", "IN": "#E45756"}
for ex in FIVE:
    d = con5[con5["exporter"] == ex].sort_values("year")
    ax.plot(d["year"], d["hhi"], marker="o", ms=4.5, lw=2.0,
            color=colors5[ex], label=CN[ex])
    last = d.iloc[-1]
    ax.annotate(f"{last['hhi']:.0f}", (last["year"], last["hhi"]),
                xytext=(6, 0), textcoords="offset points", fontsize=9,
                color=colors5[ex], va="center")
ax.set_xlabel("\u5e74\u4efd")
ax.set_ylabel("HHI \u51fa\u53e3\u5e02\u573a\u96c6\u4e2d\u5ea6")
ax.set_title("\u5341\u5e74\u95f4\u4e94\u56fd\u7684\u51fa\u53e3\u5e02\u573a\u7ed3\u6784\u662f\u8d70\u5411\u96c6\u4e2d\u8fd8\u662f\u5206\u6563\uff1f\n\uff082014\u20132024\uff0c\u5370\u5ea6\u964d\u5e45\u6700\u5927\uff09", fontsize=11.5)
ax.legend(fontsize=9.5, ncol=5, loc="upper center")
ax.grid(alpha=0.28)
fig.tight_layout()
fig.savefig(VIS / "fig3_hhi_trend.png", dpi=160)
plt.close(fig)
print("fig3 done")

# ================= FIGURE 4: R/S/L/G radar =================
dims = ["R", "S", "L", "G"]
dim_cn = {"R": "\u9650\u5236 R", "S": "\u4fdd\u969c S", "L": "\u672c\u5730\u5316 L", "G": "\u5408\u4f5c G"}
angles = np.linspace(0, 2 * np.pi, len(dims), endpoint=False).tolist()
angles += angles[:1]
fig, ax = plt.subplots(figsize=(7.6, 7.6), subplot_kw=dict(polar=True))
for ex in FIVE:
    if ex not in pol.index:
        continue
    vals = [pol.loc[ex, d] if d in pol.columns else 0 for d in dims]
    vals += vals[:1]
    ax.plot(angles, vals, lw=2.0, label=CN[ex], color=colors5[ex])
    ax.fill(angles, vals, alpha=0.10, color=colors5[ex])
ax.set_xticks(angles[:-1])
ax.set_xticklabels([dim_cn[d] for d in dims], fontsize=10.5)
ax.set_title("\u4e94\u56fd\u653f\u7b56\u5de5\u5177\u7ed3\u6784\uff1a\u9760\u9650\u5236\u8fd8\u662f\u9760\u4fdd\u969c\uff1f\n\uff08\u6761\u6b3e\u5f3a\u5ea6\u603b\u5206\uff0c\u81ea\u5efa R/S/L/G \u7f16\u7801\uff09", fontsize=11.5, pad=26)
ax.legend(loc="upper right", bbox_to_anchor=(1.20, 1.10), fontsize=9.5)
ax.grid(alpha=0.35)
fig.tight_layout()
fig.savefig(VIS / "fig4_rslg_radar.png", dpi=160)
plt.close(fig)
print("fig4 done")

# ================= FIGURE 5: cluster map =================
fig, ax = plt.subplots(figsize=(10.2, 6.6))
cmap = {"A \u9ad8\u9650\u5236-\u9ad8\u96c6\u4e2d": "#E45756",
        "B \u4f4e\u9650\u5236-\u9ad8\u96c6\u4e2d": "#F58518",
        "C \u9ad8\u9650\u5236-\u4f4e\u96c6\u4e2d": "#B279A2",
        "D \u4f4e\u9650\u5236-\u4f4e\u96c6\u4e2d": "#4C78A8"}
for lab, g in panel.groupby("cluster_label"):
    ax.scatter(g["stri2024"], g["hhi24"], s=np.sqrt(g["total24"]) / 2.6,
               alpha=0.62, c=cmap.get(lab, "#999"), label=f"{lab}\uff08n={len(g)}\uff09",
               edgecolors="white", linewidths=0.6)
for _, r in panel[panel["iso2"].isin(FIVE)].iterrows():
    ax.annotate(CN[r["iso2"]], (r["stri2024"], r["hhi24"]), xytext=(7, 5),
                textcoords="offset points", fontsize=9.5, fontweight="bold", color="#111")
ax.set_xlabel("\u6570\u5b57 STRI\uff082024\uff09")
ax.set_ylabel("HHI\uff082024\uff09")
ax.set_title("106 \u4e2a\u7ecf\u6d4e\u4f53\u80fd\u5206\u6210\u51e0\u79cd\u300c\u653f\u7b56\u2014\u5e02\u573a\u7ed3\u6784\u300d\u7ec4\u5408\uff1f\n\uff08\u70b9\u5927\u5c0f\u8868\u793a\u51fa\u53e3\u89c4\u6a21\uff0cK-means \u805a\u7c7b k=4\uff09", fontsize=11.5)
ax.legend(fontsize=8.6, loc="upper right", framealpha=0.92)
ax.grid(alpha=0.28)
fig.tight_layout()
fig.savefig(VIS / "fig5_cluster.png", dpi=160)
plt.close(fig)
print("fig5 done")

# ================= FIGURE 6: size-stratified =================
fig, ax = plt.subplots(figsize=(10, 6))
tier_color = {"\u5c0f\u578b\uff08\u4e0b1/3\uff09": "#F58518",
              "\u4e2d\u578b\uff08\u4e2d1/3\uff09": "#72B7B2",
              "\u5927\u578b\uff08\u4e0a1/3\uff09": "#4C78A8"}
for tier, g in panel.groupby("size_tier", observed=True):
    ax.scatter(g["stri2024"], g["hhi24"], s=42, alpha=0.6,
               c=tier_color[tier], label=f"{tier}, n={len(g)}", edgecolors="none")
    s = g[["stri2024", "hhi24"]].dropna()
    if len(s) > 5:
        z = np.polyfit(s["stri2024"], s["hhi24"], 1)
        xs = np.linspace(s["stri2024"].min(), s["stri2024"].max(), 30)
        ax.plot(xs, np.polyval(z, xs), "--", color=tier_color[tier], lw=1.8,
                label=f"  r={s.corr().iloc[0,1]:+.2f}")
ax.set_xlabel("\u6570\u5b57 STRI\uff082024\uff09")
ax.set_ylabel("HHI\uff082024\uff09")
ax.set_title("\u63a7\u5236\u56fd\u5bb6\u89c4\u6a21\u540e\uff0c\u653f\u7b56\u4e0e\u96c6\u4e2d\u5ea6\u7684\u5173\u7cfb\u662f\u5426\u4ecd\u7136\u6210\u7acb\uff1f\n\uff08\u6309\u51fa\u53e3\u89c4\u6a21\u4e09\u5206\u7ec4\uff09", fontsize=11.5)
ax.legend(fontsize=8.6, ncol=2, loc="upper right")
ax.grid(alpha=0.28)
fig.tight_layout()
fig.savefig(VIS / "fig6_size_strata.png", dpi=160)
plt.close(fig)
print("fig6 done")

# ---------- summary stats ----------
summary = {
    "n_countries": int(len(panel)),
    "corr_all": round(float(panel[["stri2024", "hhi24"]].dropna().corr().iloc[0, 1]), 3),
    "corr_resid": round(float(panel[["stri2024", "hhi_resid"]].dropna().corr().iloc[0, 1]), 3),
    "corr_change": round(float(panel[["stri_change", "hhi_delta"]].dropna().corr().iloc[0, 1]), 3),
    "size_strata_corr": {
        str(k): round(float(g[["stri2024", "hhi24"]].dropna().corr().iloc[0, 1]), 3)
        for k, g in panel.groupby("size_tier", observed=True)
    },
}
json.dump(summary, open(INTEG / "analysis_summary.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("\n=== summary ===")
print(json.dumps(summary, ensure_ascii=False, indent=2))
print("\nfigures ->", VIS)
