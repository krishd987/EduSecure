# Stage 1: Build the frontend
FROM node:20 AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Set up the Python backend
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies required by OpenCV and MediaPipe
RUN apt-get update && apt-get install -y \
    libgl1 \
    libgles2 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies using CPU-only version of PyTorch
COPY requirements.txt ./
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
COPY backend/ ./backend/

# Copy the built frontend from Stage 1 into the location expected by Flask
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose the port Gunicorn will listen on
EXPOSE 10000

# Set environment variables
ENV PORT=10000
ENV PYTHONUNBUFFERED=1

# Start the application
CMD cd backend && gunicorn --bind 0.0.0.0:$PORT --workers 4 --threads 2 --timeout 120 app:app
