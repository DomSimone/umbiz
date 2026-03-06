@echo off
cd /d %~dp0

echo Starting Umbuzo System (Docker Backend + Local Frontend)...

:: Define Docker Command Path
set "DOCKER_EXE=docker"
if exist "C:\Program Files\Docker\Docker\resources\bin\docker.exe" (
    set "DOCKER_EXE=C:\Program Files\Docker\Docker\resources\bin\docker.exe"
)

:: --- CHECK IF DOCKER DESKTOP IS RUNNING ---
%SystemRoot%\System32\tasklist.exe /FI "IMAGENAME eq Docker Desktop.exe" | %SystemRoot%\System32\find.exe /I "Docker Desktop.exe" >nul
if %errorlevel% neq 0 (
    echo Docker Desktop is NOT running. Starting it now...
    if exist "C:\Program Files\Docker\Docker\Docker Desktop.exe" (
        start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    ) else (
        echo Error: Could not find Docker Desktop. Please start it manually.
        pause
        exit /b
    )
    echo Waiting for Docker to initialize...
    :WaitLoop
    %SystemRoot%\System32\timeout.exe /t 5 >nul
    "%DOCKER_EXE%" info >nul 2>&1
    if %errorlevel% neq 0 goto WaitLoop
    echo Docker is ready!
)

:: Check if container is running
"%DOCKER_EXE%" ps | %SystemRoot%\System32\findstr.exe "umbuzo-container" >nul
if %errorlevel% neq 0 (
    echo Container not running. Attempting to start...
    "%DOCKER_EXE%" start umbuzo-container
    if %errorlevel% neq 0 (
        echo Container does not exist. Please run 'deploy_docker.bat' first.
        pause
        exit /b
    )
) else (
    echo Backend Container is running.
)

:: Start Frontend (Simple Python HTTP Server)
echo Starting Frontend...
cd frontend
start "Umbuzo Frontend" cmd /k "python -m http.server 8080"

echo.
echo System Started!
echo Frontend: http://localhost:8080
echo Backend: http://localhost:8001/docs (Running in Docker)
echo.
pause
