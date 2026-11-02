const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const {test}=require('node:test');
const source=fs.readFileSync('3DWET/app/static/js/viz3d.js','utf8');
const sampled={shape:[3,2,2],full_shape:[10,5,7],sampling_stride:[4,3,4],layer_indices:[0,4,9],total_layers:10,
    x:[0,4],y:[0,3],xc:[100,800],yc:[250,900],coordinate_mode:'projected',coordinate_units:'m',
    bottom:[[4,8],[6,10]],sigma:[-.95,-.55,-.05],data:[[[0,1],[2,3]],[[40,41],[42,43]],[[90,91],[92,93]]],
    min:0,max:93,units:'mg/L',long_name:'test'};
function withSampledTopology(payload) {
    if(!payload.full_shape || !payload.sampling_stride || !payload.x || !payload.y) return payload;
    const [_,rows,cols]=payload.full_shape,[ys,xs]=[payload.y,payload.x];
    const edges=(centres,indices,size)=>{
        const step=indices.length>1?(centres[1]-centres[0])/(indices[1]-indices[0]):1;
        return [centres[0]-step/2,...centres.slice(1).map((v,i)=>v-step/2),centres.at(-1)+(size-indices.at(-1)-.5)*step];
    };
    const ny=payload.yc.length,nx=payload.xc.length,status=Array.from({length:ny},()=>Array(nx).fill('wet'));
    payload.display_topology={contract:'sampled-wet-topology-v1',source_shape:[rows,cols],x_indices:xs,y_indices:ys,
        sampling_stride:payload.sampling_stride.slice(1),grid_hash:'sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        mask_cells_examined:rows*cols,x_edges:edges(payload.xc,xs,cols),y_edges:edges(payload.yc,ys,rows),
        cell_status:status,wet_mask:status.map(row=>row.map(()=>true)),land_mask:status.map(row=>row.map(()=>false)),
        wall_sides:status.map(row=>row.map(()=>[false,false,false,false])),mixed_or_unknown_cells:0};
    return payload;
}
function env(payload=sampled) {
    payload=withSampledTopology({...payload});
    const plots=[],urls=[],published=[],element={innerHTML:'',dataset:{}},status={textContent:'',dataset:{}};
    const Plotly={newPlot:async(el,traces,layout,config)=>{
        plots.push({traces,layout,config});element.data=traces;element._fullLayout={scene:{camera:layout.scene.camera}};
    }};
    const context=vm.createContext({console,URL,URLSearchParams,Plotly,window:{Plotly,ScientificWorkspace:{publish:(kind,data)=>published.push(data)}},
        state:{activeCase:'A',activeCasePath:'C:/A',caseRevision:1},
        document:{getElementById:id=>id==='viz3d-status'?status:element},
        fetch:async url=>{urls.push(url);return {json:async()=>payload};}});
    vm.runInContext(source,context);return {context,plots,urls,published,element,status};
}
test('sampled single layers select exact original ordinal and request it from the API',async()=>{
    const e=env();await e.context.render3DWaterBody('test',2,{level:4,ve:1});
    assert.match(e.urls[0],/[?&]level=4(?:&|$)/);
    const p=e.plots[0],field=p.traces.find(trace=>trace.meta?.scientificField===true);
    assert.ok(field.intensity.every(v=>v>=40&&v<=43),'original layer 4 maps to sampled array slot 1');
    assert.match(field.name,/层 4/);assert.match(field.hovertemplate,/层 4/);
    assert.match(p.layout.title.text,/层 4\/9/);assert.equal(e.published[0].level,4);
    assert.match(p.config.toImageButtonOptions.filename,/layer4/);
});
test('sampled stacks include only original ordinals up to the selected layer',async()=>{
    const e=env();await e.context.render3DWaterBody('test',0,{level:4,stack:true});
    const fields=e.plots[0].traces.filter(t=>t.meta?.scientificField===true);
    assert.equal(fields.length,1,'the stack is combined into one dynamic field trace');
    assert.deepEqual(Array.from(fields[0].meta.layerOrdinals),[0,4],
        'the combined field retains only sampled source ordinals through the requested original layer');
    assert.match(fields[0].name,/2层/);
    assert.match(e.plots[0].layout.title.text,/层 0–4\/9/);
});
test('published full detail retains sampling and transparency metadata outside compact plot titles',async()=>{
    const e=env();e.element.clientWidth=360;e.element.clientHeight=370;
    await e.context.render3DWaterBody('test',0,{level:4,stack:true,timeLabel:'2026-DOY288 12:00:00'});
    const meta=e.published[0];assert.equal(typeof meta.detail,'string');
    assert.match(meta.detail,/2026-DOY288 12:00:00/);assert.match(meta.detail,/10×5×7/);assert.match(meta.detail,/4×3×4/);
    assert.match(meta.detail,/混色/);assert.equal(e.plots[0].layout.title.text.split('<br>').length,1);
});
test('an unavailable original ordinal is an explicit error instead of a nearby sampled layer',async()=>{
    const e=env();await e.context.render3DWaterBody('test',0,{level:5});
    assert.equal(e.plots.length,0);assert.match(e.status.textContent,/5/);
});
test('default waterbody layer is the actual original surface ordinal',async()=>{
    const e=env();await e.context.render3DWaterBody('test',0);
    assert.equal(e.published[0].level,9);assert.match(e.plots[0].traces.find(trace=>trace.meta?.scientificField===true).name,/层 9/);
});
test('all physical volume modes disclose index coordinates and sampled grid resolution',async()=>{
    const payload={...sampled,coordinate_mode:'index',coordinate_units:'index',xc:[0,4],yc:[0,3]};
    for(const mode of ['water','cloud','iso']) {
        const e=env(payload);
        if(mode==='water') await e.context.render3DWaterBody('test',0,{level:4,ve:1});
        else if(mode==='cloud') await e.context.render3DCloud('test',0,22,{ve:1});
        else await e.context.render3DSurface('test',0,18,{ve:1});
        const p=e.plots[0];
        assert.match(p.layout.scene.xaxis.title,/index|索引/);assert.doesNotMatch(p.layout.scene.xaxis.title,/\(m\)/);
        assert.match(p.layout.scene.yaxis.title,/index|索引/);
        for(const trace of p.traces.filter(t=>t.hovertemplate&&/X |Y |网格|索引/.test(t.hovertemplate)))
            assert.doesNotMatch(trace.hovertemplate,/%\{[xy][^}]*\} m/);
        assert.match(e.status.textContent,/10×5×7/);assert.match(e.status.textContent,/4×3×4/);
        assert.match(p.layout.title.text,/采样|sampling/i);
        const shore=p.traces.find(t=>t.name?.includes('岸线'));
        if(shore) assert.match(shore.name,/采样|sampling/i,'coarse wet boundary is not advertised as a full original shoreline');
    }
});
test('bathymetry preview respects explicit index metadata and original resolution',async()=>{
    const e=env({depth:[[4,8],[6,10]],xc:[0,3],yc:[0,3],coordinate_mode:'index',coordinate_units:'index',
        nx:2,ny:2,nx_full:5,ny_full:5,stride:3,dx:200,dy:300});
    await e.context.renderBathymetry3D({ve:1});const p=e.plots[0];
    assert.match(p.layout.scene.xaxis.title,/index|索引/);
    assert.ok(!p.traces.some(t=>t.hovertemplate&&/%\{[xy][^}]*\} m/.test(t.hovertemplate)),
        'a hidden-bed static preview must not label grid indices as metres in any hover text');
    assert.match(e.status.textContent,/5×5/);assert.match(e.status.textContent,/3×3/);
});
test('explicit horizontal units are preserved in axes and hover',async()=>{
    const e=env({...sampled,coordinate_units:'km'});await e.context.render3DCloud('test',0);
    assert.match(e.plots[0].layout.scene.xaxis.title,/\(km\)/);
    assert.match(e.plots[0].traces[0].hovertemplate,/%\{x[^}]*\} km/);
});
test('short landscape plot keeps a usable scene instead of exhausting its height with title and legend',async()=>{
    const e=env();e.element.clientWidth=620;e.element.clientHeight=135;
    await e.context.render3DWaterBody('test',0,{level:4,ve:1,timeLabel:'2026-DOY288 12:00:00'});
    const p=e.plots[0];
    assert.ok(p.layout.margin.t+p.layout.margin.b<=75,'a 135px plot needs at least 60px of actual scene');
    assert.equal(p.layout.title.text.split('<br>').length,1);
    assert.equal(p.layout.showlegend,false,'the side rail keeps the quantitative legend visible');
    assert.match(e.status.textContent,/2026-DOY288 12:00:00/,'full date and sampling remain in status outside the compact plot');
});
test('scientific 3D resize restores full layout and never mutates the saved camera',async()=>{
    const e=env(),updates=[];e.element.clientWidth=620;e.element.clientHeight=135;
    e.context.Plotly.relayout=async(el,update)=>updates.push(update);
    await e.context.render3DWaterBody('test',0,{level:4,ve:1});
    assert.equal(typeof e.context.window.resizeScientific3D,'function');
    e.element.clientHeight=500;
    assert.equal(await e.context.window.resizeScientific3D(e.element),true);
    assert.ok(updates[0].title.text.includes('<br>'));assert.equal(updates[0].showlegend,true);
    assert.equal(updates[0].height,500);assert.ok(!Object.keys(updates[0]).some(key=>key.includes('camera')));
    e.element.clientHeight=0;
    assert.equal(await e.context.window.resizeScientific3D(e.element),false);assert.equal(updates.length,1);
    e.element.clientHeight=135;e.context.Plotly.relayout=async()=>{throw Error('resize error');};
    assert.equal(await e.context.window.resizeScientific3D(e.element),false,'resize rejections are handled, not left as unhandled promises');
});
const section={axis:'xz',index:3,time:0,name:'test',coordinate_mode:'projected',coordinate_units:'m',
    horizontal:[100,260,370,550,800,900,1000],horizontal_edges:[20,180,315,460,675,850,950,1050],
    wet:[true,true,false,true,true,false,true],grid_shape:[5,7]};
