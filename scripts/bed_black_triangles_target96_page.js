/* Read-only full-resolution frame-19 target-96 mode comparison. */
(async function () {
  'use strict';
  const status = document.getElementById('status');
  const plot = document.getElementById('plot');
  const post = async (path, payload) => {
    const response = await fetch(path, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(payload) });
    if (!response.ok) throw new Error(`${path}: HTTP ${response.status} ${await response.text()}`);
  };
  const safe = value => value === undefined ? undefined : JSON.parse(JSON.stringify(value,
    (key, item) => typeof item === 'number' && !Number.isFinite(item) ? null : item));
  try {
    const [data, replay] = await Promise.all([
      fetch('/frame19-2020-target96-layer9.json', { cache: 'no-store' }).then(response => response.json()),
      fetch('/historical-v123-audit.json', { cache: 'no-store' }).then(response => response.json()),
    ]);
    if (data.timestep !== 19 || data.shape?.[0] !== 1 || data.shape?.[1] !== 18 || data.shape?.[2] !== 44 || data.layer_indices?.[0] !== 9)
      throw new Error('Unexpected target96 fixture identity, shape or layer');
    if (replay.viewport?.width !== 1410 || replay.viewport?.height !== 905) throw new Error('Unexpected preserved replay viewport');
    const ve = 166.5;
    const depth = data.water_depth || data.bottom;
    const geometry = buildLakeGeometry(data.xc, data.yc, depth, ve, data.display_topology);
    if (!geometry) throw new Error('Production buildLakeGeometry rejected the target96 payload');
    const auditScene = replay.layout.scene;
    const generatedScene = lakeScene(ve, geometry.maxDepth, data, 0);
    const fixedScene = {
      ...generatedScene,
      camera: safe(auditScene.camera), aspectmode: auditScene.aspectmode, aspectratio: safe(auditScene.aspectratio),
      xaxis: { ...generatedScene.xaxis, range: [...auditScene.xaxis.range], autorange: false },
      yaxis: { ...generatedScene.yaxis, range: [...auditScene.yaxis.range], autorange: false },
      zaxis: { ...generatedScene.zaxis, range: [...auditScene.zaxis.range], tickvals: [...auditScene.zaxis.tickvals],
        ticktext: [...auditScene.zaxis.ticktext], tickmode: auditScene.zaxis.tickmode, autorange: false },
    };
    const width = replay.viewport.width, height = replay.viewport.height;
    const fieldOpacity = 0.55;
    const title = replay.layout.title?.text || '水温 · frame 19 · layer 9/9 · VE 166.5×';
    const results = [], pngs = [];
    for (const meshMode of ['continuous', 'triangles']) {
      const opts = { dynamicOverlay: true, meshMode, showLand: true, opacity: fieldOpacity };
      const baseTraces = lakeTraces(geometry, false, data, null, opts, null, data.var_name || 'temp');
      const smooth = meshMode === 'continuous';
      const corners = lakeLayerCornerAverages(geometry, data, 0, smooth);
      const { fieldMesh } = lakeLayerMeshes(geometry, data, 0, ve, smooth, corners);
      if (!fieldMesh.i.length) throw new Error(`${meshMode}: no production field mesh`);
      const faceted = meshMode === 'triangles';
      const field = {
        type: 'mesh3d', name: `${data.long_name || data.var_name} · 层 ${data.layer_indices[0]}`,
        ...fieldMesh, meta: { scientificField: true, waterbodyFrame: 'field', layerOrdinals: [...data.layer_indices], displayOnlyFacetLighting: faceted },
        colorscale: VIZ3D.colorScale, cmin: data.min, cmax: data.max, cauto: false, showscale: true,
        opacity: fieldOpacity, flatshading: faceted,
        lighting: faceted ? { ambient: .68, diffuse: .32, specular: 0, roughness: 1 } : { ambient: 1, diffuse: 0, specular: 0, roughness: 1 },
        ...(faceted ? { lightposition: { x: 1000, y: -1200, z: 1800 } } : {}),
      };
      let traces = [...baseTraces, field];
      if (meshMode === 'triangles') {
        const network = lakePhysicalVolumeNetwork(data, geometry, ve, [0]);
        traces.push(...lakeDisplayLines(network, geometry,
          lakeWaterbodyDisplayOptions({ ...opts, displayLayerOrdinals: data.layer_indices }, false), data));
      }
      const layout = { ...VIZ3D.layout, title: { ...replay.layout.title, text: title }, margin: safe(replay.layout.margin),
        width, height, showlegend: replay.layout.showlegend, scene: fixedScene };
      status.textContent = `Rendering target96 ${meshMode}…`;
      await Plotly.newPlot(plot, traces, layout, { staticPlot: true, responsive: false, displayModeBar: false });
      const renderedScene = plot._fullLayout.scene;
      const result = {
        mode: meshMode,
        layoutInputs: { width, height, camera: safe(fixedScene.camera), aspectmode: fixedScene.aspectmode,
          aspectratio: safe(fixedScene.aspectratio), xRange: safe(fixedScene.xaxis.range), yRange: safe(fixedScene.yaxis.range),
          zRange: safe(fixedScene.zaxis.range), margin: safe(replay.layout.margin), showlegend: replay.layout.showlegend },
        fullLayoutCheck: { width: plot._fullLayout.width, height: plot._fullLayout.height,
          camera: safe(renderedScene.camera), aspectratio: safe(renderedScene.aspectratio),
          xRange: safe(renderedScene.xaxis.range), yRange: safe(renderedScene.yaxis.range), zRange: safe(renderedScene.zaxis.range) },
        traceAudit: viz3dTraceAuditReport(plot._fullData),
        traceInventory: plot._fullData.map((trace, index) => ({ index, name: trace.name, type: trace.type,
          role: trace.meta?.waterbodyFrame || null, networkMode: trace.meta?.networkMode || null,
          visible: trace.visible ?? true, points: trace.x?.length ?? null, faces: trace.i?.length ?? null,
          color: trace.color ?? null, hasColorscale: !!trace.colorscale, flatshading: trace.flatshading ?? null,
          lighting: safe(trace.lighting) })),
      };
      const png = await Plotly.toImage(plot, { format: 'png', width, height, scale: 1 });
      const image = new Image(); image.src = png; await image.decode();
      const canvas = document.createElement('canvas'); canvas.width = image.width; canvas.height = image.height;
      const context = canvas.getContext('2d', { willReadFrequently: true }); context.drawImage(image, 0, 0);
      result.metrics = BedBlackRenderMatrix.nearBlackMetrics(context.getImageData(0, 0, canvas.width, canvas.height).data, canvas.width, canvas.height);
      result.metricsSource = 'Plotly.toImage PNG rendered to Canvas RGBA';
      result.traceSource = 'Plotly _fullData after Plotly.newPlot';
      await post(`/capture/${meshMode}`, { png, result });
      results.push(result); pngs.push(png);
      Plotly.purge(plot);
    }
    const contact = document.createElement('canvas'); contact.width = width * 2; contact.height = height;
    const ctx = contact.getContext('2d');
    for (let i = 0; i < 2; i++) { const image = new Image(); image.src = pngs[i]; await image.decode(); ctx.drawImage(image, i * width, 0, width, height); }
    await post('/finish', { comparisonPng: contact.toDataURL('image/png'), results,
      fixedConditions: { fixture: 'saved historical frame19 target96 temp layer ordinal9; shape 1×18×44; timestamp 2020-DOY001 02:00',
        historicalScreenshotTimestamp: '2020-DOY001 06:00 (four-hour mismatch; not an exact temporal match)',
        ve: '166.5×', depth: 'same target96 water_depth with bottom fallback',
        cameraAndAxes: 'exact camera, axis ranges and aspect ratio carried from current_v123_baseline.audit.json; identical in both modes',
        viewport: `${width}×${height} Plotly render`, onlyChangedFactor: 'production meshMode continuous vs triangles; field mesh/lighting and triangle display network follow the current render3DWaterBody path' } });
    status.textContent = 'target96 comparison complete.'; document.documentElement.dataset.status = 'complete';
  } catch (error) {
    status.textContent = `Diagnostic failed: ${error.stack || error}`; document.documentElement.dataset.status = 'failed';
    try { await post('/failure', { message: error.stack || String(error) }); } catch {}
  }
})();
