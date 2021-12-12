#Windows Defender Exclusions for gueen
Add-MpPreference -ExclusionPath "C:\Program Files\Mesh Agent\*"
Add-MpPreference -ExclusionPath "C:\Program Files\gueenAgent\*"
Add-MpPreference -ExclusionPath "C:\Windows\Temp\grmm\*"
Add-MpPreference -ExclusionPath "C:\Windows\Temp\winagent-v*.exe"
