"""Check meteo and river data around day 10."""
import netCDF4 as nc
import numpy as np

# Meteo
ds = nc.Dataset('meteo.nc')
t = ds.variables['time'][:] / 86400.0
print("Meteo around day 10:")
print("  day  | wind(m/s) | slp(Pa) | t2(C) | precip(m/s) | evap(m/s)")
for d in range(7, 14):
    idx = int(d)
    if idx < len(t):
        u = ds.variables['u10'][idx, 0, 0]
        v = ds.variables['v10'][idx, 0, 0]
        slp = ds.variables['slp'][idx, 0, 0]
        t2 = ds.variables['t2'][idx, 0, 0]
        pr = ds.variables['precip'][idx, 0, 0]
        ev = ds.variables['evap'][idx, 0, 0]
        wind = np.sqrt(u**2 + v**2)
        print(f"  {t[idx]:5.1f} | {wind:8.2f}   | {slp:7.0f} | {t2:5.1f} | {pr:.2e}    | {ev:.2e}")
ds.close()

# Rivers
print("\nRiver flow around day 10:")
ds = nc.Dataset('rivers.nc')
t = ds.variables['time'][:] / 86400.0
for name in ['ZYH', 'ZH', 'YH', 'XYH', 'YHT']:
    q = ds.variables[name][:]
    print(f"  {name}: day 8={q[8]:.2f}, day 9={q[9]:.2f}, day 10={q[10]:.2f}, day 11={q[11]:.2f}")
ds.close()

# Check max wind in first 15 days
ds = nc.Dataset('meteo.nc')
u10 = ds.variables['u10'][:15, 0, 0]
v10 = ds.variables['v10'][:15, 0, 0]
wind = np.sqrt(u10**2 + v10**2)
print(f"\nMax wind in first 15 days: {wind.max():.2f} m/s at day {np.argmax(wind)}")
print(f"Wind day 9: {wind[9]:.2f}, day 10: {wind[10]:.2f}")
ds.close()
