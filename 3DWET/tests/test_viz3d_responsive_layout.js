const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const { test } = require('node:test');

const context = vm.createContext({ console, window: {} });
vm.runInContext(fs.readFileSync('3DWET/app/static/js/viz3d.js', 'utf8'), context);
const baseLayout = vm.runInContext('VIZ3D.layout', context);

test('491x269 initial 3D viewport receives compact layout margins', () => {
    const layout = context.viz3dResponsiveLayout(baseLayout, 269, 491);

    assert.equal(layout.showlegend, false, 'constrained view hides the external legend');
    assert.ok(layout.margin.t <= 60, 'top margin leaves room for the 3D scene');
    assert.ok(layout.margin.b <= 28, 'bottom margin leaves room for the 3D scene');
    assert.ok(layout.margin.r >= 112, 'narrow layout reserves room for the colour bar');
});

test('desktop 3D viewport keeps its normal layout', () => {
    const layout = context.viz3dResponsiveLayout(baseLayout, 600, 800);

    assert.equal(layout, baseLayout);
});

test('3D canvas and mesh controls share the main workspace with a contextual settings rail', () => {
    const html = fs.readFileSync('3DWET/app/templates/index.html', 'utf8');
    const pageStart = html.indexOf('id="page-viz3d"');
    const timelineStart = html.indexOf('aria-label="三维结果时间控制"', pageStart);
    const page = html.slice(pageStart, timelineStart);
    const main = page.match(/<div class="sw-main">([\s\S]*)$/)?.[1];
    assert.ok(main, 'the 3D canvas and inspector are wrapped by the shared main workspace');
    assert.match(main, /<div class="sw-viewport"[^>]*>[\s\S]*?id="viz3d-plotly"/,
        'the main workspace includes the dominant 3D viewport');
    const rail = main.match(/<aside class="sw-rail" id="viz3d-settings"[\s\S]*?<\/aside>/)?.[0];
    assert.ok(rail, 'display settings are grouped in the contextual inspector rail');
    assert.match(rail, /class="sw-3d-display-controls"/,
        'mesh and shoreline controls belong to the settings rail beside the canvas');

    for (const id of ['viz3d-mesh-mode', 'viz3d-show-land']) {
        assert.equal((html.match(new RegExp(`id="${id}"`, 'g')) || []).length, 1,
            `${id} stays a single existing control rather than a duplicate`);
        assert.ok(rail.includes(`id="${id}"`), `${id} remains available in the contextual inspector`);
    }
});

test('3D desktop layout reserves a large plot and compact timeline row', () => {
    const css = fs.readFileSync('3DWET/app/static/css/scientific_workspace.css', 'utf8');
    const desktopRules = css.slice(0, css.indexOf('@media'));

    assert.match(desktopRules, /#page-viz3d #viz3d-plotly\s*\{\s*height:\s*clamp\(460px,\s*calc\(100dvh - 300px\),\s*760px\)/);
    assert.equal((desktopRules.match(/#page-viz3d #viz3d-plotly\s*\{/g) || []).length, 1,
        'only one pre-breakpoint desktop rule controls the 3D plot height');
    assert.match(css, /#page-viz3d \.sw-main #viz3d-plotly\s*\{\s*height:\s*clamp\(270px,\s*calc\(100dvh - 395px\),\s*470px\)/);
    assert.match(css, /#page-viz3d \.sw-timeline\s*\{\s*display:grid;grid-template-columns:auto minmax\(110px,1fr\)/);
    assert.match(css, /#page-viz3d \.sw-3d-display-controls\s*\{\s*display:flex/);
});

test('narrow desktop gives the 3D inspector a full-width drawer while preserving static-depth semantics', () => {
    const html = fs.readFileSync('3DWET/app/templates/index.html', 'utf8');
    const css = fs.readFileSync('3DWET/app/static/css/scientific_workspace.css', 'utf8');
    const shellCss = fs.readFileSync('3DWET/app/static/css/workbench.css', 'utf8');
    const workspaceJs = fs.readFileSync('3DWET/app/static/js/scientific_workspace.js', 'utf8');
    assert.match(html, /scientific_workspace\.css\?v=14/);
    assert.match(html, /scientific_workspace\.js\?v=19/);
    assert.match(css, /@media\s*\(min-width:\s*721px\)\s*and\s*\(max-width:\s*1180px\)[\s\S]*?#page-viz3d \.sw-main\s*\{\s*position:\s*relative;\s*grid-template-columns:\s*minmax\(0,\s*1fr\)/,
        'at compact desktop widths the inspector overlays the full-width canvas as a drawer');
    assert.match(shellCss, /\.scientific-workspace\.sw-inspector-closed \.sw-main\s*\{\s*grid-template-columns:\s*minmax\(0,\s*1fr\)/,
        'closing the inspector leaves the 3D canvas at full width');
    assert.match(workspaceJs, /root\.matchMedia\?\.\('\(max-width:\s*1180px\)'\)/,
        'the 3D inspector starts collapsed at the narrow desktop breakpoint');
    assert.match(html, /静态预览隐藏湖底；半透明蓝色水面与湿网格侧壁展示体积/,
        'the static preview explains how the visible water volume is represented');
});
