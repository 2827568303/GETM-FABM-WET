import io

DOC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\破解进展.md"

S = """

## 一百二十九、七十一轮：**481 彻底解决**（OleLoadPictureEx 替换）+ 许可被判定为"已激活"

### 1. 481 的真正来源（本轮抓到了）

hook 全部 OLE 图片 API，在 481 弹框前抓到唯一一次调用：

```
2760 CALL OleLoadPictureEx
2762   RET OleLoadPictureEx hr=0x80004005   ← E_FAIL
2763 === MSGBOX === (481 Invalid picture)
```

**一次 `OleLoadPictureEx` 失败（E_FAIL）就足以让 VB 抛 481。** 之前几轮 hook 没命中，是因为钩子脚本本身的问题。

### 2. 修复办法（`rev/diag51.js`，已实测生效）

在 `OleLoadPictureEx` 返回失败时，用 GDI 造一张 16×16 位图，再走
`OleCreatePictureIndirect` 生成真 `IPicture`，写回第 8 个参数（`ppvObj`），并把返回值改成 `S_OK`：

```
2406 SUBSTITUTE hr_orig=0x80004005 -> create=0x0  ppv=0x1af8f8
```

**结果：481 弹框彻底消失**（连续多次运行都不再出现），程序继续往下走。

### 3. 另一个关键发现：许可被判为"已激活"

把**完整**的 LicenseInfo 写进 `C:\\Users\\Public\\DSI\\EFDC_Explorer8.0\\EFDC_Explorer.ini`
（这个目录才是程序实际读取的位置！），`ee_activation.log` 里立刻出现：

```
6.  Check if the computer is already activated or not.
6.1 The license is activated. LicenseCode: A0ABBD96-D22B-46A2-AD1A-6D4FB37DAA47
6.1.1 Compare the client time with server time
6.1.2 Check valid Product Features      ← 走到这里
```

即：**许可检查已经通过**（不再走 demo 激活），现在卡在"6.1.2 校验产品特性"之后的某一步。

### 4. 当前状态（本轮结束）

| 项 | 状态 |
|---|---|
| 死域名 HTTPS | 已用本地假服务器顶替（config 重加密） |
| demo 接口 | 全部还原（含 packages 专用结构），`success=True` |
| 481 | **已消除**（`diag51.js` 的 OleLoadPictureEx 替换） |
| 许可判定 | **已激活**（完整 INI 写入 `EFDC_Explorer8.0\\EFDC_Explorer.ini`） |
| 窗体 | 2.5s 创建 `ThunderRT6FormDC "EFDC_Explore8.0"`，仍 `vis=0`，8.9s 退出（Sub Main 返回） |

### 5. 下一轮

1. 顺藤摸瓜找"6.1.2 校验产品特性"之后的代码：日志到此为止，说明特性校验后程序直接结束；
   大概率特性名/特性列表不匹配（我们的 INI 里 `FeatureName` 与程序期望不一致），
   或者 5 处旧补丁把流程导向了"静默结束"；
2. 建议先**回退 5 处旧补丁**（改用原版 exe + 假服务器 + 图片补丁 + 完整 INI），
   看窗体是否会被 `Show` 出来——因为许可现在已经是"已激活"，原版路径才应该走正常 UI 流程；
3. 若仍不 Show，再回到 vtable 槽位枚举（`rev/diag41.js`）找 `Show`。
"""

with io.open(DOC, "a", encoding="utf-8") as f:
    f.write(S)
print("ok")
