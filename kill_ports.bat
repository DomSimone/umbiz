@echo off
:: Change directory to the script's location to ensure all paths are correct
cd /d %~dp0

echo.
echo ==========================================================
echo  Cleaning up ports 8001 (Backend) and 8080 (Frontend)...
echo ==========================================================
echo.

:: Kill process listening on port 8001
for /f "tokens=5" %%a in ('netstat -aon ^| %SystemRoot%\System32\findstr.exe /R /C:":8001[ ]"') do (
    if "%%a" neq "0" (
        echo Killing PID %%a on port 8001...
        taskkill /F /PID %%a >nul 2>&1
    )
)

:: Kill process listening on port 8080
for /f "tokens=5" %%a in ('netstat -aon ^| %SystemRoot%\System32\findstr.exe /R /C:":8080[ ]"') do (
    if "%%a" neq "0" (
        echo Killing PID %%a on port 8080...
        taskkill /F /PID %%a >nul 2>&1
    )
)

echo.
echo Cleanup complete.
