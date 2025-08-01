# 상품 비교 분석 API
from flask import Blueprint, request, jsonify
from typing import Dict, List, Optional
from eleventh_street_api import EleventhStreetAPI
import sqlite3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db_connection
from datetime import datetime, timedelta
import statistics

product_comparison_bp = Blueprint('product_comparison', __name__)
eleventh_api = EleventhStreetAPI()

@product_comparison_bp.route('/api/compare/products', methods=['POST'])
def compare_products():
    """
    여러 상품 상세 비교 API
    - 최대 5개 상품까지 비교 가능
    - 가격, 평점, 리뷰, 스펙 등 종합 비교
    """
    try:
        data = request.json
        product_ids = data.get('product_ids', [])
        
        if not product_ids:
            return jsonify({'error': '비교할 상품을 선택해주세요'}), 400
        
        if len(product_ids) > 5:
            return jsonify({'error': '최대 5개 상품까지 비교 가능합니다'}), 400
        
        # 각 상품의 상세 정보 조회
        products = []
        for product_id in product_ids:
            if product_id.startswith('11st_'):
                # 11번가 상품
                product = eleventh_api.get_product_detail(product_id)
                if 'error' not in product:
                    products.append(product)
            else:
                # 데이터베이스에서 조회 (SSG 등)
                product = _get_product_from_db(product_id)
                if product:
                    products.append(product)
        
        if not products:
            return jsonify({'error': '비교할 수 있는 상품이 없습니다'}), 400
        
        # 비교 분석 수행
        comparison_result = _analyze_product_comparison(products)
        
        return jsonify({
            'products': products,
            'comparison': comparison_result,
            'total_products': len(products),
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'상품 비교 중 오류가 발생했습니다: {str(e)}'}), 500

@product_comparison_bp.route('/api/compare/similar', methods=['GET'])
def find_similar_products():
    """유사 상품 찾기 및 비교"""
    try:
        product_id = request.args.get('product_id')
        limit = request.args.get('limit', 5, type=int)
        
        if not product_id:
            return jsonify({'error': '기준 상품 ID가 필요합니다'}), 400
        
        # 기준 상품 정보 조회
        base_product = None
        if product_id.startswith('11st_'):
            base_product = eleventh_api.get_product_detail(product_id)
        else:
            base_product = _get_product_from_db(product_id)
        
        if not base_product:
            return jsonify({'error': '기준 상품을 찾을 수 없습니다'}), 400
        
        # 유사 상품 검색
        similar_products = _find_similar_products(base_product, limit)
        
        # 비교 분석
        all_products = [base_product] + similar_products
        comparison_result = _analyze_product_comparison(all_products)
        
        return jsonify({
            'base_product': base_product,
            'similar_products': similar_products,
            'comparison': comparison_result,
            'total_found': len(similar_products)
        })
        
    except Exception as e:
        return jsonify({'error': f'유사 상품 검색 중 오류가 발생했습니다: {str(e)}'}), 500

@product_comparison_bp.route('/api/compare/price-history', methods=['GET'])
def compare_price_history():
    """여러 상품의 가격 변동 이력 비교"""
    try:
        product_ids = request.args.getlist('product_ids')
        days = request.args.get('days', 30, type=int)
        
        if not product_ids:
            return jsonify({'error': '비교할 상품 ID가 필요합니다'}), 400
        
        price_histories = {}
        
        for product_id in product_ids:
            # 데이터베이스에서 가격 이력 조회
            conn = get_db_connection()
            
            # 상품 정보 조회
            product = conn.execute('''
                SELECT id, name, current_price, source 
                FROM products 
                WHERE id = ?
            ''', (product_id,)).fetchone()
            
            if product:
                # 가격 이력 조회
                since_date = datetime.now() - timedelta(days=days)
                price_logs = conn.execute('''
                    SELECT price, logged_at 
                    FROM price_logs 
                    WHERE product_id = ? AND logged_at >= ?
                    ORDER BY logged_at
                ''', (product_id, since_date.isoformat())).fetchall()
                
                price_histories[product_id] = {
                    'product_info': dict(product),
                    'price_history': [dict(log) for log in price_logs],
                    'price_stats': _calculate_price_stats([log['price'] for log in price_logs])
                }
            
            conn.close()
        
        # 전체 비교 통계
        overall_stats = _calculate_overall_price_comparison(price_histories)
        
        return jsonify({
            'price_histories': price_histories,
            'comparison_period': f'{days}일',
            'overall_stats': overall_stats,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'가격 이력 비교 중 오류가 발생했습니다: {str(e)}'}), 500

