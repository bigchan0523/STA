$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [System.Environment]::GetFolderPath("Desktop")
# 기존 "STA" 또는 "STA (스타)" 바로가기가 있을 수 있으므로 이름을 "STA"로 통일
$ShortcutPath = Join-Path $DesktopPath "STA.lnk"
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "c:\ai리터러시\STA-3.0.0\run_STA.bat"
$Shortcut.WorkingDirectory = "c:\ai리터러시\STA-3.0.0"
$Shortcut.IconLocation = "c:\ai리터러시\STA-3.0.0\assets\sta_icon.ico"
$Shortcut.Save()
Write-Output "Shortcut created at $ShortcutPath"

