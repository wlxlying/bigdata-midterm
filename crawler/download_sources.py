# -*- coding: utf-8 -*-
"""Download all midterm data sources. Designed to be resumable and rate-limited."""
import io
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(r"d:/HuaweiMoveData/Users/wlx/Desktop") / "\u6570\u636e\u9a71\u52a8" / "midterm_project"
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/125.0 Safari/537.36"}


def fetch(url, dest, headers=None, retries=3, chunk=512 * 1024, quiet=False):
    """Stream download with resume-by-restart and size check."""
    dest = Path(dest)
    if dest.exists() and dest.stat().st_size > 1024:
        if not quiet:
            print("skip exists:", dest.name, round(dest.stat().st_size / 2**20, 1), "MB")
        return dest
    h = dict(UA)
    if headers:
        h.update(headers)
    for attempt in range(1, retries + 1):
        try:
            t0 = time.time()
            req = urllib.request.Request(url, headers=h)
            with urllib.request.urlopen(req, timeout=1800) as r, open(dest, "wb") as f:
                total = 0
                while True:
                    buf = r.read(chunk)
                    if not buf:
                        break
                    f.write(buf)
                    total += len(buf)
            dt = max(time.time() - t0, 0.01)
            print("OK", dest.name, round(total / 2**20, 1), "MB", round(dt, 0), "s",
                  round(total / 1024 / dt, 0), "KB/s")
            return dest
        except Exception as e:
            print("retry", attempt, dest.name, type(e).__name__, str(e)[:90])
            time.sleep(5 * attempt)
    print("FAILED", dest.name)
    return None


GDELT_DAYS = [
    # 2014 (policy baseline year) and 2024 (latest full year)
    "20140115", "20140415", "20140715", "20141015",
    "20240115", "20240415", "20240715", "20241015",
]

def main():
    tasks = []

    # ---- CEPII BACI (goods, HS6) ----
    baci = RAW / "BACI_HS22_V202601.zip"
    if not (baci.exists() and baci.stat().st_size > 200 * 2**20):
        if baci.exists():
            baci.unlink()
        tasks.append(("BACI", "https://www.cepii.fr/DATA_DOWNLOAD/baci/data/BACI_HS22_V202601.zip", baci, None))

    # ---- CEPII Gravity ----
    grav = RAW / "Gravity_csv_V202211.zip"
    if not (grav.exists() and grav.stat().st_size > 150 * 2**20):
        if grav.exists():
            grav.unlink()
        tasks.append(("Gravity", "https://www.cepii.fr/DATA_DOWNLOAD/gravity/data/Gravity_csv_V202211.zip", grav, None))

    # ---- World Bank WDI full bulk ----
    wdi = RAW / "WDI_CSV.zip"
    if not (wdi.exists() and wdi.stat().st_size > 200 * 2**20):
        if wdi.exists():
            wdi.unlink()
        tasks.append(("WDI", "https://databank.worldbank.org/data/download/WDI_CSV.zip", wdi,
                      {"Referer": "https://databank.worldbank.org/"}))

    # ---- WTO / UNCTAD / OECD (copy from existing local store) ----
    src = Path(r"d:/HuaweiMoveData/Users/wlx/Desktop") / "\u6570\u636e\u9a71\u52a8" / "\u6570\u636e\u4e0e\u6570\u636e\u8bf4\u660e"
    copies = [
        (src / "OECD-WTO_BATIS_BPM6_December2025_bulk.csv", RAW / "OECD-WTO_BATIS_BPM6_bulk.csv"),
        (src / "OECD-WTO_BATIS_BPM6_December2025_codes.xlsx", RAW / "BATIS_codes.xlsx"),
        (src / "oecd_digital_stri_2014_2025.csv", RAW / "oecd_digital_stri.csv"),
        (src / "oecd_dstri_regulatorydatabase_2025.xlsx", RAW / "oecd_dstri_regulatory.xlsx"),
    ]
    extra = src / "\u6dfb\u52a0_\u6570\u5b57\u8d38\u6613\u6d41\u91cf"
    copies += [
        (extra / "WTO_DDS_bulk_download.csv", RAW / "WTO_DDS_bulk.csv"),
        (extra / "WTO_services_annual.zip", RAW / "WTO_services_annual.zip"),
    ]
    import shutil
    for s, d in copies:
        if s.exists() and not d.exists():
            shutil.copy2(s, d)
            print("copied", d.name, round(d.stat().st_size / 2**20, 1), "MB")

    # ---- GDELT event files (8 sample days) ----
    for day in GDELT_DAYS:
        dest = RAW / "gdelt" / f"{day}.export.CSV.zip"
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            tasks.append(("GDELT " + day, f"https://data.gdeltproject.org/events/{day}.export.CSV.zip", dest, None))

    print("\n=== %d download tasks ===" % len(tasks))
    for name, url, dest, hdr in tasks:
        print("\n---", name)
        fetch(url, dest, headers=hdr)

    print("\n=== done ===")
    for p in sorted(RAW.rglob("*")):
        if p.is_file() and p.stat().st_size > 2**20:
            print(round(p.stat().st_size / 2**20, 1), "MB", p.relative_to(RAW))


if __name__ == "__main__":
    main()
