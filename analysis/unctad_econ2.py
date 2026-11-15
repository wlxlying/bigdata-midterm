# -*- coding: utf-8 -*-
"""Finish B1/C2/C4 on the UNCTAD panel (A1/A2 already done).

B1 failed earlier because the formula string was built from a variable, which
trips a patsy tokenizer assertion on this Python version. Formulae are written
out literally here.
"""
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

warnings.filterwarnings("ignore")

ROOT = Path(r"d:/HuaweiMoveData/Users/wlx/Desktop") / "\u6570\u636e\u9a71\u52a8" / "midterm_project"
INTEG = ROOT / "data" / "integrated"


def hr(t):
    print("\n" + "=" * 70)
    print(t)
    print("=" * 70)


p = pd.read_csv(INTEG / "unctad_panel_regression.csv", dtype={"iso3": str}, low_memory=False)
for c in ["hhi", "stri", "ln_size", "ln_gdp", "inet", "trade_open",
          "ln_hhi", "ln_n", "ln_cv_term", "cv", "n_partners", "hhi_share"]:
    p[c] = pd.to_numeric(p[c], errors="coerce")
p["c_iso"] = p["iso3"].astype("category").cat.codes
p["c_year"] = p["year"].astype("category").cat.codes
print("panel: %d rows | countries %d | stri %d"
      % (len(p), p["iso3"].nunique(), p["stri"].notna().sum()))

# ---------- B1 ----------
hr("B1. two-margin decomposition ln(HHI) = -lnN + ln(1+CV^2)")
chk = p.dropna(subset=["ln_hhi", "ln_n", "ln_cv_term"])
print("  identity max error = %.12f"
      % float(((-chk["ln_n"] + chk["ln_cv_term"]) - chk["ln_hhi"]).abs().max()))

specs = [
    ("extensive margin (partner count)", "ln_n",
     "ln_n ~ stri + ln_size + ln_gdp + C(c_iso) + C(c_year)"),
    ("intensive margin (dispersion)", "ln_cv_term",
     "ln_cv_term ~ stri + ln_size + ln_gdp + C(c_iso) + C(c_year)"),
    ("total ln HHI", "ln_hhi",
     "ln_hhi ~ stri + ln_size + ln_gdp + C(c_iso) + C(c_year)"),
]
rows = []
for name, dep, formula in specs:
    d = p.dropna(subset=[dep, "stri", "ln_size", "ln_gdp"])
    if len(d) < 40:
        print("  %-36s skipped n=%d" % (name, len(d)))
        continue
    m = smf.ols(formula, data=d).fit(cov_type="cluster",
                                     cov_kwds={"groups": d["iso3"]})
    rows.append({"margin": name, "dep": dep, "n": int(m.nobs),
                 "b_stri": round(float(m.params["stri"]), 4),
                 "se": round(float(m.bse["stri"]), 4),
                 "t": round(float(m.tvalues["stri"]), 2),
                 "p": round(float(m.pvalues["stri"]), 3)})
    print("  %-36s b=%+.4f (se %.4f) t=%+.2f p=%.3f n=%d"
          % (name, m.params["stri"], m.bse["stri"], m.tvalues["stri"],
             m.pvalues["stri"], m.nobs))
b1 = pd.DataFrame(rows)
b1.to_csv(INTEG / "unctad_B1_decomposition.csv", index=False, encoding="utf-8-sig")

vd = chk[["ln_n", "ln_cv_term", "ln_hhi"]].var()
print("\n  variance shares of ln(HHI):")
print("    total var = %.4f" % vd["ln_hhi"])
print("    var(-lnN)        = %.4f  (%.1f%%)"
      % (vd["ln_n"], vd["ln_n"] / vd["ln_hhi"] * 100))
print("    var(ln(1+CV^2))  = %.4f  (%.1f%%)"
      % (vd["ln_cv_term"], vd["ln_cv_term"] / vd["ln_hhi"] * 100))
