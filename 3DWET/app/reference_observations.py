"""Opt-in, hash-verified access to official Lake Ravn workshop observations.

Only the workshop's eight plain-text ``OBSERVATIONS/*.obs`` files are placed
in a user-selected local reference folder. The source archive itself is never
bundled or retained by this application.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import tempfile
import urllib.request
import zipfile


ARCHIVE_URL = (
    'https://projects.au.dk/fileadmin/projects/wet/resources/ftp/'
    'QWET_test_case_Lake_Ravn_workshop.zip'
)
ARCHIVE_SHA256 = '9a8767c2b5e235de268d31d1808220bcb062deb2704ef890b137827ef062a56b'
ARCHIVE_MAX_BYTES = 50 * 1024 * 1024
OBSERVATION_MAX_BYTES = 2 * 1024 * 1024
OBSERVATIONS_TOTAL_MAX_BYTES = 10 * 1024 * 1024
TARGET_NAME = 'Lake Ravn workshop observations'
ARCHIVE_PREFIX = 'QWET_test_case_Lake_Ravn_workshop/OBSERVATIONS/'
EXPECTED_FILES = frozenset({
    'CHLA.obs', 'DO.obs', 'NH4.obs', 'NO23.obs', 'PO4.obs',
    'TEMP.obs', 'TOTN.obs', 'TOTP.obs',
})


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def _download_archive(path: Path, timeout: float) -> None:
    request = urllib.request.Request(
        ARCHIVE_URL,
        headers={'User-Agent': '3DWETStudio-observation-reference/1.0'},
    )
    total = 0
    with urllib.request.urlopen(request, timeout=timeout) as response, path.open('wb') as output:
        while True:
            chunk = response.read(1024 * 128)
            if not chunk:
                break
            total += len(chunk)
            if total > ARCHIVE_MAX_BYTES:
                raise ValueError('official archive exceeds the permitted download size')
            output.write(chunk)
        output.flush()
        os.fsync(output.fileno())
    if total == 0:
        raise ValueError('official archive download was empty')


def _safe_member_name(info: zipfile.ZipInfo) -> PurePosixPath:
    name = info.filename
    if (not name or '\x00' in name or '\\' in name or ':' in name
            or name.startswith('/') or name.startswith('//')):
        raise ValueError(f'unsafe archive member path: {name!r}')
    raw_parts = name[:-1].split('/') if name.endswith('/') else name.split('/')
    parsed = PurePosixPath(name)
    if parsed.is_absolute() or any(part in {'', '.', '..'} for part in raw_parts):
        raise ValueError(f'unsafe archive member path: {name!r}')
    mode = (info.external_attr >> 16) & 0xFFFF
    kind = stat.S_IFMT(mode)
    if kind == stat.S_IFLNK:
        raise ValueError(f'archive symlink member is not allowed: {name!r}')
    if kind not in (0, stat.S_IFREG, stat.S_IFDIR):
        raise ValueError(f'archive special file is not allowed: {name!r}')
    return parsed


def _observation_members(archive: zipfile.ZipFile) -> dict[str, zipfile.ZipInfo]:
    found: dict[str, zipfile.ZipInfo] = {}
    seen = set()
    total = 0
    for info in archive.infolist():
        path = _safe_member_name(info)
        normalized = path.as_posix().casefold()
        if normalized in seen:
            raise ValueError(f'duplicate archive member path: {info.filename!r}')
        seen.add(normalized)
        if info.flag_bits & 0x1:
            raise ValueError('encrypted archive members are not supported')
        name = path.as_posix()
        if not name.startswith(ARCHIVE_PREFIX) or info.is_dir():
            continue
        relative = name[len(ARCHIVE_PREFIX):]
        # Only direct-child .obs data files are accepted; other workshop
        # payloads, including executables, scripts, XML, and nested files,
        # remain inside the compressed archive and are never extracted.
        if '/' in relative or not relative.lower().endswith('.obs'):
            continue
        if relative not in EXPECTED_FILES:
            raise ValueError(f'unrecognized observation member: {info.filename!r}')
        if relative in found:
            raise ValueError(f'duplicate observation member: {relative}')
        if info.file_size > OBSERVATION_MAX_BYTES:
            raise ValueError(f'observation file exceeds size limit: {relative}')
        total += info.file_size
        if total > OBSERVATIONS_TOTAL_MAX_BYTES:
            raise ValueError('official observations exceed the total extraction size limit')
        found[relative] = info
    if set(found) != EXPECTED_FILES:
        missing = ', '.join(sorted(EXPECTED_FILES - set(found)))
        raise ValueError(f'official archive is missing required observation files: {missing}')
    return found


def install_ravn_observation_example(reference_root, *, timeout: float = 45.0) -> dict:
    """Download and safely extract the official observations under a chosen folder.

    Existing destination folders are never overwritten. Failure removes all
    staging data, leaving the user's reference root unchanged.
    """
    root_input = Path(reference_root).expanduser()
    if root_input.is_symlink():
        raise ValueError('reference root cannot be a symlink')
    root_input.mkdir(parents=True, exist_ok=True)
    root = root_input.resolve(strict=True)
    if not root.is_dir():
        raise ValueError('reference root must be a directory')
    target = root / TARGET_NAME
    if target.exists() or target.is_symlink():
        raise FileExistsError(f'reference folder already exists: {target}')

    archive_fd, archive_name = tempfile.mkstemp(prefix='.ravn-workshop-', suffix='.zip')
    os.close(archive_fd)
    archive_path = Path(archive_name)
    staging = Path(tempfile.mkdtemp(prefix='.ravn-observations-', dir=root))
    committed = False
    try:
        _download_archive(archive_path, timeout)
        archive_sha = _sha256(archive_path)
        if archive_sha != ARCHIVE_SHA256:
            raise ValueError('official archive SHA-256 did not match the verified source hash')
        observations = {}
        with zipfile.ZipFile(archive_path, 'r') as archive:
            observations = _observation_members(archive)
            extracted = {}
            for name in sorted(observations):
                info = observations[name]
                content = archive.read(info)
                if len(content) != info.file_size or len(content) > OBSERVATION_MAX_BYTES:
                    raise ValueError(f'observation member size mismatch: {name}')
                output = staging / name
                # Exclusive creation prevents accidental overwrite even if a
                # future change adds a colliding member after validation.
                with output.open('xb') as stream:
                    stream.write(content)
                    stream.flush()
                    os.fsync(stream.fileno())
                extracted[name] = hashlib.sha256(content).hexdigest()

        provenance = {
            'format_version': 1,
            'title': 'Lake Ravn workshop observations',
            'source_url': ARCHIVE_URL,
            'archive_sha256': archive_sha,
            'downloaded_at_utc': datetime.now(timezone.utc).isoformat(),
            'files': extracted,
            'redistribution_license': 'not stated by source page',
            'limitations': [
                'Observation files are supplied by the official WET workshop archive.',
                'The source page does not state a data redistribution license.',
                'Lake Ravn observations do not establish station coordinates for another lake or a 3D grid cell.',
                'Variable units, aggregation meaning, and model representativeness require review before calibration.',
            ],
        }
        with (staging / 'provenance.json').open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(provenance, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        (staging / 'README.txt').write_text(
            'Lake Ravn workshop observation reference files\n'
            f'Source: {ARCHIVE_URL}\n'
            f'Archive SHA-256: {archive_sha}\n'
            'Only the eight OBSERVATIONS/*.obs files were extracted.\n'
            'The source page does not state a redistribution license.\n'
            'Review lake/station identity, units, variable definitions, and model representation before calibration.\n',
            encoding='utf-8', newline='\n')
        os.replace(staging, target)
        committed = True
        return {
            'name': TARGET_NAME,
            'path': str(target),
            'external': True,
            'kind': 'observation_reference',
            'archive_sha256': archive_sha,
            'files': sorted(extracted),
        }
    finally:
        archive_path.unlink(missing_ok=True)
        if not committed and staging.exists():
            shutil.rmtree(staging, ignore_errors=True)


def list_ravn_observation_examples(reference_root) -> list[dict]:
    """Return ready-to-browse user-managed Ravn observations in `/api/cases` shape."""
    root_input = Path(reference_root).expanduser()
    if root_input.is_symlink():
        return []
    root = root_input.resolve(strict=False)
    folder = root / TARGET_NAME
    if folder.is_symlink() or not folder.is_dir():
        return []
    provenance_path = folder / 'provenance.json'
    if provenance_path.is_symlink() or not provenance_path.is_file():
        return []
    try:
        provenance = json.loads(provenance_path.read_text(encoding='utf-8'))
        if (provenance.get('archive_sha256') != ARCHIVE_SHA256
                or provenance.get('source_url') != ARCHIVE_URL):
            return []
        for name in EXPECTED_FILES:
            candidate = folder / name
            if candidate.is_symlink() or not candidate.is_file():
                return []
            expected = provenance.get('files', {}).get(name)
            if not expected or _sha256(candidate) != expected:
                return []
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return []
    return [{
        'name': TARGET_NAME,
        'path': str(folder),
        'external': True,
        'kind': 'observation_reference',
    }]
