/* Case-local results and explicit, reversible cleanup. No automatic deletion. */
(() => {
    'use strict';
    const tr = text => window.StudioI18n?.t(text) || text;
    const english = () => window.StudioI18n && !window.StudioI18n.locale().startsWith('zh');
    let current = null;
    let selected = new Set();
    let duplicatePaths = [];
    let pending = false;
    let generation = 0;
    const size = bytes => {
        const n = Number(bytes || 0);
        if (n < 1024) return n + ' B';
        const units = ['KB', 'MB', 'GB', 'TB'];
        const i = Math.min(Math.floor(Math.log(n) / Math.log(1024)) - 1, 3);
        return (n / Math.pow(1024, i + 1)).toFixed(1) + ' ' + units[i];
    };
    const node = (tag, text, className) => {
        const el = document.createElement(tag);
        if (text !== undefined) el.textContent = tr(text);
        if (className) el.className = className;
        return el;
    };
    function message(text, error = false) {
        if (typeof window.toast === 'function') window.toast(tr(text), error ? 'error' : 'success');
        const target = document.getElementById('result-files-message');
        if (target) { target.textContent = tr(text); target.style.color = error ? 'var(--danger, #b42318)' : ''; }
    }
    async function request(url, body) {
        const response = await fetch(url, body === undefined ? {} : {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
        });
        const data = await response.json();
        if (!response.ok || data.error) throw new Error(data.error || '操作失败');
        return data;
    }
    async function copy(value) {
        try {
            if (navigator.clipboard && window.isSecureContext) await navigator.clipboard.writeText(value);
            else {
                const field = node('textarea');
                field.value = value;
                field.style.position = 'fixed'; field.style.opacity = '0';
                document.body.appendChild(field); field.select();
                const done = document.execCommand('copy'); field.remove();
                if (!done) throw new Error('请手动选中路径复制');
            }
            message('已复制完整路径');
        } catch (error) { message(error.message, true); }
    }
    function button(label, action, disabled = false) {
        const el = node('button', label, 'btn btn-secondary btn-sm');
        el.type = 'button'; el.disabled = disabled;
        el.addEventListener('click', action);
        return el;
    }
    function render() {
        const host = document.getElementById('result-files-panel');
        if (!host || !current) return;
        host.replaceChildren();
        host.classList.add('card');
        host.appendChild(node('h3', '结果文件与磁盘清理'));
        const paths = node('div'); paths.style.cssText = 'overflow-wrap:anywhere;line-height:1.8;margin-bottom:10px';
        paths.appendChild(node('div', '当前案例：' + current.case_path));
        paths.appendChild(node('div', '运行写入目录：' + current.run_output_path));
        paths.appendChild(node('div', '完成后归档目录：' + current.output_path));
        paths.appendChild(node('div', '运行中结果写入案例根目录；成功完成后归档至 output，表格列出当前实际位置。'));
        host.appendChild(paths);
        const actions = node('div'); actions.style.cssText = 'display:flex;flex-wrap:wrap;gap:8px;margin-bottom:10px';
        actions.appendChild(button('打开输出目录', async () => {
            try { await request('/api/system/explore', { path: current.output_path }); }
            catch (error) { message(error.message, true); }
        }));
        actions.appendChild(button('打开运行目录', async () => {
            try { await request('/api/system/explore', { path: current.run_output_path }); }
            catch (error) { message(error.message, true); }
        }));
        actions.appendChild(button('复制输出目录', () => copy(current.output_path)));
        actions.appendChild(button('刷新文件', () => window.loadResultFiles(), pending));
        actions.appendChild(button('扫描完全相同的副本', () => act('duplicates', { revision: current.revision }), pending || current.busy));
        actions.appendChild(button('选中重复副本', () => { selected = new Set(duplicatePaths); render(); }, pending || current.busy || !duplicatePaths.length));
        actions.appendChild(button(selected.size === current.files.length && selected.size ? '取消全选' : '全选结果', () => {
            selected = selected.size === current.files.length ? new Set() : new Set(current.files.map(f => f.relative_path)); render();
        }, pending || current.busy || !current.files.length));
        actions.appendChild(button('清理所选（移至回收区）', async () => {
            const files = current.files.filter(f => selected.has(f.relative_path));
            if (await window.confirmStudio(english()?`Move ${files.length} selected files (${size(files.reduce((s,f)=>s+f.size,0))}) to this case's recoverable trash? This does not release disk space.`:'将所选 ' + files.length + ' 个文件（' + size(files.reduce((s, f) => s + f.size, 0)) + '）移至当前案例的回收区？可恢复；此步骤不会释放磁盘空间。')) {
                act('cleanup', { paths: files.map(f => f.relative_path), revision: current.revision });
            }
        }, pending || current.busy || !selected.size || !!current.trash.error));
        host.appendChild(actions);
        const status = node('div', current.busy ? '模型或率定运行中：仅可查看文件位置，清理操作已禁用。' : '只列出受支持的模型结果和日志；输入、配置与掩膜文件受到保护。');
        status.style.marginBottom = '8px'; host.appendChild(status);
        const scan = node('div', '重复扫描会读取文件全部内容，较大输出可能需要较长时间。扫描后每组保留修改时间最新的一份。');
        scan.style.marginBottom = '8px'; host.appendChild(scan);
        const summary = node('div', current.files.length + ' 个文件 · ' + size(current.files.reduce((s, f) => s + f.size, 0)) + ' · 已选择 ' + selected.size + ' 个');
        host.appendChild(summary);
        const wrapper = node('div'); wrapper.style.cssText = 'overflow:auto;max-height:360px;margin:8px 0';
        const table = node('table', undefined, 'results-table'); table.style.cssText = 'width:100%;font-size:12px;border-collapse:collapse';
        const header = node('tr');
        for (const label of ['选择', '当前完整路径', '类型', '大小', '修改时间', '副本']) header.appendChild(node('th', label));
        table.appendChild(header);
        for (const file of current.files) {
            const row = node('tr');
            const selectCell = node('td');
            const checkbox = node('input'); checkbox.type = 'checkbox';
            checkbox.checked = selected.has(file.relative_path); checkbox.disabled = pending || current.busy;
            checkbox.setAttribute('aria-label', '选择 ' + file.relative_path);
            checkbox.addEventListener('change', () => {
                if (checkbox.checked) selected.add(file.relative_path); else selected.delete(file.relative_path);
                render();
            }); selectCell.appendChild(checkbox); row.appendChild(selectCell);
            const location = node('td'); location.style.cssText = 'overflow-wrap:anywhere;min-width:240px;padding:6px';
            location.appendChild(node('div', file.absolute_path));
            location.appendChild(button('复制路径', () => copy(file.absolute_path)));
            row.appendChild(location);
            row.appendChild(node('td', file.kind)); row.appendChild(node('td', size(file.size)));
            row.appendChild(node('td', new Date(file.modified).toLocaleString(window.StudioI18n?.locale() || 'zh-CN')));
            row.appendChild(node('td', file.duplicate_group ? (duplicatePaths.includes(file.relative_path) ? '重复副本' : '保留最新') : ''));
            table.appendChild(row);
        }
        wrapper.appendChild(table); host.appendChild(wrapper);
        if (!current.files.length) host.appendChild(node('div', '当前案例尚无可管理的结果文件。'));
        const trash = current.trash;
        host.appendChild(node('div', '案例回收区：' + trash.count + ' 个文件 · ' + size(trash.bytes) + '（占用磁盘，可恢复）'));
        if (trash.error) host.appendChild(node('div', trash.error));
        const trashActions = node('div'); trashActions.style.cssText = 'display:flex;gap:8px;margin:8px 0';
        trashActions.appendChild(button('恢复最近一次清理', () => act('restore', { token: trash.latest_token }), pending || current.busy || !trash.latest_token || !!trash.error));
        trashActions.appendChild(button('清空回收区并释放磁盘', async () => {
            if (await window.confirmStudio(english()?`Permanently delete ${trash.count} trashed files (${size(trash.bytes)}) and release disk space? This cannot be undone.`:'永久删除当前案例回收区的 ' + trash.count + ' 个文件（' + size(trash.bytes) + '），释放磁盘空间。此操作无法恢复。确认清空？')) {
                act('empty-trash', { revision: trash.revision });
            }
        }, pending || current.busy || !trash.count || !!trash.error));
        host.appendChild(trashActions);
        const feedback = node('div', pending ? '正在处理，请稍候…' : ''); feedback.id = 'result-files-message'; feedback.setAttribute('role', 'status');
        host.appendChild(feedback);
    }
    async function act(action, body) {
        if (pending || !current) return;
        pending = true; render();
        const casePath = current.case_path;
        try {
            const data = await request('/api/results/files/' + action, body);
            if (current && current.case_path !== casePath) return;
            if (action === 'duplicates') {
                duplicatePaths = data.duplicate_paths;
                current.files = data.files;
                render();
                message('扫描完成：' + data.groups.length + ' 组完全相同文件，' + duplicatePaths.length + ' 个重复副本。点击“选中重复副本”后可清理。');
            } else {
                selected.clear();
                await window.loadResultFiles();
                await window.loadVariables?.();
                message(action === 'cleanup' ? '已移至案例回收区，可恢复。清空回收区后才释放磁盘空间。' : action === 'restore' ? '结果文件已恢复。' : '回收区已清空。');
            }
        } catch (error) { message(error.message, true); }
        finally {
            pending = false;
            // Retain message while re-enabling controls.
            const feedback = document.getElementById('result-files-message');
            const text = feedback ? feedback.textContent : '';
            render(); if (text && text !== tr('正在处理，请稍候…')) message(text);
        }
    }
    window.loadResultFiles = async () => {
        const host = document.getElementById('result-files-panel');
        if (!host) return;
        const requestGeneration = ++generation;
        try {
            const data = await request('/api/results/files');
            if (requestGeneration !== generation) return;
            if (!current || current.case_path !== data.case_path || current.revision !== data.revision) {
                selected.clear(); duplicatePaths = [];
            } else {
                const known = new Map(current.files.map(f => [f.relative_path, f.duplicate_group]));
                for (const f of data.files) f.duplicate_group = known.get(f.relative_path) || null;
            }
            current = data; render();
        } catch (error) {
            if (requestGeneration !== generation) return;
            current = null; selected.clear(); duplicatePaths = [];
            host.replaceChildren(node('h3', '结果文件与磁盘清理'), node('div', error.message));
        }
    };
    document.addEventListener('studio-language-changed',()=>render());
    document.addEventListener('DOMContentLoaded', () => window.loadResultFiles());
    document.addEventListener('case-changed', () => window.loadResultFiles());
})();
