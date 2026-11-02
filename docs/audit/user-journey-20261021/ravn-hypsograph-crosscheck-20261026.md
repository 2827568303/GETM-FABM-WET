# Ravn depth-zone / hypsograph cross-check

**Owner:** Sol 高

**Status:** measured-source audit; candidate depth raster remains **代理/未构建**; Lake Ravn 3D validation **未完成**.

## Read-only source check

Inputs were reused from the official Aarhus University QWET Ravn workshop snapshot `build/ravn-getm3d-candidate-20261024-luna01/source/`; no files were transformed and no model was run.

- `HYPSOGRAPH/Ravn_depth_map.shp` has 33 features in classes `DYBDE=0..32`. The geometric area of each feature matches its `area_hyps` field to the precision stored in the shapefile. Their total is **1,821,419.685 m²**, matching the workshop workbook's **1,821,420 m²** surface-area entry to <1 m².
- Summing classes from deepest (`DYBDE=32`) toward shallower classes and comparing the cumulative areas to the bottom-up `HYPSOGRAPH/hypsograph.csv` at the nearest integer depth step gives a maximum absolute relative difference of **0.658%**. Endpoints are 1,552 m² versus 1,546 m² at the deepest end and 1,821,420 m² versus 1,813,954 m² at the shallow/top end. This strongly supports the category ordering and area consistency of the depth zones.
- The separate shoreline polygon area in `shapefiles/Ravn_outline.shp` is **1,782,658.425 m²**, about **2.13%** below the depth-zone/workbook total. The two source geometries therefore need a spatial overlay and documented boundary decision before rasterization; this area discrepancy must not be silently normalized away.

## What this does and does not establish

The area-curve agreement supports a candidate **derived** bathymetry: assign an explicitly documented representative depth to each integer depth zone, rasterize to a chosen GETM grid, and compare the resulting hypsograph to the workshop curve. However, `DYBDE` is a band/category field, not an observed continuous depth at every point. The cross-check does not establish exact within-band bed elevation, grid resolution, shoreline reconciliation, river-cell locations, or vertical datum. Any such raster is a **proxy/derived candidate**, not pointwise measured bathymetry; it would need to retain provenance and uncertainty.

No solver-ready Ravn 3D case was created and no scientific output was generated. The official 1D study is a separate literature benchmark, not evidence that a current GETM 3D case has been validated.
