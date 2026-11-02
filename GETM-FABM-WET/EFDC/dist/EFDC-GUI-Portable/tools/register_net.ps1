# register_net.ps1 - register the .NET licence wrapper (DSILIC0.dll / DSILIC1.dll) for the
# current user so that EFDC Explorer's CreateObject() can build its FlexNet objects.
#
# The wrapper assembly exposes ~765 COM classes; the vendor install registers every one of
# them with "RegAsm /codebase".  tools\com_classes.tsv holds that exact class table
# (CLSID + ProgID + Class + Assembly) captured from a working machine, so we do not have to
# guess which ProgID the application asks for.
#
# 1st pass: HKEY_CURRENT_USER            (no admin needed)
# 2nd pass: HKEY_LOCAL_MACHINE           (only when this script is elevated)
# Then a real COM activation test runs in this 32-bit host.
#
# Usage: powershell -ExecutionPolicy Bypass -File register_net.ps1 -AppDir "<mirror>"

param(
    [string]$AppDir = "$env:LOCALAPPDATA\EFDC84\app"
)

$ErrorActionPreference = "Continue"

if (-not (Test-Path $AppDir)) { Write-Host "  !! app dir not found: $AppDir"; exit 1 }

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator)

$runtime = "v4.0.30319"
$here = Split-Path -Parent $PSCommandPath
$tablePath = Join-Path $here "com_classes.tsv"

# ------------------------------------------------------------------ class table
function Get-ClassTable {
    $rows = @()
    if (Test-Path $tablePath) {
        foreach ($line in [System.IO.File]::ReadAllLines($tablePath)) {
            if ([string]::IsNullOrWhiteSpace($line)) { continue }
            $p = $line.Split("`t")
            if ($p.Count -lt 4) { continue }
            $rows += [pscustomobject]@{ Guid = $p[0]; ProgId = $p[1]; Class = $p[2]; Assembly = $p[3] }
        }
    }
    return $rows
}

function Get-ReflectedTable {
    $rows = @()
    foreach ($dll in @("DSILIC0.dll", "DSILIC1.dll")) {
        $p = Join-Path $AppDir $dll
        if (-not (Test-Path $p)) { continue }
        try { $asm = [System.Reflection.Assembly]::LoadFrom($p) } catch { continue }
        foreach ($t in $asm.GetTypes()) {
            if (-not $t.IsPublic) { continue }
            $gi = $t.GetCustomAttributes([System.Runtime.InteropServices.GuidAttribute], $false)
            if ($gi.Count -eq 0) { continue }
            $rows += [pscustomobject]@{
                Guid = "{" + $gi[0].Value.ToUpper() + "}"
                ProgId = $t.FullName
                Class = $t.FullName
                Assembly = $asm.GetName().FullName
            }
        }
    }
    return $rows
}

$classes = Get-ClassTable
if ($classes.Count -eq 0) {
    Write-Host "  .. class table missing, falling back to reflection"
    $classes = Get-ReflectedTable
}
if ($classes.Count -eq 0) { Write-Host "  !! no COM classes to register"; exit 4 }
Write-Host ("  class table: {0} entries ({1})" -f $classes.Count, $(if (Test-Path $tablePath) { "com_classes.tsv" } else { "reflection" }))

function Get-RootKey([string]$hive) {
    if ($hive -eq "HKLM") { return [Microsoft.Win32.Registry]::LocalMachine }
    return [Microsoft.Win32.Registry]::CurrentUser
}

function Set-RegString {
    param([string]$hive, [string]$KeyPath, [string]$Name, [string]$Value)
    try {
        $k = (Get-RootKey $hive).CreateSubKey($KeyPath)
        if ($null -eq $k) { return $false }
        $k.SetValue($Name, $Value, [Microsoft.Win32.RegistryValueKind]::String)
        $k.Close()
        return $true
    } catch { return $false }
}

