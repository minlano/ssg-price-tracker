import requests
import json

print("🇰🇷 한글 인코딩 테스트")
print("=" * 40)

try:
    # 노트북 검색 테스트
    response = requests.get("http://127.0.0.1:5001/api/11st/search?keyword=노트북&limit=2", timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ API 호출 성공!")
        print(f"총 상품: {data.get('total', 0)}개")
        
        if data.get('products'):
            first_product = data['products'][0]
            print("\n📱 첫 번째 상품 (한글 표시 확인):")
            print(f"상품명: {first_product.get('name', 'N/A')}")
            print(f"브랜드: {first_product.get('brand', 'N/A')}")
            print(f"판매자: {first_product.get('seller', 'N/A')}")
            print(f"배송정보: {first_product.get('delivery_info', 'N/A')}")
            print(f"소스: {first_product.get('source', 'N/A')}")
            print(f"카테고리: {first_product.get('category', 'N/A')}")
            
            # 한글이 제대로 표시되는지 확인
            if '노트북' in first_product.get('name', ''):
                print("\n🎉 한글 인코딩 정상 작동!")
            else:
                print("\n⚠️ 한글 인코딩 확인 필요")
    else:
        print(f"❌ API 호출 실패: {response.status_code}")
        print(f"오류: {response.text}")

except Exception as e:
    print(f"❌ 테스트 오류: {e}")

print("\n" + "=" * 40)
print("테스트 완료!")