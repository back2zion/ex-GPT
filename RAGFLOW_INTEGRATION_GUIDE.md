# ex-GPT + RAGFlow 통합 가이드

한국도로공사 ex-GPT 시스템에 RAGFlow를 통합하여 고도화된 RAG(Retrieval-Augmented Generation) 기능을 제공합니다.

## 🎯 주요 기능

### RAGFlow 통합 기능
- **지능형 문서 처리**: PDF, DOCX, TXT 등 다양한 형식 지원
- **고급 임베딩**: 다국어 지원 및 의미론적 검색
- **실시간 RAG**: 문서 기반 질의응답
- **AI 어시스턴트**: 맞춤형 업무 지원 봇
- **시각적 관리**: 웹 기반 지식베이스 관리

### ex-GPT 고유 기능
- **한국어 최적화**: 한국도로공사 업무 특화
- **멀티모달 AI**: Florence-2 기반 이미지 분석
- **실시간 음성**: Whisper 기반 STT
- **통합 대시보드**: 모든 기능을 하나의 인터페이스에서

## 🚀 빠른 시작

### 1. 시스템 요구사항

**최소 요구사항:**
- CPU: 4코어 이상
- RAM: 16GB 이상
- 디스크: 50GB 이상 여유공간
- Docker & Docker Compose

**권장 요구사항:**
- CPU: 8코어 이상
- RAM: 32GB 이상
- GPU: NVIDIA RTX 시리즈 (선택사항)
- SSD: 100GB 이상

### 2. 설치 및 실행

#### Windows 사용자
```batch
# 1. 서비스 시작
start_services.bat

# 2. 서비스 중지
stop_services.bat
```

#### Linux/Mac 사용자
```bash
# 1. 스크립트 실행 권한 부여
chmod +x start_services.sh

# 2. 서비스 시작
./start_services.sh

# 3. 서비스 중지
docker-compose -f docker-compose-ragflow.yaml down
```

### 3. 수동 설정 (고급 사용자)

```bash
# 1. 의존성 설치
poetry install

# 2. RAGFlow Docker 서비스 시작
docker-compose -f docker-compose-ragflow.yaml up -d

# 3. 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 적절한 값 설정

# 4. ex-GPT 서버 시작
poetry run python server.py
```

## 🔧 설정 가이드

### 1. 환경 변수 설정

`.env` 파일에서 다음 설정들을 확인하세요:

```env
# RAGFlow 설정
RAGFLOW_HOST=http://localhost:8080
RAGFLOW_API_KEY=your_api_key_here
RAGFLOW_ENABLED=true

# 모델 설정
MODEL_CACHE_DIR=D:/huggingface_cache
FLORENCE_MODEL_PATH=microsoft/Florence-2-large

# 업로드 설정
UPLOAD_FOLDER=data/uploads
MAX_CONTENT_LENGTH=50000000
```

### 2. RAGFlow API 키 생성

1. RAGFlow 웹 인터페이스 접속: http://localhost:8080
2. 회원가입/로그인
3. 설정 → API 키 → 새 키 생성
4. 생성된 키를 `.env` 파일의 `RAGFLOW_API_KEY`에 설정

### 3. 모델 다운로드

```bash
# Florence-2 모델 다운로드
python download_florence.py

# 기타 모델들 다운로드
python simple_download.py
```

## 📚 사용 가이드

### 1. 기본 웹 인터페이스

**ex-GPT 메인 인터페이스**
- 주소: http://localhost:5001
- 기능: 통합 대시보드, 채팅, 파일 업로드

**RAGFlow 관리 인터페이스**
- 주소: http://localhost:8080
- 기능: 지식베이스 관리, 문서 파싱, 고급 설정

### 2. API 사용법

#### 지식베이스 생성
```bash
curl -X POST http://localhost:5001/api/ragflow/knowledge-base \
  -H "Content-Type: application/json" \
  -d '{
    "name": "한국도로공사_업무매뉴얼",
    "description": "업무 처리 관련 문서 모음"
  }'
```

#### 문서 업로드
```bash
curl -X POST http://localhost:5001/api/ragflow/upload \
  -F "file=@document.pdf" \
  -F "dataset_id=your_dataset_id"
```

#### RAG 질의응답
```bash
curl -X POST http://localhost:5001/api/ragflow/chat \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "your_assistant_id",
    "message": "고속도로 통행료 정책에 대해 설명해주세요"
  }'
```

### 3. Python 코드 예제

```python
from src.rag.ragflow_integration import ExGPTRAGFlowIntegration

# RAGFlow 연결
ragflow = ExGPTRAGFlowIntegration(
    ragflow_host="http://localhost:8080",
    api_key="your_api_key"
)

# 지식베이스 생성
kb_id = ragflow.create_knowledge_base(
    name="업무매뉴얼",
    description="한국도로공사 업무 매뉴얼"
)

# 문서 업로드
doc_id = ragflow.upload_document(kb_id, "manual.pdf")

# 문서 파싱
ragflow.parse_document(kb_id, [doc_id])

# AI 어시스턴트 생성
assistant_id = ragflow.create_chat_assistant(
    name="업무지원_AI",
    dataset_ids=[kb_id],
    system_prompt="한국도로공사 업무를 지원하는 AI입니다."
)

# 질의응답
response = ragflow.chat_with_assistant(
    assistant_id,
    "고속도로 요금 정책에 대해 알려주세요"
)
```

