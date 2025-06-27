# VSCode Shell Integration Unavailable 해결 방법

## 🔧 문제 상황
VSCode 터미널에서 "Shell Integration Unavailable" 메시지가 표시되는 경우

## 💡 해결 방법

### 방법 1: VSCode 설정에서 활성화
1. **VSCode 설정 열기**
   - `Ctrl + ,` (설정 단축키)
   - 또는 `File > Preferences > Settings`

2. **Shell Integration 검색**
   - 설정 검색창에 "shell integration" 입력

3. **옵션 활성화**
   - `Terminal > Integrated > Shell Integration: Enabled` 체크
   - `Terminal > Integrated > Shell Integration: Show Welcome` 체크 (선택사항)

### 방법 2: 명령 팔레트 사용
1. **명령 팔레트 열기**
   - `Ctrl + Shift + P`

2. **명령 실행**
   ```
   Terminal: Install Shell Integration
   ```

### 방법 3: 수동 설정 (Windows)
1. **PowerShell 프로필 확인**
   ```powershell
   echo $PROFILE
   ```

2. **프로필 파일 생성/편집**
   ```powershell
   notepad $PROFILE
   ```

3. **VSCode 통합 코드 추가**
   ```powershell
   # VSCode Shell Integration
   if ($env:TERM_PROGRAM -eq "vscode") {
       . "$(code --locate-shell-integration-path pwsh)"
   }
   ```

### 방법 4: 터미널 재시작
1. **현재 터미널 종료**
   - `Ctrl + Shift + `` (백틱)` 으로 터미널 열기
   - `exit` 명령어로 종료

2. **새 터미널 열기**
   - `Ctrl + Shift + `` (백틱)`

### 방법 5: VSCode 재시작
1. **VSCode 완전 종료**
   - `Ctrl + Shift + P` → `Developer: Reload Window`
   - 또는 VSCode 완전 종료 후 재시작

## 🔍 추가 확인사항

### Windows 환경
- **PowerShell 버전 확인**
  ```powershell
  $PSVersionTable.PSVersion
  ```
  - PowerShell 5.1 이상 권장

- **실행 정책 확인**
  ```powershell
  Get-ExecutionPolicy
  ```
  - `RemoteSigned` 또는 `Unrestricted` 필요시 설정

### 권한 문제 해결
```powershell
# 관리자 권한으로 PowerShell 실행 후
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## ⚙️ 한국도로공사 ex-GPT 프로젝트 전용 설정

### 프로젝트 전용 터미널 설정
1. **워크스페이스 설정 파일 생성**
   ```json
   // .vscode/settings.json
   {
     "terminal.integrated.shellIntegration.enabled": true,
     "terminal.integrated.defaultProfile.windows": "PowerShell",
     "terminal.integrated.profiles.windows": {
       "PowerShell": {
         "source": "PowerShell",
         "args": ["-NoProfile", "-ExecutionPolicy", "Bypass"]
       }
     }
   }
   ```

2. **Poetry 환경 자동 활성화**
   ```json
   // .vscode/settings.json 추가
   {
     "python.terminal.activateEnvironment": true,
     "python.defaultInterpreterPath": ".venv/Scripts/python.exe"
   }
   ```

## 🚀 검증 방법

### Shell Integration 작동 확인
1. **터미널에서 확인**
   ```bash
   # 명령어 실행 후 화살표 아이콘이 표시되는지 확인
   echo "Shell Integration Test"
   ```

2. **기능 테스트**
   - 명령어 실행 후 우클릭 → "Copy Command" 옵션 확인
   - 터미널 히스토리 네비게이션 확인

## 🔧 문제 지속시 대안

### 대안 1: 외부 터미널 사용
```json
// .vscode/settings.json
{
  "terminal.external.windowsExec": "C:\\Windows\\System32\\cmd.exe"
}
```

### 대안 2: Git Bash 사용
```json
// .vscode/settings.json
{
  "terminal.integrated.defaultProfile.windows": "Git Bash",
  "terminal.integrated.profiles.windows": {
    "Git Bash": {
      "path": "C:\\Program Files\\Git\\bin\\bash.exe"
    }
  }
}
```

## 📞 추가 지원

### 한국도로공사 내부 지원
- **IT 헬프데스크**: 내선 XXXX
- **DataStreams 기술팀**: 내선 XXXX

### 온라인 리소스
- [VSCode 공식 문서](https://code.visualstudio.com/docs/terminal/shell-integration)
- [PowerShell 설정 가이드](https://docs.microsoft.com/powershell)

---
**작성일**: 2025-06-27  
**작성자**: DataStreams 기술지원팀  
**프로젝트**: ex-GPT 한국도로공사 AI 어시스턴트
