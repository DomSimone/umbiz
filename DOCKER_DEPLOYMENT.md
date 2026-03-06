# Umbuzo Model Docker Deployment

## Overview

The umbuzo_model.gguf (13.5 GB) has been deployed to a Docker container using volume mounting for optimal performance.

## Files Created

1. **Dockerfile.optimized** - Optimized Dockerfile that excludes the model from the image
2. **docker-compose.yml** - Docker Compose configuration with volume mount
3. **.dockerignore** - Excludes unnecessary files from build context
4. **deploy_umbuzo.bat** - Simple deployment script

## Architecture

- **Image**: Contains only the Python application and dependencies (~1 GB)
- **Model**: Mounted as a read-only volume from the host system
- **Benefits**: Fast builds, easy model updates, reduced image size

## Deployment

### Method 1: Using Docker Compose (Recommended)

```bash
docker-compose up -d
```

### Method 2: Using the Batch Script

Double-click `deploy_umbuzo.bat` or run:
```bash
deploy_umbuzo.bat
```

### Method 3: Manual Docker Build + Run

```bash
# Build the image
docker build -f Dockerfile.optimized -t umbuzo-api:latest .

# Run the container
docker run -d \
  --name umbuzo-api \
  -p 8001:8001 \
  -v ./umbuzo_model.gguf:/app/umbuzo_model.gguf:ro \
  umbuzo-api:latest
```

## Container Management

### View logs
```bash
docker logs -f umbuzo-api
```

### Check status
```bash
docker ps | findstr umbuzo-api
```

### Stop container
```bash
docker-compose down
```

### Restart container
```bash
docker-compose restart
```

## API Endpoints

- **Health Check**: http://localhost:8001/health
- **Chat**: http://localhost:8001/chat (POST)
- **Voice Chat**: http://localhost:8001/chat/voice (POST)

## Troubleshooting

### Container won't start
1. Check logs: `docker logs umbuzo-api`
2. Verify model file exists: `dir umbuzo_model.gguf`
3. Ensure port 8001 is not in use: `netstat -ano | findstr :8001`

### Model not loading
- Verify the model file path in docker-compose.yml matches your actual file location
- Check file permissions (should be readable)

### Out of memory
- The model requires significant RAM (8-16 GB recommended)
- Close other applications if needed
- Consider adjusting n_ctx parameter in umbuzo_api.py (currently 4096)

## Performance Notes

- First request may take longer as the model loads into memory
- Subsequent requests should be faster
- Model stays loaded in memory until container stops

## Next Steps

1. Wait for the Docker build to complete (background job running)
2. Run `docker-compose up -d` to start the container
3. Test the API: http://localhost:8001/health
4. Connect your frontend to http://localhost:8001
