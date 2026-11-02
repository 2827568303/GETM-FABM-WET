/* Read-only frame-19 proxy comparison: production continuous vs triangles. */
(async function () {
  'use strict';
  const status = document.getElementById('status');
  const post = async (path, payload) => {
    const response = await fetch(path, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(payload) });
    if (!response.ok) throw new Error(`${path}: HTTP ${response.status} ${await response.text()}`);
  };
  const safe = value => value === undefined ? undefined : JSON.parse(JSON.stringify(value, (key, item) => Number.isFinite(item) ? item : null));
  const summarize = fullData => viz3dTraceAuditReport(fullData);
  try {
    const data = await (await fetch('/frame19-target26.json', { cache: 'no-store' })).json();
    if (data.timestep !== 19 || data.shape?.[0] !== 1 || data.layer_indices?.[0] !== 9) throw new Error('Unexpected fixture identity/shape/layer');
    const ve = 166.5;
    const depth = data.water_depth || data.bottom;
    const geometry = buildLakeGeometry(data.xc, data.yc, depth, ve, data.display_topology);
    if (!geometry) throw new Error('Production buildLakeGeometry rejected the existing payload');
    const fieldOpacity = 0.55;
    const colorScale = VIZ3D.colorScale;
    const fieldStyle = { colorscale: colorScale, cmin: data.min, cmax: data.max, cauto: false, showscale: true };
    const fixedScene = lakeScene(ve, geometry.maxDepth, data, 0.025);
    const fixedCamera = safe(fixedScene.camera || VIZ3D.layout.scene.camera);
    const width = 896, height = 760;
    const results = [], pngs = [];
    for (const meshMode of ['continuous', 'triangles']) {
      const opts = { dynamicOverlay: true, meshMode, showLand: true, opacity: fieldOpacity };
      const baseTraces = lakeTraces(geometry, false, data, null, opts, null, data.var_name || 'temp');
      const smooth = meshMode === 'continuous';
      const corners = lakeLayerCornerAverages(geometry, data, 0, smooth);
      const { fieldMesh } = lakeLayerMeshes(geometry, data, 0, ve, smooth, corners);
      if (!fieldMesh.i.length) throw new Error(`${meshMode}: no production-renderable field mesh`);
      const faceted = meshMode === 'triangles';
      const field = {
        type: 'mesh3d', name: `${data.long_name || data.var_name} · 层 ${data.layer_indices[0]}`,
        ...fieldMesh, meta: { scientificField: true, waterbodyFrame: 'field', layerOrdinals: [...data.layer_indices], displayOnlyFacetLighting: faceted },
        ...fieldStyle, opacity: fieldOpacity, flatshading: faceted,
        lighting: faceted ? { ambient: .68, diffuse: .32, specular: 0, roughness: 1 } : { ambient: 1, diffuse: 0, specular: 0, roughness: 1 },
        ...(faceted ? { lightposition: { x: 1000, y: -1200, z: 1800 } } : {}),
      };
      let traces = [...baseTraces, field];
      if (meshMode === 'triangles') {
        const networkMeshes = lakePhysicalVolumeNetwork(data, geometry, ve, [0]);
        traces.push(...lakeDisplayLines(networkMeshes, geometry,
          lakeWaterbodyDisplayOptions({ ...opts, displayLayerOrdinals: data.layer_indices }, false), data));
      }
      const layout = { ...VIZ3D.layout, width, height, showlegend: false, title: { text: `Frame 19 · ${meshMode} · VE ${ve}×` }, scene: { ...fixedScene, camera: safe(fixedCamera) } };
      const id = meshMode;
      status.textContent = `Rendering ${id}…`;
      const element = document.getElementById(id);
      await Plotly.newPlot(element, traces, layout, { staticPlot: true, responsive: false, displayModeBar: false });
      const summary = {
        mode: meshMode, metrics: null, width, height, ve,
        camera: safe(fixedCamera), scene: safe({
          xaxis: { range: fixedScene.xaxis.range, title: fixedScene.xaxis.title },
          yaxis: { range: fixedScene.yaxis.range, title: fixedScene.yaxis.title },
          zaxis: { range: fixedScene.zaxis.range, title: fixedScene.zaxis.title },
          aspectratio: fixedScene.aspectratio }),
        traceAudit: summarize(element._fullData),
        traceInventory: element._fullData.map((trace, index) => ({ index, name: trace.name, type: trace.type,
          role: trace.meta?.waterbodyFrame || null, networkMode: trace.meta?.networkMode || null,
          visible: trace.visible ?? true, points: trace.x?.length ?? null, faces: trace.i?.length ?? null,
          zmin: Array.isArray(trace.z) ? Math.min(...trace.z.filter(Number.isFinite)) : null,
          zmax: Array.isArray(trace.z) ? Math.max(...trace.z.filter(Number.isFinite)) : null,
          lighting: safe(trace.lighting), flatshading: trace.flatshading ?? null,
          color: trace.color ?? null, colorscale: !!trace.colorscale })),
      };
      const png = await Plotly.toImage(element, { format: 'png', width, height, scale: 1 });
      const image = new Image(); image.src = png; await image.decode();
      const canvas = document.createElement('canvas'); canvas.width = image.width; canvas.height = image.height;
      const context = canvas.getContext('2d', { willReadFrequently: true }); context.drawImage(image, 0, 0);
      summary.metrics = BedBlackRenderMatrix.nearBlackMetrics(context.getImageData(0, 0, canvas.width, canvas.height).data, canvas.width, canvas.height);
      await post(`/capture/${id}`, { png, summary });
      results.push(summary); pngs.push(png);
    }
    if (JSON.stringify(results[0].scene) !== JSON.stringify(results[1].scene) || JSON.stringify(results[0].camera) !== JSON.stringify(results[1].camera))
      throw new Error('Comparison scene axes/camera diverged between mesh modes');
    const contact = document.createElement('canvas'); contact.width = width * 2; contact.height = height;
    const ctx = contact.getContext('2d');
    for (let i = 0; i < 2; i++) {
      const image = new Image(); image.src = pngs[i]; await image.decode();
      ctx.drawImage(image, i * width, 0, width, height);
    }
    await post('/finish', { contactPng: contact.toDataURL('image/png'), results,
      fixedConditions: { fixture: 'existing proxy API snapshot frame=19 target=26 variable=temp layer ordinal=9; shape 1×18×22',
        depth: 'same water_depth (fallback bottom), VE=166.5×', camera: 'same current production lakeScene default camera',
        axes: 'same current production lakeScene axis ranges/aspect ratio; triangle-compatible top margin 2.5% applied to both',
        viewport: `${width}×${height} per Plotly image`, fieldOpacity, onlyChangedFactor: 'meshMode: continuous → triangles (production mesh/lighting/display network path)' } });
    status.textContent = 'Comparison complete.'; document.documentElement.dataset.status = 'complete';
  } catch (error) {
    status.textContent = `Diagnostic failed: ${error.stack || error}`; document.documentElement.dataset.status = 'failed';
    try { await post('/failure', { message: error.stack || String(error) }); } catch {}
  }
})();
