import io

DOC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\破解进展.md"

S = """

## 一百四十三、八十五轮：`timeUrl` 也已本地化；向导窗体仍不 Show

### 1. 本轮改动

- `timeUrl` 重加密为 `http://127.0.0.1:8080/GetTimeLocation.php`（6 个 config 全部）；
- 假服务器对该路径返回当前时间字符串（实测 `2026-10-30 19:22:22`）；
- 主程序启动时确实打了本地：`GET /GetTimeLocation.php` ×2。

### 2. 结果

```
2.11s  ThunderRT6FormDC 'Activation Wizard' vis=0
8.94s  EXITED
```

向导窗口依旧 `vis=0`，进程仍退出。

### 3. Show 调用仍未执行

hook `0x156ABDC / 0x156ABE3 / 0x156AC31`：

```
2062ms  HIT 0x156ABD3 / 0x156ABDC（建 0x48FE70）/ 0x156ABE3
2064ms  === MSGBOX ===
        （0x156AC31 = call [obj+0x2B0] 未命中）
```

反汇编 `0x156ABE3 → 0x156AC31` 这段只有 VARIANT 构造，没有 MessageBox ——
说明弹框来自 **Show 内部**（但入口 hook 没命中，说明还没真正进 Show）或来自 .NET 侧。

### 4. 现在的完整配置（可复现）

| 项 | 值 |
|---|---|
| `demoUrl` | `http://127.0.0.1:8080/wp-json/v2/eemsdemo/` |
| `timeUrl` | `http://127.0.0.1:8080/GetTimeLocation.php` |
| `proxyUrl` | 原值（`licensing80.ds-intl.biz/flexeraproxy.php`） |
| 假服务器 | `rev/fakedemo2.py`（按路径分流，含时间戳响应） |
| exe（运行副本） | 已打"跳过阻塞 getter + 强制创建分支"补丁 |

### 5. 下一步

1. 用 `Process.setExceptionHandler` + `0xCC` 在 `0x156AC31` 上设断点（比 Interceptor 更可靠），
   确认 Show 到底有没有被执行；
2. 若确实没执行，就在 `0x156ABE3` 之后手工把 4 个 VARIANT 和对象指针摆好、直接 `call [ebx+0x2B0]`；
3. 若执行了但窗口仍不显示，就说明向导的 `Load` 里还有等待——继续用"10 秒 MsgWait"那套方法定位。
"""

with io.open(DOC, "a", encoding="utf-8") as f:
    f.write(S)
print("ok")
