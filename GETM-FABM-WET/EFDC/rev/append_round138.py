import io

DOC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\破解进展.md"

S = """

## 一百三十八、八十轮：把 `proxyUrl` 改回原值（回滚一次误改），并确定下一步用 Stalker 追指令

### 1. 本轮回滚

上一轮把 config 里的 `proxyUrl` 也改到本地（`127.0.0.1:8080/flexeraproxy.php`），
结果流程**反而更早停住**（连 helper 都到不了）。本轮已把 6 个 config 的 `proxyUrl`
全部恢复成原始密文（`licensing80.ds-intl.biz/flexeraproxy.php`），只保留 `demoUrl` 指向本地。

恢复后：图片补丁重新生效（`SUBSTITUTE hr_orig=0x80004005 -> create=0x0`），说明 Load 又跑起来了。

### 2. 仍未解释的矛盾

- `0x156ABA8`（helper 里访问窗体属性 `call [obj+0x1B8]`）会命中；
- 但紧随其后的 `0x156ABAE` **在 14 秒内一次都不命中**；
- 与此同时 `0x81D0D3`（CheckLicensing 尾声）会在 ~9.3 秒命中。

也就是说：**helper 被调用、属性访问发起、然后（约 6.4 秒后）整个 CheckLicensing 直接收尾**，
中间没有经过 `0x156ABAE`——这条路径用断点法已经解释不通了。

### 3. 下一步（改用指令级追踪）

1. 用 Frida `Stalker.follow()` 只跟 `0x156AB70 → 0x156AC40` 这一段，抓一次完整指令流，
   看属性访问返回后到底跳到哪（是不是被 VB 的 SEH/错误展开直接带回 CheckLicensing）；
2. 或把 `0x156ABAE` 的第一个字节改成 `0xCC`（int3），用 Frida 的异常回调确认是否真被执行；
3. 一旦确认分支，就把 `0x156ABD1`/`0x156AC31` 这条"建 `0x48FE70` + `call [obj+0x2B0]`(Show)"接上。

### 4. 当前稳定状态（可复现）

| 项 | 状态 |
|---|---|
| 本地假许可服务器 | 运行中（`rev/fakedemo2.py`，8080） |
| config | `demoUrl`→本地，`proxyUrl`/`timeUrl`→原值 |
| 图片补丁 | `rev/diag51.js`（`OleLoadPictureEx` 替换） |
| 481 | 不出现 |
| 许可 | `6.1 activated / 6.1.1 / 6.1.2` 全过 |
| 窗体 | splash 创建（含 4 个 VB Timer），仍 `vis=0`，~9.9s 退出 |
"""

with io.open(DOC, "a", encoding="utf-8") as f:
    f.write(S)
print("ok")
