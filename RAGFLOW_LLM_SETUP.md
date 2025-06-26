# RAGFlow LLM API 키 설정 가이드

RAGFlow에서 LLM(대형 언어 모델)을 사용하기 위해서는 API 키 설정이 필요합니다.

## 🔧 설정 방법

### 방법 1: Docker 시작 전 설정 (권장)

1. **환경 변수로 설정**
   `.env` 파일에 다음 추가:
   ```bash
   # OpenAI API 키 (GPT 모델 사용 시)
   OPENAI_API_KEY=your_openai_api_key_here
   
   # Anthropic API 키 (Claude 모델 사용 시) 
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   
   # Google API 키 (Gemini 모델 사용 시)
   GOOGLE_API_KEY=your_google_api_key_here
   
   # 기타 모델 API 키
   AZURE_OPENAI_API_KEY=your_azure_api_key_here
   ```

2. **Docker Compose 업데이트**
   `docker-compose-ragflow.yaml`의 ragflow 서비스에 환경 변수 추가

### 방법 2: RAGFlow 웹 인터페이스에서 설정

1. **RAGFlow 접속**
   ```
   http://localhost:8080
   ```

2. **모델 제공업체 설정**
   - 우상단 프로필 → "Model providers" 클릭
   - 원하는 모델 카드 찾기
   - "Add the model" 클릭
   - API 키 입력
   - Base URL 설정 (프록시 사용 시)
   - "OK" 클릭하여 저장

## 🚀 지원되는 LLM 제공업체

### 주요 제공업체
- **OpenAI**: GPT-3.5, GPT-4, GPT-4o
- **Anthropic**: Claude 3, Claude 3.5
- **Google**: Gemini Pro, Gemini Ultra
- **Azure OpenAI**: GPT 모델들
- **로컬 모델**: Ollama, Xinference, LocalAI

### API 키 획득 방법

1. **OpenAI**
   - https://platform.openai.com/api-keys
   - 계정 생성 후 API 키 생성

2. **Anthropic**
   - https://console.anthropic.com/
   - 계정 생성 후 API 키 생성

3. **Google AI**
   - https://makersuite.google.com/app/apikey
   - Google 계정으로 로그인 후 키 생성

## ⚠️ 주의사항

- 새 계정은 보통 무료 크레딧 제공 (몇 개월 후 만료)
- API 키는 안전하게 보관하고 공개하지 마세요
- 사용량 모니터링을 위해 제공업체 대시보드 확인

## 🔄 설정 업데이트

설정 변경 후:
1. RAGFlow 컨테이너 재시작: `docker-compose restart ragflow`
2. 웹 인터페이스에서 "Model providers" 페이지 확인
3. 추가된 모델이 "Added models" 섹션에 표시되는지 확인
