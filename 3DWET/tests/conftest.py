"""Keep pytest's persistent case state away from the desktop app profile."""
import os
import tempfile
from pathlib import Path


_pytest_case_state = Path(tempfile.mkdtemp(prefix="wet-pytest-state-"))
os.environ["WET_CASE_STATE_DIR"] = str(_pytest_case_state)
