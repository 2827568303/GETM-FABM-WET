# EFDC Explorer 8.4 - automatic Demo sign-in (pure PowerShell, no Python).
# Usage: powershell -ExecutionPolicy Bypass -File autosign.ps1 -ProcessName EFDC_Explorer8.4
param(
    [string]$ProcessName = 'EFDC_Explorer8.4',
    [int]$TimeoutSec = 100,
    [int]$AppPid = 0,
    [string]$Email = '',
    [string]$Password = ''
)

$ErrorActionPreference = 'Stop'

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
using System.Text;

public class W32 {
    [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
    [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern int GetWindowTextW(IntPtr h, StringBuilder s, int n);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern int GetClassNameW(IntPtr h, StringBuilder s, int n);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr p);
    [DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr h, EnumProc cb, IntPtr p);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
    [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr h);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
    [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr after, int x, int y, int cx, int cy, uint flags);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint dx, uint dy, uint d, IntPtr e);
    [DllImport("user32.dll")] public static extern uint SendInput(uint n, INPUT[] i, int cb);
    [DllImport("user32.dll")] public static extern IntPtr SendMessageW(IntPtr h, uint m, IntPtr w, IntPtr l);
    [DllImport("user32.dll")] public static extern int GetWindowLongW(IntPtr h, int i);

    public delegate bool EnumProc(IntPtr h, IntPtr p);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
    [StructLayout(LayoutKind.Sequential)] public struct KEYBDINPUT { public ushort wVk, wScan; public uint dwFlags, time; public IntPtr dwExtraInfo; }
    [StructLayout(LayoutKind.Explicit)] public struct UNION { [FieldOffset(0)] public KEYBDINPUT ki; }
    [StructLayout(LayoutKind.Sequential)] public struct INPUT { public uint type; public UNION u; }

    public static System.Collections.Generic.List<IntPtr> TopWindows(uint pid) {
        var list = new System.Collections.Generic.List<IntPtr>();
        EnumWindows(delegate(IntPtr h, IntPtr p) {
            uint q; GetWindowThreadProcessId(h, out q);
            if (q == pid) list.Add(h);
            return true;
        }, IntPtr.Zero);
        return list;
    }
    public static System.Collections.Generic.List<IntPtr> Children(IntPtr h) {
        var list = new System.Collections.Generic.List<IntPtr>();
        EnumChildWindows(h, delegate(IntPtr c, IntPtr p) { list.Add(c); return true; }, IntPtr.Zero);
        return list;
    }
    public static string Text(IntPtr h) { var s = new StringBuilder(512); GetWindowTextW(h, s, 512); return s.ToString(); }
    public static string Cls(IntPtr h) { var s = new StringBuilder(256); GetClassNameW(h, s, 256); return s.ToString(); }
    public static void Click(int x, int y) {
        SetCursorPos(x, y); System.Threading.Thread.Sleep(60);
        mouse_event(0x0002, 0, 0, 0, IntPtr.Zero);
        mouse_event(0x0004, 0, 0, 0, IntPtr.Zero);
        System.Threading.Thread.Sleep(80);
    }
    public static void Type(string text) {
        foreach (char ch in text) {
            foreach (uint f in new uint[] { 0x0004, 0x0006 }) {
                INPUT i = new INPUT();
                i.type = 1; i.u.ki.wVk = 0; i.u.ki.wScan = ch; i.u.ki.dwFlags = f;
                SendInput(1, new INPUT[] { i }, Marshal.SizeOf(typeof(INPUT)));
                System.Threading.Thread.Sleep(18);
            }
        }
    }
    public static void Key(ushort vk) {
        foreach (uint f in new uint[] { 0, 0x0002 }) {
            INPUT i = new INPUT();
            i.type = 1; i.u.ki.wVk = vk; i.u.ki.wScan = 0; i.u.ki.dwFlags = f;
            SendInput(1, new INPUT[] { i }, Marshal.SizeOf(typeof(INPUT)));
            System.Threading.Thread.Sleep(20);
        }
    }
}
"@

[void][W32]::SetProcessDPIAware()

function Get-Proc-Id {
    $ps = @(Get-Process -Name $ProcessName -ErrorAction SilentlyContinue)
    if (-not $ps.Count) { return 0 }
    $ps = $ps | Sort-Object Id -Descending
    return $ps[0].Id
}

function Find-Form([int]$appPid, [string]$needle, [string]$exclude = '') {
    foreach ($h in [W32]::TopWindows([uint32]$appPid)) {
        $t = [W32]::Text($h)
        if ([W32]::IsWindowVisible($h) -and $t -like "*$needle*") {
            if ($exclude -and $t -like "*$exclude*") { continue }
            return $h
        }
    }
    return [IntPtr]::Zero
}

