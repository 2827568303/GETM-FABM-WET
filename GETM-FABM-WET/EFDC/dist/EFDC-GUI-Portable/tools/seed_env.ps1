# EFDC Explorer 8.4 - seed the demo login and the EFDC+ solver path (pure PowerShell)
# Usage: powershell -ExecutionPolicy Bypass -File seed_env.ps1 -AppDir "%LOCALAPPDATA%\EFDC84\app"
param(
    [string]$AppDir = "$env:LOCALAPPDATA\EFDC84\app",
    [string]$Email = 'zhang.san8888@gmail.com',
    [string]$Password = 'Efdc2026!'
)

$ErrorActionPreference = 'Continue'
$public = $env:PUBLIC
if (-not $public) { $public = 'C:\Users\Public' }

function Set-IniKeys([string]$path, [hashtable]$kv, [string]$section = $null) {
    if (-not (Test-Path (Split-Path $path))) { New-Item -ItemType Directory -Force -Path (Split-Path $path) | Out-Null }
    $lines = @()
    if (Test-Path $path) {
        try { $lines = [System.IO.File]::ReadAllLines($path) } catch { $lines = @() }
    }
    $enc = [System.Text.Encoding]::GetEncoding(28591)   # latin-1, same as the app
    $out = New-Object System.Collections.Generic.List[string]
    $done = @{}
    foreach ($l in $lines) {
        $k = $null
        if ($l -match '^\s*([^=]+)=') { $k = $matches[1].Trim() }
        if ($k -and $kv.ContainsKey($k)) {
            if (-not $done.ContainsKey($k)) { $out.Add("$k=$($kv[$k])"); $done[$k] = $true }
            continue
        }
        $out.Add($l)
    }
    if ($section -and -not ($out | Where-Object { $_.Trim() -eq "[$section]" })) {
        $out.Insert(0, "[$section]")
    }
    foreach ($k in $kv.Keys) {
        if (-not $done.ContainsKey($k)) { $out.Add("$k=$($kv[$k])") }
    }
    try {
        [System.IO.File]::WriteAllText($path, (($out -join "`r`n") + "`r`n"), $enc)
        Write-Host "  ok  $path"
    } catch {
        Write-Host "  skip $path  ($($_.Exception.Message))"
    }
}

# 1) demo login: email + password + remember
$loginIni = Join-Path $public 'DSI\EEMS8.3\EEMS.ini'
Set-IniKeys $loginIni @{
    demo_email              = $Email
    demo_password           = $Password
    demo_rememberpassword   = 'True'
} 'LicenseInfo'

# 2) EFDC+ solver path (needed by "Run EFDC" in the GUI)
$solver = $null
foreach ($n in @('EFDCPlus_084_OMP.exe', 'EFDCPlus_084_OMP_180718.PERPETUAL.exe', 'EFDCPlus_084_OMP_180718.exe')) {
    $p = Join-Path $AppDir $n
    if (Test-Path $p) { $solver = $p; break }
}
if ($solver) {
    $explorerIni = Join-Path $public 'DSI\EEMS8.4\EFDC_Explorer.ini'
    $cur = ''
    if (Test-Path $explorerIni) {
        foreach ($l in [System.IO.File]::ReadAllLines($explorerIni)) {
            if ($l -match '^EFDCPath0=(.*)$') { $cur = $matches[1].Trim() }
        }
    }
    if (-not ($cur -and (Test-Path $cur))) {
        Set-IniKeys $explorerIni @{ EFDCPath0 = $solver }
    } else {
        Write-Host "  ok  solver already set: $cur"
    }
} else {
    Write-Host "  !! solver exe not found in $AppDir"
}
