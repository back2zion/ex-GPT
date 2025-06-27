@echo off
chcp 65001 >nul
cls
echo.
echo ========================================
echo    🚀 ex-GPT 시작
echo ========================================
echo.

:: Python 확인
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python 설치 필요
    pause
    exit
)

:: Flask 설치
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo 📦 Flask 설치 중...
    pip install flask flask-cors requests
)

:: 서버 시작
echo ✅ 서버 시작 중...
echo.
start http://localhost:5000
python server.py
