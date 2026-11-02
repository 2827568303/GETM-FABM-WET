; Build with scripts/build_installer.ps1. Payload and dependencies are checked there.
#ifndef StageDir
  #error StageDir must point to the verified application staging directory.
#endif
#ifndef ToolsDir
  #error ToolsDir must point to the verified installer tools directory.
#endif
#ifndef OutputDir
  #define OutputDir "..\..\release"
#endif
#ifndef AppVersion
  #define AppVersion "1.0.0"
#endif

[Setup]
AppId={{AF91C535-725B-45C4-A0C9-622C4C2EE06C}
AppName=3DWET Studio
AppVersion={#AppVersion}
AppPublisher=3DWET Studio
DefaultDirName={localappdata}\Programs\3DWET Studio
DefaultGroupName=3DWET Studio
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0.14393
OutputDir={#OutputDir}
OutputBaseFilename=3DWETStudio-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
DisableWelcomePage=no
UninstallDisplayIcon={app}\3DWETStudio.exe
SetupIconFile={#StageDir}\3DWETStudio.ico
CloseApplications=yes
RestartApplications=no
SetupLogging=yes
UsePreviousAppDir=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式 / Create desktop shortcuts"; Flags: checkedonce

[Dirs]
Name: "{app}\3DWET\case"; Flags: uninsneveruninstall
Name: "{app}\3DWET\app"; Flags: uninsneveruninstall

[Files]
; Case data is copied once and is explicitly excluded from the uninstall log.
Source: "{#StageDir}\*"; DestDir: "{app}"; Excludes: "3DWET\case\*,3DWET\app\*,3DWET\.studio-runtime\*,*\__pycache__\*"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#StageDir}\3DWET\case\*"; DestDir: "{app}\3DWET\case"; Flags: onlyifdoesntexist uninsneveruninstall recursesubdirs createallsubdirs
#include AddBackslash(StageDir) + "case-updates.iss"
Source: "{#ToolsDir}\MicrosoftEdgeWebView2RuntimeInstallerX64.exe"; Flags: dontcopy

[Icons]
Name: "{group}\3DWET Studio (桌面 Desktop)"; Filename: "{app}\3DWETStudio.exe"; WorkingDir: "{app}"
Name: "{group}\3DWET Studio (浏览器 Web)"; Filename: "{app}\3DWETStudio.exe"; Parameters: "--web"; WorkingDir: "{app}"
Name: "{group}\使用指南 User Guide"; Filename: "{app}\使用指南\index.html"
Name: "{group}\依赖说明 Dependencies"; Filename: "{app}\DEPENDENCIES.txt"
Name: "{group}\卸载 Uninstall"; Filename: "{uninstallexe}"
Name: "{userdesktop}\3DWET Studio"; Filename: "{app}\3DWETStudio.exe"; WorkingDir: "{app}"; Tasks: desktopicon

[InstallDelete]
Type: files; Name: "{userdesktop}\3DWET Studio Web.lnk"
Type: files; Name: "{userdesktop}\3DWET 湖泊生态模拟工作台.lnk"

[Run]
Filename: "{app}\3DWETStudio.exe"; Description: "启动 3DWET Studio / Launch 3DWET Studio"; Flags: nowait postinstall skipifsilent

[Code]
const
  WebView2Key = 'Software\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}';

var
  DependencyPage: TOutputMsgMemoWizardPage;

function InstallKnownDefault(CaseName, Filename, KnownHashes: String): Boolean;
var
  TargetPath, BackupPath, Digest: String;
begin
  TargetPath := ExpandConstant('{app}\3DWET\case\') + CaseName + '\' + Filename;
  Result := not FileExists(TargetPath);
  if Result then exit;
  try
    Digest := Lowercase(GetSHA256OfFile(TargetPath));
    Result := Pos(',' + Digest + ',', ',' + Lowercase(KnownHashes) + ',') > 0;
    if Result then begin
      BackupPath := TargetPath + '.before-{#AppVersion}.bak';
      if not FileExists(BackupPath) then
        Result := FileCopy(TargetPath, BackupPath, False);
    end;
  except
    Result := False;
    Log('Preserved default configuration because checksum/backup failed: ' + TargetPath);
  end;
end;

function HasRuntimeAt(Root: Integer): Boolean;
var
  Version: String;
  PackedVersion: Int64;
begin
  Result := RegQueryStringValue(Root, WebView2Key, 'pv', Version);
  if Result then
    Result := StrToVersion(Version, PackedVersion) and (PackedVersion > 0);
end;

function HasWebView2: Boolean;
begin
  { Microsoft documents HKLM 32-bit view and HKCU on 64-bit Windows. }
  Result := HasRuntimeAt(HKLM32) or HasRuntimeAt(HKCU);
end;

procedure InitializeWizard;
var
  RuntimeStatus: String;
begin
  if HasWebView2 then
    RuntimeStatus := '检测结果：已安装 Microsoft WebView2 Runtime，将使用现有运行时。'
  else
    RuntimeStatus := '检测结果：尚未安装 Microsoft WebView2 Runtime，将使用内置 x64 离线安装程序。';
  DependencyPage := CreateOutputMsgMemoPage(wpWelcome,
    '安装前：运行环境与依赖说明',
    '安装程序将配置以下组件，无需自行安装 Python 或修改系统 PATH。',
    '请阅读运行环境说明，然后点击 Next 继续。',
    '1. 应用与科学计算环境（随程序安装）' + #13#10 +
    '内置 Python、Flask、NumPy、SciPy、netCDF4、PyYAML、pyshp、pyproj、psutil、Waitress、pywebview 及其必要依赖。' + #13#10#13#10 +
    '2. 模型运行环境（随程序安装）' + #13#10 +
    '包含 GETM/FABM/WET 模型可执行程序、所需原生 DLL、NetCDF/HDF5 与 Fortran/OpenMP 运行库，以及示例案例与模板。' + #13#10#13#10 +
    '3. Microsoft WebView2 Runtime（桌面窗口必需）' + #13#10 +
    RuntimeStatus + #13#10 +
    '此组件由 Microsoft 发布和维护，可能通过 Microsoft Edge Update 自动更新。安装器正常以当前用户权限安装；组织策略阻止安装时会显示错误并停止安装。浏览器模式使用系统默认浏览器。' + #13#10#13#10 +
    '4. Windows 系统组件' + #13#10 +
    '支持 Windows 10（1607 或更新版本）与 Windows 11 x64。桌面窗口还需要 Windows 自带的 .NET Framework 4.6.2 或更新版本；安装器会检查，缺失时明确停止并说明修复方法。' + #13#10#13#10 +
    '5. 安装位置与数据保留' + #13#10 +
    '默认安装到当前用户的 LocalAppData\Programs\3DWET Studio。升级保留用户修改过的案例配置；识别为旧版出厂默认的配置会先备份再更新。卸载保留案例与用户输出。' + #13#10#13#10 +
    '6. 许可与依赖清单' + #13#10 +
    '完整依赖清单为安装目录中的 DEPENDENCIES.txt；第三方许可位于 THIRD_PARTY_LICENSES 和 3DWET\bin\runtime\licenses。Microsoft WebView2 使用 Microsoft 的许可条款。');
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  ResultCode: Integer;
  DotNetRelease: Cardinal;
  InstallerPath: String;
begin
  Result := '';
  if not RegQueryDWordValue(HKLM32, 'SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full', 'Release', DotNetRelease) then
    DotNetRelease := 0;
  if DotNetRelease < 394802 then
  begin
    Result := '此 Windows 系统缺少桌面窗口所需的 .NET Framework 4.6.2 或更新版本。' + #13#10 +
      '安装尚未完成。请通过 Windows 更新或 Microsoft 官方 .NET Framework 安装程序修复系统组件，然后重新运行本安装器。';
    Exit;
  end;
  if HasWebView2 then
  begin
    Log('WebView2 Runtime detected; offline runtime installation skipped.');
    Exit;
  end;
  WizardForm.PreparingLabel.Caption := '正在安装 Microsoft WebView2 Runtime，请稍候……';
  ExtractTemporaryFile('MicrosoftEdgeWebView2RuntimeInstallerX64.exe');
  InstallerPath := ExpandConstant('{tmp}\MicrosoftEdgeWebView2RuntimeInstallerX64.exe');
  if not Exec(InstallerPath, '/silent /install', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    Result := '无法启动 Microsoft WebView2 离线安装程序。Windows 错误：' + IntToStr(ResultCode) + #13#10 +
      '安装尚未完成。请检查安全软件或组织策略，然后重新运行安装器。';
    Exit;
  end;
  Log('WebView2 installer exit code: ' + IntToStr(ResultCode));
  if ((ResultCode <> 0) and (ResultCode <> 3010)) or not HasWebView2 then
  begin
    Result := 'Microsoft WebView2 Runtime 安装失败或未通过安装后检测（退出码：' + IntToStr(ResultCode) + '）。' + #13#10 +
      '3DWET Studio 安装尚未完成。请检查组织策略、磁盘空间和 Microsoft Edge Update；如提示重启，请重启后再运行安装器。' + #13#10 +
      '如需管理员协助，可从 Microsoft 官方网站安装 WebView2 Runtime，再重新运行本安装器。';
    Exit;
  end;
  NeedsRestart := ResultCode = 3010;
end;
