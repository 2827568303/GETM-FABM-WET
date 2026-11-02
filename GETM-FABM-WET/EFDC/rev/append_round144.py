import io

DOC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\破解进展.md"

S = """

## 一百四十四、八十六轮：时间服务器已改回真实地址；10 秒等待与 `proxyUrl` 无关

### 1. 本轮结论来源

- 把 `timeUrl` 指向本地后，日志变成 `DSI Server Time is 00:00:00`（我们的响应格式不对，解析不出时间）；
- 改回真实地址后恢复为 `Valid DSI Server Time: 2026/10/30 11:27:06` —— **说明时间服务器这条链路本身是好的**；
- 同时把 `proxyUrl` 指到本地（`127.0.0.1:8080/flexeraproxy.php`），但假服务器**没有收到任何 flexeraproxy 请求**，
  说明那 10 秒的 `WinHttpRequest` 等待**不是**打 `proxyUrl`。

### 2. 当前配置（最优组合）

| key | 值 |
|---|---|
| `demoUrl` | 本地 `127.0.0.1:8080/wp-json/v2/eemsdemo/` |
| `timeUrl` | **原始真实地址**（能正常返回时间） |
| `proxyUrl` | 本地（当前没有被请求） |
| 运行副本 exe | 已打"跳过阻塞 getter + 强制创建分支" |

### 3. 现状

```
3.20s  Activation Wizard (vis=0)
9.89s  EXITED
```

许可日志稳定走到 `6.1.2`；向导窗体仍不显示。

### 4. 下一轮

1. 用 `Process.setExceptionHandler`+`0xCC` 在 `0x156AC31`（Show 调用）下断，确认到底有没有执行；
2. 若执行了，就在 `0x156AC31` 之后 hook `ShowWindow`，看 VB 是否调用过显示；
3. 若没执行，说明 `0x156ABE3` 之后的 VARIANT 构造/分支被跳过，需要按真实值重放。
"""

with io.open(DOC, "a", encoding="utf-8") as f:
    f.write(S)
print("ok")
