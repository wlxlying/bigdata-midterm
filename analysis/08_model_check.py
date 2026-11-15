# -*- coding: utf-8 -*-
"""Reproduce the specifications behind the saved regression tables."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

ROOT = Path(r"d:/HuaweiMoveData/Users/wlx/Desktop") / "\u6570\u636e\u9a71\u52a8" / "midterm_project"
INTEG = ROOT / "data" / "integrated"
RAW = ROOT / "data" / "raw"
POL = ROOT / "policy_raw"


def fit_row(label, model, term="stri"):
    return {
        "label": label,
        "n": int(model.nobs),
        "b": round(float(model.params[term]), 4),
        "se": round(float(model.bse[term]), 4),
        "p": round(float(model.pvalues[term]), 4),
        "r2": round(float(model.rsquared), 4),
    }


def oster(b_s, r_s, b_l, r_l, factor=1.3):
    r_max = min(1.0, factor * r_l)
    denom = (b_s - b_l) * (r_max - r_l)
    if denom == 0:
        return None
    return round(float(b_l * (r_l - r_s) / denom), 3)


def main():
    u = pd.read_csv(INTEG / "unctad_panel_regression.csv")
    d = u[u["cat"] == "SI2"].dropna(
        subset=["hhi", "stri", "ln_hhi", "ln_n", "ln_cv_term", "ln_size", "ln_gdp", "inet", "trade_open", "iso3", "year"]
    ).copy()
    d["share"] = d["hhi"] / 10000.0
    d["year"] = d["year"].astype(int)
    rows = []
    m1 = smf.ols("hhi ~ stri + C(iso3) + C(year)", data=d).fit(
        cov_type="cluster", cov_kwds={"groups": d["iso3"]}
    )
    rows.append(fit_row("FE hhi, cluster country", m1))
    m4 = smf.ols(
        "hhi ~ stri + ln_size + ln_gdp + inet + trade_open + C(iso3) + C(year)", data=d
    ).fit(cov_type="cluster", cov_kwds={"groups": d["iso3"]})
    rows.append(fit_row("FE hhi + controls", m4))
    for dep in ("ln_hhi", "ln_n", "ln_cv_term"):
        m = smf.ols(dep + " ~ stri + C(iso3) + C(year)", data=d).fit(
            cov_type="cluster", cov_kwds={"groups": d["iso3"]}
        )
        rows.append(fit_row("FE " + dep, m))
    formulas = [
        "ln_hhi ~ stri",
        "ln_hhi ~ stri + ln_gdp + inet + trade_open",
        "ln_hhi ~ stri + ln_size",
        "ln_hhi ~ stri + ln_gdp + inet + trade_open + C(year)",
        "ln_hhi ~ stri + C(year)",
        "ln_hhi ~ stri + reg_index_w",
        "ln_hhi ~ stri + ln_size + ln_gdp + inet + trade_open + C(year)",
    ]
    # reg_index may be missing on some rows
    d2 = d.dropna(subset=["reg_index_w"])
    long_grid = []
    for fml in formulas:
        data = d2 if "reg_index_w" in fml else d
        m = smf.ols(fml, data=data).fit()
        item = fit_row(fml, m)
        short = smf.ols("ln_hhi ~ stri", data=data).fit()
        item["delta_13"] = oster(short.params["stri"], short.rsquared, m.params["stri"], m.rsquared)
        item["n"] = int(m.nobs)
        long_grid.append(item)

    import statsmodels.api as sm
    frac = smf.glm(
        "share ~ stri + ln_size + ln_gdp + inet + trade_open",
        data=d,
        family=sm.families.Binomial(),
    ).fit(cov_type="cluster", cov_kwds={"groups": d["iso3"]})
    ame = float(np.mean(frac.predict(d) * (1 - frac.predict(d)) * frac.params["stri"]))

    # BaTiS panel if present
    batis_rows = []
    p = pd.read_csv(INTEG / "panel_regression.csv")
    need = ["hhi", "stri", "ln_hhi", "iso3", "year"]
    # column detection
    cols = list(p.columns)
    batis_info = {"columns_head": cols[:12], "rows": int(len(p))}

    sizes = {}
    for child in RAW.iterdir():
        if child.is_file():
            sizes[child.name] = child.stat().st_size
        elif child.is_dir():
            sizes[child.name + "/"] = sum(f.stat().st_size for f in child.rglob("*") if f.is_file())
    pol = {}
    for f in POL.rglob("*"):
        if f.is_file():
            pol[str(f.relative_to(POL)).replace("\\", "/")] = f.stat().st_size

    cl = pd.read_csv(INTEG / "model_D_clusters.csv")
    cl = cl[cl["year"] == 2024]
    panel = pd.read_csv(INTEG / "analysis_panel_full.csv")
    merged = cl.merge(panel[["iso2", "total24"]], on="iso2", how="left")
    km = []
    for lab, g in merged.groupby("km_label"):
        km.append({
            "km": int(lab),
            "n": int(len(g)),
            "hhi": round(float(g["hhi"].mean()), 1),
            "stri": round(float(g["stri"].mean()), 3),
            "total_median": round(float(g["total24"].median()), 1),
        })
    out_rows = merged[merged["dbscan_label"] == -1][
        ["iso2", "hhi", "stri", "cr5", "total24"]
    ].sort_values("hhi", ascending=False)
    outliers = [
        {
            "iso2": r.iso2,
            "hhi": round(float(r.hhi), 1),
            "stri": round(float(r.stri), 3),
            "total": None if pd.isna(r.total24) else round(float(r.total24), 1),
        }
        for r in out_rows.itertuples(index=False)
    ]

    grad = pd.read_csv(INTEG / "category_gradient.csv")
    gp = []
    for r in grad.itertuples(index=False):
        if r.n > 3 and abs(r.pearson) < 1:
            t = r.pearson * np.sqrt((r.n - 2) / (1 - r.pearson ** 2))
            pval = 2 * stats.t.sf(abs(t), r.n - 2)
        else:
            pval = None
        gp.append({"cat": r.cat, "n": int(r.n), "r": float(r.pearson), "p": None if pval is None else round(float(pval), 4)})

    placebo = pd.read_csv(INTEG / "placebo_service_categories.csv")
    pp = []
    for r in placebo.itertuples(index=False):
        t = r.r * np.sqrt((r.n - 2) / (1 - r.r ** 2))
        pval = 2 * stats.t.sf(abs(t), r.n - 2)
        pp.append({"item": r.item, "n": int(r.n), "r": float(r.r), "p": round(float(pval), 4)})

    # five-country 2024 from concentration file
    top = pd.read_csv(INTEG / "concentration_top5.csv")
    top24 = top[top["year"] == 2024][["exporter", "total", "hhi", "cr5", "n_partners"]]

    result = {
        "fe": rows,
        "long_grid": long_grid,
        "fractional": {
            "b": round(float(frac.params["stri"]), 4),
            "se": round(float(frac.bse["stri"]), 4),
            "p": round(float(frac.pvalues["stri"]), 4),
            "ame": round(ame, 5),
            "n": int(frac.nobs),
        },
        "batis_info": batis_info,
        "sizes": sizes,
        "policy_bytes": pol,
        "km": km,
        "outliers": outliers,
        "gradient_p": gp,
        "placebo_p": pp,
        "top24": top24.to_dict(orient="records"),
        "n_countries_fe": int(d["iso3"].nunique()),
        "year_min": int(d["year"].min()),
        "year_max": int(d["year"].max()),
    }
    dest = INTEG / "model_check.json"
    dest.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "fe": rows,
        "long_grid": long_grid,
        "fractional": result["fractional"],
        "km": km,
        "outliers": outliers,
        "gradient_p": gp,
        "placebo_p": pp,
        "sizes_mb": {k: round(v / 1048576, 1) for k, v in sizes.items()},
        "policy_kb": {k: round(v / 1024, 1) for k, v in pol.items()},
        "n": result["n_countries_fe"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
