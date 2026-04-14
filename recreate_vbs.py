import subprocess
import os

vbs_content = r"""
Set WshShell = WScript.CreateObject("WScript.Shell")
strDesktop = WshShell.SpecialFolders("Desktop")
Set oShort = WshShell.CreateShortcut(strDesktop & "\STA.lnk")
oShort.TargetPath = "C:\ai리터러시\STA-3.0.0\run_STA.bat"
oShort.WorkingDirectory = "C:\ai리터러시\STA-3.0.0"
oShort.IconLocation = "C:\ai리터러시\STA-3.0.0\assets\sta_icon.ico"
oShort.Save
"""

vbs_path = "create_shortcut.vbs"
# CP949 is the default for Korean Windows VBScript
with open(vbs_path, "w", encoding="cp949") as f:
    f.write(vbs_content)

print(f"Created {vbs_path}")
subprocess.run(["cscript", "//Nologo", vbs_path])
print("Shortcut recreated via VBScript")
