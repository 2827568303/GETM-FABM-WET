# Dump a type library's coclass GUIDs/names (works for VB6 OCX/DLL).
param([Parameter(Mandatory=$true)][string]$Path)

Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
using System.Runtime.InteropServices.ComTypes;

public static class TlbDump {
    [DllImport("oleaut32.dll", CharSet=CharSet.Unicode, PreserveSig=false)]
    static extern void LoadTypeLibEx(string file, int regKind, out ITypeLib tlb);

    public static string Dump(string path) {
        ITypeLib tlb;
        LoadTypeLibEx(path, 2 /*REGKIND_NONE*/, out tlb);
        var sb = new System.Text.StringBuilder();
        IntPtr pLibAttr;
        tlb.GetLibAttr(out pLibAttr);
        var la = (System.Runtime.InteropServices.ComTypes.TYPELIBATTR)Marshal.PtrToStructure(pLibAttr, typeof(System.Runtime.InteropServices.ComTypes.TYPELIBATTR));
        string libName, libDoc, libHelp;
        int helpCtx;
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
            string name, doc, help;
            int hc;
            ti.GetDocumentation(-1, out name, out doc, out hc, out help);
            sb.AppendLine(string.Format("{0}|{1}|{2}", ta.typekind, ta.guid, name));
            ti.ReleaseTypeAttr(pta);
            Marshal.ReleaseComObject(ti);
        }
        Marshal.ReleaseComObject(tlb);
        return sb.ToString();
    }
}
'@ -Language CSharp

[TlbDump]::Dump((Resolve-Path $Path).Path)
