$ErrorActionPreference = 'Continue'
Add-Type -Namespace W3 -Name U -MemberDefinition @'
[DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc cb, IntPtr l);
[DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr parent, EnumWindowsProc cb, IntPtr l);
public delegate bool EnumWindowsProc(IntPtr h, IntPtr l);
[DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
[DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetClassName(IntPtr h, System.Text.StringBuilder s, int n);
[DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr h, System.Text.StringBuilder s, int n);
[DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
[DllImport("user32.dll")] public static extern IntPtr GetParent(IntPtr h);
[DllImport("user32.dll")] public static extern int GetDlgCtrlID(IntPtr h);
'@

$exe = (Resolve-Path 'EFDC 商业版8.4\EFDC_Explorer8.4.exe').Path
$p = Start-Process -FilePath $exe -WorkingDirectory (Split-Path $exe) -PassThru
"pid=$($p.Id)"
Start-Sleep -Seconds 9

$rows = New-Object System.Collections.ArrayList
$cb = [W3.U+EnumWindowsProc]{
    param($h, $l)
    $pp = 0
    [void][W3.U]::GetWindowThreadProcessId($h, [ref]$pp)
    if ($pp -eq $p.Id) {
        $c = New-Object System.Text.StringBuilder 256; [void][W3.U]::GetClassName($h, $c, 256)
        $t = New-Object System.Text.StringBuilder 512; [void][W3.U]::GetWindowText($h, $t, 512)
        [void]$rows.Add(("TOP   hwnd={0} cls='{1}' title='{2}' vis={3}" -f $h, $c.ToString(), $t.ToString(), [W3.U]::IsWindowVisible($h)))
        $cb2 = [W3.U+EnumWindowsProc]{
            param($h2, $l2)
            $c2 = New-Object System.Text.StringBuilder 256; [void][W3.U]::GetClassName($h2, $c2, 256)
            $t2 = New-Object System.Text.StringBuilder 512; [void][W3.U]::GetWindowText($h2, $t2, 512)
            [void]$rows.Add(("  CHILD hwnd={0} cls='{1}' title='{2}' vis={3} parent={4}" -f $h2, $c2.ToString(), $t2.ToString(), [W3.U]::IsWindowVisible($h2), [W3.U]::GetParent($h2)))
            return $true
        }
        [void][W3.U]::EnumChildWindows($h, $cb2, [IntPtr]::Zero)
    }
    return $true
}
[void][W3.U]::EnumWindows($cb, [IntPtr]::Zero)
"total windows: $($rows.Count)"
$rows | ForEach-Object { $_ }
"alive=$(-not $p.HasExited)"
