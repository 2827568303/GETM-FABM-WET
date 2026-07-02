"""Generate meteo.nc from real Inputs.xlsx data (GETM format).

GETM expects specific variable names. The Fortran netCDF 4.5.4 library
REVERSES dimension order (C order -> Fortran column-major order).
GETM's ncdf_meteo.F90 uses start/edges assuming (lon, lat, time) Fortran order.
With reversal, the C variable must have dims (time, lat, lon) so that
after reversal it becomes (lon, lat, time) in Fortran order.

- Dimensions: lon, lat, time
- Coordinate variables: lon(lon), lat(lat), time(time)
- Data variables: u10/v10/slp/t2/rh/tcc/precip with C dims (time, lat, lon)
- After Fortran reversal: (lon, lat, time) - matches GETM's start/edges

Reads:
- Sheet 1 (气象数据): pressure, temp, humidity, precip, radiation, cloud
- Sheet 2 (风速风向): wind speed and direction
"""
import openpyxl
import netCDF4 as nc
import numpy as np
from datetime import datetime
import os

CASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "case")
INPUTS_DIR = os.path.join(CASE_DIR, "inputs")
INPUT_PATH = os.path.join(INPUTS_DIR, "Inputs.xlsx")


def read_meteo_data(wb, start_date, n_days):
    """Read meteorological data from Sheets 1 and 2.

    Excel columns (Sheet 1 - 气象数据):
      col5: 降水量 (m/d) - convert to m/s by /86400
      col6: 蒸发量 (m/d) - convert to m/s by /86400
    Sign convention for GETM:
      precip > 0 (water gain), evap > 0 (water loss)
      fwf = evap + precip (sealevel.F90); GETM uses evap as negative flux,
      so we store evap as -|evap| to make fwf = precip - |evap|.
    """
    ws1 = wb["气象数据"]
    meteo = {
        "t2": np.full(n_days, 5.0),           # 2m air temperature (degC)
        "slp": np.full(n_days, 101300.0),     # sea level pressure (Pa)
        "rh": np.full(n_days, 70.0),          # relative humidity (%)
        "tcc": np.full(n_days, 0.5),          # total cloud cover (0-1)
        "precip": np.zeros(n_days),           # precipitation (m/s)
        "evap": np.zeros(n_days),             # evaporation (m/s, negative = water loss)
    }

    for row in ws1.iter_rows(min_row=2, values_only=True):
        if row[1] is None:
            continue
        if isinstance(row[1], datetime):
            date = row[1]
            days = (date - start_date).days
            if 0 <= days < n_days:
                if row[2] is not None:  # 大气压 (hPa)
                    meteo["slp"][days] = float(row[2]) * 100.0  # hPa -> Pa
                if row[3] is not None:  # 气温 (degC)
                    meteo["t2"][days] = float(row[3])
                if row[4] is not None:  # 相对湿度 (%)
                    meteo["rh"][days] = float(row[4])
                if row[5] is not None:  # 降水量 (m/d)
                    precip_md = float(row[5])
                    meteo["precip"][days] = precip_md / 86400.0
                if row[6] is not None:  # 蒸发量 (m/d)
                    evap_md = float(row[6])
                    # GETM fluxes.F90: evap = rho_air/rho_0*cd*w*(qa-qs)
                    # When qa < qs (dry air), evap is negative => water loss.
                    # fwf = evap + precip; positive fwf raises water level.
                    # So evap from file should be negative for water loss.
                    meteo["evap"][days] = -abs(evap_md) / 86400.0
                if row[8] is not None:  # 云量
                    cloud_val = float(row[8])
                    # If cloud > 1, assume 0-10 scale and convert to 0-1
                    if cloud_val > 1.0:
                        cloud_val = cloud_val / 10.0
                    meteo["tcc"][days] = cloud_val

    # Sheet 2: 风速风向
    ws2 = wb["风速风向"]
    u10 = np.zeros(n_days)
    v10 = np.zeros(n_days)

    for row in ws2.iter_rows(min_row=2, values_only=True):
        if row[0] is None:
            continue
        if isinstance(row[0], datetime):
            date = row[0]
            days = (date - start_date).days
            if 0 <= days < n_days:
                speed = float(row[1]) if row[1] is not None else 0.0
                direction = float(row[2]) if row[2] is not None else 0.0
                # Filter out bad values (e.g., 999999 placeholder)
                if speed > 100.0:
                    speed = 0.0
                # Wind direction: meteorological convention (degrees from north)
                # u = -speed * sin(dir)  (east-west)
                # v = -speed * cos(dir)  (north-south)
                rad = np.deg2rad(direction)
                u10[days] = -speed * np.sin(rad)
                v10[days] = -speed * np.cos(rad)

    meteo["u10"] = u10
    meteo["v10"] = v10

    return meteo


