@echo off
setlocal
set REPO=Preetham0420/smartops-demo

REM 1) Fetch latest logs (force PowerShell to allow the script just for this call)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0fetch_logs.ps1" -Repo "%REPO%"
if errorlevel 1 (
  echo [x] fetch_logs failed
  exit /b 1
)

REM 2) Run pipeline (RCA -> suggest -> report)
py -3 "%~dp0pipeline.py"
if errorlevel 1 (
  echo [x] pipeline failed
  exit /b 2
)

REM 3) Open the report in your default viewer
start "" "C:\Users\preet\Projects\nani\smartops\data\parsed\report.md"
echo [?] Done.
endlocal
