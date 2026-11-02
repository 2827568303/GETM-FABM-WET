/* Workbench additions share existing case state and API helpers. */
(() => {
  const page = document.createElement('div');
  page.id = 'page-system'; page.className = 'page';
  page.innerHTML = `<div class="page-header"><div class="page-title">环境与启动诊断</div><p class="page-desc">区分界面可用、服务可用与计算引擎可用。查看本机依赖和实际模型位置。</p></div><div id="studio-diagnostics" class="diagnostics-grid"></div>`;
  document.querySelector('.content-area').append(page);
  window.loadStudioDiagnostics = async () => {
    const box = document.getElementById('studio-diagnostics'); box.textContent = '正在检查本机环境…';
    const d = await api('/api/system/diagnostics'); box.replaceChildren();
    const item = (name, value, note, good=true) => {
      const el = document.createElement('div'); el.className = 'diagnostic-item';
      const title = document.createElement('b'); title.textContent = name;
      const val = document.createElement('p'); val.textContent = value; val.className = good ? 'status-good' : 'status-bad';
      const hint = document.createElement('small'); hint.textContent = note || '';
      el.append(title,val,hint); box.append(el);
    };
    if (d.error) { item('诊断未完成', d.error, '请使用项目根目录的启动入口。', false); return; }
    item('应用服务','已连接',d.application);
    item('项目位置',d.writable ? '可读写' : '不可写',d.model_root,d.writable);
    item('模型求解器',d.solver.exists ? '已找到程序' : '未找到',d.solver.path,d.solver.exists);
    if (d.solver.runtime) item('模型运行库', d.solver.runtime.ready ? '文件齐全' : '缺失或不兼容', d.solver.runtime.detail, d.solver.runtime.ready);
    item('模型运行验证','须查看实际任务结果','程序文件存在并不代表运行库完整或科学计算成功。');
    Object.entries(d.dependencies).forEach(([name,ok]) => item(name,ok?'已安装':'缺少依赖','',ok));
  };
})();
