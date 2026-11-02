"""3DWET 模型构建模块 - 从case_config.yaml组装完整case目录

Usage:
    python build_case.py <case_config.yaml> [--output-dir <dir>]

Inputs:
    case_config.yaml - case配置文件（参考templates/case_config.yaml）
    前处理生成的数据文件（bathymetry.nc, meteo.nc, rivers.nc, fabm_init.nc等）

Outputs (complete case directory):
    {case_name}/
    ├── getm.inp              # GETM主配置
    ├── getm_fabm.inp         # GETM-FABM耦合配置
    ├── fabm.yaml             # FABM生态模型配置
    ├── gotm_fabm.yaml        # GOTM-FABM激活配置
    ├── gotmturb.nml          # GOTM湍流配置
    ├── output.yaml           # 输出配置
    ├── bathymetry.nc         # (复制自data_dir)
    ├── meteo.nc
    ├── rivers.nc
    ├── fabm_init.nc
    ├── riverinfo.dat
    └── meteo_input.txt
"""
import os
import sys
import shutil
import argparse
from datetime import datetime


def load_config(config_path):
    import yaml
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


# Initial condition presets
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKFLOW_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, os.path.join(WORKFLOW_DIR, '3_init_conditions', 'presets'))
from trophic_states import PRESETS


# ============================================================
# Configuration file generators
# ============================================================
def gen_getm_inp(config, case_dir):
    """Generate getm.inp from configuration."""
    case = config['case']
    grid = config['grid']
    run = config['run']
    num = config['numerics']
    out = config['output']

    # Ensure float formatting (YAML may parse as int or float)
    timestep = float(run['timestep'])
    maxdepth = float(grid['maxdepth'])
    crit_depth = float(grid['crit_depth'])
    min_depth = float(grid['min_depth'])

    content = f"""! {case['name']} - GETM-FABM-WET configuration
! {case.get('description', '')}

&param
    dryrun       = .false.
    runid        = '{case['run_id']}'
    title        = '{case['name']} GETM-FABM-WET'
    parallel     = .false.
    runtype      = 4
    hotstart     = .false.
    use_epoch    = .false.
    save_initial = .false.
/

&time
    timestep     = {timestep}
    timefmt      = 2
    start        = '{case['start_date']}'
    stop         = '{case['end_date']}'
/

&domain
    vert_cord    = 1
    maxdepth = {maxdepth}
    bathy_format = 2
    bathymetry   = 'bathymetry.nc'
    f_plane      = .true.
    il = 1
    ih = {grid['nx']}
    jl = 1
    jh = {grid['ny']}
    crit_depth = {crit_depth}
    min_depth = {min_depth}
    kdum         = {grid['kdum']}
    z0_method    = 0
    z0_const     = 0.001
    check_cfl    = .false.
/

&meteo
    metforcing   = .true.
    on_grid      = .true.
    calc_met     = .true.
    met_method   = 2
    meteo_file   = 'meteo_input.txt'
    fwf_method   = {num['fwf_method']}
    tx           = 0.0
    ty           = 0.0
    swr_const    = -100.0
    shf_const    = 0.0
/

&rivers
    river_method = 1
/

&m2d
    elev_method = 1
    elev_const  = 0.0
    MM = 35
    vel2d_adv_split = 1
    vel2d_adv_hor   = 1
    Am          = 1.0
    An_method   = 0
    An_const    = 0.001
/

&m3d
    M = {grid['kdum']}
    cnpar = 1.0
    cord_relax = 0.0
    adv_ver_iterations = 1
    vel3d_adv_split = 1
    vel3d_adv_hor = 1
    vel3d_adv_ver = 1
    turb_adv_split = 1
    turb_adv_hor = 1
    turb_adv_ver = 1
    calc_temp = .true.
    calc_salt = .{('true' if num['calc_salt'] else 'false')}.
    avmback = 0.0
    avhback = 0.0
    ip_method = 1
    ip_ramp = -1
    vel_check = 0
    min_vel = 0.0
    max_vel = 0.0
    bdy3d = .false.
    bdyfmt_3d = 1
    bdy3d_ramp = 0
    bdyfile_3d = ' '
    bdy3d_tmrlx = .false.
    bdy3d_tmrlx_ucut = 0.0
    bdy3d_tmrlx_max = 0.0
    bdy3d_tmrlx_min = 0.0
/

&temp
    temp_method = 1
    temp_const = 12.0
    temp_adv_split = 1
    temp_adv_hor = 1
    temp_adv_ver = 1
    temp_AH = -1.0
    attenuation_method = 0
    A_const = 0.6
    g1_const = 0.5
    g2_const = 20.0
    swr_bot_refl_frac = 0.0
    swr_min_bot_frac = 0.0
    temp_check = 0
    min_temp = -2.0
    max_temp = 40.0
/

&eqstate
    eqstate_method = 1
    T0 = 15.0
    S0 = 0.0
    p0 = 0.0
    dtr0 = 0.0002
    dsr0 = 0.0008
/

&io_spec
    out_fmt = 2
    hotin_fmt = 2
    hotout_fmt = 2
    save_metrics = .false.
    save_masks = .false.
    save_2d = .true.
    save_3d = .true.
    save_vel = .true.
    destag = .false.
    save_strho = .true.
    save_s = .false.
    save_t = .true.
    save_rho = .false.
    save_rad = .false.
    save_turb = .true.
    save_tke = .true.
    save_eps = .true.
    save_num = .true.
    save_nuh = .true.
    save_ss_nn = .false.
    save_taub = .false.
    first_2d = 1
    step_2d = {out['freq_2d']}
    sync_2d = 1
    first_3d = 1
    step_3d = {out['freq_3d']}
    sync_3d = 1
    save_meteo = .false.
    save_numerical_analyses = .false.
/

&getm_fabm
    fabm_config = 'fabm.yaml'
    fabm = .true.
/
&diagnostics
    diagnostics = .false.
/
"""
    path = os.path.join(case_dir, 'getm.inp')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  Generated: getm.inp")


