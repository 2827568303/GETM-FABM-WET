import io

DOC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\破解进展.md"

S = """

## 一百二十八、七十轮：把 VB6 的"间接调用表"解出来了（新工具）

### 1. 关键发现：`call dword ptr [0x401xxx]` 是**运行期填表**，不是 IAT

VB6 编译产物里大量出现 `call dword ptr [0x4014f8]` 这类写法，我一直以为是 IAT thunk，实际是
**运行期由 MSVBVM60 填好的一张函数指针表**（文件里那些 0x401xxx 位置上是 `07 00 08 00 …` 的数据）。

于是写了个运行期解析脚本（`rev/diag45.js` 思路 + `rev/thunkname.py` 静态辅助），拿到实测映射：

| 表项 | 运行期指向 | 含义 |
|---|---|---|
| `0x4014F8` | `MSVBVM60+0xa44a` | **`__vbaFileOpen`** |
| `0x401668` | `MSVBVM60+0x1de9b` | `rtcGetPresentDate` |
| `0x4014C0` | `MSVBVM60+0x5560` | `__vbaVarCat` |
| `0x401160` | `MSVBVM60+0x1060ef` | `__vbaFreeVar` |
| `0x401504` | `MSVBVM60+0xb540` | `rtcFreeFile` |
| `0x40129C` | `MSVBVM60+0x1d872` | `__vbaOnError` |
| `0x401220` | `MSVBVM60+0x427c2` | `__vbaHresultCheckObj` |
| `0x40154C` | `MSVBVM60+0x1d8f4` | `__vbaFreeStrList` |
| `0x401144` | `MSVBVM60+0x38388` | `__vbaStrI4` |
| `0x4012A0` | `MSVBVM60+0xee26a` | `rtcMsgBox` |
| `0x4012A4` / `0x40118C` / `0x4011AC` | `__vbaObjSet` / `__vbaFreeVarList` / `__vbaFreeObjList` | — |

**意义**：以后看到任何 `call [0x401xxx]` 都能立刻说出它在调 VB 运行时的哪个函数，
不用再靠猜——这对定位"哪一句 VB 语句出错"是决定性的。

### 2. 用它反读了 481 的现场

- 481 弹框前最后一次错误链里的 `0x8296D3`，正好是 `call [0x4014F8]`（**`__vbaFileOpen`**）的返回地址，
  紧随其后是 `rtcGetPresentDate`；
- 说明许可流程里有一段 **VB `Open` 语句 + 取当前日期** 的代码（很像写/读日志或写 .lic）；
- hook `__vbaFileOpen` 抓到的调用形如 `args=fileno8, -1, 0x1a0001, <ptr>`，路径参数在**第 4 个参数**上
  （本轮按 a[1]/a[2] 取到空串，下一轮按 a[3] 取即可拿到真实路径）。

### 3. 其它

- `rtcErrObj` 能拿到 Err 的 IDispatch 指针（实测 `0x1d96a80`），但属性读取那步
  （GetIDsOfNames/Invoke）在 Frida 里报 `invalid type specified`，下一轮改用
  `oleaut32!DispGetIDsOfNames` + vtable Invoke，把 `Err.Source`（出错的过程名）读出来。

### 4. 下一轮

1. `__vbaFileOpen` 取 a[3] 的 BSTR → 得到程序想打开但失败的文件路径（很可能是 `license.lic` 或某个 ini）；
2. 读 `Err.Source` 确认出错过程（预期是 `frmAct_License_Validation` 之类）；
3. 两者结合，直接在 exe 里把那句 `Open` 前后的失败分支改掉，让 CheckLicensing 走完 → 窗体 `Show`。
"""

with io.open(DOC, "a", encoding="utf-8") as f:
    f.write(S)
print("ok")
