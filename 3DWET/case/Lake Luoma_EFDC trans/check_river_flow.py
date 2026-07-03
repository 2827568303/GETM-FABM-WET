"""Check ZYH river flow data for anomalies."""
import netCDF4 as nc
import numpy as np

ds = nc.Dataset('rivers.nc')
t = ds.variables['time'][:] / 86400.0
print("ZYH flow (first 30 days):")
zyh = ds.variables['ZYH'][:]
for i in range(min(30, len(zyh))):
    marker = " <<< ANOMALY" if abs(zyh[i]) > 100 else ""
    print(f"  day {t[i]:5.1f}: Q = {zyh[i]:10.2f} m3/s{marker}")

print(f"\nZYH stats (first 30 days): min={zyh[:30].min():.2f}, max={zyh[:30].max():.2f}, mean={zyh[:30].mean():.2f}")
print(f"ZYH stats (all): min={zyh.min():.2f}, max={zyh.max():.2f}, mean={zyh.mean():.2f}")
print(f"Days with |Q| > 100: {np.sum(np.abs(zyh) > 100)}")

# Check all rivers for anomalies
print("\nAll rivers - max absolute flow:")
for name in ['ZYH', 'ZH', 'YH', 'XYH', 'YHT']:
    q = ds.variables[name][:]
    big = np.sum(np.abs(q) > 100)
    print(f"  {name}: max|Q|={np.max(np.abs(q)):.2f}, days|Q|>100={big}")

ds.close()

# Check original EFDC qser.inp for comparison
print("\nChecking original EFDC qser.inp for ZYH...")
import os
EFDC_DIR = r"D:\00_数据\00_骆马湖-模型\LMH_Balanced_test_WL0 = 21.82"
qser_path = os.path.join(EFDC_DIR, 'qser.inp')
if os.path.exists(qser_path):
    with open(qser_path, 'r', encoding='latin-1') as f:
        lines = f.readlines()
    # Find ZYH series
    for k, ln in enumerate(lines):
        if 'ZYH' in ln and '!' in ln:
            print(f"  Found ZYH header at line {k}: {ln.strip()}")
            # print next 15 data lines
            count = 0
            for j in range(k+1, min(k+20, len(lines))):
                parts = lines[j].split()
                if len(parts) >= 2:
                    try:
                        t_val = float(parts[0])
                        q_val = float(parts[1])
                        marker = " <<< ANOMALY" if abs(q_val) > 100 else ""
                        print(f"    t={t_val:8.1f}, Q={q_val:10.2f}{marker}")
                        count += 1
                        if count >= 15:
                            break
                    except ValueError:
                        pass
            break
