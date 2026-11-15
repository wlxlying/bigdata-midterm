# -*- coding: utf-8 -*-
"""Econometrics on the UNCTAD caliber (chosen for reported-value validity).

Same model set as before, re-estimated on the reported-value panel:
  A1 two-way FE OLS (country + year), country-clustered SE
  A2 fractional response (logit QMLE) on HHI share
  B1 two-margin decomposition ln(HHI) = -lnN + ln(1+CV^2)
  C2 event study around large STRI jumps
  C4 Oster delta bounds
"""
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats

warnings.filterwarnings("ignore")

ROOT = Path(r"d:/HuaweiMoveData/Users/wlx/Desktop") / "\u6570\u636e\u9a71\u52a8" / "midterm_project"
RAW = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "cleaned"
INTEG = ROOT / "data" / "integrated"


def hr(t):
    print("\n" + "=" * 70)
    print(t)
    print("=" * 70)


# ---------- assemble ----------
hr("0. assemble UNCTAD panel with policy and controls")
u = pd.read_csv(CLEAN / "unctad_panel_2014_2024.csv", dtype={"iso3": str})
u = u[(u["cat"] == "SI2") & u["iso3"].notna()]
print("SI2 rows: %d | countries: %d" % (len(u), u["iso3"].nunique()))

stri = pd.read_csv(RAW / "oecd_digital_stri.csv")
s = stri[stri["MEASURE"] == "STRI"][["REF_AREA", "TIME_PERIOD", "OBS_VALUE"]].rename(
    columns={"REF_AREA": "iso3", "TIME_PERIOD": "year", "OBS_VALUE": "stri"})

wdi = pd.read_csv(RAW / "WDI_country_panel_2014_2025.csv", dtype={"iso3": str})[
    ["iso3", "year", "gdp_usd", "population", "internet_users_pct", "trade_gdp_pct"]]

reg = pd.read_csv(INTEG / "regulatory_domain_index.csv", dtype={"Country_code": str}).rename(
    columns={"Country_code": "iso3"})
regcols = ["iso3", "year", "DG.1", "DG.2", "DG.3", "DG.4", "DG.5", "reg_index_w"]

p = (u.merge(s, on=["iso3", "year"], how="left")
      .merge(wdi, on=["iso3", "year"], how="left")
      .merge(reg[regcols], on=["iso3", "year"], how="left"))

p["hhi_share"] = (p["hhi"] / 10000).clip(1e-6, 1 - 1e-6)
p["ln_size"] = np.log(p["total_musd"].clip(lower=0.01))
p["ln_gdp"] = np.log(pd.to_numeric(p["gdp_usd"], errors="coerce").clip(lower=1))
p["inet"] = pd.to_numeric(p["internet_users_pct"], errors="coerce")
p["trade_open"] = pd.to_numeric(p["trade_gdp_pct"], errors="coerce")
p.to_csv(INTEG / "unctad_panel_regression.csv", index=False, encoding="utf-8-sig")

print("merged: %d rows | stri %d | gdp %d | reg %d"
      % (len(p), p["stri"].notna().sum(), p["gdp_usd"].notna().sum(),
         p["reg_index_w"].notna().sum()))
est = p.dropna(subset=["hhi", "stri", "ln_size"]).copy()
print("estimation sample: %d obs | %d countries | %d years"
      % (len(est), est["iso3"].nunique(), est["year"].nunique()))

