# -*- coding: utf-8 -*-
"""18-slide midterm deck. Slide copy lives in ppt_slides.json."""
import json
from pathlib import Path

from lxml import etree
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

ROOT = Path(r"d:/HuaweiMoveData/Users/wlx/Desktop") / "\u6570\u636e\u9a71\u52a8" / "midterm_project"
VIS = ROOT / "visualization"
HERE = Path(__file__).resolve().parent
OUT = Path(r"d:/HuaweiMoveData/Users/wlx/Desktop") / (
    "\u4e2d\u671f\u5927\u4f5c\u4e1a_\u5c55\u793a_\u9b4f\u5170\u99a8241820216.pptx"
)

NAVY = RGBColor(0x1F, 0x4E, 0x79)
DEEP = RGBColor(0x14, 0x2B, 0x45)
INK = RGBColor(0x1C, 0x1C, 0x1C)
MUTED = RGBColor(0x5C, 0x6B, 0x7A)
CARD = RGBColor(0xF4, 0xF7, 0xFB)
LINE = RGBColor(0xD9, 0xE1, 0xEA)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
RUST = RGBColor(0x8C, 0x3A, 0x3A)
GOLD = RGBColor(0xC4, 0xA3, 0x5A)
EA = "\u5fae\u8f6f\u96c5\u9ed1"


def load():
    raw = (HERE / "ppt_slides.json").read_bytes()
    for enc in ("utf-8", "utf-8-sig", "gb18030"):
        try:
            return json.loads(raw.decode(enc))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    raise SystemExit("slides json")


def set_run(run, size, bold, color):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = EA
    rpr = run._r.get_or_add_rPr()
    for tag, face in (("a:latin", "Calibri"), ("a:ea", EA), ("a:cs", EA)):
        el = rpr.find(qn(tag))
        if el is not None:
            rpr.remove(el)
        el = etree.SubElement(rpr, qn(tag))
        el.set("typeface", face)


