param([int]$Seconds = 240)
$ErrorActionPreference = 'Continue'
$exe = "C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
$dir = Split-Path $exe
$p = Start-Process -FilePath $exe -WorkingDirectory $dir -PassThru
"started pid=$($p.Id) at $(Get-Date -Format HH:mm:ss)"
Add-Type -Namespace W -Name U -MemberDefinition @'
[DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc cb, IntPtr l);
public delegate bool EnumWindowsProc(IntPtr h, IntPtr l);
[DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
[DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetClassName(IntPtr h, System.Text.StringBuilder s, int n);
[DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr h, System.Text.StringBuilder s, int n);
[DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
[DllImport("user32.dll")] public static extern IntPtr GetParent(IntPtr h);
[DllImport("user32.dll")] public static extern IntPtr SendMessageTimeout(IntPtr h, uint m, IntPtr w, IntPtr l, uint f, uint t, out IntPtr r);
'@
$signal = @{}
$sw = [Diagnostics.Stopwatch]::StartNew()
while ($sw.Elapsed.TotalSeconds -lt $Seconds) {
    $cur = @{}
    $cb = [W.U+EnumWindowsProc]{
        param($h, $l)
        $pid2 = 0
        [void][W.U]::GetWindowThreadProcessId($h, [ref]$pid2)
        if ($pid2 -eq $p.Id -and [W.U]::GetParent($h) -eq [IntPtr]::Zero) {
            $c = New-Object System.Text.StringBuilder 256
            [void][W.U]::GetClassName($h, $c, 256)
            $t = New-Object System.Text.StringBuilder 512
            [void][W.U]::GetWindowText($h, $t, 512)
            $key = "$($c.ToString())|$($t.ToString())|$([W.U]::IsWindowVisible($h))"
            $cur[$key] = $h
            if (-not $signal.ContainsKey($key)) {
                $r = [IntPtr]::Zero
                $ok = [W.U]::SendMessageTimeout($h, 0, [IntPtr]::Zero, [IntPtr]::Zero, 2, 200, [ref]$r)
                $signal[$key] = $true
                "{0,7:N2}s WIN cls='{1}' title='{2}' vis={3} resp={4} hwnd={5}" -f $sw.Elapsed.TotalSeconds, $c.ToString(), $t.ToString(), [W.U]::IsWindowVisible($h), ($ok -ne 0), $h
            }
        }
        return $true
    }
    [void][W.U]::EnumWindows($cb, [IntPtr]::Zero)
    foreach ($k in @($signal.Keys)) { if (-not $cur.ContainsKey($k)) { "{0,7:N2}s GONE {1}" -f $sw.Elapsed.TotalSeconds, $k; $signal.Remove($k) } }
    if ($p.HasExited) { "{0,7:N2}s PROCESS EXITED code={1}" -f $sw.Elapsed.TotalSeconds, $p.ExitCode; break }
    Start-Sleep -Milliseconds 500
}
"alive=$(-not $p.HasExited)"
