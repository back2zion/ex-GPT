@echo off
echo ========================================
echo ex-GPT Qwen2.5-14B 자동 실행
echo ========================================
echo.

echo 🚀 Qwen2.5-14B-Instruct 모델을 자동으로 다운로드하고 실행합니다.
echo 📦 첫 실행 시 약 29GB 모델 다운로드가 진행됩니다.
echo ⏱️ H100 환경에서 약 5-10분, CPU 환경에서 약 30-60분 소요됩니다.
echo.

echo [확인] GPU 사용 가능 여부 확인...
nvidia-smi >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ GPU 감지됨 - H100 고성능 모드로 실행
    echo.
    echo [시작] H100 8-GPU 병렬 처리로 Qwen2.5-14B 시작 중...
    call start_vllm_h100.bat
) else (
    echo ⚠️ GPU 미감지 - CPU 모드로 실행 (성능 저하 예상)
    echo.
    echo [시작] CPU 전용 모드로 Qwen2.5-14B 시작 중...
    call start_vllm_cpu.bat
)

echo.
echo 실행이 완료되었습니다.
pause
