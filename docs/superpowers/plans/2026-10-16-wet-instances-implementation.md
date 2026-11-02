# WET 任意藻类与鱼类实例 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. 原调查子任务仅限研究的约束已结束；主目标已明确要求实施真实多实例及完整验证，可按既有授权继续，不再要求用户选方案。每项先红后绿、需求与质量独立审查；保留本地修复和所有案例，不擅自提交整棵未整理工作树。安装整版及五轮门槛不变。

**Goal:** 提供水质与生态独立入口，支持任意数量真实 WET 藻/鱼实例、唯一引用名与显示名、可生效食物网/阶段耦合、可恢复编辑，并用新增两藻+两鱼的原生输出、重载、重建和重启证明其可用。

**Architecture:** `fabm.yaml` 是模型参数、初值、真实端口的单一科学配置；新增小型实例目录/端口编译器与跨文件事务服务，UI、旧配置路由和两个 builder 调同一服务。实例元数据与可恢复删除放旁车，不向 FABM 根插入私有字段。采用官方最新核实的动态能力与明确的上游版本清单，保留本地 fish/om_pool/macrophytes、inorganic_carbon/methane 与 GETM 适配；阶段鱼必要修复只在隔离候选求解器验证后进入正式集成。

**Tech Stack:** Python/Flask、PyYAML AST 与原生兼容 scalar emitter、vanilla JavaScript、NetCDF4/NumPy、现有 GETM-FABM-WET Fortran solver 和便携原生工具链。

---

## 边界、依据与完成定义

设计依据为 `docs/superpowers/specs/2026-10-16-navigation-ecosystem-calibration-proposal.md`；代码证据和官方链接见 `docs/audit/2026-10-16-wet-instance-code-map.md`。本计划负责实例与水质/生态配置链路；主导航外观和实测率定有各自计划，但本计划暴露必要目录与页面入口，不以它们未完成为由把实例做成静态示意。

完成必须同时满足：

- 从 UI 实际新增 `algae_a`、`algae_b`、`fish_grazer`、`fish_predator`，四者分别是独立 `wet/phytoplankton` 或 `wet/fish`，不复用固定三鱼槽位。
- 新增/复制/引用名重命名/显示名修改/禁用或删除/恢复均更新实际 YAML 及受影响旁车，预览后事务提交，运行中拒绝、重复名/悬空引用拒绝、并发过期请求拒绝。
- `prey_modelN`、`PLANpreyN`、`BENTpreyN`、`PISCpreyN` 和明确的阶段 state ports 可配置，计数/逐猎物参数同步；关系变化具有非零真实过程通量和可重复的状态响应。
- 模型输出包含新增四实例各自 D/N/P/C 状态，显示名、单位与原生来源一致；聚合无漏项和重复项。
- 页面/服务重载、CLI/GUI重建不会丢失任意实例、参数、初值、关系与输出选择。
- 同配置 checkpoint/resume 与 continuous 输出对齐；新拓扑不能套旧索引状态。阶段繁殖日期与成熟碳转移必须专项通过。
- 不覆盖已有科学修复，不将官方 master 开发模块伪称稳定 v2.3。正式连续五轮及安装包验证由主流程实施，本计划的短模型探针不能计为五轮。

## 文件分工

| 新建文件 | 单一职责 |
|---|---|
| `3DWET/app/wet_instance_catalog.py` | 以 model 分类、模板/状态/条件端口/schema；引用身份校验；原生字段名碰撞检测 |
| `3DWET/app/wet_foodweb.py` | 把类型明确的关系编译为动态计数、逐猎物参数、真实模型/状态端口；依赖/单位/域检查 |
| `3DWET/app/case_model_transaction.py` | 版本/运行锁/备份/暂存/日志/回滚/启动恢复；现有 YAML无关文本保留 |
| `3DWET/app/wet_instances_api.py` | 两个模型实例接口与目录过滤；兼容旧 network API；不承载科学公式 |
| `3DWET/app/wet_restart_identity.py` | 运行清单、FABM状态顺序/拓扑签名、checkpoint hash登记和热启身份检查 |
| `3DWET/model_builder/wet_assembly.py` | 新建种子与已有文档重建策略，共用初值/输出集成；不能从模板覆盖已有生态文档 |
| `3DWET/app/static/js/wet_instances.js` | 水质/生态目录、添加/复制/重命名/删除/恢复、预览差异和错误定位 |
| `3DWET/app/wet_upstream_manifest.json` | 固定 release/master、采用能力、保留修复、源码与binary指纹；只读运行元信息 |
| `tests/test_wet_instance_catalog.py` | 分类/条件schema/唯一名/能力契约 |
| `tests/test_wet_foodweb.py` | 动态端口编译/删除/类型域单位校验 |
| `tests/test_wet_instance_transactions.py` | API事务/过期/案例切换/进程和崩溃回滚 |
| `tests/test_wet_instance_rebuild.py` | GUI与CLI重建/各实例初值/订阅/默认值保持 |
| `tests/test_wet_restart_identity.py` | 顺序、同维错配、改名、binary变更、checkpoint hash校验 |
| `scripts/verify_wet_instances.py` | 隔离真实求解器探针/状态/通量/聚合/敏感性/重启证据归档 |
| `tests/native_wet_instances_probe.f90` | 采用同一FABM库的注册/耦合/state order探针，用于候选构建核验 |

