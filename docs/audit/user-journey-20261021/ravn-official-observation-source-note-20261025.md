# Lake Ravn observation source note (2026-10-25)

## Official portal export

Kemidata's official search returned station **21000355**, `RAVNSØ, MIDT -- RAV1 - vandkemi`, for the requested 1990-01-01 to 2006-12-31 window. Its `Datamart Feltmåling Sø` index reported 342 examinations and 18,679 result rows. The filtered station CSV is [archived here](ravn-station-21000355-field-measurements-1990-2006-20261025.csv), SHA-256 `D220B89DAD19A15EB4E6F48BAA079683C950754DF21EA8A9CD965794D2ED0176`, size 6,154,299 bytes. It contains 18,679 rows from station 21000355; 6,397 are `Temperatur` rows with values from 0.9 to 25.1 °C and depths from 0 to 32 m. Temperature occurs on 342 unique dates and 344 unique `Startdato` sampling timestamps; per timestamp there are 1–34 temperature rows. Exact date/time/depth duplicates were not found. The file includes oxygen, oxygen saturation, pH, conductivity, and salinity fields as well.

The raw record retains Danish decimal commas and timestamp offsets such as `+01:00`/`+02:00`. These offsets must be interpreted consistently before matching model output. Station name `RAV1` and the row-level cross-check below strongly connect this source to the archived Ravn observation stream; the exact spatial interpretation of the `Ravn-column` model setup remains unverified.

## Cross-check against the official workshop observations

The official workshop files `OBSERVATIONS/TEMP.obs` (SHA-256 `059f102895e18a9770e14043d624bf4413b78ed7582edd548f9b552341f512e6`) and `DO.obs` were compared against the new portal export by calendar date and absolute depth, then by measurement value and local wall-clock time. This is a source-lineage cross-check, not an independent validation:

- **Temperature:** 6,382 `TEMP.obs` rows share a date/depth with portal temperature rows. Of these, 6,369 have an exact value match, 6,378 have a value within 0.1 °C, and 6,363 have a unique exact-value match whose sampling wall-clock is within 12 hours (5,918 within one hour; median gap 0 h).
- **Dissolved oxygen:** 6,255 `DO.obs` rows share a date/depth with portal `Oxygen indhold` rows. All 6,255 are within 0.1 mg/L, 6,253 have an exact match, and 6,247 have a unique exact-value match whose local wall-clock is within 12 hours (5,837 within one hour; median gap 0 h).

These repeated value/time/depth correspondences strongly support that station 21000355 is the source stream represented in the official workshop observation files. They do not establish all original station metadata or a spatial remapping beyond that observation stream. `TEMP.obs` has 11,904 physical rows; the current parser yields 11,832 usable records and 20 parse diagnostics.

## Existing 1D temperature holdout diagnostic

Without launching a new case, the existing official GOTM-WET output `runs/grid_11_0.30/output.nc` from the archived 21-point `kNitrW` profile was paired using the application's native GOTM column extraction and time/depth interpolation (`max_time_gap_hours=12`). The output SHA-256 is `8EDD2FAF797368757B7FD12AE27D02E40F703BDCDB892C00DDC756B2295A51BF`. For 2001–2005 `TEMP.obs`, 1,810 of 1,852 rows paired; 42 were outside the output layer-center depth range. On those pairs, bias (model minus observation) was −1.239 °C, RMSE 1.966 °C, and MAE 1.571 °C. This is a **代理** diagnostic for the project's target GETM 3D validation: it is the upstream one-dimensional WET column, under the existing official/default setup and its known limitations. The observations are **实测**; this result does not complete the target Lake Ravn scientific validation.

## Status and limits

- Exported source rows and measured water properties: **实测**.
- Link from this monitoring station to the model column, time/depth conventions, quality-marker semantics, variable mapping, and performance pairing: **未完成** / **不确定**.
- The earlier official workshop `.obs` comparison remains an upstream 1D comparison and **代理** for the target GETM 3D lake validation. This new export does not upgrade it.
- The official [Feltmåling Sø catalogue](https://arealdata.miljoeportal.dk/datasets/urn:dmp:ds:feltmaaling-soe) describes the dataset fields but the applicable reuse licence was not confirmed in the retrieved page. Redistribution rights remain **不确定**.

Source: [official Kemidata portal](https://kemidata.miljoeportal.dk/), station search `Ravnsø`, station number `21000355`; [official Feltmåling Sø dataset catalogue](https://arealdata.miljoeportal.dk/datasets/urn:dmp:ds:feltmaaling-soe).

**Licence update (2026-10-25):** the official [Datavejviser JSON-LD record](https://datavejviser.dk/katalog/danmarks-miljoportal/2ba457fb-a819-4e9c-8d4a-0d2de28c5197.jsonld) identifies the `Feltmåling Sø` dataset and its CSV distribution as CC0, with public access. This resolves the earlier licence uncertainty for this category. Model-column mapping and target GETM 3D validation remain **未完成**.

## Spatial anchor follow-up

The official raw portal export for station 21000355 contains the sampling-site coordinate tuple `GeoZone=32`, `X=552519`, `Y=6218243`; the same tuple appears throughout the station CSV. The official VanDa checklist specifies its default as UTM / ETRS89 / zone 32N; the Danish geodesy authority maps ETRS89 / UTM 32N to EPSG:25832. Under that documented interpretation, the point transforms to `9.844418°E, 56.106400°N`. A point-in-polygon check against the official ETRS89/UTM32 shoreline shapefile places it inside the Ravn outline and inside one official depth-zone feature `DYBDE=31`, `area_hyps≈15,437.97 m²`. This confirms a spatial anchor and geographic consistency; it does not convert `DYBDE` into an exact depth, establish the source row's datum beyond its absent explicit CRS field, or identify a GETM grid cell that has not yet been constructed.

The original official CSV also matches the workshop `TEMP.obs` and `DO.obs` streams by date/depth/value, as documented above. The station location is no longer a missing-source blocker. A reviewed bathymetry/grid and explicit point-to-cell/time-depth matching rule remain required before scoring GETM 3D output.

Sources: [VanDa data-entry checklist](https://miljoe.atlassian.net/wiki/spaces/DFVPUB/pages/2030534658/Vanda+-+Tjekliste+til+udfyldelse+af+data), [Danish coordinate systems](https://www.klimadatastyrelsen.dk/kortlaegning/geodaesi/koordinatsystemer). Local evidence: `build/ravn-getm3d-candidate-20261024-luna01/source/shapefiles/Ravn_outline.prj`, `Ravn_outline.shp`, `HYPSOGRAPH/Ravn_depth_map.shp`, and the official CSV SHA-256 above.
