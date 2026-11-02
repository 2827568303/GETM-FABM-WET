import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'3DWET/app'))
from run_metrics import IncrementalLogReader, RunMetrics, read_rank_zero_stderr

def test_timestamped_progress_survives_variable_log_flood():
    tracker=RunMetrics()
    tracker.start({'nsteps':600},now=10)
    tracker.observe('17:23:11.985 n=         100\nlen = 364',now=12)
    for _ in range(500):tracker.observe('variable diagnostics NaN checks disabled',now=13)
    assert tracker.snapshot('running',now=14)['current_step']==99
    assert tracker.snapshot('running',now=14)['progress'] > 0

def test_finished_elapsed_and_progress_do_not_reset():
    tracker=RunMetrics();tracker.start({'nsteps':600},now=10)
    tracker.observe('n = 500',now=13);tracker.finish(now=15)
    report=tracker.snapshot('completed',now=100)
    assert report['elapsed']==5
    assert report['current_step']==600 and report['progress']==100
    assert report['eta_seconds'] is None

def test_step_monotonic_and_no_meteo_dimension_false_positive():
    tracker=RunMetrics();tracker.start({'nsteps':600},now=10)
    tracker.observe('n = 300\nlen = 364\nvariable n = 500\nn = 100',now=12)
    assert tracker.snapshot('running',now=13)['current_step']==299

def test_no_active_run_returns_idle_zero_metrics():
    tracker=RunMetrics()
    assert tracker.snapshot('idle',now=10)['elapsed']==0

def test_physics_diagnostic_exposes_only_complete_surface_and_bottom_velocity():
    tracker=RunMetrics(); tracker.start({'nsteps':200},now=10)
    line=('GETM_PHYSICS_DIAG status=available kind=center_wet_T completed_step=100 '
          'sim_time=2001-02-03T04:05:06 global_i=12 global_j=8 owner_rank=1 '
          'z_surface_m=1.25 H_static_m=4.5 D_total_m=5.75 velocity_status=available '
          'surface_k=5 bottom_k=1 u_surface_grid_m_s=0.12 v_surface_grid_m_s=-0.16 '
          'speed_surface_m_s=0.2 u_bottom_grid_m_s=0.03 v_bottom_grid_m_s=0.04 '
          'speed_bottom_m_s=0.05')
    tracker.observe(line,now=11,source='solver_log')
    diagnostic=tracker.snapshot('running',now=12)['physics_diagnostic']
    assert diagnostic['velocity_status']=='available'
    assert (diagnostic['surface_k'],diagnostic['bottom_k'])==(5,1)
    assert diagnostic['u_surface_grid_m_s']==0.12
    assert diagnostic['v_surface_grid_m_s']==-0.16
    assert diagnostic['speed_surface_m_s']==0.2
    assert diagnostic['u_bottom_grid_m_s']==0.03
    assert diagnostic['v_bottom_grid_m_s']==0.04
    assert diagnostic['speed_bottom_m_s']==0.05

def test_non_3d_cadence_explicitly_marks_velocity_unavailable():
    tracker=RunMetrics(); tracker.start({'nsteps':200},now=10)
    line=('GETM_PHYSICS_DIAG status=available kind=center_wet_T completed_step=100 '
          'sim_time=2001-02-03T04:05:06 global_i=12 global_j=8 '
          'z_surface_m=1.25 H_static_m=4.5 D_total_m=5.75 '
          'velocity_status=unavailable reason=not_3d_update_step')
    tracker.observe(line,now=11)
    diagnostic=tracker.snapshot('running',now=12)['physics_diagnostic']
    assert diagnostic['velocity_status']=='unavailable'
    assert diagnostic['velocity_reason']=='not_3d_update_step'
    assert 'speed_surface_m_s' not in diagnostic

def test_unverified_mpi_communication_marks_only_velocity_unavailable():
    tracker=RunMetrics(); tracker.start({'nsteps':200},now=10)
    line=('GETM_PHYSICS_DIAG status=available kind=center_wet_T completed_step=100 '
          'sim_time=2001-02-03T04:05:06 global_i=12 global_j=8 owner_rank=1 '
          'z_surface_m=1.25 H_static_m=4.5 D_total_m=5.75 '
          'velocity_status=unavailable reason=mpi_comm_mode_unverified')
    tracker.observe(line,now=11,source='solver_log')
    diagnostic=tracker.snapshot('running',now=12)['physics_diagnostic']
    assert diagnostic['status']=='available'
    assert diagnostic['velocity_status']=='unavailable'
    assert diagnostic['velocity_reason']=='mpi_comm_mode_unverified'
    assert diagnostic['H_static_m']==4.5 and diagnostic['D_total_m']==5.75
    assert 'u_surface_grid_m_s' not in diagnostic


def test_rank_zero_reader_handles_delayed_file_partial_lines_and_final_tail(tmp_path):
    reader=IncrementalLogReader()
    tracker=RunMetrics(); tracker.start({'nsteps':1000},now=10)
    assert read_rank_zero_stderr(tmp_path,reader)==''
    assert reader.last_error is None

    log=tmp_path/'LAKE.0000.stderr'
    log.write_text('n = 100\nn = 1',encoding='utf-8')
    first=read_rank_zero_stderr(tmp_path,reader)
    tracker.observe(first,now=11)
    assert first.splitlines()==['n = 100']
    assert tracker.snapshot('running',now=12)['current_step']==99

    with log.open('a',encoding='utf-8') as stream:
        stream.write('50\nn = 200')
    second=read_rank_zero_stderr(tmp_path,reader)
    tracker.observe(second,now=13)
    assert second.splitlines()==['n = 150']
    final=read_rank_zero_stderr(tmp_path,reader,final=True)
    tracker.observe(final,now=14)
    assert final.strip()=='n = 200'
    assert tracker.snapshot('running',now=15)['current_step']==199

def test_rank_zero_reader_rewinds_after_truncate_or_rewrite(tmp_path):
    reader=IncrementalLogReader()
    log=tmp_path/'LAKE.0000.stderr'
    log.write_text('n = 100\nn = 200\n',encoding='utf-8')
    assert read_rank_zero_stderr(tmp_path,reader).splitlines()==['n = 100','n = 200']

    # Rewritten content is longer than the old cursor, so size-only checks are insufficient.
    log.write_text('n = 5\n'+('replacement diagnostics\n'*8)+'n = 25\n',encoding='utf-8')
    text=read_rank_zero_stderr(tmp_path,reader)
    assert text.splitlines()[0]=='n = 5'
    assert text.splitlines()[-1]=='n = 25'

def test_rank_zero_reader_reports_io_error_without_raising(tmp_path):
    reader=IncrementalLogReader()
    (tmp_path/'LAKE.0000.stderr').mkdir()
    assert read_rank_zero_stderr(tmp_path,reader)==''
    assert reader.last_error