def main():
    print("=" * 70)
    print("Generating meteo.nc from real data (GETM format)")
    print("=" * 70)

    start_date = datetime(2020, 1, 1)
    n_days = 1096  # 3 years: 2020 (leap, 366d) + 2021 (365d) + 2022 (365d)

    wb = openpyxl.load_workbook(INPUT_PATH, data_only=True)
    meteo = read_meteo_data(wb, start_date, n_days)

    print(f"\nData summary ({n_days} days):")
    for key in ["t2", "slp", "rh", "tcc", "precip", "evap", "u10", "v10"]:
        val = meteo[key]
        print(f"  {key}: min={val.min():.6f}, max={val.max():.6f}, mean={val.mean():.6f}")
    # Water balance check (mm/day)
    precip_mmd = meteo["precip"] * 86400.0 * 1000.0
    evap_mmd = -meteo["evap"] * 86400.0 * 1000.0  # convert back to positive mm/day
    fwf_mmd = (meteo["precip"] + meteo["evap"]) * 86400.0 * 1000.0
    print(f"\n  Water balance (mm/day):")
    print(f"    precip: mean={precip_mmd.mean():.3f}, sum={precip_mmd.sum():.1f} mm")
    print(f"    evap:   mean={evap_mmd.mean():.3f}, sum={evap_mmd.sum():.1f} mm")
    print(f"    fwf:    mean={fwf_mmd.mean():.3f}, total={fwf_mmd.sum()/1000.0:.3f} m")

    # Read grid info from bathymetry.nc
    bathy_ds = nc.Dataset(os.path.join(CASE_DIR, "bathymetry.nc"))
    nx = len(bathy_ds.dimensions["x"])
    ny = len(bathy_ds.dimensions["y"])
    lonc = bathy_ds.variables["lonc"][:]  # (ny, nx) - geographic lon
    latc = bathy_ds.variables["latc"][:]  # (ny, nx) - geographic lat
    bathy_ds.close()
    print(f"\nGrid: {nx} x {ny}")

    # Extract 1D lon/lat from 2D arrays (take first row/column)
    lon_1d = lonc[0, :]  # (nx,) - lon varies along x
    lat_1d = latc[:, 0]  # (ny,) - lat varies along y

    # Write meteo.nc in GETM format
    meteo_path = os.path.join(CASE_DIR, "meteo.nc")
    print(f"\nWriting {meteo_path}...")

    # Use NETCDF4 format
    ds = nc.Dataset(meteo_path, "w", format="NETCDF4")

    # Dimensions: lon, lat, time (dimension order does not matter, only variable dim order matters)
    ds.createDimension("lon", nx)
    ds.createDimension("lat", ny)
    ds.createDimension("time", n_days)

    # Coordinate variables
    lon_var = ds.createVariable("lon", "f8", ("lon",))
    lon_var.units = "degrees_east"
    lon_var.long_name = "longitude"
    lon_var[:] = lon_1d

    lat_var = ds.createVariable("lat", "f8", ("lat",))
    lat_var.units = "degrees_north"
    lat_var.long_name = "latitude"
    lat_var[:] = lat_1d

    time_var = ds.createVariable("time", "f8", ("time",))
    time_var.units = "seconds since 2020-01-01 00:00:00"
    time_var.long_name = "time"
    time_var[:] = np.arange(n_days) * 86400.0

    # Meteorological variables: C dims (time, lat, lon)
    # Fortran netCDF 4.5.4 reverses dims, so Fortran sees (lon, lat, time)
    # GETM reads with start=(1,1,indx), edges=(iextr,jextr,1) - matches Fortran (lon, lat, time)
    # Use float32 for standard meteorology; use float64 for tiny freshwater flux
    # values (precip ~1e-8 m/s) to avoid precision loss.
    var_specs_f32 = [
        ("u10", "m s-1", "10m wind u-component"),
        ("v10", "m s-1", "10m wind v-component"),
        ("slp", "Pa", "sea level pressure"),
        ("t2", "degC", "2m air temperature"),
        ("rh", "1", "relative humidity"),
        ("tcc", "1", "total cloud cover"),
    ]
    var_specs_f64 = [
        ("precip", "m s-1", "precipitation rate"),
        ("evap", "m s-1", "evaporation rate (negative = water loss)"),
    ]

    for var_name, units, long_name in var_specs_f32:
        var = ds.createVariable(var_name, "f4", ("time", "lat", "lon"),
                                fill_value=np.float32(-9999.0))
        var.units = units
        var.long_name = long_name
        data_1d = meteo[var_name]
        data_3d = np.broadcast_to(data_1d[:, np.newaxis, np.newaxis],
                                   (n_days, ny, nx)).astype(np.float32).copy()
        var[:] = data_3d

    for var_name, units, long_name in var_specs_f64:
        var = ds.createVariable(var_name, "f8", ("time", "lat", "lon"),
                                fill_value=np.float64(-9999.0))
        var.units = units
        var.long_name = long_name
        data_1d = meteo[var_name]
        data_3d = np.broadcast_to(data_1d[:, np.newaxis, np.newaxis],
                                   (n_days, ny, nx)).astype(np.float64).copy()
        var[:] = data_3d

    ds.title = "Luomahu Lake meteorological data (GETM format)"
    ds.source = "Generated from Inputs.xlsx"
    ds.history = f"Created {np.datetime64('now')} with gen_meteo.py"
    ds.Conventions = "CF-1.0"
    ds.close()
    print("  Done!")


if __name__ == "__main__":
    main()
