#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify, send_from_directory, render_template_string
from flask_cors import CORS
import torch
import torch.nn as nn
import os
import gc
import logging
import threading
import time
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor
import asyncio
from functools import wraps
import warnings
import whisper
import tempfile
from werkzeug.utils import secure_filename
import requests
import json
import librosa
import noisereduce as nr
from pydub import AudioSegment
from pydub.silence import split_on_silence
import numpy as np
from datetime import datetime, timedelta
import uuid
import sentence_transformers
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor
import queue
import threading
from tqdm import tqdm
import json
import zipfile
import os
import tempfile
from pathlib import Path
import subprocess
import psutil
import threading
from queue import Queue, Empty
import asyncio
from concurrent.futures import ThreadPoolExecutor
from flask import Response
# CUDA PyTorch 환경에서 동작하는 음성 처리 시스템

import torch
import torch.nn as nn
import os
import gc
import logging
import threading
import time
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor
import tempfile
import requests
import json
import librosa
import noisereduce as nr
from pydub import AudioSegment
from pydub.silence import split_on_silence
import numpy as np
from datetime import datetime, timedelta
import uuid
# 음성 처리 관련 imports
try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
    logger.info("✅ Faster Whisper 사용 가능")
except ImportError:
    FASTER_WHISPER_AVAILABLE = False
    logger.warning("⚠️ Faster Whisper 사용 불가")

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
    logger.info("✅ SpeechRecognition 사용 가능")
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    logger.warning("⚠️ SpeechRecognition 사용 불가")

try:
    from transformers import WhisperProcessor, WhisperForConditionalGeneration
    TRANSFORMERS_AVAILABLE = True
    logger.info("✅ Transformers Whisper 사용 가능")
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("⚠️ Transformers 사용 불가")

# ============= Flask 앱 및 CORS 설정 =============
app = Flask(__name__)
CORS(app)

# 경고 메시지 억제
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 로깅 설정
logger = logging.getLogger(__name__)

# 글로벌 변수 - 듀얼 GPU 지원
florence_models = {}
florence_processors = {}
available_devices = ["cuda:0", "cuda:1"]
request_queue = Queue()
gpu_load_tracker = {device: 0 for device in available_devices}
gpu_lock = threading.Lock()

# 통계 데이터 저장
stats_data = {
    'total_requests': 0,
    'successful_requests': 0,
    'failed_requests': 0,
    'active_users': set(),
    'daily_usage': {},
    'gpu_usage_history': [],
    'recent_logs': []
}

# 업로드 세션 관리
upload_sessions = {}

# ============================================================================
# STEP 2: 전역 변수 섹션에 추가
# ============================================================================
# 글로벌 변수 선언
qdrant_client = None
embedding_model = None
whisper_model = None
optimized_ollama = None
gpu_ollama = None

# 음성 처리 모델들
faster_whisper_model = None
transformers_whisper_model = None
transformers_processor = None
speech_recognizer = None


# 음성 처리 설정
AUDIO_SETTINGS = {
    'sample_rate': 16000,
    'channels': 1,
    'bit_depth': 16,
    'format': 'wav'
}

WHISPER_OPTIONS = {
    'language': 'ko',
    'temperature': 0.0,
    'beam_size': 5,
    'condition_on_previous_text': True,
    'compression_ratio_threshold': 2.4,
    'logprob_threshold': -1.0,
    'no_speech_threshold': 0.6
}

# 음성 처리 세션 관리
audio_processing_sessions = {}
audio_processing_lock = Lock()

# ============================================================================
# STEP 3: 음성 처리 함수들 추가
# ============================================================================


# 대화 히스토리 관리
conversation_history = {}
think_sessions = {}

# Qdrant 클라이언트 초기화 및 컬렉션 생성
def initialize_qdrant():
    """Qdrant 초기화 및 컬렉션 생성"""
    global qdrant_client
    
    try:
        logger.info("🔗 Qdrant 서버 연결 시도...")
        client = QdrantClient(host="localhost", port=6333)
        
        # 헬스체크
        health = client.get_collections()
        logger.info(f"✅ Qdrant 서버 연결 성공! 기존 컬렉션: {len(health.collections)}개")
        
        # 컬렉션 존재 여부 확인
        collection_names = [col.name for col in health.collections]
        
        if "documents" not in collection_names:
            logger.info("📋 documents 컬렉션 생성 중...")
            
            # 컬렉션 생성
            client.create_collection(
                collection_name="documents",
                vectors_config=VectorParams(
                    size=384,
                    distance=Distance.COSINE
                )
            )
            logger.info("✅ documents 컬렉션 생성 완료")
            logger.info("📄 빈 컬렉션으로 시작합니다. 문서를 업로드해주세요.")
        else:
            collection_info = client.get_collection("documents")
            logger.info(f"✅ documents 컬렉션 존재: {collection_info.points_count}개 문서")
        
        qdrant_client = client
        return client
        
    except Exception as e:
        logger.error(f"❌ Qdrant 초기화 실패: {e}")
        qdrant_client = None
        return None

# 임베딩 모델 초기화
try:
    embedding_model = sentence_transformers.SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    logger.info("✅ 임베딩 모델 로드 성공")
except Exception as e:
    logger.warning(f"❌ 임베딩 모델 로드 실패: {e}")
    embedding_model = None

def embed_text(text):
    """텍스트를 벡터로 임베딩"""
    if not embedding_model:
        return [0.0] * 384
    
    try:
        embeddings = embedding_model.encode([text])
        return embeddings[0].tolist()
    except Exception as e:
        logger.error(f"임베딩 오류: {e}")
        return [0.0] * 384

