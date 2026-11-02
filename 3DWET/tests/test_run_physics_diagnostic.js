const assert = require('node:assert/strict');
const diagnosticModule = (() => {
    try { return require('../app/static/js/run_physics.js'); }
    catch (_) { return {}; }
})();

assert.equal(typeof diagnosticModule.parseGetmPhysicsDiagnostic, 'function',
    'run_physics.js must export a parser for structured GETM diagnostic log lines');

const parse = diagnosticModule.parseGetmPhysicsDiagnostic;
const line = 'GETM_PHYSICS_DIAG status=available kind=center_wet_T '
    + 'completed_step=100 sim_time=2001-02-03T04:05:06 global_i=12 global_j=8 '
    + 'owner_rank=1 z_surface_m=1.25 H_static_m=4.5 D_total_m=5.75 '
    + 'velocity_status=available surface_k=5 bottom_k=1 '
    + 'u_surface_grid_m_s=0.12 v_surface_grid_m_s=-0.16 speed_surface_m_s=0.2 '
    + 'u_bottom_grid_m_s=0.03 v_bottom_grid_m_s=0.04 speed_bottom_m_s=0.05';
assert.deepEqual(parse([line]), {
    status: 'available', kind: 'center_wet_T', completed_step: 100,
    sim_time: '2001-02-03T04:05:06', global_i: 12, global_j: 8, owner_rank: 1,
    z_surface_m: 1.25, H_static_m: 4.5, D_total_m: 5.75,
    velocity_status: 'available', surface_k: 5, bottom_k: 1,
    u_surface_grid_m_s: 0.12, v_surface_grid_m_s: -0.16, speed_surface_m_s: 0.2,
    u_bottom_grid_m_s: 0.03, v_bottom_grid_m_s: 0.04, speed_bottom_m_s: 0.05,
});
assert.deepEqual(parse([line.replace(/ velocity_status=available.*$/, '').replace('z_surface_m=1.25 H_static_m=4.5 D_total_m=5.75',
    'z_surface_m=     1.25E+000 H_static_m=     4.5E+000 D_total_m=     5.75E+000')]), {
    status: 'available', kind: 'center_wet_T', completed_step: 100,
    sim_time: '2001-02-03T04:05:06', global_i: 12, global_j: 8, owner_rank: 1,
    z_surface_m: 1.25, H_static_m: 4.5, D_total_m: 5.75,
});

assert.deepEqual(parse([
    'GETM_PHYSICS_DIAG status=unavailable reason=selected_cell_dry'
]), {status: 'unavailable', reason: 'selected_cell_dry'});
assert.equal(parse([line.replace('D_total_m=5.75', 'D_total_m=99')]), null,
    'inconsistent total depth must not be shown');
assert.equal(parse([line.replace('z_surface_m=1.25', 'z_surface_m=NaN')]), null,
    'non-finite values must not be shown');

assert.equal(typeof diagnosticModule.updateRunPhysicsDiagnostic, 'function',
    'run_physics.js must retain the latest diagnostic for one run identity');
const update = diagnosticModule.updateRunPhysicsDiagnostic;
const apiDiagnostic = {
    status: 'available', source: 'rank0_stderr', kind: 'center_wet_T', completed_step: 100,
    sim_time: '2001-02-03T04:05:06', global_i: 12, global_j: 8, owner_rank: 1,
    z_surface_m: 1.25, H_static_m: 4.5, D_total_m: 5.75,
    velocity_status: 'available', surface_k: 5, bottom_k: 1,
    u_surface_grid_m_s: 0.12, v_surface_grid_m_s: -0.16, speed_surface_m_s: 0.2,
    u_bottom_grid_m_s: 0.03, v_bottom_grid_m_s: 0.04, speed_bottom_m_s: 0.05,
};
const apiFirst = update({run_identity: 'api-run', performance: {solver_mode: 'MPI (2 ranks)'},
    physics_diagnostic: apiDiagnostic, logs: []}, null);
assert.deepEqual(apiFirst.diagnostic, apiDiagnostic,
    'a validated run-scoped API diagnostic is used without depending on the bounded log tail');
const apiRetained = update({run_identity: 'api-run', performance: {solver_mode: 'MPI (2 ranks)'},
    physics_diagnostic: null, logs: []}, apiFirst);
assert.deepEqual(apiRetained.diagnostic, apiDiagnostic,
    'the last API diagnostic remains visible while the same run has no newer record');
