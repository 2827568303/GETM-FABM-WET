const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const context=vm.createContext({console});
const sourcePath='3DWET/app/static/js/view_controls.js';
assert.ok(fs.existsSync(sourcePath),'shared view controls module must exist');
vm.runInContext(fs.readFileSync(sourcePath,'utf8'),context);
const V=vm.runInContext('ViewControlsMath',context);
assert.equal(V.appScale(0.1),0.6);
assert.equal(V.appScale(5),1.8);
assert.equal(V.appScale(NaN),1);
const range=V.zoomRange(0,100,25,2);
assert.equal(range.min,12.5);assert.equal(range.max,62.5);
const view=V.zoomViewport({scale:1,x:0,y:0},2,30,40);
assert.equal(view.scale,2);assert.equal(view.x,-30);assert.equal(view.y,-40);
assert.equal((30-view.x)/view.scale,30,'cursor maps to same data coordinate after zoom');
assert.equal((40-view.y)/view.scale,40);
assert.equal(typeof V.zoomCategoryRange,'function','category zoom needs persistent fractional bounds');
for(const count of [4,7,14]) {
    let category={min:0,max:count-1};
    for(let n=0;n<12;n++)category=V.zoomCategoryRange(category,1.18,0.5,{min:0,max:count-1});
    assert.ok(Math.ceil(category.max)-Math.floor(category.min)<count-1,'repeated wheel zoom changes short category axis');
    for(let n=0;n<40;n++)category=V.zoomCategoryRange(category,1/1.18,0.5,{min:0,max:count-1});
    assert.equal(category.min,0);assert.equal(category.max,count-1,'zoom out restores full category extent');
}
console.log('view controls: bounds and cursor-anchored zoom PASS');
assert.equal(typeof V.fitCanvas,'function','2D viewport needs an aspect-preserving fit');
for(const [w,h] of [[240,500],[1100,320],[640,900]]) {
    const size=V.fitCanvas(w,h,800,500);
    assert.ok(size.width<=w && size.height<=h);
    assert.ok(Math.abs(size.width/size.height-1.6)<1e-12,'resizing must not stretch data');
}
assert.deepEqual(JSON.parse(JSON.stringify(V.fitCanvas(0,500,800,500))),{width:0,height:0});
console.log('2D viewport: narrow, wide and tall fitting preserves aspect PASS');
