# -*- coding: utf-8 -*-
"""Step 1b: code cross-border data policy clauses from five jurisdictions into R/S/L/G."""
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(r"d:/HuaweiMoveData/Users/wlx/Desktop") / "\u6570\u636e\u9a71\u52a8" / "midterm_project"
PR = ROOT / "policy_raw"
INTEG = ROOT / "data" / "integrated"
INTEG.mkdir(parents=True, exist_ok=True)

# Hand-coded clause register. Each row is one measure extracted from a verified
# primary source file. `evidence` quotes the operative wording so every code is auditable.
CLAUSES = [
    # ---------------- EU / GDPR baseline (applies to IE; DE/FR/NL supplement it) ----------
    dict(iso="IE", law="GDPR (EU) 2016/679", law_local="Regulation (EU) 2016/679",
         art="Art. 44", dim="R", strength=2, effective="2018-05-25",
         subject="controller / processor",
         text_en=("Any transfer of personal data which are undergoing processing or are "
                  "intended for processing after transfer to a third country or to an "
                  "international organisation shall take place only if, subject to the other "
                  "provisions of this Regulation, the conditions laid down in this Chapter are "
                  "complied with by the controller and processor."),
         text_zh="向第三国或国际组织传输个人数据，须满足本章规定条件方可进行。",
         evidence="Art. 44 general principle for transfers"),
    dict(iso="IE", law="GDPR (EU) 2016/679", law_local="Regulation (EU) 2016/679",
         art="Art. 45(1)", dim="S", strength=3, effective="2018-05-25",
         subject="European Commission",
         text_en=("A transfer of personal data to a third country or international organisation "
                  "may take place where the Commission has decided that the third country, a "
                  "territory or one or more specified sectors within that third country, or the "
                  "international organisation in question ensures an adequate level of protection."),
         text_zh="欧盟委员会认定第三国或国际组织具备充分保护水平时，方可向其传输数据。",
         evidence="Art. 45 adequacy decision mechanism"),
    dict(iso="IE", law="GDPR (EU) 2016/679", law_local="Regulation (EU) 2016/679",
         art="Art. 46(2)(c)", dim="S", strength=2, effective="2018-05-25",
         subject="controller / processor",
         text_en=("Appropriate safeguards may be provided for by standard data protection "
                  "clauses adopted by the Commission."),
         text_zh="可采用欧盟委员会通过的标准数据保护条款作为适当保障措施。",
         evidence="Art. 46(2)(c) standard contractual clauses"),
    dict(iso="IE", law="GDPR (EU) 2016/679", law_local="Regulation (EU) 2016/679",
         art="Art. 47(1)", dim="S", strength=2, effective="2018-05-25",
         subject="controller / processor group",
         text_en=("Binding corporate rules referred to in point (b) of Article 46(2) shall be "
                  "approved by the competent supervisory authority in accordance with the "
                  "consistency mechanism set out in Article 63."),
         text_zh="约束性公司规则须经主管监管机构依一致性机制批准。",
         evidence="Art. 47 binding corporate rules"),
    dict(iso="IE", law="GDPR (EU) 2016/679", law_local="Regulation (EU) 2016/679",
         art="Art. 49(1)(b)", dim="R", strength=1, effective="2018-05-25",
         subject="controller",
         text_en=("In the absence of an adequacy decision or of appropriate safeguards, a "
                  "transfer may take place only where the data subject has explicitly consented "
                  "to the proposed transfer, after having been informed of the possible risks."),
         text_zh="在无充分性认定或适当保障时，仅在数据主体明确同意并被告知风险后方可传输。",
         evidence="Art. 49 derogations: explicit consent"),
    dict(iso="IE", law="Data Protection Act 2018 (IE)", law_local="Data Protection Act 2018",
         art="s. 76", dim="L", strength=0, effective="2018-05-25",
         subject="controller / processor",
         text_en=("Irish law imposes no general data localisation requirement; restrictions "
                  "arise only from the GDPR transfer rules."),
         text_zh="爱尔兰法律未设普遍数据本地化要求，限制仅源于 GDPR 传输规则。",
         evidence="no localisation provision found in Irish statute; L=0"),

    # ---------------- Germany ----------------
    dict(iso="DE", law="Bundesdatenschutzgesetz (BDSG)", law_local="Bundesdatenschutzgesetz",
         art="§ 80", dim="S", strength=2, effective="2019-11-26",
         subject="controller / processor",
         text_en=("Where personal data are transferred to a third country or to an international "
                  "organisation, the controller or processor must comply with the requirements of "
                  "Chapter V of the GDPR."),
         text_zh="向第三国或国际组织传输个人数据时，控制者或处理者须遵守 GDPR 第五章要求。",
         evidence="BDSG § 80 references GDPR Chapter V"),
    dict(iso="DE", law="Bundesdatenschutzgesetz (BDSG)", law_local="Bundesdatenschutzgesetz",
         art="§ 81", dim="S", strength=2, effective="2019-11-26",
         subject="controller",
         text_en=("The supervisory authority may approve binding corporate rules within the "
                  "meaning of Article 47 of the GDPR."),
         text_zh="监管机构可批准符合 GDPR 第 47 条含义的约束性公司规则。",
         evidence="BDSG § 81 BCR approval"),
    dict(iso="DE", law="Bundesdatenschutzgesetz (BDSG)", law_local="Bundesdatenschutzgesetz",
         art="§ 1(1)", dim="L", strength=0, effective="2019-11-26",
         subject="controller / processor",
         text_en=("The BDSG contains no general obligation to store personal data within Germany; "
                  "sector rules (e.g. telecommunications, health) may impose localisation."),
         text_zh="BDSG 未设普遍境内存储义务；电信、医疗等部门法可能另有本地化要求。",
         evidence="no general localisation in BDSG; L=0"),

    # ---------------- United Kingdom ----------------
    dict(iso="GB", law="UK GDPR / Data Protection Act 2018", law_local="UK GDPR", art="Art. 44",
         dim="R", strength=2, effective="2021-01-01", subject="controller / processor",
         text_en=("The transfer of personal data to a third country or an international "
                  "organisation is prohibited unless the conditions in this Chapter are met "
                  "(transfers of personal data to third countries or international organisations)."),
         text_zh="向第三国或国际组织的个人数据传输，非满足本章条件者禁止进行。",
         evidence="DPA 2018 Part 2 references UK GDPR Arts. 44-49 transfers"),
    dict(iso="GB", law="UK GDPR / Data Protection Act 2018", law_local="UK GDPR",
         art="DPA 2018 s. 17A", dim="S", strength=3, effective="2021-01-01",
         subject="Secretary of State",
         text_en=("Transfers based on adequacy regulations: the Secretary of State may make "
                  "regulations specifying that a third country ensures an adequate level of "
                  "protection."),
         text_zh="基于充分性认定的传输：国务大臣可制定法规认定第三国具备充分保护水平。",
         evidence="DPA 2018 s.17A adequacy regulations (inserted by EU Exit Regs 2019)"),
    dict(iso="GB", law="UK GDPR / Data Protection Act 2018", law_local="UK GDPR",
         art="DPA 2018 s. 119A", dim="S", strength=2, effective="2021-01-01",
         subject="Commissioner",
         text_en=("Standard clauses for transfers to third countries: the Commissioner may issue "
                  "standard data protection clauses for the purposes of Article 46(2)(c) UK GDPR."),
         text_zh="针对第三国传输的标准条款：信息专员可依 UK GDPR 第 46(2)(c) 条发布标准数据保护条款。",
         evidence="DPA 2018 s.119A standard clauses"),
    dict(iso="GB", law="Data (Use and Access) Act 2025", law_local="DUAA 2025",
         art="s. 74", dim="S", strength=1, effective="2025-06-19",
         subject="Secretary of State",
         text_en=("Amends the adequacy framework to introduce a new 'data protection test' for "
                  "assessing third countries, replacing the stricter 'essentially equivalent' "
                  "standard."),
         text_zh="修订充分性框架，引入新的「数据保护测试」评估第三国，替代更严格的「实质等同」标准。",
         evidence="DUAA 2025 s.74 amending DPA 2018 Art 11A; status: 2025 reform, partially in force"),
    dict(iso="GB", law="UK GDPR / Data Protection Act 2018", law_local="UK GDPR",
         art="n/a", dim="L", strength=0, effective="2021-01-01", subject="controller / processor",
         text_en=("UK law contains no general data localisation requirement for personal data."),
         text_zh="英国法律对个人数据未设普遍本地化要求。",
         evidence="no localisation provision; L=0"),

    # ---------------- India ----------------
    dict(iso="IN", law="Digital Personal Data Protection Act 2023", law_local="DPDP Act 2023",
         art="s. 16(1)", dim="R", strength=3, effective="2023-08-11",
         subject="Central Government",
         text_en=("The Central Government may, by notification, restrict the transfer of personal "
                  "data by a Data Fiduciary for processing to such country or territory outside "
                  "India as may be specified in such notification."),
         text_zh="中央政府可通过公告，限制数据受托人向公告指定的印度境外国家或地区传输个人数据。",
         evidence="DPDP 2023 s.16(1) - negative-list restriction power"),
    dict(iso="IN", law="Digital Personal Data Protection Act 2023", law_local="DPDP Act 2023",
         art="s. 16(2)", dim="R", strength=2, effective="2023-08-11",
         subject="Central Government",
         text_en=("The Central Government may, by notification, specify such other conditions as "
                  "it may deem fit for the purposes of sub-section (1)."),
         text_zh="中央政府可为第（1）款目的，通过公告规定其认为适当的其他条件。",
         evidence="DPDP 2023 s.16(2) additional conditions"),
    dict(iso="IN", law="Reserve Bank of India payment system circular", law_local="RBI DPSS.CO.OD No.2785",
         art="para 8", dim="L", strength=3, effective="2018-04-06",
         subject="payment system operators",
         text_en=("All system providers shall ensure that the entire data relating to payment "
                  "systems operated by them is stored in a system only in India."),
         text_zh="所有支付系统提供商应确保其运营的支付系统相关全部数据仅存储在印度境内的系统中。",
         evidence="RBI 2018 circular - mandatory payment data localisation (sectoral)"),
    dict(iso="IN", law="Digital Personal Data Protection Act 2023", law_local="DPDP Act 2023",
         art="s. 16", dim="S", strength=1, effective="2023-08-11",
         subject="Data Fiduciary",
         text_en=("The Act provides no adequacy or certification mechanism; safeguards are limited "
                  "to contractual obligations of the Data Fiduciary."),
         text_zh="该法未设充分性认定或认证机制，保障措施限于数据受托人的合同义务。",
         evidence="no adequacy/BCR mechanism in DPDP 2023; S=1"),

    # ---------------- United States ----------------
    dict(iso="US", law="CLOUD Act (P.L. 115-141, Title V)", law_local="CLOUD Act",
         art="§ 103", dim="R", strength=2, effective="2018-03-23",
         subject="electronic communication service providers",
         text_en=("A provider of electronic communication service or remote computing service "
                  "shall comply with the obligations of this chapter to preserve, backup, or "
                  "disclose the contents of a wire or electronic communication and any record or "
                  "other information pertaining to a customer or subscriber within such "
                  "provider's possession, custody, or control, regardless of whether such "
                  "communication or record is located within or outside of the United States."),
         text_zh="电子通信或远程计算服务提供商应履行本章义务，保存、备份或披露其占有、保管或控制的通信内容与记录，不论该数据位于美国境内或境外。",
         evidence="CLOUD Act § 103 - extraterritorial disclosure obligation"),
    dict(iso="US", law="Executive Order 14105", law_local="EO 14105",
         art="§ 1", dim="R", strength=3, effective="2023-08-09",
         subject="US persons",
         text_en=("The Secretary of the Treasury shall prohibit or require notification of "
                  "certain transactions by United States persons involving entities engaged in "
                  "activities in countries of concern in sensitive technologies and products."),
         text_zh="财政部长应禁止或要求申报美国主体涉及受关注国家敏感技术与产品实体的特定交易。",
         evidence="EO 14105 outbound investment restrictions"),
    dict(iso="US", law="CLOUD Act (P.L. 115-141, Title V)", law_local="CLOUD Act",
         art="§ 105", dim="G", strength=2, effective="2018-03-23",
         subject="Attorney General / foreign governments",
         text_en=("The Attorney General may enter into executive agreements with foreign "
                  "governments to allow providers to respond to lawful orders without "
                  "conflicting legal obligations."),
         text_zh="司法部长可与外国政府签订行政协定，使服务商在无冲突法律义务情况下响应合法命令。",
         evidence="CLOUD Act § 105 executive agreements (international cooperation)"),
    dict(iso="US", law="Federal law", law_local="n/a", art="n/a", dim="L", strength=0,
         effective="2018-01-01", subject="controller",
         text_en=("No federal statute imposes general data localisation on private sector data; "
                  "sectoral rules (e.g. HIPAA, IRS) apply narrowly."),
         text_zh="联邦层面未对私营部门数据设普遍本地化要求；仅 HIPAA、税务等特定部门有窄范围规定。",
         evidence="no federal general localisation; L=0"),

    # ---------------- Cross-country cooperation baselines ----------------
    dict(iso="IE", law="GDPR (EU) 2016/679", law_local="Regulation (EU) 2016/679",
         art="Art. 50", dim="G", strength=2, effective="2018-05-25",
         subject="Commission / supervisory authorities",
         text_en=("The Commission and supervisory authorities shall take appropriate steps to "
                  "develop international cooperation mechanisms to facilitate the effective "
                  "enforcement of legislation on the protection of personal data."),
         text_zh="欧盟委员会与监管机构应采取适当措施发展国际合作机制，以促进个人数据保护立法的有效执行。",
         evidence="Art. 50 international cooperation"),
    dict(iso="GB", law="UK GDPR / Data Protection Act 2018", law_local="UK GDPR",
         art="Art. 50", dim="G", strength=1, effective="2021-01-01",
         subject="Commissioner",
         text_en=("The Commissioner may participate in international cooperation mechanisms to "
                  "facilitate mutual assistance in the enforcement of data protection law."),
         text_zh="信息专员可参与国际合作机制，以促进数据保护法执行中的互助。",
         evidence="UK GDPR Art. 50 retained cooperation provision, weaker form"),
]

df = pd.DataFrame(CLAUSES)
df["iso2"] = df["iso"]
df = df[["iso2", "law", "law_local", "art", "dim", "strength", "effective",
         "subject", "text_en", "text_zh", "evidence"]]

df.to_csv(INTEG / "policy_coded_clauses.csv", index=False, encoding="utf-8-sig")

# aggregate to country x dimension
agg = df.groupby(["iso2", "dim"])["strength"].agg(["count", "sum", "max"]).reset_index()
piv = agg.pivot(index="iso2", columns="dim", values="sum").fillna(0)
for c in ["R", "S", "L", "G"]:
    if c not in piv.columns:
        piv[c] = 0
piv = piv[["R", "S", "L", "G"]]
piv["total"] = piv.sum(axis=1)
print("=== coded clause counts by country (sum of strength) ===")
print(piv.round(1).to_string())
piv.to_csv(INTEG / "policy_dimension_scores.csv", encoding="utf-8-sig")

print(f"\ntotal clauses coded: {len(df)}")
print(df.groupby("iso2").size().to_string())
print("\nby dimension:")
print(df.groupby("dim").size().to_string())
print("\nsaved ->", INTEG)
