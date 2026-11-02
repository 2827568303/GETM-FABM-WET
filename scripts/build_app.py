"""Build the portable Windows application and its self-contained model tree."""
import importlib.metadata
import hashlib
import json
import re
import shutil
import subprocess
import sys
import zipfile
import argparse
import os
from pathlib import Path
from demo_defaults import configure_demo

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = Path(os.environ.get(
    'WET_OUTPUT_ROOT', r'D:\GETM-FABM-WET-outputs')).expanduser()
DEFAULT_STAGE = DEFAULT_OUTPUT_ROOT / 'release' / 'build' / 'stage' / '3DWETStudio'
APP = ROOT / '3DWET' / 'app'
BUILTIN_CASE_NAMES = ('Lake Dianchi', 'Lake Luoma', 'NativeTest', 'Theoretical lake')


def builtin_case_directories(case_root, fallback_root=None):
    """Return only allow-listed built-in cases, with an optional data mirror."""
    root = Path(case_root)
    fallback = Path(fallback_root) if fallback_root is not None else None
    cases = []
    for name in BUILTIN_CASE_NAMES:
        local = root / name
        mirrored = fallback / name if fallback is not None else None
        if local.is_dir():
            cases.append(local)
        elif mirrored is not None and mirrored.is_dir():
            cases.append(mirrored)
    return tuple(cases)


def copy_optional_runtime_licenses(source, destination):
    """Copy native runtime notices when supplied; some runtime bundles omit them."""
    source = Path(source)
    if not source.is_dir():
        return False
    shutil.copytree(source, destination, dirs_exist_ok=True)
    return True


