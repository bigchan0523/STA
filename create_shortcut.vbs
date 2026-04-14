
Set WshShell = WScript.CreateObject("WScript.Shell")
strDesktop = WshShell.SpecialFolders("Desktop")
Set oShort = WshShell.CreateShortcut(strDesktop & "\STA.lnk")
oShort.TargetPath = "C:\ai리터러시\STA-3.0.0\run_STA.bat"
oShort.WorkingDirectory = "C:\ai리터러시\STA-3.0.0"
oShort.IconLocation = "C:\ai리터러시\STA-3.0.0\assets\sta_icon.ico"
oShort.Save
