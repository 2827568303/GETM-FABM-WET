const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const appSource = fs.readFileSync('3DWET/app/static/js/app.js', 'utf8');
const template = fs.readFileSync('3DWET/app/templates/index.html', 'utf8');
const css = fs.readFileSync('3DWET/app/static/css/studio.css', 'utf8');

function harness() {
    const elements = new Map();
    const get = id => {
        if (!elements.has(id)) elements.set(id, {innerHTML:'', textContent:'', hidden:false, style:{}});
        return elements.get(id);
    };
    const context = vm.createContext({
        state: {},
        $: get,
        toast: (message, kind) => context.toasts.push({message,kind}),
        toasts: [],
        escapeHtml: value => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch])),
        loadCase: (...args) => context.loads.push(args),
        loadExternalCase: (...args) => context.loads.push(args),
        showSaveAsModal: () => {}, deleteCase: () => {},
        loads: [],
    });
    const start = appSource.indexOf('function caseAction(');
    const end = appSource.indexOf('function refreshCaseStatistics(', start);
    vm.runInContext(appSource.slice(start, end), context);
    return {context, get};
}

const h = harness();
const proxy = {
    case_name: 'Engineering attempt', engineering_proxy: true, prepared: false,
    target_lake: '<Erken>', proxy_blockers: ['Missing spatial grid'],
    proxy_manifest: {
        sources:[{path:'sources/upstream.dat',role:'derived',purpose:'upstream file'},
                 {path:'missing/meteo.nc',role:'missing',purpose:'spatial forcing'}],
        geometry:{description:'No application-ready 3D grid'},
        forcing:{description:'No spatially mapped forcing'},
    },
};

h.context.renderProxyCaseStatus(proxy);
assert.equal(h.context.state.proxyCase, proxy, 'active case switch stores verified manifest context');
assert.match(h.get('case-badge').innerHTML, /代理工程准备未完成.*&lt;Erken&gt;.*非科学验证/);
for (const id of ['proxy-dashboard-notice','proxy-run-notice','proxy-viz2d-notice','proxy-viz3d-notice']) {
    assert.equal(h.get(id).hidden, false, `${id} is visible for the active proxy case`);
    assert.match(h.get(id).innerHTML, /科学验证状态：未完成/);
    assert.match(h.get(id).innerHTML, /代理\/派生/);
    assert.match(h.get(id).innerHTML, /缺失\/未完成/);
    assert.match(h.get(id).innerHTML, /Missing spatial grid/);
    assert.doesNotMatch(h.get(id).innerHTML, /<Erken>/, 'untrusted lake name is escaped');
}

h.context.state.cases = [proxy];
h.context.caseAction('load', 0);
assert.equal(h.context.loads.length, 0, 'an unprepared source record cannot be activated');
assert.equal(h.context.toasts[0].kind, 'warning');

const upstream = {
    case_name: 'Bryrup upstream reference', engineering_proxy: true, prepared: false,
    target_lake: 'Bryrup', proxy_blockers: ['No GETM grid'], proxy_manifest: {
        sources:[{path:'sources/hypsograph.dat',role:'upstream_reference',purpose:'GOTM reference'}],
        geometry:{description:'Not converted'}, forcing:{description:'Not converted'},
    },
};
h.context.renderProxyCaseStatus(upstream);
assert.match(h.get('proxy-dashboard-notice').innerHTML, /上游参考/);

const partial = {
    case_name:'Engineering Proxy - Erken - partial no GHG', engineering_proxy:true,
    partial_engineering_proxy:true, prepared:true, target_lake:'Erken', proxy_blockers:[],
    proxy_manifest:{partial_engineering_proxy:true,disabled_modules:['wet/inorganic_carbon','wet/methane'],
        sources:[],geometry:{description:'source bathymetry'},forcing:{description:'single-station proxy',confirmed:false}},
};
assert.match(h.context.proxyCaseBadgeMarkup(partial), /部分代理工程运行/);
h.context.renderProxyCaseStatus(partial);
assert.match(h.get('proxy-dashboard-notice').innerHTML, /部分工程运行：关闭模块/);
assert.match(h.get('proxy-dashboard-notice').innerHTML, /wet\/inorganic_carbon、wet\/methane/);

h.context.renderProxyCaseStatus({case_name:'Ordinary case'});
assert.equal(h.context.state.proxyCase, null, 'switching to an ordinary case clears proxy state');
assert.equal(h.get('case-badge').innerHTML, 'Ordinary case');
for (const id of ['proxy-dashboard-notice','proxy-run-notice','proxy-viz2d-notice','proxy-viz3d-notice']) {
    assert.equal(h.get(id).hidden, true, `${id} clears when the active case is ordinary`);
    assert.equal(h.get(id).innerHTML, '');
}

assert.match(appSource, /proxyCaseBadgeMarkup\(c, true\)/, 'case manager shows a manifest-backed badge');
assert.match(appSource, /disabled title="输入未齐，不可加载运行"/, 'case manager disables loading incomplete preparations');
assert.match(template, /id="proxy-dashboard-notice"/);
assert.match(template, /id="proxy-run-notice"/);
assert.match(template, /id="proxy-viz2d-notice"/);
assert.match(template, /id="proxy-viz3d-notice"/);
assert.match(css, /\.proxy-case-badge/);
assert.match(css, /\.proxy-case-notice\[hidden\]/);
console.log('proxy case disclaimer persists across case list, dashboard, run and result views PASS');
