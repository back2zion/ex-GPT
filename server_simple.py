#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ex-GPT Simple Server (Ollama 임시 사용)
간단한 Flask 서버로 UI 테스트용
"""

import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv('.env.langgraph')

app = Flask(__name__)
CORS(app)

# 기본 설정
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')

@app.route('/')
def index():
    """메인 페이지"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    """정적 파일 서빙"""
    return send_from_directory('.', filename)

@app.route('/api/chat', methods=['POST'])
def chat():
    """채팅 API - 간단한 라우팅 시뮬레이션"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': '메시지가 필요합니다.'}), 400
            
        user_message = data['message']
        search_mode = data.get('search_mode', False)
        rag_engine = data.get('rag_engine', 'ragflow')
        
        # 간단한 라우팅 로직
        if any(keyword in user_message.lower() for keyword in ['검색', '찾아', '문서', '자료']):
            route = 'rag_search'
            engine = rag_engine
        elif any(keyword in user_message.lower() for keyword in ['자세히', '상세히', '구체적으로']):
            route = 'query_expansion'
            engine = 'expansion'
        elif any(keyword in user_message.lower() for keyword in ['실행', '작업', '처리', '예약']):
            route = 'mcp_action'
            engine = 'mcp'
        else:
            route = 'direct_llm'
            engine = 'ollama'
        
        # Ollama 호출 (임시)
        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": "qwen3:8b",
                    "prompt": f"[{route}] {user_message}",
                    "stream": False
                },
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('response', '응답을 받지 못했습니다.')
                
                # <think> 태그 제거 (Qwen 모델 특성)
                if '<think>' in ai_response:
                    ai_response = ai_response.split('</think>')[-1].strip()
                
            else:
                ai_response = f"[{route} 경로] 현재 임시로 Ollama를 사용하고 있습니다. 실제 LLM 연결이 필요합니다."
                
        except Exception as e:
            ai_response = f"[{route} 경로] LLM 연결 오류: {str(e)[:100]}... (임시 Ollama 사용 중)"
        
        # 응답 구성
        response_data = {
            'reply': ai_response,
            'routing_info': {
                'path': route,
                'engine': engine,
                'timestamp': datetime.now().isoformat(),
                'note': '임시 Ollama 사용 중 - 실제 LLM 연결 필요'
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'error': '처리 중 오류가 발생했습니다.',
            'reply': f'죄송합니다. 시스템 오류가 발생했습니다: {str(e)[:100]}...',
            'routing_info': {
                'path': 'error',
                'engine': 'system',
                'timestamp': datetime.now().isoformat()
            }
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """헬스 체크"""
    status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'mode': 'temporary_ollama',
        'services': {
            'ollama': 'unknown',
            'frontend': 'healthy'
        }
    }
    
    # Ollama 상태 확인
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
        status['services']['ollama'] = 'healthy' if response.status_code == 200 else 'unhealthy'
    except:
        status['services']['ollama'] = 'unhealthy'
    
    return jsonify(status)

@app.route('/api/routing-stats', methods=['GET'])
def routing_stats():
    """라우팅 통계 (시뮬레이션)"""
    stats = {
        'total_requests': 42,
        'routing_distribution': {
            'direct_llm': 30,
            'rag_search': 50,
            'query_expansion': 15,
            'mcp_action': 5
        },
        'engine_usage': {
            'ollama_temp': 100,
            'note': '임시 Ollama 사용 중'
        },
        'timestamp': datetime.now().isoformat()
    }
    return jsonify(stats)

if __name__ == '__main__':
    print("🚀 ex-GPT Simple Server (임시 Ollama 사용)")
    print(f"🔗 서버 주소: http://localhost:5000")
    print(f"🤖 임시 LLM: {OLLAMA_BASE_URL}")
    print("⚠️  주의: 현재 임시로 Ollama를 사용하고 있습니다.")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
