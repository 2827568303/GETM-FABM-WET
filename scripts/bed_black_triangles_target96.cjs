#!/usr/bin/env node
'use strict';

const crypto = require('node:crypto');
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const { spawn } = require('node:child_process');

const root = path.resolve(__dirname, '..');
const out = path.join(root, 'build/bed-black-frame19-triangle-mode-compare-20261025-02');
const input = path.join(root, 'build/bed-black-frame19-historical-positive-probe-20261025/frame19-2020-target96-layer9.json');
const replayAudit = path.join(root, 'build/bed-black-v86-replay-20261025/current_v123_baseline.audit.json');
const renderer = path.join(root, '3DWET/app/static/js/viz3d.js');
const plotly = path.join(root, '3DWET/app/static/vendor/plotly-2.35.2.min.js');
const routes = {
  '/': path.join(__dirname, 'bed_black_triangles_target96.html'),
  '/page.js': path.join(__dirname, 'bed_black_triangles_target96_page.js'),
  '/matrix.js': path.join(__dirname, 'bed_black_render_matrix.js'),
  '/frame19-2020-target96-layer9.json': input, '/historical-v123-audit.json': replayAudit,
  '/viz3d.js': renderer, '/plotly.min.js': plotly,
};
const names = ['continuous', 'triangles'];
const outputNames = ['target96-replay-camera-continuous.png', 'target96-replay-camera-triangles.png',
  'target96-replay-camera-comparison.png', 'target96-replay-camera-render-summary.json'];
const sha = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');

