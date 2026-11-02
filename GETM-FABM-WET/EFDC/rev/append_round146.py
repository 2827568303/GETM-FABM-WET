import io

DOC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\破解进展.md"

S = """

## 一百四十六、八十八轮：**可以在主线程等待期间把窗体贴出来（vis=1）**

### 1. 新手法

在主线程的长等待（`WaitForMultipleObjects` / `WaitForSingleObject`）钩子里，
顺便对 `ThunderRT6Form*` 窗口执行 `SetWindowLong(WS_VISIBLE) + ShowWindow(SW_SHOW) + UpdateWindow`：

```
3050ms  [wait1] show 0x1b5051a title="Activation Wizard" prev=24 vis=1
        win 0x1b5051a vis=1 title='Activation Wizard' rect=(0,3 643x489)
        after: vis=1      ← 这次没有被 VB 重新隐藏
```

**窗口第一次真正变成可见（vis=1）并且保持住了**（此前所有外部 ShowWindow 都会被 VB 撤掉）。

### 2. 但客户区仍是空白

截图（`rev/app_shot5.png` / `app_shot6.png`）客户区没有渲染出控件内容：
- `ShowWindow` 返回的 prev 值是 **24**（不是 0/1），说明窗口的初始状态很怪（可能被创建成最小化/隐藏态）；
- 用 `BringWindowToTop + SetForegroundWindow` 前置后再截图，画面仍是桌面 → 窗口没有真正绘制。

### 3. 本轮另一项证据

同一时间窗内还有一次 **6.7 秒** 的 `WaitForMultipleObjects`，调用者是 **`MSVBVM60.DLL+0x86515`**
（VB 运行时内部等待，ret=0 = 等到对象），说明 `Show` 内部还有一段 VB 自身的等待。

### 4. 下一轮

1. 在"贴出窗口"之后再补 `ShowWindow(SW_RESTORE/SW_SHOWNORMAL)` + `SetWindowPos(SWP_SHOWWINDOW)`，
   并 `RedrawWindow(RDW_INVALIDATE|RDW_UPDATENOW|RDW_ALLCHILDREN)`，看能否把控件画出来；
2. 若仍空白，说明该窗体的控件确实没建（Load 没跑完），需继续定位 `MSVBVM60+0x86515` 的那次 6.7 秒等待；
3. 记录：`prev=24` 这个异常返回值值得单独查（VB 可能用 `ShowWindow(hwnd, SW_MINIMIZE)` 创建窗体）。
"""

with io.open(DOC, "a", encoding="utf-8") as f:
    f.write(S)
print("ok")
