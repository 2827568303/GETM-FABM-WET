const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {test}=require('node:test');
const source=fs.readFileSync('3DWET/app/static/js/scientific_style.js','utf8');
const plain=x=>JSON.parse(JSON.stringify(x));
function load(storage){const c=vm.createContext({console,window:{localStorage:storage}});vm.runInContext(source,c);return c.window.ScientificStyle;}
const stops=[[0,'#000000'],[.25,'#ff0000'],[1,'#ffffff']];

test('positioned custom nodes interpolate actual distances and reverse their positions',()=>{
 const s=load();s.set('A','temp',{palette:'custom',stops});
 assert.equal(s.color(.125,s.get('A','temp')),'rgb(128,0,0)');
 assert.equal(s.color(.625,s.get('A','temp')),'rgb(255,128,128)');
 s.set('A','temp',{reverse:true});
 assert.equal(s.color(.875,s.get('A','temp')),'rgb(128,0,0)');
 const r=s.resolve({caseKey:'A',variable:'temp',min:0,max:10});
 assert.deepEqual(plain(r.colorscale),[[0,'rgb(255,255,255)'],[.75,'rgb(255,0,0)'],[1,'rgb(0,0,0)']]);
});

test('discrete classes retain exact boundaries instead of quantizing into a lookup table',()=>{
 const s=load();s.set('A','v',{palette:'custom',stops:[[0,'#000000'],[1,'#ffffff']],mapping:'discrete',classes:3});
 const c=s.get('A','v');
 assert.equal(s.color(1/3-1e-10,c),'rgb(43,43,43)');
 assert.equal(s.color(1/3,c),'rgb(128,128,128)');
 assert.equal(s.color(1,c),'rgb(213,213,213)');
 const r=s.resolve({caseKey:'A',variable:'v',min:0,max:3});
 assert.deepEqual(plain(r.colorscale),[[0,'rgb(43,43,43)'],[1/3,'rgb(43,43,43)'],[1/3,'rgb(128,128,128)'],[2/3,'rgb(128,128,128)'],[2/3,'rgb(213,213,213)'],[1,'rgb(213,213,213)']]);
});

test('missing values have an editable color and remain distinct from finite zero',()=>{
 const s=load();s.set('A','v',{nanColor:'#123456'});const c=s.get('A','v');
 for(const v of [NaN,null,undefined,Infinity])assert.equal(s.color(v,c),'#123456');
 assert.notEqual(s.color(0,c),'#123456');
});

test('invalid colormap edits are atomic and never write persistence',()=>{
 const records=new Map();let writes=0;const s=load({getItem:k=>records.get(k)??null,setItem:(k,v)=>{writes++;records.set(k,v);}});
 s.set('A','v',{palette:'custom',stops,mode:'custom',min:-2,max:3});const old=plain(s.get('A','v')),count=writes;
 for(const patch of [{reverse:1},{mapping:'log'},{classes:2.5},{classes:21},{nanColor:'url(secret)'},
  {stops:[[0,'#000000'],[.2,'#ffffff']]},{stops:[[0,'#000000'],[0,'#ff0000'],[1,'#ffffff']]},
  {stops:[[0,'#000000'],[.5,'rgb(1,2,3)'],[1,'#ffffff']]},{stops:Array.from({length:33},(_,i)=>[i/32,'#000000'])}]){
  assert.throws(()=>s.set('A','v',patch));assert.deepEqual(plain(s.get('A','v')),old);assert.equal(writes,count);
 }
});

test('node arrays from callers and returned settings cannot mutate stored color mappings',()=>{
 const s=load(),input=plain(stops);s.set('A','v',{palette:'custom',stops:input});input[1][1]='#000000';
 const saved=s.get('A','v');saved.stops[1][1]='#000000';
 assert.equal(s.get('A','v').stops[1][1],'#ff0000');
 const r=s.resolve({caseKey:'A',variable:'v',min:0,max:1});r.stops[1][0]=.9;
 assert.equal(s.get('A','v').stops[1][0],.25);
});

test('v1 settings migrate without losing locked limits and v2 retains custom nodes across reload',()=>{
 const records=new Map([['3dwet.scientific-style.v1',JSON.stringify({version:1,entries:[{caseKey:'A',variable:'temp',palette:'viridis',mode:'locked',min:12,max:18}]})]]);
 const storage={getItem:k=>records.get(k)??null,setItem:(k,v)=>records.set(k,v)};
 const s=load(storage);assert.equal(s.get('A','temp').min,12);assert.equal(s.get('A','temp').reverse,false);
 s.set('A','temp',{palette:'custom',stops,reverse:true,mapping:'discrete',classes:5,nanColor:'#112233'});
 const next=load(storage);assert.deepEqual(plain(next.get('A','temp')),plain(s.get('A','temp')));
 assert.equal(next.resolve({caseKey:'A',variable:'temp',min:0,max:30}).max,18);
 assert.equal(records.has('3dwet.scientific-style.v1'),true,'migration leaves old preferences recoverable');
});

test('color configuration export/import is versioned, atomic and scoped to the selected variable',()=>{
 const s=load();s.set('A','temp',{palette:'custom',stops,mode:'custom',min:-1,max:1,reverse:true});
 const payload=s.exportConfig('A','temp');assert.equal(payload.version,2);
 assert.equal(JSON.stringify(payload).includes('caseKey'),false);
 s.importConfig('B','salt',payload);assert.deepEqual(plain(s.get('B','salt')),plain(s.get('A','temp')));
 const previous=plain(s.get('B','salt'));
 for(const bad of [{...payload,version:999},{version:2,style:{}},{version:2,style:{...payload.style,stops:[[0,'#000000']]}},[],null]){
  assert.throws(()=>s.importConfig('B','salt',bad));assert.deepEqual(plain(s.get('B','salt')),previous);
 }
 assert.equal(s.get('B','temp').palette,'lake');
});

test('presets and custom schemes use the same shared scale API',()=>{
 const s=load();for(const palette of ['lake','viridis','cividis','blueRed']){
  s.set('A',palette,{palette,reverse:true});const r=s.resolve({caseKey:'A',variable:palette,min:-1,max:1});
  assert.equal(r.colorscale[0][1],s.color(0,r));assert.equal(r.colorscale.at(-1)[1],s.color(1,r));
 }
});
