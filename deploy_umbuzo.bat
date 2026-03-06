@echo off
REM Deploy Umbuzo Model with Docker Compose

echo Building and deploying Umbuzo API container...
echo.

REM Build the Docker image (if not already built)
docker build -f Dockerfile.optimized -t umbuzo-api:latest .

if errorlevel 1 (
    echo ERROR: Docker build failed!
    pause
    exit /b 1
)

echo.
echo Build complete! Starting container with docker-compose...
echo.

REM Start the container with docker-compose
docker-compose up -d

if errorlevel 1 (
    echo ERROR: Failed to start container!
    pause
    exit /b 1
)

echo.
echo ================================================
echo Umbuzo API deployed successfully!
echo ================================================
echo.
echo Container name: umbuzo-api
echo API URL: http://localhost:8001
echo Health check: http://localhost:8001/health
echo.
echo To view logs: docker logs -f umbuzo-api
echo To stop: docker-compose down
echo.
pause
