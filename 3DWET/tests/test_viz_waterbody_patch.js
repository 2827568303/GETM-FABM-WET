// Exercise waterbody frame updates through the production renderer and a
// small Plotly boundary. Dynamic depth must patch when the wet topology and
// every trace shape stay compatible; changed topology must use react.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const {test}=require('node:test');
const source=fs.readFileSync('3DWET/app/static/js/viz3d.js','utf8');

function environment(search=''){
    const graph={innerHTML:'',dataset:{},clientWidth:800,clientHeight:600,
        _fullLayout:null,data:[],layout:null,on(){}};
    const status={dataset:{},textContent:''};
    const elements={'viz3d-plotly':graph,'viz3d-status':status};
    const parent={children:[],insertBefore(element,reference){
        element.parentNode=this;const at=reference?this.children.indexOf(reference):-1;
        this.children.splice(at<0?this.children.length:at,0,element);elements[element.id]=element;
    }};
    graph.parentNode=parent;parent.children.push(graph);
    const calls={react:0,newPlot:0,restyle:[],relayout:[],update:[]};
    const applyData=(element,update,indices)=>{
        for(const [property,perTrace] of Object.entries(update)) indices.forEach((index,n)=>{
            const raw=perTrace[n];if(raw===undefined)return;
            const keys=property.split('.');let target=element.data[index];
            for(const key of keys.slice(0,-1))target=target[key] ||= {};
            // Plotly restyle/update payloads have one outer element per
            // selected trace; that element is the complete array attribute.
            target[keys.at(-1)]=structuredClone(raw);
        });
    };
    const applyLayout=(element,update)=>{
        for(const [property,value] of Object.entries(update)){
            const keys=property.split('.');let target=element.layout;
            for(const key of keys.slice(0,-1))target=target[key] ||= {};
            target[keys.at(-1)]=structuredClone(value);
        }
        element._fullLayout=structuredClone(element.layout);
    };
    const Plotly={
        newPlot:async(element,traces,layout)=>{
            calls.newPlot++;
            element.data=structuredClone(traces);element._fullData=structuredClone(traces);element.layout=structuredClone(layout);
            element._fullLayout=structuredClone(layout);
        },
        react:async(element,traces,layout)=>{
            calls.react++;
            element.data=structuredClone(traces);element._fullData=structuredClone(traces);element.layout=structuredClone(layout);
            element._fullLayout=structuredClone(layout);
        },
        restyle:async(element,update,indices)=>{
            calls.restyle.push({update,indices:[...indices]});
            applyData(element,update,indices);
        },
        relayout:async(element,update)=>{
            calls.relayout.push(update);
            applyLayout(element,update);
        },
        update:async(element,dataUpdate,layoutUpdate,indices)=>{
            calls.update.push({dataUpdate,layoutUpdate,indices:[...indices]});
            if(element.failNextUpdate){element.failNextUpdate=false;throw new Error('simulated Plotly mesh update rejection');}
            applyData(element,dataUpdate,indices);applyLayout(element,layoutUpdate);
        },
    };
    const state={caseRevision:1,activeCase:'Lake A',activeCasePath:'C:/cases/A'};
    const context=vm.createContext({console,Plotly,state,URL,URLSearchParams,structuredClone,
        window:{Plotly,location:{search},ScientificWorkspace:{publish(){}}},
        document:{getElementById:id=>elements[id] || null,createElement:tag=>({tagName:tag.toUpperCase(),children:[],dataset:{},style:{},
            setAttribute(name,value){this[name]=value;},append(...children){for(const child of children)this.appendChild(child);},
            appendChild(child){child.parentNode=this;this.children.push(child);if(child.id)elements[child.id]=child;return child;}})},
        fetch:async url=>({json:async()=>frame(Number(new URL(url,'http://localhost').searchParams.get('time')))}),
    });
    vm.runInContext(source,context);
    // This suite inspects bed traces and bed-only diagnostic modes. Opt in at
    // the fixture boundary; separate lake display tests verify production's
    // default hidden-bed contract.
    const renderWaterbody=context.render3DWaterBody;
    context.render3DWaterBody=(variable,time,options={})=>renderWaterbody(variable,time,{showBedSurface:true,...options});
    const renderBathymetry=context.renderBathymetry3D;
    context.renderBathymetry3D=(options={})=>renderBathymetry({...options,showBedSurface:true});
    return {context,graph,calls,elements,parent,setFetch(payload){context.fetch=async()=>({json:async()=>payload});}};
}

function frame(time,mask=[true,true,true,true]){
    const depths=time===0?[[10,10],[10,10]]:[[12,12],[12,12]];
    const bottom=depths.map((row,j)=>row.map((value,i)=>mask[j*2+i]?value:0));
    return {shape:[1,2,2],xc:[0,100],yc:[0,100],bottom,water_depth:bottom,
        sigma:[-.5],layer_indices:[0],total_layers:1,
        data:[[[time===0?2:8,time===0?3:9],[time===0?4:10,time===0?5:11]]],
        min:time===0?2:8,max:time===0?5:11,units:'mg/L',long_name:'Test scalar'};
}

test('normal render exposes an accessible read-only trace audit only when URL explicitly enables it',async()=>{
    const disabled=environment();
    await disabled.context.render3DWaterBody('test',0,{level:0,ve:1});
    assert.equal(disabled.elements['viz3d-trace-audit'],undefined,'ordinary pages do not add the diagnostic panel');

    const enabled=environment('?viz3d-trace-audit=1');
    await enabled.context.render3DWaterBody('test',0,{level:0,ve:1});
    const panel=enabled.elements['viz3d-trace-audit'];
    assert.ok(panel,'the production render path adds the opt-in audit panel');
    assert.equal(panel.role,'region');
    assert.match(panel.children[0].textContent,/trace audit/i);
    const audit=JSON.parse(panel.children[1].textContent);
    const bed=audit.find(trace=>trace.name==='湖盆水深');
    assert.equal(bed.type,'mesh3d');
    assert.deepEqual(bed.arrays.x,{length:16,min:-50,max:150,nonFinite:0});
    assert.equal(bed.intensitymode,'vertex');
});

