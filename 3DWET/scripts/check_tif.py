"""Check TIF file availability and content."""
import numpy as np
import os

TIF_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "case", "inputs", "骆马湖-底部高程处理-Zhongzhao_Duan.tif"
)

print(f"TIF file: {os.path.exists(TIF_PATH)}")
print(f"Size: {os.path.getsize(TIF_PATH) / 1024 / 1024:.1f} MB")

import rasterio
with rasterio.open(TIF_PATH) as ds:
    print(f"Size: {ds.width} x {ds.height}")
    print(f"Bands: {ds.count}")
    print(f"CRS: {ds.crs}")
    print(f"Transform: {ds.transform}")
    print(f"Bounds: {ds.bounds}")
    arr = ds.read(1)
    nodata = ds.nodata
    print(f"NoData: {nodata}")
    print(f"Dtype: {arr.dtype}")
    if nodata is not None:
        valid = arr[arr != nodata]
    else:
        valid = arr
    print(f"Valid pixels: {len(valid)} of {arr.size}")
    print(f"Min: {np.nanmin(valid):.2f}, Max: {np.nanmax(valid):.2f}")
    print(f"Mean: {np.nanmean(valid):.2f}")
    # Print coordinate of first pixel
    x0 = ds.transform[0]
    y0 = ds.transform[3]
    dx = ds.transform[1]
    dy = ds.transform[5]
    print(f"Origin: ({x0:.1f}, {y0:.1f})")
    print(f"Pixel size: ({dx:.1f}, {dy:.1f})")
    print(f"X range: {x0:.1f} to {x0 + dx * ds.width:.1f}")
    print(f"Y range: {y0:.1f} to {y0 + dy * ds.height:.1f}")

