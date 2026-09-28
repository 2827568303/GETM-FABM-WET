// Pre-processing UI: shapefile upload → grid → interpolate → bathymetry.nc
// State is held in state.preprocess (boundary_id, bathy_id, grid_id, depth_array).
// All HTTP calls reuse the global api() helper from app.js.

function initPreprocess() {
    // Tab switching
    document.querySelectorAll('.pp-tab').forEach(t => {
        if (!t.dataset.bound) {
            t.dataset.bound = '1';
            t.addEventListener('click', () => {
                document.querySelectorAll('.pp-tab').forEach(x => x.classList.remove('active'));
                document.querySelectorAll('.pp-tab-content').forEach(x => x.classList.remove('active'));
                t.classList.add('active');
                const tgt = document.getElementById('pp-tab-' + t.dataset.ppTab);
                if (tgt) tgt.classList.add('active');
            });
        }
    });
    // Ensure state object exists
    if (!state.preprocess) state.preprocess = {};
    // CRS select → toggle the custom-EPSG input
    ['pp-boundary', 'pp-bathy'].forEach(prefix => {
        const sel = document.getElementById(prefix + '-crs');
        if (sel && !sel.dataset.bound) {
            sel.dataset.bound = '1';
            sel.addEventListener('change', () => {
                const epsgInput = document.getElementById(prefix + '-epsg');
                if (epsgInput) epsgInput.style.display = sel.value === 'epsg' ? '' : 'none';
            });
        }
    });
}

// Collect the CRS declaration fields for an upload request
function _ppCrsFields(prefix) {
    const sel = document.getElementById(prefix + '-crs');
    if (!sel) return {};
    const epsgInput = document.getElementById(prefix + '-epsg');
    return { crs_preset: sel.value, crs_epsg: epsgInput ? epsgInput.value.trim() : '' };
}

function _ppStatus(id, msg, ok = true) {
    const el = document.getElementById(id);
    if (!el) return;
    el.innerHTML = `<span style="color:${ok ? 'var(--success)' : 'var(--danger)'};font-size:12px;">${msg}</span>`;
}

// Generic shapefile multipart upload
async function _ppUpload(url, fileInputId, extraFields = {}) {
    const fi = document.getElementById(fileInputId);
    if (!fi || !fi.files || !fi.files.length) {
        return { error: '请先选择 shapefile 组件（.shp/.shx/.dbf 至少三个）' };
    }
    const fd = new FormData();
    let hasShp = false;
    for (const f of fi.files) {
        fd.append('files', f, f.name);
        if (f.name.toLowerCase().endsWith('.shp')) hasShp = true;
    }
    if (!hasShp) return { error: '缺少 .shp 主文件' };
    for (const [k, v] of Object.entries(extraFields)) fd.append(k, v);
    try {
        const r = await fetch(url, { method: 'POST', body: fd });
        return await r.json();
    } catch (e) {
        return { error: '网络错误: ' + e.message };
    }
}

async function uploadBoundary() {
    _ppStatus('pp-boundary-status', '上传中...', true);
    const res = await _ppUpload('/api/preprocess/boundary/upload', 'pp-boundary-files', _ppCrsFields('pp-boundary'));
    if (res.error) { _ppStatus('pp-boundary-status', '失败: ' + res.error, false); return; }
    state.preprocess.boundary_id = res.boundary_id;
    state.preprocess.bbox = res.bbox;
    // rings_preview: 每个 polygon 的外环（多部件湖体如滇池 = 外海 + 草海）
    state.preprocess.boundary_rings = res.rings_preview || [res.coords_preview];
    state.preprocess.boundary_preview = res.coords_preview;  // 兼容旧字段
    const [xmin, ymin, xmax, ymax] = res.bbox;
    const w = (xmax - xmin).toFixed(0), h = (ymax - ymin).toFixed(0);
    _ppStatus('pp-boundary-status', `✓ 上传成功`, true);
    const warnHtml = (res.warnings || []).map(w =>
        `<div style="color:var(--warning);font-size:11px;margin-top:4px;">⚠ ${w}</div>`).join('');
    const convHtml = res.conversion
        ? `<div style="color:var(--success);font-size:11px;margin-top:4px;">🔄 ${res.conversion}</div>` : '';
    document.getElementById('pp-boundary-info').innerHTML = `
        <div>点数: <strong>${res.n_points}</strong></div>
        <div>多边形个数: <strong>${res.n_polygons || 1}</strong></div>
        <div>范围: ${w}m × ${h}m</div>
        <div>坐标系: <strong>${res.crs_type}</strong>${res.utm_zone ? ' (UTM zone ' + res.utm_zone + ')' : ''}</div>
        <div>原始 CRS: ${res.orig_crs_type}</div>${warnHtml}${convHtml}`;
    drawBoundaryPreview(state.preprocess.boundary_rings, res.bbox);
}

