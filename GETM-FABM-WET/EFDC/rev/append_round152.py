import io

DOC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\破解进展.md"

S = """

## 一百五十二、九十四轮：验收复跑 + 主窗体对象/窗体句柄比对

### 1. 交付配置的复跑（当前状态）

```
0.21s  ThunderRT6Main  "EFDC_Explorer8.4"  vis=1
2.88s  ThunderRT6FormDC "Activation Wizard" vis=0
9.93s  EXITED
```

许可日志：

```
5. Get date, location from DSI's website
   Valid DSI Server Time: 2026/10/30 11:56:20
6. Check if the computer is already activated or not.
6.2 Begin the activation process...        ← 本轮走的是"未激活 → 激活"分支
```

（INI 里仍是 `IsActivated=True`，但程序这次内部判定为未激活，走了 6.2；
两条分支最终都卡在同一处：向导窗体创建后不显示、主线程死等。）

### 2. 主窗体对象与窗体句柄的比对

在 `0x156ABE3`（建完向导对象之后）读取：

```
3007ms  wizard obj=0x79a7f90  splash obj=0xc9c89c8
```

同一时刻枚举 `ThunderRT6Form*` 窗口：**没有任何窗口**（向导的窗口是在随后 `Show` 的 Load 里才创建的），
因此无法用 `GWLP_USERDATA` 直接完成"对象 ↔ 窗口"的绑定比对。

### 3. 交付物状态（已确认可复现）

| 资产 | 状态 |
|---|---|
| `rev/fakedemo2.py` | 正常（时间 / packages / 默认 JSON） |
| `rev/diag51.js` | 481 消除有效 |
| `C:\\EFDC84_RUN\\EFDC_Explorer8.4.exe` | 已打"跳过阻塞 getter + 强制创建分支" |
| `DSILIC0/1.dll.config` | `demoUrl`本地、`proxyUrl`本地、`timeUrl`真实 |
| `%PUBLIC%\\DSI\\EEMS8.4` | `EEMS.ini`/`EFDC_Explorer.ini`（IsActivated=True）+ `eems.mdb` + `license.lic/bmp` |

### 4. 结论不变

许可层已通关（有对照实验佐证），UI 层卡在 VB 运行时内部死等，9–10 秒后被另一线程 `End`。
"""

with io.open(DOC, "a", encoding="utf-8") as f:
    f.write(S)
print("ok")
