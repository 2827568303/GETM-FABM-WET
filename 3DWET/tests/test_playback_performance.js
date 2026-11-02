const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const source = fs.readFileSync('3DWET/app/static/js/playback_performance.js', 'utf8');
let now = 0;
const window = { performance: { now: () => now } };
vm.runInNewContext(source, { window, performance: window.performance, document: { getElementById: () => null } });
const perf = window.PlaybackPerformance;

const appSource = fs.readFileSync('3DWET/app/static/js/app.js', 'utf8');
const viz3dSource = fs.readFileSync('3DWET/app/static/js/viz3d.js', 'utf8');
assert.match(appSource, /perfTicket=perf\?\.begin\('viz2d'/, '2D updates must start frame telemetry');
assert.match(appSource, /perf\?\.stage\(perfTicket,'request'/, '2D records request timing');
assert.match(appSource, /perf\?\.stage\(perfTicket,'decode'/, '2D records JSON decode timing');
assert.match(appSource, /perf\?\.stage\(perfTicket,'assemble'/, '2D records assembly timing');
assert.match(appSource, /perf\?\.stage\(perfTicket,'draw'/, '2D records canvas drawing timing');
assert.match(viz3dSource, /PlaybackPerformance\?\.begin\('viz3d'/, '3D requests must start frame telemetry');
assert.match(viz3dSource, /PlaybackPerformance\?\.stage\(request\?\.playbackPerf,'request'/, '3D records request timing');
assert.match(viz3dSource, /PlaybackPerformance\?\.stage\(request\?\.playbackPerf,'decode'/, '3D records JSON decode timing');
assert.match(viz3dSource, /PlaybackPerformance\?\.stage\(request\.playbackPerf,'assemble'/, '3D records assembly timing');
assert.match(viz3dSource, /PlaybackPerformance\?\.stage\(request\.playbackPerf,'geometry'/, '3D splits geometry construction timing');
assert.match(viz3dSource, /PlaybackPerformance\?\.stage\(request\.playbackPerf,'baseTraces'/, '3D splits static trace assembly timing');
assert.match(viz3dSource, /PlaybackPerformance\?\.stage\(request\.playbackPerf,'fieldMesh'/, '3D splits field mesh construction timing');
assert.match(viz3dSource, /PlaybackPerformance\?\.stage\(request\?\.playbackPerf,'draw'/, '3D records Plotly timing');

perf.startSession('viz2d', { targetFps: 12 });
const first = perf.begin('viz2d', 0, 12, true);
now = 40; perf.stage(first, 'request', 32); perf.stage(first, 'decode', 8);
now = 70; perf.stage(first, 'assemble', 30);
now = 90; perf.stage(first, 'draw', 20); perf.finish(first);
now = 150;
const second = perf.begin('viz2d', 1, 12, true);
now = 240; perf.stage(second, 'request', 60); perf.stage(second, 'decode', 30);
now = 300; perf.stage(second, 'assemble', 60);
now = 470; perf.stage(second, 'draw', 170); perf.finish(second);

const snapshot = perf.snapshot('viz2d');
assert.equal(snapshot.targetFps, 12);
assert.equal(snapshot.frames, 2);
assert.equal(snapshot.last.frameMs, 320);
assert.equal(snapshot.last.intervalMs, 380);
assert.equal(snapshot.last.stages.plot, undefined);
assert.equal(snapshot.overBudgetFrames, 2, 'render budget counts frame work longer than the target interval');
assert.equal(snapshot.slowFrames, 1, 'slow frames count visible intervals beyond the cadence tolerance');
assert.ok(snapshot.actualFps > 2.6 && snapshot.actualFps < 2.7);
assert.equal(snapshot.last.stages.draw, 170);

// Pause gaps must not enter the cadence estimate; resume preserves frame history
// but starts a fresh interval segment.
perf.startSession('viz2d', { targetFps: 12, resume: true });
now = 10000;
const resumed = perf.begin('viz2d', 2, 12, true);
now = 10020; perf.finish(resumed);
assert.equal(perf.snapshot('viz2d').last.intervalMs, null);
now = 10070;
const resumedNext = perf.begin('viz2d', 3, 12, true);
now = 10090; perf.finish(resumedNext);
assert.equal(perf.snapshot('viz2d').last.intervalMs, 70);
assert.ok(perf.snapshot('viz2d').actualFps >= 14 && perf.snapshot('viz2d').actualFps < 15);

// A speed change starts a new measurement segment and does not mix old target FPS.
perf.startSession('viz2d', { targetFps: 4, resume: true });
now = 20000;
const changedSpeed = perf.begin('viz2d', 4, 4, true);
now = 20020; perf.finish(changedSpeed);
assert.equal(perf.snapshot('viz2d').targetFps, 4);
assert.equal(perf.snapshot('viz2d').frames, 1);
assert.equal(perf.snapshot('viz2d').last.intervalMs, null);

// Nine fresh successful frame completions spanning 3.035 seconds imply about
// 2.64 fps. This guards against a telemetry window that reports 0.8 fps for
// the same frame count and elapsed interval.
perf.startSession('viz3d', { targetFps: 4 });
const playbackStartedAt = now = 30000;
for (let frame = 0; frame < 9; frame++) {
  const ticket = perf.begin('viz3d', frame, 4, true);
  now = playbackStartedAt + frame * (3035 / 8);
  perf.finish(ticket);
}
const playback = perf.snapshot('viz3d');
assert.equal(playback.frames, 9);
assert.ok(playback.actualFps > 2.6 && playback.actualFps < 2.7,
  '9 completed frames spanning 3.035s should report about 2.64fps, not 0.8fps');

console.log('playback performance telemetry tests passed');
