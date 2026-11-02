const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {test}=require('node:test');
const sourcePath='3DWET/app/static/js/workflow_navigation.js';
function environment(){
 const body={classList:{values:new Set(),toggle(k,on){on?this.values.add(k):this.values.delete(k);},contains(k){return this.values.has(k);}}};
 const nodes={},docEvents={},groups=[],leaves=[];let active;
 function node(id){const attributes={},events={};const n={id,attributes,events,hidden:false,disabled:false,
  setAttribute(k,v){attributes[k]=String(v);},getAttribute(k){return attributes[k]??null;},removeAttribute(k){delete attributes[k];},
  addEventListener(k,f){events[k]=f;},focus(){active=n;},getClientRects(){return [{}];}};nodes[id]=n;return n;}
 for(const [group,pages] of Object.entries({
  'case-data':['dashboard','cases','preprocess','input','gridstudio'],
  configuration:['modules','ecology','parameters','initial','time'],
  'run-review':['run','system','map','viz2d','viz3d','vheat','timeseries','calibrate','autocal']
 })){
  const g=node(group);g.dataset={workflow:group};g.open=group==='project';groups.push(g);
  for(const page of pages){const n=node(page);n.dataset={page};n.closest=()=>g;leaves.push(n);}
 }
 const menu=node('menu');menu.querySelectorAll=s=>s.includes('data-workflow')?groups:leaves;
 menu.querySelector=s=>leaves.find(n=>s.includes(`"${n.dataset.page}"`));
 const sidebar=node('studio-navigation');sidebar.querySelectorAll=()=>leaves;sidebar.setAttribute('role','navigation');
 const toggle=node('studio-nav-toggle'),close=node('studio-nav-close'),backdrop=node('studio-nav-backdrop');
 const main=node('main');main.inert=false;active=toggle;
 const media={matches:true,addEventListener(){}};
 const window={matchMedia:query=>{media.query=query;return media;},addEventListener(){}};
 const document={body,getElementById:id=>nodes[id]||null,querySelector:s=>s==='.nav-menu'?menu:s==='.main-content'?main:null,
  addEventListener(k,f){docEvents[k]=f;},get activeElement(){return active;}};
 const context=vm.createContext({window,document,console});vm.runInContext(fs.readFileSync(sourcePath,'utf8'),context);
 return {window,groups,leaves,toggle,close,backdrop,main,sidebar,docEvents,document,body,media};
}
test('top-tool navigation opens only the matching ancestor and updates current page',()=>{
 const e=environment();e.window.StudioNavigation.activate('viz3d');
 assert.deepEqual(e.groups.filter(g=>g.open).map(g=>g.dataset.workflow),['run-review']);
 assert.equal(e.leaves.find(n=>n.dataset.page==='viz3d').getAttribute('aria-current'),'page');
 e.window.StudioNavigation.activate('initial');
 assert.deepEqual(e.groups.filter(g=>g.open).map(g=>g.dataset.workflow),['configuration']);
 assert.equal(e.leaves.find(n=>n.dataset.page==='viz3d').getAttribute('aria-current'),null);
});
test('ecology shortcut belongs to model configuration and becomes the current page',()=>{
 const e=environment();e.window.StudioNavigation.activate('ecology');
 assert.deepEqual(e.groups.filter(g=>g.open).map(g=>g.dataset.workflow),['configuration']);
 assert.equal(e.leaves.find(n=>n.dataset.page==='ecology').getAttribute('aria-current'),'page');
});
test('case-data pages remain inside the case-data workflow and unknown routes do not clear it',()=>{
 const e=environment();e.window.StudioNavigation.activate('cases');e.window.StudioNavigation.activate('unknown');
 assert.deepEqual(e.groups.filter(g=>g.open).map(g=>g.dataset.workflow),['case-data']);
});
test('narrow drawer traps focus, closes on Escape and restores the main content',()=>{
 const e=environment();e.toggle.events.click();
 assert.equal(e.toggle.getAttribute('aria-expanded'),'true');assert.equal(e.main.inert,true);
 assert.equal(e.sidebar.getAttribute('role'),'dialog');
 const last=e.leaves.at(-1);last.focus();let prevented=false;
 e.docEvents.keydown({key:'Tab',shiftKey:false,preventDefault(){prevented=true;}});
 assert.ok(prevented);assert.equal(e.document.activeElement,e.leaves[0]);
 e.docEvents.keydown({key:'Escape',preventDefault(){}});
 assert.equal(e.main.inert,false);assert.equal(e.toggle.getAttribute('aria-expanded'),'false');
 assert.equal(e.sidebar.getAttribute('role'),'navigation');assert.equal(e.document.activeElement,e.toggle);
});
test('selecting a leaf closes the drawer without stealing focus back to its trigger',()=>{
 const e=environment();e.toggle.events.click();e.window.StudioNavigation.activate('viz3d');
 assert.equal(e.main.inert,false);assert.equal(e.toggle.getAttribute('aria-expanded'),'false');
 assert.equal(e.document.activeElement,e.main,'focus must leave the now-hidden navigation');
});

test('short landscape viewports use the same controlled navigation as narrow phones',()=>{
 const e=environment();assert.equal(e.media.query,'(max-width: 720px), (max-width: 950px) and (max-height: 500px)');
});
