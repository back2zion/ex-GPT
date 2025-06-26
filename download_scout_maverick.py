import os
from transformers import AutoProcessor, Llama4ForConditionalGeneration
import torch

# D드라이브에 캐시 디렉토리 설정
cache_dir = "D:/huggingface_cache"
os.makedirs(cache_dir, exist_ok=True)

# 환경변수로 캐시 디렉토리 설정
os.environ['HF_HOME'] = cache_dir
os.environ['TRANSFORMERS_CACHE'] = cache_dir

print("=== Llama-4 Scout & Maverick 다운로드 ===")
print(f"저장 위치: {cache_dir}")
print("Scout (16E): 약 25-30GB")
print("Maverick (128E): 약 35-40GB")
print("총합: 약 60-70GB 필요")

# 다운로드할 모델들
models = {
    "Scout": "meta-llama/Llama-4-Scout-17B-16E-Instruct",
    "Maverick": "meta-llama/Llama-4-Maverick-17B-128E-Instruct"
}

def download_model(model_name, model_id):
    print(f"\n{'='*50}")
    print(f"다운로드 시작: {model_name}")
    print(f"모델 ID: {model_id}")
    print(f"{'='*50}")
    
    try:
        # 1. 프로세서 다운로드
        print(f"\n1. {model_name} 프로세서 다운로드 중...")
        processor = AutoProcessor.from_pretrained(
            model_id,
            cache_dir=cache_dir,
            trust_remote_code=True
        )
        print(f"✓ {model_name} 프로세서 완료")
        
        # 2. 모델 다운로드
        print(f"\n2. {model_name} 모델 다운로드 중...")
        print("   이 단계가 가장 오래 걸립니다...")
        
        model = Llama4ForConditionalGeneration.from_pretrained(
            model_id,
            cache_dir=cache_dir,
            torch_dtype=torch.bfloat16,
            trust_remote_code=True,
            device_map=None,  # 로드하지 않고 다운로드만
            low_cpu_mem_usage=True
        )
        print(f"✓ {model_name} 모델 완료")
        
        return True
        
    except Exception as e:
        print(f"❌ {model_name} 다운로드 실패: {e}")
        return False

def check_login():
    """Hugging Face 로그인 상태 확인"""
    try:
        from huggingface_hub import HfApi
        api = HfApi()
        whoami = api.whoami()
        print(f"✓ 로그인된 사용자: {whoami['name']}")
        return True
    except Exception:
        print("❌ Hugging Face 로그인이 필요합니다!")
        print("\n해결방법:")
        print("1. pip install huggingface_hub")
        print("2. huggingface-cli login")
        print("3. 또는 python -c \"from huggingface_hub import login; login()\"")
        print("\n라이센스 동의도 필요합니다:")
        print("- https://huggingface.co/meta-llama/Llama-4-Scout-17B-16E-Instruct")
        print("- https://huggingface.co/meta-llama/Llama-4-Maverick-17B-128E-Instruct")
        return False

def get_folder_size(folder_path):
    """폴더 크기 계산"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                total_size += os.path.getsize(filepath)
            except:
                pass
    return total_size

# 메인 실행
if __name__ == "__main__":
    print("로그인 상태 확인 중...")
    if not check_login():
        exit()
    
    print(f"\nD드라이브 여유 공간 확인...")
    import shutil
    free_space = shutil.disk_usage("D:/").free / (1024**3)
    print(f"D드라이브 여유 공간: {free_space:.1f} GB")
    
    if free_space < 70:
        print("⚠️  여유 공간이 부족할 수 있습니다. (70GB 권장)")
        response = input("계속하시겠습니까? (y/n): ")
        if response.lower() != 'y':
            exit()
    
    success_count = 0
    
    # 모델별 다운로드
    for model_name, model_id in models.items():
        print(f"\n{model_name} 다운로드를 시작할까요?")
        choice = input(f"{model_name} 다운로드? (y/n): ")
        
        if choice.lower() == 'y':
            if download_model(model_name, model_id):
                success_count += 1
                print(f"✅ {model_name} 다운로드 완료!")
            else:
                print(f"❌ {model_name} 다운로드 실패!")
        else:
            print(f"⏭️  {model_name} 스킵")
    
    # 최종 결과
    print(f"\n{'='*50}")
    print("다운로드 완료 요약")
    print(f"{'='*50}")
    print(f"성공: {success_count}/{len(models)} 모델")
    
    # 다운로드된 총 크기 확인
    total_size = get_folder_size(cache_dir)
    print(f"총 다운로드 크기: {total_size / (1024**3):.2f} GB")
    print(f"저장 위치: {cache_dir}")
    
    if success_count > 0:
        print("\n✅ 이제 D드라이브에서 오프라인으로 모델 사용 가능!")
        print("\n사용 예시:")
        for model_name, model_id in models.items():
            print(f"# {model_name}")
            print(f"model = Llama4ForConditionalGeneration.from_pretrained('{model_id}', cache_dir='{cache_dir}')")
    
    print("\n완료!")