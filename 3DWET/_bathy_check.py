import netCDF4, numpy as np
p = "C:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake Dianchi/bathymetry.nc"
d = netCDF4.Dataset(p)
print("variables:", list(d.variables))
for vn in d.variables:
    vl = vn.lower()
    if "dep" in vl or vl in ("h", "bathymetry", "elevation", "elev", "z"):
        a = np.array(d.variables[vn][:], dtype=float)
        print(f"[{vn}] shape={a.shape} min={np.nanmin(a):.4f} max={np.nanmax(a):.4f} "
              f"nan={int(np.isnan(a).sum())} <=0={int((a <= 0).sum())} <0.5={int((a < 0.5).sum())}")
        if a.ndim == 2:
            jc, ic = a.shape[0] // 2, a.shape[1] // 2
            print("  center cell:", a[jc, ic])
            flat = a.ravel()
            idx = int(np.nanargmin(flat))
            print("  shallowest value:", flat[idx])
        break
d.close()
