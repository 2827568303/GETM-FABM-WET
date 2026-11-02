// Small rolling browser-side measurements for successfully displayed playback frames.
(function (root) {
  'use strict';
  const histories = new Map();
  const limit = 60;
  const now = () => root.performance?.now?.() ?? Date.now();
  const quantile = (values, fraction) => {
    if (!values.length) return null;
    const sorted = [...values].sort((a, b) => a - b);
    return sorted[Math.min(sorted.length - 1, Math.ceil(fraction * sorted.length) - 1)];
  };
  function startSession(kind, options = {}) {
    const targetFps = Number(options.targetFps) || 1;
    const history = histories.get(kind);
    const sameTarget = history && history.targetFps === targetFps;
    if (!options.resume || !sameTarget) {
      histories.set(kind, { frames: [], lastEndedAt: null, targetFps, cadenceStartIndex: 0 });
    } else {
      // A pause is not part of the playback cadence. Keep the frame work
      // history, but make the first resumed frame a new interval segment.
      history.lastEndedAt = null;
      history.cadenceStartIndex = history.frames.length;
    }
    updateDisplay(kind);
  }
  function begin(kind, frame, targetFps, playing) {
    if (!playing) return null;
    return { kind, frame, targetFps: Number(targetFps) || 1, startedAt: now(), stages: {} };
  }
  function stage(ticket, name, durationMs) {
    if (!ticket || !Number.isFinite(Number(durationMs))) return;
    ticket.stages[name] = Math.max(0, Number(durationMs));
  }
  function finish(ticket) {
    if (!ticket) return null;
    const endedAt = now();
    let history = histories.get(ticket.kind);
    if (!history) { history = { frames: [], lastEndedAt: null, targetFps: ticket.targetFps, cadenceStartIndex: 0 }; histories.set(ticket.kind, history); }
    const frameMs = Math.max(0, endedAt - ticket.startedAt);
    const record = { frame: ticket.frame, targetFps: ticket.targetFps, frameMs,
      intervalMs: history.lastEndedAt === null ? null : Math.max(0, endedAt - history.lastEndedAt),
      stages: { ...ticket.stages } };
    history.lastEndedAt = endedAt;
    history.frames.push(record);
    if (history.frames.length > limit) {
      history.frames.shift();
      // Keep cadenceStartIndex relative to the retained rolling window.
      // Otherwise a long session leaves an absolute index > frames.length,
      // causing the current session's cadence intervals to disappear.
      history.cadenceStartIndex = Math.max(0, history.cadenceStartIndex - 1);
    }
    updateDisplay(ticket.kind);
    return record;
  }
  function snapshot(kind) {
    const records = histories.get(kind)?.frames || [];
    const durations = records.map(row => row.frameMs);
    const cadenceStartIndex = histories.get(kind)?.cadenceStartIndex || 0;
    const intervals = records.slice(cadenceStartIndex).map(row => row.intervalMs).filter(Number.isFinite);
    const averageInterval = intervals.length ? intervals.reduce((sum, value) => sum + value, 0) / intervals.length : null;
    const targetFps = records.at(-1)?.targetFps || null;
    const targetMs = targetFps ? 1000 / targetFps : null;
    return { frames: records.length, targetFps,
      actualFps: averageInterval ? 1000 / averageInterval : null,
      medianFrameMs: quantile(durations, .5), p95FrameMs: quantile(durations, .95),
      overBudgetFrames: targetMs ? records.filter(row => row.frameMs > targetMs).length : 0,
      slowFrames: targetMs ? records.filter(row => Number.isFinite(row.intervalMs) && row.intervalMs > targetMs * 1.1).length : 0,
      last: records.at(-1) || null, records: records.map(row => ({ ...row, stages: { ...row.stages } })) };
  }
  function format(kind) {
    const data = snapshot(kind);
    if (!data.frames) return '';
    const n = value => Number.isFinite(value) ? Math.round(value) : '—';
    const stages = data.last?.stages || {};
    const fps = data.actualFps ? data.actualFps.toFixed(1) : '—';
    return `目标 ${data.targetFps} fps · 实际 ${fps} fps · 成功帧 ${data.frames} · 整帧 ${n(data.last.frameMs)} ms（P50 ${n(data.medianFrameMs)} / P95 ${n(data.p95FrameMs)}） · 绘制超预算 ${data.overBudgetFrames}/${data.frames} · 帧间隔超目标10% ${data.slowFrames} · 请求 ${n(stages.request)} / 解码 ${n(stages.decode)} / 湖盆 ${n(stages.geometry)} / 静态迹线 ${n(stages.baseTraces)} / 角点均值 ${n(stages.cornerAverages)} / 网格数组 ${n(stages.layerMesh)} / trace组装 ${n(stages.traceAssembly)} / 网络网格 ${n(stages.networkMesh)} / 网格线 ${n(stages.displayLines)} / 变量网格合计 ${n(stages.fieldMesh)} / CPU组装 ${n(stages.assemble)}（帧准备 ${n(stages.frameBuild)} + Plotly准备 ${n(stages.plotPrepare)}：文本${n(stages.plotTranslate)}、布局${n(stages.plotLayout)}、schema${n(stages.plotSchema)}）/ 绘制队列等待 ${n(stages.queueWait)} / 绘图 ${n(stages.draw)} ms`;
  }
  function updateDisplay(kind) {
    const host = root.document?.getElementById?.(kind + '-play-perf');
    if (host) host.textContent = format(kind);
  }
  root.PlaybackPerformance = { begin, stage, finish, startSession, snapshot, format, reset(kind) {
    if (kind) histories.delete(kind); else histories.clear();
  } };
})(typeof window !== 'undefined' ? window : globalThis);
