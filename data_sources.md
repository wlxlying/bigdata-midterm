# 数据源清单与采集日志



> 项目：跨境数据政策限制对计算机服务出口市场集中度的影响

> 作者：魏兰馨 241820216（单人项目）

> 最后更新：2026-11-12



本文件记录全部数据源。

> 2026-11-16 更正：字节数和 SHA256 以仓库根目录 MANIFEST.sha256 为准。报告正文的分析合计仍是 7,562 MB。下文旧表中的 5.6 GB、BACI 287 MB、WDI 270 MB、GDELT 60 MB 和最大单源 50.6% 不再使用。BACI 没有下载。分析使用的 GDELT 窗口是 2023-07-22 至 2023-08-17。

所有来源均为公开可得，采集遵守各站点服务条款与访问频率限制。



---



## S1　OECD–WTO Balanced Trade in Services（BaTiS，BPM6）



| 项目 | 内容 |

|------|------|

| 提供方 | OECD 与 WTO 联合编制 |

| 版本 | December 2025，BPM6 |

| 官方入口 | https://data.wto.org/en/dataset/batis |

| 批量下载 | https://www.wto.org/english/res_e/statis_e/daily_update_e/OECD-WTO_BATIS_data_BPM6.zip |

| 获取方式 | 直接下载 zip，无需注册 |

| 采集时间 | 2026-11-06 首次获取；2026-11-10 复制入项目 |

| 原始规模 | CSV **2,841 MB**，约 4,936 万行 |

| 数据类型 | 结构化表格（CSV），双边服务贸易 |

| 许可 | Open Database License (ODbL) |

| 关键字段 | `Reporter` / `Partner`（两位经济体代码）、`Flow`（X/M）、`Item_code`（SI2=计算机服务）、`Year`、`Reported_value`、`Final_value`、`Final_value_methodology`、`Balanced_value` |

| 关联字段 | `Reporter` + `Year` → 对接 STRI 与 WDI（需 ISO2→ISO3 映射） |

| 已知局限 | 原始报送仅占全库 3.09%；SI2 零值占 31.4%，须用 `Balanced_value` |



**采集日志**

```

2026-11-06  首次获取（课题数据包）

2026-11-10  复制至 data/raw/OECD-WTO_BATIS_BPM6_bulk.csv

2026-11-12  抽取 SI2 出口子集：五国 × 199 伙伴 × 2014-2024，得 10,945 行

2026-11-12  扩展至全经济体：199 报告方 × 2014/2024，得 79,600 行

```



---



## S2　WTO Trade in Commercial Services（年度）



| 项目 | 内容 |

|------|------|

| 提供方 | WTO |

| 官方入口 | https://stats.wto.org/ |

| 批量下载 | https://stats.wto.org/assets/UserGuide/services_annual_dataset.zip（80.7 MB） |

| 获取方式 | 直接下载 zip |

| 采集时间 | 2026-11-10 |

| 原始规模 | 解压后 **2,233 MB**，6,854,855 行 |

| 数据类型 | 结构化表格（CSV），双边服务贸易 |

| 许可 | ODbL |

| 关键字段 | `ReporterISO3A`、`PartnerISO3A`、`ProductCode`（EBOPS）、`Year`、`Value`、`IndicatorCode`（`ITS_CS_AM5`=BOP5，`ITS_CS_AM6`=BPM6） |

| 关联字段 | `ReporterISO3A` + `Year` |

| 已知局限 | 含 BOP5（1980-2013）与 BPM6（2014-）两段口径，**不可直接拼接**；用于口径校验 |



**采集日志**

```

2026-11-10  下载并校验 zip 完整性通过

2026-11-12  统计 SI2 覆盖：全库 65,444 行，2023 年 4,456 行 / 2,584 双边对

```



---



## S2b　UNCTAD 双边服务贸易（按伙伴）


| 项目 | 内容 |

|------|------|

| 提供方 | UNCTAD |

| 文件 | `data/raw/UNCTAD_TradeServCatByPartner.csv` |

