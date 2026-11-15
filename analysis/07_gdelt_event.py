# -*- coding: utf-8 -*-
"""GDELT window around India's DPDP passage, plus numbers the report cites."""
import csv
import io
import json
import zipfile
from collections import Counter, defaultdict
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
RAW = ROOT / "data" / "raw"
GDIR = RAW / "gdelt"
INTEG = ROOT / "data" / "integrated"
CLEAN = ROOT / "data" / "cleaned"
VIS = ROOT / "visualization"
VIS.mkdir(parents=True, exist_ok=True)

NARROW = ("dpdp", "dpdpa", "digital-personal", "digitalpersonal", "personal-data-protection")
MID = NARROW + ("data-protection", "dataprotection", "privacy-bill", "privacybill")
BROAD = MID + ("privacy", "personal-data", "personaldata")


def classify(url):
    u = (url or "").lower()
    if any(k in u for k in NARROW):
        return 2
    if any(k in u for k in MID):
        return 1
    if any(k in u for k in BROAD):
        return 0
    return -1


def scan_gdelt():
    files = sorted(GDIR.glob("*.zip"))
    daily = {}
    domains = Counter()
    roots = Counter()
    sqldates = Counter()
    total_rows = 0
    short_rows = 0
    sample = None
    for zp in files:
        day_key = zp.name[:8]
        bucket = {
            "file": zp.name,
            "rows": 0,
            "in_geo": 0,
            "in_any": 0,
            "narrow": 0,
            "mid": 0,
            "broad": 0,
            "narrow_articles": 0,
            "narrow_tone_sum": 0.0,
            "narrow_tone_n": 0,
            "in_tone_sum": 0.0,
            "in_tone_n": 0,
        }
        with zipfile.ZipFile(zp) as zf:
            names = [n for n in zf.namelist() if not n.endswith("/")]
            with zf.open(names[0]) as fh:
                text = io.TextIOWrapper(fh, encoding="utf-8", errors="replace", newline="")
                reader = csv.reader(text, delimiter="\t")
                for row in reader:
                    total_rows += 1
                    bucket["rows"] += 1
                    if len(row) < 58:
                        short_rows += 1
                        continue
                    if sample is None:
                        sample = {
                            "ncols": len(row),
                            "day": row[1],
                            "a1": row[7],
                            "a2": row[17],
                            "root": row[28],
                            "geo": row[51],
                            "url": row[57][:160],
                        }
                    geo = row[51]
                    a1 = row[7]
                    a2 = row[17]
                    india = geo == "IN" or a1 in ("IN", "IND") or a2 in ("IN", "IND")
                    if a1 == "IND" or a2 == "IND":
                        bucket["ind_actor"] = bucket.get("ind_actor", 0) + 1
                    if geo == "IN":
                        bucket["in_geo"] += 1
                        try:
                            bucket["in_tone_sum"] += float(row[34])
                            bucket["in_tone_n"] += 1
                        except ValueError:
                            pass
                    if not india:
                        continue
                    bucket["in_any"] += 1
                    level = classify(row[57])
                    if level >= 0:
                        bucket["broad"] += 1
                    if level >= 1:
                        bucket["mid"] += 1
                    if level >= 2:
                        bucket["narrow"] += 1
                        try:
                            bucket["narrow_articles"] += int(float(row[33]))
                        except ValueError:
                            pass
                        try:
                            bucket["narrow_tone_sum"] += float(row[34])
                            bucket["narrow_tone_n"] += 1
                        except ValueError:
                            pass
                        host = row[57].split("/")[2] if row[57].startswith("http") and len(row[57].split("/")) > 2 else ""
                        if host:
                            domains[host.lower()] += 1
                        roots[row[28]] += 1
                        sqldates[row[1]] += 1
        daily[day_key] = bucket
    return files, daily, domains, roots, sqldates, total_rows, short_rows, sample


def write_gdelt(daily, domains, roots, sqldates):
    path = INTEG / "gdelt_india_daily.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow([
            "day", "rows", "in_geo", "in_any", "broad", "mid", "narrow",
            "narrow_articles", "narrow_tone", "in_tone",
        ])
        for day in sorted(daily):
            b = daily[day]
            nt = b["narrow_tone_sum"] / b["narrow_tone_n"] if b["narrow_tone_n"] else ""
            it = b["in_tone_sum"] / b["in_tone_n"] if b["in_tone_n"] else ""
            w.writerow([
                day, b["rows"], b["in_geo"], b["in_any"], b["broad"], b["mid"],
                b["narrow"], b["narrow_articles"], nt, it,
            ])
    dom_path = INTEG / "gdelt_india_domains.csv"
    with dom_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["domain", "narrow_events"])
        for host, n in domains.most_common(25):
            w.writerow([host, n])
    root_path = INTEG / "gdelt_india_cameo.csv"
    with root_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["event_root", "narrow_events"])
        for code, n in roots.most_common():
            w.writerow([code, n])
    sql_path = INTEG / "gdelt_india_sqldate.csv"
    with sql_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["sqldate", "narrow_events"])
        for day, n in sorted(sqldates.items()):
            w.writerow([day, n])


