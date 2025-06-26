# Poetry Dependency Management Guidelines

## Overview
Configuration guidelines for managing Python dependencies using Poetry in the ex-GPT project, ensuring reproducible builds, secure dependency management, and optimized development workflows.

## Project Configuration

### pyproject.toml Structure
```toml
[tool.poetry]
name = "ex-gpt-system"
version = "1.0.0"
description = "Advanced AI system for Korea Expressway Corporation"
authors = ["DataStreams Team <team@datastreams.co.kr>"]
readme = "README.md"
packages = [{include = "ex_gpt"}]

[tool.poetry.dependencies]
python = "^3.10"
flask = "^2.3.0"
torch = "^2.0.0"
transformers = "^4.30.0"
qdrant-client = "^1.3.0"
openai-whisper = "^20230314"
vllm = "^0.2.0"
redis = "^4.6.0"
celery = "^5.3.0"
psycopg2-binary = "^2.9.0"
sqlalchemy = "^2.0.0"
pydantic = "^2.0.0"
fastapi = {version = "^0.100.0", optional = true}
uvicorn = {version = "^0.23.0", optional = true}

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
black = "^23.7.0"
flake8 = "^6.0.0"
mypy = "^1.5.0"
pre-commit = "^3.3.0"

[tool.poetry.group.gpu.dependencies]
torch = {version = "^2.0.0+cu118", source = "pytorch"}
torchvision = {version = "^0.15.0+cu118", source = "pytorch"}

[tool.poetry.extras]
api = ["fastapi", "uvicorn"]
gpu = ["torch", "torchvision"]

[[tool.poetry.source]]
name = "pytorch"
url = "https://download.pytorch.org/whl/cu118"
priority = "explicit"
```

### Dependency Categories

#### Core Dependencies
- **Flask/FastAPI**: Web framework for API and web interface
- **PyTorch**: Deep learning framework for model inference
- **Transformers**: Hugging Face library for LLM integration
- **Qdrant-client**: Vector database client for RAG operations
- **SQLAlchemy**: Database ORM for relational data management
- **Pydantic**: Data validation and serialization
- **Redis**: Caching and session management
- **Celery**: Background task processing

#### AI/ML Specific
- **vLLM**: Optimized LLM inference engine
- **Whisper**: Speech-to-text processing
- **Sentence-transformers**: Text embedding generation
- **FAISS**: Alternative vector search library
- **NumPy/Pandas**: Data processing and manipulation
- **Scikit-learn**: Traditional ML algorithms and utilities

#### Development Tools
- **Pytest**: Testing framework with async support
- **Black**: Code formatting
- **Flake8**: Linting and style checking
- **MyPy**: Static type checking
- **Pre-commit**: Git hooks for code quality
- **Coverage**: Test coverage analysis

## Environment Management

### Virtual Environment Setup
```bash
# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Configure Poetry to create virtual environments in project directory
poetry config virtualenvs.in-project true

# Initialize new project
poetry new ex-gpt-system
cd ex-gpt-system

# Install dependencies
poetry install

# Install with GPU support
poetry install --extras gpu

# Activate virtual environment
poetry shell
```

### Environment Configurations
- **Development**: Full dependency set with debugging tools
- **Testing**: Core dependencies plus testing frameworks
- **Production**: Minimal dependencies for deployment
- **GPU**: Additional CUDA-specific packages for inference

## Dependency Resolution Strategies

### Version Pinning
- Pin exact versions for critical dependencies (PyTorch, Transformers)
- Use semantic versioning for stable libraries
- Regular dependency updates with testing validation
- Security vulnerability scanning and updates

### Conflict Resolution
- Use Poetry's dependency resolver for conflict detection
- Maintain compatibility matrices for AI/ML libraries
- Test dependency combinations in CI/CD pipeline
- Document known incompatibilities and workarounds

### Custom Package Sources
- PyTorch with CUDA support from official PyTorch index
- Private package repositories for internal libraries
- Mirror repositories for security and reliability
- Fallback sources for package availability

## Development Workflow

### Local Development
```bash
# Install project in development mode
poetry install --with dev

# Add new dependency
poetry add flask-cors

# Add development dependency
poetry add --group dev pytest-cov

# Update dependencies
poetry update

# Export requirements for non-Poetry environments
poetry export -f requirements.txt --output requirements.txt
```

### Dependency Auditing
- Regular security vulnerability scanning
- License compliance checking
- Dependency freshness monitoring
- Impact analysis for major version updates

### Lock File Management
- Commit poetry.lock for reproducible builds
- Regular lock file updates with testing
- Environment-specific lock files if needed
- Automated lock file validation in CI/CD

## Production Deployment

### Container Integration
```dockerfile
FROM python:3.10-slim

# Install Poetry
RUN pip install poetry

# Configure Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --only=main && rm -rf $POETRY_CACHE_DIR

# Copy application code
COPY . .

# Run application
CMD ["poetry", "run", "python", "-m", "ex_gpt.main"]
```

### Performance Optimization
- Minimal dependency sets for production images
- Multi-stage builds for smaller container sizes
- Dependency caching for faster builds
- Layer optimization for container efficiency

## Security Considerations

### Vulnerability Management
- Automated dependency vulnerability scanning
- Regular security updates and patching
- Dependency source verification
- Private package registry usage for sensitive components

### Access Control
- Secure credential management for package repositories
- Team-based access control for dependency management
- Audit logging for dependency changes
- Approval workflows for critical dependency updates
