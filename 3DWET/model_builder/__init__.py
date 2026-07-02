"""3DWET Model Builder Module (Module 2)

Generates configuration files for GETM-FABM-WET from LakeConfig:
  - getm.inp, getm_fabm.inp, gotmturb.nml, gotm_fabm.yaml, output.yaml
  (fabm.yaml is handled separately by build_fabm_yaml.py)
"""
from .build_configs import build_all_configs, build_getm_inp

__all__ = ["build_all_configs", "build_getm_inp"]
