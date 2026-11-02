const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const test = require('node:test');

const source = fs.readFileSync('3DWET/app/static/js/app.js', 'utf8');

function functionSource(name) {
  const start = source.indexOf(`function ${name}(`);
  assert.notEqual(start, -1, `missing ${name}`);
  const open = source.indexOf('{', start);
  let depth = 0;
  for (let i = open; i < source.length; i++) {
    if (source[i] === '{') depth++;
    if (source[i] === '}' && --depth === 0) return source.slice(start, i + 1);
  }
  throw new Error(`unterminated ${name}`);
}

test('saving another module preserves sources under mixed module checkboxes', () => {
  const partial = {
    value: 'cyanobacteria/*', checked: false, indeterminate: true,
    dataset: { partial: 'true' },
  };
  const fish = { value: 'JuFish/*', checked: true, indeterminate: false, dataset: { partial: 'false' } };
  const context = {
    _outputCfg: {
      selectionChanged: true,
      sources: ['cyanobacteria_sDW'],
      modules: [{ name: 'cyanobacteria', sources: ['cyanobacteria_sDW'], partially_selected: true }],
    },
    document: { querySelectorAll: (selector) => selector === '.out-src:checked' ? [partial, fish].filter((el) => el.checked) : [partial, fish] },
  };
  vm.runInNewContext(functionSource('_selectedOutputSources'), context);

  assert.deepEqual(Array.from(context._selectedOutputSources()), ['cyanobacteria_sDW', 'JuFish/*']);
});

