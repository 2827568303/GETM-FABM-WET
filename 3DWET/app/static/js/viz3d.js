// viz3d.js — Plotly 3D visualization module for 3DWET.
// Loaded on every page (small file), Plotly itself is vendored locally (index.html).
// Functions are called from the main app.js when the viz3d page is shown.
//
// 渲染方式（viz3d-iso-render 下拉切换）：
//   1) waterbody  ——【默认】立体水体：湖底地形面 + 逐层半透明分层面（可看到分层结构）
//                    + 四周水体剖面墙 + 垂向放大。这就是传统水动力模型 GUI 里
//                    那种"可旋转、能看到水体内部结构的三维视图"。
//   2) isosurface —— 等值面（Marching-Cubes，较重）
//   3) cloud      —— 点云（最快，逐点着色，但看不出"实体水体"感）
//   4) surface2d  —— 把 2D 场作为 3D 表面
//
// 所有渲染带令牌防重入 + 加载提示，避免快速切换时页面卡死。

const VIZ3D = {
    plotlyReady: () => typeof window.Plotly !== 'undefined',
    // Color palette for water quality fields
    colorScale: [
        [0, 'rgb(0,0,128)'], [0.2, 'rgb(0,128,255)'],
        [0.4, 'rgb(0,200,150)'], [0.6, 'rgb(255,220,0)'],
        [0.8, 'rgb(255,100,0)'], [1, 'rgb(200,0,0)']
    ],
    // 湖底/深度配色（浅→深）
    depthScale: [
        [0, 'rgb(120,210,180)'], [0.25, 'rgb(90,170,190)'],
        [0.5, 'rgb(60,120,175)'], [0.75, 'rgb(40,80,140)'], [1, 'rgb(20,40,90)']
    ],
    layout: {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { family: 'Microsoft YaHei, sans-serif', size: 11, color: '#cbd5e1' },
        scene: {
            xaxis: { title: 'X (m)', gridcolor: 'rgba(148,163,184,0.15)', zeroline: false, showbackground: false },
            yaxis: { title: 'Y (m)', gridcolor: 'rgba(148,163,184,0.15)', zeroline: false, showbackground: false },
            zaxis: { title: 'Depth (m)', gridcolor: 'rgba(148,163,184,0.15)', zeroline: false, showbackground: false },
            camera: { eye: { x: 1.35, y: -1.5, z: 0.75 } },
            aspectmode: 'data',
        },
        margin: { l: 0, r: 0, t: 30, b: 0 },
        legend: { font: { size: 10, color: '#cbd5e1' } },
    }
};

// 渲染令牌：避免快速切换时多次渲染叠加导致页面卡死
let _viz3dToken = 0;

function viz3dLoading(msg) {
    const c = document.getElementById('viz3d-plotly');
    if (c) c.innerHTML = `<div style="padding:20px;color:var(--text-muted);">${msg}</div>`;
}
function viz3dError(msg) {
    const c = document.getElementById('viz3d-plotly');
    if (c) c.innerHTML = `<div style="padding:20px;color:var(--danger);">${msg}</div>`;
}

/**
 * 把 sigma 坐标换算成「自水面算起的深度占比」depthFrac∈[0,1]（0=水面，1=湖底）。
 * GETM 的层序 k=0 为最底层：sigma=-1 对应湖底、sigma=0 对应水面。
 * 不同案例的 sigma 取值约定不同（[-1,0] / [0,1] / [-1,1]），这里按实际极值归一，
 * 保证 0 始终在水面、1 始终在湖底，避免整个水体上下颠倒。
 */
function sigmaToFraction(sigma) {
    let sMax = -Infinity, sMin = Infinity;
    (sigma || []).forEach(s => {
        if (typeof s === 'number' && isFinite(s)) { if (s > sMax) sMax = s; if (s < sMin) sMin = s; }
    });
    if (!isFinite(sMax)) {
        return (sigma || []).map((_, k) => k / Math.max(1, (sigma || []).length - 1));
    }
    const span = (sMax - sMin) || 1;
    return (sigma || []).map(s => {
        if (typeof s !== 'number' || !isFinite(s)) return 1;
        return (sMax - s) / span;      // sigma=sMax(水面) → 0；sigma=sMin(湖底) → 1
    });
}

/**
 * 沿水体外缘构建"水体剖面墙"三角面（mesh3d 用）。
 * 只取有水的边界格，陆地格自动跳过，避免出现伸到湖外的墙。
 */
