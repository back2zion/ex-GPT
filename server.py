#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import warnings
warnings.filterwarnings("ignore", message="pkg_resources is deprecated")

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import json
import logging
import time
from datetime import datetime
import os
import re

# ============= 로깅 설정 =============
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============= Flask 앱 및 CORS 설정 =============
app = Flask(__name__)
CORS(app)

# RAG API 설정 (Docker 네트워크 기반)
NEOALI_API_URL = "http://localhost:8081/v1/chat/"

# 통계 데이터
stats_data = {
    'total_requests': 0,
    'successful_requests': 0,
    'failed_requests': 0,
    'active_users': set(),
}

# 대화 이력 저장 (세션별)
conversation_history = {}

# 동적 패턴 학습 데이터
pattern_learning_data = {
    'misrouted_queries': [],
    'user_feedback': [],
    'pattern_performance': {},
    'last_update': datetime.now()
}

# 패턴 컴파일 캐시 (성능 최적화)
compiled_patterns_cache = {}

def determine_routing_path(message, mode):
    """우선순위 기반 지능형 질의 라우팅 시스템"""
    
    # 1. 최고 우선순위: 즉시 차단 패턴 (보안/개인정보)
    security_patterns = [
        r'(비밀번호|패스워드|개인정보|주민번호|신용카드|계좌번호)',
        r'(해킹|크랙|불법|위조|변조)'
    ]
    
    # 2. 고우선순위: 한국도로공사 핵심 업무 (가중치 5)
    high_priority_rag_patterns = [
        r'(통행료|부가통행료|기본요금|주행요금|거리비례|요금체계)',
        r'(할인|감면|면제|정기권|회수권|심야할인|경차할인)',
        r'(한국도로공사|도로공사|도공|KEC)',
        r'(규정|지침|매뉴얼|절차|기준|표준|방침)',
        r'(하이패스|Hi-pass|전자결제|선불|후불)'
    ]
    
    # 3. 중우선순위: 도로 시설/운영 (가중치 3)
    medium_priority_rag_patterns = [
        r'(고속도로|고속국도|자동차전용도로|톨게이트|요금소)',
        r'(나들목|인터체인지|IC|분기점|정션|JC)',
        r'(휴게소|졸음쉼터|만남의광장|주차장)',
        r'(터널|교량|고가|지하차도|육교)',
        r'(교통정보|소통상황|정체|지체|우회도로)'
    ]
    
    # 4. 저우선순위: 일반 대화 (가중치 1)
    direct_llm_patterns = [
        r'^(안녕|하이|헬로|hi|hello)',
        r'^(감사|고마워|수고)',
        r'^(네|예|아니|그래|맞아)',
        r'^\d+\s*[+\-*/]\s*\d+\s*=?',  # 단순 계산
        r'(날씨|기온|온도|비|눈|바람)',
        r'(음식|요리|맛집|식당)',
        r'(영화|드라마|음악|게임)',
        r'(스포츠|축구|야구|농구)'
    ]
    
    # 2. 한국도로공사 전문용어 RAG 검색 패턴 (대폭 확장)
    rag_search_patterns = [
        # 기본 도로공사 관련
        r'한국도로공사|도로공사|도공|KEC|Korea\s*Expressway',
        
        # 고속도로 시설 및 구조물
        r'고속도로|고속국도|자동차전용도로|톨게이트|요금소|하이패스|Hi-pass',
        r'나들목|인터체인지|IC|분기점|정션|JC|교차로|램프',
        r'휴게소|졸음쉼터|만남의광장|주차장|화물차휴게소|LPG충전소',
        r'터널|교량|고가|지하차도|육교|과선교|건널목',
        r'차로|주행차로|추월차로|갓길|중앙분리대|방음벽|가드레일',
        
        # 통행료 및 요금 체계
        r'통행료|부가통행료|기본요금|주행요금|거리비례|요금체계',
        r'할인|감면|면제|정기권|회수권|심야할인|경차할인|이용빈도할인',
        r'하이패스카드|교통카드|전자결제|선불|후불|충전',
        r'통행료수입|요금징수|미납|체납|환불|정산',
        r'요금표|요금산정|할인율|경로별요금',
        
        # 교통 운영 및 관리
        r'교통정보|소통상황|정체|지체|우회도로|통제',
        r'VMS|전광판|CCTV|ITS|하이패스시스템|ETC',
        r'교통량|교통흐름|통행속도|혼잡도|LOS',
        r'사고|돌발상황|응급상황|견인|구난|제설|제빙',
        r'도로순찰|점검|정비|보수|교체|개량|확장',
        
        # 조직 및 부서
        r'본부|사업본부|건설사업본부|운영사업본부|디지털혁신본부',
        r'처|실|부|팀|센터|사무소|지사|관리소|사업단',
        r'인력처|재무처|기획처|디지털계획처|AI데이터부|운영부',
        
        # 업무 프로세스 및 규정
        r'규정|지침|매뉴얼|절차|기준|표준|방침|지시|공지',
        r'법령|시행령|시행규칙|조례|내규|업무규정|관리규정',
        r'승인|결재|신청|허가|인가|등록|신고|보고',
        r'인장|도장|서명|날인|직인|계약서|협정서|합의서',
        
        # 인사 및 급여
        r'인사|발령|전보|승진|채용|퇴직|휴직|복직',
        r'급여|수당|상여|성과급|복리후생|퇴직금|연금',
        r'근무|출근|퇴근|연가|병가|휴가|특별휴가|육아휴직',
        r'교육|연수|훈련|워크숍|세미나|컨퍼런스|자격증',
        
        # 재무 및 회계
        r'예산|결산|회계|자금|투자|융자|대출|보증',
        r'법인카드|출장비|여비|교통비|숙박비|식비|일비',
        r'경비|비용|지출|수입|매출|손익|자산|부채',
        r'조달|구매|입찰|계약|검수|검사|납품|대금지급',
        
        # 건설 및 공사
        r'건설|신설|확장|개량|보강|정비|유지관리',
        r'공사|공정|공종|시공|준공|준공검사|준공도서',
        r'설계|감리|감독|검측|품질관리|안전관리',
        
        # 안전 및 환경
        r'안전|사고|재해|위험|점검|진단|평가|대책',
        r'안전교육|안전점검|안전관리|안전시설|안전장비',
        r'환경|친환경|녹색|탄소|배출|소음|진동|대기질',
        
        # 시간 및 날짜 관련
        r'2024년|2025년|2023년|올해|작년|내년|금년|년도',
        r'월|일|시|분|기간|기한|마감|연장|단축',
        r'평일|주말|공휴일|휴일|근무시간|업무시간',
        
        # 수치 및 통계
        r'몇|얼마|수치|비율|퍼센트|개수|명수|대수',
        r'통계|분석|현황|실적|성과|지표|목표|달성',
        r'원|억|천만|백만|만|천|백|십',
        r'km|m|cm|톤|kg|대|개|명|건|회|차례',
        
        # 위치 및 지역
        r'어디|위치|장소|지역|구간|노선|구간별',
        r'서울|부산|대구|인천|광주|대전|울산|세종',
        r'경기|강원|충북|충남|전북|전남|경북|경남|제주',
        
        # 차량 및 운송
        r'차량|자동차|승용차|화물차|버스|오토바이|이륜차',
        r'경차|소형차|중형차|대형차|특수차|건설기계',
        r'전기차|하이브리드|수소차|친환경차|무공해차'
    ]
    
    # 3. query_expansion 경로 패턴
    expansion_patterns = [
        r'^(그거|이거|저거|그것|이것|저것)\s*(뭐|어떻게|언제)',
        r'(출처|어디서|어떻게)\s*(확인|찾|알)',
        r'(더|좀더|자세히|구체적으로)\s*(알고|설명|설명해)',
        r'(관련|대한|에\s*대해)\s*(내용|정보|자료)',
        r'^(뭐|뭔가|무엇|어떤)\s*(있|하|됨)',
        r'^(네|예|아니|그럼)\s*',
        r'^[가-힣]{1,3}$'  # 매우 짧은 한글
    ]
    
    # 4. mcp_action 경로 패턴
    mcp_action_patterns = [
        r'파일|업로드|첨부|다운로드|저장',
        r'음성|녹음|변환|텍스트|변경',
        r'회의|회의록|요약|정리|기록',
        r'번역|영어|중국어|일본어|translate',
        r'비교|대조|분석|검토|평가',
        r'이미지|사진|그림|도표|차트'
    ]
    
    import re
    
    message_lower = message.lower()
    
    # 1단계: 보안 패턴 우선 검사
    for pattern in security_patterns:
        if re.search(pattern, message_lower):
            return {
                'path': 'direct_llm',
                'confidence': 'high', 
                'reasoning': '보안/개인정보 관련 질의는 답변 불가',
                'scores': {'security': 1}
            }
    
    # 2단계: 우선순위별 가중치 점수 계산
    scores = {
        'direct_llm': 0,
        'rag_search': 0, 
        'query_expansion': 0,
        'mcp_action': 0
    }
    
    # 고우선순위 패턴 검사 (가중치 5)
    for pattern in high_priority_rag_patterns:
        if re.search(pattern, message_lower):
            scores['rag_search'] += 5
            
    # 중우선순위 패턴 검사 (가중치 3)  
    for pattern in medium_priority_rag_patterns:
        if re.search(pattern, message_lower):
            scores['rag_search'] += 3
            
    # 저우선순위 일반 대화 패턴 (가중치 1)
    for pattern in direct_llm_patterns:
        if re.search(pattern, message_lower):
            scores['direct_llm'] += 1
    
    # 복합 질의 처리: "하이패스 할인 규정" 같은 경우
    question_indicators = ['어떻게', '언제', '어디서', '얼마', '몇', '알려줘', '찾아줘', '확인']
    for indicator in question_indicators:
        if indicator in message:
            scores['rag_search'] += 2  # 질문 형태면 문서 검색 우선
            break
    
    # 모드별 가중치 적용
    if mode == 'search':
        scores['rag_search'] += 3
    
    # 메시지 길이 기반 조정
    if len(message) < 5:
        scores['query_expansion'] += 1
    elif len(message) > 30:
        scores['rag_search'] += 1
    
    # 최고 점수 경로 선택
    best_path = max(scores, key=scores.get)
    max_score = scores[best_path]
    
    # 신뢰도 계산 (우선순위 기반)
    if max_score >= 5:
        confidence = 'high'
    elif max_score >= 3:
        confidence = 'medium'
    elif max_score >= 1:
        confidence = 'low'
    else:
        # 기본값: 한국도로공사 AI이므로 RAG 우선
        best_path = 'rag_search'
        confidence = 'medium'
    
    # 추론 이유 생성
    reasoning_map = {
        'direct_llm': '일반 지식/인사 질의',
        'rag_search': '도로공사 문서 검색',
        'query_expansion': '질의 확장 필요',
        'mcp_action': '특수 기능 요청'
    }
    
    # 패턴 성능 추적
    pattern_key = f"{best_path}_{confidence}"
    if pattern_key not in pattern_learning_data['pattern_performance']:
        pattern_learning_data['pattern_performance'][pattern_key] = {'count': 0, 'success': 0}
    pattern_learning_data['pattern_performance'][pattern_key]['count'] += 1
    
    return {
        'path': best_path,
        'confidence': confidence,
        'reasoning': reasoning_map[best_path],
        'scores': scores,
        'pattern_key': pattern_key
    }

