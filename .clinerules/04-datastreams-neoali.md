# DataStreams-NeoAli 협업 규칙

## 역할 분담 (R&R)
### DataStreams 담당
- 데이터 전처리 및 정제
- 시스템 통합 및 배포
- 권한 관리 및 보안
- API 인터페이스 설계

### NeoAli 담당
- AI 모델 최적화
- 벡터DB 관리 (Qdrant)
- 멀티모달 처리
- LLM 파인튜닝

## 브랜치 전략
- main (운영)
- ├── develop (통합 개발)
- ├── feature/ds-* (DataStreams 기능)
- ├── feature/na-* (NeoAli 기능)
- └── hotfix/* (긴급 수정)