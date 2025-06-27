@echo off
echo ========================================
echo Ollama 설치 및 실행
echo ========================================
echo.

echo [다운로드] Ollama Windows 버전...
powershell -Command "Invoke-WebRequest -Uri 'https://ollama.ai/download/windows' -OutFile 'ollama-windows-amd64.exe'"

echo [설치] Ollama...
start /wait ollama-windows-amd64.exe

echo [확인] Ollama 설치 상태...
ollama --version

echo [다운로드] Qwen2.5-7B 모델...
ollama pull qwen2.5:7b

echo [실행] Ollama 서버...
start ollama serve

echo.
echo ✅ Ollama 설치 및 실행 완료!
echo 🌐 서버 주소: http://localhost:11434
echo 📝 .env 파일에서 OLLAMA_BASE_URL 확인
pause
