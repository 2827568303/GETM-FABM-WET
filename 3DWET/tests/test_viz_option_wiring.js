const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('3DWET/app/static/js/app.js','utf8');
const calls=[];
const values={'viz3d-iso-var':'temp','viz3d-iso-time':'3','viz3d-iso-render':'cloud',
 'viz3d-iso-quality':'26','viz3d-iso-level':'0','viz3d-iso-layer':'-1','viz3d-iso-ve':'100', 'viz3d-opacity':'1'};
const elements=Object.fromEntries(Object.entries(values).map(([k,value])=>[k,{value,checked:false}]));
const context=vm.createContext({state:{activeCase:'A',activeCasePath:'A',timeLabels:['','','','actual output time']},
 $:id=>elements[id],document:{getElementById:id=>elements[id]},window:{},ModelDates:{format:x=>x||''},
 render3DCloud:async(...args)=>calls.push(['cloud',...args]),
 render3DSurface:async(...args)=>calls.push(['iso',...args]),
 render3DWaterBody:async(...args)=>calls.push(['body',...args]),
 renderBathymetry3D:async(...args)=>calls.push(['bathy',...args]),
 render2DAs3DSurface:async(...args)=>calls.push(['surface',...args])});
vm.runInContext(source.slice(source.indexOf('async function updateViz3dIso('),source.indexOf('async function updateViz3d()')),context);
(async()=>{
 for(const mode of ['cloud','isosurface','waterbody','surface2d']) {
  elements['viz3d-iso-render'].value=mode;await context.updateViz3dIso();
  const options=calls.at(-1).at(-1);
  assert.equal(options.ve,100,mode+': selected vertical scale must reach renderer');
  assert.equal(options.timeLabel,'actual output time',mode+': actual output time must reach renderer');
  assert.equal(options.caseKey,'A');
  assert.equal(options.opacity,1);
 }
 elements['viz3d-iso-render'].value='waterbody';elements['viz3d-iso-overlay']={checked:false};
 elements['viz3d-iso-var'].value='D';context.state.variables3d=[{name:'D',ndim:3}];
 await context.updateViz3dIso();
 assert.equal(calls.at(-1)[0],'bathy','terrain-only mode must not require an unrelated 4D scalar field');
 elements['viz3d-iso-var'].value='__bathy__';await context.updateViz3dIso();
 assert.equal(calls.at(-1).at(-1).ve,100,'no-results basin preview receives selected scale');
 console.log('3D controls pass physical scale, opacity, case and actual date to every renderer PASS');
})().catch(e=>{console.error(e);process.exitCode=1;});
