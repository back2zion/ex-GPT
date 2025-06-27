#!/usr/bin/env python3
"""
ex-GPT 통합 서버 - 깔끔하고 간단한 버전
Ollama 있으면 사용하고, 없으면 데모 모드로 동작
"""

from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import requests
import json
import os
import time
import random

app = Flask(__name__)
CORS(app)

# Ollama 연결 확인
def check_ollama():
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        return response.status_code == 200
    except:
        return False

# 데모 응답
DEMO_RESPONSES = [
    "안녕하세요! ex-GPT입니다. 현재 데모 모드로 동작 중입니다.",
    "Ollama가 설치되면 실제 AI와 대화할 수 있습니다.",
    "지금은 테스트용 응답을 보여드리고 있어요.",
    "시스템이 정상 작동하고 있습니다!",
]

# 메인 HTML
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ex-GPT</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .header {
            background: #2c3e50;
            color: white;
            padding: 1rem;
            text-align: center;
        }
        .status {
            background: {{ status_color }};
            color: white;
            padding: 0.5rem;
            text-align: center;
            font-size: 0.9rem;
        }
        .chat-container {
            flex: 1;
            max-width: 800px;
            margin: 0 auto;
            padding: 1rem;
            display: flex;
            flex-direction: column;
        }
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 1rem;
            background: white;
            border-radius: 10px;
            margin-bottom: 1rem;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .message {
            margin-bottom: 1rem;
            padding: 1rem;
            border-radius: 10px;
            max-width: 80%;
        }
        .user { background: #3498db; color: white; margin-left: auto; }
        .bot { background: #ecf0f1; color: #2c3e50; }
        .input-area {
            display: flex;
            gap: 1rem;
            background: white;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        input {
            flex: 1;
            padding: 0.8rem;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 1rem;
        }
        button {
            padding: 0.8rem 1.5rem;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1rem;
        }
        button:hover { background: #2980b9; }
        .loading { opacity: 0.7; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 ex-GPT</h1>
    </div>
    
    <div class="status">
        {{ status_message }}
    </div>
    
    <div class="chat-container">
        <div class="messages" id="messages">
            <div class="message bot">
                안녕하세요! ex-GPT입니다. 무엇을 도와드릴까요?
            </div>
        </div>
        
        <div class="input-area">
            <input type="text" id="messageInput" placeholder="메시지를 입력하세요..." 
                   onkeypress="if(event.key==='Enter') sendMessage()">
            <button onclick="sendMessage()" id="sendBtn">전송</button>
        </div>
    </div>

    <script>
        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            if (!message) return;
            
            addMessage(message, 'user');
            input.value = '';
            
            const sendBtn = document.getElementById('sendBtn');
            sendBtn.disabled = true;
            sendBtn.textContent = '...';
            
            fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            })
            .then(response => response.json())
            .then(data => {
                addMessage(data.response, 'bot');
                sendBtn.disabled = false;
                sendBtn.textContent = '전송';
            })
            .catch(error => {
                addMessage('오류가 발생했습니다.', 'bot');
                sendBtn.disabled = false;
                sendBtn.textContent = '전송';
            });
        }
        
        function addMessage(text, type) {
            const messages = document.getElementById('messages');
            const div = document.createElement('div');
            div.className = `message ${type}`;
            div.textContent = text;
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    ollama_available = check_ollama()
    
    if ollama_available:
        status_message = "✅ Ollama 연결됨 - 실제 AI 모드"
        status_color = "#27ae60"
    else:
        status_message = "⚠️ Ollama 없음 - 데모 모드 (설치: winget install ollama)"
        status_color = "#e67e22"
    
    return render_template_string(HTML_TEMPLATE, 
                                  status_message=status_message,
                                  status_color=status_color)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '')
    
    if check_ollama():
        # 실제 Ollama 사용
        try:
            response = requests.post('http://localhost:11434/api/generate', 
                                   json={
                                       'model': 'qwen2.5:7b',
                                       'prompt': message,
                                       'stream': False
                                   }, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return jsonify({'response': result.get('response', '응답을 받을 수 없습니다.')})
            else:
                return jsonify({'response': '모델이 준비되지 않았습니다. ollama pull qwen2.5:7b'})
        except:
            return jsonify({'response': 'Ollama 연결 실패'})
    else:
        # 데모 모드
        time.sleep(1)  # 실제 처리 시뮬레이션
        demo_response = random.choice(DEMO_RESPONSES)
        
        # 특별 응답
        if '안녕' in message:
            demo_response = "안녕하세요! ex-GPT 데모 모드입니다."
        elif 'ollama' in message.lower():
            demo_response = "Ollama 설치: winget install ollama 또는 https://ollama.ai"
        
        return jsonify({'response': demo_response})

@app.route('/status')
def status():
    return jsonify({
        'ollama_available': check_ollama(),
        'mode': 'production' if check_ollama() else 'demo'
    })

if __name__ == '__main__':
    print("🚀 ex-GPT 서버 시작")
    if check_ollama():
        print("✅ Ollama 연결됨 - 실제 AI 모드")
    else:
        print("⚠️ Ollama 없음 - 데모 모드")
        print("   설치: winget install ollama")
    
    print("🌐 http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)