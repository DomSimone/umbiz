@echo off
cd /d %~dp0

echo ==========================================================
echo  Umbuzo System Diagnostic Tool
echo ==========================================================
echo.

:: Define Docker Command Path
set "DOCKER_EXE=docker"
if exist "C:\Program Files\Docker\Docker\resources\bin\docker.exe" (
    set "DOCKER_EXE=C:\Program Files\Docker\Docker\resources\bin\docker.exe"
)

:: 1. Check Docker Desktop
echo [1/3] Checking Docker Desktop...
"%DOCKER_EXE%" info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Desktop is NOT running.
    echo Please start Docker Desktop and try again.
    pause
    exit /b
)
echo [OK] Docker is running.
echo.

:: 2. Check Container Status
echo [2/3] Checking Backend Container (umbuzo-container)...
"%DOCKER_EXE%" ps | %SystemRoot%\System32\findstr.exe "umbuzo-container" >nul
if %errorlevel% equ 0 (
    echo [OK] Container is RUNNING.
    echo.
    echo Backend should be accessible at http://localhost:8001
    echo If you still cannot connect, check if port 8001 is blocked by a firewall.
    echo.
    echo [3/3] Fetching recent logs to check for internal errors...
    echo ---------------------------------------------------
    "%DOCKER_EXE%" logs --tail 50 umbuzo-container
    echo ---------------------------------------------------
) else (
    echo [ERROR] Container is NOT running.

    :: Check if it exists but stopped
    "%DOCKER_EXE%" ps -a | %SystemRoot%\System32\findstr.exe "umbuzo-container" >nul
    if %errorlevel% equ 0 (
        echo Container exists but is STOPPED.
        echo.
        echo [3/3] Fetching crash logs...
        echo ---------------------------------------------------
        "%DOCKER_EXE%" logs --tail 50 umbuzo-container
        echo ---------------------------------------------------
    ) else (
        echo [ERROR] Container does not exist.
        echo Please run 'deploy_docker.bat' to build and create it.
    )
)

echo.
pause