修改文件：`server.py`、`lake_points_api.py`、`fish_support.py`、`output_subscriptions.py`、`variable_reference.py`、`variable_registry.json`、`fabm_docs.json`、`parameter_defaults.py`、`hotstart.py`、`ecology_network.js`、`index.html`/现有页面与导航注册、`model_builder/build_fabm_yaml.py`/`assemble_case.py`、`preprocessor/generate_initial_conditions.py`。原生必需阶段修复仅触及 `src/wet/src/fish.F90` 和既有探针/候选构建；不先合并全套 master。

## 最小 API 与保存协议

### GET /api/model/instances

Query `domain=water_quality|ecology|all`，可选 `family=phytoplankton|fish|zooplankton|...`。水质涵盖 abiotic_water/abiotic_sediment/om_pool/sediment_exchange/burial/bot_pel_interface/inorganic_carbon/methane；生态涵盖 phytoplankton/zooplankton/zoobenthos/bivalves/macrophytes/fish/fish_pclake。同一个真实实例只登记一次，两个目录的相互依赖是链接。

```json
{
  "case_path": "C:/.../case/MyLake", "revision": "sha256",
  "upstream": {"release": "v2.3", "release_commit": "89e172cd6f113bff2ffe9e9680cbbeb7e0dd92a6", "master_commit": "d2eee4419ab6762c092e07dc79316feff9efec5c", "adoption": "local-getm-compatible"},
  "solver_sha256": "sha256", "instances": [], "templates": [],
  "edges": [], "targets": [], "deleted": [], "restart_compatible": true
}
```

每实例返回 `id`（稳定 UUID旁车身份）、`name`（真实引用名）、`long_name`、`model`、`family`、`domain`、`enabled`、参数/初值及其 units、typed ports、受影响依赖；`target` 条目含 `kind=model|state`、`reference`、states、domain/units/来源，绝不从一条任意字符串推断“合法端口”。

### POST /api/model/instances/transaction

一次提交可同时新增四实例、接入旧 zoo、调整输出并保存；无四次部分提交。`mode=preview`只计算内存差异，`mode=apply`提交与同内容预览hash匹配的变更。`revision`包含所有受管文件的存在标志、文件名和字节hash；`preview_hash`包含 revision、operation规范JSON、候选文件hash、solver hash；案例切换、运行开始、第三方文件改动均拒绝。

```json
{
  "case_path":"C:/.../case/MyLake", "revision":"sha256", "mode":"apply", "preview_hash":"sha256",
  "operations":[
    {"op":"add","name":"algae_a","long_name":"藻群甲","template":"diatoms","initialization":{"sDW":0.12,"sNW":0.012,"sPW":0.0012,"sCW":0.054}},
    {"op":"add","name":"algae_b","long_name":"藻群乙","template":"greens","initialization":{"sDW":0.08,"sNW":0.008,"sPW":0.0008,"sCW":0.036}},
    {"op":"add","name":"fish_grazer","long_name":"浮游摄食鱼群","template":"fish-planktivore","parameters":{"qStage":0,"qTrans":0},"initialization":{"sD":0.02,"sN":0.002,"sP":0.00044,"sC":0.009,"fVul":1.0}},
    {"op":"add","name":"fish_predator","long_name":"食鱼鱼群","template":"fish-piscivore","parameters":{"qStage":0,"qTrans":0},"initialization":{"sD":0.01,"sN":0.001,"sP":0.00022,"sC":0.0045,"fVul":1.0}},
    {"op":"set_foodweb","name":"fish_grazer","groups":{"PLAN":[{"target":"algae_a","suffix":"W","clearance":0.18,"gut_occupation":1.0},{"target":"algae_b","suffix":"W","clearance":0.24,"gut_occupation":1.0}],"BEN":[],"PISC":[]}},
    {"op":"set_foodweb","name":"fish_predator","groups":{"PLAN":[],"BEN":[],"PISC":[{"target":"fish_grazer","clearance":0.021,"gut_occupation":1.0}]}},
    {"op":"subscribe","selectors":["algae_a/*","algae_b/*","fish_grazer/*","fish_predator/*"]}
  ]
}
```

参数/初始化数值为工程探针，不宣称物种率定。一般UI默认优先选择真实 zoo 作为鱼 PLAN 猎物；直接藻摄食仅在物理生物意义适合且目标 W states全满足时选。测试另增加已有 zoo 的两藻 `prey_modelN`，确保两条独立食物链均验证。

其他 operations 精确形状：

```json
[
  {"op":"clone","source":"algae_a","name":"algae_c","long_name":"藻群丙"},
  {"op":"rename","name":"algae_c","new_name":"algae_variant"},
  {"op":"update","name":"algae_variant","long_name":"藻群丙变体","parameters":{"kDRespPhyt":0.1},"initialization":{"sDW":0.05}},
  {"op":"set_couplings","name":"algae_variant","coupling":{"NH4_pool_water":"abiotic_water/sNH4W"}},
  {"op":"set_stage","name":"fish_grazer","qStage":2,"adult":"fish_predator","juvenile":null},
  {"op":"set_enabled","name":"algae_variant","enabled":false,"repairs":[]},
  {"op":"delete","name":"algae_variant","repairs":[]},
  {"op":"restore","deletion_id":"UUID","name":"algae_variant"}
]
```