def gen_getm_fabm_inp(config, case_dir):
    """Generate getm_fabm.inp."""
    content = """&getm_fabm_nml
 fabm_init_method   =  2,
 fabm_init_file    =  'fabm_init.nc',
 fabm_init_format  =  2,
 fabm_field_no     =  1,
 fabm_adv_hor      =  4,
 fabm_adv_ver      =  4,
 fabm_adv_split    =  1,
 fabm_AH           = -1.,
/
"""
    path = os.path.join(case_dir, 'getm_fabm.inp')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  Generated: getm_fabm.inp")


def gen_gotm_fabm_yaml(config, case_dir):
    """Generate gotm_fabm.yaml."""
    num = config['numerics']
    ode_method = num['ode_method']
    repair = 'true' if num['repair_state'] else 'false'
    shade = 'true' if num['shade'] else 'false'

    content = f"""fabm:
  use: true
  freshwater_impact: true
  repair_state: {repair}
  feedbacks:
    shade: {shade}
    albedo: true
    surface_drag: true
  numerics:
    ode_method: {ode_method}
    split_factor: 1
    w_adv_discr: 6
    cnpar: 1.0
"""
    path = os.path.join(case_dir, 'gotm_fabm.yaml')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  Generated: gotm_fabm.yaml")


def gen_gotmturb_nml(config, case_dir):
    """Generate gotmturb.nml."""
    content = """&turbulence
   turb_method = 2
   tke_method = 1
   len_scale_method = 1
   stab_method = 1
/

&bc
   k_ubc = 1
   k_lbc = 1
   kb_ubc = 1
   kb_lbc = 1
   psi_ubc = 1
   psi_lbc = 1
   ubc_type = 1
   lbc_type = 1
/

&turb_param
   cm0_fix = 0.5477
   Prandtl0_fix = 0.74
   cw = 100.0
   compute_kappa = .true.
   kappa = 0.4
   compute_c3 = .true.
   ri_st = 0.25
   length_lim = .true.
   galp = 0.27
   const_num = 5.0e-4
   const_nuh = 5.0e-4
   k_min = 1.0e-8
   eps_min = 1.0e-12
   kb_min = 1.0e-8
   epsb_min = 1.0e-12
/

&generic
   compute_param = .false.
   gen_m = 1.5
   gen_n = -1.0
   gen_p = 3.0
   cpsi1 = 1.44
   cpsi2 = 1.92
   cpsi3minus = 0.0
   cpsi3plus = 1.0
   sig_kpsi = 1.0
   sig_psi = 1.3
   gen_d = -1.2
   gen_alpha = -2.0
   gen_l = 0.2
/

&keps
   ce1 = 1.44
   ce2 = 1.92
   ce3minus = 0.0
   ce3plus = 1.5
   sig_k = 1.0
   sig_e = 1.3
   sig_peps = .false.
/

&my
   e1 = 1.8
   e2 = 1.33
   e3 = 1.8
   sq = 0.2
   sl = 0.2
   my_length = 1
   new_constr = .false.
/

&scnd
   scnd_method = 0
   kb_method = 0
   epsb_method = 0
   scnd_coeff = 0
   cc1 = 0.0
   cc2 = 0.0
   cc3 = 0.0
   cc4 = 0.0
   cc5 = 0.0
   cc6 = 0.0
   ct1 = 0.0
   ct2 = 0.0
   ct3 = 0.0
   ct4 = 0.0
   ct5 = 0.0
   ctt = 0.0
/

&iw
   iw_model = 0
   alpha = 0.0
   klimiw = 1e-6
   rich_cr = 0.7
   numiw = 1.e-4
   nuhiw = 5.e-5
   numshear = 5.e-3
/
"""
    path = os.path.join(case_dir, 'gotmturb.nml')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  Generated: gotmturb.nml")