async function uploadBathymetry() {
    _ppStatus('pp-bathy-status', '上传中...', true);
    const depthField = document.getElementById('pp-depth-field').value.trim();
    const extra = Object.assign({ depth_field: depthField }, _ppCrsFields('pp-bathy'));
    const res = await _ppUpload('/api/preprocess/bathymetry/upload', 'pp-bathy-files', extra);
    if (res.error) {
        _ppStatus('pp-bathy-status', '失败: ' + res.error, false);
        if (res.fields) {
            document.getElementById('pp-bathy-info').innerHTML = `可用字段: <code>${res.fields.join(', ')}</code>`;
        }
        return;
    }
    state.preprocess.bathy_id = res.bathy_id;
    state.preprocess.bathy_geom = res.geom_type;
    state.preprocess.bathy_preview_points = res.preview_points;
    state.preprocess.bathy_preview_polys = res.preview_polygons;
    state.preprocess.bathy_preview_depths = res.preview_depths;
    _ppStatus('pp-bathy-status', '✓ 上传成功', true);
    const warnHtml = (res.warnings || []).map(w =>
        `<div style="color:var(--warning);font-size:11px;margin-top:4px;">⚠ ${w}</div>`).join('');
    const convHtml = res.conversion
        ? `<div style="color:var(--success);font-size:11px;margin-top:4px;">🔄 ${res.conversion}</div>` : '';
    const fitHtml = (res.inside_ratio != null)
        ? `<div style="font-size:11px;margin-top:2px;">对齐质量: 落入边界内采样点 <strong>${(res.inside_ratio * 100).toFixed(1)}%</strong></div>` : '';
    document.getElementById('pp-bathy-info').innerHTML = `
        <div>几何类型: <strong>${res.geom_type}</strong></div>
        <div>要素数: <strong>${res.n_features}</strong></div>
        <div>水深字段: <code>${res.depth_field}</code></div>
        <div>水深范围: <strong>${res.depth_range[0].toFixed(2)} ~ ${res.depth_range[1].toFixed(2)} m</strong></div>${warnHtml}${convHtml}${fitHtml}`;
    drawBathymetryPreview(res);
}

async function uploadBathymetryXyz() {
    // Plain-text bathymetry import (CSV/TAB/space). GETM can only read
    // bathymetry from NetCDF, so the server converts the text for us.
    const input = document.getElementById('pp-bathy-xyz-file');
    if (!input.files || !input.files[0]) { _ppStatus('pp-bathy-status', '请先选择文本文件', false); return; }
    _ppStatus('pp-bathy-status', '导入中...', true);
    const fd = new FormData();
    fd.append('file', input.files[0]);
    fd.append('crs', document.getElementById('pp-bathy-xyz-crs').value || 'auto');
    let res;
    try {
        const r = await fetch('/api/preprocess/bathymetry/upload_xyz', { method: 'POST', body: fd });
        res = await r.json();
    } catch (e) {
        _ppStatus('pp-bathy-status', '网络错误: ' + e.message, false); return;
    }
    if (res.error) { _ppStatus('pp-bathy-status', '失败: ' + res.error, false); return; }
    state.preprocess.bathy_id = res.bathy_id;
    state.preprocess.bathy_geom = res.geom_type;
    state.preprocess.bathy_preview_points = res.preview_points;
    state.preprocess.bathy_preview_polys = [];
    state.preprocess.bathy_preview_depths = res.preview_depths;
    const warnHtml = (res.warnings || []).map(w =>
        `<div style="color:var(--warning);font-size:11px;margin-top:4px;">⚠ ${w}</div>`).join('');
    document.getElementById('pp-bathy-info').innerHTML = `
        <div>来源: <strong>文本文件 (x,y,depth)</strong></div>
        <div>有效点数: <strong>${res.n_features}</strong>${res.n_bad_rows ? ` （跳过 ${res.n_bad_rows} 行）` : ''}</div>
        <div>水深范围: <strong>${res.depth_range[0].toFixed(2)} ~ ${res.depth_range[1].toFixed(2)} m</strong></div>
        <div>坐标系: <strong>${res.crs_type}</strong>${warnHtml}`;
    _ppStatus('pp-bathy-status', '✓ 文本导入成功，继续“网格生成 → 插值”', true);
    drawBathymetryPreview(res);
}

