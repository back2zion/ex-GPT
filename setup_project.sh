# ex-GPT 프로젝트 올바른 설정 스크립트

echo "🔧 ex-GPT 프로젝트를 올바르게 설정합니다..."

# 1. 현재 잘못된 파일들 정리
rm -f pyproject.toml 2>/dev/null || true

# 2. 기본 디렉토리 구조 생성
echo "📁 디렉토리 구조 생성..."
mkdir -p src/api src/core src/utils src/rag src/vector_db src/llm
mkdir -p data/raw data/processed data/vectorized data/uploads
mkdir -p docs/api docs/architecture docs/deployment docs/user_guide
mkdir -p config/dev config/prod config/test
mkdir -p tests/unit tests/integration tests/e2e
mkdir -p models logs scripts frontend

# 3. .gitignore 파일 생성
echo "📄 .gitignore 생성..."
cat > .gitignore << 'GITIGNORE_EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Data & Models
*.pkl
*.h5
*.model
data/raw/*
!data/raw/.gitkeep
models/*.bin
models/*.safetensors

# Logs
logs/*.log
*.log

# Environment variables
.env
.env.local

# OS
.DS_Store
Thumbs.db

# ex-GPT specific
vector_db/
uploaded_files/
temp/
cache/
GITIGNORE_EOF

# 4. 환경변수 템플릿 생성
echo "⚙️ 환경변수 템플릿 생성..."
cat > .env.template << 'ENV_EOF'
# ex-GPT 프로젝트 환경변수 설정

# 서버 설정
SERVER_HOST=localhost
SERVER_PORT=8000
DEBUG=True

# 데이터베이스 설정
VECTOR_DB_HOST=localhost
VECTOR_DB_PORT=6333
QDRANT_COLLECTION_NAME=exgpt_documents

# LLM 설정
MODEL_NAME=qwen3-235b
MODEL_PATH=/models/qwen3
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7

# API 키 설정
OPENAI_API_KEY=your_openai_key_here
CLAUDE_API_KEY=your_claude_key_here

# 한국도로공사 특화 설정
KOEX_API_ENDPOINT=https://api.koex.re.kr
WISNUT_INTEGRATION=True
LEGACY_SYSTEM_URL=https://legacy.koex.re.kr

# 보안 설정
SECRET_KEY=your_secret_key_here
JWT_SECRET=your_jwt_secret_here
ALLOWED_HOSTS=localhost,127.0.0.1,koex.re.kr

# 파일 업로드 설정
MAX_FILE_SIZE=100MB
ALLOWED_FILE_TYPES=pdf,hwp,docx,txt,md

# 로깅 설정
LOG_LEVEL=INFO
LOG_FILE=logs/exgpt.log
ENV_EOF

# 5. pyproject.toml 올바르게 생성
echo "📦 pyproject.toml 생성..."
cat > pyproject.toml << 'TOML_EOF'
[tool.poetry]
name = "ex-gpt"
version = "1.0.0"
description = "한국도로공사 ex-GPT 고도화 프로젝트"
authors = ["DataStreams & NeoAli Team"]
readme = "README.md"
packages = [{include = "src"}]

[tool.poetry.dependencies]
python = "^3.10"
fastapi = "^0.104.1"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
pydantic = "^2.5.0"
sqlalchemy = "^2.0.23"
alembic = "^1.13.0"
redis = "^5.0.1"
celery = "^5.3.4"
transformers = "^4.36.0"
torch = "^2.1.0"
accelerate = "^0.25.0"
sentence-transformers = "^2.2.2"
langchain = "^0.0.340"
langchain-community = "^0.0.10"
qdrant-client = "^1.7.0"
chromadb = "^0.4.18"
faiss-cpu = "^1.7.4"
pypdf2 = "^3.0.1"
python-docx = "^1.1.0"
python-pptx = "^0.6.23"
openpyxl = "^3.1.2"
pandas = "^2.1.4"
numpy = "^1.26.2"
requests = "^2.31.0"
httpx = "^0.25.2"
aiofiles = "^23.2.0"
python-multipart = "^0.0.6"
openai-whisper = "^20231117"
librosa = "^0.10.1"
soundfile = "^0.12.1"
python-dotenv = "^1.0.0"
click = "^8.1.7"
rich = "^13.7.0"
tqdm = "^4.66.1"
pyyaml = "^6.0.1"
loguru = "^0.7.2"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.3"
pytest-asyncio = "^0.21.1"
pytest-cov = "^4.1.0"
black = "^23.11.0"
isort = "^5.13.0"
flake8 = "^6.1.0"
mypy = "^1.7.1"
pre-commit = "^3.6.0"

[tool.poetry.group.test.dependencies]
httpx = "^0.25.2"
pytest-mock = "^3.12.0"
factory-boy = "^3.3.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.black]
line-length = 88
target-version = ['py310']

[tool.isort]
profile = "black"
multi_line_output = 3

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = "-v --cov=src --cov-report=html --cov-report=term-missing"
TOML_EOF

# 6. 기본 Python 파일들 생성
echo "🐍 기본 Python 파일 생성..."

# __init__.py 파일들
touch src/__init__.py
touch src/api/__init__.py
touch src/core/__init__.py
touch src/utils/__init__.py
touch src/rag/__init__.py
touch src/vector_db/__init__.py
touch src/llm/__init__.py

# main.py 생성
cat > src/main.py << 'MAIN_EOF'
"""
ex-GPT 메인 애플리케이션
한국도로공사 AI 업무 지원 시스템
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# FastAPI 앱 생성
app = FastAPI(
    title="ex-GPT API",
    description="한국도로공사 AI 업무 지원 시스템",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """헬스체크 엔드포인트"""
    return {
        "message": "ex-GPT API Server",
        "status": "running",
        "version": "1.0.0",
        "description": "한국도로공사 AI 업무 지원 시스템"
    }

@app.get("/health")
async def health_check():
    """시스템 상태 확인"""
    return {
        "status": "healthy",
        "components": {
            "api": "ok",
            "database": "checking...",
            "vector_db": "checking...",
            "llm": "checking..."
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=os.getenv("SERVER_HOST", "0.0.0.0"),
        port=int(os.getenv("SERVER_PORT", 8000)),
        reload=True if os.getenv("DEBUG", "False").lower() == "true" else False
    )
MAIN_EOF

# 기본 API 파일 생성
cat > src/api/chat.py << 'CHAT_EOF'
"""채팅 관련 API 엔드포인트"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    sources: List[str]

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """채팅 API"""
    return ChatResponse(
        response=f"'{request.message}'에 대한 답변입니다.",
        conversation_id="conv_001",
        sources=["document1.pdf"]
    )
CHAT_EOF

# README.md 생성
cat > README.md << 'README_EOF'
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
README_EOF

# .gitkeep 파일들 생성
touch data/raw/.gitkeep
touch data/processed/.gitkeep
touch data/vectorized/.gitkeep
touch data/uploads/.gitkeep
touch logs/.gitkeep
touch models/.gitkeep

echo "✅ ex-GPT 프로젝트 설정이 완료되었습니다!"
echo ""
echo "📋 다음 단계:"
echo "1. Poetry 확인: poetry --version"
echo "2. 의존성 설치: poetry install"
echo "3. 환경변수 설정: cp .env.template .env"
echo "4. 개발 서버 실행: poetry run python -m src.main"
echo ""
echo "🔗 유용한 명령어:"
echo "- API 문서: http://localhost:8000/docs"
echo "- 헬스체크: http://localhost:8000/health"
echo ""
echo "🎯 7월 1일 목표를 향해 화이팅! 🚀"