# ---------- A1 ----------
hr("A1. two-way FE (country + year), clustered SE")
rows = []
for label, formula in [
    ("(1) STRI only", "hhi ~ stri"),
    ("(2) + size", "hhi ~ stri + ln_size"),
    ("(3) + GDP, internet", "hhi ~ stri + ln_size + ln_gdp + inet"),
    ("(4) + trade openness", "hhi ~ stri + ln_size + ln_gdp + inet + trade_open"),
]:
    need = ["stri", "hhi"] + [v for v in ["ln_size", "ln_gdp", "inet", "trade_open"]
                              if v in formula]
    d = est.dropna(subset=need)
    if len(d) < 40 or d["iso3"].nunique() < 8:
        print("  %-24s skipped (n=%d)" % (label, len(d)))
        continue
    m = smf.ols(formula + " + C(iso3) + C(year)", data=d).fit(
        cov_type="cluster", cov_kwds={"groups": d["iso3"]})
    ci = m.conf_int().loc["stri"]
    rows.append({"model": label, "n": int(m.nobs), "countries": d["iso3"].nunique(),
                 "r2": round(float(m.rsquared), 3),
                 "b_stri": round(float(m.params["stri"]), 1),
                 "se": round(float(m.bse["stri"]), 1),
                 "t": round(float(m.tvalues["stri"]), 2),
                 "p": round(float(m.pvalues["stri"]), 3),
                 "ci_low": round(float(ci[0]), 1), "ci_high": round(float(ci[1]), 1)})
    print("  %-24s n=%3d R2=%.3f b=%8.1f (se %.1f) t=%+.2f p=%.3f"
          % (label, m.nobs, m.rsquared, m.params["stri"], m.bse["stri"],
             m.tvalues["stri"], m.pvalues["stri"]))
pd.DataFrame(rows).to_csv(INTEG / "unctad_A1_twoway_fe.csv", index=False,
                          encoding="utf-8-sig")

# cluster-robust with two-way clustering (country and year)
hr("A1b. two-way clustered SE (country and year)")
d = est.dropna(subset=["stri", "ln_size", "ln_gdp", "inet"])
if len(d) >= 40:
    m = smf.ols("hhi ~ stri + ln_size + ln_gdp + inet + C(iso3) + C(year)",
                data=d).fit(cov_type="cluster",
                            cov_kwds={"groups": pd.factorize(
                                d["iso3"].astype(str) + "_" + d["year"].astype(str))[0]})
    print("  b=%.1f  se=%.1f  t=%+.2f  p=%.3f  n=%d"
          % (m.params["stri"], m.bse["stri"], m.tvalues["stri"],
             m.pvalues["stri"], m.nobs))
    pd.DataFrame([{"model": "A1b two-way cluster", "n": int(m.nobs),
                   "b_stri": round(float(m.params["stri"]), 1),
                   "se": round(float(m.bse["stri"]), 1),
                   "t": round(float(m.tvalues["stri"]), 2),
                   "p": round(float(m.pvalues["stri"]), 3)}]).to_csv(
        INTEG / "unctad_A1b_twoway_cluster.csv", index=False, encoding="utf-8-sig")

# ---------- A2 ----------
hr("A2. fractional response (logit QMLE) on HHI share")
d = est.dropna(subset=["hhi_share", "stri", "ln_size", "ln_gdp", "inet"])
if len(d) >= 40:
    f = smf.glm("hhi_share ~ stri + ln_size + ln_gdp + inet + C(iso3) + C(year)",
                data=d, family=sm.families.Binomial()).fit(
        cov_type="cluster", cov_kwds={"groups": d["iso3"]})
    mfx = f.get_margeff(at="overall")
    idx = list(f.params.index).index("stri")
    print("  b=%.4f se=%.4f z=%+.2f p=%.3f | AME=%.5f (se %.5f) n=%d"
          % (f.params["stri"], f.bse["stri"], f.tvalues["stri"], f.pvalues["stri"],
             mfx.margeff[idx], mfx.margeff_se[idx], f.nobs))
    pd.DataFrame([{"model": "A2 fractional logit", "n": int(f.nobs),
                   "b_stri": round(float(f.params["stri"]), 4),
                   "se": round(float(f.bse["stri"]), 4),
                   "z": round(float(f.tvalues["stri"]), 2),
                   "p": round(float(f.pvalues["stri"]), 3),
                   "ame": round(float(mfx.margeff[idx]), 5)}]).to_csv(
        INTEG / "unctad_A2_fractional.csv", index=False, encoding="utf-8-sig")

# ---------- B1 ----------
hr("B1. two-margin decomposition")
chk = p.dropna(subset=["ln_hhi", "ln_n", "ln_cv_term"])
print("  identity max error = %.10f"
      % float(((-chk["ln_n"] + chk["ln_cv_term"]) - chk["ln_hhi"]).abs().max()))

