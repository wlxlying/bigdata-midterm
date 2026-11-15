# -*- coding: utf-8 -*-
"""Build the midterm report from UTF-8 JSON blocks."""
import json
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(r"d:/HuaweiMoveData/Users/wlx/Desktop") / "\u6570\u636e\u9a71\u52a8" / "midterm_project"
VIS = ROOT / "visualization"
HERE = Path(__file__).resolve().parent
OUT = Path(r"d:/HuaweiMoveData/Users/wlx/Desktop") / "\u6570\u636e\u9a71\u52a8" / (
    "\u4e2d\u671f\u5927\u4f5c\u4e1a_\u62a5\u544a_\u9b4f\u5170\u99a8241820216.docx"
)


def load(path):
    raw = Path(path).read_bytes()
    for enc in ("utf-8", "utf-8-sig", "gb18030"):
        try:
            return json.loads(raw.decode(enc))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    raise SystemExit("cannot read " + str(path))


def set_run_font(run, east, size, bold=False, color=None):
    run.bold = bold
    run.font.size = Pt(size)
    run.font.name = "Times New Roman"
    if color is not None:
        run.font.color.rgb = RGBColor(*color)
    rpr = run._element.get_or_add_rPr()
    fonts = rpr.find(qn("w:rFonts"))
    if fonts is None:
        fonts = OxmlElement("w:rFonts")
        rpr.append(fonts)
    fonts.set(qn("w:ascii"), "Times New Roman")
    fonts.set(qn("w:hAnsi"), "Times New Roman")
    fonts.set(qn("w:eastAsia"), east)


def shade(cell, hex_color):
    tc = cell._tc
    tcpr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), hex_color)
    shd.set(qn("w:val"), "clear")
    tcpr.append(shd)


def set_cell_border(cell):
    tc = cell._tc
    tcpr = tc.get_or_add_tcPr()
    borders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right"):
        el = OxmlElement("w:" + edge)
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:color"), "D0D5DD")
        borders.append(el)
    tcpr.append(borders)


def add_page_number(paragraph):
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.append(begin)
    run2 = paragraph.add_run()
    run2._r.append(instr)
    run3 = paragraph.add_run()
    run3._r.append(end)
    for item in (run, run2, run3):
        set_run_font(item, "\u5b8b\u4f53", 9)


def add_toc(paragraph):
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = ' TOC \\o "1-2" \\h \\z \\u '
    sep = OxmlElement("w:fldChar")
    sep.set(qn("w:fldCharType"), "separate")
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.append(begin)
    run2 = paragraph.add_run()
    run2._r.append(instr)
    run3 = paragraph.add_run()
    run3._r.append(sep)
    run4 = paragraph.add_run("\u76ee\u5f55\u9879\u5728\u6253\u5f00\u6587\u6863\u66f4\u65b0\u57df\u540e\u663e\u793a\u9875\u7801\u3002")
    set_run_font(run4, "\u5b8b\u4f53", 12)
    run5 = paragraph.add_run()
    run5._r.append(end)


def enable_update(doc):
    settings = doc.settings.element
    node = OxmlElement("w:updateFields")
    node.set(qn("w:val"), "true")
    settings.append(node)


def paragraph(doc, text, *, size=12, east="\u5b8b\u4f53", bold=False, align="left",
              indent=True, before=0, after=6, center=False):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    if align == "center" or center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Pt(0)
    elif align == "justify":
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if indent:
            p.paragraph_format.first_line_indent = Pt(24)
    else:
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        if indent:
            p.paragraph_format.first_line_indent = Pt(24)
    run = p.add_run(text)
    set_run_font(run, east, size, bold=bold)
    return p


def heading(doc, text, level):
    p = doc.add_heading(text, level=level)
    size = {1: 16, 2: 14, 3: 12}[level]
    p.paragraph_format.first_line_indent = Pt(0)
    p.paragraph_format.space_before = Pt(12 if level > 1 else 18)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.25
    for run in p.runs:
        set_run_font(run, "\u9ed1\u4f53", size, bold=True, color=(31, 78, 121))
    return p


def add_table(doc, header, rows):
    table = doc.add_table(rows=1 + len(rows), cols=len(header))
    table.style = "Table Grid"
    table.autofit = True
    for j, name in enumerate(header):
        cell = table.rows[0].cells[j]
        cell.text = ""
        p = cell.paragraphs[0]
        p.paragraph_format.first_line_indent = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(str(name))
        set_run_font(run, "\u9ed1\u4f53", 9, bold=True, color=(255, 255, 255))
        shade(cell, "1F4E79")
        set_cell_border(cell)
    for i, row in enumerate(rows):
        for j, value in enumerate(row):
            cell = table.rows[i + 1].cells[j]
            cell.text = ""
            p = cell.paragraphs[0]
            p.paragraph_format.first_line_indent = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            run = p.add_run(str(value))
            set_run_font(run, "\u5b8b\u4f53", 9)
            if i % 2 == 1:
                shade(cell, "F4F7FB")
            set_cell_border(cell)
    doc.add_paragraph()


