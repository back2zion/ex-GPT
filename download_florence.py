import torch
from transformers import AutoProcessor, AutoModelForCausalLM
import os

def download_florence_model():
    print("Florence-2-large 모델 다운로드 시작...")
    
    # 모델 저장 경로 설정
    model_path = "./models/florence-2-large"
    os.makedirs(model_path, exist_ok=True)
    
    try:
        # 프로세서 다운로드
        print("1. 프로세서 다운로드 중...")
        processor = AutoProcessor.from_pretrained(
            "microsoft/Florence-2-large",
            trust_remote_code=True,
            cache_dir=model_path
        )
        print("✅ 프로세서 다운로드 완료")
        
        # 모델 다운로드
        print("2. 모델 다운로드 중... (시간이 오래 걸릴 수 있습니다)")
        model = AutoModelForCausalLM.from_pretrained(
            "microsoft/Florence-2-large",
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            trust_remote_code=True,
            cache_dir=model_path
        )
        print("✅ 모델 다운로드 완료")
        
        # 다운로드 확인
        print("3. 다운로드 확인 중...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = model.to(device)
        
        print(f"✅ 모델이 {device}에 성공적으로 로드되었습니다")
        print(f"📁 모델 저장 위치: {model_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return False

if __name__ == "__main__":
    success = download_florence_model()
    if success:
        print("\n🎉 Florence-2-large 모델 설치 완료!")
    else:
        print("\n💥 모델 설치 실패. 네트워크 연결과 디스크 공간을 확인하세요.")