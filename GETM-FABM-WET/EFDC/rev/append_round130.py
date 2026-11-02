import io

DOC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\破解进展.md"

S = """

## 一百三十、七十二轮：许可走的是**成功分支**（0x81CDBF），窗体由成功分支负责创建

### 1. 实测分支走向

hook 关键地址（原版 exe + 图片补丁 + 完整 INI）：

```
28ms    ENTER CheckLicensing   caller_ret=0x015682F9      ← Sub Main 调用点
2359ms  HIT 0x81D0F0 → leave                              ← 许可校验主体
2362ms  HIT 0x81CDBF                                      ← **成功分支**
之后    没有 0x828F50 / 0x156ACC0 / CheckLicensing 的 LEAVE
```

`0x81CDBF` 处的代码是：

```
0x81CDBF  call 0x156AB70        ← 窗体创建 helper（内部 __vbaNew2(0x4D5204) + [obj+0x1B8]）
0x81CDC4  call [0x401280]
0x81CDCA  wait
0x81CDCB  push 0x81D0DD
0x81CDD0  jmp  0x81D0D3         ← 走向函数尾声
```

也就是说：**许可判定成功后，程序确实去创建窗体了**，然后试图结束 CheckLicensing。

### 2. 特征校验的位置（已定位）

```
0x81C9B3  call 0x82E280     ← 特征检查 A
0x81C9C1  call 0x82E240     ← 特征检查 B
0x81C9D4  call 0x82E2C0     ← 特征检查 C
0x81C9E7  push [0x16203FC]; push 0x4E545C; call [0x401370]   ← 版本串比较
0x81C9FF  test eax, ebx
0x81CA01  jne 0x81CDBF      ← 全部通过 → 成功分支
0x81CA07  …失败分支（写日志）
0x81CA1F  call 0x81D3E0     ← FNO 检查（我们旧补丁 NOP 的就是这里）
```

### 3. 现状（本轮结束）

| 项 | 状态 |
|---|---|
| 481 | 已消除（OleLoadPictureEx 替换） |
| 许可判定 | `6.1 The license is activated`，且**走成功分支 0x81CDBF** |
| 窗体制建 | 已在成功分支里调用（helper `0x156AB70`） |
| 窗体显示 | 仍 `vis=0`；进程约 9.6s 退出 |
| CheckLicensing | 未见 LEAVE（成功分支用 `jmp` 走尾声，Frida 的 onLeave 不触发） |

### 4. 下一轮

1. 从 Sub Main 的调用点 `0x15682F9` 往回/往前看：CheckLicensing 返回后 Sub Main 做了什么
   （重点看是否调用 `0x828F50`（SplashInit）以及是否走到 `End`）；
2. 若 Sub Main 在 CheckLicensing 之后直接结束，就把 0x15682F9 之后的"结束"路径改成继续
   （例如跳过 `End`/`Unload`），或在 helper `0x156AB70` 内补一次 `Show`；
3. 目前许可与图片两个硬骨头都已拔掉，剩下的就是"窗体显示/保持运行"这一处。
"""

with io.open(DOC, "a", encoding="utf-8") as f:
    f.write(S)
print("ok")
