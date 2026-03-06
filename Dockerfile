# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies that might be needed for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends build-essential

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application script and the frontend directory into the container
COPY umbuzo_api.py .
COPY frontend/ /app/frontend/

# The model will be downloaded on first run if not present, as handled by the script.

# Expose the port the app runs on
EXPOSE 8001

# Define the command to run the application
# The host 0.0.0.0 is important to make it accessible from outside the container
CMD ["uvicorn", "umbuzo_api:app", "--host", "0.0.0.0", "--port", "8001"]
