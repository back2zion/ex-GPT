# ex-GPT 고도화 프로젝트

한국도로공사의 차세대 AI 기반 업무 지원 시스템

## 🚀 빠른 시작

### 1. Poetry 설치 (필요한 경우)
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 2. 의존성 설치
```bash
poetry install
```

### 3. 환경변수 설정
```bash
cp .env.template .env
# .env 파일을 편집하여 필요한 값들을 설정
```

### 4. 개발 서버 실행
```bash
poetry run python -m src.main
```

## 📁 프로젝트 구조

```
ex-GPT/
├── src/                    # 소스 코드
│   ├── api/               # API 엔드포인트
│   ├── core/              # 핵심 비즈니스 로직
│   ├── rag/               # RAG 파이프라인
│   ├── vector_db/         # 벡터 DB 인터페이스
│   ├── llm/               # LLM 통신 모듈
│   └── utils/             # 유틸리티 함수
├── data/                  # 데이터 저장소
├── models/                # 모델 파일
├── config/                # 설정 파일
├── tests/                 # 테스트 코드
└── docs/                  # 문서
```

## 🔧 개발 명령어

```bash
# 개발 서버 실행
poetry run uvicorn src.main:app --reload

# 테스트 실행
poetry run pytest

# 코드 포맷팅
poetry run black src/

# 타입 체킹
poetry run mypy src/
```

## 📊 API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 👥 팀

- **DataStreams**: 인프라, 데이터 파이프라인, API 개발
- **NeoAli**: AI 모델, RAG 엔진, 벡터 DB 관리
