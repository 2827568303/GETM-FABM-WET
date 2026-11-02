// 3DWET Web App - Main JavaScript
let state = {
    activeCase: null,
    activeCasePath: null,
    caseType: null,
    storageReadOnly: false,
    mpiSelectionByCase: new Map(),
    mpiProcessCountByCase: new Map(),
    mpiCapabilitiesRequest: 0,
    serverCaseGeneration: null,
    outputRevision: 0,
    cases: [],
    fabmModules: [],
    fabmCategories: {},
    variables2d: [],
    variables3d: [],
    charts: {},
    runPollTimer: null,
    runPhysicsDiagnosticState: null,
    calibPollTimer: null,
    calibJobId: null,
    calibPointsLoaded: false,
    calLastData: null,
    currentParams: [],
    proxyCase: null,
};

function localizedResult(item, name) {
    const key=name || item?.name || item?.var_name;
    const source=[...state.variables3d,...state.variables2d].find(v=>v.name===key) || item || {name:key};
    return window.StudioI18n?.variable(source) || {...source,display_name:source.zh_name || source.long_name || key};
}
function resultLabel(item,name) { const v=localizedResult(item,name); return v.comparison_name || v.display_name || name; }
const chartLanguageSources = new WeakMap();
function translateChartLabels(config) {
    if (!config || typeof config !== 'object') return;
    for (const [key,value] of Object.entries(config)) {
        if (['label','text'].includes(key) && typeof value === 'string') {
            let sources=chartLanguageSources.get(config);
            if (!sources) {sources=new Map();chartLanguageSources.set(config,sources);}
            const previous=sources.get(key);
            const source=previous && value===previous.output ? previous.source : value;
            let localized=source;
            const replacements = [];
            const scientificLabels = {};
            const knownTerms = [...(state.scientificTerms || new Map()).entries()].sort((a,b) => b[0].length-a[0].length);
            knownTerms.forEach(([term,original]) => {
                if (!localized.includes(term)) return;
                const token = `@@SCIENTIFIC_${replacements.length}@@`;
                localized = localized.replace(term,token);
                replacements.push([token,window.StudioI18n?.scientificText(original.zh,original.en) || term]);
            });
            for(const variable of [...state.variables3d,...state.variables2d]) {
                const label = resultLabel(variable,variable.name);
                const pairs = variable.zh_name && variable.en_name ? [
                    `${variable.zh_name} / ${variable.en_name}`, `${variable.en_name} / ${variable.zh_name}`
                ] : [];
                const names=[previous?.scientificLabels?.[variable.name],label,...pairs,variable.zh_name,variable.en_name,variable.long_name_en]
                    .filter(name=>name && (name.length>2 || /[\u3400-\u9fff]/.test(name)))
                    .sort((a,b)=>b.length-a.length);
                const match=names.find(name=>localized.includes(name));
                if (match) {
                    scientificLabels[variable.name] = match;
                    const token = `@@SCIENTIFIC_${replacements.length}@@`;
                    localized=localized.replace(match,token);
                    replacements.push([token,label]);
                }
            }
            let output=window.StudioI18n?.t(localized) || localized;
            replacements.forEach(([token,label]) => {output=output.replace(token,label);});
            sources.set(key,{source,output,scientificLabels});config[key]=output;
        } else if (value && typeof value==='object' && key!=='labels' && !(key==='data' && Array.isArray(value))) {
            translateChartLabels(value);
        }
    }
}
function localizedChart(context,config) {
    translateChartLabels(config);
    return new Chart(context,config);
}
function localizedVariableLabel(v) {
    const hasLev=hasVerticalResultDimension(v);
    return `${resultLabel(v,v.name)} · ${v.name} [${v.units||''}]${hasLev?'':' ('+(window.StudioI18n?.t('无垂向层') || '无垂向层')+')'}`;
}
const verticalResultSelectIds = new Set(['viz3d-var','viz3d-avg-var']);
function resultVariablePriority(variable) {
    const name=String(variable?.name||'').toLowerCase();
    const label=[variable?.zh_name,variable?.en_name,variable?.long_name,variable?.long_name_en,variable?.meaning,variable?.meaning_en]
        .filter(Boolean).join(' ').toLowerCase();
    const units=String(variable?.units||'').toLowerCase().replace(/\s+/g,'');
    // Saturation and methodological diagnostics remain on-demand even when
    // their names contain oxygen, PAR, or transparency terminology.
    if (/(saturation|饱和)/.test(`${name} ${label}`)) return 2;
    if (name==='ho2bod' || name.startsWith('ho2bod_')) return 2;
    // Rank only variables present in the actual results inventory. Names below
    // are output fields; model parameters and derived quantities are not added.
    if (/^(elev|z|depth|water_depth|d|temp|temperature|salt|salinity|u|v|w|uu|vv|ww)$/.test(name)) return 0;
    if (/(^|[_-])s?o2w$/.test(name) || /abiotic_water_so2w$/.test(name)
        || /(dissolved oxygen|溶解氧)/.test(`${name} ${label}`)) return 0;
    // Chlorophyll, nutrients, organic matter and COD are loaded when chosen.
    if (/^(wet_)?(totn|totp|totnwater|totpwater|chla|total_chla|tot_chla|totsuspar)$/.test(name)
        || /^wet_(totn|totp|chla)_calculator_result$/.test(name)) return 2;
    if (/(^|[_-])s?(nh4|no3|po4|tn|tp)w$/.test(name) || /abiotic_water_s(nh4|no3|po4)w$/.test(name)) return 2;
    if (/(^|[_-])cod($|[_-])|化学需氧量/.test(`${name} ${label}`)) return 2;
    if ((/(^|[_-])bod($|[_-])|biochemical oxygen demand|生化需氧量/.test(`${name} ${label}`)) && !name.startsWith('ho2bod')) return 1;
    if (/(^|[_-])ph($|[_-])|酸碱度/.test(`${name} ${label}`)) return 1;
    if (/(^|[_-])(nh4|no3|po4|tn|tp)([_-]|$)|氨氮|硝酸盐|磷酸盐|总氮|总磷/.test(`${name} ${label}`)) return 2;
    if (/total suspended|总悬浮|totsuspar/.test(`${name} ${label}`)) return 1;
    const biomass=/_sd(?:_pv)?$/.test(name) || /biomass|生物量|干重/.test(label);
    if (/(fish|jufish|adfish|piscfish|鱼类)/.test(`${name} ${label}`) && biomass) return 1;
    if (/(zoobenthos|bivalve|底栖动物)/.test(`${name} ${label}`) && biomass) return 1;
    if (/(zooplankton|cladoceran|copepod|浮游动物)/.test(`${name} ${label}`) && biomass) return 1;
    if (/(waterplant|macrophyte|水生植物)/.test(`${name} ${label}`) && biomass) return 1;
    // Transparency is a direct result only when its metadata identifies the
    // quantity and its published unit is metres; never infer it from turbidity.
    if (/(transparen|secchi|透明度)/.test(`${name} ${label}`) && units==='m') return 1;
    return 2;
}
function prioritizeResultVariables(variables) {
    return variables.map((variable,index)=>({variable,index,priority:resultVariablePriority(variable)}))
        .sort((a,b)=>a.priority-b.priority||a.index-b.index).map(item=>item.variable);
}
function hasVerticalResultDimension(variable) {
    return variable?.ndim===4 || (Array.isArray(variable?.dims) && variable.dims.includes('sigma'));
}
function resultVariableOptionLabel(variable, requiresVertical=false) {
    const label=localizedVariableLabel(variable);
    if(!requiresVertical || hasVerticalResultDimension(variable))return label;
    const reason=window.StudioI18n?.scientificText?.(
        '3D 垂向查看需要真实垂向层；请切换到 2D。',
        '3D vertical views require real vertical layers; switch to 2D.'
    ) || '3D 垂向查看需要真实垂向层；请切换到 2D。';
    return `${label} · ${reason}`;
}
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
function syncQgisStatusBar(runLabel) {
    const project = $('qgis-status-case');
    const run = $('qgis-status-run');
    if (project) project.textContent = state.activeCase || '未加载案例';
    if (run && runLabel) run.textContent = runLabel;
}
function toast(msg, type='info') {
    const t = document.createElement('div');
    t.className = `toast ${type}`;
    t.textContent = ModelDates.formatText(msg);
    $('toast-container').appendChild(t);
    setTimeout(() => t.remove(), 3000);
}
function closeModal(id) { $(id).classList.remove('active'); }
function showModal(id) { $(id).classList.add('active'); }

