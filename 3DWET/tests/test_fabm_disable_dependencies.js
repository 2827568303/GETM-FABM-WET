const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const source = fs.readFileSync('3DWET/app/static/js/app.js', 'utf8');
const start = source.indexOf('async function toggleModule(');
const end = source.indexOf('// ── 模型引擎开关', start);
const notices = [];
const calls = [];
const context = vm.createContext({
  state: { activeCase: 'isolated case' },
  confirmStudio: async () => true,
  api: async (url, options) => {
    calls.push({ url, options });
    return {
      success: false,
      blocked_by_couplings: true,
      warnings: ['burial 通过耦合 POM_phytoplankton_update1 引用 cyanobacteria'],
      repair_message: '先在生态网络重连列出的耦合端口，再禁用模块。',
    };
  },
  toast: (message, kind) => notices.push({ message, kind }),
});
vm.runInContext(source.slice(start, end), context);

(async () => {
  await context.toggleModule('cyanobacteria', true);
  assert.equal(calls.length, 1, 'blocked module operation must not retry as a forced disable');
  assert.equal(calls[0].options.body.force, undefined);
  assert.equal(notices.length, 1);
  assert.equal(notices[0].kind, 'warning');
  assert.match(notices[0].message, /先在生态网络重连/);
  assert.match(notices[0].message, /burial.*POM_phytoplankton_update1/);
  console.log('FABM module disable UI: dependency block is actionable and non-destructive PASS');
})().catch(error => { console.error(error); process.exitCode = 1; });
