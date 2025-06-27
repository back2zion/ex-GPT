# ex-GPT 핵심 개발 규칙

## 프로젝트 개요
- 한국도로공사 전용 AI 어시스턴트 시스템
- RAG + LLM + STT 멀티모달 통합 플랫폼
- 7월 1일 오픈 목표, DataStreams-NeoAli 협업

## 필수 준수사항
### 문서화
- 모든 AI 모델 변경 시 /docs/adr/ 에 ADR 작성
- API 변경 시 swagger/openapi 문서 업데이트
- 한국어 주석 필수 (공공기관 특성상)

### 코드 스타일
- Poetry 환경에서만 개발 (pip 사용 금지)
- Flask 앱 모듈화: 라우트, 서비스, 모델 분리
- AI 모델 래퍼 클래스 패턴 적용
- 비동기 처리 필수 (ThreadPoolExecutor 활용)

### 에러 핸들링
- 모든 AI 추론 작업에 타임아웃 설정
- GPU 메모리 부족 상황 대응 코드 필수
- 한국어 에러 메시지 (사용자 대상)