示例 `kDRespPhyt` 必须由实际 phytoplankton schema允许后使用；不允许客户端任意 key进入 YAML。`repairs`为同一事务中的显式 `set_foodweb`/`set_couplings` operations；引用者存在且没有修复时返回 `DEPENDENTS_EXIST`，不静默删链。delete留 tombstone、原完整实例和受影响文件备份，restore同样验证引用/名称/当前能力，不能绕过禁用对象依赖检查。

响应返回 `changes`（实例/真实ports/counts/初值/订阅/默认值/重启失效）、`warnings`、`backup`、`revision`、`preview_hash` 和原生候选验证状态。400 `INVALID_NAME|UNKNOWN_PORT|INVALID_TARGET|DOMAIN_MISMATCH|UNIT_MISMATCH|DEPENDENTS_EXIST|NONFINITE_VALUE|NATIVE_YAML_UNSUPPORTED`，409 `STALE_REVISION|CASE_CHANGED|CASE_RUNNING|RESTART_TOPOLOGY_CHANGED`，422 `NATIVE_MODEL_REJECTED`，500 `TRANSACTION_FAILED` 且恢复原文件。

旁车 `.studio-config/wet_instances.json`（version=1）只放 id/name映射、template出处、已删除实例和恢复信息；科学参数/耦合/初值仍在fabm.yaml。`initial_conditions.json.water_quality`继续使用 `instance.variable`，暂不破坏旧UI；`output.yaml`保持用户订阅语义，精确native字段随事务更新。默认快照`.studio-config/fabm_defaults.json`随 rename/clone/restore一起处理。

## Task 1：固定采用矩阵与实例能力目录

**Files:** Create catalog/manifest与测试；Read `fish.F90`、`phytoplankton.F90`、`zooplankton.F90`、`variable_registry.json`、`fabm_docs.json`及官方固定源码。

- [ ] 先写失败测试：任意 `name` 按 model分类，四个新增实例和一个禁用实例名字必须全局唯一；字段flatten碰撞也拒绝。

```python
def test_arbitrary_names_use_real_model_family():
    from wet_instance_catalog import classify_model, validate_names
    assert classify_model('wet/phytoplankton') == ('ecology', 'phytoplankton')
    assert classify_model('wet/fish') == ('ecology', 'fish')
    assert classify_model('wet/abiotic_water') == ('water_quality', 'abiotic_water')
    validate_names({'algae_a': {'model':'wet/phytoplankton'},
                    'algae_b': {'model':'wet/phytoplankton'},
                    'fish_grazer': {'model':'wet/fish'},
                    'fish_predator': {'model':'wet/fish'}}, {})
```

- [ ] 运行 `python -m pytest tests/test_wet_instance_catalog.py -q`，应先因新模块不存在失败；再实现明确model集合和验证。引用名新建约束 `[A-Za-z][A-Za-z0-9_]{0,31}`，不接受 `/ . - 空格`；旧合法长引用名允许读取、保持，不强制迁移。检查 active、disabled、tombstone保留身份与原生 `instance_state` 的碰撞。

```python
import re
ECOLOGY = frozenset(('phytoplankton','zooplankton','zoobenthos','bivalves','macrophytes','fish','fish_pclake'))
WATER_QUALITY = frozenset(('abiotic_water','abiotic_sediment','om_pool','sediment_exchange','burial','bot_pel_interface','inorganic_carbon','methane'))
def classify_model(model):
    family = model.removeprefix('wet/')
    if model.startswith('wet/') and family in ECOLOGY: return 'ecology', family
    if model.startswith('wet/') and family in WATER_QUALITY: return 'water_quality', family
    return 'other', model
def validate_names(instances, disabled):
    overlap = set(instances) & set(disabled)
    if overlap: raise ValueError('DUPLICATE_NAME: ' + ', '.join(sorted(overlap)))
    for name in instances:
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,31}', name): raise ValueError('INVALID_NAME: ' + name)
```

完整验证实现分开 `validate_new_name()` 与 `validate_existing_document()`，不要用此示例新名约束拒绝旧案例。显示名用现有native_yaml_scalar，允许普通中文单行，限制120字符；不将显示名拿来引用或输出字段拼接。

- [ ] 从本地实际注册代码建立模型/schema目录：state name、domain、units、条件(qStage/diagnostics/lSi)、模型dependency与state dependency、dynamic families、默认与范围。保留来源行/采用commit。`fabm_docs.json`/registry是解释元数据，不能单独证明一个条件diagnostic已经注册。
- [ ] `wet_upstream_manifest.json`记录：v2.3 release SHA、master SHA、当前实际采用源码sha256、保留修复列表、native library与exe sha256、ghg_gasses未采用/本地两气体采用；不把本地混合版标为原封不动master。对native probe输出再登记有序states/units/ports/aggregates，并将probe指纹绑定binary。
- [ ] 再运行catalog测试，四实例family与字段冲突反例全部通过。此任务不改变生产solver。

## Task 2：真实 foodweb 与阶段端口编译器

**Files:** Create `wet_foodweb.py`、`tests/test_wet_foodweb.py`；Read官方/本地原生注册源码。

