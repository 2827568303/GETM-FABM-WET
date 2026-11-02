import io

DOC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\破解进展.md"

S = """

## 一百三十三、七十五轮：VB6 用 **CreateWindowExA + 类原子** 建窗口；splash 里有 **4 个 VB Timer**

### 1. 之前所有窗口 hook 都失效的原因

前面一直 hook `CreateWindowExW`，但 VB6 实际走的是 **`CreateWindowExA`**，而且类名参数是
**注册类原子（ATOM）**，不是字符串。改成 hook `CreateWindowExA` 并在 `onLeave` 用
`GetClassNameW` 反查真实类名后，终于看到了完整的创建序列：

```
19ms    ThunderRT6Main
23ms    VBMsoStdCompMgr
24ms    VBFocusRT6
1339ms  _WinHttpEventMarshaller51
5934ms  ThunderRT6FormDC      ← splash 窗体
5937ms  ThunderRT6Timer
5937ms  ThunderRT6Timer
5938ms  ThunderRT6Timer
5938ms  ThunderRT6Timer       ← 4 个 VB 定时器控件
```

→ **splash 窗体里确实有 4 个 `ThunderRT6Timer`**（上一轮 hook `SetTimer` 看不到，是因为 VB 定时器是窗口，不是 Win32 定时器）。

### 2. 强制显示的实测

在窗体创建瞬间 `ShowWindow(SW_SHOW)`：

```
form window created hwnd=0x17f11a2
  ShowWindow prev=24  vis=1        ← 先变可见
  later vis=0                      ← 1.5 秒后被 VB 重新隐藏
```

**VB 会把自己的 `Visible=False` 状态重新应用**，所以外部 `ShowWindow` 没用——必须走 VB 层的 `Show`。

### 3. 找 `Show` 槽位的新方法（已跑出候选表）

统计"`push <classinfo>` + `call __vbaNew2` 之后紧跟着调用的 vtable 槽"：

```
0x310 x649   0x010 x492   0x018 x207   0x094 x170
0x0A4 x132   0x054 x87    0x020 x77    0x014 x49
```

已实测调用 `[obj+0x94](obj, &VARIANT)`：**不崩、返回 vt=0，但没有显示效果**。

### 4. 下一轮

按候选表逐个试（每次运行只试一个槽，崩了换下一个）：
`0x310 → 0x10 → 0x18 → 0xA4 → 0x54 → 0x20`，
判据是"调用后 `ThunderRT6FormDC` 的 `vis` 变 1 且 VB 不再把它隐藏"。
一旦命中，就把它固化成一处 5 字节补丁（在 `0x156ABA0` 之后 `call [eax+slot]`）。
"""

with io.open(DOC, "a", encoding="utf-8") as f:
    f.write(S)
print("ok")