def draw(daily):
    days = sorted(daily)
    labels = [d[4:6] + "-" + d[6:8] for d in days]
    in_geo = [daily[d]["in_geo"] for d in days]
    narrow = [daily[d]["narrow"] for d in days]
    mid = [daily[d]["mid"] for d in days]
    x = np.arange(len(days))
    fig, ax = plt.subplots(figsize=(10.2, 5.4))
    ax.bar(x, in_geo, color="#c5cdd6", width=0.72, label="\u884c\u52a8\u5730\u5728\u5370\u5ea6\u7684\u5168\u90e8\u4e8b\u4ef6")
    ax2 = ax.twinx()
    ax2.plot(x, mid, color="#1f4e79", marker="o", linewidth=1.8, label="\u6570\u636e\u4fdd\u62a4\u7c7b\u94fe\u63a5")
    ax2.plot(x, narrow, color="#9c2f2f", marker="s", linewidth=1.8, label="\u6cd5\u6848\u4e13\u540d\u94fe\u63a5")
    for mark, text in (("20230807", "\u4eba\u6c11\u9662\u901a\u8fc7"), ("20230809", "\u8054\u90a6\u9662\u901a\u8fc7")):
        if mark in days:
            i = days.index(mark)
            ax.axvline(i, color="#9c2f2f", linestyle="--", linewidth=0.8, alpha=0.7)
            ax.text(i, max(in_geo) * 0.98, text, rotation=90, va="top", ha="right", fontsize=8, color="#9c2f2f")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_ylabel("\u4e8b\u4ef6\u6761\u6570")
    ax2.set_ylabel("\u542b\u5173\u952e\u8bcd\u7684\u4e8b\u4ef6\u6761\u6570")
    ax.set_title(
        "\u5370\u5ea6\u300a\u6570\u5b57\u4e2a\u4eba\u6570\u636e\u4fdd\u62a4\u6cd5\u300b\u901a\u8fc7\u90a3\u4e00\u5468\uff0c\u6570\u636e\u4fdd\u62a4\u62a5\u9053\u6709\u6ca1\u6709\u62ac\u5347\uff1f\n"
        "GDELT \u65e5\u6587\u4ef6 2023-07-22 \u81f3 2023-08-14\uff0c\u7f3a 07-24\u300107-25\u300107-27\u300108-01",
        fontsize=12,
    )
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper left", frameon=False, fontsize=8)
    fig.text(
        0.01, 0.01,
        "\u5355\u4f4d\uff1a\u4e8b\u4ef6\u6761\u6570\u3002\u6765\u6e90\uff1aGDELT 2.0 \u65e5\u5ea6\u4e8b\u4ef6\u5e93\u3002"
        "\u7b5b\u9009\uff1a\u884c\u52a8\u5730\u4e3a\u5370\u5ea6\uff0c\u6216\u53c2\u4e0e\u65b9\u4e3a IND\u3002"
        "\u4e13\u540d\u94fe\u63a5\u542b dpdp / digital-personal / personal-data-protection\uff1b"
        "\u6570\u636e\u4fdd\u62a4\u7c7b\u53e6\u542b data-protection\u3002"
        "\u7f3a\u65e5\u4e0d\u4ee5 0 \u586b\u5145\u3002",
        fontsize=7.5, color="#333333",
    )
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    out = VIS / "fig12_gdelt_dpdp.png"
    fig.savefig(out, dpi=160)
    plt.close()
    return str(out)


