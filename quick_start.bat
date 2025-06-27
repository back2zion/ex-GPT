@echo off
chcp 65001 >nul
echo ========================================
echo 🚀 ex-GPT 빠른 시작 및 데모
echo ========================================
echo.
echo 이 스크립트는 ex-GPT 시스템을 빠르게 시작하고
echo 기본 기능을 테스트할 수 있도록 도와줍니다.
echo.

echo [1/5] 시스템 환경 점검...
call check_offline_system.bat
if %errorlevel% neq 0 (
    echo.
    echo ❌ 시스템 점검 실패. 먼저 문제를 해결해주세요.
    pause
    exit
)

echo.
echo [2/5] Ollama 서버 시작...
tasklist | findstr ollama >nul
if %errorlevel% neq 0 (
    echo Ollama 서버 시작 중...
    start /min ollama serve
    timeout /t 15 /nobreak >nul
    echo ✅ Ollama 서버 시작 완료
) else (
    echo ✅ Ollama 서버 이미 실행 중
)

echo.
echo [3/5] 모델 다운로드 확인...
ollama list | findstr qwen2.5 >nul
if %errorlevel% neq 0 (
    echo Qwen2.5:7B 모델 다운로드 중... (약 4.1GB)
    echo 이 과정은 시간이 걸릴 수 있습니다.
    ollama pull qwen2.5:7b
    if %errorlevel% neq 0 (
        echo ❌ 모델 다운로드 실패
        pause
        exit
    )
    echo ✅ 모델 다운로드 완료
) else (
    echo ✅ Qwen2.5 모델 사용 가능
)

echo.
echo [4/5] 기본 AI 테스트...
echo 테스트 질문 전송 중...
curl -s -X POST http://localhost:11434/api/generate ^
  -H "Content-Type: application/json" ^
  -d "{\"model\":\"qwen2.5:7b\",\"prompt\":\"안녕하세요! 간단한 인사를 해주세요.\",\"stream\":false}" | findstr "response" >nul

if %errorlevel% equ 0 (
    echo ✅ AI 모델 응답 정상
) else (
    echo ⚠️  AI 모델 응답 확인 필요
)

echo.
echo [5/5] ex-GPT 웹 서버 시작...
echo.
echo ========================================
echo 🎉 ex-GPT 준비 완료!
echo ========================================
echo.
echo 🌐 웹 인터페이스: http://localhost:5000
echo 🤖 AI 엔진: Ollama + Qwen2.5:7B
echo 🔒 실행 모드: 완전 오프라인
echo 📁 업로드 폴더: data/uploads/
echo 📊 로그 파일: logs/offline.log
echo.
echo 브라우저가 자동으로 열립니다...
timeout /t 3 /nobreak >nul
start http://localhost:5000

echo.
echo 서버 시작 중...
python server_offline.py

echo.
echo 서버가 종료되었습니다.
echo 재시작하려면 이 스크립트를 다시 실행하세요.
pause
