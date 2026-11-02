(function(root){
    'use strict';
    const prefetched=new Map();
    let operationGeneration=0;
    const sameIdentity=(a,b)=>a?.case===b?.case && a?.revision===b?.revision &&
        a?.outputRevision===b?.outputRevision &&
        a?.variable===b?.variable && Number(a?.level)===Number(b?.level) &&
        a?.rangeStart===b?.rangeStart && a?.rangeEnd===b?.rangeEnd;
    const normalizeCasePath=value=>String(value||'').replace(/\\/g,'/').replace(/\/+$/,'').toLocaleLowerCase();
    async function fetchCurrent({url,identity,isPlaying,isCurrent,endFrame,fetchResult,fetchBatch,refreshCase}){
        const activeAtStart=typeof isCurrent!=='function' || isCurrent();
        const operation=activeAtStart ? ++operationGeneration : operationGeneration;
        if(!/\/api\/results\/2d(?:\?|$)/.test(url)){
            if(activeAtStart && operation===operationGeneration)prefetched.clear();
            return fetchResult(url);
        }
        if(activeAtStart)for(const [cachedUrl,entry] of prefetched){
            if(!sameIdentity(entry.identity,identity))prefetched.delete(cachedUrl);
        }
        let data;
        const current=activeAtStart ? prefetched.get(url) : null;
        if(!activeAtStart){
            // A call that was stale before it began must not mutate shared
            // cache state: the same URL may already belong to a newer render.
            data=await fetchResult(url);
        }else if(current && sameIdentity(current.identity,identity)){
            prefetched.delete(url);
            data=await current.promise;
        }else{
            prefetched.delete(url);
            data=await fetchResult(url);
        }
        // A newer frame selection or explicit cache clear owns all later
        // mutations. An older request may finish, but it cannot touch the map.
        if(!activeAtStart || operation!==operationGeneration)return data;
        const canPrefetch=isCurrent?.() && isPlaying?.() && !data?.error && !data?.aborted;
        if(!canPrefetch){
            // A late old render may finish after a newer selection has already
            // populated the cache. Retire only this request's entries.
            for(const [cachedUrl,entry] of prefetched){
                if(sameIdentity(entry.identity,identity))prefetched.delete(cachedUrl);
            }
            return data;
        }
        const parsed=new URL(url,root.location?.href || 'http://localhost');
        const time=Number(parsed.searchParams.get('time'));
        const finalFrame=Number(endFrame);
        if(!Number.isFinite(finalFrame)){
            for(const [cachedUrl,entry] of prefetched){
                if(sameIdentity(entry.identity,identity))prefetched.delete(cachedUrl);
            }
            return data;
        }
        const makeUrl=future=>{
            const next=new URL(url,root.location?.href || 'http://localhost');
            next.searchParams.set('time',String(future));
            return next.pathname+next.search;
        };
        const timeFor=futureUrl=>Number(new URL(futureUrl,root.location?.href || 'http://localhost').searchParams.get('time'));
        const desired=[];
        if(Number.isInteger(time))for(let offset=1;offset<=2;offset++){
            const future=time+offset;
            if(future>finalFrame)break;
            desired.push(makeUrl(future));
        }
        let missing;
        if(fetchBatch && Number.isInteger(time)){
            const existingFuture=[...prefetched.entries()]
                .filter(([cachedUrl,entry])=>sameIdentity(entry.identity,identity) &&
                    Number.isInteger(timeFor(cachedUrl)) && timeFor(cachedUrl)>time && timeFor(cachedUrl)<=finalFrame)
                .sort((a,b)=>timeFor(a[0])-timeFor(b[0]));
            // Keep at most four future frames. Prime an empty window with one
            // four-frame request; refill with at most two frames once only two
            // remain, avoiding serialized startup requests under the server's
            // shared NetCDF read lock.
            const keep=existingFuture.slice(0,4).map(([cachedUrl])=>cachedUrl);
            for(const [cachedUrl] of prefetched){
                if(!keep.includes(cachedUrl))prefetched.delete(cachedUrl);
            }
            const retained=existingFuture.slice(0,4);
            const nextTime=retained.length ? timeFor(retained[retained.length-1][0])+1 : time+1;
            missing=[];
            const maxBatch=retained.length===0 ? 4 : (retained.length<=2 ? 2 : 0);
            for(let offset=0;offset<maxBatch;offset++){
                const future=nextTime+offset;
                if(future>finalFrame)break;
                const futureUrl=makeUrl(future);
                if(!prefetched.has(futureUrl))missing.push(futureUrl);
            }
        }else{
            for(const [cachedUrl,entry] of prefetched){
                if(!sameIdentity(entry.identity,identity) || !desired.includes(cachedUrl))prefetched.delete(cachedUrl);
            }
            missing=desired.filter(futureUrl=>!prefetched.has(futureUrl));
        }
        if(fetchBatch && missing.length){
            const batchPromise=Promise.resolve().then(async()=>{
                let batchIdentity={...identity};
                let batch=await fetchBatch({urls:[...missing],identity:{...batchIdentity}});
                if(batch?.error && /当前案例版本已变化/.test(batch.error) && refreshCase && isCurrent?.()){
                    const refreshed=await refreshCase();
                    if(isCurrent?.() && refreshed?.case_path && identity?.casePath &&
                        normalizeCasePath(refreshed.case_path)===normalizeCasePath(identity.casePath) &&
                        refreshed.case_generation!=null){
                        batchIdentity={...batchIdentity,serverCaseGeneration:refreshed.case_generation};
                        batch=await fetchBatch({urls:[...missing],identity:{...batchIdentity}});
                    }
                }
                if(batch && typeof batch==='object')batch._clientExpectedCaseGeneration=batchIdentity.serverCaseGeneration;
                return batch;
            })
                .catch(error=>({error:error?.message || '2D批量帧请求失败'}));
            for(const futureUrl of missing){
                const entry={url:futureUrl,identity:{...identity},promise:null};
                entry.promise=batchPromise.then(batch=>{
                    if(!batch || batch.error)return batch || {error:'2D批量帧响应为空'};
                    if(batch.case_path!=null && identity?.casePath!=null &&
                        normalizeCasePath(batch.case_path)!==normalizeCasePath(identity.casePath))
                        return {error:'案例版本已变化，请重新加载当前帧'};
                    const expectedGeneration=batch._clientExpectedCaseGeneration ?? identity?.serverCaseGeneration;
                    if(batch.case_generation!=null && expectedGeneration!=null &&
                        String(batch.case_generation)!==String(expectedGeneration))
                        return {error:'案例版本已变化，请重新加载当前帧'};
                    const time=new URL(futureUrl,root.location?.href || 'http://localhost').searchParams.get('time');
                    const frame=batch.frames?.[String(time)];
                    if(!frame || typeof frame!=='object')return {error:`批量结果缺少第 ${time} 帧`};
                    const result={...frame};
                    if(batch._clientTiming){
                        const count=Math.max(1,missing.length);
                        result._clientTiming={...batch._clientTiming,
                            requestMs:Number(batch._clientTiming.requestMs || 0)/count,
                            decodeMs:Number(batch._clientTiming.decodeMs || 0)/count,
                            batchRequestMs:Number(batch._clientTiming.requestMs || 0),
                            batchDecodeMs:Number(batch._clientTiming.decodeMs || 0),
                            batchSize:count};
                    }
                    if(batch.result_revision!=null)result._resultRevision=batch.result_revision;
                    return result;
                });
                entry.promise.catch(()=>undefined);
                prefetched.set(futureUrl,entry);
            }
        }else{
            for(const futureUrl of missing){
                const entry={url:futureUrl,identity:{...identity},promise:null};
                entry.promise=Promise.resolve().then(()=>fetchResult(futureUrl));
                entry.promise.catch(()=>undefined);
                prefetched.set(futureUrl,entry);
            }
        }
        return data;
    }
    root.Viz2DPlaybackPrefetch={fetchCurrent,clear:()=>{operationGeneration++;prefetched.clear();}};
})(typeof window!=='undefined'?window:globalThis);
