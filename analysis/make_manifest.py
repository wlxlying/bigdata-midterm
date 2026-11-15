# -*- coding: utf-8 -*-
"""Write SHA256, byte size, and relative path for the submission files and local raw data."""
import hashlib
from pathlib import Path

ROOT = Path(r"d:/HuaweiMoveData/Users/wlx/Desktop") / "\u6570\u636e\u9a71\u52a8" / "midterm_project"
SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", ".idea", ".vscode"}
SKIP_NAMES = {"MANIFEST.sha256", "desktop.ini", "Thumbs.db"}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            block = handle.read(8 * 1024 * 1024)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def main():
    rows = []
    raw_bytes = 0
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name in SKIP_NAMES or path.name.startswith("~$"):
            continue
        size = path.stat().st_size
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith("data/raw/"):
            raw_bytes += size
        rows.append((rel, size, path))
    rows.sort(key=lambda item: item[0])
    lines = []
    raw_lines = ["path\tsize_bytes"]
    done = 0
    for rel, size, path in rows:
        digest = sha256(path)
        lines.append(f"{digest}  {size}  {rel}")
        if rel.startswith("data/raw/"):
            raw_lines.append(f"{rel}\t{size}")
        done += 1
        if done % 40 == 0 or size > 100 * 1024 * 1024:
            print(done, rel, size)
    text = "\n".join(lines) + "\n"
    (ROOT / "MANIFEST.sha256").write_text(text, encoding="utf-8")
    (ROOT / "data" / "RAW_MANIFEST.txt").write_text("\n".join(raw_lines) + "\n", encoding="utf-8")
    total = sum(size for _, size, _ in rows)
    print("files", len(rows), "bytes", total, "raw_bytes", raw_bytes)


if __name__ == "__main__":
    main()
