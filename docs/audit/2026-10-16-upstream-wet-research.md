# WET官方版本与已有实测案例证据

核对日期2026-10-16。官方GitLab API标签首项为v2.3，提交89e172cd6f113bff2ffe9e9680cbbeb7e0dd92a6；master提交d2eee4419ab6762c092e07dc79316feff9efec5c，2026-07-17。官方README中“latest stable 0.2.0”与标签有历史不一致，应固定实际标签/提交，不能仅引用README旧文字。

完整源码存于`build/wet-upstream-research-20261016/wet-master-d2eee441.zip`，ZIP全部条目校验通过，52902752字节，SHA256 457c39fcb052799189a6379bead90dd98501aae798a6ef2516270e3ebc058941。保存API原文master.json/tags.json、归档条目清单和本地逐文件差异（已消除CRLF差异）。bivalves、bot_pel_interface、burial、fish_pclake、zoobenthos、zooplankton、version模板相同；主分支新增ghg_gasses，并修改藻类、非生物过程、交换、有机物等。本地已有分离的碳/甲烷实现及鱼类、植物和重启修复，不能用上游目录直接覆盖。

本地zooplankton.F90已有动态nPrey和每猎物参数/模型依赖，生态组装应真实扩展这些实例和端口。现有ecology_network.js只能编辑已有实例、现有参数和已有耦合端口；图形新增节点必须对应FABM配置、初始化、输出及汇总项的实际变更。

官方Lake Ravn workshop完整案例ZIP已下载并通过全条目校验，32714861字节，SHA256 9a8767c2b5e235de268d31d1808220bcb062deb2704ef890b137827ef062a56b。保存在`build/wet-upstream-research-20261016/Lake_Ravn_workshop-full.zip`，含八种原始观测、气象河流、实际边界/测深、工作簿及两组已率定配置。首次PowerShell下载提前断开，仅产生5506598字节的不完整Lake_Ravn_workshop.zip，保留为失败证据，禁止使用；后续完整文件单独命名并验证。

TEMP.obs原记录含时间、负的垂向坐标、实测温度（如1971-09-19 12:00:00、-0.2、14.7及-25.0、6.3）。wet_obs.xml明确TEMP→temp、DO→abiotic_water_sO2W、CHLA→wet_chla_calculator_result等映射及spinupyears=6；仍需核对单位、NO23定义和变量总量计算。不能删掉深度后当表层观测导入，不能套用于不同湖泊。

来源：[官方标签](https://gitlab.com/wateritech-public/waterecosystemstool/wet/-/tags)、[官方模型仓库](https://gitlab.com/wateritech-public/waterecosystemstool/wet)、[Zenodo v2.3](https://zenodo.org/records/17453175)、[Aarhus University案例说明](https://projects.au.dk/wet/gleon-gsa-limnoseries-wet)。

目前这只是已验证的来源与兼容性研究；新功能尚未实施，也不构成五次验收通过。