function buildWaterWalls(xc, yc, bottom, ve, zTopFrac) {
    const nx = xc.length, ny = yc.length;
    if (!bottom || bottom.length !== ny || !bottom[0] || bottom[0].length !== nx) return null;
    const isWater = (i, j) => {
        const h = bottom[j] && bottom[j][i];
        return (h !== null && h !== undefined && typeof h === 'number' && !isNaN(h) && h > 1e-6);
    };
    const zAt = (i, j) => -bottom[j][i] * ve * (zTopFrac === undefined ? 1 : zTopFrac);

    const px = [], py = [], pz = [], cint = [], tri = [];
    const pushSeg = (i0, j0, i1, j1) => {
        if (!isWater(i0, j0) || !isWater(i1, j1)) return;
        const z0 = zAt(i0, j0), z1 = zAt(i1, j1);
        const base = px.length;
        // 顺序：A_top, A_bot, B_top, B_bot
        px.push(xc[i0], xc[i0], xc[i1], xc[i1]);
        py.push(yc[j0], yc[j0], yc[j1], yc[j1]);
        pz.push(0, z0, 0, z1);
        const depth0 = isFinite(bottom[j0][i0]) ? bottom[j0][i0] : 0;
        const depth1 = isFinite(bottom[j1][i1]) ? bottom[j1][i1] : 0;
        const dmax = Math.max(depth0, depth1, 1e-6);
        cint.push(depth0 / dmax, 0, depth1 / dmax, 0);
        tri.push(base, base + 1, base + 3, base, base + 3, base + 2);
        };
    // 沿四条边按"连续水格"分段，段内逐段成墙
    const runs = [];
    const addRun = (cells) => {
        let cur = [];
        cells.forEach(([i, j]) => {
            if (isWater(i, j)) cur.push([i, j]);
            else { if (cur.length > 1) runs.push(cur); cur = []; }
        });
        if (cur.length > 1) runs.push(cur);
    };
    const cellsY = [], cellsX = [];
    for (let i = 0; i < nx; i++) { cellsY.push([i, 0]); cellsY.push([i, ny - 1]); }
    for (let j = 0; j < ny; j++) { cellsX.push([0, j]); cellsX.push([nx - 1, j]); }
    addRun(cellsY); addRun(cellsX);
    runs.forEach(run => {
        for (let k = 0; k + 1 < run.length; k++) pushSeg(run[k][0], run[k][1], run[k + 1][0], run[k + 1][1]);
    });
    if (!tri.length) return null;
    return { px, py, pz, cint, i: tri.filter((_, k) => k % 3 === 0), j: tri.filter((_, k) => k % 3 === 1), k: tri.filter((_, k) => k % 3 === 2), color: cint };
}

/**
 * 【默认】立体水体渲染：湖底地形 + 逐层叠放的半透明分层面 + 四周水体剖面墙。
 * 可旋转/缩放，直观看到湖盆形态与垂向分层结构（温跃层等）。
 */
