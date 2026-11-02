"""Check geometry/volume consistency of completed outputs (not calibration)."""
import argparse
import json
from pathlib import Path
import netCDF4 as nc
import numpy as np


def inspect(case):
    path = case / 'output/output.nc'
    if not path.exists():
        path = case / 'output.nc'
    with nc.Dataset(case / 'bathymetry.nc') as grid:
        bathy = np.ma.filled(grid['bathymetry'][:], np.nan)
    wet = np.isfinite(bathy) & (bathy > 0)
    with nc.Dataset(path) as ds:
        if not {'hn', 'D', 'z'} <= set(ds.variables):
            raise ValueError(f'{case.name}: required geometry variables missing')
        depth_error = layer_error = 0.0
        minimum_depth = minimum_layer = float('inf')
        for index in range(len(ds.dimensions['time'])):
            depth = np.asarray(ds['D'][index])
            level = np.asarray(ds['z'][index])
            layers = np.asarray(ds['hn'][index])
            if not all(np.isfinite(v[..., wet]).all() for v in (depth, level, layers)):
                raise ValueError('Nonfinite physical geometry in wet cells')
            minimum_depth = min(minimum_depth, float(depth[wet].min()))
            minimum_layer = min(minimum_layer, float(layers[..., wet].min()))
            depth_error = max(depth_error, float(np.abs(depth[wet] - bathy[wet] - level[wet]).max()))
            layer_error = max(layer_error, float(np.abs(layers.sum(axis=0)[wet] - depth[wet]).max()))
        # D/z are barotropic fields; hn is updated at the 3-D macro step.
        # Permit 1 mm staggering/float32 roundoff, report the measured error.
        tolerance = max(1e-3, minimum_depth * 1e-5)
        return dict(case=case.name, frames=len(ds.dimensions['time']),
                    minimum_depth_m=minimum_depth, minimum_layer_m=minimum_layer,
                    depth_equals_bathymetry_plus_level_error_m=depth_error,
                    summed_layer_depth_error_m=layer_error, tolerance_m=tolerance,
                    passed=minimum_depth > 0 and minimum_layer > 0 and
                           depth_error < tolerance and layer_error < tolerance)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cases', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--case', action='append', dest='selected_cases',
                        help='Check only explicitly run case(s); default checks all cases')
    args = parser.parse_args()
    results = []
    for case in args.cases.iterdir():
        if args.selected_cases and case.name not in args.selected_cases:
            continue
        if case.is_dir() and (case / 'bathymetry.nc').exists():
            try:
                results.append(inspect(case))
            except Exception as error:
                results.append(dict(case=case.name, passed=False, error=str(error)))
    report = dict(passed=bool(results) and all(r['passed'] for r in results), results=results)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
