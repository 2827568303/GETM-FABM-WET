"""The fish PISC dependency must match the native pred_dummy producer unit."""
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
FISH_SOURCE = ROOT / "3DWET/src/wet/src/fish.F90"


def test_pisc_pred_dummy_dependency_uses_the_producers_unit():
    # The legacy source has malformed replacement characters in comments, but
    # its ASCII Fortran identifiers remain intact in the byte stream.
    source = FISH_SOURCE.read_bytes().decode("ascii", errors="ignore")
    producer = re.search(
        r"register_diagnostic_variable\([^\n]*?\bid_predD\s*,\s*'pred_dummy'\s*,\s*'([^']+)'",
        source,
        flags=re.IGNORECASE,
    )
    consumer = re.search(
        r"register_state_dependency\([^\n]*?\bid_pred_dummy_Pisc\(i_prey\)\s*,\s*'pred_dummy'//trim\(index\)\s*,\s*'([^']+)'",
        source,
        flags=re.IGNORECASE,
    )
    assert producer, "fish must keep registering its native pred_dummy diagnostic/state producer"
    assert consumer, "PISC must keep registering the prey pred_dummy state dependency"
    assert consumer.group(1) == producer.group(1), (
        "PISC pred_dummy dependency unit must equal the producer unit; "
        f"producer={producer.group(1)!r}, dependency={consumer.group(1)!r}"
    )


def test_pred_dummy_contract_repair_does_not_change_stage_memory_or_restart_sources():
    source = FISH_SOURCE.read_bytes().decode("ascii", errors="ignore")
    assert "self%id_Day_last" in source
    assert "column_memory" not in source[source.find("id_Day_last") : source.find("id_Day_last") + 1200]
    assert "if (self%qStage > 0)" in source
    assert "_GET_(self%id_sFRes,sFRes)" in source


def test_zero_biomass_has_finite_reference_stoichiometry_before_respiration():
    source = FISH_SOURCE.read_bytes().decode("ascii", errors="ignore")
    zero_branch = re.search(
        r"if\s*\([^\n]*sDFi\s*>\s*NearZero\)\s*then(.*?)else(.*?)endif",
        source,
        flags=re.IGNORECASE | re.DOTALL,
    )
    assert zero_branch, "fish must avoid undefined nutrient ratios when biomass is zero"
    assert "sPFi /" in zero_branch.group(1)
    assert "rPDFi = self%cPDRef" in zero_branch.group(2)
    assert "rNDFi = self%cNDRef" in zero_branch.group(2)
    assert "rCDFi = self%cCDRef" in zero_branch.group(2)