test('extreme vertical exaggeration suppresses oversized shoreline side walls',async()=>{
    const e=environment();
    await e.context.render3DWaterBody('test',0,{level:0,ve:166});
    assert.ok(!e.graph.data.some(trace=>trace.name==='湿网格边界剖面'),
        'the 166x display exaggeration must not fill the view with enlarged side panels');
});

test('extreme vertical exaggeration retains a separately depth-colored bed and the scientific field',async()=>{
    const e=environment();
    await e.context.render3DWaterBody('test',0,{level:0,ve:166.5});
    const bed=e.graph.data.find(trace=>trace.meta?.waterbodyFrame==='bed');
    assert.ok(bed,'a high-VE dynamic overlay keeps the basin bed visible');
    assert.deepEqual(JSON.parse(JSON.stringify(bed.colorscale)),[
        [0,'#75e3d7'],[0.15,'#58d2e2'],[0.35,'#39b5e7'],[0.6,'#2b91df'],[0.8,'#236bd2'],[1,'#173fbd']
    ],
        'the bed uses the dedicated depth palette');
    assert.equal(bed.intensitymode,'vertex');
    assert.ok(bed.intensity.length>0&&bed.intensity.every(value=>value===10),
        'bed intensity contains the bathymetry depth values');
    assert.equal(bed.cmin,0);
    assert.equal(bed.cmax,10,'bed colors use bathymetry range, not the field range');
    assert.equal(bed.showscale,false,'the field colorbar must not be presented as bed depth');
    assert.ok(bed.hovertemplate.includes('床面底深'),'bed hover text identifies its depth value');
    assert.ok(e.graph.data.some(trace=>trace.meta?.scientificField),
        'the selected scientific water field remains visible');
    const status=e.context.document.getElementById('viz3d-status').textContent;
    assert.ok(status.includes('床面按湖底深度（m）着色'),
        'status explains the high-VE bed color meaning');
    assert.ok(status.includes('与所选变量色阶分离'),
        'status separates bed depth from the scientific variable color scale');
    assert.ok(status.includes('黑片成因尚未确认'),
        'status preserves the unresolved cause');
});

test('crossing the high-VE bed style threshold rebuilds the static floor trace',async()=>{
    const e=environment();
    await e.context.render3DWaterBody('test',0,{level:0,ve:50});
    const initialBed=e.graph.data.find(trace=>trace.meta?.waterbodyFrame==='bed');
    assert.ok(initialBed,'the lower-VE overlay starts with its bed trace');
    assert.deepEqual(JSON.parse(JSON.stringify(initialBed.colorscale)),[[0,'#c5cdd1'],[1,'#c5cdd1']],
        'the lower-VE bed keeps a fixed neutral colorscale');
    assert.ok(Array.isArray(initialBed.intensity),'the neutral floor keeps its bathymetry intensity values');

    await e.context.render3DWaterBody('test',0,{level:0,ve:166.5});

    assert.equal(e.calls.react,1,'a bed-style mode change must rebuild the static floor trace');
    const bed=e.graph.data.find(trace=>trace.meta?.waterbodyFrame==='bed');
    assert.equal(bed.intensitymode,'vertex');
    assert.ok(Array.isArray(bed.intensity),'the high-VE floor receives its separate depth style');
});

test('ordinary low-VE overlays render a neutral bed through a fixed colorscale',async()=>{
    const e=environment();
    await e.context.render3DWaterBody('test',0,{level:0,ve:50});
    const bed=e.graph.data.find(trace=>trace.meta?.waterbodyFrame==='bed');
    assert.ok(bed,'the ordinary dynamic overlay retains its bed trace');
    assert.equal(bed.color,undefined,'the production bed does not use Plotly direct-color encoding');
    assert.deepEqual(JSON.parse(JSON.stringify(bed.colorscale)),[[0,'#c5cdd1'],[1,'#c5cdd1']],
        'the ordinary neutral bed is encoded by a uniform gray colorscale');
    assert.equal(bed.intensitymode,'vertex');
    assert.ok(Array.isArray(bed.intensity)&&bed.intensity.length>0,
        'the bed retains its vertex bathymetry values');
    assert.deepEqual(bed.lighting,{ambient:1,diffuse:0,specular:0,roughness:1},
        'the neutral style preserves the current lighting configuration');
});

test('force-bed-neutral diagnostic changes only the bed color style',async()=>{
    const depthView=environment(),neutralView=environment();
    depthView.context.window.location={search:'?viz3d-diagnostic=force-bed'};
    neutralView.context.window.location={search:'?viz3d-diagnostic=force-bed-neutral'};
    await depthView.context.render3DWaterBody('test',0,{level:0,ve:166.5});
    await neutralView.context.render3DWaterBody('test',0,{level:0,ve:166.5});

    const depthBed=depthView.graph.data.find(trace=>trace.meta?.waterbodyFrame==='bed');
    const neutralBed=neutralView.graph.data.find(trace=>trace.meta?.waterbodyFrame==='bed');
    assert.ok(depthBed&&neutralBed,'both diagnostic views retain the high-VE bed');
    assert.equal(depthBed.color,undefined,'the control uses the existing depth colorscale');
    assert.equal(neutralBed.color,undefined,'neutral bed encoding avoids Plotly direct color');
    assert.deepEqual(JSON.parse(JSON.stringify(neutralBed.colorscale)),[[0,'#c5cdd1'],[1,'#c5cdd1']]);
    assert.equal(neutralBed.intensitymode,'vertex');
    assert.deepEqual(neutralBed.intensity,depthBed.intensity,'neutral bed retains its depth intensity data');
    for(const key of ['x','y','z','i','j','k','customdata','hovertemplate'])
        assert.deepEqual(neutralBed[key],depthBed[key],`bed ${key} stays identical between color modes`);
    const depthField=depthView.graph.data.find(trace=>trace.meta?.scientificField);
    const neutralField=neutralView.graph.data.find(trace=>trace.meta?.scientificField);
    assert.ok(depthField&&neutralField,'both views retain the scientific field trace');
    for(const key of ['x','y','z','i','j','k','intensity','customdata'])
        assert.deepEqual(neutralField[key],depthField[key],`field ${key} stays identical between color modes`);
});

