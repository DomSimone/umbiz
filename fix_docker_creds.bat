@echo off
echo Fixing Docker Credentials Configuration...

set "DOCKER_CONFIG=%USERPROFILE%\.docker\config.json"

if exist "%DOCKER_CONFIG%" (
    echo Backing up existing config to config.json.bak...
    copy "%DOCKER_CONFIG%" "%USERPROFILE%\.docker\config.json.bak"
) else (
    if not exist "%USERPROFILE%\.docker" mkdir "%USERPROFILE%\.docker"
)

echo Writing clean configuration...
(
echo {
echo   "auths": {},
echo   "credsStore": ""
echo }
) > "%DOCKER_CONFIG%"

echo.
echo Configuration fixed.
echo Please run "deploy_docker.bat" again.
pause
