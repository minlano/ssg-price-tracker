from flask import Flask, request, jsonify
from flask_cors import CORS
from database import init_db, get_db_connection
from models import Product, PriceLog, Alert
from crawler import crawl_ssg_product, search_ssg_products, compare_products
from notification import start_notification_scheduler
import sqlite3

app = Flask(__name__)
CORS(app)

# 데이터베이스 초기화
init_db()

# 알림 스케줄러 시작
start_notification_scheduler()

@app.route('/api/products', methods=['GET'])
def get_products():
    """상품 목록 조회"""
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products ORDER BY created_at DESC').fetchall()
    conn.close()
    
    return jsonify([dict(product) for product in products])

@app.route('/api/products', methods=['POST'])
def add_product():
    """상품 추가"""
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': '상품 URL이 필요합니다'}), 400
    
    # 상품 정보 크롤링
    product_info = crawl_ssg_product(url)
    if not product_info:
        return jsonify({'error': '상품 정보를 가져올 수 없습니다'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO products (name, url, current_price) VALUES (?, ?, ?)',
        (product_info['name'], url, product_info['price'])
    )
    product_id = cursor.lastrowid
    
    # 가격 이력 추가
    cursor.execute(
        'INSERT INTO price_logs (product_id, price) VALUES (?, ?)',
        (product_id, product_info['price'])
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({'id': product_id, 'message': '상품이 추가되었습니다'})

@app.route('/api/products/<int:product_id>/prices', methods=['GET'])
def get_price_history(product_id):
    """상품 가격 이력 조회"""
    conn = get_db_connection()
    prices = conn.execute(
        'SELECT price, logged_at FROM price_logs WHERE product_id = ? ORDER BY logged_at',
        (product_id,)
    ).fetchall()
    conn.close()
    
    return jsonify([dict(price) for price in prices])

@app.route('/api/alerts', methods=['POST'])
def create_alert():
    """알림 설정"""
    data = request.json
    
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO alerts (product_id, user_email, target_price) VALUES (?, ?, ?)',
        (data['product_id'], data['email'], data['target_price'])
    )
    conn.commit()
    conn.close()
    
    return jsonify({'message': '알림이 설정되었습니다'})

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
    """대시보드 데이터"""
    conn = get_db_connection()
    
    # 전체 상품 수
    total_products = conn.execute('SELECT COUNT(*) as count FROM products').fetchone()['count']
    
    # 활성 알림 수
    active_alerts = conn.execute('SELECT COUNT(*) as count FROM alerts WHERE is_active = 1').fetchone()['count']
    
    # 최근 가격 변동
    recent_changes = conn.execute('''
        SELECT p.name, pl.price, pl.logged_at
        FROM price_logs pl
        JOIN products p ON pl.product_id = p.id
        ORDER BY pl.logged_at DESC
        LIMIT 10
    ''').fetchall()
    
    conn.close()
    
    return jsonify({
        'total_products': total_products,
        'active_alerts': active_alerts,
        'recent_changes': [dict(change) for change in recent_changes]
    })

@app.route('/api/search', methods=['GET'])
def search_products():
    """상품 검색"""
    keyword = request.args.get('keyword', '')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    
    if not keyword:
        return jsonify({'error': '검색어가 필요합니다'}), 400
    
    try:
        products = search_ssg_products(keyword, page=page, limit=limit)
        return jsonify({
            'keyword': keyword,
            'page': page,
            'products': products,
            'total': len(products)
        })
    except Exception as e:
        return jsonify({'error': f'검색 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/api/compare', methods=['GET'])
def compare_product_prices():
    """상품 가격 비교"""
    keyword = request.args.get('keyword', '')
    limit = int(request.args.get('limit', 10))
    
    if not keyword:
        return jsonify({'error': '검색어가 필요합니다'}), 400
    
    try:
        products = compare_products(keyword, limit=limit)
        
        # 가격 통계 계산
        valid_prices = [p['price'] for p in products if p['price'] > 0]
        price_stats = {}
        
        if valid_prices:
            price_stats = {
                'min_price': min(valid_prices),
                'max_price': max(valid_prices),
                'avg_price': int(sum(valid_prices) / len(valid_prices)),
                'price_range': max(valid_prices) - min(valid_prices)
            }
        
        return jsonify({
            'keyword': keyword,
            'products': products,
            'total': len(products),
            'price_stats': price_stats
        })
    except Exception as e:
        return jsonify({'error': f'가격 비교 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/api/products/add-from-search', methods=['POST'])
def add_product_from_search():
    """검색 결과에서 상품 추가"""
    data = request.json
    
    required_fields = ['name', 'url', 'price']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field}가 필요합니다'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 중복 URL 체크
        existing = cursor.execute('SELECT id FROM products WHERE url = ?', (data['url'],)).fetchone()
        if existing:
            return jsonify({'error': '이미 등록된 상품입니다'}), 400
        
        # 상품 추가 (추가 정보 포함)
        cursor.execute(
            'INSERT INTO products (name, url, current_price, image_url, brand, source) VALUES (?, ?, ?, ?, ?, ?)',
            (
                data['name'], 
                data['url'], 
                data['price'],
                data.get('image_url'),
                data.get('brand', '브랜드 정보 없음'),
                data.get('source', 'SSG')
            )
        )
        product_id = cursor.lastrowid
        
        # 가격 이력 추가
        cursor.execute(
            'INSERT INTO price_logs (product_id, price) VALUES (?, ?)',
            (product_id, data['price'])
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'id': product_id,
            'message': '상품이 추가되었습니다',
            'product': {
                'id': product_id,
                'name': data['name'],
                'url': data['url'],
                'current_price': data['price'],
                'image_url': data.get('image_url'),
                'brand': data.get('brand'),
                'source': data.get('source', 'SSG')
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'상품 추가 중 오류가 발생했습니다: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)