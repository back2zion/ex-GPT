"""
개인정보 자동 검출 및 마스킹 시스템
한국도로공사 공공기관 보안 가이드라인 준수

Author: DataStreams 보안팀
Date: 2025-06-27
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import hashlib
import json

# 한국어 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/personal_data_security.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PersonalDataDetector:
    """개인정보 검출 및 마스킹 시스템
    
    한국도로공사 요구사항:
    - 개인정보 월별 점검 (휴먼 인 더 루프)
    - 모든 대화 내역 감사 로그 기록
    - 공공기관 보안 가이드라인 준수
    """
    
    def __init__(self):
        # 개인정보 패턴 정의
        self.patterns = {
            # 주민등록번호 (6자리-7자리)
            "resident_number": {
                "pattern": r'\b\d{6}[-\s]?\d{7}\b',
                "mask": "######-#######",
                "risk_level": "HIGH",
                "description": "주민등록번호"
            },
            
            # 휴대폰 번호
            "phone_number": {
                "pattern": r'\b01[0-9][-\s]?\d{3,4}[-\s]?\d{4}\b',
                "mask": "010-****-****",
                "risk_level": "MEDIUM",
                "description": "휴대폰 번호"
            },
            
            # 이메일 주소
            "email": {
                "pattern": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                "mask": "****@****.***",
                "risk_level": "MEDIUM",
                "description": "이메일 주소"
            },
            
            # 신용카드 번호 (4자리씩 4그룹)
            "credit_card": {
                "pattern": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
                "mask": "****-****-****-****",
                "risk_level": "HIGH",
                "description": "신용카드 번호"
            },
            
            # 계좌번호 (은행별 다양한 형태)
            "account_number": {
                "pattern": r'\b\d{3,4}[-\s]?\d{2,6}[-\s]?\d{4,8}\b',
                "mask": "***-***-*****",
                "risk_level": "HIGH",
                "description": "계좌번호"
            },
            
            # 여권번호 (M + 8자리 숫자)
            "passport": {
                "pattern": r'\b[M]\d{8}\b',
                "mask": "M********",
                "risk_level": "HIGH",
                "description": "여권번호"
            },
            
            # 운전면허번호 (지역코드 + 일련번호)
            "license": {
                "pattern": r'\b\d{2}[-\s]?\d{2}[-\s]?\d{6}[-\s]?\d{2}\b',
                "mask": "**-**-******-**",
                "risk_level": "MEDIUM",
                "description": "운전면허번호"
            },
            
            # 사업자등록번호 (3-2-5 형태)
            "business_number": {
                "pattern": r'\b\d{3}[-\s]?\d{2}[-\s]?\d{5}\b',
                "mask": "***-**-*****",
                "risk_level": "MEDIUM",
                "description": "사업자등록번호"
            }
        }
        
        # 검출 통계
        self.detection_stats = {
            "total_scans": 0,
            "total_detections": 0,
            "by_type": {},
            "monthly_report": {}
        }
    
    def scan_text(self, text: str, user_id: Optional[str] = None, 
                  session_id: Optional[str] = None) -> Dict:
        """텍스트에서 개인정보 검출
        
        Args:
            text: 검사할 텍스트
            user_id: 사용자 ID (감사 로그용)
            session_id: 세션 ID (감사 로그용)
            
        Returns:
            검출 결과 딕셔너리
        """
        self.detection_stats["total_scans"] += 1
        
        detections = []
        masked_text = text
        
        for data_type, config in self.patterns.items():
            matches = re.finditer(config["pattern"], text)
            
            for match in matches:
                detection = {
                    "type": data_type,
                    "description": config["description"],
                    "value": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "risk_level": config["risk_level"],
                    "mask": config["mask"]
                }
                
                detections.append(detection)
                
                # 텍스트 마스킹
                masked_text = masked_text.replace(
                    match.group(), 
                    config["mask"], 
                    1
                )
                
                # 통계 업데이트
                self.detection_stats["total_detections"] += 1
                if data_type not in self.detection_stats["by_type"]:
                    self.detection_stats["by_type"][data_type] = 0
                self.detection_stats["by_type"][data_type] += 1
        
        # 검출 결과
        result = {
            "original_text": text,
            "masked_text": masked_text,
            "detections": detections,
            "detection_count": len(detections),
            "has_personal_data": len(detections) > 0,
            "risk_assessment": self._assess_risk(detections),
            "timestamp": datetime.now().isoformat(),
            "scan_id": self._generate_scan_id(text)
        }
        
        # 감사 로그 기록
        if detections:
            self._log_detection(result, user_id, session_id)
        
        return result
    
    def _assess_risk(self, detections: List[Dict]) -> str:
        """위험도 평가"""
        if not detections:
            return "NONE"
        
        high_risk_count = sum(1 for d in detections if d["risk_level"] == "HIGH")
        medium_risk_count = sum(1 for d in detections if d["risk_level"] == "MEDIUM")
        
        if high_risk_count > 0:
            return "HIGH"
        elif medium_risk_count > 2:
            return "HIGH"
        elif medium_risk_count > 0:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _generate_scan_id(self, text: str) -> str:
        """스캔 ID 생성 (해시 기반)"""
        return hashlib.md5(
            f"{text[:50]}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]
    
    def _log_detection(self, result: Dict, user_id: Optional[str], 
                      session_id: Optional[str]):
        """개인정보 검출 감사 로그 기록"""
        log_entry = {
            "timestamp": result["timestamp"],
            "scan_id": result["scan_id"],
            "user_id": user_id,
            "session_id": session_id,
            "detection_count": result["detection_count"],
            "risk_assessment": result["risk_assessment"],
            "detected_types": [d["type"] for d in result["detections"]],
            "text_length": len(result["original_text"]),
            "text_hash": hashlib.sha256(result["original_text"].encode()).hexdigest()
        }
        
        # 보안 로그 파일에 기록
        with open('logs/personal_data_detections.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        
        logger.warning(
            f"개인정보 검출됨 - 사용자: {user_id}, 세션: {session_id}, "
            f"검출수: {result['detection_count']}, 위험도: {result['risk_assessment']}"
        )
    
    def get_monthly_report(self, year: int, month: int) -> Dict:
        """월별 개인정보 검출 보고서 생성
        
        한국도로공사 요구사항: 개인정보 월별 점검
        """
        report_key = f"{year}-{month:02d}"
        
        # 로그 파일에서 해당 월 데이터 추출
        monthly_data = self._extract_monthly_data(year, month)
        
        report = {
            "period": report_key,
            "total_scans": monthly_data.get("total_scans", 0),
            "total_detections": monthly_data.get("total_detections", 0),
            "detection_rate": 0,
            "by_type": monthly_data.get("by_type", {}),
            "by_risk_level": monthly_data.get("by_risk_level", {}),
            "top_users": monthly_data.get("top_users", []),
            "recommendations": self._generate_recommendations(monthly_data),
            "generated_at": datetime.now().isoformat()
        }
        
        if report["total_scans"] > 0:
            report["detection_rate"] = round(
                (report["total_detections"] / report["total_scans"]) * 100, 2
            )
        
        # 월별 보고서 저장
        self.detection_stats["monthly_report"][report_key] = report
        
        return report
    
    def _extract_monthly_data(self, year: int, month: int) -> Dict:
        """로그 파일에서 월별 데이터 추출"""
        monthly_data = {
            "total_scans": 0,
            "total_detections": 0,
            "by_type": {},
            "by_risk_level": {"HIGH": 0, "MEDIUM": 0, "LOW": 0},
            "top_users": []
        }
        
        try:
            with open('logs/personal_data_detections.log', 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        entry_date = datetime.fromisoformat(entry["timestamp"])
                        
                        if entry_date.year == year and entry_date.month == month:
                            monthly_data["total_scans"] += 1
                            monthly_data["total_detections"] += entry["detection_count"]
                            
                            # 타입별 통계
                            for detected_type in entry["detected_types"]:
                                if detected_type not in monthly_data["by_type"]:
                                    monthly_data["by_type"][detected_type] = 0
                                monthly_data["by_type"][detected_type] += 1
                            
                            # 위험도별 통계
                            risk_level = entry["risk_assessment"]
                            if risk_level in monthly_data["by_risk_level"]:
                                monthly_data["by_risk_level"][risk_level] += 1
                                
                    except (json.JSONDecodeError, KeyError):
                        continue
                        
        except FileNotFoundError:
            logger.warning("개인정보 검출 로그 파일을 찾을 수 없습니다.")
        
        return monthly_data
    
    def _generate_recommendations(self, monthly_data: Dict) -> List[str]:
        """월별 보고서 기반 권장사항 생성"""
        recommendations = []
        
        total_detections = monthly_data.get("total_detections", 0)
        
        if total_detections == 0:
            recommendations.append("✅ 이번 달 개인정보 검출 사례가 없어 양호한 상태입니다.")
        else:
            recommendations.append(f"⚠️ 이번 달 총 {total_detections}건의 개인정보가 검출되었습니다.")
            
            # 고위험 검출이 많은 경우
            high_risk = monthly_data.get("by_risk_level", {}).get("HIGH", 0)
            if high_risk > 10:
                recommendations.append("🚨 고위험 개인정보 검출이 빈번합니다. 직원 교육을 강화하세요.")
            
            # 특정 타입이 많이 검출되는 경우
            by_type = monthly_data.get("by_type", {})
            if by_type:
                most_detected = max(by_type.items(), key=lambda x: x[1])
                recommendations.append(
                    f"📊 가장 많이 검출된 개인정보 유형: {most_detected[0]} ({most_detected[1]}건)"
                )
        
        recommendations.append("💡 정기적인 개인정보 보호 교육을 실시하세요.")
        recommendations.append("🔒 민감한 정보는 별도의 보안 채널을 이용하세요.")
        
        return recommendations
    
    def get_statistics(self) -> Dict:
        """전체 통계 반환"""
        return {
            "current_stats": self.detection_stats,
            "supported_types": list(self.patterns.keys()),
            "pattern_count": len(self.patterns)
        }

# 전역 개인정보 검출기 인스턴스
personal_data_detector = PersonalDataDetector()

# 사용 예시
if __name__ == "__main__":
    # 테스트 텍스트 (개인정보 포함)
    test_text = """
    안녕하세요. 제 연락처는 010-1234-5678이고, 
    이메일은 test@korea-expressway.co.kr입니다.
    주민등록번호는 123456-1234567입니다.
    """
    
    # 개인정보 검출 테스트
    result = personal_data_detector.scan_text(
        test_text, 
        user_id="test_user", 
        session_id="test_session"
    )
    
    print("검출 결과:")
    print(f"원본: {result['original_text']}")
    print(f"마스킹: {result['masked_text']}")
    print(f"검출 개수: {result['detection_count']}")
    print(f"위험도: {result['risk_assessment']}")
