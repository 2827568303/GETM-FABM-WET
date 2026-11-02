// Source-project import and conservative scalar GETM/GOTM namelist editing.
(() => {
    const menu = document.querySelector('.nav-menu');
    const content = document.querySelector('.content-area');
    if (!menu || !content || document.getElementById('page-projecttools')) return;
    const nav = document.createElement('button');
    nav.type = 'button';
    nav.className = 'nav-item';
    nav.dataset.page = 'projecttools';
    nav.innerHTML = '<span class="nav-icon"><svg class="studio-icon" aria-hidden="true" focusable="false"><use href="#studio-icon-list"></use></svg></span>项目导入与物理设置';
    (menu.querySelector('[data-group-items="configuration"]') || menu).appendChild(nav);
    const page = document.createElement('div');
    page.className = 'page';
    page.id = 'page-projecttools';
    page.innerHTML = `
        <div class="page-header"><div class="page-title">项目导入与物理设置</div>
        <div class="page-desc">复制已有项目的输入数据，并编辑当前案例的 GETM/GOTM 配置。</div></div>
        <div class="card" style="margin-bottom:20px">
            <div class="card-title">导入项目副本</div>
            <div class="form-group"><label for="project-source">源目录或 project.json 文件路径</label>
            <input class="form-input" id="project-source" placeholder="例如 D:\\models\\LakeX" style="width:100%"></div>
            <div class="form-group"><label for="project-copy-name">新案例名称</label>
            <input class="form-input" id="project-copy-name" placeholder="例如 LakeX-copy" style="width:100%"></div>
            <button class="btn btn-primary" id="project-copy">复制到案例库</button>
            <p class="page-desc">导入时保留源项目，跳过模拟输出、日志、备份、私密文件和文件链接。仅包含旧版 project.json 的项目还需前处理。</p>
            <div id="project-copy-result" role="status" style="margin-top:12px;overflow-wrap:anywhere"></div>
        </div>
        <div class="card">
            <div class="card-title">当前案例的物理配置</div>
            <div class="editor-toolbar"><label for="physics-file">配置文件</label>
            <select class="form-input" id="physics-file"><option>getm.inp</option><option>gotmturb.nml</option><option>gotmmean.nml</option><option>gotmrun.nml</option><option>getm_fabm.inp</option></select>
            <button class="btn" id="physics-reload">重新加载</button>
            <button class="btn btn-primary" id="physics-save" disabled>保存修改并备份</button></div>
            <div id="physics-status" role="status" class="page-desc"></div>
            <div style="overflow:auto"><table style="width:100%"><thead><tr><th>配置组</th><th>参数</th><th>类型</th><th>值</th></tr></thead>
            <tbody id="physics-rows"></tbody></table></div>
            <p class="page-desc">保留原文件中的注释和换行。数组、复杂表达式和同一行的多个赋值暂不支持编辑；运行期间禁止保存。</p>
        </div>`;
    content.appendChild(page);
    const el = id => document.getElementById(id);
    const translate = (key, params) => window.StudioI18n?.t(key, params) || key;
    let snapshot = null;
    let generation = 0;
    let saving = false;
    let controls = [];

    nav.addEventListener('click', () => {
        navigate('projecttools');
        el('page-title').textContent = '项目导入与物理设置';
        loadPhysics();
    });

    function changed() {
        return controls.filter(item => item.input.value !== item.parameter.value)
            .map(item => ({group: item.parameter.group, key: item.parameter.key, value: item.input.value}));
    }

    function refreshSave() {
        const changes = changed();
        el('physics-save').disabled = saving || !snapshot || !changes.length;
        el('physics-save').textContent = changes.length ? `保存 ${changes.length} 项修改并备份` : '保存修改并备份';
    }

    function renderPhysics(data) {
        snapshot = data;
        controls = [];
        el('physics-rows').replaceChildren();
        const names = [...new Set([data.file, ...(data.files || [])])];
        el('physics-file').replaceChildren(...names.map(name => {
            const option = document.createElement('option');
            option.value = option.textContent = name;
            return option;
        }));
        el('physics-file').value = data.file;
        for (const parameter of data.parameters) {
            const row = document.createElement('tr');
            for (const value of [parameter.group, parameter.key, parameter.type]) {
                const cell = document.createElement('td');
                cell.textContent = value;
                row.appendChild(cell);
            }
            const cell = document.createElement('td');
            const input = document.createElement(parameter.type === 'logical' ? 'select' : 'input');
            if (parameter.type === 'logical') {
                for (const value of [...new Set([parameter.value, '.true.', '.false.'])]) {
                    const option = document.createElement('option');
                    option.value = option.textContent = value;
                    input.appendChild(option);
                }
            }
            input.className = 'form-input';
            input.style.width = '100%';
            input.setAttribute('aria-label', `${parameter.group}.${parameter.key}`);
            input.value = parameter.value;
            input.addEventListener('input', refreshSave);
            input.addEventListener('change', refreshSave);
            cell.appendChild(input);
            row.appendChild(cell);
            el('physics-rows').appendChild(row);
            controls.push({input, parameter});
        }
        el('physics-status').textContent = `${data.case_path} · ${data.parameters.length} 个可编辑参数 · ${data.uneditable_lines} 行复杂配置保留原样`;
        refreshSave();
    }

    async function loadPhysics() {
        const current = ++generation;
        snapshot = null;
        controls = [];
        el('physics-rows').replaceChildren();
        refreshSave();
        el('physics-status').textContent = '正在读取当前案例…';
        const result = await api('/api/physics/config?file=' + encodeURIComponent(el('physics-file').value));
        if (current !== generation) return;
        if (result.error) {
            el('physics-status').textContent = result.error;
            return;
        }
        renderPhysics(result);
    }

    el('physics-file').addEventListener('change', loadPhysics);
    el('physics-reload').addEventListener('click', loadPhysics);
    el('physics-save').addEventListener('click', async () => {
        if (!snapshot || saving) return;
        const data = snapshot;
        const current = generation;
        saving = true;
        refreshSave();
        const result = await api('/api/physics/config', {method: 'POST', body: {
            case_path: data.case_path, file: data.file, revision: data.revision, changes: changed()
        }});
        saving = false;
        if (current !== generation) { refreshSave(); return; }
        if (result.error) {
            el('physics-status').textContent = result.error;
            toast(result.error, 'error');
            refreshSave();
            return;
        }
        renderPhysics(result);
        el('physics-status').textContent += result.backup ? ` · 已备份至 ${result.backup}` : ' · 文件无需修改';
        toast('配置已保存', 'success');
    });

    el('project-copy').addEventListener('click', async () => {
        const source = el('project-source').value.trim();
        const name = el('project-copy-name').value.trim();
        if (!source || !name) { toast('请输入源路径和新案例名称', 'error'); return; }
        el('project-copy').disabled = true;
        el('project-copy-result').textContent = '正在复制源项目输入文件…';
        const result = await api('/api/projects/import', {method: 'POST', timeout: 300000,
            body: {source_path: source, name}});
        el('project-copy').disabled = false;
        if (result.error) { el('project-copy-result').textContent = result.error; return; }
        const status = document.createElement('p');
        status.textContent = `已复制 ${result.manifest.files.length} 个输入文件至 ${result.case_path}。` +
            (result.needs_preprocessing ? '模型输入尚不完整，需要完成前处理。' : '可打开副本继续配置和运行。');
        const audit = result.manifest.path_reference_audit;
        if (audit) {
            const counts = audit.counts || {};
            const total = Object.values(counts).reduce((sum, value) => sum + Number(value || 0), 0);
            const summary = document.createElement('p');
            summary.textContent = translate('路径预检：扫描 {files} 个配置文件，发现 {total} 条路径引用：{copied} 条相对路径可随副本映射，{source_absolute} 条仍指向源项目绝对路径，{missing} 条缺失，{absolute} 条指向项目外绝对路径，{outside} 条相对路径越出项目目录。', {
                files: audit.scanned_files || 0, total, copied: counts.copied || 0,
                source_absolute: counts.absolute_source || 0, missing: counts.missing || 0,
                absolute: counts.absolute_external || 0,
                outside: counts.outside_project || 0
            });
            el('project-copy-result').replaceChildren(status, summary);
            if (audit.references?.length) {
                const labels = {
                    copied: translate('随副本映射'), missing: translate('缺失'),
                    absolute_source: translate('源项目绝对路径'),
                    absolute_external: translate('项目外绝对路径'),
                    outside_project: translate('相对路径越出项目目录')
                };
                const examples = document.createElement('p');
                examples.textContent = translate('路径示例：') + audit.references.slice(0, 3).map(ref =>
                    `${ref.file}:${ref.line || ref.key} · ${ref.key} = ${ref.value} → ${labels[ref.status] || ref.status}` +
                    (ref.target_relative_path ? ` (${ref.target_relative_path})` : '')).join('；');
                el('project-copy-result').appendChild(examples);
            }
        } else {
            el('project-copy-result').replaceChildren(status);
        }
        const open = document.createElement('button');
        open.className = 'btn';
        open.textContent = '打开副本';
        open.addEventListener('click', () => loadExternalCase(result.case_path));
        if (result.manifest.files.some(file => ['getm.inp', 'bathymetry.nc'].includes(file.path))) {
            el('project-copy-result').appendChild(open);
        }
        if (result.needs_preprocessing) {
            const prepare = document.createElement('button');
            prepare.className = 'btn';
            prepare.textContent = '进入前处理';
            prepare.addEventListener('click', () => navigate('preprocess'));
            el('project-copy-result').appendChild(prepare);
        }
        loadCases();
    });
})();
