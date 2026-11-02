import io

DOC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\破解进展.md"

S = """

## 一百三十六、七十八轮：找到"真正显示窗体"的那一句 —— `call [obj+0x2B0]`（4 个缺省 VARIANT）

### 1. helper 的完整结构（`0x156AB70`）

```
0x156AB8C  if [0x16249B0]==0 → __vbaNew2(0x4D5204, &[0x16249B0])      ; 建第一个窗体（splash）
0x156ABA8  call [obj+0x1B8](obj, &var)                                ; 取一个属性
0x156ABC6  cmp word [esp+0x10], 0
0x156ABD1  je  0x156AC3F
0x156ABDC  __vbaNew2(0x48FE70, &[0x16204B4])                          ; 建第二个窗体
0x156ABE3  …构造 4 个 VARIANT：vt=0x0A(VT_ERROR), scode=0x80020004(DISP_E_PARAMNOTFOUND)
0x156AC31  call [ebx+0x2B0]                                           ; ★ 4 个缺省参数的方法
0x156AC3F  （另一条分支）建 0x48FE70 后同样走到 0x156AC31
```

**4 个 `DISP_E_PARAMNOTFOUND` 的 VARIANT = "全部用缺省参数"** —— 这正是 VB6 里
`frm.Show`（`Show Modal:=False, Owner:=Nothing`）的编译形态。也就是说：

> **`0x2B0` 就是 `Show` 的槽位**，而 `0x48FE70` 就是"被显示的那个窗体"（很可能就是主窗体）。

### 2. 本轮实测

- 直接把 `0x482C3C`（对象表里 `frmEFDC_Explorer` 的记录）用 `__vbaNew2` 建出来（vtable `0x163BA98`），
  **没有任何窗口出现** → 说明这个类的窗口是 `Show` 时才建；
- 运行副本（已把 `0x156ABD1` 的 `je` 改成 NOP）跑到 +6s 时出现了 `ThunderRT6FormDC`（`vis=0`），
  但 `0x156AC31` 的 hook 没有命中（该分支在这一轮的时序里没被执行到）。

### 3. 下一轮（目标非常明确）

1. 在**主线程**上（例如 hook `0x156AB70` 的入口）手工执行：
   `__vbaNew2(0x48FE70, &obj2)` → 构造 4 个 `VT_ERROR/DISP_E_PARAMNOTFOUND` 的 VARIANT →
   `call [obj2+0x2B0](obj2, &v1,&v2,&v3,&v4)`；
2. 观察是否出现 `ThunderRT6FormDC/MDIForm` 且 `vis=1`；
3. 若成功，就把这段"建 + Show"固化成一个极小的 Frida 注入脚本（或 5 字节补丁），
   之后再做许可状态写入与功能验收。
"""

with io.open(DOC, "a", encoding="utf-8") as f:
    f.write(S)
print("ok")
