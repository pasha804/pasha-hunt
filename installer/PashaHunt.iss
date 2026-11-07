; Inno Setup script for PashaHuntSetup_v2.0.exe.
#ifndef AppVersion
  #define AppVersion "2.0.0"
#endif

[Setup]
AppId={{C6287A1B-F6E2-4C92-9C8E-6FE6F62A48E1}
AppName=Pasha Hunt
AppVersion={#AppVersion}
AppVerName=Pasha Hunt {#AppVersion} (Apinex Edition)
AppPublisher=Pasha Hunt
AppPublisherURL=https://apinex.bond
AppSupportURL=https://apinex.bond
AppUpdatesURL=https://apinex.bond
AppMutex=PashaHuntMutex
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
DefaultDirName={autopf}\Pasha Hunt
DisableProgramGroupPage=yes
LicenseFile=..\LICENSE
OutputDir=E:\Job Hunt\Pasha_Hunt_Release
OutputBaseFilename=PashaHuntSetup_v2.0
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\PashaHunt.exe
UninstallDisplayName=Pasha Hunt
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
CloseApplications=yes

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\dist\PashaHunt\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "icon.ico"; DestDir: "{app}\installer"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Pasha Hunt"; Filename: "{app}\PashaHunt.exe"; WorkingDir: "{app}"; IconFilename: "{app}\PashaHunt.exe"
Name: "{autodesktop}\Pasha Hunt"; Filename: "{app}\PashaHunt.exe"; WorkingDir: "{app}"; IconFilename: "{app}\PashaHunt.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\PashaHunt.exe"; Description: "{cm:LaunchProgram,Pasha Hunt}"; Flags: nowait postinstall skipifsilent
Filename: "{app}\PashaHunt.exe"; Flags: nowait runasoriginaluser; Check: IsUpdate

[UninstallRun]
Filename: "{sys}\schtasks.exe"; Parameters: "/Delete /TN ""Remote Job Hunter"" /F"; Flags: runhidden; RunOnceId: "DeleteAutoRun"

[Code]
function IsUpdate: Boolean;
var
  I: Integer;
begin
  Result := False;
  for I := 1 to ParamCount do
    if CompareText(ParamStr(I), '/UPDATE') = 0 then
      Result := True;
end;