def gen_output_yaml(config, case_dir):
    """Generate output.yaml."""
    content = """output:
   time_unit: day
   time_step: 1
   sync_interval: 0
   variables:
      - source: *
"""
    path = os.path.join(case_dir, 'output.yaml')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  Generated: output.yaml")


def gen_fabm_yaml(config, case_dir):
    """Generate fabm.yaml by modifying the Yilong template with new initial conditions."""
    ic_config = config['initial_conditions']
    preset_name = ic_config.get('preset', 'eutrophic')

    if preset_name == 'custom':
        ic = ic_config['custom']
    else:
        ic = PRESETS.get(preset_name, PRESETS['eutrophic'])
    print(f"  Using initial condition preset: {preset_name}")

    # Load template from Yilong case (validated working version)
    template_path = os.path.join(os.path.dirname(WORKFLOW_DIR), 'case', 'Yilong', 'fabm.yaml')
    if not os.path.exists(template_path):
        # Fallback: try Theoretical lake
        template_path = os.path.join(os.path.dirname(WORKFLOW_DIR), 'case', 'Theoretical lake', 'fabm.yaml')

    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace initial conditions using string replacement
    replacements = [
        # Nutrients (abiotic_water)
        ('sNH4W: 0.30', f"sNH4W: {ic['sNH4W']}"),
        ('sNO3W: 1.0', f"sNO3W: {ic['sNO3W']}"),
        ('sPO4W: 0.06', f"sPO4W: {ic['sPO4W']}"),
        ('sO2W: 10.0', f"sO2W: {ic['sO2W']}"),
        ('sSiO2W: 3.5', f"sSiO2W: {ic['sSiO2W']}"),

        # Diatoms
        ('sDW: 0.30                                                  # water column DW (gDW/m3) - raised for Yilong (PCLake Turbid diatom ~0.3)',
         f"sDW: {ic['diatoms_sDW']}  # diatom initial (gDW/m3)"),
        # Greens
        ('sDW: 0.20                                                  # water column DW (gDW/m3) - raised for Yilong (PCLake green ~0.2)',
         f"sDW: {ic['greens_sDW']}  # green initial (gDW/m3)"),
        # Cyanobacteria
        ('sDW: 0.30                                                  # water column DW (gDW/m3) - raised for Yilong (eutrophic, blue-green dominant)',
         f"sDW: {ic['cyanobacteria_sDW']}  # cyanobacteria initial (gDW/m3)"),

        # Zooplankton (cladocerans and copepods both use sD: 0.30)
        ('sD: 0.30                                                   # DW (gDW/m3) - raised for Yilong (avoid zooplankton starvation)',
         f"sD: {ic['cladocerans_sD']}  # zooplankton initial (gDW/m3)"),

        # Fish
        ('sD: 0.15                                                   # DW (gDW/m3) - Yilong, lowered 50% to reduce predation pressure',
         f"sD: {ic['JuFish_sD']}  # juvenile fish initial (gDW/m3)"),
        ('sD: 0.40                                                   # DW (gDW/m3) - Yilong, lowered 50% to reduce predation pressure',
         f"sD: {ic['AdFish_sD']}  # adult fish initial (gDW/m3)"),
        ('sD: 0.05                                                   # DW (gDW/m3) - Yilong, lowered 50% to reduce predation pressure',
         f"sD: {ic['PiscFish_sD']}  # piscivorous fish initial (gDW/m3)"),

        # Zoobenthos
        ('sD: 0.40                                                   # DW (gDW/m2) - Yilong, moderate benthos',
         f"sD: {ic['zoobenthos_sD']}  # zoobenthos initial (gDW/m2)"),
    ]

    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
        else:
            # Try simpler pattern match
            pass

    path = os.path.join(case_dir, 'fabm.yaml')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  Generated: fabm.yaml (from template, preset={preset_name})")