# 검색 함수
def search_documents(query, limit=5):
    """실제 Qdrant 검색"""
    global qdrant_client
    
    if not qdrant_client:
        logger.warning("⚠️ Qdrant 연결 없음. 재연결 시도...")
        qdrant_client = initialize_qdrant()
        if not qdrant_client:
            return []
    
    if not embedding_model:
        logger.warning("⚠️ 임베딩 모델 없음")
        return []
    
    try:
        # 컬렉션 존재 여부 확인
        collections = qdrant_client.get_collections()
        collection_names = [col.name for col in collections.collections]
        
        if "documents" not in collection_names:
            logger.info(f"🔍 '{query}' 검색 결과: documents 컬렉션 없음")
            return []
        
        # 쿼리 벡터 생성
        query_vector = embed_text(query)
        
        # Qdrant 검색 수행
        search_result = qdrant_client.query_points(
            collection_name="documents",
            query=query_vector,
            limit=limit,
            with_payload=True,
            with_vectors=False
        )
        
        if not search_result.points:
            logger.info(f"🔍 '{query}' 검색 결과 없음")
            return []
        
        # 검색 결과 포맷팅
        results = []
        for result in search_result.points:
            payload = result.payload
            results.append({
                "filename": payload.get("filename", "unknown.pdf"),
                "content": payload.get("content", "")[:200] + "..." if len(payload.get("content", "")) > 200 else payload.get("content", ""),
                "score": float(result.score),
                "page": payload.get("page", 1),
                "document_type": payload.get("document_type", "문서")
            })
        
        logger.info(f"✅ '{query}' 검색 완료: {len(results)}개 문서")
        return results
        
    except Exception as e:
        logger.error(f"❌ 검색 오류: {e}")
        return []

# 1. Faster Whisper 사용 (기존 PyTorch와 충돌 없음)
try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
    logger.info("✅ Faster Whisper 사용 가능")
except ImportError:
    FASTER_WHISPER_AVAILABLE = False
    logger.warning("⚠️ Faster Whisper 사용 불가")

# 2. SpeechRecognition 백업 옵션
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
    logger.info("✅ SpeechRecognition 사용 가능")
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    logger.warning("⚠️ SpeechRecognition 사용 불가")

# 3. Hugging Face Transformers 사용 (PyTorch 기반)
try:
    from transformers import pipeline, WhisperProcessor, WhisperForConditionalGeneration
    TRANSFORMERS_AVAILABLE = True
    logger.info("✅ Transformers Whisper 사용 가능")
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("⚠️ Transformers 사용 불가")

# 글로벌 모델 변수들
faster_whisper_model = None
transformers_whisper_model = None
transformers_processor = None
speech_recognizer = None

# Ollama 설정
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen3:8b"
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'm4a', 'wav', 'flac', 'aac', 'ogg', 'wma'}



def transcribe_with_faster_whisper(audio_path):
    """Faster Whisper로 음성 인식"""
    if not faster_whisper_model:
        return None
    
    try:
        logger.info("🔄 Faster Whisper STT 시작...")
        
        segments, info = faster_whisper_model.transcribe(
            audio_path,
            language="ko",
            beam_size=5,
            temperature=0.0,
            condition_on_previous_text=True,
            compression_ratio_threshold=2.4,
            logprob_threshold=-1.0,
            no_speech_threshold=0.6
        )
        
        # 세그먼트들을 텍스트로 결합
        transcription = ""
        for segment in segments:
            transcription += segment.text + " "
        
        transcription = transcription.strip()
        logger.info(f"✅ Faster Whisper STT 완료: {len(transcription)}자")
        return transcription
        
    except Exception as e:
        logger.error(f"❌ Faster Whisper STT 오류: {e}")
        return None

def transcribe_with_transformers(audio_path):
    """Transformers Whisper로 음성 인식"""
    if not transformers_whisper_model or not transformers_processor:
        return None
    
    try:
        logger.info("🔄 Transformers Whisper STT 시작...")
        
        # 오디오 로드 및 전처리
        audio, sr_rate = librosa.load(audio_path, sr=16000)
        
        # 입력 특성 추출
        input_features = transformers_processor(
            audio, 
            sampling_rate=16000, 
            return_tensors="pt"
        ).input_features
        
        # GPU로 이동
        if torch.cuda.is_available():
            input_features = input_features.to("cuda")
        
        # 강제로 한국어 토큰 설정
        forced_decoder_ids = transformers_processor.get_decoder_prompt_ids(
            language="korean", 
            task="transcribe"
        )
        
        # 추론 실행
        with torch.no_grad():
            predicted_ids = transformers_whisper_model.generate(
                input_features, 
                forced_decoder_ids=forced_decoder_ids,
                max_length=448,
                temperature=0.0,
                do_sample=False
            )
        
        # 디코딩
        transcription = transformers_processor.batch_decode(
            predicted_ids, 
            skip_special_tokens=True
        )[0]
        
        logger.info(f"✅ Transformers Whisper STT 완료: {len(transcription)}자")
        return transcription.strip()
        
    except Exception as e:
        logger.error(f"❌ Transformers Whisper STT 오류: {e}")
        return None

def allowed_audio_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_AUDIO_EXTENSIONS

# ============================================================================
# STEP 3: 음성 처리 함수들 추가
# ============================================================================

# 기존 함수들 아래에 추가하세요:

def initialize_audio_models():
    """음성 처리 모델들 초기화"""
    global faster_whisper_model, transformers_whisper_model, transformers_processor, speech_recognizer
    
    models_loaded = []
    
    # Faster Whisper 초기화
    if FASTER_WHISPER_AVAILABLE:
        try:
            if torch.cuda.is_available():
                faster_whisper_model = WhisperModel("medium", device="cuda", compute_type="float16")
                logger.info("✅ Faster Whisper GPU 모델 로드 성공")
            else:
                faster_whisper_model = WhisperModel("medium", device="cpu", compute_type="int8")
                logger.info("✅ Faster Whisper CPU 모델 로드 성공")
            models_loaded.append("faster_whisper")
        except Exception as e:
            logger.error(f"❌ Faster Whisper 로드 실패: {e}")
    
    # SpeechRecognition 초기화
    if SPEECH_RECOGNITION_AVAILABLE:
        try:
            speech_recognizer = sr.Recognizer()
            models_loaded.append("speech_recognition")
            logger.info("✅ SpeechRecognition 초기화 성공")
        except Exception as e:
            logger.error(f"❌ SpeechRecognition 초기화 실패: {e}")
    
    logger.info(f"🎤 사용 가능한 STT 모델: {', '.join(models_loaded)}")
    return len(models_loaded) > 0