def add_figure(doc, name, caption):
    path = VIS / name
    if not path.exists():
        paragraph(doc, "\u7f3a\u56fe\uff1a" + name, indent=False)
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Pt(0)
    run = p.add_run()
    run.add_picture(str(path), width=Cm(15.6))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.first_line_indent = Pt(0)
    cap.paragraph_format.space_after = Pt(10)
    run = cap.add_run(caption)
    set_run_font(run, "\u6977\u4f53", 10.5)


def header_footer(section):
    header = section.header
    header.is_linked_to_previous = False
    hp = header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = hp.add_run("\u5927\u6570\u636e\u539f\u7406\u4e0e\u5e94\u7528  \u00b7  \u4e2d\u671f\u5927\u4f5c\u4e1a")
    set_run_font(run, "\u5b8b\u4f53", 9, color=(90, 98, 110))
    footer = section.footer
    footer.is_linked_to_previous = False
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    left = fp.add_run("\u6570\u5b57\u8d38\u6613\u9650\u5236\u4e0e\u8ba1\u7b97\u673a\u670d\u52a1\u51fa\u53e3\u96c6\u4e2d\u5ea6    ")
    set_run_font(left, "\u5b8b\u4f53", 9, color=(90, 98, 110))
    add_page_number(fp)


def cover(doc, meta):
    for _ in range(2):
        paragraph(doc, "", size=12, indent=False, after=0)
    paragraph(doc, meta["school"], size=16, east="\u9ed1\u4f53", bold=True, align="center", indent=False, after=4)
    paragraph(doc, meta["course"], size=14, east="\u9ed1\u4f53", align="center", indent=False, after=18)
    paragraph(doc, meta["kind"], size=18, east="\u9ed1\u4f53", bold=True, align="center", indent=False, after=16)
    paragraph(doc, meta["title"], size=18, east="\u9ed1\u4f53", bold=True, align="center", indent=False, after=6)
    paragraph(doc, meta["subtitle"], size=12, align="center", indent=False, after=18)
    lines = [
        "\u59d3\u540d\uff1a" + meta["author"] + "    \u5b66\u53f7\uff1a" + meta["sid"],
    ]
    if meta.get("group"):
        lines.append("\u5c0f\u7ec4\u6210\u5458\uff1a" + meta["group"])
    lines.append("\u65e5\u671f\uff1a" + meta["date"])
    for line in lines:
        paragraph(doc, line, size=12, align="center", indent=False, after=4)
    doc.add_page_break()


def main():
    meta = load(HERE / "report_meta.json")
    blocks = []
    for name in ("report_blocks_a.json", "report_blocks_b.json", "report_blocks_c.json"):
        blocks.extend(load(HERE / name))
    doc = Document()
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)
    section.top_margin = Cm(2.4)
    section.bottom_margin = Cm(2.3)
    section.header_distance = Cm(1.0)
    section.footer_distance = Cm(1.0)
    header_footer(section)
    cover(doc, meta)
    paragraph(doc, "\u76ee\u5f55", size=16, east="\u9ed1\u4f53", bold=True,
              align="center", indent=False, before=0, after=8)
    toc_p = doc.add_paragraph()
    toc_p.paragraph_format.first_line_indent = Pt(0)
    add_toc(toc_p)
    doc.add_page_break()
    chars = 0
    for block in blocks:
        kind = block["t"]
        if kind in ("h1", "h2", "h3"):
            heading(doc, block["s"], int(kind[1]))
            chars += len(block["s"])
        elif kind == "p":
            paragraph(doc, block["s"], align="justify")
            chars += len(block["s"])
        elif kind == "table":
            add_table(doc, block["h"], block["rows"])
            chars += sum(len(str(x)) for row in block["rows"] for x in row)
        elif kind == "fig":
            add_figure(doc, block["path"], block["cap"])
            chars += len(block["cap"])
        elif kind == "break":
            doc.add_page_break()
        else:
            raise SystemExit("unknown " + kind)
    enable_update(doc)
    doc.save(OUT)
    print("chars", chars)
    print("saved", OUT)


if __name__ == "__main__":
    main()
