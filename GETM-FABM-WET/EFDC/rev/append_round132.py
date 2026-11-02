import io

DOC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\破解进展.md"

S = """

## 一百三十二、七十四轮：那个窗体没有控件、也没有定时器 → 它是"标题/启动画面"

### 1. 本轮实测

| 实验 | 结果 |
|---|---|
| 把 `0x156ABD1` 的 `je` NOP 掉（强制走 `0x48FE70` 分支） | 没有出现第二个窗体，仍在 ~10.9s 退出 |
| hook `CreateWindowExW` 记录所有 `Thunder*` 类 | 启动期**只创建了 1 个 Thunder 窗体**，没有任何控件窗口（`ThunderRT6CommandButton` 等一个都没有） |
| hook `SetTimer` / `KillTimer` | **一次都没有**（没有 VB 定时器） |
| 外部/内部强制 `ShowWindow`+`WS_VISIBLE` | 窗口能变 `vis=1`，但客户区空白（无控件） |
| 主线程 EIP 采样 | 全部落在 ntdll 消息等待区（在跑消息循环，不是死锁） |

### 2. 结论

- 那个 815×639、标题 `EFDC_Explore8.0` 的窗体**没有任何控件**，也没有定时器；
  它更像是程序自己绘制的"标题/启动画面"（splash），真正的 `frmEFDC_Explorer` 从未被创建；
- `Sub Main` 只有 `InitParameters` + `CheckLicensing`，之后直接 `ret`；
  而 `CheckLicensing` 成功分支只创建了这个 splash，然后就 `jmp` 到函数尾声；
- 所以：**没人去创建主窗体**。主窗体的创建代码，要么在 splash 的"绘制完成/点击"回调里，
  要么被某个我们还没满足的条件挡在后面。

### 3. 下一轮（换思路）

1. 既然 splash 无控件、无定时器，它的"下一步"很可能在 **splash 的窗口过程**里（`WM_PAINT`/`WM_LBUTTONDOWN`/`WM_TIMER` 由 VB 窗体过程处理）。
   可以用 Frida 向该窗口 `PostMessage(WM_PAINT)` 或 `SendMessage(WM_SHOWWINDOW)`，看是否会触发 VB 侧回调把主窗体建出来；
2. 或直接读 `frmEFDC_Explorer` 的 class info（对象表里已有：`frmEFDC_Explorer` 记录 `0x4DF88C`，
   其 `+0x18` = `0x482C3C`），用 `__vbaNew2(0x482C3C)` 创建并调用其 `Show`（槽位仍需确定，但至少对象能建出来）；
3. 若 `Show` 槽位难以确定，可退一步：把**主窗体的 Load 事件**当作入口——VB 窗体 `Load` 时运行时会建控件，
   我们可以先 `New` 出对象，再向它发送 `WM_SHOWWINDOW`/调用其窗口过程，逼运行时走 Load。
"""

with io.open(DOC, "a", encoding="utf-8") as f:
    f.write(S)
print("ok")
