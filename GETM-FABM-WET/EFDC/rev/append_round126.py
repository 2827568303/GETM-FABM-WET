import io

DOC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\破解进展.md"

S = """

## 一百二十六、六十八轮：窗体"看得见但空白"——证明 `Show`/`Form_Load` 从未执行

### 1. 在进程退出前强行接管，第一次真正看到窗口

`rev/diag39.js`：hook `RtlExitUserProcess`，退出前枚举本进程窗口 →
发现 `ThunderRT6FormDC "EFDC_Explore8.0"` **还在**（vis=0）→ `ShowWindow(SW_SHOW)` → **vis=1**，
然后进入自建 `GetMessage/DispatchMessage` 循环阻止退出。

截图（`rev/app_shot.png`，815×639）：标题栏 `EFDC_Explore8.0`，**客户区完全空白**。

### 2. 结论（重要）

窗口空白 = 窗体的 **`Form_Load` 从未运行**（VB6 里控件是在 Form_Load/Show 时创建的）。
也就是说：**程序建了窗体对象、但从来没有调用 `Show`**，所以 Sub Main 一返回，运行时发现"没有可见窗体"就退出。

### 3. 尝试直接调用疑似 `Show` 的槽位（未成功）

在窗体创建点 `0x156ABA0` 之后取全局对象 `[0x16249B0]`（obj=`0xd3e9730`，vtable=`0x163C1F4`），
按 `0x156AD74` 的调用约定 `method[0x250](obj, &VARIANT)` 直接调：

```
call threw: Error: access violation accessing 0x0
```

→ 说明 `0x250` 这个槽的真实签名/前置条件与我猜的不同（VB6 的 thunk 需要特定的参数布局，
或需要先完成某些初始化）。**不能靠猜，要按 VB6 运行时的分发规则来找 Show 的槽位。**

### 4. 下一轮的两种确定做法

1. **枚举法（安全版）**：hook 窗体对象 vtable 的每个入口（`vt+0..0x400`），记录启动过程中**实际被调用**的槽；
   再对照"正常授权机器"上会多出哪一次调用 —— 少的那次就是 Show。为了不崩，先用 `Interceptor.attach`
   只记录、不在内部调用。
2. **静态法**：VB6 窗体方法 ID 是编译期常量，`Show` 的 ID 会以 `call dword ptr [eax+ID*4]` 出现在 exe 里。
   我们已经知道两个 ID：`0x1B8/4=0x6E`（属性 getter）、`0x250/4=0x94`。把 exe 里所有
   `call dword ptr [reg+imm]` 的 imm 统计出来，`Show` 极可能就是那个"只在授权路径上出现"的 imm。

### 5. 当前可复现状态

- 假服务器：`rev/fakedemo2.py`（按端点分流），响应文件 `rev/demo_resp.txt` / `rev/demo_resp_packages.txt`；
- 原版 exe 在 `C:\\EFDC84_RUN`，配置已指向 `127.0.0.1:8080`；
- 运行脚本：`rev/longwatch.py`（时序）、`rev/diag39.js`（退出前强显 + 接管消息循环）、`rev/shot_app.py`（截图）；
- 已知：窗体 3.0s 创建、9.2s 退出、全程 vis=0、客户区空白。
"""

with io.open(DOC, "a", encoding="utf-8") as f:
    f.write(S)
print("ok")
