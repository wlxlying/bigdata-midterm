# -*- coding: utf-8 -*-
"""Econometric layer for the report.

Models (the specifications used in the report):
  A1  two-way fixed effects OLS, country-clustered SE      -> baseline
  A2  fractional response (logit QMLE) on HHI/10000        -> bounded-DV robustness
  B1  HHI two-margin decomposition  lnHHI = -lnN + ln(1+CV^2)
  C2  event study around policy-change years
  C3  placebo on non-digital service categories
  C4  Oster (2019) delta-bound sensitivity
  D1  K-means + silhouette
  D2  hierarchical clustering (Ward) + cophenetic correlation
  D4  DBSCAN outlier detection
All outputs land in data/integrated for the report tables.
"""
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
from scipy.cluster.hierarchy import cophenet, fcluster, linkage
from scipy.spatial.distance import pdist
from sklearn.cluster import DBSCAN, KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

ROOT = Path(r"d:/HuaweiMoveData/Users/wlx/Desktop") / "\u6570\u636e\u9a71\u52a8" / "midterm_project"
RAW = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "cleaned"
INTEG = ROOT / "data" / "integrated"
OUT = {}


def hr(t):
    print("\n" + "=" * 68)
    print(t)
    print("=" * 68)


# ---------------- assemble panel ----------------
hr("0. assemble country-year panel")
hhi = pd.read_csv(CLEAN / "batis_hhi_panel_2014_2024.csv", dtype={"iso2": str})
print("concentration panel: %d rows, %d countries" % (len(hhi), hhi["iso2"].nunique()))

stri = pd.read_csv(RAW / "oecd_digital_stri.csv")
s = stri[stri["MEASURE"] == "STRI"][["REF_AREA", "TIME_PERIOD", "OBS_VALUE"]].rename(
    columns={"REF_AREA": "iso3", "TIME_PERIOD": "year", "OBS_VALUE": "stri"})

iso = pd.read_csv(INTEG / "_iso3_to_iso2.csv", dtype=str)
i2to3 = dict(zip(iso["iso2"], iso["iso3"]))
i3to2 = dict(zip(iso["iso3"], iso["iso2"]))
hhi["iso3"] = hhi["iso2"].map(i2to3)

wdi = pd.read_csv(RAW / "WDI_country_panel_2014_2025.csv", dtype={"iso3": str})
wdi = wdi[["iso3", "year", "gdp_usd", "population", "internet_users_pct",
           "trade_gdp_pct", "services_exports_usd"]]

reg = pd.read_csv(INTEG / "regulatory_domain_index.csv", dtype={"Country_code": str})
reg = reg.rename(columns={"Country_code": "iso3"})
regcols = ["iso3", "year", "DG.1", "DG.2", "DG.3", "DG.4", "DG.5", "reg_index_w"]

p = (hhi.merge(s, on=["iso3", "year"], how="left")
        .merge(wdi, on=["iso3", "year"], how="left")
        .merge(reg[regcols], on=["iso3", "year"], how="left"))

p["ln_size"] = np.log(p["total_musd"].clip(lower=0.01))
p["ln_gdp"] = np.log(pd.to_numeric(p["gdp_usd"], errors="coerce").clip(lower=1))
p["inet"] = pd.to_numeric(p["internet_users_pct"], errors="coerce")
p["trade_open"] = pd.to_numeric(p["trade_gdp_pct"], errors="coerce")
p["hhi_share"] = (p["hhi"] / 10000).clip(1e-6, 1 - 1e-6)
p["ln_hhi"] = np.log(p["hhi"].clip(lower=1))
p["ln_n"] = np.log(p["n_partners"])
p["ln_cv"] = np.log(1 + p["cv"] ** 2)

p.to_csv(INTEG / "panel_regression.csv", index=False, encoding="utf-8-sig")
print("merged panel: %d rows, %d countries, %d years"
      % (len(p), p["iso2"].nunique(), p["year"].nunique()))
print("coverage: hhi %d, stri %d, gdp %d, reg_index %d"
      % (p["hhi"].notna().sum(), p["stri"].notna().sum(),
         p["gdp_usd"].notna().sum(), p["reg_index_w"].notna().sum()))

est = p.dropna(subset=["hhi", "stri", "ln_size"]).copy()
print("estimation sample: %d obs, %d countries" % (len(est), est["iso2"].nunique()))