- [ ] 先写两个失败测试：nPLAN可到4以上、连续索引；减少到1时旧2–4的count/port/参数必须被清除，保留无关couplings。

```python
def test_dynamic_plan_family_is_not_limited_to_three():
    from wet_foodweb import compile_fish_diet
    inst = {'model':'wet/fish','parameters':{'nPLAN':1},
            'coupling':{'NH4_pool_water':'abiotic_water/sNH4W','PLANprey1':'old'}}
    prey = [{'target':f'algae_{i}','suffix':'W','clearance':0.2,'gut_occupation':1.0} for i in range(5)]
    compiled = compile_fish_diet(inst, {'PLAN':prey,'BEN':[],'PISC':[]})
    assert compiled['parameters']['nPLAN'] == 5
    assert compiled['coupling']['PLANprey5'] == 'algae_4'
    assert compiled['parameters']['PLANprey_suffix5'] == 'W'
    assert compiled['coupling']['NH4_pool_water'] == 'abiotic_water/sNH4W'
    reduced = compile_fish_diet(compiled, {'PLAN':prey[:1],'BEN':[],'PISC':[]})
    assert 'PLANprey5' not in reduced['coupling']
    assert 'cClearPlan5' not in reduced['parameters']
```

- [ ] 运行 `python -m pytest tests/test_wet_foodweb.py -q` 确认新接口失败，然后实现动态family编译核心，输入必须先通过目录target contract，任何重复/自食模型引用拒绝。

```python
from copy import deepcopy
import re
FISH_FAMILIES = {
    'PLAN': ('nPLAN','PLANprey','PLANprey_suffix','cClearPlan','fGutOccPlan'),
    'BEN': ('nBEN','BENTprey','BENprey_suffix','cClearBent','fGutOccBent'),
    'PISC': ('nPISC','PISCprey',None,'cClearPisc','fGutOccPisc'),
}
def compile_fish_diet(instance, groups):
    result = deepcopy(instance)
    params = result.setdefault('parameters', {})
    coupling = result.setdefault('coupling', {})
    for group, (count, port, suffix, clearance, gut) in FISH_FAMILIES.items():
        rows = groups[group]
        for mapping, prefixes in ((coupling, (port,)), (params, tuple(x for x in (suffix,clearance,gut) if x))):
            for key in list(mapping):
                if any(re.fullmatch(re.escape(prefix)+r'\d+', key) for prefix in prefixes): mapping.pop(key)
        params[count] = len(rows)
        for index, row in enumerate(rows, 1):
            coupling[f'{port}{index}'] = row['target']
            params[f'{clearance}{index}'] = row['clearance']
            params[f'{gut}{index}'] = row['gut_occupation']
            if suffix and row.get('suffix'): params[f'{suffix}{index}'] = row['suffix']
    return result
```

空suffix省略，不能发 `prey_suffix: ''` 给当前Fortran reader。类型严格：count整数≥0、clearance有限≥0、gut occupation有限>0、suffix只允许目录明确合法的空/W/S等值；同一family同target/suffix重复拒绝。不要删除 `plankton_*_FoodN` 等未知手工override：存在与生成模型端口冲突时预览列出且要求同一事务明确移除，否则拒绝。

- [ ] 实现zoo编译为 `nPrey`、`prey_modelN`、`cClearPreyN`、`fGutOccPreyN`、`prey_suffixN`、`lSiN`；按真实target states检查 D/N/P/C，lSi=true必须有oSi后缀。BEN targets必须具有底栖与mirror两套state；PISC targets必须为真实fish并含fVul/pred_dummy能力；不能把任何model名都列作可用猎物。
- [ ] 实现stage为明确6个state映射：D→sD、N→sN、P→sP、C→sC、Res→sFRes、Siz→sDSiz。qStage1/3生成juvenile_*，qStage2/3生成adult_*；qStage0清除两族。目标必须qStage>0并有相应state；禁止自身目标、缺一个碳端口、非法初始size、`cDfin<=cDinit`、reserve越界与非正egg size。阶段成环允许明确的成熟→繁殖cycle；不以普通图无环规则误拒绝官方手动阶段耦合，最终由native装配检查。
- [ ] 删除/禁用依赖扫描同时识别裸模型引用与`instance/state`，检查initial/output/defaults旁车及显式汇总引用；引用名重命名只改准确prefix，不使用全局字符串替换。clone自引用重映射到新实例，外部引用保持并列入preview。
- [ ] 运行foodweb测试并检查生成的真实YAML快照：5个PLAN、2个BEN、4个PISC、两藻zoo和两个阶段对象；动态端口超过3作为防固定槽位回归。

## Task 3：跨文件事务、预览、备份与恢复

**Files:** Create transaction/API与测试；Modify lake_points_api.py network route、server.py注册与相关写route。

- [ ] 先写故障注入测试：替换第三个文件时抛OSError，所有参与文件恢复原byte；过程崩溃后下次启动先回滚pending transaction，不能加载半份配置。

