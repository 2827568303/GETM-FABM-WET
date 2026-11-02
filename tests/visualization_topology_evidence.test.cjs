const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const test = require('node:test');

function functionSource(source, name) {
  const start = source.indexOf(`function ${name}(`);
  assert.notEqual(start, -1, `missing ${name}`);
  const open = source.indexOf(') {', start) + 2;
  let depth = 0;
  for (let i = open; i < source.length; i++) {
    if (source[i] === '{') depth++;
    if (source[i] === '}' && --depth === 0) return source.slice(start, i + 1);
  }
  throw new Error(`unterminated ${name}`);
}

const vizSource = fs.readFileSync('3DWET/app/static/js/viz3d.js', 'utf8');
const networkSource = fs.readFileSync('3DWET/app/static/js/ecology_network.js', 'utf8');

test('triangular display network is built from wet quadrilateral cells and reports actual face/edge counts', () => {
  const context = { Map, Object, Number, Math, Set, WeakMap, Array };
  context.mesh = {x:[0,1,1,0],y:[0,0,1,1],z:[0,0,0,0],cell:[[0,0]]};
  vm.createContext(context);
  vm.runInContext([
    'const _viz3dTriangleNetworkTemplates=new Map();',
    functionSource(vizSource, 'lakeTriangleNetworkTemplate'),
    functionSource(vizSource, 'buildDisplayNetwork'),
  ].join('\n'), context);

  const result = vm.runInContext("buildDisplayNetwork([mesh],{mode:'triangles',refinement:2})", context);

  assert.equal(result.stats.sourceQuadCells, 1);
  assert.equal(result.stats.triangleSourceCells, 1);
  assert.equal(result.stats.triangleFaces, 8, 'two source triangles each split into four real display faces');
  assert.equal(result.stats.segments, result.lines.x.filter((value, index) => index % 3 === 0 && value !== null).length);
  assert.match(result.stats.triangulation, /wet structured quad/);
});

test('single-layer playback display network excludes hidden sigma layers without changing visible triangle counts', () => {
  const context = { Map, Object, Number, Math, Set, WeakMap, Array };
  context.lakePhysicalLayerNetworkMesh = (_geometry, _data, layer) => ({
    x:[0,1,1,0],y:[0,0,1,1],z:[-layer,-layer,-layer,-layer],cell:[[0,0]],
  });
  vm.createContext(context);
  vm.runInContext([
    'const _viz3dTriangleNetworkTemplates=new Map();',
    functionSource(vizSource, 'lakeTriangleNetworkTemplate'),
    functionSource(vizSource, 'lakePhysicalVolumeNetwork'),
    functionSource(vizSource, 'buildDisplayNetwork'),
  ].join('\n'), context);

  const result = vm.runInContext(`(()=>{
    const data={shape:[3,1,1]}, geometry={};
    const visible=lakePhysicalVolumeNetwork(data,geometry,1,[1]);
    const all=lakePhysicalVolumeNetwork(data,geometry,1);
    const lines=buildDisplayNetwork(visible,{mode:'triangles',refinement:2});
    return {visible,all,lines};
  })()`, context);

  assert.equal(result.visible.length, 1);
  assert.deepEqual(Array.from(result.visible[0].z), [-1,-1,-1,-1]);
  assert.equal(result.all.length, 3, 'omitting the filter keeps all layers available for stacked views');
  assert.equal(result.lines.stats.sourceQuadCells, 1);
  assert.equal(result.lines.stats.triangleSourceCells, 1);
  assert.equal(result.lines.stats.triangleFaces, 8);
  assert.equal(result.lines.stats.segments, 16, 'one visible wet quad retains its exact subdivided edge count');
});

test('single-layer waterbody triangle playback defaults to the stable unsplit quad diagonal', () => {
  const context = {
    Map, Object, Number, Math, Set, WeakMap, Array,
    lakeDisplayTopologyValid: () => true,
    viz3dSampledBoundary: () => false,
  };
  context.mesh = {x:[0,1,1,0],y:[0,0,1,1],z:[0,0,0,0],cell:[[0,0]]};
  context.geometry = {maxDepth:1,ve:1};
  context.data = {shape:[3,1,1],display_topology:{contract:'sampled-wet-topology-v1'}};
  vm.createContext(context);
  vm.runInContext([
    'const _viz3dTriangleNetworkTemplates=new Map();',
    functionSource(vizSource, 'lakeTriangleNetworkTemplate'),
    functionSource(vizSource, 'buildDisplayNetwork'),
    functionSource(vizSource, 'lakeDisplayLines'),
    functionSource(vizSource, 'lakeWaterbodyDisplayOptions'),
  ].join('\n'), context);

  const result = vm.runInContext(`(()=>{
    const options=lakeWaterbodyDisplayOptions({meshMode:'triangles'},false);
    const line=lakeDisplayLines([mesh],geometry,options,data)[0];
    const stackedOptions=lakeWaterbodyDisplayOptions({meshMode:'triangles',lineRefinement:3},true);
    const stacked=lakeDisplayLines([mesh],geometry,stackedOptions,data)[0];
    return {line,stacked};
  })()`, context);

  assert.equal(result.line.meta.refinement, 1);
  assert.equal(result.line.meta.triangleFaces, 2, 'one structured wet quad is split into exactly two display faces');
  assert.equal(result.line.meta.displayEdges, 5, 'deduplicated outer edges plus the stable diagonal');
  assert.equal(result.stacked.meta.refinement, 3, 'stacked views retain the configured refinement');
  assert.equal(result.stacked.meta.triangleFaces, 18);
});

test('triangle overlay fails closed when the verified wet topology contract is absent', () => {
  const context = {lakeDisplayTopologyValid:()=>true};
  vm.createContext(context);
  vm.runInContext(functionSource(vizSource, 'lakeDisplayLines'), context);
  assert.deepEqual(Array.from(context.lakeDisplayLines([], {maxDepth:1,ve:1}, {meshMode:'triangles'}, {})), []);
});

test('foodweb triangle count only includes closed configured directed 3-cycles', () => {
  const context = {};
  vm.createContext(context);
  vm.runInContext(functionSource(networkSource, 'directedFoodwebCycleSummary'), context);
  const path = [{source:'algae',target:'zoo'},{source:'zoo',target:'fish'}];
  const openChain = context.directedFoodwebCycleSummary(path);
  assert.equal(openChain.count, 0, 'an open chain is not a three-node cycle');
  assert.deepEqual([...openChain.edgeKeys], [], 'open chains mark no cycle edges');

  const oneOrientation = context.directedFoodwebCycleSummary([...path,{source:'fish',target:'algae'}]);
  assert.equal(oneOrientation.count, 1);
  assert.deepEqual([...oneOrientation.edgeKeys].sort(), [
    'algae\0zoo', 'fish\0algae', 'zoo\0fish',
  ]);

  const bothOrientations = context.directedFoodwebCycleSummary([
    ...path,{source:'fish',target:'algae'},
    {source:'algae',target:'fish'},{source:'fish',target:'zoo'},{source:'zoo',target:'algae'},
  ]);
  assert.equal(bothOrientations.count, 2, 'opposite directed cycles count separately only when both are configured');
  assert.deepEqual([...bothOrientations.edgeKeys].sort(), [
    'algae\0fish', 'algae\0zoo', 'fish\0algae', 'fish\0zoo', 'zoo\0algae', 'zoo\0fish',
  ]);
});
