"""Generate rivers.nc and riverinfo.dat from real Inputs.xlsx data.

5 rivers (ERHE removed):
- YIHE (沂河): inflow from NORTH -> (21, 50)
- LUONAN (骆南中运河): inflow from SOUTH -> (28, 2)
- DAYUN (京杭大运河): bidirectional, WEST -> (7, 32)
- ZHANGSHAN (新沂河/嶂山闸): outflow EAST -> (42, 27)
- YANGHE (总六塘河/杨河滩): outflow SOUTHEAST -> (35, 28)

Sign convention: positive = inflow, negative = outflow
"""
import openpyxl
import netCDF4 as nc
import numpy as np
from datetime import datetime, timedelta
import os

CASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "case")
INPUTS_DIR = os.path.join(CASE_DIR, "inputs")
INPUT_PATH = os.path.join(INPUTS_DIR, "Inputs.xlsx")

# River positions (i, j) - 1-indexed, based on real geography
# Multi-grid rivers use a list of cells to split flow for extreme discharges.
# GETM reads riverinfo.dat and splits flow equally among same-named entries.
RIVER_POSITIONS = {
    "YIHE":      [(19, 50), (20, 50), (21, 50)],  # 沂河 - 3 cells, inflow from NORTH
    "LUONAN":    [(28, 2)],                        # 骆南中运河 - 1 cell, inflow from SOUTH
    "DAYUN":     [(2, 31), (2, 32), (3, 32)],      # 京杭大运河 - 3 cells, bidirectional WEST
    "ZHANGSHAN": [(41, 27), (42, 27), (43, 27)],   # 新沂河/嶂山闸 - 3 cells, outflow EAST
    "YANGHE":    [(35, 28)],                        # 总六塘河/杨河滩 - 1 cell, outflow SOUTHEAST
}

# River name mapping (Excel column -> river key)
# Sheet 3 columns: 运河站(京杭大运河), 皂盒闸(骆南中运河), 塂上站(沂河), 嶂山闸(新沂河), 杨河滩(总六塘河)
RIVER_COLUMNS = {
    "DAYUN":     1,  # 京杭大运河
    "LUONAN":    2,  # 骆南中运河
    "YIHE":      3,  # 沂河
    "ZHANGSHAN": 4,  # 新沂河
    "YANGHE":    5,  # 总六塘河
}

# WQ sheet mapping for inflow rivers (outflow rivers use lake water quality)
RIVER_WQ_SHEETS = {
    "DAYUN":  "入湖河道水质数据-京杭大运河",
    "LUONAN": "入湖河道水质数据-骆南中运河",
    "YIHE":   "入湖河道水质数据-沂河",
}


def read_river_discharge(wb, start_date, n_days):
    """Read river discharge data from Sheet 3."""
    ws = wb["主要入湖、出湖河道流量数据"]
    discharge = {name: np.zeros(n_days) for name in RIVER_POSITIONS}
    dates_found = []

    for row in ws.iter_rows(min_row=5, values_only=True):
        if row[0] is None:
            continue
        if isinstance(row[0], datetime):
            date = row[0]
            days = (date - start_date).days
            if 0 <= days < n_days:
                for name, col in RIVER_COLUMNS.items():
                    val = row[col]
                    if val is not None and val != "":
                        discharge[name][days] = float(val)
                dates_found.append(date)

    print(f"Discharge data: {len(dates_found)} days found")
    for name in RIVER_POSITIONS:
        print(f"  {name}: range [{discharge[name].min():.1f}, {discharge[name].max():.1f}], "
              f"mean={discharge[name].mean():.1f}")
    return discharge


def read_river_wq(wb, sheet_name, n_days, start_date):
    """Read river water quality data from specified sheet."""
    ws = wb[sheet_name]
    # Columns: 时间, 水温, pH, 溶解氧, IMN, 氨氮, 总磷, TN, ..., NH4, NO3, TDN
    # Find column indices by reading header
    header = [cell.value for cell in ws[1]]
    col_map = {}
    for i, h in enumerate(header):
        if h is None:
            continue
        h_str = str(h).replace("\n", "").replace("\r", "").strip()
        if "水温" in h_str or "水温" in str(h):
            col_map["temp"] = i
        elif "氨氮" in h_str:
            col_map["nh4"] = i
        elif "总磷" in h_str:
            col_map["tp"] = i
        elif "NO3" in h_str:
            col_map["no3"] = i
        elif "PO4" in h_str:
            col_map["po4"] = i
        elif "TN" in h_str or "总氮" in h_str:
            col_map["tn"] = i

    print(f"  {sheet_name} columns: {col_map}")

    wq = {
        "temp": np.full(n_days, 10.0),  # default temp
        "nh4": np.full(n_days, 0.1),
        "no3": np.full(n_days, 1.0),
        "po4": np.full(n_days, 0.02),
    }

    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] is None:
            continue
        if isinstance(row[0], datetime):
            date = row[0]
            days = (date - start_date).days
            if 0 <= days < n_days:
                if "temp" in col_map and row[col_map["temp"]] is not None:
                    wq["temp"][days] = float(row[col_map["temp"]])
                if "nh4" in col_map and row[col_map["nh4"]] is not None:
                    wq["nh4"][days] = float(row[col_map["nh4"]])
                if "no3" in col_map and row[col_map["no3"]] is not None:
                    wq["no3"][days] = float(row[col_map["no3"]])
                if "po4" in col_map and row[col_map["po4"]] is not None:
                    wq["po4"][days] = float(row[col_map["po4"]])

    return wq


