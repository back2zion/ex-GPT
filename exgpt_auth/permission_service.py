# exgpt_auth/permission_service.py

from typing import List, Dict, Tuple, Optional
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .models import User, DocumentPermission, PermissionMatrix, AccessLog
from .permissions import SystemAccessLevel, DocumentAccessType, DownloadPermission, DOCUMENT_POLICIES, PERMISSION_MESSAGES
from .database import get_db, get_redis_client
from .logging_utils import get_logger

logger = get_logger(__name__)

class PermissionService:
    def __init__(self):
        self.redis_client = get_redis_client()
        self.cache_ttl = 300  # 5분 캐시

    def check_system_access(self, user_id: str, db: Session) -> bool:
        """시스템 접근 권한 확인"""
        try:
            # 캐시에서 먼저 확인
            cache_key = f"system_access:{user_id}"
            cached_result = self.redis_client.get(cache_key)
            
            if cached_result is not None:
                logger.info(f"Cache hit for system access: {user_id}")
                return json.loads(cached_result)
            
            # DB에서 사용자 권한 조회
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user or not user.is_active:
                self._log_access_attempt(user_id, "system", "system_access", "denied_inactive", db)
                return False
            
            has_access = user.system_access_level > SystemAccessLevel.BLOCKED
            
            # 결과 캐시 저장
            self.redis_client.setex(cache_key, self.cache_ttl, json.dumps(has_access))
            
            self._log_access_attempt(user_id, "system", "system_access", 
                                   "allowed" if has_access else "denied", db)
            
            logger.info(f"System access check: {user_id} -> {has_access}")
            return has_access
            
        except Exception as e:
            logger.error(f"Error checking system access for {user_id}: {str(e)}")
            return False

    def get_accessible_documents(self, user_id: str, query: str, db: Session) -> List[str]:
        """사용자가 접근 가능한 문서 ID 목록 반환"""
        try:
            # 캐시 키 생성
            cache_key = f"accessible_docs:{user_id}"
            cached_docs = self.redis_client.get(cache_key)
            
            if cached_docs is not None:
                logger.info(f"Cache hit for accessible documents: {user_id}")
                return json.loads(cached_docs)
            
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                return []
            
            accessible_docs = []
            
            # 1. 전체 공개 문서 (법령규정 등)
            public_docs = db.query(DocumentPermission).filter(
                DocumentPermission.access_type == DocumentAccessType.INCLUDE,
                DocumentPermission.access_departments.op('?')('전체')
            ).all()
            accessible_docs.extend([doc.document_id for doc in public_docs])
            
            # 2. 부서별 접근 가능 문서
            dept_docs = db.query(DocumentPermission).filter(
                DocumentPermission.access_departments.op('?')(user.department_code),
                DocumentPermission.access_type == DocumentAccessType.INCLUDE
            ).all()
            accessible_docs.extend([doc.document_id for doc in dept_docs])
            
            # 3. 개인 업로드 문서 (마이AI)
            personal_docs = db.query(DocumentPermission).filter(
                DocumentPermission.owner_user_id == user_id,
                DocumentPermission.access_type == DocumentAccessType.INCLUDE
            ).all()
            accessible_docs.extend([doc.document_id for doc in personal_docs])
            
            # 4. 관리자는 추가 권한
            if user.system_access_level >= SystemAccessLevel.MANAGER:
                manager_docs = db.query(DocumentPermission).filter(
                    DocumentPermission.owner_department == user.department_code
                ).all()
                accessible_docs.extend([doc.document_id for doc in manager_docs])
            
            # 중복 제거
            unique_docs = list(set(accessible_docs))
            
            # 캐시 저장
            self.redis_client.setex(cache_key, self.cache_ttl, json.dumps(unique_docs))
            
            logger.info(f"Accessible documents for {user_id}: {len(unique_docs)} docs")
            return unique_docs
            
        except Exception as e:
            logger.error(f"Error getting accessible documents for {user_id}: {str(e)}")
            return []

    def can_download_file(self, user_id: str, document_id: str, db: Session) -> Tuple[bool, Dict]:
        """파일 다운로드 권한 확인 및 메타데이터 반환"""
        try:
            cache_key = f"download_perm:{user_id}:{document_id}"
            cached_result = self.redis_client.get(cache_key)
            
            if cached_result is not None:
                logger.info(f"Cache hit for download permission: {user_id}:{document_id}")
                return tuple(json.loads(cached_result))
            
            user = db.query(User).filter(User.user_id == user_id).first()
            doc_perm = db.query(DocumentPermission).filter(
                DocumentPermission.document_id == document_id
            ).first()
            
            if not user or not doc_perm:
                self._log_access_attempt(user_id, document_id, "download", "denied_not_found", db)
                return False, {"error": "사용자 또는 문서를 찾을 수 없습니다."}
            
            result = {"document_id": document_id, "title": doc_perm.metadata.get("title", "")}
            
            # 1. 개인 업로드 문서 체크
            if doc_perm.owner_user_id == user_id:
                self._log_access_attempt(user_id, document_id, "download", "allowed_owner", db)
                result.update({"can_download": True, "reason": "owner"})
                cache_result = (True, result)
                self.redis_client.setex(cache_key, self.cache_ttl, json.dumps(cache_result))
                return cache_result
            
            # 2. 시스템 관리자는 모든 파일 다운로드 가능
            if user.system_access_level >= SystemAccessLevel.ADMIN:
                self._log_access_attempt(user_id, document_id, "download", "allowed_admin", db)
                result.update({"can_download": True, "reason": "admin"})
                cache_result = (True, result)
                self.redis_client.setex(cache_key, self.cache_ttl, json.dumps(cache_result))
                return cache_result
            
            # 3. 일반 다운로드 권한 체크
            can_download = False
            
            # 전체 공개 문서
            if '전체' in doc_perm.access_departments and doc_perm.download_permission == DownloadPermission.ALLOWED:
                can_download = True
                reason = "public"
            
            # 부서별 권한 체크
            elif user.department_code in doc_perm.access_departments:
                if doc_perm.download_permission == DownloadPermission.ALLOWED:
                    can_download = True
                    reason = "department"
                elif doc_perm.download_permission == DownloadPermission.METADATA_ONLY:
                    # 메타데이터만 제공 (국회 요구자료 케이스)
                    result.update({
                        "can_download": False,
                        "contact_info": doc_perm.metadata.get("contact_info", {}),
                        "department": doc_perm.owner_department,
                        "reason": "metadata_only"
                    })
                    self._log_access_attempt(user_id, document_id, "download", "denied_metadata_only", db)
                    cache_result = (False, result)
                    self.redis_client.setex(cache_key, self.cache_ttl, json.dumps(cache_result))
                    return cache_result
            
            if can_download:
                result.update({"can_download": True, "reason": reason})
                self._log_access_attempt(user_id, document_id, "download", f"allowed_{reason}", db)
            else:
                result.update({
                    "can_download": False,
                    "contact_info": doc_perm.metadata.get("contact_info", {}),
                    "reason": "no_permission"
                })
                self._log_access_attempt(user_id, document_id, "download", "denied_no_permission", db)
            
            cache_result = (can_download, result)
            self.redis_client.setex(cache_key, self.cache_ttl, json.dumps(cache_result))
            
            return cache_result
            
        except Exception as e:
            logger.error(f"Error checking download permission: {user_id}:{document_id} - {str(e)}")
            return False, {"error": "권한 확인 중 오류가 발생했습니다."}

    def filter_rag_query(self, user_id: str, query: str, db: Session) -> Dict:
        """권한 기반 RAG 쿼리 필터링"""
        try:
            accessible_docs = self.get_accessible_documents(user_id, query, db)
            
            if not accessible_docs:
                logger.warning(f"No accessible documents for user {user_id}")
                return {
                    "query": query,
                    "filter": {"document_id": {"$in": []}},  # 빈 결과 반환
                    "accessible_count": 0
                }
            
            # Qdrant 벡터 검색용 필터 생성
            filtered_query = {
                "query": query,
                "filter": {
                    "must": [
                        {"key": "document_id", "match": {"any": accessible_docs}}
                    ]
                },
                "accessible_count": len(accessible_docs)
            }
            
            logger.info(f"RAG query filtered for {user_id}: {len(accessible_docs)} accessible docs")
            return filtered_query
            
        except Exception as e:
            logger.error(f"Error filtering RAG query for {user_id}: {str(e)}")
            return {"query": query, "filter": {}, "accessible_count": 0}

    def process_response_permissions(self, user_id: str, response: Dict, db: Session) -> Dict:
        """응답 후처리 및 권한 기반 필터링"""
        try:
            processed_response = {
                "answer": response.get("answer", ""),
                "references": [],
                "permission_summary": {
                    "total_references": 0,
                    "accessible_references": 0,
                    "downloadable_references": 0
                }
            }
            
            references = response.get("references", [])
            processed_response["permission_summary"]["total_references"] = len(references)
            
            for ref in references:
                doc_id = ref.get("document_id", "")
                if not doc_id:
                    continue
                
                # 다운로드 권한 확인
                can_download, download_info = self.can_download_file(user_id, doc_id, db)
                
                ref_info = {
                    "document_id": doc_id,
                    "title": ref.get("title", download_info.get("title", "")),
                    "source": ref.get("source", ""),
                    "excerpt": ref.get("excerpt", ""),
                    "can_download": can_download,
                    "download_url": f"/api/v1/download/{doc_id}" if can_download else None
                }
                
                # 다운로드 불가 시 연락처 정보 추가
                if not can_download and "contact_info" in download_info:
                    ref_info["contact_info"] = download_info["contact_info"]
                    ref_info["message"] = PERMISSION_MESSAGES["download_denied"].format(
                        contact_info=download_info["contact_info"]
                    )
                
                processed_response["references"].append(ref_info)
                processed_response["permission_summary"]["accessible_references"] += 1
                
                if can_download:
                    processed_response["permission_summary"]["downloadable_references"] += 1
            
            # 권한 제한으로 인한 부분적 답변 메시지
            if processed_response["permission_summary"]["accessible_references"] < processed_response["permission_summary"]["total_references"]:
                processed_response["warning"] = PERMISSION_MESSAGES["partial_access"]
            
            logger.info(f"Response processed for {user_id}: {processed_response['permission_summary']}")
            return processed_response
            
        except Exception as e:
            logger.error(f"Error processing response permissions for {user_id}: {str(e)}")
            return {"answer": response.get("answer", ""), "references": [], "error": "권한 처리 중 오류가 발생했습니다."}

    def handle_personal_document(self, user_id: str, doc_id: str, action: str, db: Session) -> Dict:
        """개인 업로드 문서(마이AI) 특수 처리"""
        try:
            doc_perm = db.query(DocumentPermission).filter(
                DocumentPermission.document_id == doc_id
            ).first()
            
            if not doc_perm:
                return {"success": False, "error": "문서를 찾을 수 없습니다."}
            
            # 업로드한 본인만 접근 가능
            if doc_perm.owner_user_id != user_id:
                self._log_access_attempt(user_id, doc_id, action, "denied_not_owner", db)
                return {"success": False, "error": "본인이 업로드한 문서만 접근 가능합니다."}
            
            if action == "access":
                # 접근 허용하고 임시 플래그 설정
                result = {
                    "success": True,
                    "can_access": True,
                    "temporary": True,
                    "auto_delete_after_response": True
                }
                self._log_access_attempt(user_id, doc_id, action, "allowed_owner", db)
                return result
                
            elif action == "cleanup":
                # 답변 완료 후 문서 삭제
                db.delete(doc_perm)
                db.commit()
                
                # 캐시에서도 제거
                self._invalidate_user_cache(user_id)
                
                logger.info(f"Personal document cleaned up: {doc_id} for user {user_id}")
                return {"success": True, "deleted": True}
            
            return {"success": False, "error": "알 수 없는 액션입니다."}
            
        except Exception as e:
            logger.error(f"Error handling personal document {doc_id} for {user_id}: {str(e)}")
            return {"success": False, "error": "문서 처리 중 오류가 발생했습니다."}

    def _log_access_attempt(self, user_id: str, document_id: str, action: str, result: str, db: Session):
        """접근 시도 로깅"""
        try:
            log_entry = AccessLog(
                user_id=user_id,
                document_id=document_id,
                action=action,
                result=result,
                timestamp=datetime.utcnow()
            )
            db.add(log_entry)
            db.commit()
            
            # 구조화된 로그도 남김
            logger.info(f"Access logged: {user_id} -> {document_id} [{action}] = {result}")
            
        except Exception as e:
            logger.error(f"Error logging access attempt: {str(e)}")

    def _invalidate_user_cache(self, user_id: str):
        """사용자 관련 캐시 무효화"""
        try:
            cache_patterns = [
                f"system_access:{user_id}",
                f"accessible_docs:{user_id}",
                f"download_perm:{user_id}:*"
            ]
            
            for pattern in cache_patterns:
                if "*" in pattern:
                    # 패턴 매칭으로 캐시 삭제
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        self.redis_client.delete(*keys)
                else:
                    self.redis_client.delete(pattern)
                    
            logger.info(f"Cache invalidated for user: {user_id}")
            
        except Exception as e:
            logger.error(f"Error invalidating cache for {user_id}: {str(e)}")

    def get_user_permission_summary(self, user_id: str, db: Session) -> Dict:
        """사용자 권한 요약 정보 반환 (관리자용)"""
        try:
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                return {"error": "사용자를 찾을 수 없습니다."}
            
            accessible_docs = self.get_accessible_documents(user_id, "", db)
            
            # 문서 카테고리별 통계
            category_stats = {}
            for doc_id in accessible_docs:
                doc_perm = db.query(DocumentPermission).filter(
                    DocumentPermission.document_id == doc_id
                ).first()
                if doc_perm:
                    category = doc_perm.metadata.get("category", "기타")
                    category_stats[category] = category_stats.get(category, 0) + 1
            
            return {
                "user_id": user_id,
                "department": user.department_code,
                "system_access_level": user.system_access_level,
                "is_active": user.is_active,
                "accessible_documents_count": len(accessible_docs),
                "category_breakdown": category_stats,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting permission summary for {user_id}: {str(e)}")
            return {"error": "권한 요약 조회 중 오류가 발생했습니다."}