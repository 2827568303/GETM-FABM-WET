"""Portable native solver environment and loader diagnostics.

DLL probing runs only in an empty temporary directory, never in a user's case.
"""
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

ESSENTIAL_DLLS = ('libgfortran-5.dll', 'libnetcdff-7.dll')
LOADER_ERRORS = {
    0xC0000135: '缺少模型 DLL 运行库；请修复安装或检查 bin/runtime 是否完整。',
    0xC000007B: '模型或 DLL 的位数不匹配，需要 Windows x64 版本。',
    0xC0000139: 'DLL 版本不兼容，无法找到所需函数；请修复安装。',
    0xC0000142: '模型 DLL 初始化失败；请检查系统组件和运行库。',
    0xC0000005: '模型发生非法内存访问，请检查案例配置和 model_run.log。',
}


def explain_exit_code(code):
    return LOADER_ERRORS.get(code & 0xFFFFFFFF, f'模型退出码 {code}，请查看 model_run.log。')


def log_has_solver_failure(log):
    """Recognize failures without treating 'NaN checks disabled' as an error."""
    return bool(re.search(
        r'(?im)^\s*STOP\s+[1-9]\d*\b|'
        r'^\s*Error:\s*state variable\s+\d+\s+is zero and has negative derivative!|'
          r'\b(?:fatal_error|FATAL GETM ERROR|FATAL ERROR|out-of-bound values encountered|'
        r'IEEE_INVALID(?:_FLAG)?|IEEE_DIVIDE_BY_ZERO(?:_FLAG)?|Floating invalid|forrtl:)'
        r'|\bNaN\s+(?:detected|found|at|in)\b|\b(?:is|contains)\s+NaN\b', log))


def solver_environment(exe_path, parent_env=None):
    exe_path = Path(exe_path).resolve()
    env = dict(os.environ if parent_env is None else parent_env)
    dirs = [exe_path.parent / 'runtime', exe_path.parent]
    legacy = os.environ.get('WET_TOOLCHAIN_BIN')
    if legacy:
        dirs.append(Path(legacy))
    env['PATH'] = os.pathsep.join(str(p) for p in dirs if p.is_dir()) + os.pathsep + env.get('PATH', '')
    env['GFORTRAN_UNBUFFERED_PRECONNECTED'] = 'y'
    env['GFORTRAN_UNBUFFERED_ALL'] = 'y'
    return env


def inspect_runtime(exe_path, probe=False):
    exe = Path(exe_path).resolve()
    folder = exe.parent / 'runtime'
    required = set(ESSENTIAL_DLLS)
    manifest_path = folder / 'runtime-sources.json'
    incompatible = []
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
            required.update(manifest.get('dlls', {}).keys())
            incompatible = manifest.get('missing_symbols', [])
        except (OSError, ValueError, AttributeError):
            return dict(ready=False, missing=['runtime-sources.json 无法读取'],
                        loader_verified=False, runtime_dir=str(folder), detail='运行库清单损坏，请修复安装。')
    missing = [name for name in sorted(required)
               if Path(name).name != name or not (folder / name).is_file()]
    if not exe.is_file():
        missing.insert(0, exe.name)
    ready = not missing and not incompatible
    result = dict(ready=ready, missing=missing, loader_verified=False,
                  runtime_dir=str(folder), detail='运行库文件完整；尚未执行加载检查。' if ready
                  else '运行库缺失或版本不兼容，请重新安装完整安装包。')
    if probe and ready:
        try:
            with tempfile.TemporaryDirectory(prefix='3dwet_loader_') as cwd:
                process = subprocess.run([str(exe)], cwd=cwd, env=solver_environment(exe),
                    stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                    timeout=15, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            code = process.returncode & 0xFFFFFFFF
            # Without getm.inp GETM exits with its own Fortran configuration error.
            # This demonstrates loading and entry, not a scientific simulation.
            text = process.stderr.decode('utf-8', errors='replace')
            verified = code < 256 and 'getm.inp' in text
            result.update(ready=verified, loader_verified=verified, probe_exit_code=process.returncode,
                          detail='求解器及其 DLL 已成功加载。' if verified else explain_exit_code(process.returncode))
        except subprocess.TimeoutExpired:
            result.update(ready=False, detail='求解器加载检查超时，未启动计算。')
        except OSError as error:
            result.update(ready=False, detail=f'无法加载求解器：{error}')
    return result
