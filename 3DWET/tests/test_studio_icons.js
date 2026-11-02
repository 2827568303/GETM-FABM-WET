const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const template = fs.readFileSync('3DWET/app/templates/index.html', 'utf8');
const iconSource = fs.readFileSync('3DWET/app/static/js/studio_icons.js', 'utf8');
const scripts = fs.readdirSync('3DWET/app/static/js')
  .filter(name => name.endsWith('.js'))
  .map(name => fs.readFileSync(`3DWET/app/static/js/${name}`, 'utf8')).join('\n');
const styles = ['workbench.css', 'workflow_navigation.css', 'academic_ui.css']
  .map(name => fs.readFileSync(`3DWET/app/static/css/${name}`, 'utf8')).join('\n');

assert.match(template, /<symbol id="studio-icon-[^"]+"/,
  'the app shell should define reusable technical SVG symbols');
assert.match(template, /<svg class="studio-icon[^"]*" aria-hidden="true"[^>]*><use href="#studio-icon-/,
  'static controls should reference the reusable icon family');
assert.match(template, /studio_icons\.js\?v=5/,
  'dynamic UI icon rendering should load the shared icon helper');
assert.match(scripts, /StudioIcons\.svg\(/,
  'dynamic UI should render technical icons through the shared helper');
assert.match(scripts, /StudioIcons\.node\(/,
  'DOM status and control updates should use actual SVG elements rather than markup in text nodes');
assert.match(iconSource, /const ICON_PATHS = Object\.freeze\(\{/,
  'the shared renderer should own the technical redraw paths, not only recolor shell glyphs');
assert.match(iconSource, /installIconPaths\(/,
  'the canonical paths should replace every shell symbol when the DOM is ready');
const iconRules = [...styles.matchAll(/(?:^|\n)\.studio-icon\s*\{([^}]*)\}/g)].map(match => match[1]);
assert.equal(iconRules.length, 2, 'base and academic theme should share the same icon drawing rules');
for (const rule of iconRules) {
  assert.match(rule, /stroke:\s*currentColor[^}]*stroke-width:\s*1\.7/i,
    'icons should keep the consistent restrained outline stroke');
  assert.match(rule, /stroke-linecap:\s*butt[^}]*stroke-linejoin:\s*bevel/i,
    'icons should use precise technical endpoints and non-spiking corners');
}
const referencedSymbols = new Set([...`${template}\n${scripts}`.matchAll(/href="#studio-icon-([a-z0-9-]+)"/g)].map(match => match[1]));
const symbolDefinitions = [...template.matchAll(/<symbol id="studio-icon-([^"]+)" viewBox="([^"]+)"([^>]*)>([\s\S]*?)<\/symbol>/g)];
assert.equal(symbolDefinitions.length, 58, 'the complete 58-symbol application icon set should remain covered');
const installed = new Map();
const iconWindow = {};
const fakeDocument = {
  readyState: 'loading',
  addEventListener() {},
  createElementNS(_namespace, tagName) {
    return { tagName, attributes: {}, setAttribute(key, value) { this.attributes[key] = value; }, appendChild() {} };
  }
};
vm.runInNewContext(iconSource, { window: iconWindow, document: fakeDocument });
const iconPaths = iconWindow.StudioIcons.iconPaths;
assert.equal(Object.keys(iconPaths).length, symbolDefinitions.length,
  'the shared renderer redraw catalog should cover every shell symbol');
assert.equal(new Set(Object.values(iconPaths).map(paths => paths.join(' '))).size, 58,
  'every stable symbol should have a distinct semantic drawing in the scientific glyph family');
const fakeRoot = { querySelector(selector) {
  const name = selector.slice('#studio-icon-'.length);
  return { replaceChildren(...nodes) { installed.set(name, nodes.map(node => node.attributes.d)); } };
} };
iconWindow.StudioIcons.installIconPaths(fakeRoot);
assert.equal(installed.size, symbolDefinitions.length, 'all 58 stable sprite IDs should receive the canonical path drawings');
for (const [, name] of symbolDefinitions) {
  assert.ok(Array.isArray(iconPaths[name]) && iconPaths[name].length > 0,
    `${name} should have a dedicated technical drawing`);
  assert.deepEqual(JSON.parse(JSON.stringify(installed.get(name))), JSON.parse(JSON.stringify(iconPaths[name])),
    `${name} should install its complete path geometry`);
}
for (const [, name, viewBox, attributes, body] of symbolDefinitions) {
  assert.equal(viewBox, '0 0 24 24', `${name} should use the shared 24px technical grid`);
  assert.doesNotMatch(attributes, /fill=/i, `${name} should inherit the single-color outline style`);
  assert.doesNotMatch(body, /<(?!path\b)[a-z][\w-]*\b/i, `${name} should use the common path-based drawing language`);
}
for (const name of referencedSymbols) {
  assert.match(template, new RegExp(`<symbol id="studio-icon-${name}"`),
    `the ${name} icon reference should resolve to a symbol in the shared sprite`);
}

const foodweb = template.match(/<symbol id="studio-icon-foodweb"[^>]*>([\s\S]*?)<\/symbol>/)?.[1] || '';
assert.equal((foodweb.match(/A2(?:\.2)? 2(?:\.2)? 0 1 0/g) || []).length, 6,
  'the food-web icon should show three distinct circular network nodes');
assert.ok((foodweb.match(/L\d+(?:\.\d+)? \d+(?:\.\d+)?/g) || []).length >= 6,
  'the food-web icon should use connected relationship paths rather than a decorative triangle');
assert.doesNotMatch(foodweb, /M5 5L19 7L12 19Z/,
  'the former outline triangle must not remain as the food-web mark');

const pictographs = /\p{Extended_Pictographic}/u;
assert.doesNotMatch(template, pictographs, 'the page template should not emit emoji pictographs');
assert.doesNotMatch(scripts.replaceAll('©', ''), pictographs,
  'dynamic UI scripts should not emit emoji pictographs (legal copyright attribution is retained)');
const oldPictogram = /[▣▦▷☰⌖▤◇⏮⏭⚒✓◉↥↶↷↺⊘⛶✕❚●○]/u;
assert.doesNotMatch(template, oldPictogram, 'the page template should not use Unicode pictograms as icons');
assert.doesNotMatch(scripts, oldPictogram, 'dynamic UI scripts should not use Unicode pictograms as icons');
assert.ok(/view_controls\.js\?v=8/.test(template) && /gridstudio\.js\?v=3/.test(template)
  && /ecology_network\.js\?v=34/.test(template) && /variable_guide\.js\?v=2/.test(template),
  'dynamic icon consumers should be cache-busted with their source changes');

console.log('technical SVG icon family and emoji-free UI sources PASS');
