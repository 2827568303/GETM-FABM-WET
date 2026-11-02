"""Relink the checked-in native build after compiling coordinate bounds fixes.

Uses a portable toolchain prepared by prepare_native_toolchain.py. Outputs a
candidate under build/native-pressure-fix; does not replace the shipped solver.
"""
import hashlib
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
from output_paths import output_path, require_outside_c

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--restart',action='store_true',help='Also compile restart state persistence into an isolated candidate')
    parser.add_argument('--target',type=Path,help='Isolated output directory; never replaces the shipped solver')
    args=parser.parse_args()
    model = ROOT / '3DWET'
    build = model / 'build-win/getm'
    default_target = output_path('build', 'native-restart-fix' if args.restart else 'native-pressure-fix')
    target = require_outside_c(args.target or default_target, '--target')
    if target == (model / 'bin').resolve():
        raise ValueError('Build into an isolated candidate directory')
    target.mkdir(parents=True, exist_ok=True)
    tools = output_path('build', 'native-toolchain', 'ucrt64', 'bin')
    env = dict(os.environ, PATH=str(tools) + os.pathsep + os.environ['PATH'])
    includes = [target, build, model / 'src/getm/include', model / 'src/getm/src/3d',
                tools.parent / 'include',
                build / 'gotm/modules', model / 'install-win/fabm/include',
                build / 'gotm/extern/flexout/src/modules',
                build / 'gotm/extern/flexout/extern/yaml/modules']
    flags = ['-O2', '-U_GOTM_FABM_NML_', '-ffree-line-length-none', '-O3']
    defines = ['-DCARTESIAN', '-DFORTRAN95', '-DGFORTRAN', '-DNETCDF_FMT',
               '-DREAL_4B=real(4)', '-D_FABM_', '-D_NEW_GOTM_', '-D_OLD_FABM_']
    objects = target / 'objects.a'
    shutil.copy2(build / 'CMakeFiles/getm_exe.dir/objects.a', objects)
    commands = []
    fabm_library = target / 'libfabm.a'
    shutil.copy2(model / 'install-win/fabm/lib/libfabm.a', fabm_library)
    fish_includes = [target, model / 'src/fabm/src/drivers/gotm',
                     model / 'src/fabm/include', model / 'build-win/fabm/modules',
                     model / 'build-win/fabm/models/wet', model / 'install-win/fabm/include']
    core_object=target/'fabm.F90.obj'
    command=[str(tools/'gfortran.exe'),*flags,*(f'-I{p}' for p in fish_includes),'-c',
             str(model/'src/fabm/src/fabm.F90'),'-o',str(core_object)]
    subprocess.run(command,cwd=target,env=env,check=True)
    subprocess.run([str(tools/'ar.exe'),'r',str(fabm_library),str(core_object)],env=env,check=True)
    commands.append(command)
    sources=['3d/sigma_coordinates','3d/general_coordinates','3d/getm_fabm']
    if args.restart:
        sources=['2d/variables_2d','meteo/meteo',*sources,'2d/m2d','2d/momentum','output/output','getm/initialise',
                 'ncdf/create_restart_ncdf','ncdf/write_restart_ncdf','ncdf/read_restart_ncdf']
    for source in sources:
        name=source.split('/')[-1]
        obj = target / f'{name}.F90.obj'
        command = [str(tools / 'gfortran.exe'), *flags, *defines,
                   *(f'-I{p}' for p in includes), '-c',
                   str(model / f'src/getm/src/{source}.F90'), '-o', str(obj)]
        subprocess.run(command, cwd=target, env=env, check=True)
        subprocess.run([str(tools / 'ar.exe'), 'r', str(objects), str(obj)], env=env, check=True)
        commands.append(command)
    # Compile current WET sources and factory explicitly; duplicate archive
    # names such as phytoplankton.F90.obj also belong to other model families.
    wet_sources=['utility',*[p.stem for p in sorted((model/'src/wet/src').glob('*.F90'))
                            if p.stem not in ('utility','wet_model_library','resus_sed')],'wet_model_library']
    wet_objects=[]
    for name in wet_sources:
        obj=target/f'wet_{name}.F90.obj'
        command = [str(tools / 'gfortran.exe'), *flags,
                   *(f'-I{p}' for p in fish_includes), '-c',
                   str(model / f'src/wet/src/{name}.F90'), '-o', str(obj)]
        subprocess.run(command, cwd=target, env=env, check=True)
        commands.append(command);wet_objects.append(obj)
    # Rebuild the GOTM/FABM driver privately: bottom processes must consume
    # current-column interior diagnostics, including during restart.
    gotm_library = target / 'libgotm_fabm.a'
    shutil.copy2(build / 'gotm/fabm/libgotm_fabm.a', gotm_library)
    gotm_object = target / 'gotm_fabm.F90.obj'
    gotm_includes = [*includes, model / 'src/gotm/include']
    command = [str(tools / 'gfortran.exe'), *flags,
               *(define for define in defines if define != '-D_OLD_FABM_'),
               *(f'-I{p}' for p in gotm_includes), '-c',
               str(model / 'src/gotm/src/fabm/gotm_fabm.F90'), '-o', str(gotm_object)]
    subprocess.run(command, cwd=target, env=env, check=True)
    subprocess.run([str(tools / 'ar.exe'), 'r', str(gotm_library), str(gotm_object)], env=env, check=True)
    commands.append(command)
    libs = [build / p for p in ('gotm/turbulence/libturbulence.a', 'gotm/util/libutil.a',
            'gotm/extern/flexout/src/liboutput_manager.a')]
    libs += [gotm_library]
    libs += [model / 'bin/runtime/libnetcdff-7.dll', model / 'bin/runtime/libnetcdf.dll']
    libs += [build / p for p in ('gotm/util/libutil.a', 'gotm/extern/flexout/extern/yaml/libyaml.a',
            'gotm/extern/flexout/src/libfield_manager.a')]
    libs += [fabm_library]
    exe = target / 'getm_cartesian.exe'
    subprocess.run([str(tools / 'gfortran.exe'), *flags, '-Wl,--whole-archive', str(objects),
                    '-Wl,--no-whole-archive', '-o', str(exe), *(str(p) for p in wet_objects), *(str(p) for p in libs)],
                   cwd=target, env=env, check=True)
    report = {'exe': str(exe), 'sha256': hashlib.sha256(exe.read_bytes()).hexdigest(),
              'sources': ['fabm/src/fabm.F90']+[f'{s}.F90' for s in sources]+[f'wet/src/{s}.F90' for s in wet_sources]+['gotm/src/fabm/gotm_fabm.F90'], 'compile': commands,
              'fish_source_sha256': hashlib.sha256((model/'src/wet/src/fish.F90').read_bytes()).hexdigest()}
    (target / 'build.json').write_text(json.dumps(report, indent=2))
    print(json.dumps({'exe':str(exe),'sha256':report['sha256'],'build_report':str(target/'build.json')},indent=2))


if __name__ == '__main__':
    main()
