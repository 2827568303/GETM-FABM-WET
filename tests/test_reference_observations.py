from __future__ import annotations

import hashlib
import io
import json
import stat
import sys
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET/app'))


def _archive(entries, *, symlink_name=None):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in entries:
            info = zipfile.ZipInfo(name)
            info.external_attr = ((stat.S_IFLNK | 0o777) << 16) if name == symlink_name else (stat.S_IFREG | 0o644) << 16
            archive.writestr(info, data)
    return stream.getvalue()


def _official_fixture():
    obs = [
        'CHLA.obs', 'DO.obs', 'NH4.obs', 'NO23.obs', 'PO4.obs',
        'TEMP.obs', 'TOTN.obs', 'TOTP.obs',
    ]
    return _archive([
        *[(f'QWET_test_case_Lake_Ravn_workshop/OBSERVATIONS/{name}', b'2000-01-01 00:00:00 -1 2.5\n') for name in obs],
        ('QWET_test_case_Lake_Ravn_workshop/Default/gotm.exe', b'not extracted'),
        ('QWET_test_case_Lake_Ravn_workshop/OBSERVATIONS/wet_obs.xml', b'not an observation table'),
    ])


def _install(monkeypatch, tmp_path, payload):
    import reference_observations as module

    monkeypatch.setattr(module, 'ARCHIVE_SHA256', hashlib.sha256(payload).hexdigest())
    monkeypatch.setattr(module, 'ARCHIVE_MAX_BYTES', len(payload) + 1)

    class Response(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *args):
            self.close()

    monkeypatch.setattr(module.urllib.request, 'urlopen', lambda request, timeout: Response(payload))
    return module.install_ravn_observation_example(tmp_path)


def test_download_extracts_only_official_obs_and_returns_discoverable_folder(monkeypatch, tmp_path):
    import reference_observations as module

    result = _install(monkeypatch, tmp_path, _official_fixture())

    folder = Path(result['path'])
    assert folder.name == 'Lake Ravn workshop observations'
    assert len(list(folder.glob('*.obs'))) == 8
    assert not (folder / 'gotm.exe').exists()
    assert not (folder / 'wet_obs.xml').exists()
    provenance = json.loads((folder / 'provenance.json').read_text(encoding='utf-8'))
    assert provenance['source_url'].startswith('https://projects.au.dk/')
    assert provenance['archive_sha256'] == hashlib.sha256(_official_fixture()).hexdigest()
    assert provenance['redistribution_license'] == 'not stated by source page'

    examples = module.list_ravn_observation_examples(tmp_path)
    assert examples == [{
        'name': 'Lake Ravn workshop observations',
        'path': str(folder),
        'external': True,
        'kind': 'observation_reference',
    }]


def test_archive_hash_mismatch_does_not_create_reference_folder(monkeypatch, tmp_path):
    import reference_observations as module

    payload = _official_fixture()
    monkeypatch.setattr(module, 'ARCHIVE_SHA256', '0' * 64)
    monkeypatch.setattr(module, 'ARCHIVE_MAX_BYTES', len(payload) + 1)

    class Response(io.BytesIO):
        def __enter__(self): return self
        def __exit__(self, *args): self.close()

    monkeypatch.setattr(module.urllib.request, 'urlopen', lambda request, timeout: Response(payload))
    with pytest.raises(ValueError, match='SHA-256'):
        module.install_ravn_observation_example(tmp_path)
    assert not (tmp_path / 'Lake Ravn workshop observations').exists()


@pytest.mark.parametrize('name', [
    '../outside.obs',
    '/absolute.obs',
    'C:/drive.obs',
    'QWET_test_case_Lake_Ravn_workshop/OBSERVATIONS/../../outside.obs',
])
def test_rejects_traversal_names_before_writing_any_observation(monkeypatch, tmp_path, name):
    import reference_observations as module

    payload = _archive([(name, b'bad'), *_official_fixture_entries()])
    monkeypatch.setattr(module, 'ARCHIVE_SHA256', hashlib.sha256(payload).hexdigest())
    monkeypatch.setattr(module, 'ARCHIVE_MAX_BYTES', len(payload) + 1)

    class Response(io.BytesIO):
        def __enter__(self): return self
        def __exit__(self, *args): self.close()

    monkeypatch.setattr(module.urllib.request, 'urlopen', lambda request, timeout: Response(payload))
    with pytest.raises(ValueError, match='unsafe archive member'):
        module.install_ravn_observation_example(tmp_path)
    assert not list(tmp_path.glob('**/*.obs'))
    assert not (tmp_path.parent / 'outside.obs').exists()


def _official_fixture_entries():
    return [
        (f'QWET_test_case_Lake_Ravn_workshop/OBSERVATIONS/{name}', b'2000-01-01 00:00:00 -1 2.5\n')
        for name in ('CHLA.obs', 'DO.obs', 'NH4.obs', 'NO23.obs', 'PO4.obs', 'TEMP.obs', 'TOTN.obs', 'TOTP.obs')
    ]


def test_rejects_symlink_member_and_leaves_no_partial_output(monkeypatch, tmp_path):
    import reference_observations as module

    entries = _official_fixture_entries() + [('QWET_test_case_Lake_Ravn_workshop/SWAT/unsafe-link', b'')]
    payload = _archive(entries, symlink_name='QWET_test_case_Lake_Ravn_workshop/SWAT/unsafe-link')
    monkeypatch.setattr(module, 'ARCHIVE_SHA256', hashlib.sha256(payload).hexdigest())
    monkeypatch.setattr(module, 'ARCHIVE_MAX_BYTES', len(payload) + 1)

    class Response(io.BytesIO):
        def __enter__(self): return self
        def __exit__(self, *args): self.close()

    monkeypatch.setattr(module.urllib.request, 'urlopen', lambda request, timeout: Response(payload))
    with pytest.raises(ValueError, match='symlink'):
        module.install_ravn_observation_example(tmp_path)
    assert not (tmp_path / 'Lake Ravn workshop observations').exists()


def test_refuses_to_overwrite_existing_user_reference_folder(monkeypatch, tmp_path):
    import reference_observations as module

    target = tmp_path / 'Lake Ravn workshop observations'
    target.mkdir()
    keep = target / 'my-notes.txt'
    keep.write_text('preserve', encoding='utf-8')
    with pytest.raises(FileExistsError):
        module.install_ravn_observation_example(tmp_path)
    assert keep.read_text(encoding='utf-8') == 'preserve'
