const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {test}=require('node:test');
const source=fs.readFileSync('3DWET/app/static/js/app.js','utf8');
const begin=source.indexOf('function updateResultVariableSearch('),end=source.indexOf('\n// ── Dashboard',begin);
const helper=source.slice(begin,end);
function env(){
 const items=[
  {name:'temp',zh_name:'水温',en_name:'Water temperature',long_name_en:'temperature',units:'°C',meaning:'水体温度',meaning_en:'Water temperature field',ndim:4},
  {name:'NO3',zh_name:'硝酸盐',en_name:'Nitrate',units:'mmol N m-3',meaning:'溶解硝酸盐浓度',meaning_en:'Nitrate concentration',ndim:3},
  {name:'u',zh_name:'东西向速度',en_name:'Eastward velocity',units:'m s-1',meaning:'网格东向水流速度',ndim:3}
 ];
 const nodes=new Map(),select={value:'temp',options:items.map(v=>({value:v.name,textContent:`${v.zh_name} · ${v.name} [${v.units}]`})),replaceChildren(...options){this.options=options;}};
 const search={value:'',hidden:true,dataset:{},addEventListener(type,fn){this.listener=fn;}};
 const status={textContent:''};nodes.set('viz2d-var',select);nodes.set('viz2d-var-search',search);nodes.set('viz2d-var-search-status',status);
 const context=vm.createContext({window:{},state:{variables3d:items,variables2d:[]},$:id=>nodes.get(id)});vm.runInContext(helper,context);
 return {context,select,search,status};
}
test('search matches Chinese labels, English descriptions, variable codes, and units without changing selection',()=>{
 const e=env();e.context.updateResultVariableSearch('viz2d-var');assert.equal(e.search.hidden,true,'small inventories do not need a search field');
 e.context.state.variables3d=Array.from({length:60},(_,i)=>({name:`filler_${i}`,units:'kg m-3'})).concat(e.context.state.variables3d);
 e.select.options=Array.from(e.context.state.variables3d,v=>({value:v.name,textContent:v.zh_name||v.name,hidden:false}));
 e.context.updateResultVariableSearch('viz2d-var');assert.equal(e.search.hidden,false);
 for(const query of ['硝酸盐','Nitrate concentration','temp','°C']){
  e.search.value=query;e.search.listener();
  const expected=query==='硝酸盐'||query==='Nitrate concentration'?'NO3':'temp';
  assert.ok(e.select.options.some(o=>o.value===expected),`expected candidate for ${query}`);assert.equal(e.select.value,'temp');
 }
});
test('zero matches keep the selected option accessible and clearing search restores all values',()=>{
 const e=env();e.context.state.variables3d=Array.from({length:60},(_,i)=>({name:`filler_${i}`,units:'kg m-3'})).concat(e.context.state.variables3d);
 e.select.options=Array.from(e.context.state.variables3d,v=>({value:v.name,textContent:v.zh_name||v.name,hidden:false}));
 e.context.updateResultVariableSearch('viz2d-var');
 e.search.value='definitely-no-match';e.search.listener();
 assert.match(e.status.textContent,/没有匹配项/);assert.deepEqual(e.select.options.map(o=>o.value),['temp'],'the current option stays in the native list while other options are removed');
 e.search.value='';e.search.listener();assert.equal(e.select.options.length,63);assert.equal(e.select.value,'temp');
});
