# ex-GPT 배포 및 운영 가이드

## 📋 시스템 개요

ex-GPT는 완전 오프라인/온프레미스 환경에서 동작하는 엔터프라이즈급 AI 어시스턴트 플랫폼입니다.

### 핵심 특징
- ✅ **완전 오프라인**: 인터넷 연결 없이 동작
- ✅ **Air-Gapped 지원**: 격리된 보안 환경 최적화
- ✅ **LangGraph 아키텍처**: 스마트 라우팅 시스템
- ✅ **다중 AI 엔진**: RAG, LLM, Query Expansion, MCP
- ✅ **엔터프라이즈 보안**: 개인정보 보호, 감사 로깅
- ✅ **확장 가능**: GPU/CPU 환경 모두 지원

## 🚀 빠른 시작

### 1단계: 환경 준비
```cmd
# Python 3.8+ 설치 확인
python --version

# 기본 패키지 설치
pip install -r requirements.offline.txt
```

### 2단계: AI 엔진 설치
```cmd
# Ollama 설치 (Windows)
install_ollama.bat

# 또는 수동 설치
# https://ollama.ai/download 에서 다운로드
```

### 3단계: 시스템 시작
```cmd
# 빠른 시작 (권장)
quick_start.bat

# 또는 개별 시작
start_offline.bat
```

### 4단계: 웹 접속
브라우저에서 `http://localhost:5000` 접속

## 📁 서버 구성

### 서버 종류별 특징

| 서버 | 용도 | 특징 | 실행명령 |
|------|------|------|----------|
| **server_offline.py** | 완전 오프라인 운영 | 외부 API 없음, 로컬 처리만 | `start_offline.bat` |
| **server_langgraph.py** | 엔터프라이즈급 운영 | LangGraph 라우팅, 다중 엔진 | `start_langgraph.bat` |
| **server_simple.py** | 개발/테스트 | 단순 Ollama 연동 | `start_simple.bat` |

## 🔧 환경 설정

### 오프라인 환경 (.env.offline)
```env
# LLM 엔진
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b

# 서버 설정
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# 오프라인 모드
OFFLINE_MODE=true
DISABLE_EXTERNAL_APIS=true
```

### 엔터프라이즈 환경 (.env.langgraph)
```env
# 다중 LLM 엔진
OLLAMA_BASE_URL=http://localhost:11434
OPENAI_API_KEY=your-key-if-available

# RAG 엔진
RAGFLOW_API_URL=http://localhost:9380
QDRANT_URL=http://localhost:6333

# 라우팅 비율
DIRECT_LLM_PERCENTAGE=30
RAG_SEARCH_PERCENTAGE=50
```

## 🔒 Air-Gapped 배포

### 완전 오프라인 패키지 준비
```cmd
# 인터넷 연결된 시스템에서 실행
prepare_offline_package.bat
```

### Air-Gapped 시스템 설치
```cmd
# 1. 패키지 복사
# ex-gpt-offline-package/ 폴더를 USB로 복사

# 2. 오프라인 설치
install_offline.bat

# 3. 시스템 점검
check_offline_system.bat

# 4. 서버 시작
start_offline.bat
```

## 📊 성능 최적화

### 시스템 요구사항
| 구성 | 최소 | 권장 | 고성능 |
|------|------|------|--------|
| CPU | 4코어 | 8코어 | 16코어+ |
| RAM | 8GB | 16GB | 32GB+ |
| GPU | 없음 | GTX 1660 | RTX 4090/H100 |
| 스토리지 | 20GB | 100GB SSD | 500GB NVMe |

### GPU 가속 설정
```env
# NVIDIA GPU 사용시
CUDA_VISIBLE_DEVICES=0
OLLAMA_GPU_LAYERS=33

# CPU 전용 환경
OLLAMA_NUM_PARALLEL=1
OLLAMA_MAX_LOADED_MODELS=1
```

## 🛡️ 보안 설정

### 네트워크 보안
```cmd
# 방화벽 설정 (관리자 권한 필요)
netsh advfirewall firewall add rule name="ex-GPT" dir=in action=allow protocol=TCP localport=5000
netsh advfirewall firewall add rule name="Ollama" dir=in action=allow protocol=TCP localport=11434
```

### 파일 보안
- 업로드 제한: 16MB
- 허용 확장자: txt, pdf, docx, md
- 업로드 경로: `data/uploads/` (격리됨)

### 로깅 및 감사
- 모든 요청 로깅: `logs/offline.log`
- 개인정보 처리 기록: `logs/privacy.log`
- 시스템 오류: `logs/error.log`

## 🔧 문제 해결

### 일반적인 문제

**1. Ollama 연결 실패**
```cmd
# 해결방법
tasklist | findstr ollama
netstat -an | findstr 11434
ollama serve
```

**2. Python 패키지 오류**
```cmd
# 해결방법
pip install --force-reinstall -r requirements.offline.txt
```

**3. 메모리 부족**
```cmd
# 해결방법 (환경변수 설정)
set OLLAMA_MAX_LOADED_MODELS=1
set OLLAMA_NUM_PARALLEL=1
```

### 디버그 모드
```cmd
# 상세 로그 활성화
set DEBUG_MODE=true
python server_offline.py
```

## 📈 모니터링

### 시스템 상태 점검
```cmd
# 전체 시스템 점검
check_offline_system.bat

# 개별 구성요소 점검
curl http://localhost:11434/api/tags  # Ollama
curl http://localhost:5000/health     # ex-GPT
```

### 로그 모니터링
```cmd
# 실시간 로그 확인
tail -f logs/offline.log

# 오류 로그 확인
findstr "ERROR" logs/offline.log
```

## 🔄 업데이트 및 유지보수

### 정기 유지보수
1. **로그 파일 정리** (주간)
   ```cmd
   del logs\*.log.old
   ```

2. **업로드 파일 정리** (월간)
   ```cmd
   forfiles /p data\uploads /d -30 /c "cmd /c del @path"
   ```

3. **모델 업데이트** (필요시)
   ```cmd
   ollama pull qwen2.5:7b
   ```

### 백업 및 복구
```cmd
# 설정 백업
xcopy .env.* backup\ /Y
xcopy data\uploads backup\uploads\ /E /I

# 복구
xcopy backup\* . /Y
```

## 📞 지원 및 문의

### 문서 참조
- `README.md`: 기본 설치 및 사용법
- `OFFLINE_INSTALL.md`: Air-Gapped 환경 설치
- `clinerules-bank/`: 업무별 설정 가이드

### 로그 분석
시스템 문제 발생시 다음 로그 파일을 확인:
- `logs/offline.log`: 일반 시스템 로그
- `logs/error.log`: 오류 로그
- `logs/privacy.log`: 개인정보 처리 로그

### 성능 튜닝
하드웨어 사양에 따른 최적 설정은 `clinerules-bank/hardware/` 참조
