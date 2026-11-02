# Bryrup observation source lead (2026-10-25)

## Finding

The official Danish Environmental Portal's Kemidata page was opened for the Bryrup Langsø monitoring station **21000361** (`BRYRUP LANGSØ, BRY 1`), using the `Vandkemi - Sø` examination type. The date filter **1996-01-01 through 2006-12-31** returned **221 studies** and **4,527 measurements**, with the first study on **1996-01-25** and the latest on **2006-12-12**.

This is a source-discovery result only. The measurement values have not yet been exported or matched to model variables, depth conventions, and units. It does not constitute model execution or scientific validation. Keep Bryrup science status **未完成**.

## Download/access limitation

The visible `Download alle` action and the station-row download action were invoked in the public portal, but no exported file was captured in the local Downloads folder. The dataset catalogue's public CSV endpoint also returned HTTP 401 in the earlier access attempt. Do not claim that raw values were acquired from those attempts.

## Sources

- Official station data page: <https://kemidata.miljoeportal.dk/?et=Datamart+Vandkemi+S%C3%B8&place=21000361>
- Official catalogue entry for `Vandkemi Sø`, described as all chemistry results from VanDa and licensed CC0 1.0: <https://arealdata.miljoeportal.dk/datasets/urn:dmp:ds:vandkemi-soe>
- Official Bryrup Langsø monitoring guide: <https://sgavmst.dk/natur-og-jagt/naturen-i-danmark/novana-overvaagning-af-natur-og-vandmiljoe/guider-til-danske-vandomraader/soe/bryrup-langsoe>
- WET 1.0 paper: Bryrup calibration 1996–2004 and validation 2004–2006; variables include temperature, dissolved oxygen, nutrients, TN/TP, and chlorophyll-a: <https://gmd.copernicus.org/articles/15/3861/2022/gmd-15-3861-2022.html>

## Status

- Official target station and date coverage: **实测** (directly observed on the official data portal).
- Model/data variable matching and performance validation: **未完成**.
- Any previous proxy runs remain **代理** and are not upgraded by this source lead.

## Addendum — raw field measurements exported (2026-10-25)

The official Kemidata API download was subsequently captured for station **21000361** (`BRYRUP LANGSØ, BRY 1`), examination type `Datamart Feltmåling Sø`, and the date filter 1996-01-01 through 2006-12-31. The raw semicolon-delimited CSV is [archived here](bryrup-station-21000361-field-measurements-1996-2006-20261025.csv), SHA-256 `D5014A821E0D5F9B6BB0FEC33A1F6B1B7D0303997E5CD460A39118EEA3E81841`, size 1,623,521 bytes. It contains 5,005 measurement rows from that station; 1,676 rows are `Temperatur` across 226 measurement dates. Per date, temperature rows contain 1–16 depths (median 8), spanning 0–10 m; values span 0.8–24.5 °C. The file also contains oxygen, oxygen saturation, pH, conductivity, and salinity measurements. Temperature rows include depth, result, unit (`grader C`), date, and quality marker. The source records use Danish decimal commas and include profile depths; timezone and timestamp interpretation still need to be reconciled with model output before pairing.

This supersedes the earlier note that no exported file had been captured. The earlier 1996–2006 `Vandkemi Sø` search summary (221 examinations / 4,527 measurements) remains a separate catalogue/search observation; this addendum downloaded the `Feltmåling Sø` category, not the chemistry category. The raw field-measurement file is evidence of **实测观测数据 acquisition**, not model-data pairing or scientific validation. Bryrup science validation remains **未完成**; existing model runs retain their **代理** status.