async function render3DWaterBody(varName, timestep, opts = {}) {
    const containerId = 'viz3d-plotly';
    const container = document.getElementById(containerId);
    if (!container) return;
    if (!VIZ3D.plotlyReady()) { viz3dError('Plotly 未加载（本地 vendor 缺失或被拦截）。'); return; }
    const token = ++_viz3dToken;
    viz3dLoading('加载立体水体数据中...');
    const target = opts.target || 22;
    const ve = Math.max(1, Number(opts.ve) || 100);
    const stack = opts.stack !== false;
    const url = `/api/results/3d_surface?var=${encodeURIComponent(varName)}&time=${timestep}&target=${target}`;
    try {
        const res = await fetch(url);
        if (token !== _viz3dToken) return;
        const d = await res.json();
        if (token !== _viz3dToken) return;
        if (d.error) { viz3dError(d.error); return; }
        const vol = d.data, shape = d.shape;
        const nz = shape[0], ny = shape[1], nx = shape[2];
        let vmin = d.min, vmax = d.max;
        if (!isFinite(vmin) || !isFinite(vmax)) { viz3dError('该时步无有效数据（全为空值）'); return; }
        const range = (vmax - vmin) || 1;

        const xc = d.xc && d.xc.length === nx ? d.xc : Array.from({ length: nx }, (_, i) => i);
        const yc = d.yc && d.yc.length === ny ? d.yc : Array.from({ length: ny }, (_, j) => j);
        const bottom = d.bottom;
        let dfc = sigmaToFraction((d.sigma || Array.from({ length: nz }, (_, k) => 1 - 2 * k / Math.max(1, nz - 1))).slice());
        if (!dfc || dfc.length !== nz) dfc = Array.from({ length: nz }, (_, k) => k / Math.max(1, nz - 1));

        const hasBathy = bottom && bottom.length === ny && bottom[0] && bottom[0].length === nx;
        const H = [];
        if (hasBathy) for (let j = 0; j < ny; j++) { H.push([]); for (let i = 0; i < nx; i++) { const h = bottom[j][i]; H[j].push((h === null || h === undefined || isNaN(h)) ? null : h); } }
        else { const hmax = vmax; for (let j = 0; j < ny; j++) { H.push([]); for (let i = 0; i < nx; i++) H[j].push(hmax); } }

        // 选中层（默认最上层）
        const lv = Math.max(0, Math.min(nz - 1, Number(opts.level) >= 0 ? Number(opts.level) : nz - 1));

        const traces = [];

        // ── 1) 湖底地形（不透明，按水深着色） ──────────────────────────
        const zBottom = [], depthCol = [];
        for (let j = 0; j < ny; j++) {
            zBottom.push([]); depthCol.push([]);
            for (let i = 0; i < nx; i++) {
                const h = H[j][i];
                const has = (h !== null && h !== undefined && !isNaN(h));
                zBottom[j].push(has ? -h * ve : null);
                depthCol[j].push(has ? h : null);
            }
        }
        traces.push({
            type: 'surface', name: '湖底地形',
            x: xc, y: yc, z: zBottom,
            surfacecolor: depthCol,
            colorscale: VIZ3D.depthScale, showscale: false,
            opacity: 1, connectgaps: false, hoverinfo: 'skip',
        });

        // ── 2) 逐层叠放的分层面（自底向上，越靠下越透明） ────────────────
        if (stack) {
            for (let k = 0; k <= lv; k++) {
                const zl = [];
                for (let j = 0; j < ny; j++) {
                    zl.push([]);
                    for (let i = 0; i < nx; i++) zl[j].push(H[j][i] === null ? null : -H[j][i] * dfc[k] * ve);
                }
                const isTop = (k === lv);
                traces.push({
                    type: 'surface',
                    name: `层 ${k} (σ=${(d.sigma || [])[k] !== undefined ? Number((d.sigma || [])[k]).toFixed(2) : k})`,
                    x: xc, y: yc, z: zl,
                    surfacecolor: vol[k].map((row) => row.map(v => (v === null || v === undefined || isNaN(v)) ? null : v)),
                    colorscale: VIZ3D.colorScale, cmin: vmin, cmax: vmax,
                    showscale: isTop,
                    opacity: isTop ? 0.95 : 0.28,
                    connectgaps: false,
                    hoverinfo: 'skip',
                    colorbar: isTop ? { title: { text: d.units || '' }, len: 0.6 } : undefined,
                });
            }
        } else {
            const zl = [];
            for (let j = 0; j < ny; j++) {
                zl.push([]);
                for (let i = 0; i < nx; i++) zl[j].push(H[j][i] === null ? null : -H[j][i] * dfc[lv] * ve);
            }
            traces.push({
                type: 'surface', name: `层 ${lv}`,
                x: xc, y: yc, z: zl,
                surfacecolor: vol[lv].map((row) => row.map(v => (v === null || v === undefined || isNaN(v)) ? null : v)),
                colorscale: VIZ3D.colorScale, cmin: vmin, cmax: vmax,
                showscale: true, opacity: 0.95, connectgaps: false,
                colorbar: { title: { text: d.units || '' } },
            });
        }

        // ── 3) 四周水体剖面墙（半透明，按水深着色） ─────────────────────
        const walls = buildWaterWalls(xc, yc, hasBathy ? H : null, ve, 1);
        if (walls) {
            traces.push({
                type: 'mesh3d', name: '水体剖面',
                x: walls.px, y: walls.py, z: walls.pz,
                i: walls.i, j: walls.j, k: walls.k,
                color: walls.color, colorscale: VIZ3D.depthScale,
                opacity: 0.35, flatshading: true, showscale: false, hoverinfo: 'skip',
            });
        }

        const layout = Object.assign({}, VIZ3D.layout, {
            title: `${d.long_name || varName} 立体水体　时步 ${timestep}　层 ${lv}/${nz - 1}　${stack ? '叠层显示' : '单层'}　垂向放大 ${ve}×`,
            scene: Object.assign({}, VIZ3D.layout.scene, {
                zaxis: Object.assign({}, VIZ3D.layout.scene.zaxis, { title: `深度 (m, ×${ve})` }),
            }),
            showlegend: true,
        });
        Plotly.newPlot(containerId, traces, layout, {
            responsive: true, displayModeBar: true, displaylogo: false,
            toImageButtonOptions: { format: 'png', filename: `3dwet_waterbody_${varName}_t${timestep}` },
        });
    } catch (e) {
        if (token === _viz3dToken) viz3dError(`加载失败: ${e.message}`);
    }
}

/**
 * Render a fast 3D point cloud (scatter3d) for the given variable/timestep.
 */
async function render3DCloud(varName, timestep, target = 22) {
    const containerId = 'viz3d-plotly';
    const container = document.getElementById(containerId);
    if (!container) return;
    if (!VIZ3D.plotlyReady()) {
        viz3dError('Plotly 未加载（本地 vendor 缺失或被拦截）。3D 视图不可用，2D 视图不受影响。');
        return;
    }
    const token = ++_viz3dToken;
    viz3dLoading('加载3D点云数据中...');
    const url = `/api/results/3d_surface?var=${encodeURIComponent(varName)}&time=${timestep}&target=${target}`;
    try {
        const res = await fetch(url);
        if (token !== _viz3dToken) return;
        const data = await res.json();
        if (token !== _viz3dToken) return;
        if (data.error) { viz3dError(data.error); return; }
        const { data: vol, shape, min, max, long_name, units } = data;
        if (!Number.isFinite(min) || !Number.isFinite(max)) {
            viz3dError('该时步无有效数据（全为空值）');
            return;
        }
        const nz = shape[0], ny = shape[1], nx = shape[2];
        const xs = [], ys = [], zs = [], vs = [];
        for (let k = 0; k < nz; k++) {
            for (let j = 0; j < ny; j++) {
                for (let i = 0; i < nx; i++) {
                    const v = vol[k][j][i];
                    if (v === null || v === undefined || isNaN(v)) continue;
                    xs.push(i); ys.push(j); zs.push(k); vs.push(v);
                }
            }
        }
        if (!xs.length) { viz3dError('该时步全为空值（陆地格）'); return; }
        const trace = {
            type: 'scatter3d',
            mode: 'markers',
            x: xs, y: ys, z: zs,
            marker: {
                size: 2.4,
                color: vs,
                colorscale: VIZ3D.colorScale,
                cmin: min, cmax: max,
                opacity: 0.85,
                colorbar: { title: { text: units || '' } },
            },
            name: long_name,
            hoverinfo: 'x+y+z+text',
            text: vs.map(v => v.toFixed(3)),
        };
        const layout = Object.assign({}, VIZ3D.layout, {
            title: `${long_name} (${varName})  时步 ${timestep}  点云 ${xs.length} 点  范围 ${min.toFixed(3)}~${max.toFixed(3)} ${units || ''}`,
        });
        Plotly.newPlot(containerId, [trace], layout, {
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            toImageButtonOptions: { format: 'png', filename: `3dwet_cloud_${varName}_t${timestep}` },
        });
    } catch (e) {
        if (token === _viz3dToken) viz3dError(`加载失败: ${e.message}`);
    }
}

/**
 * Render a 3D isosurface (heavier mode, optional).
 */
async function render3DSurface(varName, timestep, target = 18) {
    const containerId = 'viz3d-plotly';
    const container = document.getElementById(containerId);
    if (!container) return;
    if (!VIZ3D.plotlyReady()) {
        viz3dError('Plotly 未加载（本地 vendor 缺失或被拦截）。');
        return;
    }
    const token = ++_viz3dToken;
    viz3dLoading('计算等值面中（较重，请稍候）...');
    const url = `/api/results/3d_surface?var=${encodeURIComponent(varName)}&time=${timestep}&target=${target}`;
    try {
        const res = await fetch(url);
        if (token !== _viz3dToken) return;
        const data = await res.json();
        if (token !== _viz3dToken) return;
        if (data.error) { viz3dError(data.error); return; }
        const { data: vol, shape, x, y, z, min, max, long_name, units } = data;
        if (!Number.isFinite(min) || !Number.isFinite(max)) {
            viz3dError('该时步无有效数据（全为空值）');
            return;
        }
        const nz = shape[0], ny = shape[1], nx = shape[2];
        const range = max - min || 1;
        const fillValue = min - range * 0.1 - 1e-6;
        const values = [];
        for (let k = 0; k < nz; k++) {
            for (let j = 0; j < ny; j++) {
                for (let i = 0; i < nx; i++) {
                    const v = vol[k][j][i];
                    values.push((v === null || v === undefined || isNaN(v)) ? fillValue : v);
                }
            }
        }
        const isoLevels = [min + range * 0.4, min + range * 0.7];
        const traces = isoLevels.map((iso, idx) => ({
            type: 'isosurface',
            x: x, y: y, z: z,
            value: values,
            isomin: iso,
            isomax: iso + range * 0.05,
            colorscale: VIZ3D.colorScale,
            cmin: min,
            cmax: max,
            showscale: idx === isoLevels.length - 1,
            opacity: 0.4 + 0.2 * idx,
            surface: { fill: 1, show: true },
            caps: { x: { show: false }, y: { show: false }, z: { show: false } },
            name: `${long_name} = ${iso.toFixed(3)}`,
        }));
        const layout = Object.assign({}, VIZ3D.layout, {
            title: `${long_name} (${varName})  时步 ${timestep}  范围 ${min.toFixed(3)} ~ ${max.toFixed(3)} ${units || ''}`,
        });
        Plotly.newPlot(containerId, traces, layout, {
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            toImageButtonOptions: { format: 'png', filename: `3dwet_${varName}_t${timestep}` },
        });
    } catch (e) {
        if (token === _viz3dToken) viz3dError(`加载失败: ${e.message}`);
    }
}

/**
 * Render a 2D heatmap as a Plotly surface plot (alternative 3D view of a 2D field).
 */
async function render2DAs3DSurface(varName, timestep, level) {
    const containerId = 'viz3d-plotly';
    const container = document.getElementById(containerId);
    if (!container) return;
    if (!VIZ3D.plotlyReady()) { viz3dError('Plotly 不可用'); return; }
    const token = ++_viz3dToken;
    viz3dLoading('加载2D场数据...');
    const url = `/api/results/2d?var=${encodeURIComponent(varName)}&time=${timestep}&level=${level}`;
    try {
        const res = await fetch(url);
        if (token !== _viz3dToken) return;
        const data = await res.json();
        if (token !== _viz3dToken) return;
        if (data.error) { viz3dError(data.error); return; }
        const rows = data.data ? data.data.length : 0;
        if (!rows || !Number.isFinite(data.min) || !Number.isFinite(data.max)) {
            viz3dError('该时步无有效数据（全为空值或输出没有时间记录）');
            return;
        }
        const trace = {
            type: 'surface',
            z: data.data,
            colorscale: VIZ3D.colorScale,
            cmin: data.min,
            cmax: data.max,
            showscale: true,
            colorbar: { title: { text: data.units || '' } },
        };
        const layout = Object.assign({}, VIZ3D.layout, {
            title: `${varName}  时步 ${timestep}  层 ${level}  范围 ${data.min.toFixed(3)} ~ ${data.max.toFixed(3)}`,
            scene: Object.assign({}, VIZ3D.layout.scene, {
                xaxis: Object.assign({}, VIZ3D.layout.scene.xaxis, { title: 'X (i)' }),
                yaxis: Object.assign({}, VIZ3D.layout.scene.yaxis, { title: 'Y (j)' }),
                zaxis: Object.assign({}, VIZ3D.layout.scene.zaxis, { title: varName }),
            }),
        });
        Plotly.newPlot(containerId, [trace], layout, { responsive: true, displaylogo: false });
    } catch (e) {
        if (token === _viz3dToken) viz3dError(`加载失败: ${e.message}`);
    }
}

function var_name_label(name) {
    return name;
}

// 湖盆地形占位渲染：尚无模型结果时，3D 视图也能看到湖泊形态（z = -水深）
async function renderBathymetry3D() {
    const containerId = 'viz3d-plotly';
    const container = document.getElementById(containerId);
    if (!container) return;
    if (!VIZ3D.plotlyReady()) { viz3dError('Plotly 不可用'); return; }
    const token = ++_viz3dToken;
    viz3dLoading('加载地形数据...');
    try {
        const res = await fetch('/api/geo/grid');
        if (token !== _viz3dToken) return;
        const g = await res.json();
        if (token !== _viz3dToken) return;
        if (g.error) { viz3dError(g.error); return; }
        const z = g.depth.map(row => row.map(v => (v == null ? null : -v)));
        const trace = {
            type: 'surface',
            z: z,
            colorscale: VIZ3D.depthScale,
            showscale: true,
            colorbar: { title: { text: '水深 (m)' } },
        };
        const layout = Object.assign({}, VIZ3D.layout, {
            title: '湖盆地形（bathymetry.nc，尚无模型结果时的占位显示）',
            scene: Object.assign({}, VIZ3D.layout.scene, {
                zaxis: Object.assign({}, VIZ3D.layout.scene.zaxis, { title: '水深 (m)' }),
            }),
        });
        Plotly.newPlot(containerId, [trace], layout, { responsive: true, displaylogo: false });
    } catch (e) {
        if (token === _viz3dToken) viz3dError(`加载失败: ${e.message}`);
    }
}
