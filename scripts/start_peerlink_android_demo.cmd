@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_peerlink_android_demo.ps1"
if errorlevel 1 pause
