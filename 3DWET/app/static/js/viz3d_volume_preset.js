// Reversible display preset for reading the derived 3D volume structure.
(function (root) {
    'use strict';
    const validModes = new Set(['continuous', 'orthogonal', 'triangles', 'hidden']);
    let restore = null;

    function control(id) {
        return root.document?.getElementById?.(id) || null;
    }

    function setPressed(button, pressed) {
        button.setAttribute('aria-pressed', String(pressed));
        button.classList?.toggle?.('active', pressed);
    }

    function finishOnManualEdit(button) {
        if (restore === null) return;
        restore = null;
        setPressed(button, false);
    }

    function toggle() {
        const button = control('viz3d-volume-preset');
        const mesh = control('viz3d-mesh-mode');
        const stack = control('viz3d-iso-stack');
        const layer = control('viz3d-iso-layer');
        if (!button || !mesh || !stack || !layer) return false;

        if (restore === null) {
            const previousMode = validModes.has(mesh.value) ? mesh.value : 'triangles';
            restore = { meshMode: previousMode, stack: stack.checked === true, layer: layer.value };
            mesh.value = 'triangles';
            stack.checked = true;
            layer.value = '-1';
        } else {
            mesh.value = restore.meshMode;
            stack.checked = restore.stack;
            layer.value = restore.layer;
            restore = null;
        }

        root.Viz3dMeshModePreference?.save?.(mesh.value);
        setPressed(button, restore !== null);
        root.updateViz3dIso?.();
        return true;
    }

    function bind() {
        const button = control('viz3d-volume-preset');
        const mesh = control('viz3d-mesh-mode');
        const stack = control('viz3d-iso-stack');
        const layer = control('viz3d-iso-layer');
        if (!button || !mesh || !stack || !layer) return false;
        if (button._viz3dVolumePresetBound) return true;
        button._viz3dVolumePresetBound = true;
        button.addEventListener('click', toggle);
        mesh.addEventListener('change', () => finishOnManualEdit(button));
        stack.addEventListener('change', () => finishOnManualEdit(button));
        layer.addEventListener('change', () => finishOnManualEdit(button));
        setPressed(button, false);
        return true;
    }

    root.Viz3dVolumePreset = { bind, toggle, active: () => restore !== null };
    if (root.document?.readyState === 'loading')
        root.document.addEventListener('DOMContentLoaded', bind, { once: true });
    else bind();
})(typeof window !== 'undefined' ? window : globalThis);
