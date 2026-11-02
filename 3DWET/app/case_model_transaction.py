"""Lock-protected, recoverable case file transactions.

Windows cannot atomically replace several files as one filesystem operation.
This module stages candidates, writes a durable recovery journal, replaces files
under the caller's case lock, and restores their original bytes on failure or
the next case open after an interrupted prepared transaction.
"""
from __future__ import annotations

import hashlib
import json
import os
import uuid
from pathlib import Path


MANAGED_FILES = (
    'fabm.yaml', 'fabm_disabled.yaml', 'initial_conditions.json', 'output.yaml',
    'getm_fabm.inp', '.studio-config/wet_instances.json',
    '.studio-config/fabm_defaults.json', '.studio-hotstart.json',
)
TRANSACTION_ROOT = Path('.studio-config/transactions')


def case_revision(case: str | Path, names=MANAGED_FILES) -> str:
    case = Path(case)
    digest = hashlib.sha256()
    for name in sorted(names):
        path = case / name
        payload = path.read_bytes() if path.is_file() else None
        digest.update(name.encode('utf-8') + b'\0')
        digest.update(b'missing\0' if payload is None else b'present\0' + hashlib.sha256(payload).digest())
    return digest.hexdigest()


def _write_durable(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('wb') as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def _write_journal(path: Path, journal: dict) -> None:
    temp = path.with_suffix('.tmp')
    _write_durable(temp, json.dumps(journal, ensure_ascii=False, sort_keys=True).encode('utf-8'))
    os.replace(temp, path)


def recover_pending(case: str | Path) -> bool:
    """Roll back a prepared journal before the case is read; return if recovered."""
    case = Path(case)
    journal_path = case / TRANSACTION_ROOT / 'pending.json'
    if not journal_path.exists():
        return False
    journal = json.loads(journal_path.read_text(encoding='utf-8'))
    if journal.get('state') == 'committed':
        journal_path.unlink(missing_ok=True)
        return False
    backup = case / journal['backup']
    if not backup.resolve().is_relative_to(case.resolve()):
        raise ValueError('INVALID_JOURNAL: backup path escapes the case')
    for name in journal['files']:
        if Path(name).is_absolute() or '..' in Path(name).parts:
            raise ValueError(f'INVALID_JOURNAL: file path escapes the case: {name}')
        original = backup / name
        target = case / name
        if not target.resolve().is_relative_to(case.resolve()):
            raise ValueError(f'INVALID_JOURNAL: target escapes the case: {name}')
        if journal.get('exists', {}).get(name, original.is_file()):
            _write_durable(target, original.read_bytes())
        else:
            target.unlink(missing_ok=True)
    journal_path.unlink(missing_ok=True)
    return True


def commit_files(case: str | Path, candidates: dict[str, bytes | None], *,
                 operations=None, expected_revision: str | None = None,
                 revision_names=MANAGED_FILES, metadata=None) -> str:
    """Commit candidate bytes under the caller's case lock and return backup path."""
    case = Path(case)
    recover_pending(case)
    before_revision = case_revision(case, revision_names)
    if expected_revision is not None and before_revision != expected_revision:
        raise RuntimeError('STALE_REVISION')
    transaction_id = uuid.uuid4().hex
    backup_rel = Path('backups') / f'instances-{transaction_id}'
    backup = case / backup_rel
    backup.mkdir(parents=True)
    names = sorted(candidates)
    exists = {}
    before_hashes = {}
    after_hashes = {}
    for name in names:
        if Path(name).is_absolute() or '..' in Path(name).parts:
            raise ValueError(f'INVALID_PATH: {name}')
        target = case / name
        if not target.resolve().is_relative_to(case.resolve()):
            raise ValueError(f'INVALID_PATH: target escapes the case: {name}')
        exists[name] = target.is_file()
        if exists[name]:
            content = target.read_bytes()
            _write_durable(backup / name, content)
            before_hashes[name] = hashlib.sha256(content).hexdigest()
        else:
            before_hashes[name] = None
        candidate = candidates[name]
        after_hashes[name] = None if candidate is None else hashlib.sha256(candidate).hexdigest()
    journal_path = case / TRANSACTION_ROOT / 'pending.json'
    journal = {'version': 1, 'state': 'prepared', 'backup': backup_rel.as_posix(), 'files': names,
               'exists': exists, 'before_hashes': before_hashes, 'after_hashes': after_hashes}
    _write_journal(journal_path, journal)
    staged = {}
    try:
        for name, payload in candidates.items():
            target = case / name
            if payload is None:
                continue
            temp = target.with_name(target.name + f'.{transaction_id}.new')
            _write_durable(temp, payload)
            staged[name] = temp
        for name, payload in candidates.items():
            target = case / name
            if payload is None:
                target.unlink(missing_ok=True)
            else:
                os.replace(staged[name], target)
        manifest = {'version': 1, 'id': transaction_id, 'state': 'committed',
                    'revision_before': before_revision, 'revision_after': case_revision(case, revision_names),
                    'before_hashes': before_hashes, 'after_hashes': after_hashes,
                    'operations': operations or [], 'metadata': metadata or {}}
        _write_durable(backup / 'transaction.json', json.dumps(manifest, ensure_ascii=False, indent=2).encode('utf-8'))
        journal['state'] = 'committed'
        _write_journal(journal_path, journal)
        try:
            journal_path.unlink(missing_ok=True)
        except OSError:
            # A committed journal is safe to clean on the next recovery pass.
            pass
        return str(backup)
    except Exception:
        for temp in staged.values():
            temp.unlink(missing_ok=True)
        # Roll back from the exact byte backups while still holding the caller lock.
        for name in names:
            target = case / name
            if exists[name]:
                _write_durable(target, (backup / name).read_bytes())
            else:
                target.unlink(missing_ok=True)
        journal_path.unlink(missing_ok=True)
        raise


def preview_hash(revision: str, operations, candidates: dict[str, bytes | None], solver_hash: str = '') -> str:
    digest = hashlib.sha256()
    digest.update(revision.encode('ascii'))
    digest.update(json.dumps(operations, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8'))
    for name in sorted(candidates):
        digest.update(name.encode('utf-8') + b'\0')
        payload = candidates[name]
        digest.update(b'missing\0' if payload is None else hashlib.sha256(payload).digest())
    digest.update(solver_hash.encode('utf-8'))
    return digest.hexdigest()
