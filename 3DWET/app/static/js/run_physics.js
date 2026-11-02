/* Parse validated point diagnostics emitted by GETM into the run summary. */
(function attachRunPhysics(root) {
    'use strict';

    function parseGetmPhysicsDiagnostic(lines) {
        if (!Array.isArray(lines)) return null;
        const line = [...lines].reverse().find(value =>
            typeof value === 'string' && value.includes('GETM_PHYSICS_DIAG '));
        if (!line) return null;
        const tokens = line.trim().split(/\s+/).slice(1);
        const fields = {};
        for (let index = 0; index < tokens.length; index++) {
            const separator = tokens[index].indexOf('=');
            if (separator <= 0) continue;
            const key = tokens[index].slice(0, separator);
            let value = tokens[index].slice(separator + 1);
            if (!value && index + 1 < tokens.length && !tokens[index + 1].includes('=')) {
                value = tokens[++index];
            }
            if (value) fields[key] = value;
        }
        if (fields.status === 'unsupported') {
            return {status: 'unsupported', reason: fields.reason || 'not_validated'};
        }
        if (fields.status === 'unavailable') {
            return {status: 'unavailable', reason: fields.reason || 'unknown'};
        }
        if (fields.status !== 'available' || fields.kind !== 'center_wet_T') return null;

        const integerFields = ['completed_step', 'global_i', 'global_j'];
        const numericFields = ['z_surface_m', 'H_static_m', 'D_total_m'];
        const result = {
            status: fields.status,
            kind: fields.kind,
            sim_time: fields.sim_time,
        };
        for (const key of integerFields) {
            if (!/^\d+$/.test(fields[key] || '')) return null;
            result[key] = Number(fields[key]);
        }
        if (result.global_i < 1 || result.global_j < 1 ||
            !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/.test(result.sim_time || '')) return null;
        if (fields.owner_rank !== undefined) {
            if (!/^\d+$/.test(fields.owner_rank)) return null;
            result.owner_rank = Number(fields.owner_rank);
        }
        for (const key of numericFields) {
            const value = Number(fields[key]);
            if (!Number.isFinite(value)) return null;
            result[key] = value;
        }
        if (result.H_static_m <= 0 || result.D_total_m <= 0) return null;
        const depthTolerance = Math.max(1e-5, Math.abs(result.D_total_m) * 2e-6);
        if (Math.abs(result.D_total_m - (result.z_surface_m + result.H_static_m)) > depthTolerance) return null;
        if (fields.velocity_status === 'unavailable') {
            if (!fields.reason) return null;
            result.velocity_status = 'unavailable';
            result.velocity_reason = fields.reason;
        } else if (fields.velocity_status === 'available') {
            result.velocity_status = 'available';
            const layerIndices = ['surface_k', 'bottom_k'];
            for (const key of layerIndices) {
                if (!/^\d+$/.test(fields[key] || '')) return null;
                result[key] = Number(fields[key]);
                if (result[key] < 1) return null;
            }
            if (result.surface_k < result.bottom_k) return null;
            const velocityFields = [
                'u_surface_grid_m_s', 'v_surface_grid_m_s', 'speed_surface_m_s',
                'u_bottom_grid_m_s', 'v_bottom_grid_m_s', 'speed_bottom_m_s',
            ];
            for (const key of velocityFields) {
                const value = Number(fields[key]);
                if (!Number.isFinite(value)) return null;
                result[key] = value;
            }
            const surfaceSpeed = Math.hypot(result.u_surface_grid_m_s, result.v_surface_grid_m_s);
            const bottomSpeed = Math.hypot(result.u_bottom_grid_m_s, result.v_bottom_grid_m_s);
            const tolerance = (speed) => Math.max(1e-6, Math.abs(speed) * 2e-6);
            if (Math.abs(surfaceSpeed - result.speed_surface_m_s) > tolerance(result.speed_surface_m_s) ||
                Math.abs(bottomSpeed - result.speed_bottom_m_s) > tolerance(result.speed_bottom_m_s)) return null;
        } else if (fields.velocity_status !== undefined) {
            return null;
        }
        return result;
    }

    function updateRunPhysicsDiagnostic(status, previousState) {
        const identity = typeof status?.run_identity === 'string' && status.run_identity
            ? status.run_identity : null;
        const sameRun = identity !== null && previousState?.runIdentity === identity;
        let diagnostic = sameRun ? previousState.diagnostic : null;
        const mpi = String(status?.performance?.solver_mode || '').startsWith('MPI');
        let latest = validateApiDiagnostic(status?.physics_diagnostic, mpi);
        if (!latest) latest = parseGetmPhysicsDiagnostic(status?.logs || []);
        if (mpi && latest?.status === 'available' && !Number.isInteger(latest.owner_rank)) latest = null;
        if (latest) diagnostic = latest;
        if (identity === null) diagnostic = latest;
        return {runIdentity: identity, diagnostic};
    }

    function formatRunPhysicsPoint(diagnostic, {mpi = false, english = false} = {}) {
        if (!diagnostic || diagnostic.status !== 'available') return '—';
        const point = `T(${diagnostic.global_i}, ${diagnostic.global_j}) · ${diagnostic.sim_time} · step ${diagnostic.completed_step}`;
        if (!mpi) return point;
        return english
            ? `${point} · MPI rank 0 log · owner rank ${diagnostic.owner_rank}`
            : `${point} · MPI rank 0 日志 · 数据归属 rank ${diagnostic.owner_rank}`;
    }

    function renderRunPhysicsVelocity(diagnostic, elements, english = false) {
        const valueNames = [
            'surfaceLayer', 'surfaceX', 'surfaceY', 'surfaceSpeed',
            'bottomLayer', 'bottomX', 'bottomY', 'bottomSpeed',
        ];
        for (const name of valueNames) {
            if (elements[name]) elements[name].textContent = '—';
        }
        const waiting = english ? 'Waiting for velocity diagnostics.' : '等待速度诊断。';
        const unavailable = english ? 'Velocity unavailable.' : '速度暂不可用。';
        const reasons = {
            mpi_comm_mode_unverified: english
                ? 'Velocity is not validated for this MPI communication mode.'
                : '此 MPI 通信模式尚未验证速度诊断。',
            invalid_wet_velocity_face: english
                ? 'A surrounding velocity face is invalid; velocity is unavailable.'
                : '相邻速度面无效，当前速度不可用。',
            not_3d_update_step: english
                ? 'The 3D field was not updated at this step; velocity is unavailable.'
                : '当前步骤未更新三维场，速度暂不可用。',
            no_3d_runtime: english
                ? 'This run has no 3D velocity field.'
                : '本次运行未启用三维场，无法提供速度。',
            no_valid_3d_layer: english
                ? 'No valid 3D layer is available for velocity.'
                : '没有可用于速度诊断的三维层。',
        };
        if (!diagnostic || diagnostic.status !== 'available') {
            if (elements.status) elements.status.textContent = diagnostic?.status === 'unsupported'
                ? (english ? 'Velocity diagnostics are unsupported for this run.' : '此运行配置不支持速度诊断。')
                : waiting;
            return;
        }
        if (diagnostic.velocity_status === 'unavailable') {
            if (elements.status) elements.status.textContent = reasons[diagnostic.velocity_reason] || unavailable;
            return;
        }
        if (diagnostic.velocity_status !== 'available') {
            if (elements.status) elements.status.textContent = english
                ? 'This solver diagnostic does not include velocity values.'
                : '此求解器诊断记录未包含速度字段。';
            return;
        }
        const format = value => Number(value).toPrecision(6);
        const shown = [
            ['surfaceLayer', `k=${diagnostic.surface_k}`],
            ['surfaceX', format(diagnostic.u_surface_grid_m_s)],
            ['surfaceY', format(diagnostic.v_surface_grid_m_s)],
            ['surfaceSpeed', format(diagnostic.speed_surface_m_s)],
            ['bottomLayer', `k=${diagnostic.bottom_k}`],
            ['bottomX', format(diagnostic.u_bottom_grid_m_s)],
            ['bottomY', format(diagnostic.v_bottom_grid_m_s)],
            ['bottomSpeed', format(diagnostic.speed_bottom_m_s)],
        ];
        for (const [name, value] of shown) {
            if (elements[name]) elements[name].textContent = value;
        }
        if (elements.status) elements.status.textContent = english
            ? 'Local grid x/y components and resultant speed, all in m/s.'
            : '局部网格 x/y 分量与合速度，单位均为 m/s。';
    }

    function validateApiDiagnostic(value, mpi) {
        if (!value || typeof value !== 'object' || Array.isArray(value)) return null;
        if (mpi && value.source !== 'rank0_stderr') return null;
        if (!mpi && value.source !== 'solver_log') return null;
        if (value.status === 'unsupported' || value.status === 'unavailable') {
            return typeof value.reason === 'string' && value.reason
                ? {status: value.status, source: value.source, reason: value.reason,
                    ...(Number.isInteger(value.completed_step) ? {completed_step: value.completed_step} : {})}
                : null;
        }
        if (value.status !== 'available' || value.kind !== 'center_wet_T' ||
            !Number.isInteger(value.completed_step) || value.completed_step < 0 ||
            !Number.isInteger(value.global_i) || value.global_i < 1 ||
            !Number.isInteger(value.global_j) || value.global_j < 1 ||
            !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/.test(value.sim_time || '')) return null;
        if (mpi && !Number.isInteger(value.owner_rank)) return null;
        const numbers = ['z_surface_m', 'H_static_m', 'D_total_m'];
        if (numbers.some(key => !Number.isFinite(value[key])) ||
            value.H_static_m <= 0 || value.D_total_m <= 0) return null;
        const tolerance = Math.max(1e-5, Math.abs(value.D_total_m) * 2e-6);
        if (Math.abs(value.D_total_m - (value.z_surface_m + value.H_static_m)) > tolerance) return null;
        const result = Object.fromEntries(['status', 'source', 'kind', 'completed_step', 'sim_time',
            'global_i', 'global_j', ...(Number.isInteger(value.owner_rank) ? ['owner_rank'] : []), ...numbers]
            .map(key => [key, value[key]]));
        if (value.velocity_status === 'unavailable') {
            if (typeof value.velocity_reason !== 'string' || !value.velocity_reason) return null;
            result.velocity_status = 'unavailable';
            result.velocity_reason = value.velocity_reason;
        } else if (value.velocity_status === 'available') {
            if (!Number.isInteger(value.surface_k) || value.surface_k < 1 ||
                !Number.isInteger(value.bottom_k) || value.bottom_k < 1 || value.surface_k < value.bottom_k) return null;
            const velocityFields = [
                'u_surface_grid_m_s', 'v_surface_grid_m_s', 'speed_surface_m_s',
                'u_bottom_grid_m_s', 'v_bottom_grid_m_s', 'speed_bottom_m_s',
            ];
            if (velocityFields.some(key => !Number.isFinite(value[key]))) return null;
            const speedTolerance = speed => Math.max(1e-6, Math.abs(speed) * 2e-6);
            if (Math.abs(Math.hypot(value.u_surface_grid_m_s, value.v_surface_grid_m_s) - value.speed_surface_m_s) >
                    speedTolerance(value.speed_surface_m_s) ||
                Math.abs(Math.hypot(value.u_bottom_grid_m_s, value.v_bottom_grid_m_s) - value.speed_bottom_m_s) >
                    speedTolerance(value.speed_bottom_m_s)) return null;
            result.velocity_status = 'available';
            result.surface_k = value.surface_k;
            result.bottom_k = value.bottom_k;
            for (const key of velocityFields) result[key] = value[key];
        } else if (value.velocity_status !== undefined) {
            return null;
        }
        return result;
    }

    const api = {
        parseGetmPhysicsDiagnostic,
        updateRunPhysicsDiagnostic,
        formatRunPhysicsPoint,
        renderRunPhysicsVelocity,
    };
    root.RunPhysicsDiagnostics = api;
    if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : globalThis);
