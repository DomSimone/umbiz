@echo off
REM Quick status check for Umbuzo API container

echo ================================================
echo Umbuzo API Container Status
echo ================================================
echo.

echo [1/4] Checking if container is running...
docker ps --filter "name=umbuzo-api" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.

echo [2/4] Checking API health...
curl -s http://localhost:8001/health 2>nul
if errorlevel 1 (
    echo ERROR: Cannot reach API health endpoint
    echo Make sure the container is running: docker logs umbuzo-api
) else (
    echo.
)
echo.

echo [3/4] Recent logs (last 20 lines):
docker logs --tail 20 umbuzo-api 2>nul
echo.

echo [4/4] Resource usage:
docker stats umbuzo-api --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
echo.

echo ================================================
echo Commands:
echo   View logs: docker logs -f umbuzo-api
echo   Restart:   docker-compose restart
echo   Stop:      docker-compose down
echo ================================================
pause
