const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {test}=require('node:test');
const source=fs.readFileSync('3DWET/app/static/js/app.js','utf8');
const start=source.indexOf('const resultInventoryRequests = new Map();');
const end=source.indexOf('async function loadVariables()',start);

test('result inventory requests coalesce only while in flight and never cross case revisions',async()=>{
 assert.notEqual(start,-1,'inventory request helper is present');assert.notEqual(end,-1);
 const pending=[],state={activeCasePath:'case-a',caseRevision:1};let calls=0;
 const context=vm.createContext({state,api:()=>{calls++;return new Promise(resolve=>pending.push(resolve));}});
 vm.runInContext(source.slice(start,end)+'\nglobalThis.fetchInventoryForTest=fetchResultInventory;',context);
 const one=context.fetchInventoryForTest(),two=context.fetchInventoryForTest();
 assert.equal(calls,1,'concurrent callers share one request');
 pending[0]({ '2d':[], '3d':[], timesteps_2d:3 });
 assert.deepEqual(await Promise.all([one,two]),[
  { '2d':[], '3d':[], timesteps_2d:3 },{ '2d':[], '3d':[], timesteps_2d:3 }
 ]);
 const next=context.fetchInventoryForTest();assert.equal(calls,2,'settled results are not cached across later refreshes');
 state.activeCasePath='case-b';state.caseRevision=2;
 const other=context.fetchInventoryForTest();assert.equal(calls,3);
 pending[1]({ '2d':[], '3d':[], timesteps_2d:99 });
 assert.equal((await next).error,'案例已切换');
 pending[2]({ '2d':[], '3d':[], timesteps_2d:7 });
 assert.equal((await other).timesteps_2d,7);
});