def read_lake_wq(wb, n_days, start_date):
    """Read lake water quality for outflow rivers (use lake values)."""
    ws = wb["湖内三场点位水质数据"]
    wq = {
        "temp": np.full(n_days, 5.89),
        "nh4": np.full(n_days, 0.02),
        "no3": np.full(n_days, 2.48),
        "po4": np.full(n_days, 0.02),
    }

    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] is None:
            continue
        if isinstance(row[0], datetime):
            date = row[0]
            days = (date - start_date).days
            if 0 <= days < n_days:
                if row[1] is not None:  # 水温
                    wq["temp"][days] = float(row[1])
                if row[5] is not None:  # 氨氮
                    wq["nh4"][days] = float(row[5])
                if row[6] is not None:  # 总磷
                    wq["po4"][days] = float(row[6]) * 0.5  # PO4 ~ 50% of TP
                if row[7] is not None:  # 总氮
                    wq["no3"][days] = float(row[7]) * 0.9  # NO3 ~ 90% of TN

    return wq


def main():
    print("=" * 70)
    print("Generating rivers.nc and riverinfo.dat")
    print("=" * 70)

    start_date = datetime(2020, 1, 1)
    n_days = 1096  # 3 years: 2020 (leap, 366d) + 2021 (365d) + 2022 (365d)

    wb = openpyxl.load_workbook(INPUT_PATH, data_only=True)

    # Read discharge data
    print("\nReading river discharge data...")
    discharge = read_river_discharge(wb, start_date, n_days)

    # Read WQ for inflow rivers
    river_wq = {}
    for name, sheet_name in RIVER_WQ_SHEETS.items():
        print(f"\nReading WQ for {name} ({sheet_name})...")
        river_wq[name] = read_river_wq(wb, sheet_name, n_days, start_date)

    # For outflow rivers, use lake WQ
    print("\nReading lake WQ for outflow rivers...")
    lake_wq = read_lake_wq(wb, n_days, start_date)
    for name in ["ZHANGSHAN", "YANGHE"]:
        river_wq[name] = lake_wq
        print(f"  {name}: using lake WQ (temp={lake_wq['temp'][0]:.2f}, nh4={lake_wq['nh4'][0]:.3f})")

    # Write riverinfo.dat (multi-grid: same river name on consecutive lines)
    riverinfo_path = os.path.join(CASE_DIR, "riverinfo.dat")
    print(f"\nWriting {riverinfo_path}...")
    total_cells = sum(len(cells) for cells in RIVER_POSITIONS.values())
    with open(riverinfo_path, "w") as f:
        f.write(f"{total_cells}\n")
        for name, cells in RIVER_POSITIONS.items():
            for (i, j) in cells:
                f.write(f"{i} {j} {name} -1 -1\n")
    print("  Done!")
    for name, cells in RIVER_POSITIONS.items():
        cells_str = ", ".join(f"({i},{j})" for (i, j) in cells)
        print(f"  {name}: {cells_str} ({len(cells)} cell{'s' if len(cells)>1 else ''})")

    # Write rivers.nc
    rivers_path = os.path.join(CASE_DIR, "rivers.nc")
    print(f"\nWriting {rivers_path}...")

    ds = nc.Dataset(rivers_path, "w", format="NETCDF4")

    # Dimensions
    ds.createDimension("time", None)  # unlimited

    # Time variable
    time_var = ds.createVariable("time", "f8", ("time",))
    time_var.units = "seconds since 2020-01-01 00:00:00"
    time_var.long_name = "time"
    time_vals = np.arange(n_days) * 86400.0
    time_var[:] = time_vals

    # River variables
    for name in RIVER_POSITIONS:
        # Discharge
        var = ds.createVariable(name, "f8", ("time",))
        var.units = "m3/s"
        var.long_name = f"{name} river discharge"
        var[:] = discharge[name]

        # Water quality variables
        wq = river_wq[name]
        for wq_name, units, long_name in [
            ("temp", "degC", f"{name} temperature"),
            ("nh4", "g/m3", f"{name} ammonium"),
            ("no3", "g/m3", f"{name} nitrate"),
            ("po4", "g/m3", f"{name} phosphate"),
        ]:
            var = ds.createVariable(f"{name}_{wq_name}", "f8", ("time",))
            var.units = units
            var.long_name = long_name
            var[:] = wq[wq_name]

    ds.title = "Luomahu Lake river data (real)"
    ds.source = "Generated from Inputs.xlsx"
    ds.history = f"Created {np.datetime64('now')} with gen_rivers.py"
    ds.close()
    print("  Done!")

    # Print summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    for name in RIVER_POSITIONS:
        q = discharge[name]
        wq = river_wq[name]
        print(f"{name:12s}: Q=[{q.min():.1f}, {q.max():.1f}] CMS, "
              f"temp={wq['temp'][0]:.2f}, nh4={wq['nh4'][0]:.3f}, "
              f"no3={wq['no3'][0]:.3f}, po4={wq['po4'][0]:.4f}")


if __name__ == "__main__":
    main()
