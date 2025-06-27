@echo off
chcp 65001 >nul
cls
echo.
echo ========================================
echo    🤖 Ollama 설치
echo ========================================
echo.

echo 1. 자동 설치 시도 중...
winget install ollama
if %errorlevel% equ 0 (
    echo ✅ Ollama 설치 완료
    goto :model
)

echo.
echo 2. 수동 설치 필요
echo   https://ollama.ai 접속
echo   Download 클릭
echo   Windows 버전 다운로드 후 설치
echo.
pause

:model
echo.
echo 📦 모델 다운로드 중... (약 4GB)
ollama pull qwen2.5:7b

echo.
echo ✅ 설치 완료!
echo 서버 시작: start.bat
pause
