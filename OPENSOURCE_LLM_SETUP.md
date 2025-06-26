# 오픈소스 LLM 설정 가이드

ex-GPT는 오픈소스 LLM을 사용하여 완전히 자체 호스팅이 가능한 AI 채팅 시스템입니다.

## 🎯 지원하는 오픈소스 LLM

### 1. Ollama (추천 - 초보자용)
- **장점**: 설치가 매우 간단, 모델 관리 자동화
- **단점**: 상대적으로 낮은 성능
- **용도**: 개발/테스트, 개인 사용

### 2. vLLM (고성능)
- **장점**: 매우 빠른 추론 속도, 배치 처리 최적화
- **단점**: 설정이 복잡, GPU 메모리 요구량 높음  
- **용도**: 프로덕션 환경, 대량 사용자

## 🚀 Ollama 설치 및 설정

### 1단계: Ollama 설치
```bash
# Windows
# https://ollama.ai/download 에서 설치 프로그램 다운로드

# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh
```

### 2단계: 한국어 모델 설치
```bash
# 추천 모델들
ollama pull llama2:7b-chat          # 7B 모델 (4GB GPU 메모리)
ollama pull llama2:13b-chat         # 13B 모델 (8GB GPU 메모리)
ollama pull codellama:7b-code       # 코드 생성 특화

# 한국어 특화 모델
ollama pull solar:10.7b-instruct    # 한국어 성능 우수
ollama pull kullm:5.8b              # 한국어 전용 모델
```

### 3단계: 모델 실행
```bash
# 모델 서빙 시작
ollama serve

# 별도 터미널에서 모델 실행
ollama run llama2:7b-chat
```

### 4단계: 환경 변수 설정
`.env` 파일에 다음 추가:
```env
OLLAMA_BASE_URL=http://localhost:11434
```

## ⚡ vLLM 설치 및 설정

### 1단계: vLLM 설치
```bash
# GPU 환경 (CUDA 필요)
pip install vllm

# CPU 환경 (성능 저하)
pip install vllm[cpu]
```

### 2단계: 모델 다운로드
```bash
# Hugging Face에서 모델 다운로드
from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "microsoft/DialoGPT-medium"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
```

### 3단계: vLLM 서버 실행
```bash
# 기본 실행
python -m vllm.entrypoints.api_server \
    --model microsoft/DialoGPT-medium \
    --host 0.0.0.0 \
    --port 8000

# 고성능 설정 (GPU 메모리 8GB 이상)
python -m vllm.entrypoints.api_server \
    --model microsoft/DialoGPT-large \
    --tensor-parallel-size 2 \
    --gpu-memory-utilization 0.8 \
    --host 0.0.0.0 \
    --port 8000
```

### 4단계: 환경 변수 설정
`.env` 파일에 다음 추가:
```env
VLLM_BASE_URL=http://localhost:8000
```

## 💻 CPU에서 vLLM 실행하기 (GPU 없이)

### Qwen2.5-7B 모델 설정

#### 1단계: vLLM CPU 버전 설치
```bash
# CPU 전용 vLLM 설치
pip install vllm[cpu]

# 또는 전체 설치 후 CPU 모드로 실행
pip install vllm
```

#### 2단계: Qwen2.5-7B 모델 다운로드
```bash
# Hugging Face에서 자동 다운로드됨 (첫 실행 시)
# 약 14GB 저장 공간 필요
```

#### 3단계: CPU 모드로 vLLM 서버 실행
```bash
# 기본 CPU 실행
python -m vllm.entrypoints.api_server \
    --model Qwen/Qwen2.5-7B-Instruct \
    --host 0.0.0.0 \
    --port 8000 \
    --cpu-only

# 메모리 최적화 실행 (RAM 16GB 이하인 경우)
python -m vllm.entrypoints.api_server \
    --model Qwen/Qwen2.5-7B-Instruct \
    --host 0.0.0.0 \
    --port 8000 \
    --cpu-only \
    --max-model-len 2048 \
    --max-num-seqs 4

# 고성능 CPU 실행 (RAM 32GB 이상)
python -m vllm.entrypoints.api_server \
    --model Qwen/Qwen2.5-7B-Instruct \
    --host 0.0.0.0 \
    --port 8000 \
    --cpu-only \
    --max-model-len 4096 \
    --max-num-seqs 8
```

#### 4단계: 환경 변수 설정
`.env` 파일 설정:
```env
MODEL_NAME=Qwen/Qwen2.5-7B-Instruct
VLLM_BASE_URL=http://localhost:8000
VLLM_CPU_ONLY=True
VLLM_MAX_MODEL_LEN=4096
```

### 🎯 CPU 성능 최적화 팁

#### 하드웨어 요구사항
- **최소**: RAM 16GB, CPU 4코어
- **권장**: RAM 32GB, CPU 8코어 이상
- **최적**: RAM 64GB, CPU 16코어 이상

#### 성능 튜닝
```bash
# 1. 메모리 부족 시 - 모델 길이 축소
--max-model-len 2048

# 2. 동시 요청 수 조정
--max-num-seqs 4

# 3. CPU 코어 수 설정 (자동 감지하지만 수동 설정 가능)
export OMP_NUM_THREADS=8

# 4. 메모리 사용량 모니터링
htop  # Linux/macOS
taskmgr  # Windows
```

#### 예상 성능
| 하드웨어 | 첫 토큰 시간 | 생성 속도 | 메모리 사용량 |
|----------|-------------|----------|-------------|
| 4코어 16GB | 5-10초 | 2-5 토큰/초 | 12-14GB |
| 8코어 32GB | 3-5초 | 5-10 토큰/초 | 12-14GB |
| 16코어 64GB | 2-3초 | 10-15 토큰/초 | 12-14GB |

