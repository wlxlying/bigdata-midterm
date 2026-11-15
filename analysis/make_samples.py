# -*- coding: utf-8 -*-
"""Draw a small representative sample from the large tables."""
import csv
import io
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(r"d:/HuaweiMoveData/Users/wlx/Desktop") / "\u6570\u636e\u9a71\u52a8" / "midterm_project"
RAW = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "cleaned"
OUT = ROOT / "data" / "samples"
OUT.mkdir(parents=True, exist_ok=True)

FIVE_ISO2 = ["DE", "US", "IN", "IE", "GB"]
FIVE_ISO3 = ["DEU", "USA", "IND", "IRL", "GBR"]


def write_head(src, dst, n=12):
    lines = []
    with src.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
        for _ in range(n):
            line = handle.readline()
            if not line:
                break
            lines.append(line)
    dst.write_text("".join(lines), encoding="utf-8")
    print(dst.name, len(lines), "lines")


def batis():
    df = pd.read_csv(CLEAN / "batis_si2_top5_bilateral.csv")
    sub = df[df["exporter"].isin(FIVE_ISO2) & df["year"].isin([2014, 2024])]
    sub = sub.groupby(["exporter", "year"], sort=False).head(10)
    sub.to_csv(OUT / "batis_si2_top5_sample.csv", index=False)
    print("batis sample", len(sub))


def unctad():
    df = pd.read_csv(CLEAN / "unctad_panel_2014_2024.csv")
    sub = df[df["iso3"].isin(FIVE_ISO3) & df["year"].isin([2014, 2024])]
    computer = sub[sub["cat"].astype(str).str.startswith("SI")]
    use = computer if len(computer) else sub
    use = use.groupby(["iso3", "year"], sort=False).head(4)
    if len(use) > 80:
        use = use.head(80)
    use.to_csv(OUT / "unctad_panel_sample.csv", index=False)
    print("unctad sample", len(use), "cats", sorted(use["cat"].astype(str).unique())[:8])


def wto():
    df = pd.read_csv(CLEAN / "wto_hhi_2024.csv")
    five = df[df["iso3"].isin(FIVE_ISO3)]
    rest = df[~df["iso3"].isin(FIVE_ISO3)].head(max(0, 40 - len(five)))
    use = pd.concat([five, rest], ignore_index=True)
    use.to_csv(OUT / "wto_hhi_2024_sample.csv", index=False)
    print("wto sample", len(use))


