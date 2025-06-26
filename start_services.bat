@echo off
chcp 65001 > nul
echo 🚀 ex-GPT + RAGFlow 통합 서비스 시작
echo ==================================

REM 색상 코드 정의 (Windows)
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

REM 1. 환경 확인
echo %BLUE%[INFO]%NC% 환경 확인 중...

REM Docker 확인
docker --version > nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%[ERROR]%NC% Docker가 설치되어 있지 않습니다.
    pause
    exit /b 1
)

REM Docker Compose 확인
docker-compose --version > nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%[ERROR]%NC% Docker Compose가 설치되어 있지 않습니다.
    pause
    exit /b 1
)

REM Poetry 확인
poetry --version > nul 2>&1
if %errorlevel% neq 0 (
    echo %YELLOW%[WARNING]%NC% Poetry가 설치되어 있지 않습니다. pip를 사용합니다.
    set USE_POETRY=false
) else (
    set USE_POETRY=true
)

echo %GREEN%[SUCCESS]%NC% 환경 확인 완료

REM 2. 환경 변수 설정
echo %BLUE%[INFO]%NC% 환경 변수 설정 확인 중...

if not exist ".env" (
    if exist ".env.example" (
        echo %YELLOW%[WARNING]%NC% .env 파일이 없습니다. .env.example에서 복사합니다.
        copy ".env.example" ".env" > nul
        echo %YELLOW%[WARNING]%NC% .env 파일을 편집하여 적절한 값을 설정해주세요.
    ) else (
        echo %RED%[ERROR]%NC% .env.example 파일을 찾을 수 없습니다.
        pause
        exit /b 1
    )
)

REM 3. Python 의존성 설치
echo %BLUE%[INFO]%NC% Python 의존성 설치 중...

if "%USE_POETRY%"=="true" (
    poetry install
    if %errorlevel% neq 0 (
        echo %RED%[ERROR]%NC% Poetry 의존성 설치 실패
        pause
        exit /b 1
    )
    echo %GREEN%[SUCCESS]%NC% Poetry로 의존성 설치 완료
) else (
    pip install fastapi uvicorn requests python-dotenv
    if %errorlevel% neq 0 (
        echo %RED%[ERROR]%NC% pip 의존성 설치 실패
        pause
        exit /b 1
    )
    echo %GREEN%[SUCCESS]%NC% pip로 기본 의존성 설치 완료
)

REM 4. 필요한 디렉토리 생성
echo %BLUE%[INFO]%NC% 디렉토리 구조 생성 중...

if not exist "data\uploads" mkdir "data\uploads"
if not exist "logs" mkdir "logs"
if not exist "models" mkdir "models"

echo %GREEN%[SUCCESS]%NC% 디렉토리 구조 생성 완료

REM 5. RAGFlow Docker 서비스 시작
echo %BLUE%[INFO]%NC% RAGFlow Docker 서비스 시작 중...

docker-compose -f docker-compose-ragflow.yaml up -d

if %errorlevel% neq 0 (
    echo %RED%[ERROR]%NC% RAGFlow Docker 서비스 시작 실패
    pause
    exit /b 1
)

echo %GREEN%[SUCCESS]%NC% RAGFlow Docker 서비스 시작 완료

REM 6. RAGFlow 서비스 준비 대기
echo %BLUE%[INFO]%NC% RAGFlow 서비스 준비 대기 중...

set RAGFLOW_HOST=http://localhost:8080
set MAX_WAIT=24
set WAIT_COUNT=0

:wait_loop
if %WAIT_COUNT% geq %MAX_WAIT% (
    echo %YELLOW%[WARNING]%NC% RAGFlow 서비스 준비 대기 시간 초과. 수동으로 확인해주세요.
    goto start_server
)

REM curl 명령 시뮬레이션 (PowerShell 사용)
powershell -Command "try { Invoke-WebRequest -Uri '%RAGFLOW_HOST%' -TimeoutSec 5 -UseBasicParsing | Out-Null; exit 0 } catch { exit 1 }" > nul 2>&1
if %errorlevel% equ 0 (
    echo %GREEN%[SUCCESS]%NC% RAGFlow 서비스가 준비되었습니다
    goto start_server
)

timeout /t 5 /nobreak > nul
set /a WAIT_COUNT+=1
echo .
goto wait_loop

:start_server
REM 7. ex-GPT 서버 시작
echo %BLUE%[INFO]%NC% ex-GPT 서버 시작 중...

if "%USE_POETRY%"=="true" (
    echo Poetry 환경에서 서버를 시작합니다...
    start "ex-GPT Server" poetry run python server.py
) else (
    echo 시스템 Python 환경에서 서버를 시작합니다...
    start "ex-GPT Server" python server.py
)

echo %GREEN%[SUCCESS]%NC% ex-GPT 서버 시작 완료

REM 8. 완료 메시지
echo.
echo 🎉 모든 서비스가 시작되었습니다!
echo ==================================
echo 📍 서비스 주소:
echo   - ex-GPT 웹 인터페이스: http://localhost:5001
echo   - RAGFlow 웹 인터페이스: http://localhost:8080
echo   - Elasticsearch: http://localhost:9200
echo   - MinIO 콘솔: http://localhost:9001
echo.
echo 📋 다음 단계:
echo   1. RAGFlow 웹 인터페이스에서 회원가입/로그인
echo   2. API 키 생성 및 .env 파일에 설정
echo   3. RAGFlow 통합 예제 실행: python ragflow_example.py
echo.
echo 🛑 서비스 중지: stop_services.bat 실행
echo.
echo 🔍 실시간 로그 확인:
echo   - RAGFlow: docker-compose -f docker-compose-ragflow.yaml logs -f
echo.

REM 웹 브라우저에서 서비스 열기
echo 🌐 웹 브라우저에서 서비스를 열까요?
choice /c YN /m "Y: 예, N: 아니오"
if %errorlevel% equ 1 (
    start http://localhost:5001
    start http://localhost:8080
)

echo.
echo 서비스가 백그라운드에서 실행 중입니다.
echo 종료하려면 stop_services.bat을 실행하세요.
pause
