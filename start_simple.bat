@echo off
chcp 65001
echo ============================================
echo    ex-GPT 간단 서버 시작 (임시 Ollama)
echo ============================================
echo.

echo [1단계] 기본 의존성 확인...
python -c "import flask, flask_cors, requests" 2>nul
if %errorlevel% neq 0 (
    echo 기본 패키지 설치 중...
    pip install flask flask-cors requests python-dotenv
)

echo.
echo [2단계] 간단 서버 시작...
echo 🚀 ex-GPT Simple Server
echo 🔗 서버 주소: http://localhost:5000
echo ⚠️  주의: 임시로 Ollama 사용 중 - UI 테스트용
echo.

python server_simple.py

pause
