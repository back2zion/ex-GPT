# tests/test_permissions.py

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
import os

from main import app, get_db, get_current_user
from exgpt_auth.models import Base, User, DocumentPermission, AccessLog
from exgpt_auth.permission_service import PermissionService
from exgpt_auth.permissions import SystemAccessLevel, DocumentAccessType, DownloadPermission
from exgpt_auth.database import get_redis_client

# 테스트 데이터베이스 설정
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

def override_get_redis():
    # 테스트용 Mock Redis
    mock_redis = Mock()
    mock_redis.get.return_value = None
    mock_redis.setex.return_value = True
    mock_redis.delete.return_value = True
    mock_redis.keys.return_value = []
    mock_redis.ping.return_value = True
    return mock_redis

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_redis_client] = override_get_redis

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    """테스트 데이터베이스 설정"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    """데이터베이스 세션 픽스처"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def sample_users(db_session):
    """샘플 사용자 데이터"""
    users = [
        User(
            user_id="admin001",
            department_code="정보통신처",
            position_level=5,
            system_access_level=SystemAccessLevel.ADMIN,
            is_active=True
        ),
        User(
            user_id="manager001", 
            department_code="건설처",
            position_level=4,
            system_access_level=SystemAccessLevel.MANAGER,
            is_active=True
        ),
        User(
            user_id="user001",
            department_code="건설처", 
            position_level=2,
            system_access_level=SystemAccessLevel.BASIC,
            is_active=True
        ),
        User(
            user_id="user002",
            department_code="설계처",
            position_level=2, 
            system_access_level=SystemAccessLevel.BASIC,
            is_active=True
        ),
        User(
            user_id="blocked001",
            department_code="기획처",
            position_level=1,
            system_access_level=SystemAccessLevel.BLOCKED,
            is_active=False
        )
    ]
    
    for user in users:
        db_session.add(user)
    db_session.commit()
    
    return users

@pytest.fixture
def sample_documents(db_session):
    """샘플 문서 데이터"""
    documents = [
        DocumentPermission(
            document_id="doc_public_001",
            source_system="법령규정",
            owner_department="법무팀",
            access_departments=["전체"],
            access_type=DocumentAccessType.INCLUDE,
            download_permission=DownloadPermission.ALLOWED,
            is_sensitive=False,
            metadata={"title": "도로법 시행령", "category": "법령규정"}
        ),
        DocumentPermission(
            document_id="doc_construction_001", 
            source_system="내부자료",
            owner_department="건설처",
            access_departments=["건설처"],
            access_type=DocumentAccessType.INCLUDE,
            download_permission=DownloadPermission.ALLOWED,
            is_sensitive=False,
            metadata={"title": "건설 표준 지침", "category": "내부방침"}
        ),
        DocumentPermission(
            document_id="doc_national_001",
            source_system="국회정보시스템", 
            owner_department="건설처",
            access_departments=["건설처", "설계처", "기획처"],
            access_type=DocumentAccessType.INCLUDE,
            download_permission=DownloadPermission.METADATA_ONLY,
            is_sensitive=True,
            metadata={
                "title": "건설사업 예산 관련 국회 요구자료",
                "category": "국회요구자료",
                "contact_info": {"name": "김건설", "phone": "042-123-4567", "email": "kim@ex.co.kr"}
            }
        ),
        DocumentPermission(
            document_id="doc_personal_001",
            source_system="personal_upload",
            owner_user_id="user001",
            owner_department="건설처", 
            access_departments=["user001"],
            access_type=DocumentAccessType.INCLUDE,
            download_permission=DownloadPermission.ALLOWED,
            is_sensitive=False,
            metadata={"title": "개인 업로드 문서", "auto_delete": True}
        )
    ]
    
    for doc in documents:
        db_session.add(doc)
    db_session.commit()
    
    return documents

