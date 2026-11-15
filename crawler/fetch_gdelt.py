# -*- coding: utf-8 -*-

"""Download GDELT 2.0 event files for policy-event analysis.



Strategy: rather than sparse day sampling, download a contiguous window around

known policy effective dates plus a matched control window, so the event

comparison has a proper baseline.

"""

import ssl

import time

import urllib.request

import zipfile

from datetime import date, timedelta

from pathlib import Path



ROOT = Path(r"d:/HuaweiMoveData/Users/wlx/Desktop") / "\u6570\u636e\u9a71\u52a8" / "midterm_project"

OUT = ROOT / "data" / "raw" / "gdelt"

OUT.mkdir(parents=True, exist_ok=True)



CTX = ssl.create_default_context()

CTX.check_hostname = False

CTX.verify_mode = ssl.CERT_NONE

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "

      "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36")



# windows: (label, start, end) — centered on real policy milestones

WINDOWS = [

    # India DPDP Act 2023 assent (2023-08-11) +/- 20 days

    ("IN_dpdp2023", date(2023, 7, 22), date(2023, 8, 31)),

    # India RBI payment localisation (2018-04-06) +/- 20 days

    ("IN_rbi2018", date(2018, 3, 17), date(2018, 4, 26)),

    # UK DPA 2018 in force (2018-05-25) +/- 20 days

    ("GB_dpa2018", date(2018, 5, 5), date(2018, 6, 14)),

    # EU GDPR application (2018-05-25) +/- 20 days

    ("EU_gdpr2018", date(2018, 5, 5), date(2018, 6, 14)),

    # control window: same length, no major data policy event

    ("CTRL_2019", date(2019, 3, 1), date(2019, 4, 10)),

]



BASE = "http://data.gdeltproject.org/events/{d}.export.CSV.zip"



log = []

total_bytes = 0

for label, start, end in WINDOWS:

    d = start

    n_ok = n_skip = 0

    while d <= end:

        fname = f"{d.strftime('%Y%m%d')}.export.CSV.zip"

        dest = OUT / fname

        if dest.exists() and dest.stat().st_size > 100_000:

            n_skip += 1

            total_bytes += dest.stat().st_size

            d += timedelta(days=1)

            continue

        url = BASE.format(d=d.strftime("%Y%m%d"))

        try:

            req = urllib.request.Request(url, headers={"User-Agent": UA})

            with urllib.request.urlopen(req, timeout=120, context=CTX) as r:

                data = r.read()

            if len(data) < 50_000:

                raise ValueError(f"too small: {len(data)}")

            dest.write_bytes(data)

            with zipfile.ZipFile(dest) as z:

                if z.testzip() is not None:

                    raise ValueError("zip corrupt")

            total_bytes += len(data)

            n_ok += 1

        except Exception as e:

            print(f"  MISS {url} {type(e).__name__}")

        d += timedelta(days=1)

        time.sleep(0.35)

    print(f"  {label:14s} {start}~{end}  new={n_ok} cached={n_skip}")

    log.append({"window": label, "start": str(start), "end": str(end),

                "new": n_ok, "cached": n_skip})



n_files = len(list(OUT.glob("*.export.CSV.zip")))

print(f"\nGDELT files: {n_files}, total {total_bytes / 1024 / 1024:.1f} MB")

import json

(OUT / "_download_log.json").write_text(

    json.dumps({"windows": log, "files": n_files,

                "bytes": total_bytes}, ensure_ascii=False, indent=2), encoding="utf-8")

