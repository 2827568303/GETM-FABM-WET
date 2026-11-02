# Official WET testcase availability check (2026-10-24)

## Source snapshot

- Downloaded the public official WET repository archive from `https://gitlab.com/wateritech-public/waterecosystemstool/wet/-/archive/master/wet-master.zip`.
- Archive SHA-256: `9B41D348E5B992767DC90D7C0C9A86896598A5059E605AE5644F4C7EB0F92732`.
- Snapshot directory: `build/real-use-validation-20261024/wet-official-testcases/official_repo/wet-master/testcases`.

## Bryrup

- The repository includes `lake_bryrup_denmark` with GOTM/FABM configs, forcing, inflow chemistry, outflow, hypsograph and output schedule. Its `gotm.yaml` covers 1990-01-01 through 1995-12-31, i.e. the six-year spin-up only.
- A rerun with the `gotm.exe` supplied in the official Lake Ravn package initialized the 18-layer, 9 m Bryrup case, then stopped at FABM initialization: `AdFish: "wet/fish" is not a valid model name` (exit code 1). This binary/configuration pairing is incompatible; no Bryrup output from this attempt is accepted.
- This is consistent with the need to use a case-compatible WET/GOTM source and its calibrated parameter sets. The official WET 1.0 paper describes six spin-up years, calibration during 1996–2004, validation during 2004–2006, and NOVANA observations. See the [WET 1.0 paper](https://gmd.copernicus.org/articles/15/3861/2022/) and official [WET testcase source](https://gitlab.com/wateritech-public/waterecosystemstool/wet/-/tree/master/testcases/lake_bryrup_denmark).
- Status remains **未完成** for reproducing the scientific case and its independent validation. Earlier short smoke runs remain **代理** only.

## Arreskov

- The repository snapshot includes `lake_arreskov_denmark` with GOTM configuration, meteorology, inflow, outflow, chemistry, hypsograph, water level and manipulation schedule. It does not contain a case-local `fabm.yaml` in this downloaded `master` archive, so the run cannot be reconstructed from this directory alone without locating the matching official configuration or complete supplementary materials.
- The official paper describes a 16-layer, 4 m lake configuration, calibration over 1992–2005 with two spin-up years, and six parameter-selection ensembles; the article also says the configuration is in the WET repository. The present archive therefore appears incomplete relative to the article's referenced artifact. See the [official paper](https://doi.org/10.1016/j.envsoft.2022.105501) and [repository case directory](https://gitlab.com/wateritech-public/waterecosystemstool/wet/-/tree/master/testcases/lake_arreskov_denmark).
- No missing FABM configuration was inferred or fabricated. Status remains **未完成**; no Arreskov simulation or scientific validation is claimed.

## Follow-up release and compatibility checks

- The official WET v2.3 Zenodo package (`17453175`) contains published Windows GOTM-WET release/debug executables and a case archive. Executable archive SHA-256: `E17467A60BDCE02DE929BB432EADBF1FCE2D16130FF43F449425287440EBB6F1`; source archive SHA-256: `68873F3D623FF0A90A007C567796DFEF2FADAB61F8F8B87073FB8F7355A721A8`.
- The v2.3 Bryrup configuration was also tried with the matching v2.3 release executable. It initialized GOTM and FABM through the `AdFish` model, then stopped because `BENpref1` is not recognized by that release. This confirms a config/release incompatibility; it is not a successful rerun and produced no acceptable validation result.
- The official WET v0.2.0 Zenodo archive (`8369208`) was inspected as an additional historical release; SHA-256: `A7988737D1619722B514747CCD3DDE60C5B7B660DD95E0CE8832DC0B356D3607`. It includes the Bryrup configuration but, like v2.3 and the current master snapshot, its Arreskov folder has `.gitkeep` rather than `fabm.yaml`.
- The Arreskov publication names a Zenodo/software release and a supplemental-data DOI, but the matching case-specific FABM configuration has not yet been located. Its absence from these official archives does not authorize reconstructing model inputs from the paper narrative.
