# -*- coding: utf-8 -*-
"""Fetch UK legislation using the AWS WAF token harvested from the browser session."""
import hashlib
import json
import os
import ssl
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(r"d:/HuaweiMoveData/Users/wlx/Desktop") / "\u6570\u636e\u9a71\u52a8" / "midterm_project" / "policy_raw" / "GB"
OUT.mkdir(parents=True, exist_ok=True)

# One-time browser cookie. Keep it in the environment, not in the repository.
TOKEN = os.environ.get("GB_WAF_TOKEN", "").strip()
if not TOKEN:
    raise SystemExit("Set GB_WAF_TOKEN to the aws-waf-token cookie. Do not commit it.")

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36")

TARGETS = [
    ("dpa2018_part2_full", "Data Protection Act 2018 Part 2 (UK GDPR) - full text",
     "https://www.legislation.gov.uk/ukpga/2018/12/part/2"),
    ("dpa2018_s17_21", "DPA 2018 ss.17-21 restricted transfers",
     "https://www.legislation.gov.uk/ukpga/2018/12/crossheading/restricted-transfers"),
    ("uk_gdpr_ch5", "UK GDPR Chapter V equivalent - transfers (via DPA 2018 Part 2 Ch 5)",
     "https://www.legislation.gov.uk/ukpga/2018/12/part/2/chapter/5"),
]


def looks_law(txt: str) -> bool:
    low = txt.lower()
    if "aws-waf" in low and len(txt) < 5000:
        return False
    hits = sum(k in low for k in ["personal data", "transfer", "controller", "data protection"])
    return len(txt) > 20000 and hits >= 3


for sid, label, url in TARGETS:
    time.sleep(1.5)
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": UA,
            "Accept": ("text/html,application/xhtml+xml,application/xml;q=0.9,"
                       "image/avif,image/webp,*/*;q=0.8"),
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "Cookie": TOKEN,
            "Referer": "https://www.legislation.gov.uk/ukpga/2018/12/part/2",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Upgrade-Insecure-Requests": "1",
        })
        with urllib.request.urlopen(req, timeout=90, context=CTX) as r:
            data = r.read()
            status = r.status
        txt = data.decode("utf-8", "replace")
        ok = looks_law(txt)
        if ok:
            (OUT / f"{sid}.html").write_bytes(data)
        (OUT / f"{sid}.meta.json").write_text(json.dumps({
            "country": "GB", "id": sid, "label": label, "url": url, "status": status,
            "bytes": len(data), "validated_as_law_text": ok,
            "sha256": hashlib.sha256(data).hexdigest(),
            "access_time_utc": datetime.now(timezone.utc).isoformat(),
            "access_method": "direct fetch with AWS WAF token from browser session",
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print(("OK  " if ok else "WARN"), sid, status, round(len(data) / 1024, 1), "KB")
    except Exception as e:
        print("ERR ", sid, type(e).__name__, str(e)[:90])

print("\nGB files:")
for f in sorted(OUT.iterdir()):
    if f.suffix in (".html", ".xhtml", ".pdf"):
        print("  ", f.name, round(f.stat().st_size / 1024, 1), "KB")
