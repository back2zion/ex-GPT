import os

# D드라이브에 캐시 디렉토리 설정
cache_dir = "D:/huggingface_cache"
os.makedirs(cache_dir, exist_ok=True)

# 환경변수로 캐시 디렉토리 설정
os.environ['HF_HOME'] = cache_dir
os.environ['TRANSFORMERS_CACHE'] = cache_dir

print("=== 모델 다운로드 스크립트 ===")
print(f"저장 위치: {cache_dir}")

def download_model_files_only(model_id, model_name):
    """모델 파일만 다운로드 (로드하지 않음)"""
    print(f"\n{model_name} 다운로드 중...")
    try:
        from huggingface_hub import snapshot_download
        
        # 모델 파일들만 다운로드
        snapshot_download(
            repo_id=model_id,
            cache_dir=cache_dir,
            resume_download=True,
            local_files_only=False
        )
        print(f"✅ {model_name} 다운로드 완료!")
        return True
        
    except Exception as e:
        print(f"❌ {model_name} 다운로드 실패: {e}")
        if "gated" in str(e).lower():
            print(f"   라이센스 동의가 필요합니다: https://huggingface.co/{model_id}")
        return False

def login_huggingface():
    """Hugging Face 로그인"""
    try:
        from huggingface_hub import login
        token = input("Hugging Face 토큰을 입력하세요 (https://huggingface.co/settings/tokens에서 생성): ")
        login(token=token)
        print("✅ 로그인 성공!")
        return True
    except Exception as e:
        print(f"❌ 로그인 실패: {e}")
        return False

def check_login_status():
    """로그인 상태 확인"""
    try:
        from huggingface_hub import HfApi
        api = HfApi()
        user = api.whoami()
        print(f"✅ 로그인됨: {user['name']}")
        return True
    except:
        print("❌ 로그인 필요")
        return False

# 다운로드할 모델 목록
models = {
    "Florence-2-large": "microsoft/Florence-2-large",
    "Llama-4-Scout": "meta-llama/Llama-4-Scout-17B-16E-Instruct", 
    "Llama-4-Maverick": "meta-llama/Llama-4-Maverick-17B-128E-Instruct"
}

if __name__ == "__main__":
    print("로그인 상태 확인...")
    
    if not check_login_status():
        print("\n로그인이 필요합니다.")
        choice = input("로그인하시겠습니까? (y/n): ")
        if choice.lower() == 'y':
            if not login_huggingface():
                print("로그인에 실패했습니다. 수동으로 로그인하세요:")
                print("python -c \"from huggingface_hub import login; login()\"")
                exit()
        else:
            print("Llama 모델은 로그인이 필요합니다.")
    
    print(f"\n다운로드할 모델을 선택하세요:")
    for i, (name, model_id) in enumerate(models.items(), 1):
        print(f"{i}. {name}")
    
    choice = input("\n번호를 입력하세요 (예: 1,2,3 또는 all): ")
    
    if choice.lower() == "all":
        selected_models = list(models.items())
    else:
        try:
            numbers = [int(x.strip()) for x in choice.split(",")]
            selected_models = [list(models.items())[i-1] for i in numbers if 1 <= i <= len(models)]
        except:
            print("잘못된 입력입니다.")
            exit()
    
    print(f"\n선택된 모델: {[name for name, _ in selected_models]}")
    
    # D드라이브 공간 확인
    import shutil
    free_space = shutil.disk_usage("D:/").free / (1024**3)
    print(f"D드라이브 여유 공간: {free_space:.1f} GB")
    
    # 다운로드 실행
    success_count = 0
    for model_name, model_id in selected_models:
        if download_model_files_only(model_id, model_name):
            success_count += 1
    
    print(f"\n=== 완료 ===")
    print(f"성공: {success_count}/{len(selected_models)}")
    print(f"저장 위치: {cache_dir}")
    
    if success_count > 0:
        print("\n✅ 다운로드된 모델은 다음과 같이 사용할 수 있습니다:")
        print(f"cache_dir = '{cache_dir}'")
        print("model = AutoModelForCausalLM.from_pretrained(model_id, cache_dir=cache_dir)")