def expand_query(message):
    """질의 확장 함수"""
    
    # 모호한 질의를 구체적으로 확장
    expansion_rules = {
        r'^그거|저거|이거': '앞서 언급한 내용과 관련하여 한국도로공사의',
        r'^더|추가': message + ' 에 대한 상세한 정보와 관련 규정',
        r'^출처': message.replace('출처', '') + ' 에 대한 근거 문서와 출처',
        r'관련': message + ' 와 연관된 모든 정보',
        r'^왜|이유': message + ' 의 배경과 이유 및 관련 정책'
    }
    
    import re
    for pattern, expansion in expansion_rules.items():
        if re.search(pattern, message):
            return expansion
    
    # 기본 확장: 한국도로공사 맥락 추가
    return f"한국도로공사와 관련된 {message} 에 대한 정보"

def update_pattern_performance(pattern_key, success=True):
    """패턴 성능 업데이트"""
    if pattern_key in pattern_learning_data['pattern_performance']:
        if success:
            pattern_learning_data['pattern_performance'][pattern_key]['success'] += 1

def collect_misrouted_query(query, expected_path, actual_path):
    """잘못 라우팅된 질의 수집"""
    misrouted_data = {
        'query': query,
        'expected': expected_path,
        'actual': actual_path,
        'timestamp': datetime.now()
    }
    pattern_learning_data['misrouted_queries'].append(misrouted_data)
    
    # 최근 100개만 유지
    if len(pattern_learning_data['misrouted_queries']) > 100:
        pattern_learning_data['misrouted_queries'] = pattern_learning_data['misrouted_queries'][-100:]

