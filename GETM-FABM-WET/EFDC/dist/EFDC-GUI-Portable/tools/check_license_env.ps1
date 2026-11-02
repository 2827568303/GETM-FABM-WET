# check_license_env.ps1 - one-shot diagnostic for "The licenseWrapper is not valid ..."
# Run it with the 32-bit PowerShell (the launcher does that automatically).
#   powershell -ExecutionPolicy Bypass -File check_license_env.ps1
# It prints a report and also writes license_env.txt next to the launcher.

param(
    [string]$AppDir = "$env:LOCALAPPDATA\EFDC84\app"
)

$ErrorActionPreference = "SilentlyContinue"
$here = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$out = Join-Path $here "license_env.txt"
$lines = New-Object System.Collections.Generic.List[string]

function Add-Line([string]$s) { $lines.Add($s); Write-Host $s }

Add-Line ("EFDC license environment check  " + (Get-Date -Format "yyyy-MM-dd HH:mm:ss"))
Add-Line ("user        : " + $env:USERNAME + " @ " + $env:COMPUTERNAME)
Add-Line ("powershell  : " + [System.Environment]::Is64BitProcess + " (True=64-bit host, False=32-bit host)")
Add-Line ("app dir     : " + $AppDir)
Add-Line ""

# 1) .NET Framework
$rel = (Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full").Release
Add-Line ("1) .NET Framework 4 release : " + $(if ($rel) { $rel } else { "NOT FOUND" }))
$mgr = "C:\Windows\SysWOW64\mscoree.dll"
Add-Line ("   mscoree (32-bit)         : " + (Test-Path $mgr))
Add-Line ""

# 2) files
Add-Line "2) licence wrapper files"
foreach ($d in @("DSILIC0.dll", "DSILIC1.dll")) {
    $p = Join-Path $AppDir $d
    if (Test-Path $p) {
        $fi = Get-Item $p
        $hash = (Get-FileHash $p -Algorithm SHA256).Hash.Substring(0, 16)
        $zone = Get-Item $p -Stream Zone.Identifier
        Add-Line ("   {0}  {1} bytes  {2}  blocked={3}" -f $d, $fi.Length, $hash, ($null -ne $zone))
    } else {
        Add-Line ("   {0}  MISSING" -f $d)
    }
}
Add-Line ""

# 3) registration (32-bit view)
Add-Line "3) COM registration (HKCU 32-bit view)"
foreach ($g in @("{6399E2C8-63E4-4F31-823C-D256C17E7A13}", "{330D13A9-B2BE-4CCF-9B8A-DC2047FB3D33}", "{E326A913-D0B1-44E2-8015-952959CEA45F}")) {
    $k = "HKCU:\Software\Classes\WOW6432Node\CLSID\$g\InprocServer32"
    $v = Get-ItemProperty $k
    if ($v) {
        Add-Line ("   {0}`n      Class={1}`n      Assembly={2}`n      CodeBase={3}" -f $g, $v.Class, $v.Assembly, $v.CodeBase)
    } else { Add-Line ("   {0}  MISSING" -f $g) }
}
$hk = Get-ItemProperty "HKLM:\Software\Classes\WOW6432Node\CLSID\{6399E2C8-63E4-4F31-823C-D256C17E7A13}\InprocServer32"
Add-Line ("   HKLM entry : " + $(if ($hk) { $hk.Assembly } else { "none" }))
Add-Line ""

# 4) can this 32-bit host create the object?
Add-Line "4) CreateObject(Flexnet.WrapperDongle.FlexWrapperDongle)"
try {
    $t = [type]::GetTypeFromProgID("Flexnet.WrapperDongle.FlexWrapperDongle", $true)
    if ($null -eq $t) { Add-Line "   FAILED: ProgID not registered" }
    else {
        $o = [Activator]::CreateInstance($t)
        if ($o) {
            Add-Line ("   OK: " + $o.GetType().FullName)
            Add-Line ("   loaded from: " + $o.GetType().Assembly.Location)
            try { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($o) } catch { }
        } else { Add-Line "   FAILED: CreateInstance returned null" }
    }
} catch {
    Add-Line ("   FAILED: " + $_.Exception.GetBaseException().Message)
}
Add-Line ""

# 5) licence state files
Add-Line "5) licence state"
foreach ($f in @("$env:PUBLIC\DSI\EEMS8.3\EEMS.ini", "$env:PUBLIC\DSI\EEMS8.4\EFDC_Explorer.ini", "$env:PUBLIC\DSI\EEMS8.4\license.lic")) {
    Add-Line ("   {0}  {1}" -f $f, (Test-Path $f))
}
$ini = "$env:PUBLIC\DSI\EEMS8.3\EEMS.ini"
if (Test-Path $ini) {
    Get-Content $ini | Where-Object { $_ -match '^(IsActivated|FeatureName|LicenseFile|demo_email|demo_rememberpassword)=' } | ForEach-Object { Add-Line ("     " + $_) }
}
Add-Line ""

# 6) is the stub port open?
Add-Line "6) local licence stub 127.0.0.1:8080"
$up = $false
try { $c = New-Object Net.Sockets.TcpClient; $c.Connect("127.0.0.1", 8080); $up = $true; $c.Close() } catch { }
Add-Line ("   listening : " + $up)

try { [System.IO.File]::WriteAllLines($out, $lines, [System.Text.Encoding]::UTF8); Write-Host ""; Write-Host ("report written: " + $out) }
catch { Write-Host ("could not write report: " + $_.Exception.Message) }
exit 0
