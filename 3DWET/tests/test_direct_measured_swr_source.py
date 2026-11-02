from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
METEO = (ROOT / "3DWET/src/getm/src/meteo/meteo.F90").read_text(encoding="utf-8").lower()
NCDF_METEO = (ROOT / "3DWET/src/getm/src/ncdf/ncdf_meteo.F90").read_text(encoding="utf-8").lower()


def test_direct_measured_swr_is_opt_in_and_defaults_to_cloud_calculation():
    assert "logical, public                     :: use_measured_swr=.false." in METEO
    assert "use_measured_swr" in METEO.split("namelist /meteo/", 1)[1].split("!eop", 1)[0]
    assert "if (use_measured_swr) then" in METEO
    assert "short_wave_radiation(zenith_angle(i,j)" in METEO


def test_direct_swr_is_registered_and_interpolated_when_calc_met_is_enabled():
    calc_branch_start = NCDF_METEO.index("if (calc_met) then")
    direct_registration = NCDF_METEO.index("if (use_measured_swr) then", calc_branch_start)
    direct_branch_end = NCDF_METEO.index("name_thisvar = name_tausx", direct_registration)
    assert "nf90_inq_varid(ncid,name_swr,swr_id)" in NCDF_METEO[direct_registration:direct_branch_end]
    assert "nf90_get_var(ncid,swr_id,wrk,start,edges)" in NCDF_METEO
    assert "if (t_1 .lt. t_2) measured_swr_old = measured_swr" in NCDF_METEO
    assert "measured_swr_old(i,j) + t_frac*d_swr(i,j)" in METEO
    assert "measured_swr = wrk(1,1)" in NCDF_METEO
    assert "measured_swr(i,j) = wrk(i,j)" in NCDF_METEO
    assert "do_grid_interpol(az,wrk_dp,gridmap,ti,ui,measured_swr)" in NCDF_METEO


def test_direct_swr_rejects_nonfinite_or_negative_values():
    assert "ieee_is_finite" in NCDF_METEO
    assert "measured shortwave must be finite and nonnegative" in NCDF_METEO
    assert "units=\"w m-2\"" in NCDF_METEO


def test_direct_swr_mode_requires_calculated_flux_configuration():
    init_gate = METEO.split("if (use_measured_swr) then", 1)[1].split("LEVEL2 'Metforcing='", 1)[0]
    assert "if (.not. metforcing) then" in init_gate
    assert "if (met_method .ne. 2) then" in init_gate
    assert "if (.not. calc_met) then" in init_gate
    assert "use_measured_swr requires calc_met=.true." in METEO


def test_direct_swr_restart_is_rejected_during_meteo_initialization():
    source = (ROOT / "3DWET/src/getm/src/meteo/meteo.F90").read_text(encoding="utf-8")
    init = source.split("subroutine init_meteo(hotstart)", 1)[1].split("end subroutine init_meteo", 1)[0]
    assert "if (hotstart) then" in init
    assert "direct measured shortwave restart is not yet supported" in init
    assert init.index("direct measured shortwave restart is not yet supported") < init.index("allocate(measured_swr(E2DFIELD)")

