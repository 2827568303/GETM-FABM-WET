# Bryrup Langsø 官方观测来源核查

日期：2026-10-26（Asia/Shanghai）  
负责人：Sol 高  
状态：**实测数据源/站点元数据已核实；原始剖面尚未提取；当前案例科学验证未完成**

## 官方观测与站点信息

- SGAV 的 Bryrup Langsø 页面说明，监测站位于湖内最深处，采集水样并测量温度和溶氧剖面。页面称 2015 年起通常每两年开展 19 次测量；1989–2015 年曾逐年采样。页面同时提示近期图表中可能含尚未最终质控的数据。[SGAV Bryrup Langsø](https://sgavmst.dk/natur-og-jagt/naturen-i-danmark/novana-overvaagning-af-natur-og-vandmiljoe/guider-til-danske-vandomraader/soe/bryrup-langsoe)
- 通过 Danmarks Miljøportal VanDa GeoServer WFS 的 `vanda:feltmaaling-soe` 站点目录，在 Bryrup 周边 EPSG:25832 bbox 内查询，返回 20 个湖泊站点。Bryrup 记录为站号 `21000361`、名称 `BRYRUP LANGSØ, BRY 1`、坐标 `(532693, 6208262)`、站点元数据首末调查日期 `1978-04-12` 至 `2025-12-09`。bbox 同时包含邻湖站点；这里仅引用 Bryrup 的精确站号记录。该 WFS 层返回站点元数据和 Kemidata 深链接，不是原始温度剖面行。
- Danmarks Miljøportal Arealdata 列出 `Feltmåling Sø` 数据集，描述涵盖 VanDa 湖泊现场测量的地点、时间、测点、深度、参数与结果；另有 `Måledybder Sø` 数据集记录站点、时间、跃层、底深与透明度。这些是进一步下载/筛选原始观测的官方入口。[Feltmåling Sø 数据集](https://arealdata.miljoeportal.dk/datasets/urn:dmp:ds:feltmaaling-soe)、[Måledybder Sø 数据集](https://arealdata.miljoeportal.dk/datasets/urn:dmp:ds:maaledybder-soe)、[VanDa WFS](https://vanda-geo.miljoeportal.dk/geoserver/wfs)
- 官方 Datakatalog API 将 `urn:dmp:ds:feltmaaling-soe` 的 CSV 文件端点标为 `https://arealdata-api.miljoeportal.dk/data/vanda-ue-35/file`。公开 `info` 请求确认该文件存在，但匿名文件请求返回 HTTP 401；本核查未取得 CSV 字节，也未尝试账户登录。[Datakatalog API Swagger](https://datakatalog.miljoeportal.dk/api/swagger/index.html)

## 已发表基准及限制

Aarhus University DCE Report 402 的 Bryrup Langsø 章节列出 9 m 最大深度、4.6 m 平均深度、约 0.37 km² 面积和 18 个模型层；温度和溶氧各有 1,184 个观测配对，公开基准校准期为 2004–2005、验证期为 1996–2003。该表是发表的历史一维模型性能结果，不是本仓库当前 GETM 3D 案例结果。[DCE Report 402](https://dce2.au.dk/pub/SR402.pdf)

## 当前结论

- **实测源可用性**：已核实 Bryrup 存在长期官方温度/溶氧剖面监测，并定位到官方 VanDa 站点 `21000361`。WFS 返回的调查日期范围不能当作每个参数的实际观测覆盖期。
- **原始数据提取/配对**：**未完成**。已定位官方 CSV 端点 `vanda-ue-35`，但匿名下载返回 HTTP 401；本核查没有原始观测表，没有将温度/氧气的逐深度测量与当前 GETM 输出配对，也没有产生误差统计。
- **模型与案例状态**：Bryrup 当前案例的可运行网格、强迫、参数和匹配输出仍需单独核验；完整科学验证仍为**未完成**。未启动、创建、覆盖或删除模型案例，未打开 APP。

## 复核查询

WFS `GetCapabilities` 确认公开了 `vanda:feltmaaling-soe`、`vanda:maaledybder-soe` 等站点目录层。Bryrup 站点筛选使用 EPSG:25832 周边 bbox：`527678,6203162,537678,6213162`，站点记录核对 `Stationsnummer=21000361`。该 bbox 只用于定位官方站点，不用于插值湖底或定义模型网格。
