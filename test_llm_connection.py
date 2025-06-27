#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LLM 연결 테스트 스크립트
"""

import requests
import json

def test_ollama():
    """Ollama 연결 테스트"""
    try:
        # Ollama 상태 확인
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json()
            print("✅ Ollama 연결 성공!")
            print(f"📦 사용 가능한 모델: {[m['name'] for m in models.get('models', [])]}")
            return True
        else:
            print(f"❌ Ollama 상태 오류: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ollama 연결 실패: {e}")
        return False

def test_qwen_model():
    """Qwen 모델 테스트"""
    try:
        test_prompt = "안녕하세요? 간단히 인사해주세요."
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen3:8b",
                "prompt": test_prompt,
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('response', '응답 없음')
            print("✅ Qwen3:8b 모델 응답 성공!")
            print(f"🤖 응답: {answer[:100]}...")
            return True
        else:
            print(f"❌ 모델 응답 오류: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 모델 테스트 실패: {e}")
        return False

def test_langgraph_server():
    """LangGraph 서버 테스트"""
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ LangGraph 서버 실행 중!")
            return True
        else:
            print(f"❌ 서버 응답 오류: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        return False

if __name__ == "__main__":
    print("🔍 ex-GPT LLM 연결 상태 확인")
    print("=" * 40)
    
    # 1. Ollama 연결 테스트
    print("\n1️⃣ Ollama 서비스 확인...")
    ollama_ok = test_ollama()
    
    # 2. Qwen 모델 테스트
    if ollama_ok:
        print("\n2️⃣ Qwen3:8b 모델 테스트...")
        model_ok = test_qwen_model()
    else:
        print("\n2️⃣ Qwen3:8b 모델 테스트 스킵 (Ollama 연결 실패)")
        model_ok = False
    
    # 3. LangGraph 서버 테스트
    print("\n3️⃣ LangGraph 서버 확인...")
    server_ok = test_langgraph_server()
    
    # 결과 요약
    print("\n" + "=" * 40)
    print("📊 연결 상태 요약:")
    print(f"   Ollama: {'✅ 정상' if ollama_ok else '❌ 오류'}")
    print(f"   Qwen3:8b: {'✅ 정상' if model_ok else '❌ 오류'}")
    print(f"   LangGraph: {'✅ 정상' if server_ok else '❌ 오류'}")
    
    if all([ollama_ok, model_ok]):
        print("\n🎉 모든 LLM 연결이 정상입니다!")
        print("📱 웹 브라우저에서 http://localhost:5000 접속 가능")
    else:
        print("\n⚠️  일부 서비스에 문제가 있습니다.")
        if not ollama_ok:
            print("   - Ollama 서비스를 시작하세요: ollama serve")
        if not model_ok and ollama_ok:
            print("   - Qwen3:8b 모델을 다운로드하세요: ollama pull qwen3:8b")
        if not server_ok:
            print("   - LangGraph 서버를 시작하세요: python server_langgraph.py")
