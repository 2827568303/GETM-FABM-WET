"""The fish reproduction clock must be a native, persistent FABM state."""
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
FISH = ROOT / "3DWET/src/wet/src/fish.F90"


def test_reproduction_clock_is_registered_as_a_local_state_not_an_external_dependency():
    source = FISH.read_bytes().decode("ascii", errors="ignore")

    assert re.search(
        r"type\s*\(type_state_variable_id\)[^\n]*::[^\n]*id_Day_last_state",
        source,
        re.IGNORECASE,
    ), "fish needs a real per-cell state ID for the reproduction clock"
    assert re.search(
        r"register_state_variable\(\s*self%id_Day_last_state\s*,\s*'Day_last_state'",
        source,
        re.IGNORECASE,
    ), "the reproduction clock must enter FABM's restartable state registry"
    assert not re.search(
        r"register_dependency\(\s*self%id_Day_last\s*,\s*'Day_last'",
        source,
        re.IGNORECASE,
    ), "Day_last must not be read from an unprovided external dependency"
    assert re.search(r"_GET_\(self%id_Day_last_state,\s*Day_last\)", source)
    assert re.search(r"_SET_\(self%id_Day_last_state,\s*Day\)", source)

