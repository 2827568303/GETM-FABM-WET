"""Build the FABM model configuration (fabm.yaml) for a lake.

fabm.yaml is the most complex configuration file consumed by GETM-FABM-WET.
It describes the entire WET ecological model: abiotic water/sediment pools,
organic matter (POM/DOM/humus), macrophytes, three phytoplankton groups,
two zooplankton groups, zoobenthos, and three fish stages, along with all
PCLake parameters and inter-instance couplings.

The bulk of the file (PCLake parameters, coupling graph, sediment state,
_PV pelagic variables, etc.) is lake-independent and lives in the template.
Only the *initialization* values for the pelagic state variables are
lake-specific and are taken from :class:`LakeConfig`.

The template uses ``__PLACEHOLDER__`` tokens (double-underscore, uppercase)
that this builder replaces with the corresponding config value via plain
``str.replace``.

Reference case: 3DWET/case/Yilong/fabm.yaml (1146 lines).
"""
from __future__ import annotations

import os
import sys

# Ensure the 3DWET root is importable so we can reach preprocessor.lake_config
# whether this module is imported as part of a package or run standalone.
_3DWET_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _3DWET_ROOT not in sys.path:
    sys.path.insert(0, _3DWET_ROOT)

from preprocessor.lake_config import LakeConfig


# Path to the YAML template bundled with this module.
_TEMPLATE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "templates",
    "fabm.yaml.template",
)


def build_fabm_yaml(config: LakeConfig, output_dir: str) -> str:
    """Generate the FABM model configuration file (fabm.yaml).

    Reads ``templates/fabm.yaml.template``, substitutes every
    ``__PLACEHOLDER__`` token with the matching value from *config*, and
    writes the result to ``<output_dir>/fabm.yaml``.

    Parameters
    ----------
    config : LakeConfig
        Lake configuration. Reads the pelagic initial-condition fields
        (nh4_init, no3_init, po4_init, sio2_init, o2_init, dim_init) and the
        biomass fields for phytoplankton (diatoms/greens/cyanobacteria),
        zooplankton (cladocerans/copepods) and fish (jufish/adfish/piscfish).
    output_dir : str
        Directory where fabm.yaml will be written (created if missing).

    Returns
    -------
    str
        Absolute path to the generated fabm.yaml file.
    """
    with open(_TEMPLATE_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Map template placeholders to LakeConfig field values.
    # Each placeholder targets one initialization entry:
    #   - abiotic_water: dissolved nutrients / O2 / inorganic matter
    #   - phytoplankton (diatoms/greens/cyanobacteria): sDW water-column biomass
    #   - zooplankton (cladocerans/copepods): sD biomass
    #   - fish (JuFish/AdFish/PiscFish): sD biomass
    replacements = {
        "__NH4_INIT__": str(config.nh4_init),
        "__NO3_INIT__": str(config.no3_init),
        "__PO4_INIT__": str(config.po4_init),
        "__SIO2_INIT__": str(config.sio2_init),
        "__O2_INIT__": str(config.o2_init),
        "__DIM_INIT__": str(config.dim_init),
        "__DIATOMS_INIT__": str(config.diatoms_init),
        "__GREENS_INIT__": str(config.greens_init),
        "__CYANOBACTERIA_INIT__": str(config.cyanobacteria_init),
        "__CLADOCERANS_INIT__": str(config.cladocerans_init),
        "__COPEPODS_INIT__": str(config.copepods_init),
        "__JUFISH_INIT__": str(config.jufish_init),
        "__ADFISH_INIT__": str(config.adfish_init),
        "__PISCFISH_INIT__": str(config.piscfish_init),
    }

    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "fabm.yaml")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    return output_path