function Click-Child([IntPtr]$form, [string]$clsPrefix, [string]$textLike) {
    foreach ($c in [W32]::Children($form)) {
        $cls = [W32]::Cls($c); $t = [W32]::Text($c)
        if ($cls.StartsWith($clsPrefix) -and $t -like "*$textLike*" -and [W32]::IsWindowVisible($c)) {
            $r = New-Object W32+RECT
            [void][W32]::GetWindowRect($c, [ref]$r)
            [W32]::SetForegroundWindow($form) | Out-Null
            Start-Sleep -Milliseconds 150
            [W32]::Click([int](($r.L + $r.R) / 2), [int](($r.T + $r.B) / 2))
            return $true
        }
    }
    return $false
}

function Fill-Signin([IntPtr]$form, [string]$email, [string]$pwd) {
    $boxes = @()
    foreach ($c in [W32]::Children($form)) {
        if ([W32]::Cls($c) -eq 'ThunderRT6TextBox' -and [W32]::IsWindowVisible($c)) {
            $r = New-Object W32+RECT
            [void][W32]::GetWindowRect($c, [ref]$r)
            if (($r.R - $r.L) -gt 40) { $boxes += ,@($r.T, $c, $r) }
        }
    }
    $boxes = $boxes | Sort-Object { $_[0] }
    if ($boxes.Count -lt 2) { return $false }
    $pairs = @(@($boxes[0], $email), @($boxes[1], $pwd))
    foreach ($p in $pairs) {
        $r = $p[0][2]
        [W32]::SetForegroundWindow($form) | Out-Null
        Start-Sleep -Milliseconds 150
        [W32]::Click([int](($r.L + $r.R) / 2), [int](($r.T + $r.B) / 2))
        Start-Sleep -Milliseconds 250
        [W32]::Key(0x23) | Out-Null          # End
        for ($i = 0; $i -lt 40; $i++) { [W32]::Key(0x08) }   # Backspace
        [W32]::Type($p[1])
        Start-Sleep -Milliseconds 200
    }
    if (-not (Click-Child $form 'ThunderRT6CommandButton' 'Sign')) {
        [W32]::Key(0x0D) | Out-Null
    }
    return $true
}

# credentials: explicit -> ini -> defaults
$ini = Join-Path $env:PUBLIC 'DSI\EEMS8.3\EEMS.ini'
if ((-not $Email) -or (-not $Password)) {
    if (Test-Path $ini) {
        foreach ($line in Get-Content $ini) {
            if ($line -match '^demo_email=(.+)$' -and -not $Email) { $Email = $Matches[1].Trim() }
            if ($line -match '^demo_password=(.+)$' -and -not $Password) { $Password = $Matches[1].Trim() }
        }
    }
}
if (-not $Email) { $Email = 'zhang.san8888@gmail.com' }
if (-not $Password) { $Password = 'Efdc2026!' }

Write-Host "[autosign] waiting for $ProcessName ..."
$appPid = $AppPid
$deadline = (Get-Date).AddSeconds($TimeoutSec)
while ((Get-Date) -lt $deadline) {
    if (-not $appPid) { $appPid = Get-Proc-Id }
    if (-not $appPid) { Start-Sleep -Milliseconds 400; continue }
    $ui = Find-Form $appPid 'Demo Version' 'Sign in'
    if ($ui -ne [IntPtr]::Zero) {
        if ([W32]::IsIconic($ui)) { [void][W32]::ShowWindow($ui, 9) }
        [void][W32]::SetWindowPos($ui, [IntPtr](-1), 60, 60, 1000, 740, 0x0040)
        [void][W32]::BringWindowToTop($ui)
        [void][W32]::SetForegroundWindow($ui)
        Write-Host "[autosign] EFDC UI is up (hwnd=$ui)"
        exit 0
    }
    $wiz = Find-Form $appPid 'Activation Wizard'
    if ($wiz -ne [IntPtr]::Zero) {
        if (Click-Child $wiz 'ThunderRT6CommandButton' 'Demo Version') { Write-Host '[autosign] clicked Demo Version' }
        Start-Sleep -Milliseconds 800
        continue
    }
    $sign = Find-Form $appPid 'Sign in EEMS Demo'
    if ($sign -ne [IntPtr]::Zero) {
        Write-Host '[autosign] filling sign-in form'
        [void](Fill-Signin $sign $Email $Password)
        Start-Sleep -Seconds 3
        continue
    }
    Start-Sleep -Milliseconds 400
}
Write-Host '[autosign] timed out'
exit 1