function indicatorEnv(payload=sampled) {
    const e=env(payload),mutations=[];
    const Plotly=e.context.Plotly;
    Plotly.addTraces=async(el,trace)=>{mutations.push('add');el.data.push(trace);};
    Plotly.deleteTraces=async(el,index)=>{mutations.push('delete');el.data.splice(index,1);};
    Plotly.react=async(el,traces,layout,config)=>{
        e.plots.push({traces,layout,config});el.data=traces;el._fullLayout={scene:{camera:layout.scene.camera}};
    };
    return {...e,mutations};
}
test('the linked section legend follows the selected interface language',async()=>{
    const e=indicatorEnv();e.context.window.StudioI18n={t:value=>String(value).replace('剖面位置','Section position')};
    await e.context.render3DWaterBody('test',0,{level:4,ve:1});
    await e.context.window.set3DSectionIndicator('xz',3,section);
    assert.match(e.element.data.at(-1).name,/Section position/);
    assert.doesNotMatch(e.element.data.at(-1).name,/[\u3400-\u9fff]/);
});
test('section location uses original sampled row index and keeps dry gaps without changing camera',async()=>{
    const e=indicatorEnv();await e.context.render3DWaterBody('test',0,{level:4,ve:1});
    const camera=e.element._fullLayout.scene.camera,base=e.element.data.length;
    assert.equal(typeof e.context.window.set3DSectionIndicator,'function');
    assert.equal(await e.context.window.set3DSectionIndicator('xz',3,section),true);
    assert.equal(e.element.data.length,base+1);
    const line=e.element.data.at(-1);assert.equal(line.type,'scatter3d');assert.equal(line.mode,'lines');
    assert.ok(line.y.filter(v=>v!==null).every(v=>v===900),'row 3 uses yc at sample slot 1, not slot 3');
    assert.deepEqual(Array.from(line.x),[20,180,null,180,315,null,460,675,null,675,850,null,950,1050,null]);
    assert.ok(line.z.every(v=>v===null||v===0),'indicator is on the actual water surface');
    assert.deepEqual(e.element._fullLayout.scene.camera,camera);
    assert.equal(await e.context.window.set3DSectionIndicator('xz',3,section),true);
    assert.equal(e.element.data.length,base+1,'replace one indicator instead of accumulating traces');
});
test('an unsampled section requires its exact perpendicular coordinate instead of interpolation',async()=>{
    const e=indicatorEnv();await e.context.render3DWaterBody('test',0,{level:4});
    const base=e.element.data.length;
    assert.equal(typeof e.context.window.set3DSectionIndicator,'function');
    assert.equal(await e.context.window.set3DSectionIndicator('xz',2,{...section,index:2}),false);
    assert.equal(e.element.data.length,base);
    assert.equal(await e.context.window.set3DSectionIndicator('xz',2,{...section,index:2,fixed_coordinate:775,fixed_coordinate_units:'m'}),true);
    assert.ok(e.element.data.at(-1).y.filter(v=>v!==null).every(v=>v===775));
});
test('index main views map linked sections by original indices and reject incompatible physical units',async()=>{
    const e=indicatorEnv({...sampled,coordinate_mode:'index',coordinate_units:'index',xc:[0,4],yc:[0,3]});
    await e.context.render3DCloud('test',0);
    assert.equal(typeof e.context.window.set3DSectionIndicator,'function');
    assert.equal(await e.context.window.set3DSectionIndicator('xz',2,{...section,index:2}),true);
    const line=e.element.data.at(-1);assert.ok(line.y.filter(v=>v!==null).every(v=>v===2));
    assert.deepEqual(Array.from(line.x),[-.5,.5,null,.5,1.5,null,2.5,3.5,null,3.5,4.5,null,5.5,6.5,null]);
    assert.match(line.hovertemplate,/index|索引/);
    const m=indicatorEnv();await m.context.render3DCloud('test',0);
    assert.equal(await m.context.window.set3DSectionIndicator('xz',3,{...section,coordinate_units:'km'}),false);
});
test('section indicators stay with the explicitly stale graph until its replacement and reject obsolete selections',async()=>{
    const e=indicatorEnv();await e.context.render3DWaterBody('test',0,{level:4});
    assert.equal(typeof e.context.window.set3DSectionIndicator,'function');
    await e.context.window.set3DSectionIndicator('xz',3,section);
    const deferred={};deferred.promise=new Promise(resolve=>deferred.resolve=resolve);
    e.context.fetch=()=>deferred.promise;
    const pending=e.context.render3DCloud('test',1);await Promise.resolve();
    assert.ok(e.element.data.some(t=>t.meta?.section_indicator),'the stale graph keeps its matching old section until replacement');
    assert.equal(await e.context.window.set3DSectionIndicator('xz',3,section),false);
    deferred.resolve({json:async()=>sampled});await pending;
    assert.ok(!e.element.data.some(t=>t.meta?.section_indicator),'the replacement main graph removes the old section');
    e.context.state.caseRevision++;
    assert.equal(await e.context.window.set3DSectionIndicator('xz',3,section),false);
    e.context.fetch=async()=>({json:async()=>({...sampled,data:sampled.data[0]})});
    await e.context.render2DAs3DSurface('test',0,0);
    assert.equal(await e.context.window.set3DSectionIndicator('xz',3,section),false);
});

