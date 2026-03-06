# Umbuzo AI System

Umbuzo is a specialized AI chatbot for African history, current affairs, and academics. It features a modern web interface, voice interaction capabilities, and a robust Dockerized backend hosting a local GGUF model.

## Project Workflow

1.  **User Interface (Frontend)**:
    *   A responsive web app (`frontend/`) built with HTML, CSS, and Vanilla JS.
    *   Features: Chat interface, Voice Input (Speech-to-Text), Text-to-Speech responses, and Topic Selection.
    *   Communicates with the backend via REST API.

2.  **Backend Server (Docker Container)**:
    *   A FastAPI server (`umbuzo_api.py`) running inside a Docker container.
    *   **Model**: Hosts the `umbuzo-gemma-2b-v3data.f16.gguf` LLM directly within the container for reliability.
    *   **Voice Processing**: Uses `SpeechRecognition` for input and `gTTS` for output.
    *   **API**: Exposes endpoints for text chat (`/chat`) and voice chat (`/chat/voice`).

3.  **Deployment**:
    *   The system is deployed using a self-contained Docker image (`umbuzo-api:latest`).
    *   This approach avoids common Windows file-sharing issues by bundling the model and code together.

## Prerequisites

*   **Docker Desktop**: Must be installed and running.
*   **Python 3.9+**: Required for local scripts (though the backend runs in Docker).
*   **Model File**: `umbuzo-gemma-2b-v3data.f16.gguf` must be present in the root folder (`B:\Stripper\`).

## Quick Start Guide

### 1. Initial Setup (Build & Deploy)
Run this script **once** to build the Docker image and create the container. This step copies the large model file into the container, so it may take a few minutes.

*   **Script**: `deploy_docker.bat`
*   **Action**: Double-click the file in Windows Explorer.

### 2. Daily Usage (Start System)
Run this script to start the backend container (if stopped) and launch the frontend web server.

*   **Script**: `start_umbuzo_full_system.bat`
*   **Action**: Double-click the file.
*   **Access**: The web interface will open at `http://localhost:8080`.

### Running direct servers for terminal in frontend.
2.
Run: npm install http-server
Run: npx http-server -p 8080

### 3. Troubleshooting
If you encounter port conflicts (e.g., "Address already in use"), run this script to force-close lingering processes.

*   **Script**: `kill_ports.bat`

## File Structure

*   **`frontend/`**: Web interface files (`index.html`, `app.js`, `styles.css`, `Mbuzo.png`).
*   **`umbuzo_api.py`**: The Python backend logic (FastAPI, Llama-cpp, Voice).
*   **`Dockerfile`**: Blueprint for the backend container image.
*   **`umbuzo-gemma-2b-v3data.f16.gguf`**: The local Large Language Model file.
*   **`deploy_docker.bat`**: Script to build the image and create the container.
*   **`start_umbuzo_full_system.bat`**: Script to start the system for daily use.
*   **`kill_ports.bat`**: Utility to free up ports 8001 and 8080.

## Voice Features
*   Click the **Microphone Icon** in the chat bar to start recording.
*   Speak your query.
*   Click the microphone again to stop and send.
*   Umbuzo will process your speech and respond with both text and audio.
