#!/usr/bin/env python3
"""
SSG 가격 추적 시스템 - 시스템 환경 체크 스크립트
새로운 PC에서 실행하여 설치 가능 여부를 확인합니다.
"""

import sys
import subprocess
import platform
import os
from pathlib import Path

def print_header():
    print("=" * 50)
    print("🔍 SSG 가격 추적 시스템 - 환경 체크")
    print("=" * 50)
    print()

def print_section(title):
    print(f"\n📋 {title}")
    print("-" * 30)

def check_python():
    """Python 설치 및 버전 확인"""
    print_section("Python 환경 확인")
    
    try:
        version = sys.version_info
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        
        if version.major >= 3 and version.minor >= 8:
            print("✅ Python 버전 요구사항 충족 (3.8+)")
        else:
            print("❌ Python 3.8 이상이 필요합니다")
            return False
            
        # pip 확인
        try:
            import pip
            print(f"✅ pip 설치됨")
        except ImportError:
            print("❌ pip이 설치되지 않았습니다")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Python 확인 실패: {e}")
        return False

def check_node():
    """Node.js 설치 및 버전 확인"""
    print_section("Node.js 환경 확인")
    
    try:
        # Node.js 버전 확인
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Node.js {version}")
            
            # 버전 숫자 추출
            version_num = int(version.replace('v', '').split('.')[0])
            if version_num >= 16:
                print("✅ Node.js 버전 요구사항 충족 (16+)")
            else:
                print("❌ Node.js 16 이상이 필요합니다")
                return False
        else:
            print("❌ Node.js가 설치되지 않았습니다")
            return False
            
        # npm 확인
        result = subprocess.run(['npm', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            npm_version = result.stdout.strip()
            print(f"✅ npm {npm_version}")
        else:
            print("❌ npm이 설치되지 않았습니다")
            return False
            
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Node.js 명령 실행 시간 초과")
        return False
    except FileNotFoundError:
        print("❌ Node.js가 설치되지 않았습니다")
        return False
    except Exception as e:
        print(f"❌ Node.js 확인 실패: {e}")
        return False

def check_git():
    """Git 설치 확인"""
    print_section("Git 환경 확인")
    
    try:
        result = subprocess.run(['git', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ {version}")
            return True
        else:
            print("❌ Git이 설치되지 않았습니다")
            return False
            
    except FileNotFoundError:
        print("❌ Git이 설치되지 않았습니다")
        return False
    except Exception as e:
        print(f"❌ Git 확인 실패: {e}")
        return False

def check_system_info():
    """시스템 정보 확인"""
    print_section("시스템 정보")
    
    try:
        print(f"🖥️  운영체제: {platform.system()} {platform.release()}")
        print(f"🏗️  아키텍처: {platform.machine()}")
        print(f"🐍 Python 경로: {sys.executable}")
        
        # 메모리 확인 (Windows)
        if platform.system() == "Windows":
            try:
                import psutil
                memory = psutil.virtual_memory()
                print(f"💾 메모리: {memory.total // (1024**3)}GB")
            except ImportError:
                print("💾 메모리: 확인 불가 (psutil 미설치)")
        
        # 디스크 공간 확인
        current_dir = Path.cwd()
        if platform.system() == "Windows":
            import shutil
            total, used, free = shutil.disk_usage(current_dir)
            print(f"💿 디스크 여유공간: {free // (1024**3)}GB")
        
        return True
        
    except Exception as e:
        print(f"❌ 시스템 정보 확인 실패: {e}")
        return False

def check_network():
    """네트워크 연결 확인"""
    print_section("네트워크 연결 확인")
    
    try:
        import urllib.request
        
        # Google 연결 테스트
        urllib.request.urlopen('https://www.google.com', timeout=5)
        print("✅ 인터넷 연결 정상")
        
        # SSG 연결 테스트
        try:
            urllib.request.urlopen('https://www.ssg.com', timeout=10)
            print("✅ SSG 사이트 접근 가능")
        except:
            print("⚠️ SSG 사이트 접근 불가 (방화벽 확인 필요)")
            
        return True
        
    except Exception as e:
        print(f"❌ 네트워크 연결 실패: {e}")
        return False

def check_required_packages():
    """필수 Python 패키지 확인"""
    print_section("Python 패키지 확인")
    
    required_packages = [
        'requests',
        'beautifulsoup4',
        'flask',
        'flask-cors'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (설치 필요)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 설치 필요한 패키지: {', '.join(missing_packages)}")
        print("💡 'pip install -r requirements.txt'로 설치하세요")
        return False
    else:
        print("✅ 모든 필수 패키지 설치됨")
        return True

def generate_report(results):
    """결과 리포트 생성"""
    print_section("설치 가능성 평가")
    
    total_checks = len(results)
    passed_checks = sum(results.values())
    
    print(f"📊 통과한 검사: {passed_checks}/{total_checks}")
    
    if passed_checks == total_checks:
        print("🎉 모든 요구사항을 충족합니다!")
        print("✅ 바로 설치를 진행하세요: setup.bat (Windows) 또는 setup.sh (Mac/Linux)")
        return True
    elif passed_checks >= total_checks * 0.8:
        print("⚠️ 대부분의 요구사항을 충족합니다")
        print("💡 누락된 항목을 설치한 후 다시 시도하세요")
        return False
    else:
        print("❌ 여러 요구사항이 누락되었습니다")
        print("📋 INSTALL.md 문서를 참고하여 필수 소프트웨어를 설치하세요")
        return False

def main():
    """메인 실행 함수"""
    print_header()
    
    # 각 검사 실행
    results = {
        'Python': check_python(),
        'Node.js': check_node(), 
        'Git': check_git(),
        'System': check_system_info(),
        'Network': check_network(),
        'Packages': check_required_packages()
    }
    
    # 결과 리포트
    success = generate_report(results)
    
    print("\n" + "=" * 50)
    if success:
        print("🚀 설치 준비 완료!")
    else:
        print("🔧 추가 설정이 필요합니다")
    print("=" * 50)
    
    return success

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ 검사가 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        sys.exit(1)