async function uploadHypsograph() {
    // QWET/GOTM style depth-area curve → circular lake (boundary + depth points)
    const input = document.getElementById('pp-hyp-file');
    if (!input.files || !input.files[0]) { _ppStatus('pp-bathy-status', '请先选择 hypsograph 文件', false); return; }
    _ppStatus('pp-bathy-status', '生成中...', true);
    const fd = new FormData();
    fd.append('file', input.files[0]);
    const lon = document.getElementById('pp-hyp-lon').value.trim();
    const lat = document.getElementById('pp-hyp-lat').value.trim();
    if (lon) fd.append('center_lon', lon);
    if (lat) fd.append('center_lat', lat);
    let res;
    try {
        const r = await fetch('/api/preprocess/hypsograph', { method: 'POST', body: fd });
        res = await r.json();
    } catch (e) {
        _ppStatus('pp-bathy-status', '网络错误: ' + e.message, false); return;
    }
    if (res.error) { _ppStatus('pp-bathy-status', '失败: ' + res.error, false); return; }
    state.preprocess.boundary_id = res.boundary_id;
    state.preprocess.bathy_id = res.bathy_id;
    state.preprocess.bathy_geom = res.geom_type || 'point';
    state.preprocess.bathy_preview_points = res.preview_points;
    state.preprocess.bathy_preview_polys = [];
    state.preprocess.bathy_preview_depths = res.preview_depths;
    const warnHtml = (res.warnings || []).map(w =>
        `<div style="color:var(--warning);font-size:11px;margin-top:4px;">⚠ ${w}</div>`).join('');
    document.getElementById('pp-bathy-info').innerHTML = `
        <div>来源: <strong>深度-面积曲线</strong>（自动生成圆形湖泊）</div>
        <div>层数: <strong>${res.n_levels}</strong>，测深点 <strong>${res.n_points}</strong></div>
        <div>最大水深: <strong>${res.max_depth_m} m</strong></div>
        <div>湖面面积: <strong>${(res.surface_area_m2 / 1e6).toFixed(3)} km²</strong>（半径 ${res.lake_radius_m} m）</div>
        <div>坐标系: <strong>${res.crs_type}</strong>${warnHtml}`;
    _ppStatus('pp-bathy-status', '✓ 已从曲线生成边界 + 测深点，下一步“网格生成”', true);
    drawBathymetryPreview(res);
}

async function generateGrid() {
    if (!state.preprocess.boundary_id) {
        _ppStatus('pp-grid-status', '请先上传边界', false); return;
    }
    const dx = parseFloat(document.getElementById('pp-dx').value);
    const dy = parseFloat(document.getElementById('pp-dy').value);
    const nxVal = document.getElementById('pp-nx').value.trim();
    const nyVal = document.getElementById('pp-ny').value.trim();
    const body = {
        boundary_id: state.preprocess.boundary_id,
        dx, dy,
        nx: nxVal ? parseInt(nxVal) : null,
        ny: nyVal ? parseInt(nyVal) : null,
    };
    _ppStatus('pp-grid-status', '生成中...', true);
    const res = await api('/api/preprocess/grid/generate', { method: 'POST', body });
    if (res.error) { _ppStatus('pp-grid-status', '失败: ' + res.error, false); return; }
    state.preprocess.grid_id = res.grid_id;
    state.preprocess.grid_mask = res.mask;
    state.preprocess.grid_nx = res.nx;
    state.preprocess.grid_ny = res.ny;
    state.preprocess.grid_x0 = res.x0;
    state.preprocess.grid_y0 = res.y0;
    state.preprocess.grid_dx = res.dx;
    state.preprocess.grid_dy = res.dy;
    _ppStatus('pp-grid-status', `✓ 网格生成`, true);
    document.getElementById('pp-grid-info').innerHTML = `
        <div>网格: <strong>${res.nx} × ${res.ny}</strong> = ${res.n_total_cells} 格</div>
        <div>水域格数: <strong style="color:var(--info)">${res.n_water_cells}</strong> (${(res.water_ratio * 100).toFixed(1)}%)</div>
        <div>湖泊面积: <strong>${(res.lake_area_m2 / 1e6).toFixed(3)} km²</strong></div>
        <div>单元大小: ${res.dx}m × ${res.dy}m</div>`;
    drawGridPreview(res);
}

async function interpolateDepth() {
    if (!state.preprocess.grid_id || !state.preprocess.bathy_id) {
        _ppStatus('pp-interp-status', '请先上传边界/高程并生成网格', false); return;
    }
    const method = document.getElementById('pp-method').value;
    _ppStatus('pp-interp-status', '插值中...', true);
    const res = await api('/api/preprocess/bathymetry/interpolate', {
        method: 'POST',
        body: {
            grid_id: state.preprocess.grid_id,
            bathy_id: state.preprocess.bathy_id,
            method,
        },
    });
    if (res.error) { _ppStatus('pp-interp-status', '失败: ' + res.error, false); return; }
    state.preprocess.depth_array = res.depth_array;
    _ppStatus('pp-interp-status', '✓ 插值完成', true);
    document.getElementById('pp-depth-info').innerHTML = `
        <div>水域格数: <strong>${res.n_water_cells}</strong></div>
        <div>水深范围: <strong>${res.depth_min.toFixed(2)} ~ ${res.depth_max.toFixed(2)} m</strong></div>
        <div>平均水深: <strong>${res.depth_mean.toFixed(2)} m</strong></div>`;
    drawDepthPreview(res.depth_array, res.nx, res.ny);
}

