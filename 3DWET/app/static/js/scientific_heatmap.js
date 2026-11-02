// Rectilinear scalar cells without interpolation. Draw in CSS pixels using the
// caller's pixel ratio; returned geometry remains in canvas backing pixels.
(function (root) {
    'use strict';
    const finite = value => typeof value === 'number' && Number.isFinite(value);
    const lookupTables = new Map();
    const landColor = '#edf1f2', missingColor = '#c9cbd0';
    function coordinates(values, size) {
        if (!Array.isArray(values) || values.length !== size || !values.every(finite)) return null;
        if (size > 1) {
            const direction = Math.sign(values[1] - values[0]);
            if (!direction || values.some((value, index) => index && Math.sign(value - values[index - 1]) !== direction)) return null;
        }
        return values.slice();
    }
    function edges(centers, singletonSpacing) {
        if (centers.length === 1) return [centers[0] - singletonSpacing / 2, centers[0] + singletonSpacing / 2];
        const result = [centers[0] - (centers[1] - centers[0]) / 2];
        for (let index = 1; index < centers.length; index++) result.push(centers[index - 1] / 2 + centers[index] / 2);
        result.push(centers.at(-1) + (centers.at(-1) - centers.at(-2)) / 2);
        return result;
    }
    function containing(value, boundaries) {
        const ascending = boundaries.at(-1) > boundaries[0];
        let low = 0, high = boundaries.length - 1;
        while (low + 1 < high) {
            const mid = (low + high) >> 1;
            if (ascending ? value < boundaries[mid] : value > boundaries[mid]) high = mid;
            else low = mid;
        }
        return low;
    }
    function layout(width, height, rows, cols, { xc, yc } = {}) {
        width = finite(width) && width > 0 ? width : 0;
        height = finite(height) && height > 0 ? height : 0;
        rows = Number.isInteger(rows) && rows > 0 ? rows : 0;
        cols = Number.isInteger(cols) && cols > 0 ? cols : 0;
        let xs = coordinates(xc, cols), ys = coordinates(yc, rows);
        let mode = xs && ys && (cols > 1 || rows > 1) ? 'projected' : 'index';
        if (mode === 'index') {
            xs = Array.from({ length: cols }, (_, index) => index);
            ys = Array.from({ length: rows }, (_, index) => index);
        }
        const spacing = values => values.length > 1 ? Math.abs(values[1] - values[0]) : 1;
        let xEdges = cols ? edges(xs, spacing(ys)) : [], yEdges = rows ? edges(ys, spacing(xs)) : [];
        let xMin = Math.min(xEdges[0], xEdges.at(-1)), xMax = Math.max(xEdges[0], xEdges.at(-1));
        let yMin = Math.min(yEdges[0], yEdges.at(-1)), yMax = Math.max(yEdges[0], yEdges.at(-1));
        // Rounded or overflowing cell edges can otherwise create an invisible
        // final cell or put a center on the outside border. Use indices when
        // the supplied precision cannot support a reversible physical grid.
        const enclosedCenters = (values, boundaries) => boundaries.every(finite) && values.every((value, index) =>
            value > Math.min(boundaries[index], boundaries[index + 1]) && value < Math.max(boundaries[index], boundaries[index + 1]));
        if (mode === 'projected' && (![xMin,xMax,yMin,yMax,xMax-xMin,yMax-yMin].every(finite) || xMax <= xMin || yMax <= yMin || !enclosedCenters(xs, xEdges) || !enclosedCenters(ys, yEdges))) {
            return layout(width, height, rows, cols);
        }
        const left = Math.min(76, width * 0.19), right = Math.min(24, width * 0.06);
        const top = Math.min(24, height * 0.06), bottom = Math.min(70, height * 0.18);
        const availableWidth = Math.max(0, width - left - right), availableHeight = Math.max(0, height - top - bottom);
        const spanX = cols ? xMax - xMin : 0, spanY = rows ? yMax - yMin : 0;
        const scale = spanX > 0 && spanY > 0 ? Math.min(availableWidth / spanX, availableHeight / spanY) : 0;
        const plot = { x: left + (availableWidth - spanX * scale) / 2,
            y: top + (availableHeight - spanY * scale) / 2, width: spanX * scale, height: spanY * scale };
        // Finite coordinate spans can still be too small for a finite pixel
        // scale. Reject their derived geometry before projection or hit tests.
        if (mode === 'projected' && ![scale, plot.x, plot.y, plot.width, plot.height].every(finite)) {
            return layout(width, height, rows, cols);
        }
        const projectX = value => plot.x + (value - xMin) * scale;
        const projectY = value => plot.y + (mode === 'projected' ? yMax - value : value - yMin) * scale;
        const validCell = (i, j) => Number.isInteger(i) && Number.isInteger(j) && i >= 0 && i < cols && j >= 0 && j < rows;
        const geometry = { mode, plot, rows, cols, xMin, xMax, yMin, yMax,
            center(i, j) { return validCell(i, j) && scale > 0 ? { x: projectX(xs[i]), y: projectY(ys[j]) } : null; },
            cellAt(x, y) {
                if (!finite(x) || !finite(y) || !scale || x < plot.x || y < plot.y || x >= plot.x + plot.width || y >= plot.y + plot.height) return null;
                const physicalX = xMin + (x - plot.x) / scale;
                const physicalY = mode === 'projected' ? yMax - (y - plot.y) / scale : yMin + (y - plot.y) / scale;
                return { i: containing(physicalX, xEdges), j: containing(physicalY, yEdges) };
            },
            cellRect(i, j) {
                if (!validCell(i, j) || !scale) return null;
                const x1 = projectX(xEdges[i]), x2 = projectX(xEdges[i + 1]);
                const y1 = projectY(yEdges[j]), y2 = projectY(yEdges[j + 1]);
                return { x: Math.min(x1, x2), y: Math.min(y1, y2), width: Math.abs(x2 - x1), height: Math.abs(y2 - y1) };
            },
            projectX, projectY
        };
        return geometry;
    }
    function backingGeometry(geometry, pixelRatio) {
        if (pixelRatio === 1) return geometry;
        const point = value => value && ({ x: value.x * pixelRatio, y: value.y * pixelRatio });
        const rect = value => value && ({ ...point(value), width: value.width * pixelRatio, height: value.height * pixelRatio });
        return { ...geometry, plot: rect(geometry.plot),
            center(i, j) { return point(geometry.center(i, j)); },
            cellAt(x, y) { return finite(x) && finite(y) ? geometry.cellAt(x / pixelRatio, y / pixelRatio) : null; },
            cellRect(i, j) { return rect(geometry.cellRect(i, j)); },
            projectX(value) { return geometry.projectX(value) * pixelRatio; },
            projectY(value) { return geometry.projectY(value) * pixelRatio; }
        };
    }
    function paletteTable(palette) {
        palette = ['lake','cividis','viridis'].includes(palette) ? palette : 'lake';
        if (!lookupTables.has(palette)) {
            if (!root.ScientificStyle) throw new Error('ScientificStyle must load before drawing a scientific heatmap');
            lookupTables.set(palette, Array.from({ length: 256 }, (_, index) => root.ScientificStyle.color(index / 255, palette)));
        }
        return lookupTables.get(palette);
    }
    function pointInRing(x, y, ring) {
        let inside = false;
        for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
            const [xi, yi] = ring[i], [xj, yj] = ring[j];
            if ((yi > y) !== (yj > y) && x < (xj - xi) * (y - yi) / (yj - yi) + xi) inside = !inside;
        }
        return inside;
    }
    function contains(groups, x, y) {
        return groups.some(group => pointInRing(x, y, group.outer) &&
            !(group.holes || []).some(ring => pointInRing(x, y, ring)));
    }
    // A display-only contour around wet cells. Quarter-cell corner rounding
    // softens the raster silhouette without changing which cells are painted;
    // callers must continue to label this as a wet-grid proxy.
    function wetMaskContour(wet, rows, cols, geometry, xc, yc) {
        const edges = [], key = point => `${point.x},${point.y}`;
        const above = geometry.mode==='projected' && yc[0]<yc.at(-1) ? 1 : -1;
        const right = geometry.mode==='projected' && xc[0]>xc.at(-1) ? -1 : 1;
        const add = (a, b) => edges.push({ a, b, used: false });
        for (let j = 0; j < rows; j++) for (let i = 0; i < cols; i++) {
            if (!wet(i, j)) continue;
            const r = geometry.cellRect(i, j);
            if (!r) continue;
            const tl={x:r.x,y:r.y}, tr={x:r.x+r.width,y:r.y}, br={x:r.x+r.width,y:r.y+r.height}, bl={x:r.x,y:r.y+r.height};
            if (!wet(i, j + above)) add(tl, tr);
            if (!wet(i + right, j)) add(tr, br);
            if (!wet(i, j - above)) add(br, bl);
            if (!wet(i - right, j)) add(bl, tl);
        }
        const starts = new Map();
        for (const edge of edges) {
            const id=key(edge.a);
            if (!starts.has(id)) starts.set(id, []);
            starts.get(id).push(edge);
        }
        return edges.map(seed => {
            if (seed.used) return null;
            const loop=[]; let edge=seed;
            for (let guard=0; edge && !edge.used && guard<=edges.length; guard++) {
                edge.used=true; loop.push(edge.a);
                const candidates=starts.get(key(edge.b))?.filter(candidate=>!candidate.used)||[];
                const turn=(candidate)=>{
                    const incoming=Math.atan2(edge.b.y-edge.a.y,edge.b.x-edge.a.x);
                    const outgoing=Math.atan2(candidate.b.y-candidate.a.y,candidate.b.x-candidate.a.x);
                    return (outgoing-incoming+Math.PI*2)%(Math.PI*2);
                };
                // At diagonal wet-cell contacts, keep separate 4-connected
                // patches by preferring the clockwise wet-side turn.
                edge=candidates.sort((a,b)=>turn(a)-turn(b))[0]||null;
                if (edge === seed) break;
            }
            if (loop.length<3) return null;
            return loop;
        }).filter(Boolean);
    }
    function traceRoundedContours(ctx, contours) {
        for (const contour of contours) {
            const corners=contour.map((point,index)=>{
                const prev=contour[(index+contour.length-1)%contour.length],next=contour[(index+1)%contour.length];
                const a=Math.hypot(point.x-prev.x,point.y-prev.y),b=Math.hypot(next.x-point.x,next.y-point.y);
                const radius=Math.min(a,b)*0.32;
                return {before:{x:point.x+(prev.x-point.x)*radius/a,y:point.y+(prev.y-point.y)*radius/a},
                    after:{x:point.x+(next.x-point.x)*radius/b,y:point.y+(next.y-point.y)*radius/b},point};
            });
            if (!corners.length) continue;
            ctx.moveTo(corners[0].before.x,corners[0].before.y);
            for (const corner of corners) {
                ctx.lineTo(corner.before.x,corner.before.y);
                ctx.quadraticCurveTo(corner.point.x,corner.point.y,corner.after.x,corner.after.y);
            }
            ctx.closePath();
        }
    }
    // A saved boundary can shape display pixels only after checking its declared
    // bathymetry coordinate space and every known wet/dry cell center.
    function validateBoundary(boundary, { wetMask, dryMask, xc, yc, coordinateMode, rows, cols } = {}) {
        const groups = boundary?.projected_polygons;
        if (boundary?.coordinate_space !== 'bathymetry_projected_grid_coordinates' ||
            boundary?.provenance?.status === 'proxy-display-geometry-not-scientifically-validated' ||
            !boundary?.provenance?.source || !Array.isArray(groups) || !groups.length ||
            coordinateMode !== 'projected' || !Array.isArray(xc) || xc.length !== cols ||
            !Array.isArray(yc) || yc.length !== rows || !Array.isArray(wetMask) || wetMask.length !== rows ||
            !Array.isArray(dryMask) || dryMask.length !== rows) return null;
        let vertices = 0;
        for (const group of groups) {
            const rings = [group?.outer, ...(group?.holes || [])];
            if (!Array.isArray(group?.outer) || !Array.isArray(group?.holes || []) || rings.some(ring =>
                !Array.isArray(ring) || ring.length < 3 || ring.some(point => !Array.isArray(point) ||
                    !finite(point[0]) || !finite(point[1])))) return null;
            vertices += rings.reduce((sum, ring) => sum + ring.length, 0);
            if (vertices > 20000) return null;
        }
        if (wetMask.some(row => !Array.isArray(row) || row.length !== cols) ||
            dryMask.some(row => !Array.isArray(row) || row.length !== cols)) return null;
        let wet = 0, dry = 0;
        for (let j = 0; j < rows; j++) for (let i = 0; i < cols; i++) {
            if (!finite(xc[i]) || !finite(yc[j])) return null;
            const isWet = wetMask[j][i] === true, isDry = dryMask[j][i] === true;
            if (isWet && isDry) return null;
            const inside = contains(groups, xc[i], yc[j]);
            if (isWet) { wet++; if (!inside) return null; }
            if (isDry) { dry++; if (inside) return null; }
        }
        return wet && dry ? { groups, source: boundary.provenance.source } : null;
    }
    function draw(canvas, data, { min, max, palette = 'lake', style, wetMask, dryMask, xc, yc, boundary, coordinateMode, showGrid = false, pixelRatio = 1 } = {}) {
        if (!canvas || typeof canvas.getContext !== 'function') throw new TypeError('A Canvas2D canvas is required');
        if (!Array.isArray(data)) throw new TypeError('Heatmap data must be rectangular rows');
        const rows = data.length, cols = rows && Array.isArray(data[0]) ? data[0].length : 0;
        if (data.some(row => !Array.isArray(row) || row.length !== cols)) throw new RangeError('Heatmap data must be rectangular rows');
        if (wetMask != null && (!Array.isArray(wetMask) || wetMask.length !== rows || wetMask.some(row => !Array.isArray(row) || row.length !== cols))) {
            throw new RangeError('Wet mask shape must match the field');
        }
        pixelRatio = finite(pixelRatio) && pixelRatio > 0 ? pixelRatio : 1;
        const width = canvas.width / pixelRatio, height = canvas.height / pixelRatio;
        const geometry = layout(width, height, rows, cols, { xc, yc });
        const displayBoundary = validateBoundary(boundary, { wetMask, dryMask, xc, yc, coordinateMode, rows, cols });
        const ctx = canvas.getContext('2d');
        if (!ctx) throw new Error('Canvas2D is unavailable');
        const colors = style ? null : paletteTable(palette);
        // A full transfer function uses its exact positions and class edges.
        // Compile its nodes once per frame, rather than quantizing the mapping.
        const color=style ? root.ScientificStyle.mapper(style) : t=>colors[Math.round(Math.max(0,Math.min(1,t))*255)];
        const wet = (i, j) => i >= 0 && i < cols && j >= 0 && j < rows && (wetMask == null || wetMask[j][i] === true || (finite(wetMask[j][i]) && wetMask[j][i] > 0));
        const proxyContours = !displayBoundary && wetMask != null ? wetMaskContour(wet, rows, cols, geometry, xc, yc) : [];
        const rangeValid = finite(min) && finite(max) && max >= min;
        let validCount = 0;
        ctx.save();
        try {
            ctx.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
            ctx.clearRect(0, 0, width, height);
            ctx.fillStyle = '#ffffff';
            ctx.fillRect(0, 0, width, height);
            if (displayBoundary) {
                ctx.beginPath();
                for (const group of displayBoundary.groups) for (const ring of [group.outer, ...(group.holes || [])]) {
                    ring.forEach(([x, y], index) => {
                        const point = index ? 'lineTo' : 'moveTo';
                        ctx[point](geometry.projectX(x), geometry.projectY(y));
                    });
                    ctx.closePath();
                }
                ctx.clip('evenodd');
            } else if (proxyContours.length) {
                // Round only the display mask edge by a small fraction of a
                // cell. This is a proxy silhouette, never model geometry.
                ctx.beginPath(); traceRoundedContours(ctx, proxyContours); ctx.clip('evenodd');
            }
            for (let j = 0; j < rows; j++) for (let i = 0; i < cols; i++) {
                const rect = geometry.cellRect(i, j);
                if (!rect) continue;
                const value = data[j][i];
                if (!wet(i, j)) ctx.fillStyle = landColor;
                else if (!finite(value) || !rangeValid) ctx.fillStyle = style ? color(NaN) : missingColor;
                else {
                    validCount++;
                    // Avoid division overflow for very wide finite ranges.
                    const t = max === min ? 0.5 : (max - min === Infinity ? (value / 2 - min / 2) / (max / 2 - min / 2) : (value - min) / (max - min));
                    ctx.fillStyle = color(t);
                }
                ctx.fillRect(rect.x, rect.y, rect.width, rect.height);
            }
            // Preserve the exact wet-cell fills; smooth only the proxy outline
            // in display pixels. This path is never fed back to model geometry.
            ctx.strokeStyle = '#54798b'; ctx.lineWidth = 1.25; ctx.lineJoin = 'round'; ctx.lineCap = 'round';
            ctx.beginPath();
            traceRoundedContours(ctx, proxyContours);
            ctx.stroke();
            if (displayBoundary) {
                ctx.strokeStyle = '#356d77'; ctx.lineWidth = 1.6; ctx.beginPath();
                for (const group of displayBoundary.groups) for (const ring of [group.outer, ...(group.holes || [])]) {
                    ring.forEach(([x, y], index) => {
                        const point = index ? 'lineTo' : 'moveTo';
                        ctx[point](geometry.projectX(x), geometry.projectY(y));
                    });
                    ctx.closePath();
                }
                ctx.stroke();
            }
            if (showGrid) {
                ctx.strokeStyle = '#9eafb7'; ctx.lineWidth = 0.5; ctx.beginPath();
                const segment = (x1,y1,x2,y2) => { ctx.moveTo(x1,y1); ctx.lineTo(x2,y2); };
                for (let j = 0; j < rows; j++) for (let i = 0; i < cols; i++) {
                    if (!wet(i, j)) continue;
                    const r = geometry.cellRect(i, j);
                    if (!r) continue;
                    segment(r.x,r.y,r.x+r.width,r.y); segment(r.x+r.width,r.y,r.x+r.width,r.y+r.height);
                    segment(r.x+r.width,r.y+r.height,r.x,r.y+r.height); segment(r.x,r.y+r.height,r.x,r.y);
                }
                ctx.stroke();
            }
            drawAxes(ctx, geometry);
            if (!validCount) {
                ctx.fillStyle = '#475963'; ctx.font = '12px sans-serif'; ctx.textAlign = 'center';
                ctx.fillText('No valid data', width / 2, Math.max(14, geometry.plot.y + geometry.plot.height / 2));
            }
        } finally { ctx.restore(); }
        return { ...backingGeometry(geometry, pixelRatio), displayBoundary: displayBoundary?.source || null };
    }
    function drawAxes(ctx, g) {
        const p = g.plot;
        if (p.width <= 0 || p.height <= 0) return;
        ctx.fillStyle = '#475963'; ctx.strokeStyle = '#8c9ba4'; ctx.lineWidth = 0.75; ctx.font = '11px sans-serif';
        if (g.mode === 'index') {
            ctx.textAlign = 'center'; ctx.fillText('I / J index', p.x + p.width / 2, p.y + p.height + 24);
            return;
        }
        ctx.beginPath(); ctx.moveTo(p.x,p.y); ctx.lineTo(p.x,p.y+p.height); ctx.lineTo(p.x+p.width,p.y+p.height); ctx.stroke();
        const xTicks = root.ScientificStyle.ticks(g.xMin, g.xMax, p.width < 300 ? 3 : 5);
        const yTicks = root.ScientificStyle.ticks(g.yMin, g.yMax, p.height < 220 ? 3 : 5);
        ctx.beginPath();
        xTicks.values.forEach((v, index) => {
            const x = g.projectX(v); ctx.moveTo(x,p.y+p.height); ctx.lineTo(x,p.y+p.height+4);
            ctx.textAlign = 'center'; ctx.fillText(xTicks.labels[index],x,p.y+p.height+17);
        });
        yTicks.values.forEach((v, index) => {
            const y = g.projectY(v); ctx.moveTo(p.x-4,y); ctx.lineTo(p.x,y);
            ctx.textAlign = 'right'; ctx.fillText(yTicks.labels[index],p.x-8,y+4);
        });
        ctx.stroke();
        ctx.textAlign = 'center'; ctx.fillText('x (m)',p.x+p.width/2,p.y+p.height+35);
        ctx.save(); ctx.translate(Math.max(10,p.x-61),p.y+p.height/2); ctx.rotate(-Math.PI/2); ctx.fillText('y (m)',0,0); ctx.restore();
        // A 1/2/5 metre scale stays tied to the same physical projection.
        const target = (g.xMax - g.xMin) * 0.2;
        const base = 10 ** Math.floor(Math.log10(target));
        const scaleLength = [5,2,1].map(factor => factor * base).find(value => value <= target) || base;
        const pixels = g.projectX(g.xMin+scaleLength)-g.projectX(g.xMin);
        const x = p.x+p.width-pixels, y = p.y+p.height+51;
        ctx.beginPath(); ctx.moveTo(x,y-3); ctx.lineTo(x,y); ctx.lineTo(x+pixels,y); ctx.lineTo(x+pixels,y-3); ctx.stroke();
        ctx.textAlign = 'center'; ctx.fillText(`${Number(scaleLength.toPrecision(3))} m`,x+pixels/2,y-5);
    }
    root.ScientificHeatmap = { layout, draw, validateBoundary };
})(typeof window !== 'undefined' ? window : globalThis);
