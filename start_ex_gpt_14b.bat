@echo off
echo ========================================
echo ex-GPT 전체 시스템 자동 실행
echo ========================================
echo.

echo 🎯 ex-GPT + Qwen2.5-14B-Instruct를 자동으로 실행합니다.
echo.

echo [1단계] 환경 확인...
if not exist ".env" (
    echo ❌ .env 파일이 없습니다.
    echo 📋 .env.template을 .env로 복사합니다...
    copy .env.template .env
    echo ✅ .env 파일 생성 완료
)

echo [2단계] Python 의존성 확인...
pip show vllm >nul 2>&1
if %errorlevel% neq 0 (
    echo 📦 vLLM 설치 중...
    pip install vllm
)

echo [3단계] Qwen2.5-14B-Instruct 시작...
echo 🔥 백그라운드에서 LLM 서버를 시작합니다...
start "Qwen2.5-14B Server" cmd /c start_qwen14b.bat

echo ⏳ LLM 서버 초기화 대기 중... (약 2-5분)
timeout /t 10 /nobreak >nul

echo [4단계] ex-GPT 웹 서버 시작...
echo 🌐 ex-GPT 서버를 시작합니다...
echo 🔗 브라우저에서 http://localhost:5001 을 열어주세요
echo.

python server.py

echo.
echo ex-GPT 시스템이 종료되었습니다.
pause
