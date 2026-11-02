const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const {test}=require('node:test');
const source=fs.readFileSync('3DWET/app/static/js/viz3d.js','utf8');
const volume={shape:[2,1,2],xc:[0,100],yc:[0],bottom:[[4,8]],sigma:[-.75,-.25],
    data:[[[0,-2]],[[3,null]]],min:-2,max:3,units:'mg/L',long_name:'test'};
const isoVolume={...volume,shape:[2,2,2],yc:[0,100],bottom:[[4,8],[4,8]],
    data:[[[0,-2],[0,-2]],[[3,2],[3,2]]]};
function env(payload=volume,style) {
    const plots=[],resolved=[],relayouts=[],element={innerHTML:'',dataset:{},on:()=>{}};
    const status={textContent:'',dataset:{}};
    const Plotly={newPlot:async(e,traces,layout,config)=>{plots.push({traces,layout,config});},
        relayout:async(e,value)=>relayouts.push(value)};
    const ScientificStyle=style&&{resolve:args=>{resolved.push(args);return style;}};
    const context=vm.createContext({console,Plotly,URL,URLSearchParams,window:{Plotly,ScientificStyle},
        document:{getElementById:id=>id==='viz3d-status'?status:element},fetch:async url=>({json:async()=>String(url).includes('/api/geo/grid?display=scientific')?{shape:[payload.data.length,payload.data[0].length],coordinate_mode:'index',coordinate_units:'index',wetMask:payload.data.map(row=>row.map(()=>true))}:payload})});
    vm.runInContext(source,context);return {context,plots,resolved,relayouts,element,status};
}
test('opaque scientific slices use the shared quantitative range and exact legend ticks',async()=>{
    const scale={min:-5,max:5,palette:'cividis',mode:'locked',colorscale:[[0,'#000000'],[1,'#ffffff']],tickvals:[-5,0,5],ticktext:['-5','0','5']};
    const e=env(volume,scale);
    await e.context.render3DWaterBody('test',2,{level:0,ve:100,timeLabel:'2026-10-14 12:00',caseKey:'C:/A'});
    assert.deepEqual(JSON.parse(JSON.stringify(e.resolved)),[{caseKey:'C:/A',variable:'test',min:-2,max:3}]);
    const p=e.plots[0],field=p.traces.find(trace=>trace.meta?.scientificField===true),floor=p.traces[0];
    assert.equal(field.cmin,-5);assert.equal(field.cmax,5);
    assert.deepEqual(JSON.parse(JSON.stringify(field.colorscale)),scale.colorscale);
    assert.deepEqual(field.colorbar.tickvals,scale.tickvals);assert.deepEqual(field.colorbar.ticktext,scale.ticktext);
    assert.equal(field.opacity,1,'single-layer default supports quantitative colour reading');
    assert.equal(field.lighting.ambient,1);assert.equal(field.lighting.diffuse,0);assert.equal(field.lighting.specular,0);
    assert.ok(floor.color,'basin behind a scalar layer is a neutral material');
    assert.ok(field.intensity.includes(0)&&field.intensity.includes(-2),'zero and negative field values are retained');
    assert.match(p.layout.title.text,/2026-10-14 12:00/);assert.match(p.layout.title.text,/100×/);assert.match(p.layout.title.text,/locked|锁定/);
    assert.match(p.config.toImageButtonOptions.filename,/2026-10-14/,'export filename includes actual output date');
});
test('transparent layer stacks disclose colour mixing in the visible title/status',async()=>{
    const e=env();await e.context.render3DWaterBody('test',0,{level:1,stack:true,opacity:.55});
    assert.match(e.plots[0].layout.title.text+e.status.textContent,/混色|混合|mix/i);
    assert.ok(e.plots[0].traces.find(trace=>trace.meta?.scientificField===true).opacity<=.55);
});
test('static bathymetry views keep the bed hidden and show a translucent water surface with side walls',async()=>{
    for(const mode of ['custom','locked']){
        const style={min:0,max:12,mode,palette:'cividis',colorscale:[[0,'#000000'],[1,'#ffffff']],tickvals:[0,6,12],ticktext:['0','6','12']};
        for(const preview of [true,false]){
            const payload=preview?{depth:volume.bottom,xc:volume.xc,yc:volume.yc,nx:2,ny:1}:volume;
            const e=env(payload,style),published=[];e.context.window.ScientificWorkspace={publish:(kind,meta)=>published.push(meta)};
            if(preview)await e.context.renderBathymetry3D({caseKey:'A',ve:1});
            else await e.context.render3DWaterBody('test',0,{overlay:false,caseKey:'A',ve:1});
            assert.equal(e.resolved[0]?.variable,'__bathy__');
            assert.ok(!e.plots[0].traces.some(trace=>trace.meta?.waterbodyFrame==='bed'),
                'static bathymetry hides the lake bed by default');
            const surface=e.plots[0].traces.find(trace=>trace.meta?.waterbodyFrame==='surface');
            assert.ok(surface,'the static preview retains a spatially coherent water surface');
            assert.equal(surface.opacity,.58,'the stronger static blue surface remains translucent and readable');
            assert.equal(surface.color,'#398eae','the static water has a distinct, readable blue material');
            assert.ok(e.plots[0].traces.some(trace=>trace.meta?.waterbodyFrame==='wall'),
                'wet-grid sidewalls show volume without a rendered bed');
            assert.ok(e.plots[0].layout.scene.zaxis.range[1]>0,
                'the static surface at z=0 has headroom inside the scene instead of sitting on the axis clipping boundary');
            assert.equal(e.plots[0].layout.scene.camera.eye.z,.82,
                'the default oblique camera gives the basin side faces room to read as volume');
            const shoreline=e.plots[0].traces.find(trace=>trace.meta?.shoreline===true);
            assert.match(shoreline.name,/湿网格岸线.*代理，未验证/,
                'a wet-mask outline is labeled as an unvalidated display proxy');
            assert.ok(!e.plots[0].traces.some(t=>t.meta?.waterbodyFrame==='depthProjection'),
                'static views do not flatten the basin into an opaque top-plane depth raster');
            if(preview) assert.match(e.plots[0].layout.title.text,/湖盆地形/);
            assert.match(e.status.textContent,/(湖底隐藏.*半透明蓝色水面与湿网格侧壁展示体积|半透明蓝色水面与湿网格侧壁展示体积.*湖底隐藏)/);
            assert.equal(published[0].variable,'__bathy__');assert.deepEqual(published[0].range,style);
        }
    }
});
test('a no-output static depth preview keeps the water material visible instead of replacing it with an opaque z=0 projection',async()=>{
    const data={...volume,static_geometry_key:'static-grid',coordinate_mode:'projected',coordinate_units:'m'};
    const e=env(data,{min:0,max:12,mode:'auto',palette:'lake',colorscale:[],tickvals:[],ticktext:[]});
    const geometry=e.context.buildLakeGeometry(data.xc,data.yc,data.bottom,1);
    const traces=e.context.lakeTraces(geometry,true,data,null,
        {staticBathymetry:true},null,'__bathy__');
    const surface=traces.find(trace=>trace.meta?.waterbodyFrame==='surface');
    const wall=traces.find(trace=>trace.meta?.waterbodyFrame==='wall');
    assert.ok(surface,'static preview retains the native blue water material');
    assert.equal(surface.color,'#398eae');
    assert.equal(surface.opacity,.58,'the water plane has enough contrast to read as the lake surface');
    assert.ok(!traces.some(trace=>trace.meta?.waterbodyFrame==='bed'),'the bed is not drawn by default');
    assert.ok(wall,'the wet-grid side wall remains available to read lake volume');
    assert.ok(!traces.some(trace=>trace.meta?.waterbodyFrame==='depthProjection'),
        'bathymetry is not rendered as an opaque top plane over the water surface');
});
test('no-output preview title identifies the static basin and its status discloses the reason',async()=>{
    const payload={depth:volume.bottom,xc:volume.xc,yc:volume.yc,nx:2,ny:1};
    const e=env(payload);
    await e.context.renderBathymetry3D({caseKey:'A',staticPreviewReason:'没有3D输出文件'});
    assert.match(e.plots[0].layout.title.text,/静态湖盆（无动态输出）/);
    assert.match(e.status.textContent,/没有3D输出文件.*静态湖盆与水面示意/);
});
test('fallback adaptive ticks distinguish a narrow range and handle a constant field',async()=>{
    const e=env({...volume,min:15.149,max:15.150});await e.context.render3DCloud('test',0);
    const colorbar=e.plots[0].traces[0].marker.colorbar;
    assert.ok(colorbar.ticktext.length>1);assert.equal(new Set(colorbar.ticktext).size,colorbar.ticktext.length);
    const constant=env({...volume,min:0,max:0});await constant.context.render3DCloud('test',0);
    assert.deepEqual(Array.from(constant.plots[0].traces[0].marker.colorbar.tickvals),[0]);
});
test('an empty shared range never becomes a false zero-valued plot',async()=>{
    const e=env(volume,{min:null,max:null,palette:'lake',mode:'auto',colorscale:[],tickvals:[],ticktext:[]});
    await e.context.render3DCloud('test',0);assert.equal(e.plots.length,0);
    assert.match(e.status.textContent,/无有效|没有有效|no data/i);
});
test('named cameras stay orthographic and survive a refresh; reset restores the default',async()=>{
    const e=env();assert.equal(typeof e.context.window.set3DCamera,'function');
    await e.context.window.set3DCamera('top');await e.context.render3DCloud('test',0);
    const camera=e.plots[0].layout.scene.camera;
    assert.equal(camera.eye.x,0);assert.equal(camera.eye.y,0);assert.ok(camera.eye.z>0);
    assert.equal(camera.projection.type,'orthographic');
    await e.context.window.set3DCamera('front');await e.context.render3DCloud('test',1);
    assert.equal(e.plots[1].layout.scene.camera.eye.x,0);assert.ok(e.plots[1].layout.scene.camera.eye.y<0);
    await e.context.window.set3DCamera('reset');await e.context.render3DCloud('test',1);
    assert.equal(e.plots[2].layout.scene.camera.eye.x,0.8525);
});
test('all scalar modes use the shared scale and neutral quantitative lighting',async()=>{
    const style={min:-10,max:10,mode:'custom',palette:'viridis',colorscale:[[0,'#123456'],[1,'#abcdef']],tickvals:[-10,0,10],ticktext:['-10','0','10']};
    for(const mode of ['cloud','iso','height']) {
        const e=env(mode==='height'?{...volume,data:volume.data[0]}:mode==='iso'?isoVolume:volume,style);
        if(mode==='cloud') await e.context.render3DCloud('test',0,22,{ve:2,caseKey:'A'});
        else if(mode==='iso') await e.context.render3DSurface('test',0,18,{ve:2,caseKey:'A'});
        else await e.context.render2DAs3DSurface('test',0,1,{caseKey:'A',timeLabel:'2026-10-14'});
        const t=e.plots[0].traces[0],data=mode==='cloud'?t.marker:t;
        assert.equal(data.cmin,-10,mode);assert.equal(data.cmax,10,mode);assert.equal(e.resolved.length,1,mode);
        if(mode!=='cloud') assert.equal(t.lighting.ambient,1,mode);
        if(mode==='height') {assert.match(e.plots[0].layout.title.text,/变量高度/);assert.match(e.plots[0].layout.scene.zaxis.title,/mg\/L/);}
    }
});
test('spatial sections apply vertical scale to geometry but keep true depth in axes and hover',async()=>{
    const d={data:[[0,-2]],horizontal:[0,100],horizontal_edges:[-50,50,150],depth_edges:[[4,8],[0,0]],min:-2,max:0,units:'mg/L',long_name:'test',coordinate_units:'m'};
    const style={min:-5,max:5,mode:'locked',colorscale:[[0,'#123456'],[1,'#abcdef']],tickvals:[-5,0,5],ticktext:['-5','0','5']};
    const e=env(d,style);await e.context.renderSpatialSection('test',2,'xz',0,{ve:100,caseKey:'A',timeLabel:'2026-10-14'});
    const p=e.plots[0],mesh=p.traces[0];assert.equal(mesh.z[0],-400);assert.equal(mesh.customdata[0][0],4);
    assert.equal(p.layout.scene.zaxis.tickvals.at(-1),-800);assert.equal(p.layout.scene.zaxis.ticktext.at(-1),'8');
    assert.equal(mesh.cmin,-5);assert.match(p.layout.title.text,/2026-10-14/);assert.match(p.layout.title.text,/100×/);
});
test('narrow viewport titles remain concise without dropping the actual output time',()=>{
    const e=env();e.element.getBoundingClientRect=()=>({width:300});
    const title=e.context.viz3dTitle('温度','2026-10-14 12:00 · 层 1/2 · 垂向 100× · 锁定范围 · 透明叠层会混色');
    assert.ok((title.text.match(/<br>/g)||[]).length<=1,'detailed warnings belong in status and export metadata, leaving the plot readable');
    assert.match(title.text,/2026-10-14 12:00/);
});
test('WebGL failures explain the available 2D and numerical section paths',async()=>{
    const e=env();e.context.window.Plotly.newPlot=async()=>{throw Error('WebGL context unavailable');};
    await e.context.render3DCloud('test',0);
    assert.match(e.status.textContent,/二维|2D/i);assert.match(e.status.textContent,/剖面|section/i);
});
test('a stack retains its colour legend when the selected upper layer is empty',async()=>{
    const e=env({...volume,data:[volume.data[0],[[null,null]]]});
    await e.context.render3DWaterBody('test',1,{stack:true,level:1});
    assert.ok(e.plots[0].traces.some(t=>t.showscale && t.intensity?.some(Number.isFinite)),'at least one displayed data layer owns the scalar legend');
});
test('workspace publication contains actual data range, selected layer and effective vertical scale',async()=>{
    const e=env(),published=[];e.context.window.ScientificWorkspace={publish:(...args)=>published.push(args)};
    await e.context.render3DWaterBody('test',2,{ve:100,level:0,caseKey:'A',timeLabel:'2026-10-14 12:00'});
    assert.equal(published.length,1);const [kind,meta]=published[0];
    assert.equal(kind,'viz3d');assert.equal(meta.variable,'test');assert.equal(meta.units,'mg/L');
    assert.equal(meta.min,-2);assert.equal(meta.max,3);assert.equal(meta.range.min,-2);
    assert.equal(meta.level,0);assert.equal(meta.ve,100);assert.equal(meta.time,2);assert.equal(meta.date,'2026-10-14 12:00');
    assert.deepEqual(meta.field,volume.data);
});
test('bathymetry spacing fallback preserves distinct horizontal dx and dy',async()=>{
    const e=env({depth:[[4,8],[4,8]],nx:2,ny:2,dx:100,dy:200});
    await e.context.renderBathymetry3D({ve:1});const floor=e.plots[0].traces[0];
    assert.equal(Math.max(...floor.x)-Math.min(...floor.x),200);
    assert.equal(Math.max(...floor.y)-Math.min(...floor.y),400,'non-square cell spacing must not be replaced by dx');
});
test('existing graphs refresh through Plotly.react without clearing their DOM first',async()=>{
    const e=env();e.element.innerHTML='<div>previous graph</div>';e.element._fullLayout={scene:{}};let reacted=false;
    e.context.window.Plotly.react=async()=>{assert.equal(e.element.innerHTML,'<div>previous graph</div>');reacted=true;};
    await e.context.render3DCloud('test',0);assert.equal(reacted,true);
});
test('saved orbit cameras keep orthographic projection even when an event omits it',async()=>{
    const e=env();e.element._fullLayout={scene:{camera:{eye:{x:2,y:1,z:1}}}};
    await e.context.render3DCloud('test',0);assert.equal(e.plots[0].layout.scene.camera.projection.type,'orthographic');
});
test('animation refreshes do not accumulate camera event listeners',async()=>{
    const e=env();const listeners={};e.element.on=event=>{listeners[event]=(listeners[event] || 0)+1;};
    await e.context.render3DCloud('test',0);e.element._fullLayout={scene:{}};
    e.context.window.Plotly.react=async()=>{};
    await e.context.render3DCloud('test',1);await e.context.render3DCloud('test',2);
    assert.deepEqual(listeners,{plotly_relayout:1,plotly_relayouting:1},
        'one listener per camera event survives Plotly.react across frames');
});
test('default scalar slices keep the translucent water surface visible without taking the scientific colour scale',async()=>{
    const e=env();await e.context.render3DWaterBody('test',0,{level:0});
    const surface=e.plots[0].traces.find(t=>t.name==='水面');
    const field=e.plots[0].traces.find(t=>t.meta?.waterbodyFrame==='field');
    assert.ok(surface,'the real wet-cell water surface remains visible above the selected layer');
    assert.ok(surface.opacity>=0.28&&surface.opacity<0.5,'the water surface stays visibly blue while remaining translucent enough to read the scientific field');
    assert.notEqual(surface.showscale,true,'structural water must not claim a scientific colour scale');
    assert.equal(surface.cmin,undefined);assert.equal(surface.cmax,undefined);
    assert.equal(field.showscale,true,'the selected scalar field retains its own quantitative legend');
    assert.ok(!e.plots[0].traces.some(t=>t.meta?.waterbodyFrame==='bed'),'the basin bed remains hidden by default');
});
test('all-empty frames never initialize a locked range or publish a false zero field',async()=>{
    for(const mode of ['water','cloud','iso','height','section']) {
        const empty={...volume,data:[[[null,null]],[[null,null]]],min:0,max:0};
        const e=env(mode==='height'?{...empty,data:[[null,null]]}:mode==='section'?{
            data:[[null,null]],horizontal:[0,100],horizontal_edges:[-50,50,150],depth_edges:[[4,8],[0,0]],min:0,max:0}:empty);
        vm.runInContext(fs.readFileSync('3DWET/app/static/js/scientific_style.js','utf8'),e.context);
        const style=e.context.window.ScientificStyle;style.set('A','test',{mode:'locked'});
        const opts={caseKey:'A',level:0};
        if(mode==='water') await e.context.render3DWaterBody('test',0,opts);
        else if(mode==='cloud') await e.context.render3DCloud('test',0,22,opts);
        else if(mode==='iso') await e.context.render3DSurface('test',0,18,opts);
        else if(mode==='height') await e.context.render2DAs3DSurface('test',0,0,opts);
        else await e.context.renderSpatialSection('test',0,'xz',0,opts);
        if(['water','cloud','iso'].includes(mode)){
            assert.equal(e.plots.length,1,mode);
            assert.ok(e.plots[0].traces.some(t=>t.meta?.missingWater),mode);
            assert.ok(e.plots[0].traces.every(t=>!t.showscale&&!t.marker?.showscale),`${mode}: missing material has no numeric scale`);
        }else assert.equal(e.plots.length,0,`${mode} cannot invent scalar height or section values`);
        assert.equal(style.get('A','test').min,null,`${mode} must leave an uninitialized lock empty`);
        assert.equal(style.get('A','test').max,null,mode);
        const valid=mode==='height' ? {...volume,data:[[10,20]],min:10,max:20} : mode==='section' ? {
            data:[[10,20]],horizontal:[0,100],horizontal_edges:[-50,50,150],depth_edges:[[4,8],[0,0]],min:10,max:20}
            : mode==='iso'?{...isoVolume,data:[[[10,20],[10,20]],[[15,20],[15,20]]],min:10,max:20}
            : {...volume,data:[[[10,20]],[[15,null]]],min:10,max:20};
        e.context.fetch=async url=>({json:async()=>String(url).includes('/api/geo/grid?display=scientific')?{shape:[valid.data.length,valid.data[0].length],coordinate_mode:'index',coordinate_units:'index',wetMask:valid.data.map(row=>row.map(()=>true))}:valid});
        if(mode==='water') await e.context.render3DWaterBody('test',1,opts);
        else if(mode==='cloud') await e.context.render3DCloud('test',1,22,opts);
        else if(mode==='iso') await e.context.render3DSurface('test',1,18,opts);
        else if(mode==='height') await e.context.render2DAs3DSurface('test',1,0,opts);
        else await e.context.renderSpatialSection('test',1,'xz',0,opts);
        assert.equal(style.get('A','test').min,10,`${mode} locks the next actual finite frame`);
        assert.equal(style.get('A','test').max,20,mode);
    }
});
test('linked sections inherit the exact successful main auto range and palette',async()=>{
    const e=env();vm.runInContext(fs.readFileSync('3DWET/app/static/js/scientific_style.js','utf8'),e.context);
    e.context.window.ScientificStyle.set('A','test',{palette:'viridis'});
    let published;e.context.window.ScientificWorkspace={publish:(kind,meta)=>{published=meta;}};
    await e.context.render3DCloud('test',2,22,{caseKey:'A'});
    e.context.fetch=async()=>({json:async()=>({data:[[0,0]],horizontal:[0,100],horizontal_edges:[-50,50,150],
        depth_edges:[[4,8],[0,0]],min:0,max:0,units:'mg/L'})});
    await e.context.renderSpatialSection('test',2,'xz',0,{caseKey:'A',range:published.range});
    const marker=e.plots[0].traces[0].marker,mesh=e.plots[1].traces[0];
    assert.equal(mesh.cmin,marker.cmin);assert.equal(mesh.cmax,marker.cmax);
    assert.deepEqual(mesh.colorscale,marker.colorscale);assert.deepEqual(mesh.colorbar.ticktext,marker.colorbar.ticktext);
});
test('malformed inherited ranges are rejected instead of appearing as valid section scales',async()=>{
    const base={min:-5,max:5,palette:'lake',mode:'auto',colorscale:[[0,'rgb(0,0,0)'],[1,'rgb(255,255,255)']],tickvals:[-5,0,5],ticktext:['-5','0','5']};
    const section={data:[[0]],horizontal:[0],horizontal_edges:[-.5,.5],depth_edges:[[4],[0]],min:0,max:0};
    for(const patch of [{min:null},{max:-6},{palette:'rainbow'},{colorscale:[[0,'invalid'],[1,'invalid']]},{tickvals:[NaN]}]) {
        const e=env(section);await e.context.renderSpatialSection('test',0,'xz',0,{range:{...base,...patch}});
        assert.equal(e.plots.length,0,JSON.stringify(patch));assert.match(e.element._viz3dStatus.message,/色标|range|范围/i);
    }
});

