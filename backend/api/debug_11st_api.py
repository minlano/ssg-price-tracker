# 11번가 API 응답 구조 분석
import requests
import json
from urllib.parse import quote

def test_real_11st_api():
    """실제 11번가 API 호출 테스트"""
    
    # 제공해주신 URL 사용
    api_key = "e6a293873ce4dacd7d3431955da64232"
    base_url = "http://openapi.11st.co.kr/openapi/OpenApiService.tmall"
    
    # 테스트 파라미터
    params = {
        'key': api_key,
        'apiCode': 'ProductSearch',
        'keyword': '불닭볶음면'
    }
    
    print("=" * 60)
    print("11번가 API 실제 호출 테스트")
    print("=" * 60)
    print(f"URL: {base_url}")
    print(f"Parameters: {params}")
    print()
    
    try:
        # API 호출
        response = requests.get(base_url, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print()
        
        if response.status_code == 200:
            # 응답 내용 확인
            content_type = response.headers.get('content-type', '')
            print(f"Content-Type: {content_type}")
            
            if 'json' in content_type.lower():
                # JSON 응답
                try:
                    data = response.json()
                    print("JSON 응답 구조:")
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                except json.JSONDecodeError as e:
                    print(f"JSON 파싱 오류: {e}")
                    print("Raw Response:")
                    print(response.text[:1000])
            else:
                # XML 또는 기타 형식
                print("응답 내용 (처음 1000자):")
                print(response.text[:1000])
                
                # XML인지 확인
                if response.text.strip().startswith('<?xml') or response.text.strip().startswith('<'):
                    print("\n⚠️ XML 형식 응답입니다. XML 파싱이 필요합니다.")
                    
                    # XML 파싱 시도
                    try:
                        import xml.etree.ElementTree as ET
                        root = ET.fromstring(response.text)
                        print(f"XML Root Tag: {root.tag}")
                        print("XML 구조:")
                        for child in root:
                            print(f"  - {child.tag}: {child.text}")
                    except Exception as e:
                        print(f"XML 파싱 오류: {e}")
        else:
            print(f"API 호출 실패: {response.status_code}")
            print(f"Error Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"네트워크 오류: {e}")
    except Exception as e:
        print(f"기타 오류: {e}")

def test_different_keywords():
    """다양한 키워드로 테스트"""
    api_key = "24e0fb9e898e94041c923b76f07a3931"
    base_url = "https://openapi.11st.co.kr/openapi/OpenApiService.tmall"
    
    keywords = ['스마트폰', '노트북', '이어폰']
    
    print("\n" + "=" * 60)
    print("다양한 키워드 테스트")
    print("=" * 60)
    
    for keyword in keywords:
        print(f"\n키워드: {keyword}")
        params = {
            'key': api_key,
            'apiCode': 'ProductSearch',
            'keyword': keyword
        }
        
        try:
            response = requests.get(base_url, params=params, timeout=5)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                if 'json' in response.headers.get('content-type', '').lower():
                    data = response.json()
                    print(f"  응답 타입: JSON")
                    print(f"  주요 키: {list(data.keys()) if isinstance(data, dict) else 'Not dict'}")
                else:
                    print(f"  응답 타입: {response.headers.get('content-type', 'Unknown')}")
                    print(f"  응답 길이: {len(response.text)} 문자")
            else:
                print(f"  오류: {response.text[:100]}")
                
        except Exception as e:
            print(f"  오류: {e}")

if __name__ == "__main__":
    test_real_11st_api()
    test_different_keywords()