# 数字贸易限制与计算机服务出口集中度

魏兰馨 241820216 · 大数据原理与应用 · 中期大作业 · 单人完成

限制更严的地方，计算机服务出口会不会更集中在少数市场？贸易总额回答不了：它没有伙伴份额。限制指数本身也没有市场结构。这项作业用 BaTiS、WTO 年度库和 UNCTAD 三套独立记录计算赫芬达尔指数，用 OECD 数字服务贸易限制指数和五国法律条文表示政策，再用 GDELT 核对 2023 年 8 月印度《数字个人数据保护法》通过那一周的报道。

在 BaTiS 平衡矩阵和 UNCTAD 报送口径上，国家与年份双向固定效应都没有给出显著、而且符号稳定的关联。BaTiS 系数约为 -255 到 -660，UNCTAD 约为 +700 到 +772，p 值都大于 0.4。Oster 的 δ 分别是 -1.08 和 0.18。印度那一周的专名报道明显升高，当年的限制指数和出口集中度没有台阶。

## 三个问题

每一个问题至少用两个独立来源。

| 编号 | 问题 | 来源 |
|------|------|--------|
| Q1 | 限制更严，出口是否更集中？ | 数字 STRI，加上 BaTiS 或 UNCTAD |
| Q2 | 集中来自伙伴个数，还是份额不匀？ | BaTiS、WTO 年度库、UNCTAD |
| Q3 | 立法周在事件和年度指标里各留下什么？ | 印度法律原文、GDELT、当年的 HHI 与 STRI |

---

## 目录结构

```
midterm_project/
├── crawler/
│   ├── download_sources.py              批量下载公开数据源
│   ├── fetch_policies.py                政策原文抓取（含内容校验、SHA256）
│   └── fetch_gb_waf.py                  英国站点 WAF token 抓取（特殊处理）
├── processing/
│   └── 00_copy_iso_map.py               ISO2/ISO3 映射表准备
├── analysis/
│   ├── 01_build_panel_hhi.py            双边面板构建 + HHI/CR 计算
│   ├── 02_code_policies.py              R/S/L/G 政策编码
│   ├── 03_extend_106_cluster.py         扩展至 105 国 + K-means
│   ├── 03b_fix_cluster_labels.py        聚类标签修正
│   ├── 04_analyze_visualize.py          规模分层 + 六张核心图
│   ├── 05_placebo_service_categories.py 安慰剂检验（服务类别对照）
│   └── 06_data_quality.py               数据质量检查
├── visualization/
│   ├── 06_draw_lineage.py               多源关联图生成
│   ├── data_lineage.png                 多源数据关联图
│   ├── fig1_hhi_by_country.png          五国集中度对比
│   ├── fig2_stri_vs_hhi.png             全样本散点
│   ├── fig3_hhi_trend.png               十年趋势
│   ├── fig4_rslg_radar.png              R/S/L/G 雷达图
│   ├── fig5_cluster.png                 聚类结果
│   ├── fig6_size_strata.png             规模分层
│   └── fig7_placebo_services.png        安慰剂检验
├── data/
│   ├── raw/                             7 个原始数据源（约 5.6 GB，未上传）
│   ├── cleaned/                         batis_si2_top5_bilateral.csv（10,945 行）
│   └── integrated/                      policy_trade_panel_106.csv、policy_coded_clauses.csv、
│                                        concentration_top5.csv、cluster_profile.csv
├── policy_raw/                          五国政策原文与 .meta.json 溯源（US/IE/GB/DE/IN/EU）
├── docs/                                研究设计说明书
├── data_sources.md                      数据源清单与采集日志
├── AI_USAGE.md                          AI 使用说明与反思
└── README.md                            本文件
```

---

## 复现步骤

### 环境

```
Python 3.14
pandas, numpy, matplotlib, scikit-learn, python-docx, python-pptx,
pypdf, py7zr, openpyxl
```

### 运行顺序

```bash
# 1. 下载公开数据源（约 5.6 GB）
python crawler/download_sources.py

# 2. 抓取五国政策原文（约 4 MB）
python crawler/fetch_policies.py

# 3. 构建双边面板并计算 HHI（BaTiS 全库扫描约 3-5 分钟）
python analysis/01_build_panel_hhi.py

# 4. 政策条款 R/S/L/G 编码（24 条措施）
python analysis/02_code_policies.py

# 5. 扩展至 105 国并聚类
python analysis/03_extend_106_cluster.py
python analysis/03b_fix_cluster_labels.py

# 6. 规模分层分析 + 六张核心图
python analysis/04_analyze_visualize.py

# 7. 多源关联图
python visualization/06_draw_lineage.py

# 8. 安慰剂检验（BaTiS 内部类别对照，无需额外下载）
python analysis/05_placebo_service_categories.py

# 9. 数据质量检查报告
python analysis/06_data_quality.py
```

每一步都会把中间结果写入 `data/`，可单独重跑，不必从头开始。

---

## 主要发现

| 发现 | 数值 | 含义 |
|------|------|------|
| 政策与集中度 | r = +0.060 | 几乎无线性关系，否定简单假设 |
| 控制规模后 | r = -0.098 | 方向反转，规模是主要混杂因素 |
| 中型经济体组内 | r = -0.338 | 负相关最强 |
| 五国 HHI 差距 | 407 至 895 | 印度是爱尔兰的 2.2 倍 |
| 十年变化 | 四国下降，英国上升 | 印度降幅最大（-584） |
| 其他服务 | 运输 -0.111、旅游 -0.259、计算机 +0.060 | 旅游的负相关显著，计算机服务不是。不能写成数字服务特有 |

---

## 数据说明

- **数据量**：计入分析的原始文件 7,562 MB。BaTiS 2,841 MB，占 37.6%。WTO 压缩包不重复计算。GDELT 分析窗是 2023-07-22 至 08-17 的 23 个日文件
- **未上传内容**：data/raw 里的完整原始表。文件名和大小见 data/RAW_MANIFEST.txt
- **已上传内容**：采集、清洗、分析、作图脚本，清洗后的表，融合结果，政策原文，图表和关联图
- **仓库**：https://github.com/wlxlying/bigdata-midterm
- **校验值**：每份政策原文的 SHA256 记录在对应 .meta.json 中

---

## 已知问题

1. **安慰剂检验改用 BaTiS 内部对照**：原计划用 CEPII BACI 货物贸易做安慰剂，但 CEPII
   服务器对大文件限速（实测约 50 KB/s，287 MB 需约 1.6 小时），多次中断后改用 BaTiS
   自身的运输服务（SC）与旅游服务（SD）作为非数字对照组。这一替代在方法上更贴切——
   三类服务来自同一数据源、同一平衡方法、同一国家样本，排除了数据源差异的干扰。

2. **英国政策原文不完整**：legislation.gov.uk 与 ico.org.uk 有 Cloudflare / AWS WAF
   防护。已通过浏览器会话 token 取得 DPA 2018 Part 2 全文（414 KB），Part 5 与
   Schedule 21 未取得，涉及 2025 年 DUAA 调整的条款标注为「待核」。

3. **STRI 覆盖 106 国而非官方 129 国**：本地 CSV 是筛选后的版本，需全量请从
   OECD Data Explorer 重新导出。

---

## 引用

```
OECD & WTO (2025). Balanced Trade in Services (BaTiS), BPM6.
WTO (2026). Trade in Commercial Services.
World Bank (2026). World Development Indicators.
OECD (2025). Digital Services Trade Restrictiveness Index.
GDELT Project (2026). GDELT 2.0 Event Database.
```

详细来源、许可与采集日志见 `data_sources.md`。
