const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {test}=require('node:test');
function env(){
 const nodes=new Map();
 const create=()=>({dataset:{},style:{},textContent:'',setAttribute(k,v){this[k]=v;},appendChild(child){child.parentElement=this;nodes.set(child.id,child);}});
 const canvasHost=create(),plotHost=create();nodes.set('viz2d-viewport',canvasHost);nodes.set('viz3d-plotly',{parentElement:plotHost});
 for(const kind of ['viz2d','viz3d']){nodes.set(kind+'-status',create());nodes.set(kind==='viz3d'?'viz3d-iso-var':'viz2d-var',{value:'temp'});}
 const context=vm.createContext({console,URL,URLSearchParams,window:{StudioI18n:{scientificText:(zh,en)=>en,t:value=>value}},state:{activeCase:'Lake A',activeCasePath:'A',caseRevision:1},
  document:{readyState:'loading',getElementById:id=>nodes.get(id),createElement:create,addEventListener(){}},clearInterval(){}});
 vm.runInContext(fs.readFileSync('3DWET/app/static/js/scientific_workspace.js','utf8'),context);
 return {w:context.window.ScientificWorkspace,nodes,context};
}
for(const kind of ['viz2d','viz3d'])test(`${kind}: fullscreen retains actual result identity and marks loading/failure as stale`,()=>{
 const e=env(),meta={variable:'temp',label:'Water temperature',units:'Celsius',date:'2026-DOY288 12:34:56',level:4,ve:kind==='viz3d'?20:null,
  detail:kind==='viz3d'?'Original grid 6×14×21 · Sampling stride 1×1×1':'',range:{min:15.149,max:15.150,mode:'locked',palette:'cividis'}};
 e.w.publish(kind,meta);const caption=e.nodes.get(kind+'-fullscreen-meta');
 assert.ok(caption,'metadata must be inside the actual fullscreen host');
 for(const token of ['Lake A','temp','Celsius',meta.date,'4','locked','15.149','15.15','cividis'])assert.ok(caption.textContent.includes(token),token);
 if(kind==='viz3d'){assert.match(caption.textContent,/20×/);assert.match(caption.textContent,/6×14×21/);}
 const original=caption.textContent;e.w.loading(kind);
 assert.equal(caption.textContent,original);assert.equal(caption.dataset.phase,'loading');assert.match(caption.dataset.message,/previous/i);
 e.w.failure(kind,'offline');assert.equal(caption.textContent,original);assert.equal(caption.dataset.phase,'error');assert.match(caption.dataset.message,/offline/);
 e.w.publish(kind,{...meta,date:'2026-DOY288 12:35:56'});
 assert.equal(caption.dataset.phase,'ready');assert.equal(caption.dataset.message,'');assert.match(caption.textContent,/12:35:56/);
});
test('the production 3D renderer marks the fullscreen retained image on an actual failed refresh',async()=>{
 const e=env(),graph=e.nodes.get('viz3d-plotly');
 const Plotly={newPlot:async()=>{graph._fullLayout={scene:{}};}};e.context.Plotly=Plotly;e.context.window.Plotly=Plotly;
 let payload={shape:[2,2,2],xc:[0,100],yc:[0,100],bottom:[[4,8],[4,8]],sigma:[-.75,-.25],
  data:[[[0,1],[0,1]],[[2,3],[2,3]]],min:0,max:3,units:'Celsius'};
 e.context.fetch=async()=>({json:async()=>payload});vm.runInContext(fs.readFileSync('3DWET/app/static/js/viz3d.js','utf8'),e.context);
 await e.context.render3DCloud('temp',0,22,{ve:20,timeLabel:'2026-DOY288 12:34:56'});
 const caption=e.nodes.get('viz3d-fullscreen-meta'),original=caption.textContent;
 payload={error:'controlled missing output'};await e.context.render3DCloud('temp',1,22,{ve:20,timeLabel:'2026-DOY288 12:35:56'});
 assert.equal(caption.dataset.phase,'error');assert.match(caption.dataset.message,/controlled missing output/);
 assert.equal(caption.textContent,original,'failure must retain the identified previous date and variable');
});
test('the first fullscreen request exposes loading and failure before any successful image exists',()=>{
 const e=env();e.w.loading('viz2d');let caption=e.nodes.get('viz2d-fullscreen-meta');
 assert.ok(caption);assert.equal(caption.dataset.phase,'loading');assert.match(caption.dataset.message,/loading model results/i);
 assert.doesNotMatch(caption.dataset.message,/previous|retaining/i);
 e.w.failure('viz2d','first request offline');caption=e.nodes.get('viz2d-fullscreen-meta');
 assert.equal(caption.dataset.phase,'error');assert.match(caption.dataset.message,/first request offline/);
 assert.doesNotMatch(caption.dataset.message,/retained|previous/i);
});
test('English fullscreen details are localized independently of an original Chinese case identity',async()=>{
 const e=env();e.context.state.activeCase='滇池';e.context.document.documentElement={};e.context.document.dispatchEvent=()=>{};
 e.context.CustomEvent=class{};e.context.fetch=async()=>({ok:true,json:async()=>JSON.parse(fs.readFileSync('3DWET/app/static/i18n/en.json','utf8'))});
 vm.runInContext(fs.readFileSync('3DWET/app/static/js/i18n.js','utf8'),e.context);await e.context.window.StudioI18n.setLocale('en-US');
 e.w.publish('viz3d',{variable:'raw_temp',label:'Water temperature',units:'Celsius',date:'地形预览',level:'全部层',ve:20,
  detail:'原网格 6×14×21 · 采样步长 1×1×1',range:{min:0,max:1,mode:'auto',palette:'lake'}});
 const caption=e.nodes.get('viz3d-fullscreen-meta');assert.match(caption.textContent,/滇池/);assert.match(caption.textContent,/raw_temp/);
 assert.doesNotMatch(caption.textContent,/原网格|采样步长|地形预览|全部层/);
 assert.match(caption.textContent,/Original grid 6×14×21/);assert.match(caption.textContent,/Sampling stride 1×1×1/);
 assert.equal(caption['data-i18n-skip'],'','raw case and variable identities must remain protected');
});
test('an empty field fullscreen caption exposes no data rather than implementation null limits',()=>{
 const e=env();e.w.publish('viz2d',{variable:'temp',label:'Water temperature',range:{min:null,max:null,noData:true,mode:'auto',palette:'lake'}});
 const text=e.nodes.get('viz2d-fullscreen-meta').textContent;
 assert.match(text,/no valid data/i);assert.doesNotMatch(text,/null|undefined|NaN/);
});
test('a first-loading caption moves into the actual fullscreen wrapper after Plotly registration',()=>{
 const e=env();e.w.setRenderState('viz3d','loading','Loading');const caption=e.nodes.get('viz3d-fullscreen-meta');
 const oldParent=caption.parentElement,newHost={appendChild(child){child.parentElement=this;}};
 e.nodes.get('viz3d-plotly').parentElement=newHost;
 e.w.publish('viz3d',{variable:'temp',label:'Water temperature',date:'2026-DOY288 12:34:56'});
 assert.notEqual(oldParent,newHost);assert.equal(caption.parentElement,newHost,'ViewControls wraps the graph only after its first Plotly render');
});
test('2D fullscreen includes the actual quantitative colour gradient and endpoint ticks',()=>{
 const e=env();vm.runInContext(fs.readFileSync('3DWET/app/static/js/scientific_style.js','utf8'),e.context);
 const style=e.context.window.ScientificStyle;style.set('A','temp',{palette:'cividis'});
 const range=style.resolve({caseKey:'A',variable:'temp',min:15.149,max:15.150});
 e.w.publish('viz2d',{variable:'temp',label:'Water temperature',units:'Celsius',range});
 const gradient=e.nodes.get('viz2d-fullscreen-gradient');assert.ok(gradient);
 assert.ok(gradient.style.background.includes(style.color(0,'cividis')));assert.ok(gradient.style.background.includes(style.color(1,'cividis')));
 assert.equal(gradient.parentElement,e.nodes.get('viz2d-fullscreen-meta'));
 assert.equal(e.nodes.get('viz2d-fullscreen-min').textContent,'15.149');assert.equal(e.nodes.get('viz2d-fullscreen-max').textContent,'15.15');
});