# ---------------- A1: two-way FE ----------------
hr("A1. two-way fixed effects (country + year), clustered SE")
rows = []
specs = [
    ("(1) STRI only", "hhi ~ stri", []),
    ("(2) + size", "hhi ~ stri + ln_size", []),
    ("(3) + GDP, internet", "hhi ~ stri + ln_size + ln_gdp + inet", []),
    ("(4) + trade openness", "hhi ~ stri + ln_size + ln_gdp + inet + trade_open", []),
]
for label, formula, _ in specs:
    d = est.dropna(subset=[v for v in ["stri", "ln_size", "ln_gdp", "inet", "trade_open"]
                           if v in formula])
    if len(d) < 60:
        continue
    m = smf.ols(formula + " + C(iso2) + C(year)", data=d).fit(
        cov_type="cluster", cov_kwds={"groups": d["iso2"]})
    rows.append({
        "model": label, "n": int(m.nobs), "countries": d["iso2"].nunique(),
        "r2_within": round(float(m.rsquared), 3),
        "b_stri": round(float(m.params["stri"]), 1),
        "se_stri": round(float(m.bse["stri"]), 1),
        "t_stri": round(float(m.tvalues["stri"]), 2),
        "p_stri": round(float(m.pvalues["stri"]), 3),
        "ci_low": round(float(m.conf_int().loc["stri", 0]), 1),
        "ci_high": round(float(m.conf_int().loc["stri", 1]), 1),
    })
    print("  %-24s n=%3d R2=%.3f  b=%8.1f (se %.1f) t=%+.2f p=%.3f"
          % (label, m.nobs, m.rsquared, m.params["stri"], m.bse["stri"],
             m.tvalues["stri"], m.pvalues["stri"]))
a1 = pd.DataFrame(rows)
a1.to_csv(INTEG / "model_A1_twoway_fe.csv", index=False, encoding="utf-8-sig")
OUT["A1"] = rows

# ---------------- A2: fractional response ----------------
hr("A2. fractional response model on HHI/10000 (logit QMLE)")
try:
    d = est.dropna(subset=["hhi_share", "stri", "ln_size", "ln_gdp", "inet"])
    f = smf.glm("hhi_share ~ stri + ln_size + ln_gdp + inet + C(iso2) + C(year)",
                data=d, family=sm.families.Binomial()).fit(
        cov_type="cluster", cov_kwds={"groups": d["iso2"]})
    print("  n=%d  b(stri)=%.4f  se=%.4f  z=%+.2f  p=%.3f"
          % (f.nobs, f.params["stri"], f.bse["stri"], f.tvalues["stri"], f.pvalues["stri"]))
    # average marginal effect
    from statsmodels.stats.weightstats import DescrStatsW
    mfx = f.get_margeff(at="overall")
    print("  average marginal effect on HHI/10000: %.5f (se %.5f)"
          % (mfx.margeff[list(f.params.index).index("stri")],
             mfx.margeff_se[list(f.params.index).index("stri")]))
    pd.DataFrame([{
        "model": "A2 fractional logit", "n": int(f.nobs),
        "b_stri": round(float(f.params["stri"]), 4),
        "se": round(float(f.bse["stri"]), 4),
        "z": round(float(f.tvalues["stri"]), 2),
        "p": round(float(f.pvalues["stri"]), 3),
        "ame": round(float(mfx.margeff[list(f.params.index).index("stri")]), 5),
    }]).to_csv(INTEG / "model_A2_fractional.csv", index=False, encoding="utf-8-sig")
except Exception as e:
    print("  A2 failed:", type(e).__name__, e)

# ---------------- B1: two-margin decomposition ----------------
hr("B1. HHI decomposition: ln(HHI) = -ln(N) + ln(1+CV^2)")
d = p.dropna(subset=["ln_hhi", "ln_n", "ln_cv", "stri"])
print("  identity check: max |recon - lnHHI| = %.8f"
      % float(((-d["ln_n"] + d["ln_cv"]) - d["ln_hhi"]).abs().max()))

b1 = []
for dep, name in [("ln_n", "extensive margin (partner count)"),
                  ("ln_cv", "intensive margin (dispersion)"),
                  ("ln_hhi", "total concentration")]:
    dd = d.dropna(subset=[dep, "stri"])
    if len(dd) < 60:
        continue
    m = smf.ols("%s ~ stri + ln_size + ln_gdp + C(iso2) + C(year)" % dep, data=dd).fit(
        cov_type="cluster", cov_kwds={"groups": dd["iso2"]})
    b1.append({"margin": name, "dep": dep, "n": int(m.nobs),
               "b_stri": round(float(m.params["stri"]), 3),
               "se": round(float(m.bse["stri"]), 3),
               "t": round(float(m.tvalues["stri"]), 2),
               "p": round(float(m.pvalues["stri"]), 3)})
    print("  %-38s b=%+.3f (se %.3f) t=%+.2f p=%.3f"
          % (name, m.params["stri"], m.bse["stri"], m.tvalues["stri"], m.pvalues["stri"]))
pd.DataFrame(b1).to_csv(INTEG / "model_B1_decomposition.csv", index=False,
                        encoding="utf-8-sig")

# variance share of each margin
vd = d[["ln_n", "ln_cv", "ln_hhi"]].var()
print("\n  variance shares (of ln HHI):")
print("    var(lnHHI)=%.3f  var(-lnN)=%.3f (%.1f%%)  var(ln(1+CV2))=%.3f (%.1f%%)"
      % (vd["ln_hhi"], vd["ln_n"], vd["ln_n"] / vd["ln_hhi"] * 100,
         vd["ln_cv"], vd["ln_cv"] / vd["ln_hhi"] * 100))

print("\nA1/A2/B1 done.")