assert.equal(update({run_identity: 'api-invalid-source', performance: {solver_mode: 'MPI (2 ranks)'},
    physics_diagnostic: {...apiDiagnostic, source: 'rank1_stderr'}, logs: []}, null).diagnostic,
null, 'MPI diagnostics from non-rank-zero sources are rejected');
assert.equal(update({run_identity: 'api-invalid-owner', performance: {solver_mode: 'MPI (2 ranks)'},
    physics_diagnostic: {...apiDiagnostic, owner_rank: undefined}, logs: []}, null).diagnostic,
null, 'MPI diagnostics without owner rank are rejected');
assert.deepEqual(update({run_identity: 'api-run', performance: {solver_mode: 'MPI (2 ranks)'},
    physics_diagnostic: {status: 'unsupported', source: 'rank0_stderr', reason: 'mpi_file_decomp'}, logs: []}, apiFirst).diagnostic,
{status: 'unsupported', source: 'rank0_stderr', reason: 'mpi_file_decomp'},
'explicit unsupported API state is preserved');
assert.equal(update({run_identity: 'api-next', performance: {solver_mode: 'MPI (2 ranks)'},
    physics_diagnostic: null, logs: []}, apiFirst).diagnostic, null,
'a run identity change clears server-provided diagnostics');
const first = update({run_identity: 'run-a', logs: [line]}, null);
const truncatedTail = Array.from({length: 80}, (_, index) => `later log ${index}`);
const retained = update({run_identity: 'run-a', logs: truncatedTail}, first);
assert.equal(retained.diagnostic.completed_step, 100,
    'a tail without the old diagnostic retains the latest valid record for the same run');

const unavailable = update({run_identity: 'run-a', logs: [
    'GETM_PHYSICS_DIAG status=unavailable reason=selected_cell_dry',
]}, retained);
const retainedUnavailable = update({run_identity: 'run-a', logs: truncatedTail}, unavailable);
assert.deepEqual(retainedUnavailable.diagnostic,
    {status: 'unavailable', reason: 'selected_cell_dry'},
    'an unavailable status remains visible after its line leaves the tail');

const switched = update({run_identity: 'run-b', logs: []}, retainedUnavailable);
assert.equal(switched.diagnostic, null, 'a new run identity clears diagnostics from the old run');
const mpi = update({run_identity: 'run-c', performance: {solver_mode: 'MPI (2 ranks)'}, logs: [line]}, switched);
assert.deepEqual(mpi.diagnostic, {
    status: 'available', kind: 'center_wet_T', completed_step: 100,
    sim_time: '2001-02-03T04:05:06', global_i: 12, global_j: 8, owner_rank: 1,
    z_surface_m: 1.25, H_static_m: 4.5, D_total_m: 5.75,
    velocity_status: 'available', surface_k: 5, bottom_k: 1,
    u_surface_grid_m_s: 0.12, v_surface_grid_m_s: -0.16, speed_surface_m_s: 0.2,
    u_bottom_grid_m_s: 0.03, v_bottom_grid_m_s: 0.04, speed_bottom_m_s: 0.05,
}, 'a complete rank-zero point diagnostic is accepted for MPI');
const mpiMissingOwner = update({run_identity: 'run-c2', performance: {solver_mode: 'MPI (2 ranks)'}, logs: [
    line.replace('owner_rank=1 ', ''),
]}, switched);
assert.equal(mpiMissingOwner.diagnostic, null,
    'MPI ignores otherwise plausible diagnostic records without a rank owner');
const mpiTail = update({run_identity: 'run-c', performance: {solver_mode: 'MPI (2 ranks)'}, logs: []}, mpi);
assert.deepEqual(mpiTail.diagnostic, mpi.diagnostic,
    'the latest MPI point diagnostic is retained when its line leaves the API tail');
const mpiUnsupported = update({run_identity: 'run-d', performance: {solver_mode: 'MPI (2 ranks)'}, logs: [
    'GETM_PHYSICS_DIAG status=unsupported reason=mpi_hotstart_unverified',
]}, mpiTail);
assert.deepEqual(mpiUnsupported.diagnostic,
    {status: 'unsupported', reason: 'mpi_hotstart_unverified'},
    'an explicit unsupported solver record is preserved');
const oldMpi = update({run_identity: 'run-e', performance: {solver_mode: 'MPI (2 ranks)'}, logs: []}, mpiUnsupported);
assert.equal(oldMpi.diagnostic, null,
    'a run without a validated diagnostic does not inherit data from an older run');

