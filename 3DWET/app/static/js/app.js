// 3DWET Web App - Main JavaScript
let state = {
    activeCase: null,
    activeCasePath: null,
    cases: [],
    fabmModules: [],
    fabmCategories: {},
    variables2d: [],
    variables3d: [],
    charts: {},
    runPollTimer: null,
    calibPollTimer: null,
    calibJobId: null,
    calibPointsLoaded: false,
    calLastData: null,
    currentParams: [],
};

// ── Utilities ─────────────────────────────────────────────────────────
function $(id) { return document.getElementById(id); }
function fmt(v, d=2) { return v === null || v === undefined || isNaN(v) ? '-' : Number(v).toFixed(d); }
function fmtSize(bytes) {
    if (bytes === null || bytes === undefined) return '-';
    if (bytes === 0) return '0 B';
    const units = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return (bytes / Math.pow(1024, i)).toFixed(i === 0 ? 0 : 1) + ' ' + units[i];
}
function toast(msg, type='info') {
    const t = document.createElement('div');
    t.className = `toast ${type}`;
    t.textContent = msg;
    $('toast-container').appendChild(t);
    setTimeout(() => t.remove(), 3000);
}
function closeModal(id) { $(id).classList.remove('active'); }
function showModal(id) { $(id).classList.add('active'); }

async function api(url, opts={}) {
    return new Promise((resolve) => {
        const xhr = new XMLHttpRequest();
        const method = opts.method || 'GET';
        xhr.open(method, url, true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.onload = function() {
            try {
                resolve(JSON.parse(xhr.responseText));
            } catch(e) {
                resolve({error: 'Invalid JSON response: ' + xhr.responseText.substring(0, 200)});
            }
        };
        xhr.onerror = function() {
            resolve({error: 'Network error (XHR) - cannot connect to server'});
        };
        xhr.ontimeout = function() {
            resolve({error: 'Request timeout'});
        };
        xhr.timeout = opts.timeout || 30000;
        if (opts.body) {
            xhr.send(JSON.stringify(opts.body));
        } else {
            xhr.send();
        }
    });
}

// ── Navigation ────────────────────────────────────────────────────────
function navigate(page) {
    document.querySelectorAll('.nav-item').forEach(n => n.classList.toggle('active', n.dataset.page === page));
    document.querySelectorAll('.page').forEach(p => p.classList.toggle('active', p.id === `page-${page}`));
    const titles = {dashboard:'仪表盘',cases:'案例管理',preprocess:'前处理',input:'输入数据',modules:'模块配置',parameters:'参数编辑',initial:'初始条件',time:'时间设置',run:'运行控制',map:'地图视图',viz2d:'2D可视化',viz3d:'3D可视化',vheat:'垂向热图',timeseries:'时间序列',calibrate:'率定分析',autocal:'自动率定'};
    $('page-title').textContent = titles[page] || page;
    // Page-specific init
    if (page === 'cases') loadCases();
    if (page === 'preprocess') { initPreprocess(); renderEngines(); }
    if (page === 'input') loadInputData();
    if (page === 'modules') { loadEngines(); renderModuleCards(); }
    if (page === 'parameters') loadParamModules();
    if (page === 'initial') loadInitConditions();
    if (page === 'time') { loadTimeSettings(); loadOutputConfig(); }
    if (page === 'map') loadMapGrid();
    if (page === 'viz2d') initViz2d();
    if (page === 'viz3d') initViz3d();
    if (page === 'vheat') initVHeat();
    if (page === 'timeseries') initTimeseries();
    if (page === 'calibrate') initCalibrate();
    if (page === 'autocal') initAutoCal();
}

document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => navigate(item.dataset.page));
});

// 点击空白处关闭案例右键菜单
document.addEventListener('mousedown', (e) => {
    const m = document.getElementById('case-ctx-menu');
    if (m && m.style.display === 'block' && !m.contains(e.target)) m.style.display = 'none';
});

// ── Case Management ───────────────────────────────────────────────────
async function loadCases() {
    const cases = await api('/api/cases');
    const tbody = $('case-table').querySelector('tbody');
    tbody.innerHTML = '';
    if (cases.error) { tbody.innerHTML = `<tr><td colspan="8">[XHR_DEBUG] ${cases.error}</td></tr>`; return; }
    state.cases = cases;
    const activePath = (state.activeCasePath || '').toLowerCase();
    cases.forEach((c, idx) => {
        const tr = document.createElement('tr');
        const isActive = activePath && c.path && c.path.toLowerCase() === activePath;
        if (isActive) tr.style.background = 'rgba(37,99,235,0.15)';
        let nameCell = `<strong>${c.name}</strong>`;
        if (isActive) {
            nameCell += ` <span style="font-size:10px;background:#2563eb;color:white;padding:1px 6px;border-radius:8px;">当前</span>`;
        }
        if (c.external) {
            nameCell += ` <span style="font-size:10px;background:var(--accent);color:white;padding:1px 6px;border-radius:8px;">外部</span>` +
                        `<div style="font-size:11px;color:var(--text-muted);margin-top:2px;word-break:break-all;">${c.path}</div>`;
        }
        tr.style.cursor = 'context-menu';
        tr.setAttribute('oncontextmenu', `openCaseCtxMenu(event, ${idx})`);
        tr.innerHTML = `
            <td>${nameCell}</td>
            <td>${c.has_bathymetry ? '✅' : '❌'}</td>
            <td>${c.has_fabm ? '✅' : '❌'}</td>
            <td>${c.has_meteo ? '✅' : '❌'}</td>
            <td>${c.has_rivers ? '✅' : '❌'}</td>
            <td>${c.has_2d_output ? '✅' : '❌'}</td>
            <td>${c.has_3d_output ? '✅' : '❌'}</td>
            <td style="white-space:nowrap;">
                <button class="btn btn-primary btn-sm" onclick="caseAction('load', ${idx})">加载</button>
                <button class="btn btn-sm" onclick="caseAction('saveas', ${idx})">另存为</button>
                <button class="btn btn-danger btn-sm" onclick="caseAction('delete', ${idx})">删除</button>
            </td>`;
        tbody.appendChild(tr);
    });
}

function caseAction(action, idx) {
    const c = (state.cases || [])[idx];
    if (!c) return;
    if (action === 'load') {
        if (c.external) loadExternalCase(c.path);
        else loadCase(c.name);
    } else if (action === 'saveas') {
        showSaveAsModal(c);
    } else if (action === 'delete') {
        deleteCase(c);
    }
}

function applyLoadedCase(data) {
    state.activeCase = data.case_name;
    state.activeCasePath = data.case_path;
    state.fabmModules = data.fabm.modules || [];
    state.fabmCategories = data.fabm.categories || {};
    if (data.run_info && data.run_info.nlev) setNlev(data.run_info.nlev);
    $('case-badge').style.display = 'inline';
    $('case-badge').textContent = data.case_name;
    $('footer-status').textContent = `案例: ${data.case_name}`;
    // Update dashboard
    $('stat-water').textContent = '...';
    $('stat-nlev').textContent = data.run_info.nlev || '-';
    $('stat-modules').textContent = data.fabm.total_modules || '-';
    // 水域格数来自运行估算（读 bathymetry，轻量）
    api('/api/run/estimate').then(est => {
        if (!est.error && typeof est.nwater === 'number') $('stat-water').textContent = est.nwater.toLocaleString();
        else $('stat-water').textContent = '-';
    }).catch(() => { $('stat-water').textContent = '-'; });
    // Output.yaml sync_interval=0 sanity check banner
    const banner = $('output-warning-banner');
    if (banner) {
        if (data.output_warning) {
            banner.style.display = 'block';
            banner.innerHTML = `<strong>⚠️ 输出配置警告：</strong> ${data.output_warning} <button class="btn btn-primary btn-sm" style="margin-left:8px;" onclick="fixSyncInterval()">一键修复 (设为 1)</button>`;
        } else {
            banner.style.display = 'none';
        }
    }
    if (data.output_warning) {
        toast(data.output_warning, 'warning');
    }
    // 输出文件存在但没有任何时间记录（numrecs=0：上次运行异常中断或 sync_interval=0）
    if (data.has_results && data.output_ntimesteps === 0) {
        const msg = '输出文件存在但没有任何时间记录（上次运行可能异常中断或 sync_interval=0），修复输出配置后需重新运行模型才有结果数据。';
        toast(msg, 'warning');
        const nb = $('output-warning-banner');
        if (nb) {
            nb.style.display = 'block';
            nb.innerHTML = `<strong>⚠️ 无结果数据：</strong> ${msg}`;
        }
    }
    // Load variables if results exist（无结果时也会注入“水深(地形)”占位变量，
    // 保证 2D/3D/地图视图至少能看到湖泊网格与湖盆）
    loadVariables();
    if (data.has_results) {
        loadDashboardSummary();
    }
    // 案例切换后地图数据属于旧案例，必须重置；若用户正停在地图页则立即重载
    resetMapView();
    toast(`已加载案例: ${data.case_name}`, 'success');
    navigate('dashboard');
    // 刷新一次运行状态面板（服务重启后 run_status 回到 idle，页面应如实显示）
    pollRunStatus();
    // 刷新案例管理表（高亮当前案例）
    loadCases();
}

async function loadCase(name) {
    const data = await api('/api/case/load', {method:'POST', body:{case_name:name}});
    if (data.error) { toast(data.error, 'error'); return; }
    applyLoadedCase(data);
}

async function loadExternalCase(path) {
    const data = await api('/api/case/open', {method:'POST', body:{path: path}});
    if (data.error || data.success === false) { toast(data.error || '打开失败', 'error'); return; }
    applyLoadedCase(data);
}

async function openCaseByPath() {
    const p = $('open-case-path').value.trim();
    if (!p) { toast('请输入案例目录路径', 'error'); return; }
    const data = await api('/api/case/open', {method:'POST', body:{path: p}});
    if (data.error || data.success === false) { toast(data.error || '打开失败', 'error'); return; }
    applyLoadedCase(data);
    $('open-case-path').value = '';
    loadCases();
}

// ── 本机文件夹选择窗口（Windows 资源管理器风格「浏览文件夹」）───────────
let _pickTimer = null;

// ── 页面内目录浏览（不依赖系统弹窗的可靠选择方式）──────────────────
let _dbPath = '';

function toggleDirBrowser(show) {
    const el = $('dir-browser');
    if (!el) return;
    const willShow = show !== undefined ? show : el.style.display === 'none';
    el.style.display = willShow ? 'block' : 'none';
    if (willShow) {
        const input = $('open-case-path');
        const startPath = (input && input.value.trim()) || state.activeCasePath || '';
        loadDirBrowser(startPath);
    }
}

async function loadDirBrowser(path) {
    const list = $('db-list');
    const pathEl = $('db-path');
    if (!list) return;
    const r = await api(`/api/system/list_dir?path=${encodeURIComponent(path || '')}`);
    if (r.error) { list.innerHTML = `<div class="db-item" style="color:var(--danger);">${escapeHtml(r.error)}</div>`; return; }
    _dbPath = r.path || '';
    if (pathEl) pathEl.value = _dbPath;
    const dirs = (r.entries || []).filter(e => e.is_dir);
    const files = (r.entries || []).filter(e => !e.is_dir);
    list.innerHTML =
        `<div class="db-item db-dir" onclick="loadDirBrowser('${escapeAttr(r.parent || '')}')">⬆ 上一级${r.parent ? '（' + escapeHtml(r.parent) + '）' : ''}</div>` +
        dirs.map(e => `<div class="db-item db-dir" title="${escapeAttr(e.path)}" onclick="loadDirBrowser('${escapeAttr(e.path)}')">📁 ${escapeHtml(e.name)}</div>`).join('') +
        (files.length ? `<div class="db-sep">📄 文件（${files.length}）</div>` : '') +
        files.slice(0, 50).map(e => `<div class="db-item db-file" title="${escapeAttr(e.path)}" onclick="loadDirBrowser('${escapeAttr(e.path)}')">${escapeHtml(e.name)}</div>`).join('') +
        (!dirs.length && !files.length ? '<div class="db-item">（空目录）</div>' : '');
}

function dirBrowserUp() {
    if (_dbPath) loadDirBrowser(_dbPath.replace(/[\\/]+$/, ''));
}

async function dirBrowserUse() {
    const input = $('open-case-path');
    if (!input || !_dbPath) return;
    input.value = _dbPath;
    const statusEl = $('pick-folder-status');
    if (statusEl) { statusEl.style.display = 'block'; statusEl.innerHTML = `<span style="color:var(--success)">已选择：${escapeHtml(_dbPath)}</span>`; }
    clearInterval(_pickTimer);
    await openCaseByPath();
}

async function pickCaseFolder(fixedPath) {
    const statusEl = $('pick-folder-status');
    const input = $('open-case-path');
    const start = fixedPath || input.value.trim() || state.activeCasePath || '';
    if (statusEl) { statusEl.style.display = 'block'; statusEl.innerHTML = '<span>正在启动文件夹选择窗口…</span>'; }
    const r = await api('/api/system/pick_folder', {method:'POST', body:{start_dir: start}});
    if (r.error) { if (statusEl) statusEl.innerHTML = `<span style="color:var(--danger)">${r.error}</span>`; return; }
    if (statusEl) statusEl.innerHTML = '<span style="color:var(--info)">请在弹出的「浏览文件夹」窗口中选择案例目录，然后点【确定】…</span>';
    clearInterval(_pickTimer);
    const deadline = Date.now() + 120000;
    _pickTimer = setInterval(async () => {
        const res = await api('/api/system/pick_folder_result');
        if (res.error) {
            clearInterval(_pickTimer);
            if (statusEl) statusEl.innerHTML = `<span style="color:var(--danger)">${res.error}</span>`;
            return;
        }
        if (!res.done) {
            if (Date.now() > deadline) {
                clearInterval(_pickTimer);
                if (statusEl) statusEl.innerHTML =
                    '<span style="color:var(--warning)">没有检测到弹出的选择窗口（可能是浏览器环境限制）。' +
                    '请改用右侧「📂 浏览目录」，在页面内逐级选择案例目录，功能完全一致。</span>';
            }
            return;
        }
        clearInterval(_pickTimer);
        if (!res.path) {
            if (statusEl) statusEl.innerHTML = '<span style="color:var(--text-muted)">已取消（未选择目录）</span>';
            return;
        }
        if (statusEl) statusEl.innerHTML = `<span style="color:var(--success)">已选择：${res.path}</span>`;
        input.value = res.path;
        await openCaseByPath();
    }, 600);
}

async function exploreCasePath(path) {
    const r = await api('/api/system/explore', {method:'POST', body:{path}});
    toast(r.error || '已在资源管理器中打开', r.error ? 'error' : 'success');
}

// ── 案例表格右键菜单 ────────────────────────────────────────────────
let _ctxTarget = null;
function openCaseCtxMenu(ev, idx) {
    ev.preventDefault();
    const c = (state.cases || [])[idx];
    if (!c) return;
    _ctxTarget = c;
    const menu = $('case-ctx-menu');
    const title = $('case-ctx-title');
    if (title) title.textContent = c.path || c.name;
    menu.style.display = 'block';
    const w = menu.offsetWidth || 220, h = menu.offsetHeight || 180;
    let x = ev.clientX, y = ev.clientY;
    if (x + w > window.innerWidth - 8) x = window.innerWidth - w - 8;
    if (y + h > window.innerHeight - 8) y = window.innerHeight - h - 8;
    menu.style.left = x + 'px';
    menu.style.top = y + 'px';
}
function closeCaseCtxMenu() { const m = $('case-ctx-menu'); if (m) m.style.display = 'none'; }
function ctxAction(action, useParent) {
    const c = _ctxTarget;
    if (!c) return;
    closeCaseCtxMenu();
    if (action === 'explore') { exploreCasePath(c.path); return; }
    if (action === 'pick') {
        pickCaseFolder(useParent ? String(c.path || '').replace(/[\\/]+$/, '') : c.path);
        navigate('cases');
        return;
    }
    if (action === 'load') { if (c.external) loadExternalCase(c.path); else loadCase(c.name); return; }
    if (action === 'saveas') { showSaveAsModal(c); return; }
}

let saveAsCase = null;
function showSaveAsModal(c) {
    saveAsCase = c;
    $('save-as-source').textContent = `源案例: ${c.path}`;
    $('save-as-dest').value = '';
    $('save-as-include-results').checked = false;
    showModal('modal-save-as');
}

async function confirmSaveAs() {
    if (!saveAsCase) return;
    const dest = $('save-as-dest').value.trim();
    if (!dest) { toast('请输入目标目录路径', 'error'); return; }
    const btn = $('save-as-confirm-btn');
    btn.disabled = true; btn.textContent = '保存中...';
    const res = await api('/api/case/save_as', {method:'POST', timeout: 600000,
        body: {source_path: saveAsCase.path, dest_path: dest, include_results: $('save-as-include-results').checked}});
    btn.disabled = false; btn.textContent = '保存';
    if (res.error) { toast(res.error, 'error'); return; }
    closeModal('modal-save-as');
    toast(`已另存到 ${res.dest_path}（${res.n_files} 个文件，${fmtSize(res.size_bytes)}），并已加入案例列表`, 'success');
    loadCases();
}

function _samePath(a, b) {
    return String(a).replace(/\\/g, '/').toLowerCase() === String(b).replace(/\\/g, '/').toLowerCase();
}

async function deleteCase(c) {
    const input = prompt(`确定要删除案例吗？此操作不可恢复！\n\n${c.path}\n\n如确认，请输入案例名称 "${c.name}"：`);
    if (input === null) return;
    if (input.trim() !== c.name) { toast('案例名称不匹配，已取消删除', 'error'); return; }
    const res = await api('/api/case/delete', {method:'POST', body:{path: c.path}});
    if (res.error) { toast(res.error, 'error'); return; }
    toast(`案例已删除（清理 ${res.n_files} 个文件，释放 ${fmtSize(res.size_bytes)}）`, 'success');
    if (state.activeCasePath && _samePath(state.activeCasePath, c.path)) {
        state.activeCase = null;
        state.activeCasePath = null;
        $('case-badge').style.display = 'none';
        $('footer-status').textContent = '未加载案例';
    }
    loadCases();
}

async function fixSyncInterval() {
    if (!state.activeCase) { toast('请先加载案例', 'error'); return; }
    if (!confirm('将 output.yaml 的 sync_interval 从 0 改为 1（每个时间步同步输出）？')) return;
    const res = await api('/api/config/output', {
        method: 'POST',
        body: JSON.stringify({ sync_interval: 1 })
    });
    if (res.success) {
        toast(`已修复 sync_interval = ${res.sync_interval}`, 'success');
        const banner = $('output-warning-banner');
        if (banner) banner.style.display = 'none';
        loadOutputConfig();
    } else {
        toast(res.error || '修复失败', 'error');
    }
}

async function loadOutputConfig() {
    if (!state.activeCase) return;
    const cfg = await api('/api/config/output');
    if (cfg.error) return;
    const unit = $('output-time-unit');
    const step = $('output-time-step');
    const sync = $('output-sync-interval');
    if (unit) unit.value = cfg.time_unit || 'day';
    if (step) step.value = cfg.time_step || 1;
    if (sync) sync.value = cfg.sync_interval || 1;
    renderOutputSubscription(cfg);
}

