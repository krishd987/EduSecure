@echo off
echo Starting EduSecure Cheating Detection System...
echo.
echo Step 1: Starting Backend Server...
cd backend
call "..\.venv\Scripts\python.exe" app.py
timeout /t 3

echo.
echo Step 2: Starting Frontend...
cd ../frontend
start "Frontend Server" cmd /k "npm run dev"

echo.
echo Both servers are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Press any key to stop all servers...
pause > nul

echo.
echo Stopping servers...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
echo Servers stopped.
