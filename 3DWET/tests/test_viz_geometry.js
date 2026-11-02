// Run with node; these assertions exercise the production geometry without WebGL.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const context = vm.createContext({ console });
vm.runInContext(fs.readFileSync('3DWET/app/static/js/viz3d.js', 'utf8'), context);
const walls = context.buildWaterWalls([0, 10, 20], [0, 10, 20], [[0,0,0],[0,5,0],[0,0,0]], 2);
assert.ok(walls, 'an interior lake must have shoreline walls');
assert.equal(walls.i.length, 8, 'a single wet cell has four quads / eight triangles');
for (let n=0; n<walls.px.length; n+=4) {
    assert.ok(walls.px[n] === walls.px[n+2] || walls.py[n] === walls.py[n+2], 'shore segments follow cell edges, never diagonals');
}
assert.equal(context.buildWaterWalls([0,1],[0,1],[[NaN,0],[-10,null]],1), null, 'no land/NaN geometry');
const lake = context.buildLakeGeometry([0,10,20],[0,10,20],[[5,5,0],[5,0,0],[0,0,7]],2);
assert.equal(lake.floor.i.length, 8, 'only four water cells are triangulated');
assert.equal(lake.shoreline.x.filter(x => x === null).length, 12, 'disjoint water masks preserve each boundary segment');
assert.ok(lake.floor.z.every(Number.isFinite), 'all geometry is finite');
assert.equal(Math.min(...lake.floor.z),-14);
assert.equal(context.buildLakeGeometry([0],[0],[[0]],1), null);
const island=context.buildLakeGeometry([0,1,2],[0,1,2],[[3,3,3],[3,0,3],[3,3,3]],1);
assert.equal(island.floor.i.length,16,'island interior contributes no triangles');
assert.equal(island.shoreline.x.filter(x=>x===null).length,16,'outer shore and island edges both retained');
const degenerate=context.buildLakeGeometry([NaN],[0],[[5]],1);
assert.equal(degenerate,null,'invalid physical coordinate prevents non-finite WebGL geometry');
const auto = context.lakeVerticalScale([0,1000],[0,1000],[[5,10],[10,5]],0);
assert.ok(auto>=1 && auto<100, 'automatic scale avoids the previous excessive default');
assert.equal(context.lakeVerticalScale([0,1000],[0,1000],[[5,10],[10,5]],20),20,'explicit scale respected');
assert.deepEqual(Array.from(context.sigmaToFraction([-0.9,-0.5,-0.1])),[0.9,0.5,0.1], 'sigma layer centers are not moved to bed/surface');
assert.deepEqual(Array.from(context.sigmaToFraction([-0.8,0,0.8])),[0.9,0.5,0.09999999999999998], 'GETM [-1,1] layer centers retain distance to boundaries');
assert.equal(typeof context.lakeVolumeSamples,'function','volume modes need physical coordinates');
const samples=context.lakeVolumeSamples({shape:[2,1,2],xc:[10,20],yc:[30],bottom:[[5,0]],sigma:[-0.75,-0.25],data:[[[1,9]],[[2,9]]]},2);
assert.deepEqual(Array.from(samples.x),[10,20,10,20]);
assert.deepEqual(Array.from(samples.z),[-7.5,0,-2.5,0]);
assert.deepEqual(Array.from(samples.values),[1,null,2,null],'land variables excluded from volume modes');
const slope=context.buildLakeGeometry([0,10],[0,10],[[2,8],[2,8]],3);
const contours=context.buildLakeContours(slope,[4,6]);
assert.ok(contours.x.length>0,'a sloping bed produces bathymetric contours');
for(let n=0;n<contours.x.length;n+=3) {
    assert.equal(contours.z[n],-contours.depth[n]*3,'contour elevations retain the real depth and vertical scale');
    assert.equal(contours.z[n+1],contours.z[n]);
    assert.equal(contours.x[n+2],null,'segments are separated instead of bridging a dry cell');
    assert.ok(contours.x[n]>=-5 && contours.x[n]<=15);
}
assert.equal(context.buildLakeContours(island,[3]).x.length,0,'flat triangles never create spurious contours');
const grid=context.buildLakeGrid(lake);
assert.ok(grid.x.length>0,'grid overlay retains wet-cell edges');
for(let n=0;n<grid.x.length;n+=3) {
    assert.ok(grid.x[n]===grid.x[n+1] || grid.y[n]===grid.y[n+1],'orthogonal network edges are never diagonal');
    assert.equal(grid.x[n+2],null,'disconnected cell edges stay separate');
}
assert.ok(context.lakeDepthLevels(13).every(h=>h>0 && h<13),'contour levels stay inside observed depth range');
const scene=context.lakeScene(20,10,{xc:[100,200,300],yc:[1000,1200]});
assert.equal(scene.aspectmode,'manual','thin isosurfaces must not renormalize the camera around their own narrow z extent');
assert.deepEqual(Array.from(scene.xaxis.range),[50,350]);
assert.deepEqual(Array.from(scene.yaxis.range),[900,1300]);
assert.deepEqual(Array.from(scene.zaxis.range),[-200,0]);
assert.equal(scene.aspectratio.x/scene.aspectratio.y,300/400,'scene aspect preserves the physical horizontal ratio');
assert.equal(scene.aspectratio.z/scene.aspectratio.y,200/400,'VE changes geometry while maintaining its supplied physical ratio');
assert.equal(Math.max(...Object.values(scene.aspectratio)),4.5,'manual aspect ratios retain normalized physical proportions plus the orthographic framing scale');
const workspaceCss=fs.readFileSync('3DWET/app/static/css/scientific_workspace.css','utf8');
assert.match(workspaceCss,/#page-viz3d #viz3d-plotly\s*\{\s*height:\s*clamp\(460px, calc\(100dvh - 300px\), 760px\) !important/,'the desktop 3D scene follows the current workspace height contract');
console.log('lake geometry: shoreline, holes, disconnected cells, masks, scale and sigma PASS');
