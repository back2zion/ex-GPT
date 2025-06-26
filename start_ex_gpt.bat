@echo off
echo ========================================
echo ex-GPT 서버 시작
echo ========================================
echo.

echo [확인] .env 파일 설정 확인 중...
if not exist ".env" (
    echo 오류: .env 파일이 없습니다.
    echo .env.example을 복사하여 .env 파일을 만들고 설정해주세요.
    pause
    exit /b 1
)

echo [확인] Python 의존성 설치 중...
pip install -r requirements.txt 2>nul

echo.
echo [시작] ex-GPT 서버 시작 중...
echo 서버 주소: http://localhost:5001
echo 종료하려면 Ctrl+C를 누르세요.
echo.

python server.py
