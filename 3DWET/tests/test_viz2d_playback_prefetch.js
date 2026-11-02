const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const {test}=require('node:test');

const source=fs.readFileSync('3DWET/app/static/js/viz2d_playback_prefetch.js','utf8');
const pause=ms=>new Promise(resolve=>setTimeout(resolve,ms));

function env(){
  const requests=[];
  const context=vm.createContext({window:{},URL,fetch:async url=>{
    const time=Number(new URL(url,'http://localhost').searchParams.get('time'));
    requests.push({url,time,at:Date.now()});await pause(25);
    return {data:[[time]],timestep:time};
  }});
  vm.runInContext(source,context);
  return {helper:context.window.Viz2DPlaybackPrefetch,requests,fetchResult:url=>context.fetch(url)};
}

test('2D playback overlaps the next result request with drawing and reuses it once',async()=>{
  const e=env(),identity={case:'case-a',revision:1,variable:'temp',level:5};
  const first=await e.helper.fetchCurrent({url:'/api/results/2d?var=temp&time=0&level=5',identity,
    isPlaying:()=>true,isCurrent:()=>true,endFrame:2,fetchResult:e.fetchResult});
  const draw= pause(60);
  assert.equal(first.timestep,0);
  assert.ok(e.requests.some(item=>item.time===1),'frame 1 should be requested before frame 0 drawing completes');
  const prefetchStarted=e.requests.find(item=>item.time===1).at;
  await draw;
  assert.ok(prefetchStarted<Date.now(),'the next result request overlaps the current frame draw interval');
  await pause(60);
  const second=await e.helper.fetchCurrent({url:'/api/results/2d?var=temp&time=1&level=5',identity,
    isPlaying:()=>true,isCurrent:()=>true,endFrame:2,fetchResult:e.fetchResult});
  assert.equal(second.timestep,1);
  assert.equal(e.requests.filter(item=>item.time===1).length,1,'prefetched frame should be reused without duplicate request');
});

test('2D playback keeps exactly two future frames and reuses each once',async()=>{
  const e=env(),identity={case:'case-a',revision:1,outputRevision:2,variable:'temp',level:5};
  const options={identity,isPlaying:()=>true,isCurrent:()=>true,endFrame:3,fetchResult:e.fetchResult};
  await e.helper.fetchCurrent({...options,url:'/api/results/2d?var=temp&time=0&level=5'});
  await pause(35);
  assert.deepEqual(e.requests.map(item=>item.time).sort((a,b)=>a-b),[0,1,2],
    'initial render should request only current plus two future frames');
  await e.helper.fetchCurrent({...options,url:'/api/results/2d?var=temp&time=1&level=5'});
  await pause(35);
  assert.deepEqual(e.requests.map(item=>item.time).sort((a,b)=>a-b),[0,1,2,3],
    'next render should reuse frame 2 and extend the bounded lookahead by one frame');
  for(const time of [0,1,2,3])assert.equal(e.requests.filter(item=>item.time===time).length,1,
    `frame ${time} should be fetched exactly once`);
});

test('2D playback fetches four startup frames in one bounded batch and refills after two are consumed',async()=>{
  const e=env(),identity={case:'case-a',revision:1,outputRevision:2,variable:'temp',level:5};
  const batches=[];
  const fetchBatch=async ({urls,identity:batchIdentity})=>{
    batches.push({urls:Array.from(urls),identity:{...batchIdentity}});
    return {case_revision:batchIdentity.revision,output_revision:batchIdentity.outputRevision,
      _clientTiming:{requestMs:100,decodeMs:10},frames:Object.fromEntries(urls.map(url=>{
      const time=Number(new URL(url,'http://localhost').searchParams.get('time'));
      return [String(time),{data:[[time]],timestep:time}];
    }))};
  };
  const options={identity,isPlaying:()=>true,isCurrent:()=>true,endFrame:8,
    fetchResult:e.fetchResult,fetchBatch};
  await e.helper.fetchCurrent({...options,url:'/api/results/2d?var=temp&time=0&level=5'});
  assert.equal(batches.length,1,'two lookahead frames should share one batch request');
  assert.deepEqual(batches[0].urls.map(url=>Number(new URL(url,'http://localhost').searchParams.get('time'))),[1,2,3,4]);
  const first=await e.helper.fetchCurrent({...options,url:'/api/results/2d?var=temp&time=1&level=5'});
  const second=await e.helper.fetchCurrent({...options,url:'/api/results/2d?var=temp&time=2&level=5'});
  assert.deepEqual(first.data,[[1]]);
  assert.deepEqual(second.data,[[2]]);
  assert.equal(first._clientTiming.requestMs,25,'shared batch request time is amortized across returned frames');
  assert.equal(first._clientTiming.batchRequestMs,100,'full batch timing remains available for diagnostics');
  assert.deepEqual(batches[1].urls.map(url=>Number(new URL(url,'http://localhost').searchParams.get('time'))),[5,6],
    'when two ready frames remain, refill only the next two frames');
  assert.equal(e.requests.filter(item=>item.time>=1&&item.time<=4).length,0,
    'cached batch frames must not fall back to per-frame HTTP requests');
});

