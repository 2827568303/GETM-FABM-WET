# Four-lake proxy engineering runs — design

## Approval and purpose

The user approved proceeding with explicitly labelled proxy engineering runs for Erken, Lake Ravn, Bryrup, and Arreskov, and selected the recommended 3D workflow. These runs are intended to exercise the application and solver workflow. They are not scientific validation, calibration, or measured model results.

## Data and isolation

- Create one independent run directory per lake under a new timestamped `build/` attempt. Never edit or overwrite published/source cases, previous runs, or the active user case.
- Use only inputs already present in the audited local/official source packages. Record each input path, source description, byte count, SHA-256, and whether it is measured, derived, or synthetic proxy.
- Reuse spatial bathymetry/grid/boundary only where a traceable source exists. If a 3D GETM run requires missing spatial geometry, derive a clearly labelled engineering grid from the source hypsograph and record the derivation. Do not claim it is the real lake outline or measured bathymetry.
- Keep measured observations as comparison data only; never silently substitute observations for model initialization or forcing. If a short test needs an initialization surrogate, name it in the manifest and UI.

## User-visible behavior

- Register each attempt as `工程代理 · <lake>` and show a persistent `代理工程运行 / 非科学验证` badge in the case list, dashboard, run status, and result view.
- Show provenance status per input: `实测来源`, `代理/派生`, or `缺失/未完成`; preserve unknowns instead of filling them with plausible values.
- Disable scientific score/validation claims for these runs. Present model output as engineering-run output, and keep scientific-validation status `未完成`.
- The normal application journey must still be used: open/select case, inspect inputs, run preflight/build, launch model, inspect progress and outputs, open 2D/3D result views, and review/download results. A direct solver invocation can diagnose the engine but cannot count as UI-flow acceptance.

## Execution and failure behavior

- Start with the smallest stable, source-supported window. Do not invent a longer simulation period or forcing record to make a run appear complete.
- Preserve logs, input/output manifests, exit codes, solver identity/hash, and expected output checks in the isolated attempt.
- If any case cannot be built or run from available sources, retain its precise blocker and keep it `未完成`; do not turn another lake's output into a substitute.
- Never delete the attempt or source files as part of cleanup.

## Acceptance evidence

For each lake, acceptance requires a case visible in the app with the proxy badge, complete provenance manifest, successful preflight/build, successful solver completion with readable nonempty outputs, and successful dashboard/result-view navigation. This establishes only a proxy engineering run. Independent scientific validation remains a separate requirement and must remain `未完成` until justified by suitable observations, forcing, geometry, and evaluation design.

The design does not change the black-bed conclusion, the Nature-inspired art direction, or food-web scientific semantics. Existing tests are evidence only for their covered code; final acceptance still requires the user-requested application feature walk-through and separate case-level scientific review.
