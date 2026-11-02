const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

const source = fs.readFileSync(path.join(__dirname, '../app/static/js/observation_manager.js'), 'utf8');
const window = {};
vm.runInNewContext(source, { window, document: { addEventListener() {} }, console, fetch() {} });
const manager = window.ObservationManager;

assert.ok(manager, 'manager API is exposed');
assert.deepEqual(Array.from(manager.parseSourcePaths('C:\\obs\\TEMP.obs\n C:\\obs\\DO.obs')), [
  'C:\\obs\\TEMP.obs', 'C:\\obs\\DO.obs'
]);
assert.throws(() => manager.buildPreviewRequest('C:\\obs\\TEMP.obs', {}, ''), /显式/,
  'preview requires a positive explicit time-gap limit');
assert.throws(() => manager.buildPreviewRequest('C:\\obs\\TEMP.obs', {}, '0'), /正数/);
const request = manager.buildPreviewRequest('C:\\obs\\TEMP.obs\nC:\\obs\\DO.obs', {
  'C:\\obs\\TEMP.obs': { variable: 'temp', unit: 'degC', lake_id: 'Lake Ravn' },
  'C:\\obs\\DO.obs': { variable: 'abiotic_water_sO2W', unit: 'mg/L', lake_id: 'Lake Ravn' }
}, '3.5');
assert.deepEqual(Array.from(request.files), ['C:\\obs\\TEMP.obs', 'C:\\obs\\DO.obs']);
assert.equal(request.max_time_gap_hours, 3.5);
const ravnPaths = ['C:\\obs\\TEMP.obs', 'C:\\obs\\DO.obs', 'C:\\obs\\CHLA.obs'];
const ravnOverrides = {
  [ravnPaths[0]]: { variable: 'temp', unit: 'degC' },
  [ravnPaths[1]]: { variable: 'abiotic_water_sO2W', unit: 'mg/L' },
  [ravnPaths[2]]: { variable: 'wet_chla_calculator_result', unit: 'ug/L' }
};
const ravnRequest = manager.buildPreviewRequest(ravnPaths.join('\n'), {
  __version__: 'observation-ui-v2',
  'TEMP.obs': { lake_id: 'Lake Ravn', station_id: 'Ravn' },
  'DO.obs': { lake_id: 'Lake Ravn', station_id: 'Ravn' },
  'CHLA.obs': { lake_id: 'Lake Ravn', station_id: 'Ravn' }
}, '2', ravnOverrides);
assert.deepEqual(Array.from(ravnRequest.files), ravnPaths);
const widePath = 'C:\\obs\\Erken-profile.csv';
const wideMapping = { header_row: 70, time_column: 'TIMESTAMP', value_column: 'TW_-1.0m',
  depth_m_mode: 'constant', depth_m_constant: 1 };
const wideRequest = manager.buildPreviewRequest(widePath, { [widePath]: wideMapping }, '3');
assert.deepEqual(JSON.parse(JSON.stringify(wideRequest.mappings[widePath])), wideMapping,
  'explicit wide-file column and depth mappings are preserved for preview/signature');
for (const [path, variable, unit] of [
  [ravnPaths[0], 'temp', 'degC'],
  [ravnPaths[1], 'abiotic_water_sO2W', 'mg/L'],
  [ravnPaths[2], 'wet_chla_calculator_result', 'ug/L']
]) {
  assert.deepEqual({ variable: ravnRequest.mappings[path].variable, unit: ravnRequest.mappings[path].unit,
    lake_id: ravnRequest.mappings[path].lake_id }, { variable, unit, lake_id: 'Lake Ravn' });
}
const alteredOverrides = { ...ravnOverrides, [ravnPaths[0]]: { variable: 'other', unit: 'degC' } };
assert.notEqual(manager.previewFingerprint(ravnPaths.join('\n'), {}, ravnOverrides, '2'),
  manager.previewFingerprint(ravnPaths.join('\n'), {}, alteredOverrides, '2'),
  'per-file mapping changes produce a new preview fingerprint');
assert.match(source, /obs-file-mappings/);
assert.match(source, /source_file.*模型变量/);
assert.equal(manager.previewIsFresh({ preview: { preview_signature: 'sig' }, signature: 'sig', fingerprint: 'a' }, 'a'), true);
assert.equal(manager.previewIsFresh({ preview: { preview_signature: 'changed' }, signature: 'sig', fingerprint: 'a' }, 'a'), false,
  'a changed preview signature invalidates the preview');
assert.equal(manager.previewIsFresh({ preview: { preview_signature: 'sig' }, signature: 'sig', fingerprint: 'a' }, 'b'), false);
assert.match(manager.escapeHtml('<script>'), /&lt;script&gt;/);
const html = fs.readFileSync(path.join(__dirname, '../app/templates/index.html'), 'utf8');
assert.match(html, /id="obs-manager"/);
assert.match(html, /id="obs-max-gap"/);
assert.match(html, /id="obs-header-row"/);
assert.match(html, /id="obs-depth-constant"/);
assert.match(html, /id="obs-preview"/);
assert.match(html, /id="obs-apply"/);
assert.match(html, /id="obs-file-mappings"/);
assert.doesNotMatch(html, /\.obs 默认使用文件名/);
assert.match(source, /\/api\/calibration\/observations\/preview/);
assert.match(source, /\/api\/calibration\/observations\/apply/);
assert.match(source, /\/api\/system\/list_dir/);
console.log('observation manager tests passed');