```python
def test_stale_multi_file_revision_never_mutates(client, case, snapshot):
    state = client.get('/api/model/instances').get_json()
    (case/'initial_conditions.json').write_text('{"trophic":"custom"}', encoding='utf-8')
    before = snapshot(case)
    response = client.post('/api/model/instances/transaction', json={
        'case_path':str(case), 'revision':state['revision'], 'mode':'apply',
        'preview_hash':'stale', 'operations':[{'op':'rename','name':'algae_a','new_name':'algae_new'}]})
    assert response.status_code == 409
    assert snapshot(case) == before
```

测试fixture使用真实本地模板复制到pytest tmp_path；Flask路由用captured case path及同一run lock；`snapshot`仅hash参与文件，不把本次测试目录临时日志当产品状态。

- [ ] 实现revision：按固定受管路径排序，hash每文件name + exists + bytes；至少 `fabm.yaml`、`fabm_disabled.yaml`、`initial_conditions.json`、`output.yaml`、`getm_fabm.inp`、实例旁车、默认值旁车、`.studio-hotstart.json`。`fabm_init.nc`仅在本事务确实rename/drop变量或改变spatial初值时参与，始终只读检查其是否覆盖待修改初值。

```python
import hashlib
def case_revision(case, names):
    digest = hashlib.sha256()
    for name in sorted(names):
        path = case/name
        payload = path.read_bytes() if path.exists() else None
        digest.update(name.encode('utf-8') + b'\0')
        digest.update(b'missing\0' if payload is None else b'present\0' + hashlib.sha256(payload).digest())
    return digest.hexdigest()
```

- [ ] 实现事务状态机：`validate → preview → native candidate check → lock/recheck → backup → journal(prepared) → replace each staged file → journal(committed) → refresh caches`。候选原生检查在新临时目录进行，不在用户案例试运行；检查后重新持锁对revision/active identity/_case_in_use/solver hash验证。锁由运行开始、所有相关写route共用。启动/案例打开先处理prepared日志回滚；用户可恢复已提交事务为新事务，不能直接覆盖当前配置。
- [ ] 结构编辑按PyYAML node byte范围替换整个受影响instance block或插入新block，未触及块原byte不变；generated emitter只写block mappings/sequences，复用native_yaml_scalar且拒绝重复key/共享anchor、alias、flow collection和无法安全拆分的输入。不要无差别safe_dump整个用户文件。以PyYAML解析结果等于expected检查文本编辑正确性，并用现有native reader probe核验新block。
- [ ] backup为`backups/instances-<UUID>/`，保存全部参与文件、缺失标志、before/after hash、operations、upstream/solver、时间、影响及tombstone；每文件flush+fsync后os.replace。Windows多文件无原子目录交换，必须如实称“锁保护的可恢复事务”，不宣称崩溃时文件系统整体原子。
- [ ] 旧network scalar route委托同一事务；旧参数/initial/module/output route更新也使用case lock/revision或在同锁受管事务中更改；否则可以绕过一致性保护。返回旧字段形状兼容已有JS。
- [ ] 运行 `python -m pytest tests/test_wet_instance_transactions.py tests/test_ecology_network.py -q`；fault injection、stale、run started while checking、case switch、invalid native scalar与未知root保留全过。

## Task 4：建模、初值、启停与默认值集成

**Files:** Create wet_assembly.py/test_wet_instance_rebuild.py；Modify GUI build、CLI build、fish_support、initial routes、initial generator、parameter_defaults。

- [ ] 先写失败测试：GUI建完案例后事务新增两藻两鱼并独立初值，重建两次及CLI assemble一次，四个instance、params、couplings、display、output selector和默认值仍相同；旧运行结果不能参与这个配置断言。

```python
def test_rebuild_preserves_user_ecosystem(case, build_case, add_four_instances):
    import yaml
    add_four_instances(case)
    before = yaml.safe_load((case/'fabm.yaml').read_text(encoding='utf-8'))
    build_case(case)
    build_case(case)
    after = yaml.safe_load((case/'fabm.yaml').read_text(encoding='utf-8'))
    for name in ('algae_a','algae_b','fish_grazer','fish_predator'):
        assert after['instances'][name] == before['instances'][name]
```

- [ ] `wet_assembly`区分新建与重建：不存在fabm.yaml才从已验证模板创建；已存在时保留完整生态文档，重新生成hydro/grid关联配置但只通过明确operation更新生态初值。已有生态profile按事务保留并叠加，不从Luoma读默认后覆盖。GUI `case_build`和CLI builder调用相同策略；grid改变只重生成与grid关联的spatial初值，不能重置uniform biomass或食物网。
- [ ] `fish_case_enabled`改为检测任意启用`model=='wet/fish'`；界面fish开关只表示是否存在启用鱼，旧三鱼模板作为明示的组合添加操作。禁用所有鱼若有外部引用必须显式repair，完整配置放disabled sidecar，恢复保持原名/关系；不自动注入固定三鱼替代自定义鱼。
- [ ] initial routes按schema验证有限值、范围、状态存在、native units；新实例默认补齐本地源码要求的D/N/P/C、fVul与阶段条件states，模板初值与用户override一起存。`water_quality`旧字段名暂保留但接受真实所有实例；移除/rename同步准确`instance.variable` keys，异常返回400，不静默continue后success=true。
- [ ] 统一spatial initial generator到已修复macrophytes `(y,x)` D/N/P/C 四字段。uniform新藻/鱼仍用YAML，除非用户明确提供spatial场。保存初值前检查fabm_init.nc是否有对应`instance_state`：有则在事务内更新/rename/remove明确字段或拒绝并说明该场会覆盖uniform；不能只改YAML后给虚假成功。
- [ ] 分类使用catalog model而非MODULE_CATEGORIES固定名；defaults在clone时从source复制对应参数基线，rename移动identity映射，delete保留tombstone，restore找回基线；普通GET不得写defaults或legacy迁移。
- [ ] 运行 `python -m pytest tests/test_wet_instance_rebuild.py tests/test_initial_conditions_rebuild.py tests/test_native_macrophyte_initialization.py -q`。native probe需要工具链时应列为原生验证阶段执行，不把skip算通过。旧CLI generator二维格式修复需保留existing tests并新增GUI/CLI一致性比较。

