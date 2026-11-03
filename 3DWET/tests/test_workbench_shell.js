const assert = require('node:assert/strict');
const fs = require('node:fs');

const template = fs.readFileSync('3DWET/app/templates/index.html', 'utf8');
const stylesPath = '3DWET/app/static/css/workbench.css';
const styles = fs.existsSync(stylesPath) ? fs.readFileSync(stylesPath, 'utf8') : '';
const app = fs.readFileSync('3DWET/app/static/js/app.js', 'utf8');
const projectTools = fs.readFileSync('3DWET/app/static/js/projects_studio.js', 'utf8');
const appStyles = fs.readFileSync('3DWET/app/static/css/studio.css', 'utf8');

assert.ok(/class="page active workbench-home" id="page-dashboard"/.test(template),
  'the dashboard should be the canvas-first workbench home');
assert.ok(/id="dashboard-canvas"[^>]*aria-label="空间结果预览"/.test(template),
  'the primary result canvas region should be accessible by name');
assert.ok(/<details[^>]*id="dashboard-inspector"[^>]*>/.test(template),
  'the home inspector should be collapsible');
for (const group of ['case-data', 'configuration', 'run-review']) {
  assert.ok(new RegExp(`data-workflow="${group}"`).test(template),
    `left navigation should include the ${group} stage`);
}
assert.ok(/querySelector\('\[data-group-items="configuration"\]'\)/.test(projectTools),
  'the dynamic project import and physics settings route should be placed inside the configuration workflow group');
for (const route of ['dashboard', 'cases', 'preprocess', 'input', 'gridstudio', 'modules', 'ecology',
  'parameters', 'initial', 'time', 'run', 'system', 'map', 'viz2d', 'viz3d', 'vheat',
  'timeseries', 'calibrate', 'autocal']) {
  assert.ok(new RegExp(`data-page="${route}"`).test(template),
    `existing ${route} route should remain reachable`);
}
assert.ok(/\.workbench-home-grid/.test(styles),
  'the shell should provide a responsive canvas and inspector layout');
assert.ok(/const proxyMarkup = proxyCaseBadgeMarkup\(caseData\)/.test(app)
  && /<span class="case-name">\$\{label\}<\/span>\$\{proxyMarkup\}/.test(app)
  && /badge\.innerHTML = proxyMarkup \?/.test(app),
  'the active case identity should be separate from its proxy status badge');
const caseBadgeLayout = appStyles.slice(appStyles.lastIndexOf('.case-badge{'));
assert.ok(/display:flex;[^}]*flex-wrap:wrap;[^}]*overflow:visible/s.test(caseBadgeLayout)
  && /\.case-name\s*\{[^}]*overflow:hidden;[^}]*text-overflow:ellipsis;[^}]*white-space:nowrap/s.test(appStyles)
  && /\.topbar\s*\{height:auto;min-height:var\(--topbar-height\)/s.test(appStyles),
  'case names should truncate independently while status remains readable and the top bar can grow');
assert.ok(/workbench\.css\?v=9/.test(template) && /app\.js\?v=106/.test(template)
  && /i18n\.js\?v=19/.test(template)
  && /scientific_heatmap\.js\?v=6/.test(template)
  && /scientific_workspace\.css\?v=14/.test(template)
  && /scientific_workspace\.js\?v=19/.test(template)
  && /studio_icons\.js\?v=5/.test(template) && /viz3d\.js\?v=174/.test(template),
  'workbench CSS and inspector behavior should use fresh asset cache keys');
assert.ok(/class="workbench-heatmap" width="480" height="300" role="img"/.test(app),
  'dashboard heatmaps should retain readable intrinsic resolution and an accessible label');
assert.ok(/container\.classList\.remove\('empty-state'\)/.test(app),
  'rendered heatmap grids should leave the empty-state layout');
for (const kind of ['viz2d', 'viz3d']) {
  const railStart = template.indexOf(`id="${kind}-settings"`);
  const railEnd = template.indexOf('</aside>', railStart);
  const rail = template.slice(railStart, railEnd);
  assert.ok(rail.includes(`id="${kind === 'viz2d' ? 'viz2d-var' : 'viz3d-iso-var'}"`),
    `${kind} variable selection should live in the right inspector`);
  assert.ok(template.includes(`id="${kind}-inspector-toggle"`),
    `${kind} should expose a collapsible right inspector control`);
}
assert.ok(/sw-inspector-closed/.test(fs.readFileSync('3DWET/app/static/js/scientific_workspace.js', 'utf8')),
  'inspector control should expand/collapse the existing result rail');
assert.ok(/（待补充：参考图的具体路径或链接）/.test(
  fs.readFileSync('docs/audit/sol-bed-surface-ui-review-20261024.md', 'utf8')),
  'the missing reference image placeholder must stay explicit');

console.log('scientific workbench shell structure: canvas, inspector, navigation, routes and reference placeholder PASS');
