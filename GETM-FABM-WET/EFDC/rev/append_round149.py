import io

DOC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\破解进展.md"

S = """

## 一百四十九、九十一轮：等待对象 = **{Process, Event, Event}**；向导控件清单拿到

### 1. 句柄类型（`NtQueryObject` 精确查询）

```
WaitForMultipleObjectsEx 6091ms  0xa80(Process) ; 0xa58(Event) ; 0x9f0(Event)
WaitForMultipleObjects   6091ms  0xa80(Process) ; 0xa58(Event) ; 0x9f0(Event)
```

→ 主线程等的是 **1 个进程句柄 + 2 个事件句柄**，超时 -1（无限），约 6 秒后返回 0。
这是典型的"创建进程并等它结束（带重定向管道事件）"模式，
但 `CreateProcessW/A`、`ShellExecute*`、`WinExec` 全部 hook 结果**一次都没有调用**，
进程列表里也没有子进程 → 说明这个 Process 句柄是**自身进程**（或早期 OpenProcess 得到的），
事件是 VB 运行时自建的两个同步对象。

`SetEvent` 对两个 Event 都返回 1（成功），但对流程没有影响。

### 2. 激活向导的完整控件清单（重要资产）

```
ThunderRT6Frame
ThunderRT6CommandButton  "&Activate"
ThunderRT6CheckBox       "Report EEMS Usage Statistics:"
ThunderRT6Frame
ThunderRT6TextBox × 6
ThunderRT6OptionButton   "Activate with License Code"
ThunderRT6OptionButton   "Activate with a Dongle"
ThunderRT6CommandButton  "Copy"
ThunderRT6Frame
ThunderRT6TextBox
ThunderRT6CommandButton  "Browse..."
ThunderRT6CommandButton  "&Select Version"
ThunderRT6CommandButton  "&Buy Now"
ThunderRT6CommandButton  "&Quit and Exit"
```

→ 向导 UI 是**完整可用**的：向 `&Activate` 按钮发 `BM_CLICK` 也能发送成功，
但因为主线程被卡死，VB 无法处理消息，所以点了没有任何反应（窗口标题显示"未响应"）。

### 3. 尝试过的"边等边泵消息"方案

把 `kernel32/kernelbase!WaitForMultipleObjects` 替换成"分片等待 + `PeekMessage/DispatchMessage`"，
但替换后既没有命中日志、也没有改善 → 说明真正的阻塞点不在这个导出上（或调用路径绕过了替换）。

### 4. 结论（当前）

- 许可与资源层全部打通；
- 向导窗体与全部控件已创建；
- 主线程在 VB 运行时内部的一次等待上卡死，导致窗体既不 `Show` 也不响应；
- 约 9-10 秒后另一个线程调用 `ExitProcess`，进程结束。

### 5. 尚未尝试（留给后续）

1. 用 Stalker 跟 `0x156AB70 → 0x156AC40` 那段，抓"getter 返回后为什么不回到调用者"；
2. 直接调用 `SetWindowLong(WS_VISIBLE)` 之外，再手动 `SendMessage(hwnd, WM_SHOWWINDOW, 1, 0)` 与
   `SendMessage(hwnd, WM_ACTIVATE, 1, 0)`，配合向导的 `&Activate` 按钮点击；
3. 把 `%PUBLIC%\\DSI` 的 `EEMS.ini`/`EFDC_Explorer.ini` 换成"真实激活后应有"的完整字段
   （尤其是 `demo_email`、`UniqueId` 与 `license.lic` 内容的一致性）。
"""

with io.open(DOC, "a", encoding="utf-8") as f:
    f.write(S)
print("ok")
