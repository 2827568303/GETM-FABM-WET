# Academic UI and scientific 3D implementation plan

Implementation owner: GPT-6 Luna (medium). Overall design, root-cause uncertainty, integration, and final acceptance: GPT-6.1 Sol (high).

## Design reference

Follow `docs/superpowers/specs/2026-10-25-restrained-scientific-3d-design.md`. This plan supersedes the earlier grayscale-only styling instructions. The approved direction is an overall academic redesign in warm, restrained earth/lake colors, with strong color reserved for scientific model fields and semantic statuses.

## Task 1: Shared application visual system

- Inspect CSS cascade, page components, responsive behavior and current source app before editing.
- Define consistent tokens for warm paper/canvas, stone surfaces and separators, text hierarchy, muted lake-slate primary, sage secondary, ochre provenance/workflow, and semantic statuses.
- Redesign shared navigation, brand block, menu/toolbars, project/run topbar, dashboard, workflow indicators, cards, buttons, tables, fields, dialogs, results canvas and inspector. Maintain existing IDs, page routing, labels/data hooks, keyboard focus and all workflows.
- Remove decorative gradients, neon cyan/purple, heavy shadows and excessive rounded-card layers. Do not flatten the full UI to gray; retain visible but muted tone distinctions.
- Recheck mobile/tablet breakpoints, then review the dashboard and one scientific workbench visually.

## Task 2: Improve triangular 3D expression

- Preserve the mesh-generation path, wet mask, diagonal, source values, field color scale and tooltip semantics.
- Make the derived triangle facets read spatially through clear controlled edge definition, modest face lighting, a useful silhouette, and direct camera-elevation / vertical-exaggeration interaction where current controls allow. These are display cues only; do not alter geometry or imply physical scaling changed.
- Keep data-driven model colors intact, nodes off by default, and continuous surface available as an alternative. Keep derived display topology disclosure.
- Do not claim the black-bed defect is fixed. It is still **未修复** and the cause **不确定**.

## Task 3: Replace playful iconography

- Replace emoji/Unicode pictograms in shell navigation, toolbar, dashboard, empty states and common scientific controls with a consistent technical outline icon family.
- Use 20–22 px line icons with shared stroke and restrained corners. Keep functional labels/ARIA names and tooltips; color inactive icons with current text color, use only muted lake/sage for active state.
- Preserve behavior and selectors. Avoid adding a large third-party dependency; inline reusable SVG symbols or a small local icon helper is preferred.

## Task 4: Review, tests and desktop synchronization

- Review the diff to ensure model data, route/control behavior, and unrelated scientific logic remain unchanged.
- Run targeted existing UI/CSS/3D checks as appropriate; do not launch a new scientific case. Before any case run in a future task, inventory and remove only explicitly unwanted disposable outputs, preserving active or audit-referenced evidence.
- Start/synchronize the desktop source app through its normal launcher after code edits. Do not kill unknown or build-isolated API services. Verify the desktop source port, served template asset versions and hashes against disk.
- Sol independently reviews the visual result, reports the source sync and explicitly retains all unresolved workflow/case statuses.

## Scope boundary

This UI/3D work does not complete the full user workflow, certify Erken/Lake Ravn/Bryrup/Arreskov science, or repair the black bed patch. Report those independently as **实测 / 代理 / 未完成**, never treating proxy output as measured validation.
