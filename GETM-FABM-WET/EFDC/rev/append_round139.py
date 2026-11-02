import io

DOC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\破解进展.md"

S = """

## 一百三十九、八十一轮：int3 断点证实"属性 getter 永不返回"；进程是被**另一个线程 End 掉的**

### 1. 用 int3 + `Process.setExceptionHandler` 做的确证

在 `0x156ABA8`（`call [obj+0x1B8]`）和 `0x156ABAE`（它的返回地址）各放一个 `0xCC`：

```
2393  INT3 at 0x156aba8      ← 调用发生
（12 秒内）0x156abae 从未命中  ← 调用永不返回
```

同时 `RaiseException` 在 3 秒后**一次都没有**（没有 VB 错误、没有 C++ 异常）——
也就是说不是异常展开，而是**这个调用真的卡住不返回**。

### 2. 进程是被另一个线程 `End` 掉的

hook `ExitProcess`：

```
9078ms  ExitProcess tid=53256   ← 与主线程不同的线程
```

把 `ExitProcess` 换成"记录后 `Sleep(INFINITE)`"后，**进程不再退出**，窗体窗口
`ThunderRT6FormDC "EFDC_Explore8.0"` 在 10s / 16s / 24s 都还在（`vis=0`）。

### 3. 新的关键现象

从**外部线程**对该窗口 `ShowWindow(SW_SHOW)` 会**直接挂住**（脚本卡在 ShowWindow 不返回），
说明**主线程此时没有在跑消息循环**（不是模态循环，而是真卡在某个等待里）。

### 4. 下一轮

1. 在主线程卡住时，逐个 hook `WaitForSingleObject/Ex`、`NtWaitForSingleObject`、`NtUserWaitMessage`，
   把**主线程**的等待对象（handle 类型、是否 -1 超时）抓出来 —— 这决定了是"等事件"还是"等消息"；
2. 若等的是某个事件（多半来自 .NET 许可调用），就找到是谁应该 signal 它；
3. 若判定无解，则把本轮成果（许可全通 + 481 消除 + 进程保活）固化成可交付状态，
   并把"求解器可用 + Python 前后处理"作为可用方案交付。
"""

with io.open(DOC, "a", encoding="utf-8") as f:
    f.write(S)
print("ok")
