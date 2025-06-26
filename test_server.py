#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import time
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    """메인 페이지"""
    try:
        return send_from_directory('.', 'index.html')
    except Exception as e:
        return f"<h1>ex-GPT 테스트 서버</h1><p>index.html 파일을 찾을 수 없습니다: {str(e)}</p>", 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """테스트 채팅 엔드포인트"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        rag_engine = data.get('rag_engine', 'ragflow')
        
        logger.info(f"채팅 요청: {message[:50]}... (RAG: {rag_engine})")
        
        # 간단한 테스트 응답
        test_responses = {
            '안녕': '안녕하세요! ex-GPT 테스트 서버입니다. 🤖',
            '테스트': 'ex-GPT가 정상 작동 중입니다! ✅',
            '이름': '저는 ex-GPT 테스트 버전입니다.',
            'GPU': 'CPU 환경에서 실행 중입니다. GPU는 현재 사용하지 않습니다.',
            '상태': '서버 상태: 온라인 ✅\nRAG 엔진: ' + rag_engine
        }
        
        # 키워드 매칭
        response_text = None
        for keyword, reply in test_responses.items():
            if keyword in message:
                response_text = reply
                break
        
        if not response_text:
            response_text = f"""안녕하세요! ex-GPT 테스트 서버입니다. 🤖

**질문**: {message}

**현재 상태**:
- 서버: 정상 작동 ✅
- RAG 엔진: {rag_engine}
- 시간: {datetime.now().strftime('%H:%M:%S')}

테스트가 성공적으로 완료되었습니다!"""

        return jsonify({
            'reply': response_text,
            'routing_info': {
                'path': 'test_server',
                'engine': rag_engine,
                'reason': 'CPU 테스트 모드'
            },
            'processing_time': 0.1,
            'sources': []
        })
        
    except Exception as e:
        logger.error(f"채팅 오류: {e}")
        return jsonify({
            'error': str(e),
            'reply': '테스트 서버에서 오류가 발생했습니다.'
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    """헬스체크"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'message': 'ex-GPT 테스트 서버 정상 작동 중'
    })

# 정적 파일 서빙
@app.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory('images', filename)

@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory('css', filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('js', filename)

@app.route('/favicon.ico')
def serve_favicon():
    return send_from_directory('.', 'favicon.ico')

if __name__ == '__main__':
    logger.info("🚀 ex-GPT 테스트 서버 시작...")
    logger.info("📍 웹 서버: http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True, threaded=True)
