# 데이터 처리 고급 API
from flask import Blueprint, request, jsonify
from typing import Dict, List, Optional
import sqlite3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db_connection
from datetime import datetime, timedelta
import json
import statistics
from collections import defaultdict

data_processing_bp = Blueprint('data_processing', __name__)

@data_processing_bp.route('/api/data/analytics', methods=['GET'])
def get_analytics_data():
    """종합 분석 데이터 제공"""
    try:
        period = request.args.get('period', '30')  # 30, 90, 365 days
        analysis_type = request.args.get('type', 'overview')  # overview, price, trend, category
        
        conn = get_db_connection()
        
        # 기간 설정
        days = int(period)
        since_date = datetime.now() - timedelta(days=days)
        
        analytics_data = {}
        
        if analysis_type in ['overview', 'price']:
            analytics_data['price_analytics'] = _get_price_analytics(conn, since_date)
        
        if analysis_type in ['overview', 'trend']:
            analytics_data['trend_analytics'] = _get_trend_analytics(conn, since_date)
        
        if analysis_type in ['overview', 'category']:
            analytics_data['category_analytics'] = _get_category_analytics(conn)
        
        if analysis_type == 'overview':
            analytics_data['general_stats'] = _get_general_stats(conn, since_date)
        
        conn.close()
        
        return jsonify({
            'period': f'{period}일',
            'analysis_type': analysis_type,
            'analytics': analytics_data,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'분석 데이터 조회 중 오류가 발생했습니다: {str(e)}'}), 500

@data_processing_bp.route('/api/data/export', methods=['POST'])
def export_data():
    """데이터 내보내기"""
    try:
        data = request.json
        export_type = data.get('type', 'products')  # products, price_logs, analytics
        format_type = data.get('format', 'json')  # json, csv
        filters = data.get('filters', {})
        
        conn = get_db_connection()
        
        if export_type == 'products':
            exported_data = _export_products_data(conn, filters)
        elif export_type == 'price_logs':
            exported_data = _export_price_logs_data(conn, filters)
        elif export_type == 'analytics':
            exported_data = _export_analytics_data(conn, filters)
        else:
            return jsonify({'error': '지원하지 않는 내보내기 타입입니다'}), 400
        
        conn.close()
        
        # 포맷 변환
        if format_type == 'csv':
            csv_data = _convert_to_csv(exported_data, export_type)
            return jsonify({
                'data': csv_data,
                'format': 'csv',
                'filename': f'{export_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            })
        else:
            return jsonify({
                'data': exported_data,
                'format': 'json',
                'filename': f'{export_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
                'total_records': len(exported_data)
            })
        
    except Exception as e:
        return jsonify({'error': f'데이터 내보내기 중 오류가 발생했습니다: {str(e)}'}), 500

@data_processing_bp.route('/api/data/import', methods=['POST'])
def import_data():
    """데이터 가져오기"""
    try:
        data = request.json
        import_type = data.get('type', 'products')
        import_data = data.get('data', [])
        
        if not import_data:
            return jsonify({'error': '가져올 데이터가 없습니다'}), 400
        
        conn = get_db_connection()
        
        if import_type == 'products':
            result = _import_products_data(conn, import_data)
        elif import_type == 'price_logs':
            result = _import_price_logs_data(conn, import_data)
        else:
            return jsonify({'error': '지원하지 않는 가져오기 타입입니다'}), 400
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': '데이터 가져오기가 완료되었습니다',
            'import_type': import_type,
            'total_imported': result['imported'],
            'total_skipped': result['skipped'],
            'errors': result['errors']
        })
        
    except Exception as e:
        return jsonify({'error': f'데이터 가져오기 중 오류가 발생했습니다: {str(e)}'}), 500

