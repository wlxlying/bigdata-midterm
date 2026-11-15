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


def main():
    tasks = []

    # BACI and the full WDI zip are not part of this project.
    # Trade, STRI and the WDI extracts already used are copied below when a local store exists.
    # GDELT legislative windows are downloaded by fetch_gdelt.py, not by the eight-day sample.

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

    print("\n=== %d download tasks ===" % len(tasks))
    print("GDELT legislative windows: python crawler/fetch_gdelt.py")
    for name, url, dest, hdr in tasks:
        print("\n---", name)
        fetch(url, dest, headers=hdr)

    print("\n=== done ===")
    for p in sorted(RAW.rglob("*")):
        if p.is_file() and p.stat().st_size > 2**20:
            print(round(p.stat().st_size / 2**20, 1), "MB", p.relative_to(RAW))


if __name__ == "__main__":
    main()