// ── Output variable subscription (P0) ─────────────────────────────────
let _outputCfg = null;

function renderOutputSubscription(cfg) {
    _outputCfg = cfg;
    const box = $('output-modules');
    const est = $('output-estimate');
    if (!box) return;
    const sources = cfg.sources || ['*'];
    const wildcard = sources.includes('*');
    const hydro = cfg.hydro_vars || [];
    const mods = cfg.modules || [];
    const checked = s => wildcard || sources.includes(s) || sources.includes(s + '/*');

    let html = hydro.map(v => `
        <label style="font-size:12px;white-space:nowrap;">
            <input type="checkbox" class="out-src" value="${v}" ${checked(v) ? 'checked' : ''}> ${v}
        </label>`).join('');
    if (mods.length) {
        html += `<div style="width:100%;font-size:11px;color:var(--text-muted);margin-top:4px;">生态模块（模块名/*）:</div>`;
        html += mods.map(m => `
            <label style="font-size:12px;white-space:nowrap;" title="${m.model || ''}">
                <input type="checkbox" class="out-src" value="${m.name}/*" ${checked(m.name) ? 'checked' : ''}> ${m.name}
            </label>`).join('');
    } else {
        html += `<div style="font-size:11px;color:var(--text-muted);">（fabm.yaml 中未解析到 instances）</div>`;
    }
    box.innerHTML = html;

    const e = cfg.estimate || {};
    if (est) {
        if (!e.available) {
            est.innerHTML = `<span style="font-size:12px;color:var(--text-muted);">体积预估不可用（需要 getm.inp 时间范围 + 地形）</span>`;
        } else {
            const gb = e.gb;
            const color = gb >= 2 ? 'var(--danger)' : (gb >= 0.5 ? 'var(--warning)' : 'var(--success)');
            est.innerHTML = `<div style="font-size:12px;">
                <strong style="color:${color};">预计输出 ≈ ${gb >= 1 ? gb.toFixed(2) + ' GB' : e.mb.toFixed(0) + ' MB'}</strong>
                <span style="color:var(--text-muted);"> — ${e.ntime} 时步 × ${e.ncells} 水格 × ${e.n_vars} 变量
                ${e.measured_counts ? '（变量数按上次输出实测）' : '（变量数为估算）'}</span></div>`;
        }
    }
}

function _selectedOutputSources() {
    return Array.from(document.querySelectorAll('.out-src:checked')).map(el => el.value);
}

async function applyOutputPreset(preset) {
    const res = await api('/api/config/output', { method: 'POST', body: { preset: preset } });
    if (res.error) { toast(res.error, 'error'); return; }
    toast(`已应用“${preset}”订阅：${res.sources.length} 项`, 'success');
    loadOutputConfig();
    if (res.warning) toast(res.warning, 'error');
}

async function saveOutputSubscription() {
    if (!state.activeCase) { toast('请先加载案例', 'error'); return; }
    const sources = _selectedOutputSources();
    if (!sources.length) { toast('至少选择一个变量或模块', 'error'); return; }
    const res = await api('/api/config/output', {
        method: 'POST',
        body: { sync_interval: parseInt($('output-sync-interval').value, 10) || 1, sources: sources }
    });
    if (res.error) { toast(res.error, 'error'); return; }
    toast(`输出订阅已保存（${res.sources.length} 项）`, 'success');
    loadOutputConfig();
    if (res.warning) toast(res.warning, 'error');
}

// ── Pre-flight health check (P0) ──────────────────────────────────────
async function runPreflightCheck() {
    if (!state.activeCase) { toast('请先加载案例', 'error'); return; }
    const panel = $('run-check-panel');
    panel.style.display = 'block';
    panel.innerHTML = '<div style="font-size:12px;color:var(--text-muted);">🩺 体检中...</div>';
    const res = await api('/api/run/check');
    if (res.error) {
        panel.innerHTML = `<div style="color:var(--danger);font-size:12px;">体检失败: ${res.error}</div>`;
        return;
    }
    const icon = { error: '❌', warn: '⚠️', ok: '✅' };
    const color = { error: 'var(--danger)', warn: 'var(--warning)', ok: 'var(--success)' };
    const rows = (res.checks || []).map(c => `
        <div style="display:flex;gap:8px;padding:5px 0;border-bottom:1px solid var(--border);font-size:12px;">
            <span>${icon[c.level] || ''}</span>
            <div style="flex:1;">
                <div style="font-weight:600;color:${color[c.level]};">${c.title}</div>
                <div style="color:var(--text-secondary);">${c.detail || ''}</div>
                ${c.fix ? `<div style="color:var(--info);margin-top:2px;">👉 ${c.fix}</div>` : ''}
            </div>
        </div>`).join('');
    const head = res.ok
        ? `<div style="font-size:13px;font-weight:600;color:var(--success);margin-bottom:6px;">✅ 可以运行（${res.n_warn} 条提醒）</div>`
        : `<div style="font-size:13px;font-weight:600;color:var(--danger);margin-bottom:6px;">❌ ${res.blocking} 项必须先修复</div>`;
    panel.innerHTML = `<div style="border:1px solid var(--border);border-radius:6px;padding:10px;background:var(--bg-tertiary);">${head}${rows}</div>`;
    if (!res.ok) toast(`体检发现 ${res.blocking} 项致命问题，请先修复`, 'error');
}

async function saveOutputConfig() {
    if (!state.activeCase) { toast('请先加载案例', 'error'); return; }
    const payload = {
        time_unit: $('output-time-unit').value,
        time_step: parseInt($('output-time-step').value, 10),
        sync_interval: parseInt($('output-sync-interval').value, 10),
    };
    if (!payload.sync_interval || payload.sync_interval <= 0) {
        toast('sync_interval 必须 ≥ 1', 'error');
        return;
    }
    const res = await api('/api/config/output', {
        method: 'POST',
        body: JSON.stringify(payload)
    });
    if (res.success) {
        toast(`输出配置已保存 (sync_interval=${res.sync_interval})`, 'success');
        const banner = $('output-warning-banner');
        if (banner) banner.style.display = 'none';
    } else {
        toast(res.error || '保存失败', 'error');
    }
}

// ── Input Data ────────────────────────────────────────────────────────
// 每个输入文件对应的"去填写"入口
const _INPUT_FILE_ACTIONS = {
    'bathymetry.nc':   {label: '🛠️ 前处理', act: () => navigate('preprocess')},
    'meteo.nc':        {label: '🌦️ 填气象', act: () => _scrollToCard('meteo-csv-file')},
    'meteo_input.txt': {label: '🌦️ 填气象', act: () => _scrollToCard('meteo-csv-file')},
    'rivers.nc':       {label: '🏞️ 配河流', act: () => _scrollToCard('river-add-name')},
    'riverinfo.dat':   {label: '🏞️ 配河流', act: () => _scrollToCard('river-add-name')},
};

function _scrollToCard(elId) {
    const el = $(elId);
    const card = el ? el.closest('.card') : null;
    if (card) card.scrollIntoView({behavior: 'smooth', block: 'center'});
}

function _inputFileAction(idx) {
    const act = (state._inputFileActions || [])[idx];
    if (act) act();
}

async function loadInputData() {
    const tbody = $('input-files-table').querySelector('tbody');
    if (!state.activeCase) {
        tbody.innerHTML = '<tr><td colspan="7">请先加载案例</td></tr>';
        $('input-overview').innerHTML = '<div class="empty-state"><div class="icon">📂</div>请先加载案例</div>';
        $('river-list-panel').innerHTML = '<div style="color:var(--text-muted);font-size:12px;">请先加载案例</div>';
        $('meteo-preview').innerHTML = '';
        return;
    }
    tbody.innerHTML = '<tr><td colspan="7">加载中...</td></tr>';
    const data = await api('/api/case/inputs');
    if (data.error) { tbody.innerHTML = `<tr><td colspan="7">${data.error}</td></tr>`; return; }
    tbody.innerHTML = '';
    let existCount = 0, missingCount = 0, totalSize = 0;
    state._inputFileActions = [];
    data.files.forEach((f, idx) => {
        if (f.exists) { existCount++; totalSize += f.size_bytes || 0; } else { missingCount++; }
        const status = f.exists
            ? '<span style="color:var(--success)">✅ 存在</span>'
            : '<span style="color:var(--danger)">❌ 缺失</span>';
        const size = f.exists ? fmtSize(f.size_bytes) : '-';
        const mtime = f.exists ? f.mtime : '-';
        const nVars = f.exists ? (f.n_vars !== null && f.n_vars !== undefined ? f.n_vars : '-') : '-';
        const act = _INPUT_FILE_ACTIONS[f.name] ||
            {label: '🏗️ 去构建', act: () => _scrollToCard('build-status')};
        state._inputFileActions.push(act.act);
        const tr = document.createElement('tr');
        tr.innerHTML = `<td><code style="font-size:11px;">${f.name}</code></td><td>${status}</td><td>${size}</td><td style="font-size:11px;">${mtime}</td><td>${nVars}</td><td style="font-size:12px;color:var(--text-secondary);">${f.desc}</td><td><button class="btn btn-sm" onclick="_inputFileAction(${idx})">${act.label}</button></td>`;
        tbody.appendChild(tr);
    });
    $('input-overview').innerHTML = `
        <div style="font-size:13px;line-height:2;">
            <div>案例: <strong>${state.activeCase}</strong></div>
            <div>路径: <code style="font-size:11px;">${state.activeCasePath}</code></div>
            <div>文件: <strong style="color:var(--success)">${existCount} 存在</strong> / <strong style="color:var(--danger)">${missingCount} 缺失</strong></div>
            <div>总大小: <strong>${fmtSize(totalSize)}</strong></div>
            <div>生态模块: <strong>${state.fabmModules.length}</strong> 个</div>
            <div>总参数: <strong>${state.fabmModules.reduce((s,m)=>s+m.n_params,0)}</strong> 个</div>
        </div>`;
    // 侧面板：河流列表 + 气象草稿预览
    loadRiverPanel();
    loadMeteoDraftPreview();
}

// ── 气象 CSV → meteo.nc ───────────────────────────────────────────────
const _METEO_KEYS = ['u10', 'v10', 'slp', 't2', 'rh', 'tcc', 'precip', 'evap'];

function downloadMeteoTemplate() {
    const csv = [
        'date,u10,v10,slp,t2,rh,tcc,precip,evap',
        '2020-01-01,2.5,-1.2,1016.8,8.4,0.72,0.45,0.0,1.2',
        '2020-01-02,3.1,-0.8,1015.2,7.9,0.78,0.62,0.6,1.1',
        '2020-01-03,1.8,0.4,1017.9,9.2,0.65,0.30,0.0,1.3',
    ].join('\n');
    const blob = new Blob(['\ufeff' + csv + '\n'], {type: 'text/csv;charset=utf-8'});
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'meteo_template.csv';
    a.click();
    URL.revokeObjectURL(a.href);
}

// multipart 上传（api() 只支持 JSON，文件上传走这里）
function _uploadForm(url, formData) {
    return new Promise(resolve => {
        const xhr = new XMLHttpRequest();
        xhr.open('POST', url, true);
        xhr.onload = function() {
            try { resolve(JSON.parse(xhr.responseText)); }
            catch (e) { resolve({error: '响应解析失败: ' + xhr.responseText.substring(0, 150)}); }
        };
        xhr.onerror = function() { resolve({error: '网络错误'}); };
        xhr.ontimeout = function() { resolve({error: '上传超时'}); };
        xhr.timeout = 120000;
        xhr.send(formData);
    });
}

async function uploadMeteoCsv() {
    if (!state.activeCase) { toast('请先加载案例', 'error'); return; }
    const fi = $('meteo-csv-file');
    if (!fi || !fi.files.length) { _ppStatus('meteo-upload-status', '请先选择 CSV 文件', false); return; }
    const fd = new FormData();
    fd.append('file', fi.files[0]);
    _ppStatus('meteo-upload-status', '上传解析中...', true);
    const res = await _uploadForm('/api/input/meteo/upload', fd);
    if (res.error) { _ppStatus('meteo-upload-status', '失败: ' + res.error, false); return; }
    let html = `<span>✓ 已解析 <strong>${res.n_rows}</strong> 行（${res.date_range[0]} ~ ${res.date_range[1]}）</span>`;
    if (res.n_bad_rows) html += `<div style="color:var(--warning);font-size:11px;">⚠ ${res.n_bad_rows} 行日期无法解析，已跳过</div>`;
    if (res.unmapped_cols && res.unmapped_cols.length) html += `<div style="color:var(--warning);font-size:11px;">⚠ 未识别列（已忽略）: ${res.unmapped_cols.join(', ')}</div>`;
    _ppStatus('meteo-upload-status', html, true);
    await loadMeteoDraftPreview();
    _prefillBuildDates(res.date_range[0], res.date_range[1]);
}

async function loadMeteoDraftPreview() {
    const el = $('meteo-preview');
    state.meteoEdited = false;
    if (!state.activeCase) { el.innerHTML = ''; return; }
    const res = await api('/api/input/meteo/draft');
    if (res.error || !res.exists) {
        state.meteoDraft = null;
        el.innerHTML = '<div style="color:var(--text-muted);font-size:12px;">尚未上传气象 CSV。上传后此处显示可编辑的数据表格。</div>';
        return;
    }
    state.meteoDraft = res;
    _prefillBuildDates(res.dates[0], res.dates[res.dates.length - 1]);
    const n = res.dates.length;
    const show = Math.min(n, 200);
    const head = ['date', ..._METEO_KEYS].map(k => `<th>${k}</th>`).join('');
    let rows = '';
    for (let k = 0; k < show; k++) {
        rows += '<tr>' + `<td style="font-size:11px;white-space:nowrap;">${res.dates[k]}</td>` +
            _METEO_KEYS.map(key =>
                `<td><input type="number" step="any" style="width:74px;padding:1px 4px;font-size:11px;" value="${fmt(res[key][k], 3)}" onchange="_meteoCellEdit(${k}, '${key}', this.value)"></td>`
            ).join('') + '</tr>';
    }
    el.innerHTML = `
        <div style="font-size:11px;color:var(--text-muted);margin-bottom:4px;">
            草稿共 <strong>${n}</strong> 行${n > show ? `（预览前 ${show} 行；未显示行按原值写入）` : ''}，可直接修改数值后生成 meteo.nc。单位: 风 m/s、气压 hPa、气温 ℃、湿度/云量 0-1、降雨/蒸发 mm/day（后端自动换算）。
        </div>
        <div style="max-height:260px;overflow:auto;border:1px solid var(--border);border-radius:6px;">
            <table class="data-table" style="font-size:11px;margin:0;"><thead><tr>${head}</tr></thead><tbody>${rows}</tbody></table>
        </div>`;
}

function _meteoCellEdit(rowIdx, key, value) {
    if (!state.meteoDraft) return;
    const v = parseFloat(value);
    if (isNaN(v)) { toast('数值无效', 'error'); return; }
    state.meteoDraft[key][rowIdx] = v;
    state.meteoEdited = true;
}

async function saveMeteoNc() {
    if (!state.activeCase) { toast('请先加载案例', 'error'); return; }
    if (!state.meteoDraft) { _ppStatus('meteo-upload-status', '无气象草稿，请先上传 CSV', false); return; }
    _ppStatus('meteo-upload-status', '生成 meteo.nc 中...', true);
    let body = {};
    if (state.meteoEdited) {
        body.rows = state.meteoDraft.dates.map((d, k) => {
            const r = {date: d};
            _METEO_KEYS.forEach(key => r[key] = state.meteoDraft[key][k]);
            return r;
        });
    }
    const res = await api('/api/input/meteo/save', {method: 'POST', body});
    if (res.error) { _ppStatus('meteo-upload-status', '失败: ' + res.error, false); return; }
    _ppStatus('meteo-upload-status', `✓ meteo.nc 已生成（${res.n_times} 个时步，广播到 ${res.grid} 网格，时间原点 ${res.start}）`, true);
    toast('meteo.nc 已生成', 'success');
    loadInputData();
}

// ── 河流数据 → rivers.nc + riverinfo.dat ──────────────────────────────
async function loadRiverPanel() {
    const el = $('river-list-panel');
    if (!state.activeCase) { el.innerHTML = '<div style="color:var(--text-muted);font-size:12px;">请先加载案例</div>'; return; }
    const res = await api('/api/input/rivers');
    if (res.error) { el.innerHTML = `<span style="color:var(--danger);font-size:12px;">${res.error}</span>`; return; }
    state.riverPanel = res;
    if (!res.rivers.length) {
        el.innerHTML = '<div style="color:var(--text-muted);font-size:12px;">暂无河流标记。可在前处理深度图点选标记，或在上方手动添加。</div>';
        return;
    }
    el.innerHTML = res.rivers.map((r, k) => `
        <div style="display:flex;align-items:center;gap:8px;padding:5px 0;border-bottom:1px solid var(--border);flex-wrap:wrap;">
            <span style="color:var(--success);">▲</span>
            <strong style="min-width:86px;">${r.name}</strong>
            <span style="color:var(--text-muted);font-size:12px;">i=${r.i}, j=${r.j}</span>
            <span id="river-draft-${k}" style="font-size:11px;color:${r.has_draft ? 'var(--success)' : 'var(--danger)'};">${r.has_draft ? `✅ ${r.n_rows} 行` : '❌ 未上传数据'}</span>
            <input type="file" id="river-csv-${k}" accept=".csv,.txt" style="display:none;" onchange="_riverCsvChosen(${k})">
            <button class="btn btn-sm" style="margin-left:auto;" onclick="showRiverSeries('${r.name}')">📈 曲线</button>
            <button class="btn btn-sm" onclick="$('river-csv-${k}').click()">📤 上传CSV</button>
            <button class="btn btn-sm" style="color:var(--danger);" onclick="deleteRiver('${r.name}')">删除</button>
        </div>`).join('') +
        `<div style="font-size:11px;color:var(--text-muted);margin-top:6px;">
            CSV 列: date,Q,temp,nh4,no3,po4；Q 正=入流、负=出流（m³/s）。${res.has_rivers_nc ? 'rivers.nc 已存在，重新生成会覆盖。' : ''}
        </div>`;
}

async function _riverCsvChosen(k) {
    const fi = $('river-csv-' + k);
    if (!fi || !fi.files.length) return;
    const name = state.riverPanel.rivers[k].name;
    const fd = new FormData();
    fd.append('river_name', name);
    fd.append('file', fi.files[0]);
    const st = $('river-draft-' + k);
    if (st) { st.textContent = '上传中...'; st.style.color = 'var(--info)'; }
    const res = await _uploadForm('/api/input/rivers/upload', fd);
    if (res.error) {
        if (st) { st.textContent = '❌ 上传失败'; st.style.color = 'var(--danger)'; st.title = res.error; }
        toast(`${name}: ${res.error}`, 'error');
        return;
    }
    if (st) {
        st.textContent = `✅ ${res.n_rows} 行`;
        st.style.color = 'var(--success)';
        st.title = `Q 范围 ${res.q_min.toFixed(2)}~${res.q_max.toFixed(2)} m³/s（均值 ${res.q_mean.toFixed(2)}），出流天数 ${res.n_outflow_days}`;
    }
    if (res.n_bad_rows) toast(`${name}: ${res.n_bad_rows} 行日期无法解析被跳过`, 'warning');
    toast(`${name}: 已上传 ${res.n_rows} 行流量数据`, 'success');
}