def suggest_new_patterns():
    """새로운 패턴 제안 함수"""
    suggestions = []
    
    # 자주 잘못 라우팅되는 키워드 분석
    misrouted_queries = pattern_learning_data['misrouted_queries']
    if len(misrouted_queries) < 5:
        return suggestions
    
    # 공통 키워드 추출
    from collections import Counter
    all_words = []
    for item in misrouted_queries[-20:]:  # 최근 20개 분석
        words = item['query'].split()
        all_words.extend([w for w in words if len(w) >= 2])
    
    common_words = Counter(all_words).most_common(10)
    
    for word, count in common_words:
        if count >= 3:  # 3번 이상 등장한 단어
            suggestions.append({
                'pattern': f'({word})',
                'frequency': count,
                'suggested_path': 'rag_search',
                'reason': f'자주 등장하는 키워드: {word} ({count}회)'
            })
    
    return suggestions

def auto_update_patterns():
    """자동 패턴 업데이트 (주기적 실행)"""
    global pattern_learning_data
    
    # 1주일마다 패턴 업데이트
    time_diff = datetime.now() - pattern_learning_data['last_update']
    if time_diff.days < 7:
        return False
    
    suggestions = suggest_new_patterns()
    
    # 성능이 좋은 제안만 자동 적용
    for suggestion in suggestions:
        if suggestion['frequency'] >= 5:  # 5회 이상 등장시 자동 적용
            logger.info(f"🔄 새로운 패턴 자동 추가: {suggestion['pattern']}")
            # 실제 패턴 리스트에 추가 (여기서는 로그만)
    
    pattern_learning_data['last_update'] = datetime.now()
    return True

def expand_query_with_context(message, context):
    """맥락을 고려한 질의 확장 함수"""
    
    # 이전 대화에서 키워드 추출
    keywords = context.get('previous_topic', [])
    recent_messages = context.get('recent_messages', [])
    
    import re
    
    # 참조 표현 처리
    if re.search(r'^그거|저거|이거|그것|이것', message):
        if keywords:
            main_topic = ' '.join(keywords[:3])  # 주요 키워드 3개
            return f"{main_topic}과 관련하여 {message.replace('그거', '').replace('저거', '').replace('이거', '').strip()}"
        elif recent_messages:
            return f"앞서 언급한 '{recent_messages[-1][:20]}...'과 관련하여 추가 정보"
    
    # "더", "추가" 등의 확장 요청
    if re.search(r'^더|추가|자세히', message):
        if keywords:
            main_topic = ' '.join(keywords[:2])
            return f"{main_topic}에 대한 상세한 정보와 관련 규정 및 절차"
    
    # "왜", "이유" 등의 배경 질문
    if re.search(r'^왜|이유|배경', message):
        if keywords:
            main_topic = ' '.join(keywords[:2])
            return f"{main_topic}의 배경과 이유, 관련 정책 및 법적 근거"
    
    # 기본 맥락 확장
    if keywords:
        context_str = ' '.join(keywords[:3])
        return f"{context_str}와 관련된 {message} 에 대한 정보"
    
    return expand_query(message)

def get_conversation_history(session_id, max_turns=10):
    """대화 이력 조회"""
    if session_id not in conversation_history:
        conversation_history[session_id] = []
    
    # 최근 max_turns만 반환
    return conversation_history[session_id][-max_turns:]

