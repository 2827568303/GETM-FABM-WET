p='dgco.js'; s=open(p,encoding='utf-8').read()
s=s.replace("var h=Module.load('C:\\\\EFDC84_LIC\\\\mscomctl.ocx');","var ole32=Process.findModuleByName('ole32.dll'); var CoInit=new NativeFunction(ole32.findExportByName('CoInitializeEx'),'int',['pointer','uint']); var ci=CoInit(ptr(0),2); send2('CoInitializeEx='+ci); var h=Module.load('C:\\\\EFDC84_LIC\\\\mscomctl.ocx');")
open(p,'w',encoding='utf-8').write(s)
print('ok')
