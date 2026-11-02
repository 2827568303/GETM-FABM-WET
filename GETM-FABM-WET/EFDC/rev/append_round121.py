import io

DOC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\破解进展.md"

S = """

## 一百二十一、六十三轮：`licenseWrapper` 的真实创建方式（late binding 已确认）

### 1. 用 `CoCreateInstanceEx` 的 `MULTI_QI` 拿到了确切参数

修正参数索引后（`pResults = 第 6 个参数`，`MULTI_QI = {pIID, pItf, hr}`）实测：

```
clsid={6399E2C8-63E4-4F31-823C-D256C17E7A13}  iid={00000000-0000-0000-C000-000000000046}(IID_IUnknown)  qi.hr=0
clsid={330D13A9-B2BE-4CCF-9B8A-DC2047FB3D33}  iid=IID_IUnknown                                  qi.hr=0
```

两条 **新事实**：

1. VB6 请求的是 **IID_IUnknown**，随后用 **IDispatch 晚绑定**调用 → 不需要实现任何自定义 IID，
   自建 .NET 替身理论上完全可行（此前“IID 不匹配”的猜测被推翻）。
2. 启动期除了 `FlexWrapperDongle`，还会创建 **`DemoLicense`**（`{330D13A9-…}`）——所以两条都要替身。

### 2. 替身仍不被接受的实测现象

| 观测 | 结果 |
|---|---|
| 进程是否打开替身文件 | **是**：`CreateFileW …\\EFDC_Explorer8.4\\DSILIC1.dll`（58ms，18432 字节的替身） |
| `CoCreateInstanceEx` | `qi.hr=0`、返回非空 pItf —— 对象**创建成功** |
| 替身内部日志（3 个路径：`C:\\EFDC84_LIC`、`%TEMP%`、`C:\\EFDC84_RUN`）| **一个文件都没有** → 替身代码从未执行 |
| 程序表现 | `The licenseWrapper is not valid, the application will stop now.` |

结论：CLR 打开了我们的文件，但**类型没有被实际加载执行**（典型原因：CLR 在 app base 里找到了程序集，
但元数据/类型解析失败后回退到“类工厂失败”，VB 侧把它当成 Nothing 处理）。
用 PowerShell `Activator.CreateInstance(GetTypeFromCLSID(...))` 单测同一个 CLSID **能**加载我们的替身并写日志，
说明替身本身没问题，差异在**宿主进程的加载上下文**（app base vs 注册表 CodeBase）。

### 3. 下一轮直接可做的两步

1. 在 `CoCreateInstanceEx` 的 `pItf` 上挂 `IDispatch::GetIDsOfNames / Invoke`（`rev/diag27.js` 已写好，
   待修正 `onLeave` 读 HRESULT 的方式——`hr` 不能用 `r.toInt32()`，要读 `pItf` 是否为空来判断成功），
   直接看 VB6 问了哪些名字、传了什么、期望什么返回 —— 这是判定“wrapper 无效”的最快路径。
2. 或把替身放到**进程所在目录并同时改注册表 CodeBase 指向该目录**（让 CLR 的 app base 与 CodeBase 一致），
   排除加载上下文差异。
"""

with io.open(DOC, "a", encoding="utf-8") as f:
    f.write(S)
print("ok")
