from importlib import reload
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / '3DWET' / 'app'
sys.path.insert(0, str(APP))

import fish_support  # noqa: E402


def test_runtime_model_root_override_does_not_hide_repository_fish_template(tmp_path):
    staged_root = tmp_path / 'staged-model'
    (staged_root / 'bin').mkdir(parents=True)
    (staged_root / 'case').mkdir()
    previous_root = os.environ.get('WET_MODEL_ROOT')
    os.environ['WET_MODEL_ROOT'] = str(staged_root)
    module = reload(fish_support)
    try:
        template = module.load_fish_template()
        assert template is not None
        assert set(template) == set(module.FISH_INSTANCES)
    finally:
        if previous_root is None:
            os.environ.pop('WET_MODEL_ROOT', None)
        else:
            os.environ['WET_MODEL_ROOT'] = previous_root
        reload(module)
