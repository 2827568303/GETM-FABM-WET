<#
   3DWET 文件夹选择器 —— 备用方案
   ------------------------------------------------------------
   仅在服务进程本身无法创建 Tk 窗口时，由 server.py 回退调用。
   弹出 Windows 资源管理器风格的「浏览文件夹」对话框，用户选定后把 JSON
   写入 <app>\.picker_result.json，前端轮询该文件即可拿到路径。

   用法: powershell -ExecutionPolicy Bypass -Sta -File pick_folder.ps1 -StartDir "D:\mycases"

   注意: 必须保留 -Sta（单线程单元）。System.Windows.Forms 的对话框在 MTA
         下会出现 "EnsureThreadState" 之类的异常。
         **不要加 -WindowStyle Hidden** —— 被隐藏窗口拥有的 WinForms 对话框
         在很多会话下根本不会显示（这正是最初「点了没反应」的原因）。
#>
param(
    [string]$StartDir = ""
)

$ErrorActionPreference = "Stop"
$resultFile = Join-Path $PSScriptRoot '.picker_result.json'

$chosen = ''
try {
    Add-Type -AssemblyName System.Windows.Forms | Out-Null
} catch {
    Add-Type -Path (Join-Path ([System.Runtime.InteropServices.RuntimeEnvironment]::GetRuntimeDirectory()) 'System.Windows.Forms.dll') | Out-Null
}

$dialog = New-Object System.Windows.Forms.FolderBrowserDialog
$dialog.Description        = "选择 GETM 案例目录（须含 getm.inp 或 bathymetry.nc）"
$dialog.ShowNewFolderButton = $true
if ($StartDir -and (Test-Path -LiteralPath $StartDir)) {
    $dialog.SelectedPath = $StartDir
} else {
    $dialog.SelectedPath = $PSScriptRoot
}

if ($dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
    $chosen = $dialog.SelectedPath
}

# 前端按 JSON 解析；被取消时写 path:"" 以区分「还没操作」与「用户取消」
$payload = '{"path":' + (ConvertTo-Json $chosen -Compress) + ',"error":"","engine":"powershell(回退)"}'
[System.IO.File]::WriteAllText($resultFile, $payload, (New-Object System.Text.UTF8Encoding $false))
