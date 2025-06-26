from transformers import AutoProcessor, AutoModelForCausalLM

print("Florence-2-large 모델 다운로드 시작...")

# 모델 다운로드 (로드는 안하고 캐시에만 저장)
model = AutoModelForCausalLM.from_pretrained(
    "microsoft/Florence-2-large",
    trust_remote_code=True
)

processor = AutoProcessor.from_pretrained(
    "microsoft/Florence-2-large", 
    trust_remote_code=True
)

print("다운로드 완료!")
print("모델 파일 위치: ~/.cache/huggingface/hub/")