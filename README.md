# ex-GPT 한국도로공사 AI 어시스턴트

> **한국도로공사 전용 RAG + LLM + STT 멀티모달 통합 플랫폼**  
> DataStreams-NeoAli 협업 프로젝트 | 2025년 7월 1일 오픈 목표

## 🚀 프로젝트 개요

ex-GPT는 한국도로공사를 위한 전문 AI 어시스턴트 시스템입니다. 법령규정 검색, 국정감사 자료 관리, 회의록 자동 생성, 위험성 평가 등 도로공사 업무에 특화된 기능을 제공합니다.

### 🎯 주요 특징

- **🏢 한국도로공사 특화**: 메뉴별 차별화 인사말, 와이즈넛 시스템 연동
- **🤖 멀티모달 AI**: LLM + RAG + STT 통합 처리
- **🔒 보안 강화**: 개인정보 자동 검출, 감사 로그, 공공기관 보안 준수
- **⚡ H100 GPU 최적화**: 8장 클러스터 효율적 활용
- **📊 실시간 모니터링**: GPU 상태, 메모리 사용량, 성능 추적

## 🏗️ 시스템 아키텍처

```
ex-gpt-demo/                   # 한국도로공사 AI 어시스턴트
├── 🚀 start.bat              # 통합 실행 스크립트
├── 📖 README.md              # 프로젝트 소개
├── ⚙️ pyproject.toml         # Poetry 의존성 관리
├── 📁 app/                   # Flask 애플리케이션
│   ├── __init__.py           # 앱 팩토리
│   ├── main_server.py        # 메인 서버
│   ├── offline_server.py     # 오프라인 서버
│   ├── enterprise_server.py  # 엔터프라이즈 서버
│   ├── routes/               # API 라우트
│   ├── services/             # 비즈니스 로직
│   ├── models/               # 데이터 모델
│   └── utils/                # 유틸리티
├── 📁 ai/                    # AI 모델 관리
│   ├── model_manager.py      # 통합 모델 관리자
│   ├── llm/                  # LLM 모델 (Qwen3, Llama3)
│   ├── embedding/            # 임베딩 모델
│   ├── stt/                  # 음성 인식 (Whisper)
│   └── vector/               # 벡터 DB (Qdrant)
├── 📁 korean_expressway/     # 한국도로공사 특화
│   ├── auth/                 # 와이즈넛 연동
│   ├── greetings/            # 메뉴별 인사말
│   ├── documents/            # HWP 문서 처리
│   └── meetings/             # 회의록 생성
├── 📁 security/              # 보안 시스템
│   ├── personal_data_detector.py  # 개인정보 검출
│   ├── audit_logger.py       # 감사 로그
│   └── government_compliance.py   # 공공기관 준수
├── 📁 config/                # 환경 설정
│   └── environments/         # 환경별 설정
├── 📁 docs/                  # 문서화
│   ├── adr/                  # 아키텍처 결정 기록
│   ├── api/                  # API 문서
│   └── korean/               # 한국어 문서
├── 📁 scripts/               # 실행 스크립트
├── 📁 frontend/              # 웹 인터페이스
├── 📁 data/                  # 데이터 저장소
└── 📁 logs/                  # 로그 (한국어 메시지)
```

## 🛠️ 기술 스택

### AI/ML 모델
- **LLM**: Qwen3-235B-A22B (Primary), Llama3-70B (Fallback)
- **Embedding**: paraphrase-multilingual-MiniLM-L12-v2
- **STT**: OpenAI Whisper Large-v3
- **Vector DB**: Qdrant

### 인프라
- **GPU**: H100 8장 클러스터
- **Framework**: Flask + Poetry
- **보안**: 개인정보 검출, 감사 로그
- **모니터링**: GPU 메모리, 온도, 사용률

## 🚀 빠른 시작

### 1. 환경 설정
```bash
# Poetry 환경 설정 (pip 사용 금지)
poetry install

# 환경변수 설정
copy config\environments\.env.offline .env
```

### 2. 서버 실행
```bash
# 메인 서버 (통합 기능)
start.bat

# 오프라인 서버
scripts\start_offline.bat

# 엔터프라이즈 서버
scripts\start_langgraph.bat
```

### 3. 웹 인터페이스 접속
```
http://localhost:5000
```

## 📋 주요 기능

### 🏢 한국도로공사 특화 기능
- **법령규정 검색**: "한국도로공사, 법령규정 정보를 도와드리겠습니다."
- **국정감사 자료**: "한국도로공사, 국정감사 정보를 도와드리겠습니다."
- **위험성 평가**: 공정별 위험성 평가 표준 검색
- **회의록 생성**: STT 기반 자동 회의록 작성
- **문서 비교**: HWP, PDF 문서 비교 분석

### 🤖 AI 기능
- **멀티모달 처리**: 텍스트, 음성, 문서 통합 처리
- **RAG 검색**: 벡터 기반 정확한 정보 검색
- **개인화**: 사용자별, 부서별 맞춤 서비스

### 🔒 보안 기능
- **개인정보 검출**: 주민번호, 전화번호, 이메일 자동 마스킹
- **감사 로그**: 모든 대화 내역 기록
- **월별 보고서**: 개인정보 검출 통계 및 권장사항

## 🔧 개발 가이드

### 코드 스타일
- **언어**: Python (Flask), JavaScript (Frontend)
- **의존성**: Poetry 환경에서만 개발 (pip 금지)
- **주석**: 한국어 주석 필수 (공공기관 특성)
- **패턴**: AI 모델 래퍼 클래스, Flask Blueprint

### 에러 핸들링
- **타임아웃**: 모든 AI 추론 작업 30초 제한
- **GPU 메모리**: 부족 상황 자동 대응
- **한국어 메시지**: 사용자 대상 에러 메시지

## 📊 모니터링

### GPU 상태 확인
```bash
# AI 모델 상태 점검
python -c "from ai.model_manager import model_manager; print(model_manager.health_check())"
```

### 보안 로그 확인
```bash
# 개인정보 검출 로그
type logs\personal_data_detections.log

# 월별 보고서 생성
python -c "from security.personal_data_detector import personal_data_detector; print(personal_data_detector.get_monthly_report(2025, 6))"
```

## 👥 팀 구성

### DataStreams (시스템 통합)
- 데이터 전처리 및 정제
- 시스템 통합 및 배포
- 권한 관리 및 보안
- API 인터페이스 설계

### NeoAli (AI 모델)
- AI 모델 최적화
- 벡터DB 관리 (Qdrant)
- 멀티모달 처리
- LLM 파인튜닝

## 📅 개발 일정

- **1주차**: 핵심 구조 정리 (Flask 모듈화, 서버 통합) ✅
- **2주차**: 한국도로공사 특화 기능 구현
- **3주차**: 보안 시스템 및 문서화 완료
- **4주차**: 테스트 및 최종 점검
- **🎯 7월 1일**: 정식 오픈

## 📞 지원

### 문제 신고
- **내부**: 사내 헬프데스크
- **기술**: DataStreams-NeoAli 기술팀

### 문서
- **설치 가이드**: `docs/korean/설치가이드.md`
- **사용법**: `docs/korean/사용법.md`
- **API 문서**: `docs/api/swagger.yaml`

---

**© 2025 한국도로공사 x DataStreams x NeoAli**  
*안전하고 효율적인 도로 건설을 위한 AI 혁신*