@pytest.fixture
def auth_headers():
    """인증 헤더 생성"""
    def _auth_headers(user_id: str):
        from main import create_access_token
        token = create_access_token(data={"sub": user_id})
        return {"Authorization": f"Bearer {token}"}
    return _auth_headers

class TestSystemAccess:
    """시스템 접근 권한 테스트"""
    
    def test_admin_system_access(self, setup_database, sample_users, db_session):
        """관리자 시스템 접근 테스트"""
        permission_service = PermissionService()
        
        # 관리자는 접근 가능
        assert permission_service.check_system_access("admin001", db_session) == True
        
        # 차단된 사용자는 접근 불가
        assert permission_service.check_system_access("blocked001", db_session) == False
        
        # 존재하지 않는 사용자는 접근 불가
        assert permission_service.check_system_access("nonexistent", db_session) == False

    def test_user_permission_levels(self, setup_database, sample_users, db_session):
        """사용자 권한 레벨별 접근 테스트"""
        permission_service = PermissionService()
        
        # 일반 사용자 접근 가능
        assert permission_service.check_system_access("user001", db_session) == True
        
        # 관리자 접근 가능  
        assert permission_service.check_system_access("manager001", db_session) == True

class TestDocumentAccess:
    """문서 접근 권한 테스트"""
    
    def test_public_document_access(self, setup_database, sample_users, sample_documents, db_session):
        """전체 공개 문서 접근 테스트"""
        permission_service = PermissionService()
        
        # 모든 활성 사용자는 공개 문서에 접근 가능
        accessible_docs = permission_service.get_accessible_documents("user001", "", db_session)
        assert "doc_public_001" in accessible_docs
        
        accessible_docs = permission_service.get_accessible_documents("user002", "", db_session)
        assert "doc_public_001" in accessible_docs

    def test_department_document_access(self, setup_database, sample_users, sample_documents, db_session):
        """부서별 문서 접근 테스트"""
        permission_service = PermissionService()
        
        # 건설처 사용자는 건설처 문서에 접근 가능
        accessible_docs = permission_service.get_accessible_documents("user001", "", db_session)
        assert "doc_construction_001" in accessible_docs
        
        # 설계처 사용자는 건설처 문서에 접근 불가
        accessible_docs = permission_service.get_accessible_documents("user002", "", db_session)
        assert "doc_construction_001" not in accessible_docs

    def test_personal_document_access(self, setup_database, sample_users, sample_documents, db_session):
        """개인 문서 접근 테스트"""
        permission_service = PermissionService()
        
        # 본인만 개인 문서에 접근 가능
        accessible_docs = permission_service.get_accessible_documents("user001", "", db_session)
        assert "doc_personal_001" in accessible_docs
        
        # 다른 사용자는 개인 문서에 접근 불가
        accessible_docs = permission_service.get_accessible_documents("user002", "", db_session)
        assert "doc_personal_001" not in accessible_docs

class TestDownloadPermissions:
    """다운로드 권한 테스트"""
    
    def test_public_document_download(self, setup_database, sample_users, sample_documents, db_session):
        """공개 문서 다운로드 테스트"""
        permission_service = PermissionService()
        
        can_download, info = permission_service.can_download_file("user001", "doc_public_001", db_session)
        assert can_download == True
        assert info["can_download"] == True

    def test_national_assembly_document_download(self, setup_database, sample_users, sample_documents, db_session):
        """국회 요구자료 다운로드 권한 테스트"""
        permission_service = PermissionService()
        
        # 해당 부서 사용자는 메타데이터만 접근
        can_download, info = permission_service.can_download_file("user001", "doc_national_001", db_session)
        assert can_download == False
        assert "contact_info" in info
        assert info["contact_info"]["name"] == "김건설"
        
        # 다른 부서 사용자도 메타데이터는 접근 가능하지만 다운로드 불가
        can_download, info = permission_service.can_download_file("user002", "doc_national_001", db_session)
        assert can_download == False

    def test_personal_document_download(self, setup_database, sample_users, sample_documents, db_session):
        """개인 문서 다운로드 테스트"""
        permission_service = PermissionService()
        
        # 본인은 다운로드 가능
        can_download, info = permission_service.can_download_file("user001", "doc_personal_001", db_session)
        assert can_download == True
        assert info["reason"] == "owner"
        
        # 다른 사용자는 다운로드 불가
        can_download, info = permission_service.can_download_file("user002", "doc_personal_001", db_session)
        assert can_download == False