function readBody(req) { return new Promise((resolve, reject) => {
  const parts = []; req.on('data', part => parts.push(part));
  req.on('end', () => { try { resolve(JSON.parse(Buffer.concat(parts).toString('utf8'))); } catch (e) { reject(e); } });
  req.on('error', reject);
}); }
function resolveEdge() {
  const candidates = [process.env.EDGE_EXE,
    path.join(process.env['PROGRAMFILES(X86)'] || 'C:/Program Files (x86)', 'Microsoft/Edge/Application/msedge.exe'),
    path.join(process.env.PROGRAMFILES || 'C:/Program Files', 'Microsoft/Edge/Application/msedge.exe')].filter(Boolean);
  const edge = candidates.find(fs.existsSync);
  if (!edge) throw new Error('Microsoft Edge not found; set EDGE_EXE.');
  return edge;
}
function runEdge(edge, url) { return new Promise((resolve, reject) => {
  const child = spawn(edge, ['--headless=new', '--disable-extensions', '--disable-background-networking', '--disable-sync',
    '--no-first-run', '--no-default-browser-check', '--enable-webgl', '--enable-unsafe-swiftshader', '--use-gl=angle',
    '--use-angle=swiftshader', '--ignore-gpu-blocklist', `--user-data-dir=${path.join(out, 'target96-edge-profile')}`,
    '--window-size=1500,1000', '--virtual-time-budget=2400000', '--dump-dom', url],
  { windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'] });
  const stdout = [], stderr = []; child.stdout.on('data', chunk => stdout.push(chunk)); child.stderr.on('data', chunk => stderr.push(chunk));
  const timeout = setTimeout(() => child.kill(), 180000);
  child.once('error', error => { clearTimeout(timeout); reject(error); });
  child.once('close', code => { clearTimeout(timeout); fs.writeFileSync(path.join(out, 'target96-replay-camera-edge.stderr.log'), Buffer.concat(stderr));
    const html = Buffer.concat(stdout).toString('utf8');
    if (code !== 0) return reject(new Error(`Headless Edge exited ${code}: ${html.slice(-1200)}`));
    resolve(html);
  });
}); }

async function main() {
  if (!fs.existsSync(out)) throw new Error(`Existing comparison directory missing: ${out}`);
  for (const name of outputNames) if (fs.existsSync(path.join(out, name))) throw new Error(`Refusing to overwrite target96 replay-camera evidence: ${name}`);
  for (const file of [...Object.values(routes)]) if (!fs.existsSync(file)) throw new Error(`Missing diagnostic input: ${file}`);
  const actualFixtureHash = sha(input);
  const expectedFixtureHash = '85b2932d4149ff0e4b8e48667b374c072bf807dc2d46a879fafdf33c6e320a26';
  if (actualFixtureHash !== expectedFixtureHash) throw new Error(`target96 fixture hash mismatch: ${actualFixtureHash}`);
  const existingReportPath = path.join(out, 'render-summary.json');
  if (!fs.existsSync(existingReportPath)) throw new Error('Existing target26 report is missing; refusing to build an orphan addendum.');
  const received = new Map(); let finished = null, failure = null;
  const server = http.createServer((req, res) => {
    const pathname = new URL(req.url, 'http://127.0.0.1').pathname;
    if (req.method === 'GET' && routes[pathname]) {
      const file = routes[pathname];
      const type = file.endsWith('.js') ? 'text/javascript; charset=utf-8' : file.endsWith('.json') ? 'application/json; charset=utf-8' : 'text/html; charset=utf-8';
      res.writeHead(200, { 'content-type': type, 'cache-control': 'no-store' }); fs.createReadStream(file).pipe(res); return;
    }
    if (req.method === 'POST' && pathname.startsWith('/capture/')) {
      readBody(req).then(payload => {
        const id = pathname.slice('/capture/'.length), match = /^data:image\/png;base64,([A-Za-z0-9+/=]+)$/.exec(payload.png || '');
        if (!names.includes(id) || !match) throw new Error('Invalid target96 screenshot');
        fs.writeFileSync(path.join(out, `target96-replay-camera-${id}.png`), Buffer.from(match[1], 'base64'));
        received.set(id, payload.result); res.writeHead(200).end('{"ok":true}');
      }).catch(error => res.writeHead(400).end(error.message)); return;
    }
    if (req.method === 'POST' && pathname === '/finish') {
      readBody(req).then(payload => {
        const match = /^data:image\/png;base64,([A-Za-z0-9+/=]+)$/.exec(payload.comparisonPng || '');
        if (!match) throw new Error('Missing target96 comparison sheet');
        fs.writeFileSync(path.join(out, 'target96-replay-camera-comparison.png'), Buffer.from(match[1], 'base64'));
        finished = payload; res.writeHead(200).end('ok');
      }).catch(error => res.writeHead(400).end(error.message)); return;
    }
    if (req.method === 'POST' && pathname === '/failure') { readBody(req).then(payload => { failure = payload; res.writeHead(200).end('ok'); }); return; }
    res.writeHead(404).end('not found');
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  try {
    const address = server.address();
    const html = await runEdge(resolveEdge(), `http://127.0.0.1:${address.port}/`);
    if (failure) throw new Error(`Browser diagnostic failed: ${failure.message}`);
    if (!finished || received.size !== 2 || !/data-status="complete"/.test(html))
      throw new Error(`Incomplete target96 render: captures=${received.size}/2; status=${html.match(/data-status="([^"]+)/)?.[1] || 'missing'}`);
    const currentReport = JSON.parse(fs.readFileSync(existingReportPath, 'utf8'));
    const first = received.get('continuous'), second = received.get('triangles');
    if (JSON.stringify(first.layoutInputs) !== JSON.stringify(second.layoutInputs)) throw new Error('Mode layout inputs differ.');
    const inputs = JSON.parse(fs.readFileSync(input, 'utf8'));
    const audit = JSON.parse(fs.readFileSync(replayAudit, 'utf8'));
    const report = {
      status: '代理（historical-proxy headless renderer diagnosis; not a user-device reproduction or science validation）',
      defectStatus: '未修复', rootCause: '不确定', readOnly: true, solverStarted: false, caseCreated: false, desktopAppTouched: false,
      timestampMatch: { target96: '2020-DOY001 02:00', historicalBlackFacetScreenshot: '2020-DOY001 06:00', mismatchHours: 4,
        note: 'Same date/grid/layer/VE, but not the screenshot timestamp.' },
      fixture: { path: path.relative(root, input), sha256: actualFixtureHash, timestep: inputs.timestep,
        variable: inputs.var_name, shape: inputs.shape, fullShape: inputs.full_shape, layerIndices: inputs.layer_indices },
      replayAudit: { path: path.relative(root, replayAudit), viewport: audit.viewport, camera: audit.layout.scene.camera,
        xRange: audit.layout.scene.xaxis.range, yRange: audit.layout.scene.yaxis.range, zRange: audit.layout.scene.zaxis.range,
        aspectmode: audit.layout.scene.aspectmode, aspectratio: audit.layout.scene.aspectratio },
      conditions: finished.fixedConditions,
      fingerprints: { input: actualFixtureHash, replayAudit: sha(replayAudit), renderer: sha(renderer), plotly: sha(plotly),
        harness: sha(__filename), page: sha(routes['/page.js']) },
      results: [first, second],
      note: 'The prior replay used headless Edge/ANGLE with NVIDIA RTX 4070; this target96 pair uses headless Edge/SwiftShader. It reuses the archived camera and plot viewport, not the original user device.',
    };
    fs.writeFileSync(path.join(out, 'target96-replay-camera-render-summary.json'), JSON.stringify(report, null, 2) + '\n');
    if (currentReport.target96Comparison) {
      currentReport.target96DefaultCameraInitialSuperseded = {
        ...currentReport.target96Comparison,
        superseded: true,
        supersededReason: 'Initial page JSON sanitizer replaced nested camera, axis ranges, aspect ratio and margins with null. Plotly used fallback camera/axes; those images are retained but excluded from the matched comparison conclusion.',
      };
      delete currentReport.target96Comparison;
    }
    currentReport.target96Comparison = report;
    fs.writeFileSync(existingReportPath, JSON.stringify(currentReport, null, 2) + '\n');
    const rows = report.results.map(r => `| ${r.mode} | ${r.traceInventory.length} | ${r.traceInventory.filter(t => t.networkMode === 'triangles').length} | ${r.metrics.regionNearBlackPixels}/${r.metrics.regionPixels} | ${r.metrics.nearBlackPixels}/${r.metrics.totalPixels} |`).join('\n');
    const inputRow = report.replayAudit;
    const section = `\n## Full-resolution target96 replay-camera comparison\n\nThis addendum uses the preserved historical proxy payload at SHA-256 ${actualFixtureHash}: frame 19, temp, target 96, layer ordinal 9, sampled shape 1×18×44. It is the 2020-DOY001 02:00 state, while the archived dark-facet screenshot is 2020-DOY001 06:00: same date/grid/layer/VE but a four-hour timestamp mismatch.\n\nThe pair uses VE 166.5× and the exact archived current-v123 replay camera and scene inputs: 1410×905 plot viewport; eye {x:${inputRow.camera.eye.x},y:${inputRow.camera.eye.y},z:${inputRow.camera.eye.z}}, center {x:${inputRow.camera.center.x},y:${inputRow.camera.center.y},z:${inputRow.camera.center.z}}, up {x:${inputRow.camera.up.x},y:${inputRow.camera.up.y},z:${inputRow.camera.up.z}}, orthographic projection; X ${JSON.stringify(inputRow.xRange)}, Y ${JSON.stringify(inputRow.yRange)}, Z ${JSON.stringify(inputRow.zRange)}, aspect ratio ${JSON.stringify(inputRow.aspectratio)}. These inputs were passed identically to both modes and recorded separately from Plotly _fullData after Plotly.newPlot.\n\n| Mode | _fullData traces | triangle network traces | ROI near-black pixels (RGB < 40) | whole image |\n|---|---:|---:|---:|---:|\n${rows}\n\nSee [target96-replay-camera-comparison.png](target96-replay-camera-comparison.png), [target96-replay-camera-continuous.png](target96-replay-camera-continuous.png), and [target96-replay-camera-triangles.png](target96-replay-camera-triangles.png). Full per-trace properties/array stats and pixel counts are in [target96-replay-camera-render-summary.json](target96-replay-camera-render-summary.json).\n\nThis is a headless Edge/SwiftShader render of the saved engineering/proxy payload, not a user-device reproduction. The earlier v86 replay used ANGLE/NVIDIA RTX 4070, so renderer/GPU also differ. No solver, model case, application source, or desktop UI was touched. Black-bed status remains 未修复 and root cause 不确定.\n`;
    const readmePath = path.join(out, 'README.md');
    let existingReadme = fs.readFileSync(readmePath, 'utf8');
    existingReadme = existingReadme.replace('## Full-resolution target96 follow-up', '## Superseded initial target96 attempt (fallback camera/axes)');
    existingReadme += '\nThe first target96 images above are retained, but their camera and axis inputs were nullified by a diagnostic JSON sanitizer and Plotly used fallback values. They are superseded and excluded from the matched comparison result. The replay-camera files below are the valid fixed-input pair.\n';
    fs.writeFileSync(readmePath, existingReadme + section, 'utf8');
    process.stdout.write(JSON.stringify({ output: out, timestampMatch: report.timestampMatch, viewport: inputRow.viewport,
      results: report.results.map(r => ({ mode: r.mode, traceCount: r.traceInventory.length,
        triangleNetworkTraces: r.traceInventory.filter(t => t.networkMode === 'triangles').length,
        roiNearBlack: r.metrics.regionNearBlackPixels, roiPixels: r.metrics.regionPixels,
        wholeNearBlack: r.metrics.nearBlackPixels, camera: r.layoutInputs.camera,
        axes: { x: r.layoutInputs.xRange, y: r.layoutInputs.yRange, z: r.layoutInputs.zRange } })), hashes: report.fingerprints }, null, 2) + '\n');
  } finally { await new Promise(resolve => server.close(resolve)); }
}

main().catch(error => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });
