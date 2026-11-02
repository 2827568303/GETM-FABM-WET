# NOVANA 湖深数据源覆盖核查

日期：2026-10-26（Sol 高，只读资料核查）

## 方法与结果

- 查询 Styrelsen for Grøn Arealomlægning og Vandmiljø 官方 [NOVANA WFS GetCapabilities](https://geodata.fvm.dk/geoserver/NOVANA/ows?service=WFS&version=2.0.0&request=GetCapabilities)，HTTP 200。服务列出 `NOVANA:Soe_dybdekort_konturer`、`NOVANA:Soe_dybdekort_punkter` 和湖岸界线层。
- 通过 [等深线层](https://geodata.fvm.dk/geoserver/NOVANA/ows?service=WFS&version=2.0.0&request=DescribeFeatureType&typenames=NOVANA%3ASoe_dybdekort_konturer) 的属性字段查询记录湖名、湖 ID、深度区间和面积：共 1,096 条等深线要素、78 个不同湖名。湖名中没有 Arreskov、Bryrup 或 Ravn。
- 在 [测深点层](https://geodata.fvm.dk/geoserver/NOVANA/ows?service=WFS&version=2.0.0&request=DescribeFeatureType&typenames=NOVANA%3ASoe_dybdekort_punkter) 对 `soe_navn LIKE '%Arreskov%'`、`'%Bryrup%'`、`'%Ravn%'` 逐项查询，三项均 HTTP 200 且返回 0 条。
- 数据目录将等深线描述为 0.5 m 深度区间，并称测深点来自声呐现场测量；见 [Danmarks Miljøportal Arealdata](https://arealdata.miljoeportal.dk/)。本次只查询属性以核实覆盖，没有下载/导入几何，也没有生成模型案例。

## 结论与边界

- **实测（来源覆盖核查）**：上述官方 NOVANA 图层目前不含这三个案例的等深线或测深点记录。
- 该查询只排除这一个官方数据源；不能证明其他官方、历史或研究数据不存在。
- 在获得可追溯的空间测深或足以构建 3D 网格的湖盆资料前，不能用代表深度、等深分区或派生插值表面冒充实测地形。Lake Ravn、Bryrup、Arreskov 的 3D 输入和科学验证仍**未完成**。
- 本次没有创建、运行或删除任何案例，也没有打开 APP。
