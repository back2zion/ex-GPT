@echo off
echo ========================================
echo H100 vLLM 성능 테스트
echo ========================================
echo.

echo [GPU 상태 확인]
nvidia-smi --query-gpu=index,name,memory.total,memory.used,utilization.gpu --format=csv,noheader,nounits

echo.
echo [vLLM 서버 연결 테스트]
echo 📡 서버 주소: http://localhost:8000
echo.

echo "테스트 1: 단일 요청 처리 속도"
echo.
powershell -Command "Measure-Command { curl -X POST http://localhost:8000/v1/chat/completions -H 'Content-Type: application/json' -d '{\"model\": \"Qwen/Qwen2.5-14B-Instruct\", \"messages\": [{\"role\": \"user\", \"content\": \"한국의 수도는 어디인가요? 자세히 설명해주세요.\"}], \"max_tokens\": 200}' }"

echo.
echo "테스트 2: 긴 텍스트 생성 속도"
echo.
powershell -Command "Measure-Command { curl -X POST http://localhost:8000/v1/chat/completions -H 'Content-Type: application/json' -d '{\"model\": \"Qwen/Qwen2.5-14B-Instruct\", \"messages\": [{\"role\": \"user\", \"content\": \"인공지능의 역사와 발전 과정에 대해 1000단어 분량의 에세이를 작성해주세요.\"}], \"max_tokens\": 1000}' }"

echo.
echo "테스트 3: 코드 생성 테스트"
echo.
curl -X POST http://localhost:8000/v1/chat/completions ^
  -H "Content-Type: application/json" ^
  -d "{\"model\": \"Qwen/Qwen2.5-14B-Instruct\", \"messages\": [{\"role\": \"user\", \"content\": \"Python으로 이진 탐색 알고리즘을 구현하는 코드를 작성해주세요. 주석도 포함해서요.\"}], \"max_tokens\": 500}"

echo.
echo "테스트 4: vLLM 서버 통계"
echo.
curl http://localhost:8000/metrics

echo.
echo ========================================
echo 성능 테스트 완료
echo ========================================
pause
