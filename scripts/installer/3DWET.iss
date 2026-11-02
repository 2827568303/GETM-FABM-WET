; 3DWET per-user installer. Build with scripts/build_windows_installer.sh.
; The staged tree is an embedded CPython plus the 3DWET source, solvers, and MS-MPI runtime.
#ifndef StageDir
  #error StageDir must point to the staged 3DWET directory.
#endif
#ifndef OutputDir
  #define OutputDir "."
#endif
#ifndef AppVersion
  #define AppVersion "1.0.0"
#endif

[Setup]
AppId={{C3D8E1A4-6F20-4B9A-9E17-3A6B2D8F01C4}
AppName=3DWET
AppVersion={#AppVersion}
AppPublisher=3DWET
AppVerName=3DWET {#AppVersion}
DefaultDirName={localappdata}\Programs\3DWET
DefaultGroupName=3DWET
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
OutputDir={#OutputDir}
OutputBaseFilename=3DWET-Setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\3dwet.ico
SetupIconFile={#StageDir}\3dwet.ico
CloseApplications=yes
RestartApplications=no
SetupLogging=yes
UsePreviousAppDir=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Shortcuts:"; Flags: checkedonce

[Files]
Source: "{#StageDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "__pycache__\*,*.pyc"

[Icons]
Name: "{group}\3DWET"; Filename: "{app}\3DWET.cmd"; WorkingDir: "{app}"; IconFilename: "{app}\3dwet.ico"; Comment: "Start 3DWET and open the browser"
Name: "{group}\Uninstall 3DWET"; Filename: "{uninstallexe}"
Name: "{userdesktop}\3DWET"; Filename: "{app}\3DWET.cmd"; WorkingDir: "{app}"; IconFilename: "{app}\3dwet.ico"; Tasks: desktopicon; Comment: "Start 3DWET and open the browser"

[Run]
Filename: "{app}\3DWET.cmd"; Description: "Launch 3DWET"; Flags: nowait postinstall skipifsilent shellexec

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
