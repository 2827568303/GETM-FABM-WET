// Shared view controls. Plot data and canvas backing buffers are never changed
// by app zoom; native editors can supply their own coordinate-aware viewport.
const ViewControlsMath = {
    fitCanvas(width,height,sourceWidth,sourceHeight) {
        if (![width,height,sourceWidth,sourceHeight].every(v=>Number.isFinite(v)&&v>0)) return {width:0,height:0};
        const ratio=Math.min(width/sourceWidth,height/sourceHeight);
        return {width:sourceWidth*ratio,height:sourceHeight*ratio};
    },
    appScale(value) { return Number.isFinite(value) ? Math.max(0.6,Math.min(1.8,Math.round(value*100)/100)) : 1; },
    zoomRange(min,max,anchor,factor) {
        return {min:anchor+(min-anchor)/factor,max:anchor+(max-anchor)/factor};
    },
    zoomCategoryRange(range,factor,decimal,full) {
        const fullSpan=full.max-full.min;
        if(fullSpan<=0)return {...full};
        const span=Math.max(0.25,Math.min(fullSpan,(range.max-range.min)/factor));
        const position=Math.max(0,Math.min(1,decimal));
        const anchor=range.min+(range.max-range.min)*position;
        const min=Math.max(full.min,Math.min(full.max-span,anchor-span*position));
        return {min,max:min+span};
    },
    zoomViewport(view,factor,x,y) {
        const scale=Math.max(1,Math.min(30,view.scale*factor)), f=scale/view.scale;
        return {scale,x:x-(x-view.x)*f,y:y-(y-view.y)*f};
    }
};

