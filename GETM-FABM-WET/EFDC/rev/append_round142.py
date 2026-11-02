import io

DOC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\破解进展.md"

S = """

## 一百四十二、八十四轮：阻塞点抓到了 —— **VB 的 WinHttpRequest 在等 10 秒**

### 1. 关键证据

hook `MsgWaitForMultipleObjects(Ex)`（带线程号、句柄、超时）：

```
2580ms  MsgWaitForMultipleObjectsEx  1244ms  tid=21944  count=1 handles=2096 timeout=10000  ret=1  from USER32.DLL+0x38b1f
2580ms  MsgWaitForMultipleObjects    1245ms  tid=21944  count=1 handles=2096 timeout=10000  ret=1  from **winhttpcom.dll+0xa23b**
```

→ 窗体 `Load` 里有一个 **VB 侧的 `WinHttpRequest`（winhttpcom.dll）**，它在等 HTTP 响应，
**超时设成 10000ms**；等待结束后（超时）流程就走"失败"分支，随后进程被另一个线程 `End` 掉。

### 2. 同时确认

- `PeekMessage / GetMessage` 计数 **= 0**（这段时间根本没有消息泵）；
- 该窗口内没有任何文件/注册表/网络新建活动（日志只有 `ee_activation.log` 的打开）；
- `WinHttpOpen`（agent 为空）在 2476ms 出现，`WinHttpReceiveResponse` 在 2418ms 出现。

### 3. 结论

卡点不是 .NET，也不是 FlexNet，而是 **VB 自己用 `WinHttpRequest` 发的一次 HTTP 请求**（10 秒超时）。
我们之前只把 `demoUrl`（.NET 用）指到本地，这个 **VB 请求走的是另一个 URL**（很可能是 `timeUrl` 或
`webUrl/updateUrl` 之类的剩余地址），所以仍然打到外网并超时。

### 4. 下一轮

1. 把 config 里剩下的 URL（`timeUrl`，必要时 `webUrl`）也重加密指向本地假服务器；
2. 在假服务器上按路径返回 VB 期望的内容（`GetTimeLocation.php` 多半返回一个时间字符串）；
3. 一旦这个请求在本地秒回，`Load` 就不会再等 10 秒，窗体才有机会真正 `Show` 出来。
"""

with io.open(DOC, "a", encoding="utf-8") as f:
    f.write(S)
print("ok")
