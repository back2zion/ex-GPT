@echo off
chcp 65001 >nul
echo ========================================
echo 🚀 ex-GPT 데모 서버 (Ollama 없이 테스트)
echo ========================================
echo.
echo 이 서버는 Ollama 설치 없이 ex-GPT 시스템을
echo 테스트할 수 있도록 도와드립니다.
echo.

echo [1/3] Python 환경 확인...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되지 않았습니다.
    pause
    exit
)

echo [2/3] 필수 패키지 확인...
python -c "import flask" 2>nul
if %errorlevel% neq 0 (
    echo 📦 Flask 설치 중...
    pip install flask flask-cors
    if %errorlevel% neq 0 (
        echo ❌ 패키지 설치 실패
        pause
        exit
    )
)

echo [3/3] 데모 서버 시작...
echo.
echo ========================================
echo 🎉 ex-GPT 데모 서버 시작!
echo ========================================
echo.
echo 🌐 웹 주소: http://localhost:5000
echo 🤖 모드: 데모 (Ollama 없이 동작)
echo 📝 상태: 테스트용 응답 제공
echo.
echo ⚠️  실제 AI 기능을 위해서는 Ollama 설치 필요:
echo    1. https://ollama.ai 접속
echo    2. Windows 버전 다운로드
echo    3. 설치 후 'ollama pull qwen2.5:7b' 실행
echo.
echo 브라우저가 자동으로 열립니다...
timeout /t 3 /nobreak >nul
start http://localhost:5000

echo.
echo 데모 서버 시작 중...
python server_demo.py

echo.
echo 서버가 종료되었습니다.
pause
