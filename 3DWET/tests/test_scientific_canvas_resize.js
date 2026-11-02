const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('3DWET/app/static/js/app.js','utf8'),calls=[];
const field=[[10,11],[12,13]],host={clientWidth:360,clientHeight:340,classList:{contains:name=>name==='vc-canvas-viewport'}};
const canvas={width:800,height:500,style:{},parentElement:host,_scientificMetadata:{shape:[2,2],wetMask:[[true,true],[true,true]],coordinate_mode:'projected',xc:[100,150],yc:[200,300]},_scientificRange:{palette:'lake'},_resultField:field};
const context=vm.createContext({window:{devicePixelRatio:2,ScientificHeatmap:{draw:(c,data,opts)=>{calls.push({w:c.width,h:c.height,data,opts});return {cellAt:()=>null};}}},
 document:{getElementById:()=>null},$:()=>canvas,state:{},setupViz2dCanvasHandlers(){},drawViz2dPolygonOverlay(){}});
vm.runInContext(source.slice(source.indexOf('function drawHeatmap('),source.indexOf('function heatColor(')),context);
context.drawHeatmap('viz2d-canvas',field,10,13);
assert.deepEqual([canvas.width,canvas.height],[720,680],'backing buffer follows usable CSS viewport and DPR');
assert.equal(canvas.style.width,'360px');assert.equal(canvas.style.height,'340px');
assert.equal(calls[0].opts.pixelRatio,2,'axis text remains eleven CSS pixels rather than being shrunk with an old bitmap');
canvas._scientificResize(500,280);
assert.deepEqual([canvas.width,canvas.height],[1000,560]);
assert.equal(calls.length,2,'viewport resize redraws the cached field without another API request');
assert.strictEqual(calls[1].data,field,'resizing never resamples or edits model values');
console.log('Scientific canvas: responsive DPR buffer and cached exact-data redraw PASS');
