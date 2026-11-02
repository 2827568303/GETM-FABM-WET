import io

DOC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\破解进展.md"

SECTION = """

### 一百一十八·补充：抓到真实外联请求（本轮最有价值的单点证据）

用 `rev\\diag6.js` 在 `ws2_32!send` 层直接抓明文，启动 2.3s / 3.0s 各抓到一次代理隧道握手：

```
SEND [109B] from System.ni.dll+0x21bf84:
CONNECT www.eems-analytics.info:443 HTTP/1.1
Host: www.eems-analytics.info
Proxy-Connection: Keep-Alive

SEND [125B] from System.ni.dll+0x21bf84:
<TLS ClientHello，SNI = www.eems-analytics.info>
```

**结论（三条，全部是新的）**

1. 发起方是 **.NET（`System.ni.dll`）**，不是 VB6 的 msxml3/WinHttp——即进程里跑的托管代码（FlexNet 包装）在做
   `https://www.eems-analytics.info/...` 的 Demo 发证/校验调用；这个域名正是前几轮验证过**已不存在**的那个。
2. 它走的是**系统代理**（`HKCU\\...\\Internet Settings` 里 `ProxyEnable=1`、`ProxyServer=127.0.0.1:7897`），
   所以先发 `CONNECT`，再发 TLS ClientHello——停在 TLS 握手，之后 CPU 归零。
3. 因此"启动卡住"的核心是**一次永远完不成的 HTTPS 调用**（死域名 + 本地代理），而 `Sleep(30000)`、
   WinHTTP 20s 超时、`MsgWait(24063)` 都是围绕它的等/重试。

**本轮做过的对照实验（都记录在 `rev\\diag*_out.txt`）**

| 实验 | 结果 |
|---|---|
| `diag3.js`：`ws2_32!connect` 立即失败 | 一次 connect 都没发生；现象不变（0% CPU、零窗口） |
| 关闭系统代理（`ProxyEnable=0`）后启动（`diag7_out.txt`） | 仍 0% CPU、零窗口（已恢复原代理设置） |
| 关闭"自动拨号"（`EnableAutodial=0`/`NoNetAutodial=1`）| 现象不变（已还原） |
| `diag4.js`：命名内核对象全量枚举 | 无任何 EEMS/EFDC 相关 Mutex/Event → 排除单实例互斥体 |

**下一步唯一最短路径（已收敛）**

1. 把 `www.eems-analytics.info` 本地顶替：`hosts` 加 `127.0.0.1 www.eems-analytics.info`，本机起 443 端口的
   证书服务（自签 + 导入受信任根），按 FlexNet Operations 的 SOAP 返回一个"已验证/已授权"响应；
   或在 `DSILIC0.dll`（.NET，无混淆）里把发起请求的方法改成直接返回成功对象。
2. 该调用一旦秒回"成功/失败"，主线程就能从这条阻塞里出来，后面才是主窗体 `frmEFDC_Explorer` 的创建与显示。
3. 反编译配合：`DSILIC0.dll` 里 `Flexnet.Wrapper.FlexWrapper`（CLSID `E326A913-D0B1-44E2-8015-952959CEA45F`）
   与 `Flexnet.WrapperDongle.DemoLicense.Demo_Activationcode(email, harddisk)`（**本地计算**，无需联网）
   是两条可直接改写的入口。
"""

with io.open(DOC, "a", encoding="utf-8") as f:
    f.write(SECTION)
print("ok", len(SECTION))
