# scripts/windows-setup.ps1
# Windows 환경용 ex-GPT 권한 관리 시스템 설정 스크립트

param(
    [Parameter(Mandatory=$false)]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "=== ex-GPT Permission Management System - Windows 설정 ===" -ForegroundColor Green
    Write-Host ""
    Write-Host "사용법: .\scripts\windows-setup.ps1 -Command <명령어>" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "사용 가능한 명령어:" -ForegroundColor Cyan
    Write-Host "  init-dev     : 개발 환경 초기 설정" -ForegroundColor White
    Write-Host "  run          : 개발 서버 실행" -ForegroundColor White
    Write-Host "  run-prod     : 프로덕션 서버 실행" -ForegroundColor White
    Write-Host "  test         : 테스트 실행" -ForegroundColor White
    Write-Host "  stop         : 서버 중지" -ForegroundColor White
    Write-Host "  clean        : 정리" -ForegroundColor White
    Write-Host "  logs         : 로그 확인" -ForegroundColor White
    Write-Host "  status       : 서비스 상태 확인" -ForegroundColor White
    Write-Host "  backup       : 데이터베이스 백업" -ForegroundColor White
    Write-Host "  monitoring   : 모니터링 스택 실행" -ForegroundColor White
    Write-Host ""
    Write-Host "예시:" -ForegroundColor Yellow
    Write-Host "  .\scripts\windows-setup.ps1 -Command init-dev" -ForegroundColor Gray
    Write-Host "  .\scripts\windows-setup.ps1 -Command run" -ForegroundColor Gray
}

function Test-DockerInstalled {
    try {
        docker --version | Out-Null
        docker-compose --version | Out-Null
        return $true
    }
    catch {
        Write-Host "❌ Docker 또는 Docker Compose가 설치되지 않았습니다." -ForegroundColor Red
        Write-Host "   다음 링크에서 Docker Desktop을 설치해주세요:" -ForegroundColor Yellow
        Write-Host "   https://www.docker.com/products/docker-desktop/" -ForegroundColor Blue
        return $false
    }
}

function Initialize-Development {
    Write-Host "🚀 개발 환경 초기화 중..." -ForegroundColor Green
    
    # .env 파일 생성
    if (-not (Test-Path ".env")) {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ 환경 변수 파일 생성됨: .env" -ForegroundColor Green
        Write-Host "⚠️  .env 파일의 값들을 실제 환경에 맞게 수정해주세요." -ForegroundColor Yellow
    } else {
        Write-Host "ℹ️  .env 파일이 이미 존재합니다." -ForegroundColor Blue
    }
    
    # 필요한 디렉토리 생성
    $directories = @("uploads", "logs", "uploads/personal")
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Host "✅ 디렉토리 생성됨: $dir" -ForegroundColor Green
        }
    }
    
    Write-Host "🎉 개발 환경 초기화 완료!" -ForegroundColor Green
}

