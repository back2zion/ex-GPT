#!/bin/bash
echo "================================echo "[시작] Qwen2.5-14B-Instruct 모델 서버 시작..."
echo "📝 첫 실행 시 모델 다운로드로 시간이 걸릴 수 있습니다 (약 29GB)"
echo "🔗 서버 주소: http://localhost:8000"
echo "🛑 중지하려면 Ctrl+C를 누르세요"
echo

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7

python3 -m vllm.entrypoints.api_server \
    --model Qwen/Qwen2.5-14B-Instruct \
    --host 0.0.0.0 \
    --port 8000 \
    --tensor-parallel-size 8 \
    --gpu-memory-utilization 0.85 \
    --max-model-len 8192 \
    --max-num-seqs 256 \
    --trust-remote-code \
    --download-dir ./modelsLLM H100 8-GPU 모드로 Qwen2.5-7B 실행"
echo "========================================"
echo

echo "[확인] NVIDIA GPU 상태..."
nvidia-smi
if [ $? -ne 0 ]; then
    echo "❌ NVIDIA GPU 드라이버가 설치되지 않았습니다."
    echo "📦 NVIDIA GPU 드라이버 설치 필요"
    exit 1
fi

echo "[확인] CUDA 환경..."
nvcc --version 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️ CUDA 툴킷이 설치되지 않았습니다. (vLLM은 CUDA 런타임만 필요)"
fi

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
    echo "📦 vLLM GPU 버전 설치 중..."
    pip install vllm
    if [ $? -ne 0 ]; then
        echo "❌ vLLM 설치 실패"
        exit 1
    fi
fi

echo "✅ vLLM 설치 확인됨"
echo

echo "[GPU 정보]"
echo "🔥 H100 8대 병렬 처리 모드"
echo "💾 GPU 메모리 사용률: 85%"
echo "📏 최대 시퀀스 길이: 8192 토큰"
echo "🚀 최대 동시 요청: 256개"
echo

echo "[시작] Qwen2.5-7B 모델 서버 시작..."
echo "📝 첫 실행 시 모델 다운로드로 시간이 걸릴 수 있습니다 (약 14GB)"
echo "🔗 서버 주소: http://localhost:8000"
echo "🛑 중지하려면 Ctrl+C를 누르세요"
echo

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7

python3 -m vllm.entrypoints.api_server \
    --model Qwen/Qwen2.5-7B-Instruct \
    --host 0.0.0.0 \
    --port 8000 \
    --tensor-parallel-size 8 \
    --gpu-memory-utilization 0.85 \
    --max-model-len 8192 \
    --max-num-seqs 256 \
    --trust-remote-code

echo
echo "vLLM H100 서버가 종료되었습니다."
