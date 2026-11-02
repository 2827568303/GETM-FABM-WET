const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const sourcePath = path.join(__dirname, '../../3DWET/app/static/js/result_files.js');
const templatePath = path.join(__dirname, '../../3DWET/app/templates/index.html');

class Element {
  constructor(tagName = 'div') {
    this.tagName = tagName.toUpperCase();
    this.children = [];
    this.listeners = {};
    this.attributes = {};
    this.style = {};
    this.disabled = false;
    this.checked = false;
    this.classList = { add() {} };
    this._text = '';
  }

  set textContent(value) {
    this._text = String(value ?? '');
    this.children = [];
  }

  get textContent() {
    return this._text + this.children.map(child => child.textContent).join('');
  }

  get innerText() { return this.textContent; }
  appendChild(child) { this.children.push(child); return child; }
  replaceChildren(...children) { this._text = ''; this.children = children; }
  addEventListener(type, handler) { this.listeners[type] = handler; }
  setAttribute(name, value) { this.attributes[name] = String(value); }
  getAttribute(name) { return this.attributes[name] ?? null; }
  click() {
    if (this.disabled) return undefined;
    return this.listeners.click?.({ target: this });
  }
  querySelectorAll(selector) {
    const all = [];
    const visit = element => {
      for (const child of element.children) { all.push(child); visit(child); }
    };
    visit(this);
    if (selector === 'button') return all.filter(element => element.tagName === 'BUTTON');
    if (selector === 'input[type=checkbox]:checked') {
      return all.filter(element => element.tagName === 'INPUT' && element.type === 'checkbox' && element.checked);
    }
    return [];
  }
}

class Document {
  constructor() {
    this.listeners = {};
    this.root = new Element('document');
    this.panel = new Element('div');
    this.panel.id = 'result-files-panel';
    this.root.appendChild(this.panel);
  }
  addEventListener(type, handler) { this.listeners[type] = handler; }
  createElement(tagName) { return new Element(tagName); }
  getElementById(id) {
    const visit = element => {
      if (element.id === id) return element;
      for (const child of element.children) {
        const match = visit(child);
        if (match) return match;
      }
      return null;
    };
    return visit(this.root);
  }
  querySelectorAll(selector) {
    if (selector === '#result-files-panel button') return this.panel.querySelectorAll('button');
    if (selector === '#result-files-panel input[type=checkbox]:checked') {
      return this.panel.querySelectorAll('input[type=checkbox]:checked');
    }
    return [];
  }
}

function response(data) {
  return { ok: true, status: 200, async json() { return data; } };
}

function inventory(casePath, revision, relativePath) {
  return {
    case_path: casePath,
    revision,
    run_output_path: path.join(casePath, 'output'),
    output_path: path.join(casePath, 'output'),
    busy: false,
    trash: { count: 0, bytes: 0, latest_token: null, error: null },
    files: [{
      relative_path: relativePath,
      absolute_path: path.join(casePath, relativePath),
      kind: 'netcdf',
      size: 3,
      modified: '2026-10-26T00:00:00Z',
      duplicate_group: null,
    }],
  };
}

test('case switch during duplicate scan does not restore the old pending message', async () => {
  const document = new Document();
  const window = {};
  const caseA = path.join('C:', 'cases', 'A');
  const caseB = path.join('C:', 'cases', 'B');
  const relativePath = 'output/run_retry/duplicate.nc';
  const getResponses = [
    inventory(caseA, 'revision-a', relativePath),
    inventory(caseB, 'revision-b', 'output/run_other/result.nc'),
  ];
  let resolveScan;
  const scanResponse = new Promise(resolve => { resolveScan = resolve; });
  const requests = [];
  const fetch = (url, options = {}) => {
    requests.push({ url, options });
    if (url === '/api/results/files' && !options.method) return Promise.resolve(response(getResponses.shift()));
    if (url === '/api/results/files/duplicates') return scanResponse;
    throw new Error(`Unexpected request: ${url}`);
  };

  vm.runInNewContext(fs.readFileSync(sourcePath, 'utf8'), { document, window, fetch });
  await window.loadResultFiles();

  const scanButton = document.querySelectorAll('#result-files-panel button')
    .find(button => button.textContent.includes('扫描完全相同的副本'));
  assert.ok(scanButton, 'initial case should render the duplicate scan button');
  const scanTask = scanButton.click();
  assert.equal(document.getElementById('result-files-message').textContent, '正在处理，请稍候…');

  await window.loadResultFiles();
  assert.ok(document.getElementById('result-files-panel').textContent.includes(caseB));
  resolveScan(response({
    revision: 'revision-a',
    groups: [{ id: 'duplicate-group-a', keep: 'output/keep.nc', paths: [relativePath, 'output/keep.nc'] }],
    duplicate_paths: [relativePath],
    files: inventory(caseA, 'revision-a', relativePath).files,
  }));
  await scanTask;

  const refreshedButton = document.querySelectorAll('#result-files-panel button')
    .find(button => button.textContent.includes('扫描完全相同的副本'));
  assert.ok(refreshedButton);
  assert.equal(refreshedButton.disabled, false);
  assert.equal(document.getElementById('result-files-message').textContent, '');
  assert.deepEqual(requests.map(request => request.url), [
    '/api/results/files',
    '/api/results/files/duplicates',
    '/api/results/files',
  ]);
});

test('index template cache-busts the updated result-files script', () => {
  const template = fs.readFileSync(templatePath, 'utf8');
  assert.match(template, /<script src="\/static\/js\/result_files\.js\?v=3"><\/script>/);
});
