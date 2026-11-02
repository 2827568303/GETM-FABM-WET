# unblock_package.ps1 - clear the "downloaded from the internet" mark (Mark-of-the-Web)
# from the files EFDC Explorer loads at run time.
#
# Why: a zip downloaded by a browser tags every extracted file with a Zone.Identifier
# stream. The .NET licence wrapper (DSILIC1.dll / DSILIC0.dll) then refuses to load with
#   0x80131515 "Operation is not supported ... loadFromRemoteSources"
# and the app stops with "The licenseWrapper is not valid ...".
#
# Usage: powershell -ExecutionPolicy Bypass -File unblock_package.ps1 [-AppDir <mirror>]
# Note: paths are normalised here, so callers may pass values with a trailing backslash
# or stray quotes (cmd line "%SELF%" ends with a backslash and used to break the call).

param(
    [string]$AppDir = "$env:LOCALAPPDATA\EFDC84\app",
    [string]$PkgDir = "",
    [string]$Vb6Dir = "$env:LOCALAPPDATA\EFDC84\vb6"
)

$ErrorActionPreference = "SilentlyContinue"
$script:count = 0

function Normalize-Dir([string]$p) {
    if ([string]::IsNullOrWhiteSpace($p)) { return "" }
    $p = $p.Trim()
    $p = $p.Trim('"').Trim("'")
    $p = $p.TrimEnd('\', '/')
    return $p
}

function Test-Dir([string]$p) {
    if ([string]::IsNullOrWhiteSpace($p)) { return $false }
    try { return [System.IO.Directory]::Exists($p) } catch { return $false }
}

function Test-File([string]$p) {
    if ([string]::IsNullOrWhiteSpace($p)) { return $false }
    try { return [System.IO.File]::Exists($p) } catch { return $false }
}

function Unblock-Tree([string]$dir) {
    if (-not (Test-Dir $dir)) { return 0 }
    $n = 0
    try {
        foreach ($f in [System.IO.Directory]::EnumerateFiles($dir, "*", [System.IO.SearchOption]::AllDirectories)) {
            try {
                Unblock-File -LiteralPath $f -ErrorAction SilentlyContinue
                $script:count++
                $n++
            } catch { }
        }
    } catch { }
    return $n
}

$AppDir  = Normalize-Dir $AppDir
$Vb6Dir  = Normalize-Dir $Vb6Dir
$PkgDir  = Normalize-Dir $PkgDir
if (-not (Test-Dir $PkgDir)) {
    # fall back to the folder this script lives in: <package>\tools -> <package>
    try { $PkgDir = Split-Path -Parent (Split-Path -Parent $PSCommandPath) } catch { $PkgDir = "" }
    $PkgDir = Normalize-Dir $PkgDir
}

# 1) the mirrored app dir (this is what COM / fusion actually loads)
$a = Unblock-Tree $AppDir
# 2) the package copy (used when someone starts the exe straight from the package folder)
$b = Unblock-Tree (Join-Path $PkgDir "app")
# 3) the VB6 controls mirrored next to the app
$c = Unblock-Tree $Vb6Dir
# 4) the launcher's own scripts
$d = 0
foreach ($rel in @("attach_signin.py", "register_net.ps1", "register_controls.ps1",
                   "start_stub.ps1", "seed_env.ps1", "fix_proxy.ps1")) {
    $p = Join-Path (Join-Path $PkgDir "tools") $rel
    if (Test-File $p) {
        try { Unblock-File -LiteralPath $p -ErrorAction SilentlyContinue; $d++ } catch { }
    }
}

Write-Host ("  ok  unblocked {0} files (app {1}, pkg {2}, vb6 {3}, tools {4})" -f $script:count, $a, $b, $c, $d)
exit 0
