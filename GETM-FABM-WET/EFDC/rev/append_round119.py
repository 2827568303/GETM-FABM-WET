import io

DOC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\破解进展.md"

SECTION = """

## 一百一十九、六十一轮：把"卡点"精确到 CheckLicensing 内部 + 完成 DSILIC 层实验

### 1. 结论（本轮实测）

**`CheckLicensing`（`0x81C4C0`）在 27~104ms 进入后，30 秒内从不返回。** 本轮用最小 Hook 复测三次，
`ENTER CheckLicensing` 都出现、`LEAVE` 一次都没有。之前几轮看到的 `SplashInit/TitleInit`
属于另一种运行时状态（当时能走到 9.46s），现在这条路径根本到不了。

也就是说：**主窗体之所以不出现，是因为程序一直停在许可检查函数里**，而不是停在窗体方法里。

### 2. 已验证的事实

| 事实 | 证据 |
|---|---|
| 许可对象确实由 VB6 侧创建 | `CoCreateInstanceEx {6399E2C8-63E4-4F31-823C-D256C17E7A13}`（`Flexnet.WrapperDongle.FlexWrapperDongle`）from `MSVBVM60.DLL+0x1b11a`，t=50ms |
| CLR 随后按**进程目录**加载 | `CreateFileW …\\EFDC 商业版8.4\\DSILIC1.dll from clr.dll+0x92a4d`，t=68ms（CodeBase 虽然写的是 `C:\\EFDC84_LIC`，绑定仍先走 app base） |
| `.NET` 侧发起死域名 HTTPS | `ws2_32!send` 抓到 `CONNECT www.eems-analytics.info:443` + TLS ClientHello（`System.ni.dll+0x21bf84`），2.3s / 3.0s 各一次 |
| `Sub Main` 可被完全替身 | `Interceptor.replace(0x1568180)` 成功；替身里 `__vbaNew2(0x482C3C)` 返回对象（vtable `0x163BA98`）、`__vbaNew2(0x4D5204)` 返回对象（vtable `0x163C1F4`） |
| 这两个 class info 都不建窗口 | New2 返回后枚举窗口，只有 `ThunderRT6Main`（VB6 主窗口），没有任何 `ThunderRT6Form*` |

### 3. 本轮新增/修正的工具与产物

| 文件 | 说明 |
|---|---|
| `rev/objtbl2.py` | 解析 VB6 对象表：从 `0x4DD90C` 起 **203 条 0x30 字节记录**，每条含 名称指针 / 类型 / class-info 指针 / 标志 / 代码地址 |
| `rev/cis.py` / `rev/cis_list.js` | 全库扫描 `+4 == 0x4DD8A0` 的 class info，共 **208 个**，导出成 JS 数组 |
| `rev/mkrun.py` | 生成 `C:\\EFDC84_RUN` 可写副本（45 个文件 + 子目录），并把补丁写进副本 exe（原目录 exe 被残留进程占用，无法直接改写） |
| `rev/shim/Shim.cs` / `Shim1.cs` → `DSILIC0.dll` / `DSILIC1.dll` | 自建 .NET COM 替身：`Flexnet.Wrapper.FlexWrapper`、`Flexnet.WrapperDongle.FlexWrapperDongle`、`DemoLicense`，全部方法返回成功并写日志；已用 `[Activator]::CreateInstance(GetTypeFromCLSID)` 验证可激活 |
| `rev/diag12~16.js` | 流程 Hook / Sub Main 替身 / class info 枚举 |
| `C:\\EFDC84_LIC\\DSILIC1.dll.vendor`、`DSILIC0.dll.vendor` | 原始 DLL 备份（app 目录同） |

**结论修正**：`0x4D5204` 并不是"标题窗体"，按对象表它对应 `frmEFDC_Tools_Conversions`；
`frmEFDC_Explorer` 记录（`0x4DF88C`）里的 class-info 字段是 `0x482C3C`。两者都试过 New2，
都**不产生窗口**，说明"直接 New 主窗体"这条路缺一步（VB6 的窗体窗口在 `Show` 时才建立）。

### 4. 下一步（明确三条，按顺序执行）

1. **在 `CheckLicensing` 内部下断点式 Hook**：对 `0x81C4C0..0x81D900` 内每条 `call` 目标逐个 attach，
   记录"进入而没有离开"的那个调用 → 那就是真正的阻塞点（预计是某个模态窗体/DoEvents 等待）。
2. **拿到窗体 Show 的 vtable 槽**：`0x156AD74` 的 `[eax+0x250]` 与 `0x156ADB9` 的 `[edx+0x1bc]`
   是两个已知槽位；用 `New2` 得到的对象直接调用它们，观察是否建立窗口（`0x1bc` 带 `push -1`，
   形似 `WindowState`/`Show`）。
3. **给 DSILIC1 的 .NET 调用加超时**：`proxyURL/timeURL` 返回 `127.0.0.1:9`（已在本轮替身里实现），
   让死域名请求秒失败，再看 `CheckLicensing` 是否返回。
"""

with io.open(DOC, "a", encoding="utf-8") as f:
    f.write(SECTION)
print("ok", len(SECTION))
