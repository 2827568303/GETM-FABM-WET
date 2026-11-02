const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const catalog=JSON.parse(fs.readFileSync('3DWET/app/static/i18n/en.json','utf8')).messages;
const context=vm.createContext({window:{},console,fetch:async()=>({ok:true,json:async()=>({locale:'en-US',name:'English',messages:catalog})})});
vm.runInContext(fs.readFileSync('3DWET/app/static/js/i18n.js','utf8'),context);
const strings=[
  ['网络来源','Network source'],
  ['当前活动案例','Current active case'],
  ['Erken 配置接线示例（只读）','Erken configuration wiring example (read-only)'],
  ['配置分类','Configuration category'],
  ['全部模块','All modules'],
  ['生态网络','Ecological network'],
  ['水质模块','Water-quality modules'],
  ['网络视图','Network view'],
  ['全部耦合','All couplings'],
  ['食性配置分层图','Configured food-web layers'],
  ['编辑食性关系 ↓','Edit configured food-web links ↓'],
  ['添加或管理实例','Add or manage instances'],
  ['预览并创建实例','Preview and create instance'],
  ['软删除当前选择','Soft-delete selected instance'],
  ['已删除实例','Deleted instances'],
  ['恢复所选实例','Restore selected instance'],
  ['消费者','Consumer'],
  ['食性消费者实例','Food-web consumer instance'],
  ['食性分组','Diet group'],
  ['增加 prey','Add prey'],
  ['还原此组未保存编辑',"Restore this group's unsaved edits"],
  ['保存食性关系','Save food-web links'],
  ['猎物目标','Prey target'],
  ['猎物后缀','Prey suffix'],
  ['后缀','Suffix'],
  ['肠道占据率','Gut occupancy'],
  ['操作','Action'],
  ['查看已配置食性端口关系','View configured food-web port links'],
  ['已配置食性端口关系','Configured food-web port links'],
  ['猎物实例','Prey instance'],
  ['消费者实例','Consumer instance'],
  ['FABM 端口','FABM port'],
  ['解析证据','Resolution evidence'],
  ['已闭环三节点关系','Closed three-node relation'],
  ['未解析食性引用','Unresolved food-web references'],
  ['原始引用','Original reference']
  ,['为所选鱼类或浮游动物配置 prey。候选先按模型族筛选；真实注册状态和单位由模型端事务预览最终核验。','Configure prey for the selected fish or zooplankton instance. Candidates are filtered by model family; registered state and units are checked by the model transaction preview.']
  ,['选择一个已启用的鱼类或浮游动物实例以编辑实际食性关系。','Select an enabled fish or zooplankton instance to edit configured food-web links.']
  ,['增加 prey','Add prey']
  ,['选择 prey','Select prey']
  ,['还原此组未保存编辑',"Restore this group's unsaved edits"]
  ,['移除','Remove']
  ,['摄食清除率','Prey clearance rate']
  ,['肠道占据率','Gut occupancy']
  ,['操作','Action']
  ,['当前配置没有可解析的食性引用。','No resolvable food-web references in the current configuration.']
  ,['当前配置没有未解析食性引用。','No unresolved food-web references in the current configuration.']
  ,['注册状态/单位在预览阶段由模型校验。','Registration status and units are checked by the model during preview.']
  ,['核对已解析的 4 条食性端口关系 · 闭合三节点有向环 1 个','Review 4 resolved food-web port links · 1 closed three-node directed cycles']
  ,['当前案例 C:\\data\\cases\\Dianchi\\fabm.yaml：图中边是该 fabm.yaml 的启用且可解析食性配置引用；分层图只表示布局，不代表闭环或营养级。此视图核实实例引用与端口名，不验证模型运行时目标 state 注册、单位或求解时兼容性。配置支持的角色实例：生产者/碎屑 2，有食性边的消费者 3，有食性边的鱼类/顶级捕食者 1。 缺失/未配置：鱼类/顶级捕食者层未配置食性边。 已解析到实例的猎物→消费者引用 7 条；配置但未解析 2 条；声明食性槽未配置端口 1 个；消费者之间的配置食性边 4 条；真实已解析边构成的闭合三节点有向环 1 个。闭环数为 0 时代表当前配置没有闭环；图不推断未配置关系。','Current case C:\\data\\cases\\Dianchi\\fabm.yaml: Edges show enabled, resolvable food-web references from this fabm.yaml. Layering is for layout only; it does not indicate a closed cycle or trophic level. This view checks instance references and port names. It does not verify runtime target-state registration, units, or solver compatibility. Configured role instances: producers/detritus 2, consumers with food-web links 3, fish/top predators with food-web links 1. Missing or unconfigured: no configured food-web links for fish/top predators. Resolved prey-to-consumer references 7; configured but unresolved 2; declared diet slots without configured ports 1; configured links between consumers 4; closed three-node cycles among resolved edges 1. A cycle count of 0 means there is no closed cycle in the current configuration; the graph does not infer unconfigured links.']
  ,['已解析的三节点食性路径 3 条（3个不同实例、2条有向饮食边；不等同于三角闭环、营养级或已验证摄食）。下方逐条列出真实实例与端口。','Resolved three-node food-web paths 3 (3 distinct instances, 2 directed prey-to-consumer links; this is not a triangle cycle, trophic-level assignment, or validated feeding behavior). The actual instances and ports are listed below.']
  ,['藻类 2 个物种实例 · 鱼类 3 个物种实例；视图过滤只影响显示，修改保存到当前活动案例。','Algae 2 species instances · Fish 3 species instances; view filters affect display only, and edits are saved to the current active case.']
  ,['4 个 FABM 实例 · 9 个显式耦合端口 · 6 个已解析食性引用','4 FABM instances · 9 explicit coupling ports · 6 resolved food-web references']
  ,['未解析食性引用 0 条','0 unresolved food-web references']
  ,['phyto_A → zoo_B → fish_C；三实例配置链，2 条已解析有向饮食边','phyto_A → zoo_B → fish_C; configured three-instance path, 2 resolved directed prey-to-consumer links']
  ,['新增、软删除和恢复均通过预览校验后再应用；有其他实例引用的节点不能删除。源码基线：WET v2.3 与本地 GETM 兼容改动；双壳类来自 master 开发能力，不属于 v2.3 正式版。实例/端口按本地 Fortran 注册表读取；原生注册探针尚未执行，不能据此断言所有能力已在当前可执行文件中验证。','Additions, soft deletion, and restoration are applied only after preview checks; a node referenced by another instance cannot be deleted. Source baseline: WET v2.3 with local GETM compatibility changes; bivalves come from master development and are not part of the v2.3 release. Instances and ports are read from the local Fortran registry; the native registration probe has not run, so this does not establish that every capability is verified in the current executable.']
  ,['只显示由真实饮食边连接的配置层 1–3','Show only configured layers 1–3 connected by actual food-web links']
  ,['FABM实例耦合网络','FABM instance coupling network']
];
(async()=>{
  await context.window.StudioI18n.setLocale('en-US');
  for(const [source,expected] of strings){
    assert.equal(context.window.StudioI18n.t(source),expected,`English dynamic label: ${source}`);
  }
  const rendered= new Map(strings.slice(-9));
  const nodes=[...rendered].map(([text])=>({nodeType:3,nodeValue:text,parentElement:null}));
  const elements=nodes.map(node=>({nodeType:1,children:[node],closest:()=>null,getAttribute:()=>null,setAttribute(){}}));
  nodes.forEach((node,index)=>{node.parentElement=elements[index];});
  const ariaElement=(value)=>{const attributes={'aria-label':value};return {nodeType:1,children:[],attributes,closest:()=>null,getAttribute:name=>attributes[name]??null,setAttribute:(name,text)=>{attributes[name]=String(text);}};};
  const pathAria=ariaElement([...rendered.keys()][5]);
  const networkAria=ariaElement('FABM实例耦合网络');
  const root={nodeType:1,children:[...elements,pathAria,networkAria],closest:()=>null,getAttribute:()=>null,setAttribute(){}};
  const document={readyState:'complete',documentElement:root,dispatchEvent(){},createTreeWalker(target){
    const descendants=[];const visit=node=>{for(const child of node.children||[]){descendants.push(child);visit(child);}};visit(target);
    let index=0;return {nextNode:()=>descendants[index++]||null};
  }};
  class MutationObserver{observe(){}}
  class CustomEvent{constructor(type,options){this.type=type;this.detail=options?.detail;}}
  const renderedContext=vm.createContext({window:{},document,console,MutationObserver,CustomEvent,
    localStorage:{getItem:key=>key==='3dwet.locale'?'en-US':null,setItem(){}},
    fetch:async url=>({ok:true,json:async()=>url==='/api/system/language'?{locale:'en-US'}:{locale:'en-US',name:'English',messages:catalog}})});
  vm.runInContext(fs.readFileSync('3DWET/app/static/js/i18n.js','utf8'),renderedContext);
  await renderedContext.window.StudioI18n.ready;
  await renderedContext.window.StudioI18n.setLocale('en-US');
  for(const [index,[source,expected]] of [...rendered.entries()].entries()){
    assert.equal(nodes[index].nodeValue,expected,`rendered English food-web summary: ${source}`);
  }
  assert.equal(pathAria.getAttribute('aria-label'),rendered.get([...rendered.keys()][5]),'rendered path-card description stays English and preserves instance IDs');
  assert.equal(networkAria.getAttribute('aria-label'),'FABM instance coupling network','rendered network SVG accessibility label is English');
  console.log('ecology network editor English labels PASS');
})().catch(error=>{console.error(error);process.exitCode=1;});
