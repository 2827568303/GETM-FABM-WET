const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const source = fs.readFileSync('3DWET/app/static/js/ecology_network.js', 'utf8');

class Element {
  constructor(id = '') { this.id = id; this.children = []; this.dataset = {}; this.style = {}; this.attributes = {}; this.value = ''; this.disabled = false; this.textContent = ''; this.listeners = {}; }
  append(...items) { this.children.push(...items); }
  replaceChildren(...items) { this.children = items; }
  setAttribute(key, value) { this.attributes[key] = String(value); }
  addEventListener(name, fn) { this.listeners[name] = fn; }
  querySelector() { return null; }
  querySelectorAll() { return []; }
  closest() { return null; }
  getBoundingClientRect() { return { width: 900, height: 470 }; }
}

function setup(api) {
  const elements = new Map();
  const get = id => { if (!elements.has(id)) elements.set(id, new Element(id)); return elements.get(id); };
  const page = get('page-gridstudio');
  const filterButtons = ['all', 'ecology', 'water_quality'].map(domain => {
    const button = new Element('filter-' + domain); button.dataset.networkFilter = domain; return button;
  });
  const document = {
    getElementById: get,
    createElement: tag => new Element(tag),
    createElementNS: (_ns, tag) => new Element(tag),
    querySelectorAll: selector => selector === '[data-network-filter]' ? filterButtons : [],
  };
  const state = { activeCasePath: 'C:/cases/lake-a', fabmModules: [] };
  const window = {};
  vm.runInNewContext(source, { document, window, state, api, navigate() {}, loadModuleParams() {}, ViewControls: null, console });
  return { el: id => get('en-' + id), state, window, page, filterButtons };
}

function fakeAPI() {
  const calls = [];
  const instances = {
    case_path: 'C:/cases/lake-a', revision: 'r1',
    instances: [
      { name: 'algae', long_name: 'Algae', model: 'wet/phytoplankton', family: 'phytoplankton', domain: 'ecology', enabled: true },
      { name: 'green_template', long_name: 'Green template', model: 'wet/phytoplankton', family: 'phytoplankton', domain: 'ecology', enabled: true },
      { name: 'fish_template', long_name: 'Fish template', model: 'wet/fish', family: 'fish', domain: 'ecology', enabled: true },
    ],
    deleted: [{ id: 'deleted-1', name: 'old_fish', long_name: 'Old fish', model: 'wet/fish', family: 'fish', domain: 'ecology', enabled: false }],
  };
  const api = async (url, options = {}) => {
    calls.push({ url, options: structuredClone(options) });
    if (url === '/api/model/instances?domain=all' && !options.method) return structuredClone(instances);
    if (url === '/api/model/instances/transaction') {
      if (options.body.mode === 'preview' && api.failPreview) return { error: api.failPreview };
      if (options.body.mode === 'preview') {
        if (api.switchDuringPreview) api._state.activeCasePath = 'C:/cases/lake-b';
        const operation = options.body.operations[0];
        const integrations = operation.op === 'clone' && operation.name === 'cyanobacteria'
          ? ['burial', 'inorganic_carbon'] : [];
        return { case_path: instances.case_path, revision: api.staleRevision ? 'r0' : instances.revision, preview_hash: 'preview-1', integrations };
      }
      const operation = options.body.operations[0];
      if (operation.op === 'add') instances.instances.push({ name: operation.name, long_name: operation.long_name || operation.name, model: operation.model, family: operation.model.slice(4), domain: 'ecology', enabled: true });
      if (operation.op === 'clone') {
        const source = instances.instances.find(item => item.name === operation.source);
        instances.instances.push({ ...source, name: operation.name, long_name: operation.long_name || operation.name });
      }
      if (operation.op === 'delete') {
        const [item] = instances.instances.splice(instances.instances.findIndex(item => item.name === operation.name), 1);
        if (item) instances.deleted.push({ ...item, id: 'deleted-' + item.name, enabled: false });
      }
      if (operation.op === 'restore') {
        const index = instances.deleted.findIndex(item => item.name === operation.name);
        if (index >= 0) instances.instances.push({ ...instances.deleted.splice(index, 1)[0], enabled: true });
      }
      instances.revision = 'r2';
      return { case_path: instances.case_path, revision: instances.revision };
    }
    if (url === '/api/ecology/network') return { case_path: instances.case_path, revision: instances.revision, nodes: instances.instances.map(item => ({ ...item, parameters: {}, coupling: {} })), edges: [], targets: [] };
    return { error: 'UNEXPECTED_API' };
  };
  return { api, calls };
}

async function loaded() {
  const backend = fakeAPI();
  const app = setup(backend.api);
  backend.api._state = app.state;
  await app.window.loadEcologyNetwork();
  return { ...app, ...backend };
}

