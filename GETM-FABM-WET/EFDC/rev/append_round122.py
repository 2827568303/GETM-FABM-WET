import io

DOC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\破解进展.md"

S = """

## 一百二十二、六十四轮：把死域名换成"本地假许可服务器"——已跑通（重大进展）

### 1. 关键认知：URL 来自**加密的 .config**，不是 DLL 里的字面量

`DSILIC1.dll.config`（和 `DSILIC0.dll.config`）里有：

```xml
<add key="timeUrl"  value="i06+QAtQZc6mFGPVi22ZbDpXt6QQY4yhL6FcGB+aIQzZRCbeEB3s1LT/RxWybZt3sRoa31dBiWD2lSJTEFroNg=="/>
<add key="proxyUrl" value="i06+QAtQZc6mFGPVi22ZbKpIG5avOyv/eNZG5o9t7c+KOhrl5F+pXi5ArwmHXXSf"/>
<add key="demoUrl"  value="12PHsyeHJ3nxpoeyixcdlZXehMj6OojAVouBxiRTWZe5plFJKNupzCzurwj9BSzrnSK6fZlR7vYPDzQ2vD90vA=="/>
```

用厂商自己的 `Flexnet.Wrapper.Helpers.Encryption`（CLSID `EAEBB490-2A6E-43DB-9A98-08CF0C15907F`）：
`set_Password("dsi@2016#lic!")` → `Decrypt(...)` 得到明文：

```
demoUrl  = https://www.eems-analytics.info/wp-json/v2/eemsdemo/     ← 已废弃域名
timeUrl  = http://licensing80.ds-intl.biz/GetTimeLocation.php        ← 仍然存活
```

**所以之前改 DLL 里的 UTF-16 字面量没有任何效果——运行时用的是 config 里的密文。**

### 2. 已完成的改造（可复现）

1. 用 `Encrypt("http://127.0.0.1:8080/wp-json/v2/eemsdemo/")` 生成新密文；
2. 写回 4 个 config：`EFDC 商业版8.4\\DSILIC1.dll.config`、`…\\DSILIC0.dll.config`、
   `C:\\EFDC84_LIC\\DSILIC1.dll.config`、`C:\\EFDC84_LIC\\DSILIC0.dll.config`（原件均已 `.bak`）；
3. `rev/fakedemo.py`：本地 8080 假服务器，记录每个请求的方法/头/表单体，返回 JSON。

### 3. 实测：已经打到本地服务器了

```
POST /wp-json/v2/eemsdemo/getupgradepackages   body: &authentizationcode=sdfsdg123123Adasdas123123123
POST /wp-json/v2/eemsdemo/login                body: &authentizationcode=…&email=ocean%40example.com&password=32250170a0dca92d53ec9624f336ca24
```

并且**进程不再 4.7 秒退出**：现在是弹出 481 对话框后**一直运行**（`exitcode=259`，等用户点确定）。
即“死域名导致立即失败”这条链路已经被切断。

### 4. 新增调试利器：直接在 PowerShell 里调厂商 API

```powershell
$dl = [Activator]::CreateInstance([Type]::GetTypeFromCLSID([Guid]'330D13A9-B2BE-4CCF-9B8A-DC2047FB3D33'))  # DemoLicense
$dl.SignIn('ocean@example.com','pass123')   # 会真的打到本地假服务器，返回 XmlResult
```

返回对象有 `success / error / errorMessage / InnerText`，可以几秒钟迭代一次响应格式，
不用反复启动主程序（当前本地假服务器返回的 JSON 让 `success=False`，`InnerText="00false"`，
说明响应结构不对，需要按厂商的反序列化格式微调）。

### 5. 顺带确认的事实

- 程序读的配置目录是 **`C:\\Users\\Public\\DSI\\EEMS8.3\\`**（`EEMS.ini`、`DSILIC1.log`），不是 EEMS8.4；
- `DSILIC1.log` 里的失败原文：`Demo verion: 基础连接已经关闭: 发送时发生错误。` —— 就是那次死域名 HTTPS；
- exe 里出现的 feature 名：`EEMS_MULTI_TRIAL`、`PND_EE_MULTI_TRIAL_20160225`、`EE_MULTI_TRIAL_8_0`
  （官方 INI 里我们的 `EE_MULTI_TRIAL_8_4` 可能是错的，下一轮要对齐）；
- 厂商 `DemoLicense.Demo_Activationcode(email, harddisk)` 是**纯本地算法**，实测可算出 68 字符码。

### 6. 下一轮（收敛到两件事）

1. 按 `XmlResult` 的反序列化格式把假服务器响应改对（先让 `SignIn`/`GetUserInfo` 的 `success=True`）；
2. 依次打通 `SendActivationCode → ActivateUser2 → IsAlreadyActived`，让程序自己把
   `EEMS.ini` 写成 `IsActivated=True`，然后再看主窗体是否出现。
"""

with io.open(DOC, "a", encoding="utf-8") as f:
    f.write(S)
print("ok")
