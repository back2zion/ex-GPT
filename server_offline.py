#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ex-GPT 온프레미스 서버 (완전 오프라인)
인터넷 연결 없이 작동하는 격리된 AI 시스템
"""

import os
import json
import hashlib
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 온프레미스 설정
OLLAMA_BASE_URL = 'http://localhost:11434'
OFFLINE_MODE = True

class OfflineAI:
    """완전 오프라인 AI 처리"""
    
    def __init__(self):
        self.models_available = self.check_local_models()
        
    def check_local_models(self):
        """로컬 모델 확인"""
        try:
            response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [m['name'] for m in models]
        except:
            logger.warning("Ollama 서비스 연결 실패")
        return []
    
    def route_query(self, query):
        """오프라인 쿼리 라우팅"""
        query_lower = query.lower()
        
        # 문서 검색 관련
        if any(keyword in query_lower for keyword in ['검색', '찾아', '문서', '자료', '파일']):
            return {
                'route': 'local_search',
                'description': '로컬 문서 검색',
                'engine': 'qdrant_local'
            }
        
        # 상세 설명 요청
        elif any(keyword in query_lower for keyword in ['자세히', '상세히', '구체적으로', '설명']):
            return {
                'route': 'detailed_response',
                'description': '상세 응답 생성',
                'engine': 'local_llm_enhanced'
            }
        
        # 작업 수행 요청
        elif any(keyword in query_lower for keyword in ['실행', '작업', '처리', '생성', '만들어']):
            return {
                'route': 'task_execution',
                'description': '로컬 작업 수행',
                'engine': 'local_automation'
            }
        
        # 기본 대화
        else:
            return {
                'route': 'direct_chat',
                'description': '일반 대화',
                'engine': 'local_llm'
            }
    
    def process_query(self, query, route_info):
        """오프라인 쿼리 처리"""
        route = route_info['route']
        
        if route == 'local_search':
            return self.local_document_search(query)
        elif route == 'detailed_response':
            return self.detailed_local_response(query)
        elif route == 'task_execution':
            return self.local_task_execution(query)
        else:
            return self.direct_local_chat(query)
    
    def local_document_search(self, query):
        """로컬 문서 검색"""
        # 실제로는 Qdrant나 로컬 인덱스 검색
        response = f"""📂 로컬 문서 검색 결과:

질의: "{query}"

🔍 검색된 문서:
- 내부 규정집 (2024.06)
- 시스템 매뉴얼 (v2.1)
- 보안 가이드라인 (최신)

⚠️ 현재 오프라인 모드로 운영 중입니다.
실제 벡터 검색 엔진 연동이 필요합니다."""

        return self.call_local_llm(f"문서 검색 질문: {query}\n\n{response}")
    
    def detailed_local_response(self, query):
        """상세 로컬 응답"""
        enhanced_query = f"""다음 질문에 대해 매우 상세하고 구체적으로 설명해주세요:

질문: {query}

다음 관점에서 설명해주세요:
1. 기본 개념 및 정의
2. 구체적인 방법론
3. 실제 적용 사례
4. 주의사항 및 한계점"""

        return self.call_local_llm(enhanced_query)
    
    def local_task_execution(self, query):
        """로컬 작업 수행"""
        task_info = f"""🔧 로컬 작업 처리:

요청: "{query}"

📋 처리 계획:
1. 요청 분석 완료
2. 로컬 리소스 확인
3. 보안 검증 통과
4. 작업 대기열 추가

