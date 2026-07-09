@echo off
echo ====================================================================
echo   Smart City Traffic Patterns Forecasting & Analysis Pipeline
echo ====================================================================
echo.

echo [1/5] Downloading dataset from Google Drive...
.\venv\Scripts\python src/download_data.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Dataset download failed.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [2/5] Running Exploratory Data Analysis (EDA)...
.\venv\Scripts\python src/eda.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] EDA generation failed.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [3/5] Executing Model Training and Time-Series Forecasting...
.\venv\Scripts\python src/train.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Model training or forecasting failed.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [4/5] Serializing predictions for dashboard...
.\venv\Scripts\python src/generate_dashboard_data.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Dashboard data generation failed.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [5/5] Launching MetroPulse Interactive Dashboard...
start "" "dashboard/index.html"

echo.
echo ====================================================================
echo   Smart City Traffic Forecasting Pipeline Completed Successfully!
echo ====================================================================
echo.
pause