async function api(url, opts={}) {
    return new Promise((resolve) => {
        if (opts.signal?.aborted) { resolve({aborted:true}); return; }
        const timedResult = /\/api\/results\/2d(?:\?|$)|\/api\/results\/2d_batch(?:\?|$)|\/api\/geo\/grid(?:\?|$)/.test(url);
        const perfNow=()=>window.performance?.now?.() ?? Date.now();
        const startedAt = timedResult ? perfNow() : 0;
        const xhr = new XMLHttpRequest();
        const cancel = () => xhr.abort();
        const finish = value => {
            opts.signal?.removeEventListener('abort', cancel);
            resolve(value);
        };
        xhr.onabort = () => finish({aborted:true});
        opts.signal?.addEventListener('abort', cancel, {once:true});
        const method = opts.method || 'GET';
        xhr.open(method, url, true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.onload = function() {
            try {
                const receivedAt = timedResult ? perfNow() : 0;
                const decodeStartedAt = timedResult ? perfNow() : 0;
                const data = JSON.parse(xhr.responseText);
                if (timedResult && data && typeof data === 'object' && !Array.isArray(data)) {
                    data._clientTiming = { requestMs: receivedAt - startedAt,
                        decodeMs: perfNow() - decodeStartedAt };
                }
                finish(data);
            } catch(e) {
                finish({error: 'Invalid JSON response: ' + xhr.responseText.substring(0, 200)});
            }
        };
        xhr.onerror = function() {
            finish({error: 'Network error (XHR) - cannot connect to server'});
        };
        xhr.ontimeout = function() {
            finish({error: 'Request timeout'});
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
    window.StudioNavigation?.activate(page);
    window.ScientificWorkspace?.onNavigate(page);
    const contentPage = page === 'ecology' ? 'gridstudio' : page;
    document.querySelectorAll('.nav-item').forEach(n => n.classList.toggle('active', n.dataset.page === page));
    document.querySelectorAll('.page').forEach(p => p.classList.toggle('active', p.id === `page-${contentPage}`));
    const content=document.querySelector?.('.content-area');
    if(content)content.scrollTop=0;
    const titles = {dashboard:'仪表盘',cases:'案例管理',preprocess:'前处理',input:'输入数据',modules:'模块配置',ecology:'生态网络与食物网',parameters:'参数编辑',initial:'初始条件',time:'时间设置',run:'运行控制',map:'地图视图',viz2d:'2D可视化',viz3d:'3D可视化',vheat:'垂向热图',timeseries:'时间序列',calibrate:'率定分析',autocal:'自动率定'};
    $('page-title').textContent = titles[page] || page;
    if (contentPage === 'gridstudio') {
        if (page === 'gridstudio') $('page-title').textContent = '交互网格编辑';
        window.initGridStudio();
    }
    if (page === 'system') { $('page-title').textContent = '环境与启动诊断'; window.loadStudioDiagnostics(); }
    // Page-specific init
    if (page === 'cases') loadCases();
    if (page === 'preprocess') { initPreprocess(); renderEngines(); }
    if (page === 'input') loadInputData();
    if (page === 'modules') { loadEngines(); renderModuleCards(); }
    if (page === 'parameters') loadParamModules();
    if (page === 'initial') loadInitConditions();
    if (page === 'run') window.loadResultFiles?.();
    if (page === 'time') { loadTimeSettings(); loadOutputConfig(); }
    if (page === 'map') loadMapGrid();
    if (page === 'viz2d') initViz2d();
    if (page === 'viz3d') initViz3d();
    if (page === 'vheat') initVHeat();
    if (page === 'timeseries') initTimeseries();
    if (page === 'calibrate') initCalibrate();
    if (page === 'autocal') initAutoCal();
    if (page === 'ecology') requestAnimationFrame(() => {
        const heading = document.getElementById('ecology-network-heading');
        if (!heading) return;
        heading.scrollIntoView({block: 'start'});
        heading.focus({preventScroll: true});
    });
}

// Keep the ecology editor reachable when a desktop/web server is serving an
// older cached template that predates its model-configuration navigation item.
function ensureEcologyNavigationItem() {
    if (document.querySelector('.nav-item[data-page="ecology"]')) return;
    const modelNav = document.querySelector('[data-group-items="model"]');
    if (!modelNav) return;

    const item = document.createElement('button');
    item.type = 'button';
    item.className = 'nav-item getm-case-only';
    item.dataset.page = 'ecology';

    const icon = document.createElement('span');
    icon.className = 'nav-icon';
    icon.setAttribute('aria-hidden', 'true');
    icon.replaceChildren(StudioIcons.node('foodweb'));
    item.appendChild(icon);
    item.appendChild(document.createTextNode('生态网络与食物网'));

    const parameters = modelNav.querySelector('[data-page="parameters"]');
    if (parameters) modelNav.insertBefore(item, parameters);
    else modelNav.appendChild(item);
}

ensureEcologyNavigationItem();
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
        let nameCell = `<strong>${escapeHtml(c.name)}</strong>`;
        if (c.engineering_proxy) {
            nameCell += proxyCaseBadgeMarkup(c, true);
            if (!c.prepared) {
                nameCell += `<div class="proxy-case-blockers">${(c.proxy_blockers || []).map(escapeHtml).join('<br>')}</div>`;
            }
        }
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
            <td>${c.has_bathymetry ? '<svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-check"></use></svg>' : '<svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-error"></use></svg>'}</td>
            <td>${c.has_fabm ? '<svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-check"></use></svg>' : '<svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-error"></use></svg>'}</td>
            <td>${c.has_meteo ? '<svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-check"></use></svg>' : '<svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-error"></use></svg>'}</td>
            <td>${c.has_rivers ? '<svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-check"></use></svg>' : '<svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-error"></use></svg>'}</td>
            <td>${c.has_2d_output ? '<svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-check"></use></svg>' : '<svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-error"></use></svg>'}</td>
            <td>${c.has_3d_output ? '<svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-check"></use></svg>' : '<svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-error"></use></svg>'}</td>
            <td style="white-space:nowrap;">
                <button class="btn btn-primary btn-sm" onclick="caseAction('load', ${idx})" ${c.engineering_proxy && !c.prepared ? 'disabled title="输入未齐，不可加载运行"' : ''}>加载</button>
                <button class="btn btn-sm" onclick="caseAction('saveas', ${idx})" ${c.engineering_proxy && !c.prepared ? 'disabled title="准备记录只读"' : ''}>另存为</button>
                <button class="btn btn-danger btn-sm" onclick="caseAction('delete', ${idx})" ${c.engineering_proxy ? 'disabled title="代理工程审计记录保留"' : ''}>删除</button>
            </td>`;
        tbody.appendChild(tr);
    });
}

function caseAction(action, idx) {
    const c = (state.cases || [])[idx];
    if (!c) return;
    if (c.engineering_proxy && !c.prepared) {
        toast((c.proxy_blockers || ['代理工程输入尚未准备完成']).join('；'), 'warning');
        return;
    }
    if (action === 'load') {
        if (c.external) loadExternalCase(c.path);
        else loadCase(c.name, c.path);
    } else if (action === 'saveas') {
        showSaveAsModal(c);
    } else if (action === 'delete') {
        deleteCase(c);
    }
}

function proxyCaseBadgeMarkup(caseData, compact=false) {
    if (!caseData || caseData.engineering_proxy !== true) return '';
    const lake = escapeHtml(caseData.target_lake || '目标湖泊');
    const status = caseData.partial_engineering_proxy ? '部分代理工程运行' : (caseData.prepared ? '代理工程运行' : '代理工程准备未完成');
    return `<span class="proxy-case-badge${compact ? ' compact' : ''}" role="status">${status} · ${lake} · 非科学验证</span>`;
}

function proxyCaseDetailsMarkup(caseData) {
    if (!caseData || caseData.engineering_proxy !== true) return '';
    const manifest = caseData.proxy_manifest || caseData;
    const sources = Array.isArray(manifest.sources) ? manifest.sources : [];
    const roles = {measured:'实测来源',derived:'代理/派生',synthetic_proxy:'合成代理',upstream_reference:'上游参考',missing:'缺失/未完成'};
    const sourceRows = sources.map(source => {
        const path = escapeHtml(source.path || '（路径缺失）');
        const purpose = escapeHtml(source.purpose || '用途未说明');
        const role = escapeHtml(roles[source.role] || '来源未知');
        const description = source.source_description ? ` · ${escapeHtml(source.source_description)}` : '';
        const origin = source.origin_path ? ` · 原始路径：${escapeHtml(source.origin_path)}` : '';
        const license = source.license_path ? ` · 许可记录：${escapeHtml(source.license_path)}` : '';
        return `<li><b>${role}</b> · ${path} — ${purpose}${description}${origin}${license}</li>`;
    }).join('');
    const blockers = (caseData.proxy_blockers || manifest.blockers || []).map(escapeHtml).map(x=>`<li>${x}</li>`).join('');
    const geometry = manifest.geometry || {};
    const forcing = manifest.forcing || {};
    const partial = manifest.partial_engineering_proxy === true
        ? `<div>部分工程运行：关闭模块 ${escapeHtml((manifest.disabled_modules || []).join('、') || '未列明')}</div>` : '';
    return `<div class="proxy-case-details"><strong>${manifest.partial_engineering_proxy === true ? '部分代理工程运行' : '代理工程运行'} / 非科学验证</strong>`+
        `<div>科学验证状态：未完成</div>`+
        `${partial}`+
        `<div>空间几何：${escapeHtml(geometry.description || geometry.status || '缺少来源信息')}</div>`+
        `<div>强迫来源：${escapeHtml(forcing.description || forcing.status || '缺少来源信息')}</div>`+
        `${blockers ? `<details open><summary>未完成输入与阻塞项</summary><ul>${blockers}</ul></details>` : ''}`+
        `${sourceRows ? `<details><summary>来源清单（${sources.length} 项）</summary><ul>${sourceRows}</ul></details>` : ''}</div>`;
}

function renderProxyCaseStatus(caseData) {
    state.proxyCase = caseData?.engineering_proxy === true ? caseData : null;
    const badge = $('case-badge');
    if (badge) {
        const base = caseData?.case_type === 'gotm_working_copy'
            ? `${caseData.case_name} · GOTM 单水柱工作副本`
            : caseData?.read_only ? `${caseData.case_name} · 只读 GOTM 单水柱` : (caseData?.case_name || '未加载案例');
        const nativePeriod = Array.isArray(caseData?.native_time_range) && caseData.native_time_range.length === 2
            ? ` · ${caseData.native_time_range[0]} — ${caseData.native_time_range[1]}` : '';
        const label = escapeHtml(base + nativePeriod);
        const proxyMarkup = proxyCaseBadgeMarkup(caseData);
        badge.innerHTML = proxyMarkup ? `<span class="case-name">${label}</span>${proxyMarkup}` : label;
        badge.style.display = caseData?.case_name ? 'inline-flex' : 'none';
    }
    const details = proxyCaseDetailsMarkup(caseData);
    ['proxy-dashboard-notice','proxy-run-notice','proxy-viz2d-notice','proxy-viz3d-notice']
        .forEach(id => {
            const element = $(id);
            if (!element) return;
            element.innerHTML = details;
            element.hidden = !details;
        });
}

function refreshCaseStatistics(data) {
    const request = state.caseStatisticsRequest = (state.caseStatisticsRequest || 0) + 1;
    const revision = state.caseRevision;
    const casePath = state.activeCasePath;
    const current = () => request === state.caseStatisticsRequest
        && revision === state.caseRevision && casePath === state.activeCasePath;
    const nlev = data.run_info?.nlev;
    if (nlev) setNlev(nlev);
    $('stat-nlev').textContent = nlev || '-';
    $('stat-modules').textContent = data.fabm?.total_modules ?? '-';
    $('stat-water').textContent = '...';
    api('/api/run/estimate').then(est => {
        if (!current()) return;
        $('stat-water').textContent = !est.error && typeof est.nwater === 'number'
            ? est.nwater.toLocaleString() : '-';
    }).catch(() => {
        if (current()) $('stat-water').textContent = '-';
    });
}

function applyLoadedCase(data) {
    state.caseRevision = (state.caseRevision || 0) + 1;
    document.body.classList.toggle('readonly-gotm', !!data.read_only);
    document.body.classList.toggle('gotm-single-column', String(data.case_type || '').startsWith('gotm_'));
    window.ObservationManager?.setColumnVariableInventory(data.native_column_variables || null);
    window.set3DSectionIndicator?.(null)?.catch(()=>{});
    state.variables2d = [];
    state.variables3d = [];
    state.activeCase = data.case_name;
    state.activeCasePath = data.case_path;
    state.caseType = data.case_type || null;
    state.storageReadOnly = !!data.storage_read_only;
    document.body.classList.toggle('storage-read-only', !!data.storage_read_only);
    state.serverCaseGeneration = Number.isInteger(data.case_generation) ? data.case_generation : null;
    state.fabmModules = data.fabm.modules || [];
    state.fabmCategories = data.fabm.categories || {};
    renderProxyCaseStatus(data);
    const calibrationDesc = $('calibration-page-desc');
    if (calibrationDesc) calibrationDesc.textContent = data.read_only
        ? '当前打开的是只读 GOTM 原生输出。请使用下方官方观测文件入口进行代表水柱比较；GETM 点位、运行和观测写入功能已停用。'
        : '设置率定点位，输入实测数据，对比模拟-实测结果';
    $('footer-status').textContent = `案例: ${data.case_name}`;
    syncQgisStatusBar();
    // Update dashboard
    refreshCaseStatistics(data);
    // Output.yaml sync_interval=0 sanity check banner
    const banner = $('output-warning-banner');
    if (banner) {
        if (data.output_warning) {
            banner.style.display = 'block';
            banner.innerHTML = `<strong><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-warning"></use></svg> 输出配置警告：</strong> ${data.output_warning} <button class="btn btn-primary btn-sm" style="margin-left:8px;" onclick="fixSyncInterval()">一键修复 (设为 1)</button>`;
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
            nb.innerHTML = `<strong><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-warning"></use></svg> 无结果数据：</strong> ${msg}`;
        }
    }
    // Load variables if results exist（无结果时也会注入“水深(地形)”占位变量，
    // 保证 2D/3D/地图视图至少能看到湖泊网格与湖盆）
    loadVariables();
    window.loadResultFiles?.();
    if (data.has_results) {
        loadDashboardSummary();
    } else {
        const dashboardVars=$('dashboard-vars');
        const dashboardCanvas=$('dashboard-mini-heatmaps');
        if(dashboardVars)dashboardVars.innerHTML='<div class="empty-state">'+(window.StudioI18n?.scientificText('当前案例尚无输出结果。运行模型后显示','No model output is available for this case. Run the model to populate results.')||'当前案例尚无输出结果。运行模型后显示')+'</div>';
        if(dashboardCanvas)loadDashboardStaticPreview();
    }
    // 案例切换后地图数据属于旧案例，必须重置；若用户正停在地图页则立即重载
    resetMapView();
    const nativePeriod = Array.isArray(data.native_time_range) && data.native_time_range.length === 2
        ? `原生输出时间 ${data.native_time_range[0]} — ${data.native_time_range[1]}。` : '';
    toast(data.case_type === 'gotm_working_copy'
        ? `已加载 GOTM 单水柱工作副本: ${data.case_name}。仅表示一维代表水柱结果，不是 GETM 空间网格。${nativePeriod}`
        : data.read_only
        ? `已打开只读 GOTM 原生结果: ${data.case_name}。${nativePeriod}可进行代表水柱观测比较；不能在此目录运行或修改配置。`
        : `已加载案例: ${data.case_name}`, 'success');
    if (data.storage_read_only) {
        toast('该案例位于 C:，当前可浏览但不能修改或运行；请先另存到非 C: 磁盘。', 'warning');
    }
    navigate('dashboard');
    // 刷新一次运行状态面板（服务重启后 run_status 回到 idle，页面应如实显示）
    pollRunStatus();
    // 刷新案例管理表（高亮当前案例）
    loadCases();
    loadCorePlan();
    loadMpiRunCapabilities();
}

async function loadCase(name, path) {
    const data = await api('/api/case/load', {method:'POST', body:{case_name:name, case_path:path}});
    if (data.error) { toast(data.error, 'error'); return false; }
    applyLoadedCase(data);
    return true;
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
        `<div class="db-item db-dir" onclick="loadDirBrowser('${escapeAttr(r.parent || '')}')"><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-up"></use></svg> 上一级${r.parent ? '（' + escapeHtml(r.parent) + '）' : ''}</div>` +
        dirs.map(e => `<div class="db-item db-dir" title="${escapeAttr(e.path)}" onclick="loadDirBrowser('${escapeAttr(e.path)}')"><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-folder"></use></svg> ${escapeHtml(e.name)}</div>`).join('') +
        (files.length ? `<div class="db-sep"><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-file"></use></svg> 文件（${files.length}）</div>` : '') +
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
                    '请改用右侧「<svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-folder"></use></svg> 浏览目录」，在页面内逐级选择案例目录，功能完全一致。</span>';
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
    if (action === 'load') { if (c.external) loadExternalCase(c.path); else loadCase(c.name, c.path); return; }
    if (action === 'saveas') { showSaveAsModal(c); return; }
}

let saveAsCase = null;
function showSaveAsModal(c) {
    saveAsCase = c;
    $('save-as-source').textContent = `源案例: ${c.path}`;
    $('save-as-dest').value = '';
    const gotmReference = c.case_type === 'gotm_read_only';
    $('save-as-include-results').checked = gotmReference;
    $('save-as-include-results').disabled = false;
    $('save-as-include-label').textContent = gotmReference
        ? 'GOTM 单水柱：包含原始 output.nc、gotm_release.exe 与配置/输入，创建可运行的独立副本（必需）'
        : '包含模拟结果文件（*.3d.nc / output.nc 等，可能达数 GB、耗时数分钟）';
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
    const input = await promptStudio(`确定要删除案例吗？此操作不可恢复！\n\n${c.path}\n\n如确认，请输入案例名称 "${c.name}"：`);
    if (input === null) return;
    if (input.trim() !== c.name) { toast('案例名称不匹配，已取消删除', 'error'); return; }
    const res = await api('/api/case/delete', {method:'POST', body:{path: c.path}});
    if (res.error) { toast(res.error, 'error'); return; }
    toast(`案例已删除（清理 ${res.n_files} 个文件，释放 ${fmtSize(res.size_bytes)}）`, 'success');
    if (state.activeCasePath && _samePath(state.activeCasePath, c.path)) {
        state.caseRevision=(state.caseRevision||0)+1;
        state.activeCase = null;
        state.activeCasePath = null;
        state.caseType = null;
        state.storageReadOnly = false;
        state.serverCaseGeneration = null;
        $('case-badge').style.display = 'none';
        $('footer-status').textContent = '未加载案例';
        syncQgisStatusBar();
        clearResultInventory();
        loadCorePlan();
        loadMpiRunCapabilities();
    }
    loadCases();
}

async function fixSyncInterval() {
    if (!state.activeCase) { toast('请先加载案例', 'error'); return; }
    if (!await confirmStudio('将 output.yaml 的 sync_interval 从 0 改为 1（每个时间步同步输出）？')) return;
    const res = await api('/api/config/output', {
        method: 'POST',
        body: { sync_interval: 1 }
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
        html += `<div style="width:100%;font-size:11px;color:var(--text-muted);margin-top:4px;">生态模块（自动转换为模型支持的变量）:</div>`;
        html += mods.map(m => `
            <label style="font-size:12px;white-space:nowrap;" title="${m.model || ''}">
                <input type="checkbox" class="out-src" value="${m.name}/*" ${m.selected || m.partially_selected || checked(m.name) ? 'checked' : ''}> ${m.name}${m.partially_selected ? '（部分）' : ''}
            </label>`).join('');
    } else {
        html += `<div style="font-size:11px;color:var(--text-muted);">（fabm.yaml 中未解析到 instances）</div>`;
    }
    box.innerHTML = html;
    box.querySelectorAll('.out-src').forEach(el => {
        const module = mods.find(m => el.value === m.name + '/*');
        if (module?.partially_selected) { el.indeterminate = true; el.dataset.partial = 'true'; }
        el.addEventListener('change', () => { el.dataset.partial = 'false'; _outputCfg.selectionChanged = true; });
    });

    const e = cfg.estimate || {};
    if (est) {
        if (!e.available) {
            est.innerHTML = `<span style="font-size:12px;color:var(--text-muted);">字段负载估算不可用；完整磁盘需求未知，且未计 GETM 独立 2D/3D 输出流。</span>`;
        } else {
            const gb = e.gb;
            const color = gb >= 2 ? 'var(--danger)' : 'var(--warning)';
            const streams = e.getm_streams || {};
            const streamLabel = (dimension, filename) => {
                const stream = streams[dimension];
                if (!stream) return `${filename} 状态未知`;
                return stream.enabled
                    ? `${filename} 已启用（每 ${stream.step} 个模型步写出）`
                    : `${filename} 已关闭`;
            };
            est.innerHTML = `<div style="font-size:12px;">
                <strong style="color:${color};">output.yaml 字段负载估算 ≈ ${gb >= 1 ? gb.toFixed(2) + ' GB' : e.mb.toFixed(0) + ' MB'}；完整磁盘需求未知</strong>
                <span style="color:var(--text-muted);"> — ${e.ntime} 时步 × ${e.ncells} 水格 × ${e.n_vars} 变量
                ${e.measured_counts ? '（变量数按上次输出实测）' : '（变量数为估算）'}</span>
                <div style="color:var(--text-muted);margin-top:3px;">未计入 ${streamLabel('2d', '2d.nc')}；${streamLabel('3d', '3d.nc')}；也未计网格与文件格式开销。</div></div>`;
        }
    }
}

function _selectedOutputSources() {
    if (!_outputCfg?.selectionChanged) return _outputCfg?.sources || [];
    return Array.from(document.querySelectorAll('.out-src'))
        .filter(el => el.checked || el.dataset.partial === 'true')
        .flatMap(el => {
            if (el.dataset.partial !== 'true') return [el.value];
            const module = _outputCfg.modules.find(m => el.value === m.name + '/*');
            return _outputCfg.sources.filter(s => module?.sources.includes(s));
        });
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
    const caseAtRequest = state.activeCasePath;
    const generation = (panel._diagnosticGeneration || 0) + 1;
    panel._diagnosticGeneration = generation;
    panel.style.display = 'block';
    StudioIcons.setStatus(panel, 'health', '体检中...');
    const res = await api('/api/run/check');
    if (generation !== panel._diagnosticGeneration || state.activeCasePath !== caseAtRequest) return;
    if (res.error) {
        panel.textContent = `体检失败: ${res.error}`;
        return;
    }
    const color = { error: 'var(--danger)', warn: 'var(--warning)', ok: 'var(--success)' };
    // Use text nodes for every server-supplied value, including filenames.
    const box = document.createElement('div');
    box.style.cssText = 'border:1px solid var(--border);border-radius:6px;padding:10px;background:var(--bg-tertiary);';
    const text = (parent, value, style) => {
        const element = document.createElement('div');
        element.textContent = ModelDates.formatText(value);
        if (style) element.style.cssText = style;
        parent.appendChild(element);
        return element;
    };
    const statusLine = (parent, name, label, className, style) => {
        const element = document.createElement('div');
        StudioIcons.setStatus(element, name, label, className);
        if (style) element.style.cssText = style;
        parent.appendChild(element);
        return element;
    };
    statusLine(box, res.ok ? 'check' : 'error',
        res.ok ? `可以运行（${res.n_warn || 0} 条提醒）` : `${res.blocking} 项必须先修复`,
        `icon-status-${res.ok ? 'ok' : 'error'}`,
        `font-size:13px;font-weight:600;margin-bottom:6px;color:${res.ok ? color.ok : color.error};`);
    text(box, '体检只读取输入。修复仅执行按钮描述的修改，保存原文件备份后重新检查。CFL 通过后仍需短时试运行检查输出。',
        'font-size:11px;color:var(--text-muted);margin-bottom:8px;');
    const jump = async target => {
        if (state.activeCasePath !== caseAtRequest) { toast('当前案例已变化，请重新体检', 'error'); return; }
        if (target.page === 'projecttools') {
            const nav = document.querySelector('.nav-item[data-page="projecttools"]');
            if (!nav) { toast(`请打开物理设置并编辑 ${target.file}`, 'error'); return; }
            if ($('physics-file')) $('physics-file').value = target.file;
            nav.click(); // Also invokes the physics editor's asynchronous loader.
        } else {
            navigate(target.page);
            // navigate() starts loading; await fresh controls before highlighting.
            if (target.page === 'time') await Promise.all([loadTimeSettings(), loadOutputConfig()]);
            if (target.page === 'input') await loadInputData();
        }
        const deadline = Date.now() + 31000;
        let control;
        while (Date.now() < deadline && state.activeCasePath === caseAtRequest) {
            control = target.selector ? document.querySelector(target.selector) : $(target.control);
            if (control && control.getClientRects().length) break;
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        if (state.activeCasePath !== caseAtRequest) return;
        if (!control || !control.getClientRects().length) {
            toast(`未找到对应控件，请检查 ${target.file}`, 'error');
            return;
        }
        control.scrollIntoView({behavior: 'smooth', block: 'center'});
        const previous = control.style.outline;
        control.style.outline = '3px solid var(--warning)';
        if (typeof control.focus === 'function') control.focus({preventScroll: true});
        setTimeout(() => { control.style.outline = previous; }, 4000);
    };
    for (const c of res.checks || []) {
        const row = document.createElement('div');
        row.style.cssText = 'padding:8px 0;border-bottom:1px solid var(--border);font-size:12px;';
        statusLine(row, c.level === 'error' ? 'error' : c.level === 'ok' ? 'check' : 'warning', c.title || '',
            c.level === 'error' ? 'icon-status-error' : c.level === 'ok' ? 'icon-status-ok' : 'icon-status-warning',
            `font-weight:600;color:${color[c.level] || color.warn};`);
        text(row, c.detail || '', 'color:var(--text-secondary);white-space:pre-wrap;overflow-wrap:anywhere;');
        if (c.fix) text(row, `建议：${c.fix}`, 'color:var(--info);margin-top:2px;');
        if (c.source_file) text(row, `${c.id} · ${c.source_file}`, 'color:var(--text-muted);margin-top:3px;');
        if (c.level !== 'ok' && c.target) {
            const locate = document.createElement('button');
            locate.className = 'btn btn-sm';
            locate.textContent = '定位设置';
            locate.style.marginTop = '6px';
            locate.addEventListener('click', () => jump(c.target).catch(error => toast(String(error), 'error')));
            row.appendChild(locate);
        }
        if (c.repair && res.case_path && res.revision) {
            const repair = document.createElement('button');
            repair.className = 'btn btn-primary btn-sm';
            repair.style.cssText = 'margin-left:8px;margin-top:6px;';
            repair.textContent = c.repair.label;
            repair.addEventListener('click', async () => {
                if (state.activeCasePath !== caseAtRequest) { toast('当前案例已变化，请重新体检', 'error'); return; }
                box.querySelectorAll('button').forEach(button => { button.disabled = true; });
                const result = await api('/api/run/repair', {method: 'POST', body: {
                    case_path: res.case_path, revision: res.revision, action: c.repair.id
                }});
                if (state.activeCasePath !== caseAtRequest) return;
                if (result.error) toast(result.error, 'error');
                else toast(`已修复 ${result.file}，原文件已备份`, 'success');
                await runPreflightCheck();
            });
            row.appendChild(repair);
        }
        box.appendChild(row);
    }
    panel.replaceChildren(box);
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
        body: payload
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
    'bathymetry.nc':   {label: '<svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-tools"></use></svg> 前处理', act: () => navigate('preprocess')},
    'meteo.nc':        {label: '<svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-weather"></use></svg> 填气象', act: () => _scrollToCard('meteo-csv-file')},
    'meteo_input.txt': {label: '<svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-weather"></use></svg> 填气象', act: () => _scrollToCard('meteo-csv-file')},
    'rivers.nc':       {label: '<svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-river"></use></svg> 配河流', act: () => _scrollToCard('river-add-name')},
    'riverinfo.dat':   {label: '<svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-river"></use></svg> 配河流', act: () => _scrollToCard('river-add-name')},
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
        $('input-overview').innerHTML = '<div class="empty-state"><div class="icon"><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-folder"></use></svg></div>请先加载案例</div>';
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
            ? '<span style="color:var(--success)"><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-check"></use></svg> 存在</span>'
            : '<span style="color:var(--danger)"><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-error"></use></svg> 缺失</span>';
        const size = f.exists ? fmtSize(f.size_bytes) : '-';
        const mtime = f.exists ? ModelDates.format(f.mtime) : '-';
        const nVars = f.exists ? (f.n_vars !== null && f.n_vars !== undefined ? f.n_vars : '-') : '-';
        const act = _INPUT_FILE_ACTIONS[f.name] ||
            {label: '<svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-build"></use></svg> 去构建', act: () => _scrollToCard('build-status')};
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
const _METEO_KEYS = ['u10', 'v10', 'slp', 't2', 'rh', 'tcc', 'precip', 'evap', 'swr'];

function downloadMeteoTemplate() {
    const csv = [
        'date,u10,v10,slp,t2,rh,tcc,precip,evap',
        '2020-DOY001,2.5,-1.2,1016.8,8.4,0.72,0.45,0.0,1.2',
        '2020-DOY002,3.1,-0.8,1015.2,7.9,0.78,0.62,0.6,1.1',
        '2020-DOY003,1.8,0.4,1017.9,9.2,0.65,0.30,0.0,1.3',
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
    fd.append('source_lat', $('meteo-source-lat')?.value || '');
    fd.append('source_lon', $('meteo-source-lon')?.value || '');
    fd.append('source_url', $('meteo-source-url')?.value || '');
    fd.append('license', $('meteo-source-license')?.value || '');
    fd.append('source_time_standard', $('meteo-source-time-standard')?.value || '');
    _ppStatus('meteo-upload-status', '上传解析中...', true);
    const res = await _uploadForm('/api/input/meteo/upload', fd);
    if (res.error) { _ppStatus('meteo-upload-status', '失败: ' + res.error, false); return; }
    let html = `<span>${StudioIcons.svg('check')} 已解析 <strong>${res.n_rows}</strong> 行（${ModelDates.format(res.date_range[0])} ~ ${ModelDates.format(res.date_range[1])}）</span>`;
    if (res.n_bad_rows) html += `<div style="color:var(--warning);font-size:11px;"><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-warning"></use></svg> ${res.n_bad_rows} 行日期无法解析，已跳过</div>`;
    if (res.unmapped_cols && res.unmapped_cols.length) html += `<div style="color:var(--warning);font-size:11px;"><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-warning"></use></svg> 未识别列（已忽略）: ${res.unmapped_cols.join(', ')}</div>`;
    if (res.conversions?.length) html += `<div style="font-size:11px;">导入转换：${res.conversions.map(escapeHtml).join('；')}</div>`;
    if (res.shortwave_mode === 'measured_swr') html += `<div style="font-size:11px;">实测短波路径：保留 SW_IN/SW_Rad_Avg（W/m²）并在 GETM 中直接使用；云量单独用于长波。无云量列时使用固定 0.5 云量代理。</div>`;
    const sourceCounts = res.forcing_source_counts || {};
    for (const [field, counts] of Object.entries(sourceCounts)) {
        const summary = Object.entries(counts).map(([sourceName, count]) => `${escapeHtml(sourceName)} ${Number(count)}`).join(' / ');
        html += `<div style="font-size:11px;">${escapeHtml(field)}：${summary}</div>`;
    }
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
        for (const [id, value] of [['meteo-source-lat',''],['meteo-source-lon',''],['meteo-source-url',''],['meteo-source-license',''],['meteo-source-time-standard','']]) {
            const input = $(id); if (input) input.value = value;
        }
        el.innerHTML = '<div style="color:var(--text-muted);font-size:12px;">尚未上传气象 CSV。上传后此处显示可编辑的数据表格。</div>';
        return;
    }
    state.meteoDraft = res;
    const source = res.source || {};
    const sourceInputs = [['meteo-source-lat',source.latitude],['meteo-source-lon',source.longitude],
        ['meteo-source-url',source.source_url],['meteo-source-license',source.license],
        ['meteo-source-time-standard',source.time_standard]];
    for (const [id, value] of sourceInputs) {
        const input = $(id); if (input) input.value = value ?? '';
    }
    _prefillBuildDates(res.dates[0], res.dates[res.dates.length - 1]);
    const n = res.dates.length;
    const show = Math.min(n, 200);
    const meteoKeys = res.shortwave_mode === 'measured_swr' ? _METEO_KEYS : _METEO_KEYS.filter(k => k !== 'swr');
    const head = ['date（年内儒略日）', ...meteoKeys].map(k => `<th>${k}</th>`).join('');
    let rows = '';
    for (let k = 0; k < show; k++) {
        rows += '<tr>' + `<td style="font-size:11px;white-space:nowrap;">${ModelDates.format(res.dates[k])}</td>` +
            meteoKeys.map(key =>
                `<td><input type="number" step="any" style="width:74px;padding:1px 4px;font-size:11px;" value="${fmt(res[key][k], 3)}" onchange="_meteoCellEdit(${k}, '${key}', this.value)"></td>`
            ).join('') + '</tr>';
    }
    el.innerHTML = `
        <div style="font-size:11px;color:var(--text-muted);margin-bottom:4px;">
            草稿共 <strong>${n}</strong> 行${n > show ? `（预览前 ${show} 行；未显示行按原值写入）` : ''}，可直接修改数值后生成 meteo.nc。降雨累计周期：${Number(res.precip_period_seconds) === 3600 ? '每小时' : `${Number(res.precip_period_seconds) / 3600} 小时`}；来源和缺测填充记录保存在 meteo_provenance.json。导入的任一列若有空值会拒绝，不会静默前向填充。
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

async function saveMeteoNc(confirmationToken=null) {
    if (!state.activeCase) { toast('请先加载案例', 'error'); return; }
    if (!state.meteoDraft) { _ppStatus('meteo-upload-status', '无气象草稿，请先上传 CSV', false); return; }
    _ppStatus('meteo-upload-status', '生成 meteo.nc 中...', true);
    let body = {};
    if (state.meteoEdited) {
        body.rows = state.meteoDraft.dates.map((d, k) => {
            const r = {date: d};
            const meteoKeys = state.meteoDraft.shortwave_mode === 'measured_swr' ? _METEO_KEYS : _METEO_KEYS.filter(key => key !== 'swr');
            meteoKeys.forEach(key => r[key] = state.meteoDraft[key][k]);
            return r;
        });
    }
    body.source_lat = $('meteo-source-lat')?.value || '';
    body.source_lon = $('meteo-source-lon')?.value || '';
    body.source_url = $('meteo-source-url')?.value || '';
    body.license = $('meteo-source-license')?.value || '';
    if (confirmationToken) body.confirmation_token = confirmationToken;
    const res = await api('/api/input/meteo/save', {method: 'POST', body});
    if (res.error) { _ppStatus('meteo-upload-status', '失败: ' + res.error, false); return; }
    if (res.requires_confirmation) {
        const w = res.warning || {}, center = w.grid_center || {};
        const station = w.position_known
            ? `${w.source_position.latitude}, ${w.source_position.longitude}` : '位置未知';
        const distance = Number.isFinite(w.distance_km) ? `${w.distance_km.toFixed(1)} km` : '不可计算';
        const message = `${w.message || '空间位置未验证'}\n来源站点：${station}\n网格中心：${center.latitude ?? '未知'}, ${center.longitude ?? '未知'}\n距离：${distance}\n\n${w.explanation || '单站序列会广播到全格点。'}\n\n确认继续生成 meteo.nc？`;
        _ppStatus('meteo-upload-status', `<strong><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-warning"></use></svg> ${escapeHtml(w.message || '空间位置未验证')}</strong><div>来源站点：${escapeHtml(station)} · 网格中心：${escapeHtml(`${center.latitude ?? '未知'}, ${center.longitude ?? '未知'}`)} · 距离：${escapeHtml(distance)}</div><div>${escapeHtml(w.explanation || '')}</div>`, false);
        if (window.confirm(message)) return saveMeteoNc(res.confirmation_token);
        _ppStatus('meteo-upload-status', '已取消生成；可修正来源位置后重试，或确认仍按单站均匀广播。', false);
        return;
    }
    _ppStatus('meteo-upload-status', `${StudioIcons.svg('check')} meteo.nc 已生成（${res.n_times} 个时步，广播到 ${res.grid} 网格，时间原点 ${ModelDates.format(res.start)}）`, true);
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
            <span style="color:var(--success);"><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-river"></use></svg></span>
            <strong style="min-width:86px;">${r.name}</strong>
            <span style="color:var(--text-muted);font-size:12px;">i=${r.i}, j=${r.j}</span>
            <span id="river-draft-${k}" style="font-size:11px;color:${r.has_draft ? 'var(--success)' : 'var(--danger)'};">${r.has_draft ? `<svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-check"></use></svg> ${r.n_rows} 行` : '<svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-error"></use></svg> 未上传数据'}</span>
            <input type="file" id="river-csv-${k}" accept=".csv,.txt" style="display:none;" onchange="_riverCsvChosen(${k})">
            <button class="btn btn-sm" style="margin-left:auto;" onclick="showRiverSeries('${r.name}')"><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-chart"></use></svg> 曲线</button>
            <button class="btn btn-sm" onclick="$('river-csv-${k}').click()"><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-upload"></use></svg> 上传CSV</button>
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
        if (st) { StudioIcons.setStatus(st, 'error', '上传失败', 'icon-status-error'); st.style.color = 'var(--danger)'; st.title = res.error; }
        toast(`${name}: ${res.error}`, 'error');
        return;
    }
    if (st) {
        StudioIcons.setStatus(st, 'check', `${res.n_rows} 行`, 'icon-status-ok');
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
    if (!await confirmStudio(`删除河流 ${name} 及其已上传的流量数据？`)) return;
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
    _ppStatus('rivers-save-status', `${StudioIcons.svg('check')} 已生成 rivers.nc（${res.n_rivers} 条河 × ${res.n_times} 个时步）与 riverinfo.dat`, true);
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
    if (res.error) { StudioIcons.setStatus($('river-series-status'), 'error', '曲线读取失败', 'icon-status-error'); $('river-series-status').title = res.error; state.riverSeries = null; return; }
    state.riverSeries = res;
    const sel = $('river-series-var');
    sel.innerHTML = Object.entries(res.series).map(([k, v]) =>
        `<option value="${k}">${v.long_name || k}${v.units ? ` (${v.units})` : ''}</option>`).join('');
    StudioIcons.setStatus($('river-series-status'), 'check', `${res.times.length} 个时步`, 'icon-status-ok');
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
    state.charts.river = localizedChart($('river-series-chart').getContext('2d'), {
        type: 'line',
        data: { labels: ModelDates.chartLabels(res.times), datasets: [{
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
    if ($('build-start') && !$('build-start').value) $('build-start').value = ModelDates.format(start, {time: true});
    if ($('build-stop') && !$('build-stop').value) $('build-stop').value = ModelDates.format(stop, {time: true});
}

// Validate displayed ordinal dates, then send the solver its existing ISO contract.
function _readModelPeriod(startId, stopId) {
    const start = ModelDates.toIso($(startId).value.trim(), {time: true});
    const stop = ModelDates.toIso($(stopId).value.trim(), {time: true});
    if (ModelDates.parse(stop).date.getTime() <= ModelDates.parse(start).date.getTime()) {
        throw new Error('结束时间必须晚于开始时间（年份 + 年内儒略日）');
    }
    $(startId).value = ModelDates.format(start);
    $(stopId).value = ModelDates.format(stop);
    return {start, stop};
}

async function buildCase() {
    if (!state.activeCase) { toast('请先加载案例', 'error'); return; }
    const caseName = state.activeCase, casePath = state.activeCasePath, revision = state.caseRevision;
    const current = () => caseName === state.activeCase && casePath === state.activeCasePath
        && revision === state.caseRevision;
    // 模块组合来自「模块配置」页；营养状态来自「初始条件」页
    const engines = {};
    (state.engines || []).forEach(e => { engines[e.key] = !!e.enabled; });
    let period;
    try { period = _readModelPeriod('build-start', 'build-stop'); }
    catch (error) { _ppStatus('build-status', error.message, false); return; }
    const timestep=Number($('build-dt').value.trim() || 15);
    if(!Number.isFinite(timestep) || timestep<=0){
        _ppStatus('build-status',window.StudioI18n?.scientificText('时间步长必须为有限的正数',
            'Time step must be a finite positive number.') || '时间步长必须为有限的正数',false);return;
    }
    const body = {
        preset: (state.icData && state.icData.trophic) || 'eutrophic',
        ...period,
        timestep,
        nlev: parseInt($('build-nlev').value) || 10,
        engines,
    };
    if (!body.start || !body.stop) { _ppStatus('build-status', '请填写开始/结束时间（可先上传气象 CSV 自动填充）', false); return; }
    if (!await confirmStudio(`构建案例 ${caseName}？\n将生成 getm.inp / fabm.yaml 等 9 个配置文件（已有配置会被覆盖，数据文件保留）`)) return;
    if (!current()) return;
    _ppStatus('build-status', '构建中（生成配置文件）...', true);
    const res = await api('/api/case/build', {method: 'POST', body});
    if (!current()) return;
    if (res.error) { _ppStatus('build-status', '失败: ' + res.error, false); return; }
    let html = `<span>${StudioIcons.svg('check')} 构建成功：预设 <strong>${res.preset_label}</strong>，${res.params_applied} 个生态参数已写入 fabm.yaml</span>`;
    (res.notes || []).forEach(n => { html += `<div style="color:var(--info);font-size:11px;"><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-info"></use></svg> ${n}</div>`; });
    (res.warnings || []).forEach(w => { html += `<div style="color:var(--warning);font-size:11px;"><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-warning"></use></svg> ${w}</div>`; });
    html += `<div style="font-size:11px;color:var(--text-muted);margin-top:4px;">案例文件: ${res.files.join(', ')}</div>`;
    _ppStatus('build-status', html, true);
    toast('案例构建成功，可到「运行控制」页运行模型', 'success');
    loadInputData();
    loadCases();
    // Silently refresh fabm module state: the case was loaded before build,
    // so state.fabmModules is stale/empty and module/parameter pages show blank.
    const data = await api('/api/case/load', {method: 'POST', body: {case_name: caseName, case_path: state.activeCasePath}});
    if (!current()) return;
    if (!data.error) {
        state.fabmModules = data.fabm.modules || [];
        state.fabmCategories = data.fabm.categories || {};
        refreshCaseStatistics(data);
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
        container.innerHTML = '<div class="empty-state"><div class="icon"><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-modules"></use></svg></div>加载案例后显示模块列表（未加载案例时，上方「功能模块」可先行选择引擎组合）</div>';
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
                <div style="margin-top:6px;"><span style="font-size:11px;color:${m.enabled ? 'var(--success)' : 'var(--text-muted)'}">${m.enabled ? `${StudioIcons.svg('check','icon-status-ok')} 已启用` : `${StudioIcons.svg('info')} 已禁用`}</span></div>
            </div>`;
        });
        html += '</div></div>';
    }
    if (!any) html += '<div class="empty-state"><div class="icon"><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-search"></use></svg></div>没有匹配的模块</div>';
    container.innerHTML = html;
}

async function toggleModule(name, currentlyEnabled) {
    if (!state.activeCase) { toast('请先加载案例', 'error'); return; }
    const nextEnabled = !currentlyEnabled;
    const verb = nextEnabled ? '启用' : '禁用';
    if (!await confirmStudio(`确定${verb}模块 "${name}"？`)) return;
    const res = await api('/api/config/fabm/module', {
        method: 'POST',
        body: { module: name, enabled: nextEnabled }
    });
    if (res.blocked_by_couplings) {
        const refs = Array.isArray(res.warnings) ? res.warnings.join('\n') : '';
        toast([res.repair_message, refs].filter(Boolean).join('\n'), 'warning');
        return;
    }
    if (res.needs_confirmation) {
        const msg = `以下模块依赖 ${name}：\n${res.warnings.join('\n')}\n\n仍要${verb}吗？`;
        if (!await confirmStudio(msg)) return;
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
            html = '<div style="font-size:11px;color:var(--warning);"><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-warning"></use></svg> 温室气体模块已启用，但当前模型程序不含该模块，正在/将自动编译，完成后自动部署。</div>';
        }
        warn.innerHTML = html;
    }
}

function engineCard(e) {
    const on = !!e.enabled;
    const engineIcon = ({hydro:'water',eco:'foodweb',water_quality:'flask',fish:'modules',ghg:'cloud'})[e.key] || 'modules';
    const hint = [];
    if (e.key === 'ghg' && on && e.building) hint.push('<svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-settings"></use></svg> 正在后台编译温室气体模块…');
    if (e.key === 'ghg' && on && !e.exe_has_ghg && !e.building) hint.push('<svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-settings"></use></svg> 新程序待部署：模型结束或下次启动运行前自动生效');
    return `<div class="module-card engine-card ${on ? 'enabled' : 'disabled'}" onclick="toggleEngine('${e.key}')" title="点击切换${on ? '关闭' : '启用'}">
        <div class="engine-title">${StudioIcons.svg(engineIcon)} ${e.long_name || e.label}</div>
        <div class="engine-desc">${e.desc}</div>
        <div class="engine-foot">
            <span class="switch ${on ? 'on' : ''}"><span class="track"><span class="knob"></span></span>${on ? '启用' : '关闭'}</span>
            ${e.fixed ? `<span style="color:var(--success);margin-left:10px;">${StudioIcons.svg('check','icon-status-ok')} 必选内核</span>` : ''}
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
        eco: ['启用生态网络（FABM-WET 食物网）？\n水质化学模块可单独启用。',
              '关闭生态网络？\n水质化学模块仍可独立运行。'],
        water_quality: ['启用水质化学模块（FABM-WET）？\n生态网络可单独启用。',
              '关闭水质化学模块？\n生态网络仍可独立运行。'],
        fish: ['启用鱼类模块（食物网顶层捕食者）？\n将新增 JuFish 幼鱼 / AdFish 成鱼 / PiscFish 食鱼性鱼三组状态变量，'
               + '闭合「藻—浮游动物—鱼」的下行控制链路。模块已编译在程序中，启用无需重新编译。',
               '关闭鱼类模块？\n将从配置中移除三个鱼类实例，食物网将缺少顶层捕食者（可一键重新启用）。'],
        ghg: ['启用温室气体引擎（CO₂/CH₄）？\n将新增 DIC/碱度/pH/甲烷状态变量并闭合碳循环；若当前程序未含该模块会自动编译。',
              '关闭温室气体引擎？\n将从配置中移除温室气体模块（再次启用时自动生成）。'],
    };
    const ask = ASK[key] || ['', ''];
    if (!await confirmStudio(next ? ask[0] : ask[1])) return;
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
    if (!await confirmStudio(next
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
async function loadParamModules() {
    // The parameter page can be opened from restored/imported sessions where
    // the active case is known but the in-memory FABM module cache is empty.
    // Hydrate only that empty cache; case-load remains the normal source of truth.
    const casePath = state.activeCasePath;
    if ((!Array.isArray(state.fabmModules) || !state.fabmModules.length) && casePath) {
        const data = await api('/api/config/fabm');
        if (casePath !== state.activeCasePath) return;
        if (!data.error && Array.isArray(data.modules)) {
            state.fabmModules = data.modules;
            state.fabmCategories = data.categories || {};
        }
    }
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
        const savedValue = p.saved_value ?? p.value;
        const dirtyClass = String(p.value) !== String(savedValue) ? ' param-dirty' : '';
        const unitHtml = p.unit
            ? `<span class="param-unit" title="单位">${escapeHtml(p.unit)}</span>` : '';
        const commentHtml = p.comment
            ? `<div class="param-comment" title="${escapeAttr(p.comment)}">${escapeHtml(p.comment)}</div>`
            : '';
        const description = window.StudioI18n?.scientificText(p.desc, p.desc_en) || p.desc || p.desc_en || '';
        const descHtml = description
            ? `<div class="param-desc" data-i18n-skip="true">${escapeHtml(description)}</div>` : '';
        const descEnHtml = '';
        const resetBtn = hasDefault && isModified
            ? `<button class="btn btn-sm" style="margin-left:4px;font-size:10px;padding:2px 6px;" title="恢复为默认值 ${p.default_value}" onclick="resetParam('${moduleName}', '${p.name}', ${idx})">${StudioIcons.svg('refresh')} 默认</button>`
            : '';
        row.innerHTML = `
            <span class="param-name">${p.name}${unitHtml}</span>
            <input class="param-value${dirtyClass}" value="${escapeAttr(p.value)}" data-idx="${idx}" data-type="${p.type || typeof p.value}" data-saved="${escapeAttr(savedValue)}" data-has-default="${hasDefault}" data-default="${hasDefault ? escapeAttr(p.default_value) : ''}" oninput="this.classList.toggle('param-dirty', this.value !== this.dataset.saved); scheduleParamSave(this, '${moduleName}', '${p.name}')" onchange="saveParam(this, '${moduleName}', '${p.name}')">
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
    if (input.dataset.hasDefault === 'false' || defaultVal === undefined) { toast('无默认值', 'warning'); return; }
    if (!await confirmStudio(`恢复 ${param} 为默认值 ${defaultVal}？`)) return;
    input.value = defaultVal;
    await saveParam(input, module, param);
}

function filterParams() {
    const q = $('param-search').value.toLowerCase();
    const filtered = state.currentParams.filter(p => p.name.toLowerCase().includes(q));
    renderParams(filtered);
}

const paramSaveTimers = new WeakMap();
function scheduleParamSave(input, module, param) {
    const pending = paramSaveTimers.get(input);
    if (pending !== undefined) clearTimeout(pending);
    const timer = setTimeout(() => {
        paramSaveTimers.delete(input);
        return saveParam(input, module, param);
    }, 400);
    paramSaveTimers.set(input, timer);
}

async function saveParam(input, module, param) {
    const pending = paramSaveTimers.get(input);
    if (pending !== undefined) {
        clearTimeout(pending);
        paramSaveTimers.delete(input);
    }
    let val = input.value;
    const moduleState = state.fabmModules.find(m => m.name === module);
    const paramState = moduleState?.parameters.find(p => p.name === param);
    const type = input.dataset.type || paramState?.type || typeof paramState?.value;
    if (type === 'boolean') {
        if (!['true', 'false'].includes(val.trim().toLowerCase())) { toast('布尔参数请输入 true 或 false', 'error'); return; }
        val = val.trim().toLowerCase() === 'true';
    } else if (type === 'number') {
        if (!val.trim() || !Number.isFinite(Number(val))) { toast('数值参数必须是有限数值，不能为空', 'error'); return; }
        val = Number(val);
    }
    const res = await api('/api/config/fabm/param', {method:'POST', body:{module, param, value:val}});
    const idx = input.dataset.idx;
    if (res.success) {
        if (paramState) { paramState.value = val; paramState.saved_value = val; }
        const current = state.currentParams.find(p => p.name === param);
        if (current && moduleState?.parameters.includes(current)) { current.value = val; current.saved_value = val; }
        input.dataset.saved = String(val);
        input.classList.remove('param-dirty');
        StudioIcons.setStatus($(`param-saved-${idx}`), 'check', '已保存', 'icon-status-ok');
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
    $('time-start').value = ModelDates.format(t.start, {time: true});
    $('time-stop').value = ModelDates.format(t.stop, {time: true});
    $('time-dt').value = t.timestep;
    $('time-step2d').value = t.step_2d;
    // Hotstart
    const hs = await api('/api/config/hotstart');
    if (!hs.error) {
        document.querySelector(`input[name="hotstart"][value="${hs.enabled?1:0}"]`).checked = true;
        $('hotstart-file').value = hs.file || '';
        $('hotstart-save').checked = hs.save;
        toggleHotstart(hs.enabled);
    }
    // Estimate
    const est = await api('/api/run/estimate');
    if (!est.error) {
        $('run-estimate').innerHTML = `
            <div class="grid-4">
                <div class="stat-card"><div class="stat-label">网格 / 垂向层</div><div class="stat-value" style="font-size:16px;">${est.grid} / ${est.nlev}</div></div>
                <div class="stat-card"><div class="stat-label">水域格</div><div class="stat-value">${est.nwater}</div></div>
                <div class="stat-card"><div class="stat-label">模拟时长</div><div class="stat-value">${fmt(est.duration_days,1)}<span class="stat-unit">天</span></div></div>
                <div class="stat-card"><div class="stat-label">总步数</div><div class="stat-value">${est.nsteps.toLocaleString()}</div></div>
            </div>
            <section class="card" aria-labelledby="run-estimate-workload-title" style="margin-top:12px;padding:14px;">
                <div class="card-title" id="run-estimate-workload-title">计算工作量</div>
                <p style="margin:6px 0 0;color:var(--text-secondary);font-size:12px;line-height:1.7;">网格、垂向层、水域格、模拟时长与总步数用于描述计算规模；它们不是运行耗时或内存预测。</p>
                <div style="margin-top:10px;padding-top:10px;border-top:1px solid var(--border);">
                    <strong style="font-size:13px;">耗时与内存：暂无同机、同案例实测值</strong>
                    <div style="margin-top:4px;color:var(--text-muted);font-size:12px;line-height:1.7;">${est.runtime_estimate_note || '未在当前计算机与此案例配置下完成实测，暂不提供耗时或 RAM 数字。'} ${est.pilot_guidance || ''}</div>
                </div>
            </section>
            <section class="card" aria-labelledby="run-estimate-protocol-title" style="margin-top:8px;padding:14px;">
                <div class="card-title" id="run-estimate-protocol-title">学术验证流程</div>
                <p style="margin:6px 0 0;color:var(--text-secondary);font-size:12px;line-height:1.7;"><strong>先由研究问题选择模型复杂度：</strong>单点或垂向温度目标可优先评估一维水柱模型；只有研究问题涉及水平输运或空间异质性时才需要三维水动力；只有生态变量是目标且有相应观测时才启用生态过程。三维可视化本身不意味着必须运行三维生态求解。</p>
                <ol style="margin:8px 0 0;padding-left:20px;color:var(--text-secondary);font-size:12px;line-height:1.75;">
                    <li><strong>软件链路短时检查：</strong>确认求解器可启动、运行稳定并产出可检查的结果；此检查只用于核对软件链路，不构成科学验证或模型充分性证据。</li>
                    <li><strong>代表性时段试跑：</strong>按研究问题选取覆盖启动/预热及目标过程的时段，在案例副本上记录硬件、配置、墙钟时间和完成步数。先检查目标变量的观测支持与结果可解释性，再决定停止、增加代表性试跑或升级复杂度；只有同机同配置的记录可作为粗略工作量参考。</li>
                    <li><strong>正式校准与独立期验证：</strong>仅在研究问题、可用观测与参数可辨识性支持时开展；预先说明目标函数和参数范围，并用独立时段检验。拟合结果不等同于独立验证。</li>
                </ol>
            </section>
            ${est.cfl_ok === false ? `<div style="margin-top:8px;padding:10px 12px;background:#fde8e8;border:1px solid #f5c2c7;border-radius:6px;color:#842029;font-size:13px;">
                <strong><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-warning"></use></svg> 时间步长 ${est.timestep}s 超过稳定上限 ${est.cfl_max}s</strong>（网格 CFL≈${Math.round(est.cfl_dt)}s 的 15 倍）。此步长会导致模型数值发散、输出全为 NaN，请改小（建议 60~${Math.round(est.cfl_dt*3)}s）。
            </div>` : (est.cfl_max ? `<div style="margin-top:8px;font-size:11px;color:var(--text-muted);">当前步长 ${est.timestep}s ≤ 稳定上限 ${est.cfl_max}s ${StudioIcons.svg('check')}</div>` : '')}`;
    }
}

async function saveTimeSettings() {
    let period;
    try { period = _readModelPeriod('time-start', 'time-stop'); }
    catch (error) { toast(error.message, 'error'); return; }
    const res = await api('/api/config/time', {method:'POST', body:{
        ...period,
        timestep: Number($('time-dt').value), step_2d: Number($('time-step2d').value),
    }});
    toast(res.success ? '时间设置已保存' : (res.error || '保存失败'), res.success?'success':'error');
    if (res.success) loadTimeSettings();
}

function toggleHotstart(enabled) { $('hotstart-file-group').style.display = enabled ? 'block' : 'none'; }

async function saveHotstart() {
    const enabled = document.querySelector('input[name="hotstart"]:checked').value === '1';
    const res = await api('/api/config/hotstart', {method:'POST', body:{enabled, file:$('hotstart-file').value, save:$('hotstart-save').checked}});
    toast(res.success ? '启动设置已保存' : (res.error || '保存失败'), res.success?'success':'error');
    if (res.success) await loadTimeSettings();
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
    if (el) StudioIcons.setStatus(el, 'edit', '有未保存的修改', 'icon-status-warning');
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
    renderIcWaterQuality(false);

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
    applyPresetToFields();
    toast(`营养状态已设为「${(state.icData.trophic_presets || {})[key]}」，记得点「保存到案例」`, 'info');
}

// fabm variable name -> input element id
function icPresetVarMap() {
    const map = {};
    const bare = {};
    (state.icData.modules || []).forEach(m => {
        Object.keys(m.init || {}).forEach(p => {
            const id = `icv-${m.name}-${p}`;
            map[m.name+'_'+p] = id;
            map[m.name+'.'+p] = id;
            bare[p] = bare[p] === undefined ? id : null;
        });
    });
    Object.keys(bare).forEach(p => { if (bare[p]) map[p] = bare[p]; });
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
        if (el) { el.value = pv[f]; el.dataset.icPreset = '1'; delete el.dataset.icUser; n++; }
    });
    captureIcDrafts();
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
    Object.keys(pv).forEach(f => {
        const el = map[f] && $(map[f]);
        if (el && el.dataset.icPreset === '1' && !el.dataset.icUser) {
            el.value = pv[f]; n++;
        }
    });
    // also fill inputs generated for variables the case does not declare yet
    Object.keys(pv).forEach(f => {
        if (document.getElementById(`icv-new-${f}`)) {
            const el2 = $(`icv-new-${f}`);
            if (!el2.dataset.icUser) { el2.value = pv[f]; n++; }
        }
    });
    captureIcDrafts();
    toast(`已套用「${(state.icData.trophic_presets || {})[key]}」预设 ${n} 项`, 'success');
    icIcDirty();
}

function renderIcWaterQuality(preserveDrafts = true) {
    const host = $('ic-wq-modules');
    if (!host) return;
    const d = state.icData || {};
    if (preserveDrafts) captureIcDrafts();
    const mods = d.modules || [];
    const q = ($('ic-wq-search') ? $('ic-wq-search').value : '').trim().toLowerCase();
    const presets = d.preset_values || {};
    const pv = presets[d.trophic] || {};
    if (!mods.length) {
        host.innerHTML = `<div class="empty-state"><div class="icon"><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-flask"></use></svg></div>
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
                const id = `icv-${m.name}-${p}`;
                const draft = d.draftInputs?.[id];
                const val = draft ? draft.value : m.init[p];
                const presetValue = pv[m.name+'_'+p] ?? pv[m.name+'.'+p] ?? pv[p];
                const isPreset = presetValue !== undefined && Math.abs(Number(presetValue) - Number(val)) < 1e-9;
                const dd = docs[p] || {};
                const unit = dd.unit || (m.units && m.units[p]) || 'g/m³';
                const zh = dd.zh || '';
                const en = dd.desc_en || dd.desc || '';
                const description = window.StudioI18n?.scientificText(zh,en) || [zh,en].filter(Boolean).join(' / ');
                const descHtml = description
                    ? `<span class="ic-desc" data-i18n-skip="true" data-scientific-zh="${escapeAttr(zh)}" data-scientific-en="${escapeAttr(en)}" title="${escapeAttr(description)}">${escapeHtml(description)}</span>`
                    : '';
                return `<div class="ic-row">
                    <label title="${escapeAttr(p)}">${escapeHtml(p)}</label>
                    <input class="form-input" type="number" step="any" id="${escapeAttr(id)}" value="${escapeAttr(val)}"
                           data-ic-key="${escapeAttr(m.name+'.'+p)}" data-ic-preset="${isPreset ? 1 : 0}" ${draft?.user ? 'data-ic-user="1"' : ''} oninput="onIcVarEdit(this)">
                    <span class="ic-unit">${escapeHtml(unit)}</span>
                    ${descHtml}
                </div>`;
            }).join('');
            const searchHit = !q || m.name.toLowerCase().includes(q) ||
                (m.long_name || '').toLowerCase().includes(q) ||
                (m.desc || '').toLowerCase().includes(q) ||
                (m.desc_en || '').toLowerCase().includes(q) ||
                Object.keys(m.init || {}).some(p =>
                    p.toLowerCase().includes(q) ||
                    ((docs[p] || {}).desc || '').toLowerCase().includes(q));
            if (!searchHit) return '';
            const moduleEn = m.desc_en || m.long_name || '';
            const moduleText = window.StudioI18n?.scientificText(m.desc,moduleEn) || [m.desc,moduleEn].filter(Boolean).join(' / ');
            const modDesc = moduleText
                ? `<div class="ic-mod-desc"><span data-i18n-skip="true" data-scientific-zh="${escapeAttr(m.desc || '')}" data-scientific-en="${escapeAttr(moduleEn)}">${escapeHtml(moduleText)}</span>${m.model ? ` <code>${escapeAttr(m.model)}</code>` : ''}</div>`
                : '';
            return `<div class="ic-mod">
                <div class="ic-mod-title">${StudioIcons.svg('modules')}
                    ${escapeHtml(m.name)}
                    <em>${escapeHtml(m.long_name)}</em>
                </div>
                ${modDesc}
                <div class="ic-rows">${rows || '<div style="font-size:11px;color:var(--text-muted);">（无初始条件）</div>'}</div>
            </div>`;
        }).join('');
        const categoryEn = grouped[cat][0]?.category_en || '';
        const categoryText = window.StudioI18n?.scientificText(cat,categoryEn) || [cat,categoryEn].filter(Boolean).join(' / ');
        return `<div class="ic-group"><div class="ic-group-title" data-i18n-skip="true" data-scientific-zh="${escapeAttr(cat)}" data-scientific-en="${escapeAttr(categoryEn)}">${escapeHtml(categoryText)}</div>${cards}</div>`;
    }).join('') || '<div class="empty-state"><div class="icon"><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-search"></use></svg></div>没有匹配的模块</div>';

    renderIcExtraVars(pv);
}

function captureIcDrafts() {
    if (!state.icData || typeof document === 'undefined') return;
    const drafts = state.icData.draftInputs ||= {};
    document.querySelectorAll('[id^="icv-"]').forEach(el => {
        const rest = el.id.slice(4), split = rest.indexOf('-');
        const key = el.dataset?.icKey || (rest.startsWith('new-') ? rest.slice(4)
            : split > 0 ? rest.slice(0,split)+'.'+rest.slice(split+1) : '');
        if (key) drafts[el.id] = {key,value:el.value,user:el.dataset?.icUser === '1'};
    });
}

// Variables that are not declared in fabm instances yet – allow typing them anyway
function renderIcExtraVars(pv) {
    const host = $('ic-wq-modules');
    if (!host) return;
    const d = state.icData || {};
    const known = icPresetVarMap();
    const extra = Object.keys(pv).filter(f => !known[f] && f !== 'macro_sD' &&
        typeof pv[f] === 'number' && Number.isFinite(pv[f]));
    if (!extra.length) return;
    const rows = extra.map(f => {
        const has = document.getElementById(`icv-new-${f}`) !== null;
        if (has) return '';
        return `<div class="ic-row">
            <label title="${escapeAttr(f)}">${escapeHtml(f)}</label>
            <input class="form-input" type="number" step="any" id="icv-new-${escapeAttr(f)}" value="${escapeAttr(d.draftInputs?.['icv-new-'+f]?.value ?? pv[f])}"
                   data-ic-key="${escapeAttr(f)}" data-ic-preset="1" oninput="onIcVarEdit(this)">
            <span class="ic-unit">g/m³</span>
        </div>`;
    }).join('');
    if (!rows) return;
    const div = document.createElement('div');
    div.className = 'ic-group';
    div.innerHTML = `<div class="ic-group-title"><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-list"></use></svg> 预设中的其他变量</div><div class="ic-mod"><div class="ic-rows">${rows}</div></div>`;
    host.appendChild(div);
}

function onIcVarEdit(el) {
    el.dataset.icUser = '1';
    captureIcDrafts();
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

    // Include edits hidden by filtering; keep drafts separate from saved values.
    captureIcDrafts();
    const water_quality = {};
    for (const draft of Object.values(d.draftInputs || {})) {
        if (String(draft.value).trim()==='' || !Number.isFinite(Number(draft.value))) {
            toast(`初始条件 ${draft.key} 必须填写有限数值`, 'error'); return;
        }
        water_quality[draft.key] = Number(draft.value);
    }

    const macroEl = $('ic-macro-sd');
    const macrophytes = macroEl && macroEl.value !== '' ? { sD_max: Number(macroEl.value) } : null;

    const res = await api('/api/case/init_conditions', { method: 'POST', body: {
        hydro, water_quality, macrophytes, trophic: d.trophic || null,
    }});
    if (res.error) { toast(res.error, 'error'); return; }
    const warnings=Array.isArray(res.warnings) ? res.warnings.filter(Boolean) : [];
    if(warnings.length) {
        d.dirty = true;
        StudioIcons.setStatus($('ic-save-status'), 'warning', '部分保存失败：' + warnings.join('；'), 'icon-status-warning');
        toast('初始条件部分保存失败，请核对提示并重新保存', 'warning');
        return;
    }
    (d.modules || []).forEach(m => Object.keys(m.init || {}).forEach(p => {
        const key = m.name+'.'+p;
        if (Object.hasOwn(water_quality,key)) m.init[p] = water_quality[key];
    }));
    d.dirty = false;
    $('ic-save-status').textContent = res.notes && res.notes.length
        ? '<svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-check"></use></svg> ' + res.notes.join('；')
        : '<svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-check"></use></svg> 已保存';
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
    const coreInput = document.getElementById('core-count');
    const modeInput = document.getElementById('parallel-mode');
    const cores = Math.max(1, Math.floor(Number(coreInput && coreInput.value) || 1));
    const parallelMode = (modeInput && modeInput.value) || 'auto';
    const compressResults = !!document.getElementById('compress-run-results')?.checked;
    const mpi = parallelMode === 'mpi' || parallelMode === 'hybrid';
    const res = await api('/api/run/start', {method:'POST', body:{
        cores, parallel_mode: parallelMode, compress_results:compressResults, mpi, processes: cores}});
    if (!res.success) { toast(res.error || '启动失败', 'error'); return; }
    advanceOutputRevision();
    $('btn-start-run').disabled = true;
    $('btn-stop-run').disabled = false;
    $('run-log').innerHTML = '';
    state.runLogLimit = 80;
    state.runLogCursor = {lastLines: []};
    $('run-console-log-status').textContent = '';
    $('run-console-load-more').disabled = true;
    toast('模型已启动', 'success');
    updateRunNotificationStatus({status:'running',progress:null,eta_minutes:null,current_step:null,total_steps:null});
    state.etaNotified = new Set();  // reset ETA threshold tracker
    state.previousEtaMinutes = null;
    state.lastRunStatus = 'running';
    state.lastLogSnapshot = '';
    clearInterval(state.runPollTimer);
    // Status is lightweight and never opens in-progress model results.
    state.runPollTimer = setInterval(pollRunStatus, 2000);
    pollRunStatus();
}

function appendRunLogLines(log, lines, cursor) {
    const incoming = Array.isArray(lines) ? lines : [];
    const previous = cursor.lastLines || [];
    if (!incoming.length) return;
    const followsTail = log.scrollHeight - log.scrollTop - log.clientHeight <= 12;
    const oldHeight = log.scrollHeight;
    let appendFrom = 0;
    let prependCount = 0;

    if (previous.length && incoming.length >= previous.length &&
        previous.every((line, index) => line === incoming[index])) {
        appendFrom = previous.length;
    } else if (previous.length && incoming.length > previous.length &&
        previous.every((line, index) => line === incoming[incoming.length - previous.length + index])) {
        prependCount = incoming.length - previous.length;
    } else if (previous.length) {
        let overlap = Math.min(previous.length, incoming.length);
        while (overlap > 0 && !previous.slice(-overlap).every((line, index) => line === incoming[index])) overlap--;
        if (overlap) {
            const dropped = previous.length - overlap;
            if (dropped && log.children?.length) {
                let removedHeight = 0;
                for (let i = 0; i < dropped && log.firstChild; i++) {
                    removedHeight += log.firstChild.getBoundingClientRect?.().height || 0;
                    log.removeChild(log.firstChild);
                }
                if (!followsTail) log.scrollTop = Math.max(0, log.scrollTop - removedHeight);
            }
            appendFrom = overlap;
        } else {
            // A fresh run or rewritten log has no shared tail. Reset only on
            // this discontinuity; normal polls append to the existing DOM.
            log.replaceChildren();
            cursor.lastLines = [];
        }
    }

    const makeLine = line => {
        const node = document.createElement('div');
        node.className = 'log-line ' + (line.includes('ERROR') ? 'error' : line.includes('完成') ? 'success' : line.includes('INFO') ? 'info' : '');
        node.textContent = ModelDates.formatText(line);
        return node;
    };
    if (prependCount) {
        for (let i = prependCount - 1; i >= 0; i--) log.insertBefore(makeLine(incoming[i]), log.firstChild);
        if (!followsTail) log.scrollTop += log.scrollHeight - oldHeight;
    } else {
        for (let i = appendFrom; i < incoming.length; i++) log.appendChild(makeLine(incoming[i]));
    }
    cursor.lastLines = incoming.slice();
    if (followsTail) log.scrollTop = Math.max(0, log.scrollHeight - log.clientHeight);
}

function syncRunLogContext(log, identity, cursor) {
    if (!identity || identity === state.runLogIdentity) return false;
    state.runLogIdentity = identity;
    state.runLogLimit = 80;
    state.lastLogSnapshot = '';
    log.replaceChildren();
    cursor.lastLines = [];
    $('run-console-log-status').textContent = '';
    return true;
}

async function loadMoreRunLogs() {
    const limits = [80, 200, 500, 1000, 2000, 5000];
    const current = state.runLogLimit || 80;
    const next = limits.find(limit => limit > current);
    if (!next) return;
    state.runLogLimit = next;
    await pollRunStatus();
}

async function copyRunLogs() {
    const text = Array.from($('run-log').querySelectorAll('.log-line'), node => node.textContent).join('\n');
    const status = $('run-console-log-status');
    const translate = message => window.StudioI18n?.t(message) || message;
    if (!text) { status.textContent = translate('没有可复制的运行日志。'); return; }
    try {
        await navigator.clipboard.writeText(text);
        status.textContent = translate('运行日志已复制。');
        toast(translate('运行日志已复制。'), 'success');
    } catch (_) {
        status.textContent = translate('无法访问剪贴板，请使用键盘选择日志并复制。');
        toast(translate('无法访问剪贴板，请使用键盘选择日志并复制。'), 'warning');
    }
}

function coreStorageKey(casePath, kind) {
    return `3dwet-${kind}:${casePath || ''}`;
}

function readCoreOverride(casePath) {
    try {
        const mode = localStorage.getItem(coreStorageKey(casePath, 'mode'))
            || localStorage.getItem('3dwet-mode');
        const cores = localStorage.getItem(coreStorageKey(casePath, 'cores'))
            || localStorage.getItem('3dwet-cores');
        if (!mode || mode === 'auto') return null;
        const n = Math.floor(Number(cores));
        if (!Number.isInteger(n) || n < 1) return null;
        return {mode, cores: n};
    } catch (_) {
        return null;
    }
}

function writeCoreOverride(casePath, mode, cores) {
    try {
        localStorage.setItem(coreStorageKey(casePath, 'mode'), mode);
        localStorage.setItem(coreStorageKey(casePath, 'cores'), String(cores));
        localStorage.setItem('3dwet-mode', mode);
        localStorage.setItem('3dwet-cores', String(cores));
    } catch (_) {}
}

function clearCoreOverrides() {
    try {
        const drop = [];
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && (key.startsWith('3dwet-mode') || key.startsWith('3dwet-cores'))) drop.push(key);
        }
        drop.forEach(key => localStorage.removeItem(key));
    } catch (_) {}
}

function bindCoreControls() {
    const count = document.getElementById('core-count');
    const mode = document.getElementById('parallel-mode');
    if (!count || !mode || count.dataset.bound === '1') return;
    count.dataset.bound = '1';
    count.addEventListener('input', () => {
        state.corePlanTouched = true;
        if (mode.value === 'auto') mode.value = 'threads';
        const n = Math.max(1, Math.floor(Number(count.value) || 1));
        writeCoreOverride(state.activeCasePath, mode.value, n);
    });
    mode.addEventListener('change', () => {
        state.corePlanTouched = true;
        const n = Math.max(1, Math.floor(Number(count.value) || 1));
        if (mode.value === 'auto') {
            try {
                localStorage.removeItem(coreStorageKey(state.activeCasePath, 'mode'));
                localStorage.removeItem(coreStorageKey(state.activeCasePath, 'cores'));
                localStorage.setItem('3dwet-mode', 'auto');
            } catch (_) {}
            return;
        }
        writeCoreOverride(state.activeCasePath, mode.value, n);
    });
}

function applyCoreRecommendation(plan) {
    const count = document.getElementById('core-count');
    const mode = document.getElementById('parallel-mode');
    const note = document.getElementById('core-plan-note');
    if (!count || !mode || !note || state.corePlanTouched) {
        if (note && plan) note.textContent = plan.summary || note.textContent;
        return;
    }
    const override = readCoreOverride(state.activeCasePath);
    const rec = plan.recommendation || {};
    if (override) {
        mode.value = override.mode;
        count.value = String(override.cores);
    } else {
        mode.value = 'auto';
        count.value = String(Math.max(1, Number(rec.cores) || 1));
    }
    note.textContent = plan.summary || '';
    renderCoreTrials(plan.trials);
}

function renderCoreTrials(trials) {
    const table = document.getElementById('core-trial-table');
    if (!table) return;
    const rows = Array.isArray(trials) ? trials : [];
    if (!rows.length) {
        table.replaceChildren();
        return;
    }
    const labels = {serial: '串行', threads: 'OpenMP', mpi: 'MPI', hybrid: '混合'};
    const head = document.createElement('thead');
    const headRow = document.createElement('tr');
    ['方式', '规模', '步/秒'].forEach(text => {
        const cell = document.createElement('th');
        cell.textContent = text;
        cell.style.textAlign = 'left';
        cell.style.fontWeight = '600';
        cell.style.paddingRight = '12px';
        headRow.appendChild(cell);
    });
    head.appendChild(headRow);
    const body = document.createElement('tbody');
    rows.forEach(row => {
        const ranks = Number(row.ranks) || 1;
        const threads = Number(row.threads) || 1;
        const shape = ranks > 1 && threads > 1 ? `${ranks}×${threads}` : String(ranks > 1 ? ranks : threads);
        const rate = row.ok && Number.isFinite(Number(row.steps_per_second))
            ? Number(row.steps_per_second).toFixed(1) : '失败';
        const line = document.createElement('tr');
        [labels[row.mode] || row.mode || '', shape, rate].forEach(text => {
            const cell = document.createElement('td');
            cell.textContent = text;
            cell.style.paddingRight = '12px';
            line.appendChild(cell);
        });
        body.appendChild(line);
    });
    table.replaceChildren(head, body);
}

async function remeasureCorePlan() {
    const note = document.getElementById('core-plan-note');
    const button = document.getElementById('core-recalibrate');
    if (button) button.disabled = true;
    if (note) note.textContent = '正在重新测定…';
    state.corePlanTouched = false;
    try {
        let plan = await api('/api/run/core-plan', {method: 'POST', body: {}});
        while (plan && plan.calibrating) {
            if (note) note.textContent = plan.summary || '正在测定核数…';
            await new Promise(resolve => setTimeout(resolve, 2000));
            plan = await api('/api/run/core-plan');
        }
        if (!plan) return;
        applyCoreRecommendation(plan);
        renderCoreTrials(plan.trials);
    } catch (error) {
        if (note) note.textContent = '重新测定没有完成。可稍后再试。';
    } finally {
        if (button) button.disabled = false;
    }
}

async function loadCorePlan() {
    const count = document.getElementById('core-count');
    const mode = document.getElementById('parallel-mode');
    const note = document.getElementById('core-plan-note');
    if (!count || !mode || !note) return;
    const request = state.corePlanRequest = (state.corePlanRequest || 0) + 1;
    const casePath = state.activeCasePath;
    const isCurrent = () => request === state.corePlanRequest && casePath === state.activeCasePath;
    state.corePlanTouched = false;
    bindCoreControls();
    try {
        let plan = await api('/api/run/core-plan');
        if (!isCurrent()) return;
        if (plan.error && !plan.hardware) {
            note.textContent = plan.error;
            return;
        }
        const fingerprint = plan.fingerprint || '';
        try {
            const seen = localStorage.getItem('3dwet-hw');
            if (seen && fingerprint && seen !== fingerprint) clearCoreOverrides();
            if (fingerprint) localStorage.setItem('3dwet-hw', fingerprint);
        } catch (_) {}
        applyCoreRecommendation(plan);
        renderCoreTrials(plan.trials);
        const posted = state.coreCalibrationPosted || (state.coreCalibrationPosted = new Set());
        const postKey = `${casePath || ''}|${fingerprint}`;
        if (!plan.cached && plan.can_calibrate && !plan.calibrating && !posted.has(postKey)) {
            posted.add(postKey);
            const started = await api('/api/run/core-plan', {method:'POST', body:{}});
            if (!isCurrent()) return;
            if (started && started.hardware) plan = started;
            else if (started && started.error) note.textContent = started.error;
        }
        while (isCurrent() && plan.calibrating) {
            note.textContent = plan.summary || '正在测定核数…';
            await new Promise(resolve => setTimeout(resolve, 2000));
            if (!isCurrent()) return;
            plan = await api('/api/run/core-plan');
        }
        if (!isCurrent()) return;
        if (plan.calibration_error) {
            note.textContent = `测定没有完成（${plan.calibration_error}）。${plan.summary || ''}`;
        }
        applyCoreRecommendation(plan);
        renderCoreTrials(plan.trials);
    } catch (error) {
        if (!isCurrent()) return;
        note.textContent = '无法读取本机核数。可手动填写使用核数。';
    }
}

async function loadMpiRunCapabilities() {
    const toggle = document.getElementById('mpi-run-enabled');
    const count = document.getElementById('mpi-process-count');
    const note = document.getElementById('mpi-run-capability');
    const detectButton = document.getElementById('mpi-detect-recommendation');
    if (!toggle || !count || !note || !detectButton) return;
    const tuneButton = document.getElementById('mpi-start-tuning');
    const request = state.mpiCapabilitiesRequest = (state.mpiCapabilitiesRequest || 0) + 1;
    const caseRevision = state.caseRevision || 0;
    const casePath = state.activeCasePath;
    const caseType = state.caseType;
    const readOnly = state.storageReadOnly;
    const isCurrent = () => request === state.mpiCapabilitiesRequest
        && caseRevision === (state.caseRevision || 0)
        && casePath === state.activeCasePath
        && caseType === state.caseType
        && readOnly === state.storageReadOnly;
    const eligible = () => !!state.activeCasePath && state.caseType === 'getm' && !state.storageReadOnly;
    if (!eligible()) {
        toggle.checked = false;
        toggle.disabled = true;
        count.disabled = true;
        detectButton.disabled = true;
        if (tuneButton) tuneButton.disabled = true;
    }
    try {
        const caps = await api('/api/run/mpi-capabilities');
        if (!isCurrent()) return;
        if (!eligible() || !caps.enabled) {
            toggle.checked = false;
            toggle.disabled = true;
            count.disabled = true;
            detectButton.disabled = true;
            if (tuneButton) tuneButton.disabled = true;
            if (caps.reason) note.textContent = caps.reason;
            return;
        }
        const allowed = Array.isArray(caps.allowed_processes) ? caps.allowed_processes : [];
        count.replaceChildren(...allowed.map(value => {
            const option = document.createElement('option');
            option.value = String(value);
            option.textContent = String(value);
            return option;
        }));
        const allowedText = allowed.map(String);
        const savedCount = state.mpiProcessCountByCase && state.mpiProcessCountByCase.get(casePath);
        if (savedCount != null && allowedText.includes(String(savedCount))) count.value = String(savedCount);
        else if (allowedText.includes(String(caps.recommended_processes))) count.value = String(caps.recommended_processes);
        count.onchange = () => {
            const selected = Number(count.value);
            if (Number.isInteger(selected) && state.mpiProcessCountByCase) {
                state.mpiProcessCountByCase.set(state.activeCasePath, selected);
            }
        };
        const remembered = state.mpiSelectionByCase && state.mpiSelectionByCase.get(casePath);
        toggle.checked = remembered == null ? true : !!remembered;
        toggle.disabled = false;
        count.disabled = !toggle.checked;
        detectButton.disabled = false;
        if (tuneButton) tuneButton.disabled = false;
        toggle.onchange = () => {
            if (state.mpiSelectionByCase) state.mpiSelectionByCase.set(state.activeCasePath, toggle.checked);
            count.disabled = !toggle.checked;
        };
        note.textContent = `当前进程可用逻辑处理器：${caps.max_processes}；建议 ${caps.recommended_processes} 个进程。建议值不保证最快。`;
    } catch (error) {
        if (!isCurrent()) return;
        note.textContent = String(error?.message || error || '无法读取 MPI 运行能力');
    }
}

async function detectAndApplyMpiRecommendation() {
    const toggle = document.getElementById('mpi-run-enabled');
    const count = document.getElementById('mpi-process-count');
    const note = document.getElementById('mpi-run-capability');
    const detectButton = document.getElementById('mpi-detect-recommendation');
    if (!toggle || !count || !note || !detectButton) return;
    const request = state.mpiRecommendationRequest = (state.mpiRecommendationRequest || 0) + 1;
    const caseRevision = state.caseRevision || 0;
    const casePath = state.activeCasePath;
    const caseType = state.caseType;
    const isCurrent = () => request === state.mpiRecommendationRequest
        && caseRevision === (state.caseRevision || 0)
        && casePath === state.activeCasePath
        && caseType === state.caseType;
    if (!casePath || caseType !== 'getm' || state.storageReadOnly || toggle.disabled) return;
    detectButton.disabled = true;
    try {
        const caps = await api('/api/run/mpi-capabilities');
        if (!isCurrent()) return;
        const recommended = Number(caps.recommended_processes);
        const allowed = (caps.allowed_processes || []).map(Number);
        if (!Number.isInteger(recommended) || (allowed.length && !allowed.includes(recommended))) {
            throw new Error(caps.reason || '没有可用的建议进程数');
        }
        count.value = String(recommended);
        if (state.mpiProcessCountByCase) state.mpiProcessCountByCase.set(casePath, recommended);
        note.textContent = `可用逻辑处理器：${caps.max_processes}。已采用建议 ${recommended} 个进程。这是起点，不保证最快。`;
    } catch (error) {
        if (!isCurrent()) return;
        note.textContent = String(error?.message || error || '无法读取 MPI 运行能力');
    } finally {
        if (isCurrent()) detectButton.disabled = !!toggle.disabled;
    }
}

function applyMpiTuningResult(result, casePath, note, count) {
    const selected = Number(result?.selected_processes);
    if (!Number.isInteger(selected) || selected < 1) throw new Error('没有有效成功的测量结果');
    const samples = result.measurements?.[String(selected)] || [];
    count.value = String(selected);
    state.mpiProcessCountByCase.set(casePath, selected);
    const fastest = Math.min(...Object.values(result.measurements || {}).flat().map(Number));
    note.textContent = `实测选择 ${selected} 个进程；本机/案例指纹已缓存。候选耗时含结果合并；最快样本 ${Number.isFinite(fastest) ? fastest.toFixed(1) : '—'} 秒。此结果不代表其他案例或硬件。`;
}

async function startMpiTuning() {
    const trialHours = 3;
    const note = document.getElementById('mpi-run-capability');
    if (note) note.textContent = `覆盖至少 ${trialHours} 小时的模拟时段`;
    await api('/api/run/mpi-tuning', {method:'POST', body:{duration_seconds:10800,repetitions:2}});
}

async function cancelMpiTuning() {
    try {
        await api('/api/run/mpi-tuning', {method:'DELETE'});
        const note = document.getElementById('mpi-run-capability');
        if (note) note.textContent = '正在停止当前试跑并清理隔离副本…';
    } catch (error) {
        toast(String(error?.message || error || '无法取消测量'), 'error');
    }
}
document.addEventListener('DOMContentLoaded', () => {
    loadCorePlan();
    loadMpiRunCapabilities();
});

function advanceOutputRevision() {
    state.outputRevision=(state.outputRevision || 0)+1;
    window.Viz2DPlaybackPrefetch?.clear();
    window.clearViz3dPlaybackPrefetch?.();
}

async function stopRun() {
    await api('/api/run/stop', {method:'POST'});
    $('btn-stop-run').disabled = true;
    toast('已发送停止指令', 'info');
}

function appendRunNotificationFallback(title, body, kind='info') {
    const center = $('run-notification-center');
    const list = $('run-notification-list');
    if (!center || !list) return;
    center.hidden = false;
    const item = document.createElement('li');
    item.className = `run-notification-event ${kind}`;
    item.setAttribute('role', 'listitem');
    const iconKind = kind === 'completed' ? 'check' : kind === 'failed' ? 'error' : kind === 'stopped' ? 'stop' : 'info';
    item.appendChild(StudioIcons.node(iconKind, kind === 'failed' ? 'icon-status-error' : kind === 'completed' ? 'icon-status-ok' : ''));
    const message = document.createElement('span');
    message.textContent = `${title}: ${body}`;
    item.appendChild(message);
    list.prepend(item);
    while (list.children.length > 8) list.removeChild(list.lastElementChild);
}

function runFailureReason(status) {
    const errors = (status?.logs || []).filter(line => /\[ERROR\]|\bFATAL\b|\bSTOP\s+1\b/i.test(String(line)));
    const fromLog = errors.length ? String(errors[errors.length - 1]).replace(/^\s*\[ERROR\]\s*/i, '').trim() : '';
    const reason = String(status?.failure_reason || status?.error || fromLog || '请查看运行日志排查原因').trim();
    return reason.length > 280 ? `${reason.slice(0,277)}…` : reason;
}

function runStepSummary(status) {
    const english = window.StudioI18n?.locale?.() === 'en-US';
    const current = Number.isFinite(status?.current_step) ? status.current_step.toLocaleString() : (english ? 'Unknown' : '未知');
    const total = Number.isFinite(status?.total_steps) ? status.total_steps.toLocaleString() : (english ? 'Unknown' : '未知');
    const rate = Number.isFinite(status?.steps_per_second) ? `${fmt(status.steps_per_second,1)} ${english ? 'steps/s' : '步/秒'}` : (english ? 'Speed unknown' : '速度未知');
    if (status?.phase === 'merging') {
        const solverMode = status.performance?.solver_mode || (english ? 'Serial solver' : '串行求解器');
        return english
            ? `Steps: ${current} / ${total} · Merging outputs · ${solverMode}`
            : `步数: ${current} / ${total} · 正在合并输出 · ${solverMode}`;
    }
    if (status?.phase === 'compressing') {
        const solverMode = status.performance?.solver_mode || (english ? 'Serial solver' : '串行求解器');
        return english
            ? `Steps: ${current} / ${total} · Post-processing: compressing and verifying outputs · ${solverMode}`
            : `步数: ${current} / ${total} · 求解后处理中：压缩并逐值核验输出 · ${solverMode}`;
    }
    if (!english) {
        return `步数: ${current} / ${total} · ${rate} · ${status.performance?.solver_mode || '串行求解器'}`;
    }
    const solver = {
        '预编译串行求解器': 'Precompiled serial solver',
        '串行求解器': 'Serial solver'
    }[status.performance?.solver_mode] || status.performance?.solver_mode || 'Serial solver';
    return `Steps: ${current} / ${total} · ${rate} · ${solver}`;
}

function formatRemainingTime(seconds, english = window.StudioI18n?.locale?.() === 'en-US') {
    const value = Number(seconds);
    if (!Number.isFinite(value) || value <= 0) return '-';
    const totalMinutes = Math.ceil(value / 60);
    const hours = Math.floor(totalMinutes / 60);
    const minutes = totalMinutes % 60;
    return english ? `${hours}h ${minutes}m` : `${hours}小时${minutes}分钟`;
}

function runEtaText(status, english = window.StudioI18n?.locale?.() === 'en-US') {
    if (status?.status === 'running' && ['merging', 'compressing'].includes(status?.phase)) {
        if (status.phase === 'compressing') return english ? 'Post-processing: compressing and verifying' : '求解已结束，压缩及核验后处理中';
        return english ? 'Merging outputs' : '合并输出中';
    }
    if (status?.status === 'running' && !Number.isFinite(status?.eta_seconds) && !Number.isFinite(status?.eta_minutes)) {
        return english ? 'Unknown' : '未知';
    }
    return formatRemainingTime(status?.eta_seconds ?? (Number(status?.eta_minutes) * 60), english);
}

function updateRunNotificationStatus(status) {
    if (!status || !['running','completed','failed','stopped'].includes(status.status)) return;
    const center = $('run-notification-center');
    const summary = $('run-notification-status');
    if (!center || !summary) return;
    const english = window.StudioI18n?.locale?.() === 'en-US';
    const labels = english
        ? {running:'Running',completed:'Completed',failed:'Failed',stopped:'Stopped'}
        : {running:'运行中',completed:'已完成',failed:'失败',stopped:'已停止'};
    const progress = Number.isFinite(status.progress) ? `${fmt(status.progress,1)}%` : '';
    const parts = [labels[status.status], progress].filter(Boolean);
    if (status.status === 'running') {
        if (['merging', 'compressing'].includes(status.phase)) {
            parts.push(runEtaText(status, english));
        } else {
            const etaSeconds = Number(status.eta_seconds ?? (Number(status.eta_minutes) * 60));
            parts.push(Number.isFinite(etaSeconds) && etaSeconds > 0
                ? (english ? `ETA ${formatRemainingTime(etaSeconds, true)}` : `预计剩余 ${formatRemainingTime(etaSeconds, false)}`)
                : (english ? 'ETA updating' : '预计剩余时间更新中'));
        }
    } else if (status.status === 'failed') {
        const reason = runFailureReason(status);
        parts.push(english ? `Failure reason: ${reason}` : `失败原因：${reason}`);
    }
    summary.textContent = parts.join(' · ');
    summary.dataset.status = status.status;
    const enableButton = $('run-notification-enable');
    if (enableButton) enableButton.hidden = !('Notification' in window) || Notification.permission !== 'default';
    center.hidden = false;
}

async function enableRunNotifications() {
    if (!('Notification' in window)) {
        toast('当前环境不支持桌面通知，运行状态仍会显示在本页。', 'info');
        return;
    }
    if (Notification.permission !== 'default') return;
    try {
        const permission = await Notification.requestPermission();
        if (permission === 'granted') {
            $('run-notification-enable').hidden = true;
            toast('已启用运行通知', 'info');
        } else {
            toast('未启用桌面通知，运行状态仍会显示在本页。', 'info');
        }
    } catch (error) {
        console.warn('Notification permission request failed:', error);
        toast('无法启用桌面通知，运行状态仍会显示在本页。', 'info');
    }
}

function clearRunNotifications() {
    $('run-notification-list')?.replaceChildren();
    const status = $('run-notification-status');
    if (status && !state.runPollTimer) {
        status.textContent = '';
        $('run-notification-center').hidden = true;
    }
}

function notifyUser(title, body, kind='info') {
    // Persistent in-app fallback is independent of WebView/browser permission.
    appendRunNotificationFallback(title, body, kind);
    toast(`${title}: ${body}`, 'info');
    if ('Notification' in window && Notification.permission === 'granted') {
        try { new Notification(title, { body, icon: '/static/favicon.ico' }); } catch (e) {}
    }
}

function renderFabmRepairSummary(summary) {
    const node = $('run-repair-summary');
    if (!node) return;
    if (!summary || summary.state !== 'available' || !summary.counts) {
        node.textContent = summary?.state === 'running'
            ? 'FABM 状态检查汇总：运行中，完成后读取本次运行日志。'
            : 'FABM 状态检查汇总：未提供（本次日志没有完整且可识别的三项统计）。';
        return;
    }
    const {interior, surface, bottom} = summary.counts;
    const total = interior + surface + bottom;
    const counts = `内部/表层/底层 ${interior}/${surface}/${bottom} 次`;
    node.textContent = total > 0
        ? `FABM 状态检查汇总：${counts}。计数表示检查事件，不是变量、网格单元或实际修改总数；存在状态越界并由求解器裁剪，建议检查完整日志与结果。单凭计数不能判定结果错误或物理无效。`
        : `FABM 状态检查汇总：${counts}。计数表示检查事件，不是变量、网格单元或实际修改总数。`;
}

function renderRunMonitor(status) {
    const box = $('run-monitor-metrics');
    const alertBox = $('run-monitor-alert');
    const ranks = $('run-monitor-ranks');
    if (!box || !alertBox || !ranks) return;
    const m = status?.monitor || {};
    const rate = Number.isFinite(m.steps_per_second) ? m.steps_per_second.toFixed(1) : '—';
    const days = Number.isFinite(m.sim_days_per_wall_hour) ? m.sim_days_per_wall_hour.toFixed(2) : '—';
    const cpu = Number.isFinite(m.cpu_percent) ? `${m.cpu_percent.toFixed(0)}%` : '—';
    const eta = runEtaText(status);
    const modeLabel = {serial:'串行', threads:'OpenMP', mpi:'MPI', hybrid:'MPI×OpenMP', auto:'自动'}[m.parallel_mode] || '';
    const chosen = Number.isFinite(m.requested_cores)
        ? `使用核数 ${m.requested_cores}${modeLabel ? `（${modeLabel}）` : ''}`
        : '';
    const fallback = m.fallback_serial ? ' · 已回退串行' : '';
    const hotstart = m.hotstart_disabled ? ' · 已关闭热启动' : '';
    box.textContent = `${chosen ? chosen + ' · ' : ''}实际 MPI ${m.mpi_ranks || 1} 进程 · OpenMP ${m.omp_threads ?? '—'} 线程 · ${rate} 步/秒 · ${days} 模拟天/墙钟小时 · 剩余 ${eta} · CPU ${cpu}${fallback}${hotstart}`;
    if (m.level === 'error' || m.level === 'warn') {
        alertBox.hidden = false;
        alertBox.className = `run-monitor-alert ${m.level}`;
        alertBox.textContent = m.message || (m.level === 'error' ? '求解器报错' : '步进停滞');
    } else {
        alertBox.hidden = true;
        alertBox.textContent = '';
    }
    const consoles = Array.isArray(m.consoles) ? m.consoles : [];
    const openId = ranks.querySelector('details[open]')?.dataset.id;
    ranks.replaceChildren();
    consoles.forEach((item, index) => {
        const details = document.createElement('details');
        details.dataset.id = item.id;
        if (item.id === openId || (!openId && index === 0)) details.open = true;
        if (item.error) details.className = 'error';
        const summary = document.createElement('summary');
        summary.textContent = `${item.label || item.id}${item.error ? ' · 有报错' : ''}`;
        const pre = document.createElement('pre');
        pre.textContent = (item.lines || []).join('\n') || '（暂无输出）';
        details.append(summary, pre);
        ranks.appendChild(details);
    });
}

async function pollRunStatus() {
    if (state.runPollBusy) return;
    state.runPollBusy = true;
    try {
    const s = await api(`/api/run/status?log_limit=${state.runLogLimit || 80}`);
    if (state.resultFilesStatus !== s.status) { state.resultFilesStatus = s.status; window.loadResultFiles?.(); }
    if (s.error || !s.status) return;
    renderFabmRepairSummary(s.fabm_repair_summary);
    if (s.status === 'running') {
        $('btn-start-run').disabled = true;
        $('btn-stop-run').disabled = false;
        if (!state.runPollTimer) state.runPollTimer = setInterval(pollRunStatus, 2000);
    }
    $('run-stat-status').textContent = {idle:'空闲',running:'运行中',completed:'已完成',failed:'失败',stopped:'已停止'}[s.status] || s.status;
    const hasProgress = Number.isFinite(s.progress);
    const progressText = hasProgress ? `${fmt(s.progress,1)}%` : (window.StudioI18n?.locale?.() === 'en-US' ? 'Unknown' : '未知');
    $('run-stat-progress').textContent = progressText;
    $('run-stat-elapsed').textContent = fmt(s.elapsed,0) + 's';
    $('run-stat-eta').textContent = runEtaText(s);
    $('run-progress-fill').style.width = (hasProgress ? s.progress : 0) + '%';
    const progressBar = $('run-progress-fill').parentElement;
    progressBar.setAttribute('aria-label', window.StudioI18n?.locale?.() === 'en-US' ? 'Run progress' : '运行进度');
    if (hasProgress) {
        progressBar.setAttribute('aria-valuenow', String(Math.round(s.progress)));
        progressBar.setAttribute('aria-valuetext', progressText);
    } else {
        progressBar.removeAttribute('aria-valuenow');
        progressBar.setAttribute('aria-valuetext', progressText);
    }
    $('run-percent').textContent = progressText;
    $('run-step-info').textContent = runStepSummary(s);
    // Status display
    const dot = document.querySelector('#run-status-display .status-dot');
    dot.className = 'status-dot ' + s.status;
    const runLabels = window.StudioI18n?.locale?.() === 'en-US'
        ? {idle:'Idle',running:'Running',completed:'Completed',failed:'Failed',stopped:'Stopped'}
        : {idle:'空闲',running:'运行中',completed:'已完成',failed:'失败',stopped:'已停止'};
    const runLabel = runLabels[s.status] || s.status;
    document.querySelector('#run-status-display').childNodes[1].textContent = runLabel;
    $('run-console-state').textContent = runLabel;
    $('run-console-case').textContent = s.log_case_directory || s.case_directory || (state.activeCasePath || state.activeCase || window.StudioI18n?.t?.('尚未加载案例') || '尚未加载案例');
    updateRunPhysicsDisplay(s);
    renderRunMonitor(s);
    const loadMoreButton = $('run-console-load-more');
    loadMoreButton.disabled = (s.total_logs || 0) <= (state.runLogLimit || 80) || (state.runLogLimit || 80) >= 5000;
    const logStatus = $('run-console-log-status');
    if ((state.runLogLimit || 80) > 80) {
        const message = loadMoreButton.disabled
            ? '已加载最近 {count} 行日志；已到当前保留范围上限。完整日志仍保存在 model_run.log。'
            : '已加载最近 {count} 行日志。';
        logStatus.textContent = window.StudioI18n?.t(message, {count: s.logs?.length || 0}) || message.replace('{count}', s.logs?.length || 0);
    }
    syncQgisStatusBar(runLabel);
    updateRunNotificationStatus(s);
    // ETA threshold notifications (fire once per threshold as ETA decreases past it)
    if (s.status === 'running' && Number.isFinite(s.eta_minutes) && s.eta_minutes > 0) {
        state.etaNotified ||= new Set();
        for (const threshold of [60, 15, 5]) {
            if (Number.isFinite(state.previousEtaMinutes) && state.previousEtaMinutes > threshold &&
                s.eta_minutes <= threshold && !state.etaNotified.has(threshold)) {
                state.etaNotified.add(threshold);
                const english = window.StudioI18n?.locale?.() === 'en-US';
                notifyUser(english ? '3DWET run update' : '3DWET 运行提醒', english
                    ? `Estimated ${fmt(s.eta_minutes,0)} min remaining (${threshold}-minute threshold)`
                    : `预计剩余 ${fmt(s.eta_minutes,0)} 分钟（${threshold}分钟阈值）`);
            }
        }
        state.previousEtaMinutes = s.eta_minutes;
    }
    // Logs
    const runLogCursor = state.runLogCursor ||= {lastLines: []};
    syncRunLogContext($('run-log'), s.run_identity, runLogCursor);
    appendRunLogLines($('run-log'), s.logs, runLogCursor);
    // Status flip notifications
    if (['completed','failed','stopped'].includes(s.status)) {
        clearInterval(state.runPollTimer);
        state.runPollTimer = null;
        $('btn-start-run').disabled = false;
        $('btn-stop-run').disabled = true;
        if (state.lastRunStatus !== s.status) {
            state.lastRunStatus = s.status;
            advanceOutputRevision();
            if (s.status === 'completed') {
                const english = window.StudioI18n?.locale?.() === 'en-US';
                const completedSteps = Number.isFinite(s.current_step) ? s.current_step.toLocaleString() : (english ? 'unknown' : '未知');
                notifyUser(english ? 'Model run completed' : '模型运行完成', english
                    ? `${completedSteps} steps · total task time ${fmt(s.elapsed/60,1)} min, including post-processing`
                    : `共 ${completedSteps} 步，任务总用时 ${fmt(s.elapsed/60,1)} 分钟（含结果检查与后处理）`, 'completed');
                loadVariables();
                loadDashboardSummary();
            } else if (s.status === 'failed') {
                const english = window.StudioI18n?.locale?.() === 'en-US';
                notifyUser(english ? 'Model run failed' : '模型运行失败', `${english ? 'Failure reason: ' : '失败原因：'}${runFailureReason(s)}`, 'failed');
            } else if (s.status === 'stopped') {
                const english = window.StudioI18n?.locale?.() === 'en-US';
                const stoppedStep = Number.isFinite(s.current_step) ? s.current_step.toLocaleString() : (english ? 'unknown' : '未知');
                notifyUser(english ? 'Model run stopped' : '模型已停止', english
                    ? `Stopped at step ${stoppedStep}`
                    : `运行至第 ${stoppedStep} 步`, 'stopped');
            }
        }
    }
    } finally { state.runPollBusy = false; }
}

function updateRunPhysicsDisplay(status) {
    const english = window.StudioI18n?.locale?.() === 'en-US';
    const labels = {
        mpi: english ? 'Waiting for a complete point diagnostic from the MPI solver; older or unsupported runs may not emit one.'
            : '等待 MPI 求解器提供完整点位诊断；旧版或不支持的运行可能不会输出。',
        unsupported: english ? 'Point diagnostics are unsupported for this MPI configuration.'
            : '此 MPI 配置不支持点位诊断。',
        waiting: english ? 'Waiting for a validated solver diagnostic record.'
            : '等待求解器提供可验证的物理诊断记录。',
        unavailable: english ? 'The representative wet cell is currently unavailable.'
            : '当前代表性湿格点不可用。',
        available: english ? 'Representative central wet T-grid cell'
            : '代表性中心湿格点（T 网格）',
    };
    state.runPhysicsDiagnosticState = window.RunPhysicsDiagnostics?.updateRunPhysicsDiagnostic(
        status, state.runPhysicsDiagnosticState) || null;
    const diagnostic = state.runPhysicsDiagnosticState?.diagnostic;
    const mpi = String(status.performance?.solver_mode || '').startsWith('MPI');
    const message = $('run-physics-status');
    const point = $('run-physics-point');
    const z = $('run-physics-z');
    const h = $('run-physics-h');
    const d = $('run-physics-d');
    const velocityElements = {
        status: $('run-physics-velocity-status'),
        surfaceLayer: $('run-physics-velocity-surface-k'),
        surfaceX: $('run-physics-velocity-surface-x'),
        surfaceY: $('run-physics-velocity-surface-y'),
        surfaceSpeed: $('run-physics-velocity-surface-speed'),
        bottomLayer: $('run-physics-velocity-bottom-k'),
        bottomX: $('run-physics-velocity-bottom-x'),
        bottomY: $('run-physics-velocity-bottom-y'),
        bottomSpeed: $('run-physics-velocity-bottom-speed'),
    };
    window.RunPhysicsDiagnostics?.renderRunPhysicsVelocity(diagnostic, velocityElements, english);
    if (diagnostic?.status === 'available') {
        message.textContent = labels.available;
        point.textContent = window.RunPhysicsDiagnostics?.formatRunPhysicsPoint(
            diagnostic, {mpi, english}) || '—';
        z.textContent = Number(diagnostic.z_surface_m).toFixed(3);
        h.textContent = Number(diagnostic.H_static_m).toFixed(3);
        d.textContent = Number(diagnostic.D_total_m).toFixed(3);
        return;
    }
    point.textContent = '—';
    z.textContent = h.textContent = d.textContent = '—';
    if (diagnostic?.status === 'unsupported') message.textContent = `${labels.unsupported} (${diagnostic.reason})`;
    else if (mpi) message.textContent = labels.mpi;
    else if (diagnostic?.status === 'unavailable') message.textContent = `${labels.unavailable} (${diagnostic.reason})`;
    else message.textContent = labels.waiting;
}

// ── Variables ─────────────────────────────────────────────────────────
const resultInventoryRequests = new Map();
function resultInventoryCaseKey() {
    return `${String(state.activeCasePath || state.activeCase || '')}\n${String(state.caseRevision ?? '')}`;
}
async function fetchResultInventory() {
    const key = resultInventoryCaseKey();
    let promise = resultInventoryRequests.get(key);
    if (!promise) {
        let request;
        request = api('/api/results/variables').finally(() => {
            if (resultInventoryRequests.get(key) === request) resultInventoryRequests.delete(key);
        });
        promise = request;
        resultInventoryRequests.set(key, promise);
    }
    const result = await promise;
    return key === resultInventoryCaseKey() ? result : {error: '案例已切换'};
}

function clearResultInventory() {
    state.variables2d=[];state.variables3d=[];state.timeLabels2d=[];state.timeLabels3d=[];
    state.resultTimeAxes={};state.timesteps2d=0;state.timesteps3d=0;
    state.resultGeometry=null;
    state.serverCaseGeneration=null;
    state.viz2dRequest=(state.viz2dRequest||0)+1;state.viz2dAbort?.abort();
    state.viz3dRequest=(state.viz3dRequest||0)+1;
    ['viz2d-var','viz3d-var','viz3d-iso-var','viz3d-avg-var','ts-var','cal-var-select','cal-data-var']
        .forEach(id=>$(id)?.replaceChildren());
    window.ScientificWorkspace?.empty?.('viz2d','请先加载案例');
    window.ScientificWorkspace?.empty?.('viz3d','请先加载案例');
    window.ScientificWorkspace?.updateTimeControls?.('viz2d');
    window.ScientificWorkspace?.updateTimeControls?.('viz3d');
}

async function restoreCurrentCase() {
    const revision=state.caseRevision;
    const data=await api('/api/case/current');
    if(revision!==state.caseRevision || state.activeCasePath)return false;
    if(data.error)return false;
    if(!data.case_path){clearResultInventory();return false;}
    state.caseRevision=(state.caseRevision||0)+1;
    state.activeCase=data.case_name;state.activeCasePath=data.case_path;
    state.caseType=data.case_type || null;state.storageReadOnly=!!data.storage_read_only;
    state.serverCaseGeneration=Number.isInteger(data.case_generation)?data.case_generation:null;
    document.body.classList.toggle('readonly-gotm', !!data.read_only);
    document.body.classList.toggle('gotm-single-column', String(data.case_type || '').startsWith('gotm_'));
    window.ObservationManager?.setColumnVariableInventory(data.native_column_variables || null);
    const nativePeriod=Array.isArray(data.native_time_range)&&data.native_time_range.length===2
        ? ` · ${data.native_time_range[0]} — ${data.native_time_range[1]}` : '';
    renderProxyCaseStatus(data);
    const calibrationDesc=$('calibration-page-desc');
    if(calibrationDesc)calibrationDesc.textContent=data.read_only
        ?'当前打开的是只读 GOTM 原生输出。请使用下方官方观测文件入口进行代表水柱比较；GETM 点位、运行和观测写入功能已停用。'
        :'设置率定点位，输入实测数据，对比模拟-实测结果';
    $('footer-status').textContent=`案例: ${data.case_name}`;syncQgisStatusBar();
    refreshCaseStatistics(data);
    if (data.has_results) {
        loadDashboardSummary();
    } else {
        const empty = '<div class="empty-state"><div class="icon"><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-dashboard"></use></svg></div>当前案例尚无输出结果。运行模型后显示</div>';
        $('dashboard-vars').innerHTML = empty;
        loadDashboardStaticPreview();
    }
    loadCorePlan();
    loadMpiRunCapabilities();
    return true;
}

async function loadVariables() {
    const revision=state.caseRevision,promise=loadResultVariables();
    state.variablesPending={revision,promise};
    try{return await promise;}
    finally{if(state.variablesPending?.promise===promise)state.variablesPending=null;}
}

async function loadResultVariables() {
    const request = state.variablesRequest = (state.variablesRequest || 0) + 1;
    const revision = state.caseRevision;
    const v = await fetchResultInventory();
    if (request !== state.variablesRequest || revision !== state.caseRevision) return;
    if (v.error) return;
    if (!v.error) {
        state.variables2d = v['2d'] || [];
        state.variables3d = v['3d'] || [];
        state.resultGeometry = {twoD:v.geometry_2d||null,threeD:v.geometry_3d||null};
        // 时间轴真实日期：2d/3d 文件按 step_2d/step_3d 抽帧，间隔不一定是 1 天，
        // 所以必须按帧查日历日期，不能直接把滑块索引当成“第 N 天”。
        state.timeLabels2d = v['time_labels_2d'] || [];
        state.timeLabels3d = v['time_labels_3d'] || [];
        state.resultTimeAxes = v.time_axes || {};
        state.timesteps2d = Number(v.timesteps_2d || 0);
        state.timesteps3d = Number(v.timesteps_3d || 0);
        // The dashboard count describes availability; each view is bounded by
        // the selected variable source after its options have been populated.
        const nt = Math.max(state.timesteps2d,state.timesteps3d,
            ...[...state.variables3d,...state.variables2d].map(item=>Number(item.ntimesteps)||0));
        $('stat-timesteps').textContent = nt || '-';
        $('stat-timesteps').title = `2D: ${state.timesteps2d} 帧 · 3D: ${state.timesteps3d} 帧；各变量按实际输出来源显示时刻`;
    }
    // Populate all variable selects
    const allVars = [...state.variables3d, ...state.variables2d];
    const unique = {};
    allVars.forEach(v => { if (!unique[v.name]) unique[v.name] = v; });
    const varList = prioritizeResultVariables(Object.values(unique));
    const verticalDefaultVariable=varList.find(v=>v.name==='temp'&&hasVerticalResultDimension(v))
        || varList.find(hasVerticalResultDimension);
    const defaultVariable=verticalDefaultVariable || varList.find(v=>v.name==='temp') || varList[0];
    ['viz2d-var','viz3d-var','viz3d-iso-var','viz3d-avg-var','ts-var','cal-var-select','cal-data-var'].forEach(id => {
        const sel = $(id);
        if (!sel) return;
        const selected = sel.value;
        const requiresVertical=verticalResultSelectIds.has(id);
        sel.innerHTML = '';
        varList.forEach(v => {
            const opt = document.createElement('option');
            opt.value = v.name;
            const hasLev = hasVerticalResultDimension(v);
            opt.disabled=requiresVertical && !hasLev;
            const priority=resultVariablePriority(v);
            opt.textContent = `${priority===2?'【按需】':'【默认优先】'} ${resultVariableOptionLabel(v,requiresVertical)}`;
            if(opt.disabled)opt.title=resultVariableOptionLabel(v,true);
            opt.dataset.i18nSkip='true';
            sel.appendChild(opt);
        });
        if(requiresVertical){
            if(varList.some(v=>v.name===selected&&hasVerticalResultDimension(v)))sel.value=selected;
            else if(verticalDefaultVariable)sel.value=verticalDefaultVariable.name;
            else sel.value='';
        }else if (varList.some(v => v.name === selected)) sel.value = selected;
        else if(defaultVariable)sel.value=defaultVariable.name;
    });
    for(const id of ['viz2d-var','viz3d-iso-var'])updateResultVariableSearch(id,true);
    window.VariableGuide?.setVariables(varList);
    populateCalibrationVariables();
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
    window.ScientificWorkspace?.updateTimeControls?.('viz2d');
    window.ScientificWorkspace?.updateTimeControls?.('viz3d');
}

function updateResultVariableSearch(selectId,resetOptions=false) {
    const select=$(selectId),search=$(selectId+'-search'),status=$(selectId+'-search-status');
    if(!select || !search || !status)return;
    const variables=[...state.variables3d,...state.variables2d],byName=new Map(variables.map(item=>[item.name,item]));
    if(resetOptions || !Array.isArray(select._resultVariableOptions))select._resultVariableOptions=Array.from(select.options||[]);
    const allOptions=select._resultVariableOptions,query=String(search.value||'').trim().toLocaleLowerCase();
    const searchText=(zh,en)=>window.StudioI18n?.scientificText?.(zh,en)||zh;
    const matched=[];
    for(const option of allOptions){
        const item=byName.get(option.value),text=[option.value,option.textContent,item?.name,item?.units,item?.long_name,item?.long_name_en,item?.meaning,item?.meaning_en,item?.zh_name,item?.en_name,item?.category,item?.category_en,
            item?.ndim===4?'垂向层 sigma vertical layer':'无垂向层 no vertical layer'].filter(Boolean).join(' ').toLocaleLowerCase();
        if(!query || text.includes(query))matched.push(option);
    }
    search.hidden=variables.length<60;
    const current=allOptions.find(option=>option.value===select.value),visible=query?matched.slice():allOptions.slice();
    if(query && current && !visible.includes(current))visible.unshift(current);
    // The browser and accessibility tree see only actual matches, while the native select keeps full keyboard behavior.
    if(visible.length!==select.options.length || visible.some((option,index)=>select.options[index]!==option))select.replaceChildren(...visible);
    if(current)select.value=current.value;
    status.textContent=query
        ? matched.length?searchText(`已筛选 ${matched.length} 项；按 Tab 进入列表，再用上下键选择。当前选择保持不变。`,`Filtered to ${matched.length} items. Press Tab to focus the list, then use the arrow keys. The current selection is unchanged.`):searchText('没有匹配项；当前选择仍保留，清空搜索可恢复全部。','No matches. The current selection is retained; clear the search to restore all options.')
        : (selectId==='viz3d-iso-var' && allOptions.some(option=>option.disabled)
            ? searchText('无垂向层的变量已禁用；3D 需要真实垂向层（4D），请切换到 2D 查看。','Variables without vertical layers are disabled; 3D requires a real vertical dimension (4D). Use 2D to view them.')
            : variables.length>=60?searchText(`共 ${allOptions.length} 项；可搜索中文名称、英文名称、代码或单位。`,`${allOptions.length} items. Search by Chinese or English name, code, or unit; press Tab to move to the list and use the arrow keys.`):'');
    if(!search.dataset.bound){search.addEventListener('input',()=>updateResultVariableSearch(selectId));search.dataset.bound='true';}
}

// ── Dashboard ─────────────────────────────────────────────────────────
async function loadDashboardSummary() {
    const request = state.dashboardSummaryRequest = (state.dashboardSummaryRequest || 0) + 1;
    const revision = state.caseRevision;
    const casePath = state.activeCasePath;
    const container = $('dashboard-vars');
    const heatmaps = $('dashboard-mini-heatmaps');
    const loading = '<div class="empty-state"><div class="icon"><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-clock"></use></svg></div>正在读取当前案例结果…</div>';
    container.innerHTML = loading;
    if (heatmaps) heatmaps.innerHTML = loading;
    const summary = await api('/api/dashboard/summary');
    if (request !== state.dashboardSummaryRequest || revision !== state.caseRevision
        || casePath !== state.activeCasePath) return;
    if (summary.error) {
        const message = `<div class="empty-state"><div class="icon"><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-info"></use></svg></div>${escapeHtml(summary.error)}</div>`;
        container.innerHTML = message;
        if (heatmaps) heatmaps.innerHTML = message;
        // A results directory can exist without containing any model output.
        // In that state the overview still has useful, clearly labelled static bathymetry.
        if (/没有输出文件|no output files?/i.test(String(summary.error))) await loadDashboardStaticPreview();
        return;
    }
    const entries = Object.entries(summary)
        .map(([name,value],index)=>({name,value,index,priority:resultVariablePriority({...value,name})}))
        .sort((a,b)=>a.priority-b.priority||a.index-b.index).slice(0,12)
        .map(({name,value})=>[name,value]);
    if (!entries.length) {
        const message = '<div class="empty-state"><div class="icon"><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-info"></use></svg></div>当前输出中没有可汇总的关键变量</div>';
        container.innerHTML = message;
        if (heatmaps) heatmaps.innerHTML = message;
        return;
    }
    container.innerHTML = `<div class="grid-2">` + entries.map(([k,v]) => `
        <div style="padding:10px;background:var(--bg-tertiary);border-radius:6px;">
            <div data-i18n-skip="true" style="font-size:12px;color:var(--text-secondary);">${escapeHtml(resultLabel(v,k))}</div>
            <div style="font-size:18px;font-weight:600;margin-top:2px;">${fmt(v.mean,3)} <span style="font-size:11px;color:var(--text-muted);">${v.units||''}</span></div>
            <div style="font-size:10px;color:var(--text-muted);">范围: ${fmt(v.min,3)} ~ ${fmt(v.max,3)}</div>
        </div>`).join('') + '</div>';
    // Also load mini-heatmaps
    loadDashboardMiniHeatmaps();
}

async function loadDashboardStaticPreview() {
    const container = $('dashboard-mini-heatmaps');
    if (!container || !state.activeCasePath) return;
    const request = state.dashboardStaticRequest = (state.dashboardStaticRequest || 0) + 1;
    const revision = state.caseRevision, casePath = state.activeCasePath;
    const geometry = await getScientificGeometry();
    if (request !== state.dashboardStaticRequest || revision !== state.caseRevision || casePath !== state.activeCasePath) return;
    const depth = geometry?.depth;
    if (!Array.isArray(depth) || !depth.length || !depth[0]?.length) {
        const message = window.StudioI18n?.scientificText('当前案例没有可用水深预览。模型未运行。','No bathymetry preview is available for this case. Model not run.')
            || '当前案例没有可用水深预览。模型未运行。';
        container.classList.add('empty-state');
        container.innerHTML = `<div class="empty-state">${escapeHtml(message)}</div>`;
        return;
    }
    const label = window.StudioI18n?.scientificText('静态水深预览 · 模型未运行','Static depth preview · model not run')
        || '静态水深预览 · 模型未运行';
    const validated = window.ScientificHeatmap?.validateBoundary?.(geometry.authoritative_boundary, {
        wetMask: geometry.wetMask, dryMask: geometry.dry_mask, xc: geometry.xc, yc: geometry.yc,
        coordinateMode: geometry.coordinate_mode, rows: depth.length, cols: depth[0].length
    });
    const outline = validated
        ? (window.StudioI18n?.scientificText(`显示轮廓：${validated.source}与湿干掩膜一致（仅用于显示裁切；地理/科学真实性未验证）`,`Display outline: ${validated.source} agrees with the wet/dry mask (display clipping only; geographic/scientific validity unverified)`) || `显示轮廓：${validated.source}与湿干掩膜一致（仅用于显示裁切；地理/科学真实性未验证）`)
        : (window.StudioI18n?.scientificText('显示轮廓：湿格边缘代理；无有效保存边界','Display outline: wet-cell edge proxy; no valid saved boundary') || '显示轮廓：湿格边缘代理；无有效保存边界');
    container.classList.remove('empty-state');
    container.innerHTML = `<article class="workbench-heatmap-card dashboard-static-preview" data-preview-state="static" data-boundary-source="${validated ? 'authoritative' : 'wet-mask-proxy'}">
        <div class="workbench-heatmap-title">${escapeHtml(label)}</div>
        <canvas id="dashboard-static-bathymetry" class="workbench-heatmap" width="960" height="520" role="img" aria-label="${escapeAttr(label)}"></canvas>
        <div class="workbench-heatmap-range">${escapeHtml(outline)} · ${escapeHtml(window.StudioI18n?.scientificText('水深 (m)','Depth (m)') || '水深 (m)')}</div>
        <div class="workbench-heatmap-range">${escapeHtml(window.StudioI18n?.scientificText('静态 bathymetry.nc；未运行模型，非模拟输出。','Static bathymetry.nc; model has not run; this is not simulation output.') || '静态 bathymetry.nc；未运行模型，非模拟输出。')}</div>
    </article>`;
    const canvas = $('dashboard-static-bathymetry');
    if (!canvas) return;
    const wetDepth = depth.map(row => row.map(value => Number.isFinite(value) && value > 0 ? value : null));
    const vmax = Math.max(0, ...wetDepth.flat().filter(Number.isFinite));
    window.ScientificHeatmap?.draw(canvas, wetDepth, { min: 0, max: vmax, wetMask: geometry.wetMask,
        dryMask: geometry.dry_mask, xc: geometry.xc, yc: geometry.yc,
        coordinateMode: geometry.coordinate_mode, boundary: geometry.authoritative_boundary });
}

async function loadDashboardMiniHeatmaps() {
    const container = $('dashboard-mini-heatmaps');
    if (!container) return;
    const variableSelect = $('dashboard-variable-select');
    const request = state.dashboardHeatmapRequest = (state.dashboardHeatmapRequest || 0) + 1;
    const revision = state.caseRevision;
    const casePath = state.activeCasePath;
    container.innerHTML = '<div class="empty-state"><div class="icon"><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-clock"></use></svg></div>正在读取当前案例空间分布…</div>';
    const isCurrent = () => request === state.dashboardHeatmapRequest
        && revision === state.caseRevision && casePath === state.activeCasePath;
    const data = await api('/api/results/state_vars_surface');
    if (!isCurrent()) return;
    if (data.error) { container.innerHTML = `<div class="empty-state"><div class="icon"><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-info"></use></svg></div>${escapeHtml(data.error)}</div>`; return; }
    const entries = Object.entries(data);
    if (!entries.length) { container.innerHTML = '<div class="empty-state">无变量数据</div>'; return; }
    container.classList.remove('empty-state');
    const names = new Set(entries.map(([name]) => name));
    let selected = names.has(variableSelect?.value) ? variableSelect.value : entries[0][0];
    if (variableSelect) {
        variableSelect.replaceChildren(...entries.map(([name, info]) => {
            const item = document.createElement('option');
            item.value = name;
            item.textContent = `${resultLabel(info,name)}${info.units ? ` · ${info.units}` : ''}`;
            return item;
        }));
        variableSelect.value = selected;
        variableSelect.disabled = entries.length < 2;
    }
    const render = () => {
        const primaryLabel = window.StudioI18n?.scientificText('主视图','Main view') || '主视图';
        let html = '<div class="workbench-heatmap-grid">';
        for (const [vname, info] of entries) {
            const canvasId = `mini-heat-${vname.replace(/[^a-zA-Z0-9_]/g, '_')}`;
            const label = resultLabel(info,vname);
            html += `<article class="workbench-heatmap-card" data-dashboard-variable="${escapeAttr(vname)}" data-dashboard-primary="${String(vname===selected)}">
                <div data-i18n-skip="true" class="workbench-heatmap-title">${escapeHtml(label)}${vname===selected?` · ${escapeHtml(primaryLabel)}`:''}</div>
                <canvas id="${canvasId}" class="workbench-heatmap" width="480" height="300" role="img" aria-label="${escapeAttr(label)} 空间分布"></canvas>
                <div class="workbench-heatmap-range">${fmt(info.min,3)} ~ ${fmt(info.max,3)} ${escapeHtml(info.units||'')} · 均值 ${fmt(info.mean,3)}</div>
            </article>`;
        }
        html += '</div>';
        container.innerHTML = html;
        for (const [vname, info] of entries) {
            const canvasId = `mini-heat-${vname.replace(/[^a-zA-Z0-9_]/g, '_')}`;
            drawHeatmap(canvasId, info.data, info.min, info.max);
        }
    };
    render();
    if (variableSelect) variableSelect.onchange = () => {
        if (!names.has(variableSelect.value) || variableSelect.value === selected) return;
        selected = variableSelect.value;
        render();
    };
}

// ── 2D Visualization ──────────────────────────────────────────────────
async function getScientificGeometry() {
    const revision = state.caseRevision;
    if (state.scientificGeometryRevision === revision && state.scientificGeometry) return state.scientificGeometry;
    if (state.scientificGeometryPending?.revision === revision) return state.scientificGeometryPending.promise;
    const promise = api('/api/geo/grid?display=scientific').then(data => {
        if (revision !== state.caseRevision || !data || data.error) return null;
        state.scientificGeometryRevision = revision;
        state.scientificGeometry = data;
        const shape=data.shape,gridStatus=typeof $==='function'?$('qgis-status-grid'):null;
        if(gridStatus && shape?.length===2 && shape.every(n=>Number.isInteger(n)&&n>0))gridStatus.textContent=`${shape[1]} × ${shape[0]}`;
        return data;
    }).catch(() => null).finally(() => {
        // An older case's completion must not remove its replacement request.
        if (state.scientificGeometryPending?.promise === promise) state.scientificGeometryPending = null;
    });
    state.scientificGeometryPending = {revision, promise};
    return promise;
}

async function initViz2d() {
    if(state.currentCasePending)await state.currentCasePending;
    if(!state.activeCasePath){clearResultInventory();return;}
    state.scientificGeometry = null;
    state.scientificGeometryPending = null;
    const revision=state.caseRevision;
    if (!state.variables2d.length && !state.variables3d.length) await loadVariables();
    while(state.variablesPending && state.variablesPending.revision===revision)await state.variablesPending.promise;
    if(revision!==state.caseRevision)return;
    const singleColumn = state.resultGeometry?.threeD?.single_column === true;
    const singleColumnMessage = $('viz2d-single-column-message');
    const twoDMain = document.querySelector('#page-viz2d .sw-main');
    if(singleColumnMessage){singleColumnMessage.hidden=!singleColumn;singleColumnMessage.style.display=singleColumn?'block':'';}
    if(twoDMain){twoDMain.hidden=singleColumn;twoDMain.style.display=singleColumn?'none':'';}
    if(singleColumn){window.ScientificWorkspace?.activate('viz2d');return;}
    const changed = window.ScientificWorkspace?.activate('viz2d');
    if ($('viz2d-var').options.length) {
        const levels=$('viz2d-level'),name=$('viz2d-var').value;
        const metadata=window.ScientificWorkspace?.variableMetadata?.(name)
            || [...state.variables3d,...state.variables2d].find(v=>v.name===name);
        const hasLayers=metadata?.ndim===4 || (Array.isArray(metadata?.dims)&&metadata.dims.includes('sigma'))
            || (metadata?.ndim==null && state.variables3d.some(v=>v.name===name));
        const nlev=hasLayers?(Number.isInteger(metadata?.nlev)&&metadata.nlev>0?metadata.nlev:state.nlev || 11):1;
        const sameSelection=levels?.dataset.variable===name
            && levels.dataset.caseRevision===String(revision ?? '')
            && levels.dataset.casePath===String(state.activeCasePath || state.activeCase || '');
        if (changed || !levels?.options.length || !sameSelection || levels.dataset.nlev!==String(nlev)
                || levels.dataset.hasLayers!==String(hasLayers))await onViz2dVarChange(sameSelection);
        else await updateViz2d();
    }
}

async function updateViz2d() {
    const request = state.viz2dRequest = (state.viz2dRequest || 0) + 1;
    const revision = state.caseRevision;
    const outputRevision=state.outputRevision || 0;
    state.viz2dAbort?.abort();
    const controller = typeof AbortController === 'function' ? new AbortController() : null;
    state.viz2dAbort = controller;
    const current = () => request === state.viz2dRequest && revision === state.caseRevision
        && outputRevision === (state.outputRevision || 0);
    const geometryMatches = (geometry, field) => {
        const rows = field?.length, cols = field?.[0]?.length;
        return Array.isArray(field) && rows > 0 && cols > 0 &&
            field.every(row => Array.isArray(row) && row.length === cols) &&
            geometry?.shape?.[0] === rows && geometry?.shape?.[1] === cols &&
            Array.isArray(geometry.wetMask) && geometry.wetMask.length === rows &&
            geometry.wetMask.every(row => Array.isArray(row) && row.length === cols);
    };
    const varName = $('viz2d-var').value;
    window.ScientificWorkspace?.syncFrom('viz2d');
    window.ScientificWorkspace?.loading('viz2d');
    const timestep = Number($('viz2d-time').value);
    const perfClock=()=>window.performance?.now?.() ?? Date.now();
    const perf=window.PlaybackPerformance;
    const perfTicket=perf?.begin('viz2d',timestep,$('viz2d-speed')?.value,window.ScientificWorkspace?.isPlaying?.('viz2d'));
    const level = Number($('viz2d-level').value);
    const dateLabel = window.ScientificWorkspace?.dateLabel?.('viz2d',timestep,varName)
        ?? ModelDates.format((state.timeLabels2d || state.timeLabels)?.[timestep] || null);
    $('viz2d-time-label').textContent = dateLabel ? `${window.StudioI18n?.locale().startsWith('zh')===false?'Frame '+timestep:'第 '+timestep+' 帧'} · ${dateLabel}` : `${timestep}`;
    // 占位变量：无模型结果时显示湖盆水深（来自 bathymetry.nc）
    if (varName === '__bathy__') {
        const g = window.ScientificHeatmap ? await getScientificGeometry() : await api('/api/geo/grid');
        if (!current()) return;
        if (!g || g.error || (window.ScientificHeatmap && !geometryMatches(g,g.depth))) {
            const message = g?.error || '湖盆几何不可用或湿掩膜形状不匹配';
            window.ScientificWorkspace?.failure('viz2d',message);toast(message,'error');return;
        }
        let vmax = 0;
        for (const row of g.depth) for (const v of row) if (v != null && v > vmax) vmax = v;
        const wetDepth = g.depth.map(row=>row.map(v=>v > 0 ? v : null));
        $('viz2d-canvas')._resultField = wetDepth;
        $('viz2d-canvas')._scientificMetadata = g;
        const range = window.ScientificStyle?.resolve({caseKey:state.activeCasePath || state.activeCase,variable:varName,min:0,max:vmax}) || {min:0,max:vmax};
        $('viz2d-canvas')._scientificRange = range;
        drawHeatmap('viz2d-canvas', wetDepth, range.min, range.max);
        $('viz2d-canvas')._resultVariable = varName;
        $('viz2d-min').textContent = '0';
        $('viz2d-max').textContent = fmt(vmax, 4);
        const validatedBoundary=window.ScientificHeatmap?.validateBoundary?.(g.authoritative_boundary,{
            wetMask:g.wetMask,dryMask:g.dry_mask,xc:g.xc,yc:g.yc,coordinateMode:g.coordinate_mode,
            rows:wetDepth.length,cols:wetDepth[0]?.length||0});
        const outline=validatedBoundary
            ? (window.StudioI18n?.scientificText(`边界：${validatedBoundary.source}与湿干掩膜一致（仅用于显示裁切；地理/科学真实性未验证）`,`Boundary: ${validatedBoundary.source} agrees with the wet/dry mask (display clipping only; geographic/scientific validity unverified)`)||`边界：${validatedBoundary.source}与湿干掩膜一致（仅用于显示裁切；地理/科学真实性未验证）`)
            : (window.StudioI18n?.scientificText('边界：湿格边缘代理（未验证）','Boundary: wet-cell edge proxy (unverified)')||'边界：湿格边缘代理（未验证）');
        $('viz2d-info').textContent = `${window.StudioI18n?.scientificText('变量：水深（静态地形 bathymetry.nc；模型未运行）','Variable: depth (static bathymetry.nc; model not run)')||'变量：水深（静态地形 bathymetry.nc；模型未运行）'} | ${outline} | ${wetDepth.length}×${wetDepth[0]?.length || 0}`;
        drawColorbar('viz2d-colorbar', range.min, range.max, '湖盆水深', 'm');
        window.ScientificWorkspace?.publish('viz2d',{variable:varName,label:'湖盆水深',units:'m',min:0,max:vmax,range,field:wetDepth,date:'地形预览',level:null});
        setViz2dBoundarySummary(outline);
        return;
    }
    const resultUrl = `/api/results/2d?var=${encodeURIComponent(varName)}&time=${timestep}&level=${level}&include_bathymetry=0`;
    const prefetch2d=window.Viz2DPlaybackPrefetch;
    const selection={case:state.activeCasePath || state.activeCase || '',casePath:state.activeCasePath || null,
        serverCaseGeneration:state.serverCaseGeneration,
        rangeStart:Number($('viz2d-play-start')?.value),rangeEnd:Number($('viz2d-play-end')?.value),
        revision,outputRevision,variable:varName,level};
    const fetchResult=url=>api(url,{signal:url===resultUrl?controller?.signal:undefined});
    const fetchBatch=({urls,identity:batchIdentity})=>api('/api/results/2d_batch',{method:'POST',body:{
        var:varName,times:urls.map(url=>Number(new URL(url,window.location.href).searchParams.get('time'))),
        level,aggregation:'layer',include_bathymetry:false,
        expected_case_path:batchIdentity.casePath,
        expected_case_generation:batchIdentity.serverCaseGeneration,
    }});
    const refreshCase=async()=>{
        const refreshed=await api('/api/case/current');
        const normalizePath=value=>String(value||'').replace(/\\/g,'/').replace(/\/+$/,'').toLocaleLowerCase();
        if(current() && refreshed?.case_path &&
            normalizePath(refreshed.case_path)===normalizePath(selection.casePath) &&
            Number.isInteger(refreshed.case_generation))
            state.serverCaseGeneration=refreshed.case_generation;
        return refreshed;
    };
    const data = prefetch2d
        ? await prefetch2d.fetchCurrent({url:resultUrl,identity:selection,
            isPlaying:()=>window.ScientificWorkspace?.isPlaying?.('viz2d'),
            isCurrent:()=>current() && $('viz2d-var')?.value===varName && Number($('viz2d-level')?.value)===level,
            endFrame:Number($('viz2d-play-end')?.value),fetchResult,fetchBatch,refreshCase})
        : await api(resultUrl,{signal:controller?.signal});
    if (!current()) return;
    if(data?._clientTiming){perf?.stage(perfTicket,'request',data._clientTiming.requestMs);perf?.stage(perfTicket,'decode',data._clientTiming.decodeMs);}
    if (data.aborted) { if(current())window.ScientificWorkspace?.failure('viz2d','请求已取消，请重新加载当前帧'); return; }
    if (data.error) { window.ScientificWorkspace?.failure('viz2d',data.error); toast(data.error, 'error'); return; }
    let geometryStartedAt=perfClock();
    if (window.ScientificHeatmap) {
        const geometry = await getScientificGeometry();
        if (!current()) return;
        perf?.stage(perfTicket,'geometry',perfClock()-geometryStartedAt);
        if (!geometryMatches(geometry,data.data)) {
            const message = '湖盆几何不可用或湿掩膜与结果网格形状不匹配';
            window.ScientificWorkspace?.failure('viz2d',message);toast(message,'error');return;
        }
        $('viz2d-canvas')._scientificMetadata = geometry;
    }
    $('viz2d-canvas')._resultField = data.data;
    const assembleStartedAt=perfClock();
    window.VariableGuide?.updateValues('viz2d-var', data);
    const range = window.ScientificStyle?.resolve({caseKey:state.activeCasePath || state.activeCase,variable:varName,min:data.min,max:data.max}) || {min:data.min,max:data.max};
    $('viz2d-canvas')._scientificRange = range;
    perf?.stage(perfTicket,'assemble',perfClock()-assembleStartedAt);
    const drawStartedAt=perfClock();
    drawHeatmap('viz2d-canvas', data.data, range.min, range.max);
    $('viz2d-canvas')._resultVariable = varName;
    $('viz2d-min').textContent = fmt(data.min,4);
    $('viz2d-max').textContent = fmt(data.max,4);
    const canvasMetadata=$('viz2d-canvas')._scientificMetadata;
    const validatedBoundary=window.ScientificHeatmap?.validateBoundary?.(canvasMetadata?.authoritative_boundary,{
        wetMask:canvasMetadata?.wetMask,dryMask:canvasMetadata?.dry_mask,xc:canvasMetadata?.xc,yc:canvasMetadata?.yc,
        coordinateMode:canvasMetadata?.coordinate_mode,rows:data.data.length,cols:data.data[0]?.length||0});
    const outline=validatedBoundary
        ? (window.StudioI18n?.scientificText(`边界：${validatedBoundary.source}与湿干掩膜一致（仅用于显示裁切；地理/科学真实性未验证）`,`Boundary: ${validatedBoundary.source} agrees with the wet/dry mask (display clipping only; geographic/scientific validity unverified)`)||`边界：${validatedBoundary.source}与湿干掩膜一致（仅用于显示裁切；地理/科学真实性未验证）`)
        : (window.StudioI18n?.scientificText('边界：湿格边缘代理（未验证）','Boundary: wet-cell edge proxy (unverified)')||'边界：湿格边缘代理（未验证）');
    const contrast=data.layer_contrast;
    const contrastText=contrast
        ? ` | 底层k=${contrast.bottom_index}均值 ${fmt(contrast.bottom_mean,4)} · 表层k=${contrast.surface_index}均值 ${fmt(contrast.surface_mean,4)} · |表-底|均值 ${fmt(contrast.mean_abs_diff,4)} · 最大 ${fmt(contrast.max_abs_diff,4)}${contrast.well_mixed?'（垂向差异很小）':''}`
        : (data.level_applies===false ? ' | 该变量没有垂向层，切换层不会改变数值和色标' : '');
    $('viz2d-info').textContent = `${window.StudioI18n?.scientificText('变量','Variable')||'变量'}: ${resultLabel(data,varName)} (${varName}) | ${outline} | ${window.StudioI18n?.scientificText('时步','Frame')||'时步'}: ${timestep}${dateLabel ? ' (' + dateLabel + ')' : ''} | ${window.StudioI18n?.scientificText('均值','Mean')||'均值'}: ${fmt(data.mean,4)} | ${window.StudioI18n?.scientificText('形状','Shape')||'形状'}: ${data.shape?.join('×')}${contrastText}`;
    drawColorbar('viz2d-colorbar', range.min, range.max, resultLabel(data,varName), data.units);
    perf?.stage(perfTicket,'draw',perfClock()-drawStartedAt);
    window.ScientificWorkspace?.publish('viz2d',{variable:varName,label:resultLabel(data,varName),units:data.units,min:data.min,max:data.max,range,field:data.data,date:dateLabel,time:timestep,level});
    setViz2dBoundarySummary(outline,`${resultLabel(data,varName)} (${data.units||''})`);
    perf?.finish(perfTicket);
    // Overlay polygon vertices if any
    if (state.viz2dPolygon && state.viz2dPolygon.length) drawViz2dPolygonOverlay();
}

function setViz2dBoundarySummary(outline, baseLabel='湖盆水深 · m · 地形预览') {
    const summary=$('viz2d-summary');
    const base=baseLabel==='湖盆水深 · m · 地形预览'
        ? (window.StudioI18n?.scientificText(baseLabel,'Basin depth · m · terrain preview')||baseLabel)
        : baseLabel;
    if(summary)summary.textContent=`${base} · ${outline}`;
}

// Variable change handler: populate layer dropdown based on variable dimension
async function onViz2dVarChange(preserveLayer=false) {
    const varName = $('viz2d-var').value;
    // Determine if 3D variable by checking variables3d list
    const metadata = window.ScientificWorkspace?.variableMetadata?.(varName)
        || [...state.variables3d,...state.variables2d].find(v=>v.name===varName);
    const is3d = metadata?.ndim===4 || (Array.isArray(metadata?.dims)&&metadata.dims.includes('sigma'))
        || (metadata?.ndim==null && state.variables3d.some(v=>v.name===varName));
    const levelSel = $('viz2d-level');
    const previous=levelSel.value;
    levelSel.innerHTML = '';
    levelSel.dataset.variable=varName;
    levelSel.dataset.caseRevision=String(state.caseRevision ?? '');
    levelSel.dataset.casePath=String(state.activeCasePath || state.activeCase || '');
    levelSel.dataset.hasLayers=String(is3d);
    const nlev=is3d?(Number.isInteger(metadata?.nlev)&&metadata.nlev>0?metadata.nlev:state.nlev || 11):1;
    levelSel.dataset.nlev=String(nlev);
    if (is3d) {
        // GETM sigma: index 0=底, N-1=面. Default to surface (last).
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
    if(preserveLayer && Array.from(levelSel.options).some(option=>String(option.value)===previous))levelSel.value=previous;
    levelSel.disabled=!is3d;
    levelSel.title=is3d?'':'这个变量没有垂向层，切换层不会改变数值或色标';
    await updateViz2d();
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
    if (canvas._scientificGeometry) {
        const cell = canvas._scientificGeometry.cellAt(x,y);
        return cell ? {...cell,x,y} : null;
    }
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
        const value=canvas._resultField?.[cell.j]?.[cell.i];
        const wet = canvas._scientificMetadata?.wetMask?.[cell.j]?.[cell.i];
        const detail=typeof value==='number' && Number.isFinite(value) ? window.VariableGuide?.valueText(canvas._resultVariable,value) : wet===true ? '水域：此变量无有效值' : wet===false ? '陆地' : '无有效值（湿掩膜不可用）';
        const coord = `i=${cell.i}, j=${cell.j} · ${detail || ''}`;
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
            populateCalibrationVariables();
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
    const center = (i,j) => canvas._scientificGeometry?.center(i,j) || {x:(i+0.5)*cellW,y:(j+0.5)*cellH};
    ctx.strokeStyle = '#fbbf24';
    ctx.lineWidth = 2*(canvas._scientificPixelRatio || 1);
    ctx.beginPath();
    state.viz2dPolygon.forEach(([i, j], idx) => {
        const {x,y} = center(i,j);
        if (idx === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    });
    if (state.viz2dPolygon.length >= 3) {
        const [i0, j0] = state.viz2dPolygon[0];
        const p0 = center(i0,j0); ctx.lineTo(p0.x,p0.y);
    }
    ctx.stroke();
    // Vertex markers
    ctx.fillStyle = '#fbbf24';
    state.viz2dPolygon.forEach(([i, j]) => {
        const {x,y} = center(i,j);
        ctx.beginPath();
        ctx.arc(x, y, 4*(canvas._scientificPixelRatio || 1), 0, Math.PI * 2);
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
    state.charts.cellTs = localizedChart(ctx, {
        type: 'line',
        data: {
            labels: ModelDates.chartLabels(times),
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

async function updateSpatialSection() {
    const axis = $('viz3d-section-axis').value;
    const index = Number($('viz3d-section-index').value);
    if (!Number.isInteger(index) || index < 0) { toast('剖面格点索引必须是非负整数', 'error'); return; }
    if (!window.renderSpatialSection) { toast('剖面渲染器未加载', 'error'); return; }
    const name=$('viz3d-iso-var').value, timestep=Number($('viz3d-iso-time').value);
    const main=window.ScientificWorkspace?.current('viz3d');
    const appState=typeof state==='undefined'?{}:state;
    const revision=appState.caseRevision;
    const request=appState.spatialSectionRequest=(appState.spatialSectionRequest || 0)+1;
    const matchesMain=main?.variable===name && main.time===timestep;
    const data = await window.renderSpatialSection(name,timestep,axis,index,{
        containerId:'viz3d-section-plot',caseKey:appState.activeCasePath || appState.activeCase,
        timeLabel:window.ScientificWorkspace?.dateLabel?.('viz3d',timestep,name)
            ?? (typeof ModelDates==='undefined'?'':ModelDates.format((appState.timeLabels3d || appState.timeLabels)?.[timestep] || null) || ''),
        ve:matchesMain && Number.isFinite(main.ve)?main.ve:Number($('viz3d-iso-ve')?.value || 0),
        range:matchesMain?main.range:undefined,
    });
    if(request!==appState.spatialSectionRequest || revision!==appState.caseRevision)return;
    if (data?.grid_shape) $('viz3d-section-index').max = data.grid_shape[axis === 'xz' ? 0 : 1] - 1;
    await window.set3DSectionIndicator?.(data?.grid_shape?axis:null,index,data);
}

// ── Calibration workflow helpers ──────────────────────────────────────
function refreshScientificTerms() {
    document.querySelectorAll('[data-scientific-zh]').forEach(element => {
        element.dataset.i18nSkip = 'true';
        element.textContent = calibrationScientificText(element.dataset.scientificZh, element.dataset.scientificEn);
    });
}

function toggleAutoCalMethod() {
    const abc = $('ac-method').value === 'pyabc';
    $('ac-abc-controls').style.display = abc ? '' : 'none';
    $('ac-iterations-hint').dataset.i18nSkip = 'true';
    $('ac-iterations-hint').textContent = abc
        ? calibrationScientificText('ABC-SMC: 迭代次数为种群代数，每代需接受指定规模的粒子；模型评估次数另受上限约束。', 'ABC-SMC: iterations count populations; each population accepts the requested number of particles. The simulation budget limits model evaluations.')
        : calibrationScientificText('SciPy: 优化器迭代次数；每次迭代可包含多次模型评估。', 'SciPy: optimizer iterations; each iteration may require multiple model evaluations.');
}

function calibrationScientificText(zh, en) {
    const text = window.StudioI18n?.scientificText(zh, en) || `${zh} / ${en}`;
    if (!state.scientificTerms) state.scientificTerms = new Map();
    state.scientificTerms.set(text,{zh,en});
    return text;
}

function selectedCalibrationVariables(id) {
    return Array.from($(id).selectedOptions, option => option.value);
}

function populateCalibrationVariables() {
    const variables = [...new Map([...(state.variables3d || []), ...(state.variables2d || [])].map(v => [v.name, v])).values()];
    // Temperature is usable before the first results file exists.
    if (!variables.length) variables.push({name:'temp', zh_name:'水温', en_name:'Water temperature'});
    for (const id of ['calib-add-vars', 'new-point-vars']) {
        const select = $(id);
        if (!select) continue;
        const selected = new Set(Array.from(select.selectedOptions, option => option.value));
        const available = variables.some(v => selected.has(v.name));
        const defaultName = variables.some(v => v.name === 'temp') ? 'temp' : variables[0].name;
        select.replaceChildren();
        variables.forEach(v => {
            const option = document.createElement('option');
            option.value = v.name;
            option.textContent = `${calibrationScientificText(v.zh_name || v.name, v.en_name || v.long_name_en || v.long_name || v.name)} · ${v.name} [${v.units || ''}]`;
            option.dataset.i18nSkip = 'true';
            option.selected = available ? selected.has(v.name) : v.name === defaultName;
            select.appendChild(option);
        });
    }
}

async function runCalModelAndCompare() {
    if (state.calManualRunning) return;
    const pid = $('cal-point-select').value, variable = $('cal-var-select').value;
    if (!state.activeCase || !pid || !variable) { toast('请先加载案例并选择点位和变量', 'error'); return; }
    const button = $('cal-run-compare');
    state.calManualRunning = true;
    button.disabled = true;
    try {
        const result = await api('/api/run/start', {method:'POST'});
        if (!result.success) throw new Error(result.error || '启动失败');
        $('cal-stats').textContent = calibrationScientificText('模型运行中，完成后对比', 'Running model; comparison follows completion');
        while (true) {
            const status = await api('/api/run/status');
            if (status.error) throw new Error(status.error);
            if (status.status === 'completed') break;
            if (status.status !== 'running') throw new Error(`模型未完成: ${status.status || 'unknown'}`);
            await new Promise(resolve => setTimeout(resolve, 2000));
        }
        await loadVariables();
        $('cal-point-select').value = pid;
        $('cal-var-select').value = variable;
        await updateCalComparison(pid, variable);
    } catch (error) {
        $('cal-stats').textContent = error.message;
        toast(error.message, 'error');
    } finally {
        state.calManualRunning = false;
        button.disabled = false;
    }
}

function renderAutoCalConvergence(history) {
    const canvas = $('ac-convergence-chart');
    if (!canvas) return;
    const valid = history.filter(row => Number.isFinite(row.objective));
    let best = Infinity;
    const bestValues = valid.map(row => best = Math.min(best, row.objective));
    if (state.charts.calConvergence) state.charts.calConvergence.destroy();
    state.charts.calConvergence = localizedChart(canvas.getContext('2d'), {
        type:'line', data:{labels:valid.map(row => row.iteration), datasets:[
            {label:calibrationScientificText('目标函数', 'Objective'), data:valid.map(row => row.objective), borderColor:'#3b82f6', pointRadius:2, tension:0},
            {label:calibrationScientificText('最优目标值', 'Best objective'), data:bestValues, borderColor:'#10b981', pointRadius:0, tension:0}
        ]}, options:{responsive:true, maintainAspectRatio:false,
            scales:{x:{title:{display:true,text:calibrationScientificText('模型评估次数','Model evaluations')}},y:{title:{display:true,text:calibrationScientificText('目标函数值','Objective value')}}}}
    });
}

function renderCalibrationWeights(points) {
    const container = $('ac-objective-weights');
    if (!container) return;
    const previous = new Map(Array.from(container.querySelectorAll('.ac-weight-row'), row => [
        `${row.dataset.pointId}:${row.dataset.variable}`,
        [row.querySelector('[data-role=weight]').value,row.querySelector('[data-role=scale]').value]
    ]));
    container.replaceChildren();
    points.forEach(point => (point.variables || []).forEach(variable => {
        const row = document.createElement('div');
        row.className = 'ac-weight-row form-row';
        row.dataset.pointId = point.id;
        row.dataset.variable = variable;
        const label = document.createElement('span');
        label.textContent = `${point.name} · ${variable}`;
        row.appendChild(label);
        const values = previous.get(`${point.id}:${variable}`) || ['',''];
        ['weight','scale'].forEach((role,index) => {
            const label = document.createElement('label');
            label.dataset.i18nSkip = 'true';
            label.textContent = calibrationScientificText(index ? '尺度' : '权重', index ? 'Scale' : 'Weight');
            const input = document.createElement('input');
            input.className = 'form-input'; input.type = 'number'; input.step = 'any';
            input.min = index ? '0.000000000001' : '0';
            input.placeholder = '1'; input.value = values[index]; input.dataset.role = role;
            input.style.width = '90px';
            label.appendChild(input); row.appendChild(label);
        });
        container.appendChild(row);
    }));
}

function collectCalibrationWeights(pointIds) {
    const container = $('ac-objective-weights');
    if (!container) return [];
    const rows = [];
    container.querySelectorAll('.ac-weight-row').forEach(row => {
        if (!pointIds.includes(row.dataset.pointId)) return;
        const weightText = row.querySelector('[data-role=weight]').value;
        const scaleText = row.querySelector('[data-role=scale]').value;
        if (weightText === '' && scaleText === '') return;
        const weight = weightText === '' ? 1 : Number(weightText), scale = scaleText === '' ? 1 : Number(scaleText);
        if (!Number.isFinite(weight) || weight < 0) throw new Error('权重 Weight 必须是非负有限数值');
        if (!Number.isFinite(scale) || scale <= 0) throw new Error('尺度 Scale 必须是正有限数值');
        rows.push({point_id:row.dataset.pointId, variable:row.dataset.variable, weight, scale});
    });
    return rows;
}

async function confirmAddCalibPoint() {
    const name = $('calib-add-name').value.trim();
    const i = Number($('calib-add-i').value);
    const j = Number($('calib-add-j').value);
    const vars = selectedCalibrationVariables('calib-add-vars');
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
    if (canvasId === 'viz2d-canvas' && window.ScientificHeatmap) {
        const meta = canvas._scientificMetadata;
        const sameShape = meta?.shape?.[0] === data?.length && meta?.shape?.[1] === data?.[0]?.length;
        const paint=(width,height)=>{
            let pixelRatio=1;
            if(Number.isFinite(width)&&width>0&&Number.isFinite(height)&&height>0){
                pixelRatio=Math.max(1,Math.min(4,Number(window.devicePixelRatio)||1));
                canvas.style.width=width+'px';canvas.style.height=height+'px';
                const w=Math.round(width*pixelRatio),h=Math.round(height*pixelRatio);
                if(canvas.width!==w)canvas.width=w;if(canvas.height!==h)canvas.height=h;
            }
            canvas._scientificPixelRatio=pixelRatio;
            canvas._scientificGeometry = window.ScientificHeatmap.draw(canvas,data,{
                min:vmin,max:vmax,palette:canvas._scientificRange?.palette || 'lake',style:canvas._scientificRange,pixelRatio,
                wetMask:sameShape ? meta.wetMask : undefined,
                xc:sameShape && meta.coordinate_mode==='projected' ? meta.xc : undefined,
                yc:sameShape && meta.coordinate_mode==='projected' ? meta.yc : undefined,
                dryMask:sameShape ? meta.dry_mask : undefined,
                coordinateMode:sameShape ? meta.coordinate_mode : undefined,
                boundary:sameShape ? meta.authoritative_boundary : undefined,
                showGrid:!!document.getElementById('viz2d-grid')?.checked,
            });
            state.viz2dCellSize = {rows:data.length,cols:data[0].length};
            setupViz2dCanvasHandlers();
            if(state.viz2dPolygon?.length)drawViz2dPolygonOverlay();
        };
        canvas._scientificResize=paint;
        const host=canvas.parentElement;
        const styles=host && typeof getComputedStyle==='function'?getComputedStyle(host):{};
        const inset=(a,b)=>(parseFloat(styles[a])||0)+(parseFloat(styles[b])||0);
        if(host?.classList?.contains('vc-canvas-viewport'))paint(host.clientWidth-inset('paddingLeft','paddingRight'),host.clientHeight-inset('paddingTop','paddingBottom'));
        else paint();
        return;
    }
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
            if (!Number.isFinite(v)) {
                ctx.fillStyle = '#f1f4f5';
            } else {
                const t = Math.max(0, Math.min(1, (v - vmin) / range));
                ctx.fillStyle = heatColor(t);
            }
            ctx.fillRect(i * cellW, j * cellH, cellW, cellH);
        }
    }
    // Trace the supplied wet mask exactly; interior cell edges stay hidden.
    const wet = (i,j) => i>=0 && i<cols && j>=0 && j<rows && Number.isFinite(data[j][i]);
    ctx.strokeStyle = '#54798b';
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let j=0;j<rows;j++) for (let i=0;i<cols;i++) {
        if (!wet(i,j)) continue;
        const x=i*cellW,y=j*cellH;
        if (!wet(i,j-1)) {ctx.moveTo(x,y);ctx.lineTo(x+cellW,y);}
        if (!wet(i,j+1)) {ctx.moveTo(x,y+cellH);ctx.lineTo(x+cellW,y+cellH);}
        if (!wet(i-1,j)) {ctx.moveTo(x,y);ctx.lineTo(x,y+cellH);}
        if (!wet(i+1,j)) {ctx.moveTo(x+cellW,y);ctx.lineTo(x+cellW,y+cellH);}
    }
    ctx.stroke();
    // Record cell layout + attach canvas click handlers (viz2d only)
    if (canvasId === 'viz2d-canvas') {
        state.viz2dCellSize = { rows, cols, w: cellW, h: cellH };
        setupViz2dCanvasHandlers();
    }
}

function heatColor(t) {
    if (window.ScientificStyle) return window.ScientificStyle.color(t);
    // Sequential lake blue; shared by the 2D cells and their quantitative legend.
    const stops = [[225,241,246],[179,217,232],[115,181,209],[57,139,179],[30,97,139],[18,58,95]];
    t = Math.max(0, Math.min(1, Number.isFinite(t) ? t : 0));
    const idx = t * (stops.length - 1);
    const lo = Math.floor(idx), hi = Math.min(lo+1, stops.length-1);
    const f = idx - lo;
    const r = Math.round(stops[lo][0] + (stops[hi][0]-stops[lo][0])*f);
    const g = Math.round(stops[lo][1] + (stops[hi][1]-stops[lo][1])*f);
    const b = Math.round(stops[lo][2] + (stops[hi][2]-stops[lo][2])*f);
    return `rgb(${r},${g},${b})`;
}

function drawColorbar(id, vmin, vmax, label = '', units = '') {
    const el = $(id);
    if (!el) return;
    const range=id==='viz2d-colorbar' ? $('viz2d-canvas')?._scientificRange : undefined;
    const scale=range?.colorscale || window.ScientificStyle?.colorscale?.(range || {palette:'lake'})
        || Array.from({length:11},(_,i)=>[i/10,heatColor(i/10)]);
    const stops=scale.map(([t,color])=>`${color} ${t*100}%`);
    el.style.background = `linear-gradient(to right, ${stops.join(',')})`;
    const select = $(id === 'viz2d-colorbar' ? 'viz2d-var' : 'viz3d-avg-var');
    const title = label || select?.selectedOptions?.[0]?.textContent || '数值';
    el.setAttribute('aria-label', `${title}${units ? ' ('+units+')' : ''}：${vmin} – ${vmax}`);
    el.classList.add('scientific-colorbar');
    // Construct text nodes rather than trusting model metadata as HTML.
    el.replaceChildren();
    const heading = document.createElement('span');
    heading.className = 'scientific-colorbar-title';
    heading.textContent = `${title}${units ? ' ('+units+')' : ''}`;
    el.appendChild(heading);
    const marks = window.ScientificStyle?.legendTicks?.(vmin,vmax,el.clientWidth || 200)
        || window.ScientificStyle?.ticks(vmin,vmax) || {values:Array.from({length:5},(_,i)=>vmin+(vmax-vmin)*i/4)};
    for (let i=0;i<marks.values.length;i++) {
        const tick = document.createElement('span');
        tick.className = 'scientific-colorbar-tick';
        if(marks.values.length>1)tick.dataset.edge=i===0?'start':i===marks.values.length-1?'end':'middle';
        tick.style.left = `${marks.values.length===1 ? 50 : i/(marks.values.length-1)*100}%`;
        const value = marks.values[i];
        tick.textContent = marks.labels?.[i] || (Number.isFinite(value) ? Number(value.toPrecision(4)).toString() : '—');
        el.appendChild(tick);
    }
}

// ── 3D Visualization ──────────────────────────────────────────────────
async function initViz3d() {
    if(state.currentCasePending)await state.currentCasePending;
    if(!state.activeCasePath){clearResultInventory();return;}
    const revision=state.caseRevision;
    const sectionReady=initScientificSectionDefault();
    if (!state.variables3d.length) await loadVariables();
    while(state.variablesPending && state.variablesPending.revision===revision)await state.variablesPending.promise;
    await sectionReady;
    if(revision!==state.caseRevision)return;
    window.ScientificWorkspace?.activate('viz3d');
    if($('viz3d-var')?.value)updateViz3d();
    if($('viz3d-avg-var')?.value)updateViz3dAvg();
    return updateViz3dIso();
}

async function initScientificSectionDefault() {
    const axis=$('viz3d-section-axis'),index=$('viz3d-section-index');
    const path=String(state.activeCasePath || state.activeCase || ''),revision=state.caseRevision;
    if(!axis || !index || !path || typeof getScientificGeometry!=='function')return;
    const key=JSON.stringify([path,revision ?? null]);
    if(state.scientificSectionDefaultKey===key)return;
    if(state.scientificSectionDefaultPending?.key===key){
        await state.scientificSectionDefaultPending.promise;
        return;
    }
    let finish;const pending=new Promise(resolve=>{finish=resolve;});
    state.scientificSectionDefaultPending={key,promise:pending};
    const initialAxis=axis.value,initialIndex=index.value;
    let edited=false,applied=false;const onEdit=()=>{edited=true;};
    for(const control of [axis,index])for(const event of ['input','change'])control.addEventListener(event,onEdit);
    try{
        const geometry=await getScientificGeometry(),mask=geometry?.wetMask;
        if(edited || revision!==state.caseRevision || path!==String(state.activeCasePath || state.activeCase || '')
                || axis.value!==initialAxis || index.value!==initialIndex)return;
        const rows=mask?.length,cols=mask?.[0]?.length;
        if(!Array.isArray(mask) || !rows || !cols || geometry?.shape?.[0]!==rows || geometry?.shape?.[1]!==cols
                || !mask.every(row=>Array.isArray(row)&&row.length===cols) || !['xz','yz'].includes(initialAxis))return;
        const count=initialAxis==='xz'?rows:cols,midpoint=(count-1)/2;
        let selected=-1,distance=Infinity;
        for(let k=0;k<count;k++){
            const wet=initialAxis==='xz'?mask[k].some(value=>value===true):mask.some(row=>row[k]===true);
            if(wet && Math.abs(k-midpoint)<distance){selected=k;distance=Math.abs(k-midpoint);}
        }
        if(selected>=0){index.value=String(selected);index.max=String(count-1);applied=true;}
    }catch{
        // The main result remains usable when the optional geometry lookup fails.
    }finally{
        for(const control of [axis,index])for(const event of ['input','change'])control.removeEventListener(event,onEdit);
        if(revision===state.caseRevision && path===String(state.activeCasePath || state.activeCase || '')
                && (applied || edited || axis.value!==initialAxis || index.value!==initialIndex))state.scientificSectionDefaultKey=key;
        if(state.scientificSectionDefaultPending?.promise===pending)state.scientificSectionDefaultPending=null;
        finish();
    }
}

async function updateViz3dIso() {
    const playbackRequest=state.viz3dPlaybackRequest=(state.viz3dPlaybackRequest||0)+1,playbackRevision=state.caseRevision;
    window.invalidateScientific3D?.();
    const varName = $('viz3d-iso-var')?.value;
    if (!varName) return;
    window.ScientificWorkspace?.syncFrom('viz3d');
    const timestep = Number($('viz3d-iso-time')?.value || 0);
    const options = {
        ve: Number($('viz3d-iso-ve')?.value || 0),
        opacity: Number($('viz3d-opacity')?.value || 1),
        meshMode: $('viz3d-mesh-mode')?.value || 'continuous',
        lineDensity: Number($('viz3d-line-density')?.value || 1),
        lineOpacity: Number($('viz3d-line-opacity')?.value ?? .3),
        showNetworkNodes: $('viz3d-mesh-nodes')?.checked === true,
        showLand: $('viz3d-show-land')?.checked !== false,
        caseKey: state.activeCasePath || state.activeCase || '',
        timeLabel: window.ScientificWorkspace?.dateLabel?.('viz3d',timestep,varName)
            ?? (ModelDates.format((state.timeLabels3d || state.timeLabels)?.[timestep] || null) || ''),
    };
    if(playbackRequest!==state.viz3dPlaybackRequest || playbackRevision!==state.caseRevision || varName!==$('viz3d-iso-var')?.value || timestep!==Number($('viz3d-iso-time')?.value||0))return;
    const timeLabel = document.getElementById('viz3d-iso-time-label');
    if (timeLabel) timeLabel.textContent = options.timeLabel || `帧 ${timestep}`;
    // 占位变量：无模型结果时显示湖盆 3D 地形
    if (varName === '__bathy__') {
        if (typeof renderBathymetry3D === 'function') await renderBathymetry3D(options);
        return;
    }
    const metadata=window.ScientificWorkspace?.variableMetadata?.(varName)
        || [...(state.variables3d || []),...(state.variables2d || [])].find(v=>v.name===varName);
    const renderSelect=$('viz3d-iso-render');
    let render = renderSelect?.value || 'waterbody';  // waterbody / isosurface / cloud / surface2d
    const renderHint=$('viz3d-iso-render-hint');
    // GETM D is water depth, not a tracer to lift onto a variable-height surface.
    // In waterbody mode it selects static basin terrain; explicit surface2d remains available.
    if(varName==='D' && render==='waterbody'){
        if(renderHint){renderHint.hidden=true;renderHint.textContent='';}
        if(typeof renderBathymetry3D==='function')await renderBathymetry3D(options);
        return;
    }
    if(metadata && !hasVerticalResultDimension(metadata)){
        const message=window.StudioI18n?.scientificText(
            '该变量没有真实垂向层，已切换到“变量高度表面”；表面高度由变量值决定，不代表真实水深或水面。',
            'This variable has no real vertical layers. Switched to variable-height surface; its height represents the variable value, not bathymetry or the water surface.'
        ) || '该变量没有真实垂向层，已切换到“变量高度表面”；表面高度由变量值决定，不代表真实水深或水面。';
        if(render!=='surface2d'){
            if(renderSelect)renderSelect.value='surface2d';
            toast(message,'info');
        }
        render='surface2d';
        if(renderHint){renderHint.hidden=false;renderHint.textContent=message;}
    }else if(renderHint){renderHint.hidden=true;renderHint.textContent='';}
    if(render==='waterbody' && $('viz3d-iso-overlay')?.checked===false){
        if(typeof renderBathymetry3D==='function')await renderBathymetry3D(options);
        return;
    }
    if(render!=='surface2d' && metadata?.ndim!=null && metadata.ndim!==4){
        const message=window.StudioI18n?.scientificText('该变量没有真实垂向层（4D），请选择变量高度表面或含垂向层的变量。','This variable has no real vertical dimension (4D). Select variable-height surface or a variable with vertical layers.')
            || '该变量没有真实垂向层（4D），请选择变量高度表面或含垂向层的变量。';
        window.invalidateScientific3D?.(message);
        window.ScientificWorkspace?.failure('viz3d',message);toast(message,'error');return;
    }
    if(Number.isInteger(metadata?.nlev)&&metadata.nlev>0){
        for(const id of ['viz3d-iso-layer','viz3d-iso-level']){
            const control=$(id);if(!control)continue;
            control.max=String(metadata.nlev-1);
            control.value=String(Math.max(id==='viz3d-iso-layer'?-1:0,Math.min(metadata.nlev-1,Number(control.value)||0)));
        }
    }
    const target = Number($('viz3d-iso-quality')?.value || 96);  // 每轴降采样格数（质量档）
    const level = Number($('viz3d-iso-level')?.value || 0);
    if (render === 'waterbody') {
        // 立体水体：湖底地形 + 逐层半透明分层面 + 四周剖面墙 + 垂向放大
        if (typeof render3DWaterBody === 'function') {
            await render3DWaterBody(varName, timestep, {
                ...options,
                target,
                level: Number($('viz3d-iso-layer')?.value ?? -1),   // -1 = 最上层
                stack: !!$('viz3d-iso-stack')?.checked,
                overlay: !!$('viz3d-iso-overlay')?.checked,
            });
        }
    } else if (render === 'cloud') {
        if (typeof render3DCloud === 'function') await render3DCloud(varName, timestep, target, options);
    } else if (render === 'isosurface') {
        if (typeof render3DSurface === 'function') await render3DSurface(varName, timestep, target, options);
    } else {
        if (typeof render2DAs3DSurface === 'function') await render2DAs3DSurface(varName, timestep, level, options);
    }
    const main=window.ScientificWorkspace?.current('viz3d');
    if(main?.variable===varName && main.time===timestep && document.querySelector?.('#page-viz3d .sw-section-analysis[open]')){
        if(window.ScientificWorkspace?.isPlaying?.('viz3d'))window.setSpatialSectionPlaybackStatus?.(timestep,options.timeLabel);
        else await updateSpatialSection();
    }
}

async function updateViz3d() {
    const request = state.profileRequest = (state.profileRequest || 0) + 1;
    const revision = state.caseRevision;
    const varName = $('viz3d-var').value;
    const i = Number($('viz3d-i').value), j = Number($('viz3d-j').value);
    const t = Number($('viz3d-time').value);
    const _lbl = document.getElementById('viz3d-time-label');
    const dateLabel=window.ScientificWorkspace?.dateLabel?.('viz3d',t,varName)
        ?? ModelDates.format((state.timeLabels3d || state.timeLabels)?.[t] || null);
    if (_lbl) _lbl.textContent = `${window.StudioI18n?.locale().startsWith('zh')===false?'Frame '+t:'第 '+t+' 帧'}${dateLabel?' · '+dateLabel:''}`;
    const data = await api(`/api/results/profile?var=${varName}&time=${t}&i=${i}&j=${j}`);
    if (request !== state.profileRequest || revision !== state.caseRevision) return;
    if (data.error) return;
    window.VariableGuide?.updateValues('viz3d-var', {data:data.profile,var_name:varName});
    if (state.charts.profile) state.charts.profile.destroy();
    const ctx = $('viz3d-profile-chart').getContext('2d');
    state.charts.profile = localizedChart(ctx, {
        type: 'line',
        data: { labels: data.sigma.map(s=>s.toFixed(2)), datasets: [{
            label: `${resultLabel(data,varName)} (${data.units||''})`,
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
    const request = state.depthMeanRequest = (state.depthMeanRequest || 0) + 1;
    const revision = state.caseRevision;
    const varName = $('viz3d-avg-var').value;
    const t = Number($('viz3d-avg-time').value);
    const data = await api(`/api/results/2d?var=${encodeURIComponent(varName)}&time=${t}&aggregation=depth_mean`);
    if (request !== state.depthMeanRequest || revision !== state.caseRevision) return;
    if (data.error) { toast(data.error, 'error'); return; }
    window.VariableGuide?.updateValues('viz3d-avg-var', data);
    drawHeatmap('viz3d-avg-canvas', data.data, data.min, data.max);
    drawColorbar('viz3d-colorbar', data.min, data.max, resultLabel(data,varName), data.units);
}

// ── Time Series ───────────────────────────────────────────────────────
async function constrainPointInputsToGrid(prefix) {
    try {
        if (state.currentCasePending) await state.currentCasePending;
    } catch (_) { return false; }
    const path = String(state.activeCasePath || state.activeCase || ''), revision = state.caseRevision;
    if (!path || typeof getScientificGeometry !== 'function') return false;
    const iInput = $(`${prefix}-i`), jInput = $(`${prefix}-j`);
    if (!iInput || !jInput) return false;
    let geometry;
    try { geometry = await getScientificGeometry(); } catch (_) { return false; }
    if (revision !== state.caseRevision || path !== String(state.activeCasePath || state.activeCase || '')) return false;
    const shape = geometry?.shape, rows = shape?.[0], cols = shape?.[1];
    if (!Array.isArray(shape) || shape.length !== 2
            || !Number.isInteger(rows) || rows < 1 || !Number.isInteger(cols) || cols < 1) return false;
    iInput.min = jInput.min = '0';
    iInput.max = String(cols - 1); jInput.max = String(rows - 1);
    iInput.step = jInput.step = '1';
    const clampIndex = (input, max) => {
        const value = Number(input.value), index = Number.isFinite(value) ? Math.trunc(value) : 0;
        input.value = String(Math.max(0, Math.min(max, index)));
    };
    clampIndex(iInput, cols - 1); clampIndex(jInput, rows - 1);
    return true;
}

async function initTimeseries() {
    if (!$('ts-var').options.length) await loadVariables();
    await constrainPointInputsToGrid('ts');
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
    const request = state.timeseriesRequest = (state.timeseriesRequest || 0) + 1;
    const revision = state.caseRevision;
    const varName = $('ts-var').value;
    const mode = $('ts-mode').value;
    const scope = mode === 'layer' ? $('ts-layer-scope').value : mode;
    if (scope === 'point') {
        await constrainPointInputsToGrid('ts');
        if (revision !== state.caseRevision) return;
    }
    let url = `/api/results/timeseries?var=${encodeURIComponent(varName)}`;
    if (scope === 'point') url += `&i=${$('ts-i').value}&j=${$('ts-j').value}`;
    else if (scope === 'region') url += `&region=${$('ts-region').value}`;
    else if (scope === 'lake') url += `&lake_avg=1`;
    if (mode === 'layer') url += `&per_layer=1`;
    const data = await api(url);
    if (request !== state.timeseriesRequest || revision !== state.caseRevision) return;
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
            data: { labels: ModelDates.chartLabels(data.times), datasets },
            options: { responsive: true, maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                plugins: { legend: { display: false },
                    title: { display: true, text: `${resultLabel(data,varName)} · 每一层 (${nlev} 层) @ ${label}`, color: '#ccc' } },
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
            data: { labels: ModelDates.chartLabels(data.times), datasets: [{
                label: `${resultLabel(data,varName)} @ ${label}`,
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
    state.charts.ts = localizedChart(ctx, chartCfg);
}

// ── Vertical Heatmap (垂向热图) ───────────────────────────────────────
// 用 Plotly heatmap 绘制「层 × 时间」热图：悬停可读数值、可框选缩放、可导出 PNG。
// 纵轴默认水面在顶部，自下而上为 sigma 由大到小（层号由高到低）。
let _vheatLast = null;        // 最近一次 per_layer 结果（供"时间序列"页复用）

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
    const nm = resultLabel(v,name);
    opt.dataset.i18nSkip='true';
    const hasLev = varHasLevel(v);
    opt.textContent = withName
        ? `${nm} (${name})${hasLev ? '' : ' ('+(window.StudioI18n?.t('无垂向层') || '无垂向层')+')'}`
        : `${nm} [${v.units || ''}]${hasLev ? '' : ' ('+(window.StudioI18n?.t('无垂向层') || '无垂向层')+')'}`;
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
    await constrainPointInputsToGrid('vheat');
    window.VariableGuide?.refresh('vheat-var');
    toggleVHeatScope();
}

function toggleVHeatScope() {
    const scope = $('vheat-scope')?.value || 'point';
    ['vheat-point-group', 'vheat-point-group2'].forEach(id => { const el = $(id); if (el) el.style.display = scope === 'point' ? 'block' : 'none'; });
    const rg = $('vheat-region-group'); if (rg) rg.style.display = scope === 'region' ? 'block' : 'none';
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
    if (scope === 'point') {
        const revision = state.caseRevision;
        await constrainPointInputsToGrid('vheat');
        if (revision !== state.caseRevision) return;
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
    const physicalDepth = axis === 'depth' ? _vheatBuildPhysicalCells(data) : null;
    if (physicalDepth && physicalDepth.error) {
        const m = $('vheat-meta');
        if (m) m.innerHTML = physicalDepth.error;
        toast(physicalDepth.error, 'error');
        return;
    }
    drawVerticalHeatmap('vheat-plotly', data, axis);
    const nlev = data.series.length;
    const ntime = data.times ? data.times.length : 0;
    const scopeLabel = scope === 'lake' ? '全湖平均' : scope === 'region' ? `区域 ${$('vheat-region').value}` : `点位 (${$('vheat-i').value},${$('vheat-j').value})`;
    const m = $('vheat-meta');
    if (m) m.innerHTML =
        `变量：<b>${resultLabel(data,varName)}</b><br>范围：${scopeLabel}<br>垂向层数：<b>${nlev}</b><br>时间采样：<b>${ntime}</b> 点（步长 ${data.tstride || '?'}）<br>单位：${data.units || ''}<br>纵轴：${axis === 'depth' ? `逐时真实深度 (m)，${escapeHtml(physicalDepth.source)}` : axis === 'level' ? '层号' : 'sigma 坐标'}<br>鼠标悬停查看数值，可框选缩放`;
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
 * Validate the strict physical-depth contract and build time-varying layer
 * cell bounds. Centers are positive-down meters, indexed [level][time].
 * Layer order may be top-down or bottom-up; this sorts geometrically while
 * retaining the original level index used by `series`.
 */
function _vheatBuildPhysicalCells(data) {
    const centers = data && data.layer_center_depth_m;
    const values = data && data.series;
    const nlev = Array.isArray(values) ? values.length : 0;
    const ntime = Array.isArray(data && data.times) ? data.times.length : 0;
    const source = data && data.layer_center_depth_source;
    const fail = error => ({ cells: [], depthMax: null, error });
    if (!nlev || !ntime || !Array.isArray(centers) || centers.length !== nlev || !String(source || '').trim())
        return fail('真实深度几何缺失：需要 layer_center_depth_m（层×时刻）及 layer_center_depth_source；无法用静态水深估算代替。');
    if (centers.some(row => !Array.isArray(row) || row.length !== ntime) || values.some(row => !Array.isArray(row) || row.length !== ntime))
        return fail('真实深度几何维度错误：layer_center_depth_m 和 series 必须都是 nlev × ntime。');
    const cells = [];
    let depthMax = 0;
    for (let t = 0; t < ntime; t++) {
        const hasData = values.some(row => row[t] !== null && row[t] !== undefined && Number.isFinite(Number(row[t])));
        if (!hasData) continue;
        const column = [];
        for (let k = 0; k < nlev; k++) {
            const value = values[k][t];
            const depth = centers[k][t];
            if (depth === null || depth === undefined || !Number.isFinite(Number(depth)) || Number(depth) <= 0)
                return fail(`真实深度几何在时刻 ${t + 1}、层 ${k + 1} 缺失或非法；无法确定该时刻的层厚。`);
            column.push({ levelIndex: k, center: Number(depth), value: value === null || value === undefined || !Number.isFinite(Number(value)) ? null : Number(value) });
        }
        if (!column.length) continue;
        if (column.length < 2) return fail(`时刻 ${t + 1} 可用真实层中心少于 2 个，无法确定层厚。`);
        column.sort((a, b) => a.center - b.center);
        for (let i = 1; i < column.length; i++) if (!(column[i].center > column[i - 1].center))
            return fail(`时刻 ${t + 1} 的真实层中心重复或非单调，无法确定层界面。`);
        for (let i = 0; i < column.length; i++) {
            const top = i === 0 ? Math.max(0, column[i].center - (column[i + 1].center - column[i].center) / 2)
                : (column[i - 1].center + column[i].center) / 2;
            const bottom = i === column.length - 1 ? column[i].center + (column[i].center - column[i - 1].center) / 2
                : (column[i].center + column[i + 1].center) / 2;
            if (column[i].value !== null) cells.push({ ...column[i], timeIndex: t, top, bottom });
            depthMax = Math.max(depthMax, bottom);
        }
    }
    if (!cells.length) return fail('没有有效的垂向数据值，无法生成深度热图。');
    return { cells, depthMax: depthMax || null, error: null, source: String(source).trim() };
}

function _vheatColorAt(value, min, max) {
    const stops = [[0, [0, 0, 128]], [.2, [0, 128, 255]], [.4, [0, 200, 150]], [.6, [255, 220, 0]], [.8, [255, 100, 0]], [1, [200, 0, 0]]];
    const x = max === min ? .5 : Math.max(0, Math.min(1, (value - min) / (max - min)));
    let i = 1; while (i < stops.length - 1 && x > stops[i][0]) i++;
    const a = stops[i - 1], b = stops[i], f = (x - a[0]) / (b[0] - a[0]);
    return `rgb(${a[1].map((v, k) => Math.round(v + (b[1][k] - v) * f)).join(',')})`;
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

    if (axisMode === 'depth') {
        const physical = _vheatBuildPhysicalCells(data);
        if (physical.error) {
            el.innerHTML = `<div style="padding:16px;color:#f87171">${physical.error}</div>`;
            return;
        }
        const values = physical.cells.map(cell => cell.value);
        const min = Math.min(...values), max = Math.max(...values);
        const times = data.times || [];
        const timeAxis = ModelDates.plotlyAxis(times);
        const tx = timeAxis.x;
        const xAt = i => timeAxis.axis.type === 'category' ? i : tx[i];
        const xBounds = i => {
            const x = xAt(i);
            if (tx.length === 1) return [x - .5, x + .5];
            return [i === 0 ? x - (xAt(1) - x) / 2 : (xAt(i - 1) + x) / 2,
                i === tx.length - 1 ? x + (x - xAt(i - 1)) / 2 : (x + xAt(i + 1)) / 2];
        };
        const traces = physical.cells.map(cell => {
            const [x0, x1] = xBounds(cell.timeIndex), color = _vheatColorAt(cell.value, min, max);
            const timeLabel = timeAxis.labels[cell.timeIndex];
            return { type: 'scatter', mode: 'lines', x: [x0, x1, x1, x0, x0], y: [cell.top, cell.top, cell.bottom, cell.bottom, cell.top],
                fill: 'toself', fillcolor: color, line: { color, width: 0.5 },
                customdata: Array(5).fill([cell.value, cell.center, timeLabel, cell.levelIndex]),
                hovertemplate: '%{customdata[2]}<br>实际深度中心: %{customdata[1]:.2f} m<br>层: %{customdata[3]}<br><b>%{customdata[0]}</b> ' + (data.units || '') + '<extra></extra>',
                showlegend: false, name: `层 ${cell.levelIndex}` };
        });
        traces.push({ type: 'scatter', mode: 'markers', x: [xAt(0)], y: [0], marker: { size: 0.1, color: [min], cmin: min, cmax: max === min ? min + 1 : max,
            colorscale: [[0, 'rgb(0,0,128)'], [.2, 'rgb(0,128,255)'], [.4, 'rgb(0,200,150)'], [.6, 'rgb(255,220,0)'], [.8, 'rgb(255,100,0)'], [1, 'rgb(200,0,0)']], showscale: true,
            colorbar: { title: { text: data.units || '' }, thickness: 14, len: .85 } }, hoverinfo: 'skip', showlegend: false });
        const layout = { paper_bgcolor: 'var(--bg-secondary)', plot_bgcolor: 'var(--bg-primary)', font: { family: 'Microsoft YaHei, sans-serif', size: 10, color: '#cbd5e1' },
            margin: { l: 62, r: 60, t: 26, b: 46 }, xaxis: { ...timeAxis.axis, title: { text: '年份 + 年内儒略日 (DOY)', font: { size: 11 } }, tickangle: -30, automargin: true, showgrid: false },
            yaxis: { title: { text: '真实深度 (m, 正值向下)' }, range: [physical.depthMax, 0], automargin: true, tickfont: { size: 9 } },
            meta: { layer_center_depth_source: physical.source } };
        Plotly.react(el, traces, layout, { responsive: true, displaylogo: false, toImageButtonOptions: { format: 'png', filename: `vheat_${data.var_name || 'profile'}` } });
        return;
    }

    // 纵轴标签：自上而下（层 nlev-1 → 层 0），水面在顶部
    const dfc = _vheatDepthFrac(data.layers || []);
    const yLabels = new Array(nlev);
    for (let r = 0; r < nlev; r++) {
        const k = nlev - 1 - r;
        if (axisMode === 'level') yLabels[r] = `层 ${k}`;
        else {
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
    const timeAxis = ModelDates.plotlyAxis(times);
    const trace = {
        type: 'heatmap',
        x: timeAxis.x,
        customdata: zRows.map(() => timeAxis.labels),
        y: yLabels,
        z: zRows,
        // 与 viz2d/drawHeatmap 一致的色阶
        colorscale: [
            [0, 'rgb(0,0,128)'], [0.2, 'rgb(0,128,255)'], [0.4, 'rgb(0,200,150)'],
            [0.6, 'rgb(255,220,0)'], [0.8, 'rgb(255,100,0)'], [1, 'rgb(200,0,0)']
        ],
        showscale: true,
        colorbar: { title: { text: data.units || '' }, thickness: 14, len: 0.85 },
        hovertemplate: '%{y}　%{customdata}<br><b>%{z}</b> ' + (data.units || '') + '<extra></extra>',
        xgap: 0.5, ygap: 0.5,
    };
    const layout = {
        paper_bgcolor: 'var(--bg-secondary)', plot_bgcolor: 'var(--bg-primary)',
        font: { family: 'Microsoft YaHei, sans-serif', size: 10, color: '#cbd5e1' },
        margin: { l: 62, r: 60, t: 26, b: 46 },
        xaxis: { ...timeAxis.axis, title: { text: '年份 + 年内儒略日 (DOY)', font: { size: 11 } }, tickangle: -30, automargin: true, showgrid: false },
        yaxis: { title: { text: axisMode === 'depth' ? '深度 (m)' : axisMode === 'level' ? '层号' : 'σ (sigma，顶=水面)' }, automargin: true, tickfont: { size: 9 } },
    };
    Plotly.react(el, [trace], layout, {
        responsive: true, displaylogo: false,
        toImageButtonOptions: { format: 'png', filename: `vheat_${data.var_name || 'profile'}` },
    });
}

// ── Calibration ───────────────────────────────────────────────────────
async function initCalibrate() {
    // The template includes a default temperature option before a case is
    // loaded, so option count cannot tell us whether result variables exist.
    if (state.activeCase && !state.variables3d.length && !state.variables2d.length) {
        await loadVariables();
    }
    await loadCalPoints();
}

async function loadCalPoints() {
    const points = await api('/api/calibration/points');
    if (!Array.isArray(points)) { toast(points.error || '无法加载率定点位', 'error'); return; }
    renderCalibrationWeights(points);
    const autoPoints = $('ac-points');
    if (autoPoints) {
        const selected = new Set(Array.from(autoPoints.selectedOptions, o => o.value));
        const initialized = autoPoints.dataset.initializedCase === String(state.activeCase);
        autoPoints.replaceChildren();
        points.forEach(p => {
            const option = document.createElement('option');
            option.value = p.id; option.textContent = `${p.name} (${p.i},${p.j})`;
            option.selected = initialized ? selected.has(p.id) : true;
            autoPoints.appendChild(option);
        });
        autoPoints.dataset.initializedCase = String(state.activeCase);
    }
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

function showAddPointModal() { populateCalibrationVariables(); showModal('modal-add-point'); }

async function addCalPoint() {
    const name = $('new-point-name').value || '未命名';
    const i = Number($('new-point-i').value), j = Number($('new-point-j').value);
    const vars = selectedCalibrationVariables('new-point-vars');
    if (!vars.length) { toast('请选择率定变量', 'error'); return; }
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
    try {
        if (!Array.isArray(values)) throw new Error('实测数据须为 JSON 数组');
        values = values.map(row => ({...row, time: ModelDates.toIso(row.time)}));
    } catch (error) { toast(error.message, 'error'); return; }
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

async function updateCalComparison(pointId, variable) {
    const pid = pointId || $('cal-point-select').value;
    const varName = variable || $('cal-var-select').value;
    if (!pid || !varName) return;
    const data = await api(`/api/calibration/comparison?point_id=${encodeURIComponent(pid)}&variable=${encodeURIComponent(varName)}`);
    if (data.error) { $('cal-stats').innerHTML = `<span style="color:var(--danger)">${data.error}</span>`; return; }
    state.calLastData = data; // cache for scatter modal
    const comparisonNotes = () => {
        const source = data.mass_basis_source ? `basis来源：${data.mass_basis_source}` : 'basis尚未由模型来源确认';
        const basis = data.mass_basis ? `物质基础：${data.mass_basis}` : '';
        const evidence = data.mass_basis_provenance?.basis_evidence || '';
        const mapping = data.mapping_note || '';
        const reasons = (data.diagnostics || []).reduce((counts,item)=>{
            const reason=String(item.reason||'unknown');counts[reason]=(counts[reason]||0)+1;return counts;
        },{});
        const diagnosis = Object.entries(reasons).map(([reason,count])=>`${reason} × ${count}`).join('；');
        return `<details class="form-hint"><summary>来源与配对诊断</summary><div>${[source,basis,evidence,mapping,diagnosis].filter(Boolean).map(escapeHtml).join('<br>')}</div></details>`;
    };
    if (state.charts.cal) state.charts.cal.destroy();
    const pairs = (Array.isArray(data.scatter_pairs) ? data.scatter_pairs : [])
        .map((pair, order) => {
            const parsed = ModelDates.parse(pair.time);
            return { pair, order, timestamp: parsed?.date?.getTime() };
        })
        .filter(item => Number.isFinite(item.timestamp) &&
            Number.isFinite(item.pair.sim) && Number.isFinite(item.pair.obs))
        .sort((a, b) => a.timestamp - b.timestamp || a.order - b.order)
        .map(item => item.pair);
    if (!pairs.length) {
        state.charts.cal = null;
        const count = (data.observed || []).length;
        $('cal-stats').innerHTML = `<div style="font-size:12px;color:var(--text-muted);"><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-warning"></use></svg> ${calibrationScientificText('无有效配对，无法绘制率定对比曲线','No valid pairs are available for the calibration comparison')}（${calibrationScientificText('实测','observations')} ${count}）</div>${comparisonNotes()}`;
        return;
    }
    const ctx = $('cal-chart').getContext('2d');
    // The native model values are [time][layer]. scatter_pairs contains the
    // scalar model values already interpolated at each observation's true
    // time and depth, so preserve each pair (including equal timestamps).
    const allTimes = pairs.map(pair => pair.time);
    const simSeries = pairs.map(pair => pair.sim);
    const obsSeries = pairs.map(pair => pair.obs);
    const varLabel = resultLabel(data.simulated, varName) || data.simulated?.long_name || varName;
    const units = data.simulated?.unit || data.simulated?.units || '';
    state.charts.cal = localizedChart(ctx, {
        type: 'line',
        data: { labels: ModelDates.chartLabels(allTimes), datasets: [
            { label:`${calibrationScientificText('模拟（配对时刻/深度）','Simulated at paired times/depths')} ${varName}`, data:simSeries, borderColor:'#3b82f6', backgroundColor:'transparent', tension:0.2, pointRadius:0, borderWidth:2, spanGaps:true },
            { label:`${calibrationScientificText('实测','Observed')} ${varName}`, data:obsSeries, borderColor:'#f59e0b', backgroundColor:'#f59e0b', pointBackgroundColor:'#f59e0b', pointBorderColor:'#9a5a00', pointBorderWidth:1.5, pointRadius:5, borderWidth:1.5, showLine:false },
        ]},
        options: { responsive:true, maintainAspectRatio:false,
            plugins:{ legend:{labels:{color:'#ccc'}},
                tooltip:{ callbacks:{ title:(ctx)=>ctx[0].label, label:(c)=>`${c.dataset.label}: ${c.parsed.y===null?'—':c.parsed.y.toFixed(4)} ${units}` } } },
            scales:{ x:{ticks:{color:'#999',maxTicksLimit:10,autoSkip:true},grid:{color:'#222'}},
                     y:{ticks:{color:'#999'},grid:{color:'#333'}, title:{display:true,text:varLabel + (units?` (${units})`:'')}} }
        }
    });
    // Compute metrics using paired data from backend
    if (typeof computeMetrics === 'function') {
        const simArr = pairs.map(p => p.sim);
        const obsArr = pairs.map(p => p.obs);
        const metrics = computeMetrics(obsArr, simArr);
        $('cal-stats').innerHTML = renderMetricsHTML(metrics) + comparisonNotes();
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
    const units = data.simulated?.unit || data.simulated?.units || '';
    showModal('modal-scatter');
    const basis = data.mass_basis ? ` | 物质基础: ${data.mass_basis}` : ' | 物质基础未确认';
    const basisSource = data.mass_basis_source ? ` | 来源: ${data.mass_basis_source}` : '';
    const mappingNote = data.mapping_note ? `<div class="form-hint">${escapeHtml(data.mapping_note)}</div>` : '';
    $('scatter-meta').innerHTML = `点位: <strong>${escapeHtml(pointName)}</strong> | 变量: <strong>${escapeHtml(varName)}</strong> | 配对数: <strong>${data.scatter_pairs.length}</strong>${units ? ` | 单位: ${escapeHtml(units)}` : ''}${basis}${escapeHtml(basisSource)}${mappingNote}`;
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
        text: data.scatter_pairs.map(p => ModelDates.format(p.time)),
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
    refreshScientificTerms();
    toggleAutoCalMethod();
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
    const point_ids = Array.from($('ac-points').selectedOptions, option => option.value);
    if (!point_ids.length) { toast('请至少选择一个率定点位', 'error'); return; }
    if (!state.calibPointsLoaded) {
        // Verify at least one calibration point with data exists
        const points = await api('/api/calibration/points');
        if (!points.length) { toast('请先在率定分析页添加至少一个率定点位并上传实测数据', 'error'); return; }
        state.calibPointsLoaded = true;
    }
    let objective_weights;
    try { objective_weights = typeof collectCalibrationWeights === 'function' ? collectCalibrationWeights(point_ids) : []; }
    catch (error) { toast(error.message, 'error'); return; }
    if (objective_weights.length && objective !== 'rmse') { toast('配置权重或尺度时请选择 RMSE', 'error'); return; }
    const body = {method, iterations, objective, params, point_ids, objective_weights};
    const maxSimulations = $('ac-max-simulations').value.trim();
    if (maxSimulations) body.max_simulations = Number(maxSimulations);
    if (!Number.isInteger(body.max_simulations) || body.max_simulations < 1 || body.max_simulations > 10000000) {
        toast('请填写 1 至 10000000 之间的模型评估上限', 'error'); return;
    }
    if (method === 'pyabc') {
        body.population_size = Number($('ac-population-size').value);
        body.minimum_epsilon = Number($('ac-minimum-epsilon').value);
        if (!Number.isInteger(body.population_size) || body.population_size < 2 || body.population_size > 200 ||
            !Number.isFinite(body.minimum_epsilon) || body.minimum_epsilon < 0 ||
            body.max_simulations < 2 * body.population_size) {
            toast('请检查 ABC 种群规模、模拟上限和最小容差', 'error'); return;
        }
    }
    const res = await api('/api/calibration/auto/start', {method:'POST', body});
    if (res.error) { toast(res.error, 'error'); return; }
    state.calibJobId = res.job_id;
    state.calibPollTimer = setInterval(pollAutoCalStatus, 3000);
    const paramSummary = params.map(p => `&nbsp;&nbsp;• ${p.module}.${p.param} [${p.min}, ${p.max}]`).join('<br>');
    $('ac-progress').innerHTML = `
        <div style="padding:20px;">
            <div style="font-size:14px;margin-bottom:12px;"><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-play"></use></svg> 自动率定已启动 (任务: ${res.job_id})</div>
            <div style="font-size:12px;color:var(--text-secondary);line-height:1.8;">
                方法: <strong>${method}</strong> | 目标函数: <strong>${objective}</strong> | 最大迭代: <strong>${iterations}</strong><br>
                率定参数: <strong>${params.length}</strong> 个<br>
                ${paramSummary}
            </div>
            <div id="ac-progress-detail" style="margin-top:16px;font-size:12px;"><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-clock"></use></svg> 等待第一次迭代结果...</div>
            <div style="margin-top:12px;display:flex;gap:8px;">
                <button class="btn btn-sm btn-danger" onclick="stopAutoCal()"><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-stop"></use></svg> 停止</button>
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
    const budgetExhausted = Boolean(data.result?.budget_exhausted);
    const statusLabel = budgetExhausted ? '探索评估上限已到（非收敛）' : status;
    let html = `<div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
        <div style="flex:1;background:var(--bg-tertiary);border-radius:6px;overflow:hidden;height:18px;">
            <div style="width:${pct}%;height:100%;background:linear-gradient(90deg,#3b82f6,#10b981);transition:width 0.3s;"></div>
        </div>
        <span style="font-size:12px;">${pct}%</span>
        <span style="font-size:12px;color:${budgetExhausted ? 'var(--warning-text, #92400e)' : 'var(--text-muted)'};">${statusLabel}</span>
    </div>`;
    if (last) {
        const paramStr = (last.params || []).map(p => `${p.module}.${p.param}=${p.value.toFixed(4)}`).join(', ');
        html += `<div style="font-size:11px;color:var(--text-secondary);line-height:1.6;">
            迭代 #${last.iteration} | 目标=${Number.isFinite(last.objective) ? last.objective.toFixed(4) : '—'}<br>
            当前参数: ${paramStr}
        </div>`;
    }
    if (data.fallback) {
        html += `<div style="margin-top:8px;padding:8px;background:#fef3c7;border-radius:6px;font-size:11px;color:#92400e;"><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-warning"></use></svg> ${data.fallback}</div>`;
    }
    if (data.error) {
        html += `<div style="margin-top:8px;color:var(--danger);font-size:11px;white-space:pre-wrap;">${data.error}</div>`;
    }
    $('ac-progress-detail').innerHTML = ModelDates.formatText(html);
    if (typeof renderAutoCalConvergence === 'function') renderAutoCalConvergence(hist);
    if (status === 'completed' || status === 'failed' || status === 'stopped') {
        clearInterval(state.calibPollTimer); state.calibPollTimer = null;
        if (status === 'completed' && data.result && data.result.best_params) {
            const best = data.result.best_params.map(p => `${p.module}.${p.param}=${p.value.toFixed(4)}`).join('<br>');
            const bestObj = Number.isFinite(data.result.best_objective) ? data.result.best_objective.toFixed(4) : '—';
            const budgetNotice = data.result.budget_exhausted
                ? '<strong>探索评估上限已用尽。</strong>以下为截至上限的最佳已试值；这不表示优化收敛或科学充分性。'
                : '';
            const resultTitle = data.result.budget_exhausted ? '探索上限已到，非收敛结果' : '率定完成';
            const resultIcon = data.result.budget_exhausted ? 'warning' : 'check';
            const resultColor = data.result.budget_exhausted ? '#92400e' : 'var(--success)';
            const resultBorder = data.result.budget_exhausted ? '#d6a84f' : '#10b981';
            const resultBackground = data.result.budget_exhausted ? 'rgba(245,158,11,0.12)' : 'rgba(16,185,129,0.1)';
            const applyLabel = data.result.budget_exhausted ? '将试算值作为参数起点' : '应用最优参数到 fabm.yaml';
            $('ac-progress-detail').innerHTML += `
                <div style="margin-top:12px;padding:12px;background:${resultBackground};border:1px solid ${resultBorder};border-radius:6px;">
                    <div style="font-size:13px;color:${resultColor};font-weight:600;"><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-${resultIcon}"></use></svg> ${resultTitle}</div>
                    <div style="font-size:11px;margin-top:6px;line-height:1.6;">
                        ${budgetNotice}<br>
                        最优目标值: <strong>${bestObj}</strong><br>
                        最优参数:<br>&nbsp;&nbsp;${best}
                    </div>
                    <button class="btn btn-sm ${data.result.budget_exhausted ? 'btn-warning' : 'btn-success'}" style="margin-top:8px;" onclick="applyAutoCalResult()"><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-save"></use></svg> ${applyLabel}</button>
                </div>`;
            if (data.result.budget_exhausted) toast('模型评估上限已用尽；返回最佳已试值，不代表收敛', 'info');
            else toast('自动率定完成', 'success');
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
        const qgisGrid = $('qgis-status-grid');
        if (qgisGrid) qgisGrid.textContent = `${g.nx} × ${g.ny}`;
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
    const qgisGrid = $('qgis-status-grid');
    if (qgisGrid) qgisGrid.textContent = '待加载';
    if (mapState.map) { try { mapState.map.remove(); } catch (e) {} mapState.map = null; }
    const c = $('map-container');
    if (c) c.innerHTML = '';
}

function initLeafletMap(g) {
    const el = $('map-container');
    if (mapState.map) { mapState.map.remove(); mapState.map = null; }
    el.innerHTML = '';
    let map;
    let fitBounds = null;
    if (g.has_lonlat && g.bounds) {
        mapState.xyMode = false;
        const b = g.bounds;
        fitBounds = [[b.s, b.w], [b.n, b.e]];
        map = L.map(el, { preferCanvas: true, zoomSnap: 0.5 });
        map.fitBounds(fitBounds);
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
    if (!fitBounds && mapState.xyMode) {
        const rects = _cellRectanglesXY(g);
        if (rects.length) {
            const south = Math.min(...rects.map(rect => rect.s));
            const north = Math.max(...rects.map(rect => rect.n));
            const west = Math.min(...rects.map(rect => rect.w));
            const east = Math.max(...rects.map(rect => rect.e));
            fitBounds = [[south, west], [north, east]];
        }
    }
    const mapInstance = map;
    setTimeout(() => {
        if (mapState.map !== mapInstance) return;
        mapInstance.invalidateSize({ pan: false });
        if (fitBounds) mapInstance.fitBounds(fitBounds, { animate: false });
    }, 120);
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
        // GETM/FABM fields can contain large finite sentinels (for example
        // -2.00000004e20) for dry or missing cells. Keep ordinary negatives.
        if (!Number.isFinite(v) || Math.abs(v) >= 1e19) continue;
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
    const vs = await fetchResultInventory();
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
        <button class="btn btn-sm" style="margin-left:8px;" onclick="mapPickTimeseries(${best.i},${best.j})"><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-chart"></use></svg> 提取该点时间序列</button>`;
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
        const vs = await fetchResultInventory();
        const list = Array.isArray(vs) ? vs
            : (vs && !vs.error ? ([]).concat(vs['3d'] || [], vs['2d'] || []) : []);
        if (list.length) { tsVar.value = (list.find(v => v.name === varName) ? varName : list[0].name); }
    }
    extractTimeseries();
}

// ── Init ──────────────────────────────────────────────────────────────
function ensureViz3dVolumePresetCompatibility() {
    // GETM cannot solve triangular meshes. Drop the old preset button and
    // any leftover "triangles" option so a cached page cannot turn them back on.
    document.getElementById('viz3d-volume-preset')?.remove();
    document.querySelectorAll('#viz3d-mesh-mode option').forEach(opt => {
        if (opt.value === 'triangles') opt.remove();
    });
    const mesh = document.getElementById('viz3d-mesh-mode');
    if (mesh && mesh.value === 'triangles') mesh.value = 'continuous';
    return false;
}

window.addEventListener('load', () => {
    // Older cached templates have the mesh/layer controls but predate the
    // combined volume preset. The current app.js asset can bridge that markup.
    ensureViz3dVolumePresetCompatibility();
    refreshScientificTerms();
    loadCases();
    const pending=(async()=>{
        if(await restoreCurrentCase())await loadVariables();
        else $('stat-water').textContent='-';
    })();
    state.currentCasePending=pending;
    pending.finally(()=>{
        if(state.currentCasePending===pending)state.currentCasePending=null;
        if(document.getElementById('page-viz2d')?.classList.contains('active'))initViz2d();
        if(document.getElementById('page-viz3d')?.classList.contains('active'))initViz3d();
    });
});

// Language changes update labels and redraw the visible result without a solver run.
document.addEventListener('studio-language-changed',()=>{
    refreshScientificTerms();
    populateCalibrationVariables();
    if ($('ac-method')) toggleAutoCalMethod();
    if(state.currentParams.length) filterParams();
    Object.values(state.charts).forEach(chart=>{if(chart){translateChartLabels(chart.config._config);chart.update('none');}});
    const vars=new Map([...state.variables2d,...state.variables3d].map(v=>[v.name,v]));
    document.querySelectorAll('select option').forEach(option=>{
        const variable=vars.get(option.value);
        if(variable) {
            const requiresVertical=verticalResultSelectIds.has(option.closest('select')?.id);
            option.dataset.i18nSkip='true';
            option.disabled=requiresVertical&&!hasVerticalResultDimension(variable);
            option.textContent=`${resultVariablePriority(variable)===2?'【按需】':'【默认优先】'} ${resultVariableOptionLabel(variable,requiresVertical)}`;
            if(option.disabled)option.title=option.textContent;
        }
    });
    if(state.activeCase) {
        if(document.getElementById('page-dashboard')?.classList.contains('active')) loadDashboardSummary();
        if(document.getElementById('page-viz2d')?.classList.contains('active')) updateViz2d();
        if(document.getElementById('page-viz3d')?.classList.contains('active')) initViz3d();
    }
});