test('2D batch window holds at most four future frames and refills in one bounded two-frame request',async()=>{
  const e=env(),batches=[];
  const identity={case:'case-a',revision:1,outputRevision:2,variable:'temp',level:5};
  const fetchBatch=async ({urls})=>{
    const times=Array.from(urls,url=>Number(new URL(url,'http://localhost').searchParams.get('time')));
    batches.push(times);
    return {frames:Object.fromEntries(times.map(time=>[String(time),{data:[[time]],timestep:time}]))};
  };
  const options={identity,isPlaying:()=>true,isCurrent:()=>true,endFrame:8,fetchResult:e.fetchResult,fetchBatch};
  const render=async time=>e.helper.fetchCurrent({...options,
    url:`/api/results/2d?var=temp&time=${time}&level=5`});

  await render(0);
  assert.deepEqual(batches,[[1,2,3,4]],'prime the four-frame window with one bounded request');
  assert.equal(batches.flat().some(time=>time>4),false,'startup must not fetch beyond four future frames');
  await render(1);
  assert.equal(batches.length,1,'keep the existing four-frame window while it still has three frames');
  await render(2);
  assert.deepEqual(batches[1],[5,6],'refill after two frames have been consumed, using one two-frame batch');
  await render(3);
  assert.equal(batches.length,2,'do not refill while three future frames are already cached');
  await render(4);
  assert.deepEqual(batches[2],[7,8],'maintain a maximum four-frame lookahead in contiguous chunks');
  for(const times of batches){
    assert.ok(times.length>=1&&times.length<=4,'every HTTP batch must remain bounded to four frames');
    assert.ok(times.every((time,index)=>index===0||time===times[index-1]+1),'batch frames must be contiguous');
  }
});

test('2D four-frame lookahead never requests after the selected end frame',async()=>{
  const e=env(),batches=[],identity={case:'case-a',revision:1,outputRevision:2,variable:'temp',level:5};
  const fetchBatch=async ({urls})=>{
    const times=Array.from(urls,url=>Number(new URL(url,'http://localhost').searchParams.get('time')));
    batches.push(times);
    return {frames:Object.fromEntries(times.map(time=>[String(time),{data:[[time]],timestep:time}]))};
  };
  const options={identity,isPlaying:()=>true,isCurrent:()=>true,endFrame:3,fetchResult:e.fetchResult,fetchBatch};
  await e.helper.fetchCurrent({...options,url:'/api/results/2d?var=temp&time=0&level=5'});
  assert.deepEqual(batches,[[1,2,3]],'the startup batch is truncated at the selected endpoint');
  await e.helper.fetchCurrent({...options,url:'/api/results/2d?var=temp&time=1&level=5'});
  await e.helper.fetchCurrent({...options,url:'/api/results/2d?var=temp&time=2&level=5'});
  assert.equal(batches.flat().some(time=>time>3),false,'the inclusive selected end is a hard prefetch bound');
});

