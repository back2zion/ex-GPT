@echo off
echo ========================================
echo ex-GPT + RAGFlow 빠른 시작
echo ========================================
echo.

echo [확인] .env 파일의 LLM API 키 설정 확인 중...
if not exist ".env" (
    echo 경고: .env 파일이 없습니다.
    echo .env.example을 복사하여 .env 파일을 만들고 API 키를 설정해주세요.
    echo.
)

echo [1단계] RAGFlow Docker 서비스 시작 중...
docker-compose -f docker-compose-ragflow.yaml up -d

echo.
echo [2단계] 서비스 상태 확인 중...
timeout /t 10 >nul
docker ps --filter "name=ex-gpt-ragflow"

echo.
echo [3단계] RAGFlow 웹 인터페이스 열기...
echo RAGFlow 웹 인터페이스: http://localhost:8080
start http://localhost:8080

echo.
echo ========================================
echo 다음 단계:
echo ========================================
echo 1. RAGFlow 웹에서 계정 생성
echo 2. LLM API 키 설정:
echo    - .env 파일에 OPENAI_API_KEY 등 설정
echo    - 또는 RAGFlow 웹에서 Model providers 설정
echo 3. 채팅 어시스턴트 생성
echo 4. .env 파일에 어시스턴트 ID 입력
echo 5. start_ex_gpt.bat 실행
echo.
echo 📖 자세한 설정 방법: RAGFLOW_LLM_SETUP.md 참고
echo ========================================
echo.
pause
