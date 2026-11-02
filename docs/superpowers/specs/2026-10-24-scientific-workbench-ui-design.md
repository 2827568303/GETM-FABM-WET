# GETM-FABM-WET UI redesign direction

## Scope and decision

Redesign the existing scientific lake-model desktop/web interface as a light scientific workbench. Prioritize the lake map/result canvas and preserve scientific controls, model inputs, and workflow affordances. This is an interaction and visual hierarchy direction, not a claim that the full workflow has passed.

## Art direction

Use a quiet warm-white/cool-gray foundation, restrained blue-green accents, high-contrast text, and semantic status colors. Let model data and scientific colormaps carry most of the saturated color. Build hierarchy with spacing, typography, grouping, and consistent control sizes rather than decorative gradients or oversized marketing typography. Keep chart/map canvases visually dominant.

## Information architecture

- Left navigation groups work into case/data, configuration, and run/review stages, with the active case and run state always visible.
- Main workspace gives the largest area to map, 3D scene, charts, and result tables; keep playback and view controls adjacent to the canvas.
- Right inspector is collapsible and context-sensitive for variable selection, foodweb, diagnostics, and selected-object details.
- Long/advanced parameter sets use progressive disclosure with clear defaults, units, provenance, and validation messages.
- Foodweb opens on relationship editing and validation: select consumer and port, choose prey target, edit required parameters, inspect parsed evidence, and see unresolved/invalid references. Keep topology as a synchronized visualization, not the only editing surface. Preserve provenance distinctions between configured evidence, proxy data, and missing validation.

## Interaction and accessibility

Keep primary actions predictable and keyboard reachable. Use visible labels, units, focus indicators, and non-color status cues. Maintain readable contrast and responsive resizing. Preserve current language and scientific data semantics; do not hide errors or relabel proxy results as measured evidence.

## Alternatives considered

1. Recommended: light scientific workbench with a large canvas and contextual inspector. Best fit for multi-stage scientific work and dense 2D/3D data.
2. Minimal light dashboard: easier to scan but risks flattening the complex model workflow into generic cards.
3. Preserve current visual system with local polish: lowest disruption but does not resolve current hierarchy and discoverability issues.

## Rationale and references

- Reference selection is based on published first-party design guidance, not an asserted global ranking: there is no single comparable public score that establishes the “best” model or company style for a scientific desktop workbench.
- Apple Human Interface Guidelines, [Charts](https://developer.apple.com/design/human-interface-guidelines/charts): recommends keeping data visually prominent, maintaining consistent hierarchy, and providing contextual, accessible chart descriptions. Adopt canvas-first hierarchy and concise context labels; do not copy Apple-specific ornament or controls.
- Figma, [Define your design system](https://help.figma.com/hc/en-us/articles/14552740206743-Lesson-2-Define-your-design-system): treats accessibility, color, typography, and component dimensions as shared foundations. Adopt semantic color/type/spacing tokens so dense scientific pages remain consistent.
- Esri ArcGIS Dashboards, [Effective dashboards](https://doc.arcgis.com/en/dashboards/latest/reference/author-effective-dashboards.htm): recommends sizing and placing elements by importance and relationship, grouping maps with their legends, and limiting color overload. Adopt the map/result-first canvas, close legend/context grouping, and restrained accent use for a geospatial scientific workbench.
- IBM Carbon, [Data visualization color palettes](https://www.carbondesignsystem.com/building-blocks/data-visualization/color-palettes) and [color accessibility](https://www.carbondesignsystem.com/building-blocks/foundations/accessibility/color): separates categorical from sequential palettes, cautions against using hue alone for meaningful progression, and explicitly calls for non-color cues. Adopt semantic status colors and reserve scientific gradients for quantitative data scales.
- Microsoft Fluent 2, [Navigation usage](https://fluent2.microsoft.design/components/web/react/core/nav/usage/): emphasizes brief plain-language categories and a navigation rail that can minimize to reclaim space. Adopt concise task-grouped navigation while leaving the scientific canvas expanded.
- U.S. Web Design System, [Design principles](https://designsystem.digital.gov/design-principles/): organizes decisions around user goals and makes accessibility a design constraint. Adopt readable contrast, logical reading order, keyboard operation, and status cues that do not rely on color alone.
- Taken together, these references support a restrained scientific workbench rather than a marketing dashboard: data owns the strongest color, the workspace stays light and quiet, and workflow/state context remains explicit.

These are authoritative design-system references, not an objective ranking of the world's "best" companies or models.

## Acceptance boundary

The design direction is approved for implementation. Completion still requires reviewing the changed interface and verifying desktop synchronization. Workflow and case-science acceptance are tracked separately in the audit status; this document makes no validation claim.