def filter_chinese_characters(text):
    """중국어 문자 필터링 함수"""
    chinese_chars = [
        "如", "您", "等", "会", "网站", "或", "移动", "应用", "客服", "可以", "直接", "查询", 
        "最新", "信息", "我们", "提供", "多少", "费用", "需要", "政策", "因为", "可能", "根据", 
        "地区", "具体", "情况", "不同", "建议", "通过", "官方", "进行", "联系", "获取", "准确",
        "ไม", "包括", "任何", "禁止", "的", "语言", "字符", "不是", "讨论", "内容", "请", "继续",
        "使用", "交流", "将", "按照", "要求", "帮助", "今天", "想", "了解", "哪些", "关于",
        "日常", "感谢", "流程", "呢", "针对", "特定", "场合", "详细", "治疗", "理解", "集行",
        "主管", "部门", "指定", "管理者", "影响", "严格", "귀", "ırım", "해결", "안되고", "있음",
        "hoặc", "관련", "운영", "상황", "연관", "가장", "정확한", "얻기", "확인"
    ]
    
    filtered_text = text
    found_chinese = []
    
    for char in chinese_chars:
        if char in filtered_text:
            found_chinese.append(char)
            filtered_text = filtered_text.replace(char, "")
    
    if found_chinese:
        logger.warning(f"중국어/외국어 문자 감지 및 제거: {found_chinese}")
        
        # 의미가 심하게 깨진 문장이면 한국어 기본 응답으로 대체
        if len(filtered_text.strip()) < len(text.strip()) * 0.6:  # 40% 이상 제거되었으면
            return "죄송합니다. 해당 질문에 대한 정확한 답변을 위해 한국도로공사 고객센터(1588-2504)로 문의해주세요."
    
    return filtered_text.strip()

def add_to_conversation_history(session_id, user_message, assistant_message):
    """대화 이력에 추가 (중국어 필터링 포함)"""
    if session_id not in conversation_history:
        conversation_history[session_id] = []
    
    # 응답에서 중국어/외국어 필터링
    cleaned_response = filter_chinese_characters(assistant_message)
    
    conversation_history[session_id].append({
        'role': 'user',
        'content': user_message,
        'timestamp': datetime.now().isoformat()
    })
    
    conversation_history[session_id].append({
        'role': 'assistant', 
        'content': cleaned_response,
        'timestamp': datetime.now().isoformat()
    })
    
    # 최대 20턴(40개 메시지)까지만 유지
    if len(conversation_history[session_id]) > 40:
        conversation_history[session_id] = conversation_history[session_id][-40:]
    
    return cleaned_response

def analyze_conversation_context(session_id, current_message):
    """대화 맥락 분석"""
    history = get_conversation_history(session_id)
    
    if not history:
        return {
            'has_context': False,
            'previous_topic': None,
            'needs_expansion': False
        }
    
    # 최근 메시지들 분석
    recent_messages = [msg['content'] for msg in history[-4:]]
    context_keywords = []
    
    for msg in recent_messages:
        # 키워드 추출 (간단한 방식)
        words = msg.split()
        context_keywords.extend([word for word in words if len(word) > 2])
    
    # 현재 메시지가 맥락 참조인지 확인
    reference_patterns = [r'^그거|저거|이거|그것|이것', r'^더|추가', r'^왜|이유', r'^어떻게']
    needs_expansion = any(re.search(pattern, current_message) for pattern in reference_patterns)
    
    return {
        'has_context': len(history) > 0,
        'previous_topic': context_keywords[-5:] if context_keywords else None,
        'needs_expansion': needs_expansion,
        'recent_messages': recent_messages[-2:] if recent_messages else []
    }

def log_request(request_type, user_id, action, status, processing_time):
    """요청 로그 기록"""
    stats_data['total_requests'] += 1
    if status == 'success':
        stats_data['successful_requests'] += 1
    else:
        stats_data['failed_requests'] += 1
    
    logger.info(f"{request_type} - {user_id} - {action} - {status} - {processing_time}")

# =============================================================================
# 라우트 정의
# =============================================================================

@app.route('/')
def index():
    """메인 페이지 - 업데이트된 UI 제공"""
    try:
        return send_from_directory('.', 'index.html')
    except Exception as e:
        logger.error(f"메인 페이지 오류: {str(e)}")
        return f"<h1>ex-GPT 서버</h1><p>index.html 파일을 찾을 수 없습니다: {str(e)}</p>", 500

