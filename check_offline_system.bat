@echo off
chcp 65001 >nul
echo ========================================
echo 🔒 ex-GPT 오프라인 시스템 상태 점검
echo ========================================
echo.

echo [1] Python 환경 점검...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되지 않았습니다.
    set /a errors+=1
) else (
    echo ✅ Python 사용 가능
)

echo.
echo [2] 필수 패키지 점검...
python -c "import flask, requests, yaml" 2>nul
if %errorlevel% neq 0 (
    echo ❌ 필수 패키지가 설치되지 않았습니다.
    echo    설치: pip install -r requirements.offline.txt
    set /a errors+=1
) else (
    echo ✅ Python 패키지 사용 가능
)

echo.
echo [3] Ollama 서비스 점검...
tasklist | findstr ollama >nul
if %errorlevel% equ 0 (
    echo ✅ Ollama 서버 실행 중
) else (
    echo ⚠️  Ollama 서버가 실행되지 않음
    set /a warnings+=1
)

echo.
echo [4] Ollama API 점검...
curl -s -m 5 http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Ollama API 응답 정상
) else (
    echo ❌ Ollama API 응답 없음 (서버 시작 필요)
    set /a errors+=1
)

echo.
echo [5] AI 모델 점검...
ollama list 2>nul | findstr qwen >nul
if %errorlevel% equ 0 (
    echo ✅ Qwen 모델 사용 가능
    ollama list | findstr qwen
) else (
    echo ⚠️  Qwen 모델을 찾을 수 없음
    echo    다운로드: ollama pull qwen2.5:7b
    set /a warnings+=1
)

echo.
echo [6] 디렉토리 구조 점검...
if exist "data\uploads" (
    echo ✅ 업로드 디렉토리 존재
) else (
    echo ⚠️  업로드 디렉토리 생성 필요
    mkdir data\uploads 2>nul
)

if exist "logs" (
    echo ✅ 로그 디렉토리 존재
) else (
    echo ⚠️  로그 디렉토리 생성 필요
    mkdir logs 2>nul
)

echo.
echo [7] 환경설정 점검...
if exist ".env.offline" (
    echo ✅ 오프라인 환경설정 파일 존재
) else (
    echo ⚠️  .env.offline 파일 없음 (기본값 사용)
    set /a warnings+=1
)

echo.
echo ========================================
echo 점검 결과 요약
echo ========================================
if %errors% gtr 0 (
    echo ❌ 오류 %errors%개 발견 - 시스템 사용 불가
    echo    OFFLINE_INSTALL.md 참조하여 문제 해결
) else if %warnings% gtr 0 (
    echo ⚠️  경고 %warnings%개 - 일부 기능 제한 가능
    echo    정상 작동하지만 최적화 권장
) else (
    echo ✅ 모든 점검 통과 - 시스템 사용 준비 완료
    echo    start_offline.bat 실행하여 서버 시작
)

echo.
pause