(() => {
    if(typeof window==='undefined' || typeof document==='undefined') return;
    const registered=new Map(), chartBindings=new WeakMap();
    const storageKey='3dwet.interface-scale';
    let scale=1, resizeFrame=0;
    try {scale=ViewControlsMath.appScale(Number(localStorage.getItem(storageKey)) || 1);}catch(_){}
    function applyScale(value) {
        scale=ViewControlsMath.appScale(value);
        document.documentElement.style.setProperty('--interface-scale',scale);
        document.documentElement.style.zoom=scale;
        // CSS viewport units do not shrink after zoom; compensate layout height
        // so bottom controls remain reachable at every supported interface size.
        document.body.style.height=`${100/scale}vh`;
        const layout=document.querySelector('.app-layout');
        if(layout) layout.style.height=`${100/scale}vh`;
        try{localStorage.setItem(storageKey,String(scale));}catch(_){}
        const badge=document.getElementById('vc-app-scale');
        if(badge) badge.textContent=`${Math.round(scale*100)}%`;
        resizeAll();
    }
    document.addEventListener('wheel',e=>{
        if(!e.ctrlKey || !e.deltaY) return;
        e.preventDefault();e.stopImmediatePropagation();
        applyScale(scale+(e.deltaY<0 ? 0.05 : -0.05));
    },{capture:true,passive:false});
    document.addEventListener('keydown',e=>{
        if((e.ctrlKey || e.metaKey) && (e.key==='0' || e.code==='Numpad0')) {
            e.preventDefault();applyScale(1);
        }
    },true);
    function visible(element) {const r=element.getBoundingClientRect();return r.width>0 && r.height>0;}
    function resizeAll() {
        if(resizeFrame) return;
        resizeFrame=requestAnimationFrame(()=>{
            resizeFrame=0;
            registered.forEach((record,element)=>{
                if(!element.isConnected){record.observer?.disconnect();registered.delete(element);return;}
                if(visible(element)) record.hooks.resize?.();
            });
        });
    }
    async function fullscreen(element) {
        try {
            if(document.fullscreenElement) await document.exitFullscreen();
            else if(element.requestFullscreen) await element.requestFullscreen();
            else {element.classList.toggle('vc-expanded');resizeAll();}
        }catch(_){element.classList.toggle('vc-expanded');resizeAll();}
    }
    function registerGraphic(element,hooks={}) {
        if(typeof element==='string') element=document.getElementById(element);
        if(!element || registered.has(element)) return;
        const host=hooks.host || element.parentElement;
        if(!host) return;
        host.classList.add('vc-graphic-host');
        const toolbar=document.createElement('div');toolbar.className='vc-plot-tools';
        toolbar.setAttribute('role','group');toolbar.setAttribute('aria-label','图形视图控制');
        function button(icon,title,action) {
            const b=document.createElement('button');b.type='button';b.appendChild(window.StudioIcons.node(icon));b.title=title;b.setAttribute('aria-label',title);
            b.addEventListener('click',e=>{e.stopPropagation();action();});toolbar.append(b);
        }
        if(hooks.zoom){button('zoom-in','放大图形',()=>hooks.zoom(1.25));button('zoom-out','缩小图形',()=>hooks.zoom(0.8));}
        const reset=document.createElement('button');reset.type='button';reset.textContent='复位';reset.title='恢复完整图形范围';reset.setAttribute('aria-label','恢复完整图形范围');reset.addEventListener('click',e=>{e.stopPropagation();hooks.reset?.();});toolbar.append(reset);
        button('expand','全屏 / 退出全屏',()=>fullscreen(host));
        host.append(toolbar);
        const record={hooks,observer:null,toolbar};registered.set(element,record);
        let last='';
        if(typeof ResizeObserver!=='undefined') {
            record.observer=new ResizeObserver(()=>{
                const r=host.getBoundingClientRect(), key=`${Math.round(r.width)}:${Math.round(r.height)}`;
                if(key===last) return;last=key;
                // Coalesce updates outside observer delivery, avoiding feedback loops.
                resizeAll();
            });record.observer.observe(host);
        }
    }
    function chartRegister(chart) {
        if(chartBindings.has(chart)) return;
        const canvas=chart.canvas;
        const baseline={}, fractional={}, fullRanges={};
        const remember=()=>Object.entries(chart.scales).forEach(([id,s])=>{
            baseline[id]={min:s.options.min,max:s.options.max};
            fullRanges[id]={min:s.min,max:s.max};
            if(s.type==='category') fractional[id]={min:s.min,max:s.max};
        });
        remember();
        function zoom(factor,event) {
            for(const [id,s] of Object.entries(chart.scales)) {
                const rect=canvas.getBoundingClientRect();
                const pixel=event ? (s.isHorizontal() ? (event.clientX-rect.left)*chart.width/rect.width : (event.clientY-rect.top)*chart.height/rect.height) : (s.left+s.right)/2;
                const anchor=event ? s.getValueForPixel(pixel) : (s.min+s.max)/2;
                const range=s.type==='category' ? ViewControlsMath.zoomCategoryRange(
                    fractional[id],factor,event ? s.getDecimalForPixel(pixel) : 0.5,fullRanges[id]
                ) : ViewControlsMath.zoomRange(s.min,s.max,anchor,factor);
                if(!Number.isFinite(range.min)||!Number.isFinite(range.max)) continue;
                if(s.type==='category') fractional[id]=range;
                chart.options.scales[id].min=s.type==='category' ? Math.floor(range.min):range.min;
                chart.options.scales[id].max=s.type==='category' ? Math.ceil(range.max):range.max;
            }
            chart.update('none');
        }
        const wheel=e=>{if(e.ctrlKey || !e.deltaY) return;e.preventDefault();zoom(e.deltaY<0?1.18:1/1.18,e);};
        canvas.addEventListener('wheel',wheel,{passive:false});
        let drag=null;
        const down=e=>{if(e.button!==1 && !e.shiftKey)return;e.preventDefault();drag={x:e.clientX,y:e.clientY,ranges:Object.fromEntries(Object.entries(chart.scales).map(([id,s])=>[id,{min:s.min,max:s.max}]))};};
        const move=e=>{
            if(!drag) return;
            const rect=canvas.getBoundingClientRect();
            for(const [id,s] of Object.entries(chart.scales)) {
                const r=drag.ranges[id],delta=s.isHorizontal()?(e.clientX-drag.x)*chart.width/rect.width:(e.clientY-drag.y)*chart.height/rect.height;
                const p0=s.isHorizontal()?s.left:s.top;
                const shift=s.getValueForPixel(p0)-s.getValueForPixel(p0+delta);
                chart.options.scales[id].min=r.min+shift;chart.options.scales[id].max=r.max+shift;
                if(s.type==='category') fractional[id]={min:r.min+shift,max:r.max+shift};
            }chart.update('none');
        };
        const up=()=>{drag=null;};
        canvas.addEventListener('pointerdown',down);window.addEventListener('pointermove',move);window.addEventListener('pointerup',up);
        chartBindings.set(chart,()=>{
            canvas.removeEventListener('wheel',wheel);canvas.removeEventListener('pointerdown',down);
            window.removeEventListener('pointermove',move);window.removeEventListener('pointerup',up);
            // Chart.js clears chart.canvas before afterDestroy. Retain the
            // original element to release its resize hook and exact toolbar.
            const record=registered.get(canvas);
            record?.observer?.disconnect();record?.toolbar?.remove();
            registered.delete(canvas);chartBindings.delete(chart);
        });
        registerGraphic(canvas,{zoom,reset:()=>{
            Object.entries(baseline).forEach(([id,r])=>{chart.options.scales[id].min=r.min;chart.options.scales[id].max=r.max;if(fractional[id])fractional[id]={...fullRanges[id]};});chart.update('none');
        },resize:()=>chart.resize()});
    }
    function plotlyRegister(element) {
        if(typeof element==='string') element=document.getElementById(element);
        if(!element || registered.has(element))return;
        const host=document.createElement('div');host.className='vc-plotly-viewport';
        element.before(host);host.append(element);
        const camera=element._fullLayout?.scene?.camera;
        registerGraphic(element,{host,resize:()=>{
            if(!element._fullLayout)return;
            if(element.id==='viz3d-plotly' && window.resizeScientific3D)window.resizeScientific3D(element);
            else window.Plotly.Plots.resize(element);
        },reset:()=>{
            const update={};
            for(const key of Object.keys(element._fullLayout || {})) if(/^[xy]axis\d*$/.test(key)) update[key+'.autorange']=true;
            if(element._fullLayout?.scene) update['scene.camera']=camera || {eye:{x:1.35,y:-1.5,z:0.75}};
            window.Plotly.relayout(element,update);
        }});
    }
    function registerCanvas(canvas,hooks) {registerGraphic(canvas,hooks);}
    function genericCanvas(canvas) {
        if(registered.has(canvas)||canvas.dataset.nativeViewport==='true'||canvas.id==='pp-depth-canvas'||canvas.id==='ge-canvas'||!canvas.id)return;
        if(window.Chart?.getChart(canvas))return;
        if(!canvas.id.startsWith('pp-') && !canvas.id.startsWith('mini-heat-') && !canvas.classList.contains('viz-canvas'))return;
        const host=document.createElement('div');host.className='vc-canvas-viewport';
        canvas.before(host);host.append(canvas);
        let view={scale:1,x:0,y:0},drag=null;
        const paint=()=>{canvas.style.transformOrigin='0 0';canvas.style.transform=`translate(${view.x}px,${view.y}px) scale(${view.scale})`;};
        const resizable=canvas.id==='viz2d-canvas';
        const fit=()=>{
            if(!resizable)return;
            // Native CSS resize changes inline dimensions; keep both edit fields
            // in sync without turning responsive 100% width into a fixed width.
            const widthInput=document.getElementById('viz2d-width');
            const heightInput=document.getElementById('viz2d-height');
            if(widthInput)widthInput.value=host.style.width.endsWith('px')?String(Math.round(parseFloat(host.style.width))):'';
            if(heightInput)heightInput.value=String(Math.round(parseFloat(host.style.height)||500));
            const styles=typeof getComputedStyle==='function'?getComputedStyle(host):{};
            const inset=(a,b)=>(parseFloat(styles[a])||0)+(parseFloat(styles[b])||0);
            if(canvas._scientificResize){
                canvas._scientificResize(host.clientWidth-inset('paddingLeft','paddingRight'),host.clientHeight-inset('paddingTop','paddingBottom'));
                return;
            }
            const size=ViewControlsMath.fitCanvas(
                host.clientWidth-inset('paddingLeft','paddingRight'),
                host.clientHeight-inset('paddingTop','paddingBottom'),canvas.width,canvas.height);
            if(!size.width)return;
            canvas.style.width=size.width+'px';canvas.style.height=size.height+'px';
        };
        const setSize=(width,height)=>{
            host.style.width=Number.isFinite(width)&&width>0 ? Math.round(Math.max(120,Math.min(4000,width)))+'px':'100%';
            host.style.height=Math.round(Math.max(180,Math.min(1600,Number(height)||500)))+'px';
            view={scale:1,x:0,y:0};fit();paint();resizeAll();
        };
        if(resizable){host.id='viz2d-viewport';host.classList.add('vc-resizable');setSize(null,Math.max(300,Math.min(700,window.innerHeight*.55)));}
        const zoom=(factor,e)=>{const rect=host.getBoundingClientRect();const app=scale;
            view=ViewControlsMath.zoomViewport(view,factor,e?(e.clientX-rect.left)/app:rect.width/app/2,e?(e.clientY-rect.top)/app:rect.height/app/2);paint();};
        canvas.addEventListener('wheel',e=>{if(e.ctrlKey || !e.deltaY)return;e.preventDefault();zoom(e.deltaY<0?1.18:1/1.18,e);},{passive:false});
        canvas.addEventListener('pointerdown',e=>{if(e.button!==1)return;e.preventDefault();drag={x:e.clientX,y:e.clientY,v:{...view}};canvas.setPointerCapture(e.pointerId);});
        canvas.addEventListener('pointermove',e=>{if(!drag)return;view.x=drag.v.x+(e.clientX-drag.x)/scale;view.y=drag.v.y+(e.clientY-drag.y)/scale;paint();});
        canvas.addEventListener('pointerup',()=>{drag=null;});
        registerGraphic(canvas,{host,zoom,reset:()=>{view={scale:1,x:0,y:0};fit();paint();},resize:fit,setSize});
    }
    function installLibraries() {
        if(window.Chart && !window.Chart._vcInstalled) {
            window.Chart._vcInstalled=true;
            window.Chart.register({id:'3dwetViewControls',afterUpdate:chartRegister,
                afterDestroy(chart){chartBindings.get(chart)?.();}});
        }
        if(window.Plotly && !window.Plotly._vcInstalled) {
            window.Plotly._vcInstalled=true;
            for(const name of ['newPlot','react']) {
                const original=window.Plotly[name];
                window.Plotly[name]=function(element,data,layout,config){
                    const result=original.call(this,element,data,layout,{...config,responsive:true,scrollZoom:true});
                    Promise.resolve(result).then(()=>plotlyRegister(element));return result;
                };
            }
        }
        if(window.L && !window.L._vcInstalled) {
            window.L._vcInstalled=true;const original=window.L.map;
            window.L.map=function(element,options){const map=original.call(this,element,options), el=map.getContainer();
                // Defer until caller sets the initial center/bounds.
                requestAnimationFrame(()=>{const center=map.getCenter(),zoom=map.getZoom();
                    const host=document.createElement('div');host.className='vc-map-viewport';el.before(host);host.append(el);
                    registerGraphic(el,{host,
                    zoom:f=>map.setZoom(map.getZoom()+(f>1?1:-1)),reset:()=>map.setView(center,zoom),resize:()=>map.invalidateSize({pan:false})});});return map;};
        }
    }
    function discover() {
        installLibraries();document.querySelectorAll('canvas').forEach(genericCanvas);
        const depth=document.getElementById('pp-depth-canvas');
        if(depth && typeof window.resetDepthView==='function') registerCanvas(depth,{
            reset:()=>window.resetDepthView(),resize:()=>window._ppRedrawDepth?.()
        });
    }
    function start() {
        const topbar=document.querySelector('.topbar-right');
        if(topbar){const b=document.createElement('button');b.type='button';b.id='vc-app-scale';b.className='btn btn-sm';b.title='界面比例：Ctrl+滚轮调整，Ctrl+0 或点击复位';b.addEventListener('click',()=>applyScale(1));topbar.prepend(b);}
        applyScale(scale);discover();
        const observer=new MutationObserver(records=>{
            if(records.some(r=>r.type==='attributes' && r.target.classList.contains('page'))) resizeAll();
            if(records.some(r=>r.addedNodes.length)) discover();
        });
        observer.observe(document.body,{subtree:true,childList:true,attributes:true,attributeFilter:['class']});
        window.addEventListener('resize',resizeAll);window.addEventListener('pageshow',resizeAll);
        document.addEventListener('visibilitychange',()=>{if(!document.hidden)resizeAll();});
        document.addEventListener('fullscreenchange',resizeAll);
    }
    function setCanvasSize(id,width,height){registered.get(document.getElementById(id))?.hooks.setSize?.(width,height);}
    function fitCanvas(id){setCanvasSize(id,null,Math.max(300,Math.min(700,window.innerHeight*.55)));}
    window.ViewControls={registerCanvas,registerGraphic,resizeAll,setCanvasSize,fitCanvas,setAppScale:applyScale,getAppScale:()=>scale};
    if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
