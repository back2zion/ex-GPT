"""
ex-GPT 메인 애플리케이션
한국도로공사 AI 업무 지원 시스템
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# FastAPI 앱 생성
app = FastAPI(
    title="ex-GPT API",
    description="한국도로공사 AI 업무 지원 시스템",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """헬스체크 엔드포인트"""
    return {
        "message": "ex-GPT API Server",
        "status": "running",
        "version": "1.0.0",
        "description": "한국도로공사 AI 업무 지원 시스템"
    }

@app.get("/health")
async def health_check():
    """시스템 상태 확인"""
    return {
        "status": "healthy",
        "components": {
            "api": "ok",
            "database": "checking...",
            "vector_db": "checking...",
            "llm": "checking..."
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=os.getenv("SERVER_HOST", "0.0.0.0"),
        port=int(os.getenv("SERVER_PORT", 8000)),
        reload=True if os.getenv("DEBUG", "False").lower() == "true" else False
    )