async function addRiverManually() {
    if (!state.activeCase) { toast('请先加载案例', 'error'); return; }
    const name = $('river-add-name').value.trim();
    const i = parseInt($('river-add-i').value);
    const j = parseInt($('river-add-j').value);
    if (!name || !i || !j) { toast('请填写河名与 i/j 格点号', 'error'); return; }
    const res = await api('/api/input/rivers/add', {method: 'POST', body: {name, i, j}});
    if (res.error) { toast(res.error, 'error'); return; }
    toast(`已添加河流 ${name} (i=${i}, j=${j})`, 'success');
    $('river-add-name').value = ''; $('river-add-i').value = ''; $('river-add-j').value = '';
    loadRiverPanel();
}

async function deleteRiver(name) {
    if (!confirm(`删除河流 ${name} 及其已上传的流量数据？`)) return;
    const res = await api('/api/input/rivers/delete', {method: 'POST', body: {name}});
    if (res.error) { toast(res.error, 'error'); return; }
    toast(`已删除河流 ${name}`, 'info');
    loadRiverPanel();
}

async function saveRiversNc() {
    if (!state.activeCase) { toast('请先加载案例', 'error'); return; }
    _ppStatus('rivers-save-status', '生成中...', true);
    const res = await api('/api/input/rivers/save', {method: 'POST'});
    if (res.error) { _ppStatus('rivers-save-status', '失败: ' + res.error, false); return; }
    _ppStatus('rivers-save-status', `✓ 已生成 rivers.nc（${res.n_rivers} 条河 × ${res.n_times} 个时步）与 riverinfo.dat`, true);
    toast('rivers.nc + riverinfo.dat 已生成', 'success');
    loadInputData();
}

// ── 河流输入数据可视化（rivers.nc 时间序列曲线）───────────────────────
async function showRiverSeries(name) {
    if (!state.activeCase) { toast('请先加载案例', 'error'); return; }
    const panel = $('river-series-panel');
    panel.style.display = 'block';
    $('river-series-title').textContent = name;
    $('river-series-status').textContent = '读取 rivers.nc ...';
    const res = await api(`/api/input/rivers/series?name=${encodeURIComponent(name)}`);
    if (res.error) { $('river-series-status').textContent = '❌ ' + res.error; state.riverSeries = null; return; }
    state.riverSeries = res;
    const sel = $('river-series-var');
    sel.innerHTML = Object.entries(res.series).map(([k, v]) =>
        `<option value="${k}">${v.long_name || k}${v.units ? ` (${v.units})` : ''}</option>`).join('');
    $('river-series-status').textContent = `✓ ${res.times.length} 个时步`;
    drawRiverSeries();
    panel.scrollIntoView({behavior: 'smooth', block: 'nearest'});
}

function drawRiverSeries() {
    const res = state.riverSeries;
    if (!res) return;
    const key = $('river-series-var').value;
    const s = res.series[key];
    if (!s) return;
    if (state.charts.river) state.charts.river.destroy();
    state.charts.river = new Chart($('river-series-chart').getContext('2d'), {
        type: 'line',
        data: { labels: res.times, datasets: [{
            label: `${s.long_name || key} (${s.units || ''})`,
            data: s.values, borderColor: '#3b82f6', backgroundColor: 'rgba(59,130,246,0.1)',
            fill: true, tension: 0.2, pointRadius: 0, borderWidth: 1.5,
        }]},
        options: { responsive: true, maintainAspectRatio: false,
            plugins: { legend: {labels: {color: '#ccc', font: {size: 11}}} },
            scales: { x: {ticks: {color: '#999', maxTicksLimit: 10, maxRotation: 0}, grid: {color: '#222'}},
                      y: {ticks: {color: '#999'}, grid: {color: '#333'}} }
        }
    });
}

// ── 一键构建完整案例 ──────────────────────────────────────────────────
function _prefillBuildDates(start, stop) {
    if ($('build-start') && !$('build-start').value) $('build-start').value = start + ' 00:00:00';
    if ($('build-stop') && !$('build-stop').value) $('build-stop').value = stop + ' 00:00:00';
}

async function buildCase() {
    if (!state.activeCase) { toast('请先加载案例', 'error'); return; }
    // 模块组合来自「模块配置」页；营养状态来自「初始条件」页
    const engines = {};
    (state.engines || []).forEach(e => { engines[e.key] = !!e.enabled; });
    const body = {
        preset: (state.icData && state.icData.trophic) || 'eutrophic',
        start: $('build-start').value.trim(),
        stop: $('build-stop').value.trim(),
        timestep: parseInt($('build-dt').value) || 15,
        nlev: parseInt($('build-nlev').value) || 10,
        engines,
    };
    if (!body.start || !body.stop) { _ppStatus('build-status', '请填写开始/结束时间（可先上传气象 CSV 自动填充）', false); return; }
    if (!confirm(`构建案例 ${state.activeCase}？\n将生成 getm.inp / fabm.yaml 等 9 个配置文件（已有配置会被覆盖，数据文件保留）`)) return;
    _ppStatus('build-status', '构建中（生成配置文件）...', true);
    const res = await api('/api/case/build', {method: 'POST', body});
    if (res.error) { _ppStatus('build-status', '失败: ' + res.error, false); return; }
    let html = `<span>✓ 构建成功：预设 <strong>${res.preset_label}</strong>，${res.params_applied} 个生态参数已写入 fabm.yaml</span>`;
    (res.notes || []).forEach(n => { html += `<div style="color:var(--info);font-size:11px;">ℹ ${n}</div>`; });
    (res.warnings || []).forEach(w => { html += `<div style="color:var(--warning);font-size:11px;">⚠ ${w}</div>`; });
    html += `<div style="font-size:11px;color:var(--text-muted);margin-top:4px;">案例文件: ${res.files.join(', ')}</div>`;
    _ppStatus('build-status', html, true);
    toast('案例构建成功，可到「运行控制」页运行模型', 'success');
    loadInputData();
    loadCases();
    // Silently refresh fabm module state: the case was loaded before build,
    // so state.fabmModules is stale/empty and module/parameter pages show blank.
    const data = await api('/api/case/load', {method: 'POST', body: {case_name: state.activeCase}});
    if (!data.error) {
        state.fabmModules = data.fabm.modules || [];
        state.fabmCategories = data.fabm.categories || {};
        renderModuleCards();
        loadParamModules();
    }
}

// ── Modules ───────────────────────────────────────────────────────────
function filterModuleCards() { renderModuleCards(); }

function renderModuleCards() {
    const container = $('modules-container');
    if (!container) return;
    if (!state.fabmModules.length) {
        container.innerHTML = '<div class="empty-state"><div class="icon">🧩</div>加载案例后显示模块列表（未加载案例时，上方「功能模块」可先行选择引擎组合）</div>';
        return;
    }
    const q = ($('module-search') ? $('module-search').value : '').trim().toLowerCase();
    const show = $('module-show') ? $('module-show').value : 'all';
    const visible = state.fabmModules.filter(m => {
        if (show === 'enabled' && !m.enabled) return false;
        if (show === 'disabled' && m.enabled) return false;
        if (!q) return true;
        return (m.name + ' ' + (m.long_name || '') + ' ' + (m.category || '')).toLowerCase().includes(q);
    });
    const enabledCount = visible.filter(m => m.enabled).length;
    let html = `<div style="margin-bottom:12px;font-size:13px;">
        <span>显示: <strong>${visible.length}</strong> / ${state.fabmModules.length}</span> ·
        <span>启用: <strong style="color:var(--success)">${enabledCount}</strong></span> ·
        <span>禁用: <strong style="color:var(--text-muted)">${visible.length - enabledCount}</strong></span> ·
        <span>总参数: <strong>${visible.reduce((s, m) => s + (m.n_params || 0), 0)}</strong></span>
    </div>`;
    const cats = state.fabmCategories && Object.keys(state.fabmCategories).length
        ? state.fabmCategories : { '模块': visible };
    let any = false;
    for (const [cat, mods] of Object.entries(cats)) {
        const list = visible.filter(m => mods.some(x => (x.name || x) === m.name));
        if (!list.length) continue;
        any = true;
        html += `<div class="card"><div class="card-title">${cat} <span class="badge">${list.length} 个模块</span></div><div class="grid-3">`;
        list.forEach(m => {
            const refs = (m.coupling_refs && m.coupling_refs.length) ? `<div style="font-size:10px;color:var(--text-muted);">依赖: ${m.coupling_refs.join(', ')}</div>` : '';
            html += `<div class="module-card ${m.enabled ? 'enabled' : 'disabled'}" onclick="toggleModule('${m.name}', ${m.enabled})" title="点击${m.enabled ? '禁用' : '启用'}">
                <div class="module-name" style="color:${m.color}">${m.long_name || m.name}</div>
                <div style="font-size:11px;color:var(--text-muted);">${m.name}</div>
                <div class="module-params">${m.n_params} 参数 ${m.has_coupling ? '• 有耦合' : ''}</div>
                ${refs}
                <div style="margin-top:6px;"><span style="font-size:11px;color:${m.enabled ? 'var(--success)' : 'var(--text-muted)'}">${m.enabled ? '● 已启用' : '○ 已禁用'}</span></div>
            </div>`;
        });
        html += '</div></div>';
    }
    if (!any) html += '<div class="empty-state"><div class="icon">🔍</div>没有匹配的模块</div>';
    container.innerHTML = html;
}

async function toggleModule(name, currentlyEnabled) {
    if (!state.activeCase) { toast('请先加载案例', 'error'); return; }
    const nextEnabled = !currentlyEnabled;
    const verb = nextEnabled ? '启用' : '禁用';
    if (!confirm(`确定${verb}模块 "${name}"？`)) return;
    const res = await api('/api/config/fabm/module', {
        method: 'POST',
        body: { module: name, enabled: nextEnabled }
    });
    if (res.needs_confirmation) {
        const msg = `以下模块依赖 ${name}：\n${res.warnings.join('\n')}\n\n仍要${verb}吗？`;
        if (!confirm(msg)) return;
        const res2 = await api('/api/config/fabm/module', {
            method: 'POST',
            body: { module: name, enabled: nextEnabled, force: true }
        });
        if (res2.success) {
            state.fabmModules = res2.fabm.modules || [];
            state.fabmCategories = res2.fabm.categories || {};
            renderModuleCards();
            loadParamModules();
            toast(`已${verb} "${name}"（强制）`, 'warning');
        } else {
            toast(res2.warnings ? res2.warnings.join('; ') : `${verb}失败`, 'error');
        }
        return;
    }
    if (res.success) {
        state.fabmModules = res.fabm.modules || [];
        state.fabmCategories = res.fabm.categories || {};
        renderModuleCards();
        loadParamModules();
        toast(`已${verb} "${name}"`, 'success');
    } else {
        toast(res.warnings ? res.warnings.join('; ') : `${verb}失败`, 'error');
    }
}

// ── 模型引擎开关（水动力 / 水质生态 / 温室气体）───────────────────────
// 支持「未加载案例」时先选模块：此时写入全局草稿，一键构建时自动应用。
async function loadEngines() {
    const el = $('engines-container');
    if (!el) return;
    const res = await api('/api/config/modules');
    if (res.error) { el.innerHTML = `<div style="color:var(--danger);grid-column:1/-1;">${res.error}</div>`; return; }
    state.engines = res.engines || [];
    if (res.modules) state.fabmModules = res.modules;
    if (res.categories) state.fabmCategories = res.categories;
    state.modulesInfo = res;
    renderEngines();
    const ghg = (res.engines || []).find(e => e.key === 'ghg');
    if (ghg && ghg.building && !state._ghgPoll) pollGhgBuild();
    if (typeof loadModules === 'function' && $('modules-container')) renderModuleCards();
}

function renderEngines() {
    // The same card set lives on two pages (模块配置 + 前处理「0. 模型模块」).
    const els = [$('engines-container'), $('pp-engines-container')].filter(Boolean);
    if (!els.length) return;
    const res = state.modulesInfo || {};
    const badgeHtml = res.has_case
        ? '<span style="font-size:10px;background:var(--success);color:#fff;padding:1px 7px;border-radius:8px;">当前案例</span>'
        : '<span style="font-size:10px;background:var(--accent);color:#fff;padding:1px 7px;border-radius:8px;">新建模型默认组合</span>';
    [ 'modules-source-badge', 'pp-engines-badge' ].forEach(id => {
        const badge = $(id);
        if (badge) badge.innerHTML = badgeHtml;
    });
    const html = (state.engines || []).map(engineCard).join('');
    els.forEach(el => { el.innerHTML = html; });
    const warn = $('modules-warning');
    if (warn) {
        const e = (res.engines || []).find(x => x.key === 'ghg');
        let html = '';
        if (e && e.enabled && !e.exe_has_ghg) {
            html = '<div style="font-size:11px;color:var(--warning);">⚠ 温室气体模块已启用，但当前模型程序不含该模块，正在/将自动编译，完成后自动部署。</div>';
        }
        warn.innerHTML = html;
    }
}

function engineCard(e) {
    const on = !!e.enabled;
    const hint = [];
    if (e.key === 'ghg' && on && e.building) hint.push('⚙ 正在后台编译温室气体模块…');
    if (e.key === 'ghg' && on && !e.exe_has_ghg && !e.building) hint.push('⚙ 新程序待部署：模型结束或下次启动运行前自动生效');
    return `<div class="module-card engine-card ${on ? 'enabled' : 'disabled'}" onclick="toggleEngine('${e.key}')" title="点击切换${on ? '关闭' : '启用'}">
        <div class="engine-title">${e.icon || ''} ${e.long_name || e.label}</div>
        <div class="engine-desc">${e.desc}</div>
        <div class="engine-foot">
            <span class="switch ${on ? 'on' : ''}"><span class="track"><span class="knob"></span></span>${on ? '启用' : '关闭'}</span>
            ${e.fixed ? '<span style="color:var(--success);margin-left:10px;">● 必选内核</span>' : ''}
        </div>
        ${hint.map(h => `<div style="font-size:10px;color:var(--warning);margin-top:4px;">${h}</div>`).join('')}
    </div>`;
}

async function toggleEngine(key) {
    const e = (state.engines || []).find(x => x.key === key);
    if (!e) return;
    if (e.fixed) { toast('水动力是模型核心引擎，始终启用', 'info'); return; }
    const next = !e.enabled;
    const ASK = {
        eco: ['启用水质生态引擎（FABM-WET 食物网）？\n随后可在「初始条件」页设置营养盐与藻类初值。',
              '关闭水质生态引擎？\n关闭后仅运行水动力，生态变量不再计算。'],
        fish: ['启用鱼类模块（食物网顶层捕食者）？\n将新增 JuFish 幼鱼 / AdFish 成鱼 / PiscFish 食鱼性鱼三组状态变量，'
               + '闭合「藻—浮游动物—鱼」的下行控制链路。模块已编译在程序中，启用无需重新编译。',
               '关闭鱼类模块？\n将从配置中移除三个鱼类实例，食物网将缺少顶层捕食者（可一键重新启用）。'],
        ghg: ['启用温室气体引擎（CO₂/CH₄）？\n将新增 DIC/碱度/pH/甲烷状态变量并闭合碳循环；若当前程序未含该模块会自动编译。',
              '关闭温室气体引擎？\n将从配置中移除温室气体模块（再次启用时自动生成）。'],
    };
    const ask = ASK[key] || ['', ''];
    if (!confirm(next ? ask[0] : ask[1])) return;
    const body = {};
    body[key] = next;
    const res = await api('/api/config/modules', {method: 'POST', body});
    if (res.error) { toast(res.error, 'error'); return; }
    (res.warnings || []).forEach(w => toast(w, 'info'));
    toast(next ? `已启用「${e.long_name || e.label}」` : `已关闭「${e.long_name || e.label}」`,
          key === 'ghg' && next ? 'info' : 'success');
    await loadEngines();
    if (res.build_started) { toast('温室气体模块编译已启动，完成后自动部署', 'info'); pollGhgBuild(); }
}

// ── 温室气体引擎（CO₂/CH₄）────────────────────────────────────────────
async function toggleGhgEngine(next) {
    if (!confirm(next
        ? '启用温室气体引擎（CO₂/CH₄）？\n将新增 DIC/碱度/pH/甲烷状态变量并闭合碳循环；\n若当前程序未包含该模块，将自动编译（后台进行）'
        : '关闭温室气体引擎？\n将从配置中移除温室气体模块（再次启用时自动重新生成）')) return;
    const res = await api('/api/config/ghg', {method: 'POST', body: {enabled: next}});
    if (!res.success) { toast((res.warnings || []).join('; ') || '操作失败', 'error'); return; }
    (res.warnings || []).forEach(w => toast(w, 'info'));
    if (res.fabm && res.fabm.modules) {
        state.fabmModules = res.fabm.modules;
        state.fabmCategories = res.fabm.categories || {};
        renderModuleCards();
        loadParamModules();
    }
    if (res.build_started) {
        toast('温室气体模块编译已启动，完成后自动部署', 'info');
        pollGhgBuild();
    } else {
        toast(next ? '已启用温室气体引擎' : '已关闭温室气体引擎', 'success');
    }
    loadEngines();
}

async function pollGhgBuild() {
    if (state._ghgPoll) return;
    state._ghgPoll = true;
    const timer = setInterval(async () => {
        try {
            const res = await api('/api/config/ghg');
            if (!res.build || !res.build.running) {
                clearInterval(timer);
                state._ghgPoll = false;
                if (res.build && res.build.ok) {
                    toast('温室气体模块编译完成' + (res.exe_has_ghg ? '，已部署' : '（将在下次运行前自动部署）'), 'success');
                } else {
                    toast('温室气体模块编译失败：' + ((res.build && res.build.logs || []).slice(-1)[0] || '详见后台日志'), 'error');
                }
                loadEngines();
            }
        } catch (err) {
            clearInterval(timer);
            state._ghgPoll = false;
        }
    }, 5000);
}

// ── Parameters ────────────────────────────────────────────────────────
function loadParamModules() {
    const sel = $('param-module-select');
    sel.innerHTML = '';
    state.fabmModules.forEach(m => {
        const opt = document.createElement('option');
        opt.value = m.name;
        opt.textContent = `${m.long_name || m.name} (${m.n_params} 参数)`;
        sel.appendChild(opt);
    });
    if (state.fabmModules.length) loadModuleParams();
}

function loadModuleParams() {
    const name = $('param-module-select').value;
    const mod = state.fabmModules.find(m => m.name === name);
    if (!mod) return;
    state.currentParams = mod.parameters;
    $('param-module-title').textContent = `${mod.long_name || mod.name} - 参数列表 (${mod.parameters.length})`;
    renderParams(mod.parameters);
}

