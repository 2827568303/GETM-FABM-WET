// viz3d.js — Plotly 3D visualization module for 3DWET.
// Loaded on every page (small file), Plotly itself is vendored locally (index.html).
// Functions are called from the main app.js when the viz3d page is shown.
//
// 渲染方式（viz3d-iso-render 下拉切换）：
//   1) waterbody  ——【默认】实际湿网格湖盆 + 半透明水面 + 湖岸边界；
//                    可选择变量单层或叠层覆盖，垂向比例自动适配或明确指定。
//   2) isosurface —— 物理 sigma 网格等值面（三角网格，较重）
//   3) cloud      —— 点云（最快，逐点着色，但看不出"实体水体"感）
//   4) surface2d  —— 把 2D 场作为 3D 表面
//
// 所有渲染带令牌防重入 + 加载提示，避免快速切换时页面卡死。

const VIZ3D = {
    plotlyReady: () => typeof window.Plotly !== 'undefined',
    // Color palette for water quality fields
    colorScale: [[0,'#75e3d7'],[0.2,'#58d2e2'],[0.4,'#39b5e7'],[0.6,'#2b91df'],[0.8,'#236bd2'],[1,'#173fbd']],
    // 湖底/深度配色（浅→深）
    depthScale: [
        [0, '#75e3d7'], [0.15, '#58d2e2'], [0.35, '#39b5e7'],
        [0.6, '#2b91df'], [0.8, '#236bd2'], [1, '#173fbd']
    ],
    layout: {
        paper_bgcolor: '#f7fafb',
        plot_bgcolor: '#f7fafb',
        font: { family: 'Segoe UI, Microsoft YaHei, sans-serif', size: 11, color: '#435661' },
        scene: {
            // Use free orbit by default. Plotly's turntable mode constrains
            // pitch and can prevent looking below the basin.
            dragmode: 'orbit',
            xaxis: { title: 'X 坐标 (m)', gridcolor: '#dce4e8', showgrid:false, showline:true, linecolor:'#9aaeb9', ticks:'outside', zeroline: false, showbackground: false, showspikes:false, nticks:5, tickfont:{size:10} },
            yaxis: { title: 'Y 坐标 (m)', gridcolor: '#dce4e8', showgrid:false, showline:true, linecolor:'#9aaeb9', ticks:'outside', zeroline: false, showbackground: false, showspikes:false, nticks:5, tickfont:{size:10} },
            zaxis: { title: '水深 (m)', gridcolor: '#dce4e8', showgrid:false, showline:true, linecolor:'#9aaeb9', ticks:'outside', zeroline: false, showbackground: false, showspikes:false, tickfont:{size:10} },
            bgcolor: '#f7fafb',
            // The fitted scene area controls initial framing. Once the user
            // gestures, their camera is saved and reused by viz3dPlot.
            // A lower oblique view gives the water surface and basin walls
            // enough separation to read as a volume at first glance.
            camera: { eye: { x: 0.8525, y: -0.9625, z: 0.82 }, projection:{type:'orthographic'} },
            aspectmode: 'data',
        },
        margin: { l: 8, r: 105, t: 76, b: 52 },
        legend: { orientation:'h',x:0.02,y:-0.02,xanchor:'left',yanchor:'top',
            font: { size: 10, color: '#435661' },bgcolor:'rgba(255,255,255,0.85)' },
        hoverlabel:{bgcolor:'#ffffff',bordercolor:'#b8cbd0',font:{color:'#304b59',size:12}},
    }
};

// 渲染令牌：避免快速切换时多次渲染叠加导致页面卡死
let _viz3dToken = 0;
let _viz3dCamera = null;
let _viz3dCameraCase = null;
let _viz3dActiveCaseIdentity = null;
let _viz3dCameraAzimuth = Math.atan2(-0.9625,0.8525);
const _viz3dPrefetched3DSurfaces=new Map();
const _viz3dLakeGeometryCache=new Map();
const _viz3dLakeStaticTraceCache=new Map();
const _viz3dStaticGeometryCache=new Map();
const _viz3dTranslatedTextCache=new Map();
const VIZ3D_TRANSLATED_TEXT_CACHE_LIMIT=512;
let _viz3dSectionIndicatorToken = 0;
let _viz3dIndicatorQueue = Promise.resolve();
const _viz3dTrace=typeof window!=='undefined' && window.location?.search?.includes('camera-trace=1');
const viz3dNow=()=>window.performance?.now?.() ?? Date.now();
function viz3dTrace(phase,container,request,extra={}) {
    if(_viz3dTrace)console.debug('[3DWET camera] '+JSON.stringify({phase,time:request?.timestep,
        graph:container?.id,layout:container?._fullLayout?.scene?.camera,cached:_viz3dCamera,...extra}));
}

function viz3dCaseIdentity() {
    // app.js uses a lexical state, while independent integrations may expose it
    // on window. A revision also detects reloading the same case path.
    const s=typeof state !== 'undefined' ? state : window.state;
    return {revision:s?.caseRevision,outputRevision:s?.outputRevision || 0,name:s?.activeCase,path:s?.activeCasePath};
}
function viz3dSyncCaseIdentity(identity) {
    const key=JSON.stringify([identity?.revision,identity?.path,identity?.name]);
    if(_viz3dActiveCaseIdentity===null) {_viz3dActiveCaseIdentity=key;return;}
    if(_viz3dActiveCaseIdentity===key)return;
    _viz3dActiveCaseIdentity=key;
    ++_spatialSectionToken;
    const section=document.getElementById('viz3d-section-plot');
    if(section) {
        window.Plotly?.purge?.(section);
        section._viz3dLastPlot=null;
        section._fullLayout=null;
        section._viz3dStatus={phase:'empty',message:'案例已切换，请生成剖面',stale:false,displayed:null,requested:null};
        if(section.dataset) {section.dataset.renderPhase='empty';section.dataset.stale='false';}
        section.innerHTML='';
    }
    const status=document.getElementById('viz3d-section-status') || section?._viz3dStatusElement;
    if(status) {
        status.id='viz3d-section-status';
        status.textContent='案例已切换，请生成剖面';
        if(status.dataset)status.dataset.phase='empty';
    }
}
if(typeof window!=='undefined') window.clearViz3dPlaybackPrefetch=()=>_viz3dPrefetched3DSurfaces.clear();
function invalidateScientific3D(message) {
    // A rejected selection must retire requests just like a renderable one.
    ++_viz3dToken;
    ++_spatialSectionToken;
    ++_viz3dSectionIndicatorToken;
    const container=document.getElementById('viz3d-plotly');
    if(container) container._viz3dMainView=null;
    if(message) viz3dStatus(container,'error',message);
}
if(typeof window!=='undefined') window.invalidateScientific3D=invalidateScientific3D;
function viz3dBegin(container,varName,timestep,opts={},section=false) {
    const identity=viz3dCaseIdentity();
    viz3dSyncCaseIdentity(identity);
    const key=opts.caseKey ?? identity.path ?? identity.name ?? '';
    if(!section && _viz3dCameraCase!==null && key!==_viz3dCameraCase) _viz3dCamera=null;
    if(!section) _viz3dCameraCase=key;
    if(!section) {
        container._viz3dMainView=null;
        // Retire pending section selections. The main draw replaces its traces;
        // deleting a trace here would reset a live orbit to Plotly's old layout.
        ++_viz3dSectionIndicatorToken;
    }
    return {container,identity,key,varName,timestep,opts,section,
        token:section ? ++_spatialSectionToken : ++_viz3dToken,
        playbackPerf:!section ? window.PlaybackPerformance?.begin('viz3d',timestep,
            document.getElementById('viz3d-speed')?.value,window.ScientificWorkspace?.isPlaying?.('viz3d')) : null};
}
function viz3dCurrent(request) {
    if(!request) return true;
    const now=viz3dCaseIdentity(),old=request.identity;
    return request.token===(request.section ? _spatialSectionToken : _viz3dToken)
        && now.revision===old.revision && now.outputRevision===old.outputRevision
        && now.path===old.path && now.name===old.name;
}
async function viz3dTimedFetch(url,request) {
    const startedAt=viz3dNow();
    const response=await fetch(url);
    if(request && !viz3dCurrent(request))return null;
    const receivedAt=viz3dNow();
    const data=await response.json();
    if(data && typeof data==='object' && !Array.isArray(data))data._clientTiming={
        requestMs:receivedAt-startedAt,decodeMs:viz3dNow()-receivedAt};
    return data;
}
const VIZ3D_STATIC_GEOMETRY_FIELDS=['shape','full_shape','sampling_stride','x','y','z','layer_indices','total_layers',
    'coordinate_mode','coordinate_units','xc','yc','sigma','bottom','dry_mask','display_topology',
    'display_topology_status','display_topology_error','land_elevation'];
function viz3dStaticGeometryContext(url,request) {
    if(!request || !/\/api\/results\/3d_surface(?:\?|$)/.test(url))return null;
    const parsed=new URL(url,window.location?.href || 'http://localhost');
    const cacheKey=JSON.stringify([request.identity?.path,request.identity?.name,request.identity?.revision,request.identity?.outputRevision,
        request.varName,parsed.searchParams.get('target'),parsed.searchParams.get('level'),parsed.searchParams.get('layer_only')]);
    return {parsed,cacheKey,entry:_viz3dStaticGeometryCache.get(cacheKey)};
}
function viz3dStaticGeometryUrl(url,request) {
    const context=viz3dStaticGeometryContext(url,request);
    if(context?.entry?.serverKey)context.parsed.searchParams.set('static_key',context.entry.serverKey);
    return context?context.parsed.pathname+context.parsed.search:url;
}
function viz3dMergeStaticGeometry(data,url,request) {
    const context=viz3dStaticGeometryContext(url,request);
    if(!context || !data?.static_geometry_key)return data;
    const hasStatic=VIZ3D_STATIC_GEOMETRY_FIELDS.some(name=>Object.prototype.hasOwnProperty.call(data,name));
    if(hasStatic) {
        const payload={};
        for(const name of VIZ3D_STATIC_GEOMETRY_FIELDS)if(Object.prototype.hasOwnProperty.call(data,name))payload[name]=data[name];
        _viz3dStaticGeometryCache.set(context.cacheKey,{serverKey:data.static_geometry_key,payload});
        while(_viz3dStaticGeometryCache.size>6)_viz3dStaticGeometryCache.delete(_viz3dStaticGeometryCache.keys().next().value);
    } else if(context.entry?.serverKey===data.static_geometry_key) {
        Object.assign(data,context.entry.payload);
    }
    return data;
}
async function viz3dFetch(request,url) {
    const prefetched=_viz3dPrefetched3DSurfaces.get(url);
    let data;
    if(prefetched && prefetched.key===request?.key &&
            prefetched.identity?.revision===request?.identity?.revision &&
            prefetched.identity?.outputRevision===request?.identity?.outputRevision &&
            prefetched.identity?.path===request?.identity?.path && prefetched.identity?.name===request?.identity?.name) {
        _viz3dPrefetched3DSurfaces.delete(url);
        data=await prefetched.promise;
    } else {
        data=await viz3dTimedFetch(viz3dStaticGeometryUrl(url,request),request);
    }
    if(!viz3dCurrent(request)) return null;
    if(data?.static_geometry_key) {
        const merged=viz3dMergeStaticGeometry(data,url,request);
        const required=['bottom','xc','yc','shape'];
        if(required.some(name=>!Object.prototype.hasOwnProperty.call(merged,name))) {
            // Cache miss or a changed source revision: request one full frame
            // before rendering rather than inventing geometry from stale data.
            data=await viz3dTimedFetch(url,request);
            if(!viz3dCurrent(request))return null;
            data=viz3dMergeStaticGeometry(data,url,request);
        } else data=merged;
    }
    if(data?._clientTiming){
        window.PlaybackPerformance?.stage(request?.playbackPerf,'request',data._clientTiming.requestMs);
        window.PlaybackPerformance?.stage(request?.playbackPerf,'decode',data._clientTiming.decodeMs);
    }
    if(request)request._assemblyStartedAt=viz3dNow();
    if(!request?.section)viz3dPrefetchNext3DSurface(request,url);
    return data;
}
function viz3dPrefetchNext3DSurface(request,url) {
    if(!/\/api\/results\/3d_surface(?:\?|$)/.test(url) ||
            !window.ScientificWorkspace?.isPlaying?.('viz3d') || !viz3dCurrent(request))return;
    const timeMatch=url.match(/([?&]time=)(\d+)/);
    if(!timeMatch)return;
    const nextTime=Number(timeMatch[2])+1;
    const selectedEnd=document.getElementById('viz3d-play-end')?.value;
    const lastFrame=Number(selectedEnd!==undefined && selectedEnd!==''
        ? selectedEnd : document.getElementById('viz3d-time-slider')?.max);
    const desired=[];
    // Erken playback measurements show request + JSON decode latency can span
    // several 12 fps frame intervals. Keep a bounded four-frame window so
    // those real output requests overlap rendering without skipping frames.
    for(let offset=0;offset<4;offset++) {
        const time=nextTime+offset;
        if(Number.isFinite(lastFrame) && time>lastFrame)break;
        desired.push(url.replace(timeMatch[0],`${timeMatch[1]}${time}`));
    }
    const sameIdentity=entry=>entry.key===request.key &&
        entry.identity?.revision===request.identity?.revision && entry.identity?.path===request.identity?.path &&
        entry.identity?.outputRevision===request.identity?.outputRevision && entry.identity?.name===request.identity?.name;
    // A seek, case switch, variable change, or playback-range change retires
    // obsolete lookahead requests. At most four future frames are retained.
    for(const [cachedUrl,entry] of _viz3dPrefetched3DSurfaces) {
        if(!sameIdentity(entry) || !desired.includes(cachedUrl))_viz3dPrefetched3DSurfaces.delete(cachedUrl);
    }
    for(const nextUrl of desired) {
        const cached=_viz3dPrefetched3DSurfaces.get(nextUrl);
        if(cached && sameIdentity(cached))continue;
        const entry={url:nextUrl,key:request.key,identity:request.identity,promise:null};
        entry.promise=viz3dTimedFetch(viz3dStaticGeometryUrl(nextUrl,request),null);
        // A prefetch may fail after playback is paused or the user changes cases.
        // Keep it observed without changing the next foreground request's error path.
        entry.promise.catch(()=>undefined);
        _viz3dPrefetched3DSurfaces.set(nextUrl,entry);
    }
}
function viz3dStatus(container,phase,message,request) {
    if(!container || !viz3dCurrent(request)) return;
    let previous=container._viz3dLastPlot;
    if(phase!=='ready' && request && previous && previous.caseKey!==request.key) {
        window.Plotly?.purge?.(container);
        container._viz3dLastPlot=null;
        container._fullLayout=null;
        container.innerHTML='';
        previous=null;
    }
    const hasGraph=!!(container._fullLayout || previous);
    const stale=phase!=='ready' && hasGraph;
    const displayed=previous?.detail || (hasGraph ? '上一张图' : '');
    const requested=request ? [request.varName,request.opts.timeLabel || `时步 ${request.timestep}`].filter(Boolean).join(' · ') : '';
    const text=message+(stale ? ` · 保留旧图：${displayed}` : '')+(phase==='loading' && requested ? ` · ${requested}` : '');
    container._viz3dStatus={phase,message:text,stale,displayed:previous || null,
        requested:request ? {caseKey:request.key,variable:request.varName,timestep:request.timestep,timeLabel:request.opts.timeLabel || ''} : null};
    if(container.dataset) {container.dataset.renderPhase=phase;container.dataset.stale=String(stale);}
    let status=document.getElementById(request?.section ? 'viz3d-section-status' : 'viz3d-status');
    if(status===container) status=null;
    if(!status && document.createElement && container.parentNode) {
        status=container._viz3dStatusElement;
        if(!status) {
            status=document.createElement('div');status.className='sw-status';status.setAttribute('role','status');
            container.parentNode.insertBefore(status,container);container._viz3dStatusElement=status;
        }
    }
    if(status) {status.textContent=window.StudioI18n?.t(text) || text;if(status.dataset) status.dataset.phase=phase;}
    if(!request?.section)window.ScientificWorkspace?.setRenderState?.('viz3d',phase,phase==='ready'?'':window.StudioI18n?.t(text) || text);
    // A real Plotly graph is never removed by a loading/network-error message.
    // Minimal non-DOM harnesses have no graph children to preserve.
    if(phase!=='ready' && (!hasGraph || (!container._fullLayout && !document.createElement)))
        container.innerHTML=`<div role="status" style="padding:20px;color:var(--${phase==='error'?'danger':'text-muted'});">${viz3dEscape(text)}</div>`;
}
function viz3dCaptureCamera(c,request) {
    viz3dTrace('capture',c,request);
    if(c && !request?.section) {
        const graphCase=c._viz3dLastPlot?.caseKey;
        const camera=(graphCase===undefined || graphCase===request?.key)
            ? c._fullLayout?.scene?._scene?.getCamera?.() || _viz3dCamera || c._fullLayout?.scene?.camera : _viz3dCamera;
        if(camera) _viz3dCamera=JSON.parse(JSON.stringify(camera));
    }
}
function viz3dLoading(msg,request) {
    const c=request?.container || document.getElementById('viz3d-plotly');
    viz3dCaptureCamera(c,request);
    viz3dStatus(c,'loading',msg,request);
}
function viz3dError(msg,request) {
    const container=request?.container || document.getElementById('viz3d-plotly');
    const last=container?._viz3dLastPlot;
    const requestedMode=request?.opts?.meshMode;
    // When the new request fails, the graph is intentionally retained. Keep
    // its network selector truthful too; otherwise the control says triangles
    // while the visible Plotly legend still describes the orthogonal network.
    if(viz3dCurrent(request) && ['triangles','orthogonal'].includes(last?.meshMode)
            && ['triangles','orthogonal'].includes(requestedMode) && requestedMode!==last.meshMode) {
        const control=document.getElementById('viz3d-mesh-mode');
        if(control?.value===requestedMode)control.value=last.meshMode;
    }
    viz3dStatus(container,'error',msg,request);
}
function viz3dHasNoDynamicOutput(message) {
    return typeof message==='string' && /没有(?:3D)?输出文件|输出文件没有任何时间记录/.test(message);
}
function viz3dFailure(error,request) {
    if(!viz3dCurrent(request) || error?.name==='AbortError') return;
    const message=error?.message || String(error);
    viz3dError(`加载失败: ${message}`+(/webgl|gl context|gpu/i.test(message) ? ' · WebGL 不可用，请使用二维视图或数值剖面。' : ''),request);
}
function viz3dDone(request,data,guideId,detail,warning='',metadata={}) {
    if(!viz3dCurrent(request)) return;
    request.container._viz3dLastPlot={caseKey:request.key,variable:request.varName,timestep:request.timestep,
        timeLabel:request.opts.timeLabel || '',detail,meshMode:request.renderedMeshMode || null};
    if(guideId) window.VariableGuide?.updateValues(guideId,data);
    viz3dStatus(request.container,'ready',detail+(warning ? ` · ${warning}` : '')+
        viz3dUndersideNote(request.container._viz3dUndersideActive),request);
    if(!request.section) window.ScientificWorkspace?.publish?.('viz3d',{
        variable:request.varName,label:viz3dLabel(data,request.varName),units:data.units || '',
        min:data.min,max:data.max,field:data.data,time:request.timestep,date:request.opts.timeLabel || '',
        detail:detail+(warning ? ` · ${warning}` : ''),
        ...metadata});
    if(!request.section)window.PlaybackPerformance?.finish(request.playbackPerf);
}
function viz3dTicks(min,max,count=5) {
    if(!Number.isFinite(min) || !Number.isFinite(max)) return {values:[],labels:[]};
    const values=min===max ? [min] : Array.from({length:count},(_,i)=>i===count-1 ? max : min+(max-min)*i/(count-1));
    let labels=[];
    for(let precision=3;precision<=17;precision++) {
        labels=values.map(v=>Number(v.toPrecision(precision)).toString());
        if(new Set(labels).size===values.length) break;
    }
    return {values,labels};
}
function viz3dStyle(data,varName,request) {
    if(request.section && request.opts.range!==undefined) return viz3dInheritedRange(request.opts.range);
    if(window.ScientificStyle?.resolve) return window.ScientificStyle.resolve({caseKey:request.key,variable:varName,min:data.min,max:data.max});
    const ticks=viz3dTicks(data.min,data.max);
    return {min:data.min,max:data.max,mode:'auto',palette:'lake',colorscale:VIZ3D.colorScale,tickvals:ticks.values,ticktext:ticks.labels};
}
function viz3dValidStyle(style) {return Number.isFinite(style?.min) && Number.isFinite(style?.max) && style.min<=style.max;}
function viz3dInheritedRange(range) {
    const color=value=>{
        if(typeof value!=='string') return false;
        if(/^#(?:[\da-f]{3}|[\da-f]{6}|[\da-f]{8})$/i.test(value)) return true;
        const rgb=value.match(/^rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)$/i);
        return !!rgb && rgb.slice(1).every(v=>Number(v)<=255);
    };
    const scale=range?.colorscale,ticks=range?.tickvals,labels=range?.ticktext;
    const valid=viz3dValidStyle(range) && range.noData!==true && ['lake','cividis','viridis','blueRed','custom'].includes(range.palette)
        && ['auto','locked','custom'].includes(range.mode)
        && Array.isArray(scale) && scale.length>=2 && scale[0]?.[0]===0 && scale.at(-1)?.[0]===1
        && scale.every((s,i)=>Array.isArray(s) && s.length===2 && Number.isFinite(s[0]) && s[0]>=0 && s[0]<=1
            && (i===0 || s[0]>=scale[i-1][0]) && color(s[1]))
        && Array.isArray(ticks) && ticks.length>0 && ticks.every(v=>Number.isFinite(v) && v>=range.min && v<=range.max)
        && Array.isArray(labels) && labels.length===ticks.length
        && labels.every(v=>typeof v==='string' && v.trim()!=='' && Number.isFinite(Number(v)))
        && new Set(labels).size===labels.length;
    if(!valid) throw new RangeError('主视图色标范围无效，请重新绘制主图。');
    if(range.palette==='custom') {
        if(!window.ScientificStyle?.validateConfig)throw new RangeError('自定义色标不可用，请重新绘制主图。');
        const checked=window.ScientificStyle.validateConfig(range);
        if(JSON.stringify(window.ScientificStyle.colorscale(checked))!==JSON.stringify(scale)) {
            if(_viz3dTrace)console.debug('[3DWET colormap] '+JSON.stringify({actual:scale,expected:window.ScientificStyle.colorscale(checked)}));
            throw new RangeError('主视图自定义色标与颜色节点不一致。');
        }
    }
    return {...range,colorscale:scale.map(s=>[...s]),tickvals:[...ticks],ticktext:[...labels]};
}
function viz3dOpacity(opts,fallback=1) {return Number.isFinite(Number(opts.opacity)) ? Math.max(0.05,Math.min(1,Number(opts.opacity))) : fallback;}
function viz3dTime(timestep,opts,data={}) {return opts.timeLabel || data.time_label || data.timeLabel || `时步 ${timestep}（实际日期未提供）`;}
function viz3dRangeLabel(style) {return ({auto:'自动范围',locked:'锁定范围',custom:'自定义范围'})[style.mode] || style.mode;}
function viz3dFilename(mode,varName,timestep,opts,extra='') {
    return ['3dwet',mode,varName,opts.timeLabel || `t${timestep}`,extra].filter(Boolean).join('_').replace(/[<>:"/\\|?*\s]+/g,'-');
}
function viz3dCameraAxes(camera) {
    const visible={x:true,y:true,z:true};
    if(camera?.projection?.type && camera.projection.type!=='orthographic') return visible;
    const direction=['x','y','z'].map(axis=>camera?.eye?.[axis]-(camera?.center?.[axis] || 0));
    if(!direction.every(Number.isFinite)) return visible;
    const length=Math.hypot(...direction);
    if(!(length>0)) return visible;
    // Only an effectively exact axis direction collapses its projected axis.
    // A normal orbit gesture immediately restores all three coordinate axes.
    for(let n=0;n<3;n++) if(direction.every((v,i)=>i===n || Math.abs(v)<=length*1e-10)) visible[['x','y','z'][n]]=false;
    return visible;
}
function viz3dClampCamera(camera) {
    const axes=['x','y','z'],eye=camera?.eye,center=camera?.center || {x:0,y:0,z:0},up=camera?.up;
    if(!eye||!axes.every(axis=>Number.isFinite(Number(eye[axis]))&&Number.isFinite(Number(center[axis] ?? 0))))return null;
    const direction=axes.map(axis=>Number(eye[axis])-Number(center[axis] ?? 0));
    if(!direction.every(Number.isFinite))return null;
    // Plotly's orbit camera represents an over-the-pole view through its up
    // vector as well as eye position. Clamping eye elevation here destroys
    // that flipped orientation and snaps the released gesture back. Keep the
    // finite, non-degenerate camera exactly as Plotly reports it.
    const distance=Math.hypot(...direction);
    if(!(distance>1e-9))return null;
    if(up && (!axes.every(axis=>Number.isFinite(Number(up[axis])))||
        !(Math.hypot(...axes.map(axis=>Number(up[axis])))>1e-9)))return null;
    return camera;
}
function viz3dAxesPatch(visible) {
    return Object.fromEntries(['x','y','z'].map(axis=>[`scene.${axis}axis.visible`,visible[axis]]));
}
function viz3dSyncCameraAxes(element,camera) {
    const visible=viz3dCameraAxes(camera),previous=element._viz3dAxisVisibility;
    if(previous && ['x','y','z'].every(axis=>previous[axis]===visible[axis])) return;
    // Record before relayout: its own event may include the current camera.
    // That event must not start another axis relayout.
    element._viz3dAxisVisibility=visible;
    if(element._fullLayout && window.Plotly?.relayout)
        viz3dQueueDraw(element,()=>window.Plotly.relayout(element,viz3dAxesPatch(visible)))
            .catch(error=>viz3dFailure(error,element._viz3dResponsiveSource?.request));
}
function viz3dCameraBelowWater(camera) {
    return Number(camera?.eye?.z)-Number(camera?.center?.z||0)<-1e-6;
}
function viz3dCameraElevationDegrees(camera) {
    const center=camera?.center || {x:0,y:0,z:0},eye=camera?.eye;
    if(!eye||!['x','y','z'].every(axis=>Number.isFinite(Number(eye[axis]))&&Number.isFinite(Number(center[axis] ?? 0))))return 0;
    const dx=Number(eye.x)-Number(center.x ?? 0),dy=Number(eye.y)-Number(center.y ?? 0),dz=Number(eye.z)-Number(center.z ?? 0);
    const elevation=Math.atan2(dz,Math.hypot(dx,dy))*180/Math.PI;
    return Math.max(-89,Math.min(89,Math.round(elevation)));
}
function viz3dCameraAtElevation(camera,degrees,fallbackAzimuth=_viz3dCameraAzimuth) {
    const center=camera?.center || {x:0,y:0,z:0},eye=camera?.eye;
    if(!eye||!Number.isFinite(Number(degrees))||
        !['x','y','z'].every(axis=>Number.isFinite(Number(eye[axis]))&&Number.isFinite(Number(center[axis] ?? 0))))return null;
    const dx=Number(eye.x)-Number(center.x ?? 0),dy=Number(eye.y)-Number(center.y ?? 0),dz=Number(eye.z)-Number(center.z ?? 0);
    const distance=Math.hypot(dx,dy,dz);
    if(!(distance>1e-9))return null;
    const horizontal=Math.hypot(dx,dy),azimuth=horizontal>1e-9?Math.atan2(dy,dx):
        Number.isFinite(Number(fallbackAzimuth))?Number(fallbackAzimuth):0;
    const elevation=Math.max(-89,Math.min(89,Number(degrees)))*Math.PI/180;
    const radius=distance*Math.cos(elevation);
    return {...camera,center:{...center},eye:{x:Number(center.x ?? 0)+radius*Math.cos(azimuth),
        y:Number(center.y ?? 0)+radius*Math.sin(azimuth),z:Number(center.z ?? 0)+distance*Math.sin(elevation)},
        up:{...(camera?.up || {x:0,y:0,z:1})},projection:{...(camera?.projection || {type:'orthographic'})}};
}
function viz3dRememberCameraHeading(camera) {
    const dx=Number(camera?.eye?.x)-Number(camera?.center?.x ?? 0),dy=Number(camera?.eye?.y)-Number(camera?.center?.y ?? 0);
    if(Number.isFinite(dx)&&Number.isFinite(dy)&&Math.hypot(dx,dy)>1e-9)_viz3dCameraAzimuth=Math.atan2(dy,dx);
}
function viz3dSyncElevationControl(camera) {
    const slider=document.getElementById('viz3d-camera-elevation');
    if(!slider)return;
    const elevation=viz3dCameraElevationDegrees(camera);
    slider.value=String(elevation);
    const output=document.getElementById('viz3d-camera-elevation-value');
    if(output)output.textContent=`${elevation}°`;
}
// Plotly scene camera eye/center use normalized scene coordinates, not the
// physical units displayed on the Z axis. Keep the whole slider travel inside
// a conservative camera-space bound so large-depth cases cannot move offscreen.
const VIZ3D_VERTICAL_POSITION_LIMIT=.45;
function viz3dVerticalPositionScale() { return VIZ3D_VERTICAL_POSITION_LIMIT; }
function viz3dCameraVerticalPosition(camera,span=1) {
    const center=Number(camera?.center?.z ?? 0),scale=Number(span);
    return Number.isFinite(center)&&Number.isFinite(scale)&&scale>1e-9?Math.max(-100,Math.min(100,Math.round(-center/scale*100))):0;
}
function viz3dCameraAtVerticalPosition(camera,percent,span=1) {
    const position=Math.max(-100,Math.min(100,Number(percent)));
    const scale=Number(span);
    const center=camera?.center||{x:0,y:0,z:0};
    if(!camera?.eye||!Number.isFinite(position)||!Number.isFinite(scale)||!(scale>1e-9)||
        !['x','y','z'].every(axis=>Number.isFinite(Number(camera.eye[axis]))&&Number.isFinite(Number(center[axis] ?? 0))))return null;
    const delta=-position/100*scale-Number(center.z ?? 0);
    return {...camera,center:{...center,z:Number(center.z ?? 0)+delta},
        eye:{...camera.eye,z:Number(camera.eye.z)+delta},up:{...(camera.up||{x:0,y:0,z:1})},
        projection:{...(camera.projection||{type:'orthographic'})}};
}
function viz3dSyncVerticalPositionControl(camera) {
    const slider=document.getElementById('viz3d-camera-position');
    if(!slider)return;
    const c=document.getElementById('viz3d-plotly');
    const position=viz3dCameraVerticalPosition(camera,viz3dVerticalPositionScale(c?._fullLayout?.scene||VIZ3D.layout.scene));
    slider.value=String(position);
    const output=document.getElementById('viz3d-camera-position-value');
    if(output)output.textContent=`${position>0?'+':''}${position}%`;
}
function set3DCameraVerticalPosition(value) {
    const c=document.getElementById('viz3d-plotly'),position=Number(value);
    if(!Number.isFinite(position))return Promise.resolve();
    const current=_viz3dCamera || c?._fullLayout?.scene?._scene?.getCamera?.() ||
        c?._fullLayout?.scene?.camera || VIZ3D.layout.scene.camera;
    const camera=viz3dCameraAtVerticalPosition(current,position,viz3dVerticalPositionScale(c?._fullLayout?.scene||VIZ3D.layout.scene));
    if(!camera)return Promise.resolve();
    _viz3dCamera=camera;viz3dSyncVerticalPositionControl(camera);
    const visible=viz3dCameraAxes(camera);
    if(c)c._viz3dAxisVisibility=visible;
    if(!c)return Promise.resolve();
    return viz3dQueueDraw(c,async()=>{
        if(c?._fullLayout && window.Plotly?.relayout) {
            c._viz3dCameraPresetPending=true;
            try {
                await viz3dApplyUndersideModeNow(c,camera);
                await window.Plotly.relayout(c,{'scene.camera':camera,...viz3dAxesPatch(visible)});
            } finally {c._viz3dCameraPresetPending=false;}
            return;
        }
        await viz3dApplyUndersideModeNow(c,camera);
    });
}
function set3DCameraElevation(value) {
    const c=document.getElementById('viz3d-plotly'),degrees=Math.max(-89,Math.min(89,Number(value)));
    if(!Number.isFinite(degrees))return Promise.resolve();
    const current=_viz3dCamera || c?._fullLayout?.scene?._scene?.getCamera?.() ||
        c?._fullLayout?.scene?.camera || VIZ3D.layout.scene.camera;
    const camera=viz3dCameraAtElevation(current,degrees,_viz3dCameraAzimuth);
    if(!camera)return Promise.resolve();
    _viz3dCamera=camera;viz3dRememberCameraHeading(camera);viz3dSyncElevationControl(camera);
    const visible=viz3dCameraAxes(camera);
    if(c)c._viz3dAxisVisibility=visible;
    if(!c)return Promise.resolve();
    return viz3dQueueDraw(c,async()=>{
        if(c?._fullLayout && window.Plotly?.relayout) {
            c._viz3dCameraPresetPending=true;
            try {
                await viz3dApplyUndersideModeNow(c,camera);
                await window.Plotly.relayout(c,{'scene.camera':camera,...viz3dAxesPatch(visible)});
            } finally {c._viz3dCameraPresetPending=false;}
            return;
        }
        await viz3dApplyUndersideModeNow(c,camera);
    });
}
function viz3dIsUndersideOccluder(trace) {
    return trace?.meta?.waterbodyFrame==='bed'||trace?.meta?.waterbodyFrame==='land'||trace?.meta?.landPlane===true;
}
function viz3dUndersideOpacity(trace,active) {
    return active?0:(trace?.meta?.landNetwork===true ? 0.24 : 1);
}
function viz3dUndersideNote(active) {
    return active?' · 水体底视：已隐藏湖底与陆地示意平面':'';
}
function viz3dApplyUndersideModeNow(element,camera) {
    if(!element?.data)return Promise.resolve();
    const hasScientificField=element.data.some(trace=>trace.meta?.scientificField===true);
    const active=hasScientificField&&viz3dCameraBelowWater(camera);
    const indices=element.data.flatMap((trace,index)=>viz3dIsUndersideOccluder(trace)?[index]:[]);
    const changed=indices.filter(index=>element.data[index].opacity!==viz3dUndersideOpacity(element.data[index],active));
    element._viz3dUndersideActive=active;
    const status=element._viz3dStatus;
    if(status?.phase==='ready') {
        const base=status.message.replace(/ · 水体底视：已隐藏湖底与陆地示意平面$/,'');
        status.message=base+viz3dUndersideNote(active);
        const node=document.getElementById('viz3d-status');
        if(node)node.textContent=window.StudioI18n?.t(status.message)||status.message;
    }
    if(!changed.length||!window.Plotly?.restyle)return Promise.resolve();
    return Promise.resolve(window.Plotly.restyle(element,{opacity:changed.map(index=>viz3dUndersideOpacity(element.data[index],active))},changed));
}
function viz3dApplyUndersideMode(element,camera) {
    if(!element)return Promise.resolve();
    return viz3dQueueDraw(element,()=>viz3dApplyUndersideModeNow(element,camera));
}
function set3DCamera(view='oblique') {
    const eyes={oblique:{x:0.8525,y:-0.9625,z:0.88},reset:{x:0.8525,y:-0.9625,z:0.88},
        top:{x:0,y:0,z:2.5},bottom:{x:0,y:0,z:-2.5},front:{x:0,y:-2.5,z:0},side:{x:2.5,y:0,z:0}};
    if(!eyes[view]) throw new Error(`未知镜头：${view}`);
    _viz3dCamera={eye:{...eyes[view]},center:{x:0,y:0,z:0},up:['top','bottom'].includes(view)?{x:0,y:1,z:0}:{x:0,y:0,z:1},projection:{type:'orthographic'}};
    viz3dRememberCameraHeading(_viz3dCamera);viz3dSyncElevationControl(_viz3dCamera);viz3dSyncVerticalPositionControl(_viz3dCamera);
    const c=document.getElementById('viz3d-plotly');
    const visible=viz3dCameraAxes(_viz3dCamera);
    if(c) {
        c._viz3dAxisVisibility=visible;
        if(view==='reset'&&c._viz3dAspectRatioState)c._viz3dAspectRatioState={
            baseline:{...c._viz3dAspectRatioState.baseline},scale:1};
    }
    if(!c)return Promise.resolve();
    return viz3dQueueDraw(c,async()=>{
        if(c?._fullLayout && window.Plotly?.relayout) {
            c._viz3dCameraPresetPending=true;
            try {
                await viz3dApplyUndersideModeNow(c,_viz3dCamera);
                const resetAspect=view==='reset'?c._viz3dAspectRatioState?.baseline:undefined;
                await window.Plotly.relayout(c,{'scene.camera':_viz3dCamera,...viz3dAxesPatch(visible),
                    ...(resetAspect?{'scene.aspectratio':resetAspect}:{})});
            } finally {c._viz3dCameraPresetPending=false;}
            return;
        }
        await viz3dApplyUndersideModeNow(c,_viz3dCamera);
    });
}
if(typeof window!=='undefined') window.set3DCamera=set3DCamera;
if(typeof window!=='undefined') window.set3DCameraElevation=set3DCameraElevation;
if(typeof window!=='undefined') window.set3DCameraVerticalPosition=set3DCameraVerticalPosition;

function viz3dEscape(value) {
    return String(value ?? '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}

function viz3dColorbar(name, units = '', style) {
    const width=document.getElementById('viz3d-plotly')?.getBoundingClientRect?.().width || 700;
    const letters=Array.from(String(name || '数值'));
    const label=letters.length>12 ? letters.slice(0,11).join('')+'…' : letters.join('');
    return {title:{text:viz3dEscape(label)+(units ? '<br>('+viz3dEscape(units)+')' : ''),side:'top',font:{size:11,color:'#304b59'}},
        len:0.64,thickness:width<520 ? 11 : 15,x:1.02,xpad:8,
        outlinewidth:1,outlinecolor:'#c0cfd7',ticks:'outside',ticklen:4,tickcolor:'#718995',
        nticks:5,...(style ? {tickmode:'array',tickvals:style.tickvals,ticktext:style.ticktext} : {}),
        tickfont:{size:10,color:'#435661'},bgcolor:'rgba(247,250,251,0.92)'};
}

function viz3dReference(varName) {
    const reference=window.VariableGuide?.referenceText?.(varName);
    return reference ? '<br>'+viz3dEscape(reference) : '';
}

function viz3dTitle(name,detail) {
    const width=document.getElementById('viz3d-plotly')?.getBoundingClientRect?.().width || 700;
    const limit=Math.max(14,Math.min(45,Math.floor((width-80)/14)));
    const letters=Array.from(String(name || ''));
    const label=letters.length>limit ? letters.slice(0,limit-1).join('')+'…' : letters.join('');
    const parts=String(detail || '').split(' · ');
    // Keep the depth reference beside the name, including compact layouts
    // that retain only the first line. Full evidence remains in status and
    // published/export metadata; explanatory paragraphs must not cover data.
    const datum=parts.find(part=>/^水深 \(m,/.test(part))
        || (parts.includes('Z 为变量值，不是物理水深')?'变量高度（非水深）':null);
    const brief=parts.filter(part=>/^\d{4}[-/]|^时步 |^层 |^全部层|^垂向 |^静态地形$|^常量场$|^锁定范围$|^自定义范围$|^[XY]Z$|^[ij]=/.test(part));
    if(parts.some(part=>part.startsWith('采样步长')))brief.push('采样显示');
    return {text:[datum?label+' · '+datum:label,...(brief.length?[brief.join(' · ')]:[])].map(viz3dEscape).join('<br>'),
        font:{size:width<520?10:12},x:0.5,xanchor:'center'};
}

function viz3dLabel(item,name) {
    const localized=window.localizedResult?.(item,name);
    return localized?.comparison_name || localized?.display_name || item?.long_name || name;
}
function viz3dTranslatedText(value) {
    const identity=viz3dCaseIdentity();
    const locale=window.StudioI18n?.locale?.() || '';
    const key=JSON.stringify([locale,identity.path,identity.revision,identity.outputRevision,value]);
    if(_viz3dTranslatedTextCache.has(key)) {
        const cached=_viz3dTranslatedTextCache.get(key);
        _viz3dTranslatedTextCache.delete(key);_viz3dTranslatedTextCache.set(key,cached);
        return cached;
    }
    let translated=value;
    const direct=window.StudioI18n?.t(value);
    if(direct!==undefined && direct!==value && !/[\u3400-\u9fff]/.test(direct))translated=direct;
    else {
        // Share Chart.js's protected scientific-term translation so paired
        // Chinese/original terms survive translation of surrounding UI text.
        const wrapper={text:value};
        if(window.translateChartLabels)window.translateChartLabels(wrapper);
        else wrapper.text=window.StudioI18n?.t(value) || value;
        translated=wrapper.text;
    }
    _viz3dTranslatedTextCache.set(key,translated);
    while(_viz3dTranslatedTextCache.size>VIZ3D_TRANSLATED_TEXT_CACHE_LIMIT)
        _viz3dTranslatedTextCache.delete(_viz3dTranslatedTextCache.keys().next().value);
    return translated;
}
if(typeof document!=='undefined'&&document.addEventListener)
    document.addEventListener('studio-language-changed',()=>_viz3dTranslatedTextCache.clear());
function viz3dTranslateText(obj) {
    if (!obj || typeof obj!=='object') return obj;
    const copy={...obj};
    for(const [key,value] of Object.entries(copy)) {
        // Plotly normalizes color strings in place. Its trace must not own the
        // shared scale later inherited by linked views and export legends.
        if(key==='colorscale' && Array.isArray(value))copy[key]=value.map(stop=>[...stop]);
        else if(key==='text' && Array.isArray(value))copy[key]=value.map(text=>
            typeof text==='string'?viz3dTranslateText({text}).text:text);
        else if(['name','hovertemplate','text','title'].includes(key) && typeof value==='string') {
            copy[key]=viz3dTranslatedText(value);
        }
        else if(value && typeof value==='object' && !Array.isArray(value)) copy[key]=viz3dTranslateText(value);
    }
    return copy;
}
function viz3dResponsiveLayout(layout,height,width) {
    const short=Number.isFinite(height) && height>0 && height<300;
    const narrow=Number.isFinite(width) && width>0 && width<560;
    if(!short && !narrow)return layout;
    const hasHeight=Number.isFinite(height)&&height>0;
    const titleTop=hasHeight?Math.min(40,Math.max(32,height*.25)):40;
    const compact={...layout,title:{...layout.title,text:String(layout.title?.text || '').split('<br>')[0],font:{...layout.title?.font,size:11},
            yref:'container',yanchor:'top',y:hasHeight?Math.max(0,1-titleTop/height):.9,pad:{t:0,b:0}},
        margin:{...layout.margin,t:narrow?60:hasHeight?Math.min(54,height*.4):54,
            ...(narrow?{l:Math.max(32,layout.margin?.l || 0),r:Math.max(112,layout.margin?.r || 0)}:{}),b:narrow?28:10},showlegend:false};
    // Keep the original scene.aspectratio scale. Plotly GL3D uses a common
    // factor here as an actual zoom control (its orthographic wheel handler
    // multiplies all three axes); multiplying by a viewport fit factor shrinks
    // the entire model on narrow screens even though XYZ proportions survive.
    return compact;
}
function viz3dQueueDraw(element,operation) {
    const pending=(element?._viz3dDrawTail || Promise.resolve()).then(operation,operation);
    // Keep the rejection visible to this caller, without poisoning later draws.
    if(element)element._viz3dDrawTail=pending.catch(()=>undefined);
    return pending;
}
async function resizeScientific3D(element) {
    const saved=element?._viz3dResponsiveSource;
    if(!saved || !element._fullLayout || !viz3dCurrent(saved.request) || !window.Plotly?.relayout)return false;
    return viz3dQueueDraw(element,async()=>{
    // A delayed resize also mutates title and aspect. It must finish before a
    // newer frame draws, and a resize still queued for an old frame is skipped.
    if(!viz3dCurrent(saved.request))return false;
    const width=element.clientWidth,height=element.clientHeight;
    if(!(width>0 && height>0))return false;
    let layout=viz3dResponsiveLayout(saved.layout,height,width);
    let nextAspectState=null;
    if(saved.request.main?.mode==='waterbody') {
        const prior=element._viz3dWaterbodyPatch;
        const preserveZoom=!!(prior?.key===saved.request.main.updateKey&&
            prior.topologyKey===saved.request.main.topologyKey);
        const prepared=viz3dPrepareWaterbodyAspect(layout,element,preserveZoom);
        layout=prepared.layout;nextAspectState=prepared.state;
    }
    try{
        await window.Plotly.relayout(element,{width,height,title:layout.title,margin:layout.margin,showlegend:layout.showlegend,
            ...(layout.scene?.aspectratio ? {'scene.aspectratio':layout.scene.aspectratio} : {})});
        if(nextAspectState)element._viz3dAspectRatioState=nextAspectState;
        return viz3dCurrent(saved.request);
    }catch(error){viz3dFailure(error,saved.request);return false;}
    });
}
if(typeof window!=='undefined')window.resizeScientific3D=resizeScientific3D;

const VIZ3D_WATERBODY_PATCH_PROPERTIES=['x','y','z','i','j','k','intensity','customdata',
    'cmin','cmax','cauto','colorscale','showscale','colorbar','opacity','color','visible'];
function viz3dArrayShape(value) {
    if(!Array.isArray(value))return null;
    const first=value[0],last=value.at(-1);
    return [value.length,Array.isArray(first)?first.length:null,Array.isArray(last)?last.length:null];
}
function viz3dWaterbodyTraceSchema(traces) {
    return JSON.stringify(traces.map(trace=>({type:trace.type,name:trace.name,
        role:trace.meta?.waterbodyFrame || null,
        layerOrdinals:trace.meta?.layerOrdinals || null,
        arrays:Object.fromEntries(VIZ3D_WATERBODY_PATCH_PROPERTIES
            .filter(key=>Object.prototype.hasOwnProperty.call(trace,key))
            .map(key=>[key,viz3dArrayShape(trace[key])])),
        connectivity:Object.fromEntries(['i','j','k'].map(key=>[key,viz3dArrayShape(trace[key])]))})));
}
function viz3dWaterbodyRestyleGroups(currentTraces,nextTraces) {
    if(!Array.isArray(currentTraces)||currentTraces.length!==nextTraces.length)return null;
    const roleProperties={
        bed:['z','intensity','customdata','cmin','cmax','colorbar','opacity'],
        land:['opacity'],
        wall:['z'],contour:['x','y','z','customdata'],network:['z','x','y'],
        // Horizontal vertices and cell connectivity belong to the cached
        // wet topology. Only frame-dependent elevations, values, and hover
        // measurements need to cross Plotly's update boundary during playback.
        // Scalar validity can move between cells while the trace keeps the
        // same lengths. Refresh coordinates and connectivity so Plotly never
        // keeps the previous frame's wet-cell triangles.
        field:['x','y','z','i','j','k','intensity','customdata','cmin','cmax','colorscale','colorbar'],
        missing:['x','y','z','i','j','k','customdata'],
    };
    const indices=[],roles=[];
    for(let index=0;index<nextTraces.length;index++) {
        const oldTrace=currentTraces[index],nextTrace=nextTraces[index];
        if(!oldTrace||oldTrace.type!==nextTrace.type||oldTrace.name!==nextTrace.name||
            oldTrace.meta?.waterbodyFrame!==nextTrace.meta?.waterbodyFrame)return null;
        const properties=roleProperties[nextTrace.meta?.waterbodyFrame];
        if(!properties)continue;
        for(const property of properties) {
            if(Object.prototype.hasOwnProperty.call(oldTrace,property)!==Object.prototype.hasOwnProperty.call(nextTrace,property))return null;
        }
        indices.push(index);roles.push({trace:nextTrace,properties});
    }
    const propertyNames=[...new Set(roles.flatMap(role=>role.properties))],update={};
    for(const property of propertyNames)update[property]=roles.map(({trace,properties})=>{
        if(!properties.includes(property))return undefined;
        const value=trace[property];
        // roles.map already supplies the selected-trace dimension. Preserve
        // array-valued attributes intact as the value for this trace.
        return value;
    });
    return {indices,update};
}
function viz3dWaterbodyRelayout(layout) {
    const update={
        'title.text':layout.title?.text,'title.font':layout.title?.font,
        'margin.t':layout.margin?.t,'margin.r':layout.margin?.r,
        'margin.b':layout.margin?.b,'margin.l':layout.margin?.l,
        'showlegend':layout.showlegend,'uirevision':layout.uirevision,
    };
    for(const axis of ['x','y','z']) {
        const current=layout.scene?.[`${axis}axis`];
        if(!current)continue;
        for(const property of ['title','range','autorange','visible','tickmode','tickvals','ticktext'])
            if(Object.prototype.hasOwnProperty.call(current,property))
                update[`scene.${axis}axis${property==='title'?'.title.text':`.${property}`}`]=
                    property==='title'?current.title?.text:current[property];
    }
    if(layout.scene?.aspectmode!==undefined)update['scene.aspectmode']=layout.scene.aspectmode;
    if(layout.scene?.aspectratio!==undefined)update['scene.aspectratio']=layout.scene.aspectratio;
    // `layout.scene.camera` was captured from Plotly's live WebGL scene just
    // before this frame draw. Plotly.update can otherwise restore its old scene
    // camera when aspectratio changes, discarding an orbit made during playback.
    if(layout.scene?.camera!==undefined)update['scene.camera']=layout.scene.camera;
    return Object.fromEntries(Object.entries(update).filter(([,value])=>value!==undefined));
}
function viz3dAspectZoomScale(current,baseline) {
    if(!current||!baseline)return 1;
    const ratios=['x','y','z'].map(axis=>Number(current[axis])/Number(baseline[axis]));
    if(!ratios.every(value=>Number.isFinite(value)&&value>0))return 1;
    // Plotly's orthographic wheel handler scales all three axes together.
    // Geometric averaging preserves that common zoom factor without distorting
    // the physical x:y:z proportions when the underlying geometry changes.
    return Math.max(.05,Math.min(20,Math.exp(ratios.reduce((sum,value)=>sum+Math.log(value),0)/3)));
}
function viz3dPrepareWaterbodyAspect(layout,element,preserveZoom) {
    const baseline=layout.scene?.aspectratio;
    if(!baseline||!['x','y','z'].every(axis=>Number.isFinite(Number(baseline[axis]))&&Number(baseline[axis])>0))
        return {layout,state:null};
    const previous=element?._viz3dAspectRatioState;
    const current=element?._fullLayout?.scene?.aspectratio;
    const measured=previous?viz3dAspectZoomScale(current,previous.baseline):1;
    // Orbiting through a vertical pole can make Plotly report its base aspect
    // ratio along with the camera event. Keep the last wheel scale in that case;
    // a real wheel event updates `previous.scale` directly below.
    const scale=preserveZoom&&previous
        ? (Math.abs(measured-1)>1e-9?measured:(Number(previous.scale)||1)) : 1;
    const aspectratio=Object.fromEntries(['x','y','z'].map(axis=>[axis,Number(baseline[axis])*scale]));
    return {layout:{...layout,scene:{...layout.scene,aspectratio}},state:{baseline:{...baseline},scale}};
}

function viz3dTraceAuditReport(traces) {
    const traceArray=Array.isArray(traces)?traces:[];
    const arrayStats=value=>{
        if(!Array.isArray(value)&&!ArrayBuffer.isView(value))return {length:null,min:null,max:null,nonFinite:0};
        const values=[];
        let nonFinite=0;
        const visit=item=>{
            if(Array.isArray(item)||ArrayBuffer.isView(item)){for(const child of item)visit(child);return;}
            if(typeof item==='number'){
                if(Number.isFinite(item))values.push(item);else nonFinite++;
            }
        };
        visit(value);
        let min=null,max=null;
        for(const number of values){min=min===null?number:Math.min(min,number);max=max===null?number:Math.max(max,number);}
        return {length:value.length,min,max,nonFinite};
    };
    return traceArray.map((trace,index)=>({index,type:trace?.type ?? null,name:trace?.name ?? null,
        visible:trace?.visible ?? true,color:trace?.color ?? null,colorscale:trace?.colorscale ?? null,
        intensitymode:trace?.intensitymode ?? null,cmin:trace?.cmin ?? null,cmax:trace?.cmax ?? null,
        flatshading:trace?.flatshading ?? null,lighting:trace?.lighting ?? null,opacity:trace?.opacity ?? null,
        arrays:Object.fromEntries(['x','y','z','i','j','k','intensity','customdata'].map(key=>[key,arrayStats(trace?.[key])]))}));
}

function viz3dRefreshTraceAudit(container) {
    if(new URLSearchParams(window.location?.search || '').get('viz3d-trace-audit')!=='1')return;
    const traces=container?._fullData;
    if(!Array.isArray(traces))return;
    const report=viz3dTraceAuditReport(traces);
    const serializeValue=(value,seen=new WeakSet())=>{
        if(value===undefined)return null;
        if(value===null||typeof value==='string'||typeof value==='boolean')return value;
        if(typeof value==='number')return Number.isFinite(value)?value:String(value);
        if(typeof value!=='object')return String(value);
        if(seen.has(value))return '[Circular]';
        seen.add(value);
        if(ArrayBuffer.isView(value)||Array.isArray(value))return Array.from(value,item=>serializeValue(item,seen));
        const out={};for(const [key,item] of Object.entries(value))if(typeof item!=='function')out[key]=serializeValue(item,seen);
        return out;
    };
    const pick=(source,keys)=>Object.fromEntries(keys.filter(key=>source?.[key]!==undefined).map(key=>[key,serializeValue(source[key])]));
    const axisKeys=['visible','showgrid','gridcolor','showline','linecolor','ticks','zeroline','showbackground',
        'backgroundcolor','showticklabels','tickvals','ticktext','tickformat','range','autorange','title','nticks',
        'tickfont','showspikes','spikemode','spikesides','spikethickness'];
    const sceneSource=container._fullLayout?.scene||{};
    const scene={...pick(sceneSource,['camera','aspectmode','aspectratio','bgcolor']),
        axes:Object.fromEntries(['xaxis','yaxis','zaxis'].map(axis=>[axis,pick(sceneSource[axis],axisKeys)]))};
    const traceKeys=['type','name','meta','visible','showlegend','opacity','color','colorscale','intensitymode',
        'cmin','cmax','cauto','flatshading','lighting','lightposition','hovertemplate','showscale','colorbar',
        'x','y','z','i','j','k','intensity','customdata'];
    const fullTraces=traces.map(trace=>pick(trace,traceKeys));
    const main=container._viz3dMainView?.request || {};
    const appState=typeof state!=='undefined'?state:window.state;
    const context={capturedAt:new Date().toISOString(),plotlyVersion:window.Plotly?.version||null,
        userAgent:globalThis.navigator?.userAgent??null,webglRenderer:null,
        chart:{id:container.id||null,width:container.clientWidth||0,height:container.clientHeight||0,
            boundingRect:(()=>{const r=container.getBoundingClientRect?.();return r?{width:r.width,height:r.height,top:r.top,left:r.left}:null;})()},
        scene,
        selection:{frame:main.timestep??null,time:main.timeLabel??main.opts?.timeLabel??main.main?.data?.time_label??main.main?.data?.timeLabel??null,variable:main.varName??null,
            layer:main.opts?.level??main.opts?.layer??null,ve:main.main?.ve??main.opts?.ve??null,
            stack:main.opts?.stack??main.opts?.stackLayers??null,
            gridMode:main.opts?.gridMode??main.opts?.meshMode??main.opts?.displayMesh??null,
            case:appState?.activeCase??null,casePath:appState?.activeCasePath??null},
        application:{version:window.STUDIO_VERSION||window.APP_VERSION||null,
            build:window.STUDIO_BUILD||window.BUILD_ID||null,
            assets:Array.from(document.scripts||[]).map(s=>s.src).filter(src=>/viz3d\.js|app\.js/.test(src))}};
    try{
        const canvas=container.querySelector('canvas');const gl=canvas?.getContext('webgl2')||canvas?.getContext('webgl')||canvas?.getContext('experimental-webgl');
        if(gl){const ext=gl.getExtension('WEBGL_debug_renderer_info');context.webglRenderer=ext?gl.getParameter(ext.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER);}
    }catch{}
    const fullReport={...context,traceSummary:report,traces:fullTraces};
    let panel=document.getElementById('viz3d-trace-audit');
    if(!panel){
        panel=document.createElement('section');panel.id='viz3d-trace-audit';panel.className='sw-status';
        panel.setAttribute('role','region');panel.setAttribute('aria-label','Read-only Plotly trace audit');
        panel.style.cssText='max-height:260px;overflow:auto;white-space:pre-wrap;font:11px/1.45 ui-monospace,Consolas,monospace;';
        const heading=document.createElement('h3');heading.textContent='3D trace audit (read only)';
        heading.style.cssText='display:flex;align-items:center;justify-content:space-between;gap:12px;';
        const output=document.createElement('pre');output.setAttribute('aria-label','Trace attributes and numeric array ranges');
        const button=document.createElement('button');button.type='button';button.textContent='导出黑色床面诊断 JSON + PNG';
        button.onclick=async()=>{
            const stamp=new Date().toISOString().replace(/[:.]/g,'-');
            const download=(blob,name)=>{const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
            try{download(new Blob([JSON.stringify(panel._viz3dTraceAuditReport,null,2)],{type:'application/json'}),`viz3d-bed-diagnostic-${stamp}.json`);}
            catch(error){output.textContent=`JSON 导出失败：${error?.message||error}`;return;}
            try{const png=await window.Plotly.toImage(container,{format:'png',width:container.clientWidth||1200,height:container.clientHeight||800});
                const response=await fetch(png);download(await response.blob(),`viz3d-bed-diagnostic-${stamp}.png`);}
            catch(error){output.textContent+=`\nPNG 导出失败（JSON 已保存）：${error?.message||error}`;}
        };
        heading.append(button);
        panel.append(heading,output);
        if(container.parentNode)container.parentNode.insertBefore(panel,container.nextSibling);
        else if(container.appendChild)container.appendChild(panel);
        panel._viz3dTraceAuditOutput=output;
    }
    const output=panel._viz3dTraceAuditOutput || panel.querySelector?.('pre');
    panel._viz3dTraceAuditReport=fullReport;
    if(output)output.textContent=JSON.stringify(report,null,2);
}

async function viz3dPlot(container,traces,layout,config,request) {
    if(!viz3dCurrent(request)) return Promise.resolve();
    const element=typeof container==='string' ? document.getElementById(container) : container;
    // Plotly mutates the live graph before its promise settles. A token check
    // after react cannot undo an older draw that finishes last. Serialize draws
    // for this viewport and drop obsolete queued frames before touching it.
    const queuedAt=viz3dNow();
    const frameBuildMs=Number.isFinite(request?._assemblyStartedAt)
        ? Math.max(0,queuedAt-request._assemblyStartedAt) : 0;
    const operation=async()=>{
    if(!viz3dCurrent(request)) return;
    if(!request?.section) {
        await _viz3dIndicatorQueue;
        if(!viz3dCurrent(request)) return;
        // The permanent styled toolbar frame must contain visible tools even
        // on touch screens, where hover-only Plotly buttons stay transparent.
        config={...config,displayModeBar:true};
    }
    const plotPreparationStartedAt=viz3dNow();
    if(!request?.section)window.PlaybackPerformance?.stage(request.playbackPerf,'queueWait',plotPreparationStartedAt-queuedAt);
    const plotTranslateStartedAt=viz3dNow();
    traces=traces.map(viz3dTranslateText);layout=viz3dTranslateText(layout);
    if(!request?.section)window.PlaybackPerformance?.stage(request.playbackPerf,'plotTranslate',viz3dNow()-plotTranslateStartedAt);
    const updating=!!(element?._fullLayout && window.Plotly?.react);
    if(element && !updating) element.innerHTML='';
    const plotLayoutStartedAt=viz3dNow();
    const titleLines=String(layout.title?.text || '').split('<br>').length;
    layout={...layout,margin:{...layout.margin,t:Math.max(layout.margin?.t || 0,20+titleLines*16)}};
    const responsiveSource={layout,request};
    if(!request?.section)layout=viz3dResponsiveLayout(layout,element?.clientHeight,element?.clientWidth);
    if(!request?.section&&request.main?.mode==='waterbody') {
        const prior=element?._viz3dWaterbodyPatch;
        const preserveZoom=!!(updating&&request.main.updateKey&&prior?.key===request.main.updateKey&&
            prior.topologyKey===request.main.topologyKey);
        const prepared=viz3dPrepareWaterbodyAspect(layout,element,preserveZoom);
        layout=prepared.layout;request._viz3dAspectRatioState=prepared.state;
    } else if(!request?.section)request._viz3dAspectRatioState=null;
    // Fetching and a previous queued Plotly operation can both take time. Read
    // the live gesture camera only now, immediately before this draw starts.
    viz3dCaptureCamera(element,request);
    const dragmode=element?._fullLayout?.scene?.dragmode;
    if(!request?.section && layout.scene && ['pan','zoom','orbit','turntable',false].includes(dragmode))
        layout={...layout,scene:{...layout.scene,dragmode}};
    if(_viz3dCamera && layout.scene && !request?.section) layout={...layout,scene:{...layout.scene,
        camera:{..._viz3dCamera,projection:{type:'orthographic'}}}};
    if(!request?.section) {
        const underside=traces.some(trace=>trace.meta?.scientificField===true)&&viz3dCameraBelowWater(_viz3dCamera);
        for(const trace of traces)if(viz3dIsUndersideOccluder(trace))trace.opacity=viz3dUndersideOpacity(trace,underside);
        element._viz3dUndersideActive=underside;
    }
    if(layout.scene && !request?.section) {
        const visible=viz3dCameraAxes(layout.scene.camera);
        layout={...layout,scene:{...layout.scene,...Object.fromEntries(['x','y','z'].map(axis=>[
            `${axis}axis`,{...layout.scene[`${axis}axis`],visible:visible[axis]}]))}};
        if(element) element._viz3dAxisVisibility=visible;
    }
    if(!request?.section)window.PlaybackPerformance?.stage(request.playbackPerf,'plotLayout',viz3dNow()-plotLayoutStartedAt);
    const plotSchemaStartedAt=viz3dNow();
    const dynamicIndices=traces.flatMap((trace,index)=>trace.meta?.scientificField===true||trace.meta?.missingWater===true?[index]:[]);
    const traceSchema=viz3dWaterbodyTraceSchema(traces);
    const priorPatch=element?._viz3dWaterbodyPatch;
    const patchWaterbody=!!(updating&&request?.main?.mode==='waterbody'&&request.main.updateKey&&dynamicIndices.length&&
        priorPatch?.key===request.main.updateKey&&
        priorPatch.topologyKey===request.main.topologyKey&&
        priorPatch.schema===traceSchema&&
        priorPatch.width===element.clientWidth&&priorPatch.height===element.clientHeight&&
        window.Plotly?.update);
    if(!request?.section)window.PlaybackPerformance?.stage(request.playbackPerf,'plotSchema',viz3dNow()-plotSchemaStartedAt);
    const applyWaterbodyPatch=async()=>{
        const patch=viz3dWaterbodyRestyleGroups(element.data,traces);
        if(patch===null)throw new Error('waterbody trace structure changed');
        await window.Plotly.update(container,patch.update,viz3dWaterbodyRelayout(layout),patch.indices);
    };
    let plotting;
    const plotStartedAt=viz3dNow();
    if(!request?.section) {
        const plotPrepareMs=Math.max(0,plotStartedAt-plotPreparationStartedAt);
        window.PlaybackPerformance?.stage(request.playbackPerf,'frameBuild',frameBuildMs);
        window.PlaybackPerformance?.stage(request.playbackPerf,'plotPrepare',plotPrepareMs);
        // Keep assembly as active synchronous work; serialized Plotly wait is
        // reported separately so cadence gaps are not mistaken for CPU cost.
        window.PlaybackPerformance?.stage(request.playbackPerf,'assemble',frameBuildMs+plotPrepareMs);
    }
    if(patchWaterbody)plotting=applyWaterbodyPatch().catch(()=>Plotly.react(container,traces,layout,config));
    else plotting=updating ? Plotly.react(container,traces,layout,config) : Plotly.newPlot(container,traces,layout,config);
    viz3dTrace('draw-start',element,request,{input:layout.scene?.camera});
    return Promise.resolve(plotting).then(result=>{
        if(!request?.section)window.PlaybackPerformance?.stage(request?.playbackPerf,'draw',viz3dNow()-plotStartedAt);
        viz3dTrace('draw-finish',element,request,{layout:element?._fullLayout?.scene?.camera});
        if(!viz3dCurrent(request)) return;
        if(element && !request?.section) {
            element._viz3dRenderedLayout=layout;
            element._viz3dPlotConfig=config;
            element._viz3dAspectRatioState=request._viz3dAspectRatioState || null;
            if(request?.main?.mode==='waterbody'&&request.main.updateKey)element._viz3dWaterbodyPatch={
                key:request.main.updateKey,topologyKey:request.main.topologyKey,schema:traceSchema,
                width:element.clientWidth,height:element.clientHeight};
            else element._viz3dWaterbodyPatch=null;
        }
        if(element && !request?.section)element._viz3dResponsiveSource=responsiveSource;
        if(element && !request?.section) element._viz3dMainView=request?.main ? {...request.main,request} : null;
        // Audit the frame that just finished drawing; begin() retires the old view.
        if(element && !request?.section)viz3dRefreshTraceAudit(element);
        // Plotly's layout camera can lag behind WebGL wheel/orbit gestures.
        // Its public relayout event carries the camera actually shown on screen.
        if(element?.on && !request?.section && (!updating || !element._viz3dCameraListener)) {
            const listener=(event,continuous=false)=>{
                viz3dTrace('event',element,null,{event});
                const graphCase=element._viz3dLastPlot?.caseKey;
                if(graphCase!==undefined && graphCase!==_viz3dCameraCase)return;
                if(Object.prototype.hasOwnProperty.call(event,'scene.aspectratio')) {
                    const previous=element._viz3dAspectRatioState,aspect=event['scene.aspectratio'];
                    if(previous?.baseline) {
                        const scale=viz3dAspectZoomScale(aspect,previous.baseline);
                        // Plotly wheel gestures report both camera and aspectratio.
                        // A scale away from the fitted baseline is a real zoom. An
                        // orbit can report the baseline again while crossing a pole;
                        // retain the last wheel scale in that case. Explicit reset
                        // clears it through set3DCamera('reset').
                        if(Math.abs(scale-1)>1e-9||!event['scene.camera'])
                            element._viz3dAspectRatioState={...previous,scale};
                    }
                }
                if(event['scene.camera']) {
                    const camera=event['scene.camera'];
                    const accepted=viz3dClampCamera(camera);
                    if(!accepted)return;
                    _viz3dCamera=JSON.parse(JSON.stringify(accepted));
                    viz3dRememberCameraHeading(_viz3dCamera);
                    viz3dSyncElevationControl(_viz3dCamera);
                    viz3dSyncVerticalPositionControl(_viz3dCamera);
                    viz3dSyncCameraAxes(element,_viz3dCamera);
                    viz3dApplyUndersideMode(element,_viz3dCamera);
                }
            };
            element.on('plotly_relayout',event=>listener(event,false));
            element.on('plotly_relayouting',event=>listener(event,true));
            element._viz3dCameraListener=listener;
        }
        return result;
    });
    };
    return viz3dQueueDraw(element,operation);
}

/** One location line in the main physical view; coordinate guesses are forbidden. */
function set3DSectionIndicator(axis,index,data) {
    const token=++_viz3dSectionIndicatorToken;
    const container=document.getElementById('viz3d-plotly');
    const view=container?._viz3dMainView;
    const operation=async()=>{
        if(token!==_viz3dSectionIndicatorToken || !container) return false;
        const buildLine=()=>{
        if(token!==_viz3dSectionIndicatorToken || !['xz','yz'].includes(axis) || !data
            || !view || container._viz3dMainView!==view || !viz3dCurrent(view.request)
            || !Number.isInteger(index) || index<0) return false;
        if((data.name && data.name!==view.request.varName)
            || (Number.isInteger(data.time) && data.time!==view.request.timestep)
            || (data.axis && data.axis!==axis) || (Number.isInteger(data.index) && data.index!==index)) return false;
        const coordinates=viz3dCoordinates(view.data),sectionCoordinates=viz3dCoordinates(data);
        const perpendicular=axis==='xz'?'y':'x',centers=axis==='xz'?view.data.yc:view.data.xc;
        const ordinals=view.data[perpendicular];
        const slot=Array.isArray(ordinals) ? ordinals.indexOf(index)
            : !viz3dSampledBoundary(view.data) ? index : -1;
        let fixed;
        if(coordinates.index) fixed=index;
        else {
            if(sectionCoordinates.index || coordinates.units!==sectionCoordinates.units) return false;
            if(Number.isFinite(data.fixed_coordinate) && data.fixed_coordinate_units===coordinates.units)
                fixed=data.fixed_coordinate;
            else if(slot>=0 && slot<centers?.length) fixed=centers[slot];
        }
        if(!Number.isFinite(fixed) || !Array.isArray(data.horizontal) || !data.horizontal.length) return false;
        const n=data.horizontal.length;
        // Index mode uses the complete section's original column/row ordinals,
        // never its physical coordinates or the main volume's sampled slots.
        const edges=coordinates.index ? Array.from({length:n+1},(_,h)=>h-.5) : data.horizontal_edges;
        if(!Array.isArray(edges) || edges.length!==n+1 || !edges.every(Number.isFinite)) return false;
        const line={type:'scatter3d',mode:'lines',name:`${axis.toUpperCase()} 剖面位置 · ${axis==='xz'?'j':'i'}=${index}`,
            x:[],y:[],z:[],line:{color:'#a14923',width:6,dash:'dash'},
            meta:{section_indicator:true},showlegend:true,
            hovertemplate:viz3dHorizontalHover(view.data)+`<extra>${axis.toUpperCase()} · ${axis==='xz'?'j':'i'}=${index} (0-based)</extra>`};
        for(let h=0;h<n;h++) {
            const wet=Array.isArray(data.wet) ? data.wet[h]===true
                : Number.isFinite(data.bottom?.[h]) && data.bottom[h]>0;
            if(!wet) continue;
            for(const value of [edges[h],edges[h+1],null]) {
                line.x.push(value===null?null:axis==='xz'?value:fixed);
                line.y.push(value===null?null:axis==='xz'?fixed:value);
                line.z.push(value===null?null:0);
            }
        }
        if(!line.x.length) return false;
        return viz3dTranslateText(line);
        };
        const line=buildLine();
        const traces=(container.data || []).filter(t=>!t.meta?.section_indicator);
        if(!line && traces.length===(container.data || []).length)return false;
        if(!window.Plotly?.react)return false;
        if(line)traces.push(line);
        // Trace-only add/delete redraw from the last saved layout and can undo
        // an orbit. Replace the indicator once with the current live camera.
        viz3dCaptureCamera(container,view?.request);
        const layout=container.layout || container._viz3dRenderedLayout;
        if(!layout?.scene)return false;
        const camera=_viz3dCamera || layout.scene.camera;
        viz3dTrace('indicator-replace-before',container,view?.request,{input:camera});
        await window.Plotly.react(container,traces,{...layout,scene:{...layout.scene,camera}},container._viz3dPlotConfig);
        viz3dTrace('indicator-replace-after',container,view?.request);
        return !!line && token===_viz3dSectionIndicatorToken && container._viz3dMainView===view && viz3dCurrent(view.request);
    };
    const pending=_viz3dIndicatorQueue.then(operation,operation);
    // Keep later refreshes usable after an optional WebGL trace mutation fails.
    _viz3dIndicatorQueue=pending.catch(()=>false);
    return _viz3dIndicatorQueue;
}
if(typeof window!=='undefined') window.set3DSectionIndicator=set3DSectionIndicator;

/**
 * 把 sigma 坐标换算成「自水面算起的深度占比」depthFrac∈[0,1]（0=水面，1=湖底）。
 * GETM 的层序 k=0 为最底层：sigma=-1 对应湖底、sigma=0 对应水面。
 * 不同案例的 sigma 取值约定不同（[-1,0] / [0,1] / [-1,1]），保留约定范围内的
 * 实际层中心位置；未知约定才按实际极值归一。0 在水面，1 在湖底。
 */
function sigmaToFraction(sigma) {
    let sMax = -Infinity, sMin = Infinity;
    (sigma || []).forEach(s => {
        if (typeof s === 'number' && isFinite(s)) { if (s > sMax) sMax = s; if (s < sMin) sMin = s; }
    });
    if (!isFinite(sMax)) {
        return (sigma || []).map((_, k) => 1 - (k + 0.5) / Math.max(1, (sigma || []).length));
    }
    // Preserve layer centers for the usual [-1,0] convention. Normalizing
    // extrema would falsely move the first/last centers onto the bed/surface.
    if (sMin < 0 && sMin >= -1 && sMax <= 0) return sigma.map(s => Number.isFinite(s) ? -s : null);
    if (sMin >= 0 && sMax <= 1) return sigma.map(s => Number.isFinite(s) ? 1 - s : null);
    if (sMin >= -1 && sMax <= 1) return sigma.map(s => Number.isFinite(s) ? (1-s)/2 : null);
    const span = (sMax - sMin) || 1;
    return (sigma || []).map(s => {
        if (typeof s !== 'number' || !isFinite(s)) return 1;
        return (sMax - s) / span;      // sigma=sMax(水面) → 0；sigma=sMin(湖底) → 1
    });
}

/**
 * 根据网格中心计算单元边缘。湿单元边界用于湖岸剖面，不连接对角湿格。
 */
function lakeCellEdges(centers) {
    if (!centers.length || centers.some(v => !Number.isFinite(v))) return [];
    if (centers.length === 1) return [centers[0] - 0.5, centers[0] + 0.5];
    return [centers[0] - (centers[1]-centers[0])/2,
        ...centers.slice(1).map((v,i) => (v + centers[i])/2),
        centers.at(-1) + (centers.at(-1)-centers.at(-2))/2];
}

function lakeVerticalScale(xc, yc, bottom, requested) {
    if (Number.isFinite(Number(requested)) && Number(requested) > 0) return Number(requested);
    const depths = (bottom || []).flat().filter(h => Number.isFinite(h) && h > 0);
    if (!depths.length) return 1;
    const viewData={xc,yc,bottom},xRange=lakeViewAxisRange(viewData,lakeCellEdges(xc),'x'),
        yRange=lakeViewAxisRange(viewData,lakeCellEdges(yc),'y');
    const span=Math.max(xRange?.[1]-xRange?.[0]||0,yRange?.[1]-yRange?.[0]||0,
        Math.abs(xc.at(-1)-xc[0]),Math.abs(yc.at(-1)-yc[0]),1);
    // A restrained 3% display relief keeps shallow water legible at the default
    // oblique camera without turning broad lakes into steep-sided basins. This
    // changes presentation only; explicit user scales remain untouched above,
    // and the physical depth axis remains in metres.
    return Math.max(1, Math.min(2000, Math.round(span * 0.03 / Math.max(...depths) * 10)/10));
}

// Cell-edge geometry derives exclusively from supplied bathymetry. Corner
// depths average touching wet cells for a continuous bed; no smoothing of the
// wet mask, no triangles across land, and no inferred geographic outline.
function lakeCornerCells(u,v,i,j,valid) {
    const candidates=[[u-1,v-1],[u,v-1],[u,v],[u-1,v]].filter(([x,y])=>valid(x,y));
    const selected=[[i,j]],seen=new Set([`${i},${j}`]);
    for(let n=0;n<selected.length;n++)for(const [x,y] of candidates){
        if(seen.has(`${x},${y}`)||Math.abs(x-selected[n][0])+Math.abs(y-selected[n][1])!==1)continue;
        seen.add(`${x},${y}`);selected.push([x,y]);
    }
    return selected;
}
function lakeDisplayTopologyValid(topology, nx, ny) {
    if(!topology || topology.contract!=='sampled-wet-topology-v1' ||
        !Array.isArray(topology.source_shape) || topology.source_shape.length!==2 ||
        !topology.source_shape.every(Number.isInteger) ||
        !Array.isArray(topology.x_indices) || topology.x_indices.length!==nx ||
        !Array.isArray(topology.y_indices) || topology.y_indices.length!==ny ||
        !Array.isArray(topology.x_edges) || topology.x_edges.length!==nx+1 ||
        !Array.isArray(topology.y_edges) || topology.y_edges.length!==ny+1 ||
        !/^sha256:[a-f0-9]{64}$/.test(topology.grid_hash || '') ||
        !Number.isInteger(topology.mask_cells_examined) ||
        topology.mask_cells_examined!==topology.source_shape[0]*topology.source_shape[1]) return false;
    const indices=(values,size)=>values[0]===0 && values.every((v,i)=>Number.isInteger(v)&&v>=0&&v<size&&(i===0||v>values[i-1]));
    const edges=values=>values.every(Number.isFinite) && (values.length<2 || values.slice(1).every((v,i)=>v!==values[i]));
    if(!indices(topology.x_indices,topology.source_shape[1]) || !indices(topology.y_indices,topology.source_shape[0]) ||
        !edges(topology.x_edges) || !edges(topology.y_edges)) return false;
    for(let j=0;j<ny;j++) {
        if(!Array.isArray(topology.cell_status?.[j]) || topology.cell_status[j].length!==nx ||
            !Array.isArray(topology.wet_mask?.[j]) || topology.wet_mask[j].length!==nx ||
            !Array.isArray(topology.land_mask?.[j]) || topology.land_mask[j].length!==nx ||
            !Array.isArray(topology.wall_sides?.[j]) || topology.wall_sides[j].length!==nx) return false;
        for(let i=0;i<nx;i++) {
            const status=topology.cell_status[j][i];
            if(!['wet','dry','mixed','unknown'].includes(status) ||
                topology.wet_mask[j][i] !== (status==='wet') || topology.land_mask[j][i] !== (status==='dry') ||
                !Array.isArray(topology.wall_sides[j][i]) || topology.wall_sides[j][i].length!==4 ||
                !topology.wall_sides[j][i].every(v=>typeof v==='boolean')) return false;
        }
    }
    return true;
}
function lakeDisplayTopologyRequired(data) {
    const stride=data?.sampling_stride;
    return Array.isArray(stride) && (Number(stride[1])>1 || Number(stride[2])>1);
}
function lakeDisplayTopologyReady(data) {
    const topology=data?.display_topology;
    if(topology==null) return !lakeDisplayTopologyRequired(data);
    return lakeDisplayTopologyValid(topology,data?.xc?.length,data?.yc?.length) &&
        topology.source_shape[0]===(data.full_shape?.[1] ?? topology.source_shape[0]) &&
        topology.source_shape[1]===(data.full_shape?.[2] ?? topology.source_shape[1]) &&
        (!data.x || topology.x_indices.length===data.x.length&&topology.x_indices.every((v,i)=>v===data.x[i])) &&
        (!data.y || topology.y_indices.length===data.y.length&&topology.y_indices.every((v,i)=>v===data.y[i]));
}
function buildLakeGeometry(xc, yc, bottom, ve = 1, displayTopology=null) {
    const nx = xc.length, ny = yc.length;
    if(displayTopology!==null && !lakeDisplayTopologyValid(displayTopology,nx,ny)) return null;
    const contract=displayTopology;
    const xe = contract?.x_edges?.length===nx+1 ? contract.x_edges : lakeCellEdges(xc);
    const ye = contract?.y_edges?.length===ny+1 ? contract.y_edges : lakeCellEdges(yc);
    if (!xe.length || !ye.length || !bottom || bottom.length !== ny || bottom.some(row => !row || row.length !== nx)) return null;
    const wet = (i,j) => i>=0 && j>=0 && i<nx && j<ny && Number.isFinite(bottom[j][i]) && bottom[j][i]>0 &&
        (!contract || contract.wet_mask[j][i]===true);
    const corner = (u,v,i,j) => {
        const hs = lakeCornerCells(u,v,i,j,wet).map(([x,y])=>bottom[y][x]);
        return hs.reduce((a,b)=>a+b,0)/hs.length;
    };
    const floor = {x:[],y:[],z:[],intensity:[],i:[],j:[],k:[],cell:[]};
    const surface = {x:[],y:[],z:[],i:[],j:[],k:[],cell:[]};
    const walls = {px:[],py:[],pz:[],cint:[],i:[],j:[],k:[]};
    const shoreline = {x:[],y:[],z:[]};
    for(let j=0;j<ny;j++) for(let i=0;i<nx;i++) {
        if(!wet(i,j)) continue;
        const points = [[i,j],[i+1,j],[i+1,j+1],[i,j+1]];
        const base = floor.x.length;
        for(const [u,v] of points) {
            const h = corner(u,v,i,j);
            floor.x.push(xe[u]); floor.y.push(ye[v]); floor.z.push(-h*ve); floor.intensity.push(h);
            surface.x.push(xe[u]); surface.y.push(ye[v]); surface.z.push(0);
            floor.cell.push([i,j]); surface.cell.push([i,j]);
        }
        for(const mesh of [floor,surface]) {mesh.i.push(base,base); mesh.j.push(base+1,base+2); mesh.k.push(base+2,base+3);}
        const sides = [[0,1,i,j-1],[1,2,i+1,j],[2,3,i,j+1],[3,0,i-1,j]];
        for(let side=0;side<sides.length;side++) {
            const [a,b,ni,nj]=sides[side];
            if(contract ? contract.wall_sides?.[j]?.[i]?.[side]!==true : wet(ni,nj)) continue;
            const [u0,v0]=points[a], [u1,v1]=points[b], h0=corner(u0,v0,i,j),h1=corner(u1,v1,i,j);
            const w=walls.px.length;
            walls.px.push(xe[u0],xe[u0],xe[u1],xe[u1]); walls.py.push(ye[v0],ye[v0],ye[v1],ye[v1]);
            walls.pz.push(0,-h0*ve,0,-h1*ve); walls.cint.push(0,h0,0,h1);
            walls.i.push(w,w); walls.j.push(w+1,w+3); walls.k.push(w+3,w+2);
            shoreline.x.push(xe[u0],xe[u1],null); shoreline.y.push(ye[v0],ye[v1],null); shoreline.z.push(0,0,null);
        }
    }
    const maxDepth=bottom.reduce((max,row)=>row.reduce((m,h)=>Number.isFinite(h) ? Math.max(m,h) : m,max),0);
    return floor.i.length ? {floor,surface,walls,shoreline,ve,nx,ny,maxDepth,displayTopology:contract} : null;
}
function lakeTopologyBits(mask,predicate) {
    if(!Array.isArray(mask))return '';
    return mask.map(row=>Array.from(row || [],predicate).map(value=>value?'1':'0').join('')).join('/');
}
function lakeGeometryForFrame(xc,yc,bottom,ve,displayTopology,validGeometry=null,staticGeometryKey=null) {
    // The bathymetry/wet topology is usually invariant across playback frames.
    // An exact content key avoids stale geometry when water depth or masks do
    // change, while reusing the expensive cell/wall construction when it does not.
    const key=JSON.stringify([xc,yc,bottom,ve,displayTopology]);
    if(_viz3dLakeGeometryCache.has(key)) {
        const cached=_viz3dLakeGeometryCache.get(key);
        _viz3dLakeGeometryCache.delete(key);_viz3dLakeGeometryCache.set(key,cached);
        return cached;
    }
    const geometry=buildLakeGeometry(xc,yc,bottom,ve,displayTopology);
    if(geometry) {
        geometry.playbackCacheKey=key;
        // Water depth is frame-dependent, but a Plotly mesh can be updated in
        // place while its coordinates/connectivity and wet-cell membership are
        // stable. Keep that compatibility key separate from the exact geometry
        // cache key above; never use it to reuse old depth or scalar values.
        const wet=lakeTopologyBits(bottom,value=>Number.isFinite(value)&&value>0);
        const valid=lakeTopologyBits(validGeometry,value=>value!==false);
        // The API revision already identifies static axes, bathymetry and
        // sampled display topology. Only compact frame-varying masks are
        // inspected here; depth magnitudes never enter this key.
        const staticKey=staticGeometryKey || JSON.stringify([xc,yc,displayTopology]);
        geometry.playbackTopologyKey=JSON.stringify([staticKey,ve,wet,valid]);
        _viz3dLakeGeometryCache.set(key,geometry);
        while(_viz3dLakeGeometryCache.size>3)_viz3dLakeGeometryCache.delete(_viz3dLakeGeometryCache.keys().next().value);
    }
    return geometry;
}

// Contours intersect the actual bed triangles, so islands, disconnected wet
// cells and narrow channels use exactly the same mask as the displayed bed.
function lakeDepthLevels(maxDepth) {
    if(!Number.isFinite(maxDepth) || maxDepth<=0) return [];
    const raw=maxDepth/6, magnitude=10**Math.floor(Math.log10(raw));
    const step=[1,2,2.5,5,10].map(v=>v*magnitude).find(v=>v>=raw);
    return Array.from({length:Math.ceil(maxDepth/step)-1},(_,i)=>(i+1)*step);
}

function buildLakeContours(geometry, levels) {
    const line={x:[],y:[],z:[],depth:[]}, bed=geometry.floor;
    for(const depth of levels) for(let t=0;t<bed.i.length;t++) {
        const vertices=[bed.i[t],bed.j[t],bed.k[t]], points=[];
        for(let a=0;a<3;a++) {
            const u=vertices[a],v=vertices[(a+1)%3],h0=bed.intensity[u],h1=bed.intensity[v];
            // Half-open interval handles vertices exactly on a contour once.
            if(!((h0<=depth && h1>depth)||(h1<=depth && h0>depth))) continue;
            const f=(depth-h0)/(h1-h0);
            points.push([bed.x[u]+f*(bed.x[v]-bed.x[u]),bed.y[u]+f*(bed.y[v]-bed.y[u])]);
        }
        if(points.length!==2 || (points[0][0]===points[1][0] && points[0][1]===points[1][1])) continue;
        for(const p of points) {line.x.push(p[0]);line.y.push(p[1]);line.z.push(-depth*geometry.ve);line.depth.push(depth);}
        line.x.push(null);line.y.push(null);line.z.push(null);line.depth.push(null);
    }
    return line;
}

function buildLakeGrid(geometry, options={}) {
    const network=buildDisplayNetwork([geometry.floor],options);
    return {...network.lines,nodes:network.nodes,stats:network.stats};
}

// Triangle refinement uses the same barycentric lattice for every wet cell.
// Cache only this small, immutable subdivision pattern; frame-specific x/y/z,
// wet-cell membership, layer depths and edge deduplication remain live inputs.
const _viz3dTriangleNetworkTemplates=new Map();
function lakeTriangleNetworkTemplate(subdivisions) {
    const refinement=Math.max(1,Math.min(6,Math.round(Number(subdivisions)||1)));
    if(_viz3dTriangleNetworkTemplates.has(refinement))return _viz3dTriangleNetworkTemplates.get(refinement);
    const lattice=new Map(),points=[],edges=[],triangles=[],key=(i,j)=>`${i},${j}`;
    const point=(i,j)=>{
        const id=key(i,j);if(lattice.has(id))return lattice.get(id);
        const t=i/refinement,u=j/refinement,v=1-t-u,index=points.length;
        points.push(Object.freeze([v,t,u]));lattice.set(id,index);return index;
    };
    for(let i=0;i<refinement;i++)for(let j=0;j<refinement-i;j++){
        const p=point(i,j),pb=point(i+1,j),pc=point(i,j+1);
        triangles.push(Object.freeze([p,pb,pc]));
        edges.push(Object.freeze([p,pb]),Object.freeze([pb,pc]),Object.freeze([pc,p]));
        if(i+j<refinement-1){const pd=point(i+1,j+1);triangles.push(Object.freeze([pb,pd,pc]));edges.push(Object.freeze([pb,pd]),Object.freeze([pd,pc]));}
    }
    const template=Object.freeze({points:Object.freeze(points),edges:Object.freeze(edges),triangles:Object.freeze(triangles)});
    _viz3dTriangleNetworkTemplates.set(refinement,template);
    return template;
}

// Build a true display wireframe from native wet-cell corners. Faces remain
// independent: choosing a network never changes the colored mesh topology.
function buildDisplayNetwork(meshes,options={}) {
    const lines={x:[],y:[],z:[]},surfaceLines={x:[],y:[],z:[]},surfaceLinesByLayer=[],layerLines={x:[],y:[],z:[]},nodes={x:[],y:[],z:[]},edgeKeys=new Set(),nodeKeys=new Set();
    // Triangle subdivision reuses each sampled point in several neighboring
    // micro-edges. Canonicalize its 3D/XY key once per frame instead of
    // repeatedly formatting the same coordinates for every edge and node.
    const pointKeys=new WeakMap(),horizontalPointKeys=new WeakMap();
    const pointKey=point=>{
        let key=pointKeys.get(point);
        if(key===undefined){key=point.map(v=>Number(v).toPrecision(14)).join(',');pointKeys.set(point,key);}
        return key;
    };
    const horizontalPointKey=point=>{
        let key=horizontalPointKeys.get(point);
        if(key===undefined){key=`${Number(point[0]).toPrecision(14)},${Number(point[1]).toPrecision(14)}`;horizontalPointKeys.set(point,key);}
        return key;
    };
    const mode=options.mode || 'orthogonal',requestedStride=Math.max(1,Math.round(Number(options.density)||1));
    let subdivisions=mode==='triangles'?Math.max(1,Math.min(6,Math.round(Number(options.refinement)||4))):1;
    if(['hidden','continuous'].includes(mode))return {lines,surfaceLines,surfaceLinesByLayer,layerLines,nodes};
    const maxSegments=60000,cellCount=(meshes || []).reduce((sum,mesh)=>sum+Math.floor((mesh?.x?.length || 0)/4),0);
    const estimatedSegments=()=>cellCount*3*subdivisions*(subdivisions+1)
        +Math.max(0,(meshes?.length || 0)-1)*cellCount*(subdivisions+1)*(subdivisions+2);
    while(estimatedSegments()>maxSegments&&subdivisions>1)subdivisions--;
    let stride=requestedStride;
    const selectedCellFraction=value=>2/value-1/(value*value);
    while(estimatedSegments()*selectedCellFraction(stride)>maxSegments)stride++;
    let activeSurfaceLayer=0;
    const addNode=(point)=>{const key=pointKey(point);if(nodeKeys.has(key))return;nodeKeys.add(key);nodes.x.push(point[0]);nodes.y.push(point[1]);nodes.z.push(point[2]);};
    const addEdge=(a,b,layerLink=false)=>{
        if(!a||!b||!Number.isFinite(a[0])||!Number.isFinite(a[1])||!Number.isFinite(a[2])||
            !Number.isFinite(b[0])||!Number.isFinite(b[1])||!Number.isFinite(b[2]))return;
        const key=[pointKey(a),pointKey(b)].sort().join('|');
        if(edgeKeys.has(key))return;edgeKeys.add(key);
        const destination=layerLink?layerLines:(surfaceLinesByLayer[activeSurfaceLayer] ||= {x:[],y:[],z:[]});
        for(const p of [a,b,null])for(const target of [lines,destination]){
            target.x.push(p?.[0]??null);target.y.push(p?.[1]??null);target.z.push(p?.[2]??null);
        }
        if(!layerLink)for(const p of [a,b,null]){surfaceLines.x.push(p?.[0]??null);surfaceLines.y.push(p?.[1]??null);surfaceLines.z.push(p?.[2]??null);}
        addNode(a);addNode(b);
    };
    const addTriangleNetwork=(a,b,c)=>{
        const template=lakeTriangleNetworkTemplate(subdivisions),networkEdges=[];
        const samples=template.points.map(([v,t,u])=>a.map((value,q)=>value*v+b[q]*t+c[q]*u));
        for(const [from,to] of template.edges){const edge=[samples[from],samples[to]];networkEdges.push(edge);addEdge(...edge);}
        return {samples,edges:networkEdges};
    };
    const cellMaps=[];let networkQuadCells=0,triangleSourceCells=0,triangleFaces=0;
    const sourceQuadCells=(meshes||[]).reduce((total,mesh)=>total+Math.floor((mesh?.x?.length||0)/4),0);
    for(let meshIndex=0;meshIndex<(meshes || []).length;meshIndex++) {
        const mesh=meshes[meshIndex];activeSurfaceLayer=meshIndex;
        const cells=new Map();
        for(let q=0;q+3<mesh.x.length;q+=4) {
            const cell=mesh.cell?.[q];if(!cell)continue;const [i,j]=cell,key=`${i},${j}`;
            if(i%stride!==0&&j%stride!==0)continue;
            const points=Array.from({length:4},(_,n)=>[mesh.x[q+n],mesh.y[q+n],mesh.z[q+n]]);
            networkQuadCells++;
            const networkPoints=[],networkEdges=[];
            cells.set(key,{i,j,points,networkPoints,networkEdges});
            if(mode==='triangles'&&i%stride===0&&j%stride===0){
                triangleSourceCells++;
                const halves=(i+j)%2===0?[[0,1,2],[0,2,3]]:[[0,1,3],[1,2,3]];
                for(const [a,b,c] of halves){
                    const network=addTriangleNetwork(points[a],points[b],points[c]);
                    triangleFaces+=_viz3dTriangleNetworkTemplates.get(subdivisions).triangles.length;
                    networkPoints.push(...network.samples);networkEdges.push(...network.edges);
                }
            }else{
                const keep=[j%stride===0,(i+1)%stride===0,(j+1)%stride===0,i%stride===0];
                for(const [a,b,n] of [[0,1,0],[1,2,1],[2,3,2],[3,0,3]])if(keep[n])addEdge(points[a],points[b]);
            }
        }
        cellMaps.push(cells);
    }
    // Consecutive sigma planes connect only matching corners of the same wet
    // native cell; a dry or invalid cell can never create a vertical strut.
    for(let layer=0;layer+1<cellMaps.length;layer++)for(const [key,lower] of cellMaps[layer]) {
        const upper=cellMaps[layer+1].get(key);if(!upper)continue;
        if(mode==='triangles'&&lower.networkPoints.length===upper.networkPoints.length){
            for(let point=0;point<lower.networkPoints.length;point++)addEdge(lower.networkPoints[point],upper.networkPoints[point],true);
            const sideEdges=new Set();
            if(lower.networkEdges.length===upper.networkEdges.length)for(let edge=0;edge<lower.networkEdges.length;edge++){
                const [from,to]=lower.networkEdges[edge],[upperFrom,upperTo]=upper.networkEdges[edge];
                const fromKey=horizontalPointKey(from),toKey=horizontalPointKey(to),edgeKey=[fromKey,toKey].sort().join('|');
                if(sideEdges.has(edgeKey))continue;
                sideEdges.add(edgeKey);
                // Triangulate each vertical prism side. Vertical links alone
                // leave rectangular gaps through the sigma-column walls. Use
                // one stable diagonal per micro-edge so shared facets do not cross.
                addEdge(fromKey<toKey?from:to,fromKey<toKey?upperTo:upperFrom,true);
            }
        }else for(let corner=0;corner<4;corner++)addEdge(lower.points[corner],upper.points[corner],true);
    }
    return {lines,surfaceLines,surfaceLinesByLayer,layerLines,nodes,stats:{segments:Math.floor(lines.x.length/3),surfaceSegments:Math.floor(surfaceLines.x.length/3),layerSegments:Math.floor(layerLines.x.length/3),maxSegments,refinement:subdivisions,density:stride,
        sourceQuadCells,networkQuadCells,triangleSourceCells,triangleFaces,triangulation:'each valid wet structured quad split by stable (i+j) diagonal; no solver-native triangle cells'}};
}

// No DEM is available. This neutral display plane represents only explicitly
// dry bathymetry cells. A null/invalid depth never establishes land elevation.
function buildLakeLand(data,z=0) {
    const mesh={x:[],y:[],z:[],i:[],j:[],k:[],cell:[]};
    const contract=data.display_topology?.contract==='sampled-wet-topology-v1' ? data.display_topology : null;
    const xe=contract?.x_edges?.length===data.xc?.length+1?contract.x_edges:lakeCellEdges(data.xc || []);
    const ye=contract?.y_edges?.length===data.yc?.length+1?contract.y_edges:lakeCellEdges(data.yc || []);
    if(!xe.length || !ye.length || !Number.isFinite(z))return mesh;
    const ny=ye.length-1,nx=xe.length-1,wet=(i,j)=>contract
        ? contract.wet_mask?.[j]?.[i]===true
        : (data.wet_mask?.[j]?.[i]===true||data.wetMask?.[j]?.[i]===true||
           (Number.isFinite(data.bottom?.[j]?.[i])&&data.bottom[j][i]>0));
    const land=(i,j)=>contract?contract.land_mask?.[j]?.[i]===true:data.dry_mask?.[j]?.[i]===true;
    for(let j=0;j<ye.length-1;j++)for(let i=0;i<xe.length-1;i++){
        // Show only explicitly dry cells adjacent to the actual wet topology.
        // This gives the lake a geographic context without turning the entire
        // rectangular model domain into a fabricated land surface.
        if(!land(i,j))continue;
        let nearWet=false;
        for(let dj=-1;dj<=1&&!nearWet;dj++)for(let di=-1;di<=1;di++){
            if((di!==0||dj!==0)&&wet(i+di,j+dj)){nearWet=true;break;}
        }
        if(!nearWet)continue;
        const b=mesh.x.length;
        for(const [u,v] of [[i,j],[i+1,j],[i+1,j+1],[i,j+1]]){
            mesh.x.push(xe[u]);mesh.y.push(ye[v]);mesh.z.push(z);mesh.cell.push([i,j]);
        }
        mesh.i.push(b,b);mesh.j.push(b+1,b+2);mesh.k.push(b+2,b+3);
    }
    return mesh;
}

// Smooth only the displayed shoreline polyline. Chaikin-style passes soften
// sampled grid corners; this is a display generalization, not a surveyed
// coastline. Native wet/dry topology and scientific coordinates are untouched.
function smoothLakeShoreline(raw, passes=4) {
    const edges=[],outgoing=new Map(),key=p=>p.map(v=>Number(v).toPrecision(14)).join(',');
    for(let q=0;q+2<raw.x.length;q+=3){
        if(!Number.isFinite(raw.x[q])||!Number.isFinite(raw.x[q+1]))continue;
        const a=[raw.x[q],raw.y[q],raw.z[q]],b=[raw.x[q+1],raw.y[q+1],raw.z[q+1]],edge={a,b,used:false};
        const k=key(a);if(!outgoing.has(k))outgoing.set(k,[]);outgoing.get(k).push(edge);edges.push(edge);
    }
    const smooth={x:[],y:[],z:[]};
    const appendPath=(path,closed)=>{
        if(path.length<2)return;
        let points=path;
        if(closed&&key(path[0])===key(path.at(-1)))points=path.slice(0,-1);
        if(points.length<3)return;
        const count=Number.isInteger(passes)?Math.max(0,Math.min(5,passes)):3;
        let current=points;
        for(let step=0;step<count;step++){
            const next=[];
            if(closed){
                for(let i=0;i<current.length;i++){
                    const a=current[i],b=current[(i+1)%current.length];
                    next.push(a.map((v,k)=>.75*v+.25*b[k]),a.map((v,k)=>.25*v+.75*b[k]));
                }
            }else{
                next.push(current[0]);
                for(let i=0;i<current.length-1;i++){
                    const a=current[i],b=current[i+1];
                    next.push(a.map((v,k)=>.75*v+.25*b[k]),a.map((v,k)=>.25*v+.75*b[k]));
                }
                next.push(current.at(-1));
            }
            current=next;
        }
        if(closed&&current.length)current.push(current[0]);
        for(const p of current){smooth.x.push(p[0]);smooth.y.push(p[1]);smooth.z.push(p[2]);}
        smooth.x.push(null);smooth.y.push(null);smooth.z.push(null);
    };
    const trace=first=>{
        const path=[first.a,first.b];first.used=true;let guard=0;
        while(guard++<=edges.length){
            const end=path.at(-1),candidates=(outgoing.get(key(end))||[]).filter(edge=>!edge.used);
            if(!candidates.length||key(end)===key(path[0]))break;
            const prev=path.at(-2),vx=end[0]-prev[0],vy=end[1]-prev[1];
            candidates.sort((a,b)=>{
                const angle=edge=>{
                    const dx=edge.b[0]-end[0],dy=edge.b[1]-end[1];
                    return Math.atan2(vx*dy-vy*dx,vx*dx+vy*dy);
                };
                return angle(b)-angle(a);
            });
            const next=candidates[0];next.used=true;path.push(next.b);
        }
        appendPath(path,key(path[0])===key(path.at(-1)));
    };
    for(const edge of edges)if(!edge.used)trace(edge);
    return smooth;
}

// Return a polygon only when its declared coordinate contract and every
// available wet/dry centre agree with the unchanged native mask. This is a
// display clip contract, never a replacement for scientific wet topology.
function lakeValidatedDisplayBoundary(geometry,data={}) {
    const boundary=data?.authoritative_boundary,groups=boundary?.projected_polygons;
    if(!Array.isArray(groups)||!groups.length)return null;
    const hasSourceCrs=typeof boundary.source_crs==='string'?Boolean(boundary.source_crs.trim()):
        Boolean(boundary.source_crs?.wkt);
    const unvalidatedProxy=boundary.provenance?.status==='proxy-display-geometry-not-scientifically-validated';
    const explicitCrs=!unvalidatedProxy&&hasSourceCrs&&Boolean(boundary.projected_crs?.wkt);
    const declaredGridSpace=boundary.coordinate_space==='bathymetry_projected_grid_coordinates';
    if(!explicitCrs&&!declaredGridSpace)return null;
    if(typeof boundary.provenance?.source!=='string'||!boundary.provenance.source.trim())return null;
    const boundaryVertexCount=groups.reduce((sum,group)=>sum+(group?.outer?.length||0)+
        (group?.holes||[]).reduce((count,ring)=>count+(ring?.length||0),0),0);
    if(boundaryVertexCount>20000)return null;
    const gridCrs=data.coordinate_crs_wkt||data.projected_crs?.wkt;
    if(explicitCrs&&gridCrs&&String(gridCrs).trim()!==String(boundary.projected_crs.wkt).trim())return null;
    const pointOnRing=(point,ring)=>{
        let inside=false;
        for(let i=0,j=ring.length-1;i<ring.length;j=i++){
            const [xi,yi]=ring[i],[xj,yj]=ring[j],cross=(point[0]-xi)*(yj-yi)-(point[1]-yi)*(xj-xi);
            if(Math.abs(cross)<1e-10&&point[0]>=Math.min(xi,xj)-1e-10&&point[0]<=Math.max(xi,xj)+1e-10&&
                    point[1]>=Math.min(yi,yj)-1e-10&&point[1]<=Math.max(yi,yj)+1e-10)return true;
            if((yi>point[1])!==(yj>point[1])&&point[0]<(xj-xi)*(point[1]-yi)/(yj-yi)+xi)inside=!inside;
        }
        return inside;
    };
    const contains=(x,y)=>groups.some(group=>pointOnRing([x,y],group.outer)&&
        !(group.holes||[]).some(hole=>pointOnRing([x,y],hole)));
    if(!groups.every(group=>Array.isArray(group?.outer)&&group.outer.length>=4&&
        group.outer.every(point=>Number.isFinite(point?.[0])&&Number.isFinite(point?.[1]))&&
        Array.isArray(group.holes||[])&&(group.holes||[]).every(ring=>Array.isArray(ring)&&ring.length>=3&&
            ring.every(point=>Number.isFinite(point?.[0])&&Number.isFinite(point?.[1])))))return null;
    const wet=data.display_topology?.wet_mask||data.wet_mask||data.wetMask;
    const dry=data.display_topology?.land_mask||data.dry_mask||data.dryMask;
    const xs=data.xc,ys=data.yc;
    if(!Array.isArray(wet)||!Array.isArray(dry)||!Array.isArray(xs)||!Array.isArray(ys))return null;
    const points=[...groups.flatMap(group=>[...group.outer,...(group.holes||[]).flat()])];
    const gx=(geometry?.surface?.x||[]).filter(Number.isFinite),gy=(geometry?.surface?.y||[]).filter(Number.isFinite);
    if(!gx.length||!gy.length||!points.length)return null;
    const gridBounds=[Math.min(...gx),Math.min(...gy),Math.max(...gx),Math.max(...gy)];
    const boundaryBounds=[Math.min(...points.map(p=>p[0])),Math.min(...points.map(p=>p[1])),
        Math.max(...points.map(p=>p[0])),Math.max(...points.map(p=>p[1]))];
    const overlap=Math.max(0,Math.min(gridBounds[2],boundaryBounds[2])-Math.max(gridBounds[0],boundaryBounds[0]))*
        Math.max(0,Math.min(gridBounds[3],boundaryBounds[3])-Math.max(gridBounds[1],boundaryBounds[1]));
    const gridArea=(gridBounds[2]-gridBounds[0])*(gridBounds[3]-gridBounds[1]);
    const boundaryArea=(boundaryBounds[2]-boundaryBounds[0])*(boundaryBounds[3]-boundaryBounds[1]);
    if(overlap/Math.max(Number.EPSILON,Math.min(gridArea,boundaryArea))<.35)return null;
    let wetCount=0,dryCount=0,wetInside=0,dryOutside=0;
    for(let j=0;j<Math.max(wet.length,dry.length);j++)for(let i=0;i<Math.max(wet[j]?.length||0,dry[j]?.length||0);i++){
        const isWet=wet[j]?.[i]===true,isDry=dry[j]?.[i]===true;if(!isWet&&!isDry)continue;
        if(!Number.isFinite(xs[i])||!Number.isFinite(ys[j]))return null;
        const inside=contains(xs[i],ys[j]);
        if(isWet){wetCount++;if(inside)wetInside++;}
        if(isDry){dryCount++;if(!inside)dryOutside++;}
    }
    // CRS-transformed outlines rely on the server's projection contract and
    // overlap check; grid-coordinate proxies additionally need exact mask-center agreement.
    if(declaredGridSpace&&(!wetCount||!dryCount||wetInside!==wetCount||dryOutside!==dryCount))return null;
    return wetCount>0?{groups,provenance:boundary.provenance||null,
        sourceCrs:explicitCrs?boundary.source_crs||null:null,source:'display-boundary-clipped-wet-cells',
        label:`${boundary.provenance.source} · 显示代理裁切（坐标/湿干掩膜一致性检查仅用于显示裁切；地理/科学真实性未验证）`}:null;
}
function lakeDisplayBoundaryStatus(geometry,data={}) {
    const frame=lakeDisplayFrame(geometry,data);
    const boundary=frame.boundaryClipApplied?lakeValidatedDisplayBoundary(geometry,data):null;
    if(boundary)return `${boundary.provenance?.source||'source-vector'} · 显示代理裁切（坐标/湿干掩膜一致性检查仅用于显示裁切；地理/科学真实性未验证）`;
    return '湿网格岸线概化（代理，未验证）';
}

// Scanline tessellation clips each existing wet-cell quad to polygon outer
// rings and holes. It samples attributes from the original quad and copies
// source-cell hover data; only draw vertices are added or removed.
function lakeClipMeshToBoundary(mesh,geometry,data={}) {
    const boundary=lakeValidatedDisplayBoundary(geometry,data);
    if(!boundary||!mesh||mesh.x?.length%4||!mesh.cell?.length)return null;
    const output={x:[],y:[],z:[],...(Array.isArray(mesh.intensity)?{intensity:[]}:{}),customdata:[],cell:[],i:[],j:[],k:[]};
    const triangleBudget=200000;
    const rings=boundary.groups.flatMap(group=>[group.outer,...(group.holes||[])]);
    const hitsAt=(ring,y)=>{
        const hits=[];
        for(let n=0;n<ring.length;n++){
            const a=ring[n],b=ring[(n+1)%ring.length];
            if((a[1]<=y&&b[1]>y)||(b[1]<=y&&a[1]>y))hits.push({x:a[0]+(y-a[1])*(b[0]-a[0])/(b[1]-a[1]),a,b});
        }
        return hits.sort((a,b)=>a.x-b.x);
    };
    const xAt=(hit,y)=>hit.a[0]+(y-hit.a[1])*(hit.b[0]-hit.a[0])/(hit.b[1]-hit.a[1]);
    try { for(let q=0;q+3<mesh.x.length;q+=4){
        const cell=mesh.cell[q],points=Array.from({length:4},(_,n)=>[mesh.x[q+n],mesh.y[q+n]]);
        if(!cell||points.some(point=>!point.every(Number.isFinite)))continue;
        const x0=Math.min(...points.map(p=>p[0])),x1=Math.max(...points.map(p=>p[0]));
        const y0=Math.min(...points.map(p=>p[1])),y1=Math.max(...points.map(p=>p[1]));
        if(!(x1>x0&&y1>y0))continue;
        const breaks=[y0,y1];
        for(const ring of rings)for(let n=0;n<ring.length;n++){
            const a=ring[n],b=ring[(n+1)%ring.length];
            if(a[1]>y0&&a[1]<y1)breaks.push(a[1]);
            if(a[0]!==b[0])for(const x of [x0,x1]){const y=a[1]+(x-a[0])*(b[1]-a[1])/(b[0]-a[0]);if(y>y0&&y<y1)breaks.push(y);}
        }
        const ys=[...new Set(breaks)].sort((a,b)=>a-b);
        const corners={};
        for(let n=0;n<4;n++){const p=points[n],key=`${p[0]===x1?1:0}${p[1]===y1?1:0}`;corners[key]=n;}
        if(Object.keys(corners).length!==4)continue;
        const valueAt=(key,n)=>mesh[key]?.[q+corners[n]];
        const sample=(key,x,y)=>{
            const u=(x-x0)/(x1-x0),v=(y-y0)/(y1-y0),v00=valueAt(key,'00'),v10=valueAt(key,'10'),v11=valueAt(key,'11'),v01=valueAt(key,'01');
            if(![v00,v10,v11,v01].every(Number.isFinite))return null;
            return v00*(1-u)*(1-v)+v10*u*(1-v)+v11*u*v+v01*(1-u)*v;
        };
        const addQuad=(xl0,xr0,xl1,xr1,lo,hi)=>{
            const polygon=[[xl0,lo],[xr0,lo],[xr1,hi],[xl1,hi]],area=Math.abs(polygon.reduce((sum,p,n)=>sum+p[0]*polygon[(n+1)%4][1]-polygon[(n+1)%4][0]*p[1],0));
            if(area<1e-12)return;
            if(output.i.length+2>triangleBudget)throw new RangeError('display boundary triangle budget exceeded');
            const sampled=polygon.map(([x,y])=>({x,y,z:sample('z',x,y),intensity:output.intensity?sample('intensity',x,y):null}));
            if(sampled.some(value=>value.z===null||output.intensity&&value.intensity===null))return;
            const base=output.x.length;
            for(const value of sampled){output.x.push(value.x);output.y.push(value.y);output.z.push(value.z);
                if(output.intensity)output.intensity.push(value.intensity);
                output.customdata.push(mesh.customdata?.[q]);output.cell.push(cell);}
            output.i.push(base,base);output.j.push(base+1,base+2);output.k.push(base+2,base+3);
        };
        for(let s=0;s+1<ys.length;s++){
            const lo=ys[s],hi=ys[s+1],mid=(lo+hi)/2;if(!(hi>lo))continue;
            for(const group of boundary.groups){
                const outer=hitsAt(group.outer,mid);
                for(let h=0;h+1<outer.length;h+=2){
                    let left=outer[h],right=outer[h+1],xr=Math.min(x1,right.x);
                    // Clip endpoint edges to cell walls; interval topology is stable within this scanline slab.
                    if(xr<=Math.max(x0,left.x))continue;
                    let spans=[[left,right]];
                    for(const hole of group.holes||[]){const hs=hitsAt(hole,mid);for(let p=0;p+1<hs.length;p+=2){
                        const hl=hs[p],hr=hs[p+1];spans=spans.flatMap(([a,b])=>{
                            const al=Math.max(x0,a.x),br=Math.min(x1,b.x),ha=Math.max(x0,hl.x),hb=Math.min(x1,hr.x),out=[];
                            if(ha>al)out.push([a,{x:ha,a:hl.a,b:hl.b}]);if(hb<br)out.push([{x:hb,a:hr.a,b:hr.b},b]);return out;
                        });
                    }}
                    for(const [a,b] of spans){const mlo=Math.max(x0,a.x),mhi=Math.min(x1,b.x);if(mhi<=mlo)continue;
                        const edgePoint=(hit,y)=>Math.max(x0,Math.min(x1,xAt(hit,y)));
                        const l0=edgePoint(a,lo),r0=edgePoint(b,lo),l1=edgePoint(a,hi),r1=edgePoint(b,hi);
                        addQuad(l0,r0,l1,r1,lo,hi);
                    }
                }
            }
        }
    }} catch(error) { if(error instanceof RangeError&&error.message==='display boundary triangle budget exceeded')return null; throw error; }
    return output.i.length?{...output,meta:{displayOnly:true,source:boundary.source,provenance:boundary.provenance,
        sourceCrs:boundary.sourceCrs,wetTopologyUnchanged:true,fieldValuesInterpolatedWithinNativeCell:true}}:null;
}

function lakeWetMaskShorelineTrace(geometry,data={}) {
    return {type:'scatter3d',name:viz3dSampledBoundary(data)?'湿网格岸线（采样代理，未验证）':'湿网格岸线（代理，未验证）',
        mode:'lines',...smoothLakeShoreline(geometry.shoreline),line:{color:'#5b98a3',width:2.2},hoverinfo:'skip',
        meta:{displayOnly:true,shoreline:true,source:'native-wet-mask-boundary-display-generalization',geographicPrecision:false}};
}
function lakeShorelineTrace(geometry,data={},options={}) {
    if(options.wetGridOnly)return lakeWetMaskShorelineTrace(geometry,data);
    const displayBoundary=typeof lakeValidatedDisplayBoundary==='function'?lakeValidatedDisplayBoundary(geometry,data):null;
    if(displayBoundary){
        const x=[],y=[],z=[];
        for(const group of displayBoundary.groups)for(const ring of [group.outer,...(group.holes||[])]){
            for(let n=0;n<ring.length;n++){x.push(ring[n][0]);y.push(ring[n][1]);z.push(0);}
            if(ring.length){x.push(ring[0][0]);y.push(ring[0][1]);z.push(0);}x.push(null);y.push(null);z.push(null);
        }
        return {type:'scatter3d',name:displayBoundary.label,mode:'lines',x,y,z,line:{color:'#5b98a3',width:2.2},
            hoverinfo:'skip',showlegend:true,meta:{displayOnly:true,shoreline:true,source:displayBoundary.source,
                sourceVerticesPreserved:true,geographicPrecision:null,wetTopologyUnchanged:true,
                sourceCrs:displayBoundary.sourceCrs,provenance:displayBoundary.provenance}};
    }
    const groups=data?.authoritative_boundary?.projected_polygons;
    const rings=[];
    if(Array.isArray(groups))for(const group of groups){
        if(!Array.isArray(group?.outer))continue;
        rings.push(group.outer,...(Array.isArray(group.holes)?group.holes:[]));
    }
    const validRings=rings.length>0&&rings.every(ring=>Array.isArray(ring)&&ring.length>=3&&ring.every(point=>
        Array.isArray(point)&&typeof point[0]==='number'&&Number.isFinite(point[0])&&typeof point[1]==='number'&&Number.isFinite(point[1]))&&
        new Set(ring.map(point=>`${point[0]},${point[1]}`)).size>=3&&
        Math.abs(ring.reduce((area,point,index)=>{const next=ring[(index+1)%ring.length];return area+point[0]*next[1]-next[0]*point[1];},0))>1e-12);
    // A boundary in a different CRS or lake must never replace the actual
    // wet-mask outline. This is only a coarse extent sanity check; overlap
    // does not establish scientific or geographic validation.
    const meshX=(geometry?.surface?.x||[]).filter(Number.isFinite),meshY=(geometry?.surface?.y||[]).filter(Number.isFinite);
    const boundaryPoints=rings.flat();
    const gridBounds=meshX.length&&meshY.length?[Math.min(...meshX),Math.min(...meshY),Math.max(...meshX),Math.max(...meshY)]:null;
    const boundaryBounds=boundaryPoints.length?[Math.min(...boundaryPoints.map(point=>point[0])),Math.min(...boundaryPoints.map(point=>point[1])),
        Math.max(...boundaryPoints.map(point=>point[0])),Math.max(...boundaryPoints.map(point=>point[1]))]:null;
    const overlapWidth=gridBounds&&boundaryBounds?Math.max(0,Math.min(gridBounds[2],boundaryBounds[2])-Math.max(gridBounds[0],boundaryBounds[0])):0;
    const overlapHeight=gridBounds&&boundaryBounds?Math.max(0,Math.min(gridBounds[3],boundaryBounds[3])-Math.max(gridBounds[1],boundaryBounds[1])):0;
    const overlapArea=overlapWidth*overlapHeight;
    const gridArea=gridBounds?Math.max(0,gridBounds[2]-gridBounds[0])*Math.max(0,gridBounds[3]-gridBounds[1]):0;
    const boundaryArea=boundaryBounds?Math.max(0,boundaryBounds[2]-boundaryBounds[0])*Math.max(0,boundaryBounds[3]-boundaryBounds[1]):0;
    // A sliver of bounding-box contact is not evidence that a shoreline belongs
    // to this grid. Require a projected CRS and substantial overlap with the
    // smaller extent; this is still only a display sanity check, not science validation.
    const overlapFraction=overlapArea/Math.max(Number.EPSILON,Math.min(gridArea,boundaryArea));
    const extentsOverlap=Boolean(data?.authoritative_boundary?.source_crs)&&overlapFraction>=.35;
    const valid=validRings&&extentsOverlap;
    if(valid){
        const provenance=data.authoritative_boundary.provenance||null;
        const x=[],y=[],z=[];
        for(const ring of rings){
            const points=ring.map(point=>[point[0],point[1]]);
            if(points.length>1&&points[0][0]===points.at(-1)[0]&&points[0][1]===points.at(-1)[1])points.pop();
            if(points.length)points.push(points[0]); // Polygon rings are implicitly closed.
            for(const [px,py] of points){x.push(px);y.push(py);z.push(0);}
            x.push(null);y.push(null);z.push(null);
        }
        return {type:'scatter3d',name:`${provenance?.source||'来源边界'} · 显示代理（地理/科学真实性未验证）`,mode:'lines',x,y,z,
            line:{color:'#5b98a3',width:2.2},hoverinfo:'skip',
            meta:{displayOnly:true,shoreline:true,source:'uploaded-boundary-projected-vertices',sourceVerticesPreserved:true,
                geographicPrecision:null,
                sourceCrs:data.authoritative_boundary.source_crs||null,provenance}};
    }
    return lakeWetMaskShorelineTrace(geometry,data);
}

function lakeLandTraces(data,opts={},z=0) {
    if(opts.showLand===false)return [];
    const land=buildLakeLand(data,z);
    if(!land.i.length)return [];
    const grid=buildDisplayNetwork([land],{mode:'triangles',density:1,refinement:2});
    const lift=Number(opts.landNetworkLift)||.001;
    const lines={...grid.lines,z:grid.lines.z.map(value=>value===null?null:value+lift)};
    return [{type:'mesh3d',name:'陆地示意平面（陆地高程未提供）',...land,color:'#cecabe',
        opacity:1,showscale:false,showlegend:true,hovertemplate:'已知干单元 · 陆地高程未提供<extra>示意平面</extra>',
        lighting:{ambient:1,diffuse:0,specular:0,roughness:1},meta:{landPlane:true,waterbodyFrame:'land'}},
        ...(lines.x.length?[{type:'scatter3d',mode:'lines',name:'陆地三角网格',...lines,
            line:{color:'#a9a79d',width:1.15},opacity:.24,hoverinfo:'skip',showlegend:false,
            meta:{displayOnly:true,landNetwork:true,meshMode:'triangles',waterbodyFrame:'land'}}]:[])];
}
function buildLakeCoastalRim(geometry,data={}) {
    const floor=geometry?.floor,topology=data.display_topology?.contract==='sampled-wet-topology-v1'?data.display_topology:null;
    const rim={x:[],y:[],z:[],intensity:[],i:[],j:[],k:[],cell:[]};
    if(!floor||!geometry?.walls)return rim;
    const knownLand=(i,j)=>topology?topology.cell_status?.[j]?.[i]==='dry'&&topology.land_mask?.[j]?.[i]===true:
        (data.dry_mask?.[j]?.[i]===true||data.dryMask?.[j]?.[i]===true);
    const pointKey=(x,y)=>`${Number(x).toPrecision(14)},${Number(y).toPrecision(14)}`;
    const edgeKey=(ax,ay,bx,by)=>[pointKey(ax,ay),pointKey(bx,by)].sort().join('|');
    const sides=[[0,1,0,-1],[1,2,1,0],[2,3,0,1],[3,0,-1,0]];
    const verifiedEdges=new Map();
    for(let q=0;q+3<floor.x.length;q+=4){
        const [i,j]=floor.cell?.[q] || [];
        if(!Number.isInteger(i)||!Number.isInteger(j))continue;
        for(let side=0;side<sides.length;side++){
            const [a,b,di,dj]=sides[side];
            const ni=i+di,nj=j+dj;
            if(topology ? topology.wall_sides?.[j]?.[i]?.[side]!==true||!knownLand(ni,nj) : !knownLand(ni,nj))continue;
            verifiedEdges.set(edgeKey(floor.x[q+a],floor.y[q+a],floor.x[q+b],floor.y[q+b]),[i,j]);
        }
    }
    // Reuse the model's real wet-cell wall quads. Only verified wet-to-dry
    // interfaces are admitted above, so domain edges and mixed/unknown cells
    // remain transparent to the plot background rather than becoming fake lake.
    const walls=geometry.walls;
    for(let q=0;q+3<walls.px.length;q+=4){
        const cell=verifiedEdges.get(edgeKey(walls.px[q],walls.py[q],walls.px[q+2],walls.py[q+2]));
        if(!cell)continue;
        const base=rim.x.length;
        for(let n=0;n<4;n++){
            rim.x.push(walls.px[q+n]);rim.y.push(walls.py[q+n]);rim.z.push(walls.pz[q+n]);
            rim.intensity.push(walls.cint[q+n]);rim.cell.push(cell);
        }
        rim.i.push(base,base);rim.j.push(base+1,base+3);rim.k.push(base+3,base+2);
    }
    return rim;
}
function lakeCoastalRimTrace(geometry,data={}) {
    const rim=buildLakeCoastalRim(geometry,data);
    if(!rim.i.length)return [];
    return [{type:'mesh3d',name:'岸边水深过渡',...rim,colorscale:VIZ3D.depthScale,cmin:0,cmax:geometry.maxDepth,cauto:false,
        intensitymode:'vertex',showscale:false,showlegend:false,opacity:1,
        lighting:{ambient:1,diffuse:0,specular:0,roughness:1},hoverinfo:'skip',
        meta:{displayOnly:true,coastalRim:true}}];
}
function lakeFacetLighting() {
    // Display-only directional relief: it does not alter field values or their color scale.
    return {ambient:.48,diffuse:.52,specular:.08,roughness:.82};
}
function lakeDisplayLines(mesh,geometry,opts={},data={}) {
    const mode=opts.meshMode || 'continuous';
    const topologyRows=data.shape?.length===3?data.shape[1]:data.shape?.length===2?data.shape[0]:undefined;
    const topologyCols=data.shape?.length===3?data.shape[2]:data.shape?.length===2?data.shape[1]:undefined;
    if(mode==='triangles'&&(!data.display_topology || data.display_topology.contract!=='sampled-wet-topology-v1'||
        !lakeDisplayTopologyValid(data.display_topology,topologyCols,topologyRows)))return [];
    const grid=buildDisplayNetwork(Array.isArray(mesh)?mesh:[mesh],{mode,density:opts.lineDensity,refinement:opts.lineRefinement});
    if(!grid.lines.x.length)return [];
    const triangles=mode==='triangles';
    const lift=geometry.maxDepth*geometry.ve*(triangles?.025:.01),meshName=triangles
        ?`三角显示剖分 · ${grid.stats.triangleSourceCells} 层湿四边形 / ${grid.stats.triangleFaces} 个三角面 / ${grid.stats.segments} 条边`
        :'正交显示网格';
    const baseOpacity=Number.isFinite(Number(opts.lineOpacity))?Math.max(0,Math.min(1,Number(opts.lineOpacity))):(triangles?.9:.62);
    const edgeLayers=triangles?grid.surfaceLinesByLayer.map((layer,index)=>({layer,index})).filter(entry=>entry.layer?.x.length):[{layer:grid.lines,index:0}];
    const layerOrdinals=Array.isArray(opts.displayLayerOrdinals)?opts.displayLayerOrdinals:[];
    const layerTones=['#334a52','#465b62','#586c70','#6b7872'];
    const surfaceTraces=edgeLayers.map(({layer:edgeLayer,index},traceIndex)=>({type:'scatter3d',mode:'lines',name:(viz3dSampledBoundary(data)?'采样显示 · ':'')+meshName,
        ...edgeLayer,z:edgeLayer.z.map(z=>z===null?null:z+lift),opacity:baseOpacity,
        line:{color:triangles?layerTones[index%layerTones.length]:'#71858a',width:triangles?2.3:1.35},hoverinfo:'skip',showlegend:traceIndex===0,
        meta:{displayOnly:true,meshMode:mode,networkMode:mode,waterbodyFrame:'network',...(triangles?{geometryColorSemantics:'display-layer only; not variable values'}:{}),...(triangles&&edgeLayers.length>1?{layerOrdinal:layerOrdinals[index]??index}:{}),
            refinement:grid.stats.refinement,density:grid.stats.density,segmentBudget:grid.stats.maxSegments,displayLift:lift,
            displayLiftFraction:triangles?.025:.01,
            sourceQuadCells:grid.stats.sourceQuadCells,triangleSourceCells:grid.stats.triangleSourceCells,
            triangleFaces:grid.stats.triangleFaces,displayEdges:Math.floor(edgeLayer.x.length/3),layerLinkSegments:grid.stats.layerSegments,triangulation:grid.stats.triangulation,
            }}));
    const traces=surfaceTraces;
    if(triangles&&grid.layerLines.x.length)traces.push({type:'scatter3d',mode:'lines',name:'层间连接 · 显示辅助',
        ...grid.layerLines,z:grid.layerLines.z.map(z=>z===null?null:z+lift),opacity:Math.min(baseOpacity,.9),
        line:{color:'#657b68',width:1.8},hoverinfo:'skip',showlegend:surfaceTraces.length===0,
        meta:{displayOnly:true,meshMode:mode,networkMode:mode,waterbodyFrame:'network',layerLinks:true,displayLift:lift}});
    if(triangles&&opts.showNetworkNodes===true&&grid.nodes.x.length)traces.push({type:'scatter3d',mode:'markers',name:'三角网格节点',x:grid.nodes.x,y:grid.nodes.y,z:grid.nodes.z.map(z=>z+lift),
        marker:{size:1.1,color:'#7c898a',line:{color:'#e6e9e6',width:.35},opacity:baseOpacity},hoverinfo:'skip',showlegend:false,
        meta:{displayOnly:true,meshMode:mode,networkMode:mode,waterbodyFrame:'network'}});
    return traces;
}
function lakeWaterbodyDisplayOptions(opts={},stack=false) {
    // Single-layer playback traces should show the actual wet-quad diagonal
    // without adding a denser micro-triangulation unless explicitly requested.
    return !stack&&opts.meshMode==='triangles'&&opts.lineRefinement===undefined
        ? {...opts,lineRefinement:1}:opts;
}
function lakeCoverage(data,levels) {
    const result={valid:0,missing:0,invalid:0};
    for(const k of levels)for(let j=0;j<(data.shape?.[1] || 0);j++)for(let i=0;i<(data.shape?.[2] || 0);i++){
        if(!(Number.isFinite(data.bottom?.[j]?.[i])&&data.bottom[j][i]>0))continue;
        if(data.valid_geometry?.[j]?.[i]===false || data.display_topology?.wet_mask?.[j]?.[i]===false ||
            (Array.isArray(data.depth)&&!Number.isFinite(data.depth[k]?.[j]?.[i])))result.invalid++;
        else result[Number.isFinite(data.data?.[k]?.[j]?.[i])?'valid':'missing']++;
    }
    return result;
}
function lakeDisplayDetail(data,opts={},coverage) {
    return ' · 仅显示网格；求解器拓扑不变'+((opts.meshMode || 'continuous')==='continuous'&&opts.scalarInterpolation!==false?' · 变量角点插值仅用于显示；悬停为单元中心原值':' · 单元中心原值（不插值变量）')+
        (opts.meshMode==='triangles'?' · 显示辅助偏移 2.5%；不代表物理水深/层位 · 三角面片明暗仅为显示辅助'+(opts.stack?' · 层间连接线仅为显示辅助 · 线色用于区分显示层位，不表示变量值':''):'')+
        (opts.stack&&opts.meshMode==='triangles'?' · 相邻湿层间浅色侧面为显示辅助，不表示求解器实体边界':'')+
        (opts.staticBathymetry===true?` · 陆地高程未提供；静态预览隐藏陆地示意格；${opts.displayBoundaryStatus||'湿网格岸线概化（代理，未验证）'}；边缘淡化仅在湿单元内`:
            opts.showLand===false?'':' · 陆地高程未提供；已知干单元为示意平面，未知水深不绘制')+
        (data.display_topology?.mixed_or_unknown_cells>0?' · 采样显示可能省略窄岸线/局部干格':'')+
        (coverage?` · 有效 ${coverage.valid} · 水域缺测 ${coverage.missing} · 几何缺失 ${coverage.invalid}`:'');
}

function buildWaterWalls(xc, yc, bottom, ve, zTopFrac = 1) {
    return buildLakeGeometry(xc,yc,bottom,ve*zTopFrac)?.walls || null;
}

function viz3dCoordinates(data={}) {
    const index=data.coordinate_mode==='index' || data.coordinate_units==='index';
    const units=index ? 'index' : data.coordinate_units || 'm';
    return {index,units,x:index?'网格列 i':'X 坐标',y:index?'网格行 j':'Y 坐标'};
}
function viz3dHorizontalHover(data={}) {
    const c=viz3dCoordinates(data),units=viz3dEscape(c.units);
    return `${c.index?'网格 i':'X'} %{x:.6~g} ${units} · ${c.index?'j':'Y'} %{y:.6~g} ${units}`;
}
function viz3dSampling(data={}) {
    const shape=data.full_shape || (Number.isInteger(data.ny_full)&&Number.isInteger(data.nx_full) ? [data.ny_full,data.nx_full] : null);
    const stride=data.sampling_stride || (Number.isFinite(data.stride) ? [data.stride,data.stride] : null);
    if(!shape || !stride) return '';
    return `原网格 ${shape.join('×')} · 采样步长 ${stride.join('×')}`;
}
function lakeViewAxisRange(data,edges,axis,marginFraction=.18) {
    if(!Array.isArray(edges)||edges.length<2)return null;
    const bottom=data?.bottom,ny=bottom?.length||0,nx=bottom?.[0]?.length||0;
    const count=axis==='x'?nx:ny,rows=axis==='x'?ny:nx;
    if(edges.length!==count+1||!count||!rows)return null;
    const topology=data.display_topology?.contract==='sampled-wet-topology-v1'?data.display_topology:null;
    let wetMin=Infinity,wetMax=-Infinity;
    for(let j=0;j<ny;j++)for(let i=0;i<nx;i++){
        const depth=bottom[j]?.[i];
        if(!Number.isFinite(depth)||depth<=0||data.valid_geometry?.[j]?.[i]===false)continue;
        if(topology ? topology.wet_mask?.[j]?.[i]!==true :
            ((Array.isArray(data.wet_mask)&&data.wet_mask[j]?.[i]===false)||
             (Array.isArray(data.wetMask)&&data.wetMask[j]?.[i]===false)))continue;
        const cell=axis==='x'?i:j;
        wetMin=Math.min(wetMin,edges[cell],edges[cell+1]);
        wetMax=Math.max(wetMax,edges[cell],edges[cell+1]);
    }
    if(!Number.isFinite(wetMin)||!Number.isFinite(wetMax))return null;
    const span=wetMax-wetMin;
    if(!(span>0))return null;
    // Keep every physically wet cell and its full shoreline in frame. Unlike
    // the source-data bounds, the plot range may extend into blank space so a
    // wet basin that touches the model edge still gets a complete frame.
    const margin=span*Math.max(0,Number(marginFraction)||0);
    const low=wetMin-margin,high=wetMax+margin;
    return high>low?[low,high]:null;
}
function viz3dSampledBoundary(data={}) {
    return (data.sampling_stride?.slice(-2) || [data.stride || 1]).some(v=>v>1);
}
const LAKE_ORTHOGRAPHIC_ZOOM=4.5;
function lakeScene(ve, maxDepth, data={}, displayTopMarginFraction=0) {
    const ticks = viz3dTicks(0,maxDepth);
    const c=viz3dCoordinates(data);
    const topology=data.display_topology?.contract==='sampled-wet-topology-v1'?data.display_topology:null;
    const xe=topology?.x_edges?.length===data.xc?.length+1?topology.x_edges:lakeCellEdges(data.xc || []);
    const ye=topology?.y_edges?.length===data.yc?.length+1?topology.y_edges:lakeCellEdges(data.yc || []);
    const xr=(lakeViewAxisRange(data,xe,'x') || (xe.length?[Math.min(...xe),Math.max(...xe)]:null));
    const yr=(lakeViewAxisRange(data,ye,'y') || (ye.length?[Math.min(...ye),Math.max(...ye)]:null));
    const spans=xr&&yr?[xr[1]-xr[0],yr[1]-yr[0],maxDepth*ve]:null;
    // Plotly's orthographic camera does not use eye distance for zoom: its
    // wheel handler multiplies all three aspectratio axes. Keep the physical
    // proportions normalized to the longest span, then apply one common
    // framing scale so the full basin uses more of the available viewport.
    const valid=spans?.every(v=>Number.isFinite(v)&&v>0),scale=valid?Math.max(...spans):1;
    return Object.assign({},VIZ3D.layout.scene, {
        // Keep the current sampled lake domain across modes and frames. An
        // isosurface's narrow z extent must not enlarge or crop the whole view.
        ...(valid?{aspectmode:'manual',aspectratio:{x:LAKE_ORTHOGRAPHIC_ZOOM*spans[0]/scale,
            y:LAKE_ORTHOGRAPHIC_ZOOM*spans[1]/scale,z:LAKE_ORTHOGRAPHIC_ZOOM*spans[2]/scale}}:{}),
        xaxis:{...VIZ3D.layout.scene.xaxis,title:`${c.x} (${viz3dEscape(c.units)})`,...(xr?{range:xr,autorange:false}:{})},
        yaxis:{...VIZ3D.layout.scene.yaxis,title:`${c.y} (${viz3dEscape(c.units)})`,...(yr?{range:yr,autorange:false}:{})},
        zaxis:Object.assign({},VIZ3D.layout.scene.zaxis,{
        title:'水深 (m)', tickmode:'array', tickvals:ticks.values.map(h=>-h*ve),
        ticktext:ticks.labels,...(valid?{range:[-maxDepth*ve,maxDepth*ve*Math.max(0,Number(displayTopMarginFraction)||0)],autorange:false}:{})
    })});
}

function lakeVolumeSamples(d,ve=1) {
    if(d.depth_geometry_error)return null;
    const [nz,ny,nx]=d.shape || [];
    if(!d.xc || !d.yc || d.xc.length!==nx || d.yc.length!==ny || !d.bottom ||
        !buildLakeGeometry(d.xc,d.yc,d.bottom,ve,d.display_topology)) return null;
    const fractions=d.sigma?.length===nz ? sigmaToFraction(d.sigma) : Array.from({length:nz},(_,k)=>1-(k+0.5)/nz);
    const samples={x:[],y:[],z:[],values:[],valid:[]};
    for(let k=0;k<nz;k++) for(let j=0;j<ny;j++) for(let i=0;i<nx;i++) {
        const h=d.bottom[j][i],v=d.data?.[k]?.[j]?.[i],wet=Number.isFinite(h)&&h>0;
        const depth=Array.isArray(d.depth) ? d.depth[k]?.[j]?.[i] : h*fractions[k];
        const valid=wet&&d.valid_geometry?.[j]?.[i]!==false&&d.display_topology?.wet_mask?.[j]?.[i]!==false&&Number.isFinite(depth);
        samples.valid.push(valid);
        samples.x.push(d.xc[i]);samples.y.push(d.yc[j]);samples.z.push(valid ? -depth*ve : 0);
        samples.values.push(valid&&Number.isFinite(v) ? v : null);
    }
    return samples;
}

// Missing scalar samples keep their native physical location, with no
// quantitative intensity or legend entry mixed into the field transfer function.
function lakeMissingSamples(data,samples,style,opts={}) {
    const trace={type:'scatter3d',mode:'markers',name:'水域缺测',x:[],y:[],z:[],
        marker:{size:3,color:style.nanColor || '#c9cbd0',opacity:viz3dOpacity(opts),showscale:false},
        meta:{missingWater:true},hovertemplate:viz3dHorizontalHover(data)+'<br>变量缺测<extra>水域缺测</extra>'};
    samples.values.forEach((value,q)=>{
        if(samples.valid[q]&&!Number.isFinite(value))for(const axis of ['x','y','z'])trace[axis].push(samples[axis][q]);
    });
    return trace.x.length?[trace]:[];
}
function lakeVolumeContext(data,ve,opts) {
    const geometry=buildLakeGeometry(data.xc,data.yc,data.water_depth || data.bottom,ve,data.display_topology);
    return geometry?[...lakeLandTraces(data,opts),...lakeDisplayLines(lakePhysicalVolumeNetwork(data,geometry,ve),geometry,opts,data)]:[];
}
function buildVariableHeightMesh(values,grid) {
    const mesh={x:[],y:[],z:[],intensity:[],customdata:[],cell:[],i:[],j:[],k:[]};
    const topology=grid.display_topology?.contract==='sampled-wet-topology-v1'?grid.display_topology:null;
    const xe=topology?.x_edges?.length===grid.xc?.length+1?topology.x_edges:lakeCellEdges(grid.xc || []);
    const ye=topology?.y_edges?.length===grid.yc?.length+1?topology.y_edges:lakeCellEdges(grid.yc || []);
    if(!xe.length||!ye.length)return mesh;
    for(let j=0;j<values.length;j++)for(let i=0;i<(values[j]?.length || 0);i++){
        const value=values[j][i];if(grid.wetMask?.[j]?.[i]!==true || topology?.wet_mask?.[j]?.[i]===false || !Number.isFinite(value))continue;
        const base=mesh.x.length;
        for(const [u,v] of [[i,j],[i+1,j],[i+1,j+1],[i,j+1]]){
            mesh.x.push(xe[u]);mesh.y.push(ye[v]);mesh.z.push(value);mesh.intensity.push(value);
            mesh.customdata.push([grid.xc[i],grid.yc[j],value,i,j]);mesh.cell.push([i,j]);
        }
        mesh.i.push(base,base);mesh.j.push(base+1,base+2);mesh.k.push(base+2,base+3);
    }
    return mesh;
}
function variableHeightGrid(grid,rows,cols) {
    if(grid?.shape?.length!==2||grid.shape[0]!==rows||grid.shape[1]!==cols ||
        grid.wetMask?.length!==rows||grid.wetMask.some(row=>row?.length!==cols))return null;
    const index=grid.coordinate_mode==='index';
    const xc=index?Array.from({length:cols},(_,i)=>i):grid.xc;
    const yc=index?Array.from({length:rows},(_,j)=>j):grid.yc;
    if(!Array.isArray(xc)||xc.length!==cols||!Array.isArray(yc)||yc.length!==rows||
        ![xc,yc].every(axis=>axis.every(Number.isFinite)&&(axis.length<2||axis.slice(1).every((v,i)=>(v-axis[i])*(axis[1]-axis[0])>0))))return null;
    return {...grid,xc,yc};
}

// Four cells around a corner form a fixed cyclic graph. Precompute the exact
// ascending-neighbor BFS order for every mask/seed so playback does not build
// a fresh queue or rediscover the same tiny component graph at every corner.
const LAKE_CORNER_COMPONENT_ORDERS=Array.from({length:16},(_,mask)=>Array.from({length:4},(_,seed)=>{
    if(!(mask&(1<<seed)))return [];
    const queue=[seed];let seen=1<<seed;
    for(let q=0;q<queue.length;q++)for(let next=0;next<4;next++){
        if(!(mask&(1<<next))||(seen&(1<<next)))continue;
        const current=queue[q];
        if(Math.abs(current-next)!==1&&!(current===0&&next===3)&&!(current===3&&next===0))continue;
        seen|=1<<next;queue.push(next);
    }
    return queue;
}));
function lakeCornerComponentMeans(mask,values,means) {
    means=means || [NaN,NaN,NaN,NaN];
    means[0]=means[1]=means[2]=means[3]=NaN;
    // Four cells surround a vertex in cyclic order. Visit neighbors in the
    // same ascending order as connectedCornerAverage's original BFS. Keep a
    // mean for each seed because floating-point addition order follows that
    // seed; diagonal dry-cell components therefore stay exactly isolated.
    for(let seed=0;seed<4;seed++) {
        const order=LAKE_CORNER_COMPONENT_ORDERS[mask]?.[seed];
        if(!order?.length)continue;
        let sum=0;
        for(const cell of order)sum+=values[cell];
        means[seed]=sum/order.length;
    }
    return means;
}
function lakeLayerCornerAverages(geometry,data,layer,smooth) {
    const [ny,nx]=data.shape?.slice(1) || [0,0];
    const fractions=sigmaToFraction(data.sigma || []);
    const depths=Array.from({length:ny},()=>Array(nx));
    const depthValid=Array.from({length:ny},()=>Array(nx).fill(false));
    for(let j=0;j<ny;j++)for(let i=0;i<nx;i++) {
        const value=Array.isArray(data.depth)?data.depth[layer]?.[j]?.[i]
            :data.bottom?.[j]?.[i]*fractions[layer];
        depths[j][i]=value;
        depthValid[j][i]=data.valid_geometry?.[j]?.[i]!==false&&geometry.displayTopology?.wet_mask?.[j]?.[i]!==false&&
            Number.isFinite(data.bottom?.[j]?.[i])&&data.bottom[j][i]>0&&Number.isFinite(value);
    }
    const cornerMeansRow=()=>Array.from({length:nx+1},()=>[NaN,NaN,NaN,NaN]);
    const depthCorners=Array.from({length:ny+1},cornerMeansRow);
    const fieldCorners=smooth?Array.from({length:ny+1},cornerMeansRow):null;
    // Reuse four-slot scratch buffers across vertices. The component means
    // read only slots selected by the masks below, so stale values in dry or
    // missing slots are never observed.
    const depthValues=[NaN,NaN,NaN,NaN],fieldValues=smooth?[NaN,NaN,NaN,NaN]:null;
    for(let v=0;v<=ny;v++)for(let u=0;u<=nx;u++) {
        let depthMask=0,fieldMask=0;
        for(let slot=0;slot<4;slot++) {
            const i=(slot===0||slot===3)?u-1:u,j=slot<2?v-1:v;
            if(i<0||i>=nx||j<0||j>=ny)continue;
            if(!depthValid[j][i])continue;
            const depth=depths[j][i];
            depthMask|=1<<slot;
            depthValues[slot]=depth;
            if(smooth) {
                const value=data.data?.[layer]?.[j]?.[i];
                if(Number.isFinite(value)){
                    fieldMask|=1<<slot;
                    fieldValues[slot]=value;
                }
            }
        }
        lakeCornerComponentMeans(depthMask,depthValues,depthCorners[v][u]);
        if(smooth)lakeCornerComponentMeans(fieldMask,fieldValues,fieldCorners[v][u]);
    }
    return {depths,depthValid,depthCorners,fieldCorners};
}
function lakeLayerMeshes(geometry,data,layer,ve,smooth,cornerAverages) {
    const makeMesh=missing=>({x:[],y:[],z:[],...(missing?{}:{intensity:[]}),customdata:[],cell:[],i:[],j:[],k:[]});
    const fieldMesh=makeMesh(false),missingMesh=makeMesh(true);
    const seedSlots=[2,3,0,1];
    for(let q=0;q<geometry.floor.x.length;q+=4) {
        const [i,j]=geometry.floor.cell[q],value=data.data?.[layer]?.[j]?.[i];
        if(data.valid_geometry?.[j]?.[i]===false)continue;
        const missing=!Number.isFinite(value),mesh=missing?missingMesh:fieldMesh;
        const center=cornerAverages.depths[j]?.[i];
        if(!Number.isFinite(center))continue;
        const c0=cornerAverages.depthCorners[j]?.[i]?.[seedSlots[0]];
        const c1=cornerAverages.depthCorners[j]?.[i+1]?.[seedSlots[1]];
        const c2=cornerAverages.depthCorners[j+1]?.[i+1]?.[seedSlots[2]];
        const c3=cornerAverages.depthCorners[j+1]?.[i]?.[seedSlots[3]];
        if(!Number.isFinite(c0)||!Number.isFinite(c1)||!Number.isFinite(c2)||!Number.isFinite(c3))continue;
        const b=mesh.x.length,elevation=data.elevation?.[layer]?.[j]?.[i];
        const cell=[i,j],hoverData=[center,Number.isFinite(elevation)?elevation:null,data.xc[i],data.yc[j],i,j,missing?null:value];
        for(let a=0;a<4;a++) {
            mesh.x.push(geometry.floor.x[q+a]);mesh.y.push(geometry.floor.y[q+a]);
            const corner=a===0?c0:a===1?c1:a===2?c2:c3;
            mesh.z.push(-corner*ve);
            if(!missing){
                const u=(a===1||a===2)?i+1:i,v=a>=2?j+1:j;
                mesh.intensity.push(smooth?cornerAverages.fieldCorners[v]?.[u]?.[seedSlots[a]]:value);
            }
            // All four quad corners report the same cell-center measurement.
            // Reuse its immutable arrays instead of allocating four copies.
            mesh.cell.push(cell);mesh.customdata.push(hoverData);
        }
        // The selected network is a separate scatter3d overlay. Keep the
        // scientific colored surface faces identical in every display mode.
        mesh.i.push(b,b);mesh.j.push(b+1,b+2);mesh.k.push(b+2,b+3);
    }
    return {fieldMesh,missingMesh};
}

function lakeAppendLayerMesh(target,source,layerOrdinal) {
    const offset=target.x.length;
    for(const key of ['x','y','z','intensity','cell'])if(Array.isArray(source[key]))
        for(const value of source[key])target[key].push(value);
    for(const row of source.customdata || [])target.customdata.push([...row,layerOrdinal]);
    for(const key of ['i','j','k'])for(const index of source[key] || [])target[key].push(index+offset);
}

function lakePhysicalLayerNetworkMesh(geometry,data,layer,ve=1) {
    const mesh={x:[],y:[],z:[],cell:[]},fractions=sigmaToFraction(data.sigma || []);
    const depth=(i,j)=>Array.isArray(data.depth)?data.depth[layer]?.[j]?.[i]:data.bottom?.[j]?.[i]*fractions[layer];
    const valid=(i,j)=>data.valid_geometry?.[j]?.[i]!==false&&geometry.displayTopology?.wet_mask?.[j]?.[i]!==false&&
        Number.isFinite(data.bottom?.[j]?.[i])&&data.bottom[j][i]>0&&Number.isFinite(depth(i,j));
    const corner=(u,v,i,j)=>{const cells=lakeCornerCells(u,v,i,j,valid).map(([x,y])=>depth(x,y));return cells.length?cells.reduce((a,b)=>a+b,0)/cells.length:null;};
    for(let q=0;q<geometry.floor.x.length;q+=4) {
        const [i,j]=geometry.floor.cell[q];if(!valid(i,j))continue;
        const points=[[i,j],[i+1,j],[i+1,j+1],[i,j+1]],corners=points.map(([u,v])=>corner(u,v,i,j));
        if(!corners.every(Number.isFinite))continue;
        for(let n=0;n<4;n++){mesh.x.push(geometry.floor.x[q+n]);mesh.y.push(geometry.floor.y[q+n]);mesh.z.push(-corners[n]*ve);mesh.cell.push([i,j]);}
    }
    return mesh;
}
function lakePhysicalVolumeNetwork(data,geometry,ve,visibleLayers) {
    const layerCount=data.shape?.[0] || 0;
    const layers=Array.isArray(visibleLayers)
        ? [...new Set(visibleLayers.filter(layer=>Number.isInteger(layer)&&layer>=0&&layer<layerCount))]
        : Array.from({length:layerCount},(_,layer)=>layer);
    return layers.map(layer=>lakePhysicalLayerNetworkMesh(geometry,data,layer,ve));
}

// Join corresponding wet-cell edges between adjacent sigma-layer centres.
// These matte side panels expose the volume implied by an explicitly selected
// stack, without adding scalar values or changing either source layer surface.
function lakeInterlayerSideFacetMesh(meshes,requestedStride=1,sourceOrdinals) {
    const result={x:[],y:[],z:[],i:[],j:[],k:[],cell:[],sourceCellPairs:0,samplingStride:1};
    if(!Array.isArray(meshes)||meshes.length<2)return result;
    const cellMap=mesh=>{
        const map=new Map();
        for(let q=0;q+3<mesh.x.length;q+=4) {
            const cell=mesh.cell?.[q];
            if(Array.isArray(cell)&&cell.length===2&&cell.every(Number.isInteger))map.set(`${cell[0]},${cell[1]}`,{q,cell});
        }
        return map;
    };
    const pairs=[];
    for(let layer=0;layer+1<meshes.length;layer++) {
        if(Array.isArray(sourceOrdinals)&&sourceOrdinals.length===meshes.length&&
            sourceOrdinals[layer+1]!==sourceOrdinals[layer]+1)continue;
        const lower=cellMap(meshes[layer]),upper=cellMap(meshes[layer+1]);
        for(const [key,low] of lower) {
            const high=upper.get(key);
            if(high)pairs.push({low,high,lowerMesh:meshes[layer],upperMesh:meshes[layer+1]});
        }
    }
    result.sourceCellPairs=pairs.length;
    if(!pairs.length)return result;
    const selectedCellFraction=stride=>2/stride-1/(stride*stride);
    let stride=Math.max(1,Math.round(Number(requestedStride)||1));
    const maxQuads=12000;
    while(pairs.length*4*selectedCellFraction(stride)>maxQuads)stride++;
    result.samplingStride=stride;
    const seen=new Set(),outward=[[0,-1],[1,0],[0,1],[-1,0]];
    const pointKey=point=>point.map(value=>Number(value).toPrecision(14)).join(',');
    for(const {low,high,lowerMesh,upperMesh} of pairs) {
        const [i,j]=low.cell;
        if(i%stride!==0&&j%stride!==0)continue;
        for(let side=0;side<4;side++) {
            const next=(side+1)%4;
            const points=[
                [lowerMesh.x[low.q+side],lowerMesh.y[low.q+side],lowerMesh.z[low.q+side]],
                [lowerMesh.x[low.q+next],lowerMesh.y[low.q+next],lowerMesh.z[low.q+next]],
                [upperMesh.x[high.q+next],upperMesh.y[high.q+next],upperMesh.z[high.q+next]],
                [upperMesh.x[high.q+side],upperMesh.y[high.q+side],upperMesh.z[high.q+side]],
            ];
            if(!points.flat().every(Number.isFinite)||Math.max(...points.map(point=>point[2]))-
                Math.min(...points.map(point=>point[2]))<1e-10)continue;
            const keys=points.map(pointKey),quadKey=[...keys].sort().join('|');
            if(seen.has(quadKey))continue;
            seen.add(quadKey);
            const [outX,outY]=outward[side],ux=points[1][0]-points[0][0],uy=points[1][1]-points[0][1],
                uz=points[1][2]-points[0][2],vx=points[2][0]-points[0][0],vy=points[2][1]-points[0][1],
                vz=points[2][2]-points[0][2],normalX=uy*vz-uz*vy,normalY=uz*vx-ux*vz,
                normalZ=ux*vy-uy*vx;
            if(Math.hypot(normalX,normalY,normalZ)<1e-12)continue;
            const order=normalX*outX+normalY*outY<0?[0,3,2,1]:[0,1,2,3],base=result.x.length;
            for(const point of points){result.x.push(point[0]);result.y.push(point[1]);result.z.push(point[2]);result.cell.push([...low.cell]);}
            result.i.push(base+order[0],base+order[0]);
            result.j.push(base+order[1],base+order[2]);
            result.k.push(base+order[2],base+order[3]);
        }
    }
    return result;
}
function lakeInterlayerSideFacetTrace(meshes,opts={},sourceOrdinals) {
    const facets=lakeInterlayerSideFacetMesh(meshes,opts.lineDensity,sourceOrdinals);
    if(!facets.i.length)return null;
    return {type:'mesh3d',name:'层间侧面（显示辅助）',...facets,color:'#7b8b84',opacity:.22,
        showscale:false,showlegend:false,flatshading:true,hoverinfo:'skip',
        lighting:{ambient:.68,diffuse:.32,specular:0,roughness:1},lightposition:{x:1000,y:-1200,z:1800},
        meta:{displayOnly:true,layerStructureFacets:true,waterbodyFrame:'network',
            sourceCellPairs:facets.sourceCellPairs,samplingStride:facets.samplingStride,sideTriangleCount:facets.i.length}};
}

function lakeDepthSource(data) {
    const different=data.surface_sync_mismatch===true||data.surface_synchronized?.some((row,j)=>row.some((same,i)=>same===false&&data.valid_geometry?.[j]?.[i]===true));
    return (data.depth_source || 'sigma + 静态水深')+(different?' · 深度采用三维状态水面，二维水位更新时刻不同':'');
}
function viz3dDepthAxis(data) {
    return data.depth_reference==='below native 3D geometry surface'?'水深 (m, 三维水面为0)':
        data.depth_reference==='below instantaneous water surface'?'水深 (m, 当前水面为0)':
        data.depth_reference==='below static bathymetric surface'?'水深 (m, 静态水面为0)':'水深 (m)';
}

// March tetrahedra in the supplied structured sigma cells. Plotly's regular
// isosurface grid cannot represent z coordinates that vary with local depth.
// Every cell corner must be valid; dry/missing columns never gain fake values.
function buildStructuredIsosurface(data,iso,ve=1,suppliedSamples) {
    const mesh={x:[],y:[],z:[],i:[],j:[],k:[],intensity:[],elevation:[]};
    const [nz,ny,nx]=data.shape || [];
    if(!Number.isFinite(iso) || ![nz,ny,nx].every(n=>Number.isInteger(n)&&n>=2))return mesh;
    const samples=suppliedSamples || lakeVolumeSamples(data,ve);
    if(!samples)return mesh;
    const tetrahedra=[[0,1,2,6],[0,2,3,6],[0,3,7,6],[0,7,4,6],[0,4,5,6],[0,5,1,6]];
    const intersections=new Map(),vertices=new Map(),faces=new Set();
    const vertex=(i,j,k)=>{const q=(k*ny+j)*nx+i;return {q,v:samples.values[q],e:data.elevation?.[k]?.[j]?.[i],p:[samples.x[q],samples.y[q],samples.z[q]]};};
    const intersection=(a,b)=>{
        // Stable edge order gives neighbouring cells identical coordinates.
        // A threshold at an original vertex shares that vertex across edges.
        if(a.q>b.q)[a,b]=[b,a];
        const key=a.v===iso?`v${a.q}`:b.v===iso?`v${b.q}`:`e${a.q},${b.q}`;
        if(intersections.has(key))return intersections.get(key);
        const span=b.v-a.v;
        const t=span===Infinity || span===-Infinity?(iso/2-a.v/2)/(b.v/2-a.v/2):(iso-a.v)/span;
        const height=a.v===iso?a.e:b.v===iso?b.e:
            Number.isFinite(a.e)&&Number.isFinite(b.e)?a.e*(1-t)+b.e*t:null;
        const point={key,p:a.v===iso?a.p:b.v===iso?b.p:a.p.map((v,c)=>v*(1-t)+b.p[c]*t),e:height};
        intersections.set(key,point);return point;
    };
    const triangle=(a,b,c,direction)=>{
        if(![...a.p,...b.p,...c.p].every(Number.isFinite))return;
        const u=b.p.map((v,n)=>v-a.p[n]),w=c.p.map((v,n)=>v-a.p[n]);
        const normal=[u[1]*w[2]-u[2]*w[1],u[2]*w[0]-u[0]*w[2],u[0]*w[1]-u[1]*w[0]];
        if(!normal.some(v=>Number.isFinite(v)&&v!==0))return;
        const key=[a.key,b.key,c.key].sort().join('|');
        if(faces.has(key))return;
        faces.add(key);
        if(normal.reduce((sum,v,n)=>sum+v*direction[n],0)<0)[b,c]=[c,b];
        const indices=[a,b,c].map(point=>{
            if(vertices.has(point.key))return vertices.get(point.key);
            const q=mesh.x.length;vertices.set(point.key,q);
            mesh.x.push(point.p[0]);mesh.y.push(point.p[1]);mesh.z.push(point.p[2]);mesh.intensity.push(iso);
            mesh.elevation.push(Number.isFinite(point.e)?point.e:null);
            return q;
        });
        mesh.i.push(indices[0]);mesh.j.push(indices[1]);mesh.k.push(indices[2]);
    };
    for(let k=0;k<nz-1;k++)for(let j=0;j<ny-1;j++)for(let i=0;i<nx-1;i++){
        const corners=[[i,j,k],[i+1,j,k],[i+1,j+1,k],[i,j+1,k],
            [i,j,k+1],[i+1,j,k+1],[i+1,j+1,k+1],[i,j+1,k+1]].map(p=>vertex(...p));
        if(corners.some(c=>!Number.isFinite(c.v)||!c.p.every(Number.isFinite)))continue;
        for(const indices of tetrahedra){
            const vertices=indices.map(q=>corners[q]),above=vertices.filter(v=>v.v>=iso),below=vertices.filter(v=>v.v<iso);
            if(!above.length||!below.length)continue;
            const direction=[0,1,2].map(c=>above.reduce((sum,v)=>sum+v.p[c]/above.length,0)-below.reduce((sum,v)=>sum+v.p[c]/below.length,0));
            if(above.length===1 || below.length===1){
                const singleton=above.length===1?above[0]:below[0],others=above.length===1?below:above;
                const points=others.map(v=>intersection(singleton,v));
                triangle(points[0],points[1],points[2],direction);
            }else{
                const ac=intersection(above[0],below[0]),ad=intersection(above[0],below[1]);
                const bc=intersection(above[1],below[0]),bd=intersection(above[1],below[1]);
                triangle(ac,ad,bd,direction);triangle(ac,bd,bc,direction);
            }
        }
    }
    return mesh;
}

function lakeStaticTraceKey(geometry,data,opts,identity,varName,showDepth) {
    if(!data.static_geometry_key || !identity || !geometry?.playbackTopologyKey)return null;
    return JSON.stringify([identity.path,identity.name,identity.revision,identity.outputRevision,
        data.static_geometry_key,geometry.playbackTopologyKey,varName,showDepth,
        data.coordinate_mode,data.coordinate_units,viz3dSampledBoundary(data),data.authoritative_boundary?.provenance?.identity||null,
        opts.showLand!==false,Number(opts.landNetworkLift)||.001,opts.meshMode||'continuous',
        opts.stack===true,opts.staticBathymetry===true,opts.dynamicOverlay===true]);
}
function lakeDisplayFrame(geometry,data={}) {
    const candidate=lakeValidatedDisplayBoundary(geometry,data);
    const clipped=candidate?lakeClipMeshToBoundary(geometry.surface,geometry,data):null;
    const clippedWalls=clipped?lakeClippedSurfaceWalls(clipped,geometry,data):null;
    const boundaryClipApplied=Boolean(candidate&&clipped&&clippedWalls);
    return {
        surface:boundaryClipApplied?clipped:geometry.surface,
        wallMesh:boundaryClipApplied?clippedWalls:geometry.walls,
        shoreline:boundaryClipApplied?lakeShorelineTrace(geometry,data):lakeShorelineTrace(geometry,data,{wetGridOnly:true}),
        boundaryClipApplied
    };
}
function lakeStaticWallPresentation(mesh,data={},ve=1) {
    const zSource=mesh?.z || mesh?.pz;
    if(!mesh||!Array.isArray(zSource)||!Number.isFinite(ve)||ve<=0)return {mesh,depthLimitM:null};
    // Wall feet already come from the wet-grid bed interpolation. At extreme
    // exaggeration cap only the display height relative to the horizontal span.
    const x=Array.isArray(data.xc)?data.xc.filter(Number.isFinite):[];
    const y=Array.isArray(data.yc)?data.yc.filter(Number.isFinite):[];
    const span=Math.max(x.length?Math.max(...x)-Math.min(...x):0,y.length?Math.max(...y)-Math.min(...y):0);
    const deepest=zSource.reduce((max,value)=>Number.isFinite(value)?Math.max(max,-value):max,0);
    const maxHeight=ve>80&&span>0?span*.12:Infinity;
    const scale=deepest>maxHeight?maxHeight/deepest:1;
    return {mesh:scale===1?mesh:{...mesh,z:zSource.map(value=>Number.isFinite(value)?value*scale:value)},
        depthLimitM:scale<1?maxHeight/ve:null};
}
function lakeStaticTraces(geometry,data,opts,identity,varName,showDepth) {
    const key=lakeStaticTraceKey(geometry,data,opts,identity,varName,showDepth);
    if(key && _viz3dLakeStaticTraceCache.has(key)) {
        const cached=_viz3dLakeStaticTraceCache.get(key);
        _viz3dLakeStaticTraceCache.delete(key);_viz3dLakeStaticTraceCache.set(key,cached);
        return cached;
    }
    const frame=lakeDisplayFrame(geometry,data);
    const shoreline=frame.shoreline;
    const clippedSurface=frame.surface;
    // Give the waterbody a clear, spatially coherent fill in basin views. A
    // scientific overlay remains visible through the surface when requested.
    const surfaceOpacity=opts.dynamicOverlay===true?.36:.78;
    const traces={surface:{type:'mesh3d',name:'水面',...clippedSurface,color:'#398eae',opacity:surfaceOpacity,
        showscale:false,showlegend:true,visible:true,hoverinfo:'skip',
        meta:{...clippedSurface.meta,waterbodyFrame:'surface'},
        lighting:{ambient:0.9,diffuse:0.2,specular:0.08,roughness:0.82}},shoreline,
        // Static depth previews use no tiled land plane, which otherwise
        // makes a sampled wet-mask shoreline read as a square raster edge.
        land:lakeLandTraces(data,opts.staticBathymetry===true?{...opts,showLand:false}:opts),
        boundaryClipApplied:frame.boundaryClipApplied,wallMesh:frame.wallMesh};
    if(key) {
        _viz3dLakeStaticTraceCache.set(key,traces);
        while(_viz3dLakeStaticTraceCache.size>12)_viz3dLakeStaticTraceCache.delete(_viz3dLakeStaticTraceCache.keys().next().value);
    }
    return traces;
}
// Fade a narrow presentation band inward from confirmed wet-cell boundaries.
// This display-only trace never extends the water footprint or changes native
// bathymetry, masks, solver geometry, or per-cell values.
function lakeShorelineFeatherTrace(geometry,featherFraction=.48) {
    const surface=geometry?.surface,walls=geometry?.walls;
    if(!surface||!walls||!Number.isFinite(featherFraction)||featherFraction<=0||featherFraction>=.5||
            surface.x?.length<4||walls.px?.length<4)return null;
    const pointKey=(x,y)=>`${Number(x).toPrecision(14)},${Number(y).toPrecision(14)}`;
    const edgeKey=(a,b)=>[pointKey(a[0],a[1]),pointKey(b[0],b[1])].sort().join('|');
    const centers=new Map(),sides=[[0,1],[1,2],[2,3],[3,0]];
    for(let q=0;q+3<surface.x.length;q+=4){
        const points=Array.from({length:4},(_,n)=>[surface.x[q+n],surface.y[q+n]]);
        const center=points.reduce((sum,p)=>[sum[0]+p[0]/4,sum[1]+p[1]/4],[0,0]);
        for(const [a,b] of sides)centers.set(edgeKey(points[a],points[b]),center);
    }
    const trace={type:'mesh3d',name:'Wet-grid edge softening (display aid)',x:[],y:[],z:[],i:[],j:[],k:[],vertexcolor:[],
        opacity:1,showscale:false,showlegend:false,hoverinfo:'skip',lighting:{ambient:1,diffuse:0,specular:0,roughness:1},
        meta:{displayOnly:true,waterbodyFrame:'shorelineAntialias',source:'wet-mask-boundary-inside-wet-cells',
            featherFraction,geographicPrecision:false}};
    for(let q=0;q+3<walls.px.length;q+=4){
        const a=[walls.px[q],walls.py[q]],b=[walls.px[q+2],walls.py[q+2]],center=centers.get(edgeKey(a,b));
        if(!center)continue;
        const midpoint=[(a[0]+b[0])/2,(a[1]+b[1])/2];
        // Spread a background tint across 48% of each confirmed wet boundary
        // cell. The opaque outer edge blends the raster silhouette into the
        // plot background; the inward fade softens it without changing mesh.
        const inward=[(center[0]-midpoint[0])*featherFraction,(center[1]-midpoint[1])*featherFraction];
        const innerA=[a[0]+inward[0],a[1]+inward[1]],innerB=[b[0]+inward[0],b[1]+inward[1]];
        const base=trace.x.length;
        for(const [x,y,alpha] of [[a[0],a[1],1],[b[0],b[1],1],[innerB[0],innerB[1],0],[innerA[0],innerA[1],0]]){
            trace.x.push(x);trace.y.push(y);trace.z.push(0);
            trace.vertexcolor.push(`rgba(247,250,251,${alpha})`);
        }
        trace.i.push(base,base);trace.j.push(base+1,base+2);trace.k.push(base+2,base+3);
    }
    return trace.i.length?trace:null;
}
function lakeRaiseShorelineTraces(traces,geometry,includeFeather=true) {
    const featherIndex=traces.findIndex(trace=>trace.meta?.waterbodyFrame==='shorelineAntialias');
    let feather=featherIndex>=0?traces.splice(featherIndex,1)[0]:null;
    if(!feather&&includeFeather)feather=lakeShorelineFeatherTrace(geometry);
    if(feather)traces.push(feather);
    const shorelineIndex=traces.findIndex(trace=>trace.meta?.shoreline===true);
    if(shorelineIndex>=0)traces.push(traces.splice(shorelineIndex,1)[0]);
    return traces;
}
function lakeSurfaceDepthProjection(surface,data) {
    const bottom=data?.bottom || data?.depth,cells=surface?.cell;
    if(!Array.isArray(bottom)||!Array.isArray(cells)||cells.length!==surface.x?.length||!cells.length)return null;
    const intensity=[],native=[];
    const topology=data?.display_topology;
    const wet=(i,j)=>i>=0&&j>=0&&j<bottom.length&&i<(bottom[j]?.length||0)&&
        Number.isFinite(bottom[j][i])&&bottom[j][i]>0&&(!topology||topology.wet_mask?.[j]?.[i]===true);
    for(let n=0;n<cells.length;n++){
        const cell=cells[n];
        const [i,j]=cell || [],depth=bottom[j]?.[i];
        if(!Number.isFinite(depth)||depth<=0)return null;
        native.push(depth);
        // Match the bed's connected adjacent-wet-cell corner interpolation.
        // Keep this local: extracted render harnesses evaluate this helper alone.
        const u=n%4===1||n%4===2?i+1:i,v=n%4>=2?j+1:j;
        const adjacent=[[i,j]],seen=new Set([`${i},${j}`]);
        for(let p=0;p<adjacent.length;p++)for(const [x,y] of [[u-1,v-1],[u,v-1],[u,v],[u-1,v]]){
            if(!wet(x,y)||seen.has(`${x},${y}`)||Math.abs(x-adjacent[p][0])+Math.abs(y-adjacent[p][1])!==1)continue;
            seen.add(`${x},${y}`);adjacent.push([x,y]);
        }
        const values=adjacent.map(([x,y])=>bottom[y][x]);
        intensity.push(values.reduce((sum,value)=>sum+value,0)/values.length);
    }
    return {intensity,customdata:native};
}
function viz3dWaterbodyDiagnosticMode(search=typeof window!=='undefined' ? window.location?.search || '' : '') {
    const supported=new Set(['force-bed','skip-wall','skip-field','skip-bed','bed-depth-colors','force-bed-neutral','force-bed-neutral-scale']);
    return new URLSearchParams(search).getAll('viz3d-diagnostic')
        .flatMap(value=>value.split(',')).map(value=>value.trim()).filter(mode=>supported.has(mode));
}
function viz3dFilterWaterbodyDiagnosticTraces(traces,modes,overlay=true) {
    return overlay && modes.includes('skip-field')
        ? traces.filter(trace=>!['field','missing'].includes(trace.meta?.waterbodyFrame))
        : traces;
}
function lakeClippedSurfaceWalls(surface,geometry,data={}) {
    if(!surface?.i?.length||!surface?.j?.length||!surface?.k?.length||!Array.isArray(surface.cell))return null;
    const boundary=lakeValidatedDisplayBoundary(geometry,data),floor=geometry?.floor;
    if(!boundary||!floor?.cell?.length||!floor?.z?.length||!Array.isArray(data.xc)||!Array.isArray(data.yc))return null;
    const floorCells=new Map();
    for(let q=0;q+3<floor.cell.length;q+=4){
        const cell=floor.cell[q];if(cell)floorCells.set(`${cell[0]},${cell[1]}`,q);
    }
    const axisCellsAt=(values,value)=>{
        const edges=lakeCellEdges(values),indices=[];
        for(let i=0;i+1<edges.length;i++)if(value>=Math.min(edges[i],edges[i+1])-1e-10&&value<=Math.max(edges[i],edges[i+1])+1e-10)indices.push(i);
        return indices;
    };
    const depthAt=(q,x,y)=>{
        const x0=floor.x[q],x1=floor.x[q+1],y0=floor.y[q],y1=floor.y[q+3];
        if(Math.abs(x1-x0)<=1e-12||Math.abs(y1-y0)<=1e-12)return null;
        const u=Math.max(0,Math.min(1,(x-x0)/(x1-x0))),v=Math.max(0,Math.min(1,(y-y0)/(y1-y0)));
        const z00=floor.z[q],z10=floor.z[q+1],z11=floor.z[q+2],z01=floor.z[q+3];
        if(![z00,z10,z11,z01].every(Number.isFinite))return null;
        return z00*(1-u)*(1-v)+z10*u*(1-v)+z11*u*v+z01*(1-u)*v;
    };
    const walls={x:[],y:[],z:[],i:[],j:[],k:[]},triangleBudget=200000;
    const addSegment=(a,b)=>{
        const mx=(a[0]+b[0])/2,my=(a[1]+b[1])/2;
        let cellQuad=null;
        for(const j of axisCellsAt(data.yc,my))for(const i of axisCellsAt(data.xc,mx)){
            const q=floorCells.get(`${i},${j}`);if(Number.isInteger(q)){cellQuad=q;break;}
        }
        if(!Number.isInteger(cellQuad))return;
        const za=depthAt(cellQuad,...a),zb=depthAt(cellQuad,...b);
        if(!Number.isFinite(za)||!Number.isFinite(zb)||za>0||zb>0)return;
        if(walls.i.length+2>triangleBudget)throw new RangeError('clipped boundary wall triangle budget exceeded');
        const base=walls.x.length;
        walls.x.push(a[0],a[0],b[0],b[0]);walls.y.push(a[1],a[1],b[1],b[1]);walls.z.push(0,za,0,zb);
        walls.i.push(base,base);walls.j.push(base+1,base+3);walls.k.push(base+3,base+2);
    };
    const xEdges=[...new Set(Array.from({length:floor.x.length},(_,q)=>floor.x[q]).filter(Number.isFinite))].sort((a,b)=>a-b);
    const yEdges=[...new Set(Array.from({length:floor.y.length},(_,q)=>floor.y[q]).filter(Number.isFinite))].sort((a,b)=>a-b);
    try {
        for(const group of boundary.groups)for(const ring of [group.outer,...(group.holes||[])]){
            const count=ring.length>1&&ring[0][0]===ring.at(-1)[0]&&ring[0][1]===ring.at(-1)[1]?ring.length-1:ring.length;
            for(let n=0;n<count;n++){
                const a=ring[n],b=ring[(n+1)%count],dx=b[0]-a[0],dy=b[1]-a[1];
                if(Math.hypot(dx,dy)<=1e-12)continue;
                const breaks=[0,1];
                if(Math.abs(dx)>1e-12)for(const x of xEdges){const t=(x-a[0])/dx;if(t>1e-10&&t<1-1e-10)breaks.push(t);}
                if(Math.abs(dy)>1e-12)for(const y of yEdges){const t=(y-a[1])/dy;if(t>1e-10&&t<1-1e-10)breaks.push(t);}
                const sorted=[...new Set(breaks)].sort((u,v)=>u-v);
                for(let k=0;k+1<sorted.length;k++){
                    const at=t=>[a[0]+dx*t,a[1]+dy*t];
                    addSegment(at(sorted[k]),at(sorted[k+1]));
                }
            }
        }
    } catch(error) {
        if(error instanceof RangeError&&error.message==='clipped boundary wall triangle budget exceeded')return null;
        throw error;
    }
    return walls.i.length?{...walls,meta:{displayOnly:true,source:'clipped-polygon-rings',provenance:boundary.provenance,
        includesOuterAndHoleRings:true,internalWetCellSeamsExcluded:true}}:null;
}
function lakeTraces(geometry, showDepth = true, data={},style=null,opts={},identity=null,varName='') {
    const maxDepth=geometry.maxDepth;
    const bed=geometry.floor;
    const highVeOverlay=opts.dynamicOverlay===true && geometry.ve>80;
    const forceBedNeutral=opts.forceBedNeutral===true && geometry.ve>80;
    const forceBedNeutralScale=opts.forceBedNeutralScale===true && geometry.ve>80;
    const contours=buildLakeContours(geometry,lakeDepthLevels(maxDepth));
    const staticTraces=lakeStaticTraces(geometry,data,opts,identity,varName,showDepth);
    // The display frame chooses either the same clipped geometry for water,
    // walls and outline, or the complete native wet-grid fallback.
    const wallPresentation=opts.staticBathymetry===true
        ?lakeStaticWallPresentation(staticTraces.wallMesh,data,geometry.ve):{mesh:staticTraces.wallMesh,depthLimitM:null};
    const wallMesh=wallPresentation.mesh;
    // Display-only 0.2% depth lift prevents coplanar line/mesh flicker;
    // the contour solver, labels, bathymetry and scientific data stay exact.
    const lineLift=maxDepth*geometry.ve*0.002;
    const lift=z=>z.map(v=>v===null ? null : v+lineLift);
    const ticks=viz3dTicks(0,maxDepth);
    const colorbar=viz3dColorbar(opts.staticBathymetry===true?'湖底深度':'水深','m',style || {tickvals:ticks.values,ticktext:ticks.labels});
    const depthStyle=viz3dValidStyle(style)?style:{min:0,max:maxDepth};
    // Bathymetry belongs on the basin floor. Painting it onto the z=0 plane
    // made the static view look like a flat blue raster and hid water volume.
    // Keep the water material and the source-derived basin as separate traces.
    const waterSurface=staticTraces.surface;
    const traces=[
    // Keep the high-VE dynamic bed visible on its own depth scale; the black-patch cause remains unconfirmed.
        // Temporary presentation policy: omit the basin fill while keeping an explicit opt-in
        // so it can be restored if later model evidence warrants showing it again.
        ...((opts.showBedSurface===true) && !opts.skipBedTrace && (showDepth || geometry.ve<=80 || highVeOverlay || opts.forceBedTrace===true)?[{type:'mesh3d',name:'湖盆水深',...geometry.floor,customdata:geometry.floor.intensity,
            meta:{waterbodyFrame:'bed',displayOnly:true},
            // Interpolate the actual corner depths over one continuous basin surface.
            // The selectable triangle/orthogonal network is a separate line trace below.
            intensity:geometry.floor.intensity,intensitymode:'vertex',flatshading:false,
            // Neutral bed fills use the same intensity/colorscale path as depth beds;
            // Plotly mesh3d direct color reproduced black patches in the frame-19 audit.
            ...(forceBedNeutralScale || forceBedNeutral
                ? {colorscale:[[0,'#c5cdd1'],[1,'#c5cdd1']]}
                : showDepth || opts.bedDepthColors===true || highVeOverlay
                    ? {colorscale:VIZ3D.depthScale}
                    : {colorscale:[[0,'#c5cdd1'],[1,'#c5cdd1']]}),
            // Bed intensity is always depth in metres; never inherit the selected field's range.
            cmin:opts.staticBasin===true?depthStyle.min:0,
            cmax:opts.staticBasin===true?depthStyle.max:maxDepth,cauto:false,showscale:showDepth,showlegend:true,colorbar,opacity:1,
            lighting:{ambient:1,diffuse:0,specular:0,roughness:1},
            lightposition:{x:1000,y:-2000,z:3000},
            hovertemplate:viz3dHorizontalHover(data)+'<br>'+(highVeOverlay?'床面底深':'显示角点水深')+' %{customdata:.2f} m（邻近湿单元插值）<extra>湖盆</extra>',
            }]:[]),
        opts.staticBasin===true || opts.staticBathymetry===true?{...waterSurface,opacity:.58}:waterSurface,
            // At extreme VE the display-only shoreline curtain overwhelms the basin; keep the shoreline trace without these oversized faces.
        ...(wallMesh&&!opts.skipWallTrace && (opts.staticBathymetry===true || geometry.ve<=80)?[{type:'mesh3d',name:'湿网格边界剖面',x:wallMesh.x||wallMesh.px,y:wallMesh.y||wallMesh.py,z:wallMesh.z||wallMesh.pz,
            i:wallMesh.i,j:wallMesh.j,k:wallMesh.k,color:'#628f9b',opacity:opts.staticBathymetry===true?.28:.48,showscale:false,showlegend:false,
            lighting:{ambient:1,diffuse:0,specular:0,roughness:1},
            hoverinfo:'skip',meta:{waterbodyFrame:'wall',displayOnly:true,source:staticTraces.boundaryClipApplied?'clipped-wet-surface-boundary':'wet-mask-boundary',
                ...(wallPresentation.depthLimitM!==null?{wallDepthLimitM:wallPresentation.depthLimitM,schematicShorelineDepth:true}:{})}},
        ]:[]),
        staticTraces.shoreline,
        {type:'scatter3d',name:'等深线',mode:'lines',x:contours.x,y:contours.y,z:lift(contours.z),customdata:contours.depth,
            line:{color:'rgba(27,62,76,0.65)',width:2},hovertemplate:'水深 %{customdata:.2f} m<extra>等深线</extra>',
            meta:{waterbodyFrame:'contour'},
            },
        ...staticTraces.land,
        ...(opts.staticBathymetry&&!staticTraces.boundaryClipApplied?lakeCoastalRimTrace(geometry,data):[]),
        ...(showDepth?lakeDisplayLines(geometry.floor,geometry,opts,data):[])
    ];
    return lakeRaiseShorelineTraces(traces,geometry,opts.staticBathymetry===true);
}

/**
 * 立体湖泊渲染：网格湖盆 + 水面 + 实际陆水边界，可选择科学变量覆盖。
 */
async function render3DWaterBody(varName, timestep, opts = {}) {
    const container = document.getElementById('viz3d-plotly');
    if (!container) return;
    if (!VIZ3D.plotlyReady()) { viz3dError('Plotly 未加载。请使用二维视图或空间剖面。'); return; }
    const request = viz3dBegin(container,varName,timestep,opts);
    viz3dLoading('加载湖盆与水体数据…',request);
    try {
        const requestedLevel=Number(opts.level);
        const stack=opts.stack===true;
        const hasRequestedLevel=opts.level!==undefined && Number.isInteger(requestedLevel) && requestedLevel>=0;
        const levelQuery=stack
            ? (hasRequestedLevel?`&level=${requestedLevel}`:'')
            : `&level=${hasRequestedLevel?requestedLevel:-1}&layer_only=1&waterbody_compact=1`;
        const d = await viz3dFetch(request,`/api/results/3d_surface?var=${encodeURIComponent(varName)}&time=${timestep}&target=${opts.target || 26}${levelQuery}`);
        if (!viz3dCurrent(request) || !d) return;
        if (d.error) {
            if(viz3dHasNoDynamicOutput(d.error)) {
                await renderBathymetry3D({...opts,staticPreviewReason:d.error});
                return;
            }
            viz3dError(d.error,request); return;
        }
        if(!lakeDisplayTopologyReady(d)) {
            viz3dError(d.display_topology_error || '降采样显示缺少有效原生水陆拓扑，已停止绘制以避免跨越干格。',request);return;
        }
        if(d.bathymetry_geometry_error || (d.depth_geometry_error && opts.overlay!==false)){
            viz3dError(d.bathymetry_geometry_error || d.depth_geometry_error,request);return;
        }
        const [nz,ny,nx] = d.shape || [];
        const xc = d.xc, yc = d.yc;
        if (!xc || !yc || xc.length!==nx || yc.length!==ny || !d.bottom) {
            viz3dError('缺少湖盆水深或水平坐标，无法显示真实水体。',request); return;
        }
        const basin=opts.overlay===false?d.bottom:d.water_depth || d.bottom;
        const ve = lakeVerticalScale(xc,yc,basin,opts.ve);
        const geometryStartedAt=viz3dNow();
        const geometry = lakeGeometryForFrame(xc,yc,basin,ve,d.display_topology,d.valid_geometry,d.static_geometry_key);
        window.PlaybackPerformance?.stage(request.playbackPerf,'geometry',viz3dNow()-geometryStartedAt);
        if (!geometry) { viz3dError('没有正水深的有效水域。',request); return; }
        // API layer ordinals are physical, bottom-to-surface indices after
        // native padding is removed. Sampling must never renumber them.
        const layerIndices=d.layer_indices || Array.from({length:nz},(_,k)=>k);
        const totalLayers=d.total_layers || nz;
        const originalLevel=opts.level!==undefined && Number.isInteger(requestedLevel) && requestedLevel>=0
            ? Math.min(totalLayers-1,requestedLevel) : totalLayers-1;
        const lv=layerIndices.indexOf(originalLevel);
        if(lv<0) {viz3dError(`所选原始层 ${originalLevel} 未包含在采样数据中，请重新加载。`,request);return;}
        const fractions = d.sigma?.length===nz ? sigmaToFraction(d.sigma) : Array.from({length:nz},(_,k)=>1-(k+0.5)/nz);
        const overlay = opts.overlay !== false;
        const diagnosticModes=viz3dWaterbodyDiagnosticMode();
        const levels=stack ? layerIndices.flatMap((ordinal,k)=>ordinal<=originalLevel ? [k] : []) : [lv];
        const coverage=overlay?lakeCoverage(d,levels):null;
        const style=overlay ? viz3dStyle(coverage.valid?d:{...d,min:null,max:null},varName,request) : viz3dStyle({min:0,max:geometry.maxDepth},'__bathy__',request);
        const opacity=stack ? Math.min(.55,viz3dOpacity(opts)) : viz3dOpacity(opts);
        const warning=[
            overlay && opacity<1 ? '透明叠层/切片会混色；定量读色请使用不透明单层' : '',
            overlay && ve>80 ? '高垂向放大（>80×）：床面按湖底深度（m）着色，与所选变量色阶分离；黑片成因尚未确认' : ''
        ].filter(Boolean).join(' · ');
        const baseTracesStartedAt=viz3dNow();
        let traces = lakeTraces(geometry,!overlay,d,overlay?null:style,
            {...opts,skipWallTrace:opts.skipWallTrace===true || diagnosticModes.includes('skip-wall'),
                skipBedTrace:opts.skipBedTrace===true || (overlay&&diagnosticModes.includes('skip-bed')),
                forceBedTrace:overlay && diagnosticModes.includes('force-bed'),
                dynamicOverlay:overlay,
                forceBedNeutral:diagnosticModes.includes('force-bed-neutral'),
                forceBedNeutralScale:diagnosticModes.includes('force-bed-neutral-scale'),
                bedDepthColors:overlay && diagnosticModes.includes('force-bed') && diagnosticModes.includes('bed-depth-colors'),
                ...(!overlay?{staticBathymetry:true,staticBasin:true,showBedSurface:opts.showBedSurface===true}:{})},request.identity,varName);
        window.PlaybackPerformance?.stage(request.playbackPerf,'baseTraces',viz3dNow()-baseTracesStartedAt);
        request.renderedMeshMode=traces.find(trace=>trace.meta?.networkMode)?.meta?.networkMode || null;
        const baseTraceCount=traces.length;
        const numericTraces=[];
        if (overlay) {
            const fieldMeshStartedAt=viz3dNow();
            let cornerAveragesMs=0,layerMeshMs=0,traceAssemblyMs=0;
            const stackedField=stack?{x:[],y:[],z:[],intensity:[],customdata:[],cell:[],i:[],j:[],k:[]}:null;
            const stackedMissing=stack?{x:[],y:[],z:[],customdata:[],cell:[],i:[],j:[],k:[]}:null;
            const stackedFieldLayers=[],stackedMissingLayers=[];
            // Use wet-cell quads for fields too: surfaces at cell centers drop
            // thin peninsulas and can bridge diagonally across dry cells.
            for (const k of levels) {
                const meshMode=opts.meshMode || 'continuous';
                const smooth=meshMode==='continuous';
                const cornerAveragesStartedAt=viz3dNow();
                const cornerAverages=lakeLayerCornerAverages(geometry,d,k,smooth);
                cornerAveragesMs+=viz3dNow()-cornerAveragesStartedAt;
                const layerMeshStartedAt=viz3dNow();
                const {fieldMesh:nativeMesh,missingMesh:nativeMissing}=lakeLayerMeshes(geometry,d,k,ve,smooth,cornerAverages);
                const mesh=lakeClipMeshToBoundary(nativeMesh,geometry,d)||nativeMesh;
                const missing=lakeClipMeshToBoundary(nativeMissing,geometry,d)||nativeMissing;
                layerMeshMs+=viz3dNow()-layerMeshStartedAt;
                const traceAssemblyStartedAt=viz3dNow();
                if(missing.i.length) {
                    if(stack) {lakeAppendLayerMesh(stackedMissing,missing,layerIndices[k]);stackedMissingLayers.push(layerIndices[k]);}
                    else traces.push({type:'mesh3d',name:`水域缺测 · 层 ${layerIndices[k]}`,...missing,
                    color:style.nanColor || '#c9cbd0',opacity,showscale:false,
                    meta:{missingWater:true,waterbodyFrame:'missing',layerOrdinals:[layerIndices[k]]},
                    lighting:{ambient:1,diffuse:0,specular:0,roughness:1},
                    hovertemplate:`层 ${layerIndices[k]} · 单元中心 X %{customdata[2]} · Y %{customdata[3]}<br>单元中心水深 %{customdata[0]} m<br>变量缺测<extra>水域缺测</extra>`});
                }
                if(!mesh.i.length) {traceAssemblyMs+=viz3dNow()-traceAssemblyStartedAt;continue;}
                const top=k===lv;
                const ordinal=layerIndices[k];
                if(stack) {
                    lakeAppendLayerMesh(stackedField,mesh,ordinal);stackedFieldLayers.push(ordinal);
                    traceAssemblyMs+=viz3dNow()-traceAssemblyStartedAt;continue;
                }
                const faceted=meshMode==='triangles';
                const field={type:'mesh3d',name:`${viz3dEscape(viz3dLabel(d,varName))} · 层 ${ordinal}`,...mesh,
                    meta:{scientificField:true,waterbodyFrame:'field',layerOrdinals:[ordinal],displayOnlyFacetLighting:faceted,
                        displayClipSource:mesh.meta?.source||null,displayClipProvenance:mesh.meta?.provenance||null},
                    colorscale:style.colorscale,cmin:style.min,cmax:style.max,cauto:false,
                    showscale:top && viz3dValidStyle(style),opacity,flatshading:faceted,
                    // Directional contrast is a display cue on the field only; values and colorscale remain unchanged.
                    lighting:faceted?lakeFacetLighting():{ambient:1,diffuse:0,specular:0,roughness:1},
                    ...(faceted?{lightposition:{x:1000,y:-1200,z:1800}}:{}),
                    colorbar:viz3dColorbar(viz3dLabel(d,varName),d.units,style),
                    hovertemplate:`层 ${ordinal} · 单元中心 X %{customdata[2]:.6~g} · Y %{customdata[3]:.6~g} ${viz3dEscape(d.coordinate_units || 'm')}<br>单元中心水深 %{customdata[0]:.4~g} m`+
                        (d.elevation?'<br>模型基准高程 %{customdata[1]:.4~g} m':'<br>模型基准高程未提供')+
                        `<br>单元中心原值 %{customdata[6]:.8~g} ${viz3dEscape(d.units)}${viz3dReference(varName)}<extra>${viz3dEscape(viz3dLabel(d,varName))} · 层 ${ordinal}</extra>`};
                traces.push(field);numericTraces.push(field);
                traceAssemblyMs+=viz3dNow()-traceAssemblyStartedAt;
            }
            if(stack&&stackedMissing.i.length)traces.push({type:'mesh3d',name:`水域缺测 · ${stackedMissingLayers.length}层`,...stackedMissing,
                color:style.nanColor || '#c9cbd0',opacity,showscale:false,
                meta:{missingWater:true,waterbodyFrame:'missing',layerOrdinals:stackedMissingLayers},
                lighting:{ambient:1,diffuse:0,specular:0,roughness:1},
                hovertemplate:'层 %{customdata[7]} · 单元中心 X %{customdata[2]} · Y %{customdata[3]}<br>单元中心水深 %{customdata[0]} m<br>变量缺测<extra>水域缺测</extra>'});
            if(stack&&stackedField.i.length) {
                const faceted=opts.meshMode==='triangles';
                const field={type:'mesh3d',name:`${viz3dEscape(viz3dLabel(d,varName))} · 垂向堆叠 (${stackedFieldLayers.length}层)`,...stackedField,
                    meta:{scientificField:true,waterbodyFrame:'field',layerOrdinals:stackedFieldLayers,displayOnlyFacetLighting:faceted},
                    colorscale:style.colorscale,cmin:style.min,cmax:style.max,cauto:false,
                    showscale:viz3dValidStyle(style),opacity,flatshading:opts.meshMode==='triangles',
                    // Keep the derived field facet shading distinct from bed material and numeric field encoding.
                    lighting:faceted?lakeFacetLighting():{ambient:1,diffuse:0,specular:0,roughness:1},
                    ...(faceted?{lightposition:{x:1000,y:-1200,z:1800}}:{}),
                    colorbar:viz3dColorbar(viz3dLabel(d,varName),d.units,style),
                    hovertemplate:'层 %{customdata[7]} · 单元中心 X %{customdata[2]:.6~g} · Y %{customdata[3]:.6~g} '+
                        `${viz3dEscape(d.coordinate_units || 'm')}<br>单元中心水深 %{customdata[0]:.4~g} m`+
                        (d.elevation?'<br>模型基准高程 %{customdata[1]:.4~g} m':'<br>模型基准高程未提供')+
                        `<br>单元中心原值 %{customdata[6]:.8~g} ${viz3dEscape(d.units)}${viz3dReference(varName)}<extra>${viz3dEscape(viz3dLabel(d,varName))} · 层 %{customdata[7]}</extra>`};
                traces.push(field);numericTraces.push(field);
            }
            if(traces.length===baseTraceCount) { viz3dError('该层没有有效变量数据，请切换层或选择湖盆预览。',request);return; }
            const networkMeshStartedAt=viz3dNow();
            const networkMeshes=['triangles','orthogonal'].includes(opts.meshMode)
                ? lakePhysicalVolumeNetwork(d,geometry,ve,stack?undefined:[lv]):[];
            window.PlaybackPerformance?.stage(request.playbackPerf,'networkMesh',viz3dNow()-networkMeshStartedAt);
            if(stack&&opts.meshMode==='triangles') {
                const facetMeshes=levels.map(layer=>networkMeshes[layer]).filter(Boolean);
                const facets=lakeInterlayerSideFacetTrace(facetMeshes,opts,levels.map(layer=>layerIndices[layer]));
                if(facets)traces.push(facets);
            }
            const displayLinesStartedAt=viz3dNow();
            traces.push(...lakeDisplayLines(networkMeshes,geometry,lakeWaterbodyDisplayOptions({...opts,displayLayerOrdinals:stack?layerIndices:[originalLevel]},stack),d));
            window.PlaybackPerformance?.stage(request.playbackPerf,'displayLines',viz3dNow()-displayLinesStartedAt);
            window.PlaybackPerformance?.stage(request.playbackPerf,'cornerAverages',cornerAveragesMs);
            window.PlaybackPerformance?.stage(request.playbackPerf,'layerMesh',layerMeshMs);
            window.PlaybackPerformance?.stage(request.playbackPerf,'traceAssembly',traceAssemblyMs);
            window.PlaybackPerformance?.stage(request.playbackPerf,'fieldMesh',viz3dNow()-fieldMeshStartedAt);
            request.renderedMeshMode=traces.find(trace=>trace.meta?.networkMode)?.meta?.networkMode || null;
            // The requested upper slice may be entirely missing in a stack.
            // The last actual data layer still needs a quantitative legend.
            if(numericTraces.length)numericTraces.at(-1).showscale=true;
        }
        traces=lakeRaiseShorelineTraces(traces,geometry,overlay);
        traces=viz3dFilterWaterbodyDiagnosticTraces(traces,diagnosticModes,overlay);
        const maxDepth=geometry.maxDepth;
        const datum=viz3dDepthAxis(overlay?d:{...d,depth_reference:'below static bathymetric surface'});
        const detail=(overlay ? `${datum} · ${viz3dTime(timestep,opts,d)} · 层 ${stack?'0–':''}${originalLevel}/${totalLayers-1} · 垂向 ${ve}× · ${viz3dRangeLabel(style)}`
            : `静态水体预览 · 湖底隐藏；半透明蓝色水面与湿网格侧壁展示体积 · ${datum} · 垂向 ${ve}×`)+(overlay?` · ${lakeDepthSource(d)}`:'')+(viz3dSampling(d)?` · ${viz3dSampling(d)}`:'')+lakeDisplayDetail(d,{...opts,staticBathymetry:!overlay,displayBoundaryStatus:!overlay?lakeDisplayBoundaryStatus(geometry,d):undefined,scalarInterpolation:overlay},coverage);
        const layout=Object.assign({},VIZ3D.layout,{
            title:viz3dTitle(overlay ? viz3dLabel(d,varName) : '湖盆地形 · bathymetry.nc',
                detail+(warning ? ` · ${warning}` : '')),
        scene:lakeScene(ve,maxDepth,overlay?d:{...d,depth_reference:'below static bathymetric surface'},opts.meshMode==='triangles'?.025:.05),showlegend:true, uirevision:'lake-view'
        });
        const updateKey=overlay?JSON.stringify({identity:request.identity,
            variable:varName,levels,stack,target:opts.target || 26,
            coordinate:[d.coordinate_mode,d.coordinate_units,d.sampling_stride],meshMode:opts.meshMode || 'continuous',
            showLand:opts.showLand!==false,lineDensity:opts.lineDensity,lineRefinement:opts.lineRefinement,
            showNetworkNodes:opts.showNetworkNodes===true,opacity,nanColor:style.nanColor,colorscale:style.colorscale}):null;
        request.main={data:d,mode:'waterbody',ve,updateKey,geometryKey:geometry.playbackCacheKey,
            topologyKey:geometry.playbackTopologyKey};
        await viz3dPlot(container,traces,layout,{responsive:true,scrollZoom:true,displaylogo:false,
            toImageButtonOptions:{format:'png',filename:viz3dFilename('lake',varName,timestep,opts,`layer${originalLevel}_ve${ve}`)}},request);
        viz3dDone(request,d,overlay?'viz3d-iso-var':null,detail,warning,overlay ? {range:style,level:originalLevel,ve,stack}
            : {variable:'__bathy__',label:'湖盆地形',units:'m',min:0,max:maxDepth,range:style,field:d.bottom,date:'地形预览',level:null,ve});
    } catch(e) {viz3dFailure(e,request);}
}

// GOTM results have one horizontal cell and a real vertical water column.
// Keep that geometry as one x/y position with its native h+z depth centres;
// spreading it into a lake-shaped cloud would invent horizontal information.
async function render3DSingleColumn(data,varName,timestep,request) {
    const depths=Array.isArray(data.column_depth_m)?data.column_depth_m:[];
    const values=(Array.isArray(data.data)?data.data.flat(Infinity):[]).map(Number);
    const n=Math.min(depths.length,values.length);
    if(!n || !depths.slice(0,n).every(Number.isFinite)) {
        viz3dError('单水柱结果缺少有效的原生垂向深度坐标。',request);return;
    }
    const style=viz3dStyle(data,varName,request);
    if(!viz3dValidStyle(style) || !values.slice(0,n).some(Number.isFinite)) {
        viz3dError('该时步无有效水柱数据（全为空值）',request);return;
    }
    const validDepths=[],validValues=[];
    for(let k=0;k<n;k++) if(Number.isFinite(values[k])) {validDepths.push(depths[k]);validValues.push(values[k]);}
    const name=viz3dLabel(data,varName),units=data.units || '';
    const trace={type:'scatter3d',mode:'markers',x:validDepths.map(()=>0),y:validDepths.map(()=>0),z:validDepths,
        marker:{size:5,color:validValues,showscale:true,colorscale:style.colorscale,cmin:style.min,cmax:style.max,cauto:false,
            colorbar:viz3dColorbar(name,units,style)},name:viz3dEscape(name),
        customdata:validValues,hovertemplate:'单水柱（x=1，y=1）<br>水深 %{z:.3f} m<br>%{customdata:.8~g} '+viz3dEscape(units)+viz3dReference(varName)+'<extra>'+viz3dEscape(name)+'</extra>'};
    const detail=`单水柱（x=1，y=1） · ${viz3dTime(timestep,request.opts,data)} · ${validDepths.length} 个原生垂向层 · 保留 GOTM h+z 深度坐标 · ${viz3dRangeLabel(style)}`;
    const layout={...VIZ3D.layout,title:viz3dTitle(name,detail),showlegend:false,
        scene:{...VIZ3D.layout.scene,xaxis:{title:'单水柱',visible:false,showticklabels:false,showgrid:false,zeroline:false},
            yaxis:{title:'单水柱',visible:false,showticklabels:false,showgrid:false,zeroline:false},
            zaxis:{title:'水深 (m，水面为0)',autorange:'reversed',showgrid:true},
            aspectratio:{x:.16,y:.16,z:1},camera:{projection:{type:'orthographic'}}}};
    request.main={data,mode:'single_column',ve:1};
    await viz3dPlot('viz3d-plotly',[trace],layout,{responsive:true,displayModeBar:true,displaylogo:false,scrollZoom:true,
        toImageButtonOptions:{format:'png',filename:viz3dFilename('column',varName,timestep,request.opts)}},request);
    viz3dDone(request,data,'viz3d-iso-var',detail,'',{range:style,level:'原生垂向水柱',geometryMode:'single_column'});
}

/**
 * Render a fast 3D point cloud (scatter3d) for the given variable/timestep.
 */
async function render3DCloud(varName, timestep, target = 22, opts = {}) {
    const containerId = 'viz3d-plotly';
    const container = document.getElementById(containerId);
    if (!container) return;
    if (!VIZ3D.plotlyReady()) {
        viz3dError('Plotly 未加载。请使用二维视图或空间剖面。');
        return;
    }
    const request = viz3dBegin(container,varName,timestep,opts);
    viz3dLoading('加载3D点云数据中...',request);
    const url = `/api/results/3d_surface?var=${encodeURIComponent(varName)}&time=${timestep}&target=${target}`;
    try {
        const data = await viz3dFetch(request,url);
        if (!viz3dCurrent(request) || !data) return;
        if (data.error) { viz3dError(data.error,request); return; }
        if(data.geometry_mode==='single_column') {await render3DSingleColumn(data,varName,timestep,request);return;}
        if(!lakeDisplayTopologyReady(data)) {
            viz3dError(data.display_topology_error || '降采样显示缺少有效原生水陆拓扑，已停止绘制以避免跨越干格。',request);return;
        }
        if(data.depth_geometry_error){viz3dError(data.depth_geometry_error,request);return;}
        const { long_name, units } = data;
        const ve=lakeVerticalScale(data.xc || [],data.yc || [],data.bottom,opts.ve);
        const samples=lakeVolumeSamples(data,ve);
        if(!samples) {viz3dError('缺少湖盆水深或水平坐标，无法显示真实水体。',request);return;}
        const xs = [], ys = [], zs = [], vs = [], readouts=[], elevations=data.elevation?.flat(2);
        samples.values.forEach((v,n)=>{if(Number.isFinite(v)){
            xs.push(samples.x[n]);ys.push(samples.y[n]);zs.push(samples.z[n]);vs.push(v);
            readouts.push([-samples.z[n]/ve,v,Number.isFinite(elevations?.[n])?elevations[n]:null]);
        }});
        const coverage=lakeCoverage(data,Array.from({length:data.shape[0]},(_,k)=>k));
        const style=viz3dStyle(coverage.valid?data:{...data,min:null,max:null},varName,request);
        const missing=lakeMissingSamples(data,samples,style,opts);
        if(!xs.length&&!missing.length){viz3dError('没有有效物理几何的水域样本。',request);return;}
        if (xs.length&&!viz3dValidStyle(style)) {viz3dError('该时步无有效数据（全为空值）',request);return;}
        const trace = {
            type: 'scatter3d',
            mode: 'markers',
            x: xs, y: ys, z: zs,
            marker: {
                size: 2.4,
                color: vs,
                showscale:true,
                colorscale: style.colorscale,
                cmin: style.min, cmax: style.max,cauto:false,
                opacity: viz3dOpacity(opts),
                colorbar: viz3dColorbar(viz3dLabel({long_name},varName),units,style),
            },
            name: viz3dEscape(viz3dLabel({long_name},varName)),
            customdata:readouts,
            hovertemplate:`${viz3dHorizontalHover(data)}<br>水深 %{customdata[0]:.2f} m`+
                (data.elevation?'<br>模型基准高程 %{customdata[2]:.4~g} m':'<br>模型基准高程未提供')+
                `<br>%{customdata[1]:.8~g} ${viz3dEscape(units)}${viz3dReference(varName)}<extra>${viz3dEscape(viz3dLabel({long_name},varName))}</extra>`,
        };
        const warning=viz3dOpacity(opts)<1 ? '透明点云会混色；定量读色请使用不透明显示' : '';
        const detail=`${viz3dDepthAxis(data)} · ${viz3dTime(timestep,opts,data)} · 全部层 · 点数 ${xs.length} · 垂向 ${ve}× · ${viz3dRangeLabel(style)} · ${lakeDepthSource(data)}`+(viz3dSampling(data)?` · ${viz3dSampling(data)}`:'')+lakeDisplayDetail(data,{...opts,scalarInterpolation:false},coverage);
        const layout = Object.assign({}, VIZ3D.layout, {
            title: viz3dTitle(viz3dLabel({long_name},varName),detail+(warning ? ` · ${warning}` : '')),
            scene:lakeScene(ve,Math.max(...(data.water_depth || data.bottom).flat().filter(h=>Number.isFinite(h)&&h>0)),data),
        });
        request.main={data,mode:'cloud',ve};
        await viz3dPlot(containerId, [...(xs.length?[trace]:[]),...missing,...lakeVolumeContext(data,ve,opts)], layout, {
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            scrollZoom:true,
            toImageButtonOptions: { format: 'png', filename: viz3dFilename('cloud',varName,timestep,opts,`all-layers_ve${ve}`) },
        },request);
        viz3dDone(request,data,'viz3d-iso-var',detail,warning,{range:style,level:'全部层',ve});
    } catch (e) {
        viz3dFailure(e,request);
    }
}

/**
 * Render a 3D isosurface (heavier mode, optional).
 */
async function render3DSurface(varName, timestep, target = 18, opts = {}) {
    const containerId = 'viz3d-plotly';
    const container = document.getElementById(containerId);
    if (!container) return;
    if (!VIZ3D.plotlyReady()) {
        viz3dError('Plotly 未加载。请使用二维视图或空间剖面。');
        return;
    }
    const request = viz3dBegin(container,varName,timestep,opts);
    viz3dLoading('计算等值面中（较重，请稍候）...',request);
    const url = `/api/results/3d_surface?var=${encodeURIComponent(varName)}&time=${timestep}&target=${target}`;
    try {
        const data = await viz3dFetch(request,url);
        if (!viz3dCurrent(request) || !data) return;
        if (data.error) { viz3dError(data.error,request); return; }
        if(data.geometry_mode==='single_column') {await render3DSingleColumn(data,varName,timestep,request);return;}
        if(!lakeDisplayTopologyReady(data)) {
            viz3dError(data.display_topology_error || '降采样显示缺少有效原生水陆拓扑，已停止绘制以避免跨越干格。',request);return;
        }
        if(data.depth_geometry_error){viz3dError(data.depth_geometry_error,request);return;}
        const { min, max, long_name, units } = data;
        const ve=lakeVerticalScale(data.xc || [],data.yc || [],data.bottom,opts.ve);
        const samples=lakeVolumeSamples(data,ve);
        if(!samples) {viz3dError('该时步没有有效水域几何。',request);return;}
        const coverage=lakeCoverage(data,Array.from({length:data.shape[0]},(_,k)=>k));
        const style=viz3dStyle(coverage.valid?data:{...data,min:null,max:null},varName,request);
        const missing=lakeMissingSamples(data,samples,style,opts);
        if (coverage.valid&&(!viz3dValidStyle(style) || !Number.isFinite(min) || !Number.isFinite(max))) {
            viz3dError('该时步无有效数据（全为空值）',request);
            return;
        }
        if(coverage.valid&&min===max) {viz3dError('常量场没有可区分等值面，请使用点云或不透明单层。',request);return;}
        // Interpolate thresholds without overflowing a large finite span.
        const isoLevels = (coverage.valid?[.4,.7]:[]).map(f=>min*(1-f)+max*f);
        const traces = isoLevels.flatMap(iso => {
            const mesh=buildStructuredIsosurface(data,iso,ve,samples);
            if(!mesh.i.length) return [];
            return [{
            type: 'mesh3d',...mesh,
            intensitymode:'vertex',flatshading:true,
            colorscale: style.colorscale,
            cmin: style.min,
            cmax: style.max,cauto:false,
            showscale: false,
            colorbar: viz3dColorbar(viz3dLabel({long_name},varName),units,style),
            customdata:mesh.z.map(z=>-z/ve),
            text:mesh.elevation.map(v=>Number.isFinite(v)?`插值模型基准高程 ${Number(v.toPrecision(8))} m`:'模型基准高程未提供'),
            hovertemplate:`${viz3dHorizontalHover(data)}<br>水深 %{customdata:.2f} m<br>%{text}<br>%{intensity:.8~g} ${viz3dEscape(units)}${viz3dReference(varName)}<extra>${viz3dEscape(viz3dLabel({long_name},varName))}</extra>`,
            opacity: viz3dOpacity(opts),lighting:{ambient:1,diffuse:0,specular:0,roughness:1},
            name: `${viz3dEscape(viz3dLabel({long_name},varName))} = ${Number(iso.toPrecision(8))}`,
            }];
        });
        if(!traces.length&&!missing.length) {viz3dError('当前采样网格未形成可绘制等值面，请提高质量或使用点云。',request);return;}
        if(traces.length)traces.at(-1).showscale=true;
        const noContour=!traces.length;
        traces.push(...missing,...lakeVolumeContext(data,ve,opts));
        const warning=viz3dOpacity(opts)<1 ? '透明等值面会混色；定量读色请使用不透明显示' : '';
        const detail=`${viz3dDepthAxis(data)} · ${viz3dTime(timestep,opts,data)} · 全部层等值面 · 垂向 ${ve}× · ${viz3dRangeLabel(style)} · ${lakeDepthSource(data)}`+(viz3dSampling(data)?` · ${viz3dSampling(data)}`:'')+lakeDisplayDetail(data,{...opts,scalarInterpolation:false},coverage)+(noContour?' · 未形成等值面；仅标示缺测位置':'');
        const layout = Object.assign({}, VIZ3D.layout, {
            title: viz3dTitle(viz3dLabel({long_name},varName),detail+(warning ? ` · ${warning}` : '')),
            scene:lakeScene(ve,Math.max(...(data.water_depth || data.bottom).flat().filter(h=>Number.isFinite(h)&&h>0)),data),
        });
        request.main={data,mode:'isosurface',ve};
        await viz3dPlot(containerId, traces, layout, {
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            scrollZoom:true,
            toImageButtonOptions: { format: 'png', filename: viz3dFilename('isosurface',varName,timestep,opts,`all-layers_ve${ve}`) },
        },request);
        viz3dDone(request,data,'viz3d-iso-var',detail,warning,{range:style,level:'全部层',ve});
    } catch (e) {
        viz3dFailure(e,request);
    }
}

/**
 * Render a 2D heatmap as a Plotly surface plot (alternative 3D view of a 2D field).
 */
async function render2DAs3DSurface(varName, timestep, level, opts = {}) {
    const containerId = 'viz3d-plotly';
    const container = document.getElementById(containerId);
    if (!container) return;
    if (!VIZ3D.plotlyReady()) { viz3dError('Plotly 不可用。请使用二维视图或空间剖面。'); return; }
    const request = viz3dBegin(container,varName,timestep,opts);
    viz3dLoading('加载变量高度表面…',request);
    const url = `/api/results/2d?var=${encodeURIComponent(varName)}&time=${timestep}&level=${level}`;
    try {
        const data = await viz3dFetch(request,url);
        if (!viz3dCurrent(request) || !data) return;
        if (data.error) { viz3dError(data.error,request); return; }
        const rows = data.data ? data.data.length : 0;
        if(!rows || !data.data.some(row=>row?.some(Number.isFinite))) {
            viz3dError('该时步无有效数据（全为空值或输出没有时间记录）',request);return;
        }
        const rawGrid=await viz3dFetch(request,'/api/geo/grid?display=scientific');
        if(!viz3dCurrent(request)||!rawGrid)return;
        const cols=data.data[0].length;
        const grid=variableHeightGrid(rawGrid,rows,cols);
        if(!grid||data.data.some(row=>row?.length!==cols)){viz3dError('变量与科学网格形状或坐标不匹配，无法绘制变量高度。',request);return;}
        const mesh=buildVariableHeightMesh(data.data,grid);
        if(!mesh.i.length){viz3dError('湿单元没有有效变量高度。',request);return;}
        const style=viz3dStyle(data,varName,request);
        if (!rows || !viz3dValidStyle(style)) {
            viz3dError('该时步无有效数据（全为空值或输出没有时间记录）',request);
            return;
        }
        let heightMin=Infinity,heightMax=-Infinity;
        for(const value of mesh.z) if(Number.isFinite(value)) {
            heightMin=Math.min(heightMin,value);heightMax=Math.max(heightMax,value);
        }
        const constant=heightMin===heightMax;
        const heightTicks=window.ScientificStyle?.ticks?.(heightMin,heightMax) || viz3dTicks(heightMin,heightMax);
        const heightRange=[heightMin,heightMax];
        if(constant) {
            // Axis padding makes a flat field visible; field values and the
            // sole labelled tick remain the original constant scalar value.
            const padding=Math.max(Math.abs(heightMin)*1e-6,1e-6);
            if(Number.isFinite(heightMin-padding)) heightRange[0]=heightMin-padding;
            if(Number.isFinite(heightMax+padding)) heightRange[1]=heightMax+padding;
        }
        const topology=grid.display_topology?.contract==='sampled-wet-topology-v1'?grid.display_topology:null;
        const xe=topology?.x_edges?.length===grid.xc.length+1?topology.x_edges:lakeCellEdges(grid.xc);
        const ye=topology?.y_edges?.length===grid.yc.length+1?topology.y_edges:lakeCellEdges(grid.yc);
        const xSpan=Math.abs(xe.at(-1)-xe[0]),ySpan=Math.abs(ye.at(-1)-ye[0]);
        const horizontalSpan=Math.max(xSpan,ySpan);const coordinates=viz3dCoordinates(grid);
        const trace = {
            type:'mesh3d',...mesh,meta:{variableHeight:true},
            colorscale: style.colorscale,
            cmin: style.min,
            cmax: style.max,cauto:false,
            showscale: true,
            opacity:viz3dOpacity(opts),connectgaps:false,lighting:{ambient:1,diffuse:0,specular:0,roughness:1},
            colorbar: viz3dColorbar(viz3dLabel(data,varName),data.units,style),
            hovertemplate:`单元中心 X %{customdata[0]} · Y %{customdata[1]} ${viz3dEscape(coordinates.units)}<br>%{customdata[2]:.8~g} ${viz3dEscape(data.units)}${viz3dReference(varName)}<extra>${viz3dEscape(viz3dLabel(data,varName))}</extra>`,
        };
        const warning=viz3dOpacity(opts)<1 ? '透明表面会混色；定量读色请使用不透明显示' : '';
        const detail=`变量高度表面 · ${viz3dTime(timestep,opts,data)} · 层 ${level} · 变量原值（${data.units || '原单位'}） · ${viz3dRangeLabel(style)}`+(constant?' · 常量场':'')+' · Z 为变量值，不是物理水深 · 缺测变量没有可定义高度，保持空洞；示意平面仅作陆地参考'+lakeDisplayDetail(grid,{...opts,scalarInterpolation:false});
        const layout = Object.assign({}, VIZ3D.layout, {
            title: viz3dTitle(viz3dLabel(data,varName),detail+(warning ? ` · ${warning}` : '')),
            scene: Object.assign({}, VIZ3D.layout.scene, {
                // Index counts and scalar units are independent quantities;
                // a narrow scalar range must not enlarge the horizontal mesh.
                aspectmode:'manual',aspectratio:{x:2.6*xSpan/horizontalSpan,y:2.6*ySpan/horizontalSpan,z:.85},
                xaxis: Object.assign({}, VIZ3D.layout.scene.xaxis, { title:`${coordinates.x} (${coordinates.units})`,range:[Math.min(...xe),Math.max(...xe)],autorange:false }),
                yaxis: Object.assign({}, VIZ3D.layout.scene.yaxis, { title:`${coordinates.y} (${coordinates.units})`,range:[Math.min(...ye),Math.max(...ye)],autorange:false }),
                zaxis: Object.assign({}, VIZ3D.layout.scene.zaxis, { title: viz3dEscape(viz3dLabel(data,varName))+(data.units ? ` (${viz3dEscape(data.units)})` : ''),
                    range:heightRange,autorange:false,tickmode:'array',tickvals:heightTicks.values,ticktext:heightTicks.labels }),
            }),
        });
        await viz3dPlot(containerId, [trace,...lakeLandTraces(grid,opts,heightRange[0]),...lakeDisplayLines(mesh,{maxDepth:Math.max(heightMax-heightMin,1e-6),ve:1},opts,grid)], layout, { responsive: true, displaylogo: false,scrollZoom:true,
            toImageButtonOptions:{format:'png',filename:viz3dFilename('variable-height',varName,timestep,opts,`layer${level}`)}},request);
        viz3dDone(request,data,'viz3d-iso-var',detail,warning,{range:style,level,ve:null});
    } catch (e) {
        viz3dFailure(e,request);
    }
}

function var_name_label(name) {
    return name;
}

let _spatialSectionToken = 0;

function setSpatialSectionPlaybackStatus(timestep,timeLabel='') {
    const container=document.getElementById('viz3d-section-plot');
    if(!container)return;
    ++_spatialSectionToken;
    const appState=typeof state!=='undefined'?state:window.state;
    if(appState)appState.spatialSectionRequest=(appState.spatialSectionRequest || 0)+1;
    const previous=container._viz3dLastPlot;
    const shown=previous?.timeLabel || (Number.isInteger(previous?.timestep)?`帧 ${previous.timestep}`:'尚无已完成剖面');
    const current=timeLabel || `帧 ${timestep}`;
    const text=window.StudioI18n?.scientificText?.(
        `播放中暂停剖面刷新 · 当前剖面：${shown} · 主图：${current}`,
        `Section refresh paused during playback · section: ${shown} · main view: ${current}`)
        || `播放中暂停剖面刷新 · 当前剖面：${shown} · 主图：${current}`;
    let status=container._viz3dStatusElement;
    if(!status && container.parentNode && document.createElement){
        status=document.createElement('div');status.className='sw-status';status.setAttribute('role','status');
        container.parentNode.insertBefore(status,container);container._viz3dStatusElement=status;
    }
    if(status){status.id='viz3d-section-status';status.textContent=text;if(status.dataset)status.dataset.phase='ready';}
    container._viz3dStatus={phase:'ready',message:text,stale:!!previous,displayed:previous || null,
        requested:{timestep,timeLabel:current}};
    if(container.dataset)container.dataset.stale=String(!!previous);
}
if(typeof window!=='undefined')window.setSpatialSectionPlaybackStatus=setSpatialSectionPlaybackStatus;

/** One spatial row/column at one time; disconnected cells preserve dry gaps. */
async function renderSpatialSection(varName, timestep, axis = 'xz', index = 0, opts = {}) {
    const container = document.getElementById(opts.containerId || 'viz3d-section-plot');
    if (!container) return;
    const request=viz3dBegin(container,varName,timestep,opts,true);
    if (!VIZ3D.plotlyReady()) {viz3dError('Plotly 未加载。请使用二维视图或数值剖面。',request);return;}
    viz3dLoading('加载空间剖面…',request);
    try {
        const d = await viz3dFetch(request,`/api/results/section?var=${encodeURIComponent(varName)}&time=${timestep}&axis=${encodeURIComponent(axis)}&index=${index}`);
        if (!viz3dCurrent(request) || !d) return;
        if (d.error) {viz3dError(d.error,request);return;}
        if(!d.data?.some((row,k)=>row?.some((v,h)=>[v,d.depth_edges?.[k]?.[h],d.depth_edges?.[k+1]?.[h]].every(Number.isFinite)))) {
            viz3dError('所选剖面没有有效水域变量数据',request);return;
        }
        const style=viz3dStyle(d,varName,request);
        if (!viz3dValidStyle(style)) {viz3dError('所选剖面没有有效水域变量数据',request);return;}
        const ve=Number.isFinite(Number(opts.ve)) && Number(opts.ve)>0 ? Number(opts.ve) : 1;
        const name = window.localizedResult?.(d,varName)?.comparison_name || window.StudioI18n?.scientificText(d.zh_name || d.long_name || varName,
            d.long_name_en || d.long_name || varName) || d.long_name_en || d.long_name || varName;
        const mesh = {type:'mesh3d',x:[],y:[],z:[],i:[],j:[],k:[],intensity:[],customdata:[],
            intensitymode:'cell',flatshading:true,colorscale:style.colorscale,
            cmin:style.min,cmax:style.max,cauto:false,showscale:true,colorbar:viz3dColorbar(name,d.units,style),opacity:viz3dOpacity(opts),
            name:viz3dEscape(name),lighting:{ambient:1,diffuse:0,specular:0},
            hovertemplate:`${axis==='xz'?'X':'Y'} %{x:.3~g} ${viz3dEscape(d.coordinate_units || 'm')}<br>水深 %{customdata[0]:.3~g} m`+
                (d.elevation?'<br>单元中心模型基准高程 %{customdata[2]:.4~g} m':'')+
                `<br>%{customdata[1]:.4~g} ${viz3dEscape(d.units)}<extra>${viz3dEscape(name)}</extra>`};
        for (let k=0;k<d.data.length;k++) for (let h=0;h<d.horizontal.length;h++) {
            const v=d.data[k][h],bottom=d.depth_edges[k][h],top=d.depth_edges[k+1][h];
            if (![v,bottom,top].every(Number.isFinite)) continue;
            const first=mesh.x.length;
            for(const [x,depth] of [[d.horizontal_edges[h],bottom],[d.horizontal_edges[h],top],
                [d.horizontal_edges[h+1],top],[d.horizontal_edges[h+1],bottom]]) {
                mesh.x.push(x);mesh.y.push(0);mesh.z.push(-depth*ve);
                mesh.customdata.push([depth,v,...(d.elevation?[d.elevation[k]?.[h] ?? null]:[])]);
            }
            mesh.i.push(first,first);mesh.j.push(first+1,first+2);mesh.k.push(first+2,first+3);
            mesh.intensity.push(v,v);
        }
        if(!mesh.i.length) {viz3dError('所选剖面没有有效水域变量数据',request);return;}
        const depthMax=Math.max(...mesh.customdata.map(d=>d[0]));
        const ticks=viz3dTicks(0,depthMax);
        const span=Math.abs(d.horizontal_edges.at(-1)-d.horizontal_edges[0]) || 1;
        const fixed=axis==='xz'?'j':'i';
        const detail=`${axis.toUpperCase()} · ${fixed}=${index} (0-based) · ${viz3dTime(timestep,opts,d)} · 垂向 ${ve}× · ${viz3dRangeLabel(style)} · ${d.depth_source || '实际层界面'}`;
        const warning=viz3dOpacity(opts)<1 ? '透明剖面会混色；定量读色请使用不透明显示' : '';
        const layout={...VIZ3D.layout,title:viz3dTitle(name,detail+(warning ? ` · ${warning}` : '')),showlegend:false,
            margin:{l:8,r:100,t:70,b:20},uirevision:`section-${axis}-${index}`,
            scene:{...VIZ3D.layout.scene,
                xaxis:{...VIZ3D.layout.scene.xaxis,title:`${axis==='xz'?'X':'Y'} (${d.coordinate_units || 'm'})`},
                yaxis:{visible:false,range:[-.1,.1]},
                zaxis:{...VIZ3D.layout.scene.zaxis,title:viz3dDepthAxis(d),tickmode:'array',
                    tickvals:ticks.values.map(z=>-z*ve),ticktext:ticks.labels},
                aspectmode:'manual',aspectratio:{x:1,y:.001,z:depthMax*ve/span || 1},
                camera:{eye:{x:0,y:-2,z:0},up:{x:0,y:0,z:1},projection:{type:'orthographic'}}}};
        // The main lake's saved orbit must not rotate a planar section away
        // from its physical horizontal/depth axes.
        await viz3dPlot(container,[mesh],layout,{
            responsive:true,displaylogo:false,scrollZoom:true,
            toImageButtonOptions:{format:'png',filename:viz3dFilename('section',varName,timestep,opts,`${axis}${index}_ve${ve}`)}},request);
        if(!viz3dCurrent(request)) return;
        viz3dDone(request,d,'viz3d-section-var',detail,warning);
        return d;
    } catch(error) {viz3dFailure(error,request);}
}
if (typeof window !== 'undefined') window.renderSpatialSection = renderSpatialSection;

// 湖盆地形占位渲染：尚无模型结果时，3D 视图也能看到湖泊形态（z = -水深）
async function renderBathymetry3D(opts = {}) {
    const container = document.getElementById('viz3d-plotly');
    if (!container) return;
    if (!VIZ3D.plotlyReady()) { viz3dError('Plotly 不可用。请使用二维视图或空间剖面。'); return; }
    const request=viz3dBegin(container,'bathymetry',0,opts);
    viz3dLoading('加载湖盆地形…',request);
    try {
        const g=await viz3dFetch(request,'/api/geo/grid');
        if(!viz3dCurrent(request) || !g) return;
        if(g.error) {viz3dError(g.error,request);return;}
        const d={...g,bottom:g.depth,xc:g.xc,yc:g.yc,depth_reference:'below static bathymetric surface'};
        if(!d.xc || !d.yc) {
            if(!(Number.isFinite(g.dx)&&g.dx>0)) {viz3dError('缺少水平网格坐标，无法显示湖盆比例。',request);return;}
            d.xc=Array.from({length:g.nx},(_,i)=>i*g.dx*(g.stride || 1));
            const dy=Number.isFinite(g.dy) && g.dy>0 ? g.dy : g.dx;
            d.yc=Array.from({length:g.ny},(_,j)=>j*dy*(g.stride || 1));
        }
        const ve=lakeVerticalScale(d.xc,d.yc,d.bottom,opts.ve);
        const geometry=buildLakeGeometry(d.xc,d.yc,d.bottom,ve,d.display_topology);
        if(!geometry) {viz3dError('没有正水深的有效水域。',request);return;}
        const maxDepth=Math.max(...d.bottom.flat().filter(h=>Number.isFinite(h)&&h>0));
        const style=viz3dStyle({min:0,max:maxDepth},'__bathy__',request);
        const diagnosticModes=viz3dWaterbodyDiagnosticMode();
        const previewNote=opts.staticPreviewReason
            ? ` · 无动态输出（${opts.staticPreviewReason}），当前显示静态湖盆与水面示意`
            : '';
        const detail=`静态水体预览 · 半透明蓝色水面与湿网格侧壁展示体积；侧壁仅作体积示意，来自湿格底深插值，高垂向倍率限制显示高度，不代表岸缘实测水深；湖底隐藏；等深线仅作辅助 · ${viz3dDepthAxis(d)} · 垂向 ${ve}×`+(viz3dSampling(g)?` · ${viz3dSampling(g)}`:'')+lakeDisplayDetail(d,{...opts,staticBathymetry:true,displayBoundaryStatus:lakeDisplayBoundaryStatus(geometry,d),scalarInterpolation:false})+previewNote;
        request.main={data:d,mode:'bathymetry',ve};
        await viz3dPlot(container,lakeTraces(geometry,true,d,style,{...opts,staticBathymetry:true,staticBasin:true,showBedSurface:opts.showBedSurface===true,
            forceBedNeutral:diagnosticModes.includes('force-bed-neutral'),
            forceBedNeutralScale:diagnosticModes.includes('force-bed-neutral-scale')}),Object.assign({},VIZ3D.layout,{
            title:viz3dTitle(opts.staticPreviewReason?'静态湖盆（无动态输出）':'湖盆地形 · bathymetry.nc',detail),scene:lakeScene(ve,maxDepth,d,opts.meshMode==='triangles'?.025:.05),showlegend:true,uirevision:'lake-view'
        }),{responsive:true,scrollZoom:true,displaylogo:false,
            toImageButtonOptions:{format:'png',filename:viz3dFilename('bathymetry','depth',0,{},`ve${ve}`)}},request);
        viz3dDone(request,g,null,detail,'',{variable:'__bathy__',label:'静态水体预览',units:'m',min:0,max:maxDepth,
            range:style,field:g.depth,date:'地形预览',level:null,ve});
    }catch(e){viz3dFailure(e,request);}
}
