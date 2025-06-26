@echo off
chcp 65001 > nul
echo 🛑 ex-GPT + RAGFlow 서비스 중지
echo ===============================

set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

echo %BLUE%[INFO]%NC% 서비스 중지 중...

REM ex-GPT 서버 프로세스 종료
echo %BLUE%[INFO]%NC% ex-GPT 서버 프로세스 종료 중...
taskkill /f /im python.exe /fi "WINDOWTITLE eq ex-GPT Server*" > nul 2>&1

REM RAGFlow Docker 서비스 중지
echo %BLUE%[INFO]%NC% RAGFlow Docker 서비스 중지 중...
docker-compose -f docker-compose-ragflow.yaml down

if %errorlevel% equ 0 (
    echo %GREEN%[SUCCESS]%NC% RAGFlow Docker 서비스 중지 완료
) else (
    echo %YELLOW%[WARNING]%NC% RAGFlow Docker 서비스 중지에 문제가 있을 수 있습니다
)

REM 포트 점검 및 정리
echo %BLUE%[INFO]%NC% 포트 사용 상태 확인 중...

netstat -ano | findstr :5001 > nul
if %errorlevel% equ 0 (
    echo %YELLOW%[WARNING]%NC% 포트 5001이 여전히 사용 중입니다
    for /f "tokens=5" %%i in ('netstat -ano ^| findstr :5001') do (
        echo 프로세스 %%i를 종료합니다...
        taskkill /f /pid %%i > nul 2>&1
    )
)

netstat -ano | findstr :8080 > nul
if %errorlevel% equ 0 (
    echo %YELLOW%[WARNING]%NC% 포트 8080이 여전히 사용 중입니다 (Docker 컨테이너 확인 필요)
)

echo %GREEN%[SUCCESS]%NC% 모든 서비스가 중지되었습니다

echo.
echo 📋 정리 작업:
echo   - ex-GPT 서버: 중지됨
echo   - RAGFlow Docker 컨테이너: 중지됨
echo   - 데이터는 보존됨
echo.
echo 💡 서비스를 다시 시작하려면 start_services.bat을 실행하세요

pause
