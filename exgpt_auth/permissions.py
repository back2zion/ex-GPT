from enum import IntEnum

class SystemAccessLevel(IntEnum):
    BLOCKED = 0
    BASIC = 1
    MANAGER = 2
    ADMIN = 3
    EXTERNAL = 4

DOCUMENT_POLICIES = {
    "법령규정": {"access": "전체공개", "download": "전체허용"},
    "KCS_KDS": {"access": "설계처+지역본부", "download": "해당부서만"},
    "국회요구자료": {"access": "답변생성가능", "download": "해당부서만", "metadata": "필수표시"},
    "내부방침": {"access": "해당부서만", "download": "해당부서만"},
    "개인업로드": {"access": "본인만", "download": "본인만", "auto_delete": True}
}

PERMISSION_MESSAGES = {
    "no_system_access": "ex-GPT 시스템 접근 권한이 없습니다. 관리자에게 문의하세요.",
    "no_documents_found": "현재 권한으로 참조할 수 있는 자료가 없습니다.",
    "partial_access": "일부 자료에 대한 접근 권한이 제한되어 부분적 답변을 제공합니다.",
    "download_denied": "파일 다운로드 권한이 없습니다. 담당자 연락처: {contact_info}",
    "temp_document_expired": "임시 업로드 문서가 삭제되었습니다. 다시 업로드해 주세요."
} 