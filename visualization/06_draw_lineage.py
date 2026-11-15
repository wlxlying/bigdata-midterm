# -*- coding: utf-8 -*-
"""Lineage diagram aligned with the files actually used in the report."""
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
       / "midterm_project" / "visualization")

fig, ax = plt.subplots(figsize=(14.8, 8.6))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")
fig.patch.set_facecolor("white")


def box(x, y, w, h, title, sub, fc, ec):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.35,rounding_size=0.8",
        linewidth=1.3, facecolor=fc, edgecolor=ec,
    ))
    ax.text(x + w / 2, y + h * 0.64, title, ha="center", va="center",
            fontsize=8.6, fontweight="bold", color="#1a1a1a")
    ax.text(x + w / 2, y + h * 0.30, sub, ha="center", va="center",
            fontsize=6.7, color="#333333", linespacing=1.25)


def arrow(x, y1, y2):
    ax.add_patch(FancyArrowPatch(
        (x, y1), (x, y2), arrowstyle="-|>", mutation_scale=9,
        linewidth=0.9, color="#6b7280",
    ))


ax.text(50, 97.2, "\u591a\u6e90\u6570\u636e\u5173\u8054\u56fe", ha="center", va="center",
        fontsize=16, fontweight="bold")
ax.text(50, 93.6,
        "\u8ba1\u7b97\u673a\u670d\u52a1\u51fa\u53e3\u96c6\u4e2d\u5ea6  \u00b7  \u6570\u5b57\u8d38\u6613\u9650\u5236  \u00b7  \u7acb\u6cd5\u4e8b\u4ef6",
        ha="center", va="center", fontsize=9, color="#444444")

raw = [
    ("BaTiS", "OECD\u2013WTO\n2,841 MB\n\u5e73\u8861\u77e9\u9635", "#dbeafe", "#1d4ed8"),
    ("WTO \u5e74\u5ea6", "\u5546\u4e1a\u670d\u52a1\n2,233 MB\n\u539f\u59cb\u62a5\u9001", "#dbeafe", "#1d4ed8"),
    ("UNCTAD", "\u53cc\u8fb9\u670d\u52a1\n2,216 MB\n\u62a5\u9001\u534f\u8c03", "#dbeafe", "#1d4ed8"),
    ("\u6570\u5b57 STRI", "\u6307\u6570 + \u76d1\u7ba1\u5e93\n106 / 129 \u56fd\n\u9886\u57df\u6821\u51c6", "#ffedd5", "#c2410c"),
    ("\u6cd5\u89c4\u539f\u6587", "\u4e94\u56fd\u6761\u6b3e\n24 \u6761\nR / S / L / G", "#ffedd5", "#c2410c"),
    ("WDI", "\u4e16\u754c\u94f6\u884c\n\u7ea6 4 MB\n\u89c4\u6a21\u4e0e\u5f00\u653e", "#f3e8ff", "#6d28d9"),
    ("GDELT", "23 \u4e2a\u65e5\u6587\u4ef6\n282 \u4e07\u4e8b\u4ef6\n\u5370\u5ea6 DPDP \u7a97", "#f3e8ff", "#6d28d9"),
]
for i, (title, sub, fc, ec) in enumerate(raw):
    box(1.2 + i * 14.15, 74.5, 13.3, 15.2, title, sub, fc, ec)

mid = [
    ("SI2 \u51fa\u53e3\u9762\u677f", "2014\u20132024\n\u4e94\u56fd\u53cc\u8fb9\u4e0e\n198 \u56fd\u5e74\u5ea6 HHI", "#ecfdf5", "#047857"),
    ("\u4e09\u6e90\u96c6\u4e2d\u5ea6", "\u540c\u4e00\u5e74\u4efd\n\u4f19\u4f34\u96c6\u5408\u4e0d\u540c\nHHI \u5e76\u5217", "#ecfdf5", "#047857"),
    ("\u653f\u7b56\u2014\u63a7\u5236\u9762\u677f", "STRI\u3001\u4e94\u9886\u57df\nGDP\u3001\u4e92\u8054\u7f51\n\u8d38\u6613\u5f00\u653e", "#ecfdf5", "#047857"),
    ("\u7acb\u6cd5\u5468\u4e8b\u4ef6", "\u884c\u52a8\u5730\u6216\u53c2\u4e0e\u65b9\n\u4e3a\u5370\u5ea6\n\u4e13\u540d\u94fe\u63a5\u8ba1\u6570", "#ecfdf5", "#047857"),
]
for i, (title, sub, fc, ec) in enumerate(mid):
    box(3.5 + i * 24.2, 50.5, 22.2, 14.5, title, sub, fc, ec)

