# API 설정 파일
import os
from typing import Optional

class APIConfig:
    """API 설정 관리 클래스"""
    
    def __init__(self):
        # 11번가 API 설정
        self.ELEVENTH_STREET_API_KEY = self._get_api_key()
        self.ELEVENTH_STREET_BASE_URL = "https://openapi.11st.co.kr"
        
        # 기타 설정
        self.DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
        self.DATABASE_PATH = '../database/ssg_tracker.db'
    
    def _get_api_key(self) -> Optional[str]:
        """
        API 키를 다음 순서로 찾습니다:
        1. 환경 변수 (ELEVENTH_STREET_API_KEY 또는 api_key)
        2. .env 파일 (api_key)
        3. config.json 파일
        4. 직접 입력된 키
        """
        
        # 1. 환경 변수에서 찾기
        api_key = os.getenv('ELEVENTH_STREET_API_KEY') or os.getenv('api_key')
        if api_key:
            print("✅ 환경 변수에서 11번가 API 키를 찾았습니다.")
            return api_key
        
        # 2. .env 파일에서 찾기
        try:
            from dotenv import load_dotenv
            # .env와 .evn 파일 모두 확인
            load_dotenv('.env')
            load_dotenv('.evn')  # 현재 파일명이 .evn이므로 추가
            
            api_key = os.getenv('ELEVENTH_STREET_API_KEY') or os.getenv('api_key')
            if api_key:
                print("✅ .env 파일에서 11번가 API 키를 찾았습니다.")
                return api_key
        except ImportError:
            pass
        
        # 3. config.json 파일에서 찾기
        try:
            import json
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                api_key = config.get('eleventh_street_api_key')
                if api_key:
                    print("✅ config.json 파일에서 11번가 API 키를 찾았습니다.")
                    return api_key
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        
        # 4. 직접 입력된 키 (아래에 직접 입력하세요)
        # ⚠️ 보안상 권장하지 않습니다. 환경 변수나 .env 파일 사용을 권장합니다.
        DIRECT_API_KEY = ""  # 여기에 API 키를 직접 입력하세요
        
        if DIRECT_API_KEY:
            print("✅ 직접 입력된 11번가 API 키를 사용합니다.")
            return DIRECT_API_KEY
        
        print("⚠️ 11번가 API 키를 찾을 수 없습니다. 샘플 데이터를 사용합니다.")
        print("API 키 설정 방법:")
        print("1. 환경 변수: set ELEVENTH_STREET_API_KEY=your_api_key")
        print("2. .env 파일: ELEVENTH_STREET_API_KEY=your_api_key")
        print("3. config.json 파일: {\"eleventh_street_api_key\": \"your_api_key\"}")
        print("4. config.py 파일의 DIRECT_API_KEY 변수에 직접 입력")
        
        return None
    
    def set_api_key(self, api_key: str):
        """API 키를 동적으로 설정"""
        self.ELEVENTH_STREET_API_KEY = api_key
        print(f"✅ 11번가 API 키가 설정되었습니다: {api_key[:10]}...")

# 전역 설정 인스턴스
config = APIConfig()