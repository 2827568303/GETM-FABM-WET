# 初始条件保存及重新构建

第14次完整尝试（种子2026101404、多边形水深）在真实浏览器中发现：构建前将水温保存为16.404℃，界面提示保存成功，构建后重新读取却为15℃。初始条件POST仅在getm.inp存在时写入，sidecar没有保存水温/相对水位；构建总用模板常数。水质显式初值和已保存植被上限也未在重建中恢复。

浏览器证据位于 `docs/audit/five-workflows/attempt14-ui/03-failed-prebuild-temperature-reset.png` 及对应DOM。自动化回归 `tests/test_initial_conditions_rebuild.py` 两项初次运行均失败（预构建读取15、重新构建15）。

修复在sidecar中保留明确保存的hydro和water_quality值，GET在尚无主配置时返回草稿；构建在模板生成后应用保存的水位、水温、水质，并使用保存的植被上限生成NetCDF。只恢复当前启用模块的显式水质值。

新增两项及原生namelist三项共5项测试通过：保存→重新读取→首次构建→再次构建；另覆盖构建后修改水质及植被上限→重建→直接读取实际配置和NetCDF。

第14次后端external/features/results/scipy/abc已通过；修复改变版本，harness正确将该次标记failed并停止在restart前，连续计数仍为0/5。失败证据保留，不能算一次完整验证。最终回归、独立审查与新数据完整轮次待完成。

独立审查另复现构建中切换案例时，全局active_case_path使另一个案例的草稿污染捕获的目标案例。新增实际路由回归复现A=16.404、B=22.5，构建A中切换B后A错误变为22.5。修复_load_init_cond接收显式路径，build/GET/POST均使用捕获的case_path；该回归转绿，相关6项通过。第15次已开始但将因版本变化失败，不能计数。此前完整回归407 passed/3 skipped，新增切换回归后再次运行中。
