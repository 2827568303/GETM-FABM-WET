"""Fetch a build-only portable UCRT64 Fortran toolchain with checked packages."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import argparse
import json
from pathlib import Path
import re
from output_paths import output_path
from fetch_model_runtime import ROOT, REPO, download, archive, safe_path


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--netcdf',action='store_true',help='Include NetCDF Fortran development modules for restart code')
    args=parser.parse_args()
    repo_records = ROOT / 'build/native-toolchain-records.json'
    records_path = repo_records if repo_records.is_file() else output_path('build', 'native-toolchain-records.json')
    records = json.loads(records_path.read_text())
    selected = {}
    pending = ['mingw-w64-ucrt-x86_64-gcc-fortran']
    if args.netcdf:pending.append('mingw-w64-ucrt-x86_64-netcdf-fortran')
    while pending:
        name = pending.pop()
        if name not in records:
            providers=[key for key,record in records.items()
                       if name in [re.split(r'[<>=]',value)[0] for value in record.get('PROVIDES',[])]]
            if len(providers)!=1:
                raise ValueError(f'Cannot resolve build dependency {name}: {providers}')
            name=providers[0]
        if name in selected:
            continue
        record = records[name]
        selected[name] = record
        pending.extend(re.split(r'[<>=]', dep)[0] for dep in record.get('DEPENDS', []))
    target = output_path('build', 'native-toolchain')
    cache = target / 'packages'
    cache.mkdir(parents=True, exist_ok=True)

    def fetch(record):
        filename = record['FILENAME'][0]
        dest = cache / filename
        data = dest.read_bytes() if dest.exists() else download(REPO + filename)
        if hashlib.sha256(data).hexdigest() != record['SHA256SUM'][0]:
            raise ValueError('Checksum mismatch: ' + filename)
        if not dest.exists():
            dest.write_bytes(data)
        with archive(data) as tar:
            for member in tar:
                path = safe_path(member.name)
                if member.isfile() and path.parts[0] == 'ucrt64':
                    output = target.joinpath(*path.parts)
                    output.parent.mkdir(parents=True, exist_ok=True)
                    output.write_bytes(tar.extractfile(member).read())
        print('Ready', filename, flush=True)
        return {'package': record['NAME'][0], 'url': REPO + filename,
                'sha256': record['SHA256SUM'][0]}

    with ThreadPoolExecutor(max_workers=4) as pool:
        manifest = list(pool.map(fetch, selected.values()))
    # MSYS2 uses archive symlinks for GCC's plugin. Materialize their targets
    # as regular copies so no administrator symlink privilege is required.
    for record in selected.values():
        with archive((cache / record['FILENAME'][0]).read_bytes()) as tar:
            for member in tar:
                path = safe_path(member.name)
                if (member.issym() or member.islnk()) and path.parts[0] == 'ucrt64':
                    output = target.joinpath(*path.parts)
                    source = ((output.parent if member.issym() else target) / member.linkname).resolve()
                    source.relative_to((target / 'ucrt64').resolve())
                    if source.is_file():
                        output.parent.mkdir(parents=True, exist_ok=True)
                        output.write_bytes(source.read_bytes())
    (target / 'sources.json').write_text(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
