# 模块开关生成无效 Fortran 逻辑值

第16次（种子2026101406）六后端阶段全部通过，但真实浏览器关闭/启用温室气体模块后，getm.inp出现 `fabm = '.true.'`。运行前体检报告逻辑值引号无效并正确阻止启动，证据 `five-workflows/attempt16-ui/08-failed-engine-logical-preflight.png`。两个尝试注入故障的shell命令均在修改前失败；检查显示无效值已由模块开关产生，不能把它归为主动注入的故障。

原因：write_getm_inp按Python类型输出，字符串会带引号；三个入口仍把逻辑值赋为字符串。修复case_build关闭生态、config_engines_set与config_modules_set，改传原生布尔值。未放宽体检或更改通用字符串规则。

4组实际路由（两个入口×开/关）首次全部失败，修复后通过。每组另外由实际编译Fortran namelist reader读取结果，分别输出T/F；相关7项通过。完整Python413 passed/3 skipped，40.95秒（随后只增强4组测试的原生读取验证，单独7项再次通过）。

第16次已明确标记failed，保留六阶段成功报告及UI失败证据，连续完整计数仍0/5。源码修复后必须用新数据重新从第1次累计。