function Register-Classes {
    param([string]$hive)
    $roots = @("Software\Classes", "Software\Classes\WOW6432Node")
    $written = 0; $skipped = 0; $failed = 0
    foreach ($c in $classes) {
        $dll = if ($c.Assembly -match '^DSILIC0') { "DSILIC0.dll" } else { "DSILIC1.dll" }
        $codeBase = "file:///" + ((Join-Path $AppDir $dll) -replace '\\', '/')
        foreach ($root in $roots) {
            $p = "$root\CLSID\$($c.Guid)"
            $cur = $null
            try { $cur = (Get-RootKey $hive).OpenSubKey("$p\InprocServer32") } catch { }
            if ($cur) {
                $sameClass = $cur.GetValue("Class"); $sameAsm = $cur.GetValue("Assembly"); $sameCb = $cur.GetValue("CodeBase")
                $cur.Close()
                if ($sameClass -eq $c.Class -and $sameAsm -eq $c.Assembly -and $sameCb -eq $codeBase) { $skipped++; continue }
            }
            $ok = @(
                (Set-RegString $hive $p "" $c.ProgId),
                (Set-RegString $hive "$p\InprocServer32" "" "mscoree.dll"),
                (Set-RegString $hive "$p\InprocServer32" "Class" $c.Class),
                (Set-RegString $hive "$p\InprocServer32" "Assembly" $c.Assembly),
                (Set-RegString $hive "$p\InprocServer32" "RuntimeVersion" $runtime),
                (Set-RegString $hive "$p\InprocServer32" "CodeBase" $codeBase),
                (Set-RegString $hive "$p\InprocServer32" "ThreadingModel" "Both"),
                (Set-RegString $hive "$p\ProgID" "" $c.ProgId),
                (Set-RegString $hive "$root\$($c.ProgId)" "" $c.ProgId),
                (Set-RegString $hive "$root\$($c.ProgId)\CLSID" "" $c.Guid)
            )
            if ($ok -contains $false) { $failed++ } else { $written++ }
        }
    }
    return @{ Written = $written; Skipped = $skipped; Failed = $failed }
}

function Test-ComActivation([string]$progId) {
    $r = @{ Ok = $false; Error = ""; Where = "" }
    try {
        $t = [type]::GetTypeFromProgID($progId, $true)
        if ($null -eq $t) { $r.Error = "ProgID not found: $progId"; return $r }
        $o = [Activator]::CreateInstance($t)
        if ($null -eq $o) { $r.Error = "CreateInstance returned null: $progId"; return $r }
        $r.Ok = $true
        try { $r.Where = $o.GetType().Assembly.Location } catch { }
        try { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($o) } catch { }
    } catch { $r.Error = $_.Exception.GetBaseException().Message }
    return $r
}

$probeIds = @(
    "Flexnet.WrapperDongle.FlexWrapperDongle",
    "Flexnet.Wrapper.Dongle.LicenseService.LicenseService",
    "Flexnet.WrapperDongle.DemoLicense"
)

# ------------------------------------------------------------------ per-user first
$r = Register-Classes "HKCU"
Write-Host ("  HKCU: {0} written, {1} already ok, {2} failed" -f $r.Written, $r.Skipped, $r.Failed)

$comOk = $true
foreach ($id in $probeIds) {
    $t = Test-ComActivation $id
    if ($t.Ok) { Write-Host ("  ok  {0}" -f $id) }
    else { Write-Host ("  !! {0} -> {1}" -f $id, $t.Error); $comOk = $false }
}
if ($comOk) { Write-Host "  ok  license wrapper registered (per-user, no admin needed)"; exit 0 }

# ------------------------------------------------------------------ machine-wide fallback
if ($isAdmin) {
    Write-Host "  .. elevated, also registering machine-wide"
    $r2 = Register-Classes "HKLM"
    Write-Host ("  HKLM: {0} written, {1} already ok, {2} failed" -f $r2.Written, $r2.Skipped, $r2.Failed)
    $comOk = $true
    foreach ($id in $probeIds) {
        $t = Test-ComActivation $id
        if ($t.Ok) { Write-Host ("  ok  {0}" -f $id) } else { Write-Host ("  !! {0} -> {1}" -f $id, $t.Error); $comOk = $false }
    }
    if ($comOk) { Write-Host "  ok  license wrapper registered (machine-wide)"; exit 0 }
} else {
    Write-Host "  .. not elevated, machine-wide registration skipped"
}

$rel = (Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full" -ErrorAction SilentlyContinue).Release
if (-not $rel) { Write-Host "  !! .NET Framework 4.x not detected (required by the wrapper)" }
else { Write-Host ("  .. .NET Framework 4 release = {0}" -f $rel) }
foreach ($d in @("DSILIC0.dll", "DSILIC1.dll")) {
    $p = Join-Path $AppDir $d
    if (Test-Path $p) {
        $zone = Get-Item $p -Stream Zone.Identifier -ErrorAction SilentlyContinue
        Write-Host ("  .. {0}: {1} bytes, blocked-by-MOTW={2}" -f $d, (Get-Item $p).Length, ($null -ne $zone))
    } else { Write-Host ("  !! {0} missing" -f $d) }
}
Write-Host "  !! licence component could not be activated"
exit 3