pd.DataFrame([{"var_total": round(float(vd["ln_hhi"]), 4),
               "var_extensive": round(float(vd["ln_n"]), 4),
               "var_intensive": round(float(vd["ln_cv_term"]), 4),
               "share_extensive_pct": round(float(vd["ln_n"] / vd["ln_hhi"] * 100), 1),
               "share_intensive_pct": round(float(vd["ln_cv_term"] / vd["ln_hhi"] * 100), 1)}
              ]).to_csv(INTEG / "unctad_B1_variance.csv", index=False, encoding="utf-8-sig")

# ---------- C2 ----------
hr("C2. event study: STRI jumps >= +0.05")
sv = p[["iso3", "year", "stri", "ln_hhi"]].dropna().sort_values(["iso3", "year"]).copy()
sv["d"] = sv.groupby("iso3")["stri"].diff()
ev = (sv[sv["d"] >= 0.05].sort_values("year")
      .groupby("iso3").first().reset_index()[["iso3", "year", "d"]]
      .rename(columns={"year": "event_year", "d": "jump"}))
print("  events: %d" % len(ev))
if len(ev):
    print(ev.sort_values("jump", ascending=False).head(8).round(3).to_string(index=False))
if len(ev) >= 6:
    s2 = sv.merge(ev[["iso3", "event_year"]], on="iso3").copy()
    s2["rel"] = s2["year"] - s2["event_year"]
    s2 = s2[s2["rel"].between(-3, 3)]
    es = s2.groupby("rel").agg(
        n=("ln_hhi", "size"), m=("ln_hhi", "mean"),
        se=("ln_hhi", lambda x: x.std(ddof=1) / np.sqrt(len(x)))).reset_index()
    base = s2[s2["rel"] < 0]["ln_hhi"].mean()
    es["effect_pct"] = (np.exp(es["m"] - base) - 1) * 100
    print("\n  event-time profile (percent change vs pre-event mean):")
    print(es.round(2).to_string(index=False))
    es.to_csv(INTEG / "unctad_C2_event_study.csv", index=False, encoding="utf-8-sig")
ev.to_csv(INTEG / "unctad_C2_events.csv", index=False, encoding="utf-8-sig")

# parallel-trends check: is the pre-period flat?
if len(ev) >= 6:
    pre = s2[s2["rel"] < 0]
    if len(pre) > 3:
        slope = np.polyfit(pre["rel"], pre["ln_hhi"], 1)[0]
        print("  pre-trend slope = %+.4f per year (should be ~0 for valid design)"
              % slope)

# ---------- C4 ----------
hr("C4. Oster delta bound")
d = p.dropna(subset=["hhi", "stri", "ln_size", "ln_gdp", "inet"]).copy()
short = smf.ols("ln_hhi ~ stri", data=d).fit()
long_ = smf.ols("ln_hhi ~ stri + ln_size + ln_gdp + inet", data=d).fit()
b0, r0 = float(short.params["stri"]), float(short.rsquared)
b1_, r1 = float(long_.params["stri"]), float(long_.rsquared)
r_max = min(1.0, 1.3 * r1)
oster = {"n": int(long_.nobs), "b_short": round(b0, 4), "r2_short": round(r0, 4),
         "b_long": round(b1_, 4), "r2_long": round(r1, 4), "r_max": round(r_max, 4)}
if abs(b1_ - b0) > 1e-9:
    oster["delta"] = round((b1_ * (r1 - r0)) / ((b0 - b1_) * (r_max - r1)), 2)
    oster["interpretation"] = ("delta>1: unobservables would need to be that many times "
                               "stronger than observables to overturn the sign")
print(json.dumps(oster, indent=2))
pd.DataFrame([oster]).to_csv(INTEG / "unctad_C4_oster.csv", index=False,
                             encoding="utf-8-sig")
print("\ndone.")
