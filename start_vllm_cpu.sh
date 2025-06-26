#!/bin/bash
echo "===========echo "[시작] Qwen2.5-14B-Instruct 모델 서버 시작..."
echo "📝 첫 실행 시 모델 다운로드로 시간이 걸릴 수 있습니다 (약 29GB)"
echo "🔗 서버 주소: http://localhost:8000"
echo "🛑 중지하려면 Ctrl+C를 누르세요"
echo

python3 -m vllm.entrypoints.api_server \
    --model Qwen/Qwen2.5-14B-Instruct \
    --host 0.0.0.0 \
    --port 8000 \
    --cpu-only \
    --max-model-len 4096 \
    --max-num-seqs 4 \
    --trust-remote-code \
    --download-dir ./models================"
echo "vLLM CPU 모드로 Qwen2.5-7B 실행"
echo "========================================"
echo

echo "[확인] Python 환경..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python이 설치되지 않았습니다."
    echo "📦 Python 3.8+ 설치 필요"
    exit 1
fi

echo "[확인] vLLM 설치 상태..."
pip show vllm >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ vLLM이 설치되지 않았습니다."
    echo "📦 vLLM 설치 중..."
    pip install vllm
    if [ $? -ne 0 ]; then
        echo "❌ vLLM 설치 실패"
        exit 1
    fi
fi

echo "✅ vLLM 설치 확인됨"
echo

echo "[시작] Qwen2.5-7B 모델 서버 시작..."
echo "📝 첫 실행 시 모델 다운로드로 시간이 걸릴 수 있습니다 (약 14GB)"
echo "🔗 서버 주소: http://localhost:8000"
echo "🛑 중지하려면 Ctrl+C를 누르세요"
echo

python3 -m vllm.entrypoints.api_server \
    --model Qwen/Qwen2.5-7B-Instruct \
    --host 0.0.0.0 \
    --port 8000 \
    --cpu-only \
    --max-model-len 4096 \
    --max-num-seqs 4

echo
echo "vLLM 서버가 종료되었습니다."