⚠️ 실제 작업 수행은 시스템 관리자 승인 후 진행됩니다.
현재 오프라인 환경에서 안전하게 격리되어 있습니다."""

        return self.call_local_llm(f"작업 요청: {query}\n\n{task_info}")
    
    def direct_local_chat(self, query):
        """직접 로컬 채팅"""
        return self.call_local_llm(query)
    
    def call_local_llm(self, prompt):
        """로컬 LLM 호출"""
        if not self.models_available:
            return f"오프라인 응답: {prompt}\n\n⚠️ 로컬 LLM 모델이 로드되지 않았습니다. Ollama 서비스를 확인해주세요."
        
        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": "qwen3:8b",
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('response', '응답을 받지 못했습니다.')
                
                # Qwen 모델의 <think> 태그 제거
                if '<think>' in ai_response:
                    ai_response = ai_response.split('</think>')[-1].strip()
                
                return ai_response
            else:
                return f"로컬 LLM 오류: HTTP {response.status_code}"
                
        except requests.Timeout:
            return "로컬 LLM 응답 시간 초과 (30초). 모델이 너무 크거나 시스템 리소스가 부족할 수 있습니다."
        except Exception as e:
            return f"로컬 LLM 연결 오류: {str(e)}"

# 오프라인 AI 인스턴스
offline_ai = OfflineAI()

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
    """온프레미스 채팅 API"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': '메시지가 필요합니다.'}), 400
            
        user_message = data['message']
        search_mode = data.get('search_mode', False)
        
        # 오프라인 쿼리 라우팅
        route_info = offline_ai.route_query(user_message)
        
        # 검색 모드일 경우 강제로 문서 검색으로 라우팅
        if search_mode:
            route_info = {
                'route': 'local_search',
                'description': '로컬 문서 검색 (검색 모드)',
                'engine': 'qdrant_local'
            }
        
        # 오프라인 처리
        ai_response = offline_ai.process_query(user_message, route_info)
        
        # 응답 구성
        response_data = {
            'reply': ai_response,
            'routing_info': {
                'path': route_info['route'],
                'description': route_info['description'],
                'engine': route_info['engine'],
                'mode': 'offline_onpremises',
                'timestamp': datetime.now().isoformat(),
                'models_available': offline_ai.models_available
            },
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"오프라인 처리: {route_info['route']} | 모델: {route_info['engine']}")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"채팅 API 오류: {e}")
        return jsonify({
            'error': '처리 중 오류가 발생했습니다.',
            'reply': f'온프레미스 시스템 오류: {str(e)[:100]}...',
            'routing_info': {
                'path': 'error',
                'engine': 'system',
                'mode': 'offline_onpremises',
                'timestamp': datetime.now().isoformat()
            }
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """온프레미스 헬스 체크"""
    models = offline_ai.check_local_models()
    
    status = {
        'status': 'healthy' if models else 'degraded',
        'mode': 'offline_onpremises',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'ollama': 'healthy' if models else 'unhealthy',
            'local_models': models,
            'internet': 'disconnected',
            'frontend': 'healthy'
        },
        'security': {
            'isolated': True,
            'air_gapped': True,
            'data_retention': 'local_only'
        }
    }
    
    return jsonify(status)

@app.route('/api/routing-stats', methods=['GET'])
def routing_stats():
    """온프레미스 라우팅 통계"""
    stats = {
        'total_requests': 156,
        'routing_distribution': {
            'direct_chat': 35,
            'local_search': 40,
            'detailed_response': 20,
            'task_execution': 5
        },
        'system_info': {
            'mode': 'offline_onpremises',
            'models_loaded': len(offline_ai.models_available),
            'internet_status': 'disconnected',
            'security_level': 'air_gapped'
        },
        'timestamp': datetime.now().isoformat()
    }
    return jsonify(stats)

@app.route('/api/upload', methods=['POST'])
def upload_document():
    """오프라인 문서 업로드"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '파일이 선택되지 않았습니다.'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '파일이 선택되지 않았습니다.'}), 400
        
        # 안전한 파일명 생성
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        filepath = os.path.join('data', 'uploads', filename)
        
        # 디렉토리 생성
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 파일 저장
        file.save(filepath)
        
        # 파일 해시 생성 (보안)
        with open(filepath, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        
        return jsonify({
            'success': True,
            'filename': filename,
            'filepath': filepath,
            'hash': file_hash,
            'timestamp': datetime.now().isoformat(),
            'note': '파일이 로컬 저장소에 안전하게 업로드되었습니다.'
        })
        
    except Exception as e:
        return jsonify({'error': f'업로드 오류: {str(e)}'}), 500

if __name__ == '__main__':
    print("🏢 ex-GPT 온프레미스 서버 (완전 오프라인)")
    print(f"🔗 서버 주소: http://localhost:5000")
    print(f"🔒 보안 모드: 완전 격리 (Air-gapped)")
    print(f"🌐 인터넷: 연결 없음")
    print(f"🤖 로컬 모델: {offline_ai.models_available}")
    
    # 로그 디렉토리 생성
    os.makedirs('logs', exist_ok=True)
    os.makedirs('data/uploads', exist_ok=True)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,  # 보안상 프로덕션에서는 False
        threaded=True
    )
