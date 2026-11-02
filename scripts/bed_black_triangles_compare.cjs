#!/usr/bin/env node
'use strict';

const crypto = require('node:crypto');
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const { spawn } = require('node:child_process');

const root = path.resolve(__dirname, '..');
const input = path.join(root, 'build/bed-black-frame19-readonly-probe-20261024/frame19-target26.json');
const renderer = path.join(root, '3DWET/app/static/js/viz3d.js');
const plotly = path.join(root, '3DWET/app/static/vendor/plotly-2.35.2.min.js');
const files = { '/': path.join(__dirname, 'bed_black_triangles_compare.html'),
  '/page.js': path.join(__dirname, 'bed_black_triangles_compare_page.js'),
  '/matrix.js': path.join(__dirname, 'bed_black_render_matrix.js'),
  '/frame19-target26.json': input, '/viz3d.js': renderer, '/plotly.min.js': plotly };
const out = path.join(root, 'build/bed-black-frame19-triangle-mode-compare-20261025-02');

function sha(file) { return crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'); }
function collect(req) { return new Promise((resolve, reject) => {
  const chunks = []; req.on('data', chunk => chunks.push(chunk));
  req.on('end', () => { try { resolve(JSON.parse(Buffer.concat(chunks).toString('utf8'))); } catch (e) { reject(e); } });
  req.on('error', reject);
}); }
function edgePath() {
  const candidates = [process.env.EDGE_EXE,
    path.join(process.env['PROGRAMFILES(X86)'] || 'C:/Program Files (x86)', 'Microsoft/Edge/Application/msedge.exe'),
    path.join(process.env.PROGRAMFILES || 'C:/Program Files', 'Microsoft/Edge/Application/msedge.exe')].filter(Boolean);
  const found = candidates.find(fs.existsSync);
  if (!found) throw new Error('Microsoft Edge not found; set EDGE_EXE.');
  return found;
}
function runEdge(edge, url) { return new Promise((resolve, reject) => {
  const child = spawn(edge, ['--headless=new', '--disable-extensions', '--disable-background-networking', '--disable-sync',
    '--no-first-run', '--no-default-browser-check', '--enable-webgl', '--enable-unsafe-swiftshader', '--use-gl=angle',
    '--use-angle=swiftshader', '--ignore-gpu-blocklist', `--user-data-dir=${path.join(out, 'edge-profile')}`,
    '--window-size=1800,820', '--virtual-time-budget=1800000', '--dump-dom', url],
  { windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'] });
  const stdout = [], stderr = []; child.stdout.on('data', chunk => stdout.push(chunk)); child.stderr.on('data', chunk => stderr.push(chunk));
  const timeout = setTimeout(() => child.kill(), 120000);
  child.once('error', error => { clearTimeout(timeout); reject(error); });
  child.once('close', code => { clearTimeout(timeout); fs.writeFileSync(path.join(out, 'edge.stderr.log'), Buffer.concat(stderr));
    const html = Buffer.concat(stdout).toString('utf8');
    if (code !== 0) return reject(new Error(`Headless Edge exited ${code}: ${html.slice(-1500)}`)); resolve(html); });
}); }

async function main() {
  if (fs.existsSync(out)) throw new Error(`Output path already exists; refusing to overwrite: ${out}`);
  for (const file of [...Object.values(files)]) if (!fs.existsSync(file)) throw new Error(`Missing diagnostic input: ${file}`);
  fs.mkdirSync(out, { recursive: true });
  const received = new Map(); let finished = null, failure = null;
  const mime = file => file.endsWith('.js') ? 'text/javascript; charset=utf-8' : file.endsWith('.json') ? 'application/json' : 'text/html; charset=utf-8';
  const server = http.createServer((req, res) => {
    const pathname = new URL(req.url, 'http://127.0.0.1').pathname;
    if (req.method === 'GET' && files[pathname]) { res.writeHead(200, { 'content-type': mime(files[pathname]), 'cache-control': 'no-store' }); fs.createReadStream(files[pathname]).pipe(res); return; }
    if (req.method === 'POST' && pathname.startsWith('/capture/')) {
      collect(req).then(payload => {
        const match = /^data:image\/png;base64,([A-Za-z0-9+/=]+)$/.exec(payload.png || '');
        const id = pathname.slice('/capture/'.length);
        if (!['continuous', 'triangles'].includes(id) || !match) throw new Error('Invalid capture');
        fs.writeFileSync(path.join(out, `${id}.png`), Buffer.from(match[1], 'base64')); received.set(id, payload.summary);
        res.writeHead(200).end('{"ok":true}');
      }).catch(error => res.writeHead(400).end(error.message)); return;
    }
    if (req.method === 'POST' && pathname === '/finish') {
      collect(req).then(payload => {
        const match = /^data:image\/png;base64,([A-Za-z0-9+/=]+)$/.exec(payload.contactPng || '');
        if (!match) throw new Error('Missing contact sheet');
        fs.writeFileSync(path.join(out, 'comparison.png'), Buffer.from(match[1], 'base64')); finished = payload;
        res.writeHead(200).end('ok');
      }).catch(error => res.writeHead(400).end(error.message)); return;
    }
    if (req.method === 'POST' && pathname === '/failure') { collect(req).then(payload => { failure = payload; res.writeHead(200).end('ok'); }); return; }
    res.writeHead(404).end('Not found');
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  try {
    const address = server.address();
    const html = await runEdge(edgePath(), `http://127.0.0.1:${address.port}/`);
    if (failure) throw new Error(`Browser page failed: ${failure.message}`);
    if (!finished || received.size !== 2 || !/data-status="complete"/.test(html)) throw new Error(`Incomplete browser render; captures=${received.size}/2; page status=${html.match(/data-status="([^"]+)/)?.[1] || 'missing'}; ${html.match(/Diagnostic failed: ([^<]+)/)?.[1] || ''}`);
    const historicalImage = path.join(root, 'docs/audit/user-journey-20261021/erken-black-bed-flatshading-20261023.png');
    const report = { classification: '代理（headless render diagnosis; not a user-device reproduction or science validation）',
      defectStatus: '未修复', rootCause: '不确定', readOnly: true, solverStarted: false, caseCreated: false, desktopAppTouched: false,
      historicalReference: { path: path.relative(root, historicalImage), sha256: sha(historicalImage), frame: '2020-DOY001 06:00', layer: '9/9', ve: '166.5×',
        visibleObservation: 'blue temperature surface with a visible triangular display network and near-black underside bed facets; screenshot does not record the mesh selector state or camera coordinates' },
      method: finished.fixedConditions, fingerprints: { input: sha(input), renderer: sha(renderer), plotly: sha(plotly),
        harness: sha(__filename), page: sha(files['/page.js']), historicalScreenshot: sha(historicalImage) },
      results: finished.results, note: 'Both renders use the same saved proxy payload and fixed depth/camera/axes/viewport; only the production meshMode path differs. Headless Edge + SwiftShader is not the original user GPU/browser and does not reproduce their device.' };
    fs.writeFileSync(path.join(out, 'render-summary.json'), JSON.stringify(report, null, 2) + '\n');
    const rows = report.results.map(r => `| ${r.mode} | ${r.traceInventory.length} | ${r.traceInventory.filter(t => t.networkMode === 'triangles').length} | ${r.metrics.regionNearBlackPixels}/${r.metrics.regionPixels} | ${r.metrics.nearBlackPixels}/${r.metrics.totalPixels} |`).join('\n');
    const readme = `# Frame 19 production mesh-mode comparison\n\n**${report.classification}**. Black-bed status remains **${report.defectStatus}**; unique cause remains **${report.rootCause}**. No solver, case, or desktop application was started or changed.\n\n## Historical reference\n\nThe retained screenshot [${path.basename(historicalImage)}](../../../docs/audit/user-journey-20261021/${path.basename(historicalImage)}) shows 2020-DOY001 06:00, layer 9/9, VE 166.5×, a temperature surface with triangular display lines, and dark underside bed facets. Its exact mesh selector state and camera coordinates are not recorded. Current production render3DWaterBody represents triangular mode through lakePhysicalVolumeNetwork and lakeDisplayLines; it also uses mode-specific field mesh/shading. The historical screenshot does not prove it used precisely the current implementation.\n\n## Comparison\n\nThe existing frame-19 target-26 proxy API payload (1×18×22, source 10×18×44, selected layer ordinal 9) was rendered twice with current workspace viz3d.js and local Plotly 2.35.2. Both modes use the same water_depth (falling back to bottom), VE 166.5×, the same production default camera, axis ranges and aspect ratio, and a 896×760 Plotly viewport. The triangle-compatible 2.5% top z margin is applied to both scenes. Only meshMode changes; in triangle mode the production derived wet-grid display network is also created.\n\n| Mode | _fullData traces | triangle network traces | ROI near-black pixels (RGB < 40) | whole image |\n|---|---:|---:|---:|---:|\n${rows}\n\nNear-black is a screen-wide RGB threshold, not bed-pixel segmentation. _fullData inventory and trace-array audit are in render-summary.json. See comparison.png, continuous.png, and triangles.png.\n\n## Limits\n\nThis is an engineering/proxy payload rendered in headless Edge with SwiftShader, not a reproduction on the user device. The saved screenshot's camera and mesh selector state are unavailable. A negative headless result cannot disprove the historical observation, establish a fix, or identify the unique cause.\n\nSHA-256: input ${report.fingerprints.input}; renderer ${report.fingerprints.renderer}; Plotly ${report.fingerprints.plotly}; historical screenshot ${report.fingerprints.historicalScreenshot}.\n`;
    fs.writeFileSync(path.join(out, 'README.md'), readme, 'utf8');
    process.stdout.write(JSON.stringify({ output: out, results: report.results.map(r => ({ mode: r.mode, traceCount: r.traceInventory.length,
      triangleNetworkTraces: r.traceInventory.filter(t => t.networkMode === 'triangles').length,
      roiNearBlack: r.metrics.regionNearBlackPixels, roiPixels: r.metrics.regionPixels, wholeNearBlack: r.metrics.nearBlackPixels,
      camera: r.camera, scene: r.scene })), hashes: report.fingerprints }, null, 2) + '\n');
  } finally { await new Promise(resolve => server.close(resolve)); }
}

main().catch(error => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });
