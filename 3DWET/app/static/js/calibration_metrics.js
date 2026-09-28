// 3DWET - Calibration metrics and scatter plot helpers
// Calculates RMSE, NSE, R², PBIAS, MAE between observed and simulated series.

/**
 * Pair observed and simulated time series by nearest timestamp.
 *
 * @param {Array<{time:string,value:number}>} obs - observed series
 * @param {{times:string[], values:(number|null)[]}} sim - simulated series
 * @param {number} maxLagSec - max allowed match lag in seconds (default 1 day)
 * @returns {Array<{time:string, obs:number, sim:number}>}
 */
function pairObsSim(obs, sim, maxLagSec = 86400) {
    if (!obs || !obs.length || !sim || !sim.times || !sim.times.length) return [];
    const simTimes = sim.times.map(t => new Date(t).getTime());
    const simVals = sim.values;
    const pairs = [];
    for (const o of obs) {
        const ot = new Date(o.time).getTime();
        if (isNaN(ot)) continue;
        let bestIdx = -1, bestLag = Infinity;
        for (let i = 0; i < simTimes.length; i++) {
            const lag = Math.abs(simTimes[i] - ot);
            if (lag < bestLag) { bestLag = lag; bestIdx = i; }
        }
        if (bestIdx < 0 || bestLag > maxLagSec * 1000) continue;
        const sv = simVals[bestIdx];
        if (sv === null || sv === undefined || isNaN(sv)) continue;
        pairs.push({ time: sim.times[bestIdx], obs: Number(o.value), sim: sv });
    }
    return pairs;
}

/**
 * Compute calibration metrics from paired series.
 *
 * @param {number[]} obs - observed values (same length as sim)
 * @param {number[]} sim - simulated values
 * @returns {{n:number, rmse:number, mae:number, nse:number, r2:number, pbias:number}}
 */
function computeMetrics(obs, sim) {
    const n = Math.min(obs.length, sim.length);
    if (!n) return { n: 0, rmse: NaN, mae: NaN, nse: NaN, r2: NaN, pbias: NaN };
    let sumErr2 = 0, sumAbsErr = 0, sumSimMinusObs = 0, sumObs = 0;
    let sumO = 0, sumS = 0, sumO2 = 0, sumS2 = 0, sumOS = 0;
    let count = 0;
    for (let i = 0; i < n; i++) {
        const o = obs[i], s = sim[i];
        if (o === null || o === undefined || isNaN(o) ||
            s === null || s === undefined || isNaN(s)) continue;
        const e = s - o;
        sumErr2 += e * e;
        sumAbsErr += Math.abs(e);
        sumSimMinusObs += e;
        sumObs += o;
        sumO += o; sumS += s;
        sumO2 += o * o; sumS2 += s * s; sumOS += o * s;
        count++;
    }
    if (!count) return { n: 0, rmse: NaN, mae: NaN, nse: NaN, r2: NaN, pbias: NaN };
    const rmse = Math.sqrt(sumErr2 / count);
    const mae = sumAbsErr / count;
    const obsMean = sumObs / count;
    let denomNSE = 0;
    for (let i = 0; i < n; i++) {
        const o = obs[i], s = sim[i];
        if (o === null || o === undefined || isNaN(o) ||
            s === null || s === undefined || isNaN(s)) continue;
        denomNSE += (o - obsMean) * (o - obsMean);
    }
    const nse = denomNSE > 0 ? 1 - (sumErr2 / denomNSE) : NaN;
    // R² = (Pearson r)^2
    const meanO = sumO / count, meanS = sumS / count;
    const covOS = (sumOS / count) - (meanO * meanS);
    const varO = (sumO2 / count) - (meanO * meanO);
    const varS = (sumS2 / count) - (meanS * meanS);
    const r = (varO > 0 && varS > 0) ? covOS / Math.sqrt(varO * varS) : NaN;
    const r2 = (r === null || r === undefined || isNaN(r)) ? NaN : r * r;
    const pbias = sumObs > 0 ? 100 * (sumSimMinusObs / sumObs) : NaN;
    return { n: count, rmse, mae, nse, r2, pbias };
}

function fmtMetric(v, d = 4) {
    if (v === null || v === undefined || isNaN(v)) return '—';
    return Number(v).toFixed(d);
}

function nseColor(nse) {
    if (isNaN(nse)) return 'var(--text-muted)';
    if (nse >= 0.75) return 'var(--success)';
    if (nse >= 0.5) return '#fbbf24';
    if (nse >= 0) return '#f97316';
    return 'var(--danger)';
}

function renderMetricsHTML(metrics) {
    const nseStyle = `color:${nseColor(metrics.nse)};font-weight:600;`;
    return `
        <div class="metrics-grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:8px;">
            <div class="metric-item"><span class="metric-label">配对点数</span><span class="metric-value">${metrics.n}</span></div>
            <div class="metric-item"><span class="metric-label">RMSE</span><span class="metric-value">${fmtMetric(metrics.rmse)}</span></div>
            <div class="metric-item"><span class="metric-label">MAE</span><span class="metric-value">${fmtMetric(metrics.mae)}</span></div>
            <div class="metric-item"><span class="metric-label">NSE</span><span class="metric-value" style="${nseStyle}">${fmtMetric(metrics.nse, 3)}</span></div>
            <div class="metric-item"><span class="metric-label">R²</span><span class="metric-value">${fmtMetric(metrics.r2, 3)}</span></div>
            <div class="metric-item"><span class="metric-label">PBIAS (%)</span><span class="metric-value">${fmtMetric(metrics.pbias, 2)}</span></div>
        </div>
        <div style="margin-top:6px;font-size:11px;color:var(--text-muted);">
            NSE: ≥0.75 优秀 / 0.5-0.75 良好 / 0-0.5 一般 / &lt;0 差
        </div>`;
}
