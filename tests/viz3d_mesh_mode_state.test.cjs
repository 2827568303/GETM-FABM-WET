const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const test = require('node:test');

const source = fs.readFileSync('3DWET/app/static/js/viz3d.js', 'utf8');

function functionSource(name) {
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

function loadMeshState() {
  const meshSelect = { value: 'triangles' };
  const container = { _viz3dLastPlot: null };
  const context = {
    document: { getElementById: (id) => id === 'viz3d-mesh-mode' ? meshSelect : container },
    viz3dCurrent: () => true,
    viz3dStatus: () => {},
    viz3dLabel: () => 'temperature',
    viz3dUndersideNote: () => '',
    window: { ScientificWorkspace: { publish() {} } },
  };
  vm.createContext(context);
  vm.runInContext(`${functionSource('viz3dDone')}\n${functionSource('viz3dError')}`, context);
  return { context, meshSelect, container };
}

test('failed mesh redraw restores the selector to the mesh mode still shown by the retained plot', () => {
  const { context, meshSelect, container } = loadMeshState();
  context.viz3dDone({
    container,
    key: 'lake',
    varName: 'temperature',
    timestep: 4,
    opts: { meshMode: 'orthogonal' },
    renderedMeshMode: 'orthogonal',
    section: false,
  }, { units: '°C' }, null, 'time 4');

  meshSelect.value = 'triangles';
  context.viz3dError('没有3D输出文件', {
    container,
    key: 'lake',
    varName: 'temperature',
    timestep: 5,
    opts: { meshMode: 'triangles' },
    section: false,
  });

  assert.equal(container._viz3dLastPlot.meshMode, 'orthogonal');
  assert.equal(meshSelect.value, 'orthogonal', 'selector must describe the retained orthogonal wireframe');
});
