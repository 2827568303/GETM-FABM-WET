"""Source-backed elemental bases for variables from attested WET producers.

Names alone never authorize a basis. Callers must supply an explicit producer
identity, typically copied from a model output's ``wet_native_metadata_source``
attribute or an audited model-side manifest.
"""

_PRODUCERS = {
    'wet_getm_native': {
        'label': 'Repository WET GETM native source',
        'source_version': 'local WET v2.3-compatible hybrid; see wet_upstream_manifest.json',
    },
    'wet_ravn_gotm_943d3c4': {
        'label': 'Aarhus Lake Ravn workshop GOTM-WET output',
        'source_version': 'WET 943d3c4 (workshop run provenance)',
    },
}

_ABIOTIC = {
    'abiotic_water_sO2W': {
        'unit': 'gO2/m3', 'raw_units': {'g/m3'}, 'mass_basis': 'O2',
        'long_name': 'oxygen', 'source_file': '3DWET/src/wet/src/abiotic_water.F90',
        'source_lines': [107, 203, 230, 253],
        'basis_evidence': 'registered as oxygen; used in oxygen saturation and O2 reaeration/nitrification fluxes',
    },
    'abiotic_water_sNH4W': {
        'unit': 'gN/m3', 'raw_units': {'g/m3', 'gN/m3'}, 'mass_basis': 'N',
        'long_name': 'ammonium', 'source_file': '3DWET/src/wet/src/abiotic_water.F90',
        'source_lines': [90, 103, 219, 242, 250],
        'basis_evidence': 'tNDepoNH4 and wNAbioNH4W/wNNitrW conserve this state as nitrogen mass',
    },
    'abiotic_water_sNO3W': {
        'unit': 'gN/m3', 'raw_units': {'g/m3', 'gN/m3'}, 'mass_basis': 'N',
        'long_name': 'nitrate', 'source_file': '3DWET/src/wet/src/abiotic_water.F90',
        'source_lines': [91, 104, 243, 251],
        'basis_evidence': 'tNDepoNO3 and wNAbioNO3W are nitrogen-mass fluxes',
    },
    'abiotic_water_sPO4W': {
        'unit': 'gP/m3', 'raw_units': {'g/m3', 'gP/m3'}, 'mass_basis': 'P',
        'long_name': 'phosphate', 'source_file': '3DWET/src/wet/src/abiotic_water.F90',
        'source_lines': [89, 101, 212, 248],
        'basis_evidence': 'tPDepoPO4 and wPAbioPO4W conserve this state as phosphorus mass',
    },
    'abiotic_water_sPAIMW': {
        'unit': 'gP/m3', 'raw_units': {'g/m3', 'gP/m3'}, 'mass_basis': 'P',
        'long_name': 'inorganic-matter-adsorbed phosphorus', 'source_file': '3DWET/src/wet/src/abiotic_water.F90',
        'source_lines': [102, 214, 249],
        'basis_evidence': 'registered as adsorbed P and balanced by wPAbioAIMW',
    },
}

_TOTALS = {
    'wet_totN_calculator_result': {
        'unit': 'gN/m3', 'raw_units': {'', 'gN/m3'}, 'mass_basis': 'N',
        'source_file': '3DWET/src/wet/src/abiotic_water.F90; om_pool.F90; phytoplankton.F90; zooplankton.F90',
        'source_lines': [125, 126, 197, 254, 125],
        'basis_evidence': 'FABM wet_totN sum of NH4, NO3 and the sNW/sNZoo N pools; N states/fluxes identify elemental N',
    },
    'wet_totP_calculator_result': {
        'unit': 'gP/m3', 'raw_units': {'', 'gP/m3'}, 'mass_basis': 'P',
        'source_file': '3DWET/src/wet/src/abiotic_water.F90; om_pool.F90; phytoplankton.F90; zooplankton.F90',
        'source_lines': [127, 128, 198, 255, 126],
        'basis_evidence': 'FABM wet_totP sum of PO4, adsorbed P and the sPW/sPZoo P pools; P states/fluxes identify elemental P',
    },
}

_VARIABLES = {**_ABIOTIC, **_TOTALS}


def describe_native_variable(variable, raw_unit, producer=None):
    """Return native metadata only for an exact, attested producer and unit."""
    source = _PRODUCERS.get(str(producer or ''))
    spec = _VARIABLES.get(str(variable or ''))
    if source is None or spec is None or str(raw_unit or '').strip() not in spec['raw_units']:
        return None
    return {
        'unit': spec['unit'],
        'mass_basis': spec['mass_basis'],
        'source': source['label'],
        'provenance': {
            'source_file': spec['source_file'],
            'source_lines': spec['source_lines'],
            'source_version': source['source_version'],
            'basis_evidence': spec['basis_evidence'],
        },
    }


def known_producer(producer):
    return str(producer or '') in _PRODUCERS