async function saveBathymetry() {
    if (!state.preprocess.grid_id) { _ppStatus('pp-save-status', '请先生成网格', false); return; }
    if (!state.preprocess.depth_array) { _ppStatus('pp-save-status', '请先插值水深', false); return; }
    const caseName = document.getElementById('pp-case-name').value.trim();
    const lakeName = document.getElementById('pp-lake-name').value.trim();
    if (!caseName) { _ppStatus('pp-save-status', '请填案例名', false); return; }
    _ppStatus('pp-save-status', '保存中...', true);
    const res = await api('/api/preprocess/save', {
        method: 'POST',
        body: {
            case_name: caseName,
            grid_id: state.preprocess.grid_id,
            lake_name: lakeName || caseName,
            rivers: state.preprocess.rivers || [],
        },
    });
    if (res.error) { _ppStatus('pp-save-status', '失败: ' + res.error, false); return; }
    _ppStatus('pp-save-status', `✓ 已保存到 ${res.path}`, true);
    // Update topbar case badge so the user sees the case is now active
    state.activeCase = res.case_name;
    if (document.getElementById('case-badge')) {
        document.getElementById('case-badge').style.display = 'inline';
        document.getElementById('case-badge').textContent = res.case_name;
    }
    if (document.getElementById('footer-status')) {
        document.getElementById('footer-status').textContent = `案例: ${res.case_name}`;
    }
    document.getElementById('pp-depth-info').innerHTML += `
        <div style="margin-top:8px;color:var(--success);">案例 <strong>${res.case_name}</strong> 已加载</div>
        <div>水域格数: ${res.n_water_cells}，面积 ${(res.lake_area_m2 / 1e6).toFixed(3)} km²</div>
        <div style="margin-top:4px;font-size:11px;color:var(--text-muted);">下一步: 进入"输入数据"检查其它必需文件</div>`;
}

// ── Canvas drawing helpers ────────────────────────────────────────────
function _ppCanvasFit(canvasId, bbox) {
    // Returns { ctx, scale, ox, oy } mapping world bbox to canvas.
    const canvas = document.getElementById(canvasId);
    const ctx = canvas.getContext('2d');
    const cw = canvas.width, ch = canvas.height;
    const [xmin, ymin, xmax, ymax] = bbox;
    const w = Math.max(xmax - xmin, 1);
    const h = Math.max(ymax - ymin, 1);
    const pad = 12;
    const scale = Math.min((cw - 2 * pad) / w, (ch - 2 * pad) / h);
    const ox = pad + (cw - 2 * pad - w * scale) / 2;
    const oy = pad + (ch - 2 * pad - h * scale) / 2;
    // World → canvas: y is flipped (canvas y grows downward, world y upward)
    const tx = x => ox + (x - xmin) * scale;
    const ty = y => ch - (oy + (y - ymin) * scale);
    ctx.fillStyle = '#0a0c10';
    ctx.fillRect(0, 0, cw, ch);
    return { ctx, tx, ty, scale, cw, ch };
}

// Draws boundary ring(s) on a canvas. Accepts a flat point array (legacy
// single ring) or an array of rings (multi-part lake, e.g. 滇池外海+草海).
function _ppDrawBoundaryRings(ctx, rings, tx, ty, opts) {
    if (!rings || !rings.length) return;
    const ringList = (typeof rings[0][0] === 'number') ? [rings] : rings;
    ringList.forEach(ring => {
        if (!ring || ring.length < 3) return;
        ctx.beginPath();
        ring.forEach((p, i) => {
            const X = tx(p[0]), Y = ty(p[1]);
            if (i === 0) ctx.moveTo(X, Y); else ctx.lineTo(X, Y);
        });
        ctx.closePath();
        if (opts.fillStyle) {
            ctx.fillStyle = opts.fillStyle;
            ctx.fill();
        }
        ctx.strokeStyle = opts.strokeStyle;
        ctx.lineWidth = opts.lineWidth;
        ctx.stroke();
    });
}

function drawBoundaryPreview(rings, bbox) {
    if (!rings || !rings.length) return;
    const { ctx, tx, ty } = _ppCanvasFit('pp-boundary-canvas', bbox);
    _ppDrawBoundaryRings(ctx, rings, tx, ty, {
        strokeStyle: '#3b82f6', lineWidth: 1.5, fillStyle: 'rgba(59,130,246,0.15)',
    });
}

function drawBathymetryPreview(res) {
    const bbox = state.preprocess.bbox || [0, 0, 1, 1];
    const { ctx, tx, ty } = _ppCanvasFit('pp-bathy-canvas', bbox);
    // Draw boundary outline for context
    const bndRings = state.preprocess.boundary_rings || state.preprocess.boundary_preview;
    if (bndRings) {
        _ppDrawBoundaryRings(ctx, bndRings, tx, ty, {
            strokeStyle: 'rgba(255,255,255,0.3)', lineWidth: 1,
        });
    }
    const depths = res.preview_depths || [];
    if (res.geom_type === 'point') {
        const pts = res.preview_points || [];
        const dmin = res.depth_range[0], dmax = res.depth_range[1];
        const range = dmax - dmin || 1;
        pts.forEach((p, i) => {
            const d = depths[i];
            const t = (d - dmin) / range;
            ctx.fillStyle = _ppHeatColor(t);
            ctx.beginPath();
            ctx.arc(tx(p[0]), ty(p[1]), 3, 0, 2 * Math.PI);
            ctx.fill();
        });
    } else {
        const polys = res.preview_polygons || [];
        const dmin = res.depth_range[0], dmax = res.depth_range[1];
        const range = dmax - dmin || 1;
        polys.forEach((poly, i) => {
            const d = depths[i];
            const t = (d - dmin) / range;
            ctx.fillStyle = _ppHeatColor(t);
            ctx.beginPath();
            poly.forEach((p, j) => {
                const X = tx(p[0]), Y = ty(p[1]);
                if (j === 0) ctx.moveTo(X, Y); else ctx.lineTo(X, Y);
            });
            ctx.closePath();
            ctx.fill();
            ctx.strokeStyle = 'rgba(0,0,0,0.3)';
            ctx.lineWidth = 0.5;
            ctx.stroke();
        });
    }
}

