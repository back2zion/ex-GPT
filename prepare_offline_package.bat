@echo off
chcp 65001 >nul
echo ========================================
echo 📦 ex-GPT 오프라인 패키지 준비 도구
echo ========================================
echo.
echo 이 스크립트는 인터넷 연결이 있는 환경에서 실행하여
echo Air-Gapped 환경으로 이전할 오프라인 패키지를 준비합니다.
echo.

set PACKAGE_DIR=ex-gpt-offline-package
set DOWNLOADS_DIR=%PACKAGE_DIR%\downloads

echo [1/6] 디렉토리 구조 생성...
if exist %PACKAGE_DIR% rmdir /s /q %PACKAGE_DIR%
mkdir %PACKAGE_DIR%
mkdir %DOWNLOADS_DIR%
mkdir %DOWNLOADS_DIR%\python-packages
mkdir %DOWNLOADS_DIR%\ollama-installer
mkdir %DOWNLOADS_DIR%\models

echo ✅ 디렉토리 구조 생성 완료

echo.
echo [2/6] Python 패키지 다운로드...
pip download -r requirements.offline.txt -d %DOWNLOADS_DIR%\python-packages --no-deps
if %errorlevel% neq 0 (
    echo ❌ Python 패키지 다운로드 실패
    pause
    exit
)
echo ✅ Python 패키지 다운로드 완료

echo.
echo [3/6] Ollama 설치 파일 다운로드...
powershell -Command "Invoke-WebRequest -Uri 'https://ollama.ai/download/windows' -OutFile '%DOWNLOADS_DIR%\ollama-installer\ollama-windows-amd64.exe'"
if %errorlevel% neq 0 (
    echo ❌ Ollama 다운로드 실패
    pause
    exit
)
echo ✅ Ollama 다운로드 완료

echo.
echo [4/6] 프로젝트 파일 복사...
xcopy /E /I /H /Y . %PACKAGE_DIR%\ex-gpt-demo
del /q %PACKAGE_DIR%\ex-gpt-demo\*.log 2>nul
rmdir /s /q %PACKAGE_DIR%\ex-gpt-demo\logs 2>nul
rmdir /s /q %PACKAGE_DIR%\ex-gpt-demo\__pycache__ 2>nul
rmdir /s /q %PACKAGE_DIR%\ex-gpt-demo\data\uploads 2>nul
echo ✅ 프로젝트 파일 복사 완료

echo.
echo [5/6] 설치 스크립트 생성...
(
echo @echo off
echo chcp 65001 ^>nul
echo echo ========================================
echo echo 🔒 ex-GPT 오프라인 환경 설치
echo echo ========================================
echo echo.
echo.
echo echo [1/4] Ollama 설치...
echo start /wait downloads\ollama-installer\ollama-windows-amd64.exe
echo.
echo echo [2/4] Python 패키지 설치...
echo cd ex-gpt-demo
echo pip install --no-index --find-links ..\downloads\python-packages -r requirements.offline.txt
echo.
echo echo [3/4] 디렉토리 구조 생성...
echo if not exist data mkdir data
echo if not exist data\uploads mkdir data\uploads
echo if not exist logs mkdir logs
echo.
echo echo [4/4] 설치 완료!
echo echo ✅ 오프라인 설치 완료
echo echo 🚀 서버 시작: start_offline.bat
echo pause
) > %PACKAGE_DIR%\install_offline.bat

echo ✅ 설치 스크립트 생성 완료

echo.
echo [6/6] 사용 가이드 생성...
(
echo # ex-GPT 오프라인 패키지 사용법
echo.
echo ## 1. Air-Gapped 시스템으로 전체 폴더 복사
echo   ex-gpt-offline-package/ 폴더를 USB나 외장디스크로 복사
echo.
echo ## 2. 오프라인 시스템에서 설치 실행
echo   install_offline.bat 실행
echo.
echo ## 3. 시스템 상태 점검
echo   cd ex-gpt-demo
echo   check_offline_system.bat
echo.
echo ## 4. 서버 시작
echo   start_offline.bat
echo.
echo ## 5. 웹 접속
echo   브라우저에서 http://localhost:5000 접속
echo.
echo ## 참고사항
echo - 최소 요구사항: Python 3.8+, 8GB RAM
echo - 권장 사양: 16GB RAM, SSD 스토리지
echo - 모델 크기: Qwen2.5:7B 약 4.1GB
) > %PACKAGE_DIR%\README_OFFLINE.md

echo ✅ 사용 가이드 생성 완료

echo.
echo ========================================
echo 📦 오프라인 패키지 준비 완료!
echo ========================================
echo.
echo 📁 패키지 위치: %PACKAGE_DIR%\
echo 📋 포함된 구성요소:
echo   - ex-GPT 프로젝트 전체
echo   - Python 패키지 (오프라인)
echo   - Ollama 설치 파일
echo   - 자동 설치 스크립트
echo   - 사용법 가이드
echo.
echo 🚀 다음 단계:
echo   1. %PACKAGE_DIR% 폴더를 Air-Gapped 시스템으로 복사
echo   2. install_offline.bat 실행
echo   3. 시스템 점검 후 서버 시작
echo.
pause
