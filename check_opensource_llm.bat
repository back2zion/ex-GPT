@echo off
echo ========================================
echo 오픈소스 LLM 서버 연결 확인
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

echo [확인] 오픈소스 LLM 서버 설정...

findstr "OLLAMA_BASE_URL=" .env >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Ollama 서버 URL 설정됨
) else (
    echo ❌ Ollama 서버 URL 설정 없음
)

findstr "VLLM_BASE_URL=" .env >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ vLLM 서버 URL 설정됨
) else (
    echo ❌ vLLM 서버 URL 설정 없음  
)

echo.
echo ========================================
echo 오픈소스 LLM 서버 설치 방법:
echo ========================================
echo.
echo 📦 Ollama (추천 - 간편한 로컬 LLM):
echo    1. https://ollama.ai/download 에서 다운로드
echo    2. 설치 후: ollama pull llama2
echo    3. 모델 실행: ollama run llama2
echo.
echo 📦 vLLM (고성능 서빙):
echo    1. pip install vllm
echo    2. 모델 서빙: python -m vllm.entrypoints.api_server --model microsoft/DialoGPT-medium
echo.
echo 📖 자세한 설정 방법: RAGFLOW_LLM_SETUP.md
echo ========================================
echo.

:end
pause
