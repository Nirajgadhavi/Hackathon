# PA Co-Pilot - Installation Guide for Windows

## Prerequisites

This project requires **Python 3.11 or higher** to run the backend API server.

## Step 1: Install Python 3.11

### Option A: Download from Python.org (Recommended)

1. Go to [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Download **Python 3.11.x** for Windows (latest stable version)
3. Run the installer
4. **IMPORTANT**: Check the box "Add Python to PATH" at the bottom of the installer
5. Click "Install Now"
6. Wait for installation to complete
7. Click "Close"

### Option B: Install from Microsoft Store

1. Open **Microsoft Store**
2. Search for "Python 3.11"
3. Click **Get** or **Install**
4. Wait for installation to complete

## Step 2: Verify Python Installation

Open a **new** PowerShell window and run:

```powershell
python --version
```

You should see output like: `Python 3.11.x`

If you see an error, restart your computer and try again.

## Step 3: Install Project Dependencies

In PowerShell, navigate to the project directory and run the setup script:

```powershell
cd C:\Users\2000156357\Projects\Hackathon\Hackathon
.\setup.ps1
```

If you get an error about execution policy, run this first:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try running `.\setup.ps1` again.

### Manual Installation (Alternative)

If the script doesn't work, you can install dependencies manually:

```powershell
pip install -r requirements.txt
```

## Step 4: Start the Backend Server

Run the startup script:

```powershell
.\start-backend.ps1
```

Or manually start the server:

```powershell
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Step 5: Start the Frontend (if not already running)

Open a **new** PowerShell window and run:

```powershell
cd C:\Users\2000156357\Projects\Hackathon\Hackathon\frontend
npm run dev
```

The frontend will run on http://localhost:5000

## Step 6: Access the Application

Open your browser and go to:

**http://localhost:5000**

The frontend will automatically connect to the backend API on port 8000.

## Troubleshooting

### "Python is not recognized"

- Make sure you checked "Add Python to PATH" during installation
- Restart your computer
- Try reinstalling Python

### "pip is not recognized"

- Reinstall Python and make sure pip is included
- Or download get-pip.py and run: `python get-pip.py`

### "Cannot run scripts" error

Run this command in PowerShell (as Administrator):

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Port 8000 already in use

Kill any process using port 8000:

```powershell
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
```

### API connection errors in frontend

- Make sure the backend is running on port 8000
- Check that you see "Uvicorn running on http://0.0.0.0:8000" in the backend terminal
- Refresh the frontend page

## Environment Variables (Optional)

For full AI-powered analysis, set your OpenAI API key:

```powershell
$env:OPENAI_API_KEY = "your-api-key-here"
```

Without this, the application runs in **Demo Mode** with simulated AI responses.

## Quick Start Commands

After Python is installed, here's the quick start:

```powershell
# Install dependencies (first time only)
.\setup.ps1

# Start backend (in one terminal)
.\start-backend.ps1

# Start frontend (in another terminal)
cd frontend
npm run dev
```

Then open http://localhost:5000 in your browser.

