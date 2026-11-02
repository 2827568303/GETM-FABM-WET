const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('3DWET/app/static/js/app.js','utf8');
const lines=[],markers=[],ctx={beginPath(){},moveTo:(x,y)=>lines.push([x,y]),lineTo:(x,y)=>lines.push([x,y]),
 stroke(){},arc:(x,y)=>markers.push([x,y]),fill(){}};
const canvas={width:1200,height:800,getBoundingClientRect:()=>({left:130,top:80,width:900,height:600}),getContext:()=>ctx};
const context=vm.createContext({window:{},document:{},$:()=>canvas,state:{viz2dCellSize:{cols:3,rows:2},viz2dPolygon:[[0,0],[2,0],[1,1]]}});
vm.runInContext(fs.readFileSync('3DWET/app/static/js/scientific_heatmap.js','utf8'),context);
vm.runInContext(source.slice(source.indexOf('function getCanvasCell('),source.indexOf('function setupViz2dCanvasHandlers(')),context);
vm.runInContext(source.slice(source.indexOf('function drawViz2dPolygonOverlay('),source.indexOf('function clearViz2dPolygon(')),context);
for(const rect of [{left:130,top:80,width:900,height:600},{left:-240,top:-100,width:1800,height:1200}]){
 canvas.getBoundingClientRect=()=>rect;
 canvas._scientificGeometry=context.window.ScientificHeatmap.layout(1200,800,2,3,{xc:[100,150,200],yc:[200,300]});
 for(let j=0;j<2;j++)for(let i=0;i<3;i++){
  const p=canvas._scientificGeometry.center(i,j),cell=context.getCanvasCell({clientX:rect.left+p.x*rect.width/canvas.width,clientY:rect.top+p.y*rect.height/canvas.height});
  assert.equal(cell.i,i);assert.equal(cell.j,j,'DPR, pan and CSS zoom preserve original row identity');
 }
 assert.equal(context.getCanvasCell({clientX:rect.left+1,clientY:rect.top+1}),null,'axis margin cannot select an edge cell');
}
context.drawViz2dPolygonOverlay();
const expected=context.state.viz2dPolygon.map(([i,j])=>canvas._scientificGeometry.center(i,j));
assert.deepEqual(markers,expected.map(({x,y})=>[x,y]));
assert.deepEqual(lines,[...markers,markers[0]],'closed polygon vertices share the same forward projection as point picking');
console.log('Scientific canvas binding: DPR/CSS zoom/pan, margins and closed polygon PASS');
