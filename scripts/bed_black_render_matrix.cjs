#!/usr/bin/env node
'use strict';

const crypto = require('node:crypto');
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const { spawn } = require('node:child_process');
const { assertSingleFactorChanges, buildScenarioMatrix } = require('./bed_black_render_matrix.js');

const root = path.resolve(__dirname, '..');
const inputPath = path.join(root, 'build/bed-black-frame19-readonly-probe-20261024/frame19-target26.json');
const rendererPath = path.join(root, '3DWET/app/static/js/viz3d.js');
const plotlyPath = path.join(root, '3DWET/app/static/vendor/plotly-2.35.2.min.js');
const htmlPath = path.join(__dirname, 'bed_black_render_matrix.html');
const browserJsPath = path.join(__dirname, 'bed_black_render_matrix_page.js');
const scenarios = buildScenarioMatrix();
assertSingleFactorChanges(scenarios);

function sha256(filePath) {
  return crypto.createHash('sha256').update(fs.readFileSync(filePath)).digest('hex');
}

function parseArgs(argv) {
  const args = { out: null, edge: process.env.EDGE_EXE || null };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--out') args.out = path.resolve(argv[++i]);
    else if (argv[i] === '--edge') args.edge = path.resolve(argv[++i]);
    else if (argv[i] === '--help' || argv[i] === '-h') args.help = true;
    else throw new Error(`Unknown argument: ${argv[i]}`);
  }
  return args;
}

function resolveEdge(explicit) {
  const candidates = [explicit,
    path.join(process.env['PROGRAMFILES(X86)'] || 'C:/Program Files (x86)', 'Microsoft/Edge/Application/msedge.exe'),
    path.join(process.env.PROGRAMFILES || 'C:/Program Files', 'Microsoft/Edge/Application/msedge.exe')].filter(Boolean);
  const edge = candidates.find(candidate => fs.existsSync(candidate));
  if (!edge) throw new Error('Microsoft Edge not found. Pass --edge <path> or set EDGE_EXE.');
  return edge;
}

function freshOutputPath(requested) {
  if (requested) {
    if (fs.existsSync(requested)) throw new Error(`Output directory already exists: ${requested}`);
    return requested;
  }
  const day = new Date().toISOString().slice(0, 10).replaceAll('-', '');
  const base = path.join(root, `build/bed-black-frame19-variable-matrix-${day}`);
  for (let index = 1; ; index++) {
    const suffix = index === 1 ? '' : `-${String(index).padStart(2, '0')}`;
    const candidate = `${base}${suffix}`;
    if (!fs.existsSync(candidate)) return candidate;
  }
}

function mimeType(filePath) {
  if (filePath.endsWith('.js')) return 'text/javascript; charset=utf-8';
  if (filePath.endsWith('.json')) return 'application/json; charset=utf-8';
  return 'text/html; charset=utf-8';
}

function startLocalServer(outputPath) {
  const allowedIds = new Set(scenarios.map(item => item.id));
  const received = new Map();
  let finished = null, failure = null;
  const server = http.createServer((req, res) => {
    const pathname = new URL(req.url, 'http://127.0.0.1').pathname;
    const staticRoutes = {
      '/': htmlPath,
      '/matrix.js': path.join(__dirname, 'bed_black_render_matrix.js'),
      '/page.js': browserJsPath,
      '/frame19-target26.json': inputPath,
      '/viz3d.js': rendererPath,
      '/plotly.min.js': plotlyPath,
    };
    if (req.method === 'GET' && staticRoutes[pathname]) {
      res.writeHead(200, { 'content-type': mimeType(staticRoutes[pathname]), 'cache-control': 'no-store',
        'access-control-allow-origin': 'null' });
      fs.createReadStream(staticRoutes[pathname]).pipe(res);
      return;
    }
    if (req.method === 'POST' && pathname.startsWith('/capture/')) {
      const id = pathname.slice('/capture/'.length);
      if (!allowedIds.has(id)) { res.writeHead(404).end('Unknown scenario'); return; }
      collectBody(req).then(payload => {
        const match = /^data:image\/png;base64,([A-Za-z0-9+/=]+)$/.exec(payload.png || '');
        if (!match) throw new Error(`Invalid PNG data for ${id}`);
        const pngPath = path.join(outputPath, `${id}.png`);
        const png = Buffer.from(match[1], 'base64');
        fs.writeFileSync(pngPath, png);
        received.set(id, { pngPath, png, summary: payload.summary });
        res.writeHead(200, { 'content-type': 'application/json' }).end('{"ok":true}');
      }).catch(error => { res.writeHead(400).end(error.message); });
      return;
    }
    if (req.method === 'POST' && pathname === '/finish') {
      collectBody(req).then(payload => {
        const match = /^data:image\/png;base64,([A-Za-z0-9+/=]+)$/.exec(payload.contactPng || '');
        if (!match) throw new Error('Missing contact-sheet PNG');
        fs.writeFileSync(path.join(outputPath, 'matrix-contact.png'), Buffer.from(match[1], 'base64'));
        finished = payload;
        res.writeHead(200, { 'content-type': 'application/json' }).end('{"ok":true}');
      }).catch(error => { res.writeHead(400).end(error.message); });
      return;
    }
    if (req.method === 'POST' && pathname === '/failure') {
      collectBody(req).then(payload => {
        failure = payload;
        res.writeHead(200).end('ok');
      }).catch(() => res.writeHead(400).end('invalid'));
      return;
    }
    res.writeHead(404).end('Not found');
  });
  return new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '127.0.0.1', () => {
      const address = server.address();
      resolve({ server, url: `http://127.0.0.1:${address.port}/`, received, get finished() { return finished; },
        get failure() { return failure; } });
    });
  });
}

function collectBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    let length = 0;
    req.on('data', chunk => {
      length += chunk.length;
      if (length > 32 * 1024 * 1024) { reject(new Error('Request body too large')); req.destroy(); return; }
      chunks.push(chunk);
    });
    req.on('end', () => {
      try { resolve(JSON.parse(Buffer.concat(chunks).toString('utf8'))); }
      catch (error) { reject(error); }
    });
    req.on('error', reject);
  });
}

function runEdge(edge, url, outputPath) {
  const args = [
    '--headless=new', '--disable-extensions', '--disable-background-networking', '--disable-sync',
    '--no-first-run', '--no-default-browser-check', '--enable-webgl', '--enable-unsafe-swiftshader',
    '--use-gl=angle', '--use-angle=swiftshader', '--ignore-gpu-blocklist',
    `--user-data-dir=${path.join(outputPath, 'edge-profile')}`,
    '--window-size=1600,1000', '--virtual-time-budget=3600000', '--dump-dom', url,
  ];
  return new Promise((resolve, reject) => {
    const child = spawn(edge, args, { windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'] });
    const stdout = [], stderr = [];
    let bytes = 0;
    const timeout = setTimeout(() => child.kill(), 240000);
    child.stdout.on('data', chunk => {
      bytes += chunk.length;
      if (bytes <= 16 * 1024 * 1024) stdout.push(chunk);
    });
    child.stderr.on('data', chunk => stderr.push(chunk));
    child.once('error', error => { clearTimeout(timeout); reject(error); });
    child.once('close', code => {
      clearTimeout(timeout);
      fs.writeFileSync(path.join(outputPath, 'edge.stderr.log'), Buffer.concat(stderr));
      const output = Buffer.concat(stdout).toString('utf8');
      if (code !== 0) return reject(new Error(`Headless Edge exited with code ${code}. See edge.stderr.log.\n${output.slice(-2000)}`));
      resolve(output);
    });
  });
}

function writeReadme(outputPath, report) {
  const rows = report.scenarios.map(item => `| ${item.id} | ${item.factor || '基线'} | ${item.parameters.cameraElevation}° | ${item.parameters.ve}× | ${item.metrics.regionNearBlackPixels}/${item.metrics.regionPixels} (${(item.metrics.regionRatio * 100).toFixed(4)}%) |`).join('\n');
  const readme = `# Frame19 read-only render matrix\n\n` +
    `**代理（渲染诊断，非科学验证）**。黑片状态保持**未修复**，根因保持**不确定**。本工具只读取既有 frame19 API 快照，并用当前工作区 ` +
    '`viz3d.js`' + ` 与本地 Plotly 2.35.2 渲染；不启动模型、不新建案例、不读写案例输入/输出，不启动/刷新桌面应用。\n\n` +
    `## Reproduction\n\nRun from the repository root:\n\n` +
    '```powershell\nnode scripts/bed_black_render_matrix.cjs\n```\n\n' +
    `Pass ` + '`--out <new-directory>`' + ` or ` + '`--edge <msedge.exe>`' + ` to override defaults. Each run creates a new ` + '`build/bed-black-frame19-variable-matrix-*`' +
    ` folder, starts an ephemeral HTTP server bound to ` + '`127.0.0.1`' + `, and renders with a separate headless Edge profile using SwiftShader.\n\n` +
    `## Conditions\n\nBaseline is the frame-19 target-26 proxy snapshot, dynamic ` + '`temp`' + ` overlay, continuous mesh, VE=50×, camera elevation 34°, and bed/wall/shoreline visible. Azimuth, orthographic projection, viewport, field, bathymetry, axes, and other traces stay fixed. The camera cases call the current renderer's ` + '`viz3dCameraAtElevation`' + ` and vary elevation only. VE cases change VE only; any wall omission above 80× is the current renderer's own VE-dependent policy and is recorded in the trace summaries. Visibility cases hide one of bed, wall, or shoreline at a time while the baseline is unchanged.\n\n` +
    `The matrix is diagnostic, not a fit to the missing user reference. The source image remains ` + '`（待补充：参考图的具体路径或链接）`' + `.\n\n` +
    `## Pixel screen\n\n` +
    `“near-black” is a simple RGB screen, max(R,G,B) < 40, applied to the Plotly PNG export. ` +
    `` + '`regionRatio`' + ` counts the central crop (x=12–88%, y=10–84%) to reduce axis-label influence; ` + '`ratio`' + ` reports the whole image. This is a screening metric, not a semantic bed-pixel segmentation.\n\n` +
    `| Scenario | Factor | Elevation | VE | ROI near-black pixels |\n|---|---|---:|---:|---:|\n${rows}\n\n` +
    `## Files and fingerprints\n\n` +
    `- ` + '`matrix-contact.png`' + `: contact sheet; each scenario also has a standalone PNG.\n` +
    `- ` + '`render-summary.json`' + `: source/input hashes, fixed-condition declarations, pixel counts, camera, and Plotly fullData trace property/array summaries for every scenario.\n` +
    `- ` + '`edge.stderr.log`' + `: headless browser diagnostics.\n\n` +
    `Input SHA-256: ` + '`' + report.fingerprints.input + '`' + `  \nRenderer SHA-256: ` + '`' + report.fingerprints.renderer + '`' + `  \nPlotly SHA-256: ` + '`' + report.fingerprints.plotly + '`' + `\n\n` +
    `All renders are on a saved engineering/proxy snapshot under headless Edge/SwiftShader. A positive signal is not confirmation of a unique root cause; a negative signal is not proof of repair.\n`;
  fs.writeFileSync(path.join(outputPath, 'README.md'), readme, 'utf8');
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    process.stdout.write('Usage: node scripts/bed_black_render_matrix.cjs [--out NEW_DIRECTORY] [--edge PATH_TO_MSEDGE]\n');
    return;
  }
  for (const file of [inputPath, rendererPath, plotlyPath, htmlPath, browserJsPath]) {
    if (!fs.existsSync(file)) throw new Error(`Required read-only input missing: ${file}`);
  }
  const edge = resolveEdge(args.edge);
  const outputPath = freshOutputPath(args.out);
  fs.mkdirSync(outputPath, { recursive: true });
  const serverState = await startLocalServer(outputPath);
  try {
    const dump = await runEdge(edge, serverState.url, outputPath);
    if (serverState.failure) throw new Error(`Browser diagnostic failed: ${serverState.failure.message || JSON.stringify(serverState.failure)}`);
    if (!serverState.finished) {
      const pageStatus = dump.match(/<html[^>]*data-status="([^"]+)"/i)?.[1] || '(missing)';
      const pageError = dump.match(/Diagnostic failed: ([^<]+)/i)?.[1] || '(none)';
      throw new Error(`Browser exited without finishing; received ${serverState.received.size}/${scenarios.length} scenario renders; page status=${pageStatus}; page error=${pageError}.\n${dump.slice(-1000)}`);
    }
    if (serverState.received.size !== scenarios.length) throw new Error(`Incomplete render set: ${serverState.received.size}/${scenarios.length}`);
    const sourceReport = serverState.finished;
    const report = {
      status: '代理（渲染诊断，非科学验证）',
      defectStatus: '未修复',
      rootCause: '不确定；此矩阵用于记录可区分的渲染响应，不判定唯一机制。',
      readOnly: true,
      noSolverStarted: true,
      noCaseCreated: true,
      desktopAppTouched: false,
      viewport: { width: 1600, height: 1000, browser: 'Microsoft Edge headless + SwiftShader' },
      pixelMetric: { threshold: 'max(R,G,B) < 40', region: 'x 12–88%, y 10–84%', interpretation: 'screening metric, not semantic bed segmentation' },
      fixedConditions: sourceReport.fixedConditions,
      fingerprints: {
        input: sha256(inputPath), renderer: sha256(rendererPath), plotly: sha256(plotlyPath),
      },
      scenarios: scenarios.map(scenarioInfo => {
        const result = serverState.received.get(scenarioInfo.id)?.summary;
        return { id: scenarioInfo.id, label: scenarioInfo.label, factor: scenarioInfo.factor,
          parameters: { cameraElevation: scenarioInfo.cameraElevation, ve: scenarioInfo.ve,
            visibility: scenarioInfo.visibility }, ...result };
      }),
      note: 'No condition in this proxy/headless matrix establishes a unique cause or proves the reported production defect fixed.',
    };
    fs.writeFileSync(path.join(outputPath, 'render-summary.json'), JSON.stringify(report, null, 2) + '\n');
    writeReadme(outputPath, report);
    process.stdout.write(JSON.stringify({ outputPath, scenarios: report.scenarios.map(s => ({
      id: s.id, factor: s.factor, elevation: s.parameters.cameraElevation, ve: s.parameters.ve,
      roiNearBlack: s.metrics?.regionNearBlackPixels, roiPixels: s.metrics?.regionPixels,
      roiRatio: s.metrics?.regionRatio,
    })), result: report.status, defectStatus: report.defectStatus, rootCause: report.rootCause }, null, 2) + '\n');
  } finally {
    await new Promise(resolve => serverState.server.close(resolve));
  }
}

if (require.main === module) main().catch(error => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });

module.exports = { assertSingleFactorChanges, buildScenarioMatrix };