def copy_mpi_payload(repo_root, model_root):
    """Stage the parallel solver, MS-MPI runtime, and shard merger together."""
    repo_root = Path(repo_root)
    model_root = Path(model_root)
    source_solver = repo_root / '3DWET/bin/getm_cartesian_parallel.exe'
    source_mpi = repo_root / '3DWET/bin/mpi'
    source_merger = repo_root / '3DWET/scripts/merge_getm_rank_outputs.py'
    required = (source_solver, source_mpi / 'mpiexec.exe', source_mpi / 'msmpi.dll',
                source_mpi / 'MS-MPI-LICENSE.txt', source_merger)
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError('MPI package payload is incomplete: ' + ', '.join(missing))
    bin_dir = model_root / 'bin'
    bin_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_solver, bin_dir / source_solver.name)
    shutil.copytree(source_mpi, bin_dir / 'mpi', dirs_exist_ok=True)
    scripts_dir = model_root / 'scripts'
    scripts_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_merger, scripts_dir / source_merger.name)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root', type=Path, default=DEFAULT_STAGE.parent,
                        help='new build directory; contains the stage/3DWETStudio payload')
    args = parser.parse_args([] if argv is None else argv)
    configured_root = os.environ.get('WET_OUTPUT_ROOT')
    if configured_root and Path(configured_root).expanduser().resolve().drive.upper() == 'C:':
        parser.error(f'WET_OUTPUT_ROOT must be outside C:; got {configured_root}')
    output_root = args.output_root.resolve()
    if output_root.drive.upper() == 'C:':
        parser.error(f'output-root must be outside C:; got {output_root}')
    stage = output_root / '3DWETStudio'
    if (stage / '3DWETStudio.exe').exists():
        parser.error(f'output already contains an application: {stage / "3DWETStudio.exe"}')
    stage.parent.mkdir(parents=True, exist_ok=True)
    known_defaults = {}
    case_mirror = DEFAULT_OUTPUT_ROOT / 'cases'
    for base in (ROOT / 'docs/audit/2026-10-10-original-defaults', DEFAULT_STAGE / '3DWET/case',
                 case_mirror):
        if base.exists():
            for case in base.iterdir():
                for name in ('getm.inp', 'output.yaml'):
                    path = case / name
                    if path.is_file():
                        known_defaults.setdefault((case.name, name), set()).add(
                            hashlib.sha256(path.read_bytes()).hexdigest())
    args = [sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean',
            '--onedir', '--windowed', '--name', '3DWETStudio',
            '--distpath', str(output_root), '--workpath', str(output_root / 'pyinstaller-work'),
            '--specpath', str(output_root), '--paths', str(APP)]
    args += ['--icon', str(APP / 'static/brand/3dwet.ico')]
    for name in ('templates', 'static', 'fabm_docs.json', 'fabm_glossary.json', 'variable_registry.json', 'pick_folder.ps1'):
        if (APP / name).exists():
            args += ['--add-data', f'{APP / name};{name if (APP / name).is_dir() else "."}']
    for name in ('webview', 'pythonnet', 'clr_loader', 'pyabc', 'openpyxl', 'sqlalchemy'):
        args += ['--collect-all', name]
    for name in ('server', 'calibration', 'grid_api', 'project_api', 'solver_runtime', 'mpi_runner', 'mpi_tuning',
                 'webview.platforms.winforms', 'webview.platforms.edgechromium', 'clr',
                 'tkinter', 'tkinter.filedialog'):
        args += ['--hidden-import', name]
    for name in ('pytest', 'PyInstaller', 'IPython', 'webview.platforms.android',
                 'webview.platforms.gtk', 'webview.platforms.qt', 'webview.platforms.cocoa'):
        args += ['--exclude-module', name]
    args += [str(APP / 'launcher.py')]
    subprocess.run(args, cwd=ROOT, check=True)
    shutil.copy2(APP / 'static/brand/3dwet.ico', stage / '3DWETStudio.ico')
    shutil.copy2(ROOT / 'docs/3DWET-Studio-使用说明.md', stage / '使用说明.md')
    shutil.copytree(ROOT / 'docs/studio-guide', stage / '使用指南', dirs_exist_ok=True)
    model = stage / '3DWET'
    (model / 'bin').mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / '3DWET/bin/getm_cartesian.exe', model / 'bin')
    shutil.copytree(ROOT / '3DWET/bin/runtime', model / 'bin/runtime', dirs_exist_ok=True)
    copy_mpi_payload(ROOT, model)
    shutil.copytree(ROOT / '3DWET/model_builder/templates', model / 'model_builder/templates', dirs_exist_ok=True)
    # Only canonical model inputs: never distribute user state or calculated outputs.
    # Keep this list in sync with the built-in cases exposed by the web UI.  The
    # source tree contains a few diagnostic/output-only folders; those are not
    # runnable cases and are intentionally excluded here.
    names = {
        'bathymetry.nc', 'fabm_init.nc', 'meteo.nc', 'rivers.nc',
        'riverinfo.dat', 'meteo_input.txt', 'initial_conditions.json',
        'lake_mask.txt', 'empty_stdin.txt',
    }
    source_cases = builtin_case_directories(ROOT / '3DWET/case', case_mirror)
    for source_case in source_cases:
        case = source_case.name
        dest = model / 'case' / case
        dest.mkdir(parents=True, exist_ok=True)
        for source in source_case.iterdir():
            if source.is_file() and (source.name in names or source.suffix.lower() in ('.inp', '.yaml', '.nml')):
                shutil.copy2(source, dest / source.name)
    # A short coupled sample validated on this native solver; source cases stay untouched.
    sample = model / 'case/NativeTest/getm.inp'
    text = sample.read_text(encoding='utf-8')
    for key, value in [('timestep', '2'), ('stop', "'2020-01-01 00:20:00'"),
                       ('step_2d', '300'), ('step_3d', '300'), ('sync_2d', '1'), ('sync_3d', '1')]:
        text = re.sub(r'(?m)^(\s*' + key + r'\s*=\s*)[^\r\n!]+', lambda m: m[1] + value, text)
    sample.write_text(text, encoding='utf-8')
    # Native GETM should also perform its own grid-aware barotropic CFL check.
    text = re.sub(r'(?im)^(\s*check_cfl\s*=\s*)\.false\.', r'\g<1>.true.', text)
    sample.write_text(text, encoding='utf-8')
    output = model / 'case/NativeTest/output.yaml'
    text = output.read_text(encoding='utf-8')
    text = re.sub(r'(?m)^(\s*time_unit:\s*).*$', r'\g<1>second', text)
    text = re.sub(r'(?m)^(\s*time_step:\s*).*$', r'\g<1>600', text)
    output.write_text(text, encoding='utf-8')
    # A new case name also delivers the optimized example on upgrades, which
    # deliberately preserve all existing user cases.
    demo = model / 'case/StudioDemo'
    demo.mkdir(parents=True, exist_ok=True)
    theoretical_case = next((path for path in source_cases if path.name == 'Theoretical lake'), None)
    if theoretical_case is None:
        raise FileNotFoundError('The allow-listed Theoretical lake sample case is missing.')
    for source in theoretical_case.iterdir():
        if source.is_file() and (source.name in names or source.suffix.lower() in ('.inp', '.yaml', '.nml')):
            shutil.copy2(source, demo / source.name)
    sample = demo / 'getm.inp'
    text = sample.read_text(encoding='utf-8')
    for key, value in [('timestep', '2'), ('stop', "'2020-01-01 00:20:00'"),
                       ('step_2d', '300'), ('step_3d', '300'), ('sync_2d', '1'),
                       ('sync_3d', '1'), ('save_3d', '.false.'), ('check_cfl', '.true.')]:
        text = re.sub(r'(?im)^(\s*' + key + r'\s*=\s*)[^\r\n!]+', lambda m: m[1] + value, text)
    sample.write_text(text, encoding='utf-8')
    # Keep every registered field in the compact output file so users can
    # choose any variable after the run; renderers read selected slices on demand.
    (demo / 'output.yaml').write_text('output:\n   time_unit: second\n   time_step: 600\n'
        '   sync_interval: 1\n   variables:\n      - source: *\n', encoding='utf-8')
    (demo / 'README.txt').write_text('StudioDemo：湖泊生态耦合教学示例\n'
        '包含水动力、营养盐、浮游生物、鱼类及碳/甲烷过程。\n'
        '2 秒步长，模拟 20 分钟；保存全部已注册变量，结果视图按需读取所选变量与切片。\n'
        '这是一份功能演示案例，不代表任何真实湖泊的率定结果。\n'
        '运行完成后到三维可视化查看湖岸、湖底和水体；先检查驱动覆盖再延长模拟。\n', encoding='utf-8-sig')
    for case in (model / 'case').iterdir():
        if case.is_dir() and (case / 'getm.inp').exists():
            configure_demo(case)
    # Upgrade only recognized factory configuration bytes. User-edited cases
    # retain their inputs; the installer also backs up each replaced default.
    upgrade_lines = []
    for (case_name, filename), hashes in sorted(known_defaults.items()):
        if (model / 'case' / case_name / filename).exists():
            upgrade_lines.append(
                'Source: "{#StageDir}\\3DWET\\case\\' + case_name + '\\' + filename +
                '"; DestDir: "{app}\\3DWET\\case\\' + case_name +
                '"; Flags: ignoreversion uninsneveruninstall; Check: InstallKnownDefault(\'' +
                case_name + '\', \'' + filename + '\', \'' + ','.join(sorted(hashes)) + '\')')
    (stage / 'case-updates.iss').write_text('\n'.join(upgrade_lines) + '\n', encoding='utf-8-sig')
    (model / 'app').mkdir(exist_ok=True)
    licenses = stage / 'THIRD_PARTY_LICENSES'
    licenses.mkdir(exist_ok=True)
    versions = {}
    for dist in importlib.metadata.distributions():
        name = dist.metadata.get('Name', 'unknown')
        if name.lower() in ('pip', 'setuptools', 'wheel', 'pytest', 'pyinstaller', 'pefile', 'zstandard'):
            continue
        versions[name] = dist.version
        for entry in dist.files or []:
            if any('license' in part.lower() or 'copying' in part.lower() for part in entry.parts):
                source = Path(dist.locate_file(entry))
                if source.is_file() and source.stat().st_size < 2_000_000:
                    dest = licenses / name / str(entry)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, dest)
    for project in ('getm', 'gotm', 'fabm', 'wet'):
        for source in (ROOT / '3DWET/src' / project).glob('*'):
            if source.is_file() and re.match(r'(?i)(license|copying|copyright)', source.name):
                dest = licenses / project / source.name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, dest)
    copy_optional_runtime_licenses(ROOT / '3DWET/bin/runtime/licenses', licenses / 'native-runtime')
    shutil.copy2(Path(sys.base_prefix) / 'LICENSE.txt', licenses / 'Python-LICENSE.txt')
    # Ship the corresponding local model sources and build recipes along with the executable.
    with zipfile.ZipFile(stage / 'MODEL_SOURCE.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        allowed = {'.f90', '.f', '.f95', '.h', '.c', '.cpp', '.cmake', '.py', '.sh', '.ps1', '.patch', '.md', '.txt', '.yaml'}
        for source in (ROOT / '3DWET/src').rglob('*'):
            if not source.is_file() or any(p in ('.git', 'build', '__pycache__', 'testcases') for p in source.parts):
                continue
            if source.suffix.lower() in allowed or source.name.lower().startswith(('makefile', 'license', 'copying')):
                archive.write(source, source.relative_to(ROOT))
        for source in (ROOT / '3DWET').glob('build*'):
            if source.is_file():
                archive.write(source, source.relative_to(ROOT))
        for name in ('rebuild_native_pressure_fix.py', 'prepare_native_toolchain.py',
                     'fetch_model_runtime.py', 'demo_defaults.py'):
            source = ROOT / 'scripts' / name
            archive.write(source, source.relative_to(ROOT))
        records = ROOT / 'build/native-toolchain-records.json'
        if records.is_file():
            archive.write(records, 'build/native-toolchain-records.json')
    notice = '''3DWET Studio 运行环境与依赖说明

支持 Windows 10 1607+ / Windows 11 x64，安装到当前用户目录。
安装包内置 Python 3.10、科学计算库、网页服务、桌面窗口组件、GETM/FABM/WET 求解器及原生运行库。
运行现有模型不需要另外安装 Python、Anaconda、GCC、MSYS2 或 WSL，也不修改系统 PATH。
Microsoft WebView2 x64 离线安装器随安装包附带：缺失时安装，已有时复用。
桌面窗口需要 Windows 自带 .NET Framework 4.6.2+，安装器会检查。
修改 Fortran 源码后重新编译需要额外的编译工具链；本安装包面向预编译模型运行。
NativeTest 是经过短时耦合计算验证的示例：时间步长 2 秒，模拟 20 分钟。
StudioDemo 保留鱼类与温室气体耦合，精简关键变量输出并复用 output.nc 三维场。
全部内置案例默认运行20分钟、步长2秒、每60秒输出；运行长时案例前检查驱动覆盖与数值稳定性。
安装包内置 Lake Dianchi、Lake Luoma、NativeTest、Theoretical lake 与 StudioDemo 案例，案例列表中可直接选择。
升级保留用户修改过的配置；识别为旧版出厂默认的配置会先备份再更新。卸载保留案例与用户输出。
第三方许可见 THIRD_PARTY_LICENSES；模型源码与构建配方见 MODEL_SOURCE.zip。
DLL 来源与校验见 3DWET/bin/runtime/runtime-sources.json。

打包环境组件版本：
'''
    (stage / 'DEPENDENCIES.txt').write_text(notice + json.dumps(versions, ensure_ascii=False, indent=2), encoding='utf-8-sig')
    print(f'Staged application: {stage}')


if __name__ == '__main__':
    main(sys.argv[1:])