@data_processing_bp.route('/api/data/cleanup', methods=['POST'])
def cleanup_data():
    """데이터 정리 및 최적화"""
    try:
        data = request.json
        cleanup_type = data.get('type', 'all')  # all, duplicates, old_logs, invalid
        
        conn = get_db_connection()
        cleanup_results = {}
        
        if cleanup_type in ['all', 'duplicates']:
            cleanup_results['duplicates'] = _remove_duplicate_products(conn)
        
        if cleanup_type in ['all', 'old_logs']:
            days_to_keep = data.get('days_to_keep', 365)
            cleanup_results['old_logs'] = _remove_old_price_logs(conn, days_to_keep)
        
        if cleanup_type in ['all', 'invalid']:
            cleanup_results['invalid'] = _remove_invalid_data(conn)
        
        # 데이터베이스 최적화
        conn.execute('VACUUM')
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': '데이터 정리가 완료되었습니다',
            'cleanup_results': cleanup_results,
            'completed_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'데이터 정리 중 오류가 발생했습니다: {str(e)}'}), 500

@data_processing_bp.route('/api/data/batch-update', methods=['POST'])
def batch_update_products():
    """상품 정보 일괄 업데이트"""
    try:
        data = request.json
        update_type = data.get('type', 'prices')  # prices, info, all
        product_ids = data.get('product_ids', [])
        
        if not product_ids:
            return jsonify({'error': '업데이트할 상품 ID가 필요합니다'}), 400
        
        conn = get_db_connection()
        update_results = {
            'updated': 0,
            'failed': 0,
            'errors': []
        }
        
        for product_id in product_ids:
            try:
                if update_type in ['prices', 'all']:
                    # 가격 업데이트 (크롤링 시뮬레이션)
                    success = _update_product_price(conn, product_id)
                    if success:
                        update_results['updated'] += 1
                    else:
                        update_results['failed'] += 1
                
                if update_type in ['info', 'all']:
                    # 상품 정보 업데이트
                    success = _update_product_info(conn, product_id)
                    if not success:
                        update_results['failed'] += 1
                        
            except Exception as e:
                update_results['failed'] += 1
                update_results['errors'].append(f'상품 {product_id}: {str(e)}')
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': '일괄 업데이트가 완료되었습니다',
            'results': update_results,
            'total_processed': len(product_ids)
        })
        
    except Exception as e:
        return jsonify({'error': f'일괄 업데이트 중 오류가 발생했습니다: {str(e)}'}), 500

@data_processing_bp.route('/api/data/statistics', methods=['GET'])
def get_data_statistics():
    """데이터 통계 정보"""
    try:
        conn = get_db_connection()
        
        # 기본 통계
        stats = {}
        
        # 상품 통계
        product_stats = conn.execute('''
            SELECT 
                COUNT(*) as total_products,
                COUNT(DISTINCT source) as total_sources,
                COUNT(DISTINCT brand) as total_brands,
                AVG(current_price) as avg_price,
                MIN(current_price) as min_price,
                MAX(current_price) as max_price
            FROM products
            WHERE current_price > 0
        ''').fetchone()
        
        stats['products'] = dict(product_stats) if product_stats else {}
        
        # 가격 로그 통계
        price_log_stats = conn.execute('''
            SELECT 
                COUNT(*) as total_logs,
                COUNT(DISTINCT product_id) as products_with_logs,
                MIN(logged_at) as oldest_log,
                MAX(logged_at) as newest_log
            FROM price_logs
        ''').fetchone()
        
        stats['price_logs'] = dict(price_log_stats) if price_log_stats else {}
        
        # 알림 통계
        alert_stats = conn.execute('''
            SELECT 
                COUNT(*) as total_alerts,
                COUNT(CASE WHEN is_active = 1 THEN 1 END) as active_alerts,
                COUNT(DISTINCT user_email) as unique_users
            FROM alerts
        ''').fetchone()
        
        stats['alerts'] = dict(alert_stats) if alert_stats else {}
        
        # 소스별 상품 분포
        source_distribution = conn.execute('''
            SELECT source, COUNT(*) as count
            FROM products
            GROUP BY source
            ORDER BY count DESC
        ''').fetchall()
        
        stats['source_distribution'] = [dict(row) for row in source_distribution]
        
        # 카테고리별 분포 (브랜드를 카테고리로 사용)
        brand_distribution = conn.execute('''
            SELECT brand, COUNT(*) as count
            FROM products
            WHERE brand IS NOT NULL AND brand != ''
            GROUP BY brand
            ORDER BY count DESC
            LIMIT 10
        ''').fetchall()
        
        stats['top_brands'] = [dict(row) for row in brand_distribution]
        
        conn.close()
        
        return jsonify({
            'statistics': stats,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'통계 조회 중 오류가 발생했습니다: {str(e)}'}), 500