function Start-Development {
    Write-Host "🚀 개발 서버 시작 중..." -ForegroundColor Green
    
    # Docker 상태 확인
    if (-not (Test-DockerInstalled)) {
        return
    }
    
    # Docker Compose 실행
    try {
        docker-compose up --build -d
        Write-Host "✅ 서버가 시작되었습니다!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📍 서비스 URL:" -ForegroundColor Cyan
        Write-Host "   API 문서 (Swagger): http://localhost:8000/docs" -ForegroundColor White
        Write-Host "   API 문서 (ReDoc):   http://localhost:8000/redoc" -ForegroundColor White
        Write-Host "   헬스체크:           http://localhost:8000/api/v1/health" -ForegroundColor White
        Write-Host ""
        Write-Host "📋 로그 확인: .\scripts\windows-setup.ps1 -Command logs" -ForegroundColor Gray
        Write-Host "🛑 서버 중지: .\scripts\windows-setup.ps1 -Command stop" -ForegroundColor Gray
    }
    catch {
        Write-Host "❌ 서버 시작 실패: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Start-Production {
    Write-Host "🚀 프로덕션 서버 시작 중..." -ForegroundColor Green
    
    if (-not (Test-DockerInstalled)) {
        return
    }
    
    try {
        # 프로덕션 환경 확인
        $env:ENVIRONMENT = "production"
        docker-compose -f docker-compose.yml up --build -d
        Write-Host "✅ 프로덕션 서버가 시작되었습니다!" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ 프로덕션 서버 시작 실패: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Run-Tests {
    Write-Host "🧪 테스트 실행 중..." -ForegroundColor Green
    
    if (-not (Test-DockerInstalled)) {
        return
    }
    
    try {
        # 테스트 환경 실행
        docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
        docker-compose -f docker-compose.test.yml down
        Write-Host "✅ 테스트 완료!" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ 테스트 실행 실패: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Stop-Services {
    Write-Host "🛑 서비스 중지 중..." -ForegroundColor Yellow
    
    try {
        docker-compose down
        Write-Host "✅ 모든 서비스가 중지되었습니다." -ForegroundColor Green
    }
    catch {
        Write-Host "❌ 서비스 중지 실패: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Clean-Environment {
    Write-Host "🧹 환경 정리 중..." -ForegroundColor Yellow
    
    try {
        docker-compose down -v
        docker system prune -f
        Write-Host "✅ 환경 정리 완료!" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ 환경 정리 실패: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Show-Logs {
    Write-Host "📋 로그 확인 중..." -ForegroundColor Cyan
    
    try {
        docker-compose logs -f exgpt-auth-api
    }
    catch {
        Write-Host "❌ 로그 확인 실패: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Show-Status {
    Write-Host "📊 서비스 상태 확인 중..." -ForegroundColor Cyan
    
    try {
        Write-Host ""
        Write-Host "=== Docker 컨테이너 상태 ===" -ForegroundColor Yellow
        docker-compose ps
        
        Write-Host ""
        Write-Host "=== 서비스 헬스체크 ===" -ForegroundColor Yellow
        
        # API 헬스체크
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health" -TimeoutSec 5
            Write-Host "✅ API 서버: 정상" -ForegroundColor Green
            Write-Host "   - 상태: $($response.status)" -ForegroundColor White
            Write-Host "   - 데이터베이스: $($response.components.database)" -ForegroundColor White
            Write-Host "   - Redis: $($response.components.redis)" -ForegroundColor White
        }
        catch {
            Write-Host "❌ API 서버: 접근 불가" -ForegroundColor Red
        }
        
        Write-Host ""
    }
    catch {
        Write-Host "❌ 상태 확인 실패: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Backup-Database {
    Write-Host "💾 데이터베이스 백업 중..." -ForegroundColor Green
    
    try {
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        docker-compose exec -T postgres pg_dump -U exgpt_user exgpt_permissions > "backup_$timestamp.sql"
        Write-Host "✅ 백업 완료: backup_$timestamp.sql" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ 백업 실패: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Start-Monitoring {
    Write-Host "📊 모니터링 스택 시작 중..." -ForegroundColor Green
    
    try {
        # 모니터링 설정 파일 확인
        if (-not (Test-Path "monitoring/docker-compose.monitoring.yml")) {
            Write-Host "❌ 모니터링 설정 파일이 없습니다." -ForegroundColor Red
            return
        }
        
        docker-compose -f monitoring/docker-compose.monitoring.yml up -d
        Write-Host "✅ 모니터링 스택이 시작되었습니다!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📊 모니터링 URL:" -ForegroundColor Cyan
        Write-Host "   Grafana:    http://localhost:3000" -ForegroundColor White
        Write-Host "   Prometheus: http://localhost:9090" -ForegroundColor White
        Write-Host ""
        Write-Host "🔑 기본 로그인 정보:" -ForegroundColor Yellow
        Write-Host "   Grafana - admin/admin (첫 로그인 시 변경 필요)" -ForegroundColor Gray
    }
    catch {
        Write-Host "❌ 모니터링 스택 시작 실패: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# 메인 실행 로직
switch ($Command.ToLower()) {
    "help" { Show-Help }
    "init-dev" { Initialize-Development }
    "run" { Start-Development }
    "run-prod" { Start-Production }
    "test" { Run-Tests }
    "stop" { Stop-Services }
    "clean" { Clean-Environment }
    "logs" { Show-Logs }
    "status" { Show-Status }
    "backup" { Backup-Database }
    "monitoring" { Start-Monitoring }
    default {
        Write-Host "❌ 알 수 없는 명령어: $Command" -ForegroundColor Red
        Write-Host ""
        Show-Help
    }
}

# 스크립트 완료 메시지
if ($Command -ne "help") {
    Write-Host ""
    Write-Host "💡 도움말: .\scripts\windows-setup.ps1 -Command help" -ForegroundColor Gray
}