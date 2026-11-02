import netCDF4 as nc
import numpy as np

ds2d = nc.Dataset('THEORETICAL_LAKE.2d.nc')
ds3d = nc.Dataset('THEORETICAL_LAKE.3d.nc')

t2 = np.array(ds2d.variables['time'][:])
t3 = np.array(ds3d.variables['time'][:])

print('2d time: len=' + str(len(t2)))
print('  first 5: ' + str(t2[:5]))
print('  last 5:  ' + str(t2[-5:]))
print('3d time: len=' + str(len(t3)))
print('  first 5: ' + str(t3[:5]))
print('  last 5:  ' + str(t3[-5:]))
print()

# filter_valid logic from visualize_heart_lake.py
def filter_valid(time_arr):
    valid = np.asarray(time_arr) > 0
    n = len(time_arr)
    last = -np.inf
    for i in range(n):
        if valid[i] and time_arr[i] > last:
            last = time_arr[i]
        else:
            valid[i:] = False
            break
    return valid

v2 = filter_valid(t2)
v3 = filter_valid(t3)
print('2d valid after filter_valid: ' + str(np.sum(v2)) + ' of ' + str(len(t2)))
print('3d valid after filter_valid: ' + str(np.sum(v3)) + ' of ' + str(len(t3)))
print()

# Check if monotonic
diff2 = np.diff(t2)
print('2d time monotonic increasing: ' + str(np.all(diff2 > 0)))
print('2d time diffs: min=' + str(np.min(diff2)) + ' max=' + str(np.max(diff2)))
print('2d non-monotonic points: ' + str(np.sum(diff2 <= 0)))

diff3 = np.diff(t3)
print('3d time monotonic increasing: ' + str(np.all(diff3 > 0)))
print('3d time diffs: min=' + str(np.min(diff3)) + ' max=' + str(np.max(diff3)))
print('3d non-monotonic points: ' + str(np.sum(diff3 <= 0)))
print()

# Check where non-monotonic starts
for i in range(len(diff2)):
    if diff2[i] <= 0:
        print('2d first non-monotonic at idx ' + str(i) + ': t[' + str(i) + ']=' + str(t2[i]) + ' t[' + str(i+1) + ']=' + str(t2[i+1]))
        break

for i in range(len(diff3)):
    if diff3[i] <= 0:
        print('3d first non-monotonic at idx ' + str(i) + ': t[' + str(i) + ']=' + str(t3[i]) + ' t[' + str(i+1) + ']=' + str(t3[i+1]))
        break

# Check elev
elev = np.array(ds2d.variables['elev'][:])
print()
print('elev shape: ' + str(elev.shape))
print('elev[0] finite: ' + str(np.sum(np.isfinite(elev[0]))) + ' / ' + str(elev[0].size))
if len(t2) > 100:
    print('elev[100] finite: ' + str(np.sum(np.isfinite(elev[100]))) + ' / ' + str(elev[100].size))

# Check temp
temp = np.array(ds3d.variables['temp'][:])
print('temp shape: ' + str(temp.shape))
print('temp[0] finite: ' + str(np.sum(np.isfinite(temp[0]))) + ' / ' + str(temp[0].size))
if len(t3) > 100:
    print('temp[100] finite: ' + str(np.sum(np.isfinite(temp[100]))) + ' / ' + str(temp[100].size))

# Check bathymetry in 2d
bathymetry = np.array(ds2d.variables['bathymetry'][:])
print()
print('bathymetry shape: ' + str(bathymetry.shape))
print('bathymetry wet cells: ' + str(np.sum(bathymetry > 0)))
print('bathymetry range: ' + str(np.min(bathymetry[bathymetry > 0])) + ' to ' + str(np.max(bathymetry)))

# List some FABM variables
fabm_vars = [v for v in ds3d.variables.keys() if 'sDW' in v or 'sD' in v][:20]
print()
print('Sample FABM vars: ' + str(fabm_vars))

ds2d.close()
ds3d.close()
