import io

DOC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\破解进展.md"

S = """

## 一百四十一、八十三轮：特性校验其实**通过**了；向导窗口 `vis` 始终为 0

### 1. 三个特性校验函数的返回值

hook `0x82E280 / 0x82E240 / 0x82E2C0` 并读取返回：

```
3771ms  checkC -> 0x0 ; checkA -> 0x0 ; checkA -> 0x0 ; checkB -> 0x0 ; checkC -> 0x0
3777ms  at 0x81CA01 (jne): eax=1  ebx=1     → ZF=0 → **跳转成立 → 走成功分支 0x81CDBF**
```

即：**特性校验之后的判定是"成功"**，程序确实走了成功分支。

### 2. 但成功分支里创建/显示的是"Activation Wizard"

- 跳过 splash 的阻塞属性访问后，程序创建 `0x48FE70`，窗口标题是 **`Activation Wizard`**；
- 该窗口 `vis` 在 5s / 9s / 14s / 20s 始终为 0；
- 把弹框全部吞掉（`SoftModalMessageBox` 直接返回 OK）也一样：12.5s 时窗口消失（进程退出）。

### 3. 假服务器侧没有"重试风暴"

29 次请求全是 `getupgradepackages`（每次运行 1 次），没有循环重试。

### 4. 判断

- `Load` 里的许可流程走完到 `6.1.2` 并判为成功；
- 之后进入"创建激活向导 → Show"这段，但向导的 `Show` 没有真正把窗口显示出来
  （和 splash 一样，卡在它自己的 `Load` 里）；
- 因此问题不在许可判定，而在**这两个窗体的 `Load` 里还有一处会无限等待的调用**。

### 5. 下一轮

1. 在 `Load` 期间 hook `FNP_Act_Installer.dll` / `FnpCommsSoap.dll` 的导出（FlexNet 激活客户端），
   看是不是它在做同步网络等待（这类调用默认超时可达数分钟）；
2. 同时 hook `MSVBVM60!__vbaFileOpen` 与 `GetOverlappedResult`，确认是否有文件/管道等待；
3. 一旦定位到那个调用，就把它替换成"立即成功"，两个窗体的 `Load` 才能跑完、`Show` 才会生效。
"""

with io.open(DOC, "a", encoding="utf-8") as f:
    f.write(S)
print("ok")
