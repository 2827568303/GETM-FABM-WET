const assert = require('node:assert/strict');
const fs = require('node:fs');

const css = fs.readFileSync('3DWET/app/static/css/studio.css', 'utf8');
const workspace = fs.readFileSync('3DWET/app/static/css/scientific_workspace.css', 'utf8');
const base = fs.readFileSync('3DWET/app/static/css/style.css', 'utf8');
const workbench = fs.readFileSync('3DWET/app/static/css/workbench.css', 'utf8');
const template = fs.readFileSync('3DWET/app/templates/index.html', 'utf8');

assert.match(css, /--qgis-green:\s*#087b91/i, 'primary workbench accent is a restrained lake teal');
assert.match(css, /--qgis-green-dark:\s*#066b7c/i, 'hover and success accents use a deeper teal');
assert.match(css, /\.status-dot\.running\s*\{[^}]*background:\s*#c58a25/i, 'running state has a non-color-text amber status cue');
assert.match(base, /\.status-dot\.failed\s*\{[^}]*background:\s*var\(--danger\)/i, 'failure remains a distinct semantic error state');
assert.match(workspace, /:focus-visible\s*\{\s*outline:\s*3px solid/i, 'result controls retain a visible keyboard focus ring');
assert.match(workbench, /\.stat-card::before\s*\{[^}]*display:\s*none/i, 'decorative multicolour stat bars are removed');
assert.match(workbench, /\.workbench-heatmap-card\[data-dashboard-primary="true"\][^{]*\{[^}]*border-color:\s*#c5d0ca/i,
  'the primary dashboard canvas uses a neutral border');
assert.match(workbench, /--wb-paper:\s*#f4f1e8/i, 'the application uses a warm paper canvas');
assert.match(workbench, /--wb-lake:\s*#627986/i, 'lake slate is a low-chroma primary interaction color');
assert.match(workbench, /--wb-sage:\s*#748579/i, 'sage is available as a secondary hierarchy color');
assert.match(workbench, /--wb-ochre:\s*#927846/i, 'ochre distinguishes workflow/provenance without a saturated accent');
assert.match(template, /scientific_workspace\.css\?v=14/i, 'the updated scientific workspace stylesheet is versioned');
assert.match(workspace, /--sw-blue:\s*#627986/i, 'the visualization workspace inherits the lake-slate primary');
assert.match(workspace, /\.scientific-workspace \.btn-primary,[\s\S]*?background:\s*var\(--sw-blue\)/i,
  'scientific workspace primary and selected controls use the same lake-slate hue');
assert.match(workbench, /\.studio-mark\s*\{[^}]*background:\s*#e5ebe5/i, 'brand chrome uses a quiet sage surface');
assert.match(workbench, /body:has\(\.scientific-workspace\.active\) \.sidebar \.nav-item\.active\s*\{[^}]*background:\s*var\(--wb-lake-soft\)/i,
  'active visualization navigation stays lake-tinted instead of reverting to neutral gray');
assert.match(workbench, /\.nav-icon\s*\{[^}]*color:\s*currentColor[^}]*filter:\s*none/i,
  'navigation icons inherit the active/inactive text color without image filters');
assert.match(workbench, /#viz3d-plotly\s*\{[^}]*border-color:\s*#ccd5d1/i, 'the scientific plot frame uses a mineral separator');
assert.match(workbench, /\.workflow-strip b\s*\{[^}]*color:\s*var\(--wb-ochre\)/i, 'workflow/provenance uses a restrained ochre cue');
assert.match(workbench, /\.modal-overlay \.modal\s*\{[^}]*border-color:\s*var\(--wb-border\)/i, 'dialogs follow the shared surface and border system');
assert.match(workbench, /table\s*\{[^}]*background:\s*var\(--wb-surface\)/i, 'tables use the same warm-paper surfaces');
console.log('Scientific workbench theme checks passed');
