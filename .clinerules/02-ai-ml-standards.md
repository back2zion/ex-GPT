# AI/ML 모델 개발 표준

## 모델 관리
### 지원 모델 스택
- LLM: Qwen3-235B-A22B (primary), Llama3-70B (fallback)
- Embedding: paraphrase-multilingual-MiniLM-L12-v2
- STT: OpenAI Whisper Large-v3
- Vector DB: Qdrant

### 모델 로딩 패턴
```python
class ModelManager:
    def __init__(self):
        self.models = {}
        self.device_allocator = GPUDeviceAllocator()
    
    def load_model(self, model_type: str, device: str = "auto"):
        # 모델 로딩 로직
        pass