def transcribe_with_faster_whisper(audio_path):
    """Faster Whisper로 음성 인식"""
    if not faster_whisper_model:
        return None
    
    try:
        segments, info = faster_whisper_model.transcribe(
            audio_path,
            language="ko",
            beam_size=5,
            temperature=0.0
        )
        
        transcription = ""
        for segment in segments:
            transcription += segment.text + " "
        
        return transcription.strip()
        
    except Exception as e:
        logger.error(f"Faster Whisper STT 오류: {e}")
        return None

def transcribe_with_speech_recognition(audio_path):
    """SpeechRecognition으로 음성 인식"""
    if not speech_recognizer:
        return None
    
    try:
        # WAV 파일로 변환
        audio = AudioSegment.from_file(audio_path)
        wav_path = audio_path.rsplit('.', 1)[0] + '_sr.wav'
        audio.export(wav_path, format="wav")
        
        # 음성 인식
        with sr.AudioFile(wav_path) as source:
            audio_data = speech_recognizer.record(source)
        
        transcription = speech_recognizer.recognize_google(
            audio_data, 
            language='ko-KR'
        )
        
        # 임시 파일 정리
        if os.path.exists(wav_path):
            os.remove(wav_path)
        
        return transcription
        
    except Exception as e:
        logger.error(f"SpeechRecognition STT 오류: {e}")
        return None

def transcribe_audio(audio_path):
    """통합 음성 인식 함수"""
    # Faster Whisper 우선 시도
    if faster_whisper_model:
        result = transcribe_with_faster_whisper(audio_path)
        if result:
            return enhance_transcription_quality(result)
    
    # 백업으로 SpeechRecognition 시도
    if speech_recognizer:
        result = transcribe_with_speech_recognition(audio_path)
        if result:
            return enhance_transcription_quality(result)
    
    return None

def enhance_transcription_quality(text):
    """전사 품질 향상"""
    if not text:
        return text
    
    import re
    
    # 기본 정리
    text = text.strip()
    
    # 반복 구문 제거
    sentences = text.split('. ')
    unique_sentences = []
    prev_sentence = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence and sentence != prev_sentence:
            unique_sentences.append(sentence)
            prev_sentence = sentence
    
    text = '. '.join(unique_sentences)
    
    # 문장 부호 정리
    text = re.sub(r'\s+([,.!?])', r'\1', text)
    text = re.sub(r'([,.!?])\s*([,.!?])', r'\1', text)
    text = re.sub(r'\s+', ' ', text)
    
    if text and not text.endswith(('.', '!', '?')):
        text += '.'
    
    return text

def create_processing_session(user_id):
    """오디오 처리 세션 생성"""
    session_id = str(uuid.uuid4())
    audio_processing_sessions[session_id] = {
        'user_id': user_id,
        'status': 'initialized',
        'progress': 0,
        'message': '처리 준비 중...',
        'created_at': datetime.now(),
        'result': None
    }
    return session_id

def update_processing_session(session_id, status=None, progress=None, message=None, result=None):
    """처리 세션 업데이트"""
    if session_id in audio_processing_sessions:
        session = audio_processing_sessions[session_id]
        if status: session['status'] = status
        if progress is not None: session['progress'] = progress
        if message: session['message'] = message
        if result: session['result'] = result
        session['updated_at'] = datetime.now()
        
# GPU 가속 LLM 클래스 (수정된 버전)
class GPUAcceleratedLLM:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = None
        self.initialized = False
        
        try:
            self.initialize_gpu_model()
        except Exception as e:
            logger.warning(f"GPU LLM 초기화 실패: {e}")
            self.model = None

    def initialize_gpu_model(self):
        """GPU LLM 모델 초기화"""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            if not torch.cuda.is_available():
                logger.warning("CUDA를 사용할 수 없습니다")
                return
            
            # 간단한 모델로 테스트
            model_name = "microsoft/DialoGPT-medium"
            
            logger.info(f"GPU LLM 모델 로딩: {model_name}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            
            self.device = next(self.model.parameters()).device
            self.initialized = True
            
            logger.info(f"✅ GPU LLM 초기화 완료: {self.device}")
            
        except Exception as e:
            logger.error(f"GPU LLM 초기화 오류: {e}")
            self.model = None
            self.tokenizer = None

    def generate_response(self, prompt, max_tokens=512):
        """GPU LLM 응답 생성"""
        if not self.initialized or not self.model:
            return None
        
        try:
            inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + max_tokens,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            # 원래 프롬프트 제거
            response = response[len(prompt):].strip()
            
            return response
            
        except Exception as e:
            logger.error(f"GPU LLM 생성 오류: {e}")
            return None

# 글로벌 GPU LLM 인스턴스
gpu_llm = None

def query_ollama_streaming(prompt):
    """Ollama 스트리밍 응답"""
    try:
        logger.info("🤖 Ollama 요청 시작...")
        
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": 0.1,      # 0.3에서 0.1로 감소 (더 빠름)
                "num_predict": 150,      # 200에서 150으로 감소
                "num_ctx": 512,          # 1024에서 512로 감소
                "num_thread": 8,         # 스레드 수 추가
                "repeat_penalty": 1.1    # 반복 방지
            }
        }
        
        response = requests.post(
            OLLAMA_API_URL, 
            json=payload, 
            timeout=30,
            stream=True
        )
        response.raise_for_status()
        
        full_response = ""
        for line in response.iter_lines():
            if line:
                try:
                    decoded_line = line.decode('utf-8')
                    json_line = json.loads(decoded_line)
                    chunk = json_line.get("response", "")
                    full_response += chunk
                    if json_line.get("done"):
                        break
                except json.JSONDecodeError:
                    continue
        
        # <think> 태그 제거
        if "<think>" in full_response and "</think>" in full_response:
            start_tag = full_response.find("<think>")
            end_tag = full_response.find("</think>") + len("</think>")
            full_response = full_response[:start_tag] + full_response[end_tag:]
        
        full_response = full_response.strip()
        logger.info(f"✅ Ollama 응답 완료: {len(full_response)}자")
        return full_response
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Ollama 연결 오류: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Ollama 처리 오류: {e}")
        return None

