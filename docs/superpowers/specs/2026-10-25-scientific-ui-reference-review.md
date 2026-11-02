# Scientific application design references — 2026-10-25

This reference review informs the restrained scientific 3D design in `docs/superpowers/specs/2026-10-25-restrained-scientific-3d-design.md`. These are established scientific applications with authoritative software documentation; this note does not claim an objective global ranking or “best software” award.

## ParaView

- Source: [ParaView 6.0.1 — Basic Usage](https://docs.paraview.org/en/v6.0.1/Tutorials/SelfDirectedTutorial/basicUsage.html)
- Observed patterns: a pipeline browser for data objects, a properties panel for the selected object, a large 3D view, and a camera toolbar with reset, zoom-to-data, and axis-aligned views.
- Adoption: keep the scientific canvas dominant; keep selected layer/run context and its properties adjacent; expose camera presets rather than burying camera actions in menus.
- Not adopted: ParaView’s full desktop-panel density, which is too heavy for this web workflow.

## napari

- Source: [napari — Tour of the viewer](https://napari.org/stable/tutorials/fundamentals/viewer.html); [GUI essentials](https://napari.org/workshops/extend/gui/)
- Observed patterns: distinct canvas, layer list, layer-specific controls, status bar, compact viewer buttons, and direct toggles for 2D/3D, home, grid, axes, and scale bar.
- Adoption: make model/layer visibility and view controls easy to locate; keep axes, units and scale reference close to the rendered result; pair unfamiliar tools with labels/tooltips.
- Not adopted: image-viewer metaphors where they do not fit model setup and scientific workflows.

## QGIS 3D

- Source: [QGIS 3.44 — 3D Map View](https://docs.qgis.org/3.44/en/docs/user_manual/map_views/3d_map_view.html)
- Observed patterns: explicit terrain vertical scale, triangle/wireframe settings, separate camera/navigation actions, identifiable features, and scene export. The guide describes directional lighting and depth effects such as EDL and SSAO.
- Adoption: expose vertical exaggeration as a labeled display control; distinguish rendered mesh from underlying physical values; use subdued facets and structural edges to clarify relief.
- Not adopted: strong SSAO/EDL or dark self-shadowing as defaults. Because the product has a known unresolved dark bed-face artifact, shading must remain conservative and must not be represented as evidence of a defect fix.

## Design decision

Use a warm, low-chroma mineral interface palette with slate lake-blue, sage and muted ochre for hierarchy, while reserving vivid color for quantitative model fields and semantic alerts. Recompose the application around a generous scientific canvas, compact navigation/context, and a nearby properties inspector. Use a coherent technical line-icon family. In 3D, use valid wet-cell triangulation with stable diagonals, restrained facet lighting and edge contrast, explicit camera presets, and labeled display-only vertical exaggeration. Keep continuous-surface rendering available and keep nodes off by default. Triangle edges and vertical display offsets describe derived visualization topology, not solver-native topology or physical displacement.

This review supports interaction and visualization patterns. The palette, icon geometry, and balance between edge contrast and field color are product design judgments rather than claims made by the cited projects.

## Nature portfolio figure references for lake rendering

- Source: [Nature Research Figure Guide — Preparing figures](https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/). It calls for accessible colour, labelled axes with units, legible labels and uncluttered backgrounds, and advises against overlapping text and decorative effects. Adopt these as figure-quality constraints: keep water and land visually distinct, retain numeric legends/units, and make rendering aids quiet. The guide does not prescribe a product UI palette or a particular lake colour.
- Source: [3D-LAKES: Three-Dimensional Global Lake and Reservoir Bathymetry from ICESat-2 Altimetry and Landsat Imagery, Scientific Data (2025)](https://www.nature.com/articles/s41597-025-05911-y). This Nature-portfolio data paper presents 3D bathymetry across many waterbodies, reports product uncertainty, and compares bathymetry with in-situ measurements. Adopt the separation between a lake's mapped surface extent, depth representation, and uncertainty/provenance. Do not treat its reconstructed bathymetry as measured for this application or copy a specific lake geometry.
- Art-direction decision for the current renderer: preserve scientific depth/field scales and the actual wet-cell boundary, show the lake surface by default with restrained translucent lake-blue, and keep the bed hidden while the black-patch cause is unresolved. Use only the verified one-cell dry fringe for surrounding context when no DEM is present. Label the shoreline as sampled from the wet grid; a smoothed display line may soften cell corners but must not alter wet masks or imply survey-grade geography.
