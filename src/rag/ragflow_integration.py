"""
RAGFlow 통합 모듈
한국도로공사 ex-GPT와 RAGFlow를 연동하기 위한 모듈
"""

import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    from ragflow_sdk import RAGFlow
except ImportError:
    print("Warning: ragflow-sdk not installed. Run 'poetry install' to install dependencies.")
    RAGFlow = None

import requests
from requests.auth import HTTPBasicAuth


class ExGPTRAGFlowIntegration:
    """ex-GPT와 RAGFlow 통합 클래스"""
    
    def __init__(
        self, 
        ragflow_host: str = "http://localhost:8080",
        api_key: Optional[str] = None
    ):
        self.ragflow_host = ragflow_host
        self.api_key = api_key or os.getenv("RAGFLOW_API_KEY")
        self.logger = logging.getLogger(__name__)
        
        # RAGFlow SDK 초기화
        if RAGFlow and self.api_key:
            self.rag = RAGFlow(self.api_key, self.ragflow_host)
        else:
            self.rag = None
            self.logger.warning("RAGFlow SDK not available or API key not set")
    
    def check_connection(self) -> bool:
        """RAGFlow 서버 연결 확인"""
        try:
            response = requests.get(f"{self.ragflow_host}/health", timeout=5)
            return response.status_code == 200
        except requests.RequestException as e:
            self.logger.error(f"RAGFlow 연결 실패: {e}")
            return False
    
    def create_knowledge_base(self, name: str, description: str = "") -> Optional[str]:
        """지식베이스 생성"""
        if not self.rag:
            self.logger.error("RAGFlow SDK가 초기화되지 않았습니다")
            return None
        
        try:
            dataset = self.rag.create_dataset(name=name, description=description)
            self.logger.info(f"지식베이스 생성 성공: {name} (ID: {dataset.id})")
            return dataset.id
        except Exception as e:
            self.logger.error(f"지식베이스 생성 실패: {e}")
            return None
    
    def upload_document(self, dataset_id: str, file_path: str) -> Optional[str]:
        """문서 업로드"""
        if not self.rag:
            self.logger.error("RAGFlow SDK가 초기화되지 않았습니다")
            return None
        
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                self.logger.error(f"파일이 존재하지 않습니다: {file_path}")
                return None
            
            # 데이터셋 가져오기
            datasets = self.rag.list_datasets()
            dataset = next((ds for ds in datasets if ds.id == dataset_id), None)
            
            if not dataset:
                self.logger.error(f"데이터셋을 찾을 수 없습니다: {dataset_id}")
                return None
            
            # 파일 읽기 및 업로드
            with open(file_path, 'rb') as file:
                blob = file.read()
            
            document_infos = [{
                "display_name": file_path.name,
                "blob": blob
            }]
            
            documents = dataset.upload_documents(document_infos)
            if documents:
                doc_id = documents[0].id
                self.logger.info(f"문서 업로드 성공: {file_path.name} (ID: {doc_id})")
                return doc_id
            
        except Exception as e:
            self.logger.error(f"문서 업로드 실패: {e}")
            return None
    
    def parse_document(self, dataset_id: str, document_ids: List[str]) -> bool:
        """문서 파싱"""
        if not self.rag:
            self.logger.error("RAGFlow SDK가 초기화되지 않았습니다")
            return False
        
        try:
            datasets = self.rag.list_datasets()
            dataset = next((ds for ds in datasets if ds.id == dataset_id), None)
            
            if not dataset:
                self.logger.error(f"데이터셋을 찾을 수 없습니다: {dataset_id}")
                return False
            
            dataset.async_parse_documents(document_ids)
            self.logger.info(f"문서 파싱 시작: {document_ids}")
            return True
            
        except Exception as e:
            self.logger.error(f"문서 파싱 실패: {e}")
            return False
    
    def search_documents(
        self, 
        dataset_id: str, 
        query: str, 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """문서 검색"""
        if not self.rag:
            self.logger.error("RAGFlow SDK가 초기화되지 않았습니다")
            return []
        
        try:
            # HTTP API를 사용한 검색 (SDK에 검색 기능이 제한적일 수 있음)
            search_url = f"{self.ragflow_host}/api/v1/retrieval"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "dataset_ids": [dataset_id],
                "query": query,
                "top_k": top_k
            }
            
            response = requests.post(search_url, json=payload, headers=headers)
            if response.status_code == 200:
                results = response.json()
                self.logger.info(f"검색 완료: {len(results.get('data', []))}개 결과")
                return results.get('data', [])
            else:
                self.logger.error(f"검색 실패: {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"문서 검색 실패: {e}")
            return []
    
    def create_chat_assistant(
        self, 
        name: str, 
        dataset_ids: List[str],
        system_prompt: str = ""
    ) -> Optional[str]:
        """채팅 어시스턴트 생성"""
        if not self.rag:
            self.logger.error("RAGFlow SDK가 초기화되지 않았습니다")
            return None
        
        try:
            # HTTP API를 사용한 채팅 어시스턴트 생성
            chat_url = f"{self.ragflow_host}/api/v1/chats"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "name": name,
                "dataset_ids": dataset_ids,
                "prompt": system_prompt or "당신은 도움이 되는 AI 어시스턴트입니다."
            }
            
            response = requests.post(chat_url, json=payload, headers=headers)
            if response.status_code == 200:
                result = response.json()
                assistant_id = result.get('data', {}).get('id')
                self.logger.info(f"채팅 어시스턴트 생성 성공: {name} (ID: {assistant_id})")
                return assistant_id
            else:
                self.logger.error(f"채팅 어시스턴트 생성 실패: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"채팅 어시스턴트 생성 실패: {e}")
            return None
    
    def chat_with_assistant(
        self, 
        assistant_id: str, 
        message: str,
        session_id: Optional[str] = None
    ) -> Optional[str]:
        """어시스턴트와 채팅"""
        try:
            # 세션 생성 또는 기존 세션 사용
            if not session_id:
                session_id = self._create_session(assistant_id)
                if not session_id:
                    return None
            
            # 메시지 전송
            chat_url = f"{self.ragflow_host}/api/v1/chats/{assistant_id}/sessions/{session_id}/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "message": message,
                "stream": False
            }
            
            response = requests.post(chat_url, json=payload, headers=headers)
            if response.status_code == 200:
                result = response.json()
                answer = result.get('data', {}).get('answer', '')
                self.logger.info(f"채팅 응답 받음: {len(answer)} 문자")
                return answer
            else:
                self.logger.error(f"채팅 실패: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"채팅 실패: {e}")
            return None
    
    def _create_session(self, assistant_id: str) -> Optional[str]:
        """세션 생성"""
        try:
            session_url = f"{self.ragflow_host}/api/v1/chats/{assistant_id}/sessions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {"name": "ex-GPT Session"}
            
            response = requests.post(session_url, json=payload, headers=headers)
            if response.status_code == 200:
                result = response.json()
                session_id = result.get('data', {}).get('id')
                return session_id
            
        except Exception as e:
            self.logger.error(f"세션 생성 실패: {e}")
        
        return None


# 편의 함수들
def initialize_ragflow(
    host: str = "http://localhost:8080",
    api_key: Optional[str] = None
) -> ExGPTRAGFlowIntegration:
    """RAGFlow 통합 초기화"""
    return ExGPTRAGFlowIntegration(host, api_key)


def setup_korean_knowledge_base(ragflow: ExGPTRAGFlowIntegration) -> Optional[str]:
    """한국도로공사 전용 지식베이스 설정"""
    return ragflow.create_knowledge_base(
        name="한국도로공사_지식베이스",
        description="한국도로공사 업무 관련 문서와 정보를 담은 지식베이스"
    )


if __name__ == "__main__":
    # 테스트 코드
    logging.basicConfig(level=logging.INFO)
    
    ragflow = initialize_ragflow()
    
    if ragflow.check_connection():
        print("✅ RAGFlow 연결 성공!")
        
        # 지식베이스 생성 테스트
        kb_id = setup_korean_knowledge_base(ragflow)
        if kb_id:
            print(f"✅ 지식베이스 생성 성공: {kb_id}")
        else:
            print("❌ 지식베이스 생성 실패")
    else:
        print("❌ RAGFlow 연결 실패. Docker 서비스가 실행 중인지 확인하세요.")