def _get_price_analytics(conn, since_date):
    """가격 분석 데이터"""
    # 가격 변동 추이
    price_trends = conn.execute('''
        SELECT 
            DATE(logged_at) as date,
            AVG(price) as avg_price,
            MIN(price) as min_price,
            MAX(price) as max_price,
            COUNT(*) as log_count
        FROM price_logs
        WHERE logged_at >= ?
        GROUP BY DATE(logged_at)
        ORDER BY date
    ''', (since_date.isoformat(),)).fetchall()
    
    # 가격 변동률이 큰 상품들
    volatile_products = conn.execute('''
        SELECT 
            p.id, p.name, p.current_price,
            MIN(pl.price) as min_price,
            MAX(pl.price) as max_price,
            (MAX(pl.price) - MIN(pl.price)) * 100.0 / MIN(pl.price) as volatility
        FROM products p
        JOIN price_logs pl ON p.id = pl.product_id
        WHERE pl.logged_at >= ?
        GROUP BY p.id, p.name, p.current_price
        HAVING COUNT(pl.id) > 5
        ORDER BY volatility DESC
        LIMIT 10
    ''', (since_date.isoformat(),)).fetchall()
    
    return {
        'price_trends': [dict(row) for row in price_trends],
        'volatile_products': [dict(row) for row in volatile_products]
    }

def _get_trend_analytics(conn, since_date):
    """트렌드 분석 데이터"""
    # 일별 상품 추가 추이
    daily_additions = conn.execute('''
        SELECT 
            DATE(created_at) as date,
            COUNT(*) as products_added
        FROM products
        WHERE created_at >= ?
        GROUP BY DATE(created_at)
        ORDER BY date
    ''', (since_date.isoformat(),)).fetchall()
    
    # 인기 검색 키워드 (상품명에서 추출)
    popular_keywords = conn.execute('''
        SELECT 
            LOWER(TRIM(word)) as keyword,
            COUNT(*) as frequency
        FROM (
            SELECT 
                CASE 
                    WHEN INSTR(name, ' ') > 0 THEN SUBSTR(name, 1, INSTR(name, ' ') - 1)
                    ELSE name
                END as word
            FROM products
            WHERE created_at >= ?
        )
        WHERE LENGTH(keyword) > 2
        GROUP BY keyword
        ORDER BY frequency DESC
        LIMIT 20
    ''', (since_date.isoformat(),)).fetchall()
    
    return {
        'daily_additions': [dict(row) for row in daily_additions],
        'popular_keywords': [dict(row) for row in popular_keywords]
    }

def _get_category_analytics(conn):
    """카테고리 분석 데이터"""
    # 브랜드별 통계
    brand_stats = conn.execute('''
        SELECT 
            brand,
            COUNT(*) as product_count,
            AVG(current_price) as avg_price,
            MIN(current_price) as min_price,
            MAX(current_price) as max_price
        FROM products
        WHERE brand IS NOT NULL AND brand != '' AND current_price > 0
        GROUP BY brand
        HAVING product_count > 1
        ORDER BY product_count DESC
        LIMIT 15
    ''').fetchall()
    
    # 소스별 통계
    source_stats = conn.execute('''
        SELECT 
            source,
            COUNT(*) as product_count,
            AVG(current_price) as avg_price
        FROM products
        WHERE current_price > 0
        GROUP BY source
        ORDER BY product_count DESC
    ''').fetchall()
    
    return {
        'brand_stats': [dict(row) for row in brand_stats],
        'source_stats': [dict(row) for row in source_stats]
    }

