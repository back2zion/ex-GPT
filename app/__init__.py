"""
ex-GPT Flask 애플리케이션 초기화
한국도로공사 전용 AI 어시스턴트 시스템

Author: DataStreams-NeoAli 협업팀
Date: 2025-06-27
"""

from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv

def create_app(config_name='development'):
    """Flask 애플리케이션 팩토리 패턴
    
    Args:
        config_name (str): 환경 설정명 (development, staging, production)
    
    Returns:
        Flask: 설정된 Flask 애플리케이션 인스턴스
    """
    # 환경변수 로드
    load_dotenv()
    
    # Flask 앱 생성
    app = Flask(__name__)
    
    # CORS 설정 (한국도로공사 내부 네트워크 허용)
    CORS(app, origins=['http://localhost:*', 'http://127.0.0.1:*'])
    
    # 기본 설정
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'ex-gpt-korea-expressway-2025')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 파일 업로드 제한
    
    # 한국도로공사 특화 설정
    app.config['KOREAN_EXPRESSWAY_MODE'] = True
    app.config['WIZENUT_INTEGRATION'] = os.getenv('WIZENUT_INTEGRATION', 'true').lower() == 'true'
    
    # AI 모델 설정
    app.config['LLM_MODEL'] = os.getenv('LLM_MODEL', 'qwen3-235b-a22b')
    app.config['EMBEDDING_MODEL'] = os.getenv('EMBEDDING_MODEL', 'paraphrase-multilingual-MiniLM-L12-v2')
    app.config['STT_MODEL'] = os.getenv('STT_MODEL', 'whisper-large-v3')
    
    # H100 GPU 설정
    app.config['GPU_COUNT'] = int(os.getenv('GPU_COUNT', '8'))
    app.config['GPU_MEMORY_THRESHOLD'] = float(os.getenv('GPU_MEMORY_THRESHOLD', '0.8'))
    
    # 블루프린트 등록
    from app.routes.api import api_bp
    from app.routes.auth import auth_bp
    from app.routes.chat import chat_bp
    from app.routes.document import document_bp
    
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.register_blueprint(document_bp, url_prefix='/document')
    
    # 에러 핸들러 등록
    @app.errorhandler(404)
    def not_found_error(error):
        return {"error": "요청하신 페이지를 찾을 수 없습니다.", "code": 404}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "서버 내부 오류가 발생했습니다.", "code": 500}, 500
    
    # 헬스체크 엔드포인트
    @app.route('/health')
    def health_check():
        return {
            "status": "healthy",
            "service": "ex-GPT 한국도로공사 AI 어시스턴트",
            "version": "1.0.0",
            "timestamp": "2025-06-27"
        }
    
    return app
