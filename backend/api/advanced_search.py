# 고급 검색 필터 API
from flask import Blueprint, request, jsonify
from typing import Dict, List, Optional
from eleventh_street_api import EleventhStreetAPI
import sqlite3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db_connection

advanced_search_bp = Blueprint('advanced_search', __name__)
eleventh_api = EleventhStreetAPI()

@advanced_search_bp.route('/api/search/advanced', methods=['GET'])
def advanced_search():
    """
    고급 검색 API
    - 다중 필터 지원
    - 가격 범위, 카테고리, 브랜드, 평점 등 필터링
    - 정렬 옵션 제공
    """
    try:
        # 검색 파라미터 추출
        keyword = request.args.get('keyword', '').strip()
        category = request.args.get('category')
        min_price = request.args.get('min_price', type=int)
        max_price = request.args.get('max_price', type=int)
        min_rating = request.args.get('min_rating', type=float)
        brand = request.args.get('brand')
        sort_type = request.args.get('sort', 'popular')  # popular, price_low, price_high, rating, newest
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        source = request.args.get('source', 'all')  # all, 11st, ssg
        
        if not keyword:
            return jsonify({'error': '검색어를 입력해주세요'}), 400
        
        results = []
        
        # 11번가 검색
        if source in ['all', '11st']:
            eleventh_results = eleventh_api.search_products(
                keyword=keyword,
                page=page,
                limit=limit,
                category=category,
                min_price=min_price,
                max_price=max_price,
                sort_type=sort_type
            )
            
            if 'products' in eleventh_results:
                # 추가 필터링 적용
                filtered_products = _apply_advanced_filters(
                    eleventh_results['products'],
                    min_rating=min_rating,
                    brand=brand
                )
                results.extend(filtered_products)
        
        # SSG 검색 (기존 크롤러 사용)
        if source in ['all', 'ssg']:
            try:
                from backend.crawler import search_ssg_products
                ssg_results = search_ssg_products(keyword, page=page, limit=limit)
                
                # SSG 결과를 표준 형식으로 변환
                ssg_formatted = _format_ssg_results(ssg_results)
                
                # 추가 필터링 적용
                filtered_ssg = _apply_advanced_filters(
                    ssg_formatted,
                    min_price=min_price,
                    max_price=max_price,
                    min_rating=min_rating,
                    brand=brand
                )
                results.extend(filtered_ssg)
            except Exception as e:
                print(f"SSG 검색 오류: {e}")
        
        # 최종 정렬 및 페이징
        sorted_results = _sort_results(results, sort_type)
        
        # 통계 정보 계산
        stats = _calculate_search_stats(sorted_results)
        
        return jsonify({
            'keyword': keyword,
            'filters': {
                'category': category,
                'min_price': min_price,
                'max_price': max_price,
                'min_rating': min_rating,
                'brand': brand,
                'sort': sort_type,
                'source': source
            },
            'products': sorted_results,
            'total': len(sorted_results),
            'page': page,
            'limit': limit,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({'error': f'검색 중 오류가 발생했습니다: {str(e)}'}), 500

@advanced_search_bp.route('/api/search/filters', methods=['GET'])
def get_search_filters():
    """검색 필터 옵션 조회"""
    try:
        # 카테고리 목록
        categories = eleventh_api.get_category_list()
        
        # 데이터베이스에서 브랜드 목록 조회
        conn = get_db_connection()
        brands = conn.execute('''
            SELECT DISTINCT brand 
            FROM products 
            WHERE brand IS NOT NULL AND brand != '' 
            ORDER BY brand
        ''').fetchall()
        conn.close()
        
        brand_list = [brand['brand'] for brand in brands]
        
        # 가격 범위 옵션
        price_ranges = [
            {'label': '1만원 미만', 'min': 0, 'max': 10000},
            {'label': '1만원 ~ 5만원', 'min': 10000, 'max': 50000},
            {'label': '5만원 ~ 10만원', 'min': 50000, 'max': 100000},
            {'label': '10만원 ~ 30만원', 'min': 100000, 'max': 300000},
            {'label': '30만원 이상', 'min': 300000, 'max': None}
        ]
        
        # 정렬 옵션
        sort_options = [
            {'value': 'popular', 'label': '인기순'},
            {'value': 'price_low', 'label': '낮은 가격순'},
            {'value': 'price_high', 'label': '높은 가격순'},
            {'value': 'rating', 'label': '평점순'},
            {'value': 'newest', 'label': '최신순'},
            {'value': 'review', 'label': '리뷰 많은순'}
        ]
        
        return jsonify({
            'categories': categories,
            'brands': brand_list,
            'price_ranges': price_ranges,
            'sort_options': sort_options,
            'rating_options': [1, 2, 3, 4, 5]
        })
        
    except Exception as e:
        return jsonify({'error': f'필터 정보 조회 중 오류가 발생했습니다: {str(e)}'}), 500

@advanced_search_bp.route('/api/search/suggestions', methods=['GET'])
def get_search_suggestions():
    """검색어 자동완성"""
    try:
        query = request.args.get('q', '').strip()
        
        if len(query) < 2:
            return jsonify({'suggestions': []})
        
        # 데이터베이스에서 유사한 상품명 검색
        conn = get_db_connection()
        suggestions = conn.execute('''
            SELECT DISTINCT name 
            FROM products 
            WHERE name LIKE ? 
            ORDER BY name 
            LIMIT 10
        ''', (f'%{query}%',)).fetchall()
        conn.close()
        
        suggestion_list = [s['name'] for s in suggestions]
        
        # 인기 검색어 추가 (샘플)
        popular_keywords = [
            '스마트폰', '노트북', '이어폰', '키보드', '마우스',
            '운동화', '가방', '시계', '화장품', '의류'
        ]
        
        # 쿼리와 매치되는 인기 검색어 추가
        matching_popular = [k for k in popular_keywords if query.lower() in k.lower()]
        
        # 중복 제거하고 합치기
        all_suggestions = list(set(suggestion_list + matching_popular))[:10]
        
        return jsonify({
            'query': query,
            'suggestions': all_suggestions
        })
        
    except Exception as e:
        return jsonify({'error': f'자동완성 조회 중 오류가 발생했습니다: {str(e)}'}), 500

def _apply_advanced_filters(products: List[Dict], min_rating: float = None, 
                          brand: str = None, min_price: int = None, 
                          max_price: int = None) -> List[Dict]:
    """고급 필터 적용"""
    filtered = products
    
    if min_rating:
        filtered = [p for p in filtered if p.get('rating', 0) >= min_rating]
    
    if brand:
        filtered = [p for p in filtered if brand.lower() in p.get('brand', '').lower()]
    
    if min_price:
        filtered = [p for p in filtered if p.get('price', 0) >= min_price]
    
    if max_price:
        filtered = [p for p in filtered if p.get('price', 0) <= max_price]
    
    return filtered

def _format_ssg_results(ssg_results: List[Dict]) -> List[Dict]:
    """SSG 검색 결과를 표준 형식으로 변환"""
    formatted = []
    
    for product in ssg_results:
        formatted_product = {
            'id': f"ssg_{product.get('id', '')}",
            'name': product.get('name', ''),
            'price': product.get('price', 0),
            'original_price': product.get('original_price', product.get('price', 0)),
            'discount_rate': 0,
            'image_url': product.get('image_url', ''),
            'brand': product.get('brand', '브랜드 정보 없음'),
            'rating': product.get('rating', 0),
            'review_count': product.get('review_count', 0),
            'seller': product.get('seller', ''),
            'delivery_fee': 0,
            'is_free_delivery': True,
            'category': product.get('category', ''),
            'url': product.get('url', ''),
            'source': 'SSG'
        }
        formatted.append(formatted_product)
    
    return formatted

def _sort_results(products: List[Dict], sort_type: str) -> List[Dict]:
    """검색 결과 정렬"""
    if sort_type == 'price_low':
        return sorted(products, key=lambda x: x.get('price', 0))
    elif sort_type == 'price_high':
        return sorted(products, key=lambda x: x.get('price', 0), reverse=True)
    elif sort_type == 'rating':
        return sorted(products, key=lambda x: x.get('rating', 0), reverse=True)
    elif sort_type == 'review':
        return sorted(products, key=lambda x: x.get('review_count', 0), reverse=True)
    else:  # popular, newest
        return products

def _calculate_search_stats(products: List[Dict]) -> Dict:
    """검색 결과 통계 계산"""
    if not products:
        return {}
    
    prices = [p.get('price', 0) for p in products if p.get('price', 0) > 0]
    ratings = [p.get('rating', 0) for p in products if p.get('rating', 0) > 0]
    
    stats = {
        'total_products': len(products),
        'sources': {}
    }
    
    # 소스별 통계
    for product in products:
        source = product.get('source', 'Unknown')
        if source not in stats['sources']:
            stats['sources'][source] = 0
        stats['sources'][source] += 1
    
    # 가격 통계
    if prices:
        stats['price_stats'] = {
            'min': min(prices),
            'max': max(prices),
            'avg': int(sum(prices) / len(prices)),
            'median': sorted(prices)[len(prices) // 2]
        }
    
    # 평점 통계
    if ratings:
        stats['rating_stats'] = {
            'avg': round(sum(ratings) / len(ratings), 1),
            'max': max(ratings),
            'min': min(ratings)
        }
    
    return stats