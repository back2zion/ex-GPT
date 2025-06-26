#!/bin/bash

# RAGFlow + ex-GPT 통합 시작 스크립트

echo "🚀 ex-GPT + RAGFlow 통합 서비스 시작"
echo "=================================="

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 함수 정의
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. 환경 확인
print_status "환경 확인 중..."

# Docker 확인
if ! command -v docker &> /dev/null; then
    print_error "Docker가 설치되어 있지 않습니다."
    exit 1
fi

# Docker Compose 확인
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose가 설치되어 있지 않습니다."
    exit 1
fi

# Poetry 확인
if ! command -v poetry &> /dev/null; then
    print_warning "Poetry가 설치되어 있지 않습니다. pip를 사용합니다."
    USE_POETRY=false
else
    USE_POETRY=true
fi

print_success "환경 확인 완료"

# 2. 환경 변수 설정
print_status "환경 변수 설정 확인 중..."

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        print_warning ".env 파일이 없습니다. .env.example에서 복사합니다."
        cp .env.example .env
        print_warning ".env 파일을 편집하여 적절한 값을 설정해주세요."
    else
        print_error ".env.example 파일을 찾을 수 없습니다."
        exit 1
    fi
fi

# 3. Python 의존성 설치
print_status "Python 의존성 설치 중..."

if [ "$USE_POETRY" = true ]; then
    poetry install
    if [ $? -eq 0 ]; then
        print_success "Poetry로 의존성 설치 완료"
    else
        print_error "Poetry 의존성 설치 실패"
        exit 1
    fi
else
    pip install -r requirements.txt 2>/dev/null || pip install fastapi uvicorn requests python-dotenv
    if [ $? -eq 0 ]; then
        print_success "pip로 기본 의존성 설치 완료"
    else
        print_error "pip 의존성 설치 실패"
        exit 1
    fi
fi

# 4. 필요한 디렉토리 생성
print_status "디렉토리 구조 생성 중..."

mkdir -p data/uploads
mkdir -p logs
mkdir -p models

print_success "디렉토리 구조 생성 완료"

# 5. RAGFlow Docker 서비스 시작
print_status "RAGFlow Docker 서비스 시작 중..."

docker-compose -f docker-compose-ragflow.yaml up -d

if [ $? -eq 0 ]; then
    print_success "RAGFlow Docker 서비스 시작 완료"
else
    print_error "RAGFlow Docker 서비스 시작 실패"
    exit 1
fi

# 6. RAGFlow 서비스 준비 대기
print_status "RAGFlow 서비스 준비 대기 중..."

RAGFLOW_HOST="http://localhost:8080"
MAX_WAIT=120  # 2분 대기
WAIT_TIME=0

while [ $WAIT_TIME -lt $MAX_WAIT ]; do
    if curl -s "$RAGFLOW_HOST/health" > /dev/null 2>&1; then
        print_success "RAGFlow 서비스가 준비되었습니다"
        break
    fi
    
    sleep 5
    WAIT_TIME=$((WAIT_TIME + 5))
    echo -n "."
done

if [ $WAIT_TIME -ge $MAX_WAIT ]; then
    print_warning "RAGFlow 서비스 준비 대기 시간 초과. 수동으로 확인해주세요."
fi

# 7. ex-GPT 서버 시작
print_status "ex-GPT 서버 시작 중..."

if [ "$USE_POETRY" = true ]; then
    echo "Poetry 환경에서 서버를 시작합니다..."
    poetry run python server.py &
else
    echo "시스템 Python 환경에서 서버를 시작합니다..."
    python server.py &
fi

SERVER_PID=$!
print_success "ex-GPT 서버 시작 완료 (PID: $SERVER_PID)"

# 8. 완료 메시지
echo ""
echo "🎉 모든 서비스가 시작되었습니다!"
echo "=================================="
echo "📍 서비스 주소:"
echo "  - ex-GPT 웹 인터페이스: http://localhost:5001"
echo "  - RAGFlow 웹 인터페이스: http://localhost:8080"
echo "  - Elasticsearch: http://localhost:9200"
echo "  - MinIO 콘솔: http://localhost:9001"
echo ""
echo "📋 다음 단계:"
echo "  1. RAGFlow 웹 인터페이스에서 회원가입/로그인"
echo "  2. API 키 생성 및 .env 파일에 설정"
echo "  3. RAGFlow 통합 예제 실행: python ragflow_example.py"
echo ""
echo "🛑 서비스 중지: Ctrl+C 또는 ./stop_services.sh"
echo ""
echo "🔍 실시간 로그 확인:"
echo "  - RAGFlow: docker-compose -f docker-compose-ragflow.yaml logs -f"
echo "  - ex-GPT: tail -f logs/ex-gpt.log"

# 사용자 입력 대기
echo ""
read -p "Enter를 눌러서 종료하거나, Ctrl+C로 백그라운드 실행을 유지하세요..."

# 정리
print_status "서비스 정리 중..."
kill $SERVER_PID 2>/dev/null
docker-compose -f docker-compose-ragflow.yaml down

print_success "모든 서비스가 중지되었습니다"
