# Published Danish-lake model benchmark (context only)

**Owner:** Sol 高

**Use:** literature benchmark for case-readiness review; does not validate any local GETM-FABM-WET output.

The Aarhus University DCE Scientific Report 402 (Nielsen et al., 2020) says its five lake-specific calibrated models used **1D GOTM-FABM-PCLake**, including Ravnsø, Bryrup Langsø and Arreskov Sø. This makes it useful as a prior 1D reference, not an exact-stack benchmark for the current 3D GETM case.

For Ravnsø, the report lists maximum depth 32.6 m, mean depth 14.9 m, area 1.8 km² and 33 vertical layers. Its calibration period is 2004–2005 and validation period 1996–2003. The reported temperature comparison covers 0–5.2 m (epilimnion) and gives validation n=208, percentage bias −1.8%, Spearman rank 0.99 and R² 0.99. These values are study-reported results; no local reproduction was performed.

**Local status remains:** Lake Ravn/Ravnsø current 3D case and scientific validation **未完成**. Do not copy the published 1D performance figures into this project's result claims. Existing official 1D source files and local station observations still require a defensible grid, spatial inflow mapping, forcing/time alignment and comparison for the current GETM configuration.

Sources: [Aarhus University DCE Report 402 abstract](https://dce.au.dk/udgivelser/vr/nr-401-450/abstracts/nr-402-dynamiske-procesbaserede-modeller-som-forvaltningsvaerktoej-for-danske-soeer/) and [Report 402 PDF](https://dce2.au.dk/pub/SR402.pdf).