test('2D batch lookahead respects the inclusive end and invalidates rerun identities',async()=>{
  const e=env(),batches=[];
  const original={case:'case-a',revision:1,outputRevision:4,variable:'temp',level:5};
  const fetchBatch=async ({urls,identity})=>{
    batches.push({urls:[...urls],identity:{...identity}});
    return {frames:Object.fromEntries(urls.map(url=>{
      const time=Number(new URL(url,'http://localhost').searchParams.get('time'));
      return [String(time),{data:[[time+identity.outputRevision]],timestep:time}];
    }))};
  };
  const options={identity:original,isPlaying:()=>true,isCurrent:()=>true,endFrame:1,
    fetchResult:e.fetchResult,fetchBatch};
  await e.helper.fetchCurrent({...options,url:'/api/results/2d?var=temp&time=0&level=5'});
  assert.equal(batches.length,1);
  assert.deepEqual(batches[0].urls.map(url=>Number(new URL(url,'http://localhost').searchParams.get('time'))),[1]);
  const rerun={...original,outputRevision:5};
  const fresh=await e.helper.fetchCurrent({...options,identity:rerun,endFrame:1,
    url:'/api/results/2d?var=temp&time=1&level=5'});
  assert.deepEqual(fresh.data,[[1]],'old revision batch data must not be reused after rerun');
  assert.equal(batches[0].identity.outputRevision,4);
  assert.equal(e.requests.filter(item=>item.time===1).length,1,'new revision must fetch its own current frame');
});

test('a failed 2D batch is observable and a later frame request can recover',async()=>{
  const e=env(),identity={case:'case-a',revision:1,outputRevision:2,variable:'temp',level:5};
  let fail=true;
  const fetchBatch=async ()=>{if(fail)throw new Error('batch unavailable');return {frames:{'2':{data:[[2]],timestep:2}}};};
  const options={identity,isPlaying:()=>true,isCurrent:()=>true,endFrame:2,fetchResult:e.fetchResult,fetchBatch};
  await e.helper.fetchCurrent({...options,url:'/api/results/2d?var=temp&time=0&level=5'});
  const failed=await e.helper.fetchCurrent({...options,url:'/api/results/2d?var=temp&time=1&level=5'});
  assert.equal(failed.error,'batch unavailable');
  fail=false;
  const recovered=await e.helper.fetchCurrent({...options,url:'/api/results/2d?var=temp&time=1&level=5'});
  assert.deepEqual(recovered.data,[[1]]);
});

test('a late batch from a previous case cannot supply the new case selection',async()=>{
  const e=env(),oldIdentity={case:'case-a',revision:1,outputRevision:2,variable:'temp',level:5};
  const newIdentity={...oldIdentity,case:'case-b',revision:2};
  let releaseOld;
  const oldBatch=new Promise(resolve=>{releaseOld=resolve;});
  const fetchBatch=({urls,identity})=>identity.case==='case-a'?oldBatch.then(()=>({
    frames:Object.fromEntries(urls.map(url=>[String(new URL(url,'http://localhost').searchParams.get('time')),
      {data:[[999]],timestep:999}]))
  })):{frames:Object.fromEntries(urls.map(url=>[String(new URL(url,'http://localhost').searchParams.get('time')),
    {data:[[Number(new URL(url,'http://localhost').searchParams.get('time'))+10]],timestep:1}]))};
  await e.helper.fetchCurrent({url:'/api/results/2d?var=temp&time=0&level=5',identity:oldIdentity,
    isPlaying:()=>true,isCurrent:()=>true,endFrame:2,fetchResult:e.fetchResult,fetchBatch});
  await e.helper.fetchCurrent({url:'/api/results/2d?var=temp&time=0&level=5',identity:newIdentity,
    isPlaying:()=>true,isCurrent:()=>true,endFrame:2,fetchResult:e.fetchResult,fetchBatch});
  releaseOld();
  await pause(0);
  const current=await e.helper.fetchCurrent({url:'/api/results/2d?var=temp&time=1&level=5',identity:newIdentity,
    isPlaying:()=>true,isCurrent:()=>true,endFrame:2,fetchResult:e.fetchResult,fetchBatch});
  assert.deepEqual(current.data,[[11]],'new selection must consume only its own batch frame');
});

