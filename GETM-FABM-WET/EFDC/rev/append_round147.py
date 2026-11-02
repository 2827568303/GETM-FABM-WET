import io

DOC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\破解进展.md"

S = """

## 一百四十七、八十九轮：窗体已能显示且**有 5 个控件**，但客户区仍未绘制

### 1. 贴窗 + 还原 + 重绘（`rev/diag98.js`）

```
3174ms  BEFORE hwnd=0xfea0e7a title="Activation Wizard" style=0x06C80000 vis=0
3181ms  AFTER  vis=1 style=0x16C80000
3181ms  children(5): ThunderRT6Frame, ThunderRT6CommandButton, ThunderRT6CheckBox,
                      ThunderRT6Frame, ThunderRT6TextBox
```

**结论：窗体是完整的**——有 5 个子控件（Frame/CommandButton/CheckBox/Frame/TextBox），
说明 `Form_Load` 确实跑过、控件都建好了；窗口也能被强制显示并保持 `vis=1`。

### 2. 但仍不绘制

截图（`rev/app_shot7.png` / `app_shot8.png`，两次哈希一致）客户区是**纯灰底**，
右下角白块是另一个进程的窗口。补了 `RedrawWindow(RDW_INVALIDATE|RDW_UPDATENOW|RDW_ALLCHILDREN)`、
`ShowWindow(SW_RESTORE/SW_SHOW)`、`SetWindowPos(SWP_SHOWWINDOW)`、以及 250ms 的消息泵，都没能画出控件。

### 3. 判断

- 主线程长期卡在 `WaitForMultipleObjects`（`MSVBVM60+0x86515`，约 6.7 秒）里，
  即使我们在钩子里临时泵消息，也只处理了极少数消息；
- 控件存在但没画，很可能是 **VB 的窗体绘制依赖它自己的消息循环节奏**，被这次长等待打断。

### 4. 下一轮

1. 在贴窗之后，对**每个子控件**单独 `InvalidateRect + UpdateWindow`（子控件是独立 HWND，可以直接画）；
2. 同时把窗体的 `WM_PAINT` 直接 `SendMessage` 一遍；
3. 若仍灰底，就说明 VB 窗体把绘制委托给了 `MSVBVM60` 的 WndProc，需要让主线程真正回到消息循环
   —— 也就是必须先解决那次 6.7 秒的 `WaitForMultipleObjects`（它才是根因）。
"""

with io.open(DOC, "a", encoding="utf-8") as f:
    f.write(S)
print("ok")
