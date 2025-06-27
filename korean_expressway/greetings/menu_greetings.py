"""
한국도로공사 메뉴별 차별화 인사말 시스템
ex-GPT 전용 인사말 관리

Author: DataStreams 시스템통합팀
Date: 2025-06-27
"""

from typing import Dict, Optional
from datetime import datetime
import random

class KoreanExpresswayGreetings:
    """한국도로공사 메뉴별 인사말 관리자
    
    clinerules 요구사항:
    - 법령규정: "한국도로공사, 법령규정 정보를..."
    - 국정자료: "한국도로공사, 국정감사 정보를..."
    - 메뉴별 차별화된 인사말
    """
    
    def __init__(self):
        self.greetings = {
            # 법령규정 메뉴
            "law_regulation": {
                "primary": "한국도로공사, 법령규정 정보를 도와드리겠습니다.",
                "variations": [
                    "안녕하세요! 한국도로공사 법령규정 전문 AI 어시스턴트입니다.",
                    "한국도로공사 법령규정 검색 서비스에 오신 것을 환영합니다.",
                    "법령규정 관련 궁금한 사항이 있으시면 언제든 문의해주세요.",
                    "도로 관련 법령 및 규정 정보를 정확하게 안내해드리겠습니다."
                ],
                "context": "도로법, 고속도로법, 건설기준, 안전규정 등 법령규정 전문 검색"
            },
            
            # 국정감사 자료
            "national_audit": {
                "primary": "한국도로공사, 국정감사 정보를 도와드리겠습니다.",
                "variations": [
                    "안녕하세요! 국정감사 자료 전문 검색 서비스입니다.",
                    "한국도로공사 국정감사 관련 자료를 신속하게 찾아드리겠습니다.",
                    "국정감사 대응 자료가 필요하시면 언제든 말씀해주세요.",
                    "투명하고 정확한 국정감사 정보를 제공해드리겠습니다."
                ],
                "context": "국정감사 대응자료, 경영공시, 주요 정책자료 검색"
            },
            
            # 기술교육 평가
            "technical_education": {
                "primary": "한국도로공사 기술교육 및 평가 시스템입니다.",
                "variations": [
                    "기술교육 관련 자료와 평가 기준을 안내해드리겠습니다.",
                    "도로 건설 및 유지관리 기술교육 전문 서비스입니다.",
                    "기술 역량 향상을 위한 교육자료를 제공해드리겠습니다.",
                    "전문 기술교육과 평가 시스템에 오신 것을 환영합니다."
                ],
                "context": "기술교육 자료, 평가 기준, 역량 개발 프로그램"
            },
            
            # 위험성 평가
            "risk_assessment": {
                "primary": "한국도로공사 위험성 평가 전문 시스템입니다.",
                "variations": [
                    "공정별 위험성 평가 표준을 안내해드리겠습니다.",
                    "안전한 도로 건설을 위한 위험성 평가 서비스입니다.",
                    "건설 현장 안전관리 및 위험성 평가 전문 AI입니다.",
                    "체계적인 위험성 평가로 안전한 작업환경을 만들어가겠습니다."
                ],
                "context": "건설 공정별 위험성 평가, 안전관리 기준, 사고 예방"
            },
            
            # 회의록 작성
            "meeting_minutes": {
                "primary": "한국도로공사 회의록 자동 생성 서비스입니다.",
                "variations": [
                    "음성 인식을 통한 회의록 자동 작성을 도와드리겠습니다.",
                    "효율적인 회의 관리와 기록을 지원해드리겠습니다.",
                    "STT 기반 회의록 생성 전문 시스템입니다.",
                    "정확하고 체계적인 회의록 작성을 도와드리겠습니다."
                ],
                "context": "음성 인식, 회의록 자동 생성, 요약 및 정리"
            },
            
            # 문서 비교 분석
            "document_analysis": {
                "primary": "한국도로공사 문서 비교 및 분석 서비스입니다.",
                "variations": [
                    "문서 간 차이점 분석과 비교를 도와드리겠습니다.",
                    "정확한 문서 분석으로 업무 효율성을 높여드리겠습니다.",
                    "HWP, PDF 등 다양한 문서 형식을 지원합니다.",
                    "문서 버전 관리와 변경사항 추적을 도와드리겠습니다."
                ],
                "context": "문서 비교, 변경사항 추적, 버전 관리, 다국어 지원"
            },
            
            # 일반 채팅
            "general_chat": {
                "primary": "안녕하세요! 한국도로공사 AI 어시스턴트 ex-GPT입니다.",
                "variations": [
                    "한국도로공사 직원 여러분, 무엇을 도와드릴까요?",
                    "도로 전문 AI 어시스턴트가 업무를 지원해드리겠습니다.",
                    "한국도로공사 업무 지원 AI 시스템에 오신 것을 환영합니다.",
                    "효율적인 업무 처리를 위해 최선을 다해 도와드리겠습니다."
                ],
                "context": "일반 업무 지원, 정보 검색, 업무 효율성 향상"
            }
        }
        
        # 시간대별 인사말 추가
        self.time_greetings = {
            "morning": ["좋은 아침입니다!", "상쾌한 아침이네요!", "새로운 하루를 시작해보세요!"],
            "afternoon": ["좋은 오후입니다!", "오후 업무도 화이팅하세요!", "점심 식사는 맛있게 하셨나요?"],
            "evening": ["수고 많으셨습니다!", "오늘 하루도 고생하셨어요!", "편안한 저녁 되세요!"]
        }
    
    def get_greeting(self, menu_type: str, user_name: Optional[str] = None, 
                    department: Optional[str] = None, use_variation: bool = True) -> Dict[str, str]:
        """메뉴별 인사말 생성
        
        Args:
            menu_type: 메뉴 타입 (law_regulation, national_audit 등)
            user_name: 사용자 이름 (선택)
            department: 부서명 (선택)
            use_variation: 다양한 인사말 사용 여부
            
        Returns:
            인사말 정보 딕셔너리
        """
        if menu_type not in self.greetings:
            menu_type = "general_chat"
        
        greeting_data = self.greetings[menu_type]
        
        # 기본 인사말 또는 변형 인사말 선택
        if use_variation and greeting_data["variations"]:
            greeting = random.choice(greeting_data["variations"])
        else:
            greeting = greeting_data["primary"]
        
        # 시간대별 인사말 추가
        time_greeting = self._get_time_greeting()
        
        # 개인화 인사말 (사용자명, 부서명 포함)
        personalized_greeting = self._personalize_greeting(greeting, user_name, department)
        
        return {
            "main_greeting": personalized_greeting,
            "time_greeting": time_greeting,
            "context": greeting_data["context"],
            "menu_type": menu_type,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _get_time_greeting(self) -> str:
        """시간대별 인사말 반환"""
        current_hour = datetime.now().hour
        
        if 6 <= current_hour < 12:
            return random.choice(self.time_greetings["morning"])
        elif 12 <= current_hour < 18:
            return random.choice(self.time_greetings["afternoon"])
        else:
            return random.choice(self.time_greetings["evening"])
    
    def _personalize_greeting(self, greeting: str, user_name: Optional[str], 
                            department: Optional[str]) -> str:
        """개인화된 인사말 생성"""
        if user_name and department:
            return f"{department} {user_name}님, {greeting}"
        elif user_name:
            return f"{user_name}님, {greeting}"
        elif department:
            return f"{department} 담당자님, {greeting}"
        else:
            return greeting
    
    def get_menu_list(self) -> Dict[str, str]:
        """사용 가능한 메뉴 목록 반환"""
        return {
            menu_type: data["context"] 
            for menu_type, data in self.greetings.items()
        }
    
    def add_custom_greeting(self, menu_type: str, primary: str, 
                          variations: list, context: str):
        """사용자 정의 인사말 추가"""
        self.greetings[menu_type] = {
            "primary": primary,
            "variations": variations,
            "context": context
        }

# 전역 인사말 관리자 인스턴스
greeting_manager = KoreanExpresswayGreetings()

# 사용 예시
if __name__ == "__main__":
    # 법령규정 메뉴 인사말
    law_greeting = greeting_manager.get_greeting(
        "law_regulation", 
        user_name="김철수", 
        department="법무팀"
    )
    print(f"법령규정: {law_greeting}")
    
    # 국정감사 메뉴 인사말
    audit_greeting = greeting_manager.get_greeting(
        "national_audit",
        user_name="이영희",
        department="기획조정실"
    )
    print(f"국정감사: {audit_greeting}")
