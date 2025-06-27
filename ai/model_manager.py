"""
AI 모델 통합 관리 시스템
한국도로공사 ex-GPT H100 GPU 최적화

Author: NeoAli AI팀
Date: 2025-06-27
"""

import torch
import gc
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Optional, List
import logging
from dataclasses import dataclass
import time

# 한국어 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ai_model_manager.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class GPUStatus:
    """GPU 상태 정보"""
    device_id: int
    memory_used: float
    memory_total: float
    temperature: float
    utilization: float
    is_available: bool

class H100MemoryManager:
    """H100 GPU 메모리 관리자
    
    한국도로공사 H100 8장 클러스터 최적화
    - QWen3-235B-A22B: 6 GPU 사용
    - Llama3-70B: 2 GPU 사용
    """
    
    def __init__(self):
        self.device_count = torch.cuda.device_count() if torch.cuda.is_available() else 0
        self.memory_threshold = 0.8  # 80% 사용률 제한
        self.temperature_threshold = 85  # 85°C 온도 제한
        self.allocated_devices = {}
        self.lock = threading.Lock()
        
        logger.info(f"H100 GPU 감지됨: {self.device_count}장")
    
    def get_gpu_status(self) -> List[GPUStatus]:
        """모든 GPU 상태 조회"""
        gpu_statuses = []
        
        for i in range(self.device_count):
            try:
                # GPU 메모리 정보
                memory_info = torch.cuda.mem_get_info(i)
                memory_free = memory_info[0] / 1024**3  # GB
                memory_total = memory_info[1] / 1024**3  # GB
                memory_used = memory_total - memory_free
                
                # GPU 사용률 (근사치)
                utilization = torch.cuda.utilization(i) if hasattr(torch.cuda, 'utilization') else 0
                
                # 온도 정보 (nvidia-ml-py 필요시 추가)
                temperature = 70  # 기본값 (실제 구현시 nvidia-ml-py 사용)
                
                gpu_status = GPUStatus(
                    device_id=i,
                    memory_used=memory_used,
                    memory_total=memory_total,
                    temperature=temperature,
                    utilization=utilization,
                    is_available=memory_used/memory_total < self.memory_threshold and temperature < self.temperature_threshold
                )
                
                gpu_statuses.append(gpu_status)
                
            except Exception as e:
                logger.error(f"GPU {i} 상태 조회 실패: {e}")
                
        return gpu_statuses
    
    def allocate_gpus(self, model_size: str, required_gpus: int) -> List[int]:
        """모델 크기에 따른 GPU 할당
        
        Args:
            model_size: 모델 크기 (235B, 70B, 8B 등)
            required_gpus: 필요한 GPU 수
            
        Returns:
            할당된 GPU 디바이스 ID 리스트
        """
        with self.lock:
            gpu_statuses = self.get_gpu_status()
            available_gpus = [gpu for gpu in gpu_statuses if gpu.is_available]
            
            if len(available_gpus) < required_gpus:
                raise RuntimeError(f"사용 가능한 GPU 부족: 필요 {required_gpus}장, 사용가능 {len(available_gpus)}장")
            
            # 메모리 사용량이 적은 순으로 정렬
            available_gpus.sort(key=lambda x: x.memory_used)
            allocated_devices = [gpu.device_id for gpu in available_gpus[:required_gpus]]
            
            # 할당 기록
            self.allocated_devices[model_size] = allocated_devices
            
            logger.info(f"{model_size} 모델용 GPU 할당: {allocated_devices}")
            return allocated_devices
    
    def release_gpus(self, model_size: str):
        """GPU 메모리 해제"""
        with self.lock:
            if model_size in self.allocated_devices:
                devices = self.allocated_devices[model_size]
                for device_id in devices:
                    torch.cuda.empty_cache()
                    torch.cuda.synchronize(device_id)
                
                del self.allocated_devices[model_size]
                logger.info(f"{model_size} 모델 GPU 메모리 해제 완료: {devices}")

