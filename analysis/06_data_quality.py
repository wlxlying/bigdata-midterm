# -*- coding: utf-8 -*-
"""Generate a summary data-quality report for the report appendix."""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(r"d:/HuaweiMoveData/Users/wlx/Desktop") / "\u6570\u636e\u9a71\u52a8" / "midterm_project"
INTEG = ROOT / "data" / "integrated"
CLEAN = ROOT / "data" / "cleaned"

lines = []
lines.append("=" * 66)
lines.append("\u6570\u636e\u8d28\u91cf\u68c0\u67e5\u62a5\u544a")
lines.append("=" * 66)

b = pd.read_csv(CLEAN / "batis_si2_top5_bilateral.csv", dtype={"exporter": str, "partner": str})
lines.append(f"\n[1] \u53cc\u8fb9\u9762\u677f\uff08\u4e94\u56fd\u5b50\u96c6\uff09")
lines.append(f"    \u884c\u6570: {len(b):,}")
lines.append(f"    \u51fa\u53e3\u56fd: {sorted(b['exporter'].unique())}")
lines.append(f"    \u5e74\u4efd: {int(b['year'].min())}-{int(b['year'].max())}")
lines.append(f"    \u4f19\u4f34\u6570: {b['partner'].nunique()}")
lines.append(f"    \u503c\u7f3a\u5931: {b['value'].isna().sum()}")
lines.append(f"    \u503c\u4e3a 0: {(b['value'] == 0).sum():,} ({(b['value'] == 0).mean() * 100:.1f}%)")
lines.append(f"    \u503c\u4e3a\u8d1f: {(b['value'] < 0).sum()}")
lines.append(f"    \u6709\u539f\u59cb\u62a5\u9001\u7684\u884c: {b['reported'].sum():,} ({b['reported'].mean() * 100:.2f}%)")

p = pd.read_csv(INTEG / "policy_trade_panel_106.csv", dtype={"iso2": str})
lines.append(f"\n[2] \u56fd\u5bb6\u9762\u677f\uff08106 \u56fd\u5408\u5e76\uff09")
lines.append(f"    \u7ecf\u6d4e\u4f53\u6570: {len(p)}")
lines.append(f"    HHI 2024 \u8303\u56f4: {p['hhi24'].min():.0f} - {p['hhi24'].max():.0f}")
lines.append(f"    STRI 2024 \u8303\u56f4: {p['stri2024'].min():.3f} - {p['stri2024'].max():.3f}")
lines.append(f"    \u51fa\u53e3\u989d\u4e2d\u4f4d\u6570: {p['total24'].median():,.1f} \u767e\u4e07\u7f8e\u5143")
lines.append(f"    \u4efb\u4e00\u5b57\u6bb5\u7f3a\u5931: {p[['hhi24','hhi14','stri2024','total24']].isna().sum().sum()}")

c = pd.read_csv(INTEG / "policy_coded_clauses.csv", dtype={"iso2": str})
lines.append(f"\n[3] \u653f\u7b56\u6761\u6b3e\u7f16\u7801")
lines.append(f"    \u6761\u6b3e\u6570: {len(c)}")
lines.append(f"    \u56fd\u5bb6: {c.groupby('iso2').size().to_dict()}")
lines.append(f"    \u7ef4\u5ea6: {c.groupby('dim').size().to_dict()}")
lines.append(f"    \u5f3a\u5ea6\u5206\u5e03: {c.groupby('strength').size().to_dict()}")
lines.append(f"    \u6bcf\u6761\u90fd\u6709 evidence \u5b57\u6bb5: {(c['evidence'].astype(str).str.len() > 0).all()}")
lines.append(f"    \u6bcf\u6761\u90fd\u6709\u6cd5\u6761\u7f16\u53f7: {(c['art'].astype(str).str.len() > 0).all()}")

lines.append(f"\n[4] \u8de8\u6e90\u5339\u914d")
lines.append(f"    BaTiS \u62a5\u544a\u65b9\u6570: 199")
lines.append(f"    \u6210\u529f\u5339\u914d STRI: {len(p)}")
lines.append(f"    \u5339\u914d\u7387: {len(p) / 199 * 100:.1f}%")

summ = json.loads((INTEG / "analysis_summary.json").read_text(encoding="utf-8"))
lines.append(f"\n[5] \u6838\u5fc3\u7edf\u8ba1\u91cf")
for k, v in summ.items():
    lines.append(f"    {k}: {v}")

out = "\n".join(lines)
print(out)
(INTEG / "data_quality_report.txt").write_text(out, encoding="utf-8")
print("\nsaved ->", INTEG / "data_quality_report.txt")