def _get_general_stats(conn, since_date):
    """일반 통계"""
    # 최근 활동 통계
    recent_stats = conn.execute('''
        SELECT 
            (SELECT COUNT(*) FROM products WHERE created_at >= ?) as new_products,
            (SELECT COUNT(*) FROM price_logs WHERE logged_at >= ?) as price_updates,
            (SELECT COUNT(*) FROM alerts WHERE is_active = 1) as active_alerts
    ''', (since_date.isoformat(), since_date.isoformat())).fetchone()
    
    return dict(recent_stats) if recent_stats else {}

def _export_products_data(conn, filters):
    """상품 데이터 내보내기"""
    query = 'SELECT * FROM products WHERE 1=1'
    params = []
    
    if filters.get('source'):
        query += ' AND source = ?'
        params.append(filters['source'])
    
    if filters.get('min_price'):
        query += ' AND current_price >= ?'
        params.append(filters['min_price'])
    
    if filters.get('max_price'):
        query += ' AND current_price <= ?'
        params.append(filters['max_price'])
    
    query += ' ORDER BY created_at DESC'
    
    if filters.get('limit'):
        query += ' LIMIT ?'
        params.append(filters['limit'])
    
    products = conn.execute(query, params).fetchall()
    return [dict(product) for product in products]

def _export_price_logs_data(conn, filters):
    """가격 로그 데이터 내보내기"""
    query = '''
        SELECT pl.*, p.name as product_name, p.url as product_url
        FROM price_logs pl
        JOIN products p ON pl.product_id = p.id
        WHERE 1=1
    '''
    params = []
    
    if filters.get('product_id'):
        query += ' AND pl.product_id = ?'
        params.append(filters['product_id'])
    
    if filters.get('since_date'):
        query += ' AND pl.logged_at >= ?'
        params.append(filters['since_date'])
    
    query += ' ORDER BY pl.logged_at DESC'
    
    if filters.get('limit'):
        query += ' LIMIT ?'
        params.append(filters['limit'])
    
    logs = conn.execute(query, params).fetchall()
    return [dict(log) for log in logs]

def _export_analytics_data(conn, filters):
    """분석 데이터 내보내기"""
    since_date = datetime.now() - timedelta(days=filters.get('days', 30))
    
    return {
        'price_analytics': _get_price_analytics(conn, since_date),
        'trend_analytics': _get_trend_analytics(conn, since_date),
        'category_analytics': _get_category_analytics(conn),
        'general_stats': _get_general_stats(conn, since_date)
    }

def _convert_to_csv(data, export_type):
    """JSON 데이터를 CSV 형식으로 변환"""
    if not data:
        return ""
    
    import csv
    import io
    
    output = io.StringIO()
    
    if export_type == 'products':
        fieldnames = ['id', 'name', 'url', 'current_price', 'brand', 'source', 'created_at']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for item in data:
            row = {field: item.get(field, '') for field in fieldnames}
            writer.writerow(row)
    
    elif export_type == 'price_logs':
        fieldnames = ['id', 'product_id', 'product_name', 'price', 'logged_at']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for item in data:
            row = {field: item.get(field, '') for field in fieldnames}
            writer.writerow(row)
    
    return output.getvalue()