test('manual section replacement retains the live gesture camera instead of the last data-draw camera',async()=>{
    const e=indicatorEnv();await e.context.render3DWaterBody('test',0,{level:4,ve:1});
    await e.context.window.set3DSectionIndicator('xz',3,section);
    const camera={eye:{x:.8,y:-.4,z:2.4},center:{x:.2,y:-.1,z:.05},up:{x:0,y:0,z:1},projection:{type:'orthographic'}};
    e.element.layout=e.plots[0].layout;
    e.element._fullLayout.scene._scene={getCamera:()=>camera};
    e.context.Plotly.deleteTraces=async(el,index)=>{el.data.splice(index,1);el._fullLayout.scene.camera=el.layout.scene.camera;};
    e.context.Plotly.addTraces=async(el,trace)=>{el.data.push(trace);el._fullLayout.scene.camera=el.layout.scene.camera;};
    await e.context.window.set3DSectionIndicator('xz',3,section);
    assert.deepEqual(JSON.parse(JSON.stringify(e.element._fullLayout.scene.camera)),camera);
});

test('triangular display adds low-key facet relief and crisp edges without changing model values',async()=>{
    const triangles=env(),continuous=env();
    await triangles.context.render3DWaterBody('test',0,{level:4,ve:1,meshMode:'triangles'});
    await continuous.context.render3DWaterBody('test',0,{level:4,ve:1,meshMode:'continuous'});
    const field=triangles.plots[0].traces.find(trace=>trace.meta?.scientificField);
    const reference=continuous.plots[0].traces.find(trace=>trace.meta?.scientificField);
    const network=triangles.plots[0].traces.find(trace=>trace.meta?.networkMode==='triangles');
    assert.ok(field&&reference&&network,'the selected scalar and its display network are rendered');
    assert.equal(field.flatshading,true,'triangle facets use flat normals for readable relief');
    assert.deepEqual(JSON.parse(JSON.stringify(field.lighting)),{ambient:.48,diffuse:.52,specular:.08,roughness:.82});
    assert.deepEqual(JSON.parse(JSON.stringify(field.lightposition)),{x:1000,y:-1200,z:1800},
        'a fixed display-only light makes facet contrast reproducible');
    for(const property of ['x','y','z','i','j','k','customdata'])
        assert.deepEqual(JSON.parse(JSON.stringify(field[property])),JSON.parse(JSON.stringify(reference[property])),
            `${property} preserves the same wet-cell geometry and original hover values`);
    assert.ok(field.intensity.every(Number.isFinite),'triangle rendering retains finite scalar samples');
    assert.equal(field.cmin,reference.cmin);assert.equal(field.cmax,reference.cmax);
    assert.equal(network.line.width,2.3,'triangle boundaries stay crisp without dominating the field');
    assert.equal(network.meta.displayLiftFraction,.025,'edge separation is explicitly display-only');
    assert.ok(!triangles.plots[0].traces.some(trace=>trace.type==='scatter3d'&&trace.mode==='markers'),
        'network nodes remain off by default');
    assert.ok(triangles.plots[0].traces.some(trace=>trace.meta?.shoreline),
        'the basin silhouette stays distinct from the field mesh');
    assert.ok(triangles.plots[0].layout.scene.camera.eye.z>.5,
        'the initial camera reveals basin relief instead of starting at a flat plan view');
});

test('triangular display adds inter-layer links only for a supported multi-layer stack',async()=>{
    const single=env(),stack=env();
    await single.context.render3DWaterBody('test',0,{level:4,ve:1,meshMode:'triangles'});
    await stack.context.render3DWaterBody('test',0,{level:4,stack:true,ve:1,meshMode:'triangles'});
    assert.ok(!single.plots[0].traces.some(trace=>trace.meta?.layerLinks),
        'a single selected layer has no fabricated vertical links');
    const links=stack.plots[0].traces.find(trace=>trace.meta?.layerLinks);
    assert.ok(links&&links.x.length>0,'the supplied sigma layers support visible inter-layer cues');
    assert.equal(links.meta.displayOnly,true,'inter-layer links are declared display aids');
    assert.equal(links.meta.displayLift,.025*Math.max(...sampled.bottom.flat())*1,
        'the same disclosed small display lift prevents line/surface flicker');
});