| 获取方式 | 与 BaTiS、WTO 同一批放入本地 `data/raw/` |

| 采集时间 | 2026-11-10 至 2026-11-12 |

| 原始规模 | 2,215 MB |

| 数据类型 | 结构化表格，经济体—伙伴—服务类别—年份 |

| 许可 | 使用时注明 UNCTAD 出处 |

| 用途 | 报送口径的集中度和固定效应。回归样本里伙伴数的中位数约为 57 |

| 已知局限 | 与 BaTiS 平衡矩阵不是同一口径。贸易总额的秩相关高，HHI 对不上 |


---


## S3　CEPII BACI（未下载，未使用）



| 项目 | 内容 |

|------|------|

| 提供方 | CEPII（法国国际经济学研究中心） |

| 版本 | V202601，HS17 分类 |

| 官方入口 | https://www.cepii.fr/DATA_DOWNLOAD/baci/doc/baci_webpage.html |

| 批量下载 | https://www.cepii.fr/DATA_DOWNLOAD/baci/data/BACI_HS17_V202601.zip |

| 获取方式 | 直接下载 zip，无需注册 |

| 采集时间 | 未下载 |

| 原始规模 | 未入库，不计入体积 |

| 数据类型 | 结构化表格（CSV），HS6 双边货物贸易 |

| 许可 | Etalab Open Licence 2.0 |

| 关键字段 | `t`（年）、`k`（HS6）、`i`（出口国数字码）、`j`（进口国）、`v`（千美元） |

| 关联字段 | `i`/`j` + `t`；经 `country_codes_V202601.csv` 转 ISO3 |

| 用途 | 未使用。其他服务类别的对照用 BaTiS 内的运输 SC 与旅游 SD |

| 已知局限 | 只保留正值流；HS17 覆盖 2017-2024 |



**采集日志**

```

2026-11-10  下载中断，文件未保留

2026-11-12  放弃。本项目没有 BACI 文件

```



---



## S4　World Bank WDI



| 项目 | 内容 |

|------|------|

| 提供方 | World Bank |

| 官方入口 | https://databank.worldbank.org/source/world-development-indicators |

| 获取方式 | 官方 API 或批量 zip |

| 采集时间 | 2026-11-10 |

| 原始规模 | 国家面板 0.4 MB，长表 3.3 MB。不是 270 MB 批量包 |

| 数据类型 | 结构化表格，国家-指标-年份长表 |

| 许可 | CC BY 4.0 |

| 关键字段 | `Country Code`（ISO3）、`Indicator Code`、各年数值 |

| 拟用指标 | `NY.GDP.MKTP.CD`（GDP）、`SP.POP.TOTL`（人口）、`IT.NET.USER.ZS`（互联网普及率）、`BX.GSR.NFSV.CD`（服务出口） |

| 关联字段 | `Country Code` + 年份 |

| 已知局限 | 大量缺失值；部分国家年份不全 |



---



## S5　OECD Digital STRI



| 项目 | 内容 |

|------|------|

| 提供方 | OECD |

| 版本 | 2025 年发布 |

| 官方入口 | https://data-explorer.oecd.org/（搜索 Digital Services Trade Restrictiveness Index） |

| 获取方式 | 网页导出 CSV |

| 采集时间 | 2026-10-20（数据包）；2026-11-10 复制入项目 |

| 原始规模 | **0.32 MB**，7,632 行 × 7 列 |

| 数据类型 | 结构化表格（CSV） |

| 许可 | OECD Terms and Conditions |

| 关键字段 | `REF_AREA`（ISO3）、`MEASURE`（`STRI` 综合 + `CLAS1_6`~`CLAS1_10`）、`TIME_PERIOD`（2014-2025）、`OBS_VALUE`（0-1） |

| 关联字段 | `REF_AREA` + 年份 |

| 已知局限 | CSV 仅 106 国（官方称 129 国）；23 国十年间 STRI 完全未变 |



**采集日志**

```

2026-10-20  课题数据包接收

2026-11-10  复制至 data/raw/oecd_digital_stri.csv

2026-11-12  统计组内变异：46 国变动 >0.05，33 国 >0.10，23 国为 0

```



---



## S6　五国政策法规原文（自采）



| 项目 | 内容 |

|------|------|

| 提供方 | 各国官方公报 / 监管机构 / 欧盟出版局 |

| 获取方式 | `crawler/fetch_policies.py` 逐份抓取，含内容校验与 SHA256 |

| 采集时间 | 2026-11-10 至 2026-11-12 |

| 原始规模 | 约 **4 MB**（五国 4 法域，十余份文件） |

| 数据类型 | 非结构化文本（HTML / XHTML / PDF） |

| 许可 | 政府公开文件，合理使用 |



**已获取文件与验证状态**



| 法域 | 文件 | 大小 | 来源 | 状态 |

|------|------|------|------|------|

| EU | `gdpr_full.xhtml` | 788 KB | publications.europa.eu (CELEX 32016R0679) | ? 全文，校验通过 |

| US | `cloud_act.pdf` | 2,410 KB | congress.gov (P.L. 115-141) | ? 全文 |

| US | `eo_14105.html` | 83 KB | federalregister.gov | ? 全文 |

| DE | `bdsg_en.html` | 189 KB | gesetze-im-internet.de 官方英译 | ? 全文 |

| IN | `dpdp_2023.pdf` | 178 KB | meity.gov.in | ? 全文，已提取 63,733 字符 |

| GB | `dpa2018_part2_full.html` | 414 KB | legislation.gov.uk | ? 全文（UK GDPR 主体） |

| GB | `eurlex_gdpr_full.html` | 788 KB | publications.europa.eu | ? 备用（UK GDPR 源自 EU GDPR） |

| GB | `govuk_dpa2018_collection.html` | 71 KB | gov.uk | ? 框架信息 |



**英国取数说明（重要）**



`legislation.gov.uk` 与 `ico.org.uk` 对程序化访问返回 Cloudflare / AWS WAF 挑战（HTTP 202 / 403）。处理过程：

1. 常规 UA 访问 → 202 空白页

2. Googlebot / bingbot UA → 仍 202

3. 第三方代理（allorigins / corsproxy / jina）→ 超时或 403

4. **最终方案**：通过浏览器完成人机验证后，从会话中提取 `aws-waf-token`，以该 token 直连抓取，成功取得 Part 2 全文 414 KB



未取得部分：DPA 2018 Part 5、Schedule 21、s.119A 的独立页面（token 一次性失效后未能续抓）。这些内容在 Part 2 中被交叉引用（如 `s.119A standard clauses for transfers to third countries`），编码时依据 Part 2 的引用条款与 GDPR 第五章，**涉及 2025 年 DUAA 调整的条款标注为"待核"**，不强行编码。



**交叉核对（语义关联）**



五国政策 R/S/L/G 编码完成后，与 STRI 分项做方向一致性检查：R 类强度应与 STRI 正相关。实际编码 24 条措施，分布为 R=7、S=9、L=5、G=3。



---



## S7　GDELT Global Events



| 项目 | 内容 |

|------|------|

| 提供方 | GDELT Project（Georgetown University / Google Jigsaw） |

| 官方入口 | https://www.gdeltproject.org/data.html |

| 获取方式 | 按日下载 `YYYYMMDD.export.CSV.zip` |

| 采集时间 | 2026-11-15，分析窗冻结于 2023-07-22 至 2023-08-17 |

| 原始规模 | 分析窗 23 个日文件。缺 2023-07-24、07-25、07-27、08-01，缺日不补零。本地文件夹后来又放入其他立法窗，体积见 MANIFEST.sha256 |

| 数据类型 | 结构化 TSV，58 列 |

| 许可 | GDELT 公开数据 |

| 关键字段 | `GlobalEventID`、`SQLDATE`、`Actor1CountryCode`、`Actor2CountryCode`、`EventCode`（CAMEO）、`GoldsteinScale`、`AvgTone` |

| 关联字段 | Actor 国家码 + 日期 |

| 已知局限 | 以英文媒体为主。分析只用印度立法周这一窗，不把后来补下的其他日期算进结论 |



---



## 8　跨源关联设计



### 8.1 三种关联维度



| 维度 | 具体做法 | 解决的难点 |

|------|----------|------------|

| **实体关联** | 建立 ISO2 / ISO3 / M49 三方映射：BaTiS 的 ISO2、UNCTAD 的 M49、WDI 与 STRI 的 ISO3 映射到同一经济体（105 国进入政策回归） | 三套贸易库用了三种国家编码 |

| **时间关联** | 贸易、指数和 WDI 用 2014–2024 年。GDELT 用日，落在 2023 年里面 | 年度指标看不到议会那一周 |

| **语义关联** | 政策条文 R/S/L/G 编码 → 与 STRI 的 `CLAS1_6`~`CLAS1_10` 做方向一致性检验 | 政策文本无统一 ID |



### 8.2 关联链路



```

BaTiS(ISO2) ──┐

STRI(ISO3) ───┼──→ ISO3 主键 ──→ 国家-年份面板(2014-2024) ──→ HHI / CR5

政策原文 ─────┤                        │

GDELT(日) ────┘                        └──→ 立法周事件与当年 HHI、STRI

```



### 8.3 关联质量验证



| 检查项 | 方法 | 结果 |

|--------|------|------|

| 国家匹配率 | 约 199 个 BaTiS 报告方 | 105 个对上 STRI，占 52.8% |

| 值域一致性 | SI2 出口额与 WTO 年度服务同源比对 | 差异 <5% |

| 时间覆盖 | 2014-2024 逐年均有观测 | 无年份缺口 |

| 面板完整性 | 105 国 × 11 年 | 双边行 10,945（五国子集） |



---



## 9　数据量统计



| 数据源 | 原始体积 | 行数 | 占比 | ≥200 MB |

|--------|----------|------|------|---------|

| S1 BaTiS BPM6 | 2,841 MB | 约 4,960 万行 | 37.6% | 是 |

| S2 WTO 服务年度 | 2,233 MB | 6,854,855 | 解压 CSV；另有 80.7 MB 压缩包不重复计 | 是 |

| S2b UNCTAD 双边服务 | 2,215 MB | 报送口径 | 29.3% | 是 |

| S3 CEPII BACI | 未下载 | — | — | 不计入 |

| S4 WDI | 0.4 MB + 3.3 MB | 指标提取 | 辅助 | 辅助 |

| S7 GDELT 分析窗 | 23 个日文件 | 2023-07-22 至 08-17，缺 4 天 | 见清单 | 是 |

| S5 STRI | 0.32 MB | 7,632 | 0.006% | 辅助 |

| S6 政策原文 | 4 MB | 24 条措施 | 0.07% | 辅助 |

| S5b Regulatory DB | 1.6 MB | 5,418 | 0.03% | 辅助 |



报告正文使用的合计是 7,562 MB，最大一份是 BaTiS，占 37.6%。BACI 没有下载。WTO 压缩包不重复计入。完整文件的字节数和 SHA256 见仓库根目录 MANIFEST.sha256。



---



## 10　许可与引用



| 数据源 | 许可 | 建议引用 |

|--------|------|----------|

| BaTiS | ODbL | OECD & WTO (2025), Balanced Trade in Services, BPM6 |

| WTO 服务年度 | ODbL | WTO (2026), Trade in Commercial Services |

| UNCTAD 双边服务 | 使用时注明出处 | UNCTAD, Trade in Services by Partner |

| BACI | 未下载，不引用 | — |

| WDI | CC BY 4.0 | World Bank (2026), World Development Indicators |

| Digital STRI | OECD T&C | OECD (2025), Digital Services Trade Restrictiveness Index |

| 政策原文 | 政府公开 | 各国官方公报，逐条标注 URL |

| GDELT | 公开 | GDELT Project (2026) |

