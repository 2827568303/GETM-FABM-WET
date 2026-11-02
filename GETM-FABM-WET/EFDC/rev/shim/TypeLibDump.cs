using System;
using System.Runtime.InteropServices;
using CT = System.Runtime.InteropServices.ComTypes;

class T
{
    [DllImport("oleaut32.dll", CharSet = CharSet.Unicode, PreserveSig = false)]
    static extern void LoadTypeLibEx(string file, int regkind, out CT.ITypeLib tlb);

    static void Main(string[] args)
    {
        CT.ITypeLib tlb;
        LoadTypeLibEx(args[0], 2, out tlb);
        int n = tlb.GetTypeInfoCount();
        Console.WriteLine("typeinfos: " + n);
        for (int i = 0; i < n; i++)
        {
            CT.ITypeInfo ti;
            tlb.GetTypeInfo(i, out ti);
            string name, doc, help;
            int ctx;
            ti.GetDocumentation(-1, out name, out doc, out ctx, out help);
            IntPtr pAttr;
            ti.GetTypeAttr(out pAttr);
            CT.TYPEATTR attr = (CT.TYPEATTR)Marshal.PtrToStructure(pAttr, typeof(CT.TYPEATTR));
            if (attr.typekind == CT.TYPEKIND.TKIND_COCLASS)
                Console.WriteLine("COCLASS\t" + name + "\t" + attr.guid.ToString("B"));
            ti.ReleaseTypeAttr(pAttr);
        }
    }
}
