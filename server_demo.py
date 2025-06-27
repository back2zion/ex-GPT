#!/usr/bin/env python3
"""
ex-GPT Demo Server (Ollama 없이 동작하는 데모 버전)
Ollama 설치 전에 시스템을 테스트할 수 있는 간단한 서버
"""

from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import json
import os
import time
import random

app = Flask(__name__)
CORS(app)

# 데모용 미리 정의된 응답들
DEMO_RESPONSES = [
    "안녕하세요! 저는 ex-GPT 데모 서버입니다. 현재 Ollama 없이 동작하는 테스트 모드입니다.",
    "Ollama가 설치되면 실제 AI 모델과 대화할 수 있습니다. 지금은 데모 응답을 제공하고 있습니다.",
    "시스템이 정상적으로 작동하고 있습니다. Ollama를 설치하면 더 많은 기능을 사용할 수 있습니다.",
    "ex-GPT는 완전 오프라인 환경에서 동작하는 AI 어시스턴트입니다.",
    "현재 데모 모드에서 실행 중입니다. 실제 AI 기능을 사용하려면 Ollama를 설치해주세요.",
]

# 간단한 HTML 템플릿 (index.html이 없을 경우 대체)
DEMO_HTML = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ex-GPT 데모 서버</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .demo-notice {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 20px;
            text-align: center;
        }
        .chat-container {
            height: 400px;
            overflow-y: auto;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 20px;
            background: #f9f9f9;
        }
        .message {
            margin-bottom: 10px;
            padding: 10px;
            border-radius: 5px;
        }
        .user-message {
            background: #007bff;
            color: white;
            margin-left: 50px;
        }
        .bot-message {
            background: #e9ecef;
            color: #333;
            margin-right: 50px;
        }
        .input-container {
            display: flex;
            gap: 10px;
        }
        input[type="text"] {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        button {
            padding: 10px 20px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background: #0056b3;
        }
        .status {
            text-align: center;
            margin-top: 20px;
            padding: 10px;
            background: #d4edda;
            border-radius: 5px;
            color: #155724;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 ex-GPT 데모 서버</h1>
        
        <div class="demo-notice">
            <strong>⚠️ 데모 모드</strong><br>
            현재 Ollama 없이 동작하는 테스트 모드입니다.<br>
            실제 AI 기능을 사용하려면 Ollama를 설치해주세요.
        </div>
        
        <div class="chat-container" id="chatContainer">
            <div class="message bot-message">
                안녕하세요! ex-GPT 데모 서버입니다. 메시지를 입력해보세요.
            </div>
        </div>
        
        <div class="input-container">
            <input type="text" id="messageInput" placeholder="메시지를 입력하세요..." onkeypress="handleKeyPress(event)">
            <button onclick="sendMessage()">전송</button>
        </div>
        
        <div class="status">
            ✅ 서버 상태: 정상 동작 중 (데모 모드)
        </div>
    </div>

    <script>
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // 사용자 메시지 추가
            addMessage(message, 'user');
            input.value = '';
            
            // 서버에 요청 보내기
            fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            })
            .then(response => response.json())
            .then(data => {
                addMessage(data.response, 'bot');
            })
            .catch(error => {
                addMessage('죄송합니다. 오류가 발생했습니다.', 'bot');
            });
        }

        function addMessage(text, sender) {
            const container = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            messageDiv.textContent = text;
            container.appendChild(messageDiv);
            container.scrollTop = container.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """메인 페이지"""
    # index.html이 있으면 사용, 없으면 데모 HTML 사용
    if os.path.exists('index.html'):
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return DEMO_HTML

@app.route('/api/chat', methods=['POST'])
def chat():
    """채팅 API (데모 모드)"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        # 데모 응답 생성
        time.sleep(1)  # 실제 처리 시간 시뮬레이션
        response = random.choice(DEMO_RESPONSES)
        
        # 특정 키워드에 대한 맞춤 응답
        if '안녕' in user_message or 'hello' in user_message.lower():
            response = "안녕하세요! ex-GPT 데모 서버입니다. 현재 Ollama 없이 동작하는 테스트 모드입니다."
        elif 'ollama' in user_message.lower():
            response = "Ollama는 로컬 LLM을 실행하는 도구입니다. https://ollama.ai 에서 다운로드하여 설치하세요."
        elif '설치' in user_message:
            response = "Ollama 설치 방법: 1) https://ollama.ai 접속 2) Download 클릭 3) Windows 버전 다운로드 4) 설치 실행"
        elif '테스트' in user_message:
            response = "시스템이 정상적으로 작동하고 있습니다! 웹 인터페이스와 API가 모두 동작합니다."
        
        return jsonify({
            'response': response,
            'status': 'demo_mode',
            'timestamp': time.time()
        })
        
    except Exception as e:
        return jsonify({
            'response': f'죄송합니다. 오류가 발생했습니다: {str(e)}',
            'status': 'error',
            'timestamp': time.time()
        }), 500

@app.route('/health')
def health():
    """서버 상태 체크"""
    return jsonify({
        'status': 'healthy',
        'mode': 'demo',
        'message': 'ex-GPT Demo Server is running',
        'ollama_required': True,
        'timestamp': time.time()
    })

@app.route('/api/status')
def status():
    """시스템 상태 API"""
    return jsonify({
        'server': 'ex-GPT Demo',
        'mode': 'demo',
        'ollama_available': False,
        'python_version': '3.11+',
        'features': {
            'chat': True,
            'file_upload': False,
            'rag_search': False,
            'llm_integration': False
        },
        'next_steps': [
            'Install Ollama from https://ollama.ai',
            'Run: ollama pull qwen2.5:7b',
            'Start: python server_offline.py'
        ]
    })

if __name__ == '__main__':
    print("🚀 ex-GPT 데모 서버 시작 중...")
    print("📝 데모 모드: Ollama 없이 동작하는 테스트 서버")
    print("🌐 접속 주소: http://localhost:5000")
    print("⚠️  실제 AI 기능을 사용하려면 Ollama를 설치하세요.")
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=True)
