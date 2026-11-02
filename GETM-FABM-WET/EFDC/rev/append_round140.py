import io

DOC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\破解进展.md"

S = """

## 一百四十、八十二轮：跳过阻塞 getter 后，程序去创建的是 **"Activation Wizard"**

### 1. 关键实验：把阻塞的 getter 跳过

在 `0x156ABA8`（`call [obj+0x1B8]`，永不返回）处打补丁：

```
0x156ABA8: ff 90 b8 01 00 00   →   E9 19 00 00 00 90   (jmp 0x156ABC6)
0x156ABD1: 74 6C               →   90 90                (je → nop，强制走"创建+显示"分支)
```

跑起来后立刻出现**新窗口**：

```
[2.94s] ThunderRT6FormDC  'Activation Wizard'  vis=0
```

→ **`0x48FE70` 就是"激活向导"窗体**（不是主窗体），而 `call [obj+0x2B0]` 就是它的 `Show`。

### 2. 执行路径实测（补丁后）

```
2977ms  HIT 0x156ABD3 / 0x156ABDC（建 0x48FE70）/ 0x156ABE3
2980ms  === MSGBOX ===        ← 先弹了个消息框
        （0x156AC31 = Show 调用未命中）
```

也就是说：跳过 splash 的属性访问后，流程确实走到了"建激活向导"这一段，但在 `Show` 之前又弹了一个消息框，
随后进程仍在 ~9.7s 退出。

### 3. 结论（重要）

- `0x4D5204`（splash）的窗体属性访问会触发它的 Load，而 Load **永不返回**（int3 已证实）；
- 绕过它之后，程序认定"许可未通过"，直接去建 **Activation Wizard**；
- 说明我们伪造的 `IsActivated=True` 只让日志走到 `6.1.2`，但 `6.1.2`（特性校验）之后仍被判为未通过。

### 4. 下一轮

1. 让 `6.1.2` 真正通过：特性校验用的是 `0x82E280 / 0x82E240 / 0x82E2C0` 三个函数 + 一次版本串比较
   （`push [0x16203FC]; push 0x4E545C`），把这些逐个 hook 出来看返回值；
2. 或者直接把 `0x81CA01` 的 `jne 0x81CDBF` 改成无条件跳转（强制成功分支），
   再配合"跳过 splash getter"的补丁，看是否会去建**主窗体**而不是激活向导。
"""

with io.open(DOC, "a", encoding="utf-8") as f:
    f.write(S)
print("ok")