class ModelManager:
    """AI 모델 통합 관리자
    
    한국도로공사 요구사항:
    - 비동기 처리 (ThreadPoolExecutor)
    - 타임아웃 설정
    - 한국어 에러 메시지
    - GPU 메모리 관리
    """
    
    def __init__(self):
        self.models = {}
        self.memory_manager = H100MemoryManager()
        self.executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="AI-Worker")
        self.model_configs = {
            "qwen3-235b-a22b": {"gpus": 6, "timeout": 30},
            "llama3-70b": {"gpus": 2, "timeout": 20},
            "qwen3-8b": {"gpus": 1, "timeout": 10}
        }
        
        logger.info("AI 모델 관리자 초기화 완료")
    
    def load_model(self, model_type: str, model_name: str, device: str = "auto") -> bool:
        """모델 로딩
        
        Args:
            model_type: 모델 타입 (llm, embedding, stt, vector)
            model_name: 모델명
            device: 디바이스 설정 (auto, cpu, cuda)
            
        Returns:
            로딩 성공 여부
        """
        try:
            # GPU 할당
            if device == "auto" and torch.cuda.is_available():
                if model_name in self.model_configs:
                    required_gpus = self.model_configs[model_name]["gpus"]
                    allocated_gpus = self.memory_manager.allocate_gpus(model_name, required_gpus)
                    device = f"cuda:{allocated_gpus[0]}"  # 주 GPU 설정
            
            # 모델별 로딩 로직 (실제 구현시 각 모델 매니저 호출)
            if model_type == "llm":
                from ai.llm.qwen3_manager import Qwen3Manager
                from ai.llm.llama3_manager import Llama3Manager
                
                if "qwen3" in model_name.lower():
                    manager = Qwen3Manager()
                elif "llama3" in model_name.lower():
                    manager = Llama3Manager()
                else:
                    raise ValueError(f"지원하지 않는 LLM 모델: {model_name}")
                    
            elif model_type == "embedding":
                from ai.embedding.multilingual_manager import MultilingualManager
                manager = MultilingualManager()
                
            elif model_type == "stt":
                from ai.stt.whisper_manager import WhisperManager
                manager = WhisperManager()
                
            elif model_type == "vector":
                from ai.vector.qdrant_manager import QdrantManager
                manager = QdrantManager()
                
            else:
                raise ValueError(f"지원하지 않는 모델 타입: {model_type}")
            
            # 모델 로딩 실행
            success = manager.load(model_name, device)
            if success:
                self.models[f"{model_type}_{model_name}"] = manager
                logger.info(f"{model_type} 모델 로딩 성공: {model_name}")
            else:
                logger.error(f"{model_type} 모델 로딩 실패: {model_name}")
                
            return success
            
        except Exception as e:
            logger.error(f"모델 로딩 중 오류 발생: {e}")
            return False
    
    def unload_model(self, model_type: str, model_name: str):
        """모델 언로딩 및 메모리 해제"""
        model_key = f"{model_type}_{model_name}"
        
        if model_key in self.models:
            try:
                # 모델 언로딩
                self.models[model_key].unload()
                del self.models[model_key]
                
                # GPU 메모리 해제
                self.memory_manager.release_gpus(model_name)
                
                # 가비지 컬렉션
                gc.collect()
                torch.cuda.empty_cache()
                
                logger.info(f"모델 언로딩 완료: {model_key}")
                
            except Exception as e:
                logger.error(f"모델 언로딩 중 오류: {e}")
    
    def get_model(self, model_type: str, model_name: str):
        """모델 인스턴스 반환"""
        model_key = f"{model_type}_{model_name}"
        return self.models.get(model_key)
    
    def health_check(self) -> Dict[str, Any]:
        """시스템 상태 점검"""
        gpu_statuses = self.memory_manager.get_gpu_status()
        
        return {
            "timestamp": time.time(),
            "loaded_models": list(self.models.keys()),
            "gpu_count": self.memory_manager.device_count,
            "gpu_statuses": [
                {
                    "device_id": gpu.device_id,
                    "memory_used_gb": round(gpu.memory_used, 2),
                    "memory_total_gb": round(gpu.memory_total, 2),
                    "memory_usage_percent": round(gpu.memory_used/gpu.memory_total*100, 1),
                    "temperature": gpu.temperature,
                    "is_available": gpu.is_available
                }
                for gpu in gpu_statuses
            ],
            "system_memory_gb": round(psutil.virtual_memory().total / 1024**3, 2),
            "system_memory_usage_percent": psutil.virtual_memory().percent
        }
    
    def __del__(self):
        """소멸자 - 리소스 정리"""
        try:
            self.executor.shutdown(wait=True)
            for model_key in list(self.models.keys()):
                model_type, model_name = model_key.split('_', 1)
                self.unload_model(model_type, model_name)
        except:
            pass

# 전역 모델 관리자 인스턴스
model_manager = ModelManager()
