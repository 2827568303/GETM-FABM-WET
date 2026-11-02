import io

DOC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\破解进展.md"

S = """

## 一百四十五、八十七轮：**`Show` 确实被执行了**（int3 确认），卡在 Show 内部

### 1. 决定性证据

在 `0x156AC31`（`call [ebx+0x2B0]`，即向导窗体的 Show）用 `0xCC` 下断：

```
3306ms  INT3 at 0x156ac31
```

→ **Show 确实被调用了**（此前 Interceptor 没命中是钩子层面的问题，不是流程没走到）。

### 2. 推论

既然 `Show` 被调用，VB 会在这个调用里执行 `Form_Load`；而向导窗口始终 `vis=0`，
说明 **Show 内部的 Load 卡住/中断**（和 splash 的 Load 完全同构）。
进程仍在 ~9.9s 被另一个线程 `End` 掉。

### 3. 当前配置

| key | 值 |
|---|---|
| `demoUrl` | 本地 |
| `timeUrl` | 真实地址（正常返回时间） |
| `proxyUrl` | 本地（未被请求） |

### 4. 下一轮

1. 在 `Show`（0x2B0）入口后立刻 hook `wininet!HttpOpenRequestW / InternetConnectW / InternetOpenUrlW`
   与 `winhttp!WinHttpOpenRequest`（延迟到 2s 安装），抓出 Load 里真正请求的 URL；
2. 一旦拿到 URL，就在假服务器上按格式返回；若拿不到，就把该请求替换成"立即失败/立即成功"；
3. 目标：让 `Show` 内部 Load 跑完 → 窗口 `vis` 变 1。
"""

with io.open(DOC, "a", encoding="utf-8") as f:
    f.write(S)
print("ok")
