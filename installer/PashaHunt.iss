; Inno Setup script for Pasha Hunt Production Installer
#ifndef AppVersion
  #define AppVersion "2.0.0"
#endif

[Setup]
AppId={{C6287A1B-F6E2-4C92-9C8E-6FE6F62A48E1}
AppName=Pasha Hunt
AppVersion={#AppVersion}
AppVerName=Pasha Hunt {#AppVersion}
AppPublisher=Muhammad Mubashar (pasha804)
AppPublisherURL=https://github.com/pasha804/pasha-hunt
AppSupportURL=mailto:mubasharmuhammad790@gmail.com
AppUpdatesURL=https://github.com/pasha804/pasha-hunt
AppMutex=PashaHuntMutex
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
DefaultDirName={localappdata}\Programs\Pasha Hunt
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
RestartApplications=no

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

[UninstallRun]
Filename: "{sys}\taskkill.exe"; Parameters: "/F /IM PashaHunt.exe /T"; Flags: runhidden; RunOnceId: "KillPashaHunt"
Filename: "{sys}\taskkill.exe"; Parameters: "/F /IM JobHunter.exe /T"; Flags: runhidden; RunOnceId: "KillJobHunter"
Filename: "{sys}\schtasks.exe"; Parameters: "/Delete /TN ""Remote Job Hunter"" /F"; Flags: runhidden; RunOnceId: "DeleteRemoteJobHunter"
Filename: "{sys}\schtasks.exe"; Parameters: "/Delete /TN ""Pasha Hunt Auto-run"" /F"; Flags: runhidden; RunOnceId: "DeletePashaAutoRun"

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
Type: filesandordirs; Name: "{localappdata}\Programs\Pasha Hunt"
Type: filesandordirs; Name: "{localappdata}\Programs\Job Hunter"
Type: filesandordirs; Name: "{localappdata}\Pasha Hunt"
Type: filesandordirs; Name: "{localappdata}\Pasha Hunt 2.0"
Type: filesandordirs; Name: "{localappdata}\PashaHunt"
Type: filesandordirs; Name: "{userappdata}\Job Hunter"
Type: filesandordirs; Name: "{userappdata}\Pasha Hunt"
Type: files; Name: "{autodesktop}\Pasha Hunt.lnk"
Type: files; Name: "{autodesktop}\Job Hunter.lnk"
Type: files; Name: "{commonprograms}\Pasha Hunt.lnk"
Type: files; Name: "{autoprograms}\Pasha Hunt.lnk"

[Code]
// Pre-install: kill any running instance so file access is never denied
function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  ResultCode: Integer;
begin
  Exec('taskkill.exe', '/F /IM PashaHunt.exe /T', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Exec('taskkill.exe', '/F /IM JobHunter.exe /T', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Result := '';
end;

// Pre & Post-uninstall: kill processes and wipe all user data, caches, and shortcuts
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ResultCode: Integer;
begin
  if CurUninstallStep = usUninstall then
  begin
    Exec('taskkill.exe', '/F /IM PashaHunt.exe /T', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    Exec('taskkill.exe', '/F /IM JobHunter.exe /T', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end
  else if CurUninstallStep = usPostUninstall then
  begin
    DelTree(ExpandConstant('{app}'), True, True, True);
    DelTree(ExpandConstant('{localappdata}\Programs\Pasha Hunt'), True, True, True);
    DelTree(ExpandConstant('{localappdata}\Programs\Job Hunter'), True, True, True);
    DelTree(ExpandConstant('{localappdata}\Pasha Hunt'), True, True, True);
    DelTree(ExpandConstant('{localappdata}\Pasha Hunt 2.0'), True, True, True);
    DelTree(ExpandConstant('{localappdata}\PashaHunt'), True, True, True);
    DelTree(ExpandConstant('{userappdata}\Job Hunter'), True, True, True);
    DelTree(ExpandConstant('{userappdata}\Pasha Hunt'), True, True, True);
    DeleteFile(ExpandConstant('{autodesktop}\Pasha Hunt.lnk'));
    DeleteFile(ExpandConstant('{autodesktop}\Job Hunter.lnk'));
    DeleteFile(ExpandConstant('{autoprograms}\Pasha Hunt.lnk'));
  end;
end;