test('2D batch response from a different server case path is rejected',async()=>{
  const e=env(),identity={case:'case-a',casePath:'C:/cases/case-a',serverCaseGeneration:9,
    revision:3,outputRevision:7,variable:'temp',level:5};
  const options={identity,isPlaying:()=>true,isCurrent:()=>true,endFrame:1,fetchResult:e.fetchResult,
    fetchBatch:async ({urls})=>({case_path:'C:/cases/case-b',case_generation:9,
      frames:Object.fromEntries(urls.map(url=>[String(new URL(url,'http://localhost').searchParams.get('time')),
        {data:[[999]]}]))})};
  await e.helper.fetchCurrent({...options,url:'/api/results/2d?var=temp&time=0&level=5'});
  const response=await e.helper.fetchCurrent({...options,url:'/api/results/2d?var=temp&time=1&level=5'});
  assert.match(response.error,/案例版本已变化/);
});

test('2D batch response from an earlier server case generation is rejected',async()=>{
  const e=env(),identity={case:'case-a',casePath:'C:/cases/case-a',serverCaseGeneration:12,
    revision:3,outputRevision:7,variable:'temp',level:5};
  const options={identity,isPlaying:()=>true,isCurrent:()=>true,endFrame:1,fetchResult:e.fetchResult,
    fetchBatch:async ({urls})=>({case_path:'C:/cases/case-a',case_generation:11,
      frames:Object.fromEntries(urls.map(url=>[String(new URL(url,'http://localhost').searchParams.get('time')),
        {data:[[999]]}]))})};
  await e.helper.fetchCurrent({...options,url:'/api/results/2d?var=temp&time=0&level=5'});
  const response=await e.helper.fetchCurrent({...options,url:'/api/results/2d?var=temp&time=1&level=5'});
  assert.match(response.error,/案例版本已变化/);
});

test('2D playback respects the inclusive selected end and rejects stale selections',async()=>{
  const e=env(),identity={case:'case-a',revision:1,variable:'temp',level:5};
  await e.helper.fetchCurrent({url:'/api/results/2d?var=temp&time=1&level=5',identity,
    isPlaying:()=>true,isCurrent:()=>true,endFrame:1,fetchResult:e.fetchResult});
  await pause(35);
  assert.deepEqual(e.requests.map(item=>item.time),[1],'no prefetch beyond the selected end frame');

  await e.helper.fetchCurrent({url:'/api/results/2d?var=temp&time=0&level=5',identity,
    isPlaying:()=>true,isCurrent:()=>true,endFrame:2,fetchResult:e.fetchResult});
  const changed={case:'case-a',revision:1,variable:'salt',level:5};
  await e.helper.fetchCurrent({url:'/api/results/2d?var=salt&time=1&level=5',identity:changed,
    isPlaying:()=>true,isCurrent:()=>true,endFrame:2,fetchResult:e.fetchResult});
  assert.equal(e.requests.filter(item=>item.url.includes('var=salt')&&item.time===1).length,1,
    'a different variable must fetch its own current frame, not reuse stale prefetched output');
});

test('2D playback does not reuse a prefetched frame after the case or level changes',async()=>{
  for(const changed of [
    {case:'case-b',revision:2,variable:'temp',level:5},
    {case:'case-a',revision:1,variable:'temp',level:6},
  ]){
    const e=env(),original={case:'case-a',revision:1,variable:'temp',level:5};
    await e.helper.fetchCurrent({url:'/api/results/2d?var=temp&time=0&level=5',identity:original,
      isPlaying:()=>true,isCurrent:()=>true,endFrame:2,fetchResult:e.fetchResult});
    const url=`/api/results/2d?var=temp&time=1&level=${changed.level}`;
    await e.helper.fetchCurrent({url,identity:changed,isPlaying:()=>true,isCurrent:()=>true,
      endFrame:2,fetchResult:e.fetchResult});
    const expectedRequests=changed.case==='case-a'?1:2;
    assert.equal(e.requests.filter(item=>item.url===url).length,expectedRequests,
      `selection ${changed.case} / layer ${changed.level} must not reuse an incompatible prefetched frame`);
  }
});

