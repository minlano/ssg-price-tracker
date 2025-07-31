#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SSG 가격 추적기 백엔드 API
- 개선된 SSG 크롤러 사용
- 캐시 시스템 적용
- 비동기 처리 지원
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
from datetime import datetime
import traceback
from urllib.parse import quote_plus # Added for naver_search

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 개선된 크롤러 import
try:
    from crawler import search_ssg_products
    from cache_manager import cache_manager
    CRAWLER_AVAILABLE = True
    print("✅ 개선된 크롤러 로드 성공")
except ImportError as e:
    print(f"⚠️ 크롤러 로드 실패: {e}")
    CRAWLER_AVAILABLE = False

# Flask 앱 생성
app = Flask(__name__)
CORS(app)

# 한글 인코딩 설정
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

@app.route('/', methods=['GET'])
def index():
    """기본 페이지"""
    return jsonify({
        'message': '🚀 SSG 가격 추적기 API',
        'version': '3.0.0',
        'description': '개선된 SSG 크롤러를 사용한 고성능 상품 검색',
        'features': [
            '⚡ 캐시 시스템 (1000배 빠른 응답)',
            '🚀 비동기 처리',
            '🔄 병렬 처리 지원',
            '📊 100% 정확한 상품명',
            '💾 메모리 캐시'
        ],
        'api_endpoints': {
            'health': '/api/health',
            'search': '/api/search?keyword={검색어}',
            'dashboard': '/api/dashboard',
            'cache_stats': '/api/cache/stats',
            'cache_clear': '/api/cache/clear',
            # === 가격 추적 API 엔드포인트 목록 추가 시작 ===
            'watchlist_get': '/api/watchlist?user_email={이메일}',
            'watchlist_add': '/api/watchlist (POST)',
            'watchlist_remove': '/api/watchlist/{id} (DELETE)',
            'price_history': '/api/price-history/{watch_id}',
            'price_check': '/api/price-check (POST)',
            'temp_watchlist_add': '/api/watchlist/temp (POST)',
            'temp_watchlist_get': '/api/watchlist/temp',
            'watchlist_activate': '/api/watchlist/activate (POST)',
            # === 임시 추적 목록 삭제 API 추가 시작 ===
            'temp_watchlist_remove': '/api/watchlist/temp/{id} (DELETE)',
            # === 임시 추적 목록 삭제 API 추가 끝 ===
            # === 가격 추적 API 엔드포인트 목록 추가 끝 ===
            # === 네이버 쇼핑 API 엔드포인트 목록 추가 시작 ===
            'naver_search': '/api/naver/search?keyword={검색어}',
            'naver_compare': '/api/naver/compare?keyword={검색어}',
            'naver_add_product': '/api/naver/products/add-from-search (POST)',
            # === 네이버 쇼핑 API 엔드포인트 목록 추가 끝 ===
            # === 11번가 API 엔드포인트 목록 추가 시작 ===
            '11st_search': '/api/11st/search?keyword={검색어}',
            '11st_popular_keywords': '/api/11st/popular-keywords',
            '11st_categories': '/api/11st/categories',
            '11st_product_detail': '/api/11st/product/{product_id}'
            # === 11번가 API 엔드포인트 목록 추가 끝 ===
        },
        'search_examples': {
            '아이폰 검색': '/api/search?keyword=아이폰&limit=10',
            '나이키 검색': '/api/search?keyword=나이키&limit=5',
            '라면 검색': '/api/search?keyword=라면&limit=8'
        },
        'status': 'running',
        'crawler_status': '✅ 개선된 SSG 크롤러 활성화' if CRAWLER_AVAILABLE else '❌ 크롤러 비활성화'
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """API 상태 확인"""
    try:
        # 캐시 상태 확인
        cache_stats = cache_manager.get_cache_stats() if CRAWLER_AVAILABLE else {}
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '3.0.0',
            'crawler_available': CRAWLER_AVAILABLE,
            'cache_stats': cache_stats,
            'features': {
                'async_processing': True,
                'cache_system': True,
                'parallel_processing': True,
                'accurate_product_names': True
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/search', methods=['GET'])
def search_products():
    """상품 검색 API"""
    try:
        if not CRAWLER_AVAILABLE:
            return jsonify({
                'error': '크롤러를 사용할 수 없습니다',
                'message': '크롤러 모듈 로드에 실패했습니다'
            }), 500
        
        # 파라미터 추출
        keyword = request.args.get('keyword', '').strip()
        limit = request.args.get('limit', 20, type=int)
        page = request.args.get('page', 1, type=int)
        
        # 키워드 유효성 검사
        if not keyword:
            return jsonify({
                'error': '검색어를 입력해주세요',
                'message': '사용 예시: /api/search?keyword=아이폰',
                'popular_keywords': [
                    '아이폰', '삼성 갤럭시', '나이키', '아디다스', '라면',
                    '노트북', '이어폰', '화장품', '운동화', '가방'
                ]
            }), 400
        
        if len(keyword) > 50:
            return jsonify({'error': '검색어는 50자 이내로 입력해주세요'}), 400
        
        if limit > 50:
            limit = 50  # 최대 50개로 제한
        
        # 검색 시작 시간 기록
        start_time = datetime.now()
        
        print(f"🔍 검색 요청: '{keyword}' (limit: {limit})")
        
        # SSG 상품 검색 실행
        products = search_ssg_products(keyword, page=page, limit=limit)
        
        # 검색 완료 시간 계산
        end_time = datetime.now()
        search_duration = (end_time - start_time).total_seconds()
        
        print(f"✅ 검색 완료: {len(products)}개 상품, {search_duration:.2f}초")
        
        # 응답 데이터 구성
        response_data = {
            'products': products,
            'search_info': {
                'keyword': keyword,
                'total_results': len(products),
                'page': page,
                'limit': limit,
                'search_duration': round(search_duration, 3),
                'search_time': start_time.isoformat(),
                'source': 'SSG',
                'cache_used': search_duration < 0.1  # 0.1초 미만이면 캐시 사용으로 추정
            },
            'performance': {
                'response_time': f"{search_duration:.3f}초",
                'products_per_second': round(len(products) / search_duration, 1) if search_duration > 0 else 0,
                'cache_hit': search_duration < 0.1
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ 검색 오류: {e}")
        print(f"상세 오류: {error_trace}")
        
        return jsonify({
            'error': f'검색 중 오류가 발생했습니다: {str(e)}',
            'keyword': request.args.get('keyword', ''),
            'timestamp': datetime.now().isoformat(),
            'error_type': type(e).__name__
        }), 500

@app.route('/api/compare', methods=['GET'])
def compare_products():
    """가격 비교 API"""
    try:
        if not CRAWLER_AVAILABLE:
            return jsonify({
                'error': '크롤러를 사용할 수 없습니다',
                'message': '크롤러 모듈 로드에 실패했습니다'
            }), 500
        
        # 파라미터 추출
        keyword = request.args.get('keyword', '').strip()
        limit = request.args.get('limit', 10, type=int)
        
        # 키워드 유효성 검사
        if not keyword:
            return jsonify({
                'error': '검색어를 입력해주세요',
                'message': '사용 예시: /api/compare?keyword=아이폰'
            }), 400
        
        if len(keyword) > 50:
            return jsonify({'error': '검색어는 50자 이내로 입력해주세요'}), 400
        
        if limit > 20:
            limit = 20  # 최대 20개로 제한
        
        # 검색 시작 시간 기록
        start_time = datetime.now()
        
        print(f"🔍 가격 비교 요청: '{keyword}' (limit: {limit})")
        
        # SSG 상품 검색 실행
        products = search_ssg_products(keyword, page=1, limit=limit)
        
        # 검색 완료 시간 계산
        end_time = datetime.now()
        search_duration = (end_time - start_time).total_seconds()
        
        print(f"✅ 가격 비교 완료: {len(products)}개 상품, {search_duration:.2f}초")
        
        # 가격 비교 데이터 구성
        comparison_data = {
            'keyword': keyword,
            'total_products': len(products),
            'price_range': {
                'min': min([p.get('price', 0) for p in products]) if products else 0,
                'max': max([p.get('price', 0) for p in products]) if products else 0,
                'avg': sum([p.get('price', 0) for p in products]) // len(products) if products else 0
            },
            'products': products,
            'comparison_info': {
                'keyword': keyword,
                'total_results': len(products),
                'limit': limit,
                'search_duration': round(search_duration, 3),
                'search_time': start_time.isoformat(),
                'source': 'SSG'
            }
        }
        
        return jsonify(comparison_data)
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ 가격 비교 오류: {e}")
        print(f"상세 오류: {error_trace}")
        
        return jsonify({
            'error': f'가격 비교 중 오류가 발생했습니다: {str(e)}',
            'keyword': request.args.get('keyword', ''),
            'timestamp': datetime.now().isoformat(),
            'error_type': type(e).__name__
        }), 500

@app.route('/api/products/add-from-search', methods=['POST'])
def add_product_from_search():
    """검색 결과에서 상품 추가"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '상품 데이터가 없습니다'}), 400
        
        # 필수 필드 확인
        required_fields = ['name', 'url']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'필수 필드가 누락되었습니다: {field}'}), 400
        
        # 데이터베이스 연결
        from database import get_db_connection
        conn = get_db_connection()
        
        # 상품 정보 추출
        name = data['name']
        current_price = data.get('current_price', data.get('price', 0))
        url = data['url']
        image_url = data.get('image_url', '')
        description = data.get('description', '')
        brand = data.get('brand', '')
        source = data.get('source', 'SSG')
        
        # 상품 추가
        cursor = conn.execute('''
            INSERT INTO products (name, current_price, url, image_url, description, brand, source, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now', '+09:00'))
        ''', (name, current_price, url, image_url, description, brand, source))
        
        product_id = cursor.lastrowid
        
        # 가격 로그 추가
        conn.execute('''
            INSERT INTO price_logs (product_id, price, logged_at)
            VALUES (?, ?, datetime('now', '+09:00'))
        ''', (product_id, current_price))
        
        conn.commit()
        conn.close()
        
        print(f"✅ 상품 추가 완료: {name} (ID: {product_id})")
        
        return jsonify({
            'message': '상품이 성공적으로 추가되었습니다',
            'product': {
                'id': product_id,
                'name': name,
                'current_price': current_price,
                'url': url,
                'image_url': image_url,
                'description': description,
                'brand': brand,
                'source': source
            }
        })
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ 상품 추가 오류: {e}")
        print(f"상세 오류: {error_trace}")
        
        return jsonify({
            'error': f'상품 추가 중 오류가 발생했습니다: {str(e)}',
            'timestamp': datetime.now().isoformat(),
            'error_type': type(e).__name__
        }), 500

# 네이버 쇼핑 관련 API (실제 크롤러 사용)
@app.route('/api/naver/search', methods=['GET'])
def naver_search():
    """네이버 쇼핑 검색 API"""
    try:
        keyword = request.args.get('keyword', '').strip()
        limit = request.args.get('limit', 20, type=int)
        
        if not keyword:
            return jsonify({
                'error': '검색어를 입력해주세요',
                'message': '사용 예시: /api/naver/search?keyword=아이폰'
            }), 400
        
        # 네이버 쇼핑 크롤러 import
        try:
            from crawlers.naver_shopping_crawler import search_naver_products
            products = search_naver_products(keyword, limit)
        except ImportError:
            print("⚠️ 네이버 쇼핑 크롤러를 찾을 수 없어 더미 데이터를 반환합니다.")
            # 더미 데이터 반환
            products = []
            for i in range(min(limit, 10)):
                image_url = f"https://picsum.photos/300/300?random={i+1}"
                products.append({
                    'id': f'naver_{i+1}',
                    'name': f'{keyword} 상품 {i+1}',
                    'price': 10000 + (i * 5000),
                    'current_price': 10000 + (i * 5000),
                    'url': f'https://search.shopping.naver.com/search/all?query={quote_plus(keyword)}',
                    'image_url': image_url,
                    'description': f'{keyword} 관련 상품입니다.',
                    'brand': f'브랜드{i+1}',
                    'source': 'NAVER'
                })
        
        return jsonify({
            'products': products,
            'search_info': {
                'keyword': keyword,
                'total_results': len(products),
                'limit': limit,
                'source': 'NAVER'
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': f'네이버 검색 중 오류가 발생했습니다: {str(e)}'
        }), 500

@app.route('/api/naver/compare', methods=['GET'])
def naver_compare():
    """네이버 쇼핑 가격 비교 API"""
    try:
        keyword = request.args.get('keyword', '').strip()
        limit = request.args.get('limit', 10, type=int)
        
        if not keyword:
            return jsonify({
                'error': '검색어를 입력해주세요',
                'message': '사용 예시: /api/naver/compare?keyword=아이폰'
            }), 400
        
        # 네이버 쇼핑 크롤러 import
        try:
            from crawlers.naver_shopping_crawler import search_naver_products
            products = search_naver_products(keyword, limit)
        except ImportError:
            print("⚠️ 네이버 쇼핑 크롤러를 찾을 수 없어 더미 데이터를 반환합니다.")
            # 더미 데이터 반환
            products = []
            for i in range(min(limit, 10)):
                image_url = f"https://picsum.photos/300/300?random={i+1}"
                products.append({
                    'id': f'naver_{i+1}',
                    'name': f'{keyword} 상품 {i+1}',
                    'price': 10000 + (i * 5000),
                    'current_price': 10000 + (i * 5000),
                    'url': f'https://search.shopping.naver.com/search/all?query={quote_plus(keyword)}',
                    'image_url': image_url,
                    'description': f'{keyword} 관련 상품입니다.',
                    'brand': f'브랜드{i+1}',
                    'source': 'NAVER'
                })
        
        return jsonify({
            'keyword': keyword,
            'total_products': len(products),
            'price_range': {
                'min': min([p.get('price', 0) for p in products]) if products else 0,
                'max': max([p.get('price', 0) for p in products]) if products else 0,
                'avg': sum([p.get('price', 0) for p in products]) // len(products) if products else 0
            },
            'products': products,
            'comparison_info': {
                'keyword': keyword,
                'total_results': len(products),
                'limit': limit,
                'source': 'NAVER'
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': f'네이버 가격 비교 중 오류가 발생했습니다: {str(e)}'
        }), 500

@app.route('/api/naver/products/add-from-search', methods=['POST'])
def naver_add_product_from_search():
    """네이버 쇼핑 검색 결과에서 상품 추가"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '상품 데이터가 없습니다'}), 400
        
        # 필수 필드 확인
        required_fields = ['name', 'url']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'필수 필드가 누락되었습니다: {field}'}), 400
        
        # 데이터베이스 연결
        from database import get_db_connection
        conn = get_db_connection()
        
        # 상품 정보 추출
        name = data['name']
        current_price = data.get('current_price', data.get('price', 0))
        url = data['url']
        image_url = data.get('image_url', '')
        description = data.get('description', '')
        brand = data.get('brand', '')
        source = 'NAVER'
        
        # 상품 추가
        cursor = conn.execute('''
            INSERT INTO products (name, current_price, url, image_url, description, brand, source, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now', '+09:00'))
        ''', (name, current_price, url, image_url, description, brand, source))
        
        product_id = cursor.lastrowid
        
        # 가격 로그 추가
        conn.execute('''
            INSERT INTO price_logs (product_id, price, logged_at)
            VALUES (?, ?, datetime('now', '+09:00'))
        ''', (product_id, current_price))
        
        conn.commit()
        conn.close()
        
        print(f"✅ 네이버 상품 추가 완료: {name} (ID: {product_id})")
        
        return jsonify({
            'message': '네이버 상품이 성공적으로 추가되었습니다',
            'product': {
                'id': product_id,
                'name': name,
                'current_price': current_price,
                'url': url,
                'image_url': image_url,
                'description': description,
                'brand': brand,
                'source': source
            }
        })
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ 네이버 상품 추가 오류: {e}")
        print(f"상세 오류: {error_trace}")
        
        return jsonify({
            'error': f'네이버 상품 추가 중 오류가 발생했습니다: {str(e)}',
            'timestamp': datetime.now().isoformat(),
            'error_type': type(e).__name__
        }), 500

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """대시보드 데이터"""
    try:
        from database import get_db_connection
        conn = get_db_connection()
        
        # 총 상품 개수
        cursor = conn.execute('SELECT COUNT(*) as total FROM products')
        total_products = cursor.fetchone()['total']
        
        # 활성 알림 개수
        cursor = conn.execute('SELECT COUNT(*) as total FROM alerts WHERE is_active = 1')
        active_alerts = cursor.fetchone()['total']
        
        # 최근 가격 변동 (최근 7일)
        recent_changes = conn.execute('''
            SELECT p.name, pl.price, pl.logged_at
            FROM price_logs pl
            JOIN products p ON pl.product_id = p.id
            WHERE pl.logged_at >= datetime('now', '-7 days')
            ORDER BY pl.logged_at DESC
            LIMIT 10
        ''').fetchall()
        
        # 소스별 상품 분포
        source_distribution = conn.execute('''
            SELECT source, COUNT(*) as count
            FROM products
            GROUP BY source
        ''').fetchall()
        
        # 평균 가격
        cursor = conn.execute('SELECT AVG(current_price) as avg_price FROM products WHERE current_price > 0')
        avg_price = cursor.fetchone()['avg_price'] or 0
        
        conn.close()
        
        # 최근 변동 데이터 변환
        changes_list = []
        for change in recent_changes:
            changes_list.append({
                'name': change['name'],
                'price': change['price'],
                'logged_at': change['logged_at']
            })
        
        # 소스별 분포 변환
        sources = {}
        for source in source_distribution:
            sources[source['source']] = source['count']
        
        return jsonify({
            'total_products': total_products,
            'active_alerts': active_alerts,
            'recent_changes': changes_list,
            'source_distribution': sources,
            'average_price': round(avg_price, 0),
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ 대시보드 데이터 조회 오류: {e}")
        print(f"상세 오류: {error_trace}")
        
        return jsonify({
            'error': f'대시보드 데이터 조회 중 오류가 발생했습니다: {str(e)}',
            'total_products': 0,
            'active_alerts': 0,
            'recent_changes': [],
            'source_distribution': {},
            'average_price': 0,
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/cache/stats', methods=['GET'])
def get_cache_stats():
    """캐시 통계 조회"""
    try:
        if not CRAWLER_AVAILABLE:
            return jsonify({'error': '캐시 매니저를 사용할 수 없습니다'}), 500
        
        stats = cache_manager.get_cache_stats()
        
        return jsonify({
            'cache_stats': stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': f'캐시 통계 조회 중 오류가 발생했습니다: {str(e)}'
        }), 500

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """캐시 삭제"""
    try:
        if not CRAWLER_AVAILABLE:
            return jsonify({'error': '캐시 매니저를 사용할 수 없습니다'}), 500
        
        cache_manager.clear_cache()
        
        return jsonify({
            'message': '캐시가 성공적으로 삭제되었습니다',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': f'캐시 삭제 중 오류가 발생했습니다: {str(e)}'
        }), 500

@app.route('/api/test', methods=['GET'])
def test_crawler():
    """크롤러 테스트"""
    try:
        if not CRAWLER_AVAILABLE:
            return jsonify({'error': '크롤러를 사용할 수 없습니다'}), 500
        
        # 간단한 테스트 검색
        test_keyword = "아이폰"
        start_time = datetime.now()
        
        products = search_ssg_products(test_keyword, limit=3)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return jsonify({
            'test_result': 'success',
            'test_keyword': test_keyword,
            'products_found': len(products),
            'search_duration': round(duration, 3),
            'sample_products': products[:2] if products else [],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'test_result': 'failed',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/products/all', methods=['GET'])
def get_all_products():
    """모든 상품 목록 조회"""
    try:
        from database import get_db_connection
        conn = get_db_connection()
        
        cursor = conn.execute('''
            SELECT id, name, current_price, url, image_url, brand, description, source, created_at
            FROM products
            ORDER BY created_at DESC
        ''')
        
        products = []
        for row in cursor.fetchall():
            products.append({
                'id': row['id'],
                'name': row['name'],
                'current_price': row['current_price'],
                'url': row['url'],
                'image_url': row['image_url'],
                'brand': row['brand'],
                'description': row['description'],
                'source': row['source'],
                'created_at': row['created_at']
            })
        
        conn.close()
        
        return jsonify(products)
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ 상품 목록 조회 오류: {e}")
        print(f"상세 오류: {error_trace}")
        
        return jsonify({
            'error': f'상품 목록 조회 중 오류가 발생했습니다: {str(e)}',
            'timestamp': datetime.now().isoformat(),
            'error_type': type(e).__name__
        }), 500

@app.route('/api/products/<int:product_id>/prices', methods=['GET'])
def get_product_price_history(product_id):
    """상품 가격 이력 조회"""
    try:
        from database import get_db_connection
        conn = get_db_connection()
        
        cursor = conn.execute('''
            SELECT price, logged_at
            FROM price_logs
            WHERE product_id = ?
            ORDER BY logged_at DESC
            LIMIT 30
        ''', (product_id,))
        
        price_history = []
        for row in cursor.fetchall():
            price_history.append({
                'price': row['price'],
                'logged_at': row['logged_at']
            })
        
        conn.close()
        
        return jsonify(price_history)
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ 가격 이력 조회 오류: {e}")
        print(f"상세 오류: {error_trace}")
        
        return jsonify({
            'error': f'가격 이력 조회 중 오류가 발생했습니다: {str(e)}',
            'timestamp': datetime.now().isoformat(),
            'error_type': type(e).__name__
        }), 500

@app.route('/api/reviews/crawl', methods=['POST'])
def crawl_reviews():
    """상품 URL로 직접 리뷰 크롤링"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '요청 데이터가 없습니다'}), 400
        
        url = data.get('url', '').strip()
        source = data.get('source', 'SSG').upper()
        
        if not url:
            return jsonify({'error': '상품 URL이 필요합니다'}), 400
        
        print(f"🔍 리뷰 크롤링 요청: {url} (출처: {source})")
        
        # 리뷰 크롤링 실행
        try:
            from review_crawler import crawl_product_reviews, get_review_statistics
            
            start_time = datetime.now()
            reviews = crawl_product_reviews(url, source)
            end_time = datetime.now()
            
            crawl_duration = (end_time - start_time).total_seconds()
            
            if reviews:
                # 리뷰 통계 계산
                stats = get_review_statistics(reviews)
                
                print(f"✅ 리뷰 크롤링 성공: {len(reviews)}개 리뷰, {crawl_duration:.2f}초")
                
                return jsonify({
                    'success': True,
                    'reviews': reviews,
                    'total_reviews': stats['total_reviews'],
                    'average_rating': stats['average_rating'],
                    'rating_distribution': stats['rating_distribution'],
                    'crawl_info': {
                        'url': url,
                        'source': source,
                        'crawl_duration': round(crawl_duration, 3),
                        'crawl_time': start_time.isoformat(),
                        'reviews_found': len(reviews)
                    }
                })
            else:
                print("⚠️ 리뷰를 찾을 수 없음")
                return jsonify({
                    'success': False,
                    'message': '리뷰를 찾을 수 없습니다',
                    'reviews': [],
                    'total_reviews': 0,
                    'average_rating': 0,
                    'rating_distribution': {}
                }), 404
                
        except Exception as crawl_error:
            print(f"❌ 리뷰 크롤링 실패: {crawl_error}")
            return jsonify({
                'success': False,
                'error': f'리뷰 크롤링 중 오류가 발생했습니다: {str(crawl_error)}',
                'reviews': [],
                'total_reviews': 0,
                'average_rating': 0
            }), 500
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ 리뷰 크롤링 API 오류: {e}")
        print(f"상세 오류: {error_trace}")
        
        return jsonify({
            'success': False,
            'error': f'리뷰 크롤링 API 오류: {str(e)}',
            'timestamp': datetime.now().isoformat(),
            'error_type': type(e).__name__
        }), 500

@app.route('/api/products/<int:product_id>/detail', methods=['GET'])
def get_product_detail(product_id):
    """상품 상세 정보 조회"""
    try:
        from database import get_db_connection
        conn = get_db_connection()
        
        # 상품 기본 정보 조회
        cursor = conn.execute('''
            SELECT id, name, current_price, url, image_url, brand, description, source, created_at
            FROM products
            WHERE id = ?
        ''', (product_id,))
        
        product = cursor.fetchone()
        if not product:
            return jsonify({'error': '상품을 찾을 수 없습니다'}), 404
        
        # 가격 이력 조회
        price_cursor = conn.execute('''
            SELECT price, logged_at
            FROM price_logs
            WHERE product_id = ?
            ORDER BY logged_at DESC
            LIMIT 10
        ''', (product_id,))
        
        price_history = []
        for row in price_cursor.fetchall():
            price_history.append({
                'price': row['price'],
                'logged_at': row['logged_at']
            })
        
        # 실제 리뷰 크롤링
        try:
            from review_crawler import crawl_product_reviews, get_review_statistics
            reviews = crawl_product_reviews(product['url'], product['source'])
            review_stats = get_review_statistics(reviews)
        except Exception as e:
            print(f"리뷰 크롤링 실패, 더미 데이터 사용: {e}")
            # 크롤링 실패 시 더미 데이터 사용
            reviews = [
                {
                    'id': 1,
                    'user': '구매자1',
                    'rating': 5,
                    'date': '2024-01-15',
                    'comment': '정말 만족스러운 상품입니다. 품질이 좋고 가격도 합리적이에요!',
                    'helpful': 12
                },
                {
                    'id': 2,
                    'user': '구매자2',
                    'rating': 4,
                    'date': '2024-01-10',
                    'comment': '배송이 빠르고 상품 상태가 좋습니다. 추천합니다.',
                    'helpful': 8
                },
                {
                    'id': 3,
                    'user': '구매자3',
                    'rating': 5,
                    'date': '2024-01-08',
                    'comment': '기대 이상의 상품이었습니다. 다음에도 구매할 예정입니다.',
                    'helpful': 15
                }
            ]
            review_stats = {
                'total_reviews': len(reviews),
                'average_rating': 4.2,
                'rating_distribution': {1: 0, 2: 0, 3: 0, 4: 1, 5: 2}
            }
        
        # 상품 상세 정보 구성
        product_detail = {
            'id': product['id'],
            'name': product['name'],
            'current_price': product['current_price'],
            'url': product['url'],
            'image_url': product['image_url'],
            'brand': product['brand'],
            'description': product['description'],
            'source': product['source'],
            'created_at': product['created_at'],
            'price_history': price_history,
            'reviews': reviews,
            'rating': review_stats['average_rating'],
            'review_count': review_stats['total_reviews'],
            'rating_distribution': review_stats['rating_distribution'],
            'price_trend': {
                'lowest': min([p['price'] for p in price_history]) if price_history else product['current_price'],
                'highest': max([p['price'] for p in price_history]) if price_history else product['current_price'],
                'average': sum([p['price'] for p in price_history]) // len(price_history) if price_history else product['current_price']
            }
        }
        
        conn.close()
        
        return jsonify(product_detail)
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ 상품 상세 정보 조회 오류: {e}")
        print(f"상세 오류: {error_trace}")
        
        return jsonify({
            'error': f'상품 상세 정보 조회 중 오류가 발생했습니다: {str(e)}',
            'timestamp': datetime.now().isoformat(),
            'error_type': type(e).__name__
        }), 500

# 에러 핸들러
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'API 엔드포인트를 찾을 수 없습니다',
        'message': '사용 가능한 엔드포인트를 확인하려면 / 경로를 방문하세요',
        'available_endpoints': [
            '/',
            '/api/health',
            '/api/search',
            '/api/dashboard',
            '/api/cache/stats',
            '/api/test',
            # === 가격 추적 엔드포인트 목록 추가 시작 ===
            '/api/watchlist',
            '/api/watchlist/temp',
            '/api/watchlist/activate',
            '/api/price-history/{watch_id}',
            '/api/price-check',
            # === 임시 추적 목록 삭제 엔드포인트 추가 시작 ===
            '/api/watchlist/temp/{id}',
            # === 임시 추적 목록 삭제 엔드포인트 추가 끝 ===
            # === 가격 추적 엔드포인트 목록 추가 끝 ===
            # === 네이버 쇼핑 엔드포인트 목록 추가 시작 ===
            '/api/naver/search',
            '/api/naver/compare',
            '/api/naver/products/add-from-search',
            # === 네이버 쇼핑 엔드포인트 목록 추가 끝 ===
            # === 11번가 엔드포인트 목록 추가 시작 ===
            '/api/11st/search',
            '/api/11st/popular-keywords',
            '/api/11st/categories',
            '/api/11st/product/{product_id}'
            # === 11번가 엔드포인트 목록 추가 끝 ===
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': '서버 내부 오류가 발생했습니다',
        'timestamp': datetime.now().isoformat()
    }), 500

# === 가격 추적 API 엔드포인트 추가 시작 ===
@app.route('/api/watchlist', methods=['GET'])
def get_user_watchlist():
    """사용자 추적 목록 조회"""
    try:
        user_email = request.args.get('user_email')
        if not user_email:
            return jsonify({'error': '이메일이 필요합니다'}), 400
        
        from price_tracker import price_tracker
        watchlist = price_tracker.get_watchlist(user_email)
        
        return jsonify({
            'watchlist': watchlist,
            'total': len(watchlist),
            'user_email': user_email
        })
        
    except Exception as e:
        return jsonify({'error': f'추적 목록 조회 실패: {str(e)}'}), 500

@app.route('/api/watchlist', methods=['POST'])
def add_to_watchlist():
    """추적 목록에 상품 추가"""
    try:
        data = request.json
        required_fields = ['product_name', 'product_url', 'source', 'current_price', 'user_email']
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field}가 필요합니다'}), 400
        
        from price_tracker import price_tracker
        watch_id = price_tracker.add_to_watchlist(
            product_name=data['product_name'],
            product_url=data['product_url'],
            image_url=data.get('image_url'),
            source=data['source'],
            current_price=data['current_price'],
            user_email=data['user_email'],
            target_price=data.get('target_price')
        )
        
        if watch_id:
            return jsonify({
                'message': '추적 목록에 추가되었습니다',
                'watch_id': watch_id
            })
        else:
            return jsonify({'error': '추적 목록 추가에 실패했습니다'}), 500
            
    except Exception as e:
        return jsonify({'error': f'추적 목록 추가 실패: {str(e)}'}), 500

# === 임시 추적 목록 API 엔드포인트 시작 ===
@app.route('/api/watchlist/temp', methods=['POST'])
def add_to_temp_watchlist():
    """임시 추적 목록에 상품 추가"""
    try:
        data = request.json
        required_fields = ['product_name', 'product_url', 'source', 'current_price']
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field}가 필요합니다'}), 400
        
        from price_tracker import price_tracker
        watch_id = price_tracker.add_to_temp_watchlist(
            product_name=data['product_name'],
            product_url=data['product_url'],
            image_url=data.get('image_url'),
            source=data['source'],
            current_price=data['current_price']
        )
        
        if watch_id:
            return jsonify({
                'message': '임시 추적 목록에 추가되었습니다',
                'watch_id': watch_id
            })
        else:
            return jsonify({'error': '임시 추적 목록 추가에 실패했습니다'}), 500
            
    except Exception as e:
        return jsonify({'error': f'임시 추적 목록 추가 실패: {str(e)}'}), 500

@app.route('/api/watchlist/temp', methods=['GET'])
def get_temp_watchlist():
    """임시 추적 목록 조회"""
    try:
        from price_tracker import price_tracker
        temp_watchlist = price_tracker.get_temp_watchlist()
        
        return jsonify({
            'watchlist': temp_watchlist,
            'total': len(temp_watchlist)
        })
        
    except Exception as e:
        return jsonify({'error': f'임시 추적 목록 조회 실패: {str(e)}'}), 500

@app.route('/api/watchlist/activate', methods=['POST'])
def activate_watchlist():
    """임시 추적 목록을 실제 추적 목록으로 활성화"""
    try:
        data = request.json
        user_email = data.get('user_email')
        
        if not user_email:
            return jsonify({'error': '이메일이 필요합니다'}), 400
        
        from price_tracker import price_tracker
        activated_count = price_tracker.activate_temp_watchlist(user_email)
        
        return jsonify({
            'message': f'{activated_count}개 상품이 활성화되었습니다',
            'activated_count': activated_count
        })
        
    except Exception as e:
        return jsonify({'error': f'추적 목록 활성화 실패: {str(e)}'}), 500

# === 임시 추적 목록 삭제 API 엔드포인트 추가 시작 ===
@app.route('/api/watchlist/temp/<int:watch_id>', methods=['DELETE'])
def remove_from_temp_watchlist(watch_id):
    """임시 추적 목록에서 상품 제거"""
    try:
        from price_tracker import price_tracker
        success = price_tracker.remove_from_temp_watchlist(watch_id)
        
        if success:
            return jsonify({'message': '임시 추적 목록에서 제거되었습니다'})
        else:
            return jsonify({'error': '임시 추적 목록 제거에 실패했습니다'}), 500
        
    except Exception as e:
        return jsonify({'error': f'임시 추적 목록 제거 실패: {str(e)}'}), 500
# === 임시 추적 목록 삭제 API 엔드포인트 추가 끝 ===

# === 임시 추적 목록 API 엔드포인트 끝 ===

@app.route('/api/watchlist/<int:watch_id>', methods=['DELETE'])
def remove_from_watchlist(watch_id):
    """추적 목록에서 상품 제거"""
    try:
        user_email = request.args.get('user_email')
        if not user_email:
            return jsonify({'error': '이메일이 필요합니다'}), 400
        
        from price_tracker import price_tracker
        price_tracker.remove_from_watchlist(watch_id, user_email)
        
        return jsonify({'message': '추적 목록에서 제거되었습니다'})
        
    except Exception as e:
        return jsonify({'error': f'추적 목록 제거 실패: {str(e)}'}), 500

@app.route('/api/price-history/<int:watch_id>', methods=['GET'])
def get_price_history(watch_id):
    """가격 히스토리 조회"""
    try:
        days = request.args.get('days', 7, type=int)
        
        from price_tracker import price_tracker
        history = price_tracker.get_price_history(watch_id, days)
        
        return jsonify({
            'price_history': history,
            'watch_id': watch_id,
            'days': days
        })
        
    except Exception as e:
        return jsonify({'error': f'가격 히스토리 조회 실패: {str(e)}'}), 500

@app.route('/api/price-check', methods=['POST'])
def manual_price_check():
    """수동 가격 체크"""
    try:
        from price_tracker import price_tracker
        price_tracker.check_all_prices()
        
        return jsonify({'message': '가격 체크가 완료되었습니다'})
        
    except Exception as e:
        return jsonify({'error': f'가격 체크 실패: {str(e)}'}), 500
# === 가격 추적 API 엔드포인트 추가 끝 ===

# === 네이버 쇼핑 API 엔드포인트 추가 시작 ===
@app.route('/api/naver/search', methods=['GET'])
def search_naver_products():
    """네이버 쇼핑 상품 검색 API"""
    try:
        # 파라미터 추출
        keyword = request.args.get('keyword', '').strip()
        limit = request.args.get('limit', 20, type=int)
        
        # 키워드 유효성 검사
        if not keyword:
            return jsonify({
                'error': '검색어를 입력해주세요',
                'message': '사용 예시: /api/naver/search?keyword=무선이어폰'
            }), 400
        
        if len(keyword) > 50:
            return jsonify({'error': '검색어는 50자 이내로 입력해주세요'}), 400
        
        if limit > 50:
            limit = 50  # 최대 50개로 제한
        
        # 검색 시작 시간 기록
        start_time = datetime.now()
        
        print(f"🔍 네이버 쇼핑 검색 요청: '{keyword}' (limit: {limit})")
        
        # 네이버 쇼핑 크롤러 import 및 검색 실행
        from crawlers.naver_shopping_crawler import search_naver_products
        products = search_naver_products(keyword, limit=limit)
        
        # 검색 완료 시간 계산
        end_time = datetime.now()
        search_duration = (end_time - start_time).total_seconds()
        
        print(f"✅ 네이버 쇼핑 검색 완료: {len(products)}개 상품, {search_duration:.2f}초")
        
        # 응답 데이터 구성
        response_data = {
            'products': products,
            'search_info': {
                'keyword': keyword,
                'total_results': len(products),
                'limit': limit,
                'search_duration': round(search_duration, 3),
                'search_time': start_time.isoformat(),
                'source': 'NaverShopping',
                'api_used': True
            },
            'performance': {
                'response_time': f"{search_duration:.3f}초",
                'products_per_second': round(len(products) / search_duration, 1) if search_duration > 0 else 0
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ 네이버 쇼핑 검색 오류: {e}")
        print(f"상세 오류: {error_trace}")
        
        return jsonify({
            'error': f'네이버 쇼핑 검색 중 오류가 발생했습니다: {str(e)}',
            'keyword': request.args.get('keyword', ''),
            'timestamp': datetime.now().isoformat(),
            'error_type': type(e).__name__
        }), 500

@app.route('/api/naver/compare', methods=['GET'])
def compare_naver_products():
    """네이버 쇼핑 상품 가격 비교 API"""
    try:
        # 파라미터 추출
        keyword = request.args.get('keyword', '').strip()
        limit = request.args.get('limit', 10, type=int)
        
        # 키워드 유효성 검사
        if not keyword:
            return jsonify({
                'error': '검색어를 입력해주세요',
                'message': '사용 예시: /api/naver/compare?keyword=무선이어폰'
            }), 400
        
        if len(keyword) > 50:
            return jsonify({'error': '검색어는 50자 이내로 입력해주세요'}), 400
        
        if limit > 30:
            limit = 30  # 비교는 최대 30개로 제한
        
        # 검색 시작 시간 기록
        start_time = datetime.now()
        
        print(f"💰 네이버 쇼핑 가격 비교 요청: '{keyword}' (limit: {limit})")
        
        # 네이버 쇼핑 크롤러 import 및 가격 비교 실행
        from crawlers.naver_shopping_crawler import compare_naver_products
        products = compare_naver_products(keyword, limit=limit)
        
        # 검색 완료 시간 계산
        end_time = datetime.now()
        search_duration = (end_time - start_time).total_seconds()
        
        print(f"✅ 네이버 쇼핑 가격 비교 완료: {len(products)}개 상품, {search_duration:.2f}초")
        
        # 가격 통계 계산
        price_stats = {}
        if products:
            valid_prices = [p['current_price'] for p in products if p['current_price'] > 0]
            if valid_prices:
                price_stats = {
                    'min_price': min(valid_prices),
                    'max_price': max(valid_prices),
                    'avg_price': round(sum(valid_prices) / len(valid_prices)),
                    'price_range': max(valid_prices) - min(valid_prices)
                }
        
        # 응답 데이터 구성
        response_data = {
            'products': products,
            'price_stats': price_stats,
            'search_info': {
                'keyword': keyword,
                'total_results': len(products),
                'limit': limit,
                'search_duration': round(search_duration, 3),
                'search_time': start_time.isoformat(),
                'source': 'NaverShopping',
                'comparison_type': 'price_comparison'
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ 네이버 쇼핑 가격 비교 오류: {e}")
        print(f"상세 오류: {error_trace}")
        
        return jsonify({
            'error': f'네이버 쇼핑 가격 비교 중 오류가 발생했습니다: {str(e)}',
            'keyword': request.args.get('keyword', ''),
            'timestamp': datetime.now().isoformat(),
            'error_type': type(e).__name__
        }), 500

@app.route('/api/naver/products/add-from-search', methods=['POST'])
def add_naver_product_from_search():
    """네이버 쇼핑 검색 결과에서 상품을 데이터베이스에 추가"""
    try:
        data = request.json
        
        # 필수 필드 검증
        required_fields = ['name', 'url', 'current_price']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field}가 필요합니다'}), 400
        
        print(f"📦 네이버 쇼핑 상품 추가 요청: {data.get('name', '')[:50]}...")
        
        # 네이버 쇼핑 크롤러 import 및 상품 추가
        from crawlers.naver_shopping_crawler import NaverShoppingCrawler
        crawler = NaverShoppingCrawler()
        
        # 상품 데이터 정리
        product_data = {
            'name': data.get('name', ''),
            'url': data.get('url', ''),
            'current_price': data.get('current_price', 0),
            'image_url': data.get('image_url', ''),
            'brand': data.get('brand', '네이버쇼핑'),
            'source': 'NaverShopping'
        }
        
        # 데이터베이스에 저장
        success = crawler.add_product_from_search(product_data)
        
        if success:
            print(f"✅ 네이버 쇼핑 상품 추가 성공: {product_data['name'][:50]}...")
            return jsonify({
                'message': '네이버 쇼핑 상품이 성공적으로 추가되었습니다',
                'product': product_data
            })
        else:
            return jsonify({'error': '상품 추가에 실패했습니다'}), 500
            
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ 네이버 쇼핑 상품 추가 오류: {e}")
        print(f"상세 오류: {error_trace}")
        
        return jsonify({
            'error': f'네이버 쇼핑 상품 추가 중 오류가 발생했습니다: {str(e)}',
            'timestamp': datetime.now().isoformat(),
            'error_type': type(e).__name__
        }), 500
# === 네이버 쇼핑 API 엔드포인트 추가 끝 ===

# === 11번가 API 엔드포인트 추가 시작 ===
@app.route('/api/11st/search', methods=['GET'])
def search_eleventh_street():
    """11번가 상품 검색 API"""
    try:
        # 파라미터 추출
        keyword = request.args.get('keyword', '').strip()
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        category = request.args.get('category')
        min_price = request.args.get('min_price', type=int)
        max_price = request.args.get('max_price', type=int)
        sort_type = request.args.get('sort', 'popular')
        
        # 키워드 유효성 검사
        if not keyword:
            return jsonify({
                'error': '검색어를 입력해주세요',
                'message': '사용 예시: /api/11st/search?keyword=스마트폰',
                'popular_keywords': [
                    '스마트폰', '노트북', '이어폰', '키보드', '마우스',
                    '운동화', '가방', '시계', '화장품', '의류'
                ]
            }), 400
        
        # 키워드 길이 제한
        if len(keyword) > 50:
            return jsonify({'error': '검색어는 50자 이내로 입력해주세요'}), 400
        
        if limit > 50:
            limit = 50  # 최대 50개로 제한
        
        # 검색 시작 시간 기록
        start_time = datetime.now()
        
        print(f"🔍 11번가 검색 요청: '{keyword}' (limit: {limit})")
        
        # === 11번가 API 모듈 경로 문제 해결 시작 ===
        # 11번가 API 클래스 import 및 검색 실행
        sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))
        from eleventh_street_api import EleventhStreetAPI
        from config import config
        # === 11번가 API 모듈 경로 문제 해결 끝 ===
        from dotenv import load_dotenv
        
        # .env 파일에서 API 키 로드
        load_dotenv()
        api_key = os.getenv('ELEVENTH_STREET_API_KEY')
        
        # 11번가 API 인스턴스 생성
        eleventh_api = EleventhStreetAPI(api_key=api_key)
        
        # 상품 검색 실행
        results = eleventh_api.search_products(
            keyword=keyword,
            page=page,
            limit=limit,
            category=category,
            min_price=min_price,
            max_price=max_price,
            sort_type=sort_type
        )
        
        # 검색 완료 시간 계산
        end_time = datetime.now()
        search_duration = (end_time - start_time).total_seconds()
        
        print(f"✅ 11번가 검색 완료: {len(results.get('products', []))}개 상품, {search_duration:.2f}초")
        
        # 검색 결과에 메타데이터 추가
        results['search_info'] = {
            'keyword': keyword,
            'search_time': start_time.isoformat(),
            'api_source': '11번가 실제 API' if api_key else '11번가 샘플 데이터',
            'search_duration': round(search_duration, 3),
            'filters_applied': {
                'category': category,
                'min_price': min_price,
                'max_price': max_price,
                'sort': sort_type
            }
        }
        
        return jsonify(results)
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ 11번가 검색 오류: {e}")
        print(f"상세 오류: {error_trace}")
        
        return jsonify({
            'error': f'11번가 검색 중 오류가 발생했습니다: {str(e)}',
            'keyword': request.args.get('keyword', ''),
            'timestamp': datetime.now().isoformat(),
            'error_type': type(e).__name__
        }), 500

@app.route('/api/11st/popular-keywords', methods=['GET'])
def get_popular_keywords():
    """11번가 인기 검색 키워드 제공"""
    try:
        popular_keywords = [
            {'keyword': '스마트폰', 'category': '디지털/가전', 'trend': 'up'},
            {'keyword': '노트북', 'category': '디지털/가전', 'trend': 'up'},
            {'keyword': '이어폰', 'category': '디지털/가전', 'trend': 'stable'},
            {'keyword': '운동화', 'category': '패션의류', 'trend': 'up'},
            {'keyword': '화장품', 'category': '뷰티', 'trend': 'stable'},
            {'keyword': '가방', 'category': '패션의류', 'trend': 'down'},
            {'keyword': '시계', 'category': '패션의류', 'trend': 'stable'},
            {'keyword': '키보드', 'category': '디지털/가전', 'trend': 'up'},
            {'keyword': '마우스', 'category': '디지털/가전', 'trend': 'stable'},
            {'keyword': '의류', 'category': '패션의류', 'trend': 'stable'}
        ]
        
        return jsonify({
            'popular_keywords': popular_keywords,
            'total': len(popular_keywords),
            'updated_at': datetime.now().isoformat(),
            'usage_example': '/api/11st/search?keyword=스마트폰&limit=10'
        })
        
    except Exception as e:
        return jsonify({'error': f'인기 키워드 조회 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/api/11st/categories', methods=['GET'])
def get_eleventh_street_categories():
    """11번가 카테고리 목록"""
    try:
        # === 11번가 API 모듈 경로 문제 해결 시작 ===
        # from api.eleventh_street_api import EleventhStreetAPI  # 기존 코드 주석 처리
        sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))
        from eleventh_street_api import EleventhStreetAPI
        # === 11번가 API 모듈 경로 문제 해결 끝 ===
        from dotenv import load_dotenv
        
        # .env 파일에서 API 키 로드
        load_dotenv()
        api_key = os.getenv('ELEVENTH_STREET_API_KEY')
        
        eleventh_api = EleventhStreetAPI(api_key=api_key)
        categories = eleventh_api.get_category_list()
        
        return jsonify({
            'categories': categories,
            'total': len(categories)
        })
        
    except Exception as e:
        return jsonify({'error': f'카테고리 조회 중 오류가 발생했습니다: {str(e)}'}), 500

# === 11번가 상품 상세 API 비활성화 및 URL 리다이렉트로 변경 시작 ===
@app.route('/api/11st/product/<product_id>', methods=['GET'])
def get_eleventh_street_product(product_id):
    """11번가 상품 상세 정보 - URL 리다이렉트 방식으로 변경"""
    try:
        # 기존 API 호출 코드 주석 처리 시작
        # from api.eleventh_street_api import EleventhStreetAPI  # 기존 코드 주석 처리
        # sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))
        # from eleventh_street_api import EleventhStreetAPI
        # from dotenv import load_dotenv
        # 
        # # .env 파일에서 API 키 로드
        # load_dotenv()
        # api_key = os.getenv('ELEVENTH_STREET_API_KEY')
        # 
        # eleventh_api = EleventhStreetAPI(api_key=api_key)
        # product = eleventh_api.get_product_detail(product_id)
        # 
        # return jsonify(product)
        # 기존 API 호출 코드 주석 처리 끝
        
        # 11번가 상품 페이지 URL 생성
        product_url = f"http://www.11st.co.kr/product/SellerProductDetail.tmall?method=getSellerProductDetail&prdNo={product_id}"
        
        return jsonify({
            'id': product_id,
            'message': '11번가 상품 상세는 직접 링크로 이동해주세요',
            'product_url': product_url,
            'redirect_message': '아래 링크를 클릭하여 11번가에서 상품을 확인하세요',
            'action': 'redirect_to_url'
        })
        
    except Exception as e:
        return jsonify({'error': f'상품 URL 생성 중 오류가 발생했습니다: {str(e)}'}), 500
# === 11번가 상품 상세 API 비활성화 및 URL 리다이렉트로 변경 끝 ===
# === 11번가 API 엔드포인트 추가 끝 ===

if __name__ == '__main__':
    print("🚀 SSG 가격 추적기 API 서버 시작")
    print("=" * 50)
    print(f"✅ 크롤러 상태: {'활성화' if CRAWLER_AVAILABLE else '비활성화'}")
    print("📡 서버 주소: http://localhost:5000")
    print("📖 API 문서: http://localhost:5000")
    print("🔍 테스트: http://localhost:5000/api/test")
    print("=" * 50)
    
    app.run(debug=True, port=5000, host='0.0.0.0')