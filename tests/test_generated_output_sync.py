from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
GENERATORS = (
    ROOT / '3DWET/app/server.py',
    ROOT / '3DWET/model_builder/build_configs.py',
    ROOT / '3DWET/workflow/2_build_case/build_case.py',
)


def test_new_getm_configs_sync_each_output_record_without_changing_output_steps():
    for generator in GENERATORS:
        source = generator.read_text(encoding='utf-8')
        assert re.search(r'^\s*sync_2d\s*=\s*1\s*$', source, re.MULTILINE), generator
        assert re.search(r'^\s*sync_3d\s*=\s*1\s*$', source, re.MULTILINE), generator
    assert 'step_2d = {output_steps}' in GENERATORS[0].read_text(encoding='utf-8')
    assert 'step_3d = {output_steps}' in GENERATORS[0].read_text(encoding='utf-8')
    assert 'step_2d = 1440' in GENERATORS[1].read_text(encoding='utf-8')
    assert 'step_3d = 1440' in GENERATORS[1].read_text(encoding='utf-8')
    assert "step_2d = {out['freq_2d']}" in GENERATORS[2].read_text(encoding='utf-8')
    assert "step_3d = {out['freq_3d']}" in GENERATORS[2].read_text(encoding='utf-8')
