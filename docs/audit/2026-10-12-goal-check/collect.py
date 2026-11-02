"""Read-only requirement audit; capture fresh tests and bounded evidence."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent

def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8-sig'))

def digest(path):
    with path.open('rb') as stream:
        h = hashlib.sha256()
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

def main():
    result = subprocess.run([sys.executable, '-m', 'pytest', '3DWET/tests', 'tests', '-q', '-ra'],
                            cwd=ROOT, capture_output=True, encoding='utf-8', errors='replace')
    (OUT / 'python-tests.txt').write_text(result.stdout + result.stderr, encoding='utf-8')
    print('Python:', result.returncode, result.stdout.strip().splitlines()[-1], flush=True)
    node = shutil.which('node')
    front = []
    for path in sorted((ROOT / '3DWET/tests').glob('test_*.js')):
        run = subprocess.run([node, str(path)], cwd=ROOT, capture_output=True,
                             encoding='utf-8', errors='replace')
        front.append(dict(file=path.relative_to(ROOT).as_posix(), exit_code=run.returncode,
                          stdout=run.stdout, stderr=run.stderr))
    save('javascript-tests.json', front)
    print('JavaScript:', len(front), 'groups;', sum(x['exit_code'] != 0 for x in front), 'failed', flush=True)
    evidence = dict(collected_utc=datetime.now(timezone.utc).isoformat(),
                    python_exit_code=result.returncode, javascript_groups=len(front),
                    javascript_failed=sum(x['exit_code'] != 0 for x in front), files={}, reports={})
    for name in ['.trae/documents/3DWET_GUI_完成方案.md', '.trae/documents/preprocess_redesign.md',
                 'docs/superpowers/plans/2026-10-11-repair-and-five-workflows.md',
                 '姚杨杰/GETM-FABM-WET_3DWET模型完整说明.docx',
                 'release/installer-manifest.json', 'release/3DWETStudio-Setup.exe',
                 '3DWET/bin/getm_cartesian.exe', 'build/native-restart-fix/getm_cartesian.exe',
                 'release/stage/3DWETStudio/3DWET/bin/getm_cartesian.exe',
                 '3DWET/app/static/js/i18n.js', '3DWET/app/static/js/app.js']:
        p = ROOT / name
        evidence['files'][name] = dict(exists=p.exists(), sha256=digest(p) if p.is_file() else None)
    evidence['installer_manifest'] = read('release/installer-manifest.json')
    for name in ['build/builtin-final-candidate-20261012-02/verification.json',
                 'build/external-language-20261012-05/verification.json',
                 'build/features-resize-20261012-04/verification.json',
                 'build/results-resize-20261012-04/verification.json']:
        d = read(name)
        small = {k: v for k, v in d.items() if not isinstance(v, (dict, list))}
        if 'cases' in d:
            small['cases'] = d['cases']
            small['case_results'] = [{k: row.get(k) for k in ('case', 'name', 'passed', 'error')
                                      if k in row} for row in d['results']]
        if 'features' in d:
            small['features'] = d['features']
        small['sha256'] = digest(ROOT / name)
        evidence['reports'][name] = small
    evidence['workflow_ledger'] = read('docs/audit/five-workflows/ledger.json')
    round_data = read('build/full-workflow-20261012-attempt01/round.json')
    evidence['active_round'] = {k: round_data.get(k) for k in ('status', 'seed', 'version', 'stages', 'error')}
    save('evidence.json', evidence)
    print('Evidence saved:', OUT, flush=True)
    return int(result.returncode != 0 or any(x['exit_code'] != 0 for x in front))

if __name__ == '__main__':
    raise SystemExit(main())