# ============================================================
# Data file copier
# ============================================================
def copy_data_files(config, case_dir, config_path):
    """Copy data files from data_dir to case directory.

    Relative paths in data_dir are resolved against the config file's directory,
    not the current working directory. This makes configs portable.
    """
    data_cfg = config['data']
    config_dir = os.path.dirname(os.path.abspath(config_path))
    raw_dir = data_cfg['data_dir']
    if os.path.isabs(raw_dir):
        data_dir = raw_dir
    else:
        data_dir = os.path.join(config_dir, raw_dir)

    def _resolve(path):
        if os.path.isabs(path):
            return path
        return os.path.join(config_dir, path)

    # Individual file overrides
    files = {
        'bathymetry.nc': _resolve(data_cfg.get('bathymetry', os.path.join(data_dir, 'bathymetry.nc'))),
        'meteo.nc': _resolve(data_cfg.get('meteo', os.path.join(data_dir, 'meteo.nc'))),
        'rivers.nc': _resolve(data_cfg.get('rivers', os.path.join(data_dir, 'rivers.nc'))),
        'fabm_init.nc': _resolve(data_cfg.get('fabm_init', os.path.join(data_dir, 'fabm_init.nc'))),
        'riverinfo.dat': _resolve(data_cfg.get('riverinfo', os.path.join(data_dir, 'riverinfo.dat'))),
        'meteo_input.txt': _resolve(data_cfg.get('meteo_input', os.path.join(data_dir, 'meteo_input.txt'))),
    }

    for dest_name, src_path in files.items():
        if os.path.exists(src_path):
            shutil.copy2(src_path, os.path.join(case_dir, dest_name))
            print(f"  Copied: {dest_name} <- {src_path}")
        else:
            print(f"  WARNING: {dest_name} not found at {src_path}")


# ============================================================
# Main
# ============================================================
def main():
    parser = argparse.ArgumentParser(description='3DWET Case Build Module')
    parser.add_argument('config', help='Path to case_config.yaml')
    parser.add_argument('--output-dir', '-o', default=None,
                        help='Output directory (default: ./cases/{case_name})')
    args = parser.parse_args()

    config_path = os.path.abspath(args.config)
    if not os.path.exists(config_path):
        print(f"ERROR: Config file not found: {config_path}")
        sys.exit(1)

    config = load_config(config_path)
    case_name = config['case']['name']

    if args.output_dir:
        case_dir = os.path.abspath(args.output_dir)
    else:
        case_dir = os.path.join(os.path.dirname(config_path), 'cases', case_name)

    os.makedirs(case_dir, exist_ok=True)

    print("=" * 70)
    print(f"3DWET Case Build Module")
    print(f"Case: {case_name}")
    print(f"Config: {config_path}")
    print(f"Output: {case_dir}")
    print("=" * 70)

    # Generate configuration files
    print("\n[1/3] Generating configuration files ...")
    gen_getm_inp(config, case_dir)
    gen_getm_fabm_inp(config, case_dir)
    gen_gotm_fabm_yaml(config, case_dir)
    gen_gotmturb_nml(config, case_dir)
    gen_output_yaml(config, case_dir)
    gen_fabm_yaml(config, case_dir)

    # Copy data files
    print("\n[2/3] Copying data files ...")
    copy_data_files(config, case_dir, config_path)

    # Summary
    print("\n[3/3] Case directory summary ...")
    print(f"\n{'='*70}")
    print(f"Case build COMPLETE!")
    print(f"{'='*70}")
    print(f"\nCase directory: {case_dir}")
    print(f"\nFiles:")
    for f in sorted(os.listdir(case_dir)):
        path = os.path.join(case_dir, f)
        size = os.path.getsize(path)
        print(f"  {f:25s}  {size/1024:.1f} KB")

    print(f"\nNext step:")
    print(f"  python workflow/4_run/run_model.py {case_dir}")


if __name__ == '__main__':
    main()
