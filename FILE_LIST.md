# ex-GPT 완전 오프라인 시스템 - 파일 목록

## 🎯 핵심 서버 파일
- `server_offline.py` - 완전 오프라인 전용 서버 (메인)
- `server_langgraph.py` - LangGraph 기반 엔터프라이즈 서버
- `server_simple.py` - 단순 Ollama 테스트 서버

## 🚀 실행 스크립트
- `quick_start.bat` - 🔥 **원클릭 시작** (권장)
- `start_offline.bat` - 오프라인 서버 시작
- `start_langgraph.bat` - LangGraph 서버 시작
- `start_simple.bat` - 단순 서버 시작

## 🔧 설치 및 점검 도구
- `check_offline_system.bat` - 시스템 상태 종합 점검
- `install_ollama.bat` - Ollama 자동 설치 (온라인)
- `prepare_offline_package.bat` - Air-Gapped 패키지 준비
- `test_llm_connection.py` - LLM 연결 테스트

## 📋 환경 설정 파일
- `.env.offline` - 완전 오프라인 환경 설정
- `.env.langgraph` - LangGraph 엔터프라이즈 설정
- `requirements.offline.txt` - 오프라인 최소 의존성
- `requirements.enterprise.txt` - 엔터프라이즈 의존성

## 📚 문서 및 가이드
- `README.md` - 메인 사용법 (오프라인 강조)
- `DEPLOYMENT.md` - 배포 및 운영 가이드
- `OFFLINE_INSTALL.md` - Air-Gapped 환경 설치법
- `LICENSE` - 라이선스 정보

## 🎨 프론트엔드 파일
- `index.html` - 메인 웹 인터페이스 (엔터프라이즈 UI)
- `css/style.css` - 접근성 개선 스타일
- `js/main.js` - 클라이언트 JavaScript
- `images/` - 로고, 아바타 이미지

## 📂 데이터 및 구성
- `data/uploads/` - 파일 업로드 디렉토리
- `logs/` - 시스템 로그 디렉토리
- `clinerules-bank/` - 업무별 설정 가이드
- `pyproject.toml` - Poetry 프로젝트 설정

## 🏗️ 아키텍처 구성요소
- `src/` - 핵심 Python 모듈
  - `api/chat.py` - Chat API
  - `rag/ragflow_integration.py` - RAG 통합
  - `llm/` - LLM 엔진 모듈
  - `utils/` - 유틸리티 함수

## 📊 모니터링 및 테스트
- `models/florence-2-large/` - 로컬 AI 모델
- `qdrant_storage/` - 벡터 DB 저장소
- `ragflow_config/` - RAGFlow 설정

---

## 🎯 사용 시나리오

### 1. 빠른 시작 (권장)
```cmd
quick_start.bat
```

### 2. 완전 오프라인 운영
```cmd
start_offline.bat
```

### 3. Air-Gapped 환경 배포
```cmd
# 온라인 시스템에서
prepare_offline_package.bat

# 오프라인 시스템에서
install_offline.bat
```

### 4. 시스템 점검 및 문제 해결
```cmd
check_offline_system.bat
```

---

## ✨ 핵심 특징 요약

- ✅ **완전 오프라인**: 인터넷 연결 불필요
- ✅ **Air-Gapped 지원**: 보안 격리 환경 최적화
- ✅ **원클릭 시작**: quick_start.bat로 즉시 실행
- ✅ **다중 서버**: 용도별 서버 선택 가능
- ✅ **종합 점검**: 시스템 상태 자동 진단
- ✅ **엔터프라이즈 UI**: 50+ 연령대 접근성 고려
- ✅ **LangGraph 아키텍처**: 스마트 AI 라우팅
- ✅ **보안 강화**: 개인정보 보호, 감사 로깅
