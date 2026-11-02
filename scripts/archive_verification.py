"""Preserve final verification evidence before removing disposable model copies."""
import hashlib
import json
from pathlib import Path
import shutil
from output_paths import output_path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_AUDIT = output_path('audit', '2026-10-11-evidence')
BUILD_ROOT = output_path('build')
MIGRATED_BUILD_ROOT = output_path('_migrated_from_c_20261027', 'build')
AUDIT = output_path('build', 'archived-verification-evidence-2026-10-11')
FINAL = ('final-packaged-all6-20261011', 'final-packaged-external-20261011',
         'final-packaged-features-20261011', 'final-installed-standalone-20261011-retry')
EXTRA = ('source-final-defaults-all5-20261010', 'external-alternative-inputs-20261010',
         'native-pressure-regression-20261010-3', 'source-all-five-20261010',
         'final-preview-20261011')


def main():
    for name in FINAL:
        report = json.loads((SOURCE_AUDIT/name/'verification.json').read_text(encoding='utf-8-sig'))
        if not report.get('passed'):
            raise RuntimeError('Incomplete final verification: '+name)
    AUDIT.mkdir(parents=True, exist_ok=True)
    receipts = []
    for name in FINAL + EXTRA:
        for filename in ('verification.json', 'verification.results.json', 'hydro-invariants.json'):
            source = SOURCE_AUDIT/name/filename
            if source.is_file():
                dest = AUDIT/name/filename
                dest.parent.mkdir(exist_ok=True)
                shutil.copy2(source, dest)
                receipts.append(dict(file=dest.relative_to(AUDIT).as_posix(),
                                     sha256=hashlib.sha256(dest.read_bytes()).hexdigest(), bytes=dest.stat().st_size))
    # Keep previous failures visible in a compact history; raw solver outputs
    # are disposable and are not required to establish the final pass.
    history = []
    for source_root in (BUILD_ROOT, MIGRATED_BUILD_ROOT):
        if not source_root.is_dir():
            continue
        for source in sorted(source_root.glob('*/verification.json')):
            report = json.loads(source.read_text(encoding='utf-8-sig'))
            history.append(dict(work=source.parent.name, passed=report.get('passed'),
                                error=report.get('error'), scope=report.get('scope'),
                                cases=[dict(case=r.get('case'), passed=r.get('passed'), error=r.get('error'))
                                       for r in report.get('results', [])]))
    (AUDIT/'historical-attempts.json').write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding='utf-8')
    (AUDIT/'checksums.json').write_text(json.dumps(receipts, indent=2), encoding='utf-8')
    print('Preserved', len(receipts), 'final evidence files;', len(history), 'historical attempts')


if __name__ == '__main__':
    main()
