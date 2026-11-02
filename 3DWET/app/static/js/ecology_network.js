/* Real instance couplings from FABM; no inferred food-web connections. */
function directedFoodwebCycleSummary(edges){
  const outgoing=new Map(),names=new Set();
  for(const edge of edges){
    names.add(edge.source);names.add(edge.target);
    if(!outgoing.has(edge.source))outgoing.set(edge.source,new Set());
    outgoing.get(edge.source).add(edge.target);
  }
  const orderedNames=[...names].sort(),edgeKeys=new Set();let count=0;
  // Start each cycle at its lexically smallest instance. Walking two sparse
  // adjacency lists finds each orientation once without scanning all triples.
  for(const a of orderedNames)for(const b of outgoing.get(a)||[]){
    if(b<=a)continue;
    for(const c of outgoing.get(b)||[]){
      if(c<=a||c===b||!outgoing.get(c)?.has(a))continue;
      count++;
      edgeKeys.add(`${a}\0${b}`);edgeKeys.add(`${b}\0${c}`);edgeKeys.add(`${c}\0${a}`);
    }
  }
  return {count,edgeKeys};
}
function directedFoodwebPaths(edges){
  const outgoing=new Map();
  for(const edge of edges){if(!outgoing.has(edge.source))outgoing.set(edge.source,[]);outgoing.get(edge.source).push(edge);}
  const paths=[];
  for(const first of edges)for(const second of outgoing.get(first.target)||[]){
    if(first.source===first.target||first.source===second.target||first.target===second.target)continue;
    paths.push({nodes:[first.source,first.target,second.target],edges:[first,second]});
  }
  return paths;
}
(() => {
  const page=document.getElementById('page-gridstudio');if(!page)return;
  const box=document.createElement('section');box.id='ecology-network-editor';box.className='card';box.setAttribute('aria-labelledby','ecology-network-heading');box.style.cssText='margin-top:20px;overflow:hidden;scroll-margin-top:16px';
  box.innerHTML=`<h3 id="ecology-network-heading" tabindex="-1">生态模块网络与快捷编辑</h3><p>箭头从被引用模块指向使用该引用的模块。点击节点查看参数及耦合端口。滚轮缩放，拖动空白处平移；灰色节点为禁用模块。</p>
  <div class="editor-toolbar"><button class="btn" id="en-load">刷新网络</button><label for="en-network-source">网络来源</label><select id="en-network-source"><option value="active">当前活动案例</option><option value="erken_reference">Erken 配置接线示例（只读）</option></select><button class="btn" id="en-parameters">打开节点参数页</button><button class="btn" id="en-modules">打开模块配置</button></div>
  <div class="editor-toolbar" role="group" aria-label="配置分类"><button class="btn" data-network-filter="all">全部模块</button><button class="btn" data-network-filter="ecology">生态网络</button><button class="btn" data-network-filter="water_quality">水质模块</button></div>
  <div class="editor-toolbar" role="group" aria-label="网络视图"><button class="btn" id="en-view-couplings" type="button" aria-pressed="true">全部耦合</button><button class="btn" id="en-view-foodweb" type="button" aria-pressed="false">食性配置分层图</button><button class="btn" id="en-foodweb-three-layer" type="button" aria-pressed="false" title="只显示由真实饮食边连接的配置层 1–3">真实三层子网</button><button class="btn btn-primary" id="en-open-foodweb-editor" type="button" aria-controls="en-foodweb-editor">编辑食性关系 <svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-down"></use></svg></button><span class="editor-message">食性图仅按实际 YAML 引用分层：消费者在上、猎物在底；箭头表示猎物→消费者，悬停连线可见 FABM 端口。此布局不是营养级判定或三节点闭环；未配置的物种、关系不会补画。窄屏可横向滚动，完整关系表可逐项核查。</span></div>
  <p id="en-network-evidence" class="editor-message" role="status" aria-live="polite">加载案例后汇总实际食性引用、未解析项和闭环数量。</p><p id="en-foodweb-paths" class="editor-message" aria-live="polite">加载案例后枚举已解析的三节点食性路径。</p><div id="en-foodweb-path-list" class="foodweb-path-list" role="group" aria-label="已解析的三节点食性配置路径"></div>
  <div id="en-families" class="editor-message">节点按实际 FABM 模型族分类；每个名称代表 YAML 中的一个实例。</div><p class="editor-message">新增、软删除和恢复均通过预览校验后再应用；有其他实例引用的节点不能删除。源码基线：WET v2.3 与本地 GETM 兼容改动；双壳类来自 master 开发能力，不属于 v2.3 正式版。实例/端口按本地 Fortran 注册表读取；原生注册探针尚未执行，不能据此断言所有能力已在当前可执行文件中验证。</p>
  <details class="editor-info" id="en-instance-editor" style="margin:12px 0"><summary>添加或管理实例</summary><p>默认克隆完整复制参数、初值和耦合。等总量分摊是单独选择的模式：仅按比例分摊所有已显式声明、且注册单位可识别的初始状态；比例必须严格在 0 和 1 之间，确保两组都获得正份额。预览将列出比例和被改动状态。任何状态不明确时该模式拒绝执行。它只平分初始 biomass share，不会产生不同物种或性状差异；克隆出的同模型实例仍是两个 cohort，科学竞争比较需另行设置和验证参数、性状与显式耦合。食性耦合保持原样，由你显式编辑。</p><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px"><section class="editor-info" style="border:1px solid var(--border);border-radius:8px;padding:12px"><h4>第 1 步 · 选择模型族</h4><label for="en-add-model">模型族</label><select id="en-add-model"></select></section><section class="editor-info" style="border:1px solid var(--border);border-radius:8px;padding:12px"><h4>第 2 步 · 选择来源</h4><label for="en-add-source">同模型克隆来源</label><select id="en-add-source"></select></section><section class="editor-info" style="border:1px solid var(--border);border-radius:8px;padding:12px"><h4>第 3 步 · 设置初始状态</h4><label for="en-clone-mode">初始化方式</label><select id="en-clone-mode"><option value="copy">完整复制（默认）</option><option value="split">同功能群等总量分摊</option></select><label for="en-clone-fraction">分给新实例比例</label><input id="en-clone-fraction" type="number" min="0.000001" max="0.999999" step="0.01" value="0.5" disabled></section><section class="editor-info" style="border:1px solid var(--border);border-radius:8px;padding:12px"><h4>第 4 步 · 命名并预览</h4><label for="en-add-name">实例名</label><input id="en-add-name" maxlength="120" placeholder="如 algae_2"><label for="en-add-display-name">显示名</label><input id="en-add-display-name" maxlength="120" placeholder="可选"><button class="btn btn-primary" id="en-add">预览并创建实例</button></section></div><div id="en-add-template-hint" class="editor-message">从第 1 步选择模型族，再选择已配置的同族实例作为来源。</div><div class="editor-toolbar"><button class="btn" id="en-delete">软删除当前选择</button><label for="en-deleted">已删除实例</label><select id="en-deleted"></select><button class="btn" id="en-restore">恢复所选实例</button></div></details>
  <div id="en-message" class="editor-message">加载案例后显示真实配置。</div><div class="grid-workspace"><div style="min-width:0;position:relative"><svg id="en-svg" role="img" aria-label="FABM实例耦合网络" style="display:block;width:100%;height:470px;background:#fbfaf6;border-radius:10px;touch-action:none"></svg></div>
  <div class="editor-info" id="en-node-editor"><label for="en-node">模块实例</label><select id="en-node"></select><p id="en-model"></p><label for="en-name">显示名称（保留实例引用名）</label><input id="en-name" maxlength="120"><label for="en-param">现有参数</label><select id="en-param"></select><label for="en-value">参数值</label><input id="en-value"><label for="en-port">现有耦合端口</label><select id="en-port"></select><label for="en-target">已登记目标引用</label><select id="en-target"></select><button class="btn btn-primary" id="en-save" style="margin-top:12px">保存节点修改</button><p>只修改选择的字段并保留 YAML 其他内容。保存前生成备份，拒绝过期配置、无效引用或运行中的案例。</p></div></div>`;
  page.append(box);
  const foodwebPanel=document.createElement('section');foodwebPanel.id='en-foodweb-editor';foodwebPanel.className='editor-info';foodwebPanel.tabIndex=-1;foodwebPanel.style.cssText='margin-top:14px;scroll-margin-top:16px';
  foodwebPanel.innerHTML='<h4>食性关系</h4><p>为所选鱼类或浮游动物配置 prey。候选先按模型族筛选；真实注册状态和单位由模型端事务预览最终核验。</p>';
  const foodwebConsumer=document.createElement('select');foodwebConsumer.dataset.foodwebConsumerSelect='true';foodwebConsumer.setAttribute('aria-label','食性消费者实例');foodwebConsumer.id='en-foodweb-consumer';
  const foodwebConsumerLabel=document.createElement('label');foodwebConsumerLabel.textContent='消费者';foodwebConsumerLabel.setAttribute('for',foodwebConsumer.id);
  const foodwebConsumerField=document.createElement('div');foodwebConsumerField.className='foodweb-consumer-field';foodwebConsumerField.append(foodwebConsumerLabel,foodwebConsumer);
  const foodwebControls=document.createElement('div');foodwebControls.className='editor-toolbar';
  const foodwebGroup=document.createElement('select');foodwebGroup.dataset.foodwebGroupSelect='true';foodwebGroup.setAttribute('aria-label','食性分组');
  const foodwebAdd=document.createElement('button');foodwebAdd.className='btn';foodwebAdd.type='button';foodwebAdd.textContent='增加 prey';
  const foodwebReset=document.createElement('button');foodwebReset.className='btn';foodwebReset.type='button';foodwebReset.textContent='还原此组未保存编辑';foodwebReset.dataset.foodwebReset='true';
  const foodwebSave=document.createElement('button');foodwebSave.className='btn btn-primary';foodwebSave.type='button';foodwebSave.textContent='保存食性关系';foodwebSave.dataset.foodwebSave='true';
  foodwebControls.append(foodwebGroup,foodwebAdd,foodwebReset,foodwebSave);
  let foodwebControlIndex=0;
  const foodwebField=(title,control)=>{const field=document.createElement('div');field.className='foodweb-field';const label=document.createElement('label');control.id=`en-foodweb-field-${++foodwebControlIndex}`;label.setAttribute('for',control.id);label.textContent=title;field.append(label,control);return field;};
  const foodwebRows=document.createElement('div');foodwebRows.dataset.foodwebRowsRoot='true';
  const foodwebStatus=document.createElement('p');foodwebStatus.className='editor-message';foodwebStatus.dataset.foodwebStatus='true';
  foodwebPanel.append(foodwebConsumerField,foodwebControls,foodwebRows,foodwebStatus);box.append(foodwebPanel);
  const foodwebRelations=document.createElement('details');foodwebRelations.className='editor-info';foodwebRelations.style.cssText='margin-top:12px;overflow-x:auto';
  const foodwebRelationsSummary=document.createElement('summary');foodwebRelationsSummary.dataset.foodwebRelationsSummary='true';foodwebRelationsSummary.textContent='查看已配置食性端口关系';
  const foodwebRelationsTable=document.createElement('table');foodwebRelationsTable.setAttribute('aria-label','已配置食性端口关系');foodwebRelationsTable.style.cssText='width:100%;border-collapse:collapse;text-align:left';
  const foodwebRelationsCaption=document.createElement('caption');foodwebRelationsCaption.textContent='仅列出当前 FABM 配置中存在且可解析的实际引用；闭环标记仅表示这条真实边参与已闭合的三节点有向环。';
  const foodwebRelationsHead=document.createElement('thead'),foodwebRelationsHeadRow=document.createElement('tr');
  for(const label of ['猎物实例','方向','消费者实例','FABM 端口','解析证据','已闭环三节点关系']){const th=document.createElement('th');th.scope='col';th.textContent=label;th.style.cssText='padding:6px 8px;border-bottom:1px solid var(--border)';foodwebRelationsHeadRow.append(th);}
  foodwebRelationsHead.append(foodwebRelationsHeadRow);
  const foodwebRelationsBody=document.createElement('tbody');foodwebRelationsBody.dataset.foodwebRelationsRows='true';
  foodwebRelationsTable.append(foodwebRelationsCaption,foodwebRelationsHead,foodwebRelationsBody);foodwebRelations.append(foodwebRelationsSummary,foodwebRelationsTable);box.append(foodwebRelations);
  const foodwebUnresolved=document.createElement('details');foodwebUnresolved.className='editor-info';foodwebUnresolved.style.cssText='margin-top:8px;overflow-x:auto';foodwebUnresolved.dataset.foodwebUnresolvedPanel='true';
  const foodwebUnresolvedSummary=document.createElement('summary');
  const foodwebUnresolvedNote=document.createElement('p');foodwebUnresolvedNote.className='editor-message';
  const foodwebUnresolvedTable=document.createElement('table');foodwebUnresolvedTable.setAttribute('aria-label','未解析食性引用');foodwebUnresolvedTable.style.cssText='width:100%;border-collapse:collapse;text-align:left';
  const foodwebUnresolvedCaption=document.createElement('caption');
  const foodwebUnresolvedHead=document.createElement('thead'),foodwebUnresolvedHeadRow=document.createElement('tr');
  for(const label of ['消费者实例','FABM 端口','原始引用','解析证据']){const th=document.createElement('th');th.scope='col';th.textContent=label;th.style.cssText='padding:6px 8px;border-bottom:1px solid var(--border)';foodwebUnresolvedHeadRow.append(th);}
  foodwebUnresolvedHead.append(foodwebUnresolvedHeadRow);
  const foodwebUnresolvedBody=document.createElement('tbody');foodwebUnresolvedBody.dataset.foodwebUnresolvedRows='true';
  foodwebUnresolvedTable.append(foodwebUnresolvedCaption,foodwebUnresolvedHead,foodwebUnresolvedBody);
  foodwebUnresolved.append(foodwebUnresolvedSummary,foodwebUnresolvedNote,foodwebUnresolvedTable);box.append(foodwebUnresolved);
  const el=id=>document.getElementById('en-'+id),svg=el('svg'),NS='http://www.w3.org/2000/svg';svg.dataset.nativeViewport='true';
  let network=null,instanceCatalog=null,busy=false,networkReadOnly=false,view={scale:1,x:0,y:0},pan=null,filter='ecology',viewMode='couplings',foodwebLayerView='full',focusedFoodwebPath=null,foodwebCycleSummary={count:0,edgeKeys:new Set()},resolvedFoodwebPaths=[],visibleFoodwebPathCount=24;
  const norm=p=>String(p||'').replace(/\\/g,'/').toLowerCase();
  const MODEL_GROUPS={phytoplankton:['ecology','藻类'],zooplankton:['ecology','浮游动物'],zoobenthos:['ecology','底栖动物'],bivalves:['ecology','贝类（master 开发）'],macrophytes:['ecology','水生植物'],fish:['ecology','鱼类'],fish_pclake:['ecology','鱼类（PCLake）'],abiotic_water:['water_quality','水质·水体'],abiotic_sediment:['water_quality','水质·底泥'],om_pool:['water_quality','水质·有机质'],sediment_exchange:['water_quality','水质·沉积物交换'],burial:['water_quality','水质·埋藏'],bot_pel_interface:['water_quality','水质·底水界面'],inorganic_carbon:['water_quality','水质·无机碳'],methane:['water_quality','水质·甲烷']};
  const FOODWEB_GROUPS={PLAN:{families:['phytoplankton','zooplankton'],suffixes:['','W'],units:'m3/gDW/d'},BEN:{families:['zoobenthos','bivalves','macrophytes','fish_pclake'],suffixes:['','S'],units:'m2/gDW/d'},PISC:{families:['fish'],suffixes:[''],units:'m3/gDW/d'},prey:{families:['phytoplankton','zooplankton'],suffixes:['','W'],units:'m3/gDW/d'}};
  let foodwebRowsByGroup={},foodwebDirtyGroups=new Set();
  function modelGroup(n){const family=String(n.model||'').replace(/^wet\//,'');return MODEL_GROUPS[family]||['other','其他模块'];}
  const isDietaryPort=port=>/^(?:prey_model|PLANprey|BENTprey|PISCprey)\d+$/.test(String(port||''));
  const foodwebEdgeKey=edge=>[edge.source,edge.target,edge.port,edge.reference].join('\0');
  const foodwebPathKey=path=>path.edges.map(foodwebEdgeKey).join('\u0001');
  function focusFoodwebPath(path){
    const key=foodwebPathKey(path);
    focusedFoodwebPath=focusedFoodwebPath?.key===key?null:{key,nodes:new Set(path.nodes),edges:new Set(path.edges.map(foodwebEdgeKey))};
    viewMode='foodweb';foodwebLayerView='full';
    el('view-couplings').setAttribute('aria-pressed','false');el('view-foodweb').setAttribute('aria-pressed','true');el('foodweb-three-layer').setAttribute('aria-pressed','false');
    for(const card of el('foodweb-path-list')?.children||[])card.setAttribute('aria-pressed',String(card.dataset.foodwebPathKey===focusedFoodwebPath?.key));
    draw();updateFoodwebRelations();
  }
  function clearFoodwebPathFocus(){if(!focusedFoodwebPath)return;focusedFoodwebPath=null;for(const card of el('foodweb-path-list')?.children||[])card.setAttribute('aria-pressed','false');draw();updateFoodwebRelations();}
  function foodwebEdges(){
    if(!network)return [];
    const nodes=new Map(network.nodes.map(n=>[n.name,n]));
    return network.edges.filter(e=>isDietaryPort(e.port)&&nodes.get(e.source)?.enabled!==false&&nodes.get(e.target)?.enabled!==false);
  }
  function foodwebEvidence(){
    const nodes=network?.nodes||[],edges=foodwebEdges(),nodeMap=new Map(nodes.map(n=>[n.name,n]));
    const consumers=nodes.filter(n=>n.enabled!==false&&['wet/zooplankton','wet/zoobenthos','wet/fish','wet/fish_pclake'].includes(n.model));
    const configured=consumers.flatMap(n=>Object.entries(n.coupling||{}).filter(([port])=>isDietaryPort(port)).map(([port,reference])=>({consumer:n.name,port,reference})));
    const valid=new Set(edges.map(e=>`${e.target}\0${e.port}\0${e.reference}`));
    const unresolved=configured.filter(e=>!valid.has(`${e.consumer}\0${e.port}\0${e.reference}`));
    const missingSlots=consumers.reduce((sum,n)=>{
      const p=n.parameters||{},declared=['wet/zooplankton','wet/zoobenthos'].includes(n.model)?Number(p.nPrey||0):
        Number(p.nPLAN||0)+Number(p.nBEN||0)+Number(p.nPISC||0);
      const count=Object.keys(n.coupling||{}).filter(isDietaryPort).length;
      return sum+Math.max(0,declared-count);
    },0);
    const consumerNames=new Set(consumers.map(n=>n.name));
    const consumerLinks=edges.filter(e=>consumerNames.has(e.source)&&consumerNames.has(e.target)).length;
    const sourceNodes=new Set(edges.map(edge=>edge.source)),consumerNodes=new Set(edges.map(edge=>edge.target));
    const producersAndDetritus=nodes.filter(n=>sourceNodes.has(n.name)&&['wet/phytoplankton','wet/om_pool','wet/macrophytes'].includes(n.model));
    const configuredConsumers=nodes.filter(n=>consumerNodes.has(n.name)&&['wet/zooplankton','wet/zoobenthos','wet/bivalves'].includes(n.model));
    const configuredFish=nodes.filter(n=>consumerNodes.has(n.name)&&['wet/fish','wet/fish_pclake'].includes(n.model));
    const unsupportedPrey=nodes.filter(n=>sourceNodes.has(n.name)&&!['wet/phytoplankton','wet/om_pool','wet/macrophytes','wet/zooplankton','wet/zoobenthos','wet/bivalves','wet/fish','wet/fish_pclake'].includes(n.model));
    return {edges,consumers,unresolved,missingSlots,cycles:foodwebCycleSummary.count,consumerLinks,nodeMap,producersAndDetritus,configuredConsumers,configuredFish,unsupportedPrey};
  }
  function updateFoodwebEvidence(preserveVisiblePathCount=false){
    const evidence=el('network-evidence');if(!evidence)return;
    if(!network){evidence.textContent='加载案例后汇总实际食性引用。';return;}
    foodwebCycleSummary=directedFoodwebCycleSummary(foodwebEdges());
    const s=foodwebEvidence();
    const roleStatus=`配置支持的角色实例：生产者/碎屑 ${s.producersAndDetritus.length}，有食性边的消费者 ${s.configuredConsumers.length}，有食性边的鱼类/顶级捕食者 ${s.configuredFish.length}。`;
    const gaps=[!s.producersAndDetritus.length?'生产者/碎屑层无可确认实例':null,!s.configuredConsumers.length?'无已配置消费者层':null,!s.configuredFish.length?'鱼类/顶级捕食者层未配置食性边':null].filter(Boolean).join('；');
    const exampleNote=networkReadOnly?'Erken 配置接线示例（只读），非活动案例；仅反映 YAML 引用，不代表运行时摄食、现场验证或科学验证。':'';
    evidence.textContent=`${exampleNote}${exampleNote?' ':''}当前${networkReadOnly?'示例':'案例'} ${network.case_path}：图中边是该 fabm.yaml 的启用且可解析食性配置引用；分层图只表示布局，不代表闭环或营养级。此视图核实实例引用与端口名，不验证模型运行时目标 state 注册、单位或求解时兼容性。${roleStatus}${gaps?` 缺失/未配置：${gaps}。`:''} 已解析到实例的猎物→消费者引用 ${s.edges.length} 条；配置但未解析 ${s.unresolved.length} 条；声明食性槽未配置端口 ${s.missingSlots} 个；消费者之间的配置食性边 ${s.consumerLinks} 条；真实已解析边构成的闭合三节点有向环 ${s.cycles} 个。闭环数为 0 时代表当前配置没有闭环；图不推断未配置关系。`;
    const paths=resolvedFoodwebPaths=directedFoodwebPaths(s.edges),pathSummary=el('foodweb-paths');
    if(focusedFoodwebPath&&!paths.some(path=>foodwebPathKey(path)===focusedFoodwebPath.key))focusedFoodwebPath=null;
    visibleFoodwebPathCount=preserveVisiblePathCount?Math.min(paths.length,Math.max(visibleFoodwebPathCount,24)):Math.min(24,paths.length);
    if(pathSummary)pathSummary.textContent=paths.length?`已解析的三节点食性路径 ${paths.length} 条（3个不同实例、2条有向饮食边；不等同于三角闭环、营养级或已验证摄食）。${paths.length>visibleFoodwebPathCount?`当前显示 ${visibleFoodwebPathCount} 条，可逐批展开。`:'下方列出全部路径。'}`:`已解析的三节点/两边食性路径 0 条；${networkReadOnly?'该 Erken 示例':'当前真实配置'}没有连续的两条已解析饮食边，且当前没有可验证的三节点配置链${s.configuredFish.length?'':'，也没有鱼类食性边'}。闭合三节点有向环 ${s.cycles} 个。`;
    const pathList=el('foodweb-path-list');
    if(pathList){
      const cards=paths.slice(0,visibleFoodwebPathCount).map((path,index)=>{
        const card=document.createElement('div');card.className='foodweb-path-card';card.dataset.foodwebPathEdges=String(path.edges.length);card.dataset.foodwebPathIndex=String(index+1);card.dataset.foodwebPathKey=foodwebPathKey(path);card.setAttribute('role','button');card.setAttribute('tabindex','0');card.setAttribute('aria-pressed',String(card.dataset.foodwebPathKey===focusedFoodwebPath?.key));
        card.setAttribute('aria-label',`${path.nodes.join(' → ')}；三实例配置链，${path.edges.length} 条已解析有向饮食边`);
        const chain=document.createElement('div');chain.className='foodweb-path-nodes';chain.textContent=path.nodes.join(' → ');card.append(chain);
        path.edges.forEach((edge,edgeIndex)=>{const relation=document.createElement('div');relation.className='foodweb-path-edge';relation.dataset.foodwebPathEdge=String(edgeIndex+1);relation.textContent=`${edge.reference} · ${edge.port} → ${edge.target}`;card.append(relation);});
        card.addEventListener('click',()=>focusFoodwebPath(path));
        card.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();focusFoodwebPath(path);}else if(event.key==='Escape'){event.preventDefault();clearFoodwebPathFocus();}});
        return card;
      });
      if(!cards.length){const empty=document.createElement('div');empty.className='foodweb-path-empty';empty.dataset.foodwebPathEmpty='true';empty.textContent=`0 条三节点/两边路径 · ${networkReadOnly?'示例配置':'当前真实配置'}没有连续的两条已解析饮食边${s.configuredFish.length?'':'，没有鱼类食性边'} · 闭环 ${s.cycles} 个。`;cards.push(empty);}
      if(visibleFoodwebPathCount<paths.length){const more=document.createElement('button');more.type='button';more.className='btn foodweb-path-more';more.dataset.foodwebPathMore='true';more.textContent=`显示接下来的 ${Math.min(24,paths.length-visibleFoodwebPathCount)} 条路径（剩余 ${paths.length-visibleFoodwebPathCount} 条）`;more.setAttribute('aria-label',`显示更多三节点食性路径；已显示 ${visibleFoodwebPathCount} 条，共 ${paths.length} 条`);more.addEventListener('click',()=>{visibleFoodwebPathCount=Math.min(paths.length,visibleFoodwebPathCount+24);updateFoodwebEvidence(true);});cards.push(more);}
      pathList.replaceChildren(...cards);
    }
  }
  function updateFoodwebRelations(){
    const summary=foodwebRelationsSummary,body=foodwebRelationsBody;
    const edges=foodwebEdges().slice().sort((a,b)=>a.target.localeCompare(b.target)||a.port.localeCompare(b.port)||a.source.localeCompare(b.source));
    const cycleEdges=foodwebCycleSummary.edgeKeys;
    if(summary)summary.textContent=`核对已解析的 ${edges.length} 条食性端口关系 · 闭合三节点有向环 ${foodwebCycleSummary.count} 个`;
    body.replaceChildren(...(edges.length?edges.map((edge,index)=>{
      const row=document.createElement('tr');row.dataset.foodwebRelationRow=String(index);row.dataset.foodwebRelationSource=edge.source;row.dataset.foodwebRelationTarget=edge.target;row.dataset.foodwebRelationPort=edge.port;row.dataset.foodwebRelationReference=edge.reference;
      const focused=focusedFoodwebPath?.edges.has(foodwebEdgeKey(edge))===true;row.setAttribute('data-foodweb-path-focused',String(focused));if(focused){row.style.background='var(--wb-sage-soft, #e8eee7)';row.style.boxShadow='inset 3px 0 0 var(--wb-sage, #71856f)';row.setAttribute('aria-current','true');}
      for(const value of [edge.source,'→',edge.target,edge.port,'YAML 实例引用已解析；目标状态/单位未在此视图核验',cycleEdges.has(`${edge.source}\0${edge.target}`)?'是（配置闭环边）':'否']){const cell=document.createElement('td');cell.textContent=value;cell.style.cssText='padding:5px 8px;border-bottom:1px solid var(--border);white-space:nowrap';row.append(cell);}
      return row;
    }):[(()=>{const row=document.createElement('tr');row.dataset.foodwebRelationRow='empty';const cell=document.createElement('td');cell.colSpan=6;cell.textContent='当前配置没有可解析的食性引用。';row.append(cell);return row;})()]));
    const unresolved=foodwebEvidence().unresolved.slice().sort((a,b)=>a.consumer.localeCompare(b.consumer)||a.port.localeCompare(b.port)||a.reference.localeCompare(b.reference));
    foodwebUnresolved.open=unresolved.length>0;
    foodwebUnresolvedSummary.textContent=`未解析食性引用 ${unresolved.length} 条`;
    foodwebUnresolvedNote.textContent='以下内容来自当前案例的配置引用；此处仅表示网络未返回对应的已解析实例边，不判定原因，也不核验模型运行时目标状态或单位。';
    foodwebUnresolvedCaption.textContent=`来源：${network?.case_path||'未加载案例'} 的 fabm.yaml 中配置的消费者端口引用。`;
    foodwebUnresolvedBody.replaceChildren(...(unresolved.length?unresolved.map(item=>{
      const row=document.createElement('tr');row.dataset.foodwebUnresolvedRow='true';row.dataset.consumer=item.consumer;row.dataset.port=item.port;row.dataset.reference=item.reference;
      for(const value of [item.consumer,item.port,item.reference,'当前活动案例 YAML 中有此引用，但网络未返回对应的已解析实例边；目标状态/单位未在此视图核验。']){const cell=document.createElement('td');cell.textContent=value;cell.style.cssText='padding:5px 8px;border-bottom:1px solid var(--border);white-space:nowrap';row.append(cell);}
      return row;
    }):[(()=>{const row=document.createElement('tr');row.dataset.foodwebUnresolvedRow='empty';const cell=document.createElement('td');cell.colSpan=4;cell.textContent='当前配置没有未解析食性引用。';row.append(cell);return row;})()]));
  }
  function visibleNodes(){
    if(viewMode==='foodweb'){
      const endpointNames=new Set(foodwebEdges().flatMap(e=>[e.source,e.target]));
      return network.nodes.filter(n=>endpointNames.has(n.name));
    }
    return network.nodes.filter(n=>filter==='all'||modelGroup(n)[0]===filter);
  }
  function foodwebLayering(nodes,edges){
    const names=nodes.map(n=>n.name),adj=new Map(names.map(name=>[name,new Set()]));
    for(const edge of edges)if(adj.has(edge.source)&&adj.has(edge.target))adj.get(edge.source).add(edge.target);
    let nextIndex=0;const index=new Map(),low=new Map(),stack=[],onStack=new Set(),components=[];
    const visit=name=>{index.set(name,nextIndex);low.set(name,nextIndex++);stack.push(name);onStack.add(name);
      for(const target of adj.get(name)){if(!index.has(target)){visit(target);low.set(name,Math.min(low.get(name),low.get(target)));}else if(onStack.has(target))low.set(name,Math.min(low.get(name),index.get(target)));}
      if(low.get(name)===index.get(name)){const component=[];let member;do{member=stack.pop();onStack.delete(member);component.push(member);}while(member!==name);components.push(component);}
    };
    names.forEach(name=>{if(!index.has(name))visit(name);});
    const componentOf=new Map();components.forEach((component,id)=>component.forEach(name=>componentOf.set(name,id)));
    const outgoing=components.map(()=>new Set()),indegree=components.map(()=>0),cyclic=components.map(component=>component.length>1||component.some(name=>adj.get(name).has(name)));
    for(const [source,targets] of adj)for(const target of targets){const a=componentOf.get(source),b=componentOf.get(target);if(a!==b&&!outgoing[a].has(b)){outgoing[a].add(b);indegree[b]++;}}
    const levels=components.map(()=>0),queue=[];indegree.forEach((degree,id)=>{if(degree===0)queue.push(id);});
    for(let at=0;at<queue.length;at++){const id=queue[at];for(const child of outgoing[id]){levels[child]=Math.max(levels[child],levels[id]+1);if(--indegree[child]===0)queue.push(child);}}
    const byName=new Map();components.forEach((component,id)=>component.forEach(name=>byName.set(name,{level:levels[id],cycle:cyclic[id]})));
    return byName;
  }
  const node=()=>network?.nodes.find(n=>n.name===el('node').value);
  function message(s,error=false){el('message').textContent=s;el('message').style.color=error?'var(--danger)':'';}
  function option(value,label){const o=document.createElement('option');o.value=value;o.textContent=label;return o;}
  function element(tag,attrs={},text=''){const e=document.createElementNS(NS,tag);Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,v));if(text)e.textContent=text;return e;}
  function parameter(){const n=node(),v=n?.parameters[el('param').value];el('value').value=v===undefined?'':typeof v==='object'?JSON.stringify(v):String(v);el('value').disabled=v===undefined||v===null||typeof v==='object';}
  function coupling(){const n=node(),target=n?.coupling[el('port').value];el('target').value=target||'';}
  function selectNode(){const n=node();if(!n)return;el('model').textContent=`${n.name} · ${n.model} · ${n.enabled?'启用':'禁用'}`;
    el('name').value=n.long_name;el('name').disabled=!n.enabled||n.long_name===n.name;
    el('param').replaceChildren(option('','不修改参数'),...Object.keys(n.parameters).map(k=>option(k,k)));
    el('port').replaceChildren(option('','不修改耦合'),...Object.keys(n.coupling).map(k=>option(k,k)));
    el('target').replaceChildren(option('','请选择已登记引用'),...network.targets.map(t=>option(t,t)));
    el('save').disabled=!n.enabled;parameter();coupling();renderFoodweb();draw();
  }
  function foodwebGroupNames(n){return n?.enabled&&n.model==='wet/fish'?['PLAN','BEN','PISC']:n?.enabled&&n.model==='wet/zooplankton'?['prey']:[];}
  function foodwebRowsFor(n,group){
    const p=n.parameters||{},coupling=n.coupling||{},meta=FOODWEB_GROUPS[group];
    if(group==='prey'){
      const count=Number.isInteger(p.nPrey)?Math.max(0,Math.min(p.nPrey,100)):Object.keys(coupling).filter(k=>/^prey_model\d+$/.test(k)).length;
      return Array.from({length:count},(_,i)=>({target:coupling[`prey_model${i+1}`]||'',suffix:p[`prey_suffix${i+1}`]||'',clearance:p[`cClearPrey${i+1}`]??0,gut_occupation:p[`fGutOccPrey${i+1}`]??1,lSi:p[`lSi${i+1}`]===true}));
    }
    const prefix={PLAN:'Plan',BEN:'Bent',PISC:'Pisc'}[group],port={PLAN:'PLANprey',BEN:'BENTprey',PISC:'PISCprey'}[group],countName={PLAN:'nPLAN',BEN:'nBEN',PISC:'nPISC'}[group];
    const count=Number.isInteger(p[countName])?Math.max(0,Math.min(p[countName],100)):Object.keys(coupling).filter(k=>new RegExp('^'+port+'\\d+$').test(k)).length;
    return Array.from({length:count},(_,i)=>({target:coupling[`${port}${i+1}`]||'',suffix:p[`${group}prey_suffix${i+1}`]||'',clearance:p[`cClear${prefix}${i+1}`]??0,gut_occupation:p[`fGutOcc${prefix}${i+1}`]??1}));
  }
  function foodwebGroupKey(name,group){return `${name}\0${group}`;}
  function foodwebStatusText(n,group){return `${n.name} · ${group} · prey clearance ${FOODWEB_GROUPS[group].units}；注册状态/单位在预览阶段由模型校验。${foodwebDirtyGroups.has(foodwebGroupKey(n.name,group))?' 有未保存的食性编辑。':''}`;}
  function availableFoodwebTargets(group,n){
    const meta=FOODWEB_GROUPS[group];if(!meta||!instanceCatalog)return [];
    const nodes=instanceCatalog.instances||network?.nodes||[];
    return nodes.filter(item=>item.enabled!==false&&item.name!==n?.name&&meta.families.includes(String(item.family||item.model||'').replace('wet/',''))).map(item=>({name:item.name,label:`${item.long_name||item.name} · ${item.model}`}));
  }
  function renderFoodweb(){
    const n=node(),groups=foodwebGroupNames(n),oldGroup=foodwebGroup.value;
    const consumers=(network?.nodes||[]).filter(item=>foodwebGroupNames(item).length);
    foodwebConsumer.replaceChildren(...consumers.map(item=>option(item.name,`${item.long_name||item.name} · ${item.model}`)));
    foodwebConsumer.value=groups.length?n.name:'';foodwebConsumer.disabled=networkReadOnly||!consumers.length;
    foodwebGroup.replaceChildren(...groups.map(group=>option(group,group==='prey'?'浮游动物 prey':`${group} · ${group==='PLAN'?'浮游动物/藻类':group==='BEN'?'底栖/水生/鱼类':'鱼类'}`)));
    foodwebGroup.disabled=!groups.length;foodwebAdd.disabled=!groups.length;foodwebReset.disabled=!groups.length||!n||busy;foodwebSave.disabled=!groups.length||!n||busy;
    foodwebRowsByGroup={...foodwebRowsByGroup};
    if(!groups.length){foodwebRows.replaceChildren();foodwebStatus.textContent='选择一个已启用的鱼类或浮游动物实例以编辑实际食性关系。';return;}
    const group=groups.includes(oldGroup)?oldGroup:groups[0];foodwebGroup.value=group;
    if(!foodwebRowsByGroup[n.name])foodwebRowsByGroup[n.name]={};
    if(!foodwebRowsByGroup[n.name][group])foodwebRowsByGroup[n.name][group]=foodwebRowsFor(n,group);
    const rows=foodwebRowsByGroup[n.name][group],targets=availableFoodwebTargets(group,n);foodwebRows.dataset.foodwebRows=group;foodwebRows.replaceChildren();
    rows.forEach((row,index)=>{
      const line=document.createElement('div');line.className='foodweb-row';line.dataset.foodwebRow=String(index);
      const target=document.createElement('select');target.dataset.foodwebTarget=group;target.setAttribute('aria-label','猎物目标');const legacyTarget=row.target&&!targets.some(t=>t.name===row.target)?[option(row.target,`${row.target} · 已有配置（推荐族外）`)]:[];target.replaceChildren(option('','选择 prey'),...targets.map(t=>option(t.name,t.label)),...legacyTarget);target.value=row.target||'';target.disabled=!n.enabled;
      const suffix=document.createElement('select');suffix.dataset.foodwebSuffix=group;suffix.setAttribute('aria-label','猎物后缀');suffix.replaceChildren(...FOODWEB_GROUPS[group].suffixes.map(s=>option(s,s||'默认')));suffix.value=row.suffix||'';
      const clearance=document.createElement('input');clearance.type='number';clearance.min='0';clearance.step='any';clearance.value=String(row.clearance??0);clearance.dataset.foodwebClearance=group;clearance.setAttribute('aria-label',`摄食清除率 (${FOODWEB_GROUPS[group].units})`);
      const gut=document.createElement('input');gut.type='number';gut.min='0.000001';gut.step='any';gut.value=String(row.gut_occupation??1);gut.dataset.foodwebGut=group;gut.setAttribute('aria-label','肠道占据率');
      const markDirty=()=>{foodwebDirtyGroups.add(foodwebGroupKey(n.name,group));foodwebStatus.textContent=foodwebStatusText(n,group);};
      for(const control of [target,suffix,clearance,gut]){control.addEventListener('change',markDirty);control.addEventListener('input',markDirty);}
      const remove=document.createElement('button');remove.type='button';remove.className='btn';remove.textContent='移除';remove.dataset.foodwebRemove=group;remove.addEventListener('click',()=>{rows.splice(index,1);foodwebDirtyGroups.add(foodwebGroupKey(n.name,group));renderFoodweb();});
      line.append(foodwebField('猎物目标',target),foodwebField('后缀',suffix),foodwebField(`摄食清除率 (${FOODWEB_GROUPS[group].units})`,clearance),foodwebField('肠道占据率',gut),foodwebField('操作',remove));foodwebRows.append(line);
    });
    foodwebStatus.textContent=foodwebStatusText(n,group);
  }
  function captureFoodwebRows(){
    const group=foodwebGroup.value,n=node(),stored=foodwebRowsByGroup[n.name][group]||[];
    const rendered=foodwebRows.children;
    return Array.from(rendered,(line,index)=>{const controls=Array.from(line.children,field=>field.children[1]);const row={...stored[index],target:controls[0].value,suffix:controls[1].value,clearance:Number(controls[2].value),gut_occupation:Number(controls[3].value)};return row;});
  }
  async function saveFoodweb(){
    const n=node(),groups=foodwebGroupNames(n);if(busy||!n||!groups.length)return;
    if(!network||norm(network.case_path)!==norm(state.activeCasePath)){foodwebStatus.textContent='案例已切换，请刷新网络后再修改。';return;}
    foodwebRowsByGroup[n.name][foodwebGroup.value]=captureFoodwebRows();
    const allGroups={PLAN:[],BEN:[],PISC:[]};let operation;
    if(n.model==='wet/fish'){for(const group of ['PLAN','BEN','PISC'])allGroups[group]=(foodwebRowsByGroup[n.name][group]||foodwebRowsFor(n,group)).map(row=>({...row,clearance_units:FOODWEB_GROUPS[group].units}));operation={op:'set_foodweb',name:n.name,groups:allGroups};}
    else operation={op:'set_foodweb',name:n.name,prey:(foodwebRowsByGroup[n.name].prey||foodwebRowsFor(n,'prey')).map(row=>({...row,clearance_units:FOODWEB_GROUPS.prey.units}))};
    for(const [group,rows] of Object.entries(n.model==='wet/fish'?allGroups:{prey:operation.prey})){
      if(rows.some(row=>!row.target||!Number.isFinite(row.clearance)||row.clearance<0||!Number.isFinite(row.gut_occupation)||row.gut_occupation<=0)){foodwebStatus.textContent=`${group} prey 需选择目标，clearance 需为非负数，gut occupation 必须大于 0。`;return;}
    }
    foodwebSave.disabled=true;foodwebStatus.textContent='正在执行模型端事务预览…';
    await transact(operation,'食性关系');
    foodwebSave.disabled=false;
    if(!/失败|不能删除|过期|切换|UNKNOWN_|INVALID_|UNIT_|DOMAIN_|DUPLICATE_|CASE_|STALE_|ERROR/i.test(el('message').textContent))foodwebStatus.textContent='食性关系已应用并刷新网络。';
    else foodwebStatus.textContent=el('message').textContent;
  }
  function populateModelChoices(){
    // The map filter only controls the graph; keep every registered family available for adding.
    const families=Object.entries(MODEL_GROUPS);
    const selected=el('add-model').value;
    el('add-model').replaceChildren(...families.map(([model,group])=>option('wet/'+model,group[1]+' · wet/'+model)));
    el('add-model').value=families.some(([model])=>'wet/'+model===selected)?selected:'wet/phytoplankton';
    populateTemplateChoices();
  }
  function populateTemplateChoices(){
    const model=el('add-model').value,previous=el('add-source').value;
    const templates=(instanceCatalog?.instances||[]).filter(item=>item.enabled!==false&&item.model===model);
    el('add-source').replaceChildren(option('','请选择克隆来源'),...templates.map(item=>option(item.name,`${item.long_name||item.name} · ${item.model}`)));
    el('add-source').value=templates.some(item=>item.name===previous)?previous:'';
    el('add-source').disabled=!templates.length;
    el('add').disabled=!el('add-source').value;
    el('add-template-hint').textContent=templates.length
      ?(el('add-source').value?`将从 ${el('add-source').value} 克隆完整实例配置；克隆后可编辑参数、初值和耦合。`:'请先选择一个同模型族克隆来源；克隆后可编辑参数、初值和耦合。')
      :'当前模型族没有可克隆的已启用实例；先配置一个有效实例，再回来克隆。';
  }
  function renderInstanceCatalog(catalog){
    instanceCatalog=catalog;
    populateTemplateChoices();
    const deleted=(catalog.deleted||[]).filter(item=>filter==='all'||item.domain===filter);
    el('deleted').replaceChildren(...deleted.map(item=>option(item.name,`${item.long_name||item.name} · ${item.model}`)));
    const selected=node();el('delete').disabled=!selected||!selected.enabled;
  }
  function transactionError(error){
    const value=String(error||'实例事务失败');
    if(value.includes('INSTANCE_IN_USE'))return '不能删除：该实例仍被其他模块引用。请先解除或改接这些耦合。'+value.replace(/^INSTANCE_IN_USE:\s*/, ' ');
    if(value.includes('UNKNOWN_TARGET_STATE'))return '耦合目标状态不可用。请从目标实例当前登记的状态/诊断端口中选择。'+value.replace(/^UNKNOWN_TARGET_STATE:\s*/, ' ');
    if(value.includes('PHYTOPLANKTON_MULTIPLEXER_INCONSISTENT'))return '藻类克隆已停止：埋藏/无机碳模块的 nPHYT 或编号耦合与现有藻类不一致。请先按提示修复这些模块后重试。'+value.replace(/^PHYTOPLANKTON_MULTIPLEXER_INCONSISTENT:\s*/, ' ');
    if(value.includes('MISSING_REGISTERED_DEPENDENCY'))return '克隆配置缺少模型要求的耦合端口；请先补齐列出的端口后再克隆或运行。'+value.replace(/^MISSING_REGISTERED_DEPENDENCY:\s*/, ' ');
    if(value.includes('UNVERIFIABLE_TARGET_STATE'))return '本地注册表无法验证该目标模型的端口；请检查模块版本与耦合，不会自动更改配置。'+value.replace(/^UNVERIFIABLE_TARGET_STATE:\s*/, ' ');
    if(value.includes('STALE_REVISION'))return '案例配置已更新，实例列表已刷新；请重新操作。';
    if(value.includes('CASE_CHANGED'))return '案例已切换，已取消实例修改。';
    return value;
  }
  async function transact(operation,label){
    if(busy)return;
    if(!instanceCatalog||norm(instanceCatalog.case_path)!==norm(state.activeCasePath)||norm(network?.case_path)!==norm(state.activeCasePath)){
      message('案例已切换，请刷新网络后再操作。',true);return;
    }
    const casePath=instanceCatalog.case_path,revision=instanceCatalog.revision;busy=true;
    const body={case_path:casePath,revision,operations:[operation],mode:'preview'};
    try{
      const preview=await api('/api/model/instances/transaction',{method:'POST',body});
      if(norm(casePath)!==norm(state.activeCasePath)||norm(preview.case_path||casePath)!==norm(casePath)){
        message('预览期间案例已切换，已取消实例修改。',true);return;
      }
      if(preview.error){message(transactionError(preview.error),true);return;}
      if(!preview.preview_hash||preview.revision!==revision){message('预览版本已过期，请刷新实例列表后重试。',true);return;}
      if(preview.initial_split){const split=preview.initial_split;const percent=value=>Number((value*100).toPrecision(8));const summary=`等总量初始 biomass share 分摊预览（不是物种/性状差异或竞争结论）：${split.source} 留下 ${percent(1-split.fraction_to_clone)}%、${split.clone} 获得 ${percent(split.fraction_to_clone)}%。将更改 ${split.states.length} 个状态：${split.states.join('、')}。参数与耦合保持完整复制。继续应用？`;if(!window.confirm(summary)){message('已取消等总量克隆；案例未修改。',true);return;}}
      const applied=await api('/api/model/instances/transaction',{method:'POST',body:{...body,mode:'apply',preview_hash:preview.preview_hash}});
      if(norm(casePath)!==norm(state.activeCasePath)){message('案例已切换；请确认当前案例的实例状态后再继续。',true);return;}
      if(applied.error){message(transactionError(applied.error),true);return;}
      const integrated=(preview.integrations||[]).map(module=>module==='burial'?'埋藏':module==='inorganic_carbon'?'无机碳':'').filter(Boolean);
      const integrationNote=integrated.length?` 已自动接入${integrated.join('、')}；鱼类和浮游动物的食物网保持原样，未自动增加该藻类作为猎物。`:'';
      busy=false;
      if(operation.op==='set_foodweb')for(const key of [...foodwebDirtyGroups])if(key.startsWith(`${operation.name}\0`))foodwebDirtyGroups.delete(key);
      await load();
      message(label+'已完成。'+integrationNote);
    }catch(error){message(transactionError(error.message),true);}
    finally{busy=false;}
  }
  async function addInstance(){
    const name=el('add-name').value.trim(),model=el('add-model').value,longName=el('add-display-name').value.trim();
    if(!name){message('请填写实例名。',true);return;}
    if(!model){message('请先选择模型族。',true);return;}
    const source=el('add-source').value;
    if(!source){message('当前模型族没有已配置的克隆来源；请先配置一个同模型族实例。',true);return;}
    const operation={op:'clone',source,name};if(longName)operation.long_name=longName;
    if(el('clone-mode').value==='split')operation.initial_fraction=Number(el('clone-fraction').value);
    await transact(operation,'克隆实例');el('add-name').value='';el('add-display-name').value='';
  }
  async function deleteInstance(){const n=node();if(!n){message('请先选择要删除的实例。',true);return;}await transact({op:'delete',name:n.name},'软删除实例');}
  async function restoreInstance(){const name=el('deleted').value;if(!name){message('请选择要恢复的已删除实例。',true);return;}await transact({op:'restore',name},'恢复实例');}
  function transform(){const g=svg.querySelector('#en-graph');if(g)g.setAttribute('transform',`translate(${view.x} ${view.y}) scale(${view.scale})`);}
  function draw(){if(!network)return;svg.replaceChildren();const candidates=visibleNodes(),allDietaryEdges=foodwebEdges(),fullLayering=viewMode==='foodweb'?foodwebLayering(candidates,allDietaryEdges):new Map();
    const layoutLevels=new Set([...fullLayering.values()].map(item=>item.level));
    const supportsThreeLayerPath=viewMode==='foodweb'&&layoutLevels.size>=3&&resolvedFoodwebPaths.some(path=>new Set(path.nodes.map(name=>fullLayering.get(name)?.level)).size===3);
    const threeLayerButton=el('foodweb-three-layer');threeLayerButton.disabled=!supportsThreeLayerPath;
    if(!supportsThreeLayerPath&&foodwebLayerView==='three'){foodwebLayerView='full';threeLayerButton.setAttribute('aria-pressed','false');}
    const shown=viewMode==='foodweb'&&foodwebLayerView==='three'?candidates.filter(n=>(fullLayering.get(n.name)?.level??Infinity)<3):candidates,shownNames=new Set(shown.map(n=>n.name));
    const defs=element('defs'),marker=element('marker',{id:'en-arrow',viewBox:'0 0 10 10',refX:9,refY:5,markerWidth:5,markerHeight:5,orient:'auto-start-reverse'}),cycleMarker=element('marker',{id:'en-arrow-cycle',viewBox:'0 0 10 10',refX:9,refY:5,markerWidth:5,markerHeight:5,orient:'auto-start-reverse'});
    marker.append(element('path',{d:'M 0 0 L 10 5 L 0 10 z',fill:'#657e86'}));cycleMarker.append(element('path',{d:'M 0 0 L 10 5 L 0 10 z',fill:'#987746'}));defs.append(marker,cycleMarker);svg.append(defs);
    const g=element('g',{id:'en-graph'});svg.append(g);const positions=new Map(),foodwebTierByName=new Map(),featuredEdgeKeys=new Set(),featuredNodeNames=new Set(),count=shown.length;let centerX=450,centerY=235,cardWidth=124,cardHeight=44;
    if(viewMode==='foodweb'){
      const edges=allDietaryEdges.filter(edge=>shownNames.has(edge.source)&&shownNames.has(edge.target)),layers=foodwebLayering(shown,edges),maxLevel=Math.max(0,...[...layers.values()].map(item=>item.level)),groups=new Map();
      const familyByName=new Map(network.nodes.map(item=>[item.name,item.model]));
      const edgeKeys=new Set(edges.map(foodwebEdgeKey)),visiblePaths=resolvedFoodwebPaths.filter(path=>path.edges.every(edge=>edgeKeys.has(foodwebEdgeKey(edge))));
      const featuredPath=visiblePaths.find(path=>['wet/phytoplankton','wet/om_pool','wet/macrophytes'].includes(familyByName.get(path.nodes[0]))&&['wet/zooplankton','wet/zoobenthos','wet/bivalves'].includes(familyByName.get(path.nodes[1]))&&['wet/fish','wet/fish_pclake'].includes(familyByName.get(path.nodes[2])))||visiblePaths[0];
      if(featuredPath){featuredPath.nodes.forEach(name=>featuredNodeNames.add(name));featuredPath.edges.forEach(edge=>featuredEdgeKeys.add(`${edge.source}\0${edge.target}`));}
      for(const n of shown){const item=layers.get(n.name)||{level:0,cycle:false};if(!groups.has(item.level))groups.set(item.level,[]);groups.get(item.level).push(n);foodwebTierByName.set(n.name,item.cycle?'cycle':`level-${item.level}`);}
      for(const items of groups.values())items.sort((a,b)=>a.name.localeCompare(b.name));
      const maxLayerSize=Math.max(1,...[...groups.values()].map(items=>items.length)),viewportWidth=svg.parentElement?.clientWidth||svg.getBoundingClientRect().width||900;
      // Size cards and horizontal spacing against the available plot width. Keep
      // every configured node visible; overflow remains horizontally scrollable.
      cardWidth=Math.max(176,Math.min(236,(viewportWidth-48)/Math.min(maxLayerSize,4)));
      cardHeight=Math.max(58,Math.min(70,cardWidth*.29));
      const spacing=maxLayerSize>1?Math.max(cardWidth+28,(viewportWidth-cardWidth)/(maxLayerSize-1)):cardWidth+48;
      const canvasWidth=Math.max(viewportWidth,(maxLayerSize-1)*spacing+cardWidth+40),canvasHeight=620;
      centerX=canvasWidth/2;svg.setAttribute('viewBox',`0 0 ${canvasWidth} ${canvasHeight}`);
      if(svg.parentElement){svg.parentElement.style.width='100%';svg.parentElement.style.overflowX='auto';svg.parentElement.style.overscrollBehaviorX='contain';svg.parentElement.setAttribute('role','region');svg.parentElement.setAttribute('aria-label','可横向滚动的食性网络图');svg.parentElement.setAttribute('tabindex','0');}
      svg.style.width=`${canvasWidth}px`;svg.style.maxWidth='none';
      const enabledNodes=network.nodes.filter(n=>n.enabled!==false),fishCount=enabledNodes.filter(n=>['wet/fish','wet/fish_pclake'].includes(n.model)).length;
      const configuredEdges=edges.length,fullLayerCount=new Set([...fullLayering.values()].map(item=>item.level)).size;
      const fishStatus=fishCount?`${fishCount} 个启用鱼类实例`:'当前配置没有启用鱼类实例';
      const roles=foodwebEvidence();
      const cycleStatus=`完整配置闭合三节点有向环 ${roles.cycles} 个`;
      const layerStatus=foodwebLayerView==='three'?`真实配置三层子网（过滤视图）· 完整网络 ${allDietaryEdges.length} 条、${fullLayerCount} 个布局层`:`完整食性网络 · ${allDietaryEdges.length} 条已解析边、${fullLayerCount} 个布局层`;
      g.append(element('text',{x:18,y:26,fill:'#2d3b35','font-size':14,'font-weight':600,'data-foodweb-summary':'true'},`${layerStatus} · 当前显示 ${shown.length} 个端点实例、${configuredEdges} 条真实猎物→消费者边、${groups.size} 个关系布局层 · 橙色双边标出一条三节点/两边示例路径；金色边仅表示闭环 · ${cycleStatus} · 分层不代表营养级 · 生产者/碎屑 ${roles.producersAndDetritus.length} · 消费者 ${roles.configuredConsumers.length} · 鱼类 ${roles.configuredFish.length}（${fishStatus}）`));
      if(foodwebLayerView==='three'){
        const omitted=allDietaryEdges.filter(edge=>(fullLayering.get(edge.source)?.level??Infinity)<3&&(fullLayering.get(edge.target)?.level??Infinity)>=3);
        const omittedPairs=[...new Set(omitted.map(edge=>`${edge.source} → ${edge.target}`))];
        g.append(element('text',{x:18,y:48,fill:'#987746','font-size':12,'data-foodweb-filter-note':'true'},`未显示第4+层关系 ${omittedPairs.length} 条（完整网保留）：${omittedPairs.join('；')||'无'}`));
      }
      for(const [level,items] of groups){const y=canvasHeight-104-(maxLevel?level/maxLevel:0)*(canvasHeight-244);items.forEach((n,i)=>positions.set(n.name,[centerX+(i-(items.length-1)/2)*spacing,y]));
        const hasCycle=items.some(n=>layers.get(n.name)?.cycle),tier=hasCycle?`cycle-level-${level}`:`level-${level}`;
        const memberModels=new Set(items.map(item=>item.model));
        const basalModels=new Set(['wet/phytoplankton','wet/om_pool','wet/macrophytes']);
        const consumerModels=new Set(['wet/zooplankton','wet/zoobenthos','wet/bivalves']);
        const role=hasCycle?'含环的混合配置关系':level===0&&items.every(item=>basalModels.has(item.model))?'生产者/碎屑类型实例':memberModels.has('wet/fish')||memberModels.has('wet/fish_pclake')?'含鱼类类型实例':level>0&&items.some(item=>consumerModels.has(item.model))?'含消费者类型实例':'已配置食性关系层';
        const position=maxLevel===0?'唯一布局层':level===0?'底层':level===maxLevel?'顶层':'中间层';
        const label=hasCycle?`混合配置${position} ${level+1} · ${role}（未判定营养级）`:`${position} · 配置层 ${level+1} · ${role}（未判定营养级）`;
        g.append(element('text',{x:centerX,y:y-cardHeight/2-22,'text-anchor':'middle',fill:'#455e65','font-size':16,'font-weight':600,'data-foodweb-tier-label':tier},`${label} · ${items.length} 个实例`));
      }
    } else {svg.setAttribute('viewBox','0 0 900 470');svg.style.width='100%';svg.style.maxWidth='100%';if(svg.parentElement){svg.parentElement.style.overflowX='hidden';svg.parentElement.removeAttribute('role');svg.parentElement.removeAttribute('aria-label');svg.parentElement.removeAttribute('tabindex');}shown.forEach((n,i)=>{const angle=2*Math.PI*i/Math.max(count,1)-Math.PI/2;positions.set(n.name,[450+330*Math.cos(angle),235+170*Math.sin(angle)]);});}
    const edgesToDraw=viewMode==='foodweb'?foodwebEdges().filter(e=>shownNames.has(e.source)&&shownNames.has(e.target)):network.edges;
    const cycleEdgeKeys=viewMode==='foodweb'?foodwebCycleSummary.edgeKeys:new Set();
    const cycleNodeNames=new Set([...cycleEdgeKeys].flatMap(key=>key.split('\0')));
    const grouped=new Map();edgesToDraw.filter(e=>shownNames.has(e.source)&&shownNames.has(e.target)).forEach(e=>{const key=e.source+'\0'+e.target;if(!grouped.has(key))grouped.set(key,[]);grouped.get(key).push(e);});
    let routeIndex=0;grouped.forEach(edges=>{const edgeIndex=routeIndex++,e=edges[0],[x1,y1]=positions.get(e.source),[x2,y2]=positions.get(e.target),len=Math.hypot(x2-x1,y2-y1)||1;
      const active=el('node').value===e.source||el('node').value===e.target;
      const endX=x2-(x2-x1)/len*(viewMode==='foodweb'?cardWidth/2+5:38),endY=y2-(y2-y1)/len*(viewMode==='foodweb'?cardHeight/2+5:28);
      // Route each trophic edge around its own midpoint. A shared control
      // point makes every configured prey link converge at the canvas center.
      const dx=endX-x1,dy=endY-y1,routeOffset=viewMode==='foodweb'?((edgeIndex%5)-2)*14:0;
      const startX=viewMode==='foodweb'?x1+(dx/len)*(cardWidth/2+5):x1,startY=viewMode==='foodweb'?y1+(dy/len)*(cardHeight/2+5):y1;
      const controlX=viewMode==='foodweb'?(startX+endX)/2-(dy/len)*routeOffset:centerX;
      const controlY=viewMode==='foodweb'?(startY+endY)/2+(dx/len)*routeOffset:centerY;
      const isCycleEdge=viewMode==='foodweb'&&cycleEdgeKeys.has(`${e.source}\0${e.target}`);
      const isFeatured=viewMode==='foodweb'&&featuredEdgeKeys.has(`${e.source}\0${e.target}`);
      const pathFocused=viewMode==='foodweb'&&edges.some(edge=>focusedFoodwebPath?.edges.has(foodwebEdgeKey(edge)));
      const lineAttrs={d:`M ${startX} ${startY} Q ${controlX} ${controlY} ${endX} ${endY}`,fill:'none',stroke:isFeatured?'#75836d':isCycleEdge?'#987746':active?'#455e65':'#657e86','stroke-width':isFeatured?4:isCycleEdge?3:active?2.4:1.8,opacity:isFeatured||isCycleEdge?.98:active?.95:.62,'marker-end':isCycleEdge?'url(#en-arrow-cycle)':'url(#en-arrow)'};
      if(pathFocused)Object.assign(lineAttrs,{stroke:'#496f68','stroke-width':4.5,opacity:.98});
      if(viewMode==='foodweb')Object.assign(lineAttrs,{tabindex:0,role:'button','aria-label':`${isFeatured?'三节点/两边示例路径边；':''}${isCycleEdge?'已解析闭环边；':''}${edges.map(v=>`${v.source} 猎物 → ${v.target} 消费者 · ${v.port}`).join('；')}`,'data-foodweb-edge':'true','data-foodweb-cycle':String(isCycleEdge),'data-foodweb-featured-path':String(isFeatured),'data-foodweb-source':e.source,'data-foodweb-target':e.target,'data-foodweb-port':edges.map(v=>v.port).join(',')});
      const line=element('path',lineAttrs);
      line.setAttribute('data-foodweb-path-edge-focused',String(pathFocused));
      line.append(element('title',{},edges.map(v=>`${v.reference} → ${v.target} [${v.port}]`).join('\n')));g.append(line);
      if(viewMode==='foodweb'){
        const labelT=.42,labelX=(1-labelT)**2*startX+2*(1-labelT)*labelT*controlX+labelT**2*endX,labelY=(1-labelT)**2*startY+2*(1-labelT)*labelT*controlY+labelT**2*endY;
        const label=element('text',{x:labelX,y:labelY,'text-anchor':'middle',fill:'#2d3b35','font-size':10,'paint-order':'stroke','stroke':'#fbfaf6','stroke-width':3,'pointer-events':'none','data-foodweb-port':edges.map(v=>v.port).join(','),visibility:'hidden'} ,edges.map(v=>v.port).join(', '));
        label.append(element('title',{},edges.map(v=>`${v.source} prey → ${v.target} consumer · ${v.port}`).join('\n')));g.append(label);
        const showLabel=()=>label.setAttribute('visibility','visible'),hideLabel=()=>label.setAttribute('visibility','hidden');line.addEventListener('pointerenter',showLabel);line.addEventListener('pointerleave',hideLabel);line.addEventListener('focus',showLabel);line.addEventListener('blur',hideLabel);
      }
    });
    shown.forEach(n=>{const [x,y]=positions.get(n.name),selected=n.name===el('node').value,[,kind]=modelGroup(n);
      const attrs={transform:`translate(${x} ${y})`,tabindex:0,role:'button','aria-label':n.name,style:'cursor:pointer'};
      if(viewMode==='foodweb')attrs['data-foodweb-tier']=foodwebTierByName.get(n.name)||'unclassified';
      const group=element('g',attrs);
      const inCycle=viewMode==='foodweb'&&cycleNodeNames.has(n.name),pathFocused=viewMode==='foodweb'&&focusedFoodwebPath?.nodes.has(n.name)===true;
      if(viewMode==='foodweb')group.setAttribute('data-foodweb-cycle',String(inCycle));
      if(viewMode==='foodweb')group.setAttribute('data-foodweb-path-focused',String(pathFocused));
      const isFeaturedNode=viewMode==='foodweb'&&featuredNodeNames.has(n.name);
      group.append(element('rect',{x:-cardWidth/2,y:-cardHeight/2,width:cardWidth,height:cardHeight,rx:4,fill:n.enabled?'#657e86':'#8b9088',stroke:pathFocused?'#496f68':selected?'#987746':isFeaturedNode?'#75836d':inCycle?'#987746':'#455e65','stroke-width':pathFocused?4:selected?3:isFeaturedNode?3:inCycle?2.5:1.5}));
      const nameLines=[];let remaining=n.name;
      while(remaining.length>22){let cut=remaining.lastIndexOf('_',22);if(cut<10)cut=22;nameLines.push(remaining.slice(0,cut));remaining=remaining.slice(cut+(remaining[cut]==='_'?1:0));}
      nameLines.push(remaining);
      const nodeLabel=element('text',{'text-anchor':'middle',fill:'#fff','font-size':14,'font-weight':600});
      const lineHeight=17,startY=-(nameLines.length-1)*lineHeight/2+5;
      nameLines.forEach((line,index)=>nodeLabel.append(element('tspan',{x:0,y:startY+index*lineHeight},line)));
      group.append(nodeLabel);
      group.append(element('title',{},`${kind} · ${n.name}\n${n.long_name}\n${n.model}`));
      const pick=()=>{el('node').value=n.name;selectNode();};group.addEventListener('click',pick);group.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();pick();}});g.append(group);
    });transform();
  }
  function setReadOnlyExample(readOnly){networkReadOnly=readOnly;for(const id of ['node-editor','foodweb-editor','instance-editor']){const panel=document.getElementById('en-'+id);if(panel)panel.hidden=readOnly;}for(const id of ['parameters','modules'])el(id).disabled=readOnly;}
  async function load(source=el('network-source').value||'active'){if(busy)return;busy=true;const identity=norm(state.activeCasePath),readOnly=source==='erken_reference';try{const s=await api(readOnly?'/api/ecology/network?source=erken_reference':'/api/ecology/network');if(identity!==norm(state.activeCasePath))return;
      if(s.error){network=null;foodwebCycleSummary={count:0,edgeKeys:new Set()};svg.replaceChildren();message(s.error,true);return;}
      const old=el('node').value,changed=!network||norm(network.case_path)!==norm(s.case_path)||networkReadOnly!==readOnly;network=s;setReadOnlyExample(readOnly);if(changed){view={scale:1,x:0,y:0};foodwebRowsByGroup={};foodwebLayerView='full';focusedFoodwebPath=null;el('foodweb-three-layer').setAttribute('aria-pressed','false');}
      el('node').replaceChildren(...s.nodes.map(n=>option(n.name,`${modelGroup(n)[1]} · ${n.name}`+(n.enabled?'':'（禁用）'))));if(s.nodes.some(n=>n.name===old))el('node').value=old;else if(s.nodes.length)el('node').value=s.nodes[0].name;
      const counts=new Map();s.nodes.forEach(n=>{const [,label]=modelGroup(n);counts.set(label,(counts.get(label)||0)+1);});el('families').textContent=`${[...counts].map(([label,count])=>`${label} ${count} 个物种实例`).join(' · ')||'此案例没有已登记实例'}；${readOnly?'固定 Erken 配置示例只读，不改变活动案例。':'视图过滤只影响显示，修改保存到当前活动案例。'}`;
      if(!readOnly){populateModelChoices();const catalog=await api('/api/model/instances?domain=all');if(identity!==norm(state.activeCasePath))return;
        if(catalog.error){message('实例列表加载失败：'+catalog.error,true);return;}
        if(norm(s.case_path)!==norm(catalog.case_path||''))return;renderInstanceCatalog(catalog);
      }else{instanceCatalog=null;}
      updateFoodwebEvidence();updateFoodwebRelations();message(`${readOnly?'Erken 只读配置示例：':''}${s.nodes.length} 个 FABM 实例 · ${s.edges.length} 个显式耦合端口 · ${foodwebEvidence().edges.length} 个已解析食性引用`);selectNode();
    }catch(e){message('网络加载失败：'+e.message,true);}finally{busy=false;}}
  async function save(){const n=node();if(busy||!n)return;if(norm(network.case_path)!==norm(state.activeCasePath)){message('案例已切换，请刷新网络',true);return;}
    const body={case_path:network.case_path,revision:network.revision,module:n.name};
    if(!el('name').disabled&&el('name').value!==n.long_name)body.long_name=el('name').value;
    const p=el('param').value;if(p&&!el('value').disabled){const old=n.parameters[p],text=el('value').value;let value=text;
      if(typeof old==='boolean'){if(!['true','false'].includes(text)){message('布尔值请输入 true 或 false',true);return;}value=text==='true';}
      if(typeof old==='number'){if(!text.trim()||!Number.isFinite(Number(text))){message('请输入有限数值',true);return;}value=Number(text);}body.parameters={[p]:value};}
    const port=el('port').value;if(port)body.coupling={[port]:el('target').value};busy=true;
    try{const s=await api('/api/ecology/network',{method:'POST',body});if(norm(body.case_path)!==norm(state.activeCasePath))return;
      if(s.error){message(s.error,true);return;}network=s;updateFoodwebEvidence();updateFoodwebRelations();selectNode();message('节点已保存，原配置备份：'+s.backup);
      const fabm=await api('/api/config/fabm');if(!fabm.error&&norm(body.case_path)===norm(state.activeCasePath))state.fabmModules=fabm.modules;
    }catch(e){message('保存失败：'+e.message,true);}finally{busy=false;}}
  function zoom(factor){const before=view.scale;view.scale=Math.max(.4,Math.min(8,before*factor));const k=view.scale/before,viewBox=String(svg.getAttribute?.('viewBox')||svg.attributes?.viewBox||'0 0 900 470').split(/\s+/),anchorX=(Number(viewBox[2])||900)/2,anchorY=(Number(viewBox[3])||470)/2;view.x=anchorX+(view.x-anchorX)*k;view.y=anchorY+(view.y-anchorY)*k;transform();}
  svg.addEventListener('wheel',e=>{if(e.ctrlKey)return;e.preventDefault();zoom(Math.exp(-e.deltaY*.001));},{passive:false});
  svg.addEventListener('pointerdown',e=>{if(e.target.closest('[role="button"]'))return;pan={x:e.clientX,y:e.clientY};svg.setPointerCapture(e.pointerId);});
  svg.addEventListener('pointermove',e=>{if(!pan)return;const r=svg.getBoundingClientRect();view.x+=(e.clientX-pan.x)*900/r.width;view.y+=(e.clientY-pan.y)*470/r.height;pan={x:e.clientX,y:e.clientY};transform();});
  svg.addEventListener('pointerup',()=>pan=null);svg.addEventListener('pointercancel',()=>pan=null);
  el('node').onchange=()=>{selectNode();if(instanceCatalog)renderInstanceCatalog(instanceCatalog);};el('param').onchange=parameter;el('port').onchange=coupling;el('save').onclick=save;el('load').onclick=()=>load();el('network-source').addEventListener('change',()=>load(el('network-source').value));
  el('foodweb-three-layer').disabled=true;
  el('view-couplings').addEventListener('click',()=>{viewMode='couplings';el('view-couplings').setAttribute('aria-pressed','true');el('view-foodweb').setAttribute('aria-pressed','false');el('foodweb-three-layer').disabled=true;draw();});
  el('view-foodweb').addEventListener('click',()=>{viewMode='foodweb';el('view-couplings').setAttribute('aria-pressed','false');el('view-foodweb').setAttribute('aria-pressed','true');draw();});
  el('open-foodweb-editor').addEventListener('click',()=>{
    viewMode='foodweb';el('view-couplings').setAttribute('aria-pressed','false');el('view-foodweb').setAttribute('aria-pressed','true');draw();
    const reduceMotion=window.matchMedia?.('(prefers-reduced-motion: reduce)').matches===true;
    foodwebPanel.scrollIntoView({block:'start',behavior:reduceMotion?'auto':'smooth'});
    foodwebPanel.focus({preventScroll:true});
  });
  el('foodweb-three-layer').addEventListener('click',()=>{if(viewMode!=='foodweb')return;foodwebLayerView=foodwebLayerView==='three'?'full':'three';el('foodweb-three-layer').setAttribute('aria-pressed',String(foodwebLayerView==='three'));draw();});
  if(typeof ResizeObserver!=='undefined'&&svg.parentElement){let resizeFrame=0;new ResizeObserver(()=>{if(viewMode==='foodweb'&&!resizeFrame)resizeFrame=requestAnimationFrame(()=>{resizeFrame=0;draw();});}).observe(svg.parentElement);}
  foodwebConsumer.addEventListener('change',()=>{if(!foodwebConsumer.value)return;el('node').value=foodwebConsumer.value;selectNode();if(instanceCatalog)renderInstanceCatalog(instanceCatalog);});
  foodwebGroup.addEventListener('change',()=>renderFoodweb());foodwebAdd.addEventListener('click',()=>{const n=node(),group=foodwebGroup.value;if(!n||!group)return;if(!foodwebRowsByGroup[n.name])foodwebRowsByGroup[n.name]={};if(!foodwebRowsByGroup[n.name][group])foodwebRowsByGroup[n.name][group]=foodwebRowsFor(n,group);foodwebRowsByGroup[n.name][group].push({target:'',suffix:'',clearance:0,gut_occupation:1});foodwebDirtyGroups.add(foodwebGroupKey(n.name,group));renderFoodweb();});
  foodwebReset.addEventListener('click',()=>{const n=node(),group=foodwebGroup.value;if(!n||!group||busy)return;foodwebRowsByGroup[n.name][group]=foodwebRowsFor(n,group);foodwebDirtyGroups.delete(foodwebGroupKey(n.name,group));renderFoodweb();foodwebStatus.textContent=`${n.name} · ${group} · 已还原为当前案例中已保存的食性配置；尚未提交更改。`;});
  foodwebSave.addEventListener('click',saveFoodweb);
  el('add-model').addEventListener('change',populateTemplateChoices);el('clone-mode').addEventListener('change',()=>{el('clone-fraction').disabled=el('clone-mode').value!=='split';});el('add-source').addEventListener('change',()=>{const source=(instanceCatalog?.instances||[]).find(item=>item.name===el('add-source').value);el('add').disabled=!source;if(source)el('add-template-hint').textContent=`来源 ${source.name}。完整复制会将源实例初始值按原样复制；同一功能群初始总生物量会增加；等总量分摊仅在所有注册初始状态都显式且可识别时可用，实际状态清单会在预览中确认。捕食者/消费者不会自动引用新实例；公平竞争比较还需设置总初始生物量、食谱和显式耦合。`;else populateTemplateChoices();});
  el('add').onclick=addInstance;el('delete').onclick=deleteInstance;el('restore').onclick=restoreInstance;
  document.querySelectorAll('[data-network-filter]').forEach(button=>button.addEventListener('click',()=>{filter=button.dataset.networkFilter;document.querySelectorAll('[data-network-filter]').forEach(item=>item.setAttribute('aria-pressed',String(item===button)));populateModelChoices();if(instanceCatalog)renderInstanceCatalog(instanceCatalog);draw();}));
  el('parameters').onclick=async()=>{const n=node();if(!n)return;const identity=norm(state.activeCasePath),s=await api('/api/config/fabm');if(s.error||identity!==norm(state.activeCasePath))return;
    state.fabmModules=s.modules;navigate('parameters');document.getElementById('param-module-select').value=n.name;loadModuleParams();};
  el('modules').onclick=()=>navigate('modules');window.loadEcologyNetwork=()=>load('active');
  if(window.ViewControls)ViewControls.registerGraphic(svg,{reset:()=>{view={scale:1,x:0,y:0};transform();},resize:()=>{},zoom});
})();