@product_comparison_bp.route('/api/compare/best-deal', methods=['GET'])
def find_best_deal():
    """최적 상품 추천 (가성비 분석)"""
    try:
        keyword = request.args.get('keyword')
        max_price = request.args.get('max_price', type=int)
        min_rating = request.args.get('min_rating', 3.0, type=float)
        limit = request.args.get('limit', 10, type=int)
        
        if not keyword:
            return jsonify({'error': '검색 키워드가 필요합니다'}), 400
        
        # 11번가에서 상품 검색
        search_results = eleventh_api.search_products(
            keyword=keyword,
            limit=limit * 2,  # 더 많은 결과에서 필터링
            max_price=max_price
        )
        
        products = search_results.get('products', [])
        
        # 필터링 및 가성비 점수 계산
        filtered_products = []
        for product in products:
            if product.get('rating', 0) >= min_rating:
                # 가성비 점수 계산
                value_score = _calculate_value_score(product)
                product['value_score'] = value_score
                filtered_products.append(product)
        
        # 가성비 점수로 정렬
        best_deals = sorted(filtered_products, key=lambda x: x['value_score'], reverse=True)[:limit]
        
        # 추천 이유 생성
        for product in best_deals:
            product['recommendation_reason'] = _generate_recommendation_reason(product)
        
        return jsonify({
            'keyword': keyword,
            'filters': {
                'max_price': max_price,
                'min_rating': min_rating
            },
            'best_deals': best_deals,
            'total_analyzed': len(filtered_products),
            'analysis_criteria': {
                'price_weight': 0.4,
                'rating_weight': 0.3,
                'review_weight': 0.2,
                'discount_weight': 0.1
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'최적 상품 분석 중 오류가 발생했습니다: {str(e)}'}), 500

@product_comparison_bp.route('/api/compare/category-analysis', methods=['GET'])
def analyze_category():
    """카테고리별 상품 분석"""
    try:
        category = request.args.get('category')
        analysis_type = request.args.get('type', 'overview')  # overview, price, rating, brand
        
        if not category:
            return jsonify({'error': '분석할 카테고리가 필요합니다'}), 400
        
        # 카테고리 상품 검색
        search_results = eleventh_api.search_products(
            keyword=category,
            limit=100,
            category=category
        )
        
        products = search_results.get('products', [])
        
        if not products:
            return jsonify({'error': '해당 카테고리의 상품을 찾을 수 없습니다'}), 400
        
        # 분석 타입별 처리
        analysis_result = {}
        
        if analysis_type in ['overview', 'price']:
            analysis_result['price_analysis'] = _analyze_category_prices(products)
        
        if analysis_type in ['overview', 'rating']:
            analysis_result['rating_analysis'] = _analyze_category_ratings(products)
        
        if analysis_type in ['overview', 'brand']:
            analysis_result['brand_analysis'] = _analyze_category_brands(products)
        
        if analysis_type == 'overview':
            analysis_result['general_stats'] = _analyze_category_general(products)
        
        return jsonify({
            'category': category,
            'analysis_type': analysis_type,
            'total_products': len(products),
            'analysis': analysis_result,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'카테고리 분석 중 오류가 발생했습니다: {str(e)}'}), 500

def _get_product_from_db(product_id: str) -> Optional[Dict]:
    """데이터베이스에서 상품 정보 조회"""
    try:
        conn = get_db_connection()
        product = conn.execute('''
            SELECT * FROM products WHERE id = ?
        ''', (product_id,)).fetchone()
        conn.close()
        
        if product:
            return dict(product)
        return None
    except:
        return None

def _find_similar_products(base_product: Dict, limit: int) -> List[Dict]:
    """유사 상품 찾기"""
    # 기준 상품의 키워드 추출
    keywords = base_product.get('name', '').split()[:3]  # 상품명에서 주요 키워드 추출
    
    similar_products = []
    
    for keyword in keywords:
        if len(keyword) > 1:  # 한 글자 키워드 제외
            search_results = eleventh_api.search_products(
                keyword=keyword,
                limit=limit,
                category=base_product.get('category')
            )
            
            for product in search_results.get('products', []):
                if product['id'] != base_product['id']:
                    # 유사도 점수 계산
                    similarity_score = _calculate_similarity_score(base_product, product)
                    product['similarity_score'] = similarity_score
                    similar_products.append(product)
    
    # 유사도 점수로 정렬하고 중복 제거
    unique_products = {}
    for product in similar_products:
        if product['id'] not in unique_products:
            unique_products[product['id']] = product
    
    sorted_products = sorted(unique_products.values(), 
                           key=lambda x: x['similarity_score'], reverse=True)
    
    return sorted_products[:limit]

def _analyze_product_comparison(products: List[Dict]) -> Dict:
    """상품 비교 분석"""
    if not products:
        return {}
    
    # 가격 비교
    prices = [p.get('price', 0) for p in products if p.get('price', 0) > 0]
    price_comparison = {
        'lowest': min(prices) if prices else 0,
        'highest': max(prices) if prices else 0,
        'average': int(sum(prices) / len(prices)) if prices else 0,
        'price_difference': max(prices) - min(prices) if prices else 0
    }
    
    # 평점 비교
    ratings = [p.get('rating', 0) for p in products if p.get('rating', 0) > 0]
    rating_comparison = {
        'highest': max(ratings) if ratings else 0,
        'lowest': min(ratings) if ratings else 0,
        'average': round(sum(ratings) / len(ratings), 1) if ratings else 0
    }
    
    # 리뷰 수 비교
    reviews = [p.get('review_count', 0) for p in products]
    review_comparison = {
        'most_reviewed': max(reviews) if reviews else 0,
        'least_reviewed': min(reviews) if reviews else 0,
        'total_reviews': sum(reviews)
    }
    
    # 최고/최저 상품 식별
    best_price_product = min(products, key=lambda x: x.get('price', float('inf')))
    best_rating_product = max(products, key=lambda x: x.get('rating', 0))
    most_reviewed_product = max(products, key=lambda x: x.get('review_count', 0))
    
    return {
        'price_comparison': price_comparison,
        'rating_comparison': rating_comparison,
        'review_comparison': review_comparison,
        'recommendations': {
            'best_price': {
                'product_id': best_price_product.get('id'),
                'product_name': best_price_product.get('name'),
                'price': best_price_product.get('price')
            },
            'best_rating': {
                'product_id': best_rating_product.get('id'),
                'product_name': best_rating_product.get('name'),
                'rating': best_rating_product.get('rating')
            },
            'most_reviewed': {
                'product_id': most_reviewed_product.get('id'),
                'product_name': most_reviewed_product.get('name'),
                'review_count': most_reviewed_product.get('review_count')
            }
        }
    }

def _calculate_value_score(product: Dict) -> float:
    """가성비 점수 계산"""
    price = product.get('price', 0)
    rating = product.get('rating', 0)
    review_count = product.get('review_count', 0)
    discount_rate = product.get('discount_rate', 0)
    
    if price == 0:
        return 0
    
    # 정규화된 점수 계산
    price_score = max(0, 100 - (price / 10000))  # 가격이 낮을수록 높은 점수
    rating_score = rating * 20  # 5점 만점을 100점으로 변환
    review_score = min(100, review_count / 10)  # 리뷰 수 (최대 100점)
    discount_score = discount_rate  # 할인율 그대로 사용
    
    # 가중 평균 계산
    value_score = (
        price_score * 0.4 +
        rating_score * 0.3 +
        review_score * 0.2 +
        discount_score * 0.1
    )
    
    return round(value_score, 2)

def _generate_recommendation_reason(product: Dict) -> str:
    """추천 이유 생성"""
    reasons = []
    
    if product.get('discount_rate', 0) > 20:
        reasons.append(f"{product['discount_rate']}% 할인")
    
    if product.get('rating', 0) >= 4.5:
        reasons.append("높은 평점")
    
    if product.get('review_count', 0) > 100:
        reasons.append("많은 리뷰")
    
    if product.get('is_free_delivery'):
        reasons.append("무료배송")
    
    if not reasons:
        reasons.append("균형잡힌 가성비")
    
    return ", ".join(reasons)

def _calculate_similarity_score(product1: Dict, product2: Dict) -> float:
    """두 상품 간 유사도 점수 계산"""
    score = 0
    
    # 카테고리 유사도
    if product1.get('category') == product2.get('category'):
        score += 30
    
    # 브랜드 유사도
    if product1.get('brand') == product2.get('brand'):
        score += 20
    
    # 가격 유사도
    price1 = product1.get('price', 0)
    price2 = product2.get('price', 0)
    if price1 > 0 and price2 > 0:
        price_diff = abs(price1 - price2) / max(price1, price2)
        price_similarity = max(0, 1 - price_diff) * 30
        score += price_similarity
    
    # 이름 유사도 (간단한 키워드 매칭)
    name1_words = set(product1.get('name', '').lower().split())
    name2_words = set(product2.get('name', '').lower().split())
    common_words = name1_words.intersection(name2_words)
    if name1_words and name2_words:
        name_similarity = len(common_words) / len(name1_words.union(name2_words)) * 20
        score += name_similarity
    
    return round(score, 2)

def _calculate_price_stats(prices: List[int]) -> Dict:
    """가격 통계 계산"""
    if not prices:
        return {}
    
    return {
        'min': min(prices),
        'max': max(prices),
        'avg': int(sum(prices) / len(prices)),
        'median': int(statistics.median(prices)),
        'std_dev': int(statistics.stdev(prices)) if len(prices) > 1 else 0
    }

def _calculate_overall_price_comparison(price_histories: Dict) -> Dict:
    """전체 가격 비교 통계"""
    all_current_prices = []
    price_changes = []
    
    for product_id, data in price_histories.items():
        current_price = data['product_info'].get('current_price', 0)
        if current_price > 0:
            all_current_prices.append(current_price)
        
        history = data['price_history']
        if len(history) > 1:
            first_price = history[0]['price']
            last_price = history[-1]['price']
            change_percent = ((last_price - first_price) / first_price) * 100
            price_changes.append(change_percent)
    
    stats = {}
    
    if all_current_prices:
        stats['current_price_stats'] = {
            'min': min(all_current_prices),
            'max': max(all_current_prices),
            'avg': int(sum(all_current_prices) / len(all_current_prices))
        }
    
    if price_changes:
        stats['price_change_stats'] = {
            'avg_change_percent': round(sum(price_changes) / len(price_changes), 2),
            'max_increase': round(max(price_changes), 2),
            'max_decrease': round(min(price_changes), 2)
        }
    
    return stats

def _analyze_category_prices(products: List[Dict]) -> Dict:
    """카테고리 가격 분석"""
    prices = [p.get('price', 0) for p in products if p.get('price', 0) > 0]
    
    if not prices:
        return {}
    
    return {
        'price_distribution': {
            'under_50k': len([p for p in prices if p < 50000]),
            '50k_to_100k': len([p for p in prices if 50000 <= p < 100000]),
            '100k_to_300k': len([p for p in prices if 100000 <= p < 300000]),
            'over_300k': len([p for p in prices if p >= 300000])
        },
        'price_stats': _calculate_price_stats(prices)
    }

def _analyze_category_ratings(products: List[Dict]) -> Dict:
    """카테고리 평점 분석"""
    ratings = [p.get('rating', 0) for p in products if p.get('rating', 0) > 0]
    
    if not ratings:
        return {}
    
    return {
        'rating_distribution': {
            '5_star': len([r for r in ratings if r >= 4.5]),
            '4_star': len([r for r in ratings if 3.5 <= r < 4.5]),
            '3_star': len([r for r in ratings if 2.5 <= r < 3.5]),
            'below_3': len([r for r in ratings if r < 2.5])
        },
        'avg_rating': round(sum(ratings) / len(ratings), 1),
        'highest_rated': max(ratings),
        'lowest_rated': min(ratings)
    }

def _analyze_category_brands(products: List[Dict]) -> Dict:
    """카테고리 브랜드 분석"""
    brands = {}
    
    for product in products:
        brand = product.get('brand', '기타')
        if brand not in brands:
            brands[brand] = 0
        brands[brand] += 1
    
    # 상위 브랜드 정렬
    top_brands = sorted(brands.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        'total_brands': len(brands),
        'top_brands': [{'brand': brand, 'count': count} for brand, count in top_brands],
        'brand_diversity': len(brands) / len(products) if products else 0
    }

def _analyze_category_general(products: List[Dict]) -> Dict:
    """카테고리 일반 통계"""
    total_reviews = sum(p.get('review_count', 0) for p in products)
    free_delivery_count = len([p for p in products if p.get('is_free_delivery')])
    discount_products = len([p for p in products if p.get('discount_rate', 0) > 0])
    
    return {
        'total_products': len(products),
        'total_reviews': total_reviews,
        'avg_reviews_per_product': int(total_reviews / len(products)) if products else 0,
        'free_delivery_ratio': round(free_delivery_count / len(products) * 100, 1) if products else 0,
        'discount_product_ratio': round(discount_products / len(products) * 100, 1) if products else 0
    }