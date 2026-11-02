"""Map dashboard concepts to names actually written by the model."""


def resolve_result_name(variables, requested):
    aliases = {'wet_chla': ('wet_chla_calculator_result', 'wet_chla')}
    return next((name for name in aliases.get(requested, (requested,))
                 if name in variables), None)
