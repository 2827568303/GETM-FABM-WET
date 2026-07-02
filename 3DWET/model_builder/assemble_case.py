"""Main model_builder entry point.

Assembles all configuration files needed to run GETM-FABM-WET:
  getm.inp, getm_fabm.inp, gotmturb.nml, gotm_fabm.yaml, output.yaml, fabm.yaml

Usage:
  python -m model_builder.assemble_case --config lake_config.yaml --output case/MyLake

  # Or programmatically:
  from model_builder import assemble_case
  from preprocessor import LakeConfig
  config = LakeConfig.from_yaml("lake_config.yaml")
  assemble_case.assemble(config, output_dir="case/MyLake")
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import List

from preprocessor.lake_config import LakeConfig
from .build_configs import build_all_configs
from .build_fabm_yaml import build_fabm_yaml


def assemble(config: LakeConfig, output_dir: str) -> List[str]:
    """Generate all configuration files into output_dir.

    Args:
        config: LakeConfig instance
        output_dir: target directory (same as preprocessor output)

    Returns:
        List of generated file paths
    """
    os.makedirs(output_dir, exist_ok=True)
    generated: List[str] = []

    print("=" * 70)
    print(f"3DWET Model Builder - {config.lake_name}")
    print(f"  Output: {output_dir}")
    print("=" * 70)

    # Step 1: short config files (getm.inp, getm_fabm.inp, gotmturb.nml, gotm_fabm.yaml, output.yaml)
    print("\n[1/2] Building short config files (getm.inp, getm_fabm.inp, ...) ...")
    short_files = build_all_configs(config, output_dir)
    generated.extend(short_files)
    for f in short_files:
        print(f"  -> {os.path.basename(f)}")

    # Step 2: fabm.yaml (from template)
    print("\n[2/2] Building fabm.yaml from template ...")
    fabm_path = build_fabm_yaml(config, output_dir)
    generated.append(fabm_path)
    print(f"  -> {os.path.basename(fabm_path)}")

    # Summary
    print("\n" + "=" * 70)
    print("Model assembly complete!")
    print("=" * 70)
    print(f"Generated {len(generated)} config files in {output_dir}")
    print("\nReady for model run. Next steps:")
    print(f"  cd {output_dir}")
    print(f"  # Run GETM-FABM-WET executable")

    return generated


def main():
    """Command-line entry point."""
    parser = argparse.ArgumentParser(
        description="3DWET Model Builder: assemble configuration files for GETM-FABM-WET"
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
        script_dir = os.path.dirname(os.path.abspath(__file__))
        twet_root = os.path.dirname(script_dir)
        output_dir = os.path.join(twet_root, output_dir)

    assemble(config, output_dir)


if __name__ == "__main__":
    main()
