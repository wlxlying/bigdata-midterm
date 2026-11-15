# -*- coding: utf-8 -*-
"""Larger-type lineage for the classroom slide. Report figure stays as is."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

for name in ("Microsoft YaHei", "SimHei"):
    try:
        font_manager.findfont(name, fallback_to_default=False)
        plt.rcParams["font.sans-serif"] = [name]
        break
    except Exception:
        continue
plt.rcParams["axes.unicode_minus"] = False

OUT = (Path(r"d:/HuaweiMoveData/Users/wlx/Desktop") / "\u6570\u636e\u9a71\u52a8"
       / "midterm_project" / "visualization" / "data_lineage_slide.png")

fig, ax = plt.subplots(figsize=(13.0, 5.35))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")
fig.patch.set_facecolor("white")


def box(x, y, w, h, title, sub, fc, ec):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.3,rounding_size=1.2",
        linewidth=1.6, facecolor=fc, edgecolor=ec,
    ))
    ax.text(x + w / 2, y + h * 0.68, title, ha="center", va="center",
            fontsize=13, fontweight="bold", color="#142B45")
    ax.text(x + w / 2, y + h * 0.32, sub, ha="center", va="center",
            fontsize=10.5, color="#333333", linespacing=1.35)


def arrow(x, y1, y2):
    ax.add_patch(FancyArrowPatch(
        (x, y1), (x, y2), arrowstyle="-|>", mutation_scale=12,
        linewidth=1.1, color="#6b7280",
    ))


raw = [
    ("BaTiS", "\u5e73\u8861\u77e9\u9635\n2,841 MB", "#dbeafe", "#1d4ed8"),
    ("WTO \u5e74\u5ea6", "\u539f\u59cb\u62a5\u9001\n2,233 MB", "#dbeafe", "#1d4ed8"),
    ("UNCTAD", "\u62a5\u9001\u534f\u8c03\n2,216 MB", "#dbeafe", "#1d4ed8"),
    ("\u6570\u5b57 STRI", "\u6307\u6570 + \u76d1\u7ba1\u5e93\n106 / 129 \u56fd", "#ffedd5", "#c2410c"),
    ("\u6cd5\u89c4\u539f\u6587", "\u4e94\u56fd 24 \u6761\nR / S / L / G", "#ffedd5", "#c2410c"),
    ("WDI", "\u89c4\u6a21\u4e0e\u5f00\u653e\n\u7ea6 4 MB", "#f3e8ff", "#6d28d9"),
    ("GDELT", "23 \u4e2a\u65e5\u6587\u4ef6\n282 \u4e07\u4e8b\u4ef6", "#f3e8ff", "#6d28d9"),
]
for i, (title, sub, fc, ec) in enumerate(raw):
    box(1.0 + i * 14.15, 70, 13.2, 26, title, sub, fc, ec)

mid = [
    ("SI2 \u51fa\u53e3\u9762\u677f", "2014-2024\n\u4e94\u56fd\u53cc\u8fb9\uff0c198 \u56fd\u5e74\u5ea6 HHI", "#ecfdf5", "#047857"),
    ("\u4e09\u6e90\u96c6\u4e2d\u5ea6", "\u540c\u4e00\u5e74\u4efd\n\u4f19\u4f34\u96c6\u5408\u4e0d\u540c", "#ecfdf5", "#047857"),
    ("\u653f\u7b56\u4e0e\u63a7\u5236", "STRI\u3001\u4e94\u9886\u57df\nGDP\u3001\u4e92\u8054\u7f51", "#ecfdf5", "#047857"),
    ("\u7acb\u6cd5\u5468\u4e8b\u4ef6", "\u884c\u52a8\u5730\u6216\u53c2\u4e0e\u65b9\u4e3a\u5370\u5ea6\n\u4e13\u540d\u94fe\u63a5\u8ba1\u6570", "#ecfdf5", "#047857"),
]
for i, (title, sub, fc, ec) in enumerate(mid):
    box(2.2 + i * 24.4, 39, 22.4, 24, title, sub, fc, ec)

ax.plot([7.6, 92.4], [68.2, 68.2], color="#9ca3af", lw=1.1)
for i in range(7):
    arrow(1.0 + i * 14.15 + 6.6, 70, 68.2)
for i in range(4):
    arrow(2.2 + i * 24.4 + 11.2, 68.2, 63.0)

low = [
    ("\u53cc\u5411\u56fa\u5b9a\u6548\u5e94", "\u56fd\u5bb6 + \u5e74\u4efd\n\u56fd\u5bb6\u805a\u7c7b\u6807\u51c6\u8bef", "#fff7ed", "#9a3412"),
    ("\u53cc\u8fb9\u9645\u5206\u89e3", "ln HHI = -ln N\n+ ln(1 + CV^2)", "#fff7ed", "#9a3412"),
    ("\u7ed3\u6784\u5206\u7ec4", "K-means\n\u4e24\u7ec4\uff0c\u6309\u51fa\u53e3\u89c4\u6a21", "#fff7ed", "#9a3412"),
    ("\u4e8b\u4ef6\u6838\u5bf9", "\u63d0\u4ea4\u3001\u4e24\u9662\u901a\u8fc7\n\u5bf9\u7167\u5f53\u5e74 HHI \u4e0e STRI", "#fff7ed", "#9a3412"),
]
for i, (title, sub, fc, ec) in enumerate(low):
    box(2.2 + i * 24.4, 6, 22.4, 24, title, sub, fc, ec)
    arrow(2.2 + i * 24.4 + 11.2, 39, 30.0)

fig.tight_layout(pad=0.15)
fig.savefig(OUT, dpi=140)
print(OUT)
