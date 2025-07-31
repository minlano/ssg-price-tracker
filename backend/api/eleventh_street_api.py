# 11번가 API 연동 모듈
import requests
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
import time
from config import config

class EleventhStreetAPI:
    """11번가 API 연동 클래스"""
    
    def __init__(self, api_key: str = None):
        # API 키 설정 (우선순위: 매개변수 > 설정파일)
        self.api_key = api_key or config.ELEVENTH_STREET_API_KEY
        self.base_url = config.ELEVENTH_STREET_BASE_URL
        
        # API 키가 있으면 실제 API 사용, 없으면 샘플 데이터 사용
        self.use_real_api = bool(self.api_key)
        
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # API 키가 있으면 헤더에 추가
        if self.api_key:
            self.headers['Authorization'] = f'Bearer {self.api_key}'
            # 또는 11번가 API 스펙에 따라
            # self.headers['X-API-Key'] = self.api_key
            print(f"✅ 11번가 실제 API를 사용합니다. (키: {self.api_key[:10]}...)")
        else:
            print("⚠️ API 키가 없어 샘플 데이터를 사용합니다.")
        
    def search_products(self, keyword: str, page: int = 1, limit: int = 20, 
                       category: str = None, min_price: int = None, 
                       max_price: int = None, sort_type: str = 'popular') -> Dict:
        """
        11번가 상품 검색
        
        Args:
            keyword: 검색 키워드
            page: 페이지 번호
            limit: 페이지당 상품 수
            category: 카테고리 필터
            min_price: 최소 가격
            max_price: 최대 가격
            sort_type: 정렬 방식 (popular, price_low, price_high, newest, review)
        """
        try:
            if self.use_real_api:
                # 실제 11번가 API 호출
                return self._call_real_api_search(keyword, page, limit, category, min_price, max_price, sort_type)
            else:
                # 샘플 데이터 반환
                return self._get_sample_search_results(keyword, page, limit, min_price, max_price, sort_type)
            
        except Exception as e:
            print(f"11번가 API 검색 오류: {e}")
            return {'products': [], 'total': 0, 'error': str(e)}
    
    def get_product_detail(self, product_id: str) -> Dict:
        """상품 상세 정보 조회"""
        try:
            if self.use_real_api:
                # 실제 11번가 API 호출
                return self._call_real_api_product_detail(product_id)
            else:
                # 샘플 데이터 반환
                return self._get_sample_product_detail(product_id)
            
        except Exception as e:
            print(f"11번가 상품 상세 조회 오류: {e}")
            return {'error': str(e)}
    
    def get_category_list(self) -> List[Dict]:
        """카테고리 목록 조회"""
        return [
            {'id': 'fashion', 'name': '패션의류'},
            {'id': 'beauty', 'name': '뷰티'},
            {'id': 'digital', 'name': '디지털/가전'},
            {'id': 'sports', 'name': '스포츠/레저'},
            {'id': 'home', 'name': '홈/리빙'},
            {'id': 'food', 'name': '식품'},
            {'id': 'book', 'name': '도서'},
            {'id': 'baby', 'name': '출산/육아'},
            {'id': 'pet', 'name': '반려동물'},
            {'id': 'car', 'name': '자동차용품'}
        ]
    
    def compare_products(self, product_ids: List[str]) -> List[Dict]:
        """여러 상품 비교"""
        products = []
        for product_id in product_ids:
            product = self.get_product_detail(product_id)
            if 'error' not in product:
                products.append(product)
        return products
    
    def _get_sample_search_results(self, keyword: str, page: int, limit: int, 
                                 min_price: int = None, max_price: int = None, 
                                 sort_type: str = 'popular') -> Dict:
        """샘플 검색 결과 생성"""
        import random
        
        # 키워드별 샘플 상품 생성
        base_products = [
            {
                'id': f'11st_{i}_{keyword}',
                'name': f'{keyword} 상품 {i}',
                'price': random.randint(10000, 500000),
                'original_price': random.randint(15000, 600000),
                'discount_rate': random.randint(5, 50),
                'image_url': f'https://cdn.11st.co.kr/images/product_{i}.jpg',
                'brand': f'브랜드{i}',
                'rating': round(random.uniform(3.0, 5.0), 1),
                'review_count': random.randint(10, 1000),
                'seller': f'판매자{i}',
                'delivery_fee': random.choice([0, 2500, 3000]),
                'is_free_delivery': random.choice([True, False]),
                'category': random.choice(['패션의류', '뷰티', '디지털/가전', '홈/리빙']),
                'url': f'https://www.11st.co.kr/products/{i}',
                'source': '11번가'
            }
            for i in range(1, 101)
        ]
        
        # 가격 필터 적용
        filtered_products = base_products
        if min_price:
            filtered_products = [p for p in filtered_products if p['price'] >= min_price]
        if max_price:
            filtered_products = [p for p in filtered_products if p['price'] <= max_price]
        
        # 정렬 적용
        if sort_type == 'price_low':
            filtered_products.sort(key=lambda x: x['price'])
        elif sort_type == 'price_high':
            filtered_products.sort(key=lambda x: x['price'], reverse=True)
        elif sort_type == 'review':
            filtered_products.sort(key=lambda x: x['review_count'], reverse=True)
        elif sort_type == 'newest':
            random.shuffle(filtered_products)
        
        # 페이징 적용
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        page_products = filtered_products[start_idx:end_idx]
        
        return {
            'products': page_products,
            'total': len(filtered_products),
            'page': page,
            'limit': limit,
            'total_pages': (len(filtered_products) + limit - 1) // limit
        }
    
    def _get_sample_product_detail(self, product_id: str) -> Dict:
        """샘플 상품 상세 정보 생성"""
        import random
        
        return {
            'id': product_id,
            'name': f'상품 상세 {product_id}',
            'price': random.randint(50000, 300000),
            'original_price': random.randint(60000, 400000),
            'discount_rate': random.randint(10, 40),
            'description': f'{product_id} 상품의 상세 설명입니다.',
            'images': [
                f'https://cdn.11st.co.kr/images/{product_id}_1.jpg',
                f'https://cdn.11st.co.kr/images/{product_id}_2.jpg',
                f'https://cdn.11st.co.kr/images/{product_id}_3.jpg'
            ],
            'brand': f'브랜드_{product_id}',
            'rating': round(random.uniform(3.5, 5.0), 1),
            'review_count': random.randint(50, 2000),
            'seller': {
                'name': f'판매자_{product_id}',
                'rating': round(random.uniform(4.0, 5.0), 1),
                'business_type': random.choice(['개인', '사업자'])
            },
            'delivery': {
                'fee': random.choice([0, 2500, 3000]),
                'is_free': random.choice([True, False]),
                'estimated_days': random.randint(1, 5)
            },
            'specifications': {
                '제조사': f'제조사_{product_id}',
                '모델명': f'모델_{product_id}',
                '색상': random.choice(['블랙', '화이트', '실버', '골드']),
                '크기': random.choice(['S', 'M', 'L', 'XL'])
            },
            'category': random.choice(['패션의류', '뷰티', '디지털/가전', '홈/리빙']),
            'url': f'https://www.11st.co.kr/products/{product_id}',
            'source': '11번가',
            'last_updated': datetime.now().isoformat()
        }  
  
    def _call_real_api_search(self, keyword: str, page: int, limit: int, 
                             category: str = None, min_price: int = None, 
                             max_price: int = None, sort_type: str = 'popular') -> Dict:
        """실제 11번가 API 검색 호출"""
        try:
            # 11번가 API 엔드포인트
            endpoint = f"{self.base_url}/openapi/OpenApiService.tmall"
            
            # API 파라미터 설정
            params = {
                'key': self.api_key,
                'apiCode': 'ProductSearch',
                'keyword': keyword
            }
            
            # 선택적 파라미터 추가 (11번가 API 스펙에 맞게 조정)
            if category:
                params['categoryCode'] = category
            if min_price:
                params['minPrice'] = min_price
            if max_price:
                params['maxPrice'] = max_price
            
            # API 호출
            response = requests.get(endpoint, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # XML 응답 파싱
            return self._parse_xml_search_response(response.text, page, limit)
            
        except requests.exceptions.RequestException as e:
            print(f"11번가 API 호출 오류: {e}")
            # API 호출 실패 시 샘플 데이터로 대체
            return self._get_sample_search_results(keyword, page, limit, min_price, max_price, sort_type)
        except Exception as e:
            print(f"11번가 API 응답 파싱 오류: {e}")
            return {'products': [], 'total': 0, 'error': str(e)}
    
    def _call_real_api_product_detail(self, product_id: str) -> Dict:
        """실제 11번가 API 상품 상세 조회"""
        try:
            # 11번가 API 엔드포인트 (실제 API 문서에 따라 수정 필요)
            endpoint = f"{self.base_url}/openapi/OpenApiService.tmall"
            
            params = {
                'key': self.api_key,
                'apiCode': 'ProductDetail',
                'productCode': product_id
            }
            
            # API 호출
            response = requests.get(endpoint, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # 응답 데이터 파싱
            data = response.json()
            
            # 11번가 API 응답 형식에 맞게 변환
            return self._parse_product_detail_response(data)
            
        except requests.exceptions.RequestException as e:
            print(f"11번가 상품 상세 API 호출 오류: {e}")
            # API 호출 실패 시 샘플 데이터로 대체
            return self._get_sample_product_detail(product_id)
        except Exception as e:
            print(f"11번가 상품 상세 API 응답 파싱 오류: {e}")
            return {'error': str(e)}
    
    def _parse_search_response(self, api_response: Dict) -> Dict:
        """11번가 API 검색 응답을 표준 형식으로 변환"""
        try:
            # 11번가 API 응답 구조에 맞게 수정 필요
            products = []
            
            # API 응답에서 상품 목록 추출 (실제 구조에 맞게 수정)
            if 'ProductSearchResponse' in api_response:
                product_list = api_response['ProductSearchResponse'].get('products', [])
                
                for item in product_list:
                    product = {
                        'id': item.get('productCode', ''),
                        'name': item.get('productName', ''),
                        'price': int(item.get('salePrice', 0)),
                        'original_price': int(item.get('originalPrice', 0)),
                        'discount_rate': item.get('discountRate', 0),
                        'image_url': item.get('imageUrl', ''),
                        'brand': item.get('brandName', ''),
                        'rating': float(item.get('rating', 0)),
                        'review_count': int(item.get('reviewCount', 0)),
                        'seller': item.get('sellerName', ''),
                        'delivery_fee': int(item.get('deliveryFee', 0)),
                        'is_free_delivery': item.get('freeDelivery', False),
                        'category': item.get('categoryName', ''),
                        'url': item.get('productUrl', ''),
                        'source': '11번가'
                    }
                    products.append(product)
                
                return {
                    'products': products,
                    'total': api_response['ProductSearchResponse'].get('totalCount', 0),
                    'page': api_response['ProductSearchResponse'].get('pageNum', 1),
                    'limit': api_response['ProductSearchResponse'].get('pageSize', 20),
                    'total_pages': api_response['ProductSearchResponse'].get('totalPages', 1)
                }
            
            return {'products': [], 'total': 0, 'error': 'Invalid API response format'}
            
        except Exception as e:
            print(f"API 응답 파싱 오류: {e}")
            return {'products': [], 'total': 0, 'error': str(e)}
    
    def _parse_product_detail_response(self, api_response: Dict) -> Dict:
        """11번가 API 상품 상세 응답을 표준 형식으로 변환"""
        try:
            # 11번가 API 응답 구조에 맞게 수정 필요
            if 'ProductDetailResponse' in api_response:
                item = api_response['ProductDetailResponse']
                
                return {
                    'id': item.get('productCode', ''),
                    'name': item.get('productName', ''),
                    'price': int(item.get('salePrice', 0)),
                    'original_price': int(item.get('originalPrice', 0)),
                    'discount_rate': item.get('discountRate', 0),
                    'description': item.get('description', ''),
                    'images': item.get('images', []),
                    'brand': item.get('brandName', ''),
                    'rating': float(item.get('rating', 0)),
                    'review_count': int(item.get('reviewCount', 0)),
                    'seller': {
                        'name': item.get('sellerName', ''),
                        'rating': float(item.get('sellerRating', 0)),
                        'business_type': item.get('businessType', '')
                    },
                    'delivery': {
                        'fee': int(item.get('deliveryFee', 0)),
                        'is_free': item.get('freeDelivery', False),
                        'estimated_days': int(item.get('deliveryDays', 0))
                    },
                    'specifications': item.get('specifications', {}),
                    'category': item.get('categoryName', ''),
                    'url': item.get('productUrl', ''),
                    'source': '11번가',
                    'last_updated': datetime.now().isoformat()
                }
            
            return {'error': 'Invalid API response format'}
            
        except Exception as e:
            print(f"상품 상세 API 응답 파싱 오류: {e}")
            return {'error': str(e)}
    
    def _parse_xml_search_response(self, xml_response: str, page: int, limit: int) -> Dict:
        """11번가 API XML 검색 응답을 표준 형식으로 변환"""
        try:
            import xml.etree.ElementTree as ET
            
            # XML 파싱
            root = ET.fromstring(xml_response)
            
            # 전체 상품 수 추출
            total_count_elem = root.find('.//TotalCount')
            total_count = int(total_count_elem.text) if total_count_elem is not None else 0
            
            # 상품 목록 추출
            products = []
            product_elements = root.findall('.//Product')
            
            for product_elem in product_elements:
                try:
                    # 각 필드 추출 (CDATA 처리 포함)
                    product_code = self._get_xml_text(product_elem, 'ProductCode')
                    product_name = self._get_xml_text(product_elem, 'ProductName')
                    product_price = self._get_xml_int(product_elem, 'ProductPrice')
                    sale_price = self._get_xml_int(product_elem, 'SalePrice')
                    product_image = self._get_xml_text(product_elem, 'ProductImage')
                    seller_nick = self._get_xml_text(product_elem, 'SellerNick')
                    seller = self._get_xml_text(product_elem, 'Seller')
                    seller_grd = self._get_xml_int(product_elem, 'SellerGrd')
                    rating = self._get_xml_text(product_elem, 'Rating')
                    detail_page_url = self._get_xml_text(product_elem, 'DetailPageUrl')
                    delivery = self._get_xml_text(product_elem, 'Delivery')
                    review_count = self._get_xml_int(product_elem, 'ReviewCount')
                    buy_satisfy = self._get_xml_int(product_elem, 'BuySatisfy')
                    
                    # 할인 정보 추출
                    benefit_elem = product_elem.find('Benefit')
                    discount = 0
                    if benefit_elem is not None:
                        discount_elem = benefit_elem.find('Discount')
                        if discount_elem is not None:
                            discount = int(discount_elem.text) if discount_elem.text else 0
                    
                    # 할인율 계산
                    discount_rate = 0
                    if product_price > 0 and discount > 0:
                        discount_rate = round((discount / product_price) * 100, 1)
                    
                    # 평점 처리 (빈 값일 수 있음)
                    rating_value = 0.0
                    if rating and rating.strip():
                        try:
                            rating_value = float(rating)
                        except ValueError:
                            rating_value = 0.0
                    
                    # 무료배송 여부 판단
                    is_free_delivery = delivery and '무료' in delivery
                    
                    # 표준 형식으로 변환
                    product = {
                        'id': product_code,
                        'name': product_name,
                        'price': sale_price if sale_price > 0 else product_price,
                        'original_price': product_price,
                        'discount_rate': discount_rate,
                        'image_url': product_image,
                        'brand': seller_nick,  # 11번가에서는 판매자명을 브랜드로 사용
                        'rating': rating_value,
                        'review_count': review_count,
                        'seller': seller_nick,
                        'seller_id': seller,
                        'seller_grade': seller_grd,
                        'delivery_fee': 0 if is_free_delivery else 2500,  # 기본 배송비
                        'is_free_delivery': is_free_delivery,
                        'delivery_info': delivery,
                        'category': '기타',  # 11번가 API에서 카테고리 정보가 명시적이지 않음
                        'url': detail_page_url,
                        'source': '11번가',
                        'buy_satisfaction': buy_satisfy,
                        'discount_amount': discount
                    }
                    
                    products.append(product)
                    
                except Exception as e:
                    print(f"상품 파싱 오류: {e}")
                    continue
            
            # 페이징 처리
            start_idx = (page - 1) * limit
            end_idx = start_idx + limit
            page_products = products[start_idx:end_idx]
            
            total_pages = (total_count + limit - 1) // limit if total_count > 0 else 1
            
            return {
                'products': page_products,
                'total': total_count,
                'page': page,
                'limit': limit,
                'total_pages': total_pages,
                'actual_returned': len(products)
            }
            
        except ET.ParseError as e:
            print(f"XML 파싱 오류: {e}")
            return {'products': [], 'total': 0, 'error': f'XML 파싱 오류: {str(e)}'}
        except Exception as e:
            print(f"응답 처리 오류: {e}")
            return {'products': [], 'total': 0, 'error': str(e)}
    
    def _get_xml_text(self, element, tag_name: str) -> str:
        """XML 요소에서 텍스트 추출 (CDATA 처리 포함)"""
        elem = element.find(tag_name)
        if elem is not None and elem.text:
            return elem.text.strip()
        return ''
    
    def _get_xml_int(self, element, tag_name: str) -> int:
        """XML 요소에서 정수 추출"""
        text = self._get_xml_text(element, tag_name)
        if text:
            try:
                return int(text)
            except ValueError:
                return 0
        return 0
    
    def _call_real_api_product_detail(self, product_id: str) -> Dict:
        """실제 11번가 API 상품 상세 조회"""
        try:
            # 11번가 API 엔드포인트
            endpoint = f"{self.base_url}/openapi/OpenApiService.tmall"
            
            params = {
                'key': self.api_key,
                'apiCode': 'ProductDetail',
                'productCode': product_id
            }
            
            # API 호출
            response = requests.get(endpoint, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # XML 응답 파싱 (상품 상세는 다른 구조일 수 있음)
            return self._parse_xml_product_detail_response(response.text)
            
        except requests.exceptions.RequestException as e:
            print(f"11번가 상품 상세 API 호출 오류: {e}")
            # API 호출 실패 시 샘플 데이터로 대체
            return self._get_sample_product_detail(product_id)
        except Exception as e:
            print(f"11번가 상품 상세 API 응답 파싱 오류: {e}")
            return {'error': str(e)}
    
    def _parse_xml_product_detail_response(self, xml_response: str) -> Dict:
        """11번가 API XML 상품 상세 응답 파싱"""
        try:
            import xml.etree.ElementTree as ET
            
            # XML 파싱
            root = ET.fromstring(xml_response)
            
            # 상품 상세 정보 추출 (실제 API 응답 구조에 따라 조정 필요)
            product_elem = root.find('.//Product')
            if product_elem is None:
                return {'error': '상품 정보를 찾을 수 없습니다'}
            
            product_code = self._get_xml_text(product_elem, 'ProductCode')
            product_name = self._get_xml_text(product_elem, 'ProductName')
            product_price = self._get_xml_int(product_elem, 'ProductPrice')
            sale_price = self._get_xml_int(product_elem, 'SalePrice')
            
            # 이미지 URL들 수집
            images = []
            for size in ['ProductImage', 'ProductImage100', 'ProductImage200', 'ProductImage300']:
                img_url = self._get_xml_text(product_elem, size)
                if img_url and img_url not in images:
                    images.append(img_url)
            
            seller_nick = self._get_xml_text(product_elem, 'SellerNick')
            seller = self._get_xml_text(product_elem, 'Seller')
            seller_grd = self._get_xml_int(product_elem, 'SellerGrd')
            rating = self._get_xml_text(product_elem, 'Rating')
            detail_page_url = self._get_xml_text(product_elem, 'DetailPageUrl')
            delivery = self._get_xml_text(product_elem, 'Delivery')
            review_count = self._get_xml_int(product_elem, 'ReviewCount')
            
            # 할인 정보
            benefit_elem = product_elem.find('Benefit')
            discount = 0
            if benefit_elem is not None:
                discount_elem = benefit_elem.find('Discount')
                if discount_elem is not None:
                    discount = int(discount_elem.text) if discount_elem.text else 0
            
            # 평점 처리
            rating_value = 0.0
            if rating and rating.strip():
                try:
                    rating_value = float(rating)
                except ValueError:
                    rating_value = 0.0
            
            return {
                'id': product_code,
                'name': product_name,
                'price': sale_price if sale_price > 0 else product_price,
                'original_price': product_price,
                'discount_rate': round((discount / product_price) * 100, 1) if product_price > 0 and discount > 0 else 0,
                'description': f'{product_name} 상품입니다.',
                'images': images,
                'brand': seller_nick,
                'rating': rating_value,
                'review_count': review_count,
                'seller': {
                    'name': seller_nick,
                    'id': seller,
                    'rating': seller_grd,
                    'business_type': '판매자'
                },
                'delivery': {
                    'fee': 0 if delivery and '무료' in delivery else 2500,
                    'is_free': delivery and '무료' in delivery,
                    'info': delivery,
                    'estimated_days': 2
                },
                'specifications': {
                    '상품코드': product_code,
                    '판매자': seller_nick
                },
                'category': '기타',
                'url': detail_page_url,
                'source': '11번가',
                'last_updated': datetime.now().isoformat()
            }
            
        except ET.ParseError as e:
            print(f"상품 상세 XML 파싱 오류: {e}")
            return {'error': f'XML 파싱 오류: {str(e)}'}
        except Exception as e:
            print(f"상품 상세 처리 오류: {e}")
            return {'error': str(e)}
    
    def set_api_key(self, api_key: str):
        """API 키를 동적으로 설정"""
        self.api_key = api_key
        self.use_real_api = bool(api_key)
        
        if api_key:
            self.headers['Authorization'] = f'Bearer {api_key}'
            print(f"✅ 11번가 API 키가 업데이트되었습니다: {api_key[:10]}...")
        else:
            self.headers.pop('Authorization', None)
            print("⚠️ API 키가 제거되었습니다. 샘플 데이터를 사용합니다.")