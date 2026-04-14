@echo off
setlocal
cd /d "%~dp0\app"

REM Set Qt plugin path for embedded python
set QT_QPA_PLATFORM_PLUGIN_PATH=%~dp0python\Lib\site-packages\PyQt5\Qt5\plugins

start "" "../python/pythonw.exe" main.py
endlocal