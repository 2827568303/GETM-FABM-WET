const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const source = fs.readFileSync('3DWET/app/static/js/i18n.js', 'utf8');
const template = fs.readFileSync('3DWET/app/templates/index.html', 'utf8');
const catalog = JSON.parse(fs.readFileSync('3DWET/app/static/i18n/en.json', 'utf8'));
assert.ok(Number(template.match(/\/static\/js\/i18n\.js\?v=(\d+)/)?.[1]) > 14,
  'the page must use a new localization script URL so an existing WebView cannot keep the stale translator');
assert.ok(Number(template.match(/\/static\/js\/viz3d\.js\?v=(\d+)/)?.[1]) > 130,
  'the page must invalidate the cached 3D renderer after its legend copy changes');
assert.equal(catalog.messages['主视图选择'], 'Main view selection',
  'dashboard accessibility labels are part of the English workbench catalog');
for (const [source, translated] of [['案例与数据', 'Case and data'], ['运行与复核', 'Run and review']]) {
  assert.equal(catalog.messages[source], translated, `the workflow rail label “${source}” is translated`);
}
const bedNote = '静态预览隐藏湖底；半透明蓝色水面与湿网格侧壁展示体积；岸线为代理，未验证；陆地高程未提供';
assert.ok(template.includes(`<p class="sw-legend-note">${bedNote}</p>`),
  'the 3D legend note must describe the currently shown static preview and boundary provenance');
assert.equal(catalog.messages[bedNote], 'The static preview hides the bed; translucent blue water and wet-grid side walls show the basin volume; the shoreline is a proxy and unverified; land elevation is unavailable.',
  'the current 3D legend note must have an English translation');
const dashboardMessages = {
  '湖泊模型工作台': 'Lake model workbench',
  '以空间结果为主视图；案例与运行状态始终显示在顶部。': 'Spatial results are the primary view; case and run status stay visible at the top.',
  '二维结果': '2D results',
  '三维结果': '3D results',
  '空间结果预览': 'Spatial results preview',
  '当前案例的表层变量分布；选择地图、二维或三维结果可进入对应的完整视图。': 'Surface-variable distribution for the active case. Open the full map, 2D, or 3D view for more detail.',
  '打开地图工作区 ↗': 'Open map workspace ↗',
  '案例与数据': 'Case and data',
  '运行与复核': 'Run and review',
  '加载案例并运行模型后，此处显示空间结果预览。': 'Run a case to show its spatial results here.',
  '选择或加载案例': 'Select or load a case',
  '工作区检查器': 'Workspace inspector',
  '模型概况': 'Model overview',
  '水域格数': 'Wet cells',
  '垂向层数': 'Vertical layers',
  '生态模块': 'Ecological modules',
  '输出时步': 'Output time step',
  '最新时步表层均值': 'Latest timestep surface means',
  '常用工作流操作': 'Common workflow actions',
  '常用操作': 'Common actions',
  '选择/加载案例': 'Select / load case',
  '新建模型与网格': 'Create model and grid',
  '编辑模型参数': 'Edit model parameters',
  '运行模型': 'Run model',
};

function pageContext(storage, preferences) {
  const dashboardTextNodes = [];
  const dashboardActionGroup = {
    nodeType: 1,
    attrs: { 'aria-label': '主视图选择' },
    closest: () => null,
    matches: () => false,
    getAttribute(name) { return this.attrs[name] ?? null; },
    setAttribute(name, value) { this.attrs[name] = value; },
  };
  const root = {
    nodeType: 1,
    attrs: {},
    closest: () => null,
    matches: () => false,
    getAttribute(name) { return this.attrs[name] ?? null; },
    setAttribute(name, value) { this.attrs[name] = value; },
  };
  for (const label of Object.keys(dashboardMessages)) {
    dashboardTextNodes.push({ nodeType: 3, nodeValue: label, parentElement: root });
  }
  const document = {
    readyState: 'complete',
    documentElement: root,
    createTreeWalker: () => {
      let index = -1;
      const nodes = [dashboardActionGroup, ...dashboardTextNodes];
      return { nextNode: () => nodes[++index] ?? null };
    },
    dispatchEvent() {},
  };
  class Observer { observe() {} }
  const context = vm.createContext({
    window: {}, document, console, Intl, URLSearchParams, TextEncoder,
    CustomEvent: class { constructor(type, options) { this.type = type; this.detail = options.detail; } },
    MutationObserver: Observer,
    localStorage: {
      getItem: (key) => storage.get(key) ?? null,
      setItem: (key, value) => storage.set(key, value),
    },
    fetch: async (url, options = {}) => {
      if (String(url).startsWith('/static/i18n/en.json')) return { ok: true, json: async () => catalog };
      if (url === '/api/system/language' && options.method === 'PUT') {
        preferences.value = JSON.parse(options.body);
        return { ok: true, json: async () => ({ saved: true }) };
      }
      if (url === '/api/system/language') return { ok: true, json: async () => preferences.value };
      throw new Error(`Unexpected request: ${url}`);
    },
  });
  vm.runInContext(source, context);
  return { context, dashboardTextNodes, dashboardActionGroup };
}

async function waitFor(predicate) {
  for (let i = 0; i < 20; i++) {
    if (predicate()) return;
    await new Promise((resolve) => setTimeout(resolve, 0));
  }
  assert.fail('page locale initialization did not finish');
}

(async () => {
  const storage = new Map([['3dwet.locale', 'zh-CN']]);
  const preferences = { value: { locale: 'zh-CN', packs: [] } };

  const { context: firstPage } = pageContext(storage, preferences);
  await firstPage.window.StudioI18n.ready;
  await waitFor(() => firstPage.document.documentElement.lang === 'zh-CN');
  await firstPage.window.StudioI18n.setLocale('en-US');
  assert.equal(preferences.value.locale, 'en-US', 'Apply stores the selected locale in service preferences');
  assert.equal(firstPage.window.StudioI18n.t('仪表盘'), 'Dashboard');

  const { context: reloadedPage, dashboardTextNodes, dashboardActionGroup } = pageContext(storage, preferences);
  await reloadedPage.window.StudioI18n.ready;
  await waitFor(() => reloadedPage.document.documentElement.lang === 'en-US');
  assert.equal(reloadedPage.window.StudioI18n.locale(), 'en-US');
  assert.equal(reloadedPage.window.StudioI18n.t('仪表盘'), 'Dashboard');
  assert.deepEqual(dashboardTextNodes.map((node) => node.nodeValue), Object.values(dashboardMessages),
    'the visible dashboard shell is translated after a page reload');
  assert.equal(dashboardActionGroup.attrs['aria-label'], 'Main view selection',
    'dashboard accessibility labels are translated after a page reload');
  console.log('i18n page reload: persisted English locale restored from service preferences PASS');
})().catch((error) => { console.error(error); process.exitCode = 1; });
