@echo off
cd /d %~dp0

echo ==========================================================
echo  Deploying Umbuzo to a Self-Contained Docker Container
echo ==========================================================
echo.

:: Define Docker Command Path
set "DOCKER_EXE=docker"
if exist "C:\Program Files\Docker\Docker\resources\bin\docker.exe" (
    set "DOCKER_EXE=C:\Program Files\Docker\Docker\resources\bin\docker.exe"
)

:: --- CHECK IF DOCKER DESKTOP IS RUNNING ---
%SystemRoot%\System32\tasklist.exe /FI "IMAGENAME eq Docker Desktop.exe" | %SystemRoot%\System32\find.exe /I "Docker Desktop.exe" >nul
if %errorlevel% equ 0 (
    echo Docker Desktop is running.
) else (
    echo Docker Desktop is NOT running. Starting it now...
    if exist "C:\Program Files\Docker\Docker\Docker Desktop.exe" (
        start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    ) else (
        echo Error: Could not find Docker Desktop at expected path.
        echo Please start Docker manually.
        pause
        exit /b
    )

    echo Waiting for Docker to initialize...
    :WaitLoop
    %SystemRoot%\System32\timeout.exe /t 5 >nul
    "%DOCKER_EXE%" info >nul 2>&1
    if %errorlevel% neq 0 (
        echo ...still waiting
        goto WaitLoop
    )
    echo Docker is ready!
)

echo.
echo 1. Cleaning Docker Build Cache (Fixes memory/grpc errors)...
"%DOCKER_EXE%" builder prune -f >nul 2>&1

echo.
echo 2. Clearing Docker Credentials...
"%DOCKER_EXE%" logout >nul 2>&1

echo.
echo 3. Building Self-Contained Docker Image (umbuzo-api:latest)...
echo    This may take a while as the model is being copied into the image.
"%DOCKER_EXE%" build --no-cache -t umbuzo-api:latest .

echo.
echo 4. Stopping any existing container...
"%DOCKER_EXE%" stop umbuzo-container >nul 2>&1
"%DOCKER_EXE%" rm umbuzo-container >nul 2>&1

echo.
echo 5. Running the new container...
"%DOCKER_EXE%" run -d -p 8001:8001 --name umbuzo-container umbuzo-api:latest

echo.
echo ==========================================================
echo  Deployment Complete!
echo ==========================================================
echo.
echo Backend is running at: http://localhost:8001
echo.
echo To view logs: "%DOCKER_EXE%" logs -f umbuzo-container
echo.
pause