test('force-bed-neutral diagnostic also toggles static high-VE bed colors only',async()=>{
    const normal=environment(),diagnostic=environment();
    const grid={...frame(0),depth:[[10,10],[10,10]]};
    normal.setFetch(grid);diagnostic.setFetch(grid);
    diagnostic.context.window.location={search:'?viz3d-diagnostic=force-bed-neutral'};
    await normal.context.renderBathymetry3D({ve:166.5});
    await diagnostic.context.renderBathymetry3D({ve:166.5});

    const normalBed=normal.graph.data.find(trace=>trace.meta?.waterbodyFrame==='bed');
    const neutralBed=diagnostic.graph.data.find(trace=>trace.meta?.waterbodyFrame==='bed');
    assert.ok(normalBed&&neutralBed,'both static views retain the bed trace');
    assert.ok(Array.isArray(normalBed.colorscale),'normal static bathymetry keeps its depth colorscale');
    assert.equal(neutralBed.color,undefined,'the explicit neutral diagnostic avoids direct mesh3d color');
    assert.deepEqual(JSON.parse(JSON.stringify(neutralBed.colorscale)),[[0,'#c5cdd1'],[1,'#c5cdd1']]);
    assert.equal(neutralBed.intensitymode,'vertex');
    assert.deepEqual(neutralBed.intensity,normalBed.intensity,'neutral style retains depth intensity');
    for(const key of ['x','y','z','i','j','k','customdata','hovertemplate'])
        assert.deepEqual(neutralBed[key],normalBed[key],`static bed ${key} remains identical`);
    assert.ok(!diagnostic.graph.data.some(trace=>trace.meta?.scientificField),
        'static bathymetry does not invent a scientific water-field trace');
});

test('fixed neutral colorscale diagnostic preserves high-VE bed and field data',async()=>{
    const normal=environment(),direct=environment(),scale=environment();
    direct.context.window.location={search:'?viz3d-diagnostic=force-bed-neutral'};
    scale.context.window.location={search:'?viz3d-diagnostic=force-bed-neutral-scale'};
    await normal.context.render3DWaterBody('test',0,{level:0,ve:166.5});
    await direct.context.render3DWaterBody('test',0,{level:0,ve:166.5});
    await scale.context.render3DWaterBody('test',0,{level:0,ve:166.5});

    const bed=normal.graph.data.find(trace=>trace.meta?.waterbodyFrame==='bed');
    const directBed=direct.graph.data.find(trace=>trace.meta?.waterbodyFrame==='bed');
    const scaleBed=scale.graph.data.find(trace=>trace.meta?.waterbodyFrame==='bed');
    assert.ok(bed&&directBed&&scaleBed,'all three high-VE views retain the bed');
    assert.equal(directBed.color,undefined,'neutral diagnostic avoids Plotly direct color');
    assert.deepEqual(JSON.parse(JSON.stringify(directBed.colorscale)),[[0,'#c5cdd1'],[1,'#c5cdd1']]);
    assert.equal(scaleBed.color,undefined,'uniform-scale diagnostic does not use the direct color attribute');
    assert.deepEqual(JSON.parse(JSON.stringify(scaleBed.colorscale)),[[0,'#c5cdd1'],[1,'#c5cdd1']]);
    assert.deepEqual(scaleBed.intensity,bed.intensity,'the scale mode retains the bed depth intensity data');
    assert.deepEqual(directBed.intensity,bed.intensity,'neutral mode retains the bed depth intensity data');
    assert.equal(directBed.intensitymode,'vertex');
    for(const key of ['x','y','z','i','j','k','customdata','hovertemplate']) {
        assert.deepEqual(scaleBed[key],bed[key],`scale-mode bed ${key} matches depth-colored default`);
        assert.deepEqual(scaleBed[key],directBed[key],`scale-mode bed ${key} matches neutral-color diagnostic`);
    }
    const defaultField=normal.graph.data.find(trace=>trace.meta?.scientificField);
    const directField=direct.graph.data.find(trace=>trace.meta?.scientificField);
    const scaleField=scale.graph.data.find(trace=>trace.meta?.scientificField);
    assert.deepEqual(scaleField,defaultField,'the field trace is unchanged by the color diagnostic');
    assert.deepEqual(scaleField,directField,'the field trace is unchanged from the direct-neutral control');
});

test('dynamic wet-grid boundary walls use neutral lighting under vertical exaggeration',async()=>{
    const e=environment();
    await e.context.render3DWaterBody('test',0,{level:0,ve:40});
    const wall=e.graph.data.find(trace=>trace.name==='湿网格边界剖面');
    assert.ok(wall,'waterbody rendering retains the dynamic wet-grid boundary wall');
    assert.ok(wall.lighting,'boundary walls must explicitly set neutral lighting');
    assert.equal(wall.lighting.ambient,1);
    assert.equal(wall.lighting.diffuse,0);
    assert.equal(wall.lighting.specular,0);
    assert.equal(wall.lighting.roughness,1);
});

