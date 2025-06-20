@echo off
echo Setting up SmartReminder app...
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Install required packages
echo Installing required packages...
pip install -r requirements.txt

REM Install Gunicorn
echo Installing Gunicorn...
pip install gunicorn

REM Create data directory if it doesn't exist
if not exist "data" mkdir data

echo.
echo Starting SmartReminder app...
echo.
echo Press Ctrl+C to stop the server when done.
echo.

REM Run the app using the run.py script
python run.py

pause