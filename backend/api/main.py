# Flask API 메인 애플리케이션 (고도화 버전)
from flask import Flask, request, jsonify
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Database imports - 선택적 import로 변경
try:
    from database import init_db, get_db_connection
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    print("⚠️ database 모듈을 찾을 수 없습니다.")
# Blueprint imports - 선택적 import로 변경
try:
    from advanced_search import advanced_search_bp
    ADVANCED_SEARCH_AVAILABLE = True
except ImportError:
    ADVANCED_SEARCH_AVAILABLE = False
    print("⚠️ advanced_search 모듈을 찾을 수 없습니다.")

try:
    from product_comparison import product_comparison_bp
    PRODUCT_COMPARISON_AVAILABLE = True
except ImportError:
    PRODUCT_COMPARISON_AVAILABLE = False
    print("⚠️ product_comparison 모듈을 찾을 수 없습니다.")

try:
    from data_processing import data_processing_bp
    DATA_PROCESSING_AVAILABLE = True
except ImportError:
    DATA_PROCESSING_AVAILABLE = False
    print("⚠️ data_processing 모듈을 찾을 수 없습니다.")
# 추가 모듈 imports - 선택적 import로 변경
try:
    from eleventh_street_api import EleventhStreetAPI
    ELEVENTH_API_AVAILABLE = True
except ImportError:
    ELEVENTH_API_AVAILABLE = False
    print("⚠️ eleventh_street_api 모듈을 찾을 수 없습니다.")

try:
    from config import config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    print("⚠️ config 모듈을 찾을 수 없습니다.")
import sqlite3
from datetime import datetime
import traceback

# Flask 앱 생성
app = Flask(__name__)

# 한글 인코딩 설정
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# Blueprint 등록 (조건부)
if ADVANCED_SEARCH_AVAILABLE:
    app.register_blueprint(advanced_search_bp)
    print("✅ advanced_search Blueprint 등록됨")

if PRODUCT_COMPARISON_AVAILABLE:
    app.register_blueprint(product_comparison_bp)
    print("✅ product_comparison Blueprint 등록됨")

if DATA_PROCESSING_AVAILABLE:
    app.register_blueprint(data_processing_bp)
    print("✅ data_processing Blueprint 등록됨")

# 11번가 API 인스턴스 (조건부)
if ELEVENTH_API_AVAILABLE:
    eleventh_api = EleventhStreetAPI()
    print("✅ 11번가 API 인스턴스 생성됨")
else:
    eleventh_api = None
    print("⚠️ 11번가 API를 사용할 수 없습니다.")

# 데이터베이스 초기화 (조건부)
if DATABASE_AVAILABLE:
    init_db()
    print("✅ 데이터베이스 초기화됨")
else:
    print("⚠️ 데이터베이스를 사용할 수 없습니다.")

