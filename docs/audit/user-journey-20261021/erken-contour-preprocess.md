# SITES Erken contour import and grid preprocessing audit

Date: 2026-10-21

## Scope

Verified the shapefile import → boundary mask → contour interpolation workflow using isolated copies of SITES Erken GIS files. No model case was saved or modified, and no solver was run. This is a preprocessing/API workflow check, not an Erken simulation or scientific validation.

## Source and provenance

- SITES Erken background/GIS package: [official SITES metadata record](https://meta.fieldsites.se/objects/QKSpXl2ew-4DMYlryJ3oM7hD), licensed under SITES CC BY 4.0.
- Lake outline: `SITES-ERK-ERK_Lake-Outline_EPSG3006.geojson`, EPSG:3006, SHA-256 `a718d8ff93d648220b2763fd43f9a6c7eae0bb6ae18dec69856380fdffef0dbd`.
- 1 m contours: `SITES-ERK-ERK_Bathymetry_contour-1m_EPSG3006.geojson`, EPSG:3006, SHA-256 `5829b9ec8e5fcc5c98a59c73ce76232be15985ad46ed0d6f52fc9d5677840722`.
- Isolated shapefile derivatives and the reproducible API-trial script/report are under `build/real-use-validation-20261021/erken_contour_import_trial/`. Official GeoJSON source files were read only.

## Defects found and changes

1. Boundary upload selected only `parts[0]` for each feature. The official outline has a small island polygon before the main lake and many interior rings; treating the first part as the lake boundary produced a tiny bbox and no useful water cells. Import now groups every clockwise ring as an exterior, attaches contained counter-clockwise rings as holes, and rasterizes each exterior minus its holes before unioning lake/island groups. The cache and response expose exterior and hole counts.
2. Geographic boundary conversion used a linear lon/lat approximation while point/contour data used PyProj. At 18.55°E, 59.85°N this placed the approximate northing at 6,617,854 m versus exact WGS84 / UTM 34N at 6,637,244 m, a roughly 19.4 km discrepancy. Geographic-to-UTM conversion now uses a zone-keyed cached PyProj transformer.
3. Bathymetry import previously tried to infer a depth column and did not accept PolyLine. The upload now requires an explicit numeric `depth_field`, supports line contours, samples line parts without connecting multipart gaps, reports source/target CRS, fields, depth range, and sample count, and resamples contours at a grid-relative spacing for interpolation. The UI draws open contour lines and explains the explicit field requirement.

## Verification

Focused regression file: `3DWET/tests/test_bathymetry_contour_import.py` — **5 passed**. It covers missing-field rejection without cache writes, explicit `CONTOUR` import and interpolation, multipart line separation, multipart exterior/hole mask behavior, and exact geographic-to-UTM projection. Combined with `test_geo_field_fill.py` and `test_spatial_sections.py`, the relevant suite reported **17 passed**. `node --check 3DWET/app/static/js/preprocess.js` and `python -m py_compile 3DWET/app/server.py` passed. Pytest emitted one NumPy binary-compatibility runtime warning during import; it did not fail tests.

Sol independently exercised the official chain against the running 8766 HTTP service:

| Grid spacing | Grid result | Interpolation result |
|---|---|---|
| 250 m | 376 water cells, 23.5 km² | 4,985 effective samples; 1–19.37 m; 0.18 s |
| 100 m | 2,291 water cells, 22.91 km² | 11,834 effective samples; 1–20 m; 0.35 s |

Both runs uploaded the 286 contour features with an explicitly selected `CONTOUR` field (1–20 m); the 25 m preview contained 23,228 points and upload took 0.427 s. The outline resolved to 2 exterior groups and 68 holes. Direct exterior-minus-hole area was about 23.038 km²; the 100 m raster area differed by about 0.56%. The 250 m water-area estimate is coarser and should not be treated as a precise shoreline-area measurement.

The implementation environment did not expose a browser or local file chooser (`cua.getState()` returned no apps/browsers). The served page loaded `preprocess.js?v=11`, and the UI now overlays separately sampled holes; manual selection of local shapefile sidecars and visual inspection of the colored line preview remain unverified here. Sol confirmed the file chooser tool did not populate the browser input. The API import/interpolation results above are independently verified over HTTP; do not describe the browser upload gesture as accepted.

At the latest source check, `/api/system/health` returned ready on desktop instance `2de79e6b31894df5969737cfe1046ddb`, PID `15372`; the run status was idle. `GET /` referenced `preprocess.js?v=11`; the served and workspace JS SHA-256 both equaled `D6CEE72C56B3B937C4FF886F6E3941D49097535EA5B21B6FE4A48B9F78D81175`. `GET /api/preprocess/help` returned the updated MultiPolygon/hole and explicit depth-field/PolyLine metadata. The current synchronized workspace server source SHA-256 is `0EE6631E0F5EFA34DEF57B49102F3D7EEDBA9283F600AD09B806B7F182D4F1EF`.

## Limits

- Contour interpolation is display-independent preprocessing from line depth samples; it does not validate the contour survey, vertical datum, or lake hydrology.
- The input files are official SITES Erken geometry, but the measured grid and interpolated bathymetry are only preprocessing artifacts. No Erken model output or scientific result was validated.
- Review CRS labels and alignment percentage before interpolation. Use a finer grid when shoreline area accuracy matters, subject to memory and solver costs.
