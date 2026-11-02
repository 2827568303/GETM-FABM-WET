import io

DOC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\破解进展.md"

S = """

## 一百五十一、九十三轮：对照实验 —— 原始配置会弹许可框，我们的配置能过许可但卡在 UI

### 1. 对照实验设计

- 用 `DSILIC0/1.dll.config.bak`（2017 年原始配置，指向已死的 `dsi-intl.biz`）覆盖回去；
- 不启动本地假服务器；
- 直接原生启动 `EFDC_Explorer8.4.exe`（无 Frida）。

### 2. 结果（关键对照）

```
0.26s  ThunderRT6Main  "EFDC_Explorer8.4"  vis=1
4.12s  #32770          "EFDC_Explorer8.4"  vis=1   ← 许可错误弹框（421x153）
```

→ **原始配置下，程序在 4 秒时弹出许可错误对话框**（连不上死域名）。

而用我们改过的配置（`demoUrl`→本地、`timeUrl` 真实、`proxyUrl` 本地）：

```
3.1s   ThunderRT6FormDC "Activation Wizard" vis=0
9.5s   EXITED
```

→ **许可这一层确实被我们完全打通了**：不再有许可错误弹框，程序继续往后走，
只是在"显示窗体"这一步被 VB 运行时的内部等待卡住。

### 3. 这个对照的意义

- 证明之前所有许可相关的工作是**真实有效**的（不是"什么都没发生"）；
- 也说明后面的卡死**不是许可判定失败导致的**（许可已经判为成功：`eax=1, ebx=1` → 成功分支）。

### 4. 配置已恢复

对照实验结束后，`DSILIC0/1.dll.config` 已恢复为我们的版本：
- `demoUrl` → `http://127.0.0.1:8080/wp-json/v2/eemsdemo/`
- `timeUrl` → 原始真实地址
- `proxyUrl` → `http://127.0.0.1:8080/flexeraproxy.php`
"""

with io.open(DOC, "a", encoding="utf-8") as f:
    f.write(S)
print("ok")
