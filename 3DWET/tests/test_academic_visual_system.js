const assert = require('node:assert/strict');
const fs = require('node:fs');
const { test } = require('node:test');
const template = fs.readFileSync('3DWET/app/templates/index.html', 'utf8');
const cssPath = '3DWET/app/static/css/academic_ui.css';
const css = fs.existsSync(cssPath) ? fs.readFileSync(cssPath, 'utf8') : '';
const ecology = fs.readFileSync('3DWET/app/static/js/ecology_network.js', 'utf8');

test('academic UI theme is linked after the existing shell and defines natural hierarchy colors', () => {
  assert.match(template,
    /<link rel="stylesheet" href="[^"]*workbench\.css(?:\?[^"]*)?">[\s\S]*?<link rel="stylesheet" href="[^"]*academic_ui\.css(?:\?[^"]*)?">/,
    'the academic theme should load after the workbench shell regardless of its cache-busting version');
  for (const token of ['--ui-paper', '--ui-stone', '--ui-ink', '--ui-lake', '--ui-moss', '--ui-ochre']) {
    assert.ok(css.includes(token), `theme token ${token} should be present`);
  }
  for (const selector of [
    /--ui-sidebar:\s*#[\da-f]{6}/i,
    /--ui-toolbar:\s*#[\da-f]{6}/i,
    /--ui-inspector:\s*#[\da-f]{6}/i,
    /--ui-canvas-surface:\s*#[\da-f]{6}/i
  ]) assert.match(css, selector, 'the shell should define distinct material surfaces for its working regions');
  assert.match(css, /--ui-sidebar:\s*#dfe5da/i, 'the navigation rail should read as a sage material, not gray');
  assert.match(css, /--ui-toolbar:\s*#d5dfdc/i, 'the tool row should read as lake slate');
  assert.match(css, /--ui-inspector:\s*#e2e9dd/i, 'the property inspector should carry a distinct reed tint');
  assert.match(css, /--ui-canvas-surface:\s*#faf8f1/i, 'the results canvas should retain warm paper contrast');
  assert.match(css, /\.sidebar\s*\{[^}]*background:\s*var\(--ui-sidebar\)/s);
  assert.match(css, /\.qgis-tool-bar\s*\{[^}]*background:\s*var\(--ui-toolbar\)/s);
  assert.match(css, /\.scientific-workspace \.sw-rail[^{}]*\{[^}]*background:\s*var\(--ui-inspector\)/s);
  assert.match(css, /\.workbench-primary-canvas\s*\{[^}]*background:\s*var\(--ui-canvas-surface\)/s);
  assert.match(css, /\.sidebar\s*\{[^}]*width:\s*248px/s, 'navigation should have a stable compact workstation rail');
  assert.match(css, /\.workbench-home-grid\s*\{[^}]*grid-template-columns:\s*minmax\(0,\s*1fr\)\s*292px/s,
    'dashboard layout should keep the result canvas dominant beside a fixed context inspector');
  assert.match(css, /\.workbench-primary-canvas\s*\{[^}]*min-height:\s*min\(72vh,\s*800px\)/s,
    'the main results canvas should own the available workspace height');
  assert.match(css, /\.scientific-workspace \.btn:hover\s*\{[^}]*background:\s*var\(--ui-lake-soft\)/s,
    'scientific workspace hover controls use the same subdued lake-slate tint');
  assert.match(css, /\.scientific-workspace select,[\s\S]*?color:\s*var\(--ui-ink\) !important; border-color:\s*var\(--ui-border\) !important/s,
    'scientific workspace form controls inherit the shared ink and mineral borders');
  assert.match(css, /\.workbench-inspector\s*\{[^}]*position:\s*sticky/s,
    'context properties should remain adjacent while the central workspace scrolls');
  assert.match(css, /\.form-row\s*\{[^}]*display:\s*grid/s, 'forms should use aligned scientific control rows');
  assert.match(css, /\.data-table tbody tr:nth-child\(even\)/, 'dense scientific tables should preserve scan lines');
  for (const selector of ['.sidebar', '.topbar', '.qgis-menu-bar', '.qgis-tool-bar', '.workflow-strip',
    '.card', '.stat-card', '.modal-overlay .modal', '.scientific-workspace .sw-shell', '#en-svg']) {
    assert.ok(css.includes(selector), `shared theme should cover ${selector}`);
  }
  assert.doesNotMatch(css, /(?:linear|radial)-gradient\s*\(/i);
  assert.match(css, /\.studio-icon\s*\{[^}]*stroke-width:\s*1\.7/i);
  for (const selector of ['.qgis-menu-item', '.qgis-tool-btn.active', '.pp-tab.active', '.data-table', '.toast']) {
    assert.ok(css.includes(selector), `shared theme should cover ${selector}`);
  }
  assert.doesNotMatch(css, /\.scientific-colorbar|\.workbench-heatmap\s*\{[^}]*filter/i,
    'interface theme must not alter quantitative palettes or field images');
});

test('all shared SVG symbols use the same 24px path-only line drawing system', () => {
  const block = template.match(/<svg class="studio-icon-sprite"[\s\S]*?<\/svg>/)?.[0] || '';
  const symbols = [...block.matchAll(/<symbol id="studio-icon-([^"]+)" viewBox="([^"]+)">([\s\S]*?)<\/symbol>/g)];
  assert.equal(symbols.length, 58, 'the current application sprite contains 58 symbols');
  assert.equal(new Set(symbols.map(match => match[1])).size, symbols.length, 'symbol ids remain unique');
  for (const [, name, viewBox, body] of symbols) {
    assert.equal(viewBox, '0 0 24 24', `${name} uses the shared 24px coordinate grid`);
    assert.ok(body.trim(), `${name} has a visible technical outline`);
    assert.doesNotMatch(body, /<(?:circle|rect|polygon|ellipse|line|polyline)\b/i,
      `${name} should be redrawn as intentional path geometry, not inherited toy-like primitives`);
    assert.match(body, /<path\b/, `${name} uses path-based outline geometry`);
  }
});

test('food-web display chrome uses muted role colors without changing graph relationships', () => {
  for (const color of ['#657e86', '#455e65', '#75836d', '#987746']) {
    assert.ok(ecology.toLowerCase().includes(color), `food-web display should use ${color}`);
  }
  for (const color of ['#74bec4', '#ffd166', '#ff8d5a', '#1d646f', '#7fc8c9']) {
    assert.ok(!ecology.toLowerCase().includes(color), `high-chroma chrome color ${color} should be removed`);
  }
  assert.match(ecology, /data-foodweb-cycle/);
  assert.match(ecology, /data-foodweb-featured-path/);
});
