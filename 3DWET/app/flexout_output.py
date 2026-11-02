"""Flexout output.yaml for a 3DWET case.

GETM registers each FABM field with
``category='fabm'//model%get_path()`` (see ``getm_fabm.F90``), so an
instance named ``abiotic_water`` lives in ``fabm/abiotic_water``.
Flexout treats ``source: abiotic_water/*`` as a different category.
That category is empty, the log says it has no variables at the
requested output level, and ``ext_wq.nc`` is not created.

State variables use ``output_level_default`` (8) unless the FABM
variable itself sets ``output=output_none``, which is registered at
the debug level (32) and stays out of the weekly file.

The weekly file lists those state names explicitly. A wildcard
``fabm/<instance>/*`` at level 8 also pulls every instantaneous
diagnostic (rates, limitation factors, burial fluxes). That set is
opt-in: put the wildcard back in ``output.yaml`` when it is needed.
Chlorophyll is not a state variable; the three phytoplankton
``oChla`` fields and the ``wet_chla`` aggregate are included because
the result pages look them up by name.
"""

WEEKLY_INSTANCES = (
    'abiotic_water',
    'abiotic_sediment',
    'POM',
    'DOM',
    'humus',
    'cyanobacteria',
    'diatoms',
    'greens',
    'macrophytes',
    'cladocerans',
    'copepods',
    'zoobenthos',
    'JuFish',
    'AdFish',
    'PiscFish',
    'inorganic_carbon',
    'methane',
)

# field_manager.F90: output_level_default = 8, output_level_debug = 32.
OUTPUT_LEVEL_DEFAULT = 8
OUTPUT_LEVEL_DEBUG = 32

# Initialization keys from the Dianchi WET configuration. These are the
# pelagic and sediment state variables. Names are ``<instance>_<key>``,
# which is how GETM registers them.
WEEKLY_STATE_KEYS = {
    'abiotic_water': ('sNH4W', 'sNO3W', 'sPO4W', 'sPAIMW', 'sSiO2W', 'sO2W', 'sDIMW', 'sSiPaW'),
    'abiotic_sediment': ('sNH4S', 'sNO3S', 'sPO4S', 'sPAIMS', 'sDIMS', 'sSiO2S', 'sSiPaS'),
    'POM': ('sDW', 'sNW', 'sPW', 'sCW', 'sDS', 'sNS', 'sPS', 'sCS', 'sDS_PV', 'sNS_PV', 'sPS_PV', 'sCS_PV'),
    'DOM': ('sDW', 'sNW', 'sPW', 'sCW', 'sDS', 'sNS', 'sPS', 'sCS'),
    'humus': ('sDS', 'sNS', 'sPS', 'sCS', 'sDS_PV', 'sNS_PV', 'sPS_PV', 'sCS_PV'),
    'cyanobacteria': ('sDW', 'sNW', 'sPW', 'sCW', 'sDS', 'sNS', 'sPS', 'sCS', 'sDS_PV', 'sNS_PV', 'sPS_PV', 'sCS_PV'),
    'diatoms': ('sDW', 'sNW', 'sPW', 'sCW', 'sDS', 'sNS', 'sPS', 'sCS', 'sDS_PV', 'sNS_PV', 'sPS_PV', 'sCS_PV'),
    'greens': ('sDW', 'sNW', 'sPW', 'sCW', 'sDS', 'sNS', 'sPS', 'sCS', 'sDS_PV', 'sNS_PV', 'sPS_PV', 'sCS_PV'),
    'macrophytes': ('sD', 'sN', 'sP', 'sC', 'sD_PV', 'sN_PV', 'sP_PV', 'sC_PV'),
    'cladocerans': ('sD', 'sN', 'sP', 'sC'),
    'copepods': ('sD', 'sN', 'sP', 'sC'),
    'zoobenthos': ('sD', 'sN', 'sP', 'sC', 'sD_PV', 'sN_PV', 'sP_PV', 'sC_PV'),
    'JuFish': ('sD', 'sP', 'sN', 'sC'),
    'AdFish': ('sD', 'sP', 'sN', 'sC'),
    'PiscFish': ('sD', 'sP', 'sN', 'sC'),
    'inorganic_carbon': ('sDICW', 'sAlkW'),
    'methane': ('sCH4W',),
}

# Chlorophyll is a diagnostic. Group fields plus the aggregate the
# dashboard resolves through result_aliases (wet_chla_calculator_result).
WEEKLY_CHLOROPHYLL = (
    'cyanobacteria_oChla',
    'diatoms_oChla',
    'greens_oChla',
    'wet_chla_calculator_result',
)


def weekly_variable_names():
    """State variables, then chlorophyll. Diagnostics are not included."""
    names = []
    for instance in WEEKLY_INSTANCES:
        names.extend(f'{instance}_{key}' for key in WEEKLY_STATE_KEYS[instance])
    names.extend(WEEKLY_CHLOROPHYLL)
    return tuple(names)


def case_output_yaml(daily_step_seconds) -> str:
    """Daily key fields plus a weekly water-quality file."""
    step = str(daily_step_seconds)
    weekly = '\n'.join(f'      - source: {name}' for name in weekly_variable_names())
    return (
        'allow_missing_fields: true\n'
        'output:\n'
        '   time_unit: second\n'
        f'   time_step: {step}\n'
        '   sync_interval: 1\n'
        '   variables:\n'
        '      - source: temp\n'
        '      - source: D\n'
        '      - source: hn\n'
        '      - source: z\n'
        '      - source: abiotic_water_sO2W\n'
        'ext_wq:\n'
        '   time_unit: day\n'
        '   time_step: 7\n'
        '   sync_interval: 1\n'
        '   variables:\n'
        f'{weekly}\n'
    )


def fields_for_source(fields, source, output_level=OUTPUT_LEVEL_DEFAULT):
    """Fields flexout would put in one wildcard source.

    ``fields`` items are ``(name, category, output_level)``. A wildcard
    walks that category and its children, and keeps fields whose level
    is less than or equal to the requested level. This is
    ``get_all_fields`` in ``field_manager.F90``.
    """
    if not str(source).endswith('/*'):
        return [name for name, _category, _level in fields if name == source]
    category = source[:-2]
    prefix = category + '/'
    chosen = []
    for name, field_category, level in fields:
        in_category = field_category == category or field_category.startswith(prefix)
        if in_category and level <= output_level:
            chosen.append(name)
    return chosen