assert.deepEqual(parse([
    line.replace(/velocity_status=available.*$/, 'velocity_status=unavailable reason=not_3d_update_step')
]).velocity_status, 'unavailable',
'a valid water diagnostic can explicitly report unavailable velocity at non-3D cadence');
assert.equal(parse([line.replace('speed_surface_m_s=0.2', 'speed_surface_m_s=0.8')]), null,
    'speed magnitudes must agree with their grid component values');
assert.equal(parse([line.replace('surface_k=5 bottom_k=1', 'surface_k=0 bottom_k=1')]), null,
    'surface and bottom layer indices must be positive');

const renderVelocity = diagnosticModule.renderRunPhysicsVelocity;
const formatPoint = diagnosticModule.formatRunPhysicsPoint;
assert.equal(typeof renderVelocity, 'function', 'run physics module exports an accessible velocity renderer');
assert.equal(typeof formatPoint, 'function', 'run physics module formats point identity including MPI ownership');
const velocityElementNames = [
    'status', 'surfaceLayer', 'surfaceX', 'surfaceY', 'surfaceSpeed',
    'bottomLayer', 'bottomX', 'bottomY', 'bottomSpeed',
];
const makeVelocityElements = () => Object.fromEntries(velocityElementNames.map(name => [name, {textContent: 'stale'}]));
const velocityElements = makeVelocityElements();
renderVelocity(mpi.diagnostic, velocityElements, false);
assert.equal(velocityElements.surfaceLayer.textContent, 'k=5');
assert.equal(velocityElements.surfaceX.textContent, '0.120000');
assert.equal(velocityElements.surfaceY.textContent, '-0.160000');
assert.equal(velocityElements.surfaceSpeed.textContent, '0.200000');
assert.equal(velocityElements.bottomLayer.textContent, 'k=1');
assert.equal(velocityElements.bottomX.textContent, '0.0300000');
assert.equal(velocityElements.bottomY.textContent, '0.0400000');
assert.equal(velocityElements.bottomSpeed.textContent, '0.0500000');
assert.match(velocityElements.status.textContent, /x\/y.*m\/s/,
    'the renderer states local-grid component semantics and units');
assert.match(formatPoint(mpi.diagnostic, {mpi: true}), /MPI rank 0 日志.*rank 1/,
    'MPI point identity distinguishes rank-zero log source from data owner');
assert.match(formatPoint(mpi.diagnostic, {mpi: true, english: true}), /MPI rank 0 log.*owner rank 1/,
    'MPI ownership is also explicit in English');

const unavailableDiagnostic = parse([
    line.replace(/velocity_status=available.*$/, 'velocity_status=unavailable reason=mpi_comm_mode_unverified'),
]);
renderVelocity(unavailableDiagnostic, velocityElements, false);
assert.match(velocityElements.status.textContent, /MPI.*尚未验证/);
assert.equal(velocityElements.surfaceX.textContent, '—', 'unavailable state clears prior values');
assert.equal(velocityElements.bottomSpeed.textContent, '—', 'unavailable state clears both layers');

const legacyDiagnostic = parse([line.replace(/ velocity_status=available.*$/, '')]);
renderVelocity(legacyDiagnostic, velocityElements, true);
assert.match(velocityElements.status.textContent, /does not include velocity/,
    'legacy water-only diagnostics are clearly distinguished from unavailable velocity');
assert.equal(velocityElements.surfaceY.textContent, '—');

renderVelocity(null, velocityElements, false);
assert.equal(velocityElements.status.textContent, '等待速度诊断。',
    'a new run with no diagnostic returns to waiting and does not retain old UI values');
assert.equal(velocityElements.bottomLayer.textContent, '—');

const fs = require('node:fs');
const html = fs.readFileSync(require('node:path').join(__dirname, '../app/templates/index.html'), 'utf8');
for (const id of [
    'run-physics-velocity-surface-x', 'run-physics-velocity-surface-y',
    'run-physics-velocity-surface-speed', 'run-physics-velocity-bottom-x',
    'run-physics-velocity-bottom-y', 'run-physics-velocity-bottom-speed',
    'run-physics-velocity-status',
]) assert.match(html, new RegExp(`id="${id}"`), `run page includes ${id}`);
assert.match(html, /role="status" aria-live="polite"[^>]*data-i18n="等待速度诊断。"/,
    'velocity availability updates are announced accessibly and translated');