test('skip-field diagnostic hides variable and missing traces while retaining the rest',async()=>{
    const e=environment(),payload=frame(0);
    payload.data[0][0][0]=null;
    e.setFetch(payload);
    e.context.window.location={search:'?viz3d-diagnostic=skip-field'};
    await e.context.render3DWaterBody('test',0,{level:0,ve:40});
    assert.ok(e.graph.data.some(trace=>trace.name==='湖盆水深'));
    assert.ok(e.graph.data.some(trace=>trace.name==='湿网格边界剖面'));
    assert.ok(!e.graph.data.some(trace=>['field','missing'].includes(trace.meta?.waterbodyFrame)));
});

test('skip-bed diagnostic hides only the lake-floor trace',async()=>{
    const e=environment();
    e.context.window.location={search:'?viz3d-diagnostic=skip-bed'};
    await e.context.render3DWaterBody('test',0,{level:0,ve:40});
    assert.ok(!e.graph.data.some(trace=>trace.meta?.waterbodyFrame==='bed'));
    assert.ok(e.graph.data.some(trace=>trace.name==='湿网格边界剖面'));
    assert.ok(e.graph.data.some(trace=>trace.meta?.scientificField));
});

test('first waterbody draw applies compact margins at the 491x269 viewport',async()=>{
    const e=environment();
    e.graph.clientWidth=491;e.graph.clientHeight=269;
    await e.context.render3DWaterBody('test',23,{level:0,ve:1});

    assert.equal(e.calls.newPlot,1,'the initial frame uses Plotly.newPlot');
    assert.equal(e.graph.layout.showlegend,false);
    assert.deepEqual(JSON.parse(JSON.stringify(e.graph.layout.margin)),{l:32,r:112,t:60,b:28});
});

test('water-depth and field changes with stable wet topology patch dynamically without Plotly.react',async()=>{
    const e=environment();
    await e.context.render3DWaterBody('test',0,{level:0,ve:1});
    const initialFloor=e.graph.data.find(trace=>trace.name==='湖盆水深');
    const initialField=e.graph.data.find(trace=>trace.meta?.scientificField);
    const initialFloorZ=structuredClone(initialFloor.z);
    const initialFieldIntensity=structuredClone(initialField.intensity);
    const initialCamera={eye:{x:2,y:-2,z:1},center:{x:0,y:0,z:0},up:{x:0,y:0,z:1},projection:{type:'orthographic'}};
    e.graph._fullLayout.scene.camera=structuredClone(initialCamera);
    e.graph.layout.scene.camera=structuredClone(initialCamera);
    const baseAspect=structuredClone(e.graph.layout.scene.aspectratio);
    const zoomedAspect=Object.fromEntries(['x','y','z'].map(axis=>[axis,baseAspect[axis]*1.5]));
    e.graph._fullLayout.scene.aspectratio=structuredClone(zoomedAspect);
    e.graph.layout.scene.aspectratio=structuredClone(zoomedAspect);

    await e.context.render3DWaterBody('test',1,{level:0,ve:1});

    assert.equal(e.calls.react,0,'the second frame must not rebuild the graph');
    assert.equal(e.calls.newPlot,1,'the graph is initially created once');
    assert.equal(e.calls.update.length,1,'dynamic traces and layout are submitted in one Plotly update');
    assert.equal(e.calls.restyle.length,0,'the update is not split across per-role redraws');
    const fieldIndex=e.graph.data.findIndex(trace=>trace.meta?.scientificField);
    const field=e.graph.data.find(trace=>trace.meta?.scientificField);
    const fieldPatchPosition=e.calls.update[0].indices.indexOf(fieldIndex);
    assert.notEqual(fieldPatchPosition,-1,'the current scientific field is part of the dynamic update');
    assert.ok(e.calls.update[0].dataUpdate.x[fieldPatchPosition],
        'current-frame wet field coordinates are patched with scalar membership');
    assert.ok(e.calls.update[0].dataUpdate.i[fieldPatchPosition],
        'current-frame field connectivity is patched with scalar membership');
    const patchedIndices=new Set(e.calls.update.flatMap(call=>call.indices));
    for(const name of ['湖盆水深','湿网格边界剖面','等深线'])
        assert.ok(patchedIndices.has(e.graph.data.findIndex(trace=>trace.name===name)),`${name} follows frame depth`);
    assert.equal(patchedIndices.has(e.graph.data.findIndex(trace=>trace.name==='水面')),false,
        'the static water-surface trace is not sent through restyle');
    assert.equal(patchedIndices.has(e.graph.data.findIndex(trace=>trace.name==='湿网格岸线（代理，未验证）')),false,
        'stable shoreline topology is not sent through restyle');
    const floor=e.graph.data.find(trace=>trace.name==='湖盆水深');
    assert.notDeepEqual(floor.z,initialFloorZ,'the displayed lake bed follows the current water-depth frame');
    assert.notDeepEqual(field.intensity,initialFieldIntensity,'the scientific field follows the current frame');
    assert.equal(field.cmin,8);assert.equal(field.cmax,11,'the current-frame auto range is retained');
    assert.equal(field.customdata[0][0],6,'hover depth follows the current physical water-depth frame');
    assert.equal(field.customdata[0][6],8,'hover customdata reports the current cell-center scalar');
    assert.equal(e.graph.layout.scene.camera.eye.x,2,'incremental updates preserve the live camera');
    const patchedAspect=e.graph.layout.scene.aspectratio,updatedBase=e.graph._viz3dAspectRatioState.baseline;
    for(const axis of ['x','y','z'])assert.ok(Math.abs(patchedAspect[axis]/updatedBase[axis]-1.5)<1e-9,
        `frame updates must preserve the common wheel zoom scale on ${axis} while updating physical aspect`);
});

