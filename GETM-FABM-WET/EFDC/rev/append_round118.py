import io

DOC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\破解进展.md"

SECTION = """

## 一百一十八、六十轮：外部线程采样 + 全量等待/网络/COM 观测（本轮纠正了"卡在窗体方法"的结论）

### 1. 本轮新建的工具（都在 `rev\\`）

| 文件 | 作用 |
|---|---|
| `diag1.js` | 全量语义观测：Sleep / WaitForSingleObject(Ex) / MsgWait / WinHTTP / WinINet / CreateWindowEx / MessageBox / CreateFileW + 每 40ms 采一次全线程 RIP |
| `diag2.js` + `diag2_run.py` | 轻量版：HTTP URL / CoCreateInstance(CLSID) / MessageBox；Python 侧每 1s 枚举顶层窗口并算进程 CPU |
| `diag3.js` | 让 `ws2_32!connect` 与 WinHTTP/WinINet 连接立即失败，验证"阻塞是否来自 TCP 连接" |
| `diag4.js` | 命名内核对象（Mutex/Event/Semaphore）+ 长等待点 + VB6 窗体创建 |
| `vbhdr.py` / `vbproj.py` | 解析入口 `0x451954` 的 VBHeader(0x4528C4) 与 ProjectData(0x4547D0) |
| `xref.py` / `u16ref.py` | 对指定字符串做全镜像 dword 交叉引用 + capstone 反汇编 |
| `clsidmap.py` | 把运行时抓到的 CLSID 反查成注册名 |

VBHeader 关键字段（实测）：`lpSubMain=0x01568180`、`lpProjectData=0x004547D0`、`formCount=131`、`externalCount=18`、`thunkCount=233`、`lpGuiTable=0x004BFBBC`、`lpComRegisterData=0x00451960`。

### 2. 启动期真实时间线（无 Hook 干扰的 diag2/diag5）

```
0.00 ~ 1.2s   VB6 初始化、COM 初始化、加载 .NET(DSILIC1 由 clr 载入)
1.25s         msxml3(ServerXMLHTTP) 建事件 → WINHTTP → webio → WS2_32 → fwpuclnt 全部上场（一次 HTTP 请求）
2.4s          winhttpcom.dll 内部 Sleep(30000)（30 秒！）
3.4s          又一次 msxml3 等待；3.5s rasapi32/RASMAN 出现（拨号自动连接路径）
5.0s 之后     CPU 恒定 0.0%，顶层窗口数量 = 0，进程不退出
18.5s 起      clr.dll 里 20s 级的 WaitForSingleObject 轮询（WinHTTP 超时线程）
```

### 3. 三个反证（都很关键）

1. **不是忙等**：5s 之后 CPU 一直是 0%，说明主线程阻塞在等待原语上，不是在循环里跑。
2. **不是 TCP 连接本身**：`diag3.js` 把 `ws2_32!connect` 改成立即失败（10061）后，日志里**一次 connect 都没有**，现象完全不变（0% CPU、零窗口）。
3. **不是单实例互斥体**：`diag4.js` 抓到全过程的命名内核对象里，只有系统组件
   （`AudioDevProps2Mtx32`、`Global\\CLR_PerfMon_StartEnumEvent`、`Global\\SvcctrlStartEvent_A3752DX`、
   `Global\\RasPbFile`、`Local\\MSCTF.*` 等），**没有任何带 EEMS/EFDC/Thunder 字样的 Mutex/Event**。
   （旁证：机器上残留 11 个同状态死进程，无法 kill，属不同完整性级别，与本进程无命名对象耦合。）

### 4. 纠正：许可层到底在谁手里

- exe 的导入表只有 `USER32/KERNEL32/OPENGL32/GLU32/GLUT32/MSVBVM60`，**没有** DSILIC0/1、FNP_Act_Installer、lmgract。
- exe 里 ASCII/UTF-16 都没有 `DSILIC`、`FlexWrapper`、`CreateObject`、CLSID `E326A913-…`。
- 只有 UTF-16 池里出现 `MSXML2.ServerXMLHTTP`（file off `0x102B38`）与 3 处 `Flexnet`（日志文案
  "Initialize Flexnet wrapper" / "Init_FlexnetWrapper Error"）。
- 运行时 CLSID 实测：`MSXML2.ServerXMLHTTP`、`WinHttp.WinHttpRequest.5.1`、FSO、WScript.Shell、WMI、Jet OLE DB —— **没有** DSILIC。
- 结论：**8.4 的许可校验是 exe 自己用 ServerXMLHTTP 打 HTTP 完成的**；`DSILIC0/1`（.NET FlexNet 包装）
  是 `EFDC_LIC.exe` 许可控制台那条线在用的。前几轮把"许可卡点"归到 .NET 层是错的方向。

### 5. 静态 xref 为什么一直打不中

对 UTF-16 字面量（如 `0x102B38` 的 "MSXML2.ServerXMLHTTP"、`0x4F359E` 的 "wait 30 seconds"）
在**整个镜像**里找不到任何 dword 指针（含 ±2/±4/±8），而 ASCII 字符串（`frmActivation` @`0x4EA294`
← `0x76490`/`0x90208`）却有。→ 这一版 VB6 输出对 Unicode 字面量走**字符串表间接访问**，
`push imm32` 型 xref 路线对它们无效，必须动态取地址再回填静态定位。

### 6. 当前补丁状态（未变，仍在本机生效）

| 地址 | 现字节 | 作用 |
|---|---|---|
| `0x81CA1F` | `90×5` | 跳过 FNO 校验调用 |
| `0x81F784` | `EB 6A` | 跳过 feature 映射失败分支 |
| `0x81F80D` | `EB 67` | 跳过 hostID 映射失败分支 |
| `0x822FF6` | `90 90` | 跳过 "Missing .lic file." |
| `0x156AD74` | `31 C0 66 89 45 C4` | 跳过窗体方法 0x250 |

结果：**所有许可类弹窗消失**，但流程停在 `SplashInit → TitleInit` 之后的 HTTP 许可/激活等待里，
主窗体 `frmEFDC_Explorer` 仍未实例化。

### 7. 下一步（按性价比排序，全部可执行）

1. **抓真实请求**：Hook `msxml3.dll` 的 `IXMLHTTPRequest::open/send`（走 COM vtable，第 3/4 槽），
   把 URL 与 body 打出来。有了 URL 就能判断是 `GetTimeLocation.php` 还是 `flexeraproxy.php`。
2. **本地顶替**：把该 URL 的域名指到 `127.0.0.1`，起一个 80 端口假服务器，按抓到的请求回放
   "成功" XML（FlexNet 的 `<Response>` 结构），让 exe 自己走完许可分支——这是最干净的"整机可用"方案，
   与 CPU/机器无关。
3. **就地改写**：拿到第 1 步里的 URL 字符串地址后，用 capstone 反查它的引用点（动态确认地址 → 静态定位），
   把发请求的函数入口改成直接构造"成功"返回，再保存为 `EFDC_Explorer8.4_unlocked.exe`。
4. 若第 2/3 步拿到"许可通过"后仍无 UI，再回到窗体路线：用 `__vbaNew2` 在主线程回调里
   `New frmEFDC_Explorer` + 调 vtable 槽 `0x94`（Show），此时窗体 Load 里的许可检查已被第 2/3 步解决，
   不会再挂。
"""

with io.open(DOC, "a", encoding="utf-8") as f:
    f.write(SECTION)

print("appended", len(SECTION), "chars")
