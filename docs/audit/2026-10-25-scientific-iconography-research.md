# Scientific application iconography research

## Sources reviewed by Sol

- [napari viewer tutorial](https://napari.org/stable/tutorials/fundamentals/viewer.html): establishes a compact viewer structure with layer controls, a layer list, canvas actions, dimension controls and a status bar. Layer rows distinguish visibility, layer type and selection.
- [napari layer documentation](https://napari.org/stable/getting_started/layers.html): maps distinct scientific objects (images, labels, points, shapes, surfaces, tracks and vectors) to appropriate layer types and controls. It keeps data display and interaction semantic.
- [QGIS 3D Map View](https://docs.qgis.org/3.44/en/docs/user_manual/map_views/3d_map_view.html): groups camera control and zoom-to-extent operations with the 3D map canvas; the dockable view remains a working tool rather than a decorative presentation.
- [ParaView User's Guide](https://docs.paraview.org/_/downloads/en/latest/pdf/): documents pipeline and render-view workflows, where object and camera actions are explicit and contextual.

## Design conclusion

These references do not prescribe one universal icon pack or a monochrome appearance. Their useful shared lesson is semantic discipline: icons identify concrete data objects and operations in a dense scientific workspace. For 3DWET, redraw the entire icon family as restrained technical line drawings on the same 24-unit grid. Use consistent optical weight, mostly straight/orthogonal geometry, clear negative space, and recognizable scientific motifs (layer stack, structured grid, axes, section, gauge/measurement, camera, time series, and network nodes with directed relations). Avoid generic toy-like shapes, oversized rounded strokes, emoji, decorative leaves, gratuitous filled multicolor forms, and unrelated novelty metaphors.

The whole interface should stay quiet but not black and white: warm paper and mineral surfaces, ink-green text, lake-slate selected states, moss secondary actions, and muted ochre for provenance. High-chroma colors stay with model values and their legends, where they carry scientific meaning. Icons inherit the nearby control's subdued text color; selected/pressed state uses the established lake-slate/moss accents. Color must not carry meaning alone; retain labels, tooltips and focus states.

For the user's requested 3D expression, use geometry-aware faceted display, silhouette and restrained lighting/depth cues in the 3D viewport. Treat the triangular network as model visualization, not as decorative interface iconography. Keep it distinct from solver-native topology and preserve quantitative model colors.

## Scope and evidence status

This is a design direction based on official software documentation, not a claim that these apps were objectively ranked as the world's best. The user has approved a full UI redesign and specifically requested academic, restrained color and improved 3D expression. The reference image remains `（待补充：参考图的具体路径或链接）`.
