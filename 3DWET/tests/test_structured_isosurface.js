const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const context=vm.createContext({window:{},console});
vm.runInContext(fs.readFileSync('3DWET/app/static/js/viz3d.js','utf8'),context);
assert.equal(typeof context.buildStructuredIsosurface,'function','terrain-following structured cells require a physical-space isosurface mesh');
const cube={shape:[2,2,2],xc:[100,200],yc:[1000,1100],bottom:[[4,8],[4,8]],sigma:[-1,0],
 data:[[[0,1],[0,1]],[[0,1],[0,1]]]};
const mesh=context.buildStructuredIsosurface(cube,.5,1);
assert.ok(mesh.i.length>0);
for(let n=0;n<mesh.i.length;n++){
 const [a,b,c]=[mesh.i[n],mesh.j[n],mesh.k[n]];
 const normalX=(mesh.y[b]-mesh.y[a])*(mesh.z[c]-mesh.z[a])-(mesh.z[b]-mesh.z[a])*(mesh.y[c]-mesh.y[a]);
 assert.ok(normalX>0,'all faces must point towards the increasing scalar, including adjacent tetrahedra');
}
assert.ok(mesh.x.every(x=>Math.abs(x-150)<1e-10),'the analytic x=150 isoplane must be exact');
assert.equal(Math.min(...mesh.y),1000);assert.equal(Math.max(...mesh.y),1100);
assert.equal(Math.min(...mesh.z),-6);assert.equal(Math.max(...mesh.z),0,'depth follows the actual sigma grid, not a fictitious Cartesian z axis');
assert.ok(mesh.intensity.every(v=>v===.5));
const enlarged=context.buildStructuredIsosurface(cube,.5,20);
assert.deepEqual(Array.from(enlarged.x),Array.from(mesh.x));assert.equal(Math.min(...enlarged.z),-120);
const negative={...cube,data:[[[ -1,1],[-1,1]],[[-1,1],[-1,1]]]};
assert.ok(context.buildStructuredIsosurface(negative,0,1).i.length>0,'zero isovalues remain valid');
const dry={shape:[2,2,4],xc:[0,1,2,3],yc:[0,1],bottom:[[4,null,4,4],[4,null,4,4]],sigma:[-1,0],
 data:[[[0,1,2,3],[0,1,2,3]],[[0,1,2,3],[0,1,2,3]]]};
assert.equal(context.buildStructuredIsosurface(dry,.5,1).i.length,0,'isosurfaces cannot bridge a dry column');
assert.ok(context.buildStructuredIsosurface(dry,2.5,1).i.length>0,'the disconnected valid wet region remains available');
const missing={...cube,data:[[[null,1],[0,1]],[[0,1],[0,1]]]};
assert.equal(context.buildStructuredIsosurface(missing,.5,1).i.length,0,'missing corners cannot be replaced with artificial values');
const constant={...cube,data:[[[3,3],[3,3]],[[3,3],[3,3]]]};
assert.equal(context.buildStructuredIsosurface(constant,3,1).i.length,0,'a constant field has no distinct interior surface');
const plateau={shape:[2,2,3],xc:[0,1,2],yc:[0,1],bottom:[[4,4,4],[4,4,4]],sigma:[-.75,-.25],
 data:[[[ -1,0,-1],[-1,0,-1]],[[-1,0,-1],[-1,0,-1]]]};
const faces=context.buildStructuredIsosurface(plateau,0,1);
const keys=faces.i.map((a,n)=>[a,faces.j[n],faces.k[n]].map(q=>[faces.x[q],faces.y[q],faces.z[q]].join(',')).sort().join('|'));
assert.equal(new Set(keys).size,keys.length,'neighbouring cells may not duplicate a coincident threshold face');
console.log('Structured sigma isosurfaces: analytic plane, physical depths, VE, zero values, dry and missing cells PASS');