async function run() {
  {
    const app = await loaded();
    assert.equal(app.el('add-source').value, '', 'clone source must not be silently preselected');
    assert.equal(app.el('add').disabled, true, 'clone button stays disabled until the user chooses a source');
    assert.equal(app.el('add-source').children[0].value, '', 'source picker starts with an explicit placeholder');
    // The visible network filter must not constrain which model families can be added.
    app.filterButtons.find(button => button.dataset.networkFilter === 'water_quality').listeners.click();
    const offered = app.el('add-model').children.map(item => item.value);
    for (const family of ['phytoplankton', 'zooplankton', 'zoobenthos', 'macrophytes', 'fish']) {
      assert.ok(offered.includes('wet/' + family), `ecology family ${family} remains addable while viewing water quality`);
    }
  }
  {
    const app = await loaded();
    app.el('add-name').value = 'new_benthos';
    app.el('add-model').value = 'wet/zoobenthos';
    app.el('add-model').listeners.change();
    await app.el('add').onclick();
    const tx = app.calls.filter(c => c.url === '/api/model/instances/transaction');
    assert.equal(tx.length, 0, 'without a matching clone source the UI must not call the transaction API');
    assert.equal(app.el('add').disabled, true);
    assert.match(app.el('add-template-hint').textContent, /没有可克隆的已启用实例/);
  }
  {
    const app = await loaded();
    app.el('add-name').value = 'cyanobacteria';
    app.el('add-display-name').value = 'Cyanobacteria';
    app.el('add-model').value = 'wet/phytoplankton';
    app.el('add-model').listeners.change();
    app.el('add-source').value = 'green_template';
    app.el('add-source').listeners.change();
    assert.match(app.el('add-template-hint').textContent, /初始值.*原样复制/);
    assert.match(app.el('add-template-hint').textContent, /同一功能群.*初始总生物量.*增加/);
    assert.match(app.el('add-template-hint').textContent, /捕食者.*消费者.*不会自动.*新实例/);
    assert.match(app.el('add-template-hint').textContent, /公平.*竞争.*总初始生物量.*食谱.*耦合/);
    assert.deepEqual(app.el('add-source').children.map(item => item.value), ['', 'algae', 'green_template'], 'template picker only offers the placeholder and enabled instances in the selected model family');
    await app.el('add').onclick();
    const tx = app.calls.filter(c => c.url === '/api/model/instances/transaction');
    assert.deepEqual(tx.map(c => c.options.body.mode), ['preview', 'apply']);
    assert.equal(tx[0].options.body.operations[0].op, 'clone');
    assert.equal(tx[0].options.body.operations[0].source, 'green_template');
    assert.equal(tx[0].options.body.operations[0].name, 'cyanobacteria');
    assert.equal(tx[1].options.body.preview_hash, 'preview-1');
    assert.equal(app.calls.filter(c => c.url === '/api/ecology/network').length, 2, 'successful apply reloads the graph');
    assert.ok(app.el('node').children.some(item => item.value === 'cyanobacteria'), 'new instance appears in the refreshed node selector');
    assert.match(app.el('message').textContent, /已自动接入埋藏、无机碳/);
    assert.match(app.el('message').textContent, /未自动增加该藻类作为猎物/);
  }
  {
    const app = await loaded();
    app.el('deleted').value = 'old_fish';
    await app.el('restore').onclick();
    const tx = app.calls.filter(c => c.url === '/api/model/instances/transaction');
    assert.equal(tx[0].options.body.operations[0].op, 'restore');
    assert.equal(tx[0].options.body.operations[0].name, 'old_fish');
    assert.equal(tx[1].options.body.mode, 'apply');
    assert.ok(app.el('deleted').children.every(item => item.value !== 'old_fish'), 'restored instance leaves the deleted selector');
  }
  {
    const app = await loaded();
    app.api.switchDuringPreview = true;
    app.el('add-name').value = 'new_algae';
    app.el('add-model').value = 'wet/phytoplankton';
    app.el('add-model').listeners.change();
    app.el('add-source').value = 'green_template';
    app.el('add-source').listeners.change();
    await app.el('add').onclick();
    const tx = app.calls.filter(c => c.url === '/api/model/instances/transaction');
    assert.equal(tx.length, 1, 'case switch during preview must prevent the apply request');
    assert.equal(tx[0].options.body.mode, 'preview');
    assert.match(app.el('message').textContent, /案例已切换/);
  }
  {
    const app = await loaded();
    app.api.staleRevision = true;
    app.el('add-name').value = 'new_algae';
    app.el('add-model').value = 'wet/phytoplankton';
    app.el('add-model').listeners.change();
    app.el('add-source').value = 'green_template';
    app.el('add-source').listeners.change();
    await app.el('add').onclick();
    assert.equal(app.calls.filter(c => c.url === '/api/model/instances/transaction').length, 1, 'stale preview revision must not apply');
    assert.match(app.el('message').textContent, /版本已过期/);
  }
  {
    const app = await loaded();
    app.el('node').value = 'algae';
    app.api.failPreview = "INSTANCE_IN_USE: 'algae' is referenced by fish/prey";
    await app.el('delete').onclick();
    assert.match(app.el('message').textContent, /不能删除/);
    assert.match(app.el('message').textContent, /fish\/prey/);
    assert.equal(app.calls.filter(c => c.url === '/api/model/instances/transaction').length, 1, 'reference rejection must prevent apply');
  }
  {
    const app = await loaded();
    app.el('node').value = 'algae';
    await app.el('delete').onclick();
    const tx = app.calls.filter(c => c.url === '/api/model/instances/transaction');
    assert.deepEqual(tx.map(c => c.options.body.mode), ['preview', 'apply']);
    assert.equal(tx[0].options.body.operations[0].op, 'delete');
    assert.equal(tx[0].options.body.operations[0].name, 'algae');
    assert.equal(tx[1].options.body.preview_hash, 'preview-1');
    assert.ok(app.el('deleted').children.some(item => item.value === 'algae'), 'soft-deleted instance appears in deleted selector');
  }
}

run().catch(error => { console.error(error); process.exitCode = 1; });