for i in range(7):
    arrow(1.2 + i * 14.15 + 6.6, 74.5, 66.2)
ax.plot([8, 92], [66.2, 66.2], color="#9ca3af", lw=0.8)
for i in range(4):
    arrow(3.5 + i * 24.2 + 11.1, 66.2, 65.0)

low = [
    ("\u53cc\u5411\u56fa\u5b9a\u6548\u5e94", "\u56fd\u5bb6 + \u5e74\u4efd\n\u56fd\u5bb6\u805a\u7c7b\u6807\u51c6\u8bef\n\u5206\u6570 logit", "#fff7ed", "#9a3412"),
    ("\u53cc\u8fb9\u9645\u5206\u89e3", "ln HHI = \u2212ln N\n+ ln(1+CV\u00b2)\n\u6052\u7b49\u5f0f\u8bef\u5dee\u7ea6\u4e3a 0", "#fff7ed", "#9a3412"),
    ("\u7ed3\u6784\u5206\u7ec4", "K-means\nWard \u5c42\u6b21\nDBSCAN \u79bb\u7fa4", "#fff7ed", "#9a3412"),
    ("\u4e8b\u4ef6\u6838\u5bf9", "\u63d0\u4ea4\u3001\u4e24\u9662\u901a\u8fc7\n\u5bf9\u7167\u5e74\u5ea6 HHI\n\u4e0e STRI", "#fff7ed", "#9a3412"),
]
for i, (title, sub, fc, ec) in enumerate(low):
    box(3.5 + i * 24.2, 27.2, 22.2, 14.5, title, sub, fc, ec)
    arrow(3.5 + i * 24.2 + 11.1, 50.5, 41.7)

ax.text(50, 20.6, "\u56db\u79cd\u5173\u8054", ha="center", fontsize=10, fontweight="bold")
notes = [
    ("#1d4ed8", "\u5b9e\u4f53", "ISO2\u3001ISO3 \u4e0e M49 \u6620\u5c04\u5230\u540c\u4e00\u7ecf\u6d4e\u4f53"),
    ("#047857", "\u65f6\u95f4", "\u8d38\u6613\u4e0e\u6307\u6570\u7528\u5e74\uff1b\u4e8b\u4ef6\u7528\u65e5\uff0c\u843d\u5728 2023 \u5e74\u5185"),
    ("#c2410c", "\u8bed\u4e49", "EBOPS \u7684 SI2\uff1b\u76d1\u7ba1\u9886\u57df DG.1\u2013DG.5\uff1b\u6761\u6b3e R/S/L/G"),
    ("#6d28d9", "\u4e8b\u4ef6", "\u5370\u5ea6 DPDP \u7684\u63d0\u4ea4\u4e0e\u4e24\u9662\u901a\u8fc7\u65e5\uff0c\u5bf9\u63a5 GDELT \u4e13\u540d\u94fe\u63a5"),
]
for i, (color, name, text) in enumerate(notes):
    x = 4 + (i % 4) * 24
    ax.add_patch(FancyBboxPatch((x, 8.2), 2.2, 2.2, boxstyle="square,pad=0",
                                facecolor=color, edgecolor=color))
    ax.text(x + 3.0, 9.3, name, ha="left", va="center", fontsize=8, fontweight="bold", color=color)
    ax.text(x, 5.6, text, ha="left", va="center", fontsize=6.6, color="#333333")

ax.text(50, 1.6,
        "\u6570\u636e\u8303\u56f4\uff1a\u8d38\u6613\u4e0e\u6307\u6570 2014\u20132024\uff1bGDELT \u65e5\u6587\u4ef6 2023-07-22 \u81f3 2023-08-17\uff0c\u7f3a 4 \u5929\u3002"
        "\u4f53\u79ef\u4e3a\u89e3\u538b\u540e\u7684\u539f\u59cb\u6587\u4ef6\uff0c\u4e0d\u91cd\u590d\u8ba1\u5165\u538b\u7f29\u5305\u3002",
        ha="center", va="center", fontsize=7, color="#555555")

fig.tight_layout()
fig.savefig(OUT / "data_lineage.png", dpi=160)
print(OUT / "data_lineage.png")
