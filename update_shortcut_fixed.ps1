$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [System.Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "STA.lnk"

# Remove existing shortcut if it exists to ensure refresh
if (Test-Path $ShortcutPath) {
    Remove-Item $ShortcutPath -Force
}

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "C:\ai리터러시\STA-3.0.0\run_STA.bat"
$Shortcut.WorkingDirectory = "C:\ai리터러시\STA-3.0.0"
$Shortcut.IconLocation = "C:\ai리터러시\STA-3.0.0\assets\sta_icon.ico"
$Shortcut.Save()

Write-Output "Shortcut successfully recreated at $ShortcutPath"
