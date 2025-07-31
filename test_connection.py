#!/usr/bin/env python3
# 연결 테스트 및 진단
import requests
import socket
import time

def test_server_connection():
    print("🔍 서버 연결 진단 시작")
    print("=" * 50)
    
    # 1. 포트 확인
    print("1. 포트 5001 상태 확인...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(('127.0.0.1', 5001))
        sock.close()
        
        if result == 0:
            print("   ✅ 포트 5001이 열려있습니다")
        else:
            print("   ❌ 포트 5001에 연결할 수 없습니다")
            return False
    except Exception as e:
        print(f"   ❌ 포트 확인 오류: {e}")
        return False
    
    # 2. HTTP 연결 테스트
    print("\n2. HTTP 연결 테스트...")
    urls_to_test = [
        "http://127.0.0.1:5001/",
        "http://localhost:5001/",
        "http://127.0.0.1:5001/api/health"
    ]
    
    for url in urls_to_test:
        try:
            print(f"   테스트: {url}")
            response = requests.get(url, timeout=5)
            print(f"   ✅ 상태 코드: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'message' in data:
                        print(f"   📄 응답: {data['message']}")
                    elif 'status' in data:
                        print(f"   📄 상태: {data['status']}")
                except:
                    print(f"   📄 응답 길이: {len(response.text)} 문자")
                return True
            
        except requests.exceptions.ConnectionError:
            print(f"   ❌ 연결 거부: {url}")
        except requests.exceptions.Timeout:
            print(f"   ❌ 타임아웃: {url}")
        except Exception as e:
            print(f"   ❌ 오류: {e}")
    
    return False

def test_api_endpoints():
    """API 엔드포인트 테스트"""
    print("\n3. API 엔드포인트 테스트...")
    
    base_url = "http://127.0.0.1:5001"
    endpoints = [
        "/",
        "/api/health",
        "/api/11st/search?keyword=test&limit=1",
        "/api/11st/popular-keywords"
    ]
    
    for endpoint in endpoints:
        try:
            url = base_url + endpoint
            print(f"\n   🔗 테스트: {endpoint}")
            
            response = requests.get(url, timeout=10)
            print(f"   📊 상태: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if endpoint == "/":
                        print(f"   📝 메시지: {data.get('message', 'N/A')}")
                        print(f"   🔢 버전: {data.get('version', 'N/A')}")
                    elif endpoint == "/api/health":
                        print(f"   💚 상태: {data.get('status', 'N/A')}")
                        print(f"   🗄️ DB: {data.get('database', 'N/A')}")
                    elif "search" in endpoint:
                        products = data.get('products', [])
                        total = data.get('total', 0)
                        print(f"   🛍️ 총 상품: {total:,}개")
                        print(f"   📦 반환: {len(products)}개")
                        if products:
                            print(f"   🏷️ 첫 상품: {products[0].get('name', 'N/A')[:30]}...")
                    elif "keywords" in endpoint:
                        keywords = data.get('popular_keywords', [])
                        print(f"   🔥 인기 키워드: {len(keywords)}개")
                        if keywords:
                            print(f"   🏆 1위: {keywords[0].get('keyword', 'N/A')}")
                            
                except Exception as e:
                    print(f"   📄 JSON 파싱 오류: {e}")
                    print(f"   📝 응답 미리보기: {response.text[:100]}...")
            else:
                print(f"   ❌ 오류 응답: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ 요청 실패: {e}")

def show_browser_urls():
    """브라우저 테스트 URL 표시"""
    print("\n" + "=" * 50)
    print("🌐 브라우저에서 다음 URL들을 복사해서 테스트하세요:")
    print("=" * 50)
    
    urls = [
        ("기본 페이지", "http://127.0.0.1:5001/"),
        ("API 상태", "http://127.0.0.1:5001/api/health"),
        ("스마트폰 검색", "http://127.0.0.1:5001/api/11st/search?keyword=스마트폰&limit=3"),
        ("노트북 검색", "http://127.0.0.1:5001/api/11st/search?keyword=노트북&limit=5"),
        ("인기 키워드", "http://127.0.0.1:5001/api/11st/popular-keywords"),
        ("대시보드", "http://127.0.0.1:5001/api/dashboard/advanced")
    ]
    
    for name, url in urls:
        print(f"📌 {name}:")
        print(f"   {url}")
        print()

if __name__ == "__main__":
    if test_server_connection():
        test_api_endpoints()
        show_browser_urls()
        
        print("💡 문제 해결 팁:")
        print("1. 브라우저에서 F12 → Network 탭에서 오류 확인")
        print("2. 방화벽이나 바이러스 백신 소프트웨어 확인")
        print("3. 다른 브라우저로 시도해보기")
        print("4. http://localhost:5001/ 도 시도해보기")
    else:
        print("\n❌ 서버 연결 실패!")
        print("💡 해결 방법:")
        print("1. Flask 서버가 실행 중인지 확인")
        print("2. 포트 5001이 다른 프로그램에서 사용 중인지 확인")
        print("3. 서버를 재시작해보기 (Ctrl+C 후 다시 실행)")
    
    print("\n" + "=" * 50)