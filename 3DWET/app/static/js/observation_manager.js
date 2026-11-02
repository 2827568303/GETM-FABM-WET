(function (root) {
  'use strict';

  const SUPPORTED = new Set(['.obs', '.csv', '.xlsx', '.xlsm']);
  const $ = (id) => document.getElementById(id);
  let selectedFiles = new Set();
  let previewState = null;
  let browseTimer = null;

  function parseSourcePaths(text) {
    return String(text || '').split(/[\r\n]+/).map((p) => p.trim()).filter(Boolean);
  }

  function buildPreviewRequest(paths, mappings, maxGap, perFileOverrides = {}) {
    const files = parseSourcePaths(paths);
    const gap = Number(maxGap);
    if (!files.length) throw new Error('请至少选择一个观测文件');
    if (!String(maxGap || '').trim() || !Number.isFinite(gap) || gap <= 0) {
      throw new Error('必须显式填写有限正数最大时间差（小时）');
    }
    const resolved = Object.assign({}, mappings || {});
    for (const path of files) {
      const name = path.split(/[\\/]/).pop();
      const base = resolved[path] || resolved[name] || {};
      const override = perFileOverrides[path] || perFileOverrides[name] || {};
      const item = Object.assign({}, base);
      ['variable', 'unit', 'mass_basis'].forEach((field) => {
        if (String(override[field] || '').trim()) item[field] = String(override[field]).trim();
      });
      if (/\.obs$/i.test(name) && (!String(item.variable || '').trim() || !String(item.unit || '').trim())) {
        throw new Error(`${name}：.obs 文件必须明确填写模型变量和单位`);
      }
      if (!/\.obs$/i.test(name) && item.header_row != null &&
          (!Number.isInteger(Number(item.header_row)) || Number(item.header_row) < 1)) {
        throw new Error(`${name}：表头行必须是从 1 开始的正整数`);
      }
      if (item.depth_m_mode === 'constant') {
        if (String(item.depth_m_column || '').trim()) {
          throw new Error(`${name}：使用恒定深度时请清空深度列`);
        }
        if (!Number.isFinite(Number(item.depth_m_constant))) {
          throw new Error(`${name}：恒定深度必须是有限数值`);
        }
      }
      resolved[path] = item;
      resolved[name] = item;
    }
    return { files, mappings: resolved, max_time_gap_hours: gap };
  }

  function previewIsFresh(state, fingerprint) {
    return !!(state && state.preview && state.signature &&
      state.preview.preview_signature === state.signature && state.fingerprint === fingerprint);
  }

  function escapeHtml(value) {
    return String(value == null ? '' : value).replace(/[&<>"']/g, (c) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    })[c]);
  }

  async function api(url, options) {
    const response = await fetch(url, Object.assign({ headers: { 'Content-Type': 'application/json' } }, options || {}));
    let data;
    try { data = await response.json(); } catch (_) { data = {}; }
    if (!response.ok || data.error) throw new Error(data.error || `HTTP ${response.status}`);
    return data;
  }

  function status(message, bad) {
    const el = $('obs-manager-status');
    if (el) { el.textContent = message; el.style.color = bad ? 'var(--danger)' : 'var(--text-secondary)'; }
  }

  function commonMapping() {
    const get = (id) => ($(id) || {}).value || '';
    const mapping = { __version__: 'observation-ui-v3' };
    const global = {
      lake_id: get('obs-map-lake'), station_id: get('obs-map-station'),
      point_id: get('obs-map-point'),
      unit: get('obs-map-unit'), variable: get('obs-map-variable')
    };
    const columns = {
      time_column: get('obs-col-time'), value_column: get('obs-col-value'),
      depth_m_column: get('obs-col-depth'), unit_column: get('obs-col-unit'),
      variable_column: get('obs-col-variable'), lake_id_column: get('obs-col-lake'),
      station_id_column: get('obs-col-station'), point_id_column: get('obs-col-point'), quality_column: get('obs-col-quality')
    };
    for (const path of parseSourcePaths(($('obs-file-paths') || {}).value)) {
      const name = path.split(/[\\/]/).pop();
      const isObs = /\.obs$/i.test(name);
      const item = {};
      Object.entries(global).forEach(([k, v]) => {
        if (v.trim() && !(isObs && ['unit', 'variable'].includes(k))) item[k] = v.trim();
      });
      if (!isObs) {
        Object.entries(columns).forEach(([k, v]) => { if (v.trim()) item[k] = v.trim(); });
        const headerRow = get('obs-header-row');
        if (headerRow.trim()) item.header_row = Number(headerRow);
        const constantDepth = get('obs-depth-constant');
        if (constantDepth.trim()) {
          item.depth_m_mode = 'constant';
          item.depth_m_constant = Number(constantDepth);
        }
      }
      const sign = get('obs-depth-sign');
      if (sign) item.depth_sign = sign;
      const maxDepth = get('obs-review-depth');
      if (maxDepth.trim()) item.review_depth_max = Number(maxDepth);
      if (isObs) item.depth_sign = 'negative_down';
      mapping[name] = item;
      mapping[path] = item;
    }
    return mapping;
  }

  function renderFileMappings() {
    const host = $('obs-file-mappings');
    if (!host) return;
    const paths = parseSourcePaths(($('obs-file-paths') || {}).value);
    host.innerHTML = paths.map((path) => {
      const name = path.split(/[\\/]/).pop();
      const obs = /\.obs$/i.test(name);
      const required = obs ? 'required per .obs file' : 'optional override; otherwise use CSV/XLSX defaults';
      const safePath = escapeHtml(path);
      const safeName = escapeHtml(name);
      return `<div class="form-row obs-file-mapping" style="border:1px solid var(--border);border-radius:6px;padding:8px;margin:6px 0;">
        <div class="form-group" style="min-width:180px;flex:1;"><strong>${safeName}</strong><small style="display:block;overflow-wrap:anywhere;">${safePath}</small></div>
        <div class="form-group"><label class="form-label">映射到模型变量</label><input class="form-input" data-obs-file-mapping data-path="${safePath}" data-field="variable" value="${escapeHtml(fileMappingValues[path]?.variable || '')}" placeholder="${required}"></div>
        <div class="form-group"><label class="form-label">文件单位</label><input class="form-input" data-obs-file-mapping data-path="${safePath}" data-field="unit" value="${escapeHtml(fileMappingValues[path]?.unit || '')}" placeholder="${required}"></div>
        <div class="form-group"><label class="form-label">质量元素 basis（可选）</label><input class="form-input" data-obs-file-mapping data-path="${safePath}" data-field="mass_basis" value="${escapeHtml(fileMappingValues[path]?.mass_basis || '')}" placeholder="仅有来源依据时填写 O2 / N / P"></div>
      </div>`;
    }).join('') || '<div class="page-desc">先选择文件后，为每个文件设置变量和单位映射。</div>';
    host.querySelectorAll('[data-obs-file-mapping]').forEach((input) => {
      const update = () => {
        if (!fileMappingValues[input.dataset.path]) fileMappingValues[input.dataset.path] = {};
        fileMappingValues[input.dataset.path][input.dataset.field] = input.value;
        refreshColumnVariables();
        invalidatePreview();
      };
      input.addEventListener('input', update);
      input.addEventListener('change', update);
    });
    refreshColumnVariables();
  }

  const fileMappingValues = Object.create(null);
  let nativeColumnVariables = null;

  function readFileMappingValues() {
    const values = {};
    const host = $('obs-file-mappings');
    if (!host) return values;
    host.querySelectorAll('[data-obs-file-mapping]').forEach((input) => {
      const path = input.dataset.path;
      const field = input.dataset.field;
      if (!values[path]) values[path] = {};
      values[path][field] = input.value.trim();
    });
    Object.assign(fileMappingValues, values);
    return values;
  }

  function refreshColumnVariables() {
    const select = $('obs-column-variable');
    if (!select) return;
    const previous = select.value;
    const mappings = commonMapping();
    const overrides = readFileMappingValues();
    const choices = new Set();
    parseSourcePaths(($('obs-file-paths') || {}).value).forEach((path) => {
      const name = path.split(/[\\/]/).pop();
      const mapping = overrides[path] || overrides[name] || mappings[path] || mappings[name] || {};
      const variable = String(mapping.variable || '').trim();
      if (variable && (!nativeColumnVariables || nativeColumnVariables.has(variable))) choices.add(variable);
    });
    select.replaceChildren(...Array.from(choices).sort().map((variable) => {
      const option = document.createElement('option');
      option.value = variable; option.textContent = variable; return option;
    }));
    if (choices.has(previous)) select.value = previous;
  }

  function setColumnVariableInventory(items) {
    nativeColumnVariables = Array.isArray(items)
      ? new Set(items.map((item) => typeof item === 'string' ? item : item?.name).filter(Boolean))
      : null;
    refreshColumnVariables();
  }

  function previewFingerprint(paths, mappings, perFile, gap) {
    return JSON.stringify({ paths: parseSourcePaths(paths), mappings, per_file_mappings: perFile, gap });
  }

  function currentFingerprint() {
    return previewFingerprint(($('obs-file-paths') || {}).value, commonMapping(),
      readFileMappingValues(), ($('obs-max-gap') || {}).value);
  }

  function invalidatePreview() {
    previewState = null;
    const apply = $('obs-apply');
    if (apply) apply.disabled = true;
    const preview = $('obs-preview-result');
    if (preview) preview.textContent = '设置有变化，请重新预览。';
    if (columnComparisonChart) { columnComparisonChart.destroy(); columnComparisonChart = null; }
    const columnResult = $('obs-column-result');
    if (columnResult) columnResult.textContent = '设置有变化；请重新执行只读配对。';
  }

  function showExamples(cases) {
    const host = $('obs-case-examples');
    if (!host) return;
    host.innerHTML = (cases || []).map((c) => `<button type="button" class="btn btn-sm obs-case-shortcut" data-path="${escapeHtml(c.path)}" style="margin:2px;">${escapeHtml(c.name)}${c.external ? '（外部）' : ''}</button>`).join('') || '<span>未发现已有案例目录</span>';
    host.querySelectorAll('.obs-case-shortcut').forEach((button) => button.addEventListener('click', () => browseDirectory(button.dataset.path)));
  }

  function renderDirectory(data) {
    const host = $('obs-directory-list');
    if (!host) return;
    const entries = data.entries || [];
    host.innerHTML = `<div style="margin-bottom:6px;word-break:break-all;">目录：${escapeHtml(data.path)}</div>` +
      (data.parent ? `<button type="button" class="btn btn-sm" data-dir="${escapeHtml(data.parent)}"><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-up"></use></svg> 上级</button>` : '') +
      entries.map((entry) => {
        if (entry.is_dir) return `<button type="button" class="btn btn-sm obs-dir" data-dir="${escapeHtml(entry.path)}"><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-folder"></use></svg> ${escapeHtml(entry.name)}</button>`;
        const ext = (entry.name.match(/\.[^.]+$/) || [''])[0].toLowerCase();
        if (!SUPPORTED.has(ext)) return '';
        const checked = selectedFiles.has(entry.path) ? 'checked' : '';
        return `<label style="display:inline-block;margin:4px 10px 4px 0;"><input type="checkbox" class="obs-file" data-path="${escapeHtml(entry.path)}" ${checked}> ${escapeHtml(entry.name)}</label>`;
      }).join('') || '<div>该目录没有可选的 .obs、CSV 或 XLSX 文件。</div>';
    host.querySelectorAll('.obs-dir').forEach((button) => button.addEventListener('click', () => browseDirectory(button.dataset.dir)));
    const up = host.querySelector('[data-dir]:not(.obs-dir)');
    if (up) up.addEventListener('click', () => browseDirectory(up.dataset.dir));
    host.querySelectorAll('.obs-file').forEach((checkbox) => checkbox.addEventListener('change', () => {
      if (checkbox.checked) selectedFiles.add(checkbox.dataset.path); else selectedFiles.delete(checkbox.dataset.path);
      const paths = $('obs-file-paths');
      paths.value = Array.from(selectedFiles).join('\n');
      renderFileMappings();
      invalidatePreview();
    }));
  }

  async function browseDirectory(path) {
    try {
      const data = await api('/api/system/list_dir?path=' + encodeURIComponent(path));
      renderDirectory(data);
      status('已读取真实目录内容；勾选文件后预览。');
    } catch (error) { status(error.message, true); }
  }

  async function pickDirectory() {
    const start = ($('obs-source-dir') || {}).value || '';
    try {
      await api('/api/system/pick_folder', { method: 'POST', body: JSON.stringify({ start_dir: start }) });
      status('请在系统文件夹窗口中选择观测数据目录…');
      clearInterval(browseTimer);
      const deadline = Date.now() + 120000;
      browseTimer = setInterval(async () => {
        try {
          const result = await api('/api/system/pick_folder_result');
          if (result.done) {
            clearInterval(browseTimer);
            if (result.path) { $('obs-source-dir').value = result.path; await browseDirectory(result.path); }
            else status('未选择目录。');
          } else if (Date.now() > deadline) { clearInterval(browseTimer); status('等待系统目录窗口超时。', true); }
        } catch (error) { clearInterval(browseTimer); status(error.message, true); }
      }, 700);
    } catch (error) { status(error.message, true); }
  }

  function displayPreview(data) {
    const host = $('obs-preview-result');
    const rows = [];
    (data.files || []).forEach((file) => {
      rows.push(`<h4>${escapeHtml(file.source_file)} · ${file.row_count} 行 · SHA256 ${escapeHtml(file.sha256)}</h4>`);
      const mapping = file.mapping || {};
      rows.push(`<div>所选映射：源文件 ${escapeHtml(file.source_file)} → 模型变量 ${escapeHtml(mapping.variable || '未设置')} · 单位 ${escapeHtml(mapping.unit || '未设置')} · 湖泊 ${escapeHtml(mapping.lake_id || '未设置')} · 站位 ${escapeHtml(mapping.station_id || '未设置')}</div>`);
      rows.push(`<div>有效记录 ${file.records.length}；逐行诊断 ${file.diagnostics.length}</div>`);
      if (file.diagnostics.length) rows.push(`<pre>${escapeHtml(JSON.stringify(file.diagnostics, null, 2))}</pre>`);
      if (file.records.length) rows.push(`<pre>${escapeHtml(JSON.stringify(file.records.slice(0, 8), null, 2))}${file.records.length > 8 ? '\n…其余记录已省略' : ''}</pre>`);
    });
    rows.push(`<div>预览有效期至 ${escapeHtml(new Date(data.expires_at * 1000).toLocaleString())}；最大配对时间差 ${escapeHtml(data.max_time_gap_hours)} 小时。</div>`);
    host.innerHTML = rows.join('');
  }

  async function preview() {
    try {
      const body = buildPreviewRequest(($('obs-file-paths') || {}).value, commonMapping(),
        ($('obs-max-gap') || {}).value, readFileMappingValues());
      status('正在读取并诊断所选文件…');
      const data = await api('/api/calibration/observations/preview', { method: 'POST', body: JSON.stringify(body) });
      previewState = { preview: data, signature: data.preview_signature,
        mappings: body.mappings, fingerprint: currentFingerprint() };
      displayPreview(data);
      $('obs-apply').disabled = false;
      status('预览完成。检查列映射与每行诊断后再应用。');
    } catch (error) { invalidatePreview(); status(error.message, true); }
  }

  let columnComparisonChart = null;
  function displayColumnComparison(data) {
    const host = $('obs-column-result');
    if (!host) return;
    if (columnComparisonChart) { columnComparisonChart.destroy(); columnComparisonChart = null; }
    const pairs = data.scatter_pairs || [];
    const fileRows = (data.files || []).map((file) =>
      `<li>${escapeHtml(file.source_file)} → ${escapeHtml(file.mapping?.variable || '')} · 单位 ${escapeHtml(file.mapping?.unit || '')} · SHA-256 ${escapeHtml(file.sha256)} · 可解析 ${file.usable_records}/${file.row_count} 行 · 解析排除 ${file.diagnostics?.length || 0}</li>`).join('');
    const sourceDiagnostics = (data.files || []).flatMap((file) => file.diagnostics || []);
    const diagnostics = (data.diagnostics || []).length
      ? `<details><summary>配对排除诊断 (${data.diagnostics.length})</summary><pre>${escapeHtml(JSON.stringify(data.diagnostics, null, 2))}</pre></details>`
      : '<div>无配对排除项。</div>';
    const sourceReview = sourceDiagnostics.length
      ? `<details><summary>观测文件解析排除 (${sourceDiagnostics.length})</summary><pre>${escapeHtml(JSON.stringify(sourceDiagnostics, null, 2))}</pre></details>`
      : '<div>观测文件没有解析排除项。</div>';
    host.innerHTML = `<div><strong>只读 GOTM 代表性水柱 · ${escapeHtml(data.variable)}</strong> · 配对 ${pairs.length} 条 · 最大时间差 ${escapeHtml(data.max_time_gap_hours)} 小时</div>` +
      `<ul>${fileRows}</ul>${sourceReview}${diagnostics}` +
      (pairs.length ? '<div style="height:250px;"><canvas id="obs-column-chart"></canvas></div>' : '<div>没有满足时间、深度、单位和身份约束的配对值。</div>');
    if (!pairs.length || typeof Chart === 'undefined') return;
    const context = $('obs-column-chart').getContext('2d');
    columnComparisonChart = new Chart(context, {
      type: 'line',
      data: { labels: pairs.map((pair) => pair.time), datasets: [
        { label: `模拟（配对时刻/深度） · ${data.variable}`, data: pairs.map((pair) => pair.sim),
          borderColor: '#3b82f6', backgroundColor: 'transparent', pointRadius: 0, borderWidth: 2, tension: 0.15 },
        { label: `观测 · ${data.variable}`, data: pairs.map((pair) => pair.obs),
          borderColor: '#f59e0b', backgroundColor: '#f59e0b', pointRadius: 3, borderWidth: 1.5, tension: 0.15 }
      ] },
      options: { responsive: true, maintainAspectRatio: false,
        plugins: { tooltip: { callbacks: { label: (item) => `${item.dataset.label}: ${item.parsed.y} ${data.simulated?.unit || ''}` } } },
        scales: { x: { ticks: { maxTicksLimit: 8, autoSkip: true } }, y: { title: { display: true, text: data.simulated?.unit || '' } } } }
    });
  }

  async function compareColumn() {
    try {
      const prepared = buildPreviewRequest(($('obs-file-paths') || {}).value, commonMapping(),
        ($('obs-max-gap') || {}).value, readFileMappingValues());
      const body = { ...prepared, variable: ($('obs-column-variable') || {}).value,
        lake_id: ($('obs-map-lake') || {}).value, point_id: ($('obs-map-point') || {}).value };
      if (!body.variable) throw new Error('请先为所选文件填写模型变量映射');
      if (!String(body.lake_id || '').trim() || !String(body.point_id || '').trim())
        throw new Error('请填写湖泊 ID 和观测组 ID；后者只用于将剖面记录归组');
      $('obs-column-gap').textContent = `${body.max_time_gap_hours} 小时`;
      status('正在对当前活动案例执行只读 GOTM 水柱配对…');
      const data = await api('/api/calibration/observations/compare-column',
        { method: 'POST', body: JSON.stringify(body) });
      displayColumnComparison(data);
      status(`只读配对完成：${data.scatter_pairs.length} 条，未写入当前案例观测。`);
    } catch (error) {
      if (columnComparisonChart) { columnComparisonChart.destroy(); columnComparisonChart = null; }
      if ($('obs-column-result')) $('obs-column-result').textContent = error.message;
      status(error.message, true);
    }
  }

  async function refreshApplied() {
    const data = await api('/api/calibration/observations');
    const host = $('obs-current-records');
    if (!host) return;
    host.innerHTML = `<div>当前记录 ${((data.records || []).length)} 条；诊断 ${(data.diagnostics || []).length} 条。</div>` +
      `<pre>${escapeHtml(JSON.stringify({ manifest: data.manifest || [], diagnostics: data.diagnostics || [], records: (data.records || []).slice(0, 8) }, null, 2))}</pre>`;
  }

  async function applyPreview() {
    if (!previewState || !previewIsFresh(previewState, currentFingerprint())) { invalidatePreview(); status('预览签名与当前设置不匹配，请重新预览。', true); return; }
    try {
      status('正在将已签名预览原子应用到当前案例…');
      await api('/api/calibration/observations/apply', { method: 'POST', body: JSON.stringify({ preview: previewState.preview, mappings: previewState.mappings }) });
      await refreshApplied();
      previewState = null;
      $('obs-apply').disabled = true;
      status('应用成功，已刷新当前案例观测记录。');
    } catch (error) { status(error.message, true); }
  }

  async function init() {
    if (!$('obs-manager')) return;
    $('obs-browse-native').addEventListener('click', pickDirectory);
    $('obs-list-path').addEventListener('click', () => browseDirectory(($('obs-source-dir').value || '').trim()));
    $('obs-preview').addEventListener('click', preview);
    $('obs-apply').addEventListener('click', applyPreview);
    $('obs-column-compare').addEventListener('click', compareColumn);
    $('obs-file-paths').addEventListener('input', () => { renderFileMappings(); invalidatePreview(); });
    $('obs-file-paths').addEventListener('change', () => { renderFileMappings(); invalidatePreview(); });
    ['obs-file-paths', 'obs-max-gap', 'obs-map-lake', 'obs-map-station', 'obs-map-point', 'obs-map-unit', 'obs-map-variable',
      'obs-col-time', 'obs-col-value', 'obs-col-depth', 'obs-col-unit', 'obs-col-variable', 'obs-col-lake',
      'obs-col-station', 'obs-col-point', 'obs-col-quality', 'obs-header-row', 'obs-depth-constant',
      'obs-depth-sign', 'obs-review-depth'].forEach((id) => {
      $(id).addEventListener('input', invalidatePreview);
      $(id).addEventListener('change', invalidatePreview);
      if (id === 'obs-map-lake' || id === 'obs-map-point' || id === 'obs-map-variable') {
        $(id).addEventListener('input', refreshColumnVariables);
        $(id).addEventListener('change', refreshColumnVariables);
      }
    });
    try {
      renderFileMappings();
      const cases = await api('/api/cases');
      showExamples(cases);
      await refreshApplied();
      status('已载入案例目录清单与当前案例观测。');
    } catch (error) { status(error.message, true); }
  }

  const manager = { parseSourcePaths, buildPreviewRequest, previewIsFresh, previewFingerprint, escapeHtml, init, compareColumn, setColumnVariableInventory };
  root.ObservationManager = manager;
  if (typeof document !== 'undefined' && document.addEventListener) document.addEventListener('DOMContentLoaded', init);
})(typeof window !== 'undefined' ? window : globalThis);
