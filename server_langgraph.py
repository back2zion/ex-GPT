#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ex-GPT Enterprise Edition - LangGraph Based Architecture
엔터프라이즈급 AI 어시스턴트 플랫폼

LangGraph 기반 아키텍처:
- 사용자 질의 → LangGraph 라우터 → direct_llm/rag_search/query_expansion/mcp_action
- 멀티 엔진 지원 (Ollama, RAGFlow, DSRAG)
- 엔터프라이즈 보안 & 모니터링
"""

import os
import json
import uuid
import time
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Literal
from dataclasses import dataclass
from enum import Enum

# Web Framework
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# LangGraph & LangChain
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI

# Ollama import
try:
    from langchain_ollama import OllamaLLM as Ollama
except ImportError:
    from langchain_community.llms import Ollama

# Utilities
import requests
from loguru import logger
from dotenv import load_dotenv

# Load environment
load_dotenv('.env.enterprise')

# Configuration
class Config:
    """엔터프라이즈 설정"""
    # Server
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # LLM Engines
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    # RAG Engines
    RAGFLOW_API_URL = os.getenv('RAGFLOW_API_URL', 'http://localhost:9380')
    RAGFLOW_API_KEY = os.getenv('RAGFLOW_API_KEY', '')
    QDRANT_URL = os.getenv('QDRANT_URL', 'http://localhost:6333')
    
    # Enterprise Features
    JWT_SECRET = os.getenv('JWT_SECRET', 'ex-gpt-enterprise-secret')
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    ENABLE_MONITORING = os.getenv('ENABLE_MONITORING', 'True').lower() == 'true'

# Data Models
@dataclass
class ChatState:
    """LangGraph 상태 관리"""
    messages: List[dict]
    user_query: str
    route_decision: Optional[str] = None
    llm_response: Optional[str] = None
    rag_results: Optional[List[dict]] = None
    expanded_query: Optional[str] = None
    mcp_result: Optional[dict] = None
    routing_info: Optional[dict] = None
    
class RouteType(Enum):
    """라우팅 타입"""
    DIRECT_LLM = "direct_llm"        # 30%
    RAG_SEARCH = "rag_search"        # 50%
    QUERY_EXPANSION = "query_expansion"  # 15%
    MCP_ACTION = "mcp_action"        # 5%

# LangGraph Router
class ExGPTRouter:
    """ex-GPT LangGraph 라우터"""
    
    def __init__(self):
        self.ollama_llm = None
        self.openai_llm = None
        self._init_llms()
        
    def _init_llms(self):
        """LLM 초기화"""
        try:
            # Ollama 초기화
            self.ollama_llm = Ollama(
                base_url=Config.OLLAMA_BASE_URL,
                model="qwen3:8b"
            )
            logger.info("Ollama LLM 초기화 완료")
        except Exception as e:
            logger.warning(f"Ollama LLM 초기화 실패: {e}")
            
        try:
            # OpenAI 초기화 (백업)
            if Config.OPENAI_API_KEY:
                self.openai_llm = ChatOpenAI(
                    api_key=Config.OPENAI_API_KEY,
                    model="gpt-3.5-turbo"
                )
                logger.info("OpenAI LLM 초기화 완료")
        except Exception as e:
            logger.warning(f"OpenAI LLM 초기화 실패: {e}")
    
    def classify_query(self, state: ChatState) -> ChatState:
        """질의 분류 (LangGraph 노드)"""
        query = state.user_query.lower()
        
        # 간단한 규칙 기반 분류 (향후 ML 모델로 교체 가능)
        if any(keyword in query for keyword in ['검색', '찾아', '문서', '자료']):
            state.route_decision = RouteType.RAG_SEARCH.value
        elif any(keyword in query for keyword in ['자세히', '상세히', '구체적으로']):
            state.route_decision = RouteType.QUERY_EXPANSION.value
        elif any(keyword in query for keyword in ['실행', '작업', '처리']):
            state.route_decision = RouteType.MCP_ACTION.value
        else:
            state.route_decision = RouteType.DIRECT_LLM.value
            
        state.routing_info = {
            "path": state.route_decision,
            "timestamp": datetime.now().isoformat(),
            "query_length": len(state.user_query)
        }
        
        logger.info(f"Query classified as: {state.route_decision}")
        return state
    
    def direct_llm_response(self, state: ChatState) -> ChatState:
        """Direct LLM 응답 (30%)"""
        try:
            # Ollama 우선 시도
            if self.ollama_llm:
                response = self.ollama_llm.invoke(state.user_query)
                state.llm_response = response
                state.routing_info["engine"] = "ollama"
            elif self.openai_llm:
                messages = [HumanMessage(content=state.user_query)]
                response = self.openai_llm.invoke(messages)
                state.llm_response = response.content
                state.routing_info["engine"] = "openai"
            else:
                state.llm_response = "죄송합니다. LLM 서비스가 현재 사용할 수 없습니다."
                state.routing_info["engine"] = "fallback"
                
        except Exception as e:
            logger.error(f"Direct LLM 오류: {e}")
            state.llm_response = f"일반 상식 질문: {state.user_query}\n\n죄송합니다. 현재 LLM 서버에 연결할 수 없습니다."
            state.routing_info["engine"] = "error"
            
        return state
    
    def rag_search_response(self, state: ChatState) -> ChatState:
        """RAG 검색 응답 (50%)"""
        try:
            # RAGFlow 또는 DSRAG 호출
            rag_engine = getattr(state, 'rag_engine', 'ragflow')
            
            if rag_engine == 'ragflow':
                state = self._call_ragflow(state)
            else:
                state = self._call_dsrag(state)
                
        except Exception as e:
            logger.error(f"RAG 검색 오류: {e}")
            state.llm_response = f"문서 검색 질문: {state.user_query}\n\n죄송합니다. 문서 검색 서비스가 현재 사용할 수 없습니다."
            state.routing_info["engine"] = "error"
            
        return state
    
    def _call_ragflow(self, state: ChatState) -> ChatState:
        """RAGFlow 호출"""
        try:
            # RAGFlow API 호출
            response = requests.post(
                f"{Config.RAGFLOW_API_URL}/api/chat",
                json={
                    "query": state.user_query,
                    "top_k": 5
                },
                headers={
                    "Authorization": f"Bearer {Config.RAGFLOW_API_KEY}"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                state.llm_response = data.get('answer', '응답을 받지 못했습니다.')
                state.rag_results = data.get('references', [])
                state.routing_info["engine"] = "ragflow"
            else:
                raise Exception(f"RAGFlow API 오류: {response.status_code}")
                
        except Exception as e:
            logger.error(f"RAGFlow 호출 오류: {e}")
            # Fallback to direct LLM
            state = self.direct_llm_response(state)
            state.routing_info["engine"] = "ragflow_fallback"
            
        return state
    
    def _call_dsrag(self, state: ChatState) -> ChatState:
        """DSRAG 호출"""
        try:
            # DSRAG 로직 (Qdrant + 로컬 임베딩)
            state.llm_response = f"DSRAG 검색 결과: {state.user_query}\n\n[구현 예정 - Qdrant 벡터 검색 + 로컬 LLM]"
            state.routing_info["engine"] = "dsrag"
            
        except Exception as e:
            logger.error(f"DSRAG 호출 오류: {e}")
            # Fallback to direct LLM
            state = self.direct_llm_response(state)
            state.routing_info["engine"] = "dsrag_fallback"
            
        return state
    
    def query_expansion_response(self, state: ChatState) -> ChatState:
        """질문 확장 응답 (15%)"""
        try:
            # 질문을 더 구체적으로 확장
            expanded_query = f"다음 질문에 대해 상세하고 구체적으로 설명해주세요: {state.user_query}"
            
            # 확장된 질문으로 LLM 호출
            temp_state = ChatState(
                messages=state.messages,
                user_query=expanded_query
            )
            temp_state = self.direct_llm_response(temp_state)
            
            state.expanded_query = expanded_query
            state.llm_response = temp_state.llm_response
            state.routing_info["engine"] = "query_expansion"
            
        except Exception as e:
            logger.error(f"Query expansion 오류: {e}")
            state = self.direct_llm_response(state)
            state.routing_info["engine"] = "expansion_fallback"
            
        return state
    
    def mcp_action_response(self, state: ChatState) -> ChatState:
        """MCP 액션 응답 (5%)"""
        try:
            # MCP (Model Context Protocol) 액션
            state.mcp_result = {
                "action": "task_automation",
                "query": state.user_query,
                "status": "planned"
            }
            state.llm_response = f"작업 자동화 요청: {state.user_query}\n\n[구현 예정 - MCP 기반 외부 시스템 연동]"
            state.routing_info["engine"] = "mcp"
            
        except Exception as e:
            logger.error(f"MCP 액션 오류: {e}")
            state = self.direct_llm_response(state)
            state.routing_info["engine"] = "mcp_fallback"
            
        return state
    
    def create_graph(self):
        """LangGraph 생성"""
        workflow = StateGraph(ChatState)
        
        # 노드 추가
        workflow.add_node("classify", self.classify_query)
        workflow.add_node("direct_llm", self.direct_llm_response)
        workflow.add_node("rag_search", self.rag_search_response)
        workflow.add_node("query_expansion", self.query_expansion_response)
        workflow.add_node("mcp_task", self.mcp_action_response)
        
        # 엣지 추가
        workflow.add_edge(START, "classify")
        
        # 조건부 라우팅
        workflow.add_conditional_edges(
            "classify",
            lambda state: state.route_decision,
            {
                RouteType.DIRECT_LLM.value: "direct_llm",
                RouteType.RAG_SEARCH.value: "rag_search",
                RouteType.QUERY_EXPANSION.value: "query_expansion",
                RouteType.MCP_ACTION.value: "mcp_task"
            }
        )
        
        # 모든 노드에서 END로
        workflow.add_edge("direct_llm", END)
        workflow.add_edge("rag_search", END)
        workflow.add_edge("query_expansion", END)
        workflow.add_edge("mcp_task", END)
        
        return workflow.compile()

# Flask App
app = Flask(__name__)
CORS(app)

# LangGraph 라우터 초기화
router = ExGPTRouter()
graph = router.create_graph()

# Logging 설정
logger.add("logs/ex-gpt-enterprise.log", rotation="1 day", retention="30 days")

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
    """채팅 API - LangGraph 기반"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': '메시지가 필요합니다.'}), 400
            
        user_message = data['message']
        search_mode = data.get('search_mode', False)
        rag_engine = data.get('rag_engine', 'ragflow')
        conversation_history = data.get('conversation_history', [])
        
        # 채팅 상태 생성
        state = ChatState(
            messages=conversation_history,
            user_query=user_message
        )
        
        # RAG 엔진 설정
        state.rag_engine = rag_engine
        
        # 검색 모드일 경우 RAG 우선
        if search_mode:
            state.route_decision = RouteType.RAG_SEARCH.value
        
        # LangGraph 실행
        logger.info(f"Processing query: {user_message[:100]}...")
        result = graph.invoke(state)
        
        # 응답 구성
        response_data = {
            'reply': result.llm_response,
            'routing_info': result.routing_info,
            'rag_results': result.rag_results,
            'expanded_query': result.expanded_query,
            'mcp_result': result.mcp_result,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Response generated via: {result.routing_info.get('path', 'unknown')}")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Chat API 오류: {e}")
        return jsonify({
            'error': '처리 중 오류가 발생했습니다.',
            'reply': '죄송합니다. 일시적인 오류가 발생했습니다. 다시 시도해주세요.',
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
        'services': {
            'ollama': 'unknown',
            'ragflow': 'unknown',
            'qdrant': 'unknown'
        }
    }
    
    # Ollama 상태 확인
    try:
        response = requests.get(f"{Config.OLLAMA_BASE_URL}/api/tags", timeout=5)
        status['services']['ollama'] = 'healthy' if response.status_code == 200 else 'unhealthy'
    except:
        status['services']['ollama'] = 'unhealthy'
    
    # RAGFlow 상태 확인
    try:
        response = requests.get(f"{Config.RAGFLOW_API_URL}/api/health", timeout=5)
        status['services']['ragflow'] = 'healthy' if response.status_code == 200 else 'unhealthy'
    except:
        status['services']['ragflow'] = 'unhealthy'
    
    # Qdrant 상태 확인
    try:
        response = requests.get(f"{Config.QDRANT_URL}/collections", timeout=5)
        status['services']['qdrant'] = 'healthy' if response.status_code == 200 else 'unhealthy'
    except:
        status['services']['qdrant'] = 'unhealthy'
    
    return jsonify(status)

@app.route('/api/routing-stats', methods=['GET'])
def routing_stats():
    """라우팅 통계"""
    # 실제 운영에서는 Redis나 DB에서 통계 조회
    stats = {
        'total_requests': 1000,
        'routing_distribution': {
            'direct_llm': 30,
            'rag_search': 50,
            'query_expansion': 15,
            'mcp_action': 5
        },
        'engine_usage': {
            'ollama': 70,
            'ragflow': 25,
            'openai': 5
        },
        'timestamp': datetime.now().isoformat()
    }
    return jsonify(stats)

if __name__ == '__main__':
    logger.info("🚀 ex-GPT Enterprise Edition 시작")
    logger.info(f"🔗 서버 주소: http://{Config.HOST}:{Config.PORT}")
    logger.info(f"🤖 Ollama: {Config.OLLAMA_BASE_URL}")
    logger.info(f"📚 RAGFlow: {Config.RAGFLOW_API_URL}")
    logger.info(f"🔍 Qdrant: {Config.QDRANT_URL}")
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG,
        threaded=True
    )