## 🔧 추천 설정

### 개발/테스트 환경
```env
# Ollama 사용 (간단함)
OLLAMA_BASE_URL=http://localhost:11434
```

### 프로덕션 환경
```env
# vLLM 사용 (고성능)
VLLM_BASE_URL=http://localhost:8000
```

## 📊 성능 비교

| 모델 | 메모리 요구량 | 추론 속도 | 한국어 성능 | 설치 난이도 |
|------|-------------|----------|------------|------------|
| Ollama llama2:7b | 4GB | 보통 | 보통 | 매우 쉬움 |
| Ollama solar:10.7b | 6GB | 보통 | 우수 | 매우 쉬움 |
| vLLM DialoGPT-medium | 2GB | 빠름 | 보통 | 보통 |
| vLLM DialoGPT-large | 4GB | 빠름 | 좋음 | 보통 |

## 🛠️ 문제 해결

### Ollama 연결 오류
```bash
# 서비스 상태 확인
ollama list

# 서비스 재시작
ollama serve
```

### vLLM 메모리 부족
```bash
# GPU 메모리 사용량 확인
nvidia-smi

# 메모리 사용량 줄이기
python -m vllm.entrypoints.api_server \
    --model microsoft/DialoGPT-medium \
    --gpu-memory-utilization 0.6
```

## 📝 테스트 방법

### 1. 연결 테스트
```bash
# Ollama 테스트
curl http://localhost:11434/api/generate \
    -d '{"model": "llama2", "prompt": "안녕하세요"}'

# vLLM 테스트  
curl http://localhost:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{"model": "default", "messages": [{"role": "user", "content": "안녕하세요"}]}'
```

### 2. ex-GPT에서 테스트
1. 오픈소스 LLM 서버 실행
2. ex-GPT 서버 시작: `python server.py`
3. 브라우저에서 `http://localhost:5001` 접속
4. 채팅 테스트

## 🎯 추천 워크플로우

1. **개발 단계**: Ollama + llama2:7b로 시작
2. **테스트 단계**: Ollama + solar:10.7b (한국어 성능 향상)
3. **배포 단계**: vLLM + 최적화된 모델

이제 완전히 오픈소스 LLM으로 ex-GPT를 운영할 수 있습니다! 🚀

## 🔥 H100 8-GPU 환경에서 vLLM 실행하기

### H100 8대 고성능 설정

#### 1단계: 환경 확인
```bash
# GPU 상태 확인
nvidia-smi

# CUDA 버전 확인
nvcc --version

# 사용 가능한 GPU 메모리 확인
nvidia-smi --query-gpu=memory.total,memory.free --format=csv
```

#### 2단계: vLLM 설치 (GPU 버전)
```bash
# CUDA 지원 vLLM 설치
pip install vllm

# 또는 최신 개발 버전
pip install git+https://github.com/vllm-project/vllm.git
```

#### 3단계: H100 최적화 설정
```bash
# H100 8대 병렬 처리로 Qwen2.5-7B 실행
python -m vllm.entrypoints.api_server \
    --model Qwen/Qwen2.5-7B-Instruct \
    --host 0.0.0.0 \
    --port 8000 \
    --tensor-parallel-size 8 \
    --gpu-memory-utilization 0.85 \
    --max-model-len 8192 \
    --max-num-seqs 256 \
    --trust-remote-code

# 더 큰 모델 실행 (Qwen2.5-14B)
python -m vllm.entrypoints.api_server \
    --model Qwen/Qwen2.5-14B-Instruct \
    --tensor-parallel-size 8 \
    --gpu-memory-utilization 0.9 \
    --max-model-len 4096 \
    --max-num-seqs 128
```

#### 4단계: 환경 변수 설정
`.env` 파일에서 H100 설정:
```env
# H100 8대 환경 설정
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
VLLM_TENSOR_PARALLEL_SIZE=8
VLLM_GPU_MEMORY_UTILIZATION=0.85
VLLM_MAX_MODEL_LEN=8192
VLLM_MAX_NUM_SEQS=256
```

### 🎯 H100 성능 최적화

#### 하드웨어 사양
- **GPU**: H100 80GB × 8대
- **총 GPU 메모리**: 640GB
- **NVLink**: 고속 GPU 간 통신
- **예상 처리량**: 1000+ 토큰/초

#### 모델별 권장 설정

| 모델 크기 | Tensor Parallel | GPU 메모리 사용률 | 최대 시퀀스 | 동시 요청 |
|-----------|----------------|------------------|-------------|----------|
| 7B | 4 | 0.7 | 8192 | 512 |
| 13B | 8 | 0.8 | 4096 | 256 |
| 34B | 8 | 0.9 | 2048 | 128 |
| 70B | 8 | 0.95 | 2048 | 64 |

#### 성능 모니터링
```bash
# GPU 사용률 실시간 모니터링
watch -n 1 nvidia-smi

# vLLM 메트릭 확인
curl http://localhost:8000/metrics

# 처리량 벤치마크
python -m vllm.entrypoints.api_server \
    --model Qwen/Qwen2.5-7B-Instruct \
    --tensor-parallel-size 8 \
    --benchmark
```

#### 문제 해결

**메모리 부족 오류**
```bash
# GPU 메모리 사용률 줄이기
--gpu-memory-utilization 0.7

# 시퀀스 길이 줄이기
--max-model-len 4096

# 동시 요청 수 줄이기
--max-num-seqs 128
```

**통신 오류**
```bash
# NVLink 상태 확인
nvidia-smi nvlink -s

# Ray 클러스터 재시작
ray stop
ray start --head
```
