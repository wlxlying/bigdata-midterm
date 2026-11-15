# -*- coding: utf-8 -*-
"""Fetch official policy texts for the top-10 economies (cross-border data rules).

Every download is validated: the file must contain law-like keywords, otherwise it is
flagged as BLOCKED rather than silently kept. A sidecar .meta.json records provenance.
"""
import hashlib
import json
import ssl
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(r"d:/HuaweiMoveData/Users/wlx/Desktop") / "\u6570\u636e\u9a71\u52a8" / "midterm_project"
OUT = ROOT / "policy_raw"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0 Safari/537.36")

_CTX = ssl.create_default_context()
_CTX.check_hostname = False
_CTX.verify_mode = ssl.CERT_NONE

KEYWORDS = ["Article", "Regulation", "Directive", "personal data", "cross-border",
            "\u4e2a\u4eba\u4fe1\u606f", "\u6570\u636e\u5b89\u5168", "\u5883\u5916",
            "loi", "wet", "Bundesdatenschutz", "Data Protection"]

# (country, id, label, url, kind, extra_headers)
TARGETS = [
    # ---- EU baseline: GDPR full text via official Publications Office (XHTML) ----
    ("EU", "gdpr_full", "GDPR Regulation (EU) 2016/679 full text (Publications Office)",
     "https://publications.europa.eu/resource/celex/32016R0679",
     "xhtml", {"Accept": "application/xhtml+xml", "Accept-Language": "eng"}),

    # ---- United States ----
    ("US", "cloud_act", "CLOUD Act - Public Law 115-141 Title V",
     "https://www.congress.gov/115/plaws/publ141/PLAW-115publ141.pdf", "pdf", {}),
    ("US", "eo_14105", "Executive Order 14105 (Federal Register)",
     "https://www.federalregister.gov/documents/2023/08/11/2023-17449/address-software-vulnerabilities-and-threats-investments-by-the-peoples-republic-of-china-in-certain-national-security-sensitive-technologies-products-and-services",
     "html", {}),

    # ---- Germany ----
    ("DE", "bdsg_en", "Bundesdatenschutzgesetz - official English translation",
     "https://www.gesetze-im-internet.de/englisch_bdsg/englisch_bdsg.html", "html", {}),

    # ---- India ----
    ("IN", "dpdp_2023", "Digital Personal Data Protection Act 2023 (MeitY)",
     "https://www.meity.gov.in/static/uploads/2024/06/2bf1f0e9f04e6fb4f8fef35e82c42aa5.pdf",
     "pdf", {}),

    # ---- China ----
    ("CN", "pipl_cac", "Personal Information Protection Law (CAC official)",
     "http://www.cac.gov.cn/2021-08/20/c_1631050028355286.htm", "html", {}),
    ("CN", "dsl_cac", "Data Security Law (CAC official)",
     "http://www.cac.gov.cn/2021-06/11/c_1624994566919140.htm", "html", {}),
    ("CN", "assessment_2022", "Measures for Security Assessment of Data Export (gov.cn)",
     "https://www.gov.cn/zhengce/zhengceku/2022-07/08/content_5699851.htm", "html", {}),
    ("CN", "provisions_2024", "Provisions on Promoting and Regulating Cross-border Data Flows",
     "https://www.gov.cn/zhengce/zhengceku/202403/content_6940159.htm", "html", {}),

    # ---- Singapore ----
    ("SG", "pdpa_sso", "Personal Data Protection Act 2012 (Singapore Statutes Online)",
     "https://sso.agc.gov.sg/Act/PDPA2012", "html", {}),

    # ---- Switzerland ----
    ("CH", "fadp_fedlex", "Federal Act on Data Protection (Fedlex, rev. 2023)",
     "https://www.fedlex.admin.ch/eli/cc/2022/491/en", "html", {}),

    # ---- EU mirror for IE / NL / FR (they apply GDPR directly) ----
    ("IE", "gdpr_applies", "GDPR applies directly (IE) - see EU/gdpr_full",
     "https://publications.europa.eu/resource/celex/32016R0679",
     "xhtml", {"Accept": "application/xhtml+xml", "Accept-Language": "eng"}),
    ("NL", "gdpr_applies", "GDPR applies directly (NL) - see EU/gdpr_full",
     "https://publications.europa.eu/resource/celex/32016R0679",
     "xhtml", {"Accept": "application/xhtml+xml", "Accept-Language": "eng"}),
    ("FR", "gdpr_applies", "GDPR applies directly (FR) - see EU/gdpr_full",
     "https://publications.europa.eu/resource/celex/32016R0679",
     "xhtml", {"Accept": "application/xhtml+xml", "Accept-Language": "eng"}),
    ("GB", "uk_gdpr_note", "UK GDPR retained from EU GDPR; DPA 2018 see legislation.gov.uk",
     "https://www.legislation.gov.uk/ukpga/2018/12/contents", "html", {}),
]

