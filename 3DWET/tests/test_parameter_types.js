const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('3DWET/app/static/js/app.js','utf8');
const params=[{name:'enabled',value:true,type:'boolean'},{name:'code',value:'001',type:'string'},
  {name:'label',value:'name',type:'string',default_value:''},{name:'rate',value:1,type:'number'}];
const sent=[],warnings=[];
const elements={'params-list':{innerHTML:'',rows:[],appendChild(row){this.rows.push(row)}},'param-module-select':{value:'m'}};
let selected;
const ctx=vm.createContext({StudioIcons:{node:()=>({}),svg:()=>'<svg></svg>',setStatus:()=>{}},state:{fabmModules:[{name:'m',parameters:params}],currentParams:params},
  $:id=>elements[id]||{},document:{createElement:()=>({}),querySelector:()=>selected},window:{},
  api:async(u,o)=>{sent.push(o.body);return{success:true}},toast:(...args)=>warnings.push(args),confirmStudio:async()=>true,setTimeout:()=>{}});
vm.runInContext(source.slice(source.indexOf('function renderParams('),source.indexOf('// ── Time Settings')),ctx);
const input=(value,type)=>({value,dataset:{idx:'0',type},classList:{remove(){}}});
(async()=>{
  await ctx.saveParam(input('false','boolean'),'m','enabled');assert.equal(sent.pop().value,false);
  await ctx.saveParam(input('00123','string'),'m','code');assert.equal(sent.pop().value,'00123');
  await ctx.saveParam(input('','string'),'m','label');assert.equal(sent.pop().value,'');
  await ctx.saveParam(input('2.5','number'),'m','rate');assert.equal(sent.pop().value,2.5);
  for(const value of ['',' ','NaN','Infinity','abc']){await ctx.saveParam(input(value,'number'),'m','rate');assert.equal(sent.length,0);}
  await ctx.saveParam(input('0','boolean'),'m','enabled');assert.equal(sent.length,0);
  params[2].value='name';ctx.renderParams(params);
  assert.match(elements['params-list'].rows[0].innerHTML,/data-type="boolean"/);
  assert.match(elements['params-list'].rows[2].innerHTML,/data-has-default="true"/);
  selected=input('name','string');selected.dataset.default='';selected.dataset.hasDefault='true';
  await ctx.resetParam('m','label',0);assert.equal(sent.pop().value,'');
  console.log('parameter types: boolean/string/number save, invalid rejection, empty-string reset PASS');
})().catch(e=>{console.error(e);process.exitCode=1});
