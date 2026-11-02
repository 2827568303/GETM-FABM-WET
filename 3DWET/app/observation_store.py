"""Case-scoped, atomic persistence for imported observations."""
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import secrets
import tempfile
import time
from decimal import Decimal

from observations import merge_observation_records, parse_observations


class ObservationStore:
    def __init__(self, root, preview_ttl_seconds=1800):
        self.root = Path(root).resolve()
        self.preview_ttl_seconds = int(preview_ttl_seconds)
        self.root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _case_id(case_id):
        text = str(case_id or '')
        if (text in {'.', '..'} or not text.strip() or len(text) > 150
                or any(ord(c) < 32 for c in text) or '/' in text or '\\' in text
                or ':' in text):
            raise ValueError('invalid case id')
        return text

    def _case_dir(self, case_id, create=False):
        raw = self.root / self._case_id(case_id)
        if raw.is_symlink():
            raise ValueError('case path escapes store root')
        case = raw.resolve()
        if not case.is_relative_to(self.root):
            raise ValueError('case symlink escapes store root')
        if create:
            raw.mkdir(parents=True, exist_ok=True)
        return case

    def _input_path(self, value):
        path = Path(value)
        resolved = path.resolve(strict=True)
        if not resolved.is_file():
            raise ValueError('selected input must be a file')
        return resolved

    def _calibration_dir(self, case_id, create=False):
        case = self._case_dir(case_id, create=create)
        raw = case / 'calibration'
        if raw.is_symlink() or not raw.resolve(strict=False).is_relative_to(self.root):
            raise ValueError('calibration path escapes store root')
        if create:
            raw.mkdir(parents=True, exist_ok=True)
        return raw

    def _key(self):
        path = self.root / '.observation-preview.key'
        if path.is_symlink():
            raise ValueError('preview key path is a symlink')
        if not path.exists():
            try:
                path.write_bytes(secrets.token_bytes(32))
            except FileExistsError:
                pass
        key = path.read_bytes()
        if len(key) != 32:
            raise ValueError('invalid preview signing key')
        return key

    @staticmethod
    def _canonical(payload):
        """Serialize JSON values with browser-compatible canonical numbers.

        Browsers parse JSON numbers as IEEE-754 numbers and JSON.stringify turns
        integral floats such as 1.0 into 1. Python's json.dumps preserves 1.0,
        so signing its output made an untouched preview fail after the browser
        round-trip. Use normalized plain-decimal JSON number tokens on both
        preview and apply while keeping them numeric (and therefore tamper
        detectable) in the signed document.
        """
        def number(value):
            if isinstance(value, bool):
                return 'true' if value else 'false'
            if isinstance(value, int):
                return str(value)
            decimal = Decimal(str(value))
            if not decimal.is_finite():
                raise ValueError('non-finite number in signed payload')
            if decimal.is_zero():
                return '0'
            text = format(decimal, 'f')
            if '.' in text:
                text = text.rstrip('0').rstrip('.')
            return text

        def encode(value):
            if value is None:
                return 'null'
            if isinstance(value, bool):
                return 'true' if value else 'false'
            if isinstance(value, (int, float)):
                return number(value)
            if isinstance(value, str):
                return json.dumps(value, ensure_ascii=False)
            if isinstance(value, list):
                return '[' + ','.join(encode(item) for item in value) + ']'
            if isinstance(value, dict):
                if not all(isinstance(key, str) for key in value):
                    raise TypeError('signed JSON object keys must be strings')
                entries = (json.dumps(key, ensure_ascii=False) + ':' + encode(value[key])
                           for key in sorted(value))
                return '{' + ','.join(entries) + '}'
            raise TypeError(f'unsupported signed JSON value: {type(value).__name__}')

        return encode(payload).encode('utf-8')

    def _sign(self, payload):
        return hmac.new(self._key(), self._canonical(payload), hashlib.sha256).hexdigest()

    def _atomic_write(self, target, payload):
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_symlink() or not target.resolve(strict=False).is_relative_to(self.root):
            raise ValueError('write path escapes store root')
        fd, name = tempfile.mkstemp(prefix='.observations-', suffix='.tmp', dir=target.parent)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as stream:
                json.dump(payload, stream, ensure_ascii=False, allow_nan=False, indent=2)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(name, target)
        finally:
            if os.path.exists(name):
                os.unlink(name)

    def _persist(self, case_id, data):
        directory = self._calibration_dir(case_id, create=True)
        target = directory / 'observations.json'
        if target.exists():
            previous = json.loads(target.read_text(encoding='utf-8'))
            self._atomic_write(directory / 'observations.previous.json', previous)
        self._atomic_write(target, data)

    def save(self, case_id, data):
        if not isinstance(data, dict) or not isinstance(data.get('records'), list):
            raise ValueError('invalid observation payload')
        # JSON serialization rejects NaN/Infinity before any mutation.
        json.dumps(data, allow_nan=False)
        self._persist(case_id, data)

    def load(self, case_id):
        directory = self._calibration_dir(case_id, create=False)
        target = directory / 'observations.json'
        if target.is_symlink() or not target.resolve(strict=False).is_relative_to(self.root):
            raise ValueError('observation path escapes store root')
        if not target.is_file():
            return {'records': [], 'diagnostics': [], 'version': 1}
        return json.loads(target.read_text(encoding='utf-8'))

    def preview(self, case_id, files, mappings=None):
        self._case_dir(case_id, create=False)
        entries = []
        for item in files:
            path = self._input_path(item)
            mapping = (mappings or {}).get(str(path), (mappings or {}).get(path.name, {}))
            result = parse_observations(path, mapping)
            entries.append({'path': str(path), 'sha256': result['source_sha256'],
                            'source_file': path.name, 'row_count': result['row_count'],
                            'mapping': mapping, 'mapping_sha256': hashlib.sha256(self._canonical(mapping)).hexdigest(),
                            'records': result['records'], 'diagnostics': result['diagnostics']})
        now = int(time.time())
        payload = {'version': 1, 'case_id': self._case_id(case_id),
                   'mapping_version': (mappings or {}).get('__version__'), 'files': entries,
                   'created_at': now, 'expires_at': now + self.preview_ttl_seconds}
        payload['preview_signature'] = self._sign(payload)
        return payload

    def apply(self, case_id, preview, mappings=None):
        if not isinstance(preview, dict) or preview.get('case_id') != self._case_id(case_id):
            raise ValueError('preview case mismatch')
        signed = {k: v for k, v in preview.items() if k != 'preview_signature'}
        expected_sig = self._sign(signed)
        if not hmac.compare_digest(str(preview.get('preview_signature', '')), expected_sig):
            raise ValueError('preview content or mapping was modified')
        if int(preview.get('expires_at', 0)) < int(time.time()):
            raise ValueError('preview expired')
        if mappings is not None:
            expected_version = mappings.get('__version__')
            mapping_mismatch = any(
                mappings.get(entry['path'], mappings.get(entry['source_file'], entry['mapping'])) != entry['mapping']
                for entry in preview.get('files', []))
            unexpected = {k for k in mappings if k != '__version__'} - {
                key for entry in preview.get('files', []) for key in (entry['path'], entry['source_file'])}
            if mapping_mismatch or unexpected or expected_version != preview.get('mapping_version'):
                raise ValueError('preview mapping changed')
        records, diagnostics, manifest = [], [], []
        for entry in preview.get('files', []):
            path = self._input_path(entry['path'])
            current = hashlib.sha256(path.read_bytes()).hexdigest()
            if current != entry.get('sha256'):
                raise ValueError('preview file changed')
            result = parse_observations(path, entry['mapping'])
            records.extend(result['records'])
            diagnostics.extend(result['diagnostics'])
            manifest.append({'source_file': path.name, 'source_path': str(path), 'sha256': current,
                             'mapping_sha256': entry['mapping_sha256'], 'row_count': result['row_count']})
        records, duplicate_diagnostics = merge_observation_records(records)
        diagnostics.extend(duplicate_diagnostics)
        payload = {'version': 1, 'case_id': self._case_id(case_id), 'records': records,
                   'diagnostics': diagnostics, 'manifest': manifest,
                   'mapping_version': preview.get('mapping_version')}
        json.dumps(payload, ensure_ascii=False, allow_nan=False)
        self._persist(case_id, payload)
        return payload

    def restore(self, case_id):
        directory = self._calibration_dir(case_id, create=False)
        backup = directory / 'observations.previous.json'
        if not backup.is_file():
            raise ValueError('no previous observation snapshot')
        payload = json.loads(backup.read_text(encoding='utf-8'))
        self._persist(case_id, payload)
        return payload