test('2D playback does not reuse a prefetched frame after the same case produces a new output revision',async()=>{
  const e=env(),first={case:'case-a',revision:1,outputRevision:4,variable:'temp',level:5};
  await e.helper.fetchCurrent({url:'/api/results/2d?var=temp&time=0&level=5',identity:first,
    isPlaying:()=>true,isCurrent:()=>true,endFrame:2,fetchResult:e.fetchResult});
  const rerun={...first,outputRevision:5};
  const fresh=await e.helper.fetchCurrent({url:'/api/results/2d?var=temp&time=1&level=5',identity:rerun,
    isPlaying:()=>true,isCurrent:()=>true,endFrame:2,fetchResult:e.fetchResult});
  assert.deepEqual(fresh.data,[[1]]);
  assert.equal(e.requests.filter(item=>item.url.includes('time=1')).length,2,
    'same case/variable/layer must fetch the current run instead of consuming its previous-run prefetch');
});

test('2D playback discards prefetched frames when the selected playback range changes',async()=>{
  const e=env(),batches=[];
  const original={case:'case-a',revision:1,outputRevision:2,variable:'temp',level:5,rangeStart:0,rangeEnd:4};
  const fetchBatch=async ({urls})=>{
    batches.push(urls.map(url=>Number(new URL(url,'http://localhost').searchParams.get('time'))));
    return {frames:Object.fromEntries(urls.map(url=>{
      const time=Number(new URL(url,'http://localhost').searchParams.get('time'));
      return [String(time),{data:[[time]],timestep:time}];
    }))};
  };
  const options={identity:original,isPlaying:()=>true,isCurrent:()=>true,endFrame:4,
    fetchResult:e.fetchResult,fetchBatch};
  await e.helper.fetchCurrent({...options,url:'/api/results/2d?var=temp&time=0&level=5'});
  const changed={...original,rangeEnd:3};
  const next=await e.helper.fetchCurrent({...options,identity:changed,endFrame:3,
    url:'/api/results/2d?var=temp&time=1&level=5'});
  assert.equal(next.timestep,1);
  assert.equal(e.requests.filter(item=>item.time===1).length,1,
    'frame 1 from the old range must not satisfy the new range selection');
  assert.deepEqual(batches.map(times=>Array.from(times)),[[1,2,3,4],[2,3]],
    'the new range primes only its own remaining outputs');
});

test('a late old render cannot clear the new selection prefetch',async()=>{
  const e=env(),oldIdentity={case:'case-a',revision:1,outputRevision:2,variable:'temp',level:5};
  const newIdentity={...oldIdentity,variable:'salt'};
  let oldCurrent=true,releaseOld;
  const oldFrame=new Promise(resolve=>{releaseOld=resolve;});
  const fetchResult=async url=>{
    const time=Number(new URL(url,'http://localhost').searchParams.get('time'));
    e.requests.push({url,time,at:Date.now()});
    if(url.includes('var=temp')&&time===0)return oldFrame;
    return {data:[[time]],timestep:time};
  };
  const oldRender=e.helper.fetchCurrent({url:'/api/results/2d?var=temp&time=0&level=5',identity:oldIdentity,
    isPlaying:()=>true,isCurrent:()=>oldCurrent,endFrame:2,fetchResult});
  await pause(0);
  oldCurrent=false;
  await e.helper.fetchCurrent({url:'/api/results/2d?var=salt&time=0&level=5',identity:newIdentity,
    isPlaying:()=>true,isCurrent:()=>true,endFrame:2,fetchResult});
  releaseOld({data:[[99]],timestep:0});
  await oldRender;
  const fresh=await e.helper.fetchCurrent({url:'/api/results/2d?var=salt&time=1&level=5',identity:newIdentity,
    isPlaying:()=>true,isCurrent:()=>true,endFrame:2,fetchResult});
  assert.deepEqual(fresh.data,[[1]]);
  assert.equal(e.requests.filter(item=>item.url.includes('var=salt')&&item.time===1).length,1,
    'finishing the stale request must leave the active selection prefetch available');
});