@app.route('/', methods=['GET'])
def index():
    """기본 페이지 - 사용자 키워드 선택 가이드"""
    return jsonify({
        'message': '🚀 11번가 API 고도화 시스템',
        'version': '2.0.0',
        'description': '사용자가 원하는 키워드로 실제 11번가 상품을 검색할 수 있습니다',
        'api_endpoints': {
            'health': '/api/health',
            '11st_search': '/api/11st/search?keyword={사용자_키워드}',
            'popular_keywords': '/api/11st/popular-keywords',
            'advanced_search': '/api/search/advanced?keyword={키워드}',
            'dashboard': '/api/dashboard/advanced',
            'categories': '/api/11st/categories'
        },
        'search_examples': {
            '스마트폰 검색': '/api/11st/search?keyword=스마트폰&limit=10',
            '노트북 검색': '/api/11st/search?keyword=노트북&min_price=500000&max_price=2000000',
            '이어폰 검색': '/api/11st/search?keyword=이어폰&sort=price_low',
            '화장품 검색': '/api/11st/search?keyword=화장품&limit=5'
        },
        'search_parameters': {
            'keyword': '검색할 키워드 (필수)',
            'limit': '결과 개수 (기본값: 20)',
            'page': '페이지 번호 (기본값: 1)',
            'min_price': '최소 가격',
            'max_price': '최대 가격',
            'sort': 'popular, price_low, price_high, newest, review'
        },
        'status': 'running',
        'api_key_status': '✅ 실제 11번가 API 연동됨'
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """API 상태 확인"""
    try:
        if DATABASE_AVAILABLE:
            conn = get_db_connection()
            conn.execute('SELECT 1').fetchone()
            conn.close()
            db_status = 'connected'
        else:
            db_status = 'not_available'
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': db_status,
            'version': '2.0.0',
            'modules': {
                'database': DATABASE_AVAILABLE,
                'advanced_search': ADVANCED_SEARCH_AVAILABLE,
                'product_comparison': PRODUCT_COMPARISON_AVAILABLE,
                'data_processing': DATA_PROCESSING_AVAILABLE,
                'eleventh_api': ELEVENTH_API_AVAILABLE,
                'config': CONFIG_AVAILABLE
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/dashboard/advanced', methods=['GET'])
def get_advanced_dashboard():
    """고도화된 대시보드 데이터"""
    if not DATABASE_AVAILABLE:
        return jsonify({
            'error': '데이터베이스를 사용할 수 없습니다',
            'message': '대시보드 기능을 사용하려면 데이터베이스 설정이 필요합니다'
        }), 503
    
    try:
        conn = get_db_connection()
        
        # 기본 통계
        basic_stats = conn.execute('''
            SELECT 
                COUNT(*) as total_products,
                COUNT(DISTINCT source) as total_sources,
                COUNT(DISTINCT brand) as total_brands,
                AVG(current_price) as avg_price
            FROM products
            WHERE current_price > 0
        ''').fetchone()
        
        # 최근 7일 가격 변동
        recent_price_changes = conn.execute('''
            SELECT 
                p.name,
                p.current_price,
                pl.price as previous_price,
                pl.logged_at,
                ((p.current_price - pl.price) * 100.0 / pl.price) as change_percent
            FROM products p
            JOIN price_logs pl ON p.id = pl.product_id
            WHERE pl.logged_at >= datetime('now', '-7 days')
            ORDER BY ABS(change_percent) DESC
            LIMIT 10
        ''').fetchall()
        
        # 소스별 상품 분포
        source_distribution = conn.execute('''
            SELECT 
                source,
                COUNT(*) as count,
                AVG(current_price) as avg_price
            FROM products
            WHERE current_price > 0
            GROUP BY source
            ORDER BY count DESC
        ''').fetchall()
        
        # 인기 브랜드 (상품 수 기준)
        popular_brands = conn.execute('''
            SELECT 
                brand,
                COUNT(*) as product_count,
                AVG(current_price) as avg_price,
                MIN(current_price) as min_price,
                MAX(current_price) as max_price
            FROM products
            WHERE brand IS NOT NULL AND brand != '' AND current_price > 0
            GROUP BY brand
            ORDER BY product_count DESC
            LIMIT 10
        ''').fetchall()
        
        # 활성 알림 통계
        alert_stats = conn.execute('''
            SELECT 
                COUNT(*) as total_alerts,
                COUNT(CASE WHEN is_active = 1 THEN 1 END) as active_alerts,
                COUNT(DISTINCT user_email) as unique_users,
                AVG(target_price) as avg_target_price
            FROM alerts
        ''').fetchone()
        
        conn.close()
        
        return jsonify({
            'basic_stats': dict(basic_stats) if basic_stats else {},
            'recent_price_changes': [dict(row) for row in recent_price_changes],
            'source_distribution': [dict(row) for row in source_distribution],
            'popular_brands': [dict(row) for row in popular_brands],
            'alert_stats': dict(alert_stats) if alert_stats else {},
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'대시보드 데이터 조회 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/api/products/trending', methods=['GET'])
def get_trending_products():
    """인기 상품 조회"""
    if not DATABASE_AVAILABLE:
        return jsonify({
            'error': '데이터베이스를 사용할 수 없습니다',
            'message': '인기 상품 기능을 사용하려면 데이터베이스 설정이 필요합니다'
        }), 503
    
    try:
        limit = request.args.get('limit', 20, type=int)
        category = request.args.get('category')
        
        conn = get_db_connection()
        
        query = '''
            SELECT 
                p.*,
                COUNT(pl.id) as price_log_count,
                COUNT(a.id) as alert_count,
                (COUNT(pl.id) + COUNT(a.id) * 2) as popularity_score
            FROM products p
            LEFT JOIN price_logs pl ON p.id = pl.product_id
            LEFT JOIN alerts a ON p.id = a.product_id
            WHERE p.current_price > 0
        '''
        
        params = []
        
        if category:
            # 브랜드를 카테고리로 사용
            query += ' AND p.brand LIKE ?'
            params.append(f'%{category}%')
        
        query += '''
            GROUP BY p.id
            ORDER BY popularity_score DESC, p.created_at DESC
            LIMIT ?
        '''
        params.append(limit)
        
        trending_products = conn.execute(query, params).fetchall()
        conn.close()
        
        return jsonify({
            'trending_products': [dict(product) for product in trending_products],
            'total': len(trending_products),
            'category': category,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'인기 상품 조회 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/api/products/recommendations', methods=['GET'])
def get_product_recommendations():
    """상품 추천"""
    if not DATABASE_AVAILABLE:
        return jsonify({
            'error': '데이터베이스를 사용할 수 없습니다',
            'message': '상품 추천 기능을 사용하려면 데이터베이스 설정이 필요합니다'
        }), 503
    
    try:
        user_email = request.args.get('user_email')
        limit = request.args.get('limit', 10, type=int)
        
        if not user_email:
            # 일반 추천 (가성비 기준)
            recommendations = _get_general_recommendations(limit)
        else:
            # 개인화 추천
            recommendations = _get_personalized_recommendations(user_email, limit)
        
        return jsonify({
            'recommendations': recommendations,
            'user_email': user_email,
            'total': len(recommendations),
            'recommendation_type': 'personalized' if user_email else 'general'
        })
        
    except Exception as e:
        return jsonify({'error': f'상품 추천 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/api/alerts/smart', methods=['POST'])
def create_smart_alert():
    """스마트 알림 생성 (가격 예측 기반)"""
    if not DATABASE_AVAILABLE:
        return jsonify({
            'error': '데이터베이스를 사용할 수 없습니다',
            'message': '스마트 알림 기능을 사용하려면 데이터베이스 설정이 필요합니다'
        }), 503
    
    try:
        data = request.json
        product_id = data.get('product_id')
        user_email = data.get('user_email')
        alert_type = data.get('type', 'price_drop')  # price_drop, target_price, discount
        
        if not all([product_id, user_email]):
            return jsonify({'error': '상품 ID와 이메일이 필요합니다'}), 400
        
        conn = get_db_connection()
        
        # 상품 정보 조회
        product = conn.execute('''
            SELECT * FROM products WHERE id = ?
        ''', (product_id,)).fetchone()
        
        if not product:
            return jsonify({'error': '상품을 찾을 수 없습니다'}), 400
        
        # 가격 이력 분석
        price_history = conn.execute('''
            SELECT price, logged_at 
            FROM price_logs 
            WHERE product_id = ? 
            ORDER BY logged_at DESC 
            LIMIT 30
        ''', (product_id,)).fetchall()
        
        # 스마트 목표 가격 계산
        target_price = _calculate_smart_target_price(
            product['current_price'], 
            [p['price'] for p in price_history],
            alert_type
        )
        
        # 알림 생성
        conn.execute('''
            INSERT INTO alerts (product_id, user_email, target_price, is_active)
            VALUES (?, ?, ?, 1)
        ''', (product_id, user_email, target_price))
        
        alert_id = conn.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'alert_id': alert_id,
            'message': '스마트 알림이 생성되었습니다',
            'target_price': target_price,
            'current_price': product['current_price'],
            'expected_savings': product['current_price'] - target_price,
            'alert_type': alert_type
        })
        
    except Exception as e:
        return jsonify({'error': f'스마트 알림 생성 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/api/11st/categories', methods=['GET'])
def get_eleventh_street_categories():
    """11번가 카테고리 목록"""
    if not ELEVENTH_API_AVAILABLE or not eleventh_api:
        return jsonify({
            'error': '11번가 API를 사용할 수 없습니다',
            'message': '11번가 API 기능을 사용하려면 API 설정이 필요합니다'
        }), 503
    
    try:
        categories = eleventh_api.get_category_list()
        return jsonify({
            'categories': categories,
            'total': len(categories)
        })
    except Exception as e:
        return jsonify({'error': f'카테고리 조회 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/api/11st/search', methods=['GET'])
def search_eleventh_street():
    """11번가 상품 검색 - 사용자 키워드 선택"""
    try:
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
        
        # 11번가 API 호출
        results = eleventh_api.search_products(
            keyword=keyword,
            page=page,
            limit=limit,
            category=category,
            min_price=min_price,
            max_price=max_price,
            sort_type=sort_type
        )
        
        # 검색 결과에 메타데이터 추가
        results['search_info'] = {
            'keyword': keyword,
            'search_time': datetime.now().isoformat(),
            'api_source': '11번가 실제 API',
            'filters_applied': {
                'category': category,
                'min_price': min_price,
                'max_price': max_price,
                'sort': sort_type
            }
        }
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': f'11번가 검색 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/api/11st/popular-keywords', methods=['GET'])
def get_popular_keywords():
    """인기 검색 키워드 제공"""
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

@app.route('/api/11st/product/<product_id>', methods=['GET'])
def get_eleventh_street_product(product_id):
    """11번가 상품 상세 정보"""
    try:
        product = eleventh_api.get_product_detail(product_id)
        return jsonify(product)
    except Exception as e:
        return jsonify({'error': f'상품 상세 조회 중 오류가 발생했습니다: {str(e)}'}), 500

def _get_general_recommendations(limit: int):
    """일반 추천 상품"""
    try:
        conn = get_db_connection()
        
        # 가성비 좋은 상품 (가격 대비 높은 평점 - 시뮬레이션)
        recommendations = conn.execute('''
            SELECT 
                p.*,
                COUNT(pl.id) as price_updates,
                COUNT(a.id) as alert_count
            FROM products p
            LEFT JOIN price_logs pl ON p.id = pl.product_id
            LEFT JOIN alerts a ON p.id = a.product_id
            WHERE p.current_price > 0
            GROUP BY p.id
            ORDER BY (alert_count + price_updates) DESC, p.current_price ASC
            LIMIT ?
        ''', (limit,)).fetchall()
        
        conn.close()
        
        result = []
        for product in recommendations:
            product_dict = dict(product)
            product_dict['recommendation_reason'] = '가성비 우수'
            product_dict['recommendation_score'] = min(100, (product['alert_count'] * 10 + product['price_updates'] * 5))
            result.append(product_dict)
        
        return result
        
    except Exception:
        return []

def _get_personalized_recommendations(user_email: str, limit: int):
    """개인화 추천 상품"""
    try:
        conn = get_db_connection()
        
        # 사용자의 알림 설정 기반 추천
        user_interests = conn.execute('''
            SELECT 
                p.brand,
                AVG(a.target_price) as avg_target_price,
                COUNT(*) as interest_count
            FROM alerts a
            JOIN products p ON a.product_id = p.id
            WHERE a.user_email = ?
            GROUP BY p.brand
            ORDER BY interest_count DESC
        ''', (user_email,)).fetchall()
        
        if not user_interests:
            return _get_general_recommendations(limit)
        
        # 관심 브랜드 기반 추천
        interested_brands = [interest['brand'] for interest in user_interests[:3]]
        
        recommendations = []
        for brand in interested_brands:
            brand_products = conn.execute('''
                SELECT * FROM products 
                WHERE brand = ? AND current_price > 0
                ORDER BY current_price ASC
                LIMIT ?
            ''', (brand, limit // len(interested_brands) + 1)).fetchall()
            
            for product in brand_products:
                product_dict = dict(product)
                product_dict['recommendation_reason'] = f'관심 브랜드: {brand}'
                product_dict['recommendation_score'] = 85
                recommendations.append(product_dict)
        
        conn.close()
        
        return recommendations[:limit]
        
    except Exception:
        return _get_general_recommendations(limit)

def _calculate_smart_target_price(current_price: int, price_history: list, alert_type: str):
    """스마트 목표 가격 계산"""
    if not price_history:
        # 기본 할인율 적용
        if alert_type == 'price_drop':
            return int(current_price * 0.9)  # 10% 할인
        elif alert_type == 'discount':
            return int(current_price * 0.8)  # 20% 할인
        else:
            return int(current_price * 0.95)  # 5% 할인
    
    # 가격 이력 기반 계산
    min_price = min(price_history)
    avg_price = sum(price_history) / len(price_history)
    
    if alert_type == 'price_drop':
        # 최근 최저가 기준
        return int(min_price * 1.05)  # 최저가 + 5%
    elif alert_type == 'discount':
        # 평균가 기준
        return int(avg_price * 0.9)  # 평균가 - 10%
    else:
        # 현재가 기준
        return int(current_price * 0.95)  # 현재가 - 5%

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

@app.route('/api/auto-email', methods=['GET'])
def get_auto_email():
    """자동 이메일 감지 - 데이터베이스에서 가장 최근에 사용된 이메일 반환"""
    if not DATABASE_AVAILABLE:
        return jsonify({'error': '데이터베이스를 사용할 수 없습니다.'}), 500
    
    try:
        conn = get_db_connection()
        cursor = conn.execute('''
            SELECT DISTINCT user_email 
            FROM alerts 
            WHERE is_active = 1 
            ORDER BY id DESC 
            LIMIT 1
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return jsonify({
                'email': result[0],
                'found': True
            })
        else:
            return jsonify({
                'email': '',
                'found': False
            })
            
    except Exception as e:
        return jsonify({'error': f'이메일 감지 오류: {str(e)}'}), 500

# === 가격 추적 API 엔드포인트 추가 끝 ===

@app.route('/api/search/enhanced', methods=['GET'])
def search_products_enhanced():
    """향상된 상품 검색 API (페이지네이션 및 필터 지원)"""
    try:
        # 크롤러 모듈 import 확인
        try:
            from crawler import search_ssg_products
            CRAWLER_AVAILABLE = True
        except ImportError:
            CRAWLER_AVAILABLE = False
        
        if not CRAWLER_AVAILABLE:
            return jsonify({
                'error': '크롤러를 사용할 수 없습니다',
                'message': '크롤러 모듈 로드에 실패했습니다'
            }), 500
        
        # 파라미터 추출
        keyword = request.args.get('keyword', '').strip()
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        
        # 필터 파라미터
        min_price = request.args.get('min_price', type=int)
        max_price = request.args.get('max_price', type=int)
        brand = request.args.get('brand', '').strip()
        sort_by = request.args.get('sort_by', 'relevance')  # relevance, price_asc, price_desc, name
        
        # 키워드 유효성 검사
        if not keyword:
            return jsonify({
                'error': '검색어를 입력해주세요',
                'message': '사용 예시: /api/search/enhanced?keyword=아이폰&page=1&limit=20'
            }), 400
        
        if len(keyword) > 50:
            return jsonify({'error': '검색어는 50자 이내로 입력해주세요'}), 400
        
        if limit > 50:
            limit = 50  # 최대 50개로 제한
        
        if page < 1:
            page = 1
        
        # 검색 시작 시간 기록
        start_time = datetime.now()
        
        print(f"🔍 향상된 검색 요청: '{keyword}' (page: {page}, limit: {limit})")
        print(f"🔍 필터: min_price={min_price}, max_price={max_price}, brand={brand}, sort_by={sort_by}")
        
        # SSG 상품 검색 실행 (더 많은 결과를 가져와서 필터링)
        base_limit = limit * 3  # 필터링을 위해 더 많은 결과 가져오기
        products = search_ssg_products(keyword, page=page, limit=base_limit)
        
        # 필터링 적용
        filtered_products = []
        for product in products:
            price = product.get('price', 0) or product.get('current_price', 0)
            
            # 가격 필터
            if min_price is not None and price < min_price:
                continue
            if max_price is not None and price > max_price:
                continue
            
            # 브랜드 필터
            if brand and product.get('brand', '').lower() != brand.lower():
                continue
            
            filtered_products.append(product)
        
        # 정렬 적용
        if sort_by == 'price_asc':
            filtered_products.sort(key=lambda x: x.get('price', 0) or x.get('current_price', 0))
        elif sort_by == 'price_desc':
            filtered_products.sort(key=lambda x: x.get('price', 0) or x.get('current_price', 0), reverse=True)
        elif sort_by == 'name':
            filtered_products.sort(key=lambda x: x.get('name', ''))
        
        # 페이지네이션 적용
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_products = filtered_products[start_idx:end_idx]
        
        # 검색 완료 시간 계산
        end_time = datetime.now()
        search_duration = (end_time - start_time).total_seconds()
        
        print(f"✅ 향상된 검색 완료: {len(paginated_products)}개 상품 (전체: {len(filtered_products)}개), {search_duration:.2f}초")
        
        # 응답 데이터 구성
        response_data = {
            'products': paginated_products,
            'pagination': {
                'current_page': page,
                'total_pages': (len(filtered_products) + limit - 1) // limit,
                'total_results': len(filtered_products),
                'results_per_page': limit,
                'has_next': len(filtered_products) > end_idx,
                'has_prev': page > 1
            },
            'filters': {
                'applied': {
                    'min_price': min_price,
                    'max_price': max_price,
                    'brand': brand,
                    'sort_by': sort_by
                },
                'available_brands': list(set([p.get('brand', '') for p in filtered_products if p.get('brand')])),
                'price_range': {
                    'min': min([p.get('price', 0) or p.get('current_price', 0) for p in filtered_products]) if filtered_products else 0,
                    'max': max([p.get('price', 0) or p.get('current_price', 0) for p in filtered_products]) if filtered_products else 0
                }
            },
            'search_info': {
                'keyword': keyword,
                'search_duration': round(search_duration, 3),
                'search_time': start_time.isoformat(),
                'source': 'SSG',
                'cache_used': search_duration < 0.1
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ 향상된 검색 오류: {e}")
        print(f"상세 오류: {error_trace}")
        
        return jsonify({
            'error': f'검색 중 오류가 발생했습니다: {str(e)}',
            'keyword': request.args.get('keyword', ''),
            'timestamp': datetime.now().isoformat(),
            'error_type': type(e).__name__
        }), 500

# === 향상된 검색 API 엔드포인트 추가 끝 ===

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')  # 프론트엔드와 연결