@echo off
echo ========================================
echo RAGFlow LLM API 키 설정 확인
echo ========================================
echo.

echo [확인] .env 파일 존재 여부...
if not exist ".env" (
    echo ❌ .env 파일이 없습니다.
    echo 📋 .env.example을 복사하여 .env 파일을 만들어주세요.
    echo.
    echo copy .env.example .env
    echo.
    goto :end
)

echo ✅ .env 파일 발견
echo.

echo [확인] LLM API 키 설정...
findstr /B "OPENAI_API_KEY=" .env >nul
if %errorlevel% equ 0 (
    echo ✅ OpenAI API 키 설정 발견
) else (
    echo ⚠️  OpenAI API 키가 설정되지 않음
)

findstr /B "ANTHROPIC_API_KEY=" .env >nul
if %errorlevel% equ 0 (
    echo ✅ Anthropic API 키 설정 발견
) else (
    echo ⚠️  Anthropic API 키가 설정되지 않음
)

findstr /B "GOOGLE_API_KEY=" .env >nul
if %errorlevel% equ 0 (
    echo ✅ Google API 키 설정 발견
) else (
    echo ⚠️  Google API 키가 설정되지 않음
)

echo.
echo ========================================
echo API 키 획득 방법:
echo ========================================
echo 🔗 OpenAI (권장):
echo    https://platform.openai.com/api-keys
echo.
echo 🔗 Anthropic (Claude):
echo    https://console.anthropic.com/
echo.
echo 🔗 Google (Gemini):
echo    https://makersuite.google.com/app/apikey
echo.
echo 📖 자세한 설정 방법: RAGFLOW_LLM_SETUP.md
echo ========================================

:end
echo.
pause
