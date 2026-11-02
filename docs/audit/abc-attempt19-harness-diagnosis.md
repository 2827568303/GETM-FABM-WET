# attempt19 ABC acceptance harness diagnosis

Date reviewed: 2026-10-21

## Finding

`build/full-workflow-20261016-attempt19/round.json` remains a failed historical round. Its ABC stage failed while validating saved evidence; no native ABC rerun was performed, and this record does not relabel the old round as passed.

The saved API result reports `completed`, `success=true`, engine `pyabc-abcsmc`, 31 actual evaluations, and two populations. The saved SQLite database contains the same 31 simulations and four accepted particles in each population. Replaying the current strict database-backed validator against the saved result succeeds, including checks for accepted trial identity, parameter bounds, posterior weights, population epsilon, and improvement over the fixed midpoint baseline.

The original verification report ended with `AssertionError: `, had no `abc_evidence`, and its API call log contains no `/api/calibration/auto/apply` request. Thus failure occurred during evidence validation before apply. The recorded verifier hash for attempt19 was `9fe6a41027baf79b0be6dbce4e29986187360e8934ca49fd23a80efaf9a15539`.

The specific data-dependent failure is reproduced from the saved `abc.db`: in population 0 there are four distinct accepted `particle_id` values, but pyabc's default tidy `get_population_extended()` pivot returns only three rows. Particles 2 and 4 have the same distance (`0.0008415950817079984`) and weight (`0.25`) but different parameter values, so the tidy pivot merges them. The raw `tidy=False` view preserves all four particle identities (eight parameter rows). Population 1's tidy view has four rows. The old row-count assertion therefore rejected valid evidence only when distinct accepted particles shared both distance and weight.

This is an acceptance evidence extraction bug, not a solver/data failure or a scientific conclusion. The recorded status remains failed because the historical verifier report failed; the saved artifacts now independently validate under the corrected verifier.

## Repair and regression evidence

`scripts/verify_calibration_acceptance.py` now uses raw non-tidied database rows and groups by `particle_id`, matching every accepted particle back to an actual history evaluation. The distribution count, weights, bounds, posterior/database correspondence, baseline improvement, and evaluation budget requirements remain enforced. Acceptance errors now have descriptive assertion text and carry a named `failure_phase` plus error type/message in `verification.json`.

`tests/test_abc_acceptance_evidence.py` has a deterministic constant-objective fixture that confirms pyabc's tidy pivot loses duplicate distance/weight entries while the verifier still validates all four distinct particles. It also checks that even an empty `AssertionError` is recorded with its stage.

Focused verification on 2026-10-21: `python -m pytest tests/test_abc_acceptance_evidence.py -q` — 12 passed; `py_compile` passed for the verifier and test module. No full native ABC acceptance run was repeated.

## Scope

This change fixes and explains the ABC acceptance harness only. It does not claim attempt19 passed, does not establish scientific calibration accuracy, and does not prove a new full multi-stage workflow acceptance. The separate historical attempt artifacts were not modified.