def query_ollama_fast(prompt):
    """빠른 Ollama 호출"""
    try:
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 200,
                "num_ctx": 1024
            }
        }
        
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "").strip()
        else:
            return None
            
    except Exception as e:
        logger.error(f"❌ 빠른 Ollama 오류: {e}")
        return None

def log_request(request_type, user_id, action, status, processing_time):
    """요청 로그 기록"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'type': request_type,
        'user': user_id,
        'action': action,
        'status': status,
        'processing_time': processing_time
    }
    
    stats_data['recent_logs'].insert(0, log_entry)
    if len(stats_data['recent_logs']) > 100:
        stats_data['recent_logs'].pop()
    
    stats_data['total_requests'] += 1
    if status == 'success':
        stats_data['successful_requests'] += 1
    else:
        stats_data['failed_requests'] += 1
    
    today = datetime.now().strftime('%Y-%m-%d')
    if today not in stats_data['daily_usage']:
        stats_data['daily_usage'][today] = 0
    stats_data['daily_usage'][today] += 1

# =============================================================================
# 라우트 정의
# =============================================================================

@app.route('/')
def index():
    """메인 페이지"""
    try:
        if os.path.exists('index.html'):
            return send_from_directory('.', 'index.html')
        else:
            with open('paste-3.txt', 'r', encoding='utf-8') as f:
                return f.read()
    except Exception as e:
        logger.error(f"메인 페이지 오류: {str(e)}")
        return render_template_string("""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <title>EX-GPT 서버</title>
            <style>
                body { font-family: 'Malgun Gothic', sans-serif; margin: 40px; }
                .status { background: #f0f8ff; padding: 20px; border-radius: 8px; margin: 20px 0; }
                .success { color: #28a745; }
            </style>
        </head>
        <body>
            <h1>🚀 EX-GPT 서버</h1>
            <div class="status">
                <p class="success">✅ 서버가 정상적으로 실행 중입니다</p>
            </div>
        </body>
        </html>
        """)

@app.route('/admin')
def admin_dashboard():
    """관리자 대시보드"""
    try:
        # 절대 경로로 파일 찾기
        admin_file_path = '/mnt/c/projects/ex-gpt-demo/admin_dashboard.html'
        
        if os.path.exists(admin_file_path):
            with open(admin_file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # 상대 경로도 시도
            if os.path.exists('admin_dashboard.html'):
                with open('admin_dashboard.html', 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                raise FileNotFoundError("관리자 대시보드 파일을 찾을 수 없습니다")
                
    except Exception as e:
        logger.error(f"관리자 대시보드 오류: {str(e)}")
        return render_template_string("""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <title>EX-GPT 관리자 대시보드</title>
            <style>
                body { font-family: 'Malgun Gothic', sans-serif; margin: 40px; }
                .error { color: #dc3545; background: #f8d7da; padding: 20px; border-radius: 8px; }
            </style>
        </head>
        <body>
            <h1>EX-GPT 관리자 대시보드</h1>
            <div class="error">
                <h3>⚠️ 관리자 대시보드 파일이 없습니다</h3>
                <p>admin_dashboard.html 파일이 다음 경로에 없습니다:</p>
                <ul>
                    <li>/mnt/c/projects/ex-gpt-demo/admin_dashboard.html</li>
                    <li>현재 디렉토리/admin_dashboard.html</li>
                </ul>
                <p><a href="/">메인 페이지로 돌아가기</a></p>
            </div>
        </body>
        </html>
        """), 500

@app.route('/api/chat', methods=['POST'])
def enhanced_text_chat():
    """향상된 텍스트 채팅 API"""
    start_time = time.time()
    
    try:
        data = request.json
        if not data:
            return jsonify({'error': '요청 데이터가 없습니다.'}), 400
            
        message = data.get('message', '').strip()
        user_id = data.get('user_id', request.remote_addr)
        mode = data.get('mode', 'standard')
        
        if not message:
            return jsonify({'error': '메시지를 입력해주세요.'}), 400
        
        logger.info(f"💬 사용자 메시지: '{message}' (모드: {mode})")
        
        # 활성 사용자 추가
        stats_data['active_users'].add(user_id)
        
        # 1. 관련 문서 검색
        logger.info(f"🔍 문서 검색 시작: '{message}'")
        relevant_docs = search_documents(message, limit=3)
        logger.info(f"📋 검색 완료: {len(relevant_docs)}개 문서 발견")
        
        # 2. 프롬프트 구성
        if mode == 'think':
            # Think 모드 프롬프트
            if relevant_docs:
                context = "\n".join([
                    f"📄 {doc['filename']} (관련도: {doc['score']:.2f})\n{doc['content']}" 
                    for doc in relevant_docs
                ])
                
                prompt = f"""당신은 한국도로공사의 전문 AI 어시스턴트입니다.

<think>
단계별 분석을 수행하세요:
1. 질문의 핵심 파악: 사용자가 정확히 무엇을 묻고 있는가?
2. 관련 문서 평가: 제공된 문서들이 얼마나 관련성이 있는가?
3. 추가 정보 필요성: 더 필요한 정보가 있는가?
4. 답변 구조화: 어떤 순서로 설명하는 것이 좋을까?
5. 실무적 관점: 한국도로공사 직원에게 실제로 도움이 되는 답변인가?
</think>

=== 참고 문서 ===
{context}

=== 사용자 질문 ===
{message}

=== 답변 지침 ===
1. <think> 태그 안에서 단계별 사고 과정을 상세히 기록하세요
2. 문서의 내용을 바탕으로 정확하고 실무적인 답변을 제공하세요
3. 불확실한 내용은 명확히 표시하고 추가 확인을 권하세요
4. 한국도로공사의 업무 특성을 반영한 전문적인 조언을 포함하세요

답변:"""
            else:
                prompt = f"""당신은 한국도로공사의 전문 AI 어시스턴트입니다.

<think>
단계별 분석을 수행하세요:
1. 질문의 핵심 파악: {message}
2. 도로공사 관련 지식 활용
3. 실무적 답변 구조화
4. 추가 도움 방안 제시
</think>

사용자 질문: {message}

도로, 교통, 고속도로와 관련된 전문 지식으로 도움이 되는 답변을 제공해주세요.

답변:"""
        else:
            # 일반 모드 프롬프트
            if relevant_docs:
                context = "\n".join([
                    f"📄 {doc['filename']} (관련도: {doc['score']:.2f})\n{doc['content']}" 
                    for doc in relevant_docs
                ])
                
                prompt = f"""당신은 한국도로공사의 전문 AI 어시스턴트입니다.

다음 문서 정보를 참고하여 사용자의 질문에 답변해주세요:

=== 참고 문서 ===
{context}

=== 사용자 질문 ===
{message}

=== 답변 지침 ===
1. 참고 문서의 내용을 바탕으로 정확하고 도움이 되는 답변을 제공하세요
2. 문서에 없는 내용은 일반적인 지식으로 보완하되, 추측이라고 명시하세요
3. 한국도로공사의 전문성을 살려 답변하세요
4. 친근하고 전문적인 톤을 유지하세요

답변:"""
            else:
                prompt = f"""당신은 한국도로공사의 전문 AI 어시스턴트입니다.

사용자 질문: {message}

현재 관련 문서가 없지만, 도로, 교통, 고속도로와 관련된 일반적인 지식으로 도움이 되는 답변을 제공해주세요.
한국도로공사의 전문성을 살려 친근하고 정확한 답변을 해주세요.

답변:"""
        
        # 3. 빠른 모드 또는 일반 모드로 응답 생성
        # standard 모드일 때 더 간단한 프롬프트 사용
        if mode == 'think':
            ai_response = query_ollama_streaming(prompt)
        else:
            # 더 간단한 프롬프트로 빠른 응답
            simple_prompt = f"한국도로공사 AI입니다. 간단히 답변하세요: {message}"
            ai_response = query_ollama_fast(simple_prompt)
        
        if not ai_response:
            if relevant_docs:
                ai_response = f"죄송합니다. AI 모델에 일시적인 문제가 있습니다.\n\n하지만 '{message}'와 관련된 문서 {len(relevant_docs)}개를 찾았습니다. 아래 출처를 참고해주세요."
            else:
                ai_response = f"안녕하세요! 한국도로공사 AI 어시스턴트입니다.\n'{message}'에 대해 도움을 드리고 싶지만, 현재 관련 문서가 없고 AI 모델에 일시적인 문제가 있습니다. 잠시 후 다시 시도해주세요."
        
        # Think 모드 응답 처리
        thinking_process = None
        if mode == 'think' and ai_response:
            if "<think>" in ai_response and "</think>" in ai_response:
                start_idx = ai_response.find("<think>") + len("<think>")
                end_idx = ai_response.find("</think>")
                thinking_process = ai_response[start_idx:end_idx].strip()
                ai_response = ai_response[ai_response.find("</think>") + len("</think>"):].strip()
        
        processing_time = time.time() - start_time
        
        # 4. 출처 정보 구성
        sources = []
        if relevant_docs:
            sources = [
                {
                    "title": doc["filename"],
                    "content_preview": doc["content"],
                    "relevance_score": round(doc["score"], 3),
                    "page": doc.get("page", 1),
                    "document_type": doc.get("document_type", "문서")
                }
                for doc in relevant_docs
            ]
        
        # 5. 로그 기록
        log_request('텍스트', user_id, f'모드: {mode}', 'success', f"{processing_time:.2f}초")
        
        response_data = {
            'reply': ai_response,
            'sources': sources,
            'status': 'success',
            'processing_time': f"{processing_time:.2f}초",
            'documents_found': len(relevant_docs),
            'mode': mode,
            'timestamp': datetime.now().isoformat()
        }
        
        # Think 모드인 경우 사고 과정 추가
        if thinking_process:
            response_data['thinking_process'] = thinking_process
        
        return jsonify(response_data)
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"❌ 텍스트 채팅 오류: {str(e)}")
        
        log_request('텍스트', request.remote_addr, '오류', 'error', f"{processing_time:.2f}초")
        
        return jsonify({
            'error': f'처리 중 오류가 발생했습니다: {str(e)}',
            'status': 'error',
            'processing_time': f"{processing_time:.2f}초"
        }), 500

@app.route('/api/chat_stream', methods=['POST'])
def chat_stream():
    """스트리밍 채팅 API"""
    def generate():
        try:
            data = request.json
            message = data.get('message', '').strip()
            mode = data.get('mode', 'standard')
            
            # 간단한 응답 생성
            if mode == 'think':
                prompt = f"<think>생각: {message}에 대해 분석</think>\n한국도로공사 AI입니다. {message}"
            else:
                prompt = f"한국도로공사 AI입니다. 간단히: {message}"
            
            # Ollama 스트리밍 호출
            payload = {
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 100,
                    "num_ctx": 256
                }
            }
            
            response = requests.post(OLLAMA_API_URL, json=payload, stream=True, timeout=30)
            
            for line in response.iter_lines():
                if line:
                    try:
                        json_line = json.loads(line.decode('utf-8'))
                        chunk = json_line.get("response", "")
                        if chunk:
                            yield f"data: {chunk}\n\n"
                        if json_line.get("done"):
                            break
                    except:
                        continue
                        
        except Exception as e:
            yield f"data: 오류가 발생했습니다: {str(e)}\n\n"
    
    return Response(generate(), mimetype='text/plain')

@app.route('/api/admin/dashboard_data', methods=['GET'])
def get_dashboard_data():
    """대시보드 실시간 데이터"""
    try:
        # GPU 상태
        gpu_info = []
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                device = f"cuda:{i}"
                memory_allocated = torch.cuda.memory_allocated(device)
                memory_total = torch.cuda.get_device_properties(device).total_memory
                
                gpu_info.append({
                    'device': device,
                    'memory_used_gb': memory_allocated / 1024**3,
                    'memory_total_gb': memory_total / 1024**3,
                    'utilization_percent': (memory_allocated / memory_total) * 100
                })
        
        # 시스템 통계
        total_requests = stats_data['total_requests']
        active_users = len(stats_data['active_users'])
        
        # 문서 통계
        document_count = 0
        if qdrant_client:
            try:
                collection_info = qdrant_client.get_collection("documents")
                document_count = collection_info.points_count
            except:
                pass
        
        return jsonify({
            'total_requests': total_requests,
            'active_users': active_users,
            'gpu_usage': gpu_info,
            'document_count': document_count,
            'target_document_count': 2199,
            'system_uptime': "99.8%",
            'upload_sessions': len(upload_sessions),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """시스템 통계 데이터 반환"""
    try:
        current_active = len(stats_data['active_users'])
        
        today = datetime.now()
        daily_data = {}
        for i in range(15):
            date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            daily_data[date] = stats_data['daily_usage'].get(date, 0)
        
        total = stats_data['total_requests']
        success_rate = (stats_data['successful_requests'] / total * 100) if total > 0 else 100
        
        return jsonify({
            'total_requests': stats_data['total_requests'],
            'successful_requests': stats_data['successful_requests'], 
            'failed_requests': stats_data['failed_requests'],
            'success_rate': f"{success_rate:.1f}%",
            'active_users': current_active,
            'daily_usage': daily_data,
            'recent_logs': stats_data['recent_logs'][:20],
            'gpu_usage_history': stats_data['gpu_usage_history'][-50:],
            'system_uptime': "99.7%",
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"통계 데이터 조회 오류: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """서버 상태 확인"""
    try:
        return jsonify({
            'status': 'healthy',
            'whisper_loaded': whisper_model is not None,
            'qdrant_connected': qdrant_client is not None,
            'embedding_model_loaded': embedding_model is not None,
            'torch_version': torch.__version__,
            'cuda_available': torch.cuda.is_available(),
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

@app.route('/api/qdrant_status', methods=['GET'])
def qdrant_status():
    """Qdrant 상태 확인 API"""
    try:
        if not qdrant_client:
            return jsonify({"status": "disconnected", "error": "클라이언트가 초기화되지 않음"})
        
        collections = qdrant_client.get_collections()
        collection_names = [col.name for col in collections.collections]
        
        if "documents" in collection_names:
            collection_info = qdrant_client.get_collection("documents")
            return jsonify({
                "status": "connected",
                "collection_exists": True,
                "points_count": collection_info.points_count,
                "vectors_count": collection_info.vectors_count
            })
        else:
            return jsonify({
                "status": "connected",
                "collection_exists": False,
                "error": "documents 컬렉션이 존재하지 않음"
            })
            
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/api/test', methods=['GET']) 
def test_endpoint():
    """테스트 엔드포인트"""
    return jsonify({
        "message": "EX-GPT 서버가 정상 작동 중입니다.", 
        "whisper_loaded": whisper_model is not None,
        "qdrant_connected": qdrant_client is not None,
        "embedding_loaded": embedding_model is not None,
        "endpoints": [
            "/api/chat",
            "/api/stats",
            "/api/health",
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

@app.route('/images/<path:filename>')
def serve_images(filename):
    """이미지 파일 서비스"""
    try:
        # 절대 경로로 이미지 디렉토리 지정
        image_directory = '/mnt/c/projects/ex-gpt-demo/images'
        return send_from_directory(image_directory, filename)
    except Exception as e:
        logger.error(f"이미지 서비스 오류 ({filename}): {e}")
        return jsonify({'error': f'Image not found: {filename}'}), 404
 
@app.route('/api/upload_voice', methods=['POST'])
def upload_voice():
    """음성 파일 업로드 및 STT 처리"""
    start_time = time.time()
    session_id = None
    
    try:
        # 파일 검증
        if 'audio' not in request.files:
            return jsonify({'error': '음성 파일이 없습니다.'}), 400
        
        file = request.files['audio']
        if file.filename == '':
            return jsonify({'error': '파일이 선택되지 않았습니다.'}), 400
        
        if not allowed_audio_file(file.filename):
            return jsonify({'error': f'지원되지 않는 파일 형식입니다.'}), 400
        
        user_id = request.form.get('user_id', request.remote_addr)
        process_type = request.form.get('type', 'transcribe')
        
        # 처리 세션 생성
        session_id = create_processing_session(user_id)
        
        logger.info(f"🎤 음성 파일 업로드: {file.filename} (세션: {session_id})")
        
        # 임시 파일 저장
        temp_dir = tempfile.mkdtemp()
        filename = secure_filename(file.filename)
        temp_file_path = os.path.join(temp_dir, filename)
        file.save(temp_file_path)
        
        update_processing_session(session_id, 'uploading', 20, '파일 업로드 완료')
        
        try:
            # 오디오 전처리
            update_processing_session(session_id, 'preprocessing', 40, '오디오 전처리 중...')
            processed_audio_path = preprocess_audio(temp_file_path)
            
            # STT 수행
            update_processing_session(session_id, 'transcribing', 60, '음성 인식 중...')
            transcription_result = transcribe_audio(processed_audio_path)
            
            if not transcription_result:
                raise Exception('STT 처리에 실패했습니다.')
            
            # 후처리
            update_processing_session(session_id, 'processing', 80, f'{process_type} 처리 중...')
            processed_result = process_transcription(transcription_result, process_type)
            
            processing_time = time.time() - start_time
            
            # 결과 구성
            final_result = {
                'status': 'success',
                'transcription': transcription_result,
                'processed_content': processed_result,
                'processing_time': f"{processing_time:.2f}초",
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            }
            
            update_processing_session(session_id, 'completed', 100, '처리 완료', final_result)
            
            # 로그 기록
            log_request('음성', user_id, f'STT-{process_type}', 'success', f"{processing_time:.2f}초")
            
            return jsonify(final_result)
            
        finally:
            # 임시 파일 정리
            try:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                if processed_audio_path and os.path.exists(processed_audio_path):
                    os.remove(processed_audio_path)
                if os.path.exists(temp_dir):
                    os.rmdir(temp_dir)
            except Exception as e:
                logger.warning(f"임시 파일 정리 실패: {e}")
                
    except Exception as e:
        processing_time = time.time() - start_time
        error_message = f'음성 처리 중 오류가 발생했습니다: {str(e)}'
        
        logger.error(f"❌ 음성 처리 오류: {str(e)}")
        
        if session_id:
            update_processing_session(session_id, 'error', 0, error_message)
        
        log_request('음성', request.remote_addr, 'STT 오류', 'error', f"{processing_time:.2f}초")
        
        return jsonify({
            'error': error_message,
            'status': 'error',
            'processing_time': f"{processing_time:.2f}초",
            'session_id': session_id
        }), 500

@app.route('/api/audio_progress/<session_id>', methods=['GET'])
def get_audio_progress(session_id):
    """오디오 처리 진행률 조회"""
    session = audio_processing_sessions.get(session_id)
    if not session:
        return jsonify({'error': '세션을 찾을 수 없습니다.'}), 404
    
    return jsonify({
        'session_id': session_id,
        'status': session['status'],
        'progress': session['progress'],
        'message': session['message'],
        'timestamp': session.get('updated_at', session['created_at']).isoformat()
    })
    
def preprocess_audio(audio_path):
    """오디오 전처리 (노이즈 제거, 포맷 변환 등)"""
    try:
        logger.info("🔧 오디오 전처리 시작...")
        
        # 오디오 로드
        audio = AudioSegment.from_file(audio_path)
        
        # 스테레오를 모노로 변환
        if audio.channels > 1:
            audio = audio.set_channels(1)
        
        # 샘플레이트 16kHz로 변환 (Whisper 최적화)
        audio = audio.set_frame_rate(16000)
        
        # 볼륨 정규화
        audio = audio.normalize()
        
        # 무음 제거
        chunks = split_on_silence(
            audio,
            min_silence_len=500,  # 0.5초 이상 무음
            silence_thresh=audio.dBFS - 16,
            keep_silence=250  # 0.25초 무음 유지
        )
        
        if chunks:
            audio = sum(chunks)
        
        # 전처리된 오디오 저장
        processed_path = audio_path.replace('.', '_processed.')
        if not processed_path.endswith('.wav'):
            processed_path = processed_path.rsplit('.', 1)[0] + '.wav'
        
        audio.export(processed_path, format="wav")
        
        # 노이즈 리덕션 (선택적)
        try:
            import librosa
            y, sr = librosa.load(processed_path, sr=16000)
            y_reduced = nr.reduce_noise(y=y, sr=sr, prop_decrease=0.8)
            
            # 다시 저장
            import soundfile as sf
            sf.write(processed_path, y_reduced, sr)
            
        except Exception as e:
            logger.warning(f"노이즈 리덕션 실패: {e}")
        
        logger.info("✅ 오디오 전처리 완료")
        return processed_path
        
    except Exception as e:
        logger.error(f"오디오 전처리 오류: {e}")
        return audio_path  # 전처리 실패 시 원본 반환

# Flask 앱 시작 시 모델 초기화
def initialize_app_with_audio():
    """Flask 앱 시작 시 호출할 초기화 함수"""
    logger.info("🎤 음성 처리 시스템 초기화 시작...")
    
    # CUDA 환경 확인
    if torch.cuda.is_available():
        logger.info(f"✅ CUDA 사용 가능: {torch.cuda.get_device_name()}")
        logger.info(f"📊 GPU 메모리: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")
    else:
        logger.info("💻 CPU 모드로 실행")
    
    # 오디오 모델들 초기화
    success = initialize_audio_models()
    
    if success:
        logger.info("🎉 음성 처리 시스템 초기화 완료!")
        return True
    else:
        logger.error("❌ 음성 처리 시스템 초기화 실패!")
        return False

# 메모리 관리 함수
def cleanup_gpu_memory():
    """GPU 메모리 정리"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        gc.collect()
        logger.info("🧹 GPU 메모리 정리 완료")

logger.info("🎤 CUDA 호환 음성 처리 모듈 로드 완료")

def transcribe_audio(audio_path):
    """Whisper를 사용한 음성 인식"""
    try:
        if not whisper_model:
            raise Exception("Whisper 모델이 로드되지 않았습니다.")
        
        logger.info("🎯 Whisper STT 실행...")
        
        # Whisper 옵션 설정
        options = {
            "language": "ko",  # 한국어 우선
            "task": "transcribe",
            "fp16": torch.cuda.is_available(),  # GPU 사용 시 FP16
            "temperature": 0,  # 더 정확한 결과를 위해
            "best_of": 2,
            "beam_size": 5,
            "patience": 1.0,
            "length_penalty": -0.05,
            "suppress_tokens": "-1",
            "initial_prompt": "안녕하세요. 한국도로공사입니다."  # 컨텍스트 힌트
        }
        
        # STT 수행
        result = whisper_model.transcribe(audio_path, **options)
        
        # 결과 검증
        text = result.get("text", "").strip()
        if not text:
            raise Exception("음성을 인식할 수 없습니다.")
        
        # 언어 감지 결과 로깅
        detected_language = result.get("language", "unknown")
        logger.info(f"🌐 감지된 언어: {detected_language}")
        
        if detected_language != "ko" and detected_language != "korean":
            logger.warning(f"⚠️ 한국어가 아닌 언어가 감지되었습니다: {detected_language}")
        
        logger.info(f"✅ STT 완료: {len(text)}자")
        return text
        
    except Exception as e:
        logger.error(f"STT 처리 오류: {e}")
        return None

def process_transcription(text, process_type):
    """STT 결과 후처리"""
    try:
        if process_type == "transcribe":
            # 단순 전사
            return format_transcription(text)
            
        elif process_type == "summarize":
            # 요약 처리
            return summarize_text(text)
            
        elif process_type == "analyze":
            # 분석 처리
            return analyze_speech_content(text)
            
        else:
            return format_transcription(text)
            
    except Exception as e:
        logger.error(f"후처리 오류: {e}")
        return format_transcription(text)

def format_transcription(text):
    """전사 텍스트 포맷팅"""
    # 기본 포맷팅
    formatted = text.strip()
    
    # 문장 부호 추가
    if formatted and not formatted.endswith(('.', '!', '?')):
        formatted += '.'
    
    # 줄바꿈 처리
    sentences = formatted.split('. ')
    if len(sentences) > 3:
        formatted = '. '.join(sentences[:len(sentences)//2]) + '.\n\n' + '. '.join(sentences[len(sentences)//2:])
    
    return formatted

def summarize_text(text):
    """텍스트 요약"""
    try:
        # Ollama를 사용한 요약
        prompt = f"""다음 음성 전사 내용을 요약해주세요:

원본 내용:
{text}

요약 지침:
1. 핵심 내용만 간단히 정리
2. 중요한 키워드 포함
3. 3-5문장으로 요약
4. 한국도로공사 업무와 관련된 내용이면 더 자세히

요약:"""

        summary = query_ollama_fast(prompt)
        if summary:
            return f"📝 **요약**\n\n{summary}\n\n---\n\n📄 **원본 전사**\n\n{format_transcription(text)}"
        else:
            return format_transcription(text)
            
    except Exception as e:
        logger.error(f"요약 처리 오류: {e}")
        return format_transcription(text)

def analyze_speech_content(text):
    """음성 내용 분석"""
    try:
        # 분석 프롬프트
        prompt = f"""다음 음성 전사 내용을 분석해주세요:

전사 내용:
{text}

분석 항목:
1. 주요 주제
2. 핵심 키워드
3. 감정/톤
4. 액션 아이템 (있다면)
5. 한국도로공사 업무 관련성

분석 결과:"""

        analysis = query_ollama_fast(prompt)
        if analysis:
            return f"🔍 **음성 내용 분석**\n\n{analysis}\n\n---\n\n📄 **원본 전사**\n\n{format_transcription(text)}"
        else:
            return format_transcription(text)
            
    except Exception as e:
        logger.error(f"분석 처리 오류: {e}")
        return format_transcription(text)

def get_audio_duration(audio_path):
    """오디오 파일 길이 반환"""
    try:
        audio = AudioSegment.from_file(audio_path)
        return round(len(audio) / 1000.0, 1)  # 초 단위
    except:
        return 0.0

# 실시간 음성 처리를 위한 WebSocket 지원 (선택사항)
@app.route('/api/voice_stream', methods=['POST'])
def voice_stream():
    """실시간 음성 스트리밍 처리"""
    try:
        # 실시간 음성 데이터 처리
        # 구현 시 WebSocket이나 Server-Sent Events 사용 권장
        return jsonify({"message": "실시간 음성 처리는 WebSocket으로 구현 예정"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
# 주기적 정리 작업
def cleanup_old_data():
    """오래된 데이터 정리"""
    if len(stats_data['recent_logs']) > 1000:
        stats_data['recent_logs'] = stats_data['recent_logs'][:500]
    
    if len(stats_data['gpu_usage_history']) > 2000:
        stats_data['gpu_usage_history'] = stats_data['gpu_usage_history'][-1000:]
    
    # 활성 사용자 목록 정리
    stats_data['active_users'].clear()

def periodic_cleanup():
    """주기적 정리 실행"""
    while True:
        time.sleep(3600)  # 1시간마다
        cleanup_old_data()

# ============================================================================
# STEP 5: 메인 실행 부분 수정
# ============================================================================

# 기존 메인 실행 부분을 찾아서 수정하세요:

if __name__ == '__main__':
    logger.info("🚀 EX-GPT 서버 시작...")
    
    # 1. CUDA 환경 검증
    if torch.cuda.is_available():
        logger.info(f"✅ CUDA 사용 가능: {torch.cuda.get_device_name()}")
    else:
        logger.warning("⚠️ CUDA를 사용할 수 없습니다. CPU 모드로 실행합니다.")
    
    # 2. Qdrant 초기화
    logger.info("🔗 Qdrant 초기화...")
    qdrant_client = initialize_qdrant()
    if qdrant_client:
        logger.info("✅ Qdrant 준비 완료")
    else:
        logger.warning("⚠️ Qdrant 초기화 실패. 문서 검색 기능이 제한됩니다.")

    # 3. 음성 처리 모델 초기화 (새로 추가)
    logger.info("🎤 음성 처리 모델 초기화...")
    audio_success = initialize_audio_models()
    if audio_success:
        logger.info("✅ 음성 처리 준비 완료")
    else:
        logger.warning("⚠️ 음성 처리 초기화 실패. STT 기능이 제한됩니다.")
    
    # 4. 정리 작업 시작
    cleanup_thread = threading.Thread(target=periodic_cleanup, daemon=True)
    cleanup_thread.start()
    
    logger.info("🎉 모든 시스템 준비 완료!")
    logger.info("📍 서버 주소: http://localhost:5001")
    logger.info("📊 관리자: http://localhost:5001/admin")
    logger.info("🔍 기능:")
    logger.info("   - ✅ 실시간 Ollama LLM 연동")
    logger.info("   - ✅ Qdrant 문서 검색")
    logger.info("   - ✅ 음성 인식 및 요약")  # 새로 추가
    
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)