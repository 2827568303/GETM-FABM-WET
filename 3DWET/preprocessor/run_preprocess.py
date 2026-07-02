"""Main preprocessor entry point.

Runs all generators in sequence:
  bathymetry -> rivers -> meteo -> initial_conditions -> validate

Usage:
  python -m preprocessor.run_preprocess --config lake_config.yaml --output case/MyLake

  # Or programmatically:
  from preprocessor import run_preprocess, LakeConfig
  config = LakeConfig.from_yaml("lake_config.yaml")
  run_preprocess(config, output_dir="case/MyLake")
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import List

from .lake_config import LakeConfig
from .generate_bathymetry import generate_bathymetry
from .generate_rivers import generate_rivers
from .generate_meteo import generate_meteo
from .generate_initial_conditions import generate_initial_conditions
from .validate_inputs import validate_all


def run_preprocess(config: LakeConfig, output_dir: str) -> List[str]:
    """Generate all standardized input files into output_dir.

    Args:
        config: LakeConfig instance (or loaded from YAML)
        output_dir: target directory for input files

    Returns:
        List of paths to generated files
    """
    os.makedirs(output_dir, exist_ok=True)
    generated: List[str] = []

    print("=" * 70)
    print(f"3DWET Preprocessor - {config.lake_name}")
    print(f"  Grid: {config.nx}x{config.ny} @ {config.dx}m")
    print(f"  Simulation: {config.start_date} to {config.end_date} ({config.n_days} days)")
    print(f"  Rivers: {len(config.rivers)} ({len(config.inflow_rivers)} inflow, {len(config.outflow_rivers)} outflow)")
    print(f"  Output: {output_dir}")
    print("=" * 70)

    # Step 1: bathymetry
    print("\n[1/5] Generating bathymetry.nc ...")
    bathy_path = generate_bathymetry(config, output_dir)
    generated.append(bathy_path)

    # Step 2: rivers
    print("\n[2/5] Generating riverinfo.dat + rivers.nc ...")
    rivers_path = generate_rivers(config, bathy_path, output_dir)
    if rivers_path:
        generated.append(rivers_path)
    generated.append(os.path.join(output_dir, "riverinfo.dat"))

    # Step 3: meteo
    print("\n[3/5] Generating meteo.nc + meteo_input.txt ...")
    meteo_path = generate_meteo(config, bathy_path, output_dir)
    generated.append(meteo_path)
    generated.append(os.path.join(output_dir, "meteo_input.txt"))

    # Step 4: initial conditions
    print("\n[4/5] Generating fabm_init.nc ...")
    fabm_init_path = generate_initial_conditions(config, bathy_path, output_dir)
    generated.append(fabm_init_path)

    # Step 5: validate
    print("\n[5/5] Validating all input files ...")
    errors = validate_all(config, output_dir)
    if errors:
        print("\n*** VALIDATION ERRORS ***")
        for e in errors:
            print(f"  ERROR: {e}")
        print(f"\n{len(errors)} error(s) found. Please fix before running model.")
    else:
        print("  All input files validated OK.")

    # Summary
    print("\n" + "=" * 70)
    print("Preprocessing complete!")
    print("=" * 70)
    print(f"Generated {len(generated)} files in {output_dir}:")
    for f in generated:
        print(f"  {os.path.basename(f)}")

    return generated


def main():
    """Command-line entry point."""
    parser = argparse.ArgumentParser(
        description="3DWET Preprocessor: generate standardized input files for GETM-FABM-WET"
    )
    parser.add_argument("--config", "-c", required=True,
                        help="Path to lake_config.yaml")
    parser.add_argument("--output", "-o", default=None,
                        help="Output directory (default: case_dir from config)")
    args = parser.parse_args()

    config = LakeConfig.from_yaml(args.config)
    output_dir = args.output or config.case_dir

    # Resolve relative to 3DWET root if needed
    if not os.path.isabs(output_dir):
        # 3DWET root is the parent of the preprocessor package
        script_dir = os.path.dirname(os.path.abspath(__file__))
        twet_root = os.path.dirname(script_dir)  # go up from preprocessor/ to 3DWET/
        output_dir = os.path.join(twet_root, output_dir)

    run_preprocess(config, output_dir)


if __name__ == "__main__":
    main()
