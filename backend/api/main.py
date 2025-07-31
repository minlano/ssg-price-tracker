# Flask API 메인 애플리케이션 (고도화 버전)
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_db, get_db_connection
from advanced_search import advanced_search_bp
from product_comparison import product_comparison_bp
from data_processing import data_processing_bp
from eleventh_street_api import EleventhStreetAPI
from config import config
import sqlite3
from datetime import datetime

# Flask 앱 생성
app = Flask(__name__)
CORS(app)

# 한글 인코딩 설정
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# Blueprint 등록
app.register_blueprint(advanced_search_bp)
app.register_blueprint(product_comparison_bp)
app.register_blueprint(data_processing_bp)

# 11번가 API 인스턴스
eleventh_api = EleventhStreetAPI()

# 데이터베이스 초기화
init_db()

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
        conn = get_db_connection()
        conn.execute('SELECT 1').fetchone()
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected',
            'version': '2.0.0'
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

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # 기존 앱과 포트 분리