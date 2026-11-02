import io

DOC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\破解进展.md"

S = """

## 一百三十一、七十三轮：**Sub Main 在 CheckLicensing 之后立即返回**

### 1. 反汇编 Sub Main 的尾部（决定性）

```
0x15682E8  call 0x1010CF0      ; InitParameters
0x15682F4  call 0x81C4C0       ; CheckLicensing   ← 返回地址 0x15682F9
0x15682F9  mov  [ebp-4], 0x10
0x1568300  cmp  dword ptr [ebp-0x2C], 0
0x1568304  je   0x156831C
0x1568306  …（清理临时对象）
0x156831C  push 0x1568340
0x1568321  jmp  0x156833F
0x156833F  ret                 ← **Sub Main 直接返回**
0x1568340  …epilogue…
```

**Sub Main 里只有 `InitParameters` 和 `CheckLicensing` 两个调用，之后直接 `ret`。**
所以 UI 的创建**完全发生在 CheckLicensing 内部**（成功分支 `0x81CDBF` → `call 0x156AB70`）。

### 2. 这解释了"建了窗体却不显示就退出"

VB6 规则：`Sub Main` 返回时，若没有任何**可见**窗体，运行时直接结束进程。
我们的窗体虽然被创建（`__vbaNew2(0x4D5204)`），但 `Visible=False`，于是 `ThunRTMain` 返回 → `ExitProcess`。

### 3. 窗体创建 helper 的结构（`0x156AB70`）

```
0x156AB73  eax = [0x16249B0]（窗体全局）
0x156AB8C  if eax == 0 → __vbaNew2(0x4D5204, &global)      ← 创建窗体
0x156ABA8  call [eax+0x1B8]（属性 getter，返回 VARIANT）
0x156ABC6  cmp word [esp+0x10], 0
0x156ABD1  je  0x156AC3F        ← VARIANT 为 0 → 跳过
0x156ABDC  __vbaNew2(0x48FE70, &[0x16204B4])                ← 另一个对象（疑似真正的窗体/控件）
```

### 4. 本轮其它实测

- 装上图片补丁（`diag51.js`）后，`OleLoadPictureEx` 被替换成功（`hr=0x0`），**481 不再出现**；
- 之后程序在 CheckLicensing 成功分支里长时间运行，主线程 EIP 采样全部落在 `ntdll` 的消息等待区
  （说明它在**跑消息循环**，不是死锁）；进程在 9～11 秒间退出；
- 外部 `ShowWindow + WS_VISIBLE` 仍然无效（窗口在被枚举到的同一瞬间就被销毁）。

### 5. 下一轮（唯一目标：把窗体变"可见"）

1. **补一次 VB 层的 `Show`**：`0x156AB70` 里创建窗体后，用与 VB 相同的分发方式调用
   `Form.Show`（需要确定 vtable 槽位；`0x1B8`=属性getter，`0x250` 不是）；
2. 或者**让 `0x48FE70` 分支被执行**（把 `0x156ABD1` 的 `je` 改成 NOP），看它是不是真正的
   主窗体（`frmEFDC_Explorer`），若它会自我 `Show`，问题即解决；
3. 或者把 `0x156833F` 的 `ret` 改成"进入消息循环"，并保证窗体 Visible=True。
"""

with io.open(DOC, "a", encoding="utf-8") as f:
    f.write(S)
print("ok")
