# 五组层级导航实施计划

> **For agentic workers:** 当前会话逐项执行；独立规格与质量审查，随后统一真实UI回归。用户已委托参考成熟模型定稿，直接实施，无需再次选择布局。

**Goal:** 将左侧长功能列表收敛为五个可展开主菜单，保持全部旧页面、顶部菜单与工具可用，并支持键盘和窄屏导航。

**Architecture:** HTML原生details/summary负责层级展开，叶节点为原生button并保留data-page。小型workflow_navigation.js只管理活动祖先、单主组展开和窄屏抽屉，不重写业务路由。动态项目工具沿用现有监听器并放入项目分组。

**Tech Stack:** 现有Flask模板、原生HTML/CSS/JavaScript、node:test及实际浏览器。

## 任务1：导航结构与行为回归

Files: create `3DWET/tests/test_workflow_navigation.js`、`tests/test_workflow_navigation.py`；modify `3DWET/app/templates/index.html`。

- [x] HTMLParser记录五个`details[data-workflow]`内所有`button[data-page]`，断言既有dashboard/cases/preprocess/gridstudio/input/modules/parameters/initial/time/run/map/viz2d/viz3d/vheat/timeseries/calibrate/autocal/system均存在且无重复。
- [x] 断言原顶部8个菜单与8个工具的onclick目标未变；左侧叶节点均为button，summary按原生键盘语义操作。
- [x] 添加运行时测试：从顶部导航到viz3d会打开results组；从results导航到initial关闭results打开model；动态projecttools进入project组；非已知页不会展开错误组；抽屉关闭恢复aria-expanded。
- [x] 运行 `.venv/Scripts/python.exe -m pytest tests/test_workflow_navigation.py -q` 和 `node --test 3DWET/tests/test_workflow_navigation.js`，旧布局应因没有五个details/行为模块失败。

## 任务2：实现折叠树和活动同步

Files: modify `3DWET/app/templates/index.html`、`3DWET/app/static/js/app.js`、`3DWET/app/static/js/projects_studio.js`；create `3DWET/app/static/js/workflow_navigation.js`、`3DWET/app/static/css/workflow_navigation.css`。

- [x] 模板用以下五组，默认只展开project：
```text
project: dashboard,cases,[动态projecttools]
data: preprocess,input,gridstudio
model: modules,parameters,initial,time
compute: run,system
results: map,viz2d,viz3d,vheat,timeseries,calibrate,autocal
```
- [x] 叶按钮保留`.nav-item`和`data-page`；现有app.js绑定继续处理业务加载。项目工具使用`.nav-group-items[data-group-items="project"]`作为插入目标，保留其原事件。
- [x] navigate开头调用`window.StudioNavigation?.activate(page)`，所有来源（叶按钮/顶部工具/快速操作/地图跳转）共享活动祖先同步。
- [x] 新模块核心行为：
```javascript
function activate(page) {
  const leaves=[...menu.querySelectorAll('[data-page]')];
  const item=leaves.find(el=>el.dataset.page===page);
  if(!item)return;
  const group=item.closest('details[data-workflow]');
  for(const details of groups)details.open=details===group;
  for(const leaf of menu.querySelectorAll('[data-page]')) {
    if(leaf===item)leaf.setAttribute('aria-current','page');
    else leaf.removeAttribute('aria-current');
  }
  closeDrawer();
}
```
- [x] summary原生toggle展开时关闭其他顶级组。手动收起允许五组全部关闭，业务页面保持不变。脚本初始化activate('dashboard')。
- [x] 新CSS放在既有样式之后，仅覆盖导航；顶部原菜单/工具不删除，不改变onclick。源脚本/样式版本号随本批更新防旧缓存。
- [x] 运行上述测试，全通过后再实际浏览器检查。

## 任务3：窄屏抽屉与真实访问

Files: `workflow_navigation.js/css`、模板topbar。

- [x] topbar加入`button#studio-nav-toggle`与`aria-controls="studio-navigation" aria-expanded="false"`；sidebar id为studio-navigation，标记navigation landmark。
- [x] ≤720px，或≤950px且高度≤500px时sidebar默认隐藏，打开为固定面板；提供内部关闭按钮、Escape关闭并返回触发按钮，点击导航叶关闭。背景关闭按钮可靠可见，主内容暂设inert，抽屉内部Tab循环，关闭恢复原inert状态；桌面不使用modal属性。
- [x] 保留窄屏顶部菜单和工具通过横向滚动可达，移除旧scientific_workspace.css在小屏隐藏顶部工具的规则。不得只保留结果页自己的部分导航替代原工具。
- [ ] 在430×900与默认1280×720检查五组逐级展开、键盘Enter/Space、Escape/焦点恢复、所有旧功能页及顶部工具；确认无横向溢出、原运行/结果状态未被路由清空。

## 后续接口

水质/生态真实分离、生态实例目录、已有实测案例、观测文件夹导入在各自功能实现后挂入五组相应节点；不先提供点击后无功能的假入口。中央主画布与属性面板在连续水体可视化计划中实现。

完成本计划仍不启动新正式轮次；待整个版本集中修复及新增功能结束、桌面统一安装并固定指纹后，再执行五套新数据的完整连续验收。

## 源码实际核对（2026-10-17）

19个入口（含动态项目工具）实际导航均到达对应活动页，记录 navigation-reachability.json。430×900与900×480抽屉、顶部工具、无横向溢出已检查；默认当前442×641下补查Space两次可展开/收起模型组，全部收起时现有三维页保留，Escape关闭并聚焦studio-nav-toggle。证据 invalid-selection-and-keyboard.json。旧业务功能端到端、1280×720最终桌面版和原生通知仍待统一验收，不能从入口可达推断全部业务已完成。
