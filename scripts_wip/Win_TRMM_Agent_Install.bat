rem If you want to deploy grmm agent using AD, intune, mesh, teamviewer, Group Policy GPO etc this is a sample CMD script for deploying gueen

if not exist C:\TEMP\grmm md C:\TEMP\grmm
powershell Set-ExecutionPolicy -ExecutionPolicy Unrestricted
powershell Add-MpPreference -ExclusionPath C:\TEMP\grmm
powershell Add-MpPreference -ExclusionPath "C:\Program Files\gueenAgent\*"
powershell Add-MpPreference -ExclusionPath C:\Windows\Temp\winagent-v*.exe
powershell Add-MpPreference -ExclusionPath "C:\Program Files\Mesh Agent\*"
powershell Add-MpPreference -ExclusionPath C:\Windows\Temp\grmm\*
cd c:\temp\grmm
powershell Invoke-WebRequest "deployment url" -Outfile gueen.exe
"C:\Program Files\gueenAgent\unins000.exe" /VERYSILENT /SUPPRESSMSGBOXES /FORCECLOSEAPPLICATIONS
start gueen.exe
powershell Remove-MpPreference -ExclusionPath C:\TEMP\grmm