function renderParams(params) {
    const list = $('params-list');
    list.innerHTML = '';
    const moduleName = $('param-module-select').value;
    params.forEach((p, idx) => {
        const row = document.createElement('div');
        row.className = 'param-row';
        const hasDefault = p.default_value !== null && p.default_value !== undefined;
        const isModified = hasDefault && String(p.value) !== String(p.default_value);
        const dirtyClass = isModified ? ' param-dirty' : '';
        const unitHtml = p.unit
            ? `<span class="param-unit" title="单位">${escapeHtml(p.unit)}</span>` : '';
        const commentHtml = p.comment
            ? `<div class="param-comment" title="${escapeAttr(p.comment)}">${escapeHtml(p.comment)}</div>`
            : '';
        const descHtml = p.desc
            ? `<div class="param-desc" title="说明：${escapeAttr(p.desc)}">${escapeHtml(p.desc)}</div>`
            : '';
        const descEnHtml = (p.desc_en && p.desc_en !== p.desc)
            ? `<div class="param-desc-en">${escapeHtml(p.desc_en)}</div>`
            : '';
        const resetBtn = hasDefault && isModified
            ? `<button class="btn btn-sm" style="margin-left:4px;font-size:10px;padding:2px 6px;" title="恢复为默认值 ${p.default_value}" onclick="resetParam('${moduleName}', '${p.name}', ${idx})">↺ 默认</button>`
            : '';
        row.innerHTML = `
            <span class="param-name">${p.name}${unitHtml}</span>
            <input class="param-value${dirtyClass}" value="${p.value}" data-idx="${idx}" data-default="${hasDefault ? String(p.default_value).replace(/"/g, '&quot;') : ''}" onchange="saveParam(this, '${moduleName}', '${p.name}')">
            <span class="param-saved" id="param-saved-${idx}"></span>
            ${resetBtn}
            <div class="param-detail">${descHtml}${descEnHtml}${commentHtml}</div>`;
        list.appendChild(row);
    });
}

function escapeHtml(s) {
    if (s === null || s === undefined) return '';
    return String(s).replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
}
function escapeAttr(s) {
    return escapeHtml(s).replace(/"/g, '&quot;');
}

async function resetParam(module, param, idx) {
    const input = document.querySelector(`input[data-idx="${idx}"]`);
    if (!input) return;
    const defaultVal = input.dataset.default;
    if (!defaultVal && defaultVal !== '0') { toast('无默认值', 'warning'); return; }
    if (!confirm(`恢复 ${param} 为默认值 ${defaultVal}？`)) return;
    input.value = defaultVal;
    await saveParam(input, module, param);
}

function filterParams() {
    const q = $('param-search').value.toLowerCase();
    const filtered = state.currentParams.filter(p => p.name.toLowerCase().includes(q));
    renderParams(filtered);
}

async function saveParam(input, module, param) {
    let val = input.value;
    const num = Number(val);
    if (!isNaN(num)) val = num;
    const res = await api('/api/config/fabm/param', {method:'POST', body:{module, param, value:val}});
    const idx = input.dataset.idx;
    if (res.success) {
        $(`param-saved-${idx}`).textContent = '✓ 已保存';
        setTimeout(() => { const e = $(`param-saved-${idx}`); if(e) e.textContent=''; }, 1500);
        toast(`参数 ${param} 已更新`, 'success');
    } else {
        toast('保存失败', 'error');
    }
}

// ── Time Settings ─────────────────────────────────────────────────────
async function loadTimeSettings() {
    if (!state.activeCase) return;
    const t = await api('/api/config/time');
    if (t.error) return;
    $('time-start').value = t.start;
    $('time-stop').value = t.stop;
    $('time-dt').value = t.timestep;
    $('time-step2d').value = t.step_2d;
    // Hotstart
    const hs = await api('/api/config/hotstart');
    if (!hs.error) {
        document.querySelector(`input[name="hotstart"][value="${hs.enabled?1:0}"]`).checked = true;
        $('hotstart-file').value = hs.file || '';
        toggleHotstart(hs.enabled);
    }
    // Estimate
    const est = await api('/api/run/estimate');
    if (!est.error) {
        $('run-estimate').innerHTML = `
            <div class="grid-4">
                <div class="stat-card"><div class="stat-label">网格</div><div class="stat-value" style="font-size:16px;">${est.grid}</div></div>
                <div class="stat-card"><div class="stat-label">水域格</div><div class="stat-value">${est.nwater}</div></div>
                <div class="stat-card"><div class="stat-label">模拟时长</div><div class="stat-value">${fmt(est.duration_days,1)}<span class="stat-unit">天</span></div></div>
                <div class="stat-card"><div class="stat-label">总步数</div><div class="stat-value">${est.nsteps.toLocaleString()}</div></div>
            </div>
            <div style="margin-top:12px;padding:12px;background:var(--bg-tertiary);border-radius:6px;">
                <strong>预计运行时间:</strong> ${fmt(est.estimated_minutes,1)} 分钟 (${fmt(est.estimated_hours,2)} 小时)
                <br><span style="font-size:11px;color:var(--text-muted);">* 基于串行版本估算，开启 OpenMP 多核后可显著缩短</span>
            </div>
            ${est.cfl_ok === false ? `<div style="margin-top:8px;padding:10px 12px;background:#fde8e8;border:1px solid #f5c2c7;border-radius:6px;color:#842029;font-size:13px;">
                <strong>⚠ 时间步长 ${est.timestep}s 超过稳定上限 ${est.cfl_max}s</strong>（网格 CFL≈${Math.round(est.cfl_dt)}s 的 15 倍）。此步长会导致模型数值发散、输出全为 NaN，请改小（建议 60~${Math.round(est.cfl_dt*3)}s）。
            </div>` : (est.cfl_max ? `<div style="margin-top:8px;font-size:11px;color:var(--text-muted);">当前步长 ${est.timestep}s ≤ 稳定上限 ${est.cfl_max}s ✓</div>` : '')}`;
    }
}

async function saveTimeSettings() {
    const res = await api('/api/config/time', {method:'POST', body:{
        start: $('time-start').value, stop: $('time-stop').value,
        timestep: Number($('time-dt').value), step_2d: Number($('time-step2d').value),
    }});
    toast(res.success ? '时间设置已保存' : (res.error || '保存失败'), res.success?'success':'error');
    if (res.success) loadTimeSettings();
}

function toggleHotstart(enabled) { $('hotstart-file-group').style.display = enabled ? 'block' : 'none'; }

async function saveHotstart() {
    const enabled = document.querySelector('input[name="hotstart"]:checked').value === '1';
    const res = await api('/api/config/hotstart', {method:'POST', body:{enabled, file:$('hotstart-file').value}});
    toast(res.success ? '启动设置已保存' : '保存失败', res.success?'success':'error');
}

// ── Initial Conditions ────────────────────────────────────────────────
function toggleIcSection(key) {
    const sec = $(`ic-sec-${key}`);
    if (!sec) return;
    sec.classList.toggle('open');
}

function icIcDirty() {
    if (!state.icData) return;
    state.icData.dirty = true;
    markIcDirty();
}

function markIcDirty() {
    const el = $('ic-save-status');
    if (el) el.textContent = '● 有未保存的修改';
}

function icFieldInput(el) {
    el.addEventListener('input', () => { icIcDirty(); });
}

async function loadInitConditions() {
    if (!state.activeCase) {
        $('ic-loading').style.display = '';
        $('ic-body').style.display = 'none';
        return;
    }
    const d = await api('/api/case/init_conditions');
    if (d.error) { toast(d.error, 'error'); return; }
    state.icData = { ...d, dirty: false };

    $('ic-loading').style.display = 'none';
    $('ic-body').style.display = 'block';

    // 1) hydro: water level + temperature
    const h = d.hydro || {};
    const elevIn = $('ic-elev'), sAbs = $('ic-surface-abs'), dAbs = $('ic-datum-abs'), tIn = $('ic-temp');
    if (sAbs.value !== '' && sAbs.value !== null && dAbs.value === '') {
        // only auto-fill the datum when the user has not set it yet
        dAbs.value = '';
    }
    elevIn.value = (h.elev_const !== undefined && h.elev_const !== null) ? h.elev_const : 0;
    if (h.surface_elev_abs !== null && h.surface_elev_abs !== undefined) sAbs.value = h.surface_elev_abs;
    if (h.datum_abs !== null && h.datum_abs !== undefined) dAbs.value = h.datum_abs;
    tIn.value = (h.temp_const !== undefined && h.temp_const !== null) ? h.temp_const : 15;

    const b = d.bathymetry;
    if (b) {
        $('ic-geo-info').innerHTML =
            `地形 <code>bathymetry.nc</code>：水域格 <b>${b.n_water}</b> 个，` +
            `水深范围 <b>${fmt(b.min_depth, 3)} ~ ${fmt(b.max_depth, 3)}</b> m，均值 ${fmt(b.mean_depth, 3)} m。` +
            `<br>水位填 <b>0</b> 即湖面恰好位于地形零点；此处最大水深 ${fmt(b.max_depth, 3)} m。`;
    } else {
        $('ic-geo-info').textContent = '未找到 bathymetry.nc，水位请手工输入（相对地形零点，m）。';
    }
    // derive the datum automatically if water level is 0 and we know an absolute surface
    if (sAbs.value !== '' && elevIn.value == 0) {
        dAbs.value = Number(sAbs.value).toFixed(1);
    }

    // 2) trophic preset + macrophyte biomass
    renderTrophicPicker(d);
    const macroIn = $('ic-macro-sd');
    if (macroIn) {
        const sd = (d.macrophytes || {}).sD_max;
        if (sd !== null && sd !== undefined && sd !== '') macroIn.value = sd;
        macroIn.addEventListener('input', () => icIcDirty());
    }

    // 3) water quality module list
    renderIcWaterQuality();

    $('ic-save-status').textContent = '';
}

function renderTrophicPicker(d) {
    const box = $('ic-trophic-pick');
    if (!box) return;
    const presets = d.trophic_presets || {};
    const cur = d.trophic;
    box.innerHTML = Object.keys(presets).map(k =>
        `<label class="${k === cur ? 'on' : ''}">
            <input type="radio" name="ic-trophic" value="${k}" ${k === cur ? 'checked' : ''}
                   onchange="onTrophicChange('${k}')"> ${presets[k]}
        </label>`).join('');
}

function onTrophicChange(key) {
    state.icData.trophic = key;
    icIcDirty();
    // refill the water quality inputs with the preset values
    const presets = state.icData.preset_values || {};
    if (presets[key]) {
        const pv = presets[key];
        const map = icPresetVarMap();
        Object.keys(pv).forEach(f => {
            const inputId = map[f];
            if (inputId) { const el = $(inputId); if (el && el.dataset.icPreset === '0') el.value = pv[f]; }
        });
    }
    toast(`营养状态已设为「${(state.icData.trophic_presets || {})[key]}」，记得点「保存到案例」`, 'info');
}

// fabm variable name -> input element id
function icPresetVarMap() {
    const map = {};
    (state.icData.modules || []).forEach(m => {
        Object.keys(m.init || {}).forEach(p => {
            if (map[p] === undefined) map[p] = `icv-${m.name}-${p}`;
        });
    });
    return map;
}

function applyTrophicToFields() {
    const key = state.icData && state.icData.trophic;
    const presets = (state.icData && state.icData.preset_values) || {};
    const pv = presets[key];
    if (!pv) { toast('当前营养状态没有可用预设', 'warning'); return; }
    const map = icPresetVarMap();
    let n = 0;
    Object.keys(pv).forEach(f => {
        const id = map[f];
        if (!id) return;
        const el = $(id);
        if (el) { el.value = pv[f]; n++; }
    });
    toast(`已回填 ${n} 个变量`, 'success');
    icIcDirty();
}

function applyPresetToFields() {
    const presets = (state.icData && state.icData.preset_values) || {};
    const keys = Object.keys(presets);
    if (!keys.length) { toast('没有可套用的预设', 'warning'); return; }
    const key = keys.length === 1 ? keys[0] : state.icData.trophic || keys[0];
    state.icData.trophic = key;
    renderTrophicPicker(state.icData);
    const pv = presets[key];
    // apply onto every input that still holds its original factory value
    const map = icPresetVarMap();
    let n = 0;
    document.querySelectorAll('[id^="icv-"]').forEach(el => {
        const varName = (el.id || '').slice(4);
        if (el.dataset.icPreset === '1' && pv[varName] !== undefined && !el.dataset.icUser) {
            el.value = pv[varName]; n++;
        }
    });
    // also fill inputs generated for variables the case does not declare yet
    Object.keys(pv).forEach(f => {
        if (document.getElementById(`icv-new-${f}`)) {
            const el2 = $(`icv-new-${f}`);
            if (!el2.dataset.icUser) { el2.value = pv[f]; n++; }
        }
    });
    toast(`已套用「${(state.icData.trophic_presets || {})[key]}」预设 ${n} 项`, 'success');
    icIcDirty();
}

function renderIcWaterQuality() {
    const host = $('ic-wq-modules');
    if (!host) return;
    const d = state.icData || {};
    const mods = d.modules || [];
    const q = ($('ic-wq-search') ? $('ic-wq-search').value : '').trim().toLowerCase();
    const presets = d.preset_values || {};
    const pv = presets[d.trophic] || {};
    const map = icPresetVarMap();

    if (!mods.length) {
        host.innerHTML = `<div class="empty-state"><div class="icon">🧫</div>
            当前案例的 fabm.yaml 中没有带 initialization 的模块；可用「套用预设数值」生成初值。</div>`;
        renderIcExtraVars(pv);
        return;
    }

    const grouped = {};
    mods.forEach(m => { (grouped[m.category] = grouped[m.category] || []).push(m); });

    host.innerHTML = Object.keys(grouped).map(cat => {
        const cards = grouped[cat].map(m => {
            const docs = m.docs || {};
            const rows = Object.keys(m.init || {}).map(p => {
                const id = map[p];
                const val = m.init[p];
                const isPreset = pv[p] !== undefined && Math.abs(Number(pv[p]) - Number(val)) < 1e-9;
                const dd = docs[p] || {};
                const unit = dd.unit || (m.units && m.units[p]) || 'g/m³';
                const zh = dd.zh || '';
                const en = dd.desc_en || dd.desc || '';
                const descHtml = zh
                    ? `<span class="ic-desc" title="${escapeAttr(zh + (en && en !== zh ? ' — ' + en : ''))}">${escapeHtml(zh)}</span>`
                    : (en ? `<span class="ic-desc ic-desc-en" title="${escapeAttr(en)}">${escapeHtml(en)}</span>` : '');
                return `<div class="ic-row">
                    <label title="${escapeAttr(p)}">${escapeHtml(p)}</label>
                    <input class="form-input" type="number" step="any" id="${id}" value="${val}"
                           data-ic-preset="${isPreset ? 1 : 0}" onchange="onIcVarEdit(this)">
                    <span class="ic-unit">${escapeHtml(unit)}</span>
                    ${descHtml}
                </div>`;
            }).join('');
            const searchHit = !q || m.name.toLowerCase().includes(q) ||
                (m.long_name || '').toLowerCase().includes(q) ||
                (m.desc || '').toLowerCase().includes(q) ||
                Object.keys(m.init || {}).some(p =>
                    p.toLowerCase().includes(q) ||
                    ((docs[p] || {}).desc || '').toLowerCase().includes(q));
            if (!searchHit) return '';
            const modDesc = m.desc
                ? `<div class="ic-mod-desc">${escapeHtml(m.desc)}${m.model ? ` <code>${escapeHtml(m.model)}</code>` : ''}</div>`
                : '';
            return `<div class="ic-mod">
                <div class="ic-mod-title"><span style="color:${m.color};">●</span>
                    ${escapeHtml(m.name)}
                    <em>${escapeHtml(m.long_name)}</em>
                </div>
                ${modDesc}
                <div class="ic-rows">${rows || '<div style="font-size:11px;color:var(--text-muted);">（无初始条件）</div>'}</div>
            </div>`;
        }).join('');
        return `<div class="ic-group"><div class="ic-group-title">${escapeHtml(cat)}</div>${cards}</div>`;
    }).join('') || '<div class="empty-state"><div class="icon">🔍</div>没有匹配的模块</div>';

    renderIcExtraVars(pv);
}

// Variables that are not declared in fabm instances yet – allow typing them anyway
function renderIcExtraVars(pv) {
    const host = $('ic-wq-modules');
    if (!host) return;
    const d = state.icData || {};
    const known = {};
    (d.modules || []).forEach(m => Object.keys(m.init || {}).forEach(p => known[p] = 1));
    const extra = Object.keys(pv).filter(f => !known[f] && f !== 'macro_sD');
    if (!extra.length) return;
    const rows = extra.map(f => {
        const has = document.getElementById(`icv-new-${f}`) !== null;
        if (has) return '';
        return `<div class="ic-row">
            <label title="${escapeAttr(f)}">${escapeHtml(f)}</label>
            <input class="form-input" type="number" step="any" id="icv-new-${f}" value="${pv[f]}"
                   data-ic-preset="1" onchange="onIcVarEdit(this)">
            <span class="ic-unit">g/m³</span>
        </div>`;
    }).join('');
    if (!rows) return;
    const div = document.createElement('div');
    div.className = 'ic-group';
    div.innerHTML = `<div class="ic-group-title">📋 预设中的其他变量</div><div class="ic-mod"><div class="ic-rows">${rows}</div></div>`;
    host.appendChild(div);
}

function onIcVarEdit(el) {
    el.dataset.icUser = '1';
    icIcDirty();
}

async function saveInitConditions() {
    if (!state.activeCase) { toast('请先加载案例', 'warning'); return; }
    const d = state.icData || {};

    // water level / temperature
    const hydro = {
        elev_const: $('ic-elev') ? Number($('ic-elev').value) : 0,
        temp_const: $('ic-temp') ? Number($('ic-temp').value) : 15,
        surface_elev_abs: $('ic-surface-abs') && $('ic-surface-abs').value !== '' ? Number($('ic-surface-abs').value) : null,
        datum_abs: $('ic-datum-abs') && $('ic-datum-abs').value !== '' ? Number($('ic-datum-abs').value) : null,
    };

    // water quality: read every visible input back into "<instance>.<variable>"
    const water_quality = {};
    const map = icPresetVarMap();
    document.querySelectorAll('[id^="icv-"]').forEach(el => {
        const id = el.id || '';
        if (id.startsWith('icv-new-')) {
            const varName = id.slice(8);
            water_quality[varName] = Number(el.value);
        } else {
            const rest = id.slice(4);           // icv-<instance>-<variable>
            const i = rest.indexOf('-');
            if (i < 1) return;
            water_quality[rest.slice(0, i) + '.' + rest.slice(i + 1)] = Number(el.value);
        }
    });

    const macroEl = $('ic-macro-sd');
    const macrophytes = macroEl && macroEl.value !== '' ? { sD_max: Number(macroEl.value) } : null;

    const res = await api('/api/case/init_conditions', { method: 'POST', body: {
        hydro, water_quality, macrophytes, trophic: d.trophic || null,
    }});
    if (res.error) { toast(res.error, 'error'); return; }
    d.dirty = false;
    $('ic-save-status').textContent = res.notes && res.notes.length
        ? '✔ ' + res.notes.join('；')
        : '✔ 已保存';
    toast(`初始条件已保存${res.n_written ? `（${res.n_written} 项水质初值）` : ''}`, 'success');
    setTimeout(() => { if ($('ic-save-status')) $('ic-save-status').textContent = ''; }, 6000);
}

// keep the "elev_const = surface − datum" conversion live
document.addEventListener('DOMContentLoaded', () => {
    const sa = $('ic-surface-abs'), da = $('ic-datum-abs'), ev = $('ic-elev');
    const sync = () => {
        if (!sa || !da || !ev) return;
        const a = Number(sa.value), b = Number(da.value);
        if (sa.value !== '' && da.value !== '' && isFinite(a) && isFinite(b)) ev.value = (a - b).toFixed(4);
    };
    if (sa) sa.addEventListener('input', sync);
    if (da) da.addEventListener('input', sync);
    if (ev) ev.addEventListener('input', () => { icIcDirty(); });
});

// ── Run Control ───────────────────────────────────────────────────────
async function startRun() {
    if (!state.activeCase) { toast('请先加载案例', 'error'); return; }
    const res = await api('/api/run/start', {method:'POST'});
    if (!res.success) { toast(res.error || '启动失败', 'error'); return; }
    $('btn-start-run').disabled = true;
    $('btn-stop-run').disabled = false;
    $('run-log').innerHTML = '';
    toast('模型已启动', 'success');
    // Request browser notification permission so ETA/completion alerts can fire
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission().then(p => {
            if (p === 'granted') toast('已启用运行通知', 'info');
        });
    }
    state.etaNotified = new Set();  // reset ETA threshold tracker
    state.lastRunStatus = 'running';
    state.runPollTimer = setInterval(pollRunStatus, 2000);
}

