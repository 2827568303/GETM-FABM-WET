import re
from pathlib import Path


SOURCE = (
    Path(__file__).resolve().parents[1]
    / "3DWET"
    / "src"
    / "wet"
    / "src"
    / "phytoplankton.F90"
)


def test_every_set_phytoplankton_diagnostic_id_is_registered():
    # The legacy Fortran source contains non-UTF-8 comments; all tokens checked
    # below are ASCII, so Latin-1 gives a lossless byte-to-character read.
    source = SOURCE.read_text(encoding="latin-1")
    written_ids = set(
        re.findall(r"_SET_(?:HORIZONTAL_)?DIAGNOSTIC_\(self%(id_\w+)", source)
    )
    registered_ids = set(
        re.findall(r"register_diagnostic_variable\(self%(id_\w+)", source)
    )

    assert written_ids <= registered_ids, (
        "diagnostic IDs are written without registration: "
        + ", ".join(sorted(written_ids - registered_ids))
    )
