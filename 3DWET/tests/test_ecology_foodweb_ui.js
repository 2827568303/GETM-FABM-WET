const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const source = fs.readFileSync('3DWET/app/static/js/ecology_network.js', 'utf8');
const indexTemplate = fs.readFileSync('3DWET/app/templates/index.html', 'utf8');
const studioCss = fs.readFileSync('3DWET/app/static/css/studio.css', 'utf8');
assert.match(indexTemplate, /\/static\/js\/ecology_network\.js\?v=34/, 'food-web script cache version matches the updated source');
assert.match(indexTemplate, /\/static\/css\/scientific_workspace\.css\?v=14/, 'food-web stylesheet cache version matches the updated styles');
assert.match(indexTemplate, /\/static\/css\/studio\.css\?v=12/, 'food-web editor card styles use a refreshed stylesheet URL');
assert.match(studioCss, /#en-foodweb-editor \.foodweb-row\s*\{[^}]*grid-template-columns:\s*repeat\(2,\s*minmax\(0,\s*1fr\)\)[^}]*border:\s*1px solid/s,
  'each prey relationship is a bordered card with two readable field columns');
assert.match(studioCss, /#en-foodweb-editor \.foodweb-field\s*\{[^}]*min-width:\s*0[^}]*background:/s,
  'individual prey controls are visually grouped as fields within their card');

function testThreeNodeFoodwebPaths() {
  const context={document:{getElementById:()=>null},window:{}};
  const run=vm.runInNewContext;
  const paths=run(source+`\ndirectedFoodwebPaths([
    {source:'a',target:'b',reference:'a/sDW',port:'prey_model1'},
    {source:'b',target:'c',reference:'b/sDW',port:'PLANprey1'},
    {source:'c',target:'a',reference:'c/sDW',port:'PISCprey1'},
    {source:'a',target:'a',reference:'a/sDW',port:'self'},
  ])`,context);
  assert.equal(paths.length,3,'closed triangle exposes its three directed two-edge paths');
  assert.ok(paths.some(path=>path.nodes.join('>')==='a>b>c'),'path nodes are three distinct instances');
  assert.ok(paths.every(path=>new Set(path.nodes).size===3&&path.edges.length===2),'self links and repeated-node paths are excluded');
  assert.equal(run(source+`\ndirectedFoodwebPaths([{source:'a',target:'b',reference:'a/sDW',port:'p'}]).length`,context),0,'one isolated dietary edge cannot form a three-node path');
}
testThreeNodeFoodwebPaths();

