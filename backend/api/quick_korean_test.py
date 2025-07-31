import requests
import time

print("🇰🇷 한글 인코딩 빠른 테스트")
print("=" * 40)

# 서버 준비 시간
time.sleep(2)

try:
    # 노트북 검색 테스트
    print("📱 노트북 검색 테스트...")
    response = requests.get("http://127.0.0.1:5001/api/11st/search?keyword=노트북&limit=1", timeout=15)
    
    print(f"상태 코드: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ API 호출 성공!")
        
        if data.get('products') and len(data['products']) > 0:
            product = data['products'][0]
            print("\n📦 상품 정보 (한글 확인):")
            print(f"상품명: {product.get('name', 'N/A')}")
            print(f"브랜드: {product.get('brand', 'N/A')}")
            print(f"소스: {product.get('source', 'N/A')}")
            
            # 한글 정상 표시 확인
            name = product.get('name', '')
            if any(ord(char) > 127 for char in name):  # 한글 문자 포함 확인
                print("\n🎉 한글 인코딩 정상!")
            else:
                print("\n⚠️ 한글 확인 필요")
        else:
            print("⚠️ 상품 데이터 없음")
    else:
        print(f"❌ 오류: {response.text}")

except Exception as e:
    print(f"❌ 테스트 오류: {e}")

print("\n" + "=" * 40)
print("테스트 완료!")