def stri():
    src = RAW / "oecd_digital_stri.csv"
    rows = []
    with src.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames
        for row in reader:
            if row.get("REF_AREA") not in FIVE_ISO3:
                continue
            if row.get("MEASURE") != "STRI":
                continue
            if row.get("STRI_TYPE") not in (None, "", "DIGITAL"):
                continue
            rows.append(row)
    with (OUT / "stri_five_countries.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print("stri sample", len(rows))


def gdelt():
    src = RAW / "gdelt" / "20230807.export.CSV.zip"
    cols = [1, 7, 17, 26, 30, 33, 34, 51, 57]
    names = [
        "SQLDATE", "Actor1CountryCode", "Actor2CountryCode", "EventCode",
        "GoldsteinScale", "NumArticles", "AvgTone", "ActionGeo_CountryCode", "SOURCEURL",
    ]
    tokens = ("dpdp", "dpdpa", "digital-personal", "digitalpersonal", "data-protection", "dataprotection")
    prefer = []
    other = []
    with zipfile.ZipFile(src) as archive:
        name = archive.namelist()[0]
        with archive.open(name) as raw:
            text = io.TextIOWrapper(raw, encoding="utf-8", errors="replace", newline="")
            for row in csv.reader(text, delimiter="\t"):
                if len(row) < 58:
                    continue
                geo = row[51]
                actors = {row[7], row[17]}
                if geo != "IN" and not ({"IN", "IND"} & actors):
                    continue
                picked = [row[i] for i in cols]
                url = row[57].lower()
                if any(token in url for token in tokens):
                    prefer.append(picked)
                elif len(other) < 80:
                    other.append(picked)
                if len(prefer) >= 80:
                    break
    chosen = (prefer + other)[:80]
    with (OUT / "gdelt_20230807_india_sample.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(names)
        writer.writerows(chosen)
    print("gdelt sample", len(chosen), "named", len(prefer))


def readme():
    text = (
        "# \u6837\u672c\n\n"
        "\u8fd9\u4e9b\u6587\u4ef6\u4ece\u6e05\u6d17\u8868\u548c\u539f\u59cb\u65e5\u6587\u4ef6\u91cc\u62bd\u51fa\uff0c\u7528\u6765\u770b\u5b57\u6bb5\uff0c\u4e0d\u80fd\u4ee3\u66ff\u5168\u8868\u3002\n\n"
        "- `batis_si2_top5_sample.csv`\uff1a\u4e94\u56fd\uff0c2014 \u4e0e 2024\uff0c\u6bcf\u4e2a\u56fd\u5bb6\u2014\u5e74\u4efd\u6700\u591a 10 \u4e2a\u4f19\u4f34\n"
        "- `unctad_panel_sample.csv`\uff1a\u4e94\u4e2a\u7ecf\u6d4e\u4f53\u5728 2014 \u4e0e 2024 \u7684\u670d\u52a1\u7c7b\u522b\u884c\uff0c\u4f18\u5148\u8ba1\u7b97\u673a\u670d\u52a1\n"
        "- `wto_hhi_2024_sample.csv`\uff1a2024 \u5e74\u96c6\u4e2d\u5ea6\u7684\u4e00\u5c0f\u6bb5\uff0c\u542b\u4e94\u4e2a\u7ecf\u6d4e\u4f53\n"
        "- `stri_five_countries.csv`\uff1a\u5370\u5ea6\u3001\u7f8e\u56fd\u3001\u5fb7\u56fd\u3001\u7231\u5c14\u5170\u3001\u82f1\u56fd\u7684\u6570\u5b57 STRI\n"
        "- `gdelt_20230807_india_sample.csv`\uff1a2023-08-07 \u65e5\u6587\u4ef6\u91cc\uff0c\u884c\u52a8\u5730\u7406\u4e3a IN \u6216\u884c\u4e3a\u4f53\u4e3a IND \u7684\u8bb0\u5f55\uff0c\u4f18\u5148\u4fdd\u7559\u4e13\u540d\u94fe\u63a5\uff0c\u6700\u591a 80 \u6761\n"
        "- `batis_raw_head.csv`\u3001`unctad_raw_head.csv`\u3001`wto_raw_head.csv`\uff1a\u4e09\u4efd\u5927\u8868\u7684\u8868\u5934\u548c\u524d\u51e0\u884c\n\n"
        "\u539f\u59cb\u5168\u8868\u4ecd\u5728\u672c\u5730 `data/raw/`\uff0c\u4e0d\u4e0a\u4f20\u3002\u4f53\u79ef\u548c SHA256 \u89c1\u4ed3\u5e93\u6839\u76ee\u5f55 `MANIFEST.sha256`\u3002"
        "\u62a5\u544a\u6b63\u6587\u7684\u5206\u6790\u5408\u8ba1\u4ecd\u662f 7,562 MB\u3002\n"
    )
    (OUT / "README.md").write_text(text, encoding="utf-8")


def main():
    batis()
    unctad()
    wto()
    stri()
    gdelt()
    write_head(RAW / "OECD-WTO_BATIS_BPM6_bulk.csv", OUT / "batis_raw_head.csv")
    write_head(RAW / "UNCTAD_TradeServCatByPartner.csv", OUT / "unctad_raw_head.csv")
    write_head(RAW / "WTO_services_annual.csv", OUT / "wto_raw_head.csv")
    readme()
    print("samples ready", OUT)


if __name__ == "__main__":
    main()
