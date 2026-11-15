# -*- coding: utf-8 -*-
from pathlib import Path
import pandas as pd

raw = Path(r"d:/HuaweiMoveData/Users/wlx/Desktop") / "\u6570\u636e\u9a71\u52a8" / "midterm_project" / "data" / "raw"
s = pd.read_csv(raw / "oecd_digital_stri.csv")
s = s[(s["STRI_TYPE"] == "DIGITAL") & (s["MEASURE"] == "STRI")]
keep = ["DEU", "IRL", "GBR", "USA", "IND", "FRA"]
sub = s[s["REF_AREA"].isin(keep)]
wide = sub.pivot_table(index="TIME_PERIOD", columns="REF_AREA", values="OBS_VALUE")
print(wide.loc[2014:2024].round(4).to_string())
print("measures", sorted(pd.read_csv(raw / "oecd_digital_stri.csv")["MEASURE"].astype(str).unique())[:20])
