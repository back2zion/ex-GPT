#!/usr/bin/env python3
"""
Hugging Face 빠른 로그인 스크립트
"""

def quick_login():
    """Hugging Face에 로그인"""
    print("=== Hugging Face 로그인 ===")
    print("1. https://huggingface.co/settings/tokens 방문")
    print("2. 'New token' 클릭")
    print("3. 'Read' 권한으로 토큰 생성")
    print("4. 생성된 토큰을 복사")
    print()
    
    try:
        from huggingface_hub import login
        token = input("토큰을 여기에 붙여넣기: ").strip()
        
        if not token:
            print("❌ 토큰이 입력되지 않았습니다.")
            return False
            
        login(token=token)
        
        # 로그인 확인
        from huggingface_hub import HfApi
        api = HfApi()
        user = api.whoami()
        
        print(f"✅ 로그인 성공!")
        print(f"사용자: {user['name']}")
        print(f"이메일: {user.get('email', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 로그인 실패: {e}")
        print("\n해결방법:")
        print("- 토큰이 올바른지 확인")
        print("- 토큰에 'Read' 권한이 있는지 확인")
        print("- 인터넷 연결 확인")
        return False

def check_login():
    """현재 로그인 상태 확인"""
    try:
        from huggingface_hub import HfApi
        api = HfApi()
        user = api.whoami()
        print(f"✅ 이미 로그인됨: {user['name']}")
        return True
    except:
        print("❌ 로그인되지 않음")
        return False

if __name__ == "__main__":
    if not check_login():
        quick_login()
    else:
        choice = input("다시 로그인하시겠습니까? (y/n): ")
        if choice.lower() == 'y':
            quick_login()