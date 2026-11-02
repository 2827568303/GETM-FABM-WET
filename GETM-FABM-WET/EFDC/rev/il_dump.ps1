$ErrorActionPreference = 'Continue'
$path = 'C:\EFDC84_LIC\DSILIC1.dll'
$bytes = [IO.File]::ReadAllBytes($path)
$asm = [Reflection.Assembly]::Load($bytes)
$t = $asm.GetType('Flexnet.WrapperDongle.DemoLicense')
if (-not $t) { 'type not found'; exit 1 }
$mod = $t.Module
$methods = @('GetUpgradePackagesResponse')
$lines = New-Object System.Collections.ArrayList

foreach ($name in $methods) {
    $m = $t.GetMethod($name, [Reflection.BindingFlags]"Public,NonPublic,Instance,Static")
    if (-not $m) { [void]$lines.Add("=== $name missing"); continue }
    $il = $m.GetMethodBody().GetILAsByteArray()
    [void]$lines.Add("=== $name IL=$($il.Length)")
    for ($i = 0; $i -lt ($il.Length - 3); $i++) {
        $tok = [uint32]([BitConverter]::ToUInt32($il, $i))
        $hi = [int]($tok -shr 24)
        $try = $false
        if ($hi -eq 112) { $try = $true }
        if ($hi -eq 10) { $try = $true }
        if ($hi -eq 6) { $try = $true }
        if ($hi -eq 43) { $try = $true }
        if ($hi -eq 1) { $try = $true }
        if ($hi -eq 2) { $try = $true }
        if (-not $try) { continue }
        try {
            if ($hi -eq 112) {
                $s = $mod.ResolveString([int]$tok)
                [void]$lines.Add(("  +{0:X3} str  {1}" -f $i, $s))
            } elseif (($hi -eq 10) -or ($hi -eq 6) -or ($hi -eq 43)) {
                $mm = $mod.ResolveMethod([int]$tok)
                [void]$lines.Add(("  +{0:X3} meth {1}::{2}" -f $i, $mm.DeclaringType.FullName, $mm.Name))
            } else {
                $tt = $mod.ResolveType([int]$tok)
                [void]$lines.Add(("  +{0:X3} type {1}" -f $i, $tt.FullName))
            }
        } catch { }
    }
}
$lines | Out-File -FilePath 'C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\il_demo.txt' -Encoding UTF8
'wrote il_demo.txt'




