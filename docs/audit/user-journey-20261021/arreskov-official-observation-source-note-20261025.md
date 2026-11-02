# Arreskov observation source note (2026-10-25)

## Official portal search and export

The official Danish Environmental Portal's Kemidata API returned station **45000018** (`Arreskov Sø /004`) for the 1990-01-01 to 2004-12-31 interval. It returned 294 `Datamart Feltmåling Sø` examinations and 4,627 measurements, dated 1990-01-10 through 2004-11-22. The search by the whole-lake label (`ARRESKOV SØ - HELE SØEN`, station 45000060) did not return matching field measurements for that interval; this export is specifically from station `/004`. Whether `/004` is the sampling location represented by the WET model column is **不确定**.

The filtered raw CSV is [archived here](arreskov-station-45000018-field-measurements-1990-2004-20261025.csv), SHA-256 `EDDF2EBA3EAA526B60C107254D10E8206A7E38C9117F734E4803E26543982546`, size 1,494,215 bytes. It contains 4,627 rows, including 1,565 `Temperatur` observations across 294 measurement dates. Temperature sample counts per date range from 1 to 7 (median 5); depths range from 0.2 to 3.5 m; values range from 0.4 to 25.0 °C. The same file also contains oxygen, oxygen saturation, pH, conductivity, and salinity. It uses Danish decimal commas. This confirms **实测 observation data acquisition**, not a complete profile on every date and not model-data pairing.

## Use and remaining limits

- The upstream WET archive and 1990–2004 forcing support files are documented in the [existing source recovery audit](../../../build/real-use-validation-20261023/arreskov-v010-recovery/RECOVERY_AUDIT.md). The missing case-specific `fabm.yaml`, matched model build, calibrated ensemble, and initial/restart state still prevent author-case execution.
- Date overlap alone does not establish that station `/004` represents the model's one-dimensional column; station/column mapping, timestamp convention, variable mapping, units, and quality-marker semantics remain to be resolved before pairing.
- The official [Feltmåling Sø catalogue entry](https://arealdata.miljoeportal.dk/datasets/urn:dmp:ds:feltmaaling-soe) describes fields including time, depth, parameter, and result, but the applicable licence could not be confirmed from the retrieved catalogue page. The local copy is retained as research audit evidence; redistribution rights are **不确定**.
- Arreskov model science validation remains **未完成**. Existing proxy/model sensitivity results remain **代理** and are not upgraded by this observation export.

Sources: [official Kemidata search](https://kemidata.miljoeportal.dk/?et=Datamart+Feltm%C3%A5ling+S%C3%B8&place=45000018), [official Feltmåling Sø dataset catalogue](https://arealdata.miljoeportal.dk/datasets/urn:dmp:ds:feltmaaling-soe), and [Danmarks Miljøportal dataset guide](https://datavejviser.dk/katalog/danmarks-miljoportal/2ba457fb-a819-4e9c-8d4a-0d2de28c5197).

**Licence update (2026-10-25):** the official [Datavejviser JSON-LD record](https://datavejviser.dk/katalog/danmarks-miljoportal/2ba457fb-a819-4e9c-8d4a-0d2de28c5197.jsonld) identifies the `Feltmåling Sø` dataset and its CSV distribution as CC0, with public access. This resolves the earlier licence uncertainty for this category. Station-to-model mapping and scientific pairing remain **不确定 / 未完成**.
