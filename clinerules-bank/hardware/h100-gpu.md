# H100 GPU 최적화 규칙

## 메모리 관리
```python
class H100MemoryManager:
    def __init__(self):
        self.device_count = 8  # H100 8장
        self.memory_threshold = 0.8  # 80% 사용률 제한
    
    def allocate_model(self, model_size: str):
        # 모델 크기에 따른 GPU 할당
        if model_size == "235B":  # QWen3
            return self.allocate_multiple_gpus(6)  # 6장 사용
        elif model_size == "70B":  # Llama3
            return self.allocate_multiple_gpus(2)  # 2장 사용

드라이버 호환성

최소 NVIDIA 드라이버: 550
QWen3 권장: 570 이상
CUDA 버전: 12.1+

모니터링

GPU 사용률 실시간 추적
온도 모니터링 (85°C 이하)
메모리 누수 방지 코드 필수

          