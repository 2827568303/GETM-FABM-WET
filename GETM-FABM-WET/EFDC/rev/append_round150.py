import io

DOC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\破解进展.md"

S = """

## 一百五十、九十二轮：Stalker 跟踪结果 —— 主线程最终在 ntdll 里空转

### 1. Stalker 跟踪（`0x156AB70` 入口起跟）

```
2958ms  helper entered, stalking tid=44332
...（400 条事件，尾部全部集中在）
11805   call 0x61c05d17->0x61bf1b14
11805   call 0x61bf24d0->0x77601660
11805   call 0x77601714->0x77645f90
11805   call 0x77645f99->0x7764600e
```

解读：
- `0x61xxxxxx` = **MSVBVM60**（VB 运行时）；`0x776xxxxx` = **ntdll**；
- 事件时间戳全部停在 11805ms，说明线程从 ~3 秒起就一直在这段
  "MSVBVM60 → ntdll 系统调用" 的循环里打转，**没有回到 exe 的代码**（`0x156xxxxx` 区域再没出现）。

### 2. 与之前结论的关系

- `0x156ABAE`（getter 返回处）int3 从未命中 ✔
- `Show` 入口/返回都命中（说明 Show 是另一条路径，正常返回）✔
- 主线程等待 = `{Process, Event, Event}`，超时 -1 ✔
- 约 9–10 秒后另一线程 `ExitProcess` ✔

合并起来：**VB 运行时在窗体 Load 之后进入一个内部等待循环，永远不会回到调用者**。

### 3. 尝试过的所有旁路（均已验证无效）

| 方案 | 结果 |
|---|---|
| 外部 `ShowWindow + WS_VISIBLE` | VB 会撤掉；在等待钩子里做才能保持 `vis=1`，但不绘制 |
| `RedrawWindow / UpdateWindow / 子控件重绘` | 客户区仍灰底 |
| 向 `&Activate` 发 `BM_CLICK` | 消息发得出去，但主线程不处理（未响应） |
| 替换 `WaitForMultipleObjects` 为"泵消息等待" | 未命中，无改善 |
| 阻断 `ExitProcess` | 进程保活，但主线程仍卡死 |
| 移除伪造 INI / 清空 DSI | 分别进入 `6.2 Begin the activation process...` 与 `Missing file: eems.mdb` |
| 移除 license.lic/bmp | 行为不变 |
| `SetEvent` 两个事件句柄 | 返回 1，对流程无影响 |

### 4. 结论

在不修改 VB 运行时内部逻辑、也没有厂商授权文件的前提下，
**当前环境无法让主窗体进入正常的消息循环**。已能稳定复现的部分（许可全通、无任何弹框、窗体与控件完整创建）
已全部记录在 `交付说明.md`。
"""

with io.open(DOC, "a", encoding="utf-8") as f:
    f.write(S)
print("ok")
