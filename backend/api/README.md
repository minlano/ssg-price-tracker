# Flask API 고도화 (11번가 연동)

이 모듈은 11번가 API와 연동하여 고급 검색, 상품 비교, 데이터 분석 기능을 제공하는 고도화된 Flask API입니다.

## 주요 기능

### 1. 11번가 API 연동 (`eleventh_street_api.py`)
- 11번가 상품 검색
- 상품 상세 정보 조회
- 카테고리별 검색
- 가격 필터링 및 정렬

### 2. 고급 검색 필터 API (`advanced_search.py`)
- 다중 필터 검색 (가격, 카테고리, 브랜드, 평점)
- 검색어 자동완성
- 통합 검색 (11번가 + SSG)
- 검색 결과 통계

### 3. 상품 비교 분석 API (`product_comparison.py`)
- 여러 상품 상세 비교
- 유사 상품 찾기
- 가격 이력 비교
- 최적 상품 추천 (가성비 분석)
- 카테고리별 분석

### 4. 데이터 처리 고급 API (`data_processing.py`)
- 종합 분석 데이터
- 데이터 내보내기/가져오기
- 데이터 정리 및 최적화
- 일괄 업데이트
- 통계 정보

## API 엔드포인트

### 기본 API
```
GET  /api/health                    # API 상태 확인
GET  /api/dashboard/advanced        # 고도화된 대시보드
GET  /api/products/trending         # 인기 상품
GET  /api/products/recommendations  # 상품 추천
POST /api/alerts/smart              # 스마트 알림 생성
```

### 11번가 API
```
GET  /api/11st/categories           # 카테고리 목록
GET  /api/11st/search               # 상품 검색
GET  /api/11st/product/<id>         # 상품 상세 정보
```

### 고급 검색 API
```
GET  /api/search/advanced           # 고급 검색
GET  /api/search/filters            # 검색 필터 옵션
GET  /api/search/suggestions        # 검색어 자동완성
```

### 상품 비교 API
```
POST /api/compare/products          # 상품 비교
GET  /api/compare/similar           # 유사 상품 찾기
GET  /api/compare/price-history     # 가격 이력 비교
GET  /api/compare/best-deal         # 최적 상품 추천
GET  /api/compare/category-analysis # 카테고리 분석
```

### 데이터 처리 API
```
GET  /api/data/analytics            # 분석 데이터
POST /api/data/export               # 데이터 내보내기
POST /api/data/import               # 데이터 가져오기
POST /api/data/cleanup              # 데이터 정리
POST /api/data/batch-update         # 일괄 업데이트
GET  /api/data/statistics           # 통계 정보
```

## 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 데이터베이스 초기화
```bash
cd backend
python database.py
```

### 3. API 서버 실행
```bash
cd backend/api
python main.py
```

서버는 `http://localhost:5000`에서 실행됩니다.

### 4. API 테스트
```bash
python test_api.py
```

## 사용 예제

### 고급 검색
```python
import requests

# 고급 검색 (가격 필터, 정렬 적용)
response = requests.get('http://localhost:5000/api/search/advanced', params={
    'keyword': '스마트폰',
    'min_price': 300000,
    'max_price': 1000000,
    'sort': 'price_low',
    'source': '11st',
    'page': 1,
    'limit': 20
})

data = response.json()
print(f"검색 결과: {len(data['products'])}개")
```

### 상품 비교
```python
# 여러 상품 비교
compare_data = {
    'product_ids': ['11st_1_스마트폰', '11st_2_스마트폰', '11st_3_스마트폰']
}

response = requests.post('http://localhost:5000/api/compare/products', 
                        json=compare_data)

data = response.json()
comparison = data['comparison']
print(f"가격 범위: {comparison['price_comparison']['lowest']:,}원 ~ {comparison['price_comparison']['highest']:,}원")
```

### 최적 상품 찾기
```python
# 가성비 좋은 상품 찾기
response = requests.get('http://localhost:5000/api/compare/best-deal', params={
    'keyword': '노트북',
    'max_price': 1500000,
    'min_rating': 4.0,
    'limit': 10
})

data = response.json()
for product in data['best_deals']:
    print(f"{product['name']} - {product['price']:,}원 (가성비: {product['value_score']})")
```

### 데이터 분석
```python
# 종합 분석 데이터
response = requests.get('http://localhost:5000/api/data/analytics', params={
    'period': '30',
    'type': 'overview'
})

data = response.json()
analytics = data['analytics']
print(f"신규 상품: {analytics['general_stats']['new_products']}개")
```

## 주요 특징

### 1. 통합 검색
- 11번가와 SSG를 동시에 검색
- 결과 통합 및 중복 제거
- 소스별 필터링 가능

### 2. 지능형 필터링
- 다중 조건 필터링
- 동적 필터 옵션 제공
- 검색 결과 통계

### 3. 고급 비교 분석
- 최대 5개 상품 동시 비교
- 유사도 기반 상품 추천
- 가격 변동 이력 분석

### 4. 데이터 인사이트
- 실시간 분석 대시보드
- 트렌드 분석
- 카테고리별 통계

### 5. 스마트 알림
- 가격 이력 기반 목표가 설정
- 개인화된 추천
- 다양한 알림 타입

## 확장 가능성

### 1. 추가 쇼핑몰 연동
- 쿠팡, 옥션, G마켓 등
- 통합 검색 및 비교

### 2. 머신러닝 기능
- 가격 예측 모델
- 개인화 추천 시스템
- 이상 거래 탐지

### 3. 실시간 기능
- WebSocket 기반 실시간 알림
- 실시간 가격 모니터링
- 라이브 대시보드

### 4. 모바일 최적화
- 모바일 전용 API
- 푸시 알림 연동
- 위치 기반 서비스

## 주의사항

1. **API 키 설정**: 실제 11번가 API 사용 시 API 키가 필요합니다.
2. **크롤링 정책**: 각 쇼핑몰의 크롤링 정책을 준수해야 합니다.
3. **성능 최적화**: 대용량 데이터 처리 시 인덱싱과 캐싱이 필요합니다.
4. **보안**: 사용자 데이터 보호를 위한 보안 조치가 필요합니다.

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.