The official [Feltmåling Sø catalogue entry](https://arealdata.miljoeportal.dk/datasets/urn:dmp:ds:feltmaaling-soe) confirms the dataset contains place, time, sampling location, depth, parameter, and result; the catalogue page's licence field was not available in the retrieved page, so the applicable licence is **uncertain** and redistribution rights have not been asserted. The separate [Vandkemi Sø catalogue entry](https://arealdata.miljoeportal.dk/datasets/urn:dmp:ds:vandkemi-soe) is explicitly CC0 1.0 and must not be conflated with the downloaded `Feltmåling Sø` category. Source page: [official Kemidata search](https://kemidata.miljoeportal.dk/?et=Datamart+Feltm%C3%A5ling+S%C3%B8&place=21000361).

**Licence verification update (2026-10-25):** the official [Datavejviser JSON-LD record](https://datavejviser.dk/katalog/danmarks-miljoportal/2ba457fb-a819-4e9c-8d4a-0d2de28c5197.jsonld) identifies the `Feltmåling Sø` dataset and its CSV distribution as CC0, with public access. This resolves the earlier licence uncertainty for this category. Station/model matching and science validation remain **未完成**.

## Addendum — 1990 smoke-run coverage check (2026-10-26)

The archived `bryrup-wet1-stim-one-day/gotm.yaml` and successful smoke log show a one-day model run from **1990-01-01 12:00:00 to 1990-01-02 12:00:00**. The locally archived station 21000361 `Feltmåling Sø` CSV currently covers 1996–2006, so it contains no timestamps overlapping this smoke run. However, the official Bryrup monitoring guide says the lake was selected for monitoring in 1989 and that nutrient/oxygen samples were taken annually from 1989 through 2015 ([official guide](https://sgavmst.dk/natur-og-jagt/naturen-i-danmark/novana-overvaagning-af-natur-og-vandmiljoe/guider-til-danske-vandomraader/soe/bryrup-langsoe)). Therefore the absence of 1990 in this local CSV does **not** establish that 1990 measurements do not exist. Availability and exact profile/time matching for 1990 remain **uncertain**; no 1990 pairing was performed. The one-day output remains **代理**, and Bryrup scientific validation remains **未完成**.

The official catalogue's [Feltmåling Sø metadata](https://datavejviser.dk/katalog/danmarks-miljoportal/2ba457fb-a819-4e9c-8d4a-0d2de28c5197) lists an overall dataset coverage beginning **1939-07-31** and a public CC0 licence. This is dataset-wide temporal coverage, not a station-specific inventory: it does not establish that station 21000361 has a 1990 record or a temperature profile suitable for pairing. That station-level check remains **uncertain**.

An official read-only WFS query for station 21000361 returned `FoersteUndersoegelsesDato = 1978-04-12 12:00:00 +01:00` and `SenesteUndersoegelsesDato = 2025-12-09 12:00:00 +01:00` ([official station WFS layer](https://vanda-geo.miljoeportal.dk/geoserver/wfs?SERVICE=WFS&TYPENAMES=vanda%3Afeltmaaling-soe)). This station-level range establishes that the archive spans 1990, but it does not establish a temperature record on 1990-01-01/02. Parameter-level and timestamp-level 1990 availability remains **uncertain** until the official station/date-filtered records are retrieved.

## Resolution — 1990 station measurements downloaded (2026-10-26)

The official Kemidata API (`POST https://kemidata.miljoeportal.dk/api/download`) was queried with station `21000361`, media `Sø`, examination type `Datamart Feltmåling Sø`, and period `1990-01-01` through `1990-12-31`. Its official catalogue record marks the dataset public and CC0. The raw semicolon-delimited CSV is archived as [bryrup-station-21000361-field-measurements-1990-20261026.csv](bryrup-station-21000361-field-measurements-1990-20261026.csv), 182,208 bytes, SHA-256 `F18CE9C915B20470DAE7EF92CC5E9652D9A69D81E7585AA0A50310B061C8F062`. The export contains **561 measurement rows**, including **187 temperature measurements** over **19 profile dates** (9–13 depths per date, 0.2–8 m); temperature-profile dates run from **1990-01-23** through **1990-12-04**. The output therefore has no same-date observation for the existing Jan 1–2 smoke run. The observed profiles are **实测**; the one-day model output remains **代理**; model-observation comparison and Bryrup scientific validation remain **未完成**.

## 2026-10-26 Sol：论文验证期与归档配置核对

- **实测（官方文献/归档配置核对）**：[WET 1.0 论文](https://gmd.copernicus.org/articles/15/3861/2022/gmd-15-3861-2022.html)说明 Bryrup 配置采用 6 年 spin-up、1996–2004 校准、2004–2006 验证；比较温度、DO、营养盐、TN/TP 和 chl-a，并用 ParSAC 校准。模型资料来自 NOVANA，温度/DO为垂向多点，化学营养盐和 chl-a 的采样深度规则不同。
- 本地官方 WET v0.1.0 发布包中的 `testcases/lake_bryrup_denmark/gotm.yaml` 只覆盖 **1990-01-01 至 1995-12-31**，可作为 spin-up 配置来源；它不是论文完整的 1996–2006 校准/验证输入，也不能单独产生验证分数。已下载的站点 21000361 现场测量 CSV 覆盖 1996–2006，但温度/DO观测并不自动等同于论文使用的完整 NOVANA 多变量对照数据。
- **状态**：Bryrup 科学验证仍**未完成**；当前模型 smoke 输出没有与上述校准/验证窗口配对，既有结果保持**代理**。不得以 6 年 spin-up 或站点文件覆盖期声称论文验证完成。
