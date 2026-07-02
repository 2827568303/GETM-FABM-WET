"""3DWET Preprocessor Module (Module 1)

Generates standardized input files for GETM-FABM-WET lake model:
  - bathymetry.nc      (lake grid + bottom topography)
  - riverinfo.dat      (river index file)
  - rivers.nc          (river discharge + water quality)
  - meteo.nc           (meteorological forcing)
  - meteo_input.txt    (meteo file pointer)
  - fabm_init.nc       (FABM initial conditions)

Usage:
  from preprocessor import LakeConfig, run_preprocess
  config = LakeConfig.from_yaml("lake_config.yaml")
  run_preprocess(config, output_dir="case/MyLake")
"""
from .lake_config import LakeConfig, RiverConfig
from .run_preprocess import run_preprocess

__all__ = ["LakeConfig", "RiverConfig", "run_preprocess"]