def add_text(slide, x, y, w, h, text, size=18, bold=False, color=INK,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = shape.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    tf.margin_left = Emu(0)
    tf.margin_right = Emu(0)
    tf.margin_top = Emu(0)
    tf.margin_bottom = Emu(0)
    tf.vertical_anchor = anchor
    lines = text.split("\n") if isinstance(text, str) else list(text)
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_before = Pt(0)
        p.space_after = Pt(0)
        run = p.add_run()
        run.text = line
        set_run(run, size, bold, color)
    return shape


def rect(slide, x, y, w, h, fill, line=None, radius=True):
    kind = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    shape = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    if line is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line
        shape.line.width = Pt(1)
    if radius:
        shape.adjustments[0] = 0.08
    return shape


def blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def footer(slide, page, total=18):
    rect(slide, 0, 7.22, 13.333, 0.02, NAVY, radius=False)
    add_text(slide, 0.48, 7.26, 8.5, 0.22,
             "\u5927\u6570\u636e\u539f\u7406\u4e0e\u5e94\u7528  \u00b7  \u4e2d\u671f\u5c55\u793a",
             11, False, MUTED)
    add_text(slide, 11.4, 7.26, 1.45, 0.22, "%d / %d" % (page, total),
             11, False, MUTED, align=PP_ALIGN.RIGHT)


def title(slide, text, y=0.28, h=0.62, size=28):
    add_text(slide, 0.48, y, 12.3, h, text, size, True, DEEP)


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def fit_picture(slide, name, x, y, w, h, crop_bottom=0):
    path = VIS / name
    im = Image.open(path)
    if crop_bottom:
        im = im.crop((0, 0, im.width, int(im.height * (1 - crop_bottom))))
        path = HERE / "_crop_preview.png"
        im.save(path)
    aspect = im.width / im.height
    if w / h > aspect:
        hh = h
        ww = h * aspect
    else:
        ww = w
        hh = w / aspect
    left = x + (w - ww) / 2
    top = y + (h - hh) / 2
    slide.shapes.add_picture(str(path), Inches(left), Inches(top), Inches(ww), Inches(hh))


def chrome(slide, page):
    rect(slide, 0, 0, 0.1, 7.5, NAVY, radius=False)
    footer(slide, page)


def s01(prs, d):
    s = blank(prs)
    rect(s, 0, 0, 13.333, 7.5, DEEP, radius=False)
    rect(s, 0.7, 1.55, 1.15, 0.08, GOLD, radius=False)
    add_text(s, 0.7, 1.85, 11.5, 0.36, d["kicker"], 16, False, GOLD)
    add_text(s, 0.7, 2.35, 11.8, 1.7, d["title"], 40, True, WHITE)
    add_text(s, 0.7, 4.25, 11, 0.4, d["sub"], 18, False, RGBColor(0xD6, 0xDE, 0xE8))
    add_text(s, 0.7, 5.7, 8, 0.32, d["who"], 16, False, WHITE)
    add_text(s, 0.7, 6.08, 10, 0.32, d["group"], 16, False, RGBColor(0xD6, 0xDE, 0xE8))
    notes(s, d["notes"])


def s02(prs, d, page):
    s = blank(prs)
    chrome(s, page)
    title(s, d["title"])
    tops = [1.25, 3.15, 5.05]
    for (num, head, body), top in zip(d["items"], tops):
        rect(s, 0.48, top, 12.35, 1.75, CARD)
        rect(s, 0.48, top, 0.1, 1.75, NAVY, radius=False)
        add_text(s, 0.8, top + 0.18, 1.1, 0.4, num, 20, True, NAVY)
        add_text(s, 1.9, top + 0.18, 10.5, 0.42, head, 20, True, DEEP)
        add_text(s, 1.9, top + 0.7, 10.5, 0.85, body, 15, False, INK)
    notes(s, d["notes"])


def s03(prs, d, page):
    s = blank(prs)
    chrome(s, page)
    title(s, d["title"], size=26)
    xs = [0.48, 4.7, 8.92]
    for (big, small), x in zip(d["chips"], xs):
        rect(s, x, 1.2, 3.9, 1.15, CARD)
        add_text(s, x + 0.2, 1.32, 3.5, 0.5, big, 26, True, NAVY, align=PP_ALIGN.CENTER)
        add_text(s, x + 0.2, 1.86, 3.5, 0.32, small, 13, False, MUTED, align=PP_ALIGN.CENTER)
    y = 2.6
    for name, size, role in d["rows"]:
        rect(s, 0.48, y, 12.35, 0.72, CARD)
        add_text(s, 0.7, y + 0.16, 4.3, 0.4, name, 16, True, DEEP, anchor=MSO_ANCHOR.MIDDLE)
        add_text(s, 5.1, y + 0.16, 2.2, 0.4, size, 16, True, NAVY, anchor=MSO_ANCHOR.MIDDLE)
        add_text(s, 7.4, y + 0.16, 5.1, 0.4, role, 15, False, INK, anchor=MSO_ANCHOR.MIDDLE)
        y += 0.82
    add_text(s, 0.48, 6.78, 12.3, 0.36, d["foot"], 13, False, MUTED)
    notes(s, d["notes"])


def s04(prs, d, page):
    s = blank(prs)
    chrome(s, page)
    title(s, d["title"], size=26)
    fit_picture(s, d["image"], 0.35, 1.05, 12.6, 5.55)
    add_text(s, 0.48, 6.6, 12.3, 0.5, d["take"], 14, False, INK)
    notes(s, d["notes"])


def s05(prs, d, page):
    s = blank(prs)
    chrome(s, page)
    title(s, d["title"], size=26, h=0.7)
    rect(s, 0.48, 1.25, 12.35, 1.55, DEEP)
    add_text(s, 0.7, 1.42, 11.9, 0.55, d["formula"], 26, True, WHITE, align=PP_ALIGN.CENTER)
    add_text(s, 0.7, 2.1, 11.9, 0.45, d["formula2"], 15, False, RGBColor(0xD6, 0xDE, 0xE8),
             align=PP_ALIGN.CENTER)
    xs = [0.48, 4.7, 8.92]
    for (big, head, body), x in zip(d["cards"], xs):
        rect(s, x, 3.15, 3.9, 3.35, CARD)
        add_text(s, x + 0.2, 3.4, 3.5, 0.7, big, 32, True, NAVY, align=PP_ALIGN.CENTER)
        add_text(s, x + 0.25, 4.2, 3.4, 0.7, head, 16, True, DEEP, align=PP_ALIGN.CENTER)
        add_text(s, x + 0.28, 5.05, 3.35, 1.15, body, 14, False, INK, align=PP_ALIGN.CENTER)
    notes(s, d["notes"])


def s06(prs, d, page):
    s = blank(prs)
    chrome(s, page)
    title(s, d["title"])
    card_h = 4.7 if d.get("foot") else 5.35
    xs = [0.48, 4.7, 8.92]
    for (head, body), x in zip(d["cols"], xs):
        rect(s, x, 1.25, 3.9, card_h, CARD)
        rect(s, x, 1.25, 3.9, 0.1, NAVY, radius=False)
        add_text(s, x + 0.25, 1.55, 3.4, 0.7, head, 20, True, DEEP)
        add_text(s, x + 0.25, 2.4, 3.4, card_h - 1.4, body, 15, False, INK)
    if d.get("foot"):
        add_text(s, 0.48, 6.15, 12.3, 0.9, d["foot"], 14, False, INK)
    notes(s, d["notes"])


def s07(prs, d, page):
    s = blank(prs)
    chrome(s, page)
    title(s, d["title"], size=26, h=0.7)
    rect(s, 0.48, 1.25, 6.05, 4.95, CARD)
    rect(s, 6.78, 1.25, 6.05, 4.95, CARD)
    add_text(s, 0.75, 1.45, 5.5, 0.5, d["left_h"], 20, True, NAVY)
    add_text(s, 7.05, 1.45, 5.5, 0.5, d["right_h"], 20, True, RUST)
    y = 2.2
    for line in d["left"]:
        add_text(s, 0.75, y, 5.5, 0.7, line, 18, False, INK)
        y += 0.85
    y = 2.2
    for line in d["right"]:
        add_text(s, 7.05, y, 5.5, 0.85, line, 18, False, INK)
        y += 0.85
    add_text(s, 0.48, 6.4, 12.3, 0.7, d["foot"], 13, False, MUTED)
    notes(s, d["notes"])


def figure_slide(prs, d, page):
    s = blank(prs)
    chrome(s, page)
    title(s, d["title"], size=24, h=0.5)
    fit_picture(s, d["image"], 0.35, 1.0, 12.6, 5.15)
    add_text(s, 0.48, 6.25, 12.3, 0.85, d["take"], 14, False, INK)
    notes(s, d["notes"])


def s11(prs, d, page):
    s = blank(prs)
    chrome(s, page)
    title(s, d["title"], size=26)
    rect(s, 0.48, 1.25, 6.05, 4.7, CARD)
    rect(s, 6.78, 1.25, 6.05, 4.7, CARD)
    add_text(s, 0.75, 1.5, 5.5, 0.5, d["left_h"], 22, True, NAVY)
    add_text(s, 7.05, 1.5, 5.5, 0.5, d["right_h"], 22, True, RUST)
    y = 2.3
    for line in d["left"]:
        add_text(s, 0.85, y, 5.3, 0.6, line, 22, False, INK)
        y += 0.8
    y = 2.3
    for line in d["right"]:
        add_text(s, 7.15, y, 5.3, 0.6, line, 22, False, INK)
        y += 0.8
    add_text(s, 0.48, 6.2, 12.3, 0.85, d["foot"], 15, False, INK)
    notes(s, d["notes"])


def s13(prs, d, page):
    s = blank(prs)
    chrome(s, page)
    title(s, d["title"], size=26)
    xs = [0.48, 6.78]
    colors = [NAVY, RUST]
    for card, x, color in zip(d["cards"], xs, colors):
        rect(s, x, 1.3, 6.05, 4.55, CARD)
        add_text(s, x + 0.35, 1.55, 5.4, 0.6, card[0], 26, True, color)
        yy = 2.5
        for line in card[1:]:
            add_text(s, x + 0.35, yy, 5.4, 0.7, line, 22, False, INK)
            yy += 0.9
    add_text(s, 0.48, 6.1, 12.3, 0.95, d["foot"], 14, False, MUTED)
    notes(s, d["notes"])


def s14(prs, d, page):
    s = blank(prs)
    chrome(s, page)
    title(s, d["title"], size=24, h=0.55)
    y = 1.2
    heads = ["\u7c7b\u522b", "\u76f8\u5173", "\u6837\u672c", "\u6765\u6e90"]
    xs = [0.55, 5.3, 7.3, 10.6]
    for head, x in zip(heads, xs):
        add_text(s, x, y, 2.4, 0.35, head, 13, True, MUTED)
    y = 1.65
    for row in d["rows"]:
        rect(s, 0.48, y, 12.35, 0.78, CARD)
        widths = [4.6, 1.8, 3.2, 2.2]
        xx = 0.7
        for value, w, size, bold in zip(row, widths, [16, 20, 15, 15], [True, True, False, False]):
            color = NAVY if bold and value[:1] in "+-" or value[:1] == "\u2212" or value[:1] == "+" else INK
            if bold and (value.startswith("+") or value.startswith("\u2212") or value.startswith("-")):
                color = RUST if value.startswith("\u2212") or value.startswith("-") else NAVY
            add_text(s, xx, y + 0.16, w, 0.48, value, size, bold, color, anchor=MSO_ANCHOR.MIDDLE)
            xx += w
        y += 0.88
    add_text(s, 0.48, 6.2, 12.3, 0.85, d["foot"], 14, False, INK)
    notes(s, d["notes"])


def s15(prs, d, page):
    s = blank(prs)
    chrome(s, page)
    title(s, d["title"])
    tops = [1.25, 3.15, 5.05]
    for (num, head, body), top in zip(d["items"], tops):
        rect(s, 0.48, top, 12.35, 1.75, CARD)
        add_text(s, 0.75, top + 0.28, 1.0, 0.45, num, 20, True, NAVY)
        add_text(s, 1.9, top + 0.22, 10.5, 0.45, head, 20, True, DEEP)
        add_text(s, 1.9, top + 0.78, 10.5, 0.75, body, 16, False, INK)
    notes(s, d["notes"])


def s16(prs, d, page):
    s = blank(prs)
    chrome(s, page)
    title(s, d["title"])
    positions = [(0.48, 1.25), (6.78, 1.25), (0.48, 4.05), (6.78, 4.05)]
    for (head, body), (x, y) in zip(d["items"], positions):
        rect(s, x, y, 6.05, 2.55, CARD)
        add_text(s, x + 0.28, y + 0.22, 5.5, 0.45, head, 20, True, NAVY)
        add_text(s, x + 0.28, y + 0.85, 5.5, 1.45, body, 15, False, INK)
    notes(s, d["notes"])


def s18(prs, d):
    s = blank(prs)
    rect(s, 0, 0, 13.333, 7.5, DEEP, radius=False)
    rect(s, 0.7, 1.9, 1.15, 0.08, GOLD, radius=False)
    add_text(s, 0.7, 2.2, 10, 0.9, d["title"], 48, True, WHITE)
    add_text(s, 0.7, 3.3, 11.5, 0.7, d["sub"], 20, False, RGBColor(0xD6, 0xDE, 0xE8))
    y = 4.6
    for line in d["lines"]:
        add_text(s, 0.7, y, 10, 0.4, line, 16, False, WHITE)
        y += 0.48
    notes(s, d["notes"])


def main():
    data = load()
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    prs.core_properties.title = "\u6570\u5b57\u8d38\u6613\u9650\u5236\u4e0e\u8ba1\u7b97\u673a\u670d\u52a1\u51fa\u53e3\u96c6\u4e2d\u5ea6"
    prs.core_properties.author = "\u9b4f\u5170\u99a8"
    s01(prs, data["s01"])
    s02(prs, data["s02"], 2)
    s03(prs, data["s03"], 3)
    s04(prs, data["s04"], 4)
    s05(prs, data["s05"], 5)
    s06(prs, data["s06"], 6)
    s07(prs, data["s07"], 7)
    figure_slide(prs, data["s08"], 8)
    figure_slide(prs, data["s09"], 9)
    figure_slide(prs, data["s10"], 10)
    s11(prs, data["s11"], 11)
    figure_slide(prs, data["s12"], 12)
    s13(prs, data["s13"], 13)
    s14(prs, data["s14"], 14)
    s15(prs, data["s15"], 15)
    s16(prs, data["s16"], 16)
    s06(prs, data["s17"], 17)
    s18(prs, data["s18"])
    prs.save(OUT)
    print("slides", len(prs.slides))
    print("saved", OUT)


if __name__ == "__main__":
    main()
