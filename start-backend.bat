@echo off
echo ========================================
echo Starting PA Co-Pilot Backend Server
echo ========================================
echo.
echo Backend will run on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

