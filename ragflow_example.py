#!/usr/bin/env python3
"""
RAGFlow 통합 예제 스크립트
한국도로공사 ex-GPT에서 RAGFlow를 활용하는 방법을 보여주는 예제
"""

import asyncio
import logging
import os
from pathlib import Path
import sys

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rag.ragflow_integration import ExGPTRAGFlowIntegration


def setup_logging():
    """로깅 설정"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    """메인 실행 함수"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print("🚀 RAGFlow 통합 예제 시작")
    print("=" * 50)
    
    # RAGFlow 초기화
    ragflow = ExGPTRAGFlowIntegration(
        ragflow_host="http://localhost:8080",
        api_key=os.getenv("RAGFLOW_API_KEY")
    )
    
    # 1. 연결 확인
    print("\n1️⃣ RAGFlow 서버 연결 확인 중...")
    if not ragflow.check_connection():
        print("❌ RAGFlow 서버에 연결할 수 없습니다.")
        print("다음을 확인해주세요:")
        print("  - Docker 서비스가 실행 중인지 확인")
        print("  - 포트 8080이 사용 가능한지 확인")
        print("  - 'docker-compose -f docker-compose-ragflow.yaml up -d' 명령으로 서비스 시작")
        return
    
    print("✅ RAGFlow 서버 연결 성공!")
    
    # 2. 지식베이스 생성
    print("\n2️⃣ 한국도로공사 지식베이스 생성 중...")
    kb_id = ragflow.create_knowledge_base(
        name="한국도로공사_업무매뉴얼",
        description="한국도로공사 업무 처리를 위한 매뉴얼과 가이드라인 모음"
    )
    
    if not kb_id:
        print("❌ 지식베이스 생성 실패")
        return
    
    print(f"✅ 지식베이스 생성 성공! ID: {kb_id}")
    
    # 3. 문서 업로드 (샘플 문서가 있는 경우)
    print("\n3️⃣ 샘플 문서 업로드 시도 중...")
    
    # 업로드할 문서 찾기
    sample_docs = []
    docs_dir = Path("data/uploads")
    if docs_dir.exists():
        for ext in ["*.pdf", "*.docx", "*.txt", "*.md"]:
            sample_docs.extend(docs_dir.glob(ext))
    
    # README.md도 샘플로 추가
    if Path("README.md").exists():
        sample_docs.append(Path("README.md"))
    
    uploaded_docs = []
    for doc_path in sample_docs[:3]:  # 최대 3개 문서만
        print(f"  📄 {doc_path.name} 업로드 중...")
        doc_id = ragflow.upload_document(kb_id, str(doc_path))
        if doc_id:
            uploaded_docs.append(doc_id)
            print(f"    ✅ 업로드 성공: {doc_id}")
        else:
            print(f"    ❌ 업로드 실패")
    
    if not uploaded_docs:
        print("⚠️ 업로드된 문서가 없습니다. 샘플 문서를 data/uploads/ 폴더에 추가해보세요.")
    else:
        print(f"✅ {len(uploaded_docs)}개 문서 업로드 완료")
        
        # 4. 문서 파싱
        print("\n4️⃣ 문서 파싱 시작...")
        if ragflow.parse_document(kb_id, uploaded_docs):
            print("✅ 문서 파싱 시작됨 (백그라운드에서 처리 중)")
            print("  💡 파싱 완료까지 시간이 걸릴 수 있습니다.")
        else:
            print("❌ 문서 파싱 시작 실패")
    
    # 5. 채팅 어시스턴트 생성
    print("\n5️⃣ AI 어시스턴트 생성 중...")
    assistant_id = ragflow.create_chat_assistant(
        name="한국도로공사_업무지원_AI",
        dataset_ids=[kb_id],
        system_prompt="""
당신은 한국도로공사의 업무를 지원하는 전문 AI 어시스턴트입니다.
다음 원칙을 따라 답변해주세요:

1. 정확하고 신뢰할 수 있는 정보만 제공합니다
2. 업무 관련 질문에 구체적이고 실용적인 답변을 제공합니다
3. 불확실한 정보는 명확히 표시하고, 추가 확인을 권장합니다
4. 한국어로 정중하고 전문적인 답변을 제공합니다
5. 제공된 문서와 지식베이스를 우선적으로 참조합니다
        """.strip()
    )
    
    if not assistant_id:
        print("❌ AI 어시스턴트 생성 실패")
        return
    
    print(f"✅ AI 어시스턴트 생성 성공! ID: {assistant_id}")
    
    # 6. 테스트 질문
    print("\n6️⃣ AI 어시스턴트와 대화 테스트...")
    test_questions = [
        "안녕하세요. 업무 지원이 필요합니다.",
        "한국도로공사의 주요 업무는 무엇인가요?",
        "문서 관리 시스템에 대해 설명해주세요."
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n  📝 질문 {i}: {question}")
        
        answer = ragflow.chat_with_assistant(assistant_id, question)
        
        if answer:
            print(f"  🤖 답변: {answer}")
        else:
            print("  ❌ 답변을 받을 수 없습니다")
        
        if i < len(test_questions):
            print("  ⏳ 잠시 대기 중...")
            import time
            time.sleep(2)  # API 호출 간격 조절
    
    # 완료 메시지
    print("\n" + "=" * 50)
    print("🎉 RAGFlow 통합 예제 완료!")
    print("\n📋 생성된 리소스:")
    print(f"  - 지식베이스 ID: {kb_id}")
    print(f"  - AI 어시스턴트 ID: {assistant_id}")
    print(f"  - 업로드된 문서: {len(uploaded_docs)}개")
    
    print("\n💡 다음 단계:")
    print("  1. RAGFlow 웹 인터페이스에서 결과 확인: http://localhost:8080")
    print("  2. 더 많은 문서를 업로드하여 지식베이스 확장")
    print("  3. ex-GPT 메인 애플리케이션에 RAGFlow 통합")
    print("  4. 사용자 인터페이스에서 RAG 기능 활용")


def print_setup_instructions():
    """설정 안내 출력"""
    print("🔧 RAGFlow 설정 안내")
    print("=" * 50)
    print("1. Docker 서비스 시작:")
    print("   docker-compose -f docker-compose-ragflow.yaml up -d")
    print()
    print("2. RAGFlow API 키 설정:")
    print("   - http://localhost:8080 접속")
    print("   - 회원가입/로그인 후 API 키 생성")
    print("   - 환경변수 설정: export RAGFLOW_API_KEY=your_api_key")
    print()
    print("3. 의존성 설치:")
    print("   poetry install")
    print()


if __name__ == "__main__":
    # API 키 확인
    if not os.getenv("RAGFLOW_API_KEY"):
        print("⚠️ RAGFLOW_API_KEY 환경변수가 설정되지 않았습니다.")
        print()
        print_setup_instructions()
        
        # 사용자 입력으로 API 키 받기
        api_key = input("\nRAGFlow API 키를 입력하세요 (Enter로 건너뛰기): ").strip()
        if api_key:
            os.environ["RAGFLOW_API_KEY"] = api_key
        else:
            print("API 키 없이 연결 테스트만 진행합니다.")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        logging.exception("예상치 못한 오류")
    
    print("\n👋 RAGFlow 예제를 실행해주셔서 감사합니다!")
