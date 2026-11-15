# -*- coding: utf-8 -*-
import win32com.client

path = str(
    (r"d:\HuaweiMoveData\Users\wlx\Desktop")
    + "\\\u6570\u636e\u9a71\u52a8"
    + "\\\u4e2d\u671f\u5927\u4f5c\u4e1a_\u62a5\u544a_\u9b4f\u5170\u99a8241820216.docx"
)
word = win32com.client.Dispatch("Word.Application")
word.Visible = False
word.DisplayAlerts = 0
doc = word.Documents.Open(path)
doc.Fields.Update()
count = doc.TablesOfContents.Count
for i in range(1, count + 1):
    doc.TablesOfContents(i).Update()
doc.Repaginate()
pages = doc.ComputeStatistics(2)
doc.Save()
doc.Close(False)
word.Quit()
print("toc", count, "pages", pages)
