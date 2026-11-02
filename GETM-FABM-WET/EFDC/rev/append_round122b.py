import io

DOC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\破解进展.md"

S = """

### 一百二十二·补充：响应格式的试探结果（下一轮从这里接着做）

假服务器响应可热改（`rev/demo_resp.txt`，`rev/fakedemo.py` 每次请求都重读），
用 PowerShell 直调 `DemoLicense.SignIn` 做秒级迭代。已试过的 14 种响应**全部** `success=False`：

```
{"status":"success"} / {"result":"success","code":"0"} / {"success":true} / {"status":"ok","message":"ok"}
{"error":0,"message":"ok"} / {"code":"0","msg":"ok"} / {"status":1} / ok / {"data":{"status":0,…}}
{"status":"0","code":"0","data":{…}} / <Response>…</Response> / {"success":"true",…} / {"status":true,"error":0}
{"StatusCode":0,"Message":"ok","Data":true}
```

返回对象始终是 `success=False, error=0, errorMessage="", InnerText="00false"`，
说明 `XmlResult` 的这几个字段是 .NET 侧自己拼的，跟响应内容无关；
**真正要满足的是 `DemoLicense` 内部那个 DTO 的反序列化结果**。

下一轮的正确做法（已明确）：把 `DemoLicense.SignIn` 的 IL 取出来
（`[Reflection.Assembly]::Load(bytes).GetType('Flexnet.WrapperDongle.DemoLicense').GetMethod('SignIn').GetMethodBody().GetILAsByteArray()`），
用 Python 解 IL + 解析 token，找出 `JsonConvert.DeserializeObject<T>` 里的 **T 类型**，
再反射出 T 的**属性名**，按属性名构造 JSON —— 一次就能对上。
"""

with io.open(DOC, "a", encoding="utf-8") as f:
    f.write(S)
print("ok")