_last_hit = {}


def polite_delay(url):
    host = urlparse(url).netloc
    now = time.time()
    wait = 1.5 - (now - _last_hit.get(host, 0))
    if wait > 0:
        time.sleep(wait)
    _last_hit[host] = time.time()


def looks_like_law(data: bytes, kind: str) -> bool:
    if kind == "pdf":
        return data[:4] == b"%PDF"
    try:
        txt = data.decode("utf-8", "replace")
    except Exception:
        return False
    if "awsWafCookie" in txt or "Just a moment" in txt:
        return False
    hits = sum(1 for k in KEYWORDS if k in txt)
    return hits >= 1 or len(txt) > 60000


def fetch_one(iso, sid, label, url, kind, extra):
    d = OUT / iso
    d.mkdir(parents=True, exist_ok=True)
    ext = {"pdf": ".pdf", "html": ".html", "xhtml": ".xhtml"}[kind]
    dest = d / f"{sid}{ext}"
    meta_path = d / f"{sid}.meta.json"

    if dest.exists() and dest.stat().st_size > 2000:
        ok = looks_like_law(dest.read_bytes()[:200000], kind)
        if ok:
            print("skip ok", iso, sid, round(dest.stat().st_size / 1024, 1), "KB")
            return

    polite_delay(url)
    headers = {"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"}
    headers.update(extra or {})
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=90, context=_CTX) as r:
            data = r.read()
            status = r.status
            ctype = r.headers.get("Content-Type", "")
        valid = looks_like_law(data, kind)
        dest.write_bytes(data)
        meta = {"country": iso, "id": sid, "label": label, "url": url,
                "status": status, "content_type": ctype, "bytes": len(data),
                "validated_as_law_text": valid,
                "sha256": hashlib.sha256(data).hexdigest(),
                "access_time_utc": datetime.now(timezone.utc).isoformat()}
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        print(("OK  " if valid else "WARN"), iso, sid, status,
              round(len(data) / 1024, 1), "KB", "valid" if valid else "NOT-LAW-CONTENT")
    except Exception as e:
        print("ERR ", iso, sid, type(e).__name__, str(e)[:80])
        meta_path.write_text(json.dumps(
            {"country": iso, "id": sid, "label": label, "url": url,
             "error": type(e).__name__ + ": " + str(e)[:200],
             "access_time_utc": datetime.now(timezone.utc).isoformat()},
            ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    print("targets:", len(TARGETS))
    for t in TARGETS:
        fetch_one(*t)
    print("\n=== summary ===")
    grand = 0
    for d in sorted(OUT.iterdir()):
        if not d.is_dir():
            continue
        files = [f for f in d.iterdir() if f.suffix in (".html", ".xhtml", ".pdf")]
        total = sum(f.stat().st_size for f in files)
        grand += total
        print(d.name, len(files), "files", round(total / 1024, 1), "KB")
    print("TOTAL", round(grand / 1024, 1), "KB")


if __name__ == "__main__":
    main()