test('playback frame patches replay the just-captured live orbit camera through Plotly.update',async()=>{
    const e=environment();
    await e.context.render3DWaterBody('test',0,{level:0,ve:1});
    const userCamera={eye:{x:3.2,y:-.7,z:1.8},center:{x:.2,y:-.1,z:0},
        up:{x:0,y:0,z:1},projection:{type:'orthographic'}};

    // Simulate the camera changed by active orbit / wheel gestures between frames.
    for(const time of [1,2,3]) {
        e.graph.liveCamera=structuredClone(userCamera);
        e.graph._fullLayout.scene.camera=structuredClone(userCamera);
        e.graph._fullLayout.scene._scene={getCamera:()=>e.graph.liveCamera};
        e.graph.layout.scene.camera=structuredClone(userCamera);
        await e.context.render3DWaterBody('test',time,{level:0,ve:1});
        const call=e.calls.update.at(-1);
        assert.equal(JSON.stringify(call.layoutUpdate['scene.camera']),JSON.stringify(userCamera),
            `frame ${time} patch must explicitly preserve the live Plotly camera`);
        assert.deepEqual(e.graph.layout.scene.camera,userCamera,
            `frame ${time} keeps the current user camera without a jump`);
    }

    // If an incremental mesh patch fails and the renderer falls back to react,
    // the fallback still needs the latest camera captured immediately pre-draw.
    const presetCamera={eye:{x:0,y:0,z:-2.5},center:{x:0,y:0,z:0},
        up:{x:0,y:1,z:0},projection:{type:'orthographic'}};
    e.graph.liveCamera=structuredClone(presetCamera);
    e.graph._fullLayout.scene.camera=structuredClone(presetCamera);
    e.graph._fullLayout.scene._scene={getCamera:()=>e.graph.liveCamera};
    e.graph.layout.scene.camera=structuredClone(presetCamera);
    assert.equal(typeof e.graph._viz3dCameraListener,'function','the plot must subscribe to Plotly camera gestures');
    e.graph._viz3dCameraListener({'scene.camera':presetCamera},true);
    e.graph.failNextUpdate=true;
    await e.context.render3DWaterBody('test',4,{level:0,ve:1});
    assert.equal(e.calls.react,1,'a rejected mesh patch falls back to a full draw');
    assert.deepEqual(e.graph.layout.scene.camera,presetCamera,
        'full-draw fallback retains the latest preset camera, including an underside view');
});

test('explicit camera reset restores the baseline orthographic model size after playback zoom',async()=>{
    const e=environment();
    await e.context.render3DWaterBody('test',0,{level:0,ve:1});
    const baseline=e.graph._viz3dAspectRatioState.baseline;
    const zoomed=Object.fromEntries(['x','y','z'].map(axis=>[axis,baseline[axis]*1.75]));
    e.graph._fullLayout.scene.aspectratio=structuredClone(zoomed);
    e.graph.layout.scene.aspectratio=structuredClone(zoomed);
    await e.context.render3DWaterBody('test',1,{level:0,ve:1});
    assert.ok(Math.abs(e.graph._viz3dAspectRatioState.scale-1.75)<1e-10,
        'the live orthographic zoom is retained across playback');
    const currentBaseline=structuredClone(e.graph._viz3dAspectRatioState.baseline);
    await e.context.window.set3DCamera('reset');
    assert.deepEqual(e.graph.layout.scene.aspectratio,currentBaseline,'reset restores the fitted physical model size');
    assert.equal(e.graph._viz3dAspectRatioState.scale,1,'reset clears the retained user zoom factor');
});

test('wheel zoom survives a Plotly camera-orbit event that resets scene aspectratio',async()=>{
    const e=environment();
    await e.context.render3DWaterBody('test',0,{level:0,ve:1});
    const baseline=structuredClone(e.graph._viz3dAspectRatioState.baseline);
    const zoomed=Object.fromEntries(['x','y','z'].map(axis=>[axis,baseline[axis]*1.5]));
    e.graph._fullLayout.scene.aspectratio=structuredClone(zoomed);
    e.graph.layout.scene.aspectratio=structuredClone(zoomed);
    const wheelCamera={eye:{x:NaN}}; // Partial Plotly camera payload must not hide the valid wheel aspectratio.
    e.graph._viz3dCameraListener({'scene.camera':wheelCamera,'scene.aspectratio':zoomed},true);

    const flipped={eye:{x:-1,y:1,z:.1},center:{x:0,y:0,z:0},up:{x:0,y:-1,z:0},projection:{type:'orthographic'}};
    e.graph._fullLayout.scene.aspectratio=structuredClone(baseline);
    e.graph.layout.scene.aspectratio=structuredClone(baseline);
    e.graph._viz3dCameraListener({'scene.camera':flipped,'scene.aspectratio':baseline},true);
    await e.context.render3DWaterBody('test',1,{level:0,ve:1});

    assert.ok(Math.abs(e.graph._viz3dAspectRatioState.scale-1.5)<1e-10,
        'camera-driven aspect changes must not discard the wheel scale');
    for(const axis of ['x','y','z'])assert.ok(Math.abs(e.graph.layout.scene.aspectratio[axis]/e.graph._viz3dAspectRatioState.baseline[axis]-1.5)<1e-9,
        `the next frame reapplies wheel zoom on ${axis}`);
    assert.equal(JSON.stringify(e.graph.layout.scene.camera),JSON.stringify(flipped),
        'the next frame retains the flipped orbit camera');
});

