# Make loopback bypass the system proxy (needed by the DSI licensing client).
$k = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings'
$cur = (Get-ItemProperty -Path $k -ErrorAction SilentlyContinue).ProxyOverride
$want = '<local>;127.*;localhost;*.local'
if ($cur -ne $want) {
    try {
        Set-ItemProperty -Path $k -Name ProxyOverride -Value $want -Type String
        Add-Type -TypeDefinition 'using System;using System.Runtime.InteropServices;public class WIF{[DllImport("wininet.dll",SetLastError=true)]public static extern bool InternetSetOption(IntPtr h,int o,IntPtr b,int l);}'
        [WIF]::InternetSetOption([IntPtr]::Zero, 39, [IntPtr]::Zero, 0) | Out-Null
        [WIF]::InternetSetOption([IntPtr]::Zero, 37, [IntPtr]::Zero, 0) | Out-Null
        Write-Host "proxy bypass for loopback: updated"
    } catch { Write-Host "proxy bypass: could not update (ignored)" }
} else { Write-Host "proxy bypass for loopback: already set" }
