import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "app"))
from wet_foodweb import compile_zooplankton_diet


POM = {
    "model": "wet/om_pool",
    "states": {"sD", "sP", "sN", "sC", "oSi"},
    "state_units": {"sD": "gDW/m3", "sP": "gP/m3", "sN": "gN/m3", "sC": "gC/m3"},
}
PHYTOPLANKTON = {
    "model": "wet/phytoplankton",
    "states": {"sD", "sP", "sN", "sC"},
    "state_units": {"sD": "gDW/m3", "sP": "gP/m3", "sN": "gN/m3", "sC": "gC/m3"},
}


def _configured_consumer():
    return {
        "name": "cladocerans",
        "model": "wet/zooplankton",
        "parameters": {
            "nPrey": 1,
            "cClearPrey1": 0.25,
            "fGutOccPrey1": 0.5,
            "lSi1": False,
        },
        "coupling": {"prey_model1": "POM"},
    }


def test_existing_out_of_family_pom_is_preserved_when_saving_an_added_valid_prey():
    original = _configured_consumer()
    rows = [
        {"target": "POM", "suffix": "", "clearance": 0.25, "gut_occupation": 0.5, "lSi": False},
        {"target": "diatoms", "suffix": "", "clearance": 0.3, "gut_occupation": 0.6, "lSi": False},
    ]

    saved = compile_zooplankton_diet(original, rows, {"POM": POM, "diatoms": PHYTOPLANKTON})

    assert saved["coupling"]["prey_model1"] == "POM"
    assert saved["parameters"]["cClearPrey1"] == 0.25
    assert saved["parameters"]["fGutOccPrey1"] == 0.5
    assert saved["parameters"]["lSi1"] is False
    assert saved["coupling"]["prey_model2"] == "diatoms"
    assert saved["parameters"]["nPrey"] == 2


def test_new_out_of_family_pom_target_is_still_rejected():
    with pytest.raises(ValueError, match="DOMAIN_MISMATCH"):
        compile_zooplankton_diet(
            {"model": "wet/zooplankton", "parameters": {}, "coupling": {}},
            [{"target": "POM", "suffix": "", "clearance": 0.25, "gut_occupation": 0.5}],
            {"POM": POM},
        )


def test_changing_an_existing_prey_to_a_different_out_of_family_target_is_rejected():
    with pytest.raises(ValueError, match="DOMAIN_MISMATCH"):
        compile_zooplankton_diet(
            _configured_consumer(),
            [{"target": "other_POM", "suffix": "", "clearance": 0.25, "gut_occupation": 0.5}],
            {"POM": POM, "other_POM": POM},
        )


def test_existing_out_of_family_pom_still_validates_and_saves_edited_diet_parameters():
    original = _configured_consumer()
    rows = [{"target": "POM", "suffix": "", "clearance": 0.4, "gut_occupation": 0.7, "lSi": True}]

    saved = compile_zooplankton_diet(original, rows, {"POM": POM})

    assert saved["parameters"]["cClearPrey1"] == 0.4
    assert saved["parameters"]["fGutOccPrey1"] == 0.7
    assert saved["parameters"]["lSi1"] is True


@pytest.mark.parametrize(
    ("catalog", "row", "message"),
    [
        ({"POM": {**POM, "states": set(POM["states"]) - {"sD"}}},
         {"target": "POM", "suffix": "", "clearance": 0.4, "gut_occupation": 0.7, "lSi": False},
         "UNKNOWN_PORT"),
        ({"POM": {**POM, "state_units": {**POM["state_units"], "sD": "gDW/m2"}}},
         {"target": "POM", "suffix": "", "clearance": 0.4, "gut_occupation": 0.7, "lSi": False},
         "UNIT_MISMATCH"),
        ({"POM": {**POM, "states": set(POM["states"]) - {"oSi"}}},
         {"target": "POM", "suffix": "", "clearance": 0.4, "gut_occupation": 0.7, "lSi": True},
         "UNKNOWN_PORT"),
        ({"POM": POM},
         {"target": "POM", "suffix": "", "clearance": -0.1, "gut_occupation": 0.7, "lSi": False},
         "INVALID_VALUE"),
        ({"POM": POM},
         {"target": "POM", "suffix": "", "clearance": 0.4, "gut_occupation": 0, "lSi": False},
         "INVALID_VALUE"),
    ],
)
def test_existing_out_of_family_prey_still_checks_state_unit_and_silica_contract(catalog, row, message):
    with pytest.raises(ValueError, match=message):
        compile_zooplankton_diet(_configured_consumer(), [row], catalog)
