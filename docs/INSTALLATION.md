# 3DWET Studio Windows 安装说明

分发文件是 `release/3DWETStudio-Setup.exe`。双击后按向导安装；安装前会显示中文运行环境说明，并检查桌面模式的系统依赖。支持 Windows 10 1607 或更新版本、Windows 11，x64。

## 安装内容

安装包包含应用的 Python 运行环境，以及 Flask、NumPy、SciPy、netCDF4、PyYAML、pyshp、pyproj、psutil、Waitress、pywebview 和必要依赖。无需另装 Python、运行 pip 或修改系统 PATH。

模型部分包含 GETM/FABM/WET 可执行程序、原生 DLL、NetCDF/HDF5 和 Fortran/OpenMP 运行库，以及示例案例和模板。具体构建版本见安装目录中的 `DEPENDENCIES.txt`；第三方许可见 `THIRD_PARTY_LICENSES` 和 `3DWET/bin/runtime/licenses`。模型源码与构建配方随 `MODEL_SOURCE.zip` 提供；修改 Fortran 源码后重新编译仍需另行配置编译工具链。

桌面窗口使用 Microsoft WebView2 Runtime。安装器按[微软说明](https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/distribution)检查 HKLM 32 位视图与 HKCU 中的 WebView2 `pv` 版本值；已有运行时则直接使用，缺少时运行内置的 x64 Evergreen Standalone 离线安装程序。这个操作不需要联网下载运行时。Microsoft Edge Update 可能随后自动更新共享的 WebView2 Runtime。

安装器以当前用户权限运行，不会默认要求管理员权限。组织策略或安全软件阻止 WebView2 安装时，向导显示退出码和修复说明，并停止应用安装。桌面窗口也依赖 Windows 自带的 .NET Framework 4.6.2 或更新版本；该组件缺失时向导停止，提示通过 Windows 更新或微软安装程序修复。

## 启动与数据

默认目录为 `%LOCALAPPDATA%\Programs\3DWET Studio`。开始菜单包含桌面模式和浏览器模式；安装时可以创建两种模式的桌面快捷方式。直接运行 `3DWETStudio.exe` 打开桌面窗口，`3DWETStudio.exe --web` 使用默认浏览器。

案例及其输入、模型输出位于安装目录的 `3DWET\case`。升级安装只添加不存在的初始案例文件，保留已经修改的文件。卸载保留案例、模型输出和安装后新增的用户文件；再次安装到同一目录即可继续使用。用户日志位于 `%LOCALAPPDATA%\3DWET Studio\logs`，卸载也保留日志。卸载不移除其他应用共用的 Microsoft WebView2 Runtime。

安装器日志默认由 Inno Setup 写入当前用户临时目录（`Setup Log ... .txt`）。也可在命令行使用 `/LOG="C:\path\install.log"` 指定日志位置。遇到依赖检查失败时，先查看向导错误和日志，再按提示修复并重新运行安装器。

## 开发者构建

先从仓库根目录使用已安装构建依赖的项目虚拟环境打包应用：

```powershell
.venv\Scripts\python.exe scripts/build_app.py
```

脚本生成 `release/stage/3DWETStudio`。该目录必须包含 `3DWETStudio.exe`、`_internal`、`3DWET/bin/getm_cartesian.exe`、`3DWET/bin/runtime`、`3DWET/case`、`DEPENDENCIES.txt` 和包含实际许可文件的 `THIRD_PARTY_LICENSES`。安装器排除暂存目录中的 `3DWET/app` 状态文件和 `3DWET/.studio-runtime` 临时工作文件；应用资源由 `_internal` 提供。

然后从仓库根目录运行：

```powershell
.\scripts\build_installer.ps1 -AppVersion 1.0.0
```

产物为 `release/3DWETStudio-Setup.exe`，同时生成含大小、SHA256 和前置组件来源的 `release/installer-manifest.json`。脚本也接受 `-StageDir` 和 `-OutputDir`。只准备构建工具可运行 `-PrepareToolsOnly`。

安装后可在关闭所有 Studio 窗口、没有模型运行时验证实际安装目录。下面的报告路径由 `LOCALAPPDATA` 展开为绝对路径（例如 `C:\Users\23801\AppData\Local\3DWET Studio\reports\self-test.json`），不接受相对路径：

```powershell
$studioExe = Join-Path $env:LOCALAPPDATA 'Programs\3DWET Studio\3DWETStudio.exe'
$selfTestReport = Join-Path $env:LOCALAPPDATA '3DWET Studio\reports\self-test.json'
$uiSmokeReport = Join-Path $env:LOCALAPPDATA '3DWET Studio\reports\ui-smoke.json'
Start-Process -FilePath $studioExe -ArgumentList @('--self-test', '--report', ('"' + $selfTestReport + '"')) -Wait
Start-Process -FilePath $studioExe -ArgumentList @('--ui-smoke', '--report', ('"' + $uiSmokeReport + '"')) -Wait
Get-Content -LiteralPath $selfTestReport, $uiSmokeReport
```

`--self-test` 验证打包依赖、HTTP 服务、主要界面响应和模型运行库加载；`--ui-smoke` 打开一个测试桌面窗口，验证 WebView2 实际渲染后自动关闭，并写出 JSON 报告。检查报告中的成功状态；这些启动检查不能代替具体案例的科学计算验证。自定义了安装目录时，应将 `$studioExe` 改为实际程序的完整路径。

构建工具和 WebView2 离线安装文件缓存于忽略的 `build/installer-tools`。下载来源及固定 SHA256 记录在 `scripts/installer/downloads.json`；构建时同时要求数字签名有效，发布者分别为 Microsoft Corporation 和 Pyrsys B.V.。Inno Setup 编译器从[官方分发页](https://jrsoftware.org/isdl.php)指向的版本安装到任务目录。缓存完整后，构建不需要重新下载这些文件。升级 WebView2 固定包时，应从[微软官方下载页](https://developer.microsoft.com/en-us/microsoft-edge/webview2/)重新获取 x64 离线包，检查 Authenticode 发布者并更新来源、大小和 SHA256，不能跳过校验。

应用安装器自身若未配置项目代码签名证书，会以未签名文件发布；Windows SmartScreen 可能显示未知发布者提示。下载的 Microsoft 和 Inno Setup 前置组件签名验证与应用自身代码签名是两个不同的检查。
