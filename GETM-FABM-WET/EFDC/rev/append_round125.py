import io

DOC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\破解进展.md"

S = """

## 一百二十五、六十七轮：`getupgradepackages` 是**另一种**响应结构（已修正）

### 1. 关键发现：不同端点的 JSON 结构不同

`DSILIC1.log` 里一直有这条错误：

```
Demo verion: 无法将类型为"System.String"的对象转换为类型
  "System.Collections.Generic.List`1[Flexnet.Wrapper.Dongle.Objects.DemoLicense.PackageInfo]"
```

反查 `GetUpgradePackagesResponse` 的 IL 后确认：这个方法**不走** `DemoRespone`，而是用自己的

```csharp
class PackageRespone { string Status; List<PackageInfo> ReturnedData; }
class PackageInfo { string idversion; string product; string versiondate; }
```

所以 `getupgradepackages` 的响应必须是：

```json
{"Status":"Success","ReturnedData":[{"idversion":"1","product":"EFDC_Explorer8.4","versiondate":"2030-01-01"}]}
```

而其它端点（`login` / `activateuser2` / `sendactivationemail`）仍是
`{"Status":"Success","ReturnedData":"<XmlResult>…","Exception":""}`。

### 2. 已改造

新增 `rev/fakedemo2.py`（按路径返回不同响应）：
- `/…/getupgradepackages` → `rev/demo_resp_packages.txt`（JSON 数组）
- 其它 → `rev/demo_resp.txt`（XmlResult 字符串）

改造后 `DSILIC1.log` **不再出现那条类型转换错误**（已实测），假服务器日志也确认三个 packages 请求都被正确应答。

### 3. 仍然存在的现象（下一轮主攻）

| 版本 | 现象 |
|---|---|
| 原版 exe + 假服务器 | `3.0s` 建出 `ThunderRT6FormDC "EFDC_Explore8.0"`（815×639，vis=0）→ `9.2s` 进程退出（`ThunRTMain` 返回） |
| 打了 5 处补丁的 exe | 弹 481 → 确定 → 退出；`diag21` 实测它卡在 `0x156ABA8: call [eax+0x1B8]`（属性 getter，永不返回） |

结论：现在的核心只剩一件事——**让建出来的窗体真正 `Show` 出来（或让 Sub Main 不返回）**。
下一步工具已就绪：`rev/force_show3.py`（50ms 轮询 + `SetWindowLong(WS_VISIBLE)`+`ShowWindow`）、
`rev/late_attach.py`（3 秒后 attach Frida，避免扰动启动）、`rev/longwatch.py`（窗口时序）。

下一步具体做法：
1. 在 `__vbaNew2(classinfo=0x4D5204)` 返回时拿到窗体对象指针，**逐个试 vtable 槽位**（0x1B8 / 0x1BC / 0x250 / 0x2B0）
   找出能让窗口 `vis` 变 1 的那个（一次试一个槽，崩了换下一个）；
2. 或者把 `0x156ABA8` 的 `call [eax+0x1B8]` 改成跳过并伪造 VARIANT 结果，看流程是否继续到主窗体创建。
"""

with io.open(DOC, "a", encoding="utf-8") as f:
    f.write(S)
print("ok")
