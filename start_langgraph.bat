@echo off
chcp 65001
echo ============================================
echo    ex-GPT LangGraph 기반 서버 시작
echo ============================================
echo.

echo [1단계] Poetry 의존성 설치 중...
poetry install
if %errorlevel% neq 0 (
    echo Poetry 설치 실패. requirements.txt로 대체 설치 시도...
    pip install -r requirements.enterprise.txt
)

echo.
echo [2단계] Ollama 서비스 확인 중...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo Ollama가 실행되지 않음. 자동 시작 중...
    start "" "ollama" serve
    timeout /t 5 /nobreak >nul
)

echo.
echo [3단계] Qwen2.5:3b 모델 확인 중...
ollama list | findstr "qwen2.5:3b" >nul 2>&1
if %errorlevel% neq 0 (
    echo Qwen2.5:3b 모델 다운로드 중... (시간이 걸릴 수 있습니다)
    ollama pull qwen2.5:3b
)

echo.
echo [4단계] 로그 디렉토리 생성...
if not exist logs mkdir logs

echo.
echo [5단계] LangGraph 서버 시작...
echo 🚀 ex-GPT Enterprise Edition (LangGraph 기반)
echo 🔗 서버 주소: http://localhost:5000
echo 📊 아키텍처: 사용자 질의 → LangGraph 라우터 → direct_llm/rag_search/query_expansion/mcp_action
echo.

poetry run python server_langgraph.py

pause