test('sequential frames 0 to 1 to 2 patch the current field values and range while retaining land',async()=>{
    const e=environment();
    const payloadFor=time=>{
        const payload=frame(time);
        const offset=time*10;
        payload.bottom=[[10+time,10+time],[10+time,10+time]];
        payload.water_depth=payload.bottom.map(row=>[...row]);
        payload.data=[[[offset+2,offset+3],[offset+4,offset+5]]];
        payload.min=offset+2;payload.max=offset+5;
        payload.dry_mask=[[false,true],[false,false]];
        return payload;
    };
    e.setFetch(payloadFor(0));
    await e.context.render3DWaterBody('test',0,{level:0,ve:1});
    const fieldIndex=e.graph.data.findIndex(trace=>trace.meta?.scientificField);
    const bedIndex=e.graph.data.findIndex(trace=>trace.meta?.waterbodyFrame==='bed');
    const landPlaneIndex=e.graph.data.findIndex(trace=>trace.meta?.landPlane===true);
    const landNetworkIndex=e.graph.data.findIndex(trace=>trace.meta?.landNetwork===true);
    assert.ok([fieldIndex,bedIndex,landPlaneIndex,landNetworkIndex].every(index=>index>=0),
        'frame 0 fixture includes field, lake bed, land plane, and land network traces');
    const frameZeroField=structuredClone(e.graph.data[fieldIndex].intensity);

    for(const time of [1,2]) {
        e.setFetch(payloadFor(time));
        await e.context.render3DWaterBody('test',time,{level:0,ve:1});
        const call=e.calls.update[time-1];
        const fieldPatchPosition=call.indices.indexOf(fieldIndex);
        assert.notEqual(fieldPatchPosition,-1,`frame ${time} includes the scientific field in its update`);
        assert.equal(call.indices.includes(bedIndex),true,`frame ${time} keeps the bed in the update`);
        assert.equal(call.indices.includes(landPlaneIndex),true,`frame ${time} keeps the land plane in the update`);
        assert.equal(call.indices.includes(landNetworkIndex),true,`frame ${time} keeps the land network in the update`);
        for(const key of ['intensity','cmin','cmax']) {
            const payload=call.dataUpdate[key];
            assert.equal(payload.length,call.indices.length,
                `${key} has one trace-index slot for frame ${time}`);
            const fieldValue=payload[fieldPatchPosition];
            assert.ok(fieldValue!==undefined,`${key} is included for the scientific field at frame ${time}`);
            assert.ok(!Array.isArray(fieldValue?.[0]),
                `${key} uses one trace-index wrapper, without extra nesting, for frame ${time}`);
        }
        const field=e.graph.data[fieldIndex];
        assert.deepEqual(JSON.parse(JSON.stringify(field.intensity)),
            JSON.parse(JSON.stringify(call.dataUpdate.intensity[fieldPatchPosition])),
            `frame ${time} visible field values match the trace-indexed update payload`);
        assert.equal(field.cmin,10*time+2,`frame ${time} displays its current color minimum`);
        assert.equal(field.cmax,10*time+5,`frame ${time} displays its current color maximum`);
        assert.deepEqual(JSON.parse(JSON.stringify(e.graph.data[bedIndex].z)),
            JSON.parse(JSON.stringify(call.dataUpdate.z[call.indices.indexOf(bedIndex)])),
            `frame ${time} bed remains synchronized with its update`);
        assert.equal(e.graph.data[landPlaneIndex].opacity,1,`frame ${time} retains the land plane`);
        assert.equal(e.graph.data[landNetworkIndex].opacity,.24,`frame ${time} retains the land network`);
    }

    assert.notDeepEqual(e.graph.data[fieldIndex].intensity,frameZeroField,
        'the frame 2 water field remains colored with its current scalar data');
    assert.equal(e.calls.react,0,'stable topology advances through incremental updates');
    assert.equal(e.calls.update.length,2,'both frame 1 and frame 2 use their own current-frame patch');
});

test('Plotly update arrays use one per-trace array level for field and missing meshes',()=>{
    const context=vm.createContext({console,window:{}});
    vm.runInContext(source,context);
    const oldTraces=[
        {type:'mesh3d',name:'field',meta:{waterbodyFrame:'field'},
            x:[0,1,1],y:[0,0,1],z:[1,1,1],i:[0],j:[1],k:[2],
            intensity:[1,2,3],customdata:[[1],[2],[3]],cmin:1,cmax:3,
            colorscale:[[0,'blue'],[1,'red']],colorbar:{title:{text:'old'}}},
        {type:'mesh3d',name:'missing',meta:{waterbodyFrame:'missing'},
            x:[2,3,3],y:[0,0,1],z:[1,1,1],i:[0],j:[1],k:[2],customdata:[[null],[null],[null]]},
    ];
    const nextTraces=[
        {...oldTraces[0],z:[2,2,2],intensity:[8,9,10],customdata:[[8],[9],[10]],cmin:8,cmax:10,
            colorbar:{title:{text:'new'}}},
        {...oldTraces[1],z:[2,2,2],customdata:[[null],[null],[null]]},
    ];
    const patch=context.viz3dWaterbodyRestyleGroups(oldTraces,nextTraces);
    assert.deepEqual(JSON.parse(JSON.stringify(patch.update.intensity)),[nextTraces[0].intensity,null],
        'Plotly.update expects the trace dimension outside the complete mesh intensity array');
    assert.deepEqual(JSON.parse(JSON.stringify(patch.update.customdata)),[nextTraces[0].customdata,nextTraces[1].customdata],
        'field and missing hover arrays each have exactly one value-array level per trace');
    assert.deepEqual(JSON.parse(JSON.stringify(patch.update.i)),[nextTraces[0].i,nextTraces[1].i],
        'field and missing mesh triangle arrays are passed intact per trace');
});

