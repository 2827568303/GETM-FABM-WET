const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const plots=[];
const element={innerHTML:''};
let url;
const payload={axis:'xz',index:1,time:2,data:[[1,null,3],[4,5,null]],
    horizontal:[10,20,40],horizontal_edges:[5,15,30,50],depth:[[7,null,7],[2,2,3]],
    depth_edges:[[10,null,8],[4,4,6],[0,0,0]],coordinate_units:'m',
    long_name:'温度',long_name_en:'temperature',units:'degC',min:1,max:5};
const Plotly={newPlot:async(c,traces,layout)=>plots.push({traces,layout})};
const context=vm.createContext({console,Plotly,window:{Plotly,StudioI18n:{
    scientificText:(zh,en)=>`${zh} (${en})`,t:s=>s}},
    document:{getElementById:()=>element},fetch:async u=>{url=u;return {json:async()=>payload};}});
vm.runInContext(fs.readFileSync('3DWET/app/static/js/viz3d.js','utf8'),context);
(async()=>{
    await context.renderSpatialSection('temp',2,'xz',1);
    assert.ok(url.includes('axis=xz&index=1'));
    const mesh=plots[0].traces[0];
    assert.equal(mesh.i.length,8,'only four finite cells generate geometry');
    assert.equal(mesh.x.length,16,'cells have disconnected vertices to avoid bridging missing cells');
    assert.equal(mesh.z[0],-10,'real hn interface depth, not sigma layer index');
    assert.equal(mesh.z[1],-4);
    assert.equal(mesh.intensitymode,'cell');
    assert.ok(plots[0].layout.title.text.includes('temperature'),'retain original scientific label');
    assert.equal(plots[0].layout.scene.zaxis.title,'水深 (m)');
    console.log('Spatial section rendering passed');
})().catch(e=>{console.error(e);process.exit(1);});
