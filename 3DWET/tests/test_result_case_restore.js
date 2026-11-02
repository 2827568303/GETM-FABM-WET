const assert = require('node:assert/strict');
const fs = require('node:fs');

const source = fs.readFileSync('3DWET/app/static/js/app.js', 'utf8');

assert.match(source, /async function restoreCurrentCase\(/,
  'browser startup must reconcile the backend-restored case identity');
assert.match(source, /api\(['"]\/api\/case\/current['"]\)/,
  'case restoration must use the read-only identity endpoint');
assert.match(source, /state\.activeCasePath\s*=\s*data\.case_path/,
  'the restored path must become the frontend result identity');
assert.match(source, /const pending=\(async\(\)=>\{\s*if\(await restoreCurrentCase\(\)\)/,
  'result pages must be able to wait for case restoration');
assert.match(source, /state\.currentCasePending\s*=\s*pending/,
  'the bootstrap promise must be exposed to visualization initialization');
assert.match(source, /await state\.currentCasePending/,
  'visualization initialization must not race backend case restoration');
assert.match(source, /function clearResultInventory\(\)/,
  'a missing backend case must remove stale variable inventory');
assert.match(source, /state\.timesteps2d=0;state\.timesteps3d=0/,
  'a missing backend case must not retain a stale playback extent');
assert.match(source, /ScientificWorkspace\?\.empty\?\.\('viz2d','请先加载案例'\)/,
  'the empty case state must replace a white infinite-loading canvas');
assert.match(source, /if\(!state\.activeCasePath\)\{clearResultInventory\(\);return;\}/,
  '2D and 3D initialization must stop when no case is active');
assert.match(source, /data\.aborted\) \{ if\(current\(\)\)window\.ScientificWorkspace\?\.failure\('viz2d'/,
  'a cancelled current 2D request must leave loading with a visible message');