test('a late frame request with the same selection cannot clear newer frame prefetches',async()=>{
  const e=env(),identity={case:'case-a',revision:1,outputRevision:2,variable:'temp',level:5};
  let oldCurrent=true,releaseOld;
  const oldFrame=new Promise(resolve=>{releaseOld=resolve;});
  const fetchResult=async url=>{
    const time=Number(new URL(url,'http://localhost').searchParams.get('time'));
    e.requests.push({url,time,at:Date.now()});
    if(time===0)return oldFrame;
    return {data:[[time]],timestep:time};
  };
  const oldRender=e.helper.fetchCurrent({url:'/api/results/2d?var=temp&time=0&level=5',identity,
    isPlaying:()=>true,isCurrent:()=>oldCurrent,endFrame:3,fetchResult});
  await pause(0);
  oldCurrent=false;
  await e.helper.fetchCurrent({url:'/api/results/2d?var=temp&time=1&level=5',identity,
    isPlaying:()=>true,isCurrent:()=>true,endFrame:3,fetchResult});
  releaseOld({data:[[0]],timestep:0});
  await oldRender;
  const next=await e.helper.fetchCurrent({url:'/api/results/2d?var=temp&time=2&level=5',identity,
    isPlaying:()=>true,isCurrent:()=>true,endFrame:3,fetchResult});
  assert.deepEqual(next.data,[[2]]);
  assert.equal(e.requests.filter(item=>item.time===2).length,1,
    'an older frame completion must not remove same-selection prefetches created by a newer operation');
});

test('a request already stale at entry cannot delete a cached frame at the same URL',async()=>{
  const e=env(),identity={case:'case-a',revision:1,outputRevision:2,variable:'temp',level:5};
  await e.helper.fetchCurrent({url:'/api/results/2d?var=temp&time=0&level=5',identity,
    isPlaying:()=>true,isCurrent:()=>true,endFrame:2,fetchResult:e.fetchResult});
  await pause(35);
  const frameUrl='/api/results/2d?var=temp&time=1&level=5';
  await e.helper.fetchCurrent({url:frameUrl,identity,isPlaying:()=>true,isCurrent:()=>false,
    endFrame:2,fetchResult:e.fetchResult});
  const active=await e.helper.fetchCurrent({url:frameUrl,identity,isPlaying:()=>true,isCurrent:()=>true,
    endFrame:2,fetchResult:e.fetchResult});
  assert.deepEqual(active.data,[[1]]);
  assert.equal(e.requests.filter(item=>item.url===frameUrl).length,2,
    'the stale-at-entry request must not delete the active prefetched result for its URL');
});

test('2D playback does not prefetch when the selected end frame is invalid',async()=>{
  const e=env(),identity={case:'case-a',revision:1,outputRevision:2,variable:'temp',level:5};
  await e.helper.fetchCurrent({url:'/api/results/2d?var=temp&time=0&level=5',identity,
    isPlaying:()=>true,isCurrent:()=>true,endFrame:Number.NaN,fetchResult:e.fetchResult});
  await pause(35);
  assert.deepEqual(e.requests.map(item=>item.time),[0],'invalid end frame must disable lookahead');
});

test('2D playback reports a rejected prefetched request and can recover on the next request',async()=>{
  const e=env(),identity={case:'case-a',revision:1,outputRevision:2,variable:'temp',level:5};
  let rejectNext=true;
  const fetchResult=async url=>{
    const time=Number(new URL(url,'http://localhost').searchParams.get('time'));
    e.requests.push({url,time,at:Date.now()});
    if(time===1&&rejectNext){rejectNext=false;throw new Error('prefetch failed');}
    return {data:[[time]],timestep:time};
  };
  await e.helper.fetchCurrent({url:'/api/results/2d?var=temp&time=0&level=5',identity,
    isPlaying:()=>true,isCurrent:()=>true,endFrame:2,fetchResult});
  await pause(0);
  await assert.rejects(e.helper.fetchCurrent({url:'/api/results/2d?var=temp&time=1&level=5',identity,
    isPlaying:()=>true,isCurrent:()=>true,endFrame:2,fetchResult}),/prefetch failed/);
  const recovered=await e.helper.fetchCurrent({url:'/api/results/2d?var=temp&time=1&level=5',identity,
    isPlaying:()=>true,isCurrent:()=>true,endFrame:2,fetchResult});
  assert.deepEqual(recovered.data,[[1]]);
  assert.equal(e.requests.filter(item=>item.time===1).length,2,'a rejected cache entry is removed before retry');
});

