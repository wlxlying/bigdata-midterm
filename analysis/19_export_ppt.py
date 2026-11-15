# -*- coding: utf-8 -*-
import shutil
from pathlib import Path

import win32com.client

src = Path(r"d:/HuaweiMoveData/Users/wlx/Desktop") / (
    "\u4e2d\u671f\u5927\u4f5c\u4e1a_\u5c55\u793a_\u9b4f\u5170\u99a8241820216.pptx"
)
out = Path(r"d:/HuaweiMoveData/Users/wlx/Desktop") / "\u6570\u636e\u9a71\u52a8" / "midterm_project" / "_ppt_preview"
if out.exists():
    shutil.rmtree(out)
out.mkdir(parents=True)
app = win32com.client.Dispatch("PowerPoint.Application")
app.Visible = True
pres = app.Presentations.Open(str(src), WithWindow=False)
pres.Export(str(out), "PNG", 1600, 900)
pres.Close()
app.Quit()
print("exported", len(list(out.glob("*.PNG"))))
