# Stage 1: Build the frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Set up the Python backend (lightweight for Render free tier)
FROM python:3.11-slim
WORKDIR /app

# Install minimal system dependencies (OpenCV headless needs very little)
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install lightweight Python dependencies (no PyTorch/YOLO/MediaPipe)
COPY requirements-render.txt ./
RUN pip install --no-cache-dir -r requirements-render.txt

# Copy the backend code
COPY backend/ ./backend/

# Copy the built frontend from Stage 1 into the location expected by Flask
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose the port Gunicorn will listen on
EXPOSE 10000

# Set environment variables
ENV PORT=10000
ENV PYTHONUNBUFFERED=1
ENV LOW_MEMORY_MODE=true

# Start the application (1 worker to minimize memory)
CMD cd backend && gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120 app:app