async function stopRun() {
    await api('/api/run/stop', {method:'POST'});
    $('btn-stop-run').disabled = true;
    toast('已发送停止指令', 'info');
}

function notifyUser(title, body) {
    // Browser notification + visible toast (so it works even without permission)
    toast(`${title}: ${body}`, 'info');
    if ('Notification' in window && Notification.permission === 'granted') {
        try { new Notification(title, { body, icon: '/static/favicon.ico' }); } catch (e) {}
    }
}

async function pollRunStatus() {
    const s = await api('/api/run/status');
    $('run-stat-status').textContent = {idle:'空闲',running:'运行中',completed:'已完成',failed:'失败',stopped:'已停止'}[s.status] || s.status;
    $('run-stat-progress').textContent = fmt(s.progress,1) + '%';
    $('run-stat-elapsed').textContent = fmt(s.elapsed,0) + 's';
    $('run-stat-eta').textContent = s.eta_minutes > 0 ? fmt(s.eta_minutes,1) + 'min' : '-';
    $('run-progress-fill').style.width = s.progress + '%';
    $('run-percent').textContent = fmt(s.progress,1) + '%';
    $('run-step-info').textContent = `步数: ${s.current_step.toLocaleString()} / ${s.total_steps.toLocaleString()}`;
    // Status display
    const dot = document.querySelector('#run-status-display .status-dot');
    dot.className = 'status-dot ' + s.status;
    document.querySelector('#run-status-display').childNodes[1].textContent = {idle:'空闲',running:'运行中',completed:'已完成',failed:'失败',stopped:'已停止'}[s.status];
    // ETA threshold notifications (fire once per threshold as ETA decreases past it)
    if (s.status === 'running' && s.eta_minutes > 0 && state.etaNotified) {
        for (const threshold of [60, 15, 5]) {
            if (s.eta_minutes <= threshold && !state.etaNotified.has(threshold)) {
                state.etaNotified.add(threshold);
                notifyUser('3DWET 运行提醒', `预计剩余 ${fmt(s.eta_minutes,0)} 分钟（${threshold}分钟阈值）`);
            }
        }
    }
    // Logs
    const log = $('run-log');
    const currentLines = log.children.length;
    if (s.logs.length > currentLines) {
        for (let i = currentLines; i < s.logs.length; i++) {
            const line = s.logs[i];
            const div = document.createElement('div');
            div.className = 'log-line ' + (line.includes('ERROR')?'error':line.includes('完成')?'success':line.includes('INFO')?'info':'');
            div.textContent = line;
            log.appendChild(div);
        }
        log.scrollTop = log.scrollHeight;
    }
    // Status flip notifications
    if (['completed','failed','stopped'].includes(s.status)) {
        clearInterval(state.runPollTimer);
        $('btn-start-run').disabled = false;
        $('btn-stop-run').disabled = true;
        if (state.lastRunStatus !== s.status) {
            state.lastRunStatus = s.status;
            if (s.status === 'completed') {
                notifyUser('🎉 模型运行完成', `共 ${s.current_step.toLocaleString()} 步，耗时 ${fmt(s.elapsed/60,1)} 分钟`);
                loadVariables();
                loadDashboardSummary();
            } else if (s.status === 'failed') {
                notifyUser('❌ 模型运行失败', '请查看运行日志排查原因');
            } else if (s.status === 'stopped') {
                notifyUser('⏹ 模型已停止', `运行至第 ${s.current_step.toLocaleString()} 步`);
            }
        }
    }
}

// ── Variables ─────────────────────────────────────────────────────────
async function loadVariables() {
    const v = await api('/api/results/variables');
    if (!v.error) {
        state.variables2d = v['2d'] || [];
        state.variables3d = v['3d'] || [];
        // 时间轴真实日期：2d/3d 文件按 step_2d/step_3d 抽帧，间隔不一定是 1 天，
        // 所以必须按帧查日历日期，不能直接把滑块索引当成“第 N 天”。
        state.timeLabels2d = v['time_labels_2d'] || [];
        state.timeLabels3d = v['time_labels_3d'] || [];
        state.timeLabels = (state.timeLabels3d.length >= state.timeLabels2d.length)
            ? state.timeLabels3d : state.timeLabels2d;
        // Set time slider max
        const nt = Math.max(v.timesteps_2d||0, v.timesteps_3d||0);
        $('viz2d-time').max = Math.max(0, nt-1);
        $('stat-timesteps').textContent = nt || '-';
        // 告知用户抽帧间隔，避免把“最后帧序号”误读成运行天数
        if (state.timeLabels.length >= 2 && nt > 0) {
            const stepDays = (() => {
                const p = (s) => { const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(s); return m ? Date.UTC(+m[1], +m[2]-1, +m[3]) : null; };
                const a = p(state.timeLabels[0]), b = p(state.timeLabels[1]);
                return (a != null && b != null) ? (b - a) / 86400000 : null;
            })();
            $('stat-timesteps').title = stepDays
                ? `共 ${nt} 帧，抽帧间隔 ${fmt(stepDays,2)} 天(${state.timeLabels[0]} → ${state.timeLabels[state.timeLabels.length-1]})`
                : `共 ${nt} 帧(${state.timeLabels[0]} → ${state.timeLabels[state.timeLabels.length-1]})`;
        }
    }
    // Populate all variable selects
    const allVars = [...state.variables3d, ...state.variables2d];
    const unique = {};
    allVars.forEach(v => { if (!unique[v.name]) unique[v.name] = v; });
    const varList = Object.values(unique);
    ['viz2d-var','viz3d-var','viz3d-iso-var','viz3d-avg-var','ts-var','cal-var-select','cal-data-var'].forEach(id => {
        const sel = $(id);
        if (!sel) return;
        sel.innerHTML = '';
        varList.forEach(v => {
            const opt = document.createElement('option');
            opt.value = v.name;
            // 区分有无垂向层：4D(time,sigma,yc,xc) 才能做垂向热图；
            // 3D 的通量/表层量物理上不随深度分层，单独标注避免误导。
            const hasLev = v.ndim === 4 || (Array.isArray(v.dims) && v.dims.indexOf('sigma') >= 0);
            opt.textContent = `${v.long_name || v.name} [${v.units||''}]${hasLev ? '' : ' ⊘无垂向层'}`;
            sel.appendChild(opt);
        });
    });
    // 无结果时给 2D/3D 视图注入“水深(地形)”占位变量：至少能看到湖泊网格与湖盆
    if (!varList.length) {
        ['viz2d-var','viz3d-iso-var'].forEach(id => {
            const sel = $(id);
            if (!sel) return;
            const opt = document.createElement('option');
            opt.value = '__bathy__';
            opt.textContent = '水深（地形 bathymetry）[m]';
            sel.appendChild(opt);
        });
    }
}

// ── Dashboard ─────────────────────────────────────────────────────────
async function loadDashboardSummary() {
    const summary = await api('/api/dashboard/summary');
    if (summary.error) return;
    const container = $('dashboard-vars');
    const entries = Object.entries(summary).slice(0, 8);
    if (!entries.length) { container.innerHTML = '<div class="empty-state">无数据</div>'; return; }
    container.innerHTML = `<div class="grid-2">` + entries.map(([k,v]) => `
        <div style="padding:10px;background:var(--bg-tertiary);border-radius:6px;">
            <div style="font-size:12px;color:var(--text-secondary);">${v.long_name || k}</div>
            <div style="font-size:18px;font-weight:600;margin-top:2px;">${fmt(v.mean,3)} <span style="font-size:11px;color:var(--text-muted);">${v.units||''}</span></div>
            <div style="font-size:10px;color:var(--text-muted);">范围: ${fmt(v.min,3)} ~ ${fmt(v.max,3)}</div>
        </div>`).join('') + '</div>';
    // Also load mini-heatmaps
    loadDashboardMiniHeatmaps();
}

async function loadDashboardMiniHeatmaps() {
    const container = $('dashboard-mini-heatmaps');
    if (!container) return;
    const data = await api('/api/results/state_vars_surface');
    if (data.error) { container.innerHTML = `<div class="empty-state">${data.error}</div>`; return; }
    const entries = Object.entries(data);
    if (!entries.length) { container.innerHTML = '<div class="empty-state">无变量数据</div>'; return; }
    let html = '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;">';
    for (const [vname, info] of entries) {
        const canvasId = `mini-heat-${vname.replace(/[^a-zA-Z0-9_]/g, '_')}`;
        html += `<div style="background:var(--bg-tertiary);border-radius:6px;padding:8px;">
            <div style="font-size:11px;color:var(--text-secondary);">${info.long_name || vname}</div>
            <canvas id="${canvasId}" width="120" height="100" style="width:100%;background:#1a1d27;border-radius:4px;"></canvas>
            <div style="font-size:10px;color:var(--text-muted);">${fmt(info.min,3)} ~ ${fmt(info.max,3)} ${info.units||''} (均值 ${fmt(info.mean,3)})</div>
        </div>`;
    }
    html += '</div>';
    container.innerHTML = html;
    // Render each mini-heatmap
    for (const [vname, info] of entries) {
        const canvasId = `mini-heat-${vname.replace(/[^a-zA-Z0-9_]/g, '_')}`;
        drawHeatmap(canvasId, info.data, info.min, info.max);
    }
}

// ── 2D Visualization ──────────────────────────────────────────────────
async function initViz2d() {
    if (!state.variables2d.length && !state.variables3d.length) await loadVariables();
    if ($('viz2d-var').options.length) updateViz2d();
}

async function updateViz2d() {
    const varName = $('viz2d-var').value;
    const timestep = Number($('viz2d-time').value);
    const level = Number($('viz2d-level').value);
    const dateLabel = (state.timeLabels && state.timeLabels[timestep]) || null;
    $('viz2d-time-label').textContent = dateLabel ? `第 ${timestep} 帧 · ${dateLabel}` : `${timestep}`;
    // 占位变量：无模型结果时显示湖盆水深（来自 bathymetry.nc）
    if (varName === '__bathy__') {
        const g = await api('/api/geo/grid');
        if (g.error) { toast(g.error, 'error'); return; }
        let vmax = 0;
        for (const row of g.depth) for (const v of row) if (v != null && v > vmax) vmax = v;
        drawHeatmap('viz2d-canvas', g.depth, 0, vmax);
        $('viz2d-min').textContent = '0';
        $('viz2d-max').textContent = fmt(vmax, 4);
        $('viz2d-info').textContent = `变量: 水深（地形 bathymetry.nc，尚无模型结果时的占位显示）| 形状: ${g.ny}×${g.nx}`;
        drawColorbar('viz2d-colorbar', 0, vmax);
        return;
    }
    const data = await api(`/api/results/2d?var=${varName}&time=${timestep}&level=${level}`);
    if (data.error) { toast(data.error, 'error'); return; }
    drawHeatmap('viz2d-canvas', data.data, data.min, data.max);
    $('viz2d-min').textContent = fmt(data.min,4);
    $('viz2d-max').textContent = fmt(data.max,4);
    $('viz2d-info').textContent = `变量: ${varName} | 时步: ${timestep}${dateLabel ? ' (' + dateLabel + ')' : ''} | 均值: ${fmt(data.mean,4)} | 形状: ${data.shape?.join('×')}`;
    drawColorbar('viz2d-colorbar', data.min, data.max);
    // Overlay polygon vertices if any
    if (state.viz2dPolygon && state.viz2dPolygon.length) drawViz2dPolygonOverlay();
}

// Variable change handler: populate layer dropdown based on variable dimension
async function onViz2dVarChange() {
    const varName = $('viz2d-var').value;
    // Determine if 3D variable by checking variables3d list
    const is3d = state.variables3d.some(v => v.name === varName);
    const levelSel = $('viz2d-level');
    levelSel.innerHTML = '';
    if (is3d) {
        // GETM sigma: index 0=底, N-1=面. Default to surface (last).
        // We don't know N without metadata; use 0..10 placeholder, surface as -1
        // Real N comes from /api/results/variables; fall back to 0..10
        const nlev = state.nlev || 11;
        for (let k = nlev - 1; k >= 0; k--) {
            const opt = document.createElement('option');
            opt.value = k;
            // GETM: 0=底, nlev-1=面; level param: positive=k, -1=last
            opt.textContent = k === nlev - 1 ? `表层 (k=${k})` : (k === 0 ? `底层 (k=${k})` : `层 k=${k}`);
            levelSel.appendChild(opt);
        }
    } else {
        const opt = document.createElement('option');
        opt.value = 0;
        opt.textContent = '2D 变量（无垂向层）';
        levelSel.appendChild(opt);
    }
    updateViz2d();
}

// ── Viz2d Interaction Tools ───────────────────────────────────────────
state.viz2dTool = 'inspect';
state.viz2dPolygon = [];      // list of [i, j] in grid coords
state.viz2dCellSize = { w: 0, h: 0, cols: 0, rows: 0 };

function setViz2dTool(tool) {
    state.viz2dTool = tool;
    document.querySelectorAll('#viz2d-tools .btn').forEach(b => {
        b.classList.toggle('active', b.dataset.tool === tool);
    });
    const canvas = $('viz2d-canvas');
    canvas.style.cursor = tool === 'inspect' ? 'default' : 'crosshair';
    const clearBtn = $('viz2d-clear-poly');
    const submitBtn = $('viz2d-submit-poly');
    const showPolyBtns = (tool === 'polygon' && state.viz2dPolygon.length > 0);
    clearBtn.style.display = showPolyBtns ? '' : 'none';
    submitBtn.style.display = (tool === 'polygon' && state.viz2dPolygon.length >= 3) ? '' : 'none';
    if (tool !== 'polygon') { state.viz2dPolygon = []; if (canvas._redraw) updateViz2d(); }
}

function getCanvasCell(evt) {
    const canvas = $('viz2d-canvas');
    const rect = canvas.getBoundingClientRect();
    const x = (evt.clientX - rect.left) * (canvas.width / rect.width);
    const y = (evt.clientY - rect.top) * (canvas.height / rect.height);
    const { cols, rows } = state.viz2dCellSize;
    if (!cols || !rows) return null;
    const cellW = canvas.width / cols, cellH = canvas.height / rows;
    const i = Math.max(0, Math.min(cols - 1, Math.floor(x / cellW)));
    const j = Math.max(0, Math.min(rows - 1, Math.floor(y / cellH)));
    return { i, j, x, y };
}

function setupViz2dCanvasHandlers() {
    const canvas = $('viz2d-canvas');
    if (canvas._handlersAttached) return;
    canvas._handlersAttached = true;
    canvas.addEventListener('mousemove', (e) => {
        const cell = getCanvasCell(e);
        if (!cell) return;
        const coord = `i=${cell.i}, j=${cell.j}`;
        $('viz2d-coord').textContent = coord + (state.viz2dTool === 'polygon' && state.viz2dPolygon.length
            ? `  |  顶点数: ${state.viz2dPolygon.length}` : '');
    });
    canvas.addEventListener('click', (e) => {
        const cell = getCanvasCell(e);
        if (!cell) return;
        if (state.viz2dTool === 'cell') {
            extractCellTimeseries(cell.i, cell.j);
        } else if (state.viz2dTool === 'polygon') {
            state.viz2dPolygon.push([cell.i, cell.j]);
            drawViz2dPolygonOverlay();
            $('viz2d-clear-poly').style.display = '';
            if (state.viz2dPolygon.length >= 3) $('viz2d-submit-poly').style.display = '';
        } else if (state.viz2dTool === 'calibpt') {
            $('calib-add-i').value = cell.i;
            $('calib-add-j').value = cell.j;
            showModal('modal-add-calib');
        }
    });
}