## Task 5：原生聚合、字段注册与输出订阅

**Files:** Modify output_subscriptions.py、variable_reference.py、registry/docs；Create native probe/tests；Read fabm_coupling.F90/fabm_builtin_models.F90。

- [ ] 先写失败测试：新鱼qStage0目录不列sFRes/sDSiz；qStage>0列出；diagnostics=false不订阅tDConsFiPlan_N；5个prey的diagnostics=true准确扩展1–5；新增实例不会沿用旧output.nc同prefix的已删字段。
- [ ] 给输出目录增加origin：`registered`（与当前solver/config匹配的native probe）、`expected`（catalog约束）、`observed`（带run fingerprint的结果文件）；预览可以显示expected，实际保存explicit field必须是该条件合法并在native候选中注册，或保留`*`。不可从历史输出“有这个名字”就认定当前注册。
- [ ] 订阅保持conceptual selector与exact native names关系：rename将自身selectors和exact prefixes重写；delete移除自身订阅并在preview列出；新增四实例默认最小states都选中，过程诊断由本次验证或用户选择打开。现有用户“minimal hydro”保持其语义，但新增操作明确subscribe才更新，不静默把所有诊断打开。
- [ ] 复用原生自动aggregation，native probe记录真实贡献者列表；不新增重复wet_chla求和实例。验收按native定义重算wet_chla＝所有启用藻oChla、wet_fish_totD＝所有启用鱼sD、wet_totN/P/C/悬浮颗粒＝manifest明确的贡献者及scale。显式用户汇总仅识别其真实模型和输入schema；未知公式不猜，不强改。
- [ ] `variable_reference._instance`现有最长prefix复用；label取display name，native单位优先registry。dynamic diagnostics的local wildcard覆盖underscore数字形式，例如tDConsFiPlan_1；catalog标明g/m3/s与日率转换来源，拒绝同单位假设。鱼sC本地gC/m3修复不可由上游gN/m3错误回退。
- [ ] 运行 `python -m pytest tests/test_output_subscriptions.py tests/test_output_selection.py tests/test_case_output_flags.py tests/test_wet_instance_catalog.py -q`，然后原生候选probe输出四个新实例state name/units与输出NetCDF逐一一致。

## Task 6：检查点身份、阶段碳与日期记忆

**Files:** Create wet_restart_identity.py/test_wet_restart_identity.py；Modify hotstart.py、run metadata/archive；隔离候选修改fish.F90、native probe。

- [ ] 先写同维错配反例：两实例调换顺序或rename后array shape完全相同仍拒绝restart；config不变、display name只改不影响结构时允许；binary变化拒绝。

```python
def test_reordered_same_size_states_are_incompatible():
    from wet_restart_identity import state_signature
    a = [{'name':'fish_a_sD','units':'gDW/m3','domain':'interior'},
         {'name':'fish_b_sD','units':'gDW/m3','domain':'interior'}]
    assert state_signature(a) != state_signature(a[::-1])
```

- [ ] 签名至少含有序active instances/model、qStage/动态counts/所有影响注册或memory的参数、有序native state names/units/domain、temporal expressions与诊断memory names、couplings、solver/library hash。不用排序states掩盖native索引顺序。默认保守冻结全参数科学配置；仅display name与输出选择可独立更改。初值改变在hotstart下不应用，UI明确当前从checkpoint恢复。

```python
import hashlib, json
def state_signature(states):
    payload = json.dumps(states, ensure_ascii=False, separators=(',',':'), allow_nan=False)
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()
```

- [ ] 启动时把signature与完整configuration hash写run manifest，模型成功关闭checkpoint后保存相邻`restart.out.studio.json`（version1、checkpoint sha256、run id、solver hash、signature、时间/grid）。归档/复制恢复连同旁车。`prepare_restart`验证file hash、signature、ordered dimensions及既有temporal校验后才stage restart.in。无签名旧ecology checkpoint只能在可信原run manifest与配置/Binary hash能重建一致来源时迁移登记，否则要求新冷启，不能拿当前配置给旧文件补一张“匹配”签名。
- [ ] stage真实科学probe先在本地原代码失败定位：juvenile qStage2成年目标qStage1，隔离关闭不相关通量/设置正生物量和个体size，检查juvenile成熟C损失=adult成熟C增加。当前fish.F90计算tCAgeFish并从source扣除，却未写adult_C；候选最小修复是与N/P邻近增加同一C ODE转移，不改公式。

