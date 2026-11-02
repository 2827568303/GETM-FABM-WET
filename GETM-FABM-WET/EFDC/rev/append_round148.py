import io

DOC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\破解进展.md"

S = """

## 一百四十八、九十轮：等待句柄、两处等待、以及"干净首次运行"分支

### 1. 主线程长等待的句柄细节

hook `WaitForMultipleObjects(Ex)`（时长 > 1s）：

```
10729ms  WaitForMultipleObjectsEx 7644ms ret=0 count=3 timeout=0
         h=0xa5c wait0=0 ; h=0xa2c wait0=258 ; h=0x9d8 wait0=258  from KERNELBASE.dll+0x15f4d8
10731ms  WaitForMultipleObjects   7646ms ret=0 count=3 timeout=-1
         同一组句柄                                from KERNEL32.DLL+0x6cf56
```

- 3 个句柄、超时 **-1（无限）**；其中一个（`0xa5c`）已 signaled，另两个没有；
- `GetThreadId/GetProcessId` 对三者都返回 0 → 不是线程/进程句柄（更像 Event/Section）。

### 2. FlexNet 原生客户端已排除

- 进程里确实加载了 `FNP_Act_Installer.dll`（7 个导出）与 `lmgract.dll`；
- 全部 7 个导出都 hook 了，**没有任何一次调用超过 800ms** → 卡点不在 FNP。

### 3. `Show` 立刻返回（重要）

int3 同时放在 `0x156AC31`（Show 入口）与 `0x156AC39`（Show 返回处）：

```
3082ms  INT3 0x156ac31
3082ms  INT3 0x156ac39     ← 同一毫秒返回
```

→ `Show` 本身没问题；但窗口 `WS_VISIBLE` 依旧没置上，说明 VB 认为这个窗体"不该显示"
（或它只是被创建出来当数据容器）。

### 4. 去掉伪造 INI 后的新分支

把 `%PUBLIC%\\DSI\\EEMS8.4\\EEMS.ini` 与 `EFDC_Explorer.ini` 移走后再跑：

```
5. Get date, location from DSI's website
   Valid DSI Server Time: 2026/10/30 11:43:53
6. Check if the computer is already activated or not.
6.2 Begin the activation process...        ← 进入激活流程
（随后无日志，9.1s 退出；Activation Wizard 仍 vis=0）
```

把这些 INI 完全删掉、连 `eems.mdb` 也没有时，会弹真实消息框：

```
Missing file: C:\\Users\\Public\\DSI\\EEMS8.4\\eems.mdb
```

→ 说明这两个 INI + `eems.mdb` + `license.lic/bmp` 缺一不可。

### 5. 现状（已恢复伪造 INI）

- 许可日志稳定到 `6.1.2`；
- 向导窗体创建、`Show` 立即返回，但 `WS_VISIBLE` 从未置上；
- 主线程在 3 句柄上无限等待，~9-10 秒后被另一线程 `End`。

### 6. 下一轮

1. 对那 3 个句柄用 `NtQueryObject(ObjectTypeInformation)` 精确取类型名（Event/Mutant/Section）；
2. 若是 Event，直接 `SetEvent(h)` 把它放行，看主线程是否恢复；
3. 同时用 `0xCC` 断点确认为什么 `Show` 没置 `WS_VISIBLE`（是否走了 `BOF` 里的 `Visible=False` 恢复）。
"""

with io.open(DOC, "a", encoding="utf-8") as f:
    f.write(S)
print("ok")
