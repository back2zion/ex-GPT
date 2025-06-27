# exgpt_auth/rag_filter.py

from typing import List, Dict, Any, Optional
import json
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sqlalchemy.orm import Session
from .permission_service import PermissionService
from .logging_utils import get_logger
from .permissions import PERMISSION_MESSAGES

logger = get_logger(__name__)

class RAGPermissionFilter:
    def __init__(self, qdrant_client: QdrantClient, permission_service: PermissionService):
        self.qdrant_client = qdrant_client
        self.permission_service = permission_service
        self.collection_name = "exgpt_documents"

    async def search_with_permissions(
        self, 
        user_id: str, 
        query: str, 
        db: Session, 
        limit: int = 10,
        score_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """권한 기반 벡터 검색 실행"""
        try:
            # 1. 사용자 권한 기반 필터 생성
            permission_filter = self.permission_service.filter_rag_query(user_id, query, db)
            
            if permission_filter["accessible_count"] == 0:
                logger.warning(f"No accessible documents for user {user_id}")
                return {
                    "success": False,
                    "message": PERMISSION_MESSAGES["no_documents_found"],
                    "results": [],
                    "total_found": 0,
                    "permission_filtered": 0
                }

            # 2. 쿼리 벡터 생성 (실제 환경에서는 embedding 모델 사용)
            query_vector = await self._generate_query_embedding(query)
            
            # 3. Qdrant 검색 필터 구성
            accessible_doc_ids = permission_filter["filter"]["must"][0]["match"]["any"]
            qdrant_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_id",
                        match=models.MatchAny(any=accessible_doc_ids)
                    )
                ]
            )

            # 4. 벡터 검색 실행
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=qdrant_filter,
                limit=limit * 2,  # 권한 필터링으로 일부 제거될 수 있으므로 여유분 검색
                score_threshold=score_threshold,
                with_payload=True,
                with_vectors=False
            )

            # 5. 검색 결과 후처리
            filtered_results = await self._post_process_search_results(
                user_id, search_results, db, limit
            )

            logger.info(f"RAG search completed for {user_id}: {len(filtered_results)} results")
            
            return {
                "success": True,
                "results": filtered_results,
                "total_found": len(search_results),
                "permission_filtered": len(search_results) - len(filtered_results),
                "accessible_documents": permission_filter["accessible_count"]
            }

        except Exception as e:
            logger.error(f"Error in RAG search for {user_id}: {str(e)}")
            return {
                "success": False,
                "message": "검색 중 오류가 발생했습니다.",
                "results": [],
                "error": str(e)
            }

    async def _generate_query_embedding(self, query: str) -> List[float]:
        """쿼리 임베딩 생성 (실제 환경에서는 embedding 모델 사용)"""
        # TODO: 실제 임베딩 모델로 교체 필요
        # 예시: OpenAI Embedding, HuggingFace Transformers, 또는 자체 모델
        try:
            # 임시 더미 벡터 (실제로는 embedding 모델 결과 사용)
            import hashlib
            import numpy as np
            
            # 쿼리 해시를 이용한 재현 가능한 더미 벡터 생성
            hash_object = hashlib.md5(query.encode())
            seed = int(hash_object.hexdigest(), 16) % 1000000
            np.random.seed(seed)
            
            # 768차원 벡터 생성 (BERT 기본 차원)
            embedding = np.random.normal(0, 1, 768).tolist()
            
            logger.debug(f"Generated embedding for query: {query[:50]}...")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating query embedding: {str(e)}")
            # 실패 시 영벡터 반환
            return [0.0] * 768

    async def _post_process_search_results(
        self, 
        user_id: str, 
        search_results: List, 
        db: Session, 
        limit: int
    ) -> List[Dict]:
        """검색 결과 후처리 및 권한 재확인"""
        processed_results = []
        
        for i, result in enumerate(search_results):
            if len(processed_results) >= limit:
                break
                
            try:
                payload = result.payload
                document_id = payload.get("document_id", "")
                
                if not document_id:
                    continue

                # 권한 재확인 (캐시된 결과 활용)
                can_download, download_info = self.permission_service.can_download_file(
                    user_id, document_id, db
                )

                # 결과 구성
                processed_result = {
                    "document_id": document_id,
                    "title": payload.get("title", ""),
                    "content": payload.get("content", ""),
                    "excerpt": self._extract_relevant_excerpt(
                        payload.get("content", ""), payload.get("query", "")
                    ),
                    "source": payload.get("source", ""),
                    "category": payload.get("category", ""),
                    "score": float(result.score),
                    "rank": i + 1,
                    "can_download": can_download,
                    "download_url": f"/api/v1/download/{document_id}" if can_download else None,
                    "metadata": {
                        "created_at": payload.get("created_at", ""),
                        "updated_at": payload.get("updated_at", ""),
                        "file_type": payload.get("file_type", ""),
                        "page_number": payload.get("page_number", 1)
                    }
                }

                # 다운로드 불가 시 추가 정보
                if not can_download and "contact_info" in download_info:
                    processed_result["contact_info"] = download_info["contact_info"]
                    processed_result["access_message"] = download_info.get("message", "")

                processed_results.append(processed_result)

            except Exception as e:
                logger.error(f"Error processing search result {i}: {str(e)}")
                continue

        return processed_results

    def _extract_relevant_excerpt(self, content: str, query: str, max_length: int = 200) -> str:
        """관련성 높은 텍스트 발췌 추출"""
        try:
            if not content or not query:
                return content[:max_length] if content else ""

            # 간단한 키워드 매칭 기반 발췌
            query_terms = query.lower().split()
            content_lower = content.lower()
            
            # 첫 번째 매칭 키워드 위치 찾기
            match_positions = []
            for term in query_terms:
                pos = content_lower.find(term)
                if pos != -1:
                    match_positions.append(pos)
            
            if match_positions:
                # 가장 앞쪽 매칭 위치를 중심으로 발췌
                start_pos = min(match_positions)
                excerpt_start = max(0, start_pos - 50)
                excerpt_end = min(len(content), start_pos + max_length - 50)
                
                excerpt = content[excerpt_start:excerpt_end]
                
                # 앞뒤 생략 표시
                if excerpt_start > 0:
                    excerpt = "..." + excerpt
                if excerpt_end < len(content):
                    excerpt = excerpt + "..."
                    
                return excerpt
            else:
                # 매칭이 없으면 앞부분 반환
                return content[:max_length] + ("..." if len(content) > max_length else "")
                
        except Exception as e:
            logger.error(f"Error extracting excerpt: {str(e)}")
            return content[:max_length] if content else ""

    async def index_document_with_permissions(
        self, 
        document_id: str, 
        content: str, 
        metadata: Dict,
        permissions: Dict,
        db: Session
    ) -> bool:
        """권한 정보와 함께 문서 인덱싱"""
        try:
            # 1. 문서 임베딩 생성
            embedding = await self._generate_query_embedding(content)
            
            # 2. Qdrant 페이로드 구성
            payload = {
                "document_id": document_id,
                "title": metadata.get("title", ""),
                "content": content,
                "source": metadata.get("source", ""),
                "category": metadata.get("category", ""),
                "file_type": metadata.get("file_type", ""),
                "created_at": metadata.get("created_at", ""),
                "updated_at": metadata.get("updated_at", ""),
                "page_number": metadata.get("page_number", 1),
                # 권한 정보도 페이로드에 포함 (빠른 필터링용)
                "owner_department": permissions.get("owner_department", ""),
                "access_departments": permissions.get("access_departments", []),
                "is_sensitive": permissions.get("is_sensitive", False)
            }

            # 3. Qdrant에 문서 추가
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=hash(document_id) % (2**31),
                        vector=embedding,
                        payload=payload
                    )
                ]
            )

            logger.info(f"Document indexed with permissions: {document_id}")
            return True

        except Exception as e:
            logger.error(f"Error indexing document {document_id}: {str(e)}")
            return False

    async def remove_document_from_index(self, document_id: str) -> bool:
        """인덱스에서 문서 제거"""
        try:
            point_id = hash(document_id) % (2**31)
            
            self.qdrant_client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(points=[point_id])
            )
            
            logger.info(f"Document removed from index: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing document {document_id} from index: {str(e)}")
            return False

    async def update_document_permissions_in_index(
        self, 
        document_id: str, 
        new_permissions: Dict,
        db: Session
    ) -> bool:
        """인덱스 내 문서의 권한 정보 업데이트"""
        try:
            point_id = hash(document_id) % (2**31)
            
            # 기존 페이로드 조회
            existing_points = self.qdrant_client.retrieve(
                collection_name=self.collection_name,
                ids=[point_id],
                with_payload=True
            )
            
            if not existing_points:
                logger.warning(f"Document not found in index: {document_id}")
                return False
            
            # 페이로드 업데이트
            existing_payload = existing_points[0].payload
            existing_payload.update({
                "owner_department": new_permissions.get("owner_department", ""),
                "access_departments": new_permissions.get("access_departments", []),
                "is_sensitive": new_permissions.get("is_sensitive", False),
                "updated_at": new_permissions.get("updated_at", "")
            })
            
            # Qdrant 업데이트
            self.qdrant_client.set_payload(
                collection_name=self.collection_name,
                payload=existing_payload,
                points=[point_id]
            )
            
            logger.info(f"Document permissions updated in index: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating document permissions in index {document_id}: {str(e)}")
            return False

    async def get_user_accessible_document_stats(self, user_id: str, db: Session) -> Dict:
        """사용자가 접근 가능한 문서 통계"""
        try:
            accessible_docs = self.permission_service.get_accessible_documents(user_id, "", db)
            
            if not accessible_docs:
                return {
                    "total_accessible": 0,
                    "by_category": {},
                    "by_department": {},
                    "by_sensitivity": {"sensitive": 0, "normal": 0}
                }
            
            # Qdrant에서 접근 가능한 문서들의 메타데이터 조회
            point_ids = [hash(doc_id) % (2**31) for doc_id in accessible_docs]
            
            accessible_points = self.qdrant_client.retrieve(
                collection_name=self.collection_name,
                ids=point_ids,
                with_payload=True
            )
            
            # 통계 집계
            stats = {
                "total_accessible": len(accessible_points),
                "by_category": {},
                "by_department": {},
                "by_sensitivity": {"sensitive": 0, "normal": 0}
            }
            
            for point in accessible_points:
                payload = point.payload
                
                # 카테고리별 통계
                category = payload.get("category", "기타")
                stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
                
                # 부서별 통계
                owner_dept = payload.get("owner_department", "알수없음")
                stats["by_department"][owner_dept] = stats["by_department"].get(owner_dept, 0) + 1
                
                # 민감도별 통계
                if payload.get("is_sensitive", False):
                    stats["by_sensitivity"]["sensitive"] += 1
                else:
                    stats["by_sensitivity"]["normal"] += 1
            
            logger.info(f"Document stats generated for user {user_id}: {stats['total_accessible']} accessible")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting document stats for {user_id}: {str(e)}")
            return {"error": "통계 조회 중 오류가 발생했습니다."}

    async def batch_permission_update(self, updates: List[Dict], db: Session) -> Dict:
        """권한 정보 일괄 업데이트"""
        try:
            success_count = 0
            error_count = 0
            errors = []
            
            for update in updates:
                document_id = update.get("document_id")
                new_permissions = update.get("permissions", {})
                
                if not document_id:
                    error_count += 1
                    errors.append({"document_id": "", "error": "document_id 누락"})
                    continue
                
                success = await self.update_document_permissions_in_index(
                    document_id, new_permissions, db
                )
                
                if success:
                    success_count += 1
                else:
                    error_count += 1
                    errors.append({"document_id": document_id, "error": "업데이트 실패"})
            
            result = {
                "total_updates": len(updates),
                "success_count": success_count,
                "error_count": error_count,
                "success_rate": success_count / len(updates) if updates else 0
            }
            
            if errors:
                result["errors"] = errors
            
            logger.info(f"Batch permission update completed: {success_count}/{len(updates)} successful")
            return result
            
        except Exception as e:
            logger.error(f"Error in batch permission update: {str(e)}")
            return {
                "total_updates": len(updates) if updates else 0,
                "success_count": 0,
                "error_count": len(updates) if updates else 0,
                "error": str(e)
            }

    async def create_collection_if_not_exists(self):
        """Qdrant 컬렉션 생성 (초기 설정용)"""
        try:
            # 컬렉션 존재 여부 확인
            collections = self.qdrant_client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                # 컬렉션 생성
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=768,  # 임베딩 차원 (BERT 기본)
                        distance=models.Distance.COSINE
                    ),
                    # 인덱스 설정
                    hnsw_config=models.HnswConfigDiff(
                        m=16,
                        ef_construct=100,
                        full_scan_threshold=10000
                    ),
                    # 페이로드 인덱스 설정 (빠른 필터링용)
                    optimizers_config=models.OptimizersConfigDiff(
                        default_segment_number=2
                    )
                )
                
                # 페이로드 필드 인덱스 생성
                payload_indexes = [
                    ("document_id", models.PayloadSchemaType.KEYWORD),
                    ("category", models.PayloadSchemaType.KEYWORD),
                    ("owner_department", models.PayloadSchemaType.KEYWORD),
                    ("is_sensitive", models.PayloadSchemaType.BOOL)
                ]
                
                for field_name, field_type in payload_indexes:
                    self.qdrant_client.create_payload_index(
                        collection_name=self.collection_name,
                        field_name=field_name,
                        field_schema=field_type
                    )
                
                logger.info(f"Qdrant collection created: {self.collection_name}")
            else:
                logger.info(f"Qdrant collection already exists: {self.collection_name}")
                
            return True
            
        except Exception as e:
            logger.error(f"Error creating Qdrant collection: {str(e)}")
            return False

    async def health_check(self) -> Dict:
        """RAG 시스템 상태 확인"""
        try:
            # Qdrant 연결 상태 확인
            collections = self.qdrant_client.get_collections()
            
            # 컬렉션 정보 조회
            collection_info = self.qdrant_client.get_collection(self.collection_name)
            
            return {
                "status": "healthy",
                "qdrant_connected": True,
                "collection_exists": True,
                "total_documents": collection_info.points_count,
                "collection_status": collection_info.status,
                "vector_size": collection_info.config.params.vectors.size,
                "distance_metric": collection_info.config.params.vectors.distance,
                "last_check": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"RAG health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "qdrant_connected": False,
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }