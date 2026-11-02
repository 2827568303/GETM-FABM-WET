// Scientific result controls. Renderers own data/geometry; this module owns the
// visible selection, range controls, playback and complete-figure export.
(function(root){
    'use strict';
    const $=id=>document.getElementById(id), records=new Map(),emptyTimeLabels=[];
    let bound=false, identity='', shared=null, activePage='';
    const tr=(zh,en)=>root.StudioI18n?.scientificText(zh,en) || zh;
    const app=()=>typeof state==='undefined' ? {} : state;
    const caseKey=()=>String(app().activeCasePath || app().activeCase || '');
    const revision=()=>`${caseKey()}\n${app().caseRevision ?? ''}`;
    const variable=kind=>$(kind==='viz3d'?'viz3d-iso-var':'viz2d-var');
    const time=kind=>$(kind==='viz3d'?'viz3d-iso-time':'viz2d-time');
    const settingsVariable=kind=>kind==='viz3d' && $('viz3d-iso-render')?.value==='waterbody' && $('viz3d-iso-overlay')?.checked===false
        ? '__bathy__' : variable(kind)?.value;
    function record(kind){
        if(!records.has(kind)) records.set(kind,{timer:null,animationFrame:null,paintTimer:null,playing:false,playGeneration:0,busy:0,last:null,rangeDirty:false,rangeError:'',renderFailures:0});
        return records.get(kind);
    }
    function refreshStoppedSpatialSection(){
        if(activePage!=='viz3d' || !document.querySelector?.('#page-viz3d .sw-section-analysis[open]'))return;
        Promise.resolve(root.updateSpatialSection?.()).catch(()=>{});
    }
    function stop(kind,refreshAuxiliary=false){
        for(const name of kind?[kind]:['viz2d','viz3d']){
            const r=record(name),wasPlaying=r.playing;r.playGeneration++;r.playing=false;r.resume=false;if(r.timer!==null)clearTimeout(r.timer);r.timer=null;
            if(r.animationFrame!==null)root.cancelAnimationFrame?.(r.animationFrame);r.animationFrame=null;
            if(r.paintTimer!==null)clearTimeout(r.paintTimer);r.paintTimer=null;
            const button=$(name+'-play');if(button){button.replaceChildren(root.StudioIcons.node('play'));button.setAttribute('aria-pressed','false');button.setAttribute('aria-label',tr('播放实际输出帧','Play actual output frames'));}
            if(refreshAuxiliary && wasPlaying && r.busy===0 && name==='viz3d')refreshStoppedSpatialSection();
        }
    }
    function checkIdentity(){
        const key=revision();if(key!==identity){stop();identity=key;shared=null;records.forEach(r=>{r.last=null;r.rangeDirty=false;r.rangeError='';});}
        return key;
    }
    function variableEntry(name){
        for(const kind of ['viz3d','viz2d']){
            const metadata=app()[kind==='viz3d'?'variables3d':'variables2d']?.find(v=>v.name===name);
            if(metadata)return {kind,metadata};
        }
        return null;
    }
    const variableMetadata=name=>variableEntry(name)?.metadata || null;
    function timeLabels(kind,name=variable(kind)?.value){
        const entry=variableEntry(name),meta=entry?.metadata;
        if(Array.isArray(meta?.time_labels))return meta.time_labels;
        const axis=meta?.time_axis;
        if(axis && Array.isArray(app().resultTimeAxes?.[axis]))return app().resultTimeAxes[axis];
        const stream=entry?.kind || kind;
        const labels=app()[stream==='viz3d'?'timeLabels3d':'timeLabels2d'];
        if(Array.isArray(labels))return labels;
        return Array.isArray(app().timeLabels)?app().timeLabels:emptyTimeLabels;
    }
    function frameCount(kind,name=variable(kind)?.value){
        if(name==='__bathy__')return 1;
        const entry=variableEntry(name),count=entry?.metadata?.ntimesteps;
        if(Number.isInteger(count)&&count>=0)return count;
        const labels=timeLabels(kind,name);if(labels.length)return labels.length;
        const stream=entry?.kind || kind,legacy=app()[stream==='viz3d'?'timesteps3d':'timesteps2d'];
        return Number.isInteger(legacy)&&legacy>=0?legacy:0;
    }
    function dateLabel(kind,index,name=variable(kind)?.value){
        const raw=timeLabels(kind,name)[index];
        const formatter=root.ModelDates || (typeof ModelDates!=='undefined'?ModelDates:null);
        return raw==null?'':formatter?.format?.(raw) || raw;
    }
    function maxFrame(kind){
        return Math.max(0,frameCount(kind)-1);
    }
    function playbackControls(kind){
        const r=record(kind),name=settingsVariable(kind),count=frameCount(kind),labels=timeLabels(kind);
        // Static terrain is a display of the selected result source. Retain
        // that source's frame and range while its timeline is disabled.
        const source={key:revision(),name:variable(kind)?.value,count,labels,first:labels[0],last:labels.at(-1)};
        const old=r.playSource;
        if(!old || Object.keys(source).some(key=>old[key]!==source[key])){
            stop(kind);r.playSource=source;r.playRange={start:0,end:Math.max(0,count-1)};r.playRangeError='';
            for(const edge of ['start','end'])if($(kind+'-play-'+edge)){
                $(kind+'-play-'+edge).value=String(r.playRange[edge]);$(kind+'-play-'+edge).setAttribute('aria-invalid','false');
            }
        }
        for(const edge of ['start','end']){
            const input=$(kind+'-play-'+edge);if(input){input.max=String(Math.max(0,count-1));input.disabled=count===0 || name==='__bathy__';}
            const label=$(kind+'-play-'+edge+'-label');
            if(label)label.textContent=name==='__bathy__'?tr('静态地形','Static terrain'):count?dateLabel(kind,r.playRange[edge]) || `${tr('帧','Frame')} ${r.playRange[edge]}`:tr('尚无输出时刻','No output times yet');
        }
        const note=$(kind+'-play-range-status');if(note)note.textContent=r.playRangeError;
        return r.playRange;
    }
    function applyPlaybackRange(kind){
        playbackControls(kind);const r=record(kind),values={};
        for(const edge of ['start','end']){
            const raw=$(kind+'-play-'+edge)?.value??r.playRange[edge];
            values[edge]=String(raw).trim()?Number(raw):NaN;
        }
        const count=frameCount(kind),{start,end}=values;
        if(!Number.isInteger(start)||!Number.isInteger(end)||start<0||start>end||end>=count){
            r.playRangeError=tr('播放范围无效：请输入实际输出范围内的整数帧，且起始帧不大于结束帧。','Invalid playback range: enter integer output frames with start no later than end.');
            const note=$(kind+'-play-range-status');if(note)note.textContent=r.playRangeError;
            for(const edge of ['start','end'])$(kind+'-play-'+edge)?.setAttribute('aria-invalid','true');
            return false;
        }
        r.playRange=values;r.playRangeError='';
        for(const edge of ['start','end'])$(kind+'-play-'+edge)?.setAttribute('aria-invalid','false');
        playbackControls(kind);return true;
    }
    function updateTimeControls(kind){
        const control=time(kind);if(!control)return;
        const max=maxFrame(kind), current=Math.max(0,Math.min(max,Math.round(Number(control.value)||0)));
        control.value=String(current);control.max=String(max);
        const slider=$(kind+'-time-slider');if(slider){slider.value=String(current);slider.max=String(max);}
        const date=settingsVariable(kind)==='__bathy__'?tr('静态地形','Static terrain'):dateLabel(kind,current) || `${tr('帧','Frame')} ${current}`;
        const label=$(kind==='viz3d'?'viz3d-iso-time-label':'viz2d-time-label');if(label)label.textContent=date;
        playbackControls(kind);
        const terrain=settingsVariable(kind)==='__bathy__',unavailable=max===0 || terrain;
        if(terrain)stop(kind);
        control.disabled=terrain;if(slider)slider.disabled=terrain;
        for(const action of ['prev','next'])if($(kind+'-'+action))$(kind+'-'+action).disabled=unavailable;
        if($(kind+'-play'))$(kind+'-play').disabled=frameCount(kind)===0 || terrain;
    }
    function syncFrom(kind){
        checkIdentity();const input=variable(kind);if(!input?.value)return;
        const r=record(kind);
        const target=settingsVariable(kind);
        if(r.rangeVariable!==target){stop(kind);r.rangeDirty=false;r.rangeError='';r.rangeVariable=target;}
        updateTimeControls(kind);const frame=Number(time(kind)?.value)||0;
        shared={key:identity,variable:input.value,time:frame,date:timeLabels(kind)[frame]};
    }
    function activate(kind){
        checkIdentity();const input=variable(kind);let changed=false;
        if(shared?.key===identity && input && Array.from(input.options || []).some(o=>o.value===shared.variable)){
            changed=input.value!==shared.variable;input.value=shared.variable;
            const labels=timeLabels(kind),sameDate=shared.date==null?-1:labels.indexOf(shared.date);
            time(kind).value=String(sameDate>=0?sameDate:shared.time);
        }
        updateTimeControls(kind);renderSettings(kind);return changed;
    }
    function status(kind,text){const el=$(kind+'-status');if(el)el.textContent=text;}
    function ensureFullscreenCaption(kind){
        const host=kind==='viz2d'?$('viz2d-viewport'):$('viz3d-plotly')?.parentElement;
        if(!host?.appendChild)return null;
        let caption=$(kind+'-fullscreen-meta');
        if(!caption){caption=document.createElement('div');caption.id=kind+'-fullscreen-meta';caption.className='sw-fullscreen-meta';
            caption.setAttribute('role','note');caption.setAttribute('data-i18n-skip','');host.appendChild(caption);}
        else if(caption.parentElement!==host)host.appendChild(caption);
        return caption;
    }
    function fullscreenState(kind,phase,message=''){
        if(phase==='error')record(kind).renderFailures++;
        const caption=ensureFullscreenCaption(kind);if(!caption)return;
        caption.dataset.phase=phase;caption.dataset.message=message;
    }
    function fullscreenMetadata(kind,meta){
        const caption=ensureFullscreenCaption(kind);if(!caption)return;
        const label=value=>root.StudioI18n?.t?.(String(value??'')) || String(value??'');
        const range=meta.range,parts=[`${app().activeCase || caseKey()} · ${meta.label || meta.variable} (${meta.variable})${meta.units?' · '+meta.units:''}`,
            label(meta.date),meta.level==null?'':`${tr('层','Layer')} ${label(meta.level)}`,
            Number.isFinite(meta.ve)?`${tr('垂向','Vertical')} ${meta.ve}×`:'',
            range?range.noData?tr('无有效数据','No valid data'):`${tr('色标','Colour range')}: ${range.mode} · ${range.min} – ${range.max} · ${range.palette}`:'',label(meta.detail)];
        caption.textContent=parts.filter(Boolean).join(' · ');
        const style=root.ScientificStyle;
        if(kind==='viz2d' && range && !range.noData && style?.color && style?.ticks){
            const gradient=document.createElement('div');gradient.id=kind+'-fullscreen-gradient';gradient.className='sw-fullscreen-gradient';
            gradient.style.background=`linear-gradient(to right,${colorStops(range).map(([t,color])=>`${color} ${t*100}%`).join(',')})`;
            const marks=style.ticks(range.min,range.max),limits=document.createElement('div');
            limits.id=kind+'-fullscreen-limits';limits.className='sw-fullscreen-limits';
            for(const [edge,text] of [['min',marks.labels[0]],['max',marks.labels.at(-1)]]){
                const tick=document.createElement('span');tick.id=kind+'-fullscreen-'+edge;tick.textContent=text || '—';limits.appendChild(tick);
            }
            caption.appendChild(gradient);caption.appendChild(limits);
        }
        fullscreenState(kind,'ready');
    }
    function loading(kind){
        const previous=record(kind).last || $(kind+'-fullscreen-meta')?.textContent;
        status(kind,previous?tr('正在加载；画布暂保留上次成功结果，以下摘要标明其时刻。','Loading; the canvas retains the previous successful result identified below.'):
            tr('正在加载模型结果…','Loading model results…'));
        fullscreenState(kind,'loading',previous?tr('正在加载，保留上次成功画面','Loading; retaining the previous successful figure'):tr('正在加载模型结果…','Loading model results…'));
    }
    function failure(kind,message){
        const r=record(kind),last=r.last,expected=settingsVariable(kind);
        const previous=last || $(kind+'-fullscreen-meta')?.textContent;
        // A failed request leaves the previous canvas and legend visible. Keep
        // the timeline on that same successfully published frame as well.
        // The revision and variable guards prevent an old case/view result
        // from moving controls after the user has changed selection.
        stop(kind);
        if(last?.key===revision() && last.variable===expected && Number.isInteger(last.time)
                && last.time>=0 && last.time<=maxFrame(kind)){
            const control=time(kind);if(control)control.value=String(last.time);
            updateTimeControls(kind);
        }
        const text=`${previous?tr('加载失败，保留的画面不是新选择的结果','Load failed; the retained image is not the new selection'):tr('模型结果加载失败','Model results failed to load')}: ${message}`;
        status(kind,text);fullscreenState(kind,'error',text);
    }
    function empty(kind,message){
        const r=record(kind);stop(kind);r.last=null;
        status(kind,message);fullscreenState(kind,'empty',message);
        if(kind==='viz2d'){
            const canvas=$('viz2d-canvas'),ctx=canvas?.getContext?.('2d');
            if(ctx)ctx.clearRect(0,0,canvas.width,canvas.height);
            if(canvas){canvas._resultField=null;canvas._scientificRange=null;canvas._resultVariable=null;}
            for(const id of ['viz2d-info','viz2d-min','viz2d-max'])if($(id))$(id).textContent=message;
        }else{
            const graph=$('viz3d-plotly');if(graph)root.Plotly?.purge?.(graph);
            for(const id of ['viz3d-main-colorbar','viz3d-main-min','viz3d-main-max'])if($(id))$(id).textContent=message;
        }
        const summary=$(kind+'-summary');if(summary)summary.textContent=message;
        updateTimeControls(kind);
    }
    function clipped(meta){
        const range=meta.range;if(!range || !Number.isFinite(range.min)||!Number.isFinite(range.max))return 0;
        let count=0;
        const visit=a=>{if(Array.isArray(a))a.forEach(visit);else if(typeof a==='number'&&Number.isFinite(a)&&(a<range.min||a>range.max))count++;};
        visit(meta.field);return count;
    }
    function colorStops(range){
        return range?.colorscale || root.ScientificStyle?.colorscale?.(range || {palette:'lake'})
            || Array.from({length:11},(_,i)=>[i/10,root.ScientificStyle.color(i/10,range)]);
    }
    function railLegend(kind,meta){
        if(kind!=='viz3d')return;
        const el=$('viz3d-main-colorbar');if(!el)return;
        const range=meta.range,style=root.ScientificStyle;
        if(!range || range.noData || !Number.isFinite(range.min)){
            el.style.background='#c9cbd0';el.textContent=tr('无有效数据','No valid data');return;
        }
        el.replaceChildren();const stops=colorStops(range).map(([t,color])=>`${color} ${t*100}%`);
        el.style.background=`linear-gradient(to right,${stops.join(',')})`;
        const title=document.createElement('span');title.className='scientific-colorbar-title';
        title.textContent=`${meta.label || meta.variable}${meta.units?' ('+meta.units+')':''}`;el.appendChild(title);
        const marks=style.legendTicks?style.legendTicks(range.min,range.max,el.clientWidth || 200):style.ticks(range.min,range.max);
        marks.labels.forEach((text,i)=>{const tick=document.createElement('span');tick.className='scientific-colorbar-tick';
            if(marks.labels.length>1)tick.dataset.edge=i===0?'start':i===marks.labels.length-1?'end':'middle';
            tick.style.left=`${marks.labels.length===1?50:i/(marks.labels.length-1)*100}%`;tick.textContent=text;el.appendChild(tick);});
        el.setAttribute('aria-label',`${title.textContent}: ${range.min} – ${range.max}`);
        if($('viz3d-main-min'))$('viz3d-main-min').textContent=marks.labels[0]||'—';
        if($('viz3d-main-max'))$('viz3d-main-max').textContent=marks.labels.at(-1)||'—';
    }
    function renderSettings(kind){
        const name=settingsVariable(kind),style=root.ScientificStyle;if(!name||!style)return;
        const saved=style.get(caseKey(),name),meta=record(kind).last;
        if(!record(kind).rangeDirty){
            if($(kind+'-palette'))$(kind+'-palette').value=saved.palette;
            if($(kind+'-range-mode'))$(kind+'-range-mode').value=saved.mode;
            for(const edge of ['min','max']){
                const input=$(kind+'-range-'+edge);if(!input)continue;
                input.disabled=saved.mode!=='custom';
                const value=saved.mode==='custom'?saved[edge]:meta?.variable===name?meta.range?.[edge]:null;
                input.value=Number.isFinite(value)?String(value):'';
            }
        }
        if(kind==='viz3d'){
            const surface=name!=='__bathy__' && $('viz3d-iso-render')?.value==='surface2d',ve=$('viz3d-iso-ve');
            if(ve){ve.disabled=surface;ve.title=surface?tr('此模式高度表示变量值，物理垂向倍数不适用','Height represents the variable; physical vertical scale does not apply'):'';}
            const terrain=name==='__bathy__';
            if($('viz3d-iso-layer'))$('viz3d-iso-layer').disabled=terrain;
            if($('viz3d-opacity')){$('viz3d-opacity').disabled=terrain;$('viz3d-opacity').title=terrain?tr('地形定量色面保持不透明','Quantitative bathymetry remains opaque'):'';}
        }
    }
    function publish(kind,meta){
        checkIdentity();
        record(kind).last={...meta,key:identity};
        const parts=[`${meta.label || meta.variable}${meta.units?' · '+meta.units:''}`,meta.date];
        if(meta.level!==null&&meta.level!==undefined)parts.push(`${tr('层','Layer')} ${meta.level}`);
        const summary=$(kind+'-summary');if(summary)summary.textContent=parts.filter(Boolean).join('  ·  ');
        if(kind==='viz3d' && $('viz3d-ve-label'))$('viz3d-ve-label').textContent=Number.isFinite(meta.ve)?`${tr('垂向','Vertical')} ${Number(meta.ve.toPrecision(4))}×`:tr('变量高度表面','Variable-height surface');
        const count=clipped(meta),rangeStatus=$(kind+'-range-status');
        if(rangeStatus)rangeStatus.textContent=record(kind).rangeError || (meta.range?.noData?tr('当前场没有有效值','The current field has no valid values'):
            count?`${tr('范围外数据已截色，数量','Values outside the colour range are clipped; count')}: ${count}`:
            meta.range?.mode==='locked'?tr('色标已锁定，可跨帧比较；这不是正常值范围。','Colour range locked for frame comparison; it is not a normal-value threshold.'):
            tr('色标按当前场自动缩放；跨帧比较可锁定。','Colour range follows the current field; lock it for frame comparison.'));
        renderSettings(kind);railLegend(kind,meta);updateTimeControls(kind);fullscreenMetadata(kind,meta);
        if(kind==='viz2d')status(kind,meta.range?.noData?tr('无有效数据','No valid data'):tr('显示当前模型结果','Showing current model results'));
    }
    async function refresh(kind){
        const r=record(kind),failures=r.renderFailures;r.busy++;
        try{
            if(kind==='viz2d'&&typeof updateViz2d==='function')await updateViz2d();
            if(kind==='viz3d'&&typeof updateViz3dIso==='function'){
                await updateViz3dIso();
            }
            return r.renderFailures===failures;
        }catch(error){
            failure(kind,error.message || String(error));return false;
        }finally{r.busy--;}
    }
    function applySettings(kind){
        const name=settingsVariable(kind);if(!name||!root.ScientificStyle)return false;
        const mode=$(kind+'-range-mode')?.value||'auto';
        try{
            const patch={palette:$(kind+'-palette')?.value||'lake',mode};
            if(mode==='custom'){
                const min=$(kind+'-range-min')?.value,max=$(kind+'-range-max')?.value;
                if(!String(min??'').trim()||!String(max??'').trim())throw Error(tr('请输入有限的上下限，且下限小于上限','Enter finite limits with minimum below maximum'));
                patch.min=Number(min);patch.max=Number(max);
            }
            root.ScientificStyle.set(caseKey(),name,patch);
            record(kind).rangeDirty=false;record(kind).rangeError='';
            const meta=record(kind).last;
            if(mode==='locked'&&meta?.variable===name)root.ScientificStyle.resolve({caseKey:caseKey(),variable:name,min:meta.min,max:meta.max});
            renderSettings(kind);refresh(kind);return true;
        }catch(error){
            const message=/Custom range requires/.test(error.message)?tr('请输入有限的上下限，且下限小于上限','Enter finite limits with minimum below maximum'):error.message;
            record(kind).rangeDirty=true;record(kind).rangeError=message;
            const el=$(kind+'-range-status');if(el)el.textContent=message;return false;
        }
    }
    async function step(kind,delta){
        checkIdentity();stop(kind);const input=time(kind);if(!input)return;
        const current=Number(input.value)||0,next=Math.max(0,Math.min(maxFrame(kind),current+delta));
        input.value=String(next);updateTimeControls(kind);syncFrom(kind);
        if(next!==current)await refresh(kind);
    }
    function togglePlay(kind){
        checkIdentity();const r=record(kind);if(r.playing){stop(kind,true);r.resume=true;return;}
        syncFrom(kind);
        if(frameCount(kind)===0 || settingsVariable(kind)==='__bathy__' || !applyPlaybackRange(kind))return;
        const resumeRequested=r.resume;stop();const name=variable(kind)?.value,meta=r.last;
        const {start,end}=r.playRange,current=Number(time(kind).value);
        const currentInRange=current>=start && current<end,resume=resumeRequested && currentInRange;
        if(!currentInRange)time(kind).value=String(start);
        syncFrom(kind);
        const captured=identity,generation=++r.playGeneration,speed=Math.max(.25,Math.min(12,Number($(kind+'-speed')?.value)||1));
        root.PlaybackPerformance?.startSession(kind,{targetFps:speed,resume});
        const frameInterval=1000/speed;
        const monotonicNow=()=>root.performance?.now?.() ?? Date.now();
        let nextFrameDeadline=monotonicNow()+frameInterval;
        r.playing=true;
        const valid=()=>r.playing && r.playGeneration===generation;
        const visible=()=>captured===revision() && !document.hidden && activePage===kind;
        const schedulePaint=(callback)=>{
            if(typeof root.requestAnimationFrame!=='function'){r.paintTimer=setTimeout(()=>{r.paintTimer=null;callback();},0);return;}
            let settled=false,frame=null;
            const finish=()=>{
                if(settled)return;settled=true;
                if(r.paintTimer!==null)clearTimeout(r.paintTimer);r.paintTimer=null;
                if(frame!==null && r.animationFrame===frame){root.cancelAnimationFrame?.(frame);r.animationFrame=null;}
                callback();
            };
            // Embedded and background browser views can suspend rAF while their
            // timers continue. Let the playback clock proceed after one paint
            // opportunity instead of remaining indefinitely marked as playing.
            r.paintTimer=setTimeout(finish,50);
            frame=root.requestAnimationFrame(()=>{
                if(r.animationFrame===frame)r.animationFrame=null;
                finish();
            });
            r.animationFrame=frame;
        };
        const waitForPaint=()=>new Promise(resolve=>{
            schedulePaint(resolve);
        });
        const afterRender=async success=>{
            if(!valid())return;
            if(!success || !visible()){stop(kind);return;}
            if(Number(time(kind).value)>=end){await waitForPaint();if(valid())stop(kind,true);return;}
            await waitForPaint();if(!valid())return;
            const completedAt=monotonicNow();
            // Keep the original cadence when a timer was only slightly late.
            // If rendering missed one or more beats, continue as soon as that
            // render completes. The next frame's work itself consumes time;
            // adding another full interval here would throttle slow renders
            // below both their render throughput and the selected target.
            if(nextFrameDeadline<=completedAt)nextFrameDeadline=completedAt;
            scheduleNext(nextFrameDeadline);
        };
        const scheduleNext=(deadline)=>{
            if(!valid())return;
            const delay=Math.max(0,deadline-monotonicNow());
            r.timer=setTimeout(()=>{
                r.timer=null;
                if(!valid())return;
                if(!visible()){stop(kind);return;}
                const advanceOnPaint=()=>{
                    r.animationFrame=null;
                    if(!valid())return;
                    if(!visible()){stop(kind);return;}
                    // Keep settings-driven refreshes serialized with playback.
                    // The next request starts only after the outstanding work
                    // settles and the scheduled display beat has arrived.
                    if(r.busy || monotonicNow()<deadline){
                        if(typeof root.requestAnimationFrame==='function')schedulePaint(advanceOnPaint);
                        else r.timer=setTimeout(advanceOnPaint,Math.max(1,deadline-monotonicNow()));
                        return;
                    }
                    updateTimeControls(kind);if(!valid())return;
                    if(Number(time(kind).value)>=end){stop(kind,true);return;}
                    time(kind).value=String(Number(time(kind).value)+1);syncFrom(kind);
                    nextFrameDeadline+=frameInterval;
                    refresh(kind).then(afterRender);
                };
                if(typeof root.requestAnimationFrame==='function')schedulePaint(advanceOnPaint);
                else advanceOnPaint();
            },delay);
        };
        const button=$(kind+'-play');if(button){button.replaceChildren(root.StudioIcons.node('pause'));button.setAttribute('aria-pressed','true');button.setAttribute('aria-label',tr('暂停播放','Pause playback'));}
        if(resume){scheduleNext(nextFrameDeadline);return;}
        refresh(kind).then(afterRender);
    }
    function onNavigate(page){
        activePage=page;checkIdentity();
        for(const kind of ['viz2d','viz3d'])if(kind!==page)stop(kind);
        if(page!=='viz2d'){app().viz2dAbort?.abort();}
    }
    function saveBlob(blob,name){
        if(!blob)throw Error(tr('图形导出失败','Figure export failed'));
        const link=document.createElement('a'),url=URL.createObjectURL(blob);link.href=url;link.download=name;link.click();
        setTimeout(()=>URL.revokeObjectURL(url),1000);
    }
    function exportLines(ctx,text,width){
        const lines=[];
        for(const paragraph of String(text).split('\n')){
            let line='';
            for(const character of Array.from(paragraph)){
                if(line && ctx.measureText(line+character).width>width){lines.push(line);line='';}
                line+=character;
            }
            lines.push(line);
        }
        return lines;
    }
    function exportHeader(ctx,meta,caseName,width){
        const range=meta.range,number=value=>Number.isFinite(value)?String(value):'—';
        const label=value=>root.StudioI18n?.t(String(value??'')) || String(value??'');
        const rows=[
            [label(meta.label || meta.variable),22],
            [`${tr('原始变量','Variable')}: ${meta.variable}`,16],
            [`${tr('单位','Units')}: ${meta.units || '—'}`,16],
            [`${tr('案例','Case')}: ${caseName}`,16],
            [`${tr('实际时刻','Actual date')}: ${label(meta.date) || tr('未提供','Unavailable')}`,16],
            [`${tr('层','Layer')}: ${label(meta.level??'—')}${meta.stack?' (stack)':''} · ${tr('有效垂向倍数','Effective vertical scale')}: ${Number.isFinite(meta.ve)?meta.ve+'×':tr('不适用','Not applicable')}`,16],
            [`${tr('色标模式','Range mode')}: ${range?.mode || '—'} · ${tr('范围','Limits')}: ${number(range?.min)} – ${number(range?.max)} · ${tr('配色','Palette')}: ${range?.palette || '—'}`,16],
        ];
        if(meta.detail)rows.push([label(meta.detail),16]);
        const lines=[];let y=30;
        for(const [text,size] of rows){
            const font=`${size}px Segoe UI, Microsoft YaHei, sans-serif`;ctx.font=font;
            for(const line of exportLines(ctx,text,width-52)){lines.push({text:line,font,x:26,y});y+=size+7;}
        }
        return {lines,height:y+12};
    }
    async function exportImage(url){
        return new Promise((resolve,reject)=>{
            const image=new root.Image();image.onload=()=>resolve(image);
            image.onerror=()=>reject(Error(tr('导出图像无法读取','Unable to read the exported image')));image.src=url;
        });
    }
    async function exportFigure(kind){
        const meta=record(kind).last;if(!meta || meta.key!==revision())throw Error(tr('请先加载本案例的结果','Load a result from the current case first'));
        const caseName=String(app().activeCase || caseKey());
        let graph=null,renderStatus;
        const assertCurrent=()=>{if(record(kind).last!==meta || meta.key!==revision() || (graph && graph._viz3dStatus!==renderStatus))throw Error(tr('显示结果已变化，请重新导出','The displayed result changed; export it again'));};
        const filename=`3DWET_${meta.variable}_${meta.date || meta.time || 0}`.replace(/[<>:"/\\|?*\s]+/g,'_');
        let image,plotWidth,plotHeight;
        if(kind==='viz3d'){
            graph=$('viz3d-plotly');if(!graph?._fullLayout||!root.Plotly?.toImage || graph._viz3dStatus?.phase==='loading')throw Error(tr('三维图尚未完成绘制','The 3D figure is not ready'));
            renderStatus=graph._viz3dStatus;
            plotWidth=1600;plotHeight=1000;
            const url=await root.Plotly.toImage(graph,{format:'png',width:plotWidth,height:plotHeight});
            assertCurrent();image=await exportImage(url);assertCurrent();
        }else{
            const source=$('viz2d-canvas'),geometry=source?._scientificMetadata,field=meta.field;
            const rows=field?.length,cols=field?.[0]?.length;
            if(!root.ScientificHeatmap || !Array.isArray(field) || !rows || !cols ||
                field.some(row=>!Array.isArray(row)||row.length!==cols) ||
                geometry?.shape?.[0]!==rows || geometry?.shape?.[1]!==cols ||
                !Array.isArray(geometry.wetMask) || geometry.wetMask.length!==rows ||
                geometry.wetMask.some(row=>!Array.isArray(row)||row.length!==cols))
                throw Error(tr('缺少原始字段或一致的湿网格，无法科学导出','Original field or matching wet geometry is unavailable'));
            plotWidth=1200;plotHeight=720;image=document.createElement('canvas');image.width=plotWidth;image.height=plotHeight;
            root.ScientificHeatmap.draw(image,field,{min:meta.range?.min,max:meta.range?.max,palette:meta.range?.palette,style:meta.range,pixelRatio:1,
                wetMask:geometry.wetMask,xc:geometry.coordinate_mode==='projected'?geometry.xc:undefined,
                yc:geometry.coordinate_mode==='projected'?geometry.yc:undefined,showGrid:!!$('viz2d-grid')?.checked});
        }
        const out=document.createElement('canvas');out.width=plotWidth;
        const ctx=out.getContext('2d'),header=exportHeader(ctx,meta,caseName,plotWidth);
        ctx.font='14px Segoe UI, Microsoft YaHei, sans-serif';
        const note=kind==='viz2d'?tr(`陆地浅灰，水域缺测色 ${meta.range?.nanColor || '#c9cbd0'}；原始网格无插值。`,
            `Light grey: land; missing water color ${meta.range?.nanColor || '#c9cbd0'}; original cells without interpolation.`):
            tr('图内保留当前相机和色标；完整变量身份与显示说明见页眉。','The plot retains the current camera and colour legend; full variable identity and display details are above.');
        const footer=exportLines(ctx,note,plotWidth-52),legendHeight=kind==='viz2d'?70:0;
        out.height=header.height+plotHeight+legendHeight+footer.length*21+30;
        ctx.fillStyle='#ffffff';ctx.fillRect(0,0,out.width,out.height);ctx.fillStyle='#203843';ctx.textAlign='left';
        for(const line of header.lines){ctx.font=line.font;ctx.fillText(line.text,line.x,line.y);}
        ctx.drawImage(image,0,header.height,plotWidth,plotHeight);
        const y=header.height+plotHeight+20;
        if(kind==='viz2d'){
            const width=out.width-120,range=meta.range,gradient=ctx.createLinearGradient(60,0,60+width,0);
            for(const [position,color] of colorStops(range))gradient.addColorStop(position,color);
            ctx.fillStyle=range?.noData?'#c9cbd0':gradient;ctx.fillRect(60,y,width,16);ctx.fillStyle='#203843';
            ctx.font='14px Segoe UI, Microsoft YaHei, sans-serif';
            const marks=root.ScientificStyle.ticks(range?.min,range?.max);
            marks.labels.forEach((label,i)=>{ctx.textAlign='center';ctx.fillText(label,60+(marks.labels.length===1 ? .5 : i/(marks.labels.length-1))*width,y+36);});
        }
        ctx.textAlign='left';ctx.font='14px Segoe UI, Microsoft YaHei, sans-serif';
        footer.forEach((line,index)=>ctx.fillText(line,26,header.height+plotHeight+legendHeight+21+index*21));
        const blob=await new Promise(resolve=>out.toBlob(resolve,'image/png'));assertCurrent();saveBlob(blob,filename+'.png');
    }
    function bind(){
        if(bound)return;bound=true;
        const narrow=root.matchMedia?.('(max-width: 720px)').matches || false;
        const compactInspector=root.matchMedia?.('(max-width: 1180px)').matches || false;
        for(const kind of ['viz2d','viz3d']){
            const workspace=$('page-'+kind),settingsOpen=!narrow&&kind==='viz2d';workspace?.classList.toggle('sw-settings-open',settingsOpen);
            const toggle=$(kind+'-settings-toggle');toggle?.setAttribute('aria-expanded',String(settingsOpen));
            toggle?.addEventListener('click',()=>{const open=workspace.classList.toggle('sw-settings-open');toggle.setAttribute('aria-expanded',String(open));root.ViewControls?.resizeAll();});
            const inspector=$(kind+'-inspector-toggle');
            const inspectorOpen=kind!=='viz3d'||!compactInspector;
            workspace?.classList.toggle('sw-inspector-closed',!inspectorOpen);
            inspector?.setAttribute('aria-expanded',String(inspectorOpen));
            inspector?.addEventListener('click',()=>{
                const closed=workspace.classList.toggle('sw-inspector-closed');
                inspector.setAttribute('aria-expanded',String(!closed));
                root.ViewControls?.resizeAll();
            });
            for(const name of ['palette','range-mode','range-min','range-max'])$(kind+'-'+name)?.addEventListener('change',()=>applySettings(kind));
            for(const edge of ['min','max'])$(kind+'-range-'+edge)?.addEventListener('input',()=>{record(kind).rangeDirty=true;record(kind).rangeError='';});
            $(kind+'-prev')?.addEventListener('click',()=>step(kind,-1));$(kind+'-next')?.addEventListener('click',()=>step(kind,1));
            $(kind+'-play')?.addEventListener('click',()=>togglePlay(kind));
            $(kind+'-speed')?.addEventListener('change',()=>{if(record(kind).playing){stop(kind);record(kind).resume=true;togglePlay(kind);}});
            for(const edge of ['start','end']){
                $(kind+'-play-'+edge)?.addEventListener('input',()=>{stop(kind);applyPlaybackRange(kind);});
                $(kind+'-play-'+edge)?.addEventListener('change',()=>{if(applyPlaybackRange(kind))refresh(kind);});
            }
            const seek=()=>{stop(kind);syncFrom(kind);refresh(kind);};
            time(kind)?.addEventListener('input',seek);
            if(kind==='viz3d')$('viz3d-time-slider')?.addEventListener('input',()=>{time(kind).value=$('viz3d-time-slider').value;seek();});
            $(kind+'-export')?.addEventListener('click',()=>exportFigure(kind).catch(e=>failure(kind,e.message)));
        }
        $('viz3d-camera')?.addEventListener('change',()=>root.set3DCamera?.($('viz3d-camera').value));
        $('viz3d-opacity')?.addEventListener('change',()=>refresh('viz3d'));
        $('viz2d-grid')?.addEventListener('change',()=>refresh('viz2d'));
        document.querySelectorAll?.('.sw-analysis').forEach(details=>details.addEventListener('toggle',()=>{
            if(!details.open)return;root.ViewControls?.resizeAll();
            if(details.classList.contains('sw-section-analysis')){if(typeof updateSpatialSection==='function')updateSpatialSection();}
            else {if(typeof updateViz3d==='function')updateViz3d();if(typeof updateViz3dAvg==='function')updateViz3dAvg();}
        }));
        document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
    }
    const current=kind=>record(kind).last?.key===revision()?record(kind).last:null;
    const colorContext=kind=>{
        const name=settingsVariable(kind),meta=current(kind);
        return {caseKey:caseKey(),revision:revision(),variable:name,label:meta?.variable===name?meta.label:name,
            units:meta?.variable===name?meta.units:'',range:meta?.variable===name?meta.range:null};
    };
    root.ScientificWorkspace={bind,caseKey,colorContext,activate,syncFrom,updateTimeControls,variableMetadata,timeLabels,frameCount,dateLabel,
        isPlaying:kind=>record(kind).playing,loading,failure,empty,publish,current,applySettings,refresh,step,togglePlay,stop,onNavigate,exportFigure,setRenderState:fullscreenState};
    if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',bind,{once:true});else bind();
})(typeof window!=='undefined'?window:globalThis);