function drawGridPreview(res) {
    const bbox = state.preprocess.bbox;
    const { ctx, tx, ty, scale, cw, ch } = _ppCanvasFit('pp-grid-canvas', bbox);
    // Draw boundary outline
    const bndRings = state.preprocess.boundary_rings || state.preprocess.boundary_preview;
    if (bndRings) {
        _ppDrawBoundaryRings(ctx, bndRings, tx, ty, {
            strokeStyle: '#ef4444', lineWidth: 1.2,
        });
    }
    // Draw grid cells: water=blue, land=grey
    const { nx, ny, mask, x0, y0, dx, dy } = res;
    const cellPxW = dx * scale;
    const cellPxH = dy * scale;
    // Skip rendering individual cells if grid is too dense (perf)
    const skipThreshold = 8000;  // nx*ny above this → just draw water mask as a single pass
    if (nx * ny <= skipThreshold) {
        for (let j = 0; j < ny; j++) {
            for (let i = 0; i < nx; i++) {
                const x = x0 + (i + 0.5) * dx;
                const y = y0 + (j + 0.5) * dy;
                const X = tx(x) - cellPxW / 2;
                const Y = ty(y) - cellPxH / 2;
                ctx.fillStyle = mask[j][i] ? 'rgba(59,130,246,0.55)' : 'rgba(120,120,130,0.25)';
                ctx.fillRect(X, Y, cellPxW + 0.5, cellPxH + 0.5);
            }
        }
    } else {
        // Fallback: rasterise mask via ImageData
        const img = ctx.createImageData(nx, ny);
        for (let j = 0; j < ny; j++) {
            for (let i = 0; i < nx; i++) {
                // ImageData 第 0 行渲染在画布顶部（北），而数据 j=0 在最南，需行翻转
                const idx = ((ny - 1 - j) * nx + i) * 4;
                if (mask[j][i]) {
                    img.data[idx] = 59; img.data[idx + 1] = 130; img.data[idx + 2] = 246; img.data[idx + 3] = 160;
                } else {
                    img.data[idx] = 80; img.data[idx + 1] = 80; img.data[idx + 2] = 90; img.data[idx + 3] = 80;
                }
            }
        }
        // Draw to an offscreen canvas then scale onto the main canvas
        const off = document.createElement('canvas');
        off.width = nx; off.height = ny;
        off.getContext('2d').putImageData(img, 0, 0);
        ctx.imageSmoothingEnabled = false;
        const x0px = tx(x0 + 0.5 * dx) - cellPxW / 2;
        const y0px = ty(y0 + (ny - 0.5) * dy) - cellPxH / 2;  // top edge in canvas space
        ctx.drawImage(off, x0px, y0px, nx * cellPxW, ny * cellPxH);
    }
}

function drawDepthPreview(depthArray, nx, ny) {
    // Find valid depth range (exclude -9999 land)
    let dmin = Infinity, dmax = -Infinity;
    for (let j = 0; j < ny; j++) {
        for (let i = 0; i < nx; i++) {
            const v = depthArray[j][i];
            if (v > -1000) { if (v < dmin) dmin = v; if (v > dmax) dmax = v; }
        }
    }
    if (!isFinite(dmin)) { dmin = 0; dmax = 1; }
    const range = dmax - dmin || 1;
    // Bake the depth raster once into an offscreen canvas; pan/zoom only
    // re-transforms this cached bitmap (fast redraws on wheel/drag).
    const img = document.createElement('canvas').getContext('2d').createImageData(nx, ny);
    for (let j = 0; j < ny; j++) {
        for (let i = 0; i < nx; i++) {
            const v = depthArray[j][i];
            // ImageData 第 0 行渲染在画布顶部（北），而数据 j=0 在最南，需行翻转
            const idx = ((ny - 1 - j) * nx + i) * 4;
            if (v <= -1000) {
                img.data[idx] = 26; img.data[idx + 1] = 28; img.data[idx + 2] = 39; img.data[idx + 3] = 255;
            } else {
                // 分级设色：量化为 N 级色块，保证相邻水深肉眼可区分
                const t = Math.max(0, Math.min(1, (v - dmin) / range));
                const lev = Math.min(_PP_DEPTH_LEVELS - 1, Math.floor(t * _PP_DEPTH_LEVELS));
                const [r, g, b] = _ppHeatColorRGB((lev + 0.5) / _PP_DEPTH_LEVELS);
                img.data[idx] = r; img.data[idx + 1] = g; img.data[idx + 2] = b; img.data[idx + 3] = 255;
            }
        }
    }
    const off = document.createElement('canvas');
    off.width = nx; off.height = ny;
    off.getContext('2d').putImageData(img, 0, 0);
    state.preprocess._depthOff = off;
    state.preprocess._depthDmin = dmin;
    state.preprocess._depthDmax = dmax;
    // Reset interaction state on new interpolation
    state.preprocess.view = null;
    if (!state.preprocess.rivers) state.preprocess.rivers = [];
    _ppBindDepthCanvas();
    _ppRedrawDepth();
    _ppRenderRiverList();
}