@app.route('/api/chat', methods=['POST'])
def chat_proxy():
    """RAG RAG API로 프록시하는 채팅 엔드포인트"""
    start_time = time.time()
    
    try:
        # 요청 데이터 파싱 시도
        try:
            data = request.get_json(force=True)
        except Exception as json_error:
            logger.error(f"JSON 파싱 오류: {str(json_error)}")
            try:
                # raw data로 시도
                raw_data = request.get_data(as_text=True)
                logger.info(f"Raw 요청 데이터: {raw_data}")
                data = json.loads(raw_data)
            except Exception as raw_error:
                logger.error(f"Raw 데이터 파싱 오류: {str(raw_error)}")
                return jsonify({'error': f'요청 데이터 파싱 실패: {str(json_error)}'}), 400
        
        if not data:
            return jsonify({'error': '요청 데이터가 없습니다.'}), 400
        
        # 요청 모드 및 세션 정보 확인
        message = data.get('message', '')
        mode = data.get('mode', 'general')
        force_rag = data.get('force_rag', False)
        session_id = data.get('session_id', request.remote_addr)  # 세션 ID (기본값: IP)
        
        # 대화 맥락 분석
        context = analyze_conversation_context(session_id, message)
        logger.info(f"🔍 대화 맥락: {context}")
        
        # 맥락 기반 라우팅 결정
        routing_result = determine_routing_path(message, mode)
        route_path = routing_result['path']
        confidence = routing_result['confidence']
        reasoning = routing_result['reasoning']
        
        # 맥락이 있는 경우 query_expansion 우선 고려
        if context['needs_expansion'] and context['has_context']:
            route_path = 'query_expansion'
            confidence = 'high'
            reasoning = '대화 맥락 참조 질의'
            logger.info(f"🔄 맥락 기반 라우팅 조정: query_expansion")
        
        logger.info(f"📍 최종 라우팅 결정: {route_path} (신뢰도: {confidence}, 이유: {reasoning})")
        
        # 대화 이력 구성
        history = get_conversation_history(session_id)
        
        # 라우팅 경로별 처리
        if route_path == 'rag_search':
            # RAG 검색 경로 - 대화 이력 포함
            full_history = history + [{
                "role": "user",
                "content": message
            }]
            neoali_payload = {
                "history": full_history,
                "stream": False,
                "search_documents": True,
                "return_documents": True,
                "include_default_system_prompt": True
            }
            use_rag = True
        elif route_path == 'query_expansion':
            # 질의 확장 경로 - 맥락을 고려한 확장
            if context['has_context']:
                expanded_query = expand_query_with_context(message, context)
            else:
                expanded_query = expand_query(message)
            
            full_history = history + [{
                "role": "user",
                "content": expanded_query
            }]
            neoali_payload = {
                "history": full_history,
                "stream": False,
                "search_documents": True,
                "return_documents": True,
                "include_default_system_prompt": True
            }
            use_rag = True
        elif route_path == 'mcp_action':
            # 특수 기능 경로 - 현재는 일반 LLM으로 처리하고 향후 확장
            neoali_payload = None
            use_rag = False
        else:
            # direct_llm 경로 - 대화 이력 포함
            neoali_payload = None
            use_rag = False
        
        user_id = data.get('user_id', request.remote_addr)
        stats_data['active_users'].add(user_id)
        
        if use_rag and neoali_payload:
            logger.info(f"💬 채팅 요청 -> RAG RAG API (한국도로공사 문서 검색)")
            
            # RAG RAG API 호출 시도
            try:
                response = requests.post(
                    NEOALI_API_URL,
                    json=neoali_payload,
                    headers={
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    timeout=30
                )
            except requests.exceptions.ConnectionError:
                # RAG API 연결 실패시 직접 vLLM 호출
                logger.warning("RAG API 연결 실패, vLLM 직접 호출로 전환")
                use_rag = False
        
        if not use_rag:
            logger.info(f"💬 일반 대화 요청 -> vLLM 직접 호출")
            
            # 대화 이력을 vLLM 형식으로 변환
            system_prompt = """You are ex-GPT, an AI assistant for Korea Expressway Corporation (한국도로공사).

## Core Identity
- Role: Professional Korean expressway expert assistant
- Organization: Korea Expressway Corporation (KEC)
- Language: ALWAYS respond in Korean only

## Language Policy (CRITICAL)
```python
ALLOWED_LANGUAGES = ["korean"]
FORBIDDEN_LANGUAGES = ["chinese", "english", "japanese"]
FORBIDDEN_CHARS = ["如", "您", "等", "会", "网站", "或", "移动", "应用", "客服", "可以", "直接", "查询", "最新", "信息", "我们", "提供", "多少", "费用", "需要", "政策", "因为", "可能", "根据", "地区", "具体", "情况", "不同", "建议", "通过", "官方", "进行", "联系", "获取", "准确"]

def validate_response(text):
    return not any(char in text for char in FORBIDDEN_CHARS)
```

## Memory & Context
- Remember user names and conversation history
- When asked about names, recall accurately
- Maintain conversation context across turns

## Response Templates (Markdown Format)
```python
GREETING_TEMPLATE = "## 안녕하세요, **{name}님**! 👋\n\n한국도로공사 `ex-GPT`입니다."
HELP_TEMPLATE = "> 💡 **도움말**: 한국도로공사 관련 문의사항이 있으시면 언제든 말씀해주세요."
PROCEDURE_TEMPLATE = "## {title}\\n\\n### 📋 절차 개요\\n{overview}\\n\\n### 📝 단계별 안내\\n{steps}\\n\\n### ⚠️ 주의사항\\n{notes}"
```

## Output Rules
1. ONLY Korean language in responses
2. NO Chinese/English/Japanese characters
3. ALWAYS use Markdown formatting - THIS IS MANDATORY:
   - **Bold** for important points and emphasis
   - ## Headers for sections and topics
   - ### Sub-headers for detailed breakdown
   - - Lists for multiple items and procedures
   - 1. Numbered lists for step-by-step processes
   - `code` for technical terms, amounts, percentages
   - > Blockquotes for important notes and warnings
   - | Tables | for | structured data |
4. Professional and helpful tone
5. Remember conversation context
6. Structure responses with clear sections using headers"""
            messages = [{"role": "system", "content": system_prompt}]
            
            # 대화 이력 추가 (최근 5턴만)
            for hist_msg in history[-10:]:  # 최근 10개 메시지 (5턴)
                messages.append({
                    "role": hist_msg["role"],
                    "content": hist_msg["content"]
                })
            
            # 현재 메시지 추가
            messages.append({"role": "user", "content": message})
            
            vllm_payload = {
                "model": "default-model",
                "messages": messages,
                "stream": False
            }
            
            try:
                response = requests.post(
                    "http://localhost:8000/v1/chat/completions",
                    json=vllm_payload,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer dummy-key'
                    },
                    timeout=30
                )
            except requests.exceptions.ConnectionError:
                # vLLM 연결 실패시 대체 응답
                fallback_response = {
                    'reply': f"죄송합니다. 현재 AI 모델이 시작 중입니다. 잠시 후 다시 시도해주세요.\n\n질문: {message}\n\n한국도로공사 관련 문의는 고객센터(1588-2504)로 연락하시거나 잠시 후 다시 이용해주세요.",
                    'sources': [],
                    'status': 'AI 모델 로딩 중',
                    'processing_time': f"0.01초",
                    'timestamp': datetime.now().isoformat()
                }
                log_request('채팅', user_id, '연결 오류', 'error', '0.00초')
                return jsonify(fallback_response)
        
        processing_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            # RAG가 "Connection error" 응답하는 경우 vLLM 직접 호출
            if 'detail' in result and 'Connection error' in str(result.get('detail', '')):
                logger.warning("RAG 내부 연결 오류, vLLM 직접 호출로 전환")
                
                korean_only_prompt = """당신은 한국도로공사의 AI 어시스턴트 ex-GPT입니다.

CRITICAL LANGUAGE RULES - MUST FOLLOW:
1. 오직 한국어로만 답변하세요. 
2. 중국어, 영어, 일본어 사용 절대 금지
3. 중국어 문자(如, 您, 等, 会, 鲷鱼, 欢迎) 사용 금지
4. 영어 단어 최소화, 한국어 우선
5. 대화 상대방의 이름을 정확히 기억하세요

CONVERSATION CONTEXT:
- 사용자 이름과 이전 대화 내용을 기억하세요
- 이름을 물으면 정확히 답변하세요

RESPONSE FORMAT:
- 인사: "안녕하세요, [이름]님!"
- 도움 제안: "한국도로공사 관련 문의사항이 있으시면 언제든 말씀해주세요."
- 한국어만 사용

절대 중국어를 사용하지 마세요!"""
                
                vllm_payload = {
                    "model": "default-model",
                    "messages": [
                        {"role": "system", "content": korean_only_prompt},
                        {"role": "user", "content": message}
                    ],
                    "stream": False
                }
                
                try:
                    vllm_response = requests.post(
                        "http://localhost:8000/v1/chat/completions",
                        json=vllm_payload,
                        headers={
                            'Content-Type': 'application/json',
                            'Authorization': 'Bearer dummy-key'
                        },
                        timeout=30
                    )
                except requests.exceptions.ConnectionError:
                    # vLLM 연결 실패시 대체 응답
                    fallback_response = {
                        'reply': f"죄송합니다. 현재 AI 모델이 시작 중입니다. 잠시 후 다시 시도해주세요.\n\n질문: {message}\n\n한국도로공사 관련 문의는 고객센터(1588-2504)로 연락하시거나 잠시 후 다시 이용해주세요.",
                        'sources': [],
                        'status': 'AI 모델 로딩 중',
                        'processing_time': f"{processing_time:.2f}초",
                        'timestamp': datetime.now().isoformat()
                    }
                    log_request('채팅', user_id, '연결 오류', 'error', f"{processing_time:.2f}초")
                    return jsonify(fallback_response)
                
                if vllm_response.status_code == 200:
                    vllm_result = vllm_response.json()
                    content = vllm_result['choices'][0]['message']['content']
                    formatted_response = {
                        'reply': content,
                        'sources': [],
                        'status': 'success (vLLM 직접 호출)',
                        'route_path': route_path,
                        'confidence': confidence,
                        'reasoning': reasoning,
                        'processing_time': f"{processing_time:.2f}초",
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # 대화 이력에 추가 (자동 필터링)
                    cleaned_content = add_to_conversation_history(session_id, message, content)
                    formatted_response['reply'] = cleaned_content  # 필터링된 응답으로 업데이트
                    log_request('채팅', user_id, 'vLLM 직접 연동', 'success', f"{processing_time:.2f}초")
                    return jsonify(formatted_response)
            
            # 응답 형식에 따라 처리
            if 'response' in result:
                # RAG 형식: {"response": "...", "sources": [...]}
                formatted_response = {
                    'reply': result['response'],
                    'sources': result.get('sources', []),
                    'status': f'success ({route_path})',
                    'route_path': route_path,
                    'confidence': confidence,
                    'reasoning': reasoning,
                    'processing_time': f"{processing_time:.2f}초",
                    'timestamp': datetime.now().isoformat()
                }
                
                # 대화 이력에 추가 (자동 필터링)
                cleaned_response = add_to_conversation_history(session_id, message, result['response'])
                formatted_response['reply'] = cleaned_response  # 필터링된 응답으로 업데이트
                log_request('채팅', user_id, 'RAG 검색', 'success', f"{processing_time:.2f}초")
            elif 'choices' in result:
                # vLLM 형식: {"choices": [{"message": {"content": "..."}}]}
                content = result['choices'][0]['message']['content']
                formatted_response = {
                    'reply': content,
                    'sources': [],
                    'status': f'success ({route_path})',
                    'route_path': route_path,
                    'confidence': confidence,
                    'reasoning': reasoning,
                    'processing_time': f"{processing_time:.2f}초",
                    'timestamp': datetime.now().isoformat()
                }
                
                # 대화 이력에 추가 (자동 필터링)
                cleaned_content = add_to_conversation_history(session_id, message, content)
                formatted_response['reply'] = cleaned_content  # 필터링된 응답으로 업데이트
                log_request('채팅', user_id, '일반 대화', 'success', f"{processing_time:.2f}초")
            else:
                formatted_response = result
                log_request('채팅', user_id, '기타', 'success', f"{processing_time:.2f}초")
            
            return jsonify(formatted_response)
            
        else:
            # 500 오류에서 Connection error인 경우 vLLM 직접 호출
            if response.status_code == 500:
                try:
                    error_detail = response.json().get('detail', '')
                    if 'Connection error' in str(error_detail):
                        logger.warning("RAG 500 오류 (Connection error), vLLM 직접 호출로 전환")
                        
                        korean_strict_prompt = """You are ex-GPT, an AI assistant for Korea Expressway Corporation (한국도로공사).

## Core Identity
- Role: Professional Korean expressway expert assistant
- Organization: Korea Expressway Corporation (KEC)
- Language: ALWAYS respond in Korean only

## Language Policy (CRITICAL)
```python
ALLOWED_LANGUAGES = ["korean"]
FORBIDDEN_LANGUAGES = ["chinese", "english", "japanese"]
FORBIDDEN_CHARS = ["如", "您", "等", "会", "网站", "或", "移动", "应用", "客服", "可以", "直接", "查询", "最新", "信息", "我们", "提供", "多少", "费用", "需要", "政策", "因为", "可能", "根据", "地区", "具体", "情况", "不同", "建议", "通过", "官方", "进行", "联系", "获取", "准确"]

def validate_response(text):
    return not any(char in text for char in FORBIDDEN_CHARS)
```

## Memory & Context
- Remember user names and conversation history
- When asked about names, recall accurately
- Maintain conversation context across turns

## Response Templates (Markdown Format)
```python
GREETING_TEMPLATE = "## 안녕하세요, **{name}님**! 👋\n\n한국도로공사 `ex-GPT`입니다."
HELP_TEMPLATE = "> 💡 **도움말**: 한국도로공사 관련 문의사항이 있으시면 언제든 말씀해주세요."
PROCEDURE_TEMPLATE = "## {title}\\n\\n### 📋 절차 개요\\n{overview}\\n\\n### 📝 단계별 안내\\n{steps}\\n\\n### ⚠️ 주의사항\\n{notes}"
```

## Output Rules
1. ONLY Korean language in responses
2. NO Chinese/English/Japanese characters
3. ALWAYS use Markdown formatting - THIS IS MANDATORY:
   - **Bold** for important points and emphasis
   - ## Headers for sections and topics
   - ### Sub-headers for detailed breakdown
   - - Lists for multiple items and procedures
   - 1. Numbered lists for step-by-step processes
   - `code` for technical terms, amounts, percentages
   - > Blockquotes for important notes and warnings
   - | Tables | for | structured data |
4. Professional and helpful tone
5. Remember conversation context
6. Structure responses with clear sections using headers"""

                        # 대화 이력을 포함한 메시지 구성
                        vllm_messages = [{"role": "system", "content": korean_strict_prompt}]
                        
                        # 대화 이력 추가 (최근 5턴만)
                        for hist_msg in history[-10:]:
                            vllm_messages.append({
                                "role": hist_msg["role"],
                                "content": hist_msg["content"]
                            })
                        
                        # 현재 메시지 추가
                        vllm_messages.append({"role": "user", "content": message})
                        
                        vllm_payload = {
                            "model": "default-model", 
                            "messages": vllm_messages,
                            "stream": False
                        }
                        
                        try:
                            vllm_response = requests.post(
                                "http://localhost:8000/v1/chat/completions",
                                json=vllm_payload,
                                headers={
                                    'Content-Type': 'application/json',
                                    'Authorization': 'Bearer dummy-key'
                                },
                                timeout=30
                            )
                        except requests.exceptions.ConnectionError:
                            # vLLM도 연결 실패시 안내 메시지
                            processing_time = time.time() - start_time
                            fallback_response = {
                                'reply': f"죄송합니다. 현재 AI 모델이 시작 중입니다. 잠시 후 다시 시도해주세요.\n\n질문: {message}\n\n한국도로공사 관련 문의는 고객센터(1588-2504)로 연락하시거나 잠시 후 다시 이용해주세요.",
                                'sources': [],
                                'status': 'AI 모델 로딩 중',
                                'processing_time': f"{processing_time:.2f}초",
                                'timestamp': datetime.now().isoformat()
                            }
                            log_request('채팅', user_id, 'RAG 오류', 'error', f"{processing_time:.2f}초")
                            return jsonify(fallback_response)
                        
                        if vllm_response.status_code == 200:
                            vllm_result = vllm_response.json()
                            content = vllm_result['choices'][0]['message']['content']
                            formatted_response = {
                                'reply': content,
                                'sources': [],
                                'status': 'success (vLLM 직접 호출)',
                                'route_path': route_path,
                                'confidence': confidence,
                                'reasoning': reasoning,
                                'processing_time': f"{processing_time:.2f}초",
                                'timestamp': datetime.now().isoformat()
                            }
                            
                            # 대화 이력에 추가 (자동 필터링)
                            cleaned_content = add_to_conversation_history(session_id, message, content)
                            formatted_response['reply'] = cleaned_content  # 필터링된 응답으로 업데이트
                            log_request('채팅', user_id, 'vLLM 직접 연동', 'success', f"{processing_time:.2f}초")
                            return jsonify(formatted_response)
                except:
                    pass
            
            error_msg = f"RAG API 오류 (HTTP {response.status_code})"
            try:
                error_detail = response.json().get('detail', response.text)
                error_msg += f": {error_detail}"
            except:
                error_msg += f": {response.text}"
            
            log_request('채팅', user_id, 'RAG 오류', 'error', f"{processing_time:.2f}초")
            
            return jsonify({
                'error': error_msg,
                'status': 'error',
                'processing_time': f"{processing_time:.2f}초"
            }), response.status_code
            
    except requests.exceptions.ConnectionError:
        processing_time = time.time() - start_time
        
        # vLLM 직접 연결도 시도해보고, 실패하면 안내 메시지
        fallback_response = {
            'reply': f"죄송합니다. 현재 AI 모델이 시작 중입니다. 잠시 후 다시 시도해주세요.\n\n질문: {message}\n\n한국도로공사 관련 문의는 고객센터(1588-2504)로 연락하시거나 잠시 후 다시 이용해주세요.",
            'sources': [],
            'status': 'AI 모델 로딩 중',
            'processing_time': f"{processing_time:.2f}초",
            'timestamp': datetime.now().isoformat()
        }
        
        log_request('채팅', request.remote_addr, '연결 오류', 'error', f"{processing_time:.2f}초")
        return jsonify(fallback_response)
        
    except requests.exceptions.Timeout:
        processing_time = time.time() - start_time
        error_msg = "요청 시간이 초과되었습니다. 잠시 후 다시 시도해주세요."
        
        log_request('채팅', request.remote_addr, '타임아웃', 'error', f"{processing_time:.2f}초")
        
        return jsonify({
            'error': error_msg,
            'status': 'timeout',
            'processing_time': f"{processing_time:.2f}초"
        }), 408
        
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = f"처리 중 오류가 발생했습니다: {str(e)}"
        
        logger.error(f"❌ 채팅 프록시 오류: {str(e)}")
        log_request('채팅', request.remote_addr, '내부 오류', 'error', f"{processing_time:.2f}초")
        
        return jsonify({
            'error': error_msg,
            'status': 'error',
            'processing_time': f"{processing_time:.2f}초"
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """서버 상태 확인"""
    try:
        # RAG 서버 상태 확인
        neoali_status = "unknown"
        try:
            health_response = requests.get("http://localhost:8080/health", timeout=5)
            if health_response.status_code == 200:
                neoali_status = "connected"
            else:
                neoali_status = "error"
        except:
            neoali_status = "disconnected"
        
        return jsonify({
            'status': 'healthy',
            'neoali_rag_status': neoali_status,
            'total_requests': stats_data['total_requests'],
            'active_users': len(stats_data['active_users']),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"헬스체크 오류: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/patterns', methods=['GET'])
def get_pattern_analytics():
    """패턴 분석 및 관리 API"""
    try:
        # 패턴 성능 통계
        performance_stats = {}
        for pattern_key, data in pattern_learning_data['pattern_performance'].items():
            success_rate = (data['success'] / data['count'] * 100) if data['count'] > 0 else 0
            performance_stats[pattern_key] = {
                'count': data['count'],
                'success': data['success'],
                'success_rate': f"{success_rate:.1f}%"
            }
        
        # 새로운 패턴 제안
        suggestions = suggest_new_patterns()
        
        # 최근 라우팅 오류
        recent_errors = pattern_learning_data['misrouted_queries'][-10:]
        
        return jsonify({
            'pattern_performance': performance_stats,
            'pattern_suggestions': suggestions,
            'recent_misrouted': recent_errors,
            'last_update': pattern_learning_data['last_update'].isoformat(),
            'total_queries': sum(data['count'] for data in pattern_learning_data['pattern_performance'].values())
        })
        
    except Exception as e:
        logger.error(f"패턴 분석 오류: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/patterns/feedback', methods=['POST'])
def submit_pattern_feedback():
    """패턴 피드백 제출 API"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        expected_path = data.get('expected_path', '')
        actual_path = data.get('actual_path', '')
        
        # 피드백 데이터 수집
        collect_misrouted_query(query, expected_path, actual_path)
        
        logger.info(f"📝 패턴 피드백 수집: {query} -> 예상:{expected_path}, 실제:{actual_path}")
        
        return jsonify({
            'status': 'success',
            'message': '피드백이 성공적으로 수집되었습니다.'
        })
        
    except Exception as e:
        logger.error(f"패턴 피드백 오류: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """시스템 통계 데이터 반환"""
    try:
        total = stats_data['total_requests']
        success_rate = (stats_data['successful_requests'] / total * 100) if total > 0 else 100
        
        return jsonify({
            'total_requests': stats_data['total_requests'],
            'successful_requests': stats_data['successful_requests'], 
            'failed_requests': stats_data['failed_requests'],
            'success_rate': f"{success_rate:.1f}%",
            'active_users': len(stats_data['active_users']),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"통계 데이터 조회 오류: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/test', methods=['GET']) 
def test_endpoint():
    """테스트 엔드포인트"""
    return jsonify({
        "message": "ex-GPT + RAG 서버가 정상 작동 중입니다.", 
        "neoali_integration": True,
        "endpoints": [
            "/api/chat",
            "/api/health", 
            "/api/stats",
            "/api/test"
        ]
    })

# 오류 핸들러
@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"내부 서버 오류: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

# ============================================================================
# 메인 실행 부분 
# ============================================================================

if __name__ == '__main__':
    logger.info("🚀 ex-GPT 통합 서버 시작...")
    logger.info("🔗 RAG API: http://localhost:8081")
    logger.info("📍 웹 서버: http://localhost:5001") 
    logger.info("🎉 준비 완료!")
    
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)