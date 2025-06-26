# ex-GPT CPU 테스트 가이드

GPU가 없는 환경에서 ex-GPT UI와 기본 기능을 테스트하는 방법입니다.

## 🚀 빠른 시작 (CPU 환경)

### Windows 사용자
```bash
# 1. 테스트 서버 실행
start_cpu_test.bat

# 2. 웹 브라우저에서 열기
http://localhost:5001
```

### Linux/Mac 사용자
```bash
# 1. 실행 권한 부여
chmod +x start_cpu_test.sh

# 2. 테스트 서버 실행
./start_cpu_test.sh

# 3. 웹 브라우저에서 열기
http://localhost:5001
```

## ✅ 테스트 가능한 기능

### 1. UI 확인사항
- ✅ 로고 표시 (사이드바)
- ✅ AI 아바타 이미지 (채팅창)
- ✅ RAG 엔진 선택 (RAGFlow/DSRAG)
- ✅ 채팅 인터페이스
- ✅ 반응형 디자인

### 2. 채팅 테스트
다음 키워드로 테스트 응답을 확인할 수 있습니다:

- `안녕` → 인사 응답
- `테스트` → 시스템 상태 확인
- `이름` → ex-GPT 소개
- `GPU` → CPU 환경 확인
- `상태` → 서버 상태 및 RAG 엔진 정보

### 3. RAG 엔진 선택 테스트
1. 채팅 헤더에서 **RAGFlow** 또는 **DSRAG** 선택
2. 메시지 전송 시 선택된 엔진 정보가 응답에 포함됨
3. 라우팅 상태 표시 확인

## 🔧 문제 해결

### 로고/이미지가 표시되지 않는 경우
```bash
# 이미지 파일 확인
ls -la images/
# 또는 Windows에서
dir images\
```

### 포트 충돌 시
```python
# test_server.py 수정
app.run(host='0.0.0.0', port=5002, debug=True)  # 포트 변경
```

### 패키지 설치 오류 시
```bash
# 가상환경 사용 (권장)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate     # Windows

pip install flask flask-cors requests
```

## 📁 파일 구조

```
ex-gpt-demo/
├── index.html              # 메인 UI
├── test_server.py          # CPU 테스트 서버
├── start_cpu_test.bat      # Windows 실행 스크립트
├── start_cpu_test.sh       # Linux/Mac 실행 스크립트
├── images/
│   ├── ex-logo.png         # 로고 이미지
│   └── favicon-16x16.png   # AI 아바타 이미지
└── README_CPU_TEST.md      # 이 파일
```

## 🎯 다음 단계

CPU 테스트가 완료되면:

1. **GPU 환경 설정**: `OPENSOURCE_LLM_SETUP.md` 참조
2. **RAGFlow 설정**: `RAGFLOW_INTEGRATION_GUIDE.md` 참조
3. **프로덕션 서버**: `server.py` 사용

## 💡 참고사항

- 이 테스트 서버는 GPU나 실제 LLM 없이 기본 UI와 통신을 테스트하는 용도입니다.
- 실제 AI 응답을 위해서는 vLLM, Ollama, 또는 RAGFlow 설정이 필요합니다.
- 파일 업로드/다운로드 기능은 프로덕션 서버에서만 사용 가능합니다.
