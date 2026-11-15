# 数字贸易限制与计算机服务出口集中度

魏兰馨 241820216 · 大数据原理与应用 · 中期大作业 · 单人完成

限制更严的地方，计算机服务出口会不会更集中在少数市场？贸易总额回答不了：它没有伙伴份额。限制指数本身也没有市场结构。这项作业用 BaTiS、WTO 年度库和 UNCTAD 三套独立记录计算赫芬达尔指数，用 OECD 数字服务贸易限制指数和五国法律条文表示政策，再用 GDELT 核对 2023 年 8 月印度《数字个人数据保护法》通过那一周的报道。

在 BaTiS 平衡矩阵和 UNCTAD 报送口径上，国家与年份双向固定效应都没有给出显著、而且符号稳定的关联。BaTiS 系数约为 -255 到 -660，UNCTAD 约为 +700 到 +772，p 值都大于 0.4。Oster 的 δ 分别是 -1.08 和 0.18。印度那一周的专名报道明显升高，当年的限制指数和出口集中度没有台阶。

仓库：https://github.com/wlxlying/bigdata-midterm

## 三个问题

每一个问题至少用两个独立来源。

| 编号 | 问题 | 来源 |
|------|------|------|
| Q1 | 限制更严，出口是否更集中？ | 数字 STRI，加上 BaTiS 或 UNCTAD |
| Q2 | 集中来自伙伴个数，还是份额不匀？ | BaTiS、WTO 年度库、UNCTAD |
| Q3 | 立法周在事件和年度指标里各留下什么？ | 印度法律原文、GDELT、当年的 HHI 与 STRI |

## 目录

```
midterm_project/
├── crawler/          公开数据与政策原文、GDELT 日文件的采集脚本
├── processing/       ISO2、ISO3、M49 对照
├── analysis/         集中度、回归、事件核对、报告生成
├── visualization/    关联图与结果图
├── data/
│   ├── raw/          原始表，只在本地，不上传
│   ├── cleaned/      清洗后的面板
│   ├── integrated/   回归、相关、聚类和事件结果
│   └── samples/      从大表抽出的小样本
├── policy_raw/       条款原文与采集记录
├── docs/             说明
├── data_sources.md   来源、日期、许可、缺日
├── AI_USAGE.md       工具使用记录
├── MANIFEST.sha256   体积与校验值
└── README.md
```

## 复现

环境：Python 3.14，以及 pandas、numpy、matplotlib、scikit-learn、statsmodels、python-docx、python-pptx、openpyxl。

原始表不在仓库里。把它们放到 `data/raw/`，文件名与 `data_sources.md` 一致，然后按下面的顺序运行。每一步写自己的结果表，不必从第一步重跑。

```bash
python crawler/download_sources.py
python crawler/fetch_policies.py
python crawler/fetch_gdelt.py
python processing/00_copy_iso_map.py
python analysis/01_build_panel_hhi.py
python analysis/panel_full.py
python analysis/wto_hhi.py
python analysis/unctad_hhi.py
python analysis/unctad_panel.py
python analysis/02_code_policies.py
python analysis/03_extend_106_cluster.py
python analysis/03b_fix_cluster_labels.py
python analysis/econ_batis.py
python analysis/unctad_econ.py
python analysis/unctad_econ2.py
python analysis/05_placebo_service_categories.py
python analysis/06_data_quality.py
python analysis/07_gdelt_event.py
python analysis/04_analyze_visualize.py
python visualization/06_draw_lineage.py
python visualization/07_lineage_slide.py
python analysis/make_samples.py
python analysis/make_manifest.py
```

`unctad_econ.py` 与 `unctad_econ2.py` 写出 UNCTAD 的双向固定效应、分解和 Oster 界。`econ_batis.py` 写出 BaTiS 的对应表。`07_gdelt_event.py` 写出印度立法周的日表。这些就是报告里的结果表。

## 数据量

计入报告正文的原始文件合计 7,562 MB。BaTiS 2,841 MB，占 37.6%。WTO 年度库另有一个 80.7 MB 的压缩包，与已解压的 CSV 重复，不计入。BACI 没有下载。

GDELT 的分析窗是 2023-07-22 至 2023-08-17，缺 07-24、07-25、07-27、08-01，缺日不补零。本地 `data/raw/gdelt/` 后来又放进了其他立法窗口，体积以 `MANIFEST.sha256` 为准。报告里的事件结论只用这一窗。

许可：BaTiS 与 WTO 年度库为 ODbL；WDI 为 CC BY 4.0；STRI 遵循 OECD 使用条款；GDELT 为公开事件数据；法律原文是政府公开文本。UNCTAD 双边服务统计使用时注明出处。

## 主要结果

| 结果 | 数值 |
|------|------|
| BaTiS 固定效应 | 约 -255 至 -660，p 大于 0.4 |
| UNCTAD 固定效应 | 约 +700 至 +772，p 大于 0.4 |
| Oster δ | UNCTAD 0.18，BaTiS -1.08 |
| 2024 年截面 | BaTiS r = 0.073；WTO r = -0.047；UNCTAD r = 0.154 |
| 其他服务 | 旅游 -0.259（p = 0.008），计算机服务不是最强的一类 |
| 印度立法周 | 专名事件在提交日、人民院、联邦院升高；当年 STRI 仍是 0.283 |

旅游服务上的负相关不能写成“限制指数只捕捉数字服务”。

## 已知限制

英国 DPA 2018 的 Part 5 和 Schedule 21 没有取全，涉及 2025 年 DUAA 的条款标为待核。STRI 与 BaTiS 对得上的是 105 个经济体，约占 199 个报告方的 52.8%，不是 98.1%。
