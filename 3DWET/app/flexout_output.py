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


def case_output_yaml(daily_step_seconds) -> str:
    """Daily key fields plus a weekly water-quality file."""
    step = str(daily_step_seconds)
    weekly = '\n'.join(
        f'      - source: fabm/{name}/*\n        output_level: {OUTPUT_LEVEL_DEFAULT}'
        for name in WEEKLY_INSTANCES
    )
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
