import io

DOC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\破解进展.md"

S = """

## 一百二十七、六十九轮：481 的真实来源 = 一次 **VARIANT 比较**（不是 LoadPicture）

### 1. 用 RaiseException 卡住时间点

在打了 5 处补丁的 exe 上 hook `RaiseException`（只要 VB 错误码 `0xc000008f`），记录时间与栈：

```
@2395 VBERR#11  … MSVBVM60+0x384a7 ← MSVBVM60+0x3847f ← MSVBVM60+0x38566 ← MSVBVM60+0x891fa
                ← OLEAUT32+0x1639b ← OLEAUT32+0x165ed ← MSVBVM60+0x40fc0 ← …
                ← EFDC_Explorer8.4.exe+0x50f76 ← MSVBVM60+0x2dbb ← MSVBVM60+0xa424 ← EFDC_Explorer8.4.exe+0x4296d3
@2399 MSGBOX（481 弹框）
```

把 `OLEAUT32` 的偏移解析成导出名：

| 偏移 | 导出 |
|---|---|
| `OLEAUT32+0x1639b` | `VarCmp+0x93b` |
| `OLEAUT32+0x165ed` | `VarCmp+0xb8d` |

**结论：这次的 481 是在一次 `VARIANT` 比较里抛出来的（`VarCmp`），不是 `LoadPicture`/`OleLoadPicture`。**
也就是说 VB 代码在比较一个"图片型 VARIANT"——而那个值之所以非法，是因为**窗体根本没被正常 Load**
（`PrintWindow` 抓出来的客户区是纯黑，证明控件从未创建）。

### 2. 本轮其它实测

| 实验 | 结果 |
|---|---|
| 在 `0x156ABA0` 后直接调 `[obj+0x250]`（疑似 Show） | 访问违例（签名不对，0x250 是属性 getter） |
| hook 窗体 vtable 全部槽位（`0..0x400`） | 启动期**只**调用了 `0x1B8`（ID `0x6E`）这一个方法，之后再无窗体方法调用 |
| `0x156ABD1: 74 6C → 90 90`（强制走"创建 0x48FE70"分支） | 有时进程不再退出，但窗口依旧 `vis=0`，多数情况下仍在 9.2s 退出 |
| 把 `license.lic`/`license.bmp` 换成 320×80 24bpp BMP（带文字） | 仍然 481 → 不是许可证图片格式问题 |
| 在退出前强显窗口（`diag39.js`） | `vis` 能变 1，但客户区纯黑（从未绘制） |

### 3. 现在的因果链（最完整的一版）

```
Sub Main
 → CheckLicensing（许可链已被假服务器打通）
    → 创建窗体对象 classinfo=0x4D5204（窗口 815×639 存在，vis=0）
       → 调用该窗体的属性 getter [obj+0x1B8]（ID 0x6E）——这一步会触发窗体 Load
          → Load 过程中某处对一个"图片型 VARIANT"做比较 → VarCmp → Err 481
          → 错误处理：弹 "There is an error when checking the license. Error 481"
 → 弹框关闭后 Sub Main 返回 → ThunRTMain 返回 → ExitProcess
```

### 4. 下一轮的具体动作

1. 反查 `EFDC_Explorer8.4.exe+0x4296d3` 与 `+0x50f76` 这两帧，定位"比较图片 VARIANT"的那条 VB 语句
   （在 `0x4296d3` 附近反汇编，找 `VarCmp`/`__vbaVarTstEq` 调用及其操作数来源）；
2. 若确认是"窗体未 Load 导致控件 Picture 非法"，则把该比较改成跳过（补丁 2–6 字节），
   让 CheckLicensing 走完并把窗体 `Show` 出来；
3. 或者继续用"退出前强显 + 自己接管消息循环"的路线，但必须在 **Load 完成之后** 才有效——
   所以核心仍是让 Load 跑完。
"""

with io.open(DOC, "a", encoding="utf-8") as f:
    f.write(S)
print("ok")
