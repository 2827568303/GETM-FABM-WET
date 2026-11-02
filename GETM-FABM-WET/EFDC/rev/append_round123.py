import io

DOC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\破解进展.md"

S = """

## 一百二十三、六十五轮：**演示许可接口已被完整还原并跑通（success=True）**

### 1. 用 IL 反查拿到了响应结构（决定性）

对 `Flexnet.WrapperDongle.DemoLicense.GetResponse` 私方法取 IL 并解析 token，得到完整逻辑：

```csharp
var req  = (HttpWebRequest)WebRequest.Create(Settings.demoUrl + "<method>");
req.Method = "POST"; req.ContentType = "application/x-www-form-urlencoded";
req.KeepAlive = false;
// 写表单：authentizationcode=sdfsdg123123Adasdas123123123 + 各方法自己的字段
var text = new StreamReader(resp.GetResponseStream()).ReadToEnd();
var r = new JavaScriptSerializer().Deserialize<DemoRespone>(text);   // 关键
if (r.Status.CompareTo("Success") == 0) { success = true; }
else if (r.ReturnedData.CompareTo("-999") == 0) { ... }
XmlDocument doc; doc.LoadXml("<ReturnedData>" + r.ReturnedData + "</ReturnedData>");
```

`DemoRespone` 的字段就三个：**`Status` / `ReturnedData` / `Exception`**（PascalCase）。

### 2. 正确的响应（实测 success=True）

把 `rev/demo_resp.txt`（假服务器每次请求都重读）写成：

```json
{"Status":"Success","ReturnedData":"<status>ok</status>","Exception":""}
```

PowerShell 直调验证：

```
SignIn        -> success=True  inner=00oktrue
ActivateUser2 -> success=True  inner=00oktrue
```

### 3. 主程序已经打到这些接口

```
POST /wp-json/v2/eemsdemo/getupgradepackages   &authentizationcode=…
POST /wp-json/v2/eemsdemo/login                …&email=…&password=<md5>
POST /wp-json/v2/eemsdemo/activateuser2        …&email=…&machineId=DISK_SERIAL_NUM%3d2db6323c
```

各方法的表单字段（IL 直接读出）：

| 方法 | 端点 | 表单字段 |
|---|---|---|
| `SignIn` | `login` | authentizationcode, email, password(md5) |
| `SignIn2` | — | authentizationcode, email, machineId |
| `SendActivationCode` | `sendactivationemail` | authentizationcode, to, fullname, activationcode |
| `ActivateUser2` | `activateuser2` | authentizationcode, email, machineId |
| `DeactiveUser2` | — | 同上 |
| `GetUpgradePackages` | `getupgradepackages` | authentizationcode |

### 4. 仍然存在的 481（唯一剩余点）

现在 `activateuser2` 已经成功返回，但 VB 侧仍弹 `There is an error when checking the license. Error 481 (Invalid picture)`。
本轮已排除"缺图片文件"这一可能：hook `CreateFileW` 后**没有任何 bmp/jpg/ico/emf/.lic 文件被打开**。

exe 里的相关字符串提示了下一步方向：

```
004FCBD6 A  KspicPicture
005046B0 U  Picture
00504D54 U  Invalid Picture.
00504DFC U  Error loading picture into the DIB!
00525634 A  LoadPicture_DIBhandle
0052564C A  LoadPicture_FileName
```

即：**许可/激活返回的 `ReturnedData` 里应该带一块图片（DIB/BMP base64 之类），VB 侧把它塞进 Picture 属性；我们给的 `<status>ok</status>` 里没有这块数据 → Err 481。**

下一轮：把 `ReturnedData` 换成一个带图片数据的许可证 XML（先用 `C:\\Users\\Public\\DSI\\EEMS8.4\\license.lic` 的 822 字节 BMP 做 base64），
再逐个补齐 `ActivationID / FulfillmentID / FulfillDate / ExpirationDate / VersionDate / TotalCopies` 等字段，
让程序自己把 `EEMS.ini` 写成 `IsActivated=True`。
"""

with io.open(DOC, "a", encoding="utf-8") as f:
    f.write(S)
print("ok")