def ols_r2(y, X):
    y = np.asarray(y, dtype=float)
    X = np.asarray(X, dtype=float)
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    X = np.column_stack([np.ones(len(X)), X])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    fitted = X @ beta
    ss_res = np.sum((y - fitted) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot else np.nan
    return float(beta[1]), float(r2)


def verify():
    out = {}
    sizes = []
    for p in RAW.rglob("*"):
        if p.is_file():
            sizes.append((str(p.relative_to(RAW)).replace("\\", "/"), p.stat().st_size))
    out["raw_files"] = sizes
    out["raw_bytes"] = int(sum(s for _, s in sizes))

    clean_rows = {}
    for p in list(CLEAN.glob("*.csv")) + list(INTEG.glob("*.csv")):
        with p.open("rb") as fh:
            n = sum(1 for _ in fh) - 1
        clean_rows[p.name] = n
    out["table_rows"] = {k: clean_rows[k] for k in sorted(clean_rows)}

    u = pd.read_csv(INTEG / "unctad_panel_regression.csv")
    si = u[u["cat"] == "SI2"].copy()
    out["unctad_si2_rows_regfile"] = int(len(si))
    out["unctad_si2_countries"] = int(si["iso3"].nunique())
    out["unctad_si2_years"] = [int(si["year"].min()), int(si["year"].max())]
    out["unctad_partner_median"] = float(si["n_partners"].median())
    out["unctad_hhi_median"] = float(si["hhi"].median())

    # identity
    ident = si["ln_hhi"] + si["ln_n"] - si["ln_cv_term"]
    out["identity_max_abs"] = float(np.nanmax(np.abs(ident)))

    d = si.dropna(subset=["hhi", "stri", "ln_size", "ln_gdp", "inet", "trade_open", "ln_hhi", "ln_n", "ln_cv_term"]).copy()
    out["unctad_complete_n"] = int(len(d))
    out["unctad_complete_countries"] = int(d["iso3"].nunique())

    specs = {
        "hhi": d["hhi"],
        "hhi_000": d["hhi"] / 1000.0,
        "share": d["hhi"] / 10000.0,
        "ln_hhi": d["ln_hhi"],
        "z": (d["hhi"] - d["hhi"].mean()) / d["hhi"].std(ddof=0),
    }
    matches = []
    ctrl = d[["ln_size", "ln_gdp", "inet", "trade_open"]].to_numpy()
    for name, y in specs.items():
        b, r2 = ols_r2(y, d["stri"])
        Xlong = np.column_stack([d["stri"].to_numpy(), ctrl])
        # coefficient on first slope after intercept is recomputed below
        X = np.column_stack([np.ones(len(d)), Xlong])
        beta, *_ = np.linalg.lstsq(X, np.asarray(y, float), rcond=None)
        fitted = X @ beta
        yy = np.asarray(y, float)
        r2l = 1 - np.sum((yy - fitted) ** 2) / np.sum((yy - yy.mean()) ** 2)
        matches.append({
            "y": name, "b_short": round(b, 4), "r2_short": round(r2, 4),
            "b_long": round(float(beta[1]), 4), "r2_long": round(float(r2l), 4),
        })
    out["oster_grid"] = matches

    # margins covariance on the regression sample
    a = -d["ln_n"].to_numpy()
    b = d["ln_cv_term"].to_numpy()
    t = d["ln_hhi"].to_numpy()
    out["var_ext"] = float(np.var(a, ddof=0))
    out["var_int"] = float(np.var(b, ddof=0))
    out["var_tot"] = float(np.var(t, ddof=0))
    out["cov_2"] = float(2 * np.cov(a, b, ddof=0)[0, 1])

    panel = pd.read_csv(INTEG / "analysis_panel_full.csv")
    out["panel_n"] = int(len(panel))
    sub = panel.dropna(subset=["stri2024", "reg_index_w"])
    out["reg_vs_stri_n"] = int(len(sub))
    out["reg_vs_stri_pearson"] = float(sub["stri2024"].corr(sub["reg_index_w"]))
    india = panel[panel["iso2"] == "IN"]
    if len(india):
        row = india.iloc[0]
        out["india_panel"] = {
            "hhi14": float(row["hhi14"]), "hhi24": float(row["hhi24"]),
            "stri2014": float(row["stri2014"]), "stri2024": float(row["stri2024"]),
            "total14": float(row["total14"]), "total24": float(row["total24"]),
            "cr514": float(row["cr514"]), "cr524": float(row["cr524"]),
        }

    cl = pd.read_csv(INTEG / "model_D_clusters.csv")
    cl24 = cl[cl["year"] == 2024]
    profiles = []
    for lab, g in cl24.groupby("km_label"):
        profiles.append({
            "km": int(lab), "n": int(len(g)),
            "hhi": round(float(g["hhi"].mean()), 1),
            "stri": round(float(g["stri"].mean()), 3),
            "cr5": round(float(g["cr5"].mean()), 1),
        })
    out["km_profiles"] = profiles
    out["dbscan_outliers"] = sorted(cl24.loc[cl24["dbscan_label"] == -1, "iso2"].astype(str).tolist())

    stri = pd.read_csv(RAW / "oecd_digital_stri.csv")
    ind = stri[(stri["REF_AREA"] == "IND") & (stri["STRI_TYPE"] == "DIGITAL")]
    out["india_stri_measures"] = sorted(ind["MEASURE"].astype(str).unique().tolist())[:12]
    head = ind[ind["MEASURE"] == ind["MEASURE"].iloc[0]] if len(ind) else ind
    # prefer a single series: the modal measure with 2014 and 2024
    series = {}
    for measure, g in ind.groupby("MEASURE"):
        s = g.drop_duplicates("TIME_PERIOD").set_index("TIME_PERIOD")["OBS_VALUE"].astype(float)
        if 2014 in s.index and 2024 in s.index:
            series[str(measure)] = {str(int(k)): round(float(v), 4) for k, v in s.items() if 2014 <= int(k) <= 2024}
    out["india_stri_series_keys"] = list(series)[:8]
    # pick the series whose 2024 value is closest to panel stri2024 if available
    target = out.get("india_panel", {}).get("stri2024")
    best_key, best_gap = None, 99
    for k, s in series.items():
        if target is None or "2024" not in s:
            continue
        gap = abs(s["2024"] - target)
        if gap < best_gap:
            best_key, best_gap = k, gap
    out["india_stri_used"] = best_key
    out["india_stri_gap"] = None if best_key is None else round(best_gap, 6)
    out["india_stri_path"] = series.get(best_key, {})

    # jumps
    if best_key:
        path = series[best_key]
        years = sorted(int(y) for y in path)
        jumps = []
        for a, b in zip(years, years[1:]):
            delta = path[str(b)] - path[str(a)]
            if abs(delta) >= 0.05:
                jumps.append({"from": a, "to": b, "delta": round(delta, 4)})
        out["india_stri_jumps_005"] = jumps

    return out


def main():
    files, daily, domains, roots, sqldates, total_rows, short_rows, sample = scan_gdelt()
    write_gdelt(daily, domains, roots, sqldates)
    fig = draw(daily)
    summary = {
        "n_files": len(files),
        "files": [p.name for p in files],
        "total_rows": total_rows,
        "short_rows": short_rows,
        "sample": sample,
        "daily": {
            d: {
                "rows": daily[d]["rows"],
                "in_geo": daily[d]["in_geo"],
                "narrow": daily[d]["narrow"],
                "mid": daily[d]["mid"],
                "broad": daily[d]["broad"],
                "narrow_tone": (
                    round(daily[d]["narrow_tone_sum"] / daily[d]["narrow_tone_n"], 3)
                    if daily[d]["narrow_tone_n"] else None
                ),
            }
            for d in sorted(daily)
        },
        "narrow_total": int(sum(daily[d]["narrow"] for d in daily)),
        "mid_total": int(sum(daily[d]["mid"] for d in daily)),
        "broad_total": int(sum(daily[d]["broad"] for d in daily)),
        "in_geo_total": int(sum(daily[d]["in_geo"] for d in daily)),
        "top_domains": domains.most_common(12),
        "top_roots": roots.most_common(8),
        "figure": fig,
    }
    summary["verify"] = verify()
    dest = INTEG / "gdelt_report_numbers.json"
    dest.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "rows": total_rows,
        "files": len(files),
        "narrow": summary["narrow_total"],
        "mid": summary["mid_total"],
        "in_geo": summary["in_geo_total"],
        "ind_actor": int(sum(daily[d].get("ind_actor", 0) for d in daily)),
        "sqldate_top": sqldates.most_common(12),
        "sample": sample,
        "daily_narrow": {d: summary["daily"][d]["narrow"] for d in summary["daily"]},
        "daily_mid": {d: summary["daily"][d]["mid"] for d in summary["daily"]},
        "daily_in": {d: summary["daily"][d]["in_geo"] for d in summary["daily"]},
        "domains": summary["top_domains"][:8],
        "roots": summary["top_roots"],
        "oster_grid": summary["verify"]["oster_grid"],
        "identity": summary["verify"]["identity_max_abs"],
        "reg_corr": summary["verify"].get("reg_vs_stri_pearson"),
        "india": summary["verify"].get("india_panel"),
        "india_stri": summary["verify"].get("india_stri_path"),
        "india_jumps": summary["verify"].get("india_stri_jumps_005"),
        "km": summary["verify"].get("km_profiles"),
        "outliers": summary["verify"].get("dbscan_outliers"),
        "complete": summary["verify"].get("unctad_complete_n"),
        "countries": summary["verify"].get("unctad_complete_countries"),
        "partner_median": summary["verify"].get("unctad_partner_median"),
        "raw_gb": round(summary["verify"]["raw_bytes"] / 1024**3, 3),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
