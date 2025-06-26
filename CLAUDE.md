# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ex-GPT is an AI-powered business support system for Korea Expressway Corporation (한국도로공사). It's a FastAPI-based application with RAG (Retrieval Augmented Generation) capabilities, vector database integration, and LLM services.

## Development Commands

### Setup and Installation
```bash
# Install dependencies
poetry install

# Copy environment template and configure
cp .env.template .env
# Edit .env file with required values
```

### Running the Application
```bash
# Development server with hot reload
poetry run uvicorn src.main:app --reload

# Alternative development server
poetry run python -m src.main

# Production server
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Code Quality and Testing
```bash
# Run all tests with coverage
poetry run pytest

# Code formatting
poetry run black src/

# Import sorting
poetry run isort src/

# Type checking
poetry run mypy src/

# Linting
poetry run flake8 src/
```

### Single Test Execution
```bash
# Run specific test file
poetry run pytest tests/unit/test_specific.py

# Run specific test method
poetry run pytest tests/unit/test_specific.py::test_method_name

# Run tests with verbose output
poetry run pytest -v
```

## Architecture

### Core Components Structure
- **src/api/**: FastAPI router endpoints and request/response models
- **src/core/**: Business logic and domain services
- **src/rag/**: RAG pipeline implementation for document retrieval and processing
- **src/vector_db/**: Vector database abstraction layer (Qdrant, ChromaDB, FAISS)
- **src/llm/**: LLM integration and communication modules
- **src/utils/**: Shared utilities and helper functions
- **src/preprocessing/**: Document processing and data preparation
- **src/web/**: Web interface components (if applicable)

### Data Flow Architecture
The system follows a typical RAG architecture:
1. Document ingestion → preprocessing → vectorization → vector DB storage
2. User query → vector similarity search → context retrieval → LLM generation → response

### Configuration Management
- Environment-specific configs in `config/dev/`, `config/prod/`, `config/test/`
- Main environment variables defined in `.env.template`
- Korea Expressway Corporation specific integrations (KOEX API, WISNUT, legacy systems)

### Key Dependencies
- **FastAPI**: Web framework and API
- **LangChain**: LLM orchestration framework
- **Transformers/Sentence-Transformers**: NLP models
- **Vector DBs**: Qdrant (primary), ChromaDB, FAISS
- **Torch**: Deep learning framework
- **Whisper**: Audio processing (if speech features are implemented)

## Korean-Specific Considerations

This codebase contains Korean language content and is designed for Korea Expressway Corporation. When working with:
- Korean text processing and tokenization
- HWP file format support (Korean word processor)
- Integration with Korean government/corporate systems (KOEX, WISNUT)
- Korean language model configurations (Qwen2.5-7B-Instruct)

## Development Environment

### Docker-based RAG Server
This project uses Docker containers for the RAG server infrastructure:

**Docker Registry**: `registry.cloud.neoali.com`
**Repository**: `gitlab.cloud.neoali.com/datastreams/ex-gpt`

#### Setup Commands
```bash
# Login to NeoALI Docker Registry
docker login registry.cloud.neoali.com

# Pull all images
docker compose pull

# Configure environment
cp template.env .env
# Edit .env with your HuggingFace token
```

#### Running Services
```bash
# Full test run (recommended for first setup)
docker compose up --abort-on-container-exit test_runner; docker compose down

# Development (single machine)
docker compose up

# Production API server
docker compose -f docker-compose-api-server.yaml up

# Production model server (H100 GPU)
docker compose -f docker-compose-model-server.yaml up
```

### Model Configuration
- Primary LLM: Qwen/Qwen2.5-7B-Instruct (via vLLM server)
- Embedding Model: BAAI/bge-m3
- Vector DB: Qdrant (pre-indexed data pulled from registry)
- Collection name: "exgpt_documents"

#### Supported vLLM Versions
- `vllm/vllm-openai:v0.9.0.1` (CUDA 12.8) - recommended
- `vllm/vllm-openai:v0.8.5.post1` (CUDA 12.4)
- `vllm/vllm-openai:v0.7.3` (CUDA 12.1)

### File Upload Support
- Supported formats: PDF, HWP, DOCX, TXT, MD
- Max file size: 100MB
- Upload directory: `data/uploads/`

### Manual Testing
```bash
# Test individual services
docker compose run --rm test_runner python3 /scripts/tests/test_vllm_server.py --wait

# Other available tests in /scripts/tests/
```

### API Documentation
Once running, API docs available at:
- Swagger UI: http://hostname:port/docs
- ReDoc: http://hostname:port/redoc
- REST API spec available via Swagger interface

### Production Deployment Notes
- Set `CHAT_MODEL_ENDPOINT` and `EMBEDDING_MODEL_ENDPOINT` environment variables for distributed setup
- For offline environments, mount HuggingFace cache directory and set `TRANSFORMERS_OFFLINE="1"`
- Pre-indexed vector data is automatically pulled with the Qdrant image
- Supports H100 GPUs with CUDA 12.x compatibility

## Web UI Application

### Running the Web Interface
```bash
# Start web server for ex-GPT UI
python3 -m http.server 5000

# Access the web application
# http://localhost:5000
```

### Web UI Features
- **Korean-optimized chat interface** with ex-GPT branding
- **Deep Think mode** toggle for enhanced reasoning
- **Real-time RAG integration** with document sources
- **Responsive design** with sidebar navigation
- **Voice input support** (planned)
- **Markdown rendering** for rich text responses

### UI Components
- `index.html`: Main web application with embedded CSS/JS
- Korean language support with Noto Sans KR fonts
- Korea Expressway Corporation color scheme and branding
- Integration with RAG API endpoints at `http://localhost:8080/v1/chat/`

## Testing Strategy

The project uses pytest with:
- Unit tests in `tests/unit/`
- Integration tests in `tests/integration/`
- End-to-end tests in `tests/e2e/`
- Coverage reporting enabled by default
- Factory Boy for test data generation

### Web UI Testing
```bash
# Test web server
curl http://localhost:5000

# Test RAG API integration
curl -X POST http://localhost:8080/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"history": [{"role": "user", "content": "안녕하세요"}]}'
```