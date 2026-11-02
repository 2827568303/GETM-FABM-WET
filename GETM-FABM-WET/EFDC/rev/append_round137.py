import io

DOC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\破解进展.md"

S = """

## 一百三十七、七十九轮：卡点是"窗体属性 getter 里的 6.4 秒等待"，之后直接走尾声

### 1. 精确时间线（运行副本 + 图片补丁 + 完整 INI + 本地假服务器）

```
2946ms  HIT 0x156ABA8        ← helper 里第一次访问窗体属性 call [obj+0x1B8]
        ……6.4 秒无任何事件……
9294ms  HIT 0x81D0D3         ← CheckLicensing 的函数尾声（成功分支的 jmp 目标）
        → Sub Main 返回 → 进程退出（~9.9s）
```

期间 **0x156ABD1 / 0x156ABD3（属性返回后的分支）从未命中**，也**没有 VB 错误、没有消息框**。

### 2. 结论

- 窗体属性访问（`[obj+0x1B8]`）会触发窗体 Load，Load 里有一段**约 6.4 秒的等待**（网络/许可相关，现已无报错）；
- 等待结束后，流程**没有走"检查 VARIANT → 建第二个窗体 → 调 Show(0x2B0)"**，
  而是直接到了 CheckLicensing 的尾声 —— 也就是说 `Show` 那条路被跳过了；
- 因此 splash 永远不会被显示，`Sub Main` 返回后进程结束。

### 3. 下一轮

1. 在 `0x156ABAE`（getter 返回处）读 `eax` 和 `[esp+0x10]` 的 VARIANT 值，确认进来的是哪条分支；
2. 若确认 `jge` 跳到了错误处理（`__vbaHresultCheckObj`），说明 getter 返回了负 HRESULT —— 那就把这个 HRESULT 判定的分支改成"继续"，
   让流程走到 `0x156ABDC`（建 `0x48FE70`）和 `0x156AC31`（`call [obj+0x2B0]` = Show）；
3. `0x2B0` 已确认是"4 个缺省参数"的方法（`DISP_E_PARAMNOTFOUND` × 4），与 VB6 `Form.Show` 完全吻合。
"""

with io.open(DOC, "a", encoding="utf-8") as f:
    f.write(S)
print("ok")
