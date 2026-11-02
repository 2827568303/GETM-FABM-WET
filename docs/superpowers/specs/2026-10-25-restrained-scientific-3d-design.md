# Academic scientific workspace redesign and 3D expression

## User direction

Redesign the application as a whole. Make it academically restrained and simple, but do not reduce it to black and white. Use quiet, natural color in the interface and reserve strong color for scientific model displays. Improve the expressive 3D presentation of the triangular network. The user approved the direction to proceed. Reference image: `（待补充：参考图的具体路径或链接）` (user expects to provide it later).

## Research and design judgment

The references are specialist scientific software documentation, not claims about a ranked list of the world's best products or companies:

- [ParaView: Displaying data](https://docs.paraview.org/en/latest/UsersGuide/displayingData.html) separates render view, pipeline visibility, and selected-object display properties. Adopt a clear primary workspace with controls contextual to the selected view/data.
- [napari: Quick start](https://napari.org/dev/getting_started/quick_start.html) frames layers as the way to inspect multidimensional images, models, and analysis in one viewer. Adopt legible, controllable layer/overlay hierarchy without putting decorative color on controls.
- [QGIS: 3D Map View](https://docs.qgis.org/3.44/en/docs/user_manual/map_views/3d_map_view.html) exposes terrain resolution, model scale, camera, cross-section and optional rendering effects. Adopt direct, labeled camera/vertical scale controls and keep effects optional.
- [Matplotlib: Choosing Colormaps](https://matplotlib.org/stable/tutorials/colors/colormaps.html) recommends perceptually appropriate sequential/diverging/cyclic maps and uniform lightness for data. Preserve quantitative palettes and legends; distinguish them from interface theme colors.

Further source review following the user's correction:

- [ParaView: Displaying data](https://docs.paraview.org/en/latest/UsersGuide/displayingData.html) documents scalar coloring, surface-with-edges line width, and contextual display properties. This supports keeping the selected field's scale/legend attached to the view while exposing mesh structure as a separate, adjustable representation.
- [ParaView: Color maps and transfer functions](https://docs.paraview.org/en/latest/ReferenceManual/colorMapping.html) explains transfer-function ranges, legends, and separate color maps. This supports preserving meaningful field palettes and explicitly separating those from interface chrome and structural mesh color.
- [napari: Layers](https://napari.org/stable/getting_started/layers.html) treats surfaces, vectors, points, labels, and images as distinct, controllable layer types in 2D/3D. This supports an explicit layer hierarchy rather than decorative overlay clutter.
- [QGIS: 3D Map View](https://docs.qgis.org/3.44/en/docs/user_manual/map_views/3d_map_view.html) provides camera/zoom, measurement, export, optional effects, and debug controls. This supports grouped, labeled view controls and making rendering aids optional.

The application-specific art direction is **field notebook + geoscience workstation**: a warm limestone/paper foundation; blue-green slate for primary navigation and selected state; muted lake blue and reed/sage green for secondary hierarchy; restrained clay/ochre for provenance and calibration; ink-green text; and fine mineral-gray separators. This intentionally uses a small, coordinated, low-chroma color family—not black-and-white, not one accent color, and not bright decoration. It should feel like a serious scientific instrument with a natural-material palette. Preserve strong, quantitatively meaningful color in model fields and their legends. This palette is Sol's design judgment; the sources inform scientific interaction patterns, not an objectively best brand palette. Avoid neon cyan/purple chrome, gradients, glows, excessive rounded cards, oversized empty hero areas, and repeated shadows.

For the food-web inspector, promote each enumerated three-instance/two-edge configured path from passive prose to an actionable focus control: activating it should identify its exact nodes, edges, and matching relation-table rows; keyboard users need equivalent activation and a clear-focus command. This follows the source-backed pattern of keeping object selection contextual to the scientific view and improves traceability without implying runtime feeding or trophic validation.

### Revised whole-interface direction

The previous implementation is not accepted merely because it is restrained: the whole shell must feel deliberately designed, colored, and academically mature. Recompose the dashboard and each workflow around a clear information hierarchy: compact scientific navigation, a visible case/run context, a generous result canvas, and a contextual properties pane. Use real content density, useful section headers, thin rules, tabular alignment, and small but legible labels. Distinguish primary/secondary/tertiary actions with layout and subdued material colors, not a field of identical white cards. Preserve workflow and control behavior. Keep strong color for model values and semantic alerts.

### Revised technical icon system

Redesign every visible icon (including menu, toolbar, page navigation, view tools, empty states, and dynamically rendered controls) as one coherent scientific icon family. Use precise drafting/diagram cues—axes, sections, grids, basin contours, layer stacks, instruments, and measured arrows—with geometric rather than toy-like silhouettes. Use a consistent 24-unit grid, mostly 1.5–1.7 px strokes, crisp controlled joins, limited filled anchors only where needed for legibility, and no cartoon/emoji/rounded-puffy styling. Active states may use lake slate, sage, or ochre according to role; inactive icons retain sufficient contrast. Pair less familiar icons with text/tooltips and preserve keyboard/focus accessibility. Icons should reinforce the function, not act as decoration.

## Whole-interface redesign

Redesign the shared application shell rather than adding a theme patch to one page: navigation/sidebar, menu and tool rows, project/run status header, dashboard, workflow steps, cards/tables/forms, visualization workspace, contextual inspector, dialogs, and responsive breakpoints. Establish a small set of consistent design tokens for warm canvas/surfaces, borders, text hierarchy, lake-slate primary, sage secondary, ochre/provenance, and semantic statuses. Use typography and spacing to establish hierarchy, thin separators, restrained corner radii and little/no elevation. Keep all controls and page identifiers/behavior intact. Do not remove scientific controls or workflows.

The working layout should prioritize the scientific canvas, keep layer/model and run context findable, and place view-specific properties in a compact inspector adjacent to the canvas. Keep menus and toolbars compact and labels explicit. Data tables and numerical controls should remain dense enough for scientific work. Apply the system consistently to both dashboard and active workspaces.

## Iconography

Redraw **every** icon in the application shell, scientific controls, and dynamically generated UI as a single original technical line-icon family; recoloring existing artwork is insufficient. ParaView documents a toolbar/camera-control row and contextual object actions; napari documents a compact viewer-button row for 2D/3D, home/reset, grid, axes, and scale bar, with layer visibility controls. Adopt the same recognizable action semantics and keep icons close to their related canvas/control. Use a consistent 24×24 viewBox/pixel grid and 1.7 px stroke, with optically balanced geometry, consistent endcaps and joins, and deliberate scientific motifs such as sections, grids, and measurement marks where relevant. Avoid emoji, playful Unicode, cartoon faces, toy-like rounded shapes, decorative foliage, gradients, and multicolor fills. Icons inherit text color in the inactive state and use lake-rock blue-green or moss for active state; retain labels/tooltips for navigation and less familiar operations. The icon set must remain high-contrast and keyboard accessible.

Sources: [ParaView GUI and toolbars](https://docs.paraview.org/en/v6.0.1/Tutorials/SelfDirectedTutorial/basicUsage.html) and [napari GUI controls](https://napari.org/workshops/intro-gui/block2-gui/). These document action/control patterns; the technical icon styling above is the design decision for this product.

## 3D triangular-network expression

Make the 3D result view read as a spatial scientific object, not a decorative wireframe. Retain the existing valid-wet-cell triangulation and stable diagonal. Keep model field colors and numerical values unchanged. Improve expression using a coordinated set of visible depth cues: shaded cell facets with low-key ambient/directional lighting, crisp but subdued triangle boundaries, a readable basin silhouette, a restrained vertical stack/inter-layer structure where the data supports it, spatially separated shoreline/bed/water layers, and purposeful initial camera elevation. Give direct camera presets and labeled vertical-exaggeration controls with units/interpretation. The mesh should remain legible over both neutral bathymetry and a colored model field; its structural ink must not compete with the field palette. Avoid node markers by default, neon mesh lines, glow, arbitrary per-face colors, and effects that could be mistaken for model data. Keep continuous surface as an explicit alternative. State that displayed triangles/links are derived display topology rather than solver-native topology, and that display-only lifts/exaggeration are not physical geometry.

Do not present this work as a black-bed defect fix. The defect remains **未修复**; the current frame-19 comparison at 200x static bed / 50x overlay did not reproduce it. Its unique cause remains **不确定**. Reproduction and controlled one-variable comparisons are needed before cause or fix claims.

## Trade-offs and acceptance

Earthy low-chroma interface colors are more differentiated than grayscale while keeping data fields visually dominant. A muted active state is less flashy than a neon highlight, so pair color with shape, text, and focus indicators. Facets and inter-layer cues improve depth expression but may increase clutter and render cost; keep structure styling controlled, nodes off by default, and maintain a continuous alternative. Camera/vertical exaggeration improve relief readability but are display controls and must not imply changed physical geometry.

Acceptance requires: (1) a coordinated, visibly colored low-chroma system rather than grayscale, (2) a clear whole-shell redesign including dashboard, workflow pages, icons, and scientific workspace, (3) strong colors retained for model values and semantic status, (4) a perceptibly more spatial 3D network with understandable depth cues and direct view controls, (5) preserved controls/data/workflow behavior, and (6) visual review in the synchronized desktop application. This does not certify black-bed repair, complete user-flow execution, or validation of Erken, Lake Ravn, Bryrup, or Arreskov.

### Additional Sol research: scientific network visualization

The user's request refers to highly regarded scientific applications; “best” is not an objective rank, so the references below are selected as established specialist tools with inspectable official manuals rather than presented as a ranking.

- [Cytoscape 3.10.5: Styles](https://manual.cytoscape.org/en/latest/Styles.html) maps table attributes to node/edge color, size, shape, line type, and opacity, and places those controls in a dedicated Style panel. Adopt the principle that visual encoding should map to an explicit ecological/network attribute, while structural relation types can use restrained line/shape differences; avoid decorative color or arbitrary emphasis.
- [ParaView 6.2: Displaying data](https://docs.paraview.org/en/latest/UsersGuide/displayingData.html) keeps a central render view and updates contextual display properties for the active data/view. Adopt a dominant scientific canvas with controls grouped around selected data and allow rendering-only changes to update directly.
- [napari: Layers and viewer](https://napari.org/stable/getting_started/layers.html) distinguishes surfaces, points, vectors, labels, and other layer types with independent visibility and interaction modes. Adopt explicit layer roles and visibility for bed, field, shoreline, and display mesh, rather than fusing them into one decorative object.
- [QGIS 3.44: 3D Map View](https://docs.qgis.org/3.44/en/docs/user_manual/map_views/3d_map_view.html) exposes pitch/heading/camera distance and model scale as explicit view settings, and documents vertical exaggeration as a view property. Adopt labeled camera presets and vertical exaggeration as visualization controls, clearly separated from physical dimensions.

These sources inform interaction and encoding patterns; they do not establish a universal UI rating or dictate this application's colors. The low-chroma paper/limestone, lake-slate, sage, and restrained ochre palette remains Sol's art-direction decision. User-supplied reference image remains `（待补充：参考图的具体路径或链接）`.