class Element {
  constructor(tag = 'div') { this.tagName = tag; this.children = []; this.dataset = {}; this.style = {}; this.attributes = {}; this.listeners = {}; this.value = ''; this.disabled = false; this.textContent = ''; this.type = ''; }
  append(...children) { this.children.push(...children); }
  appendChild(child) { this.children.push(child); return child; }
  replaceChildren(...children) { this.children = children; }
  setAttribute(k, v) { this.attributes[k] = String(v); }
  removeAttribute(k) { delete this.attributes[k]; }
  addEventListener(k, fn) { this.listeners[k] = fn; }
  focus() { this.focused = true; }
  scrollIntoView(options) { this.scrolledIntoView = options; }
  closest() { return null; }
  querySelector(selector) { return find(this, e => e !== this && e.attributes?.id === selector.replace(/^#/, '')); }
  querySelectorAll() { return []; }
  getBoundingClientRect() { return { width: this.layoutWidth || 900, height: 470 }; }
  click() { return this.listeners.click?.({ target: this, preventDefault() {} }); }
  get value() { return this._value || ''; }
  set value(value) { this._value = this.tagName === 'select' && this.children.length && !this.children.some(child => child.value === String(value)) ? '' : String(value); }
}

function find(root, predicate) {
  if (predicate(root)) return root;
  for (const child of root.children || []) { const found = find(child, predicate); if (found) return found; }
  return null;
}
function makeNode(name, model, parameters = {}, coupling = {}) {
  return { name, long_name: name, model, enabled: true, parameters, coupling };
}
function setup({ reject = false, graph = null, referenceGraph = null, width = 900, controls = null } = {}) {
  const elements = new Map();
  const get = id => { if (!elements.has(id)) elements.set(id, new Element(id)); return elements.get(id); };
  const page = get('page-gridstudio');
  get('en-svg').layoutWidth = width;
  get('en-svg').parentElement = new Element('div');
  get('en-svg').parentElement.clientWidth = width;
  const document = { getElementById: get, createElement: tag => new Element(tag), createElementNS: (_ns, tag) => new Element(tag), querySelectorAll: () => [] };
  const state = { activeCasePath: 'C:/cases/lake-a', fabmModules: [] };
  const fish = makeNode('fish_a', 'wet/fish', { nPLAN: 1, PLANprey_suffix1: 'W', cClearPlan1: 0.2, fGutOccPlan1: 0.7 }, { PLANprey1: 'phyto_a' });
  const nodes = [fish, makeNode('phyto_a', 'wet/phytoplankton'), makeNode('zoo_a', 'wet/zooplankton'), makeNode('benthos_a', 'wet/zoobenthos'), makeNode('other_fish', 'wet/fish_pclake')];
  const calls = [];
  const api = async (url, options = {}) => {
    calls.push({ url, options: structuredClone(options) });
    if (url === '/api/ecology/network?source=erken_reference' && !options.method && referenceGraph)
      return { case_path: 'C:/cases/Erken_real_20200101_24h_stage', revision: 'ref-rev', nodes: referenceGraph.nodes.map(n => structuredClone(n)), edges: referenceGraph.edges.map(e => structuredClone(e)), targets: [] };
    if (url === '/api/ecology/network' && !options.method) return { case_path: state.activeCasePath, revision: 'rev-1', nodes: (graph?.nodes||nodes).map(n => structuredClone(n)), edges: graph?.edges||[{ source: 'phyto_a', target: 'fish_a', port: 'PLANprey1', reference: 'phyto_a/sDW' }], targets: [] };
    if (url === '/api/model/instances?domain=all') return { case_path: state.activeCasePath, revision: 'rev-1', instances: (graph?.nodes||nodes).map(n => ({ name: n.name, model: n.model, family: n.model.slice(4), enabled: true })), deleted: [] };
    if (url === '/api/model/instances/transaction') {
      if (options.body.mode === 'preview' && reject) return { error: 'UNKNOWN_PORT: phyto_a missing registered state sDW' };
      if (options.body.mode === 'preview') return { case_path: state.activeCasePath, revision: 'rev-1', preview_hash: 'foodweb-preview' };
      return { case_path: state.activeCasePath, revision: 'rev-2' };
    }
    return { error: 'UNEXPECTED_API ' + url };
  };
  const viewControls=controls ? { registerGraphic: (_svg, api) => controls.push(api) } : null;
  const window = { ViewControls: viewControls };
  vm.runInNewContext(source, { document, window, state, api, navigate() {}, loadModuleParams() {}, ViewControls: viewControls, console });
  return { page, calls, state, window, el: id => get('en-' + id), find: predicate => find(page, predicate) };
}

async function main() {
  const app = setup();
  await app.window.loadEcologyNetwork();
  const foodwebEditorJump = app.el('open-foodweb-editor');
  foodwebEditorJump.click();
  assert.equal(app.el('view-foodweb').attributes['aria-pressed'], 'true', 'the foodweb editor shortcut switches the synchronized topology to dietary configuration');
  assert.equal(app.el('view-couplings').attributes['aria-pressed'], 'false', 'the all-couplings view is no longer marked active after opening foodweb editing');
  const foodwebEditor = app.find(e => e.id === 'en-foodweb-editor');
  assert.equal(foodwebEditor.scrolledIntoView.block, 'start', 'the shortcut aligns the relationship editor at the top');
  assert.equal(foodwebEditor.scrolledIntoView.behavior, 'smooth', 'the shortcut scrolls smoothly for standard-motion users');
  assert.equal(foodwebEditor.focused, true, 'the relationship editor receives keyboard focus');
  const consumer = app.find(e => e.dataset.foodwebConsumerSelect);
  assert.ok(consumer, 'foodweb editor has a directly visible consumer selector');
  assert.ok(consumer.children.some(option => option.value === 'fish_a'), 'consumer choices come from configured instances');
  assert.equal(consumer.value, 'fish_a', 'consumer selector stays synchronized with the selected module');
  app.el('node').value = 'fish_a'; app.el('node').onchange();
  const group = app.find(e => e.dataset.foodwebGroupSelect);
  assert.ok(group, 'fish foodweb exposes a PLAN diet group');
  group.value = 'PLAN';
  await group.listeners.change();
  const prey = app.find(e => e.dataset.foodwebTarget === 'PLAN');
  assert.ok(prey, 'diet row includes a target selector');
  const firstDietRow = app.find(e => e.dataset.foodwebRows === 'PLAN').children[0];
  const foodwebLabels = firstDietRow.children.map(field => field.children[0].textContent);
  assert.deepEqual(foodwebLabels, ['猎物目标', '后缀', '摄食清除率 (m3/gDW/d)', '肠道占据率', '操作'], 'diet fields have visible labels and group-specific units');
  const optionValues = prey.children.map(o => o.value);
  assert.deepEqual(optionValues, ['', 'phyto_a', 'zoo_a'], 'PLAN only offers enabled, registered plankton families');
  assert.equal(prey.value, 'phyto_a', 'existing diet is reconstructed from actual target references');
  prey.value = 'zoo_a';
  await prey.listeners.change();
  assert.match(app.find(e => e.dataset.foodwebStatus).textContent, /未保存/, 'changing a prey target visibly marks the selected group as unsaved');
  await app.find(e => e.dataset.foodwebReset).click();
  assert.doesNotMatch(app.find(e => e.dataset.foodwebStatus).textContent, /未保存/, 'restoring the saved group clears its unsaved indicator');
  const add = app.find(e => e.textContent === '增加 prey');
  await add.click();
  const rows = app.find(e => e.dataset.foodwebRows === 'PLAN');
  assert.equal(rows.children.length, 2, 'users can add multiple prey to a group');
  rows.children[1].children[0].children[1].value = 'zoo_a';
  const callsBeforeRestore = app.calls.length;
  await app.find(e => e.dataset.foodwebReset).click();
  const restoredRows = app.find(e => e.dataset.foodwebRows === 'PLAN');
  assert.equal(restoredRows.children.length, 1, 'restore removes staged prey rows');
  assert.equal(restoredRows.children[0].children[0].children[1].value, 'phyto_a', 'restore reloads the saved target');
  assert.equal(app.calls.length, callsBeforeRestore, 'restore changes only staged editor state and sends no request');
  await add.click();
  const stagedRows = app.find(e => e.dataset.foodwebRows === 'PLAN');
  stagedRows.children[1].children[0].children[1].value = 'zoo_a';
  const save = app.find(e => e.dataset.foodwebSave);
  await save.click();
  const tx = app.calls.filter(c => c.url === '/api/model/instances/transaction');
  assert.deepEqual(tx.map(c => c.options.body.mode), ['preview', 'apply']);
  const op = tx[0].options.body.operations[0];
  assert.equal(op.op, 'set_foodweb');
  assert.equal(op.name, 'fish_a');
  assert.equal(op.groups.PLAN.length, 2);
  assert.deepEqual(op.groups.PLAN[0], { target: 'phyto_a', suffix: 'W', clearance: 0.2, clearance_units: 'm3/gDW/d', gut_occupation: 0.7 });
  assert.equal(tx[1].options.body.preview_hash, 'foodweb-preview');
  assert.equal(app.calls.filter(c => c.url === '/api/ecology/network' && !c.options.method).length, 2, 'successful apply reloads the network');

  const zoo = setup();
  await zoo.window.loadEcologyNetwork();
  zoo.el('node').value = 'zoo_a'; zoo.el('node').onchange();
  zoo.find(e => e.textContent === '增加 prey').click();
  const zooTargets = zoo.find(e => e.dataset.foodwebTarget === 'prey');
  assert.deepEqual(zooTargets.children.map(o => o.value), ['', 'phyto_a'], 'zooplankton only offers plankton prey and excludes itself');
  const zooRows = zoo.find(e => e.dataset.foodwebRows === 'prey');
  zooRows.children[0].children[0].children[1].value = 'phyto_a';
  await zoo.find(e => e.dataset.foodwebSave).click();
  const zooTx = zoo.calls.filter(c => c.url === '/api/model/instances/transaction');
  assert.equal(zooTx[0].options.body.operations[0].op, 'set_foodweb');
  assert.equal(zooTx[0].options.body.operations[0].name, 'zoo_a');
  assert.equal(zooTx[0].options.body.operations[0].prey[0].target, 'phyto_a');

  const legacyConsumer=makeNode('cladocerans','wet/zooplankton',{nPrey:1,prey_suffix1:'',cClearPrey1:0.25,fGutOccPrey1:0.5},{prey_model1:'POM'});
  const legacy=setup({graph:{nodes:[legacyConsumer,makeNode('phyto_a','wet/phytoplankton'),makeNode('POM','wet/detritus')],edges:[]}});
  await legacy.window.loadEcologyNetwork();
  legacy.el('node').value='cladocerans'; legacy.el('node').onchange();
  const legacyRows=legacy.find(e=>e.dataset.foodwebRows==='prey');
  const legacySelect=legacyRows.children[0].children[0].children[1];
  assert.equal(legacySelect.value,'POM','configured legacy target remains selected');
  assert.match(legacySelect.children.find(o=>o.value==='POM').textContent,/已有配置.*族外/,'legacy option explains its origin');
  legacy.find(e=>e.textContent==='增加 prey').click();
  const stagedLegacy=legacy.find(e=>e.dataset.foodwebRows==='prey');
  const newSelect=stagedLegacy.children[1].children[0].children[1];
  assert.deepEqual(newSelect.children.map(o=>o.value),['','phyto_a'],'new rows retain family-filtered choices');
  newSelect.value='phyto_a';
  await legacy.find(e=>e.dataset.foodwebSave).click();
  const legacyTx=legacy.calls.filter(c=>c.url==='/api/model/instances/transaction');
  assert.deepEqual(legacyTx.map(c=>c.options.body.mode),['preview','apply'],'legacy target is not mistaken for an empty row');
  assert.deepEqual(legacyTx[0].options.body.operations[0].prey[0],{target:'POM',suffix:'',clearance:0.25,gut_occupation:0.5,lSi:false,clearance_units:'m3/gDW/d'},'the existing configuration is preserved in the transaction');

  const bad = setup({ reject: true });
  await bad.window.loadEcologyNetwork();
  bad.el('node').value = 'fish_a'; bad.el('node').onchange();
  await bad.find(e => e.dataset.foodwebSave).click();
  const rejected = bad.calls.filter(c => c.url === '/api/model/instances/transaction');
  assert.equal(rejected.length, 1, 'backend schema rejection never reaches apply');
  assert.match(bad.find(e => e.dataset.foodwebStatus).textContent, /registered state|UNKNOWN_PORT/i, 'the exact typed validation reason is shown');

  const unresolvedConsumer=makeNode('zoo_missing','wet/zooplankton',{nPrey:1},{prey_model1:'missing_prey/sDW'});
  const unresolved=setup({graph:{nodes:[unresolvedConsumer,makeNode('phyto_a','wet/phytoplankton')],edges:[]}});
  await unresolved.window.loadEcologyNetwork();
  const unresolvedPanel=unresolved.find(e=>e.dataset.foodwebUnresolvedPanel==='true');
  assert.ok(unresolvedPanel?.open,'an unresolved configured reference expands its own evidence panel');
  assert.match(unresolvedPanel.children[0].textContent,/1 条/,'the panel summary makes the unresolved count visible');
  const unresolvedRow=unresolved.find(e=>e.dataset.foodwebUnresolvedRow==='true');
  assert.deepEqual(unresolvedRow.children.map(cell=>cell.textContent),[
    'zoo_missing','prey_model1','missing_prey/sDW',
    '当前活动案例 YAML 中有此引用，但网络未返回对应的已解析实例边；目标状态/单位未在此视图核验。'
  ],'the audit table preserves the exact consumer, port, raw reference, and bounded resolution evidence');
  assert.ok(unresolved.find(e=>e.tagName==='caption'&&/C:\/cases\/lake-a/.test(e.textContent)),'the unresolved reference is tied to the active case source path');

  const sources=['cyanobacteria','diatoms','greens','POM'].map(name=>makeNode(name,name==='POM'?'wet/om_pool':'wet/phytoplankton'));
  const consumers=['cladocerans','copepods','zoobenthos'].map(name=>makeNode(name,name==='zoobenthos'?'wet/zoobenthos':'wet/zooplankton',{nPrey:4},Object.fromEntries(sources.map((source,index)=>[`prey_model${index+1}`,source.name]))));
  const graphNodes=[...sources,...consumers,makeNode('abiotic_water','wet/abiotic_water')];
  const graphEdges=consumers.flatMap(consumer=>sources.map((source,index)=>({source:source.name,target:consumer.name,port:`prey_model${index+1}`,reference:`${source.name}/sDW`})));
  graphEdges.push({source:'abiotic_water',target:'cladocerans',port:'oxygen_pool_water',reference:'abiotic_water/sO2W'});
  const layered=setup({graph:{nodes:graphNodes,edges:graphEdges},width:617});
  await layered.window.loadEcologyNetwork();
  await layered.el('view-foodweb').click();
  assert.ok(Number.parseFloat(layered.el('svg').style.width)>617,'narrow food-web view keeps the graph wider than the visible viewport when its layout requires it');
  assert.equal(layered.el('svg').parentElement.style.overflowX,'auto','narrow food-web graph is horizontally scrollable');
  const evidence=layered.el('network-evidence').textContent;
  assert.match(layered.el('foodweb-paths').textContent,/路径 0 条.*没有可验证的三节点配置链/,'a graph without consecutive configured dietary edges reports no chain');
  const emptyPathList=layered.el('foodweb-path-list');
  assert.ok(emptyPathList,'the food-web summary exposes a dedicated visual path list');
  assert.match(emptyPathList.children[0]?.textContent||'',/0 条.*没有连续的两条已解析饮食边/,'an empty Lake Luoma style graph visibly reports zero paths');
  assert.match(evidence,/引用 12 条/,'the summary counts only the twelve configured prey couplings, including POM');
  assert.match(evidence,/闭合三节点有向环 0 个/,'the case summary reports no fabricated three-node cycle');
  assert.match(evidence,/消费者之间的配置食性边 0 条/,'consumer-to-consumer relations remain explicitly absent');
  const labels=[];
  const visit=e=>{if(e?.tagName==='text'&&e?.attributes?.['data-foodweb-port'])labels.push(e.attributes['data-foodweb-port']);for(const child of e?.children||[])visit(child);};
  visit(layered.el('svg'));
  assert.equal(labels.length,12,'all actual port labels remain available on their corresponding paths');
  const compactLabels=[];
  const collectLabels=e=>{if(e?.tagName==='text'&&e?.attributes?.['data-foodweb-port'])compactLabels.push(e);for(const child of e?.children||[])collectLabels(child);};
  collectLabels(layered.el('svg'));
  const edgePaths=[];const collectPaths=e=>{if(e.tagName==='path'&&e.attributes['data-foodweb-edge'])edgePaths.push(e);for(const child of e?.children||[])collectPaths(child);};collectPaths(layered.el('svg'));
  assert.equal(edgePaths.length,12,'the food-web view preserves exactly the twelve configured dietary edges');
  const routeControls=edgePaths.map(path=>path.attributes.d.match(/ Q (-?[0-9.]+) (-?[0-9.]+)/)?.slice(1).join(','));
  assert.ok(routeControls.every(Boolean),'each configured edge has an explicit quadratic route');
  assert.ok(new Set(routeControls).size>1,'configured prey links fan through distinct route control points instead of converging at one canvas-center point');
  assert.ok(edgePaths.every(path=>path.attributes.tabindex==='0'&&path.attributes['aria-label'].includes(path.attributes['data-foodweb-port'])),'each exact prey-to-consumer edge and port remains keyboard-focusable and auditable');
  const relationRows=layered.find(e=>e.dataset.foodwebRelationsRows==='true');
  assert.ok(relationRows,'full relationships remain available in the accessible details table');
  assert.equal(relationRows.children.length,12,'the readable relation table retains all twelve configured edges');
  assert.ok(relationRows.children.every(row=>row.children.length===6&&row.children[4].textContent==='YAML 实例引用已解析；目标状态/单位未在此视图核验'),'each listed edge exposes source, direction, consumer, exact FABM port, resolution evidence, and cycle status');
  assert.ok(relationRows.children.some(row=>row.children.slice(0,5).map(cell=>cell.textContent).join('|')==='POM|→|cladocerans|prey_model4|YAML 实例引用已解析；目标状态/单位未在此视图核验'),'the exact POM relation, port, and evidence remain legible in the table');
  const tiers=new Map(),tierHeadings=[];
  const collect=e=>{const tier=e?.attributes?.['data-foodweb-tier'];if(tier){if(!tiers.has(tier))tiers.set(tier,[]);tiers.get(tier).push({name:e.attributes['aria-label'],xy:e.attributes.transform.match(/translate\(([-\d.]+) ([-\d.]+)\)/).slice(1).map(Number)});}const heading=e?.attributes?.['data-foodweb-tier-label'];if(heading)tierHeadings.push(heading);for(const child of e?.children||[])collect(child);};
  collect(layered.el('svg'));
  assert.deepEqual([...tiers.keys()].sort(),['level-0','level-1'],'only source-distance trophic levels are rendered');
  assert.equal(tiers.get('level-1').length,3,'all three configured consumers occupy the upper tier');
  assert.equal(tiers.get('level-0').length,4,'the four configured prey, including POM, occupy the base tier');
  assert.ok(tiers.get('level-1')[0].xy[1]<tiers.get('level-0')[0].xy[1],'consumer tier sits above the prey base');
  assert.deepEqual(tierHeadings.sort(),['level-0','level-1'],'only populated trophic level labels are rendered');

  const trophicNodes=[
    ...['cyanobacteria','diatoms','greens','POM'].map(name=>makeNode(name,name==='POM'?'wet/om_pool':'wet/phytoplankton')),
    ...['cladocerans','copepods','zoobenthos'].map(name=>makeNode(name,name==='zoobenthos'?'wet/zoobenthos':'wet/zooplankton',{nPrey:4},Object.fromEntries(['cyanobacteria','diatoms','greens','POM'].map((prey,index)=>[`prey_model${index+1}`,prey])))),
    makeNode('JuFish','wet/fish',{nPLAN:2},{PLANprey1:'copepods',PLANprey2:'cladocerans'}),
    makeNode('AdFish','wet/fish',{nBEN:1},{BENTprey1:'zoobenthos'}),
    makeNode('PiscFish','wet/fish',{nPISC:2},{PISCprey1:'JuFish',PISCprey2:'AdFish'}),
  ];
  const dietaryEdges=[];
  for(const consumer of trophicNodes.filter(n=>['wet/zooplankton','wet/zoobenthos'].includes(n.model)))
    for(const [port,reference] of Object.entries(consumer.coupling))dietaryEdges.push({source:reference,target:consumer.name,port,reference});
  for(const consumer of trophicNodes.filter(n=>n.model==='wet/fish'))
    for(const [port,reference] of Object.entries(consumer.coupling))dietaryEdges.push({source:reference,target:consumer.name,port,reference});
  const fourLevels=setup({graph:{nodes:trophicNodes,edges:dietaryEdges}});
  await fourLevels.window.loadEcologyNetwork();
  fourLevels.el('view-couplings').setAttribute('aria-pressed','true');fourLevels.el('view-foodweb').setAttribute('aria-pressed','false');
  assert.equal(fourLevels.el('view-couplings').attributes['aria-pressed'],'true','the path interaction is tested from the default all-couplings view');
  assert.equal(fourLevels.el('view-foodweb').attributes['aria-pressed'],'false','food-web view starts inactive before path selection');
  const verifiedPaths=fourLevels.el('foodweb-path-list').children.map(card=>card.children?.map(part=>part.textContent).join(' ')||card.textContent).join(' | ');
  assert.match(verifiedPaths,/cyanobacteria → cladocerans → JuFish/,'the actual graph derives the three-node chain from configured edges');
  assert.match(verifiedPaths,/cyanobacteria · prey_model1.*cladocerans · PLANprey2/,'each path segment exposes its YAML instance reference and consumer port');
  assert.match(fourLevels.el('foodweb-paths').textContent,/不等同于三角闭环、营养级或已验证摄食/,'chain wording remains distinct from scientific validation and closed cycles');
  const visiblePathList=fourLevels.el('foodweb-path-list');
  const relationRows4=fourLevels.find(e=>e.dataset.foodwebRelationsRows==='true');
  assert.ok(visiblePathList,'real dietary chains are rendered separately from the evidence paragraph');
  const targetPath=visiblePathList.children.find(card=>card.children[0]?.textContent==='cyanobacteria → cladocerans → JuFish');
  assert.ok(targetPath,'the real three-instance, two-edge Erken chain is prominent and readable');
  assert.match(targetPath.children.map(part=>part.textContent).join(' '),/cyanobacteria · prey_model1.*cladocerans · PLANprey2/,'both edges expose their exact YAML reference and consumer port');
  assert.equal(targetPath.dataset.foodwebPathEdges,'2','a three-node path is explicitly labeled as two configured edges');
  assert.equal(targetPath.attributes.role,'button','each configured path card is an accessible action');
  assert.equal(targetPath.attributes.tabindex,'0','path cards can receive keyboard focus');
  await targetPath.click();
  assert.equal(fourLevels.el('view-couplings').attributes['aria-pressed'],'false','path activation deactivates the all-couplings view');
  assert.equal(fourLevels.el('view-foodweb').attributes['aria-pressed'],'true','path activation switches to the food-web view');
  assert.equal(fourLevels.el('foodweb-three-layer').disabled,false,'food-web controls reflect the newly active view and its available layers');
  assert.equal(targetPath.attributes['aria-pressed'],'true','activating a path card exposes its selected state');
  const activeNodes=[],activeEdges=[];
  const collectActive=e=>{if(e?.attributes?.['data-foodweb-path-focused']==='true')activeNodes.push(e.attributes['aria-label']);if(e?.attributes?.['data-foodweb-path-edge-focused']==='true')activeEdges.push(`${e.attributes['data-foodweb-source']}→${e.attributes['data-foodweb-target']}`);for(const child of e?.children||[])collectActive(child);};
  collectActive(fourLevels.el('svg'));
  assert.deepEqual(activeNodes.sort(),['JuFish','cladocerans','cyanobacteria'].sort(),'activating a path highlights exactly its three configured instances');
  assert.deepEqual(activeEdges.sort(),['cyanobacteria→cladocerans','cladocerans→JuFish'].sort(),'activating a path highlights exactly its two configured edges');
  const activeRows=relationRows4.children.filter(row=>row.attributes['data-foodweb-path-focused']==='true');
  assert.deepEqual(activeRows.map(row=>`${row.children[0].textContent}→${row.children[2].textContent}`).sort(),['cyanobacteria→cladocerans','cladocerans→JuFish'].sort(),'the relationship table marks the same two configured rows');
  await targetPath.click();
  assert.equal(fourLevels.el('view-foodweb').attributes['aria-pressed'],'true','clearing selection by repeated activation keeps the food-web view active');
  assert.ok(!fourLevels.find(e=>e.attributes?.['data-foodweb-path-focused']==='true'),'activating the selected path again clears the graph focus');
  assert.ok(!relationRows4.children.some(row=>row.attributes['data-foodweb-path-focused']==='true'),'clearing the path removes table row emphasis');
  targetPath.listeners.keydown({key:'Enter',preventDefault(){}});
  assert.equal(targetPath.attributes['aria-pressed'],'true','Enter activates a focused path card');
  targetPath.listeners.keydown({key:'Escape',preventDefault(){}});
  assert.equal(targetPath.attributes['aria-pressed'],'false','Escape clears path focus while the card is focused');
  assert.equal(fourLevels.el('view-foodweb').attributes['aria-pressed'],'true','Escape clears path emphasis without switching away from the food-web view');
  assert.ok(!fourLevels.find(e=>e.attributes?.['data-foodweb-path-focused']==='true'),'Escape clears instance and edge emphasis');
  const pathCardCount=visiblePathList.children.length;
  await fourLevels.el('load').click();
  assert.equal(fourLevels.el('foodweb-path-list').children.length,pathCardCount,'refresh replaces the path cards without duplicating entries');
  assert.equal(fourLevels.el('foodweb-path-list').children.filter(card=>card.children?.[0]?.textContent==='cyanobacteria → cladocerans → JuFish').length,1,'refresh retains exactly one card for the same configured three-node path');
  const threeLayerToggle=fourLevels.el('foodweb-three-layer');
  assert.ok(threeLayerToggle,'users can open a clearly labeled three-layer filtered view while retaining the complete network');
  await threeLayerToggle.click();
  assert.equal(threeLayerToggle.attributes['aria-pressed'],'true','the three-layer filtered view announces its selected state');
  const subsetNodes=[],subsetEdges=[];
  const collectSubset=e=>{if(e?.attributes?.['data-foodweb-tier'])subsetNodes.push(e.attributes['aria-label']);if(e?.attributes?.['data-foodweb-edge'])subsetEdges.push([e.attributes['data-foodweb-source'],e.attributes['data-foodweb-target']]);for(const child of e?.children||[])collectSubset(child);};
  collectSubset(fourLevels.el('svg'));
  assert.equal(subsetNodes.length,9,'the filtered view shows only real dietary endpoints from layout levels 0–2');
  assert.equal(subsetEdges.length,15,'the filtered view contains only the 15 configured edges whose endpoints remain visible');
  assert.ok(!subsetEdges.some(([,target])=>target==='PiscFish'),'the two configured edges into the fourth-layer PiscFish are outside the three-layer subnetwork');
  assert.match(fourLevels.el('svg').children[1].children[0].textContent,/三层子网.*完整网络 17 条、4 个布局层.*15 条/,'the graph label distinguishes filtered subnetwork counts from full configuration counts');
  const filterNote=find(fourLevels.el('svg'),e=>e.attributes?.['data-foodweb-filter-note']==='true');
  assert.match(filterNote?.textContent||'',/未显示第4\+层.*JuFish → PiscFish.*AdFish → PiscFish/,'the filtered view explains the exact configured edges omitted from layer four');
  const featuredEdges=[];const collectFeatured=e=>{if(e?.attributes?.['data-foodweb-featured-path']==='true')featuredEdges.push(`${e.attributes['data-foodweb-source']}→${e.attributes['data-foodweb-target']}`);for(const child of e?.children||[])collectFeatured(child);};collectFeatured(fourLevels.el('svg'));
  assert.deepEqual(featuredEdges.sort(),['cyanobacteria→cladocerans','cladocerans→JuFish'].sort(),'the real cyanobacteria to cladocerans to JuFish route is highlighted as two exact edges');
  await threeLayerToggle.click();
  assert.equal(threeLayerToggle.attributes['aria-pressed'],'false','users can return to the complete configured network');
  const levelNodes=new Map(),levelLabels=[];
  const collectLevels=e=>{
    const level=e?.attributes?.['data-foodweb-tier'];
    if(level){if(!levelNodes.has(level))levelNodes.set(level,[]);levelNodes.get(level).push({name:e.attributes['aria-label'],x:Number(e.attributes.transform.match(/translate\(([-\d.]+) ([-\d.]+)\)/)[1])});}
    const label=e?.attributes?.['data-foodweb-tier-label'];if(label)levelLabels.push(label);
    for(const child of e?.children||[])collectLevels(child);
  };
  collectLevels(fourLevels.el('svg'));
  assert.deepEqual([...levelNodes.keys()].sort(),['level-0','level-1','level-2','level-3'],'the actual prey graph determines four longest-path trophic levels');
  assert.deepEqual([...levelNodes.values()].map(items=>items.length),[4,3,2,1],'the ten real configured instances occupy their graph-derived levels');
  for(const nodesAtLevel of levelNodes.values())for(let i=0;i<nodesAtLevel.length;i++)for(let j=i+1;j<nodesAtLevel.length;j++)
    assert.ok(Math.abs(nodesAtLevel[i].x-nodesAtLevel[j].x)>=144,`cards ${nodesAtLevel[i].name} and ${nodesAtLevel[j].name} do not overlap`);
  assert.equal(dietaryEdges.length,17,'the fixture represents all 17 actual resolved dietary couplings');
  assert.ok(relationRows4.children.every(row=>row.children.length===6&&row.children[4].textContent==='YAML 实例引用已解析；目标状态/单位未在此视图核验'),'each four-level relation keeps its explicit resolution evidence and cycle status');
  const actualRelationRows=relationRows4.children.map(row=>row.children.slice(0,4).map(cell=>cell.textContent).join('|'));
  assert.deepEqual(actualRelationRows.sort(),dietaryEdges.map(edge=>`${edge.source}|→|${edge.target}|${edge.port}`).sort(),'every drawn/audited relation matches one exact configured source, consumer and FABM port');
  const fourPaths=[];const collectFourPaths=e=>{if(e.tagName==='path'&&e.attributes['data-foodweb-edge'])fourPaths.push(e);for(const child of e?.children||[])collectFourPaths(child);};collectFourPaths(fourLevels.el('svg'));
  const renderedPorts=[];const collectPorts=e=>{if(e?.tagName==='text'&&e?.attributes?.['data-foodweb-port'])renderedPorts.push(e.textContent);for(const child of e?.children||[])collectPorts(child);};collectPorts(fourLevels.el('svg'));
  assert.equal(renderedPorts.length,17,'each actual path retains its exact port label');
  const portTexts=[];const collectPortTexts=e=>{if(e?.tagName==='text'&&e?.attributes?.['data-foodweb-port'])portTexts.push(e);for(const child of e?.children||[])collectPortTexts(child);};collectPortTexts(fourLevels.el('svg'));
  assert.ok(portTexts.every(label=>label.attributes.visibility==='hidden'),'dense labels stay hidden until the matching edge is hovered or focused');
  const firstPath=fourPaths[0],firstLabel=portTexts.find(label=>label.attributes['data-foodweb-port']===firstPath.attributes['data-foodweb-port']);
  firstPath.listeners.focus();assert.equal(firstLabel.attributes.visibility,'visible','keyboard focus reveals only the focused edge port label');firstPath.listeners.blur();assert.equal(firstLabel.attributes.visibility,'hidden','leaving the edge hides its label again');
  assert.deepEqual(fourPaths.map(path=>`${path.attributes['data-foodweb-source']}|${path.attributes['data-foodweb-target']}|${path.attributes['data-foodweb-port']}`).sort(),dietaryEdges.map(edge=>`${edge.source}|${edge.target}|${edge.port}`).sort(),'every interactive edge still matches a real source, consumer, and exact coupling port');
  const layerText=[];const collectLayerText=e=>{if(e?.attributes?.['data-foodweb-tier-label'])layerText.push(e.textContent);for(const child of e?.children||[])collectLayerText(child);};collectLayerText(fourLevels.el('svg'));
  assert.ok(layerText.some(text=>text.includes('配置层 1'))&&layerText.some(text=>text.includes('配置层 4'))&&layerText.every(text=>text.includes('未判定营养级')),'source-distance layout uses configuration-layer labels without asserting scientific trophic levels');
  const wideViewport=setup({graph:{nodes:trophicNodes,edges:dietaryEdges},width:1200});await wideViewport.window.loadEcologyNetwork();await wideViewport.el('view-foodweb').click();
  const viewportCanvasWidth=Number(wideViewport.el('svg').attributes.viewBox.split(' ')[2]);
  assert.ok(viewportCanvasWidth>=1200,'wide viewBox is at least as wide as the available desktop viewport');
  assert.equal(wideViewport.el('svg').style.width,`${viewportCanvasWidth}px`,'wide view fills its viewport without shrinking the graph canvas');
  const wideBase=[];const collectWideBase=e=>{if(e?.attributes?.['data-foodweb-tier']==='level-0')wideBase.push(Number(e.attributes.transform.match(/translate\(([-\d.]+)/)[1]));for(const child of e?.children||[])collectWideBase(child);};collectWideBase(wideViewport.el('svg'));
  assert.ok(Math.abs((Math.min(...wideBase)+Math.max(...wideBase))/2-viewportCanvasWidth/2)<1,'wide configuration-layer layout remains centered in its canvas');

  const controls=[],wideNodes=[...Array.from({length:8},(_,i)=>makeNode(`prey_${i}`,'wet/phytoplankton')),
    makeNode('consumer_a','wet/zooplankton'),makeNode('consumer_b','wet/zooplankton')];
  const wideEdges=wideNodes.slice(0,8).flatMap((prey,i)=>[
    {source:prey.name,target:'consumer_a',port:`prey_model${i+1}`,reference:prey.name},
    {source:prey.name,target:'consumer_b',port:`prey_model${i+1}`,reference:prey.name},
  ]);
  const wide=setup({graph:{nodes:wideNodes,edges:wideEdges},controls});await wide.window.loadEcologyNetwork();await wide.el('view-foodweb').click();
  const wideCanvasWidth=Number(wide.el('svg').attributes.viewBox.split(' ')[2]);assert.ok(wideCanvasWidth>900,'wide trophic layers expand the SVG viewBox instead of overlapping cards');
  assert.equal(controls.length,1,'graphic zoom controls are registered');controls[0].zoom(2);
  const wideCanvasHeight=Number(wide.el('svg').attributes.viewBox.split(' ')[3]);
  assert.equal(wide.el('svg').querySelector('#en-graph').attributes.transform,`translate(${-wideCanvasWidth/2} ${-wideCanvasHeight/2}) scale(2)`,'zoom on a dynamic-width graph remains anchored at its center');

  const cyclicGraph=setup({graph:{nodes:[makeNode('source','wet/phytoplankton'),makeNode('loop_a','wet/zooplankton'),makeNode('loop_b','wet/zooplankton'),makeNode('consumer','wet/fish'),makeNode('isolated','wet/phytoplankton')],edges:[
    {source:'source',target:'loop_a',port:'prey_model1',reference:'source/sDW'},
    {source:'loop_a',target:'loop_b',port:'prey_model1',reference:'loop_a/sDW'},
    {source:'loop_b',target:'loop_a',port:'prey_model1',reference:'loop_b/sDW'},
    {source:'loop_b',target:'consumer',port:'PLANprey1',reference:'loop_b/sDW'},
  ]}});
  await cyclicGraph.window.loadEcologyNetwork();await cyclicGraph.el('view-foodweb').click();
  const cyclicPathText=cyclicGraph.el('foodweb-path-list').children.map(card=>card.children?.map(part=>part.textContent).join(' ')||card.textContent).join(' | ');
  assert.match(cyclicPathText,/loop_a → loop_b → consumer/,'a real cycle can contain a distinct-node two-edge path');
  assert.doesNotMatch(cyclicPathText,/loop_a → loop_b → loop_a/,'paths that repeat the source instance are excluded even inside a cycle');
  const cycleNodes=[],cycleLabels=[];const collectCycles=e=>{if(e?.attributes?.['data-foodweb-tier'])cycleNodes.push([e.attributes['aria-label'],e.attributes['data-foodweb-tier']]);if(e?.attributes?.['data-foodweb-tier-label'])cycleLabels.push(e.attributes['data-foodweb-tier-label']);for(const child of e?.children||[])collectCycles(child);};collectCycles(cyclicGraph.el('svg'));
  assert.deepEqual(cycleNodes.sort(),[['consumer','level-2'],['loop_a','cycle'],['loop_b','cycle'],['source','level-0']].sort(),'SCC nodes are marked as cyclic and isolated instances receive no inferred tier');
  assert.ok(cycleLabels.includes('cycle-level-1'),'the cyclic component is honestly labeled as a mixed/cycle layer');

  const luoma=setup({graph:{nodes:[...sources,...consumers],edges:graphEdges},referenceGraph:{nodes:trophicNodes,edges:dietaryEdges}});
  await luoma.window.loadEcologyNetwork();await luoma.el('view-foodweb').click();
  const luomaThreeLayer=luoma.el('foodweb-three-layer');
  assert.equal(luomaThreeLayer.disabled,true,'a two-level active food web cannot be presented as an available three-layer subnetwork');
  assert.match(luoma.el('foodweb-paths').textContent,/0 条.*没有鱼类食性边/,'Luoma empty state states both zero verified paths and no configured fish dietary edge');
  assert.match(luoma.el('network-evidence').textContent,/闭合三节点有向环 0 个/,'Luoma evidence keeps its truthful zero-cycle count');
  assert.equal(luoma.find(e=>e.dataset.foodwebRelationsRows==='true').children.length,12,'the empty-path case retains all 12 exact dietary relations for audit');
  const sourceSelect=luoma.el('network-source');
  assert.ok(sourceSelect,'network can load a named read-only Erken config example without switching the active case');
  sourceSelect.value='erken_reference';await sourceSelect.listeners.change();
  assert.ok(luoma.calls.some(call=>call.url==='/api/ecology/network?source=erken_reference'),'Erken example uses the fixed read-only source endpoint');
  assert.equal(luoma.state.activeCasePath,'C:/cases/lake-a','reading the Erken network leaves Lake Luoma active');
  assert.match(luoma.el('network-evidence').textContent,/Erken.*配置.*示例.*非活动案例.*运行时摄食/,'the example is visibly separated from the active case and from validated feeding');
  assert.equal(luoma.el('foodweb-three-layer').disabled,false,'the three-layer filter becomes available when the read-only Erken config supports it');
  const examplePath=luoma.el('foodweb-path-list').children.find(card=>card.children?.[0]?.textContent==='cyanobacteria → cladocerans → JuFish');
  assert.ok(examplePath,'the read-only source renders the exact configured three-instance path');
  assert.match(examplePath.children.map(part=>part.textContent).join(' '),/cyanobacteria · prey_model1.*cladocerans · PLANprey2/,'the example exposes the original exact prey and consumer ports');
  assert.equal(luoma.el('node-editor').hidden,true,'read-only example hides the active-case editor');
  const exampleRows=luoma.find(e=>e.dataset.foodwebRelationsRows==='true').children;
  assert.equal(exampleRows.length,17,'read-only example retains the complete four-layer Erken dietary edge list');

  const denseSources=Array.from({length:5},(_,i)=>makeNode(`source_${i}`,'wet/phytoplankton'));
  const denseConsumers=Array.from({length:5},(_,i)=>makeNode(`consumer_${i}`,'wet/zooplankton'));
  const denseFish=Array.from({length:5},(_,i)=>makeNode(`fish_${i}`,'wet/fish'));
  const denseEdges=[
    ...denseSources.flatMap(source=>denseConsumers.map(consumer=>({source:source.name,target:consumer.name,port:'prey_model1',reference:`${source.name}/sDW`}))),
    ...denseConsumers.flatMap(consumer=>denseFish.map(fish=>({source:consumer.name,target:fish.name,port:'PLANprey1',reference:`${consumer.name}/sDW`})))
  ];
  const dense=setup({graph:{nodes:[...denseSources,...denseConsumers,...denseFish],edges:denseEdges}});
  await dense.window.loadEcologyNetwork();
  const denseList=dense.el('foodweb-path-list');
  assert.match(dense.el('foodweb-paths').textContent,/125 条/,'the path summary preserves the full count when initial rendering is paged');
  assert.equal(denseList.children.filter(card=>card.dataset.foodwebPathKey).length,24,'the initial DOM contains only the first 24 path cards');
  const morePaths=denseList.children.find(card=>card.dataset.foodwebPathMore==='true');
  assert.ok(morePaths&&morePaths.tagName==='button'&&morePaths.attributes['aria-label'].includes('125 条'),'the progressive expansion control is keyboard accessible and announces total paths');
  morePaths.click();
  assert.equal(dense.el('foodweb-path-list').children.filter(card=>card.dataset.foodwebPathKey).length,48,'expansion appends the next batch while retaining the previously rendered paths');
  assert.match(dense.el('foodweb-paths').textContent,/125 条/,'the full path count remains visible after expansion');

  console.log('ecology typed foodweb DOM behavior: family filtering, row editing, preview/apply, reload and rejection PASS');
  console.log('ecology layered evidence view: 12 configured edges including POM, visible port labels, zero three-node cycles PASS');
  console.log('ecology path list: full counts, 24-card initial render, keyboard-accessible progressive expansion PASS');
}
main().catch(error => { console.error(error); process.exitCode = 1; });
