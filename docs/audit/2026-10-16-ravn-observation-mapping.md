# Lake Ravn 实测观测、单位和模型对应核验

核验日：2026-10-16。范围是静态调查与实施设计；未运行官方可执行文件、GETM、优化或服务，未安装依赖。研究目录为 `build/ravn-calibration-research-20261016/`。本报告不能作为科学率定通过记录。

## 可交付案例的准确含义

官方 Lake Ravn 教学包提供同湖真实观测、边界/测深、气象/入流和已率定配置。另一个官方压缩包提供完整可执行 GOTM 柱模型。应首先提供“Ravn 原始柱模型/剖面率定”案例，明确采用原官方一维水平代表性假设；没有精确站点映射的原观测不能自动用于任意湖，也不能称为三维 GETM 指定水格实测率定。三维迁移是另一个验收对象。

一手来源：

- [Aarhus workshop 页面](https://projects.au.dk/wet/gleon-gsa-limnoseries-wet)：说明两套参数分别针对温度/氧和全部可用观测率定，并提供独立运行默认模型。
- [官方数据格式与率定说明](https://projects.au.dk/wet/resources)：观测格式、负深度、单位、强迫数据格式、分阶段率定和 ParSac 示例。研究副本 `build/ravn-calibration-research-20261016/resources.html`，SHA256 `cfb38bc5cd4c079faa2e0be452eb1f4418822b27cc7c9577d4ca34d1830c9283`。
- [完整 workshop ZIP](https://projects.au.dk/fileadmin/projects/wet/resources/ftp/QWET_test_case_Lake_Ravn_workshop.zip)：已由主任务下载并校验，32714861 bytes，SHA256 `9a8767c2b5e235de268d31d1808220bcb062deb2704ef890b137827ef062a56b`；研究目录中展开为 `QWET_test_case_Lake_Ravn_workshop/`。
- [官方默认可执行模型 ZIP](https://projects.au.dk/fileadmin/projects/wet/resources/ftp/default_lakeRavn_setup.zip)：本次下载10611286 bytes，SHA256 `a6ab09c604ed39c802cf7567482eb81ea09bb196c9d1127eb6dd582fe1db827e`，ZIP CRC全通过。保存在研究目录；只提取小型文本到 `default-text/Default/`，未执行其中的exe或bat。
- [官方 ParSac XML](https://projects.au.dk/fileadmin/projects/wet/config_parsac.xml)：本次保存为研究目录 `config_parsac.xml`；包含实际参数路径和边界，包括八变量（含 NH4）观测映射。该文件是通用示例，内部 Lake_name 路径不可直接运行，不是证明 Ravn 独立验证的数据分割。

## 文件与时间/深度盘点

`.obs`每行是空白分隔的日期、时间、负的水面以下米坐标和数值，无表头、无站号、无时区和无分析方法字段。已对所有行解析；未发现非四列或无法解析的行。`obs-inventory.json`保存精确盘点。记录数包含重复和后续须隔离的记录。

|文件|行数|首时刻|末时刻|原负深度范围 m|原值范围|重复键多余行数|
|---|---:|---|---|---|---|---:|
|TEMP.obs|11904|1971-09-19 12:00:00|2018-12-17 12:43:00|-32～-0.2|-0.2～72|53|
|DO.obs|11680|1974-10-16 12:00:00|同上|-32～-0.2|0～20.5|44|
|CHLA.obs|1420|1977-08-09 10:45:00|同上|-30.5～-0.2|0.01～70|0|
|NH4.obs|1674|1973-11-19 12:00:00|同上|-31～-0.2|0.001～3.5|0|
|NO23.obs|1688|1973-11-19 12:00:00|同上|-31～-0.2|0.099～6.7|0|
|PO4.obs|1782|1971-09-19 12:00:00|同上|-99～-0.2|0～0.68|0|
|TOTN.obs|1691|1973-11-19 12:00:00|同上|-31～-0.2|0.89～8.3|0|
|TOTP.obs|1780|1971-09-19 12:00:00|同上|-99～-0.2|0.005～0.7|1|

重复键为同文件同时间同深度，不应按仅时间去重，否则整个剖面会被误删。TEMP有49组重复键，其中19组值冲突；DO有40组，其中14组冲突；TOTP一组冲突。保留全部原文和行号；完全相同行可在派生数据中折叠并记来源，多值冲突默认隔离，不能未经声明取均值。

实测异常证据：`TEMP.obs:6800`为2006-07-11 10:30:00、-14m、72°C；`PO4.obs:137`与`TOTP.obs:140`为1975-10-26、-99m。不能把72改成7.2或把-99解释成缺测编码后静默删行；只标记物理异常/深度超域，保留原值。上述具体异常均不在推荐1996–2005评分窗口中，但完整导入仍必须报告。

时间保留无时区原历时。未知是否UTC或丹麦本地时，不能根据运行机器的Asia/Shanghai或夏令时自动移位。官方原柱模型与原观测采用同一不带时区历时的操作约定；三维输入若采用UTC则必须先补充源时间依据。NetCDF需要尊重`calendar`；不允许数字时间无单位时兜底解释为2000年起秒数。

## 变量、单位和测量定义

官方说明规定.obs使用对应输出单位：温度°C，营养盐和溶氧mg/L，Chl a μg/L。这证明原案例的操作单位约定，不等于为每条历史测定提供实验室方法、检出限或检验认证。无证据不能把数值自动判成μmol/L或按NO3/PO4离子分子量转换。

|源文件|官方wet_obs.xml目标|原操作单位|当前WET预期单位/定义|处理|
|---|---|---|---|---|
|TEMP|temp|°C|Celsius/degC|直接数值，负坐标转正向下深度|
|DO|abiotic_water_sO2W|mg O2/L|g O2/m³|量纲相等，数值乘1；不要用GOTM的o2.scale_factor=31.25转换WET sO2W|
|CHLA|wet_chla_calculator_result|μg Chl a/L|WET聚合wet_chla单位ug/L|按实际输出metadata解析calculator别名，数值乘1|
|NH4|原workshop XML缺项；官方ParSac XML有abiotic_water_sNH4W|mg N/L操作约定|g N/m³、ammonium|补显式映射，保留原XML缺项证据|
|NO23|abiotic_water_sNO3W|mg N/L操作约定|g N/m³、nitrate|默认不进入科学目标；合计NO2+NO3与纯NO3差别未解释|
|PO4|abiotic_water_sPO4W|mg P/L操作约定|g P/m³、phosphate|数值乘1，待实验室metadata进一步核实分析对象|
|TOTN|wet_totN_calculator_result|mg N/L|WET水柱聚合g N/m³|必须核实聚合成员，不能只取NH4+NO3|
|TOTP|wet_totP_calculator_result|mg P/L|WET水柱聚合g P/m³|必须核实聚合成员，不能只取PO4|

源码证据：当前及固定上游`src/abiotic_water.F90`注册sO2W/sNH4W/sNO3W/sPO4W为g/m3，sNO3W名称为nitrate；原官方ParSac注释hNO3DenitW为mgN/L，且官方入流说明分别明确mg N/L和mg P/L。当前`om_pool.F90`、`phytoplankton.F90`、`zooplankton.F90`把真实水柱N/P状态加入wet_totN/wet_totP，`abiotic_water.F90`加入溶解营养盐及吸附P。Chl a由藻群oChla聚合且abiotic dummy注册ug/L。必须从实际运行NetCDF的单位、变量及固定源码验证，不能假设所有求解器版本输出名称相同。旧模型和当前模型的聚合成员可能不同；不要把沉积物g/m²、鱼的面积生物量或水柱积分量直接加到g/m³。

NO23文件名通常暗示亚硝酸盐+硝酸盐，但该包未给化验定义。这里不将这个推断冒充已核实定义。官方XML的历史映射只能作为带明示假设的原案例重放；严格率定须取得StanCode/分析参数、含氮质量基础、亚硝酸盐分量或原作者解释。单纯把文件重命名NO3不是核实。

## 湖泊身份、站点和坐标

原workbook：longitude9.84、latitude56.11、最大深度32m、32层、表面积1821420m²、1990-01-01至2005-12-31。已率定GOTM：location.name=Lake Ravn、56.11/9.84、深度32.65m、33层、1990-01-01 12:00至2005-12-31 12:00、dt3600s。默认独立GOTM：同经纬度、32m/32层、1990-01-01 00:00至2005-12-31 00:00。配置不同必须分别保存，不能静默混用。

真实边界`Ravn_outline.shp`字段NAVN=Ravn Sø、DMU_REC=490、LONR=21321、AREA=1782658.425m²、X_COORD=552363.27167、Y_COORD=6218184.35167。这些是湖面/轮廓属性，不能当观测站ID和坐标。其PRJ与测深PRJ为ETRS89/UTM32N，采用EPSG:25832；测深是33个polygon，字段DYBDE、area_hyps，不是XYZ点。DBF含丹麦ø，UTF-8解码失败，cp1252可读；导入必须显式存实际编码选择。

轮廓bbox为(551242.1996,6217596.6063,553484.3437,6218772.0971)，测深bbox为(551242.6463,6217596.4251,553488.8224,6218777.4242)。两位小数模型经纬度转换到EPSG:25832约(552239.3582,6218640.2860)，不是高精度采样坐标。

`hypsograph.csv`从(0,1546)增至(32.65,1813954)，不是直接的“正向下深度→面积”序列。官方默认`hypsograph.dat`头为`33 3`；本地GOTM `meanflow/hypsograph.F90`的up_down=3明确从湖底参考向上读取并根据depth0移位。因此必须按底参考高度解释，不能把高度32.65m当湖底深度。面积来源/最大值与workbook、outline存在差异，应以选择的原模型版本重放并独立报告几何差异。

## 强迫与运行覆盖

- meteo_file.dat：1979-01-01 07:00至2019-12-27 23:00，359297条数据；明确头为u10、v10、pressure_hPa、air_temperature、dew_point、cloud_cover_frc。hPa→Pa乘100；露点不能直接填入GETM相对湿度列。
- inflow.dat：1990-01-01 00:00至2018-12-31 00:00，696条，m³/s。
- inflow_chem.dat：相同696条，PPOM/PDOM/PO4/NPOM/NDOM/NO3/NH4，mg/L，N/P基准见官方说明；官方文本说明这些是全湖聚合流量及流量加权浓度，而非有确定地理河口的每一条支流。SWAT目录中的output.rch属于流域模型情景输出，不是实测强迫证明。
- 原`wet_obs.xml`每变量spinupyears=6。推荐工程分割为1990–1995热身、1996–2000训练、2001–2005留出；这不是官方原率定分割。两套官方calibrated_config可能已使用全部观测，不能在这些已率定参数上把2001–2005称为从未使用过的独立验证。要做留出验证需从默认参数重新率定，或公开承认已有历史信息泄漏。

|变量|原已率定run范围内行数|建议训练窗口原行数|建议验证窗口原行数|
|---|---:|---:|---:|
|TEMP|6001|1686|1852|
|DO|5872|1671|1812|
|CHLA|1074|386|195|
|NH4|1133|385|261|
|NO23|1147|389|261|
|PO4|1137|382|263|
|TOTN|1151|389|265|
|TOTP|1133|381|262|

训练按1996-01-01 12:00开始，验证2001-01-01 00:00开始、止于2005-12-31 12:00。代码实现应以明确半开区间1996-01-01 00:00～2001-01-01 00:00与2001-01-01～2006-01-01评分，且先裁到模型实际stop；当前盘点中没有1996-01-01上午观测，所以训练计数一致。

## GOTM到当前GETM的静态迁移结论

不能直接复制gotm.yaml/fabm.yaml并声称等效：原fish_mod当前库不注册；当前fish/fish_pclake、模块化POM/DOM/humus和猎物接口已经演进，旧abiotic内sDPOMW等状态不存在。官方原始配置还含疑似异常的macrophyte POM_N/P耦合互换（`fabm-all_obs.yaml`中POM_N_pool_water→sPPOMW、POM_P_pool_water→sNPOMW），不能静默修正后称为原配置重放。旧GOTM hypsograph底通量分配、流入层0～-1m、自动水量平衡也不与三维GETM岸线底栖/河口配置逐字段等价。

现有产品`input_rivers_save`只写Q/temp/NH4/NO3/PO4，不写PPOM/NPOM/PDOM/NDOM，而且简短`_nh4`列不符合GETM FABM reader实际寻找的`<河名>_<model state variable name>`。`3DWET/src/getm/src/ncdf/ncdf_rivers.F90`约180行确实按完整FABM状态名查列；迁移须实际验证这些完整命名列被日志识别、载荷非零且质量一致，不能只看到rivers.nc创建成功。强迫温度和水量闭合也需明确原模型假设，不得补造实测温度或河口坐标。

当前`get_timeseries`默认level=-1=表层，并自动限制3000点；`calibration_comparison`及`calibration.run_model_in_temp`均未传深度/无降采样参数。1990–2005六小时输出约2.3万时刻，现有默认抽稀会让原24h配对不可靠。原upload只接受CSV/XLSX并保存time/value；depth/unit/station/quality丢失。率定数据目前放全局DATA_DIR，跨案例没有湖身份隔离。必须同步修复这些基础接口，而非仅加.obs文件解析器。

## 许可与尚未核实项

两个ZIP中未发现数据LICENSE/COPYING/README条款。官方页面明确QWET为开源，但没有明确这些历史观测、底图及SWAT/气象的再分发许可；不能把代码GPL推及全部数据。现阶段应用应支持用户选择已下载原目录，或从官方URL按需下载并保存出处/校验；不要将研究ZIP/官方exe装进公开安装包，直到取得适用数据及二进制再分发条款。该结论是许可证据不足，不是宣布禁止研究使用。

未核实：观测精确测站/历史移站、时区、NO23分析定义、检出限/质量码、原始观测提供单位的逐文件凭证、气象与SWAT强迫来源及不确定性、校准参数历史训练窗口、原exe构建版本和哈希对应源码、数据再分发许可。导入预览可以展示这些未知项；只有原一维代表性假设范围内的重放可继续，不得自动升级为三维站点严格匹配。

后续丹麦官方监测元数据检索与替代案例证据另见本文件追加记录及实施计划。实施工作见 `docs/superpowers/plans/2026-10-16-ravn-calibration-implementation.md`。

## 2026-10-17 原官方模型实际运行补验

在新的隔离目录 `build/ravn-official-replay-20261017-attempt01/Default` 中展开已校验的 `default_lakeRavn_setup.zip`，实际运行官方 `gotm_release.exe`。没有改写原参数、气象、入流、日期、层数或输出配置。原设置 `restart.load=false`，1990-01-01 00:00 至2005-12-31 00:00，dt3600秒、32层/32米。进程退出0，日志明确GOTM finished；实际耗时19.97秒、日志CPU19.14秒。

真实输出 `output.nc` 为155,083,660字节，5,844个逐日时刻、276个变量，首尾精确覆盖原设置、步长86400秒。逐变量分128时刻扫描全部未屏蔽数据，没有NaN/Inf；h全部正且全时刻累积深度32米。原参数和强迫哈希保持一致；唯一变化的原文件是求解器在结束时写出的 `restart.nc`，原始字节仍保留在已校验ZIP中，不能把该变化隐藏成“全部输入文件未变”。

日志版本为GOTM `v5.3-679-gc0add0a2-dirty (au branch)`、FABM `v0.95.3-298-gf73ec4c (au branch)`、WET `943d3c4 (master branch)`、Intel18编译器。它是独立的官方原柱模型基线，不能称为当前本地GETM/WET修复版或最新WET。输出总N/P计算器单位字段为空，深度字段为实际层厚h而不是本地hn；后续读取器须显式适配并保留来源。

证据为该目录 `verification.json`、`native.log`、`output-inventory.json` 及真实NetCDF。复现脚本在 `build/diagnostic-version-20261016/replay_official_ravn.py`、`check_official_ravn_output.py`，前者拒绝覆盖已有目录。此项只证明原模型完整运行和有限输出，不证明生态收支或预测精度；尚未做实际观测配对、优化或应用内接入，也不计入五套新数据的完整验收。
