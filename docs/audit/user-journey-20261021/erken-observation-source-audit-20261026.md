# Erken 官方温度剖面数据来源与下载核查

日期：2026-10-26（Asia/Shanghai）  
负责人：Sol 高  
状态：**官方实测数据已下载并通过哈希核验；与本仓库模型结果配对及科学验证仍未完成**

## 数据来源与许可

- 数据集：Erken Laboratory, *Physical variables - lake temperature profile from Erken, year-round anchored TW-profile*, 2017-06-28 至 2024-09-14。站点：Erken Laboratory；采样点坐标：59.84247°N, 18.630983°E；时间分辨率：60 分钟；元数据记录 62,959 行。[SITES 数据集元数据](https://meta.fieldsites.se/objects/Kq6E7t69ZyKJejMcANJQVoHP)
- 用户已授权接受 SITES 下载页的 CC BY 4.0 数据使用说明；按授权在 SITES 数据政策页执行了 “Yes, I accept”。许可要求保留来源归属，提供许可证和原始数据集链接，并标明修改；相关说明见 [SITES 数据政策](https://data.fieldsites.se/licence) 与 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。
- 元数据给出的引用：Erken Laboratory (2024). *Physical variables - lake temperature profile from Erken, year-round anchored TW-profile, 2017-06-28–2024-09-14* [Data set]. Swedish Infrastructure for Ecosystem Science (SITES). https://hdl.handle.net/11676.1/Kq6E7t69ZyKJejMcANJQVoHP

## 下载与本地核验

- 原始 ZIP 与解压文件已在先前审计中归档：[`SITES_TW-PROF_ERK_LRK_20170628-20240914_L2_60min.zip`](../../../build/observation-evidence-20261027-sites-erken-2017-2024/SITES_TW-PROF_ERK_LRK_20170628-20240914_L2_60min.zip)、[`SITES_TW-PROF_ERK_LRK_20170628-20240914_L2_60min.csv`](../../../build/observation-evidence-20261027-sites-erken-2017-2024/SITES_TW-PROF_ERK_LRK_20170628-20240914_L2_60min.csv)。ZIP 包含原 CSV、`!TOC.csv` 与 `!LICENCE.pdf`。本次授权后重新下载并核实了相同数据；由于发现已有完全相同的哈希归档，主记录仍指向既有来源文件。
- CSV 字节数为 29,452,645；SHA-256 为 `2aae84eedebd6722897a331c00d2505681cf98de7966b2e88aaa4ec30211d83e`，与数据集元数据公布值一致，也与刚下载的原档副本一致。
- CSV 时间戳数据行计数为 62,959，首条 `2017-06-28 19:00`，末条 `2024-09-14 08:00`。数据说明标记时区为 UTC+1。表格包含多个深度的水温（°C）列。以上核验确认文件身份与内容完整性，不代表模型匹配验证通过。

## 当前科学验证状态

- Erken 温度实测源：**实测**（官方数据集下载、元数据与哈希已核实）。
- 时间/深度坐标转换、质控掩码、与本仓库当前 GETM 运行的站点/垂向插值配对：**未完成**。
- 偏差、RMSE、分层结构或其它科学技能指标：**未计算**；Erken 案例总体科学验证仍为**未完成**。
- 该下载不启动或改写任何模型案例，也不触及既有案例文件。

## Attribution

SITES, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Original source: [SITES dataset PID 11676.1/Kq6E7t69ZyKJejMcANJQVoHP](https://meta.fieldsites.se/objects/Kq6E7t69ZyKJejMcANJQVoHP). Original bytes were not transformed; only extracted from the supplied ZIP for local inspection.
