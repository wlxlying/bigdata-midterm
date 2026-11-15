# -*- coding: utf-8 -*-
from pptx import Presentation

path = "d:/HuaweiMoveData/Users/wlx/Desktop/\u4e2d\u671f\u5927\u4f5c\u4e1a_\u5c55\u793a_\u9b4f\u5170\u99a8241820216.pptx"
prs = Presentation(path)
print("slides", len(prs.slides))
for i, slide in enumerate(prs.slides, 1):
    texts = []
    for shape in slide.shapes:
        if shape.has_text_frame:
            t = shape.text_frame.text.strip().replace("\n", " | ")
            if t:
                texts.append(t[:100])
    print("%02d" % i, " || ".join(texts[:3]))