b1 = []
for dep, name in [("ln_n", "extensive margin (partner count)"),
                  ("ln_cv_term", "intensive margin (dispersion)"),
                  ("ln_hhi", "total ln HHI")]:
    d = p.dropna(subset=[dep, "stri", "ln_size", "ln_gdp"])
    if len(d) < 40:
        continue
    m = smf.ols("%s ~ stri + ln_size + ln_gdp + C(iso3) + C(year)", data=d).fit(
        cov_type="cluster", cov_kwds={"groups": d["iso3"]})
    b1.append({"margin": name, "dep": dep, "n": int(m.nobs),
               "b_stri": round(float(m.params["stri"]), 3),
               "se": round(float(m.bse["stri"]), 3),
               "t": round(float(m.tvalues["stri"]), 2),
               "p": round(float(m.pvalues["stri"]), 3)})
    print("  %-36s b=%+.3f (se %.3f) t=%+.2f p=%.3f n=%d"
          % (name, m.params["stri"], m.bse["stri"], m.tvalues["stri"],
             m.pvalues["stri"], m.nobs))
pd.DataFrame(b1).to_csv(INTEG / "unctad_B1_decomposition.csv", index=False,
                        encoding="utf-8-sig")

vd = chk[["ln_n", "ln_cv_term", "ln_hhi"]].var()
print("\n  variance shares of ln(HHI):")
print("    var(lnHHI)=%.3f | var(-lnN)=%.3f (%.1f%%) | var(ln(1+CV2))=%.3f (%.1f%%)"
      % (vd["ln_hhi"], vd["ln_n"], vd["ln_n"] / vd["ln_hhi"] * 100,
         vd["ln_cv_term"], vd["ln_cv_term"] / vd["ln_hhi"] * 100))

# ---------- C2 ----------
hr("C2. event study: STRI jumps >= +0.05")
sv = est[["iso3", "year", "stri", "ln_hhi"]].dropna().sort_values(["iso3", "year"])
sv["d"] = sv.groupby("iso3")["stri"].diff()
ev = sv[sv["d"] >= 0.05].groupby("iso3").first().reset_index()[
    ["iso3", "year", "d"]].rename(columns={"year": "event_year", "d": "jump"})
print("  events: %d" % len(ev))
if len(ev) >= 6:
    s2 = sv.merge(ev[["iso3", "event_year"]], on="iso3").copy()
    s2["rel"] = s2["year"] - s2["event_year"]
    s2 = s2[s2["rel"].between(-3, 3)]
    es = s2.groupby("rel").agg(n=("ln_hhi", "size"), m=("ln_hhi", "mean"),
                               se=("ln_hhi", lambda x: x.std(ddof=1) / np.sqrt(len(x)))
                               ).reset_index()
    base = s2[s2["rel"] < 0]["ln_hhi"].mean()
    es["effect_pct"] = (np.exp(es["m"] - base) - 1) * 100
    print(es.round(2).to_string(index=False))
    es.to_csv(INTEG / "unctad_C2_event_study.csv", index=False, encoding="utf-8-sig")
ev.to_csv(INTEG / "unctad_C2_events.csv", index=False, encoding="utf-8-sig")

# ---------- C4 ----------
hr("C4. Oster delta bound")
d = est.dropna(subset=["hhi", "stri", "ln_size", "ln_gdp", "inet"]).copy()
d["ln_hhi"] = np.log(d["hhi"].clip(lower=1))
short = smf.ols("ln_hhi ~ stri", data=d).fit()
long_ = smf.ols("ln_hhi ~ stri + ln_size + ln_gdp + inet", data=d).fit()
b0, r0 = float(short.params["stri"]), float(short.rsquared)
b1_, r1 = float(long_.params["stri"]), float(long_.rsquared)
r_max = min(1.0, 1.3 * r1)
oster = {"b_short": round(b0, 4), "r2_short": round(r0, 4),
         "b_long": round(b1_, 4), "r2_long": round(r1, 4), "r_max": round(r_max, 4)}
if abs(b1_ - b0) > 1e-9:
    oster["delta"] = round((b1_ * (r1 - r0)) / ((b0 - b1_) * (r_max - r1)), 2)
print(json.dumps(oster, indent=2))
pd.DataFrame([oster]).to_csv(INTEG / "unctad_C4_oster.csv", index=False,
                             encoding="utf-8-sig")

print("\nUNCTAD-caliber estimation complete.")
