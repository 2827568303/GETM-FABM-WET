// Keep the user's 3D water mesh display choice across cases and page reloads.
(function (root) {
    'use strict';
    const storageKey = '3dwet.viz3d.mesh-mode.v2';
    const modes = new Set(['continuous', 'orthogonal', 'hexa', 'curvilinear', 'hidden']);

    function read(fallback = 'continuous') {
        const defaultMode = modes.has(fallback) && fallback !== 'triangles' ? fallback : 'continuous';
        try {
            const value = root.localStorage?.getItem(storageKey);
            return modes.has(value) ? value : defaultMode;
        } catch (_) {
            return defaultMode;
        }
    }

    function save(value) {
        if (!modes.has(value)) return false;
        try {
            root.localStorage?.setItem(storageKey, value);
            return true;
        } catch (_) {
            return false;
        }
    }

    function bind(select = root.document?.getElementById?.('viz3d-mesh-mode')) {
        if (!select) return false;
        select.value = read(select.value);
        select.addEventListener?.('change', () => save(select.value));
        return true;
    }

    root.Viz3dMeshModePreference = { bind, read, save };
    if (root.document?.readyState === 'loading')
        root.document.addEventListener('DOMContentLoaded', () => bind(), { once: true });
    else bind();
})(typeof window !== 'undefined' ? window : globalThis);