test('underside camera hides basin, land plane, and land network across playback patches',async()=>{
    const e=environment();
    e.context.fetch=async url=>({json:async()=>{
        const data=frame(Number(new URL(url,'http://localhost').searchParams.get('time')));
        data.dry_mask=[[false,true],[false,false]];return data;
    }});
    await e.context.render3DWaterBody('test',0,{level:0,ve:1});
    const fieldIndex=e.graph.data.findIndex(trace=>trace.meta?.scientificField);
    const bedIndex=e.graph.data.findIndex(trace=>trace.meta?.waterbodyFrame==='bed');
    const landIndex=e.graph.data.findIndex(trace=>trace.meta?.landPlane===true);
    const networkIndex=e.graph.data.findIndex(trace=>trace.meta?.landNetwork===true);
    assert.ok(fieldIndex>=0&&bedIndex>=0&&landIndex>=0&&networkIndex>=0,
        'fixture contains scalar field, basin/land planes, and the actual land-network trace');
    assert.equal(e.graph.data[networkIndex].meta.waterbodyFrame,'land',
        'the actual land network participates in the underside and waterbody-frame paths');
    const field=e.graph.data[fieldIndex];
    const originalIntensity=structuredClone(field.intensity),originalColorbar=field.colorbar;

    await e.context.window.set3DCamera('bottom');
    assert.equal(e.graph.data[networkIndex].opacity,0,'frame 0 underside view hides the land network');
    await e.context.render3DWaterBody('test',1,{level:0,ve:1});

    assert.equal(e.graph.layout.scene.camera.eye.z,-2.5,'underside view preserves the requested camera');
    assert.equal(e.graph.data[bedIndex].opacity,0,'opaque lake bed is bypassed below the lake');
    assert.equal(e.graph.data[landIndex].opacity,0,'opaque land plane is bypassed below the lake');
    assert.equal(e.graph.data[networkIndex].opacity,0,'frame 1 patch keeps the land network hidden');
    assert.equal(e.graph.data[fieldIndex].opacity,1,'scientific field stays visible');
    assert.notDeepEqual(e.graph.data[fieldIndex].intensity,originalIntensity,'playback field advances');
    assert.equal(e.graph.data[fieldIndex].colorbar.title.text,originalColorbar.title.text,'scientific colorbar remains attached');
    assert.equal(e.graph.data[fieldIndex].colorbar.tickvals.at(-1),11,'colorbar advances to the current frame range');
    assert.match(e.graph._viz3dStatus.message,/水体底视.*已隐藏湖底与陆地示意平面/);
    const patch=e.calls.update.at(-1);
    assert.equal(patch.dataUpdate.opacity[patch.indices.indexOf(bedIndex)],0,
        'playback patch retains underside opacity for the bed');
    assert.equal(patch.dataUpdate.opacity[patch.indices.indexOf(networkIndex)],0,
        'playback patch retains underside opacity for the actual land-network trace');

    await e.context.window.set3DCamera('top');
    assert.equal(e.graph.data[bedIndex].opacity,1,'returning above the lake restores the bed');
    assert.equal(e.graph.data[landIndex].opacity,1,'returning above the lake restores the land plane');
    assert.equal(e.graph.data[networkIndex].opacity,.24,'returning above the lake restores the land network opacity');
    assert.equal(e.graph.data[fieldIndex].opacity,1,'camera changes never hide the scientific field');
});

test('camera preset Plotly mutations wait behind an in-flight playback frame',async()=>{
    const e=environment();
    await e.context.render3DWaterBody('test',0,{level:0,ve:1});

    let releaseFrame;
    let frameUpdateStarted;
    const started=new Promise(resolve=>{frameUpdateStarted=resolve;});
    const frameGate=new Promise(resolve=>{releaseFrame=resolve;});
    const update=e.context.Plotly.update;
    e.context.Plotly.update=async(...args)=>{
        frameUpdateStarted();
        await frameGate;
        return update(...args);
    };

    const frameDraw=e.context.render3DWaterBody('test',1,{level:0,ve:1});
    await started;
    const camera=e.context.window.set3DCamera('bottom');
    assert.equal(e.calls.relayout.length,0,'preset camera relayout waits for the active frame draw');
    assert.equal(e.calls.restyle.length,0,'underside opacity restyle waits for the active frame draw');

    releaseFrame();
    await Promise.all([frameDraw,camera]);
    assert.equal(e.calls.relayout.length,1,'camera preset is applied after the frame completes');
    assert.equal(e.calls.restyle.length,1,'underside opacity follows the camera preset in the same draw queue');
    assert.equal(e.graph.layout.scene.camera.eye.z,-2.5);
    assert.equal(e.graph.data.find(trace=>trace.meta?.waterbodyFrame==='bed').opacity,0);
});

test('changed wet topology or incompatible trace shape safely falls back to Plotly.react',async()=>{
    const e=environment();
    await e.context.render3DWaterBody('test',0,{level:0,ve:1});
    e.setFetch(frame(1,[true,false,true,true]));
    await e.context.render3DWaterBody('test',1,{level:0,ve:1});
    assert.equal(e.calls.react,1,'changed wet-cell topology must rebuild rather than patch incompatible connectivity');
});

test('Plotly update rejection falls back to react with visible current-frame scalar data',async()=>{
    const e=environment();
    await e.context.render3DWaterBody('test',0,{level:0,ve:1});
    e.graph.failNextUpdate=true;
    await e.context.render3DWaterBody('test',1,{level:0,ve:1});
    assert.equal(e.calls.react,1,'failed incremental updates use the established full-render fallback');
    const field=e.graph.data.find(trace=>trace.meta?.scientificField);
    assert.ok(field?.intensity.length>0,'fallback leaves the scientific field trace present');
    assert.equal(field.cmin,8,
        'fallback presents current-frame color range');
});

test('a frame that changes field/missing trace shapes falls back even when wet topology is stable',async()=>{
    const e=environment();
    await e.context.render3DWaterBody('test',0,{level:0,ve:1});
    const changed=frame(1);changed.data[0][0][0]=null;
    e.setFetch(changed);
    await e.context.render3DWaterBody('test',1,{level:0,ve:1});
    assert.equal(e.calls.react,1,'an incompatible scientific/missing trace shape uses the full safe render path');
    assert.ok(e.graph.data.some(trace=>trace.meta?.missingWater),'the fallback frame still displays its missing cell');
});

