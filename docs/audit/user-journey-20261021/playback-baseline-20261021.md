# 2D / 3D playback baseline (Sol observation)

Date: 2026-10-21 (Asia/Shanghai)

## Scope

This is an interactive playback and response-time baseline for the generated `competition_treatment` case currently selected in the local desktop application (`http://127.0.0.1:8766/`). It is a UI/performance repro case, not a real-lake dataset or scientific validation. The case has 24 hourly outputs from 2020-01-01 01:00 through 2020-01-02 00:00. The 2D selected result is surface temperature (`temp`, level 5; 14×21). The 3D temperature field is 6×14×21.

Output file SHA-256:

- `EXTERNAL_SEED_LAKE_WET.2d.nc`: `C28ADDE1086CC2BFACE21BD66843E44553107CA464E750BCB92261C9B66DCAAA`
- `EXTERNAL_SEED_LAKE_WET.3d.nc`: `61B9E8D353FF725B2D50A6AB2536A6792E5AC90DDA18B8AE2441FCFC48A0B6CD`

## Observed UI behavior

- In 3D, starting at frame 0 and selecting a target of 12 frames/s advanced the visible model time, frame slider, 3D colorbar, and displayed temperature range. The observed main-view range included frame 0 at approximately 15.3399–15.4934 °C and frame 23 at 14.1569–15.5572 °C.
- In 2D, starting at frame 0 with a 12 frames/s target advanced the visible slider through at least frame 14. API results show changing current-frame ranges: frame 0 15.34–15.44 °C, frame 1 15.34–15.47 °C, frame 10 15.07–15.46 °C, and frame 23 14.16–15.19 °C.
- In 3D, a pointer drag across the model visibly changed its viewing angle. The `俯视` preset also changed the scene to a top-down view; choosing `复位` returned it to the default oblique view. Playback was paused during the camera check.
- Playback was paused afterward. The UI was restored to 3D temperature at frame 23, paused, with the original 1 frames/s setting.

The UI frame observations used repeated accessibility snapshots. A snapshot itself took a substantial fraction of a second, so the sampled frame transitions cannot be treated as an exact renderer frame-rate measurement; the polling may also add browser work. This confirms that playback changes the displayed result but does not quantify the true render cadence. A dedicated in-page performance trace is required for that.

## Sequential API baseline

Measured locally with sequential `Invoke-RestMethod` requests against the selected case. The first request is shown separately as a cold/warm-up observation. These numbers include server work, serialization, transfer, and client decoding; they do not include frontend mesh construction or Plotly rendering.

| View | Requests | Response shape / bytes | Cold request | Warm requests | Warm median |
|---|---|---:|---:|---|---:|
| 2D `temp`, level 5 | frames 0, 1, 2, 3, 10, 23 | 14×21 | 401 ms | 248, 264, 246, 243, 254 ms | 248 ms |
| 3D `temp`, target 22 | frames 0, 1, 2, 3, 10, 23 | 6×14×21; frame 23 response 110,978 B | 314 ms | 129, 138, 127, 128, 129 ms | 129 ms |

At the 12 frames/s target, the nominal interval is 83 ms. The 2D and 3D result endpoints alone exceed that interval in this case, before the browser draws anything. The playback control is therefore an upper target; current evidence does not show that 12 frames/s is achievable for this case.

## Implementation fingerprints at baseline

- `3DWET/app/server.py`: `FDD016AF8D49BF4444732010D998ED90E7175B02E4227BD3224513DDA22FFE01`
- `3DWET/app/static/js/app.js`: `C178E16B699A4AC2B4166C4BB5BD11B31DBDBA102FF66796383EB31D58B17C5B`
- `3DWET/app/static/js/viz3d.js`: `8E415705AAF753F1D7D016A5D6D17AD9A72321228604B4367BC56EE383071396`
- `3DWET/app/static/js/scientific_workspace.js`: `E5CB990547A202D56EBC3659F8DE9EA8F4AF96E12AAB505459DD2D39C752DF1E`

## Next measurement

Capture frame request, data/geometry preparation, Plotly draw start/end, published timestamp and current frame inside the page without repeated accessibility snapshots. Compare before/after on this exact case and fingerprint. Preserve the separate endpoint and frontend timings; do not describe the endpoint baseline as total frame time.
