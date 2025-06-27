from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Query, BackgroundTasks, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse, StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import jwt
import json
import os
import io
from datetime import datetime, timedelta
from pathlib import Path

# ex-GPT 모듈 imports
from exgpt_auth.database import get_db, get_redis_client
from exgpt_auth.models import User, DocumentPermission
from exgpt_auth.permission_service import PermissionService
from exgpt_auth.permissions import SystemAccessLevel, PERMISSION_MESSAGES
from exgpt_auth.logging_utils import get_logger

app = FastAPI(
    title="ex-GPT Permission Management API",
    description="한국도로공사 ex-GPT 시스템 권한 관리 API",
    version="1.0.0"
)

# 정적 파일 서빙 (CSS, JS, 이미지)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/images", StaticFiles(directory="images"), name="images")

permission_service = PermissionService()
security = HTTPBearer()
logger = get_logger(__name__)

# 메인 페이지 서빙
@app.get("/", response_class=HTMLResponse)
async def serve_main_page():
    html_file = Path("index.html")
    if html_file.exists():
        return HTMLResponse(content=html_file.read_text(encoding='utf-8'))
    else:
        return HTMLResponse(content='''
        <!DOCTYPE html>
        <html><head><title>ex-GPT</title></head>
        <body>
        <h1>ex-GPT 시스템</h1>
        <p>index.html 파일이 없습니다.</p>
        </body></html>
        ''')

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "database": "healthy",
            "redis": "healthy", 
            "rag": "healthy"
        }
    }

# 채팅 API 엔드포인트
@app.post("/api/chat")
async def chat_endpoint(request: Request):
    try:
        body = await request.json()
        message = body.get("message", "")
        mode = body.get("mode", "standard")
        user_id = body.get("user_id", "anonymous")
        
        logger.info(f"Chat request: {user_id} - {mode} mode - {message[:50]}...")
        
        if not message:
            raise HTTPException(status_code=400, detail="메시지가 없습니다.")
        
        # 간단한 더미 응답 (실제로는 LLM 호출)
        response_content = f"안녕하세요! '{message}' 에 대한 답변입니다.\n\n"
        response_content += "현재 개발 중인 ex-GPT 시스템입니다. "
        response_content += "도로 관련 질문을 도와드리겠습니다."
        
        thinking_process = None
        if mode == "think":
            thinking_process = f"사용자의 질문 '{message}'을 분석하고 있습니다...\n"
            thinking_process += "관련 문서를 검색하고 권한을 확인합니다.\n"
            thinking_process += "최적의 답변을 구성합니다."
        
        # 더미 출처 정보
        sources = [
            {
                "title": "도로법 시행령",
                "content_preview": "도로의 구조와 시설에 관한 기준...",
                "relevance_score": 0.95
            }
        ]
        
        return {
            "reply": response_content,
            "thinking_process": thinking_process,
            "sources": sources,
            "documents_found": len(sources),
            "mode": mode,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"채팅 처리 오류: {str(e)}")

# 음성 업로드 API (UI에서 사용)
@app.post("/api/upload_voice")
async def upload_voice(audio: UploadFile = File(...), type: str = "transcribe", user_id: str = "anonymous"):
    try:
        # 파일 저장
        upload_dir = Path("uploads/voice")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{audio.filename}"
        
        with open(file_path, "wb") as f:
            content = await audio.read()
            f.write(content)
        
        # 더미 응답 (실제로는 음성 처리)
        if type == "transcribe":
            result = "이것은 테스트 음성 전사 결과입니다."
        elif type == "summarize":
            result = "**요약**: 주요 내용은 다음과 같습니다.\n- 첫 번째 포인트\n- 두 번째 포인트"
        else:
            result = "**분석 결과**: 긍정적 톤, 핵심 키워드: 도로, 건설, 관리"
        
        return {
            "transcription": result,
            "processed_content": result,
            "processing_time": "2.3초",
            "file_info": {
                "size": len(content),
                "duration": 45,
                "format": "mp3"
            }
        }
        
    except Exception as e:
        logger.error(f"Voice upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"음성 처리 오류: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)