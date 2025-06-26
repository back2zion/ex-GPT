# ex-GPT + RAGFlow 통합 설정 가이드

## 🎯 개요

ex-GPT 프로젝트가 NeoAli RAG 대신 **완전한 오픈소스 RAGFlow**를 사용하도록 성공적으로 업데이트되었습니다.

## ✅ 완료된 작업

1. **NeoAli RAG 제거**: 모든 NeoAli RAG 관련 코드 제거 완료
2. **RAGFlow 통합**: 완전히 오픈소스 RAGFlow로 교체
3. **서버 업데이트**: `server.py`에서 RAGFlow API만 사용하도록 수정
4. **UI 클린업**: 조직별 정보 제거, 일반적인 ex-GPT로 변경

## 🚀 RAGFlow 시작 방법

### 1단계: LLM API 키 준비 (중요!)

RAGFlow가 작동하려면 LLM(대형 언어 모델) API 키가 필요합니다:

**OpenAI (권장)**:
```bash
# https://platform.openai.com/api-keys 에서 생성
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

**기타 지원 모델**:
- Anthropic Claude: https://console.anthropic.com/
- Google Gemini: https://makersuite.google.com/app/apikey
- Azure OpenAI: Azure 포털에서 설정

### 2단계: 환경 설정

`.env` 파일에 API 키 추가:
```bash
# 사용할 LLM의 API 키를 설정
OPENAI_API_KEY=your_actual_api_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here
```

### 3단계: RAGFlow 서비스 시작

```bash
# RAGFlow Docker 서비스 시작
cd c:\ex-GPT\ex-gpt-demo
docker-compose -f docker-compose-ragflow.yaml up -d
```

### 2단계: RAGFlow 웹 인터페이스 접속

1. 브라우저에서 http://localhost:8080 접속
2. 초기 설정 완료
3. 새 사용자 계정 생성

### 3단계: API 키 및 어시스턴트 생성

1. **API 키 생성**:
   - RAGFlow 웹 → 설정 → API 키 → 새 키 생성
   - 생성된 키를 `.env` 파일의 `RAGFLOW_API_KEY`에 입력

2. **채팅 어시스턴트 생성**:
   - RAGFlow 웹 → Chat → 새 어시스턴트 생성
   - 생성된 어시스턴트 ID를 `.env` 파일의 `RAGFLOW_ASSISTANT_ID`에 입력

### 4단계: 환경 설정 파일 수정

`.env` 파일에서 다음 값들을 설정:

```bash
# RAGFlow API 키 (3단계에서 생성한 키)
RAGFLOW_API_KEY=your_actual_api_key_here

# RAGFlow 어시스턴트 ID (3단계에서 생성한 ID)
RAGFLOW_ASSISTANT_ID=your_actual_assistant_id_here
```

### 5단계: ex-GPT 서버 시작

```bash
# ex-GPT 서버 시작
python server.py
```

## 🔍 연결 상태 확인

### 헬스체크 API
```bash
curl http://localhost:5001/api/health
```

### RAGFlow 상태 확인
```bash
curl http://localhost:5001/api/ragflow/status
```

## 📋 현재 시스템 상태

✅ **완료된 항목**:
- NeoAli RAG 완전 제거
- RAGFlow 통합 완료
- 서버 코드 업데이트
- UI 클린업 (조직별 정보 제거)
- 환경 설정 파일 준비
- Docker Compose 설정 완료

⏳ **설정 필요한 항목**:
- RAGFlow Docker 서비스 시작
- RAGFlow API 키 생성 및 설정
- RAGFlow 어시스턴트 생성 및 설정

## 🛠 문제 해결

### 1. RAGFlow 연결 실패
- Docker 서비스가 실행 중인지 확인: `docker ps`
- RAGFlow 웹 인터페이스 접속 확인: http://localhost:8080

### 2. API 키 문제
- RAGFlow 웹에서 API 키가 올바르게 생성되었는지 확인
- `.env` 파일의 `RAGFLOW_API_KEY` 값 확인

### 3. 어시스턴트 문제
- RAGFlow에서 어시스턴트가 생성되었는지 확인
- `.env` 파일의 `RAGFLOW_ASSISTANT_ID` 값 확인

## 🎉 결론

이제 ex-GPT는 **100% 오픈소스 RAGFlow**를 사용합니다:
- ❌ NeoAli RAG (제거됨)
- ✅ RAGFlow (오픈소스)
- ✅ MySQL, Redis, MinIO, Elasticsearch (모두 오픈소스)
- ✅ 완전히 자체 호스팅 가능

RAGFlow 서비스만 시작하고 API 키/어시스턴트 ID를 설정하면 모든 LLM 기능이 작동합니다!