class TestPersonalDocumentHandling:
    """개인 문서(마이AI) 특수 처리 테스트"""
    
    def test_personal_document_lifecycle(self, setup_database, sample_users, sample_documents, db_session):
        """개인 문서 생명주기 테스트"""
        permission_service = PermissionService()
        
        # 접근 허용 확인
        result = permission_service.handle_personal_document("user001", "doc_personal_001", "access", db_session)
        assert result["success"] == True
        assert result["temporary"] == True
        assert result["auto_delete_after_response"] == True
        
        # 정리 실행
        result = permission_service.handle_personal_document("user001", "doc_personal_001", "cleanup", db_session)
        assert result["success"] == True
        assert result["deleted"] == True
        
        # 정리 후 문서가 삭제되었는지 확인
        doc = db_session.query(DocumentPermission).filter(
            DocumentPermission.document_id == "doc_personal_001"
        ).first()
        assert doc is None

class TestAPIEndpoints:
    """API 엔드포인트 테스트"""
    
    @patch('main.get_current_user')
    def test_query_endpoint_with_permissions(self, mock_get_current_user, setup_database, sample_users, sample_documents):
        """권한 기반 질의응답 API 테스트"""
        # Mock 사용자 설정
        mock_user = User(
            user_id="user001",
            department_code="건설처", 
            system_access_level=SystemAccessLevel.BASIC
        )
        mock_get_current_user.return_value = mock_user
        
        # RAG 필터 Mock
        with patch('main.rag_filter') as mock_rag:
            mock_rag.search_with_permissions = AsyncMock(return_value={
                "success": True,
                "results": [
                    {
                        "document_id": "doc_public_001",
                        "title": "도로법 시행령",
                        "content": "도로 관련 법령 내용...",
                        "score": 0.95
                    }
                ],
                "total_found": 1,
                "permission_filtered": 0
            })
            
            response = client.post(
                "/api/v1/query",
                json={
                    "query": "도로 건설 관련 법령은?",
                    "max_results": 10,
                    "cleanup_personal_docs": False
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "answer" in data
            assert len(data["references"]) > 0

    def test_download_endpoint_with_permissions(self, setup_database, sample_users, sample_documents, auth_headers):
        """권한 기반 파일 다운로드 API 테스트"""
        headers = auth_headers("user001")
        
        # 존재하지 않는 파일 다운로드 시도
        response = client.get("/api/v1/download/nonexistent", headers=headers)
        assert response.status_code == 404
        
        # 권한 없는 파일 다운로드 시도
        headers_user2 = auth_headers("user002")
        response = client.get("/api/v1/download/doc_construction_001", headers=headers_user2)
        assert response.status_code == 403

    def test_personal_upload_endpoint(self, setup_database, sample_users, auth_headers):
        """개인 문서 업로드 API 테스트"""
        headers = auth_headers("user001")
        
        # 테스트 파일 생성
        test_content = b"Test document content"
        
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file_path = temp_file.name
        
        try:
            with open(temp_file_path, "rb") as f:
                response = client.post(
                    "/api/v1/upload/personal",
                    headers=headers,
                    files={"file": ("test.txt", f, "text/plain")}
                )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] == True
            assert "document_id" in data
            assert data["auto_delete"] == True
            
        finally:
            # 테스트 파일 정리
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    def test_admin_endpoints(self, setup_database, sample_users, sample_documents, auth_headers):
        """관리자 API 엔드포인트 테스트"""
        admin_headers = auth_headers("admin001")
        user_headers = auth_headers("user001")
        
        # 사용자 권한 조회 (관리자)
        response = client.get("/api/v1/admin/permissions/user001", headers=admin_headers)
        assert response.status_code == 200
        
        # 사용자 권한 조회 (일반 사용자 - 실패해야 함)
        response = client.get("/api/v1/admin/permissions/user002", headers=user_headers)
        assert response.status_code == 403
        
        # 문서 통계 조회
        response = client.get("/api/v1/admin/documents/stats", headers=admin_headers)
        assert response.status_code == 200
        
        # 캐시 무효화
        response = client.post(
            "/api/v1/admin/cache/invalidate",
            headers=admin_headers,
            json={"user_ids": ["user001"], "all_users": False}
        )
        assert response.status_code == 200

class TestPermissionCaching:
    """권한 캐싱 테스트"""
    
    def test_permission_cache_hit_miss(self, setup_database, sample_users, db_session):
        """권한 캐시 히트/미스 테스트"""
        permission_service = PermissionService()
        
        # 첫 번째 호출 (캐시 미스)
        with patch.object(permission_service.redis_client, 'get', return_value=None) as mock_get:
            with patch.object(permission_service.redis_client, 'setex') as mock_setex:
                result = permission_service.check_system_access("user001", db_session)
                assert result == True
                mock_get.assert_called_once()
                mock_setex.assert_called_once()
        
        # 두 번째 호출 (캐시 히트)
        with patch.object(permission_service.redis_client, 'get', return_value=b'true') as mock_get:
            with patch.object(permission_service.redis_client, 'setex') as mock_setex:
                result = permission_service.check_system_access("user001", db_session)
                assert result == True
                mock_get.assert_called_once()
                mock_setex.assert_not_called()

    def test_cache_invalidation(self, setup_database, sample_users, db_session):
        """캐시 무효화 테스트"""
        permission_service = PermissionService()
        
        with patch.object(permission_service.redis_client, 'keys', return_value=['key1', 'key2']) as mock_keys:
            with patch.object(permission_service.redis_client, 'delete') as mock_delete:
                permission_service._invalidate_user_cache("user001")
                mock_delete.assert_called()

class TestAuditLogging:
    """감사 로그 테스트"""
    
    def test_access_logging(self, setup_database, sample_users, sample_documents, db_session):
        """접근 로그 기록 테스트"""
        permission_service = PermissionService()
        
        # 권한 확인 시 로그 기록되는지 확인
        permission_service.check_system_access("user001", db_session)
        
        # 로그 확인
        log_entry = db_session.query(AccessLog).filter(
            AccessLog.user_id == "user001",
            AccessLog.action == "system_access"
        ).first()
        
        assert log_entry is not None
        assert log_entry.result in ["allowed", "denied"]

    def test_download_attempt_logging(self, setup_database, sample_users, sample_documents, db_session):
        """다운로드 시도 로그 테스트"""
        permission_service = PermissionService()
        
        # 다운로드 권한 확인
        permission_service.can_download_file("user001", "doc_public_001", db_session)
        
        # 로그 확인
        log_entry = db_session.query(AccessLog).filter(
            AccessLog.user_id == "user001",
            AccessLog.document_id == "doc_public_001",
            AccessLog.action == "download"
        ).first()
        
        assert log_entry is not None

class TestPermissionMatrix:
    """권한 매트릭스 테스트"""
    
    def test_department_permission_matrix(self, setup_database, sample_users, sample_documents, db_session):
        """부서별 권한 매트릭스 테스트"""
        permission_service = PermissionService()
        
        # 건설처 사용자의 접근 가능 문서
        construction_docs = permission_service.get_accessible_documents("user001", "", db_session)
        
        # 설계처 사용자의 접근 가능 문서  
        design_docs = permission_service.get_accessible_documents("user002", "", db_session)
        
        # 공개 문서는 모든 부서에서 접근 가능
        assert "doc_public_001" in construction_docs
        assert "doc_public_001" in design_docs
        
        # 부서별 문서는 해당 부서만 접근 가능
        assert "doc_construction_001" in construction_docs
        assert "doc_construction_001" not in design_docs

    def test_manager_additional_permissions(self, setup_database, sample_users, sample_documents, db_session):
        """관리자 추가 권한 테스트"""
        permission_service = PermissionService()
        
        # 관리자는 본인 부서의 모든 문서에 접근 가능
        manager_docs = permission_service.get_accessible_documents("manager001", "", db_session)
        
        # 관리자는 일반 사용자보다 더 많은 문서에 접근 가능해야 함
        user_docs = permission_service.get_accessible_documents("user001", "", db_session)
        
        # 같은 부서이므로 최소한 같은 수준 이상의 접근 권한
        assert len(manager_docs) >= len(user_docs)

class TestSpecialCases:
    """특수 케이스 테스트"""
    
    def test_national_assembly_document_special_handling(self, setup_database, sample_users, sample_documents, db_session):
        """국회 요구자료 특수 처리 테스트"""
        permission_service = PermissionService()
        
        # 모든 부서에서 답변은 확인 가능하지만 다운로드는 제한
        can_download_construction, info_construction = permission_service.can_download_file(
            "user001", "doc_national_001", db_session
        )
        can_download_design, info_design = permission_service.can_download_file(
            "user002", "doc_national_001", db_session  
        )
        
        # 둘 다 다운로드는 불가하지만 메타데이터는 제공
        assert can_download_construction == False
        assert can_download_design == False
        assert "contact_info" in info_construction
        assert "contact_info" in info_design

    def test_blocked_user_access_denied(self, setup_database, sample_users, db_session):
        """차단된 사용자 접근 거부 테스트"""
        permission_service = PermissionService()
        
        # 차단된 사용자는 시스템 접근 불가
        assert permission_service.check_system_access("blocked001", db_session) == False
        
        # 접근 가능한 문서도 없어야 함
        accessible_docs = permission_service.get_accessible_documents("blocked001", "", db_session)
        assert len(accessible_docs) == 0

    def test_external_user_limited_access(self, setup_database, db_session):
        """외부 사용자 제한적 접근 테스트"""
        # 외부 사용자 생성
        external_user = User(
            user_id="external001",
            department_code="외부",
            position_level=1,
            system_access_level=SystemAccessLevel.EXTERNAL,
            is_active=True
        )
        db_session.add(external_user)
        
        # 전자조달 매뉴얼 문서 생성
        manual_doc = DocumentPermission(
            document_id="doc_manual_001",
            source_system="전자조달",
            owner_department="정보통신처",
            access_departments=["외부", "전체"],
            access_type=DocumentAccessType.INCLUDE,
            download_permission=DownloadPermission.ALLOWED,
            is_sensitive=False,
            metadata={"title": "전자조달 사용자 매뉴얼", "category": "매뉴얼"}
        )
        db_session.add(manual_doc)
        db_session.commit()
        
        permission_service = PermissionService()
        
        # 외부 사용자도 시스템 접근은 가능
        assert permission_service.check_system_access("external001", db_session) == True
        
        # 하지만 제한된 문서만 접근 가능
        accessible_docs = permission_service.get_accessible_documents("external001", "", db_session)
        assert "doc_manual_001" in accessible_docs
        assert len(accessible_docs) >= 1  # 매뉴얼과 전체 공개 문서

class TestErrorHandling:
    """에러 처리 테스트"""
    
    def test_database_error_handling(self, setup_database):
        """데이터베이스 에러 처리 테스트"""
        permission_service = PermissionService()
        
        # 잘못된 세션으로 테스트
        with patch('exgpt_auth.permission_service.Session') as mock_session:
            mock_session.side_effect = Exception("Database connection failed")
            
            # 에러가 발생해도 안전하게 False 반환
            result = permission_service.check_system_access("user001", None)
            assert result == False

    def test_redis_error_handling(self, setup_database, sample_users, db_session):
        """Redis 에러 처리 테스트"""
        permission_service = PermissionService()
        
        # Redis 에러 시에도 DB에서 조회하여 정상 동작
        with patch.object(permission_service.redis_client, 'get', side_effect=Exception("Redis error")):
            result = permission_service.check_system_access("user001", db_session)
            assert result == True  # DB에서 조회하여 정상 결과

    def test_invalid_document_id_handling(self, setup_database, sample_users, db_session):
        """잘못된 문서 ID 처리 테스트"""
        permission_service = PermissionService()
        
        # 존재하지 않는 문서 ID
        can_download, info = permission_service.can_download_file("user001", "nonexistent_doc", db_session)
        assert can_download == False
        assert "error" in info

class TestPerformance:
    """성능 테스트"""
    
    @pytest.mark.performance
    def test_bulk_permission_check_performance(self, setup_database, sample_users, sample_documents, db_session):
        """대량 권한 확인 성능 테스트"""
        permission_service = PermissionService()
        
        import time
        
        # 100번 반복 권한 확인
        start_time = time.time()
        for i in range(100):
            permission_service.check_system_access("user001", db_session)
        end_time = time.time()
        
        # 평균 응답 시간이 10ms 이하여야 함 (캐싱 효과 포함)
        avg_time = (end_time - start_time) / 100
        assert avg_time < 0.01, f"Average response time too high: {avg_time:.4f}s"

    @pytest.mark.performance  
    def test_document_access_list_performance(self, setup_database, sample_users, db_session):
        """대량 문서 접근 목록 조회 성능 테스트"""
        permission_service = PermissionService()
        
        # 1000개 문서 생성
        documents = []
        for i in range(1000):
            doc = DocumentPermission(
                document_id=f"perf_doc_{i:04d}",
                source_system="성능테스트",
                owner_department="건설처" if i % 2 == 0 else "설계처",
                access_departments=["건설처"] if i % 2 == 0 else ["설계처"],
                access_type=DocumentAccessType.INCLUDE,
                download_permission=DownloadPermission.ALLOWED,
                is_sensitive=False,
                metadata={"title": f"성능 테스트 문서 {i}"}
            )
            documents.append(doc)
        
        db_session.add_all(documents)
        db_session.commit()
        
        import time
        
        # 접근 가능 문서 목록 조회 성능 측정
        start_time = time.time()
        accessible_docs = permission_service.get_accessible_documents("user001", "", db_session)
        end_time = time.time()
        
        # 1초 이내에 완료되어야 함
        query_time = end_time - start_time
        assert query_time < 1.0, f"Query time too high: {query_time:.4f}s"
        assert len(accessible_docs) > 500  # 절반 이상은 접근 가능해야 함

class TestHealthCheck:
    """헬스체크 테스트"""
    
    def test_health_endpoint(self):
        """헬스체크 엔드포인트 테스트"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "components" in data
        assert "database" in data["components"]
        assert "redis" in data["components"]

    def test_individual_component_health(self, setup_database):
        """개별 컴포넌트 상태 확인 테스트"""
        response = client.get("/api/v1/health")
        data = response.json()
        
        # DB는 테스트 환경에서 정상이어야 함
        assert data["components"]["database"] == "healthy"
        
        # Redis는 Mock이므로 정상으로 표시
        assert data["components"]["redis"] == "healthy"

if __name__ == "__main__":
    # 테스트 실행
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--durations=10",  # 가장 느린 10개 테스트 표시
        "-m", "not performance"  # 성능 테스트는 기본적으로 제외
    ])