// ── Interactive depth map: zoom / pan / river marking ────────────────

// Compute the world→canvas transform honouring the current view state.
function _ppDepthTransform() {
    const canvas = document.getElementById('pp-depth-canvas');
    if (!canvas || !state.preprocess.bbox) return null;
    const cw = canvas.width, ch = canvas.height;
    const [xmin, ymin, xmax, ymax] = state.preprocess.bbox;
    const w = Math.max(xmax - xmin, 1), h = Math.max(ymax - ymin, 1);
    const pad = 12;
    const baseScale = Math.min((cw - 2 * pad) / w, (ch - 2 * pad) / h);
    const view = state.preprocess.view || {};
    const zoom = view.zoom || 1;
    const scale = baseScale * zoom;
    const cx = (view.cx != null) ? view.cx : (xmin + xmax) / 2;
    const cy = (view.cy != null) ? view.cy : (ymin + ymax) / 2;
    // Center the view point (cx, cy) on the canvas center
    const ox = cw / 2 - (cx - xmin) * scale;
    const oy = ch / 2 - (cy - ymin) * scale;
    const tx = x => ox + (x - xmin) * scale;                  // world → canvas x
    const ty = y => ch - (oy + (y - ymin) * scale);           // world → canvas y (flipped)
    const invX = X => (X - ox) / scale + xmin;                // canvas → world
    const invY = Y => ymin + (ch - Y - oy) / scale;
    return { ctx: canvas.getContext('2d'), tx, ty, invX, invY, scale, cw, ch, zoom };
}

function _ppRedrawDepth() {
    const T = _ppDepthTransform();
    if (!T || !state.preprocess._depthOff) return;
    const { ctx, tx, ty, scale, cw, ch } = T;
    ctx.fillStyle = '#0a0c10';
    ctx.fillRect(0, 0, cw, ch);
    const nx = state.preprocess.grid_nx, ny = state.preprocess.grid_ny;
    const x0 = state.preprocess.grid_x0, y0 = state.preprocess.grid_y0;
    const dx = state.preprocess.grid_dx, dy = state.preprocess.grid_dy;
    const cellPxW = dx * scale, cellPxH = dy * scale;
    ctx.imageSmoothingEnabled = false;
    const x0px = tx(x0 + 0.5 * dx) - cellPxW / 2;
    const y0px = ty(y0 + (ny - 0.5) * dy) - cellPxH / 2;
    ctx.drawImage(state.preprocess._depthOff, x0px, y0px, nx * cellPxW, ny * cellPxH);
    // Grid lines when sufficiently zoomed in
    if (cellPxW > 14 && cellPxH > 14) {
        ctx.strokeStyle = 'rgba(255,255,255,0.10)';
        ctx.lineWidth = 0.5;
        for (let i = 0; i <= nx; i++) {
            const X = tx(x0 + i * dx);
            ctx.beginPath(); ctx.moveTo(X, 0); ctx.lineTo(X, ch); ctx.stroke();
        }
        for (let j = 0; j <= ny; j++) {
            const Y = ty(y0 + j * dy);
            ctx.beginPath(); ctx.moveTo(0, Y); ctx.lineTo(cw, Y); ctx.stroke();
        }
    }
    // Boundary overlay
    const bndRings = state.preprocess.boundary_rings || state.preprocess.boundary_preview;
    if (bndRings) {
        _ppDrawBoundaryRings(ctx, bndRings, tx, ty, {
            strokeStyle: 'rgba(255,255,255,0.6)', lineWidth: 1,
        });
    }
    // River marks (▲ symbol + name)
    (state.preprocess.rivers || []).forEach(r => {
        const X = tx(x0 + (r.i - 0.5) * dx);
        const Y = ty(y0 + (r.j - 0.5) * dy);
        if (X < -20 || X > cw + 20 || Y < -20 || Y > ch + 20) return;
        ctx.fillStyle = '#22c55e';
        ctx.strokeStyle = '#052e16';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(X, Y - 9); ctx.lineTo(X - 7, Y + 5); ctx.lineTo(X + 7, Y + 5);
        ctx.closePath(); ctx.fill(); ctx.stroke();
        ctx.font = 'bold 11px "Microsoft YaHei", sans-serif';
        ctx.fillStyle = '#bbf7d0';
        ctx.textAlign = 'center';
        ctx.fillText(r.name, X, Y + 18);
    });
    // Legend + zoom hint
    _ppDrawDepthLegend(ctx, cw, ch, state.preprocess._depthDmin, state.preprocess._depthDmax, _PP_DEPTH_LEVELS);
    ctx.font = '10px "Microsoft YaHei", sans-serif';
    ctx.fillStyle = 'rgba(229,231,235,0.55)';
    ctx.textAlign = 'left';
    ctx.fillText(`缩放 ${T.zoom.toFixed(1)}×（滚轮缩放 / 拖拽平移${state.preprocess._riverMode ? ' / 标记模式：点击水域格' : ''}）`, 8, ch - 8);
}

// Bind wheel / drag / click handlers once per canvas element.
function _ppBindDepthCanvas() {
    const canvas = document.getElementById('pp-depth-canvas');
    if (!canvas || canvas._ppBound) return;
    canvas._ppBound = true;
    canvas.addEventListener('wheel', ev => {
        if (!state.preprocess._depthOff) return;
        ev.preventDefault();
        const T = _ppDepthTransform();
        if (!T) return;
        const rect = canvas.getBoundingClientRect();
        const mx = (ev.clientX - rect.left) * (canvas.width / rect.width);
        const my = (ev.clientY - rect.top) * (canvas.height / rect.height);
        const wx = T.invX(mx), wy = T.invY(my);
        const factor = ev.deltaY < 0 ? 1.18 : 1 / 1.18;
        const view = state.preprocess.view || (state.preprocess.view = {});
        const zoomOld = view.zoom || 1;
        const zoom = Math.max(1, Math.min(60, zoomOld * factor));
        // Keep the world point under the cursor stationary:
        // canvasX(x) = cw/2 + (x - cx)*scale, canvasY(y) = ch/2 + (cy - y)*scale
        // ⇒ new center satisfies mx = cw/2 + (wx - cx2)*s2, my = ch/2 + (cy2 - wy)*s2
        const s2 = T.scale * zoom / zoomOld;
        view.zoom = zoom;
        view.cx = wx + (T.cw / 2 - mx) / s2;
        view.cy = wy + (my - T.ch / 2) / s2;
        _ppRedrawDepth();
    }, { passive: false });
    // Pan by dragging
    let drag = null;
    canvas.addEventListener('mousedown', ev => {
        if (!state.preprocess._depthOff) return;
        drag = { x: ev.clientX, y: ev.clientY, moved: false };
    });
    window.addEventListener('mousemove', ev => {
        if (!drag) return;
        const dx = ev.clientX - drag.x, dy = ev.clientY - drag.y;
        if (Math.abs(dx) + Math.abs(dy) > 3) drag.moved = true;
        const T = _ppDepthTransform();
        if (!T) return;
        const view = state.preprocess.view || (state.preprocess.view = {});
        const cx = (view.cx != null) ? view.cx : (state.preprocess.bbox[0] + state.preprocess.bbox[2]) / 2;
        const cy = (view.cy != null) ? view.cy : (state.preprocess.bbox[1] + state.preprocess.bbox[3]) / 2;
        view.cx = cx - dx / T.scale;
        view.cy = cy + dy / T.scale;
        drag.x = ev.clientX; drag.y = ev.clientY;
        _ppRedrawDepth();
    });
    window.addEventListener('mouseup', () => { drag = null; });
    // Click to mark a river cell
    canvas.addEventListener('click', ev => {
        if (!state.preprocess._depthOff) return;
        if (!state.preprocess._riverMode) return;
        const T = _ppDepthTransform();
        if (!T) return;
        const rect = canvas.getBoundingClientRect();
        const mx = (ev.clientX - rect.left) * (canvas.width / rect.width);
        const my = (ev.clientY - rect.top) * (canvas.height / rect.height);
        const wx = T.invX(mx), wy = T.invY(my);
        const { grid_x0, grid_y0, grid_dx, grid_dy, grid_nx, grid_ny } = state.preprocess;
        const i = Math.floor((wx - grid_x0) / grid_dx) + 1;   // 1-based column
        const j = Math.floor((wy - grid_y0) / grid_dy) + 1;   // 1-based row
        if (i < 1 || i > grid_nx || j < 1 || j > grid_ny) { toast('点击位置在网格范围外', 'error'); return; }
        const depth = state.preprocess.depth_array[j - 1][i - 1];
        if (depth <= -1000) { toast(`(${i}, ${j}) 是陆地格点，请点击水域`, 'error'); return; }
        if ((state.preprocess.rivers || []).some(r => r.i === i && r.j === j)) {
            toast(`(${i}, ${j}) 已标记过河流`, 'warning'); return;
        }
        const name = prompt(`在格点 (i=${i}, j=${j}) 添加河流\n河流名（英文大写，如 PANLONGJING）：`, '');
        if (!name || !name.trim()) return;
        const clean = name.trim().toUpperCase();
        if (!/^[A-Z_][A-Z0-9_]{0,23}$/.test(clean)) { toast('河流名须为英文/数字/下划线', 'error'); return; }
        if ((state.preprocess.rivers || []).some(r => r.name === clean)) { toast(`河流名 ${clean} 已存在`, 'error'); return; }
        state.preprocess.rivers.push({ i, j, name: clean });
        _ppRedrawDepth();
        _ppRenderRiverList();
    });
}

