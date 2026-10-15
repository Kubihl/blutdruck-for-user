@echo off
"%~dp0runtime\python.exe" "%~dp0start_web.py"
if errorlevel 1 pause
