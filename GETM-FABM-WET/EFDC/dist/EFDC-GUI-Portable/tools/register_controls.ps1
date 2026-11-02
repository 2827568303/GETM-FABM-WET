# Register every VB6 ActiveX control in a folder for the CURRENT USER (no admin needed).
# Reads each control's type library, then writes CLSID / TypeLib / ProgID entries to HKCU.
param(
    [string]$Folder = ""
)

$ErrorActionPreference = "Continue"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
if ([string]::IsNullOrWhiteSpace($Folder)) { $Folder = Join-Path $here "..\vb6" }
$Folder = (Resolve-Path $Folder).Path

# Add-Type needs a writable temp dir; keep it inside the package.
$tmp = Join-Path $here "tmp"
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TEMP = $tmp
$env:TMP = $tmp

Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
using System.Runtime.InteropServices.ComTypes;

public static class TlbReader {
    [DllImport("oleaut32.dll", CharSet=CharSet.Unicode, PreserveSig=false)]
    static extern void LoadTypeLibEx(string file, int regKind, out ITypeLib tlb);

    public static string Dump(string path) {
        ITypeLib tlb;
        LoadTypeLibEx(path, 2, out tlb);
        var sb = new System.Text.StringBuilder();
        IntPtr pLibAttr;
        tlb.GetLibAttr(out pLibAttr);
        var la = (System.Runtime.InteropServices.ComTypes.TYPELIBATTR)Marshal.PtrToStructure(pLibAttr, typeof(System.Runtime.InteropServices.ComTypes.TYPELIBATTR));
        string libName, libDoc, libHelp; int helpCtx;
        tlb.GetDocumentation(-1, out libName, out libDoc, out helpCtx, out libHelp);
        sb.AppendLine(string.Format("LIB|{0}|{1}.{2}|{3}", la.guid, la.wMajorVerNum, la.wMinorVerNum, libName));
        tlb.ReleaseTLibAttr(pLibAttr);
        int n = tlb.GetTypeInfoCount();
        for (int i = 0; i < n; i++) {
            ITypeInfo ti;
            tlb.GetTypeInfo(i, out ti);
            IntPtr pta;
            ti.GetTypeAttr(out pta);
            var ta = (System.Runtime.InteropServices.ComTypes.TYPEATTR)Marshal.PtrToStructure(pta, typeof(System.Runtime.InteropServices.ComTypes.TYPEATTR));
            if (ta.typekind == System.Runtime.InteropServices.ComTypes.TYPEKIND.TKIND_COCLASS) {
                string name, doc, help; int hc;
                ti.GetDocumentation(-1, out name, out doc, out hc, out help);
                sb.AppendLine(string.Format("COCLASS|{0}|{1}", ta.guid, name));
            }
            ti.ReleaseTypeAttr(pta);
            Marshal.ReleaseComObject(ti);
        }
        Marshal.ReleaseComObject(tlb);
        return sb.ToString();
    }
}
'@ -Language CSharp

# --- registry helpers (use the .NET API: PowerShell cmdlets reset keys with -Force) ---
function Open-Key([string]$path) {
    $sub = $path -replace '^HKCU:\\', ''
    return [Microsoft.Win32.Registry]::CurrentUser.CreateSubKey($sub)
}

function Set-Str([string]$path, [string]$name, [string]$value) {
    $k = Open-Key $path
    if ($null -eq $k) { Write-Host "  !! cannot create $path"; return }
    $k.SetValue($name, $value, [Microsoft.Win32.RegistryValueKind]::String)
    $k.Close()
}

function Set-Dword([string]$path, [string]$name, [int]$value) {
    $k = Open-Key $path
    if ($null -eq $k) { return }
    $k.SetValue($name, $value, [Microsoft.Win32.RegistryValueKind]::DWord)
    $k.Close()
}

$Roots = @("HKCU:\Software\Classes", "HKCU:\Software\Classes\WOW6432Node")
$files = @(Get-ChildItem -Path $Folder -File | Where-Object { $_.Extension -match '^\.ocx$' })
Write-Host ("folder : {0}" -f $Folder)
Write-Host ("controls: {0}" -f $files.Count)

$total = 0
foreach ($f in $files) {
    try {
        $text = [TlbReader]::Dump($f.FullName)
    }
    catch {
        Write-Host ("  skip {0} (old typelib - use the 32-bit PowerShell)" -f $f.Name)
        continue
    }
    $lib = $null; $libVer = $null; $libName = $null; $classes = @()
    foreach ($line in ($text -split "`r?`n")) {
        $p = $line.Split("|")
        if ($p[0] -eq "LIB" -and $p.Length -ge 4) {
            $lib = $p[1].Trim('{', '}').ToUpper()
            $libVer = $p[2]
            $libName = $p[3]
        }
        elseif ($p[0] -eq "COCLASS" -and $p.Length -ge 3) {
            $classes += , @($p[2], $p[1].Trim('{', '}').ToUpper())
        }
    }
    if (-not $lib -or $classes.Count -eq 0) {
        Write-Host ("  skip {0} (no typelib)" -f $f.Name)
        continue
    }
    foreach ($root in $Roots) {
        $tl = "$root\TypeLib\{$lib}\$libVer"
        Set-Str "$tl\0\win32" "" $f.FullName
        Set-Str "$tl\HELPDIR" "" $f.DirectoryName
        Set-Dword $tl "FLAGS" 2
        foreach ($c in $classes) {
            $name = $c[0]; $clsid = $c[1]
            $progid = "$libName.$name"
            $base = "$root\CLSID\{$clsid}"
            Set-Str $base "" $progid
            Set-Str "$base\InprocServer32" "" $f.FullName
            Set-Str "$base\InprocServer32" "ThreadingModel" "Apartment"
            Set-Str "$base\TypeLib" "" "{$lib}"
            Set-Str "$base\TypeLib" "Version" $libVer
            Set-Str "$base\Version" "" $libVer
            Set-Str "$base\ProgID" "" $progid
            (Open-Key "$base\Control") | Out-Null
            Set-Str "$root\$progid\CLSID" "" "{$clsid}"
            $total++
        }
    }
    Write-Host ("  ok {0,-16} {1} classes ({2})" -f $f.Name, $classes.Count, $libName)
}
Write-Host ("class entries written: {0}" -f $total)
