# EduSecure - Cheating Detection Web Application

## Project Structure

```
final website/
├── frontend/          # React web application
│   ├── src/
│   ├── package.json
│   └── ... (web files)
├── backend/           # Python Flask API server
│   ├── app.py              # Main Flask server
│   ├── main.py             # Detection logic
│   ├── eye_movement_opencv.py
│   ├── head_pose_opencv.py
│   ├── mobile_detection.py
│   ├── best_yolov12.pt       # YOLO model
│   └── requirements.txt       # Python dependencies
├── .venv/             # Python virtual environment
└── start.bat          # Easy startup script
```

## Setup Instructions

### Backend Setup

1. **Virtual Environment (Already Included):**
   - The `.venv` folder contains all required Python packages
   - No need to install dependencies manually

2. **Start the Flask Server:**

   ```bash
   cd backend
   ..\.venv\Scripts\python.exe app.py
   ```

   Server will start at: `http://localhost:8000`

### Frontend Setup

1. **Install Node.js Dependencies:**

   ```bash
   cd frontend
   npm install
   ```

2. **Start the Development Server:**

   ```bash
   npm run dev
   ```

   Frontend will start at: `http://localhost:5173` (or similar)

### Quick Start

**Use the included startup script:**

```bash
start.bat
```

This will automatically start both backend and frontend servers.

## Deployment to Render

### Backend Deployment

1. **Automatic with `render.yaml`:**
   - I have created a `render.yaml` file in the root directory.
   - When you push this to your GitHub repository, Render will automatically detect it and configure the service correctly.

2. **Manual Dashboard Setup:**
   - **Service Type:** Web Service
   - **Environment:** Python
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `gunicorn --chdir backend app:app`
   - **Root Directory:** (Keep it as the repository root)
   - **Environment Variables:**
     - `PYTHON_VERSION`: `3.11.0`
     - `PORT`: `10000` (optional, Render handles this)

### Frontend Deployment

1. **Update API URL:**
   - In `frontend/src/App.tsx`, ensure the API URL points to your Render backend link (it usually looks like `https://edusecure-backend.onrender.com`).

2. **Deploy on Vercel/Netlify:**
   - Connect your GitHub repository.
   - Set the **Root Directory** to `frontend`.
   - Build Command: `npm run build`
   - Output Directory: `dist`

### Frontend Deployment

1. **Update API URL:**
   - In `frontend/src/App.tsx`, change `http://localhost:8000` to your Render backend URL

2. **Deploy on Vercel/Netlify:**
   - Connect your GitHub repository
   - Auto-deploy from `frontend` folder

## How It Works

1. **Calibration (First 5 seconds):**
   - Keep your head straight and looking at the screen
   - System calibrates your normal head position

2. **Detection Features:**
   - **Eye Movement Detection:** Tracks where you're looking
   - **Head Pose Detection:** Monitors head position and orientation
   - **Mobile Detection:** Detects phone usage in frame

3. **Alert System:**
   - Screenshots saved when suspicious behavior detected for 3+ seconds
   - Real-time feedback on web interface

## API Endpoints

- `POST /detect_base64` - Main detection endpoint
- `POST /reset_calibration` - Reset calibration
- `GET /health` - Health check

## Features

- ✅ Real-time cheating detection
- ✅ Web-based interface
- ✅ Automatic screenshot logging
- ✅ Mobile phone detection
- ✅ Eye movement tracking
- ✅ Head pose monitoring
- ✅ Calibration system
- ✅ Virtual environment included
- ✅ Deployment-ready

## Troubleshooting

1. **Camera Access:** Ensure browser has camera permissions
2. **Backend Connection:** Make sure Flask server is running on port 8000
3. **Model Loading:** Ensure `best_yolov12.pt` is in backend folder
4. **Virtual Environment:** Use the included .venv for all Python operations
5. **Deployment:** Follow Render/Vercel deployment guides above