function stackedFrame(time){
    const base=frame(time);
    const shallow=time===0?[[4,4],[4,4]]:[[5,5],[5,5]];
    const deep=time===0?[[8,8],[8,8]]:[[9,9],[9,9]];
    const shift=time===0?0:10;
    return {...base,shape:[2,2,2],sigma:[-.75,-.25],layer_indices:[0,1],total_layers:2,
        depth:[shallow,deep],data:[[[1+shift,2+shift],[3+shift,4+shift]],[[5+shift,6+shift],[7+shift,8+shift]]],min:time===0?1:11,max:time===0?8:18,
        long_name:'Stacked scalar'};
}

test('stacked waterbody layers publish one dynamic field trace with layer-resolvable hover data',async()=>{
    const e=environment();
    e.setFetch(stackedFrame(0));
    await e.context.render3DWaterBody('test',0,{level:1,stack:true,ve:1});
    const fields=e.graph.data.filter(trace=>trace.meta?.scientificField);
    assert.equal(fields.length,1,'a vertical stack should use one Plotly field trace');
    const initial=fields[0];
    assert.equal(initial.name,'Stacked scalar · 垂向堆叠 (2层)');
    assert.deepEqual(initial.meta.layerOrdinals,[0,1]);
    assert.equal(initial.intensity.length,32,'both layers retain all four corners per wet cell');
    assert.equal(initial.i.length,16,'both layers retain the same two triangles per cell');
    assert.equal(Math.max(...initial.i,...initial.j,...initial.k),31,'later-layer indices are offset into combined vertices');
    assert.deepEqual(initial.customdata.filter((row,index)=>index%4===0).map(row=>row[7]),
        [0,0,0,0,1,1,1,1],'every hovered cell carries its physical layer ordinal');
    assert.match(initial.hovertemplate,/customdata\[7\]/,'hover text exposes the layer ordinal');
    const referenceLayers=[];
    for(const layer of [0,1]){
        const reference=environment();reference.setFetch(stackedFrame(0));
        await reference.context.render3DWaterBody('test',0,{level:layer,stack:false,ve:1});
        referenceLayers.push(reference.graph.data.find(trace=>trace.meta?.scientificField));
    }
    for(const property of ['x','y','z','intensity'])assert.deepEqual(initial[property],referenceLayers.flatMap(trace=>trace[property]),
        `${property} preserves the original layer-by-layer geometry/data exactly`);
    let vertexOffset=0,triangleOffset=0;
    for(let layer=0;layer<referenceLayers.length;layer++){
        const reference=referenceLayers[layer];
        for(const property of ['i','j','k'])assert.deepEqual(initial[property].slice(triangleOffset,triangleOffset+reference[property].length),
            reference[property].map(index=>index+vertexOffset),`${property} preserves triangle order for layer ${layer}`);
        for(let q=0;q<reference.customdata.length;q++)assert.deepEqual(initial.customdata[vertexOffset+q].slice(0,7),reference.customdata[q],
            `hover values preserve layer ${layer} cell ${q}`);
        vertexOffset+=reference.x.length;
        triangleOffset+=reference.i.length;
    }

    e.setFetch(stackedFrame(1));
    await e.context.render3DWaterBody('test',1,{level:1,stack:true,ve:1});
    const updated=e.graph.data.filter(trace=>trace.meta?.scientificField);
    assert.equal(updated.length,1);
    assert.equal(e.calls.react,0,'stable stacked topology updates without rebuilding Plotly traces');
    assert.equal(updated[0].cmin,11);assert.equal(updated[0].cmax,18,'the merged trace keeps current-frame auto range');
    assert.equal(updated[0].customdata[0][6],11,'hover still reports current-frame model values');
    assert.equal(updated[0].customdata[0][0],5,'hover depth follows the current water column');
});

test('missing values across a stack remain separately traceable from the combined valid field',async()=>{
    const e=environment(),data=stackedFrame(0);
    data.data[0][0][0]=NaN;data.data[1][1][1]=NaN;
    e.setFetch(data);
    await e.context.render3DWaterBody('test',0,{level:1,stack:true,ve:1});
    const fields=e.graph.data.filter(trace=>trace.meta?.scientificField);
    const missing=e.graph.data.filter(trace=>trace.meta?.missingWater);
    assert.equal(fields.length,1);
    assert.equal(missing.length,1,'missing cells across layers share one display trace');
    assert.ok(missing[0].customdata.every(row=>row.length>7&&[0,1].includes(row[7])));
});

test('stacked fields and stable missing meshes patch across playback together',async()=>{
    const e=environment();
    const makeFrame=time=>{
        const data=stackedFrame(time);
        data.data[0][0][0]=NaN;
        data.data[1][0][0]=NaN;
        return data;
    };
    e.setFetch(makeFrame(0));
    await e.context.render3DWaterBody('test',0,{level:1,stack:true,ve:1});
    const missingBefore=e.graph.data.find(trace=>trace.meta?.missingWater);
    assert.ok(missingBefore,'the initial stacked frame includes a missing-water mesh');
    const beforeDepth=structuredClone(missingBefore.z);
    e.setFetch(makeFrame(1));
    await e.context.render3DWaterBody('test',1,{level:1,stack:true,ve:1});
    assert.equal(e.calls.react,0,'stable stacked scalar/missing topology uses the patch path');
    const field=e.graph.data.find(trace=>trace.meta?.scientificField);
    const missing=e.graph.data.find(trace=>trace.meta?.missingWater);
    assert.equal(field.cmin,11,'the stacked scientific field carries the current frame range');
    assert.notDeepEqual(missing.z,beforeDepth,'the missing mesh receives current water depths');
    const patch=e.calls.update.at(-1);
    const missingIndex=e.graph.data.findIndex(trace=>trace.meta?.missingWater);
    const missingPosition=patch.indices.indexOf(missingIndex);
    assert.ok(missingPosition>=0,'the missing-water mesh participates in the frame patch');
    assert.deepEqual(JSON.parse(JSON.stringify(patch.dataUpdate.customdata[missingPosition])),
        JSON.parse(JSON.stringify(missing.customdata)),
        'missing mesh hover data is one intact per-trace array');
});