## 🔧 고급 설정

### 1. 커스텀 임베딩 모델

RAGFlow에서 한국어에 최적화된 임베딩 모델 사용:

```yaml
# docker-compose-ragflow.yaml
environment:
  - EMBEDDING_MODEL=jhgan/ko-sroberta-multitask
  - CHAT_MODEL=gpt-4
```

### 2. GPU 가속 설정

NVIDIA GPU 사용 시:

```yaml
# docker-compose-ragflow.yaml
services:
  ragflow:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### 3. 성능 최적화

```env
# .env
# 동시 처리 작업 수
WORKER_PROCESSES=4

# 메모리 사용량 제한
MEMORY_LIMIT=8G

# 캐시 설정
REDIS_CACHE_TTL=3600
```

## 📊 모니터링 및 로깅

### 1. 서비스 상태 확인

```bash
# RAGFlow 상태
curl http://localhost:5001/api/ragflow/status

# Docker 서비스 상태
docker-compose -f docker-compose-ragflow.yaml ps

# 시스템 리소스 사용량
docker stats
```

### 2. 로그 확인

```bash
# ex-GPT 로그
tail -f logs/ex-gpt.log

# RAGFlow 로그
docker-compose -f docker-compose-ragflow.yaml logs -f

# 특정 서비스 로그
docker logs ex-gpt-ragflow
```

### 3. 성능 메트릭

ex-GPT 대시보드에서 확인 가능:
- 총 요청 수
- 성공/실패 비율
- 활성 사용자 수
- 응답 시간
- RAGFlow 연결 상태

## 🔒 보안 설정

### 1. API 키 보안

```env
# 강력한 API 키 사용
RAGFLOW_API_KEY=ragflow_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# JWT 시크릿 키
JWT_SECRET_KEY=your_strong_jwt_secret_here

# 세션 보안
SECRET_KEY=your_session_secret_here
```

### 2. 네트워크 보안

```yaml
# docker-compose-ragflow.yaml
networks:
  ragflow-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### 3. 파일 업로드 제한

```env
# 파일 크기 제한 (50MB)
MAX_CONTENT_LENGTH=50000000

# 허용된 파일 형식
ALLOWED_EXTENSIONS=pdf,docx,txt,md,pptx,xlsx
```

## 🚨 문제 해결

### 1. 일반적인 문제들

**RAGFlow 연결 실패**
```bash
# Docker 서비스 확인
docker-compose -f docker-compose-ragflow.yaml ps

# 포트 충돌 확인
netstat -ano | findstr :8080

# 재시작
docker-compose -f docker-compose-ragflow.yaml restart
```

**메모리 부족**
```bash
# Docker 메모리 제한 확인
docker system df

# 불필요한 이미지 정리
docker system prune -a
```

**API 키 오류**
- RAGFlow 웹 인터페이스에서 새 API 키 생성
- `.env` 파일의 `RAGFLOW_API_KEY` 업데이트
- 서비스 재시작

### 2. 디버깅 모드

```bash
# 디버그 모드로 실행
FLASK_DEBUG=True python server.py

# 상세 로깅 활성화
LOG_LEVEL=DEBUG python server.py
```

### 3. 데이터 백업 및 복구

```bash
# 데이터 백업
docker-compose -f docker-compose-ragflow.yaml exec ragflow-mysql mysqldump -u ragflow -p ragflow > backup.sql

# 볼륨 백업
docker run --rm -v ragflow_data:/data -v $(pwd):/backup ubuntu tar czf /backup/ragflow_data.tar.gz /data

# 복구
docker run --rm -v ragflow_data:/data -v $(pwd):/backup ubuntu tar xzf /backup/ragflow_data.tar.gz -C /
```

## 📈 성능 최적화 팁

### 1. 하드웨어 최적화
- SSD 사용 권장
- 충분한 RAM (32GB+)
- GPU 가속 활용

### 2. 소프트웨어 최적화
- 정기적인 Docker 이미지 업데이트
- 불필요한 컨테이너 정리
- 적절한 워커 프로세스 수 설정

### 3. 문서 최적화
- 적절한 문서 크기 유지
- 정기적인 인덱스 최적화
- 중복 문서 제거

## 📞 지원 및 문의

### 기술 지원
- GitHub Issues: [프로젝트 저장소](https://github.com/your-repo)
- 이메일: support@your-domain.com

### 커뮤니티
- RAGFlow 공식 문서: https://ragflow.io/docs
- Discord: https://discord.gg/ragflow
- 한국어 커뮤니티: [링크]

---

**ex-GPT + RAGFlow 통합을 통해 더욱 강력한 AI 업무 지원 시스템을 경험해보세요!** 🚀
