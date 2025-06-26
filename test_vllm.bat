@echo off
echo ========================================
echo vLLM 연결 테스트
echo ========================================
echo.

echo [테스트] vLLM 서버 연결 확인...
echo 📡 서버 주소: http://localhost:8000
echo.

curl -X POST http://localhost:8000/v1/chat/completions ^
  -H "Content-Type: application/json" ^
  -d "{\"model\": \"Qwen/Qwen2.5-7B-Instruct\", \"messages\": [{\"role\": \"user\", \"content\": \"안녕하세요! 간단한 자기소개를 해주세요.\"}], \"max_tokens\": 100}"

if %errorlevel% equ 0 (
    echo.
    echo ✅ vLLM 서버 연결 성공!
) else (
    echo.
    echo ❌ vLLM 서버 연결 실패
    echo 🔧 문제 해결:
    echo    1. vLLM 서버가 실행 중인지 확인
    echo    2. start_vllm_cpu.bat 실행
    echo    3. 포트 8000이 사용 중인지 확인
)

echo.
pause