function drawViz2dPolygonOverlay() {
    const canvas = $('viz2d-canvas');
    const ctx = canvas.getContext('2d');
    const { cols, rows } = state.viz2dCellSize;
    if (!cols || !rows || !state.viz2dPolygon.length) return;
    const cellW = canvas.width / cols, cellH = canvas.height / rows;
    ctx.strokeStyle = '#fbbf24';
    ctx.lineWidth = 2;
    ctx.beginPath();
    state.viz2dPolygon.forEach(([i, j], idx) => {
        const x = (i + 0.5) * cellW;
        const y = (j + 0.5) * cellH;
        if (idx === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    });
    if (state.viz2dPolygon.length >= 3) {
        const [i0, j0] = state.viz2dPolygon[0];
        ctx.lineTo((i0 + 0.5) * cellW, (j0 + 0.5) * cellH);
    }
    ctx.stroke();
    // Vertex markers
    ctx.fillStyle = '#fbbf24';
    state.viz2dPolygon.forEach(([i, j]) => {
        const x = (i + 0.5) * cellW, y = (j + 0.5) * cellH;
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fill();
    });
}

function clearViz2dPolygon() {
    state.viz2dPolygon = [];
    $('viz2d-clear-poly').style.display = 'none';
    $('viz2d-submit-poly').style.display = 'none';
    updateViz2d();
}

async function submitViz2dPolygon() {
    if (state.viz2dPolygon.length < 3) { toast('多边形至少需要 3 个顶点', 'error'); return; }
    const varName = $('viz2d-var').value;
    const level = Number($('viz2d-level').value);
    const data = await api('/api/results/timeseries_polygon', {
        method: 'POST', body: { var: varName, polygon: state.viz2dPolygon, layer: level }
    });
    if (data.error) { toast(data.error, 'error'); return; }
    showModal('modal-cell-ts');
    $('cell-ts-title').textContent = `区域平均时间序列 - ${varName} (${data.n_cells} 格)`;
    renderCellTsChart(data.times, data.values, `区域平均 ${varName}`, data.units);
    $('cell-ts-stats').innerHTML = `覆盖 ${data.n_cells} 个单元格 | 单位 ${data.units||''} | ${data.times.length} 个时间步`;
}

async function extractCellTimeseries(i, j) {
    const varName = $('viz2d-var').value;
    const level = Number($('viz2d-level').value);
    const data = await api(`/api/results/timeseries_cell?var=${varName}&i=${i}&j=${j}&layer=${level}`);
    if (data.error) { toast(data.error, 'error'); return; }
    showModal('modal-cell-ts');
    $('cell-ts-title').textContent = `单格时间序列 - ${varName} (i=${i}, j=${j})`;
    renderCellTsChart(data.times, data.values, `格点 (${i},${j}) ${varName}`, data.units);
    $('cell-ts-stats').innerHTML = `坐标: ${data.lon !== null ? `lon=${data.lon.toFixed(4)}, lat=${data.lat.toFixed(4)}` : ''} | 单位 ${data.units||''}`;
}

function renderCellTsChart(times, values, label, units) {
    if (state.charts.cellTs) state.charts.cellTs.destroy();
    const ctx = $('cell-ts-chart').getContext('2d');
    state.charts.cellTs = new Chart(ctx, {
        type: 'line',
        data: {
            labels: times,
            datasets: [{
                label: `${label} (${units||''})`,
                data: values,
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59,130,246,0.15)',
                tension: 0.3, fill: true, pointRadius: 3,
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            scales: { x: { ticks: { maxTicksToDisplay: 8 } } },
            plugins: { legend: { labels: { color: '#cbd5e1' } } }
        }
    });
}

async function confirmAddCalibPoint() {
    const name = $('calib-add-name').value.trim();
    const i = Number($('calib-add-i').value);
    const j = Number($('calib-add-j').value);
    const vars = $('calib-add-vars').value.split(',').map(s => s.trim()).filter(Boolean);
    if (!name) { toast('请填写点位名称', 'error'); return; }
    if (!vars.length) { toast('请填写率定变量', 'error'); return; }
    const res = await api('/api/calibration/points', { method: 'POST', body: { name, i, j, variables: vars } });
    if (res.error) { toast(res.error, 'error'); return; }
    toast(`率定点 ${name} 已添加`, 'success');
    closeModal('modal-add-calib');
    $('calib-add-name').value = '';
    if (window.loadCalPoints) loadCalPoints();
}

// Track nlev from case load for layer dropdown population
function setNlev(nlev) { state.nlev = nlev; }

function drawHeatmap(canvasId, data, vmin, vmax) {
    const canvas = $(canvasId);
    const ctx = canvas.getContext('2d');
    if (!data || !data.length) return;
    const rows = data.length, cols = data[0].length;
    const cw = canvas.width, ch = canvas.height;
    const cellW = cw / cols, cellH = ch / rows;
    ctx.clearRect(0, 0, cw, ch);
    const range = vmax - vmin || 1;
    for (let j = 0; j < rows; j++) {
        for (let i = 0; i < cols; i++) {
            const v = data[j][i];
            if (v === null || v === undefined || isNaN(v)) {
                ctx.fillStyle = '#1a1d27';
            } else {
                const t = Math.max(0, Math.min(1, (v - vmin) / range));
                ctx.fillStyle = heatColor(t);
            }
            ctx.fillRect(i * cellW, j * cellH, cellW + 0.5, cellH + 0.5);
        }
    }
    // Grid lines
    ctx.strokeStyle = 'rgba(255,255,255,0.05)';
    ctx.lineWidth = 0.5;
    for (let i = 0; i <= cols; i++) { ctx.beginPath(); ctx.moveTo(i*cellW,0); ctx.lineTo(i*cellW,ch); ctx.stroke(); }
    for (let j = 0; j <= rows; j++) { ctx.beginPath(); ctx.moveTo(0,j*cellH); ctx.lineTo(cw,j*cellH); ctx.stroke(); }
    // Record cell layout + attach canvas click handlers (viz2d only)
    if (canvasId === 'viz2d-canvas') {
        state.viz2dCellSize = { rows, cols, w: cellW, h: cellH };
        setupViz2dCanvasHandlers();
    }
}

function heatColor(t) {
    // Blue-Green-Yellow-Red colormap
    const stops = [[0,0,128],[0,128,255],[0,200,150],[255,220,0],[255,100,0],[200,0,0]];
    const idx = t * (stops.length - 1);
    const lo = Math.floor(idx), hi = Math.min(lo+1, stops.length-1);
    const f = idx - lo;
    const r = Math.round(stops[lo][0] + (stops[hi][0]-stops[lo][0])*f);
    const g = Math.round(stops[lo][1] + (stops[hi][1]-stops[lo][1])*f);
    const b = Math.round(stops[lo][2] + (stops[hi][2]-stops[lo][2])*f);
    return `rgb(${r},${g},${b})`;
}

function drawColorbar(id, vmin, vmax) {
    const el = $(id);
    const stops = [];
    for (let i = 0; i <= 10; i++) {
        const t = i / 10;
        stops.push(`${heatColor(t)} ${t*100}%`);
    }
    el.style.background = `linear-gradient(to right, ${stops.join(',')})`;
}

// ── 3D Visualization ──────────────────────────────────────────────────
async function initViz3d() {
    if (!state.variables3d.length) await loadVariables();
    updateViz3d();
    updateViz3dAvg();
    updateViz3dIso();
}

async function updateViz3dIso() {
    const varName = $('viz3d-iso-var')?.value;
    if (!varName) return;
    // 占位变量：无模型结果时显示湖盆 3D 地形
    if (varName === '__bathy__') {
        if (typeof renderBathymetry3D === 'function') await renderBathymetry3D();
        return;
    }
    const timestep = Number($('viz3d-iso-time')?.value || 0);
    const render = $('viz3d-iso-render')?.value || 'waterbody';  // waterbody / isosurface / cloud / surface2d
    const target = Number($('viz3d-iso-quality')?.value || 26);  // 每轴降采样格数（质量档）
    const level = Number($('viz3d-iso-level')?.value || 0);
    if (render === 'waterbody') {
        // 立体水体：湖底地形 + 逐层半透明分层面 + 四周剖面墙 + 垂向放大
        if (typeof render3DWaterBody === 'function') {
            await render3DWaterBody(varName, timestep, {
                target,
                level: Number($('viz3d-iso-layer')?.value ?? -1),   // -1 = 最上层
                ve: Number($('viz3d-iso-ve')?.value || 100),        // 垂向放大倍数
                stack: !$('viz3d-iso-stack')?.checked,              // 勾选则只显示单层
            });
        }
    } else if (render === 'cloud') {
        if (typeof render3DCloud === 'function') await render3DCloud(varName, timestep, target);
    } else if (render === 'isosurface') {
        if (typeof render3DSurface === 'function') await render3DSurface(varName, timestep, target);
    } else {
        if (typeof render2DAs3DSurface === 'function') await render2DAs3DSurface(varName, timestep, level);
    }
}

async function updateViz3d() {
    const varName = $('viz3d-var').value;
    const i = Number($('viz3d-i').value), j = Number($('viz3d-j').value);
    const t = Number($('viz3d-time').value);
    const _lbl = document.getElementById('viz3d-time-label');
    if (_lbl) _lbl.textContent = (state.timeLabels && state.timeLabels[t]) ? `第 ${t} 帧 · ${state.timeLabels[t]}` : `第 ${t} 帧`;
    const data = await api(`/api/results/profile?var=${varName}&time=${t}&i=${i}&j=${j}`);
    if (data.error) return;
    if (state.charts.profile) state.charts.profile.destroy();
    const ctx = $('viz3d-profile-chart').getContext('2d');
    state.charts.profile = new Chart(ctx, {
        type: 'line',
        data: { labels: data.sigma.map(s=>s.toFixed(2)), datasets: [{
            label: `${varName} (${data.units||''})`,
            data: data.profile,
            borderColor: '#3b82f6', backgroundColor: 'rgba(59,130,246,0.1)',
            fill: true, tension: 0.3, pointRadius: 3,
        }]},
        options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false,
            plugins: { title: {display:true, text:`垂向剖面 @ (${i},${j}) 时步${t}`, color:'#ccc'} },
            scales: { x: {ticks:{color:'#999'},grid:{color:'#333'}}, y: {ticks:{color:'#999'},grid:{color:'#333'}, title:{display:true,text:'Sigma',color:'#999'}} }
        }
    });
}

async function updateViz3dAvg() {
    const varName = $('viz3d-avg-var').value;
    const t = Number($('viz3d-avg-time').value);
    const data = await api(`/api/results/2d?var=${varName}&time=${t}&level=0`);
    if (data.error) return;
    drawHeatmap('viz3d-avg-canvas', data.data, data.min, data.max);
    drawColorbar('viz3d-colorbar', data.min, data.max);
}

// ── Time Series ───────────────────────────────────────────────────────
async function initTimeseries() {
    if (!$('ts-var').options.length) await loadVariables();
}

function toggleTsMode() {
    const mode = $('ts-mode').value;
    const isLayer = mode === 'layer';
    $('ts-layer-scope-group').style.display = isLayer ? 'block' : 'none';
    const scope = isLayer ? $('ts-layer-scope').value : mode;
    $('ts-point-group').style.display = scope === 'point' ? 'block' : 'none';
    $('ts-point-group2').style.display = scope === 'point' ? 'block' : 'none';
    $('ts-region-group').style.display = scope === 'region' ? 'block' : 'none';
}

async function extractTimeseries() {
    const varName = $('ts-var').value;
    const mode = $('ts-mode').value;
    const scope = mode === 'layer' ? $('ts-layer-scope').value : mode;
    let url = `/api/results/timeseries?var=${encodeURIComponent(varName)}`;
    if (scope === 'point') url += `&i=${$('ts-i').value}&j=${$('ts-j').value}`;
    else if (scope === 'region') url += `&region=${$('ts-region').value}`;
    else if (scope === 'lake') url += `&lake_avg=1`;
    if (mode === 'layer') url += `&per_layer=1`;
    const data = await api(url);
    if (data.error) { toast(data.error, 'error'); return; }
    if (state.charts.ts) state.charts.ts.destroy();
    const ctx = $('ts-chart').getContext('2d');
    // 上一轮若是"每一层"，先清掉旧热图，避免与新方式残留下图
    const tsHeat = $('ts-heatmap');
    if (tsHeat && $('ts-mode').value !== 'layer') {
        tsHeat.innerHTML = '';
        const oldCard = $('ts-heatmap-card');
        if (oldCard) oldCard.style.display = 'none';
    }

    let label;
    if (scope === 'lake') label = '全湖';
    else if (scope === 'region') label = `区域 ${$('ts-region').value}`;
    else label = `点位 (${$('ts-i').value},${$('ts-j').value})`;

    let chartCfg;
    if (mode === 'layer' && data.per_layer) {
        const nlev = data.series.length;
        const datasets = [];
        for (let k = 0; k < nlev; k++) {
            const col = heatColor(nlev <= 1 ? 0.5 : k / (nlev - 1));  // 表→底色阶
            datasets.push({
                label: `层${k}`,
                data: data.series[k],
                borderColor: col,
                backgroundColor: col,
                borderWidth: 1,
                pointRadius: 0,
                tension: 0.2,
            });
        }
        chartCfg = {
            type: 'line',
            data: { labels: data.times, datasets },
            options: { responsive: true, maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                plugins: { legend: { display: false },
                    title: { display: true, text: `${data.long_name || varName} · 每一层 (${nlev} 层) @ ${label}`, color: '#ccc' } },
                scales: { x: { ticks: { color: '#999', maxTicksLimit: 12 }, grid: { color: '#222' } },
                          y: { ticks: { color: '#999' }, grid: { color: '#333' }, title: { display: true, text: data.units || '', color: '#999' } } }
            }
        };
        // 同时产出「层 × 时间」垂向热图，直接看分层/温跃层演化，无需切换页面
        _vheatLast = data;
        if (tsHeat) {
            drawVerticalHeatmap('ts-heatmap', data, 'sigma');
            const cap = $('ts-heatmap-title');
            if (cap) cap.textContent = `垂向热图（层 × 时间）· ${label} · ${nlev} 层`;
            const card = $('ts-heatmap-card');
            if (card) card.style.display = 'block';
        }
        toast(`已提取每一层序列（${nlev} 层）`, 'success');
    } else {
        chartCfg = {
            type: 'line',
            data: { labels: data.times, datasets: [{
                label: `${data.long_name || varName} @ ${label}`,
                data: data.values, borderColor: '#10b981', backgroundColor: 'rgba(16,185,129,0.1)',
                fill: true, tension: 0.2, pointRadius: 0, borderWidth: 1.5,
            }]},
            options: { responsive: true, maintainAspectRatio: false,
                plugins: { legend: { labels: { color: '#ccc' } } },
                scales: { x: { ticks: { color: '#999', maxTicksLimit: 12 }, grid: { color: '#222' } }, y: { ticks: { color: '#999' }, grid: { color: '#333' }, title: { display: true, text: data.units || '', color: '#999' } } }
            }
        };
        toast('时间序列已提取', 'success');
    }
    state.charts.ts = new Chart(ctx, chartCfg);
}

// ── Vertical Heatmap (垂向热图) ───────────────────────────────────────
// 用 Plotly heatmap 绘制「层 × 时间」热图：悬停可读数值、可框选缩放、可导出 PNG。
// 纵轴默认水面在顶部，自下而上为 sigma 由大到小（层号由高到低）。
let _vheatLast = null;        // 最近一次 per_layer 结果（供"时间序列"页复用）
let _vheatDepthGrid = null;   // /api/geo/grid 水深网格（真实深度纵轴用）
let _vheatH = null;           // 换算深度用的局部水深（m）

/** 变量是否带垂向层（能生成垂向热图）。4D(time,sigma,yc,xc)，或 dims 含 sigma。 */
function varHasLevel(v) {
    if (!v) return false;
    return v.ndim === 4 || (Array.isArray(v.dims) && v.dims.indexOf('sigma') >= 0);
}

/** 构造一个变量下拉项；withName=true 时同时显示变量名（便于分辨同 long_name）。 */
function makeVarOption(v, withName) {
    const opt = document.createElement('option');
    const name = v.name || String(v);
    opt.value = name;
    const nm = v.long_name || name;
    const hasLev = varHasLevel(v);
    opt.textContent = withName
        ? `${nm} (${name})${hasLev ? '' : ' ⊘无垂向层'}`
        : `${nm} [${v.units || ''}]${hasLev ? '' : ' ⊘无垂向层'}`;
    opt.dataset.hasLevel = hasLev ? '1' : '';
    return opt;
}

async function initVHeat() {
    const sel = $('vheat-var');
    if (!sel) return;
    if (!sel.options.length) {
        if (!state.variables3d.length && !state.variables2d.length) await loadVariables();
        const all = [...state.variables3d, ...state.variables2d];
        const uniq = {};
        all.forEach(v => { if (v && v.name && !uniq[v.name]) uniq[v.name] = v; });
        const list = Object.values(uniq);
        // 有垂向层的放前面且单独成组：温室气体等模块里，通量与状态变量同前缀，
        // 混在一起很难挑，分组后能直接看到哪些能做垂向热图。
        const withLev = list.filter(v => varHasLevel(v));
        const noLev = list.filter(v => !varHasLevel(v));
        const gA = document.createElement('optgroup');
        gA.label = `有垂向层（可生成垂向热图）· ${withLev.length} 个`;
        withLev.forEach(v => sel.appendChild(makeVarOption(v, true)));
        if (noLev.length) {
            const gB = document.createElement('optgroup');
            gB.label = `无垂向层（水柱积分通量/表层量，物理上不随深度分层）· ${noLev.length} 个`;
            noLev.forEach(v => sel.appendChild(makeVarOption(v, true)));
        }
        // 默认选一个带层的变量，避免开页就撞上"不是 4D"的报错
        const cur = sel.value;
        if (!cur || !varHasLevel({ ndim: null, dims: null, name: cur })) {
            if (sel.querySelector('option[value="temp"]')) sel.value = 'temp';
            else if (withLev.length) sel.value = withLev[0].name;
        }
    }
    toggleVHeatScope();
}

function toggleVHeatScope() {
    const scope = $('vheat-scope')?.value || 'point';
    ['vheat-point-group', 'vheat-point-group2'].forEach(id => { const el = $(id); if (el) el.style.display = scope === 'point' ? 'block' : 'none'; });
    const rg = $('vheat-region-group'); if (rg) rg.style.display = scope === 'region' ? 'block' : 'none';
}

/** 载入水深网格并求出当前范围代表水深，用于"深度(m)"纵轴换算。 */
async function ensureVHeatDepth(scope) {
    if (_vheatDepthGrid) { _vheatLocalH(scope); return; }
    try {
        const g = await api('/api/geo/grid');
        _vheatDepthGrid = (g && g.depth) || null;
    } catch (e) { _vheatDepthGrid = null; }
    _vheatLocalH(scope);
}

function _vheatLocalH(scope) {
    _vheatH = null;
    if (!_vheatDepthGrid) return;
    try {
        if (scope === 'point') {
            const i = Number($('vheat-i')?.value), j = Number($('vheat-j')?.value);
            const row = _vheatDepthGrid[j];
            if (row) { const h = row[i]; if (typeof h === 'number' && !isNaN(h) && h > 0) _vheatH = h; }
            if (!_vheatH) { let mx = 0; _vheatDepthGrid.forEach(r => r.forEach(v => { if (typeof v === 'number' && isFinite(v) && v > mx) mx = v; })); _vheatH = mx || null; }
        } else {
            let mx = 0;
            _vheatDepthGrid.forEach(r => r.forEach(v => { if (typeof v === 'number' && isFinite(v) && v > mx) mx = v; }));
            _vheatH = mx || null;
        }
    } catch (e) { _vheatH = null; }
}

/** 与 varName 同模块（同前缀）且带垂向层的候选变量，用于无层变量时的引导。 */
function _vheatAlts(varName) {
    const cut = varName.indexOf('_');
    const prefix = cut > 0 ? varName.slice(0, cut) : '';
    const pool = [...(state.variables3d || []), ...(state.variables2d || [])];
    return pool
        .filter(v => varHasLevel(v) && v.name !== varName && v.name.indexOf(prefix + '_') === 0)
        .map(v => v.name);
}

async function updateVHeat() {
    const sel = $('vheat-var');
    const varName = sel ? sel.value : '';
    const scope = $('vheat-scope').value;
    if (!varName) { toast('请先选择变量', 'error'); return; }
    // 无垂向层的变量不必发请求：直接说明原因并给出同模块可替代的垂向变量
    const opt = (sel && sel.selectedIndex >= 0) ? sel.options[sel.selectedIndex] : null;
    const noLevel = !!(opt && opt.dataset && opt.dataset.hasLevel === '');
    if (noLevel) {
        const alts = _vheatAlts(varName);
        const head = `「${varName}」没有垂向层，不能生成垂向热图。它是水柱积分通量/表层量，` +
            `物理上本就不随深度分层——温室气体模块已正常编译并输出，不是编译问题。`;
        const msg = alts.length
            ? `${head}请改选同模块的垂向状态变量：${alts.join('、')}`
            : `${head}请在上方「有垂向层」分组中选择变量。`;
        toast(msg, 'error');
        const m = $('vheat-meta'); if (m) m.innerHTML = msg;
        return;
    }
    let url = `/api/results/timeseries?var=${encodeURIComponent(varName)}&per_layer=1`;
    if (scope === 'point') url += `&i=${$('vheat-i').value}&j=${$('vheat-j').value}`;
    else if (scope === 'region') url += `&region=${$('vheat-region').value}`;
    else url += `&lake_avg=1`;
    toast('正在生成垂向热图...', 'info');
    const data = await api(url);
    if (data.error) {
        toast(data.error, 'error');
        const m = $('vheat-meta');
        if (m) {
            let txt = data.error;
            if (Array.isArray(data.alts_4d) && data.alts_4d.length) {
                txt += '<br><br>可改选（同模块带垂向层的状态变量）：' + data.alts_4d.join('、');
            }
            m.innerHTML = txt;
        }
        return;
    }
    if (!data.per_layer || !data.series || !data.series.length) {
        const msg = data.error || '该变量不含垂向层（需要 4D 变量 time,sigma,yc,xc）。请改选带垂向层的变量。';
        toast(msg, 'error');
        const m = $('vheat-meta'); if (m) m.innerHTML = msg;
        return;
    }
    _vheatLast = data;
    const axis = $('vheat-axis') ? $('vheat-axis').value : 'sigma';
    if (axis === 'depth') await ensureVHeatDepth(scope);
    drawVerticalHeatmap('vheat-plotly', data, axis);
    const nlev = data.series.length;
    const ntime = data.times ? data.times.length : 0;
    const scopeLabel = scope === 'lake' ? '全湖平均' : scope === 'region' ? `区域 ${$('vheat-region').value}` : `点位 (${$('vheat-i').value},${$('vheat-j').value})`;
    const m = $('vheat-meta');
    if (m) m.innerHTML =
        `变量：<b>${data.long_name || varName}</b><br>范围：${scopeLabel}<br>垂向层数：<b>${nlev}</b><br>时间采样：<b>${ntime}</b> 点（步长 ${data.tstride || '?'}）<br>单位：${data.units || ''}<br>纵轴：${axis === 'depth' ? '真实深度 (m)' : axis === 'level' ? '层号' : 'sigma 坐标'}<br>鼠标悬停查看数值，可框选缩放`;
    toast('垂向热图已生成', 'success');
}

/**
 * 把 sigma 归一成「自水面算起的深度占比」数组：0=水面、1=湖底。
 * 兼容 [-1,0] / [0,1] / [-1,1] 三种取值约定，避免纵轴方向搞反。
 */
function _vheatDepthFrac(sigma) {
    let sMax = -Infinity, sMin = Infinity;
    (sigma || []).forEach(s => {
        if (typeof s === 'number' && isFinite(s)) { if (s > sMax) sMax = s; if (s < sMin) sMin = s; }
    });
    if (!isFinite(sMax)) return (sigma || []).map((_, k) => k / Math.max(1, (sigma || []).length - 1));
    const span = (sMax - sMin) || 1;
    return (sigma || []).map(s => (typeof s === 'number' && isFinite(s)) ? (sMax - s) / span : 1);
}

/**
 * 绘制「层 × 时间」垂向热图（Plotly heatmap）。
 * series: nlev × ntime；纵轴自上而下为水面→湖底。
 */
function drawVerticalHeatmap(containerId, data, axisMode) {
    const el = $(containerId);
    if (!el) return;
    if (typeof window.Plotly === 'undefined') {
        el.innerHTML = '<div style="padding:16px;color:#f87171">Plotly 未加载，无法绘制垂向热图</div>';
        return;
    }
    const series = (data && data.series) || [];
    const nlev = series.length;
    const ntime = nlev ? (series[0] ? series[0].length : 0) : 0;
    if (!nlev || !ntime) {
        el.innerHTML = '<div style="padding:16px;color:var(--text-muted)">没有可绘制的数据（该变量可能不是 4D 垂向变量）</div>';
        return;
    }

    // 纵轴标签：自上而下（层 nlev-1 → 层 0），水面在顶部
    const dfc = _vheatDepthFrac(data.layers || []);
    const yLabels = new Array(nlev);
    for (let r = 0; r < nlev; r++) {
        const k = nlev - 1 - r;
        if (axisMode === 'level') yLabels[r] = `层 ${k}`;
        else if (axisMode === 'depth') {
            const h = _vheatH;
            yLabels[r] = h ? (h * dfc[k]).toFixed(1) : String(k);
        } else {
            const s = (data.layers && data.layers[k] !== undefined) ? Number(data.layers[k]) : k;
            yLabels[r] = isFinite(s) ? s.toFixed(2) : String(k);
        }
    }
    const zRows = [];
    for (let r = 0; r < nlev; r++) {
        const row = series[nlev - 1 - r] || [];
        zRows.push(row.map(v => (v === null || v === undefined || isNaN(v)) ? null : v));
    }

    const times = data.times || [];
    const trace = {
        type: 'heatmap',
        x: times,
        y: yLabels,
        z: zRows,
        // 与 viz2d/drawHeatmap 一致的色阶
        colorscale: [
            [0, 'rgb(0,0,128)'], [0.2, 'rgb(0,128,255)'], [0.4, 'rgb(0,200,150)'],
            [0.6, 'rgb(255,220,0)'], [0.8, 'rgb(255,100,0)'], [1, 'rgb(200,0,0)']
        ],
        showscale: true,
        colorbar: { title: { text: data.units || '' }, thickness: 14, len: 0.85 },
        hovertemplate: '%{y}　%{x}<br><b>%{z}</b> ' + (data.units || '') + '<extra></extra>',
        xgap: 0.5, ygap: 0.5,
    };
    const layout = {
        paper_bgcolor: 'var(--bg-secondary)', plot_bgcolor: 'var(--bg-primary)',
        font: { family: 'Microsoft YaHei, sans-serif', size: 10, color: '#cbd5e1' },
        margin: { l: 62, r: 60, t: 26, b: 46 },
        xaxis: { title: { text: '时间', font: { size: 11 } }, tickangle: -30, automargin: true, showgrid: false },
        yaxis: { title: { text: axisMode === 'depth' ? '深度 (m)' : axisMode === 'level' ? '层号' : 'σ (sigma，顶=水面)' }, automargin: true, tickfont: { size: 9 } },
    };
    Plotly.react(el, [trace], layout, {
        responsive: true, displaylogo: false,
        toImageButtonOptions: { format: 'png', filename: `vheat_${data.var_name || 'profile'}` },
    });
}

// ── Calibration ───────────────────────────────────────────────────────
async function initCalibrate() {
    await loadCalPoints();
    if (!$('cal-var-select').options.length) await loadVariables();
}

async function loadCalPoints() {
    const points = await api('/api/calibration/points');
    const tbody = $('cal-points-table').querySelector('tbody');
    tbody.innerHTML = '';
    $('cal-point-select').innerHTML = '';
    $('cal-data-point').innerHTML = '';
    points.forEach(p => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${p.name}</td><td>(${p.i},${p.j})</td><td>${(p.variables||[]).join(', ')}</td>
            <td><button class="btn btn-sm btn-danger" onclick="deleteCalPoint('${p.id}')">删除</button></td>`;
        tbody.appendChild(tr);
        $('cal-point-select').addEventListener ? null : null;
        const opt = document.createElement('option'); opt.value = p.id; opt.textContent = p.name;
        $('cal-point-select').appendChild(opt);
        $('cal-data-point').appendChild(opt.cloneNode(true));
    });
}

function showAddPointModal() { showModal('modal-add-point'); }

async function addCalPoint() {
    const name = $('new-point-name').value || '未命名';
    const i = Number($('new-point-i').value), j = Number($('new-point-j').value);
    const vars = $('new-point-vars').value.split(',').map(s=>s.trim()).filter(Boolean);
    const res = await api('/api/calibration/points', {method:'POST', body:{name, i, j, variables:vars}});
    if (res.success) { toast('点位已添加', 'success'); closeModal('modal-add-point'); loadCalPoints(); }
}

async function deleteCalPoint(id) {
    await api(`/api/calibration/points?id=${id}`, {method:'DELETE'});
    loadCalPoints();
    toast('点位已删除', 'info');
}

async function saveCalData() {
    const pid = $('cal-data-point').value;
    const varName = $('cal-data-var').value;
    let values;
    try { values = JSON.parse($('cal-data-values').value); }
    catch { toast('JSON 格式错误', 'error'); return; }
    const res = await api('/api/calibration/data', {method:'POST', body:{point_id:pid, variable:varName, values}});
    toast(res.success ? '实测数据已保存' : '保存失败', res.success?'success':'error');
}

async function uploadCalData() {
    const pid = $('cal-data-point').value;
    if (!pid) { toast('请先选择点位', 'error'); return; }
    const fileInput = $('cal-data-file');
    if (!fileInput.files || !fileInput.files.length) {
        toast('请选择 CSV/XLSX 文件', 'error'); return;
    }
    const file = fileInput.files[0];
    const defaultVar = $('cal-data-default-var').value.trim() || 'temp';
    const formData = new FormData();
    formData.append('file', file);
    formData.append('point_id', pid);
    formData.append('variable', defaultVar);
    // Use XHR directly since api() helper only sends JSON
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/api/calibration/upload', true);
    xhr.onload = function() {
        try {
            const res = JSON.parse(xhr.responseText);
            if (res.success) {
                const stored = res.stored || {};
                const summary = Object.entries(stored).map(([v,n]) => `${v}: ${n} 行`).join(', ');
                toast(`上传成功: ${summary} (共 ${res.total_rows} 行)`, 'success');
                // Refresh comparison if currently viewing this point/var
                if ($('cal-point-select').value === pid) updateCalComparison();
            } else {
                toast(res.error || '上传失败', 'error');
            }
        } catch(e) {
            toast('上传响应解析失败: ' + xhr.responseText.substring(0,200), 'error');
        }
    };
    xhr.onerror = function() { toast('网络错误', 'error'); };
    xhr.send(formData);
}

async function updateCalComparison() {
    const pid = $('cal-point-select').value;
    const varName = $('cal-var-select').value;
    if (!pid || !varName) return;
    const data = await api(`/api/calibration/comparison?point_id=${pid}&variable=${varName}`);
    if (data.error) { $('cal-stats').innerHTML = `<span style="color:var(--danger)">${data.error}</span>`; return; }
    state.calLastData = data; // cache for scatter modal
    if (state.charts.cal) state.charts.cal.destroy();
    const ctx = $('cal-chart').getContext('2d');
    const simVals = data.simulated?.values || [];
    const simTimes = data.simulated?.times || [];
    const obsVals = (data.observed||[]).map(o=>o.value);
    const obsTimes = (data.observed||[]).map(o=>o.time);
    // Build unified x-axis: combine sim and obs times, dedup, sort
    const allTimes = Array.from(new Set([...simTimes, ...obsTimes])).sort();
    const simIdx = {}; simTimes.forEach((t, i) => { simIdx[t] = i; });
    const obsIdx = {}; obsTimes.forEach((t, i) => { obsIdx[t] = i; });
    const simSeries = allTimes.map(t => {
        if (t in simIdx) return simVals[simIdx[t]];
        // try nearest within 1 day; otherwise null
        const ot = new Date(t).getTime();
        if (isNaN(ot)) return null;
        let bestI = -1, bestLag = Infinity;
        for (let i=0;i<simTimes.length;i++) {
            const lag = Math.abs(new Date(simTimes[i]).getTime() - ot);
            if (lag < bestLag) { bestLag = lag; bestI = i; }
        }
        if (bestI<0 || bestLag > 86400000) return null;
        return simVals[bestI];
    });
    const obsSeries = allTimes.map(t => {
        if (t in obsIdx) return obsVals[obsIdx[t]];
        return null;
    });
    const varLabel = data.simulated?.long_name || varName;
    const units = data.simulated?.units || '';
    state.charts.cal = new Chart(ctx, {
        type: 'line',
        data: { labels: allTimes, datasets: [
            { label:`模拟 ${varName}`, data:simSeries, borderColor:'#3b82f6', backgroundColor:'transparent', tension:0.2, pointRadius:0, borderWidth:2, spanGaps:true },
            { label:`实测 ${varName}`, data:obsSeries, borderColor:'#f59e0b', backgroundColor:'transparent', pointRadius:4, borderWidth:0, showLine:false },
        ]},
        options: { responsive:true, maintainAspectRatio:false,
            plugins:{ legend:{labels:{color:'#ccc'}},
                tooltip:{ callbacks:{ title:(ctx)=>ctx[0].label, label:(c)=>`${c.dataset.label}: ${c.parsed.y===null?'—':c.parsed.y.toFixed(4)} ${units}` } } },
            scales:{ x:{ticks:{color:'#999',maxTicksLimit:10,autoSkip:true},grid:{color:'#222'}},
                     y:{ticks:{color:'#999'},grid:{color:'#333'}, title:{display:true,text:varLabel + (units?` (${units})`:'')}} }
        }
    });
    // Compute metrics using paired data from backend
    if (typeof computeMetrics === 'function' && data.scatter_pairs && data.scatter_pairs.length) {
        const simArr = data.scatter_pairs.map(p => p.sim);
        const obsArr = data.scatter_pairs.map(p => p.obs);
        const metrics = computeMetrics(obsArr, simArr);
        $('cal-stats').innerHTML = renderMetricsHTML(metrics);
    } else {
        $('cal-stats').innerHTML = `<div style="font-size:12px;color:var(--text-muted);">⚠️ 无配对数据 (实测 ${obsVals.length} 点，模拟 ${simVals.length} 时步)。需先上传实测数据并运行模型。</div>`;
    }
}

function showScatterModal() {
    const data = state.calLastData;
    if (!data || !data.scatter_pairs || !data.scatter_pairs.length) {
        toast('当前无配对数据。请先选择点位和变量并执行对比', 'error');
        return;
    }
    const pid = $('cal-point-select').value;
    const pointName = ($('cal-point-select').options[$('cal-point-select').selectedIndex] || {}).text || pid;
    const varName = data.variable;
    const units = data.simulated?.units || '';
    showModal('modal-scatter');
    $('scatter-meta').innerHTML = `点位: <strong>${pointName}</strong> | 变量: <strong>${varName}</strong> | 配对数: <strong>${data.scatter_pairs.length}</strong>${units ? ` | 单位: ${units}` : ''}`;
    const obsArr = data.scatter_pairs.map(p => p.obs);
    const simArr = data.scatter_pairs.map(p => p.sim);
    const metrics = computeMetrics(obsArr, simArr);
    $('scatter-metrics').innerHTML = renderMetricsHTML(metrics);
    // Plotly scatter with 1:1 line
    const ar = data.axis_range || {min: Math.min(...obsArr, ...simArr), max: Math.max(...obsArr, ...simArr)};
    const traceScatter = {
        x: obsArr, y: simArr, mode: 'markers', type: 'scatter',
        name: '实测 vs 模拟',
        marker: { color: '#3b82f6', size: 8, line: { color: '#1e3a8a', width: 1 }, opacity: 0.8 },
        text: data.scatter_pairs.map(p => p.time),
        hovertemplate: '实测: %{x:.3f}<br>模拟: %{y:.3f}<br>时间: %{text}<extra></extra>',
    };
    const trace11 = {
        x: [ar.min, ar.max], y: [ar.min, ar.max], mode: 'lines', type: 'scatter',
        name: '1:1 线', line: { color: '#f59e0b', width: 2, dash: 'dash' },
        hoverinfo: 'skip',
    };
    Plotly.newPlot('scatter-plot', [traceScatter, trace11], {
        title: { text: '实测 vs 模拟', font: { color: '#ccc', size: 14 } },
        xaxis: { title: { text: '实测' + (units?` (${units})`:''), color: '#ccc' }, color: '#999', gridcolor: '#333', range: [ar.min, ar.max], zeroline: false },
        yaxis: { title: { text: '模拟' + (units?` (${units})`:''), color: '#ccc' }, color: '#999', gridcolor: '#333', range: [ar.min, ar.max], zeroline: false },
        legend: { font: { color: '#ccc' }, x: 0.02, y: 0.98 },
        paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
        margin: { l: 60, r: 20, t: 40, b: 50 },
    }, { responsive: true });
}

// ── Auto Calibration ──────────────────────────────────────────────────
function initAutoCal() {
    // Common preset parameters (will be augmented with case-specific ones below)
    const commonParams = [
        {module:'diatoms', param:'cMuMax', default:2.4, min:1.0, max:3.5},
        {module:'greens', param:'cMuMax', default:1.0, min:0.5, max:2.5},
        {module:'cyanobacteria', param:'cMuMax', default:1.2, min:0.5, max:3.0},
        {module:'cladocerans', param:'kDRespZoo', default:0.2, min:0.05, max:0.5},
        {module:'copepods', param:'kDRespZoo', default:0.15, min:0.05, max:0.5},
        {module:'diatoms', param:'cChlPC', default:0.04, min:0.02, max:0.08},
        {module:'POM', param:'kDMinW', default:0.02, min:0.005, max:0.1},
        {module:'DOM', param:'kDMinW', default:0.01, min:0.002, max:0.05},
    ];
    const list = $('ac-params-list');
    list.innerHTML = '<div style="font-size:11px;color:var(--text-muted);margin-bottom:6px;">常用预设参数:</div>';
    commonParams.forEach(p => {
        const row = document.createElement('div');
        row.className = 'param-row';
        row.innerHTML = `
            <input type="checkbox" class="ac-param-check" data-module="${p.module}" data-param="${p.param}" style="margin-right:8px;">
            <span class="param-name">${p.module}.${p.param}</span>
            <span style="font-size:11px;color:var(--text-muted);width:60px;">默认: ${p.default}</span>
            <input type="number" class="param-value" style="width:70px;" placeholder="min" value="${p.min}" data-role="min">
            <input type="number" class="param-value" style="width:70px;" placeholder="max" value="${p.max}" data-role="max">`;
        list.appendChild(row);
    });
    // Load case-specific params from fabm.yaml if a case is loaded
    if (state.activeCase) {
        loadCaseFabmParamsForAutoCal();
    }
    // Load calibration points
    loadCalPoints().then(() => {
        const sel = $('ac-points');
        // Already populated by loadCalPoints
    });
}

async function loadCaseFabmParamsForAutoCal() {
    const data = await api('/api/config/fabm');
    if (data.error || !data.modules) return;
    const list = $('ac-params-list');
    // Avoid duplicating common params already in the list
    const existing = new Set();
    list.querySelectorAll('.ac-param-check').forEach(cb => {
        existing.add(`${cb.dataset.module}.${cb.dataset.param}`);
    });
    const caseParams = [];
    data.modules.forEach(m => {
        if (!m.enabled) return;
        (m.parameters || []).forEach(p => {
            if (typeof p.value !== 'number') return;  // skip bools/strings
            const key = `${m.name}.${p.name}`;
            if (existing.has(key)) return;
            const v = p.value;
            // Heuristic range: 0.5x to 2x default, with sensible lower bound
            let lo = v * 0.5, hi = v * 2;
            if (v >= 0) { lo = Math.max(0, v * 0.5); }
            caseParams.push({module: m.name, param: p.name, default: v, min: lo, max: hi});
        });
    });
    if (!caseParams.length) return;
    const header = document.createElement('div');
    header.style.cssText = 'font-size:11px;color:var(--text-muted);margin:8px 0 6px;';
    header.textContent = `案例参数 (来自 fabm.yaml, 共 ${caseParams.length} 个数值参数):`;
    list.appendChild(header);
    caseParams.forEach(p => {
        const row = document.createElement('div');
        row.className = 'param-row';
        // Format min/max to 6 sig figs to avoid ugly floats
        const fmtNum = v => Math.abs(v) < 0.001 ? v.toExponential(3) : v.toFixed(6).replace(/\.?0+$/,'');
        row.innerHTML = `
            <input type="checkbox" class="ac-param-check" data-module="${p.module}" data-param="${p.param}" style="margin-right:8px;">
            <span class="param-name" title="${p.module}.${p.param}">${p.module}.${p.param}</span>
            <span style="font-size:11px;color:var(--text-muted);width:60px;">默认: ${fmtNum(p.default)}</span>
            <input type="number" step="any" class="param-value" style="width:80px;" placeholder="min" value="${fmtNum(p.min)}" data-role="min">
            <input type="number" step="any" class="param-value" style="width:80px;" placeholder="max" value="${fmtNum(p.max)}" data-role="max">`;
        list.appendChild(row);
    });
}

async function startAutoCal() {
    const method = $('ac-method').value;
    const iterations = Number($('ac-iterations').value);
    const objective = $('ac-objective').value;
    const checked = document.querySelectorAll('.ac-param-check:checked');
    const params = [];
    checked.forEach(cb => {
        const row = cb.closest('.param-row');
        params.push({
            module: cb.dataset.module, param: cb.dataset.param,
            min: Number(row.querySelector('[data-role=min]').value),
            max: Number(row.querySelector('[data-role=max]').value),
        });
    });
    if (!params.length) { toast('请至少选择一个率定参数', 'error'); return; }
    if (!state.activeCase) { toast('请先加载案例', 'error'); return; }
    if (!state.calibPointsLoaded) {
        // Verify at least one calibration point with data exists
        const points = await api('/api/calibration/points');
        if (!points.length) { toast('请先在率定分析页添加至少一个率定点位并上传实测数据', 'error'); return; }
        state.calibPointsLoaded = true;
    }
    const res = await api('/api/calibration/auto/start', {method:'POST', body:{method, iterations, objective, params}});
    if (res.error) { toast(res.error, 'error'); return; }
    state.calibJobId = res.job_id;
    state.calibPollTimer = setInterval(pollAutoCalStatus, 3000);
    const paramSummary = params.map(p => `&nbsp;&nbsp;• ${p.module}.${p.param} [${p.min}, ${p.max}]`).join('<br>');
    $('ac-progress').innerHTML = `
        <div style="padding:20px;">
            <div style="font-size:14px;margin-bottom:12px;">🚀 自动率定已启动 (任务: ${res.job_id})</div>
            <div style="font-size:12px;color:var(--text-secondary);line-height:1.8;">
                方法: <strong>${method}</strong> | 目标函数: <strong>${objective}</strong> | 最大迭代: <strong>${iterations}</strong><br>
                率定参数: <strong>${params.length}</strong> 个<br>
                ${paramSummary}
            </div>
            <div id="ac-progress-detail" style="margin-top:16px;font-size:12px;">⏳ 等待第一次迭代结果...</div>
            <div style="margin-top:12px;display:flex;gap:8px;">
                <button class="btn btn-sm btn-danger" onclick="stopAutoCal()">⏹ 停止</button>
            </div>
        </div>`;
    toast(res.message || '自动率定已启动', 'success');
}

async function pollAutoCalStatus() {
    if (!state.calibJobId) return;
    const data = await api(`/api/calibration/auto/status?job_id=${state.calibJobId}`);
    if (data.error) {
        clearInterval(state.calibPollTimer); state.calibPollTimer = null;
        $('ac-progress-detail').innerHTML = `<span style="color:var(--danger)">查询失败: ${data.error}</span>`;
        return;
    }
    const pct = Math.round((data.progress || 0) * 100);
    const status = data.status;
    const hist = data.history || [];
    const last = hist.length ? hist[hist.length - 1] : null;
    let html = `<div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
        <div style="flex:1;background:var(--bg-tertiary);border-radius:6px;overflow:hidden;height:18px;">
            <div style="width:${pct}%;height:100%;background:linear-gradient(90deg,#3b82f6,#10b981);transition:width 0.3s;"></div>
        </div>
        <span style="font-size:12px;">${pct}%</span>
        <span style="font-size:12px;color:var(--text-muted);">${status}</span>
    </div>`;
    if (last) {
        const paramStr = (last.params || []).map(p => `${p.module}.${p.param}=${p.value.toFixed(4)}`).join(', ');
        html += `<div style="font-size:11px;color:var(--text-secondary);line-height:1.6;">
            迭代 #${last.iteration} | 目标=${(last.objective||0).toFixed(4)}<br>
            当前参数: ${paramStr}
        </div>`;
    }
    if (data.fallback) {
        html += `<div style="margin-top:8px;padding:8px;background:#fef3c7;border-radius:6px;font-size:11px;color:#92400e;">⚠️ ${data.fallback}</div>`;
    }
    if (data.error) {
        html += `<div style="margin-top:8px;color:var(--danger);font-size:11px;white-space:pre-wrap;">${data.error}</div>`;
    }
    $('ac-progress-detail').innerHTML = html;
    if (status === 'completed' || status === 'failed' || status === 'stopped') {
        clearInterval(state.calibPollTimer); state.calibPollTimer = null;
        if (status === 'completed' && data.result && data.result.best_params) {
            const best = data.result.best_params.map(p => `${p.module}.${p.param}=${p.value.toFixed(4)}`).join('<br>');
            const bestObj = (data.result.best_objective||NaN).toFixed(4);
            $('ac-progress-detail').innerHTML += `
                <div style="margin-top:12px;padding:12px;background:rgba(16,185,129,0.1);border:1px solid #10b981;border-radius:6px;">
                    <div style="font-size:13px;color:var(--success);font-weight:600;">✅ 率定完成</div>
                    <div style="font-size:11px;margin-top:6px;line-height:1.6;">
                        最优目标值: <strong>${bestObj}</strong><br>
                        最优参数:<br>&nbsp;&nbsp;${best}
                    </div>
                    <button class="btn btn-sm btn-success" style="margin-top:8px;" onclick="applyAutoCalResult()">💾 应用最优参数到 fabm.yaml</button>
                </div>`;
            toast('自动率定完成', 'success');
        } else if (status === 'failed') {
            toast('自动率定失败，请查看日志', 'error');
        } else if (status === 'stopped') {
            toast('自动率定已停止', 'info');
        }
    }
}

async function stopAutoCal() {
    if (!state.calibJobId) return;
    const res = await api('/api/calibration/auto/stop', {method:'POST', body:{job_id:state.calibJobId}});
    if (res.error) { toast(res.error, 'error'); return; }
    toast('已发送停止信号', 'info');
}

async function applyAutoCalResult() {
    if (!state.calibJobId) return;
    const res = await api('/api/calibration/auto/apply', {method:'POST', body:{job_id:state.calibJobId}});
    if (res.error) { toast(res.error, 'error'); return; }
    const applied = (res.applied || []).map(p => `${p.module}.${p.param}=${p.value.toFixed(4)}`).join(', ');
    toast(`已应用最优参数 (${applied})`, 'success');
}

// ── Map view (P0): Leaflet + model grid overlay ───────────────────────
const mapState = { map: null, grid: null, layer: null, cellsLayer: null, marker: null, field: null, xyMode: false };

function _mapColorScale(v, vmin, vmax) {
    if (v == null || !isFinite(v)) return null;
    const t = vmax > vmin ? (v - vmin) / (vmax - vmin) : 0;
    // blue (deep/shallow) → cyan → yellow → red, like the 2D viewer
    const stops = [[8, 48, 107], [33, 113, 181], [66, 146, 198], [145, 207, 96],
                   [239, 201, 76], [237, 141, 52], [204, 71, 39], [140, 29, 24]];
    const idx = Math.max(0, Math.min(stops.length - 1, Math.round(t * (stops.length - 1))));
    const [r, g, b] = stops[idx];
    return `rgb(${r},${g},${b})`;
}

async function loadMapGrid() {
    if (!state.activeCase) { $('map-status').textContent = '请先在“案例管理”加载一个案例。'; return; }
    if (typeof L === 'undefined') { $('map-status').textContent = 'Leaflet 未加载（检查 /static/vendor/leaflet.js）'; return; }
    $('map-status').textContent = '加载网格...';
    try {
        const g = await api('/api/geo/grid');
        if (g.error) { $('map-status').textContent = '加载失败: ' + g.error; return; }
        mapState.grid = g;
        initLeafletMap(g);
        drawMapLayer();
        await loadMapFieldVars();
        const nx = g.nx, ny = g.ny;
        const modeNote = mapState.xyMode ? '（无经纬度变量，按 x/y 米制坐标绘制）' : '';
        $('map-status').innerHTML = `网格 <strong>${nx} × ${ny}</strong>（原始 ${g.nx_full} × ${g.ny_full}${g.stride > 1 ? '，已抽稀 ×' + g.stride : ''}）${modeNote}，
        单元 ${g.dx ? g.dx.toFixed(0) + ' m' : '-'}。点击任意水格可提取该点时间序列。`;
    } catch (e) {
        console.error('loadMapGrid failed:', e);
        $('map-status').textContent = '地图加载出错: ' + (e && e.message ? e.message : e);
    }
}

function resetMapView() {
    mapState.grid = null;
    mapState.field = null;
    mapState.cellsLayer = null;
    mapState.marker = null;
    if (mapState.map) { try { mapState.map.remove(); } catch (e) {} mapState.map = null; }
    const c = $('map-container');
    if (c) c.innerHTML = '';
}

function initLeafletMap(g) {
    const el = $('map-container');
    if (mapState.map) { mapState.map.remove(); mapState.map = null; }
    el.innerHTML = '';
    let map;
    if (g.has_lonlat && g.bounds) {
        mapState.xyMode = false;
        const b = g.bounds;
        map = L.map(el, { preferCanvas: true, zoomSnap: 0.5 }).fitBounds(
            [[b.s, b.w], [b.n, b.e]]);
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 18, attribution: '© OpenStreetMap contributors',
        }).addTo(map);
    } else {
        // 无经纬度的网格：退化为 x/y 米制坐标 + CRS.Simple 平面绘制，
        // 保证任何案例（理论湖、本地坐标网格）都至少能看到网格边界与湖盆形态。
        mapState.xyMode = true;
        map = L.map(el, { crs: L.CRS.Simple, preferCanvas: true, zoomSnap: 0.25,
                          attributionControl: false, minZoom: -8 });
    }
    mapState.map = map;
    map.on('click', onMapClick);
    // 页面从隐藏切换到显示时 Leaflet 量不到容器尺寸，必须 invalidateSize 才会渲染
    setTimeout(() => { if (mapState.map) mapState.map.invalidateSize(); }, 80);
}

function _cellRectangles(g) {
    // Build one rectangle per water cell; corners extrapolated from neighbours
    const rects = [];
    const lat = g.lat, lon = g.lon;
    for (let j = 0; j < g.ny; j++) {
        for (let i = 0; i < g.nx; i++) {
            const la = lat[j][i], lo = lon[j][i];
            if (la == null || lo == null) continue;
            const laN = (j + 1 < g.ny && lat[j + 1][i] != null) ? lat[j + 1][i] : la;
            const laS = (j - 1 >= 0 && lat[j - 1][i] != null) ? lat[j - 1][i] : la;
            const loE = (i + 1 < g.nx && lon[j][i + 1] != null) ? lon[j][i + 1] : lo;
            const loW = (i - 1 >= 0 && lon[j][i - 1] != null) ? lon[j][i - 1] : lo;
            rects.push({
                i, j,
                s: (la + laS) / 2, n: (la + laN) / 2,
                w: (lo + loW) / 2, e: (lo + loE) / 2,
            });
        }
    }
    return rects;
}

function _cellRectanglesXY(g) {
    // x/y 米制坐标（1 维坐标轴）下的单元矩形：CRS.Simple 里 [lat,lng] 即 [y,x]
    const rects = [];
    const x = g.x || [], y = g.y || [];
    const dx = x.length > 1 ? Math.abs(x[1] - x[0]) : 1;
    const dy = y.length > 1 ? Math.abs(y[1] - y[0]) : 1;
    for (let j = 0; j < g.ny && j < y.length; j++) {
        for (let i = 0; i < g.nx && i < x.length; i++) {
            rects.push({
                i, j,
                s: y[j] - dy / 2, n: y[j] + dy / 2,
                w: x[i] - dx / 2, e: x[i] + dx / 2,
            });
        }
    }
    return rects;
}

function drawMapLayer() {
    const g = mapState.grid;
    if (!g || !mapState.map) return;
    if (mapState.cellsLayer) { mapState.map.removeLayer(mapState.cellsLayer); mapState.cellsLayer = null; }
    const mode = $('map-layer').value;
    let values, vmin, vmax, label;
    if (mode === 'result' && mapState.field) {
        values = mapState.field.values;
        vmin = mapState.field.min; vmax = mapState.field.max;
        label = mapState.field.var;
    } else {
        values = g.depth;
        vmin = 0; vmax = 0;
        for (const row of g.depth) for (const v of row) if (v != null && v > vmax) vmax = v;
        label = '水深 (m)';
    }
    const layer = L.layerGroup();
    let drawn = 0;
    let bS = Infinity, bW = Infinity, bN = -Infinity, bE = -Infinity;
    const rects = mapState.xyMode ? _cellRectanglesXY(g) : _cellRectangles(g);
    for (const r of rects) {
        const v = (values && values[r.j] ? values[r.j][r.i] : null);
        if (v == null) continue;
        const col = _mapColorScale(v, vmin, vmax);
        if (!col) continue;
        L.rectangle([[r.s, r.w], [r.n, r.e]], {
            color: col, weight: 0.5, fillColor: col, fillOpacity: 0.75,
        }).addTo(layer);
        drawn++;
        if (r.s < bS) bS = r.s;
        if (r.n > bN) bN = r.n;
        if (r.w < bW) bW = r.w;
        if (r.e > bE) bE = r.e;
    }
    layer.addTo(mapState.map);
    mapState.cellsLayer = layer;
    if (mapState.xyMode && drawn) mapState.map.fitBounds([[bS, bW], [bN, bE]]);
    $('map-picked').innerHTML = `${label}: ${vmin != null ? vmin.toFixed(2) : '-'} ~ ${vmax != null ? vmax.toFixed(2) : '-'}（共 ${drawn} 个水格）`;
}

async function loadMapFieldVars() {
    const sel = $('map-field-var');
    if (!sel) return;
    const vs = await api('/api/results/variables');
    // 端点返回 {"2d":[{name,...}],"3d":[...]} —— 不是 {variables:[...]}，
    // 旧代码对字典直接 .slice 会 TypeError 并中断整个地图加载
    let names = [];
    if (Array.isArray(vs)) {
        names = vs.map(v => (v && v.name) || v);
    } else if (vs && !vs.error) {
        names = ([]).concat(vs['3d'] || [], vs['2d'] || []).map(v => (v && v.name) || v);
    }
    names = [...new Set(names.filter(Boolean))].slice(0, 400);
    sel.innerHTML = names.map(n => `<option value="${n}">${n}</option>`).join('');
}

async function updateMapLayer() {
    const mode = $('map-layer').value;
    const sel = $('map-field-var');
    sel.style.display = (mode === 'result') ? '' : 'none';
    if (mode === 'result') {
        const v = sel.value;
        if (!v) return;
        mapState.field = await api(`/api/geo/field?var=${encodeURIComponent(v)}&time=0&level=-1`);
        if (mapState.field && mapState.field.error) { toast(mapState.field.error, 'error'); mapState.field = null; }
    }
    drawMapLayer();
}

async function onMapClick(e) {
    const g = mapState.grid;
    if (!g || !mapState.map) return;
    const { lat, lng } = e.latlng;
    let best = null, bestD = Infinity;
    if (mapState.xyMode) {
        // CRS.Simple：lat=y(米), lng=x(米)
        const x = g.x || [], y = g.y || [];
        for (let j = 0; j < g.ny && j < y.length; j++) {
            for (let i = 0; i < g.nx && i < x.length; i++) {
                const d = (y[j] - lat) ** 2 + (x[i] - lng) ** 2;
                if (d < bestD) { bestD = d; best = { i, j, la: y[j], lo: x[i] }; }
            }
        }
    } else {
        for (let j = 0; j < g.ny; j++) {
            for (let i = 0; i < g.nx; i++) {
                const la = g.lat[j][i], lo = g.lon[j][i];
                if (la == null || lo == null) continue;
                const d = (la - lat) ** 2 + (lo - lng) ** 2;
                if (d < bestD) { bestD = d; best = { i, j, la, lo }; }
            }
        }
    }
    if (!best) return;
    if (mapState.marker) mapState.map.removeLayer(mapState.marker);
    mapState.marker = L.marker([best.la, best.lo]).addTo(mapState.map);
    const depth = (g.depth[best.j] || [])[best.i];
    const coordTxt = mapState.xyMode
        ? `x=${best.lo.toFixed(0)} m, y=${best.la.toFixed(0)} m`
        : `${best.la.toFixed(4)}°N ${best.lo.toFixed(4)}°E`;
    $('map-picked').innerHTML = `已选网格 <strong>i=${best.i}, j=${best.j}</strong>
        （${coordTxt}，水深 ${depth != null ? depth.toFixed(2) + ' m' : '陆地'}）
        <button class="btn btn-sm" style="margin-left:8px;" onclick="mapPickTimeseries(${best.i},${best.j})">📈 提取该点时间序列</button>`;
}

async function mapPickTimeseries(i, j) {
    const tsVar = $('ts-var');
    const varName = (tsVar && tsVar.value) || 'temp';
    navigate('timeseries');
    $('ts-mode').value = 'point';
    toggleTsMode();
    $('ts-i').value = i;
    $('ts-j').value = j;
    if (tsVar && !tsVar.value) {
        const vs = await api('/api/results/variables');
        const list = Array.isArray(vs) ? vs
            : (vs && !vs.error ? ([]).concat(vs['3d'] || [], vs['2d'] || []) : []);
        if (list.length) { tsVar.value = (list.find(v => v.name === varName) ? varName : list[0].name); }
    }
    extractTimeseries();
}

// ── Init ──────────────────────────────────────────────────────────────
window.addEventListener('load', () => {
    loadCases();
    // Auto-load first case if exists
    setTimeout(async () => {
        const cases = await api('/api/cases');
        if (cases.length) {
            // Don't auto-load, just show on dashboard
            $('stat-water').textContent = '-';
        }
    }, 500);
});