test('custom positioned and discrete colormaps propagate unchanged from the main graph to its linked section',async()=>{
 for(const mapping of ['continuous','discrete']){
  const e=env();vm.runInContext(fs.readFileSync('3DWET/app/static/js/scientific_style.js','utf8'),e.context);
  e.context.window.ScientificStyle.set('A','test',{palette:'custom',stops:[[0,'#000000'],[.25,'#ff0000'],[1,'#ffffff']],reverse:true,mapping,classes:3});
  let meta;e.context.window.ScientificWorkspace={publish:(_,value)=>{meta=value;}};
  await e.context.render3DCloud('test',0,22,{caseKey:'A'});
  e.context.fetch=async()=>({json:async()=>({data:[[0,0]],horizontal:[0,100],horizontal_edges:[-50,50,150],depth_edges:[[4,8],[0,0]],min:0,max:0,units:'mg/L'})});
  await e.context.renderSpatialSection('test',0,'xz',0,{caseKey:'A',range:meta.range});
  assert.equal(e.plots.length,2,'a valid custom scheme must render its linked section');
  assert.deepEqual(e.plots[1].traces[0].colorscale,e.plots[0].traces[0].marker.colorscale);
 }
});

test('Plotly color normalization cannot mutate the published shared transfer function',async()=>{
 const e=env();vm.runInContext(fs.readFileSync('3DWET/app/static/js/scientific_style.js','utf8'),e.context);
 e.context.window.ScientificStyle.set('A','test',{palette:'custom',stops:[[0,'#000000'],[.25,'#ff0000'],[1,'#ffffff']]});
 const plot=e.context.Plotly.newPlot;
 e.context.Plotly.newPlot=async(...args)=>{
  await plot(...args);const scale=args[1][0].marker?.colorscale;
  if(scale)scale[0][1]='rgb(0, 0, 0)';
 };
 let meta;e.context.window.ScientificWorkspace={publish:(_,value)=>{meta=value;}};
 await e.context.render3DCloud('test',0,22,{caseKey:'A'});
 assert.equal(meta.range.colorscale[0][1],'rgb(0,0,0)','plot-library changes must stay inside its own trace');
 e.context.fetch=async()=>({json:async()=>({data:[[0,0]],horizontal:[0,100],horizontal_edges:[-50,50,150],depth_edges:[[4,8],[0,0]],min:0,max:0,units:'mg/L'})});
 await e.context.renderSpatialSection('test',0,'xz',0,{caseKey:'A',range:meta.range});
 assert.equal(e.plots.length,2);
});
