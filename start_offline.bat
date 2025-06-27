@echo off
chcp 65001
echo ============================================
echo    ex-GPT 완전 오프라인 서버 시작
echo ============================================
echo.
echo 🔒 완전 격리 환경 - 인터넷 연결 불필요
echo 🚀 All AI processing happens locally
echo.

echo [1단계] 오프라인 의존성 확인...
python -c "import flask, flask_cors, requests" 2>nul
if %errorlevel% neq 0 (
    echo 기본 패키지 설치 중... (오프라인 모드)
    pip install flask flask-cors requests python-dotenv
    if %errorlevel% neq 0 (
        echo 오프라인 패키지 설치 실패. 미리 다운로드된 wheel 파일이 필요합니다.
        pause
        exit /b 1
    )
)

echo.
echo [2단계] Ollama 로컬 서비스 확인...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo Ollama가 실행되지 않음. 로컬 서비스 시작 시도...
    echo 주의: Ollama는 미리 설치되어 있어야 합니다.
    start "" "ollama" serve
    timeout /t 10 /nobreak >nul
    
    curl -s http://localhost:11434/api/tags >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ Ollama 서비스를 시작할 수 없습니다.
        echo 수동으로 "ollama serve" 명령을 실행해주세요.
        pause
    )
)

echo.
echo [3단계] 로컬 AI 모델 확인...
echo 사용 가능한 모델 확인 중...
ollama list 2>nul
if %errorlevel% neq 0 (
    echo ❌ Ollama CLI를 찾을 수 없습니다.
    echo Ollama가 설치되어 있는지 확인해주세요.
) else (
    echo ✅ Ollama 명령줄 도구 사용 가능
)

echo.
echo [4단계] 오프라인 데이터 디렉토리 준비...
if not exist data mkdir data
if not exist data\uploads mkdir data\uploads
if not exist data\vectorized mkdir data\vectorized
if not exist logs mkdir logs

echo.
echo [5단계] 완전 오프라인 서버 시작...
echo.
echo 🔒 보안 모드: Air-gapped (완전 격리)
echo 🌐 인터넷 연결: 불필요 (모든 처리가 로컬)
echo 🤖 AI 엔진: 로컬 Ollama + Qwen3:8b
echo 📊 웹 인터페이스: http://localhost:5000
echo 🔧 API 서버: http://localhost:11434 (Ollama)
echo.
echo 시작 중...

python server_offline.py

echo.
echo 서버가 종료되었습니다.
pause