```fortran
! Within qStage == 2 or 3 mature transfer block, after P transfer:
_SET_ODE_(self%id_FiAd_C, tCAgeFish)
```

- [ ] stage日期记忆probe跨繁殖日前/后的checkpoint比较：原Day_last隐藏diagnostic无column_memory，不能假设当前restart保存了它。将其纳入已有column_memory机制，使用与macrophytes同样的properties/API且native probe检查save_index有效；若开启仅qStage>0，则qStage0完全保持既有行为。

```fortran
! Match the established property API used by macrophytes.F90.
if (self%qStage > 0) then
   call self%set_variable_property(self%id_Day_last_save, 'column_memory', .true.)
   call self%set_variable_property(self%id_Day_last_save, 'column_memory_initial', 0.0_rk)
endif
```

若output_none让save_index无效，使用既有column_memory存储要求的原生输出标志，不改公开默认订阅，也不能凭示例直接假定有效；先以失败探针确定要求再实现。验证第一步初始化当天日期的繁殖含义与连续运行一致，不能通过改繁殖日掩盖重复/遗漏事件。
- [ ] 保留本地fish timestep移除、qStage0 reserve guard、diagnostics guard、sC单位、植物/OM/Benthic镜像与temporal修复。此task只构建隔离candidate binary，与冻结生产solver跑原案例基线比对；不替换生产文件。上述科学补丁与上游差异写manifest，候选不通过就不能宣称阶段功能完成。
- [ ] 运行 `python -m pytest tests/test_wet_restart_identity.py tests/test_hotstart.py tests/test_native_fish_state.py tests/test_native_temporal_memory.py -q`；实际native通过后跑连续/分段探针。数组与temporal/diagnostic memory逐项 `rtol=1e-9, atol=1e-10`，仅时间边界记录去重，不任意放宽容差。

## Task 7：水质/生态独立页面与真实实例组装

**Files:** Create wet_instances.js；Modify index.html/现有导航注册与ecology_network.js；以主导航计划提供的模型配置父节点集成。

- [ ] 先写UI数据层测试：目录request明确domain；添加流程使用GET提供的template/port choices；四实例保存一次事务；case switch丢弃旧请求；错误后表单保留草稿。
- [ ] 水质页独立列出营养盐/氧、有机物、沉积物、碳与气体，生态页列出藻/浮游动物/底栖/植物/鱼/关系网。两个入口各有family选择、真实enabled/parameter/initial编辑，跨域连接显示目标和units，可跳转对方实例；不要另复制一份水质model造成重复反应。
- [ ] 生态新增选择functional type/已有实例template→唯一name/display→traits/parameters/initial→typed ports→preview→apply。表单用schema生成有限数值/enum/单位，引用名与显示名独立；多实例无硬编码数量上限，超过视图可搜索/折叠，后端容量只按native注册/资源证据决定。
- [ ] foodweb编辑使用group rows，增减猎物时编译端口族。预览展示 `fish_grazer/PLANprey2 → algae_b`、自动state `sDW/sNW/sPW/sCW` 与m3/gDW/d clearance；stage展示6个真实状态目标。关系箭头明确“猎物→消费者”，states/pools与model links使用不同说明。删除列出依赖并允许同事务替换；恢复显示冲突，不偷偷改引用名。
- [ ] 保存成功后刷新统一catalog、initial、output、parameters、network及cached metadata；错误定位具体instance/port；运行中禁用结构操作。保留现有网络pan/zoom/selected node；reload恢复同case目录与display，不假造已执行状态。
- [ ] 浏览器验证在实施阶段进行：真实新案例新增两藻两鱼，至少一次clone/rename/delete/restore；reload/service restart与rebuild再次确认；中英文与键盘焦点验证。截图/网络请求仅是UI证据，不能替代Task8原生输出。

## Task 8：可复现真实模型证据与回归门槛

**Files:** Create scripts/verify_wet_instances.py；Extend native probe与专用tests；所有运行写独立build目录。