test('2D playback does not prefetch after its request becomes stale',async()=>{
  const e=env(),identity={case:'case-a',revision:1,variable:'temp',level:5};
  await e.helper.fetchCurrent({url:'/api/results/2d?var=temp&time=0&level=5',identity,
    isPlaying:()=>true,isCurrent:()=>false,endFrame:2,fetchResult:e.fetchResult});
  await pause(35);
  assert.deepEqual(e.requests.map(item=>item.time),[0],'stale output must not start a speculative next-frame request');
});

test('2D playback does not prefetch after an invalid current result',async()=>{
  const e=env(),identity={case:'case-a',revision:1,variable:'temp',level:5};
  const data=await e.helper.fetchCurrent({url:'/api/results/2d?var=temp&time=0&level=5',identity,
    isPlaying:()=>true,isCurrent:()=>true,endFrame:2,fetchResult:async url=>{
      e.requests.push({url,time:Number(new URL(url,'http://localhost').searchParams.get('time')),at:Date.now()});
      return {error:'missing frame'};
    }});
  await pause(5);
  assert.equal(data.error,'missing frame');
  assert.equal(e.requests.length,1,'invalid current output should not start an unnecessary next-frame request');
});

test('2D batch refreshes generation and retries once when the active path is unchanged',async()=>{
  const e=env(),identity={case:'case-a',casePath:'C:/cases/case-a/',serverCaseGeneration:9,
    revision:3,outputRevision:7,variable:'temp',level:5};
  const attempts=[];
  const fetchBatch=async ({urls,identity:batchIdentity})=>{
    attempts.push(batchIdentity.serverCaseGeneration);
    if(attempts.length===1)return {error:'当前案例版本已变化，请重新请求当前帧'};
    return {case_path:'c:/CASES/case-a',case_generation:10,
      frames:Object.fromEntries(urls.map(url=>[String(new URL(url,'http://localhost').searchParams.get('time')),{data:[[10]]}]))};
  };
  const refreshCase=async()=>({case_path:'C:/cases/case-a',case_generation:10});
  const options={identity,isPlaying:()=>true,isCurrent:()=>true,endFrame:1,fetchResult:e.fetchResult,fetchBatch,refreshCase};
  await e.helper.fetchCurrent({...options,url:'/api/results/2d?var=temp&time=0&level=5'});
  await pause(0);
  const response=await e.helper.fetchCurrent({...options,url:'/api/results/2d?var=temp&time=1&level=5'});
  assert.deepEqual(response.data,[[10]],JSON.stringify({response,attempts}));
  assert.deepEqual(attempts,[9,10],'the stale batch is retried once with the refreshed generation');
});

test('2D batch does not retry when refreshed active path differs',async()=>{
  const e=env(),identity={case:'case-a',casePath:'C:/cases/case-a',serverCaseGeneration:9,
    revision:3,outputRevision:7,variable:'temp',level:5};
  let batchCalls=0,refreshCalls=0;
  const options={identity,isPlaying:()=>true,isCurrent:()=>true,endFrame:1,fetchResult:e.fetchResult,
    fetchBatch:async()=>{batchCalls++;return {error:'当前案例版本已变化，请重新请求当前帧'};},
    refreshCase:async()=>{refreshCalls++;return {case_path:'C:/cases/case-b',case_generation:10};}};
  await e.helper.fetchCurrent({...options,url:'/api/results/2d?var=temp&time=0&level=5'});
  await pause(0);
  const response=await e.helper.fetchCurrent({...options,url:'/api/results/2d?var=temp&time=1&level=5'});
  assert.match(response.error,/案例版本已变化/);
  assert.equal(batchCalls,1,'a different active case must not receive a retry');
  assert.equal(refreshCalls,1);
});



