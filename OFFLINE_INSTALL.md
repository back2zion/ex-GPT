# ex-GPT 완전 오프라인 설치 가이드

## 🔒 Air-Gapped 환경 완전 오프라인 설치

> **중요**: 이 가이드는 인터넷 연결이 전혀 없는 완전 격리된 환경에서의 설치를 다룹니다.

### 1단계: 오프라인 패키지 준비 (인터넷 연결된 다른 시스템에서)

#### Python 패키지 다운로드
```bash
# 인터넷 연결된 시스템에서 실행
pip download -r requirements.offline.txt -d offline_packages/
```

#### Ollama 오프라인 설치 파일 준비
1. https://ollama.ai/download 에서 Windows 버전 다운로드
2. 모델 파일 준비:
   - `ollama pull qwen2.5:7b` (약 4.1GB)
   - 모델 파일 위치: `~/.ollama/models/`

### 2단계: Air-Gapped 시스템으로 파일 전송

필요한 파일들을 USB/외장디스크로 복사:
```
ex-gpt-offline-package/
├── ex-gpt-demo/                 # 전체 프로젝트
├── offline_packages/            # Python 패키지들
├── ollama-windows-amd64.exe     # Ollama 설치 파일
└── ollama-models/               # 미리 다운로드된 모델
    └── qwen2.5:7b/
```

### 3단계: 오프라인 시스템에서 설치

#### Python 의존성 설치
```cmd
cd ex-gpt-demo
pip install --no-index --find-links ../offline_packages -r requirements.offline.txt
```

#### Ollama 설치
```cmd
# Ollama 설치
..\ollama-windows-amd64.exe

# 모델 파일 복사 (사용자 홈 디렉토리로)
xcopy ..\ollama-models %USERPROFILE%\.ollama\models\ /E /I
```

### 4단계: 시스템 실행

```cmd
# Ollama 서버 시작
start ollama serve

# ex-GPT 오프라인 서버 시작
start_offline.bat
```

### 5단계: 접속 확인

- 웹 브라우저에서 `http://localhost:5000` 접속
- Ollama API: `http://localhost:11434`

## 🔧 오프라인 환경 최적화

### 메모리 사용량 최적화
- Qwen2.5:7B 모델: 최소 8GB RAM 권장
- GPU 사용시: VRAM 8GB+ 권장
- CPU 전용: 16GB+ RAM 권장

### 스토리지 요구사항
- 프로젝트 파일: ~500MB
- Ollama + 모델: ~5GB
- 로그/업로드 공간: 1GB+

### 보안 설정
- 네트워크 방화벽: 5000, 11434 포트만 허용
- 파일 업로드 제한: 16MB
- 로그 레벨: INFO (디버그 정보 최소화)

## 🚨 문제 해결

### Ollama 연결 실패
```cmd
# Ollama 프로세스 확인
tasklist | findstr ollama

# 포트 사용 확인
netstat -an | findstr 11434
```

### Python 패키지 오류
```cmd
# 오프라인 패키지 재설치
pip install --force-reinstall --no-index --find-links offline_packages flask
```

### 메모리 부족
```cmd
# CPU 전용 모드로 실행
set OLLAMA_NUM_PARALLEL=1
set OLLAMA_MAX_LOADED_MODELS=1
```