function toggleRiverMarkMode() {
    state.preprocess._riverMode = !state.preprocess._riverMode;
    const btn = document.getElementById('pp-river-mode-btn');
    if (btn) {
        btn.textContent = state.preprocess._riverMode ? '🖱️ 标记模式: 开' : '🖱️ 标记模式: 关';
        btn.style.background = state.preprocess._riverMode ? 'var(--success)' : '';
        btn.style.color = state.preprocess._riverMode ? '#fff' : '';
    }
    const canvas = document.getElementById('pp-depth-canvas');
    if (canvas) canvas.style.cursor = state.preprocess._riverMode ? 'crosshair' : 'grab';
    _ppRedrawDepth();
}

function resetDepthView() {
    state.preprocess.view = null;
    _ppRedrawDepth();
}

function removePpRiver(idx) {
    state.preprocess.rivers.splice(idx, 1);
    _ppRedrawDepth();
    _ppRenderRiverList();
}

function _ppRenderRiverList() {
    const el = document.getElementById('pp-river-list');
    if (!el) return;
    const rivers = state.preprocess.rivers || [];
    if (!rivers.length) {
        el.innerHTML = '<div style="color:var(--text-muted);">暂无河流标记。开启标记模式后在图上点击水域格点。</div>';
        return;
    }
    el.innerHTML = rivers.map((r, k) =>
        `<div style="display:flex;align-items:center;gap:8px;padding:3px 0;border-bottom:1px solid var(--border);">
            <span style="color:var(--success);">▲</span>
            <strong>${r.name}</strong>
            <span style="color:var(--text-muted);">i=${r.i}, j=${r.j}</span>
            <button class="btn" style="padding:1px 8px;font-size:11px;margin-left:auto;" onclick="removePpRiver(${k})">删除</button>
        </div>`).join('');
}

// 离散色标：右侧竖向 colorbar，上=浅（dmin）下=深（dmax），标注每级边界值
function _ppDrawDepthLegend(ctx, cw, ch, dmin, dmax, nLevels) {
    const lw = 14;                                       // 色条宽度
    const rowH = Math.min(20, Math.max(11, (ch - 60) / nLevels));
    const totalH = rowH * nLevels;
    if (totalH < 44 || cw < 280) return;                 // 画布太小放不下则跳过
    const x0 = cw - 96;
    const y0 = (ch - totalH) / 2;
    // 背板 + 标题
    ctx.fillStyle = 'rgba(13,17,28,0.78)';
    ctx.fillRect(x0 - 10, y0 - 30, 86, totalH + 44);
    ctx.fillStyle = '#e5e7eb';
    ctx.font = '11px "Microsoft YaHei", sans-serif';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'alphabetic';
    ctx.fillText('水深 (m)', x0 - 3, y0 - 12);
    // 色块（自上而下 = 由浅到深）
    for (let k = 0; k < nLevels; k++) {
        const [r, g, b] = _ppHeatColorRGB((k + 0.5) / nLevels);
        ctx.fillStyle = `rgb(${r},${g},${b})`;
        ctx.fillRect(x0, y0 + k * rowH, lw, rowH + 0.5);
    }
    ctx.strokeStyle = 'rgba(255,255,255,0.35)';
    ctx.lineWidth = 1;
    ctx.strokeRect(x0, y0, lw, totalH);
    // 每级边界值标注
    ctx.fillStyle = '#d1d5db';
    ctx.font = '10px "Microsoft YaHei", sans-serif';
    for (let k = 0; k <= nLevels; k++) {
        const val = dmin + (dmax - dmin) * (k / nLevels);
        ctx.fillText(val.toFixed(1), x0 + lw + 6, y0 + k * rowH + 3);
    }
}

// 水深分级设色的级数（离散色块，相邻水深可肉眼区分）
const _PP_DEPTH_LEVELS = 10;

function _ppHeatColor(t) {
    const [r, g, b] = _ppHeatColorRGB(t);
    return `rgb(${r},${g},${b})`;
}

function _ppHeatColorRGB(t) {
    // ColorBrewer RdYlBu 11 段：t=0（浅）深蓝 → t=1（深）暗红
    const stops = [
        [5, 48, 97], [34, 94, 168], [65, 171, 193], [116, 196, 167],
        [171, 221, 164], [230, 245, 152], [255, 255, 191], [254, 224, 139],
        [253, 174, 97], [244, 109, 67], [202, 0, 32],
    ];
    const idx = t * (stops.length - 1);
    const lo = Math.floor(idx), hi = Math.min(lo + 1, stops.length - 1);
    const f = idx - lo;
    return [
        Math.round(stops[lo][0] + (stops[hi][0] - stops[lo][0]) * f),
        Math.round(stops[lo][1] + (stops[hi][1] - stops[lo][1]) * f),
        Math.round(stops[lo][2] + (stops[hi][2] - stops[lo][2]) * f),
    ];
}
