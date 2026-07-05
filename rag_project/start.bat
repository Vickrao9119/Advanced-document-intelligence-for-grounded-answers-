@echo off
echo Starting SmartDocs AI Pro deployment...

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create data directories
echo Creating data directories...
if not exist "data\uploads" mkdir data\uploads
if not exist "data\docs" mkdir data\docs

REM Start Flask backend
echo Starting Flask backend on port 8000...
start "SmartDocs Backend" python backend/app.py

REM Wait for backend to start
timeout /t 5 /nobreak

REM Start Streamlit frontend
echo Starting Streamlit frontend on port 8501...
start "SmartDocs Frontend" python -m streamlit run src/app.py

echo Deployment complete!
echo Frontend: http://localhost:8501
echo Backend: http://localhost:8000
echo.
echo Press any key to stop services...
pause

REM Stop services (optional - you can also just close the windows)
taskkill /FI "WINDOWTITLE eq SmartDocs*" /T