def _import_products_data(conn, import_data):
    """상품 데이터 가져오기"""
    imported = 0
    skipped = 0
    errors = []
    
    for product_data in import_data:
        try:
            # 중복 체크
            existing = conn.execute(
                'SELECT id FROM products WHERE url = ?',
                (product_data.get('url', ''),)
            ).fetchone()
            
            if existing:
                skipped += 1
                continue
            
            # 상품 추가
            conn.execute('''
                INSERT INTO products (name, url, current_price, brand, source, image_url)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                product_data.get('name', ''),
                product_data.get('url', ''),
                product_data.get('current_price', 0),
                product_data.get('brand', ''),
                product_data.get('source', 'imported'),
                product_data.get('image_url', '')
            ))
            
            imported += 1
            
        except Exception as e:
            errors.append(f"상품 '{product_data.get('name', 'Unknown')}': {str(e)}")
    
    return {'imported': imported, 'skipped': skipped, 'errors': errors}

def _import_price_logs_data(conn, import_data):
    """가격 로그 데이터 가져오기"""
    imported = 0
    skipped = 0
    errors = []
    
    for log_data in import_data:
        try:
            # 상품 존재 확인
            product_exists = conn.execute(
                'SELECT id FROM products WHERE id = ?',
                (log_data.get('product_id', 0),)
            ).fetchone()
            
            if not product_exists:
                errors.append(f"상품 ID {log_data.get('product_id')}가 존재하지 않습니다")
                continue
            
            # 가격 로그 추가
            conn.execute('''
                INSERT INTO price_logs (product_id, price, logged_at)
                VALUES (?, ?, ?)
            ''', (
                log_data.get('product_id'),
                log_data.get('price', 0),
                log_data.get('logged_at', datetime.now().isoformat())
            ))
            
            imported += 1
            
        except Exception as e:
            errors.append(f"가격 로그: {str(e)}")
    
    return {'imported': imported, 'skipped': skipped, 'errors': errors}

def _remove_duplicate_products(conn):
    """중복 상품 제거"""
    # URL 기준으로 중복 찾기
    duplicates = conn.execute('''
        SELECT url, COUNT(*) as count, MIN(id) as keep_id
        FROM products
        GROUP BY url
        HAVING count > 1
    ''').fetchall()
    
    removed_count = 0
    
    for duplicate in duplicates:
        # 가장 오래된 것을 제외하고 삭제
        conn.execute('''
            DELETE FROM products 
            WHERE url = ? AND id != ?
        ''', (duplicate['url'], duplicate['keep_id']))
        
        removed_count += duplicate['count'] - 1
    
    return {'removed_duplicates': removed_count}

def _remove_old_price_logs(conn, days_to_keep):
    """오래된 가격 로그 제거"""
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    
    result = conn.execute('''
        DELETE FROM price_logs 
        WHERE logged_at < ?
    ''', (cutoff_date.isoformat(),))
    
    return {'removed_old_logs': result.rowcount}

def _remove_invalid_data(conn):
    """유효하지 않은 데이터 제거"""
    # 가격이 0이거나 음수인 상품
    invalid_price = conn.execute('''
        DELETE FROM products 
        WHERE current_price <= 0
    ''')
    
    # URL이 없는 상품
    no_url = conn.execute('''
        DELETE FROM products 
        WHERE url IS NULL OR url = ''
    ''')
    
    # 존재하지 않는 상품의 가격 로그
    orphaned_logs = conn.execute('''
        DELETE FROM price_logs 
        WHERE product_id NOT IN (SELECT id FROM products)
    ''')
    
    # 존재하지 않는 상품의 알림
    orphaned_alerts = conn.execute('''
        DELETE FROM alerts 
        WHERE product_id NOT IN (SELECT id FROM products)
    ''')
    
    return {
        'removed_invalid_price': invalid_price.rowcount,
        'removed_no_url': no_url.rowcount,
        'removed_orphaned_logs': orphaned_logs.rowcount,
        'removed_orphaned_alerts': orphaned_alerts.rowcount
    }

def _update_product_price(conn, product_id):
    """상품 가격 업데이트 (시뮬레이션)"""
    try:
        # 현재 가격 조회
        current = conn.execute(
            'SELECT current_price FROM products WHERE id = ?',
            (product_id,)
        ).fetchone()
        
        if not current:
            return False
        
        # 가격 변동 시뮬레이션 (±10% 범위)
        import random
        current_price = current['current_price']
        change_percent = random.uniform(-0.1, 0.1)
        new_price = int(current_price * (1 + change_percent))
        
        # 상품 가격 업데이트
        conn.execute('''
            UPDATE products 
            SET current_price = ? 
            WHERE id = ?
        ''', (new_price, product_id))
        
        # 가격 로그 추가
        conn.execute('''
            INSERT INTO price_logs (product_id, price)
            VALUES (?, ?)
        ''', (product_id, new_price))
        
        return True
        
    except Exception:
        return False

def _update_product_info(conn, product_id):
    """상품 정보 업데이트 (시뮬레이션)"""
    try:
        # 간단한 정보 업데이트 시뮬레이션
        conn.execute('''
            UPDATE products 
            SET created_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (product_id,))
        
        return True
        
    except Exception:
        return False