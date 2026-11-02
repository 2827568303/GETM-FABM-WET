# Result Variable Inventory Implementation Plan

> **For agentic workers:** Use the repository's GPT-6 Luna implementation assignment. The Sol owner will review the change and perform final browser and desktop acceptance.

**Goal:** Make variables present in valid companion `*.3d.nc` results selectable in 2D/3D analysis even when `output.nc` is the preferred default source.

**Architecture:** Keep the current preferred output file and its variable precedence. Expose valid companion 3D result files to the inventory endpoint, append variables not present in the preferred source, preserve each variable's actual `time_axis`, and include every companion file revision in the inventory cache key. Variable reads continue to use the existing variable-aware output selection.

**Tech Stack:** Flask, NetCDF metadata, Python pytest, browser-based 3DWET Studio.

---

### Task 1: Include companion 3D result variables in the inventory

**Files:**
- Modify: `3DWET/app/server.py` (`find_output_files`, `results_variables`)
- Modify: `3DWET/app/result_inventory_cache.py` (`inventory_key`)
- Create: `tests/test_result_inventory_companion_outputs.py`

- [ ] **Step 1: Add regression coverage**

  Create synthetic preferred and companion output files. Stub `get_variable_list` so the preferred file exposes `temp` and `greens_sDW`, while the companion exposes `temp` and `greens_cohort2_sDW`. Assert the inventory contains the preferred metadata for `temp`, includes `greens_cohort2_sDW` with its companion `time_axis`, and returns time labels for that companion axis.

  Add a cache invalidation assertion: changing only the companion file revision must cause `get_variable_list` to be read again and include the newly revised companion inventory.

- [ ] **Step 2: Run the focused test and confirm the regression**

  Run: `\.venv\Scripts\python.exe -m pytest tests/test_result_inventory_companion_outputs.py -q`

  Expected: the inventory omits the companion-only variable before the implementation.

- [ ] **Step 3: Implement companion discovery and merge**

  Extend `find_output_files` to return all existing non-empty 3D candidates in preferred-source order while retaining its current `2d`, `3d`, and `legacy3d` results. Merge their variable metadata into the 3D inventory by name, keeping the existing preferred source's record when names collide. Add all returned candidate paths to `inventory_key` so changes to any companion invalidate the cached inventory.

- [ ] **Step 4: Run focused and adjacent verification**

  Run: `\.venv\Scripts\python.exe -m pytest tests/test_result_inventory_companion_outputs.py tests/test_results_inventory_cache.py tests/test_output_selection.py -q`

  Expected: all focused inventory, cache, and output-selection checks pass.

  Query `/api/results/variables` for the isolated Erken cohort case and confirm `greens_cohort2_sDW` appears with the archived `ERKEN_USER_WORKFLOW_2026_WET.3d.nc` time axis. In the browser, confirm the variable appears in the 2D/3D selectors, select it, and read a frame.

- [ ] **Step 5: Synchronize and verify the desktop application**

  Restart the running desktop application from this workspace after the source change. Confirm `/api/results/variables` and static script responses from the desktop app match the current source and the new variable remains selectable in its browser view.