- [ ] 脚本参数定义：`--work`必须新目录、`--model-source`默认3DWET、`--case`默认NativeTest、`--solver`默认冻结bin/getm_cartesian.exe、`--duration-seconds 172800`、`--checkpoint-seconds 86400`、`--timeout 300`、`--scenario multiple|foodweb|stage|all`。复用verify_restart_acceptance.py的prepare_model/APIProbe/run_case与无浏览器launcher。复制时不带旧output/restart/log；记录source/solver/input/output SHA256。不得替换正式案例、占用正在运行的app或自动安装。
- [ ] 验证脚本按API添加本文4实例，并在实际zoo中追加两藻prey_modelN，保留原prey rows；输出订阅新D/N/P/C、藻oChla、鱼consumption诊断、原生aggregates及temp/z/hn。用现有solver环境真实运行，不stub netCDF、不mock求解器。若normal case既有鱼已在，则新增两鱼后按model数应增加2，而不是总数强制等于3。
- [ ] 冷启动前运行catalog+native registration probe；save_initial确保首帧或以restart/短probe取得真实initial值，按真实输出时刻解释首帧，不能把已经积分后的值当精确初值。确认4个实例各自初值不同、四element states独立，湿网格全时段有限、非空、无未掩码NaN、log无fatal。
- [ ] foodweb A/B成对运行：完全相同forcing/initial/solver，A使用positive clearance，B将对应clearance设0（保留nPrey与相同维数）。A明确tD/N/P/C consumption>0，B对应flux为0（数值容差1e-14）；比较target与consumer最终states差值>输出有效精度。再交换fish_grazer的algae_a/algae_b prey绑定，检验响应随真实target改变而变化；不能仅检查YAML多一行或结果曲线不同。
- [ ] native aggregations逐timestamp/湿cell对照：CHLA所有藻oChla之和；fish_totD所有鱼sD之和；N/P/C按native贡献清单重算。误差阈值由输出dtype：float64 `rtol=1e-9, atol=1e-10`；float32 `rtol=2e-6, atol=1e-7`，JSON记录dtype与阈值，不因失败任意放宽。计算真D/N/P/C inventory用cell体积+底栖面积并标清边界/外部通量；不要把缺鱼的wet_totN当完整系统元素守恒。
- [ ] 同配置运行continuous 48h和24h checkpoint/resume至48h，比所有新增四实例状态、hydro、benthic mirrors、temporal/diagnostic memory及相同timestamp outputs；reload和服务重启后resume也通过。新增实例/rename/顺序变化后旧checkpoint必须在写restart.in前拒绝，保存当前文件hash未变证据。
- [ ] stage独立case将两新鱼作为成熟/繁殖链，按source正parameter/size设置、模拟窗覆盖cDayReprFish边界；分别在日界/繁殖事件前后1步设checkpoint，检查事件恰好一次、C成熟转移守恒、continuous/resume一致。qStage0不能代替这一项，官方development status写报告。
- [ ] bench regression：冻结既有NativeTest、Lake Luoma、Theoretical lake、Lake Dianchi的现有配置与solver，应用层改动在未改配置下结果应一致；阶段候选solver对qStage0/OM/macrophytes/碳甲烷基线无新增差异，阶段更改只出现预期修复。完整时间窗科学验证及正式五轮由主工作流安排，这里不冒用短探针计轮次。
- [ ] 执行命令（实施时运行，当前调查不运行）：

```powershell
python -m pytest tests/test_wet_instance_catalog.py tests/test_wet_foodweb.py tests/test_wet_instance_transactions.py tests/test_wet_instance_rebuild.py tests/test_wet_restart_identity.py -q
python -m pytest tests/test_ecology_network.py tests/test_initial_conditions_rebuild.py tests/test_output_subscriptions.py tests/test_hotstart.py -q
python scripts/verify_wet_instances.py --work build/wet-instances-20261016-multiple --scenario multiple --duration-seconds 172800 --checkpoint-seconds 86400 --timeout 300
python scripts/verify_wet_instances.py --work build/wet-instances-20261016-foodweb --scenario foodweb --duration-seconds 172800 --checkpoint-seconds 86400 --timeout 300
python scripts/verify_wet_instances.py --work build/wet-instances-20261016-stage --scenario stage --solver build/wet-instances-candidate/bin/getm_cartesian.exe --duration-seconds 172800 --checkpoint-seconds 86400 --timeout 300
```

预期前两条全PASS（native tests不能skip算PASS）；三次脚本exit0且`verification.json.passed=true`、`scope='dedicated-instance-regression-not-five-workflow-round'`。每次保留candidate YAML与diff、API请求响应、native日志、状态目录/顺序/units/aggregates、完整output.nc、restart与identity旁车、敏感性/阶段/重启比较JSON、模型来源指纹与UI截图引用。另保存旧案例不变性报告，任何必需结果缺失均FAIL。

## 实施依赖与完成汇报

依赖顺序：1 → 2 → 3 → 4/5 → 6 → 7 → 8；任务4/5可以独立排查但共享修改文件必须顺序整合。当前只交付本计划，不执行提交；实施阶段完成一个可测试边界后才按上级工作流要求保存检查点，不创建无授权PR、安装或发布。

最小可交付是所有任务通过；可以先完成qStage0任意多实例，但不能把阶段耦合标为完成，必须继续到必要native修复和stage真实验证。对官方最新的采用以manifest逐文件记录；对本地版本混合不能只显示“WET最新”。最终向用户汇报实际新增实例、真couplings与模型证据路径、测试结果、采用版本、剩余科学限制和正式轮次状态。

## 本计划自审

- [x] 设计要求映射：独立入口Task7，任意实例Task1–4，真实端口Task2，事务/恢复Task3，重建/初值Task4，汇总/输出Task5，重启/阶段科学Task6，真实模型证明Task8。
- [x] 唯一名/显示名明确区分，任意5猎物回归排除固定三槽位；不存在以固定三鱼代替新增两鱼的方案。
- [x] 已说明native parser标量限制、旧模板覆盖、spatial初值覆盖、conditional diagnostics和同维restart错配。
- [x] 已核对官方最新master源码与v2.3来源；保留本地修复、独立气体及现有solver；阶段必要修复采用隔离候选。
- [x] 操作/字段名称前后一致，动态suffix BEN使用源码`BENprey_suffixN`，port使用`BENTpreyN`，stage为state ports而非不存在的*_target。
- [x] 本文未把研究、单元测试、UI截图或短原生probe记为正式五轮，当前没有执行产品更改或模型验证。
