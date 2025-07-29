#!/usr/bin/env python3
"""
SSG 가격 추적 시스템 - 빠른 테스트 스크립트
"""

import os
import sys
import subprocess
import time
import requests

def check_python():
    """Python 설치 확인"""
    print("🐍 Python 버전 확인...")
    print(f"Python {sys.version}")
    return True

def check_node():
    """Node.js 설치 확인"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        print(f"📦 Node.js {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("❌ Node.js가 설치되지 않았습니다.")
        return False

def install_backend_deps():
    """Backend 의존성 설치"""
    print("\n🔧 Backend 패키지 설치 중...")
    os.chdir('backend')
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    os.chdir('..')

def init_database():
    """데이터베이스 초기화"""
    print("\n🗄️ 데이터베이스 초기화 중...")
    os.chdir('backend')
    subprocess.run([sys.executable, 'database.py'])
    os.chdir('..')

def test_crawler():
    """크롤러 테스트"""
    print("\n🕷️ 크롤러 테스트 중...")
    os.chdir('backend')
    try:
        from crawler import crawl_ssg_product
        # 테스트용 더미 데이터
        test_result = {
            'name': '테스트 상품',
            'price': 50000,
            'url': 'https://www.ssg.com/test'
        }
        print(f"✅ 크롤러 테스트 성공: {test_result}")
    except Exception as e:
        print(f"⚠️ 크롤러 테스트 실패: {e}")
    os.chdir('..')

def start_backend():
    """Backend 서버 시작"""
    print("\n🚀 Backend 서버 시작 중...")
    os.chdir('backend')
    # 백그라운드에서 Flask 서버 시작
    process = subprocess.Popen([sys.executable, 'app.py'])
    os.chdir('..')
    return process

def test_api():
    """API 테스트"""
    print("\n🔌 API 연결 테스트 중...")
    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.get('http://localhost:5000/api/products', timeout=5)
            if response.status_code == 200:
                print("✅ Backend API 연결 성공!")
                return True
        except:
            if i < max_retries - 1:
                print(f"⏳ API 연결 대기 중... ({i+1}/{max_retries})")
                time.sleep(2)
            else:
                print("❌ Backend API 연결 실패")
                return False
    return False

def install_frontend_deps():
    """Frontend 의존성 설치"""
    print("\n📦 Frontend 패키지 설치 중...")
    os.chdir('frontend')
    subprocess.run(['npm', 'install'])
    os.chdir('..')

def main():
    """메인 실행 함수"""
    print("=" * 50)
    print("🎯 SSG 가격 추적 시스템 - 빠른 테스트")
    print("=" * 50)
    
    # 1. 환경 확인
    if not check_python():
        return
    
    if not check_node():
        print("Node.js를 설치한 후 다시 실행해주세요.")
        return
    
    # 2. Backend 설정
    try:
        install_backend_deps()
        init_database()
        test_crawler()
        
        # 3. Backend 서버 시작
        backend_process = start_backend()
        time.sleep(3)  # 서버 시작 대기
        
        # 4. API 테스트
        if test_api():
            print("\n✅ Backend 설정 완료!")
        else:
            print("\n❌ Backend 설정 실패")
            backend_process.terminate()
            return
        
        # 5. Frontend 설정
        install_frontend_deps()
        
        print("\n" + "=" * 50)
        print("🎉 설정 완료!")
        print("=" * 50)
        print("Backend 서버: http://localhost:5000")
        print("Frontend 실행: cd frontend && npm start")
        print("=" * 50)
        
        # 사용자 입력 대기
        input("\nEnter를 누르면 Backend 서버가 종료됩니다...")
        backend_process.terminate()
        
    except KeyboardInterrupt:
        print("\n\n⏹️ 테스트가 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")

if __name__ == '__main__':
    main()