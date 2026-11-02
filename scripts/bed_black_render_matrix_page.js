/* Browser-side runner for the read-only frame-19 render matrix. */
(async function () {
  'use strict';
  const status = document.getElementById('status');
  const plot = document.getElementById('plot');
  const scenarios = BedBlackRenderMatrix.buildScenarioMatrix();
  const post = async (path, payload) => {
    const response = await fetch(path, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(payload) });
    if (!response.ok) throw new Error(`${path}: HTTP ${response.status} ${await response.text()}`);
  };
  try {
    const data = await (await fetch('/frame19-target26.json', { cache: 'no-store' })).json();
    if (data.timestep !== 19 || data.shape?.[0] !== 1 || data.layer_indices?.[0] !== 9) throw new Error('Unexpected fixture identity/shape');
    const veBaseline = 50;
    const basin = data.water_depth || data.bottom;
    const geometry = buildLakeGeometry(data.xc, data.yc, basin, veBaseline, data.display_topology);
    if (!geometry) throw new Error('Production buildLakeGeometry rejected the existing snapshot');
    const baseTraces = lakeTraces(geometry, false, data, null,
      { dynamicOverlay: true, meshMode: 'continuous', showLand: true }, null, data.var_name || 'temp');
    const cornerAverages = lakeLayerCornerAverages(geometry, data, 0, true);
    const meshes = lakeLayerMeshes(geometry, data, 0, veBaseline, true, cornerAverages);
    if (!meshes.fieldMesh.i.length) throw new Error('Fixture has no production-renderable field mesh');
    const fieldTrace = {
      type: 'mesh3d', name: `${data.long_name || data.var_name} · 层 ${data.layer_indices[0]}`,
      ...meshes.fieldMesh,
      meta: { scientificField: true, waterbodyFrame: 'field', layerOrdinals: [...data.layer_indices] },
      colorscale: VIZ3D.colorScale, cmin: data.min, cmax: data.max, cauto: false,
      showscale: true, opacity: 0.55, flatshading: false,
      lighting: { ambient: 1, diffuse: 0, specular: 0, roughness: 1 },
    };
    const fixedScene = lakeScene(veBaseline, geometry.maxDepth, data);
    const fixedCamera = fixedScene.camera;
    const fixedLayout = { ...VIZ3D.layout, width: 640, height: 480, showlegend: true, scene: fixedScene };
    const summaries = [];
    const imageSources = [];
    for (const scenario of scenarios) {
      const ve = scenario.ve;
      const scenarioGeometry = ve === veBaseline ? geometry : buildLakeGeometry(data.xc, data.yc, basin, ve, data.display_topology);
      let traces = lakeTraces(scenarioGeometry, false, data, null,
        { dynamicOverlay: true, meshMode: 'continuous', showLand: true }, null, data.var_name || 'temp');
      const layerMesh = ve === veBaseline ? meshes : lakeLayerMeshes(scenarioGeometry, data, 0, ve, true,
        lakeLayerCornerAverages(scenarioGeometry, data, 0, true));
      const field = ve === veBaseline ? fieldTrace : { ...fieldTrace, ...layerMesh.fieldMesh };
      traces = [...traces, field];
      if (scenario.visibility.bed === false) traces = traces.map(trace => trace.meta?.waterbodyFrame === 'bed' ? { ...trace, visible: false } : trace);
      if (scenario.visibility.wall === false) traces = traces.map(trace => trace.meta?.waterbodyFrame === 'wall' ? { ...trace, visible: false } : trace);
      if (scenario.visibility.shoreline === false) traces = traces.map(trace => trace.meta?.shoreline === true ? { ...trace, visible: false } : trace);
      for (const key of ['bed', 'wall', 'shoreline']) {
        const candidate = traces.find(trace => key === 'shoreline' ? trace.meta?.shoreline === true : trace.meta?.waterbodyFrame === key);
        if (scenario.visibility[key] && !candidate && !(key === 'wall' && ve > 80)) {
          throw new Error(`${scenario.id}: expected ${key} trace absent`);
        }
      }
      const scene = lakeScene(ve, scenarioGeometry.maxDepth, data);
      scene.camera = viz3dCameraAtElevation(fixedCamera, scenario.cameraElevation);
      const layout = { ...fixedLayout, scene, title: `${scenario.id} · elevation ${scenario.cameraElevation}° · VE ${ve}×` };
      status.textContent = `Rendering ${scenario.id} (${summaries.length + 1}/${scenarios.length})`;
      await Plotly.newPlot(plot, traces, layout, { staticPlot: true, responsive: false, displayModeBar: false, toImageButtonOptions: { format: 'png' } });
      const fullDataSummary = viz3dTraceAuditReport(plot._fullData);
      const png = await Plotly.toImage(plot, { format: 'png', width: 640, height: 480, scale: 1 });
      const image = new Image(); image.src = png;
      await image.decode();
      const canvas = document.createElement('canvas'); canvas.width = image.width; canvas.height = image.height;
      const context = canvas.getContext('2d', { willReadFrequently: true }); context.drawImage(image, 0, 0);
      const pixels = context.getImageData(0, 0, canvas.width, canvas.height).data;
      const metrics = BedBlackRenderMatrix.nearBlackMetrics(pixels, canvas.width, canvas.height);
      const summary = {
        metrics,
        parameters: { cameraElevation: scenario.cameraElevation, ve, visibility: scenario.visibility },
        geometry: { maxDepth: scenarioGeometry.maxDepth, floorCells: scenarioGeometry.floor.cell.length,
          wallQuads: scenarioGeometry.walls?.i?.length || 0 },
        traceAudit: fullDataSummary,
      };
      await post(`/capture/${scenario.id}`, { png, summary });
      imageSources.push({ id: scenario.id, label: scenario.label, src: png });
      summaries.push(summary);
      Plotly.purge(plot);
    }
    const contact = document.createElement('canvas'); contact.width = 1280; contact.height = 1600;
    const ctx = contact.getContext('2d'); ctx.fillStyle = '#f7fafb'; ctx.fillRect(0, 0, contact.width, contact.height);
    for (let index = 0; index < imageSources.length; index++) {
      const item = imageSources[index]; const image = new Image(); image.src = item.src; await image.decode();
      const col = index % 2, row = Math.floor(index / 2), x = col * 640, y = row * 320;
      ctx.drawImage(image, x, y + 20, 640, 300);
      ctx.fillStyle = '#23343b'; ctx.font = '14px sans-serif'; ctx.fillText(`${item.id} — ${item.label}`, x + 8, y + 15);
    }
    const fixedConditions = {
      fixture: 'existing proxy API snapshot frame=19 target=26 variable=temp layer ordinal=9; shape 1×18×22',
      bathymetry: 'same fixture bottom/water_depth arrays and sampled wet topology',
      field: 'same data values, range and 0.55 overlay opacity; production mesh builder',
      azimuth: 'fixed production default camera heading', projection: 'orthographic', viewport: '640×480 PNG',
      scene: 'current lakeScene axes, ranges, colors and traces; only declared factor changes',
    };
    await post('/finish', { contactPng: contact.toDataURL('image/png'), fixedConditions, summaries });
    status.textContent = 'Diagnostic matrix complete.'; document.documentElement.dataset.status = 'complete';
  } catch (error) {
    status.textContent = `Diagnostic failed: ${error.stack || error}`;
    document.documentElement.dataset.status = 'failed';
    try { await post('/failure', { message: error.stack || String(error) }); } catch {}
  }
})();
