# 样本

这些文件从清洗表和原始日文件里抽出，用来看字段，不能代替全表。

- `batis_si2_top5_sample.csv`：五国，2014 与 2024，每个国家—年份最多 10 个伙伴
- `unctad_panel_sample.csv`：五个经济体在 2014 与 2024 的服务类别行，优先计算机服务
- `wto_hhi_2024_sample.csv`：2024 年集中度的一小段，含五个经济体
- `stri_five_countries.csv`：印度、美国、德国、爱尔兰、英国的数字 STRI
- `gdelt_20230807_india_sample.csv`：2023-08-07 日文件里，行动地理为 IN 或行为体为 IND 的记录，优先保留专名链接，最多 80 条
- `batis_raw_head.csv`、`unctad_raw_head.csv`、`wto_raw_head.csv`：三份大表的表头和前几行

原始全表仍在本地 `data/raw/`，不上传。体积和 SHA256 见仓库根目录 `MANIFEST.sha256`。报告正文的分析合计仍是 7,562 MB。
