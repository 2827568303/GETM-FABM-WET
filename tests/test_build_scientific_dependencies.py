"""Exercise the actual PyInstaller command, stopping before any build mutation."""
import importlib.util
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))


def test_abc_and_xlsx_dependencies_are_collected_not_excluded(monkeypatch, tmp_path):
    spec=importlib.util.spec_from_file_location('audit_build_app',ROOT/'scripts/build_app.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    commands=[]
    class Captured(Exception):pass
    def run(args,**kwargs):
        commands.append(args);raise Captured
    monkeypatch.setattr(module.subprocess,'run',run)
    try:module.main(['--output-root',str(tmp_path/'package')])
    except Captured:pass
    command=commands[0]
    excluded=[command[i+1] for i,v in enumerate(command[:-1]) if v=='--exclude-module']
    collected=[command[i+1] for i,v in enumerate(command[:-1]) if v=='--collect-all']
    assert 'matplotlib' not in excluded
    assert {'pyabc','openpyxl','sqlalchemy'} <= set(collected)


def test_build_can_target_a_fresh_directory_without_touching_release(monkeypatch, tmp_path):
    spec=importlib.util.spec_from_file_location('isolated_build_app',ROOT/'scripts/build_app.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    commands=[]
    class Captured(Exception):pass
    def run(args,**kwargs):
        commands.append(args)
        (output/'3DWETStudio').mkdir(parents=True,exist_ok=True)
        (output/'3DWETStudio'/'3DWETStudio.exe').write_bytes(b'fake frozen app')
        raise Captured
    monkeypatch.setattr(module.subprocess,'run',run)
    output=tmp_path/'new-package'
    release_executables={path.relative_to(ROOT/'release'):path.stat().st_size
                         for path in (ROOT/'release').rglob('3DWETStudio.exe')}
    try:module.main(['--output-root',str(output)])
    except Captured:pass
    command=commands[0]
    assert command[command.index('--distpath')+1] == str(output.resolve())
    assert command[command.index('--workpath')+1] == str(output.resolve()/'pyinstaller-work')
    assert command[command.index('--specpath')+1] == str(output.resolve())
    assert (output/'3DWETStudio').is_dir()
    assert release_executables == {path.relative_to(ROOT/'release'):path.stat().st_size
                                   for path in (ROOT/'release').rglob('3DWETStudio.exe')}


def test_build_refuses_to_replace_existing_package(monkeypatch, tmp_path):
    spec=importlib.util.spec_from_file_location('protected_build_app',ROOT/'scripts/build_app.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    output=tmp_path/'existing'; executable=output/'3DWETStudio'/'3DWETStudio.exe'
    executable.parent.mkdir(parents=True);executable.write_bytes(b'keep')
    try:
        module.main(['--output-root',str(output)])
    except SystemExit as error:
        assert error.code == 2
    else:
        raise AssertionError('existing package must be protected')
    assert executable.read_bytes() == b'keep'


def test_builtin_case_selection_uses_only_existing_canonical_source_cases(tmp_path):
    spec=importlib.util.spec_from_file_location('case_selection_build_app',ROOT/'scripts/build_app.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    case_root=tmp_path/'case'
    (case_root/'Lake Dianchi').mkdir(parents=True)
    (case_root/'_dc_rivertest').mkdir()

    selected=module.builtin_case_directories(case_root)

    assert [path.name for path in selected] == ['Lake Dianchi']
    assert all(path.is_dir() for path in selected)


def test_runtime_license_copy_is_optional_but_preserves_available_licenses(tmp_path):
    spec=importlib.util.spec_from_file_location('runtime_license_build_app',ROOT/'scripts/build_app.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    missing_source=tmp_path/'missing-runtime-licenses'
    missing_destination=tmp_path/'package'/'native-runtime'

    assert module.copy_optional_runtime_licenses(missing_source,missing_destination) is False
    assert not missing_destination.exists()

    source=tmp_path/'runtime'/'licenses'
    source.mkdir(parents=True)
    (source/'runtime-license.txt').write_text('license terms',encoding='utf-8')
    destination=tmp_path/'package'/'native-runtime'
    assert module.copy_optional_runtime_licenses(source,destination) is True
    assert (destination/'runtime-license.txt').read_text(encoding='utf-8') == 'license terms'


def test_desktop_and_web_shortcuts_use_the_same_launcher_and_project_root():
    desktop=(ROOT/'launch_desktop.cmd').read_text(encoding='utf-8')
    web=(ROOT/'launch_web.cmd').read_text(encoding='utf-8')
    assert 'cd /d "%~dp0"' in desktop and 'cd /d "%~dp0"' in web
    assert '3DWET\\app\\launcher.py' in desktop and '3DWET\\app\\launcher.py' in web
    assert '--desktop' in desktop and '--web' in web
