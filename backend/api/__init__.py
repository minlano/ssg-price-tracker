# 팀원 A - Backend API 개발 영역
# 이 폴더에서 고급 검색, 상품 비교, 가격 예측 API 개발

"""
Flask API 고도화 모듈

주요 기능:
1. 11번가 API 연동 (eleventh_street_api.py)
2. 고급 검색 필터 API (advanced_search.py)
3. 상품 비교 분석 API (product_comparison.py)
4. 데이터 처리 고급 API (data_processing.py)
5. 메인 애플리케이션 (main.py)

사용법:
python backend/api/main.py

API 엔드포인트:
- /api/search/advanced - 고급 검색
- /api/compare/products - 상품 비교
- /api/data/analytics - 데이터 분석
- /api/11st/search - 11번가 검색
"""

from .main import app
from .eleventh_street_api import EleventhStreetAPI
from .advanced_search import advanced_search_bp
from .product_comparison import product_comparison_bp
from .data_processing import data_processing_bp

__all__ = [
    'app',
    'EleventhStreetAPI',
    'advanced_search_bp',
    'product_comparison_bp',
    'data_processing_bp'
]