@echo off
chcp 65001 >nul
echo ========================================
echo Ollama 경로 확인 및 설정
echo ========================================
echo.

echo [확인] Ollama 실행 파일 위치...
if exist "C:\Users\user\AppData\Local\Programs\Ollama\ollama.exe" (
    echo ✅ 발견: C:\Users\user\AppData\Local\Programs\Ollama\ollama.exe
    set OLLAMA_PATH=C:\Users\user\AppData\Local\Programs\Ollama\ollama.exe
) else (
    echo ❌ 기본 경로에 없음. 다른 위치 확인 중...
    where ollama >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ PATH에서 발견
        set OLLAMA_PATH=ollama
    ) else (
        echo ❌ Ollama를 찾을 수 없습니다.
        echo 📁 수동으로 확인해주세요: %USERPROFILE%\AppData\Local\Programs\Ollama\
        pause
        exit /b 1
    )
)

echo.
echo [테스트] Ollama 버전 확인...
"%OLLAMA_PATH%" --version

echo.
echo [테스트] 설치된 모델 목록...
"%OLLAMA_PATH%" list

echo.
pause
