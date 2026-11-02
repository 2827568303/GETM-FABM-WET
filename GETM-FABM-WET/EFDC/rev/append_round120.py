import io

DOC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\破解进展.md"

SECTION = """

## 一百二十、六十二轮：把"卡死"还原成一条完整可读的许可流程（含唯一弹框文案）

### 1. 现状（一句话）

程序启动 → `CheckLicensing` → 走到 `6.2 Begin the activation process...` → 抛出
**`There is an error when checking the license. Error 481 (Invalid picture)`** → 点“确定”后 **4.9 秒进程退出**。
这就是“没有界面”的全部原因：**没有第二个弹框，也没有隐藏窗口**。

### 2. 许可流程实证（`%PUBLIC%\\DSI\\EEMS8.4\\ee_activation.log`）

```
****** Check Licensing ******
UserName=…, ComputerName=…
VersionDate:EE8.4.3 Release 180723
1. Initialize Flexnet wrapper
2. Read license information
4. Get the machine id
 MachineID=DISK_SERIAL_NUM=2db6323c
5. Get date, location from DSI's website
   Valid DSI Server Time: 2026/10/30 8:51:20      ← 时间服务器是通的
6. Check if the computer is already activated or not.
6.2 Begin the activation process...                 ← 卡在这里后失败
```

### 3. 本轮修复的环境缺件（重要）

`C:\\Users\\Public\\DSI\\EEMS8.4\\` 原本**缺三样东西**，本轮已从 `EEMS8.4_stale_114223` / `EEMS8.3` 补齐：

| 文件 | 说明 |
|---|---|
| `license.lic` | 822 字节，**BMP 头 `42 4d`**（许可就是一张位图，程序用 `LoadPicture` 读它） |
| `license.bmp` | 4240 字节 |
| `EEMS.ini` | 与 `EFDC_Explorer.ini` 同内容（`IsActivated=True`、`FeatureName=EE_MULTI_TRIAL_8_4`、`LicenseFile=…\\license.lic`） |

### 4. .NET 替身实验的结论（负面但关键）

自建 `DSILIC1.dll` 替身（`Flexnet.WrapperDongle.FlexWrapperDongle`，同 CLSID `6399E2C8-…`、
同程序集名/版本，`Initialized` 恒为 true）装上后，程序**改报**：

```
The licenseWrapper is not valid, the application will stop now. Please contact DS-INTL.
```

且替身日志**一条都没有**（方法一次没被调用）→ 说明 VB6 侧 `CoCreateInstanceEx` 拿到的对象被判为无效，
大概率是 **IID/接口不匹配**（VB6 请求的是某个具体接口，我们的类只暴露 IDispatch）。
`CoCreateInstanceEx {6399E2C8-63E4-4F31-823C-D256C17E7A13}` 确实在 **50ms** 发生（`MSVBVM60.DLL+0x1b11a`）。

### 5. 本轮新增工具

| 文件 | 作用 |
|---|---|
| `rev/dialogs.py` | 枚举进程内 `#32770` 弹框、读取 Static 文案、自动点“确定”，记录轮次 |
| `rev/run_swallow.py` | 用 Frida 打脚本 + 轮询窗口 + 用 `GetExitCodeProcess` 精确检测进程退出时刻 |
| `rev/diag22.js` | `SoftModalMessageBox` 替换为「自动按 OK」+ 记录文案与调用链 |
| `rev/diag23.js` | `RaiseException` 追踪（VB 错误码 `0xc000008f`；.NET 异常 `0xe0434352`） |
| `rev/diag24.js` | `CoCreateInstanceEx` 的 CLSID/IID/HRESULT 观测 |
| `rev/diag25.js` | `rtcMsgBox` 调用点观测（VB6 走 thunk，返回地址落在 `0x41E3xx` thunk 区） |

时间线（实测）：`4.48s` .NET（`System.ni.dll`）抛异常 → `4.70s` 弹 481 → `4.9s` 退出。
即 **481 的根因是 .NET 许可调用失败后返回的许可数据无效**。

### 6. 下一轮的三条确定路线

1. **拿到 VB6 请求的 IID**：修正 `diag24.js` 的参数索引（`CoCreateInstanceEx` 的 `pResults` 是第 6 个参数，
   `MULTI_QI = {pIID, pItf, hr}`），再据此在替身里实现**同 IID、同 vtable 顺序**的接口。
2. **改打“有效性判定”**：定位 `The licenseWrapper is not valid` 分支（经 `SoftModalMessageBox` 的 app 侧调用点，
   或对 `0x41E3xx` thunk 反查 IAT 槽），把该分支改成“视为有效”，让替身接管后续调用。
3. **绕过 .NET，直接给 VB 一个合法 `XmlResult`**：在 `Checkout/GetStatus/GetInfo2` 返回值里放
   程序期望的 XML（可以先让替身把所有入参/返回值 dump 到日志，用真实调用序列反推结构）。
"""

with io.open(DOC, "a", encoding="utf-8") as f:
    f.write(SECTION)
print("ok", len(SECTION))
