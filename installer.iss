; Inno Setup script for Teams Call Recorder
; Builds a Windows installer with Start Menu + optional desktop shortcuts
; and an entry in Add/Remove Programs.

#define MyAppName "Teams Call Recorder"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Teams Call Recorder"
#define MyAppExeName "TeamsCallRecorder.exe"

[Setup]
AppId={{B6F2A8E4-3C7D-4A91-9E2F-7D5C1A0B3E88}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
; Install into the user's area so admin rights are not required.
PrivilegesRequired=lowest
OutputDir=installer_output
OutputBaseFilename=TeamsCallRecorder_Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayName={#MyAppName}
; Icon shown for the installer and in Add/Remove Programs.
SetupIconFile=assets\app.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"
Name: "startupicon"; Description: "Start automatically when Windows starts"; GroupDescription: "Startup:"; Flags: unchecked

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
; Optional: launch at Windows startup.
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startupicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
