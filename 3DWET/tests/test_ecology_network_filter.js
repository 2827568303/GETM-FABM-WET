const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const source = fs.readFileSync('3DWET/app/static/js/ecology_network.js', 'utf8');

class Element {
  constructor(id = '') { this.id = id; this.children = []; this.dataset = {}; this.style = {}; this.attributes = {}; this.listeners = {}; this.value = ''; this.textContent = ''; }
  append(...items) { this.children.push(...items); }
  replaceChildren(...items) { this.children = items; }
  setAttribute(key, value) { this.attributes[key] = String(value); }
  addEventListener(name, fn) { this.listeners[name] = fn; }
  querySelector(selector) { return selector === '#en-graph' ? this.children.find(child => child.id === 'en-graph' || child.attributes.id === 'en-graph') || null : null; }
  getBoundingClientRect() { return { width: 900, height: 470 }; }
}

async function main() {
  const elements = new Map();
  const get = id => { if (!elements.has(id)) elements.set(id, new Element(id)); return elements.get(id); };
  const filters = ['all', 'ecology', 'water_quality'].map(value => {
    const button = new Element('filter-' + value);
    button.dataset.networkFilter = value;
    return button;
  });
  const svg = get('en-svg');
  const document = {
    getElementById: get,
    createElement: tag => new Element(tag),
    createElementNS: (_ns, tag) => new Element(tag),
    querySelectorAll: selector => selector === '[data-network-filter]' ? filters : [],
  };
  const state = { activeCasePath: 'C:/cases/lake-a', fabmModules: [] };
  const nodes = [
    { name: 'phyto_a', model: 'wet/phytoplankton', long_name: 'Algae', enabled: true, parameters: {}, coupling: {} },
    { name: 'fish_a', model: 'wet/fish', long_name: 'Fish', enabled: true, parameters: {}, coupling: {} },
    { name: 'water_a', model: 'wet/abiotic_water', long_name: 'Water', enabled: true, parameters: {}, coupling: {} },
  ];
  const api = async url => {
    if (url === '/api/ecology/network') return { case_path: state.activeCasePath, revision: 'r1', nodes, edges: [], targets: [] };
    if (url === '/api/model/instances?domain=all') return { case_path: state.activeCasePath, revision: 'r1', instances: nodes, deleted: [] };
    throw new Error('Unexpected API request: ' + url);
  };
  const window = {};
  vm.runInNewContext(source, { document, window, state, api, navigate() {}, loadModuleParams() {}, ViewControls: null, console });
  await window.loadEcologyNetwork();

  const renderedNames = () => svg.children.find(child => child.id === 'en-graph' || child.attributes.id === 'en-graph').children
    .filter(child => child.attributes.role === 'button')
    .map(child => child.attributes['aria-label']);
  filters.find(button => button.dataset.networkFilter === 'ecology').listeners.click();
  assert.deepEqual(renderedNames(), ['phyto_a', 'fish_a'], 'ecology view retains ecological nodes and excludes water-quality nodes');
  filters.find(button => button.dataset.networkFilter === 'water_quality').listeners.click();
  assert.deepEqual(renderedNames(), ['water_a'], 'water-quality view retains water-quality nodes');
  console.log('ecology network category filtering renders ecology and water-quality nodes correctly PASS');
}

main().catch(error => { console.error(error); process.exitCode = 1; });
