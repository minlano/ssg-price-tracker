import requests
from bs4 import BeautifulSoup
import re
import time
import json
from urllib.parse import quote

# 새로운 비동기 크롤러 import
try:
    from async_crawler import search_ssg_products_enhanced
    ASYNC_AVAILABLE = True
    print("✅ 비동기 크롤러 로드 성공")
except ImportError as e:
    print(f"⚠️ 비동기 크롤러 로드 실패: {e}")
    ASYNC_AVAILABLE = False

def get_headers():
    """공통 헤더 반환"""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

def search_ssg_products_legacy(keyword, page=1, limit=20):
    """SSG에서 상품 검색 (개선된 버전)"""
    try:
        encoded_keyword = quote(keyword)
        search_url = f"https://www.ssg.com/search.ssg?target=all&query={encoded_keyword}&page={page}"
        
        headers = get_headers()
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        products = []
        
        print(f"🔍 SSG 검색 페이지 접근 성공: {search_url}")
        
        # 실제 SSG 상품 선택자들 (실제 사이트 구조 기반)
        product_selectors = [
            '.cunit_prod',  # SSG 메인 상품 컨테이너
            '.cunit_item',  # 상품 아이템
            '.prod_item',   # 상품 아이템 대체
            '.item_thmb',   # 썸네일 컨테이너
            'div[class*="cunit"]',  # cunit 관련 클래스
            '[data-item-id]'  # 데이터 속성 기반
        ]
        
        product_elements = []
        for selector in product_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"✅ 선택자 '{selector}'로 {len(elements)}개 상품 발견")
                product_elements = elements
                break
        
        if not product_elements:
            print("⚠️ 상품 요소를 찾을 수 없습니다. 링크 기반으로 시도합니다.")
            # 링크 기반 폴백
            product_links = soup.select('a[href*="itemView.ssg"]')
            for link in product_links[:limit * 2]:
                href = link.get('href', '')
                if 'itemId=' in href and 'advertBidId' not in href:
                    product_elements.append(link.parent or link)
        
        print(f"📦 총 {len(product_elements)}개 상품 요소 발견")
        
        # 상품 정보 추출 (중복 제거 로직 추가)
        seen_urls = set()
        seen_names = set()
        
        for element in product_elements[:limit * 2]:
            if len(products) >= limit:
                break
                
            try:
                product_info = extract_ssg_product_info(element, keyword)
                if product_info and product_info.get('name') and len(product_info['name']) > 5:
                    # 중복 체크
                    url = product_info.get('url', '')
                    name = product_info.get('name', '').strip()
                    
                    if (url not in seen_urls and 
                        name not in seen_names and 
                        len(name) > 5):
                        
                        products.append(product_info)
                        seen_urls.add(url)
                        seen_names.add(name)
                        print(f"✅ 상품 추출: {product_info['name'][:50]}...")
                    
            except Exception as e:
                print(f"⚠️ 상품 정보 추출 실패: {e}")
                continue
        
        print(f"🎯 최종 추출된 상품: {len(products)}개")
        
        # 결과가 부족하면 더미 데이터로 보완
        if len(products) < limit // 2:
            print("📝 결과가 부족하여 테스트 데이터로 보완합니다.")
            dummy_products = create_dummy_products(keyword, limit - len(products))
            products.extend(dummy_products)
        
        return products[:limit]
        
    except Exception as e:
        print(f"❌ SSG 검색 오류: {e}")
        return create_dummy_products(keyword, limit)

def extract_ssg_product_info(element, keyword):
    """SSG 상품 요소에서 정보 추출 (개선된 버전)"""
    try:
        # 1. 상품 URL 찾기
        product_url = None
        link = element.find('a', href=re.compile(r'itemView\.ssg.*itemId='))
        if link:
            href = link.get('href', '')
            if href.startswith('/'):
                product_url = f"https://www.ssg.com{href}"
            else:
                product_url = href
        
        if not product_url:
            return None
        
        # 2. 상품명 추출 (개선된 로직)
        name = None
        
        # 먼저 개별 상품 페이지에서 정확한 상품명 가져오기
        if product_url:
            try:
                page_response = requests.get(product_url, headers=get_headers(), timeout=5)
                if page_response.status_code == 200:
                    page_soup = BeautifulSoup(page_response.content, 'html.parser')
                    
                    # SSG 상품 페이지의 정확한 상품명 선택자
                    page_name_selectors = [
                        'h2.cdtl_prd_nm',
                        'h1.cdtl_prd_nm',
                        '.prod_tit',
                        'title'
                    ]
                    
                    for selector in page_name_selectors:
                        name_elem = page_soup.select_one(selector)
                        if name_elem:
                            candidate_name = name_elem.get_text(strip=True)
                            if candidate_name and candidate_name != "SSG.COM" and len(candidate_name) > 10:
                                name = candidate_name
                                break
                    
                    if name:
                        print(f"✅ 개별 페이지에서 상품명 추출: {name[:50]}...")
            except:
                pass  # 실패해도 계속 진행
        
        # 개별 페이지에서 실패하면 검색 페이지에서 추출
        if not name:
            name_selectors = [
                '.cunit_tit a',           # SSG 메인 상품명
                '.cunit_info .item_tit',  # 상품 정보 제목
                '.prod_tit',              # 상품 제목
                '.item_tit',              # 아이템 제목
                '.cunit_prod .tit',       # 유닛 제목
                'a[href*="itemView"]'     # 링크 텍스트
            ]
            
            for selector in name_selectors:
                name_elem = element.select_one(selector)
                if name_elem:
                    candidate_name = name_elem.get_text(strip=True)
                    if candidate_name and len(candidate_name) > 5 and not is_generic_product_text(candidate_name):
                        name = candidate_name
                        break
            
            # 상품명이 없으면 전체 텍스트에서 추출
            if not name:
                all_text = element.get_text(strip=True)
                lines = [line.strip() for line in all_text.split('\n') if line.strip()]
                for line in lines:
                    if (len(line) > 10 and 
                        keyword.lower() in line.lower() and 
                        not is_generic_product_text(line)):
                        name = line
                        break
                
                if not name and lines:
                    # 첫 번째 의미있는 라인 선택
                    for line in lines:
                        if len(line) > 10 and not is_generic_product_text(line):
                            name = line
                            break
                    
                    if not name:
                        name = f"{keyword} 상품"
        
        # 3. 가격 추출 (개선된 로직)
        price = 0
        
        # 먼저 개별 상품 페이지에서 정확한 가격 가져오기
        if product_url:
            try:
                page_response = requests.get(product_url, headers=get_headers(), timeout=5)
                if page_response.status_code == 200:
                    page_soup = BeautifulSoup(page_response.content, 'html.parser')
                    
                    # SSG 상품 페이지의 정확한 가격 선택자
                    page_price_selectors = [
                        '.cdtl_price .blind',      # 상세 페이지 가격 (숨김 텍스트)
                        '.cdtl_old_price .blind',  # 원가
                        '.price_original',         # 원가
                        '.price_discount',         # 할인가
                        '.ssg_price'              # SSG 가격
                    ]
                    
                    for selector in page_price_selectors:
                        price_elem = page_soup.select_one(selector)
                        if price_elem:
                            price_text = price_elem.get_text(strip=True)
                            price_matches = re.findall(r'(\d{1,3}(?:,\d{3})*)', price_text)
                            if price_matches:
                                try:
                                    candidate_price = int(price_matches[0].replace(',', ''))
                                    if 1000 <= candidate_price <= 50000000:
                                        price = candidate_price
                                        print(f"✅ 개별 페이지에서 가격 추출: {price:,}원")
                                        break
                                except:
                                    continue
                    
                    if price > 0:
                        pass  # 가격을 찾았으므로 검색 페이지에서는 찾지 않음
            except:
                pass  # 실패해도 계속 진행
        
        # 개별 페이지에서 실패하면 검색 페이지에서 추출
        if price == 0:
            price_selectors = [
                '.cunit_price .blind',     # SSG 가격 (숨김 텍스트)
                '.price_original',         # 원가
                '.price_discount',         # 할인가
                '.ssg_price',             # SSG 가격
                '.price',                 # 일반 가격
                '[class*="price"]'        # 가격 관련 클래스
            ]
            
            for selector in price_selectors:
                price_elem = element.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    price_matches = re.findall(r'(\d{1,3}(?:,\d{3})*)', price_text)
                    if price_matches:
                        try:
                            candidate_price = int(price_matches[0].replace(',', ''))
                            if 1000 <= candidate_price <= 50000000:
                                price = candidate_price
                                break
                        except:
                            continue
            
            # 가격이 없으면 전체 텍스트에서 찾기
            if price == 0:
                all_text = element.get_text()
                price_matches = re.findall(r'(\d{1,3}(?:,\d{3})*)\s*원', all_text)
                if price_matches:
                    for match in price_matches:
                        try:
                            candidate_price = int(match.replace(',', ''))
                            if 1000 <= candidate_price <= 50000000:
                                price = candidate_price
                                break
                        except:
                            continue
        
        # 4. 이미지 URL 추출
        image_url = None
        img_selectors = [
            '.cunit_img img',         # SSG 상품 이미지
            '.prod_img img',          # 상품 이미지
            '.item_img img',          # 아이템 이미지
            'img'                     # 모든 이미지
        ]
        
        for selector in img_selectors:
            img_elem = element.select_one(selector)
            if img_elem:
                image_url = img_elem.get('src') or img_elem.get('data-src') or img_elem.get('data-original')
                if image_url:
                    if image_url.startswith('//'):
                        image_url = f"https:{image_url}"
                    elif image_url.startswith('/'):
                        image_url = f"https://www.ssg.com{image_url}"
                    
                    # 유효한 이미지 URL인지 확인
                    if any(ext in image_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                        break
                    else:
                        image_url = None
        
        # 5. 브랜드 추출
        brand = extract_brand_from_element(element, name or "")
        
        # 6. 상품명 정제
        if name:
            name = clean_product_name(name)
        else:
            name = f"{keyword} 관련 상품"
        
        return {
            'name': name,
            'price': price,
            'url': product_url,
            'image_url': image_url,
            'brand': brand,
            'source': 'SSG'
        }
        
    except Exception as e:
        print(f"⚠️ 상품 정보 추출 중 오류: {e}")
        return None

def extract_brand_from_element(element, product_name):
    """요소에서 브랜드 정보 추출"""
    try:
        # 1. 브랜드 관련 클래스에서 찾기
        brand_selectors = [
            '.cunit_brand',           # SSG 브랜드
            '.brand_name',            # 브랜드명
            '.brand',                 # 브랜드
            '.maker',                 # 제조사
            '.vendor'                 # 판매자
        ]
        
        for selector in brand_selectors:
            brand_elem = element.select_one(selector)
            if brand_elem:
                brand_text = brand_elem.get_text(strip=True)
                if brand_text and len(brand_text) < 50:
                    return brand_text
        
        # 2. 상품명에서 브랜드 추출
        if product_name:
            known_brands = [
                'APPLE', '삼성', 'SAMSUNG', 'LG', '나이키', 'NIKE', 
                '아디다스', 'ADIDAS', '농심', '오뚜기', '삼양'
            ]
            
            product_upper = product_name.upper()
            for brand in known_brands:
                if brand.upper() in product_upper:
                    return brand
            
            # 첫 단어가 브랜드일 가능성
            first_word = product_name.split()[0] if product_name.split() else ''
            if first_word and 2 < len(first_word) < 20:
                return first_word
        
        return '브랜드 정보 없음'
        
    except Exception:
        return '브랜드 정보 없음'

def is_generic_product_text(text):
    """일반적인/의미없는 상품 텍스트인지 확인"""
    if not text:
        return True
    
    text_lower = text.lower()
    
    # 의미없는 텍스트 패턴들
    generic_patterns = [
        '함께 보면 좋은',
        '관련 상품',
        '추천 상품',
        '인기 상품',
        '베스트',
        '할인',
        '무료배송',
        '당일배송',
        '리뷰',
        '별점',
        '평점',
        '더보기',
        '자세히',
        '상품정보',
        '상품상세',
        '브랜드 전체보기',
        '검색 필터',
        '정렬',
        '가격대',
        '배송비',
        '적립금'
    ]
    
    for pattern in generic_patterns:
        if pattern in text_lower:
            return True
    
    # 너무 짧거나 숫자만 있는 경우
    if len(text) < 5 or text.isdigit():
        return True
    
    # 특수문자만 있는 경우
    if re.match(r'^[^\w가-힣]+$', text):
        return True
    
    return False

def create_dummy_products(keyword, limit=5):
    """테스트용 더미 상품 데이터 생성"""
    import random
    
    dummy_products = []
    base_prices = [29900, 49900, 79900, 99900, 149900, 199900, 299900]
    
    for i in range(min(limit, 5)):
        price = random.choice(base_prices) + random.randint(-10000, 10000)
        dummy_products.append({
            'name': f"{keyword} 관련 상품 {i+1} - 테스트 데이터",
            'price': max(price, 10000),
            'url': f"https://www.ssg.com/item/itemView.ssg?itemId=test{i+1}",
            'image_url': f"https://via.placeholder.com/200x200?text={keyword}+{i+1}",
            'brand': f"테스트 브랜드 {i+1}",
            'source': 'SSG'
        })
    
    return dummy_products

def crawl_ssg_product(url):
    """SSG 상품 정보 크롤링 (개선된 버전)"""
    try:
        headers = get_headers()
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 상품명 추출 (개선된 패턴)
        name_selectors = [
            'h2.cdtl_prd_nm',
            'h1.cdtl_prd_nm',
            '.prod_tit',
            '.item_tit',
            'title'
        ]
        
        name = None
        for selector in name_selectors:
            name_element = soup.select_one(selector)
            if name_element:
                name = name_element.get_text(strip=True)
                if name and name != "SSG.COM":
                    break
        
        if not name:
            name = "상품명 없음"
        
        # 가격 추출 (대폭 개선된 패턴)
        price = 0
        
        # 1. 메인 가격 선택자들 (실제 SSG 구조 기반)
        main_price_selectors = [
            '.cdtl_price .blind',      # 메인 가격 (숨김 텍스트)
            '.cdtl_old_price .blind',  # 원가 (숨김 텍스트)
            '.price_original',         # 원가
            '.price_discount',         # 할인가
            '.ssg_price',             # SSG 가격
            '.price'                  # 일반 가격
        ]
        
        for selector in main_price_selectors:
            price_element = soup.select_one(selector)
            if price_element:
                price_text = price_element.get_text(strip=True)
                # 여러 가격 패턴 시도
                price_patterns = [
                    r'판매가격\s*(\d{1,3}(?:,\d{3})*)',
                    r'정상가격\s*(\d{1,3}(?:,\d{3})*)',
                    r'할인가\s*(\d{1,3}(?:,\d{3})*)',
                    r'(\d{1,3}(?:,\d{3})*)\s*원',
                    r'(\d{1,3}(?:,\d{3})*)'
                ]
                
                for pattern in price_patterns:
                    price_matches = re.findall(pattern, price_text)
                    if price_matches:
                        try:
                            candidate_price = int(price_matches[0].replace(',', ''))
                            if 1000 <= candidate_price <= 50000000:  # 합리적인 가격 범위
                                price = candidate_price
                                print(f"✅ 가격 추출 성공: {price:,}원 (선택자: {selector})")
                                break
                        except:
                            continue
                
                if price > 0:
                    break
        
        # 2. 가격을 찾지 못했으면 전체 페이지에서 검색
        if price == 0:
            print("⚠️ 메인 선택자에서 가격을 찾지 못함. 전체 페이지 검색 중...")
            page_text = soup.get_text()
            
            # 더 광범위한 가격 패턴
            comprehensive_patterns = [
                r'판매가격[:\s]*(\d{1,3}(?:,\d{3})*)',
                r'정상가격[:\s]*(\d{1,3}(?:,\d{3})*)',
                r'할인가[:\s]*(\d{1,3}(?:,\d{3})*)',
                r'가격[:\s]*(\d{1,3}(?:,\d{3})*)',
                r'(\d{1,3}(?:,\d{3})*)\s*원',
                r'₩\s*(\d{1,3}(?:,\d{3})*)',
                r'KRW\s*(\d{1,3}(?:,\d{3})*)'
            ]
            
            all_prices = []
            for pattern in comprehensive_patterns:
                matches = re.findall(pattern, page_text)
                for match in matches:
                    try:
                        candidate_price = int(match.replace(',', ''))
                        if 10000 <= candidate_price <= 10000000:  # 더 넓은 범위
                            all_prices.append(candidate_price)
                    except:
                        continue
            
            if all_prices:
                # 가격들을 정렬하고 중간값 선택 (이상치 제거)
                all_prices.sort()
                if len(all_prices) == 1:
                    price = all_prices[0]
                else:
                    # 중간값들 중에서 선택
                    mid_start = len(all_prices) // 3
                    mid_end = len(all_prices) * 2 // 3
                    mid_prices = all_prices[mid_start:mid_end] if mid_end > mid_start else all_prices
                    price = mid_prices[0] if mid_prices else all_prices[0]
                
                print(f"✅ 전체 페이지에서 가격 추출: {price:,}원")
        
        # 3. 여전히 가격이 없으면 스크립트 태그에서 찾기
        if price == 0:
            print("⚠️ 스크립트 태그에서 가격 검색 중...")
            script_tags = soup.find_all('script')
            for script in script_tags:
                if script.string:
                    script_text = script.string
                    # JSON 데이터에서 가격 찾기
                    price_patterns = [
                        r'"price"[:\s]*(\d+)',
                        r'"salePrice"[:\s]*(\d+)',
                        r'"originalPrice"[:\s]*(\d+)',
                        r'"sellPrice"[:\s]*(\d+)'
                    ]
                    
                    for pattern in price_patterns:
                        matches = re.findall(pattern, script_text)
                        if matches:
                            try:
                                candidate_price = int(matches[0])
                                if 1000 <= candidate_price <= 50000000:
                                    price = candidate_price
                                    print(f"✅ 스크립트에서 가격 추출: {price:,}원")
                                    break
                            except:
                                continue
                    
                    if price > 0:
                        break
        
        # 이미지 URL 추출 (개선된 패턴)
        image_url = None
        img_selectors = [
            '.cdtl_img_wrap img',
            '.prod_img img',
            '.item_img img',
            '.product_img img',
            'img[src*="item"]',
            'img[data-src*="item"]'
        ]
        
        for selector in img_selectors:
            img_element = soup.select_one(selector)
            if img_element:
                image_url = img_element.get('src') or img_element.get('data-src') or img_element.get('data-original')
                if image_url:
                    if image_url.startswith('//'):
                        image_url = f"https:{image_url}"
                    elif image_url.startswith('/'):
                        image_url = f"https://www.ssg.com{image_url}"
                    
                    # 유효한 이미지 URL인지 확인
                    if any(ext in image_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                        break
                    else:
                        image_url = None
        
        return {
            'name': name,
            'price': price,
            'url': url,
            'image_url': image_url
        }
        
    except Exception as e:
        print(f"크롤링 오류: {e}")
        return None

def compare_products(keyword, limit=10):
    """상품 검색 및 가격 비교"""
    try:
        products = search_ssg_products(keyword, limit=limit)
        
        if not products:
            return []
        
        # 가격순 정렬
        products_sorted = sorted(products, key=lambda x: x['price'] if x['price'] > 0 else float('inf'))
        
        # 가격 비교 정보 추가
        for i, product in enumerate(products_sorted):
            if i == 0 and product['price'] > 0:
                product['price_rank'] = '최저가'
                product['price_diff'] = 0
            elif product['price'] > 0:
                lowest_price = products_sorted[0]['price']
                product['price_diff'] = product['price'] - lowest_price
                product['price_rank'] = f"{i+1}위"
            else:
                product['price_rank'] = '가격 정보 없음'
                product['price_diff'] = 0
        
        return products_sorted
        
    except Exception as e:
        print(f"상품 비교 오류: {e}")
        return []

def extract_product_name_from_ssg(link, product_url, keyword):
    """SSG에서 정확한 상품명 추출"""
    try:
        # 1. 링크 텍스트에서 상품명 추출
        name = link.get_text(strip=True)
        
        # 2. 링크 텍스트가 부족하면 주변 요소에서 찾기
        if not name or len(name) < 10:
            current = link.parent
            for level in range(7):  # 더 많은 레벨 확인
                if current:
                    # 상품명 관련 클래스 찾기
                    name_selectors = [
                        '.item_tit', '.prod_tit', '.product_title', '.title',
                        '.item_name', '.prod_name', '.product_name', '.name',
                        '.goods_name', '.goods_title', '.item_info_tit'
                    ]
                    
                    for selector in name_selectors:
                        name_elem = current.select_one(selector)
                        if name_elem:
                            candidate_name = name_elem.get_text(strip=True)
                            if candidate_name and len(candidate_name) > 10:
                                name = candidate_name
                                break
                    
                    if name and len(name) > 10:
                        break
                    
                    # 클래스 기반으로 찾지 못했으면 텍스트 패턴으로 찾기
                    current_text = current.get_text(strip=True)
                    if current_text and 15 < len(current_text) < 300:
                        # 불필요한 텍스트 제거
                        clean_text = re.sub(r'(리뷰|별점|갯수|할인율|정상가격|판매가격|배송|무료배송|당일배송).*', '', current_text)
                        clean_text = re.sub(r'(\d{1,3}(?:,\d{3})*원).*', '', clean_text)  # 가격 이후 텍스트 제거
                        
                        if len(clean_text) > 15:
                            name = clean_text[:150]
                            break
                    
                    current = current.parent
                else:
                    break
        
        # 3. 개별 페이지 접근은 제거 (속도 개선을 위해)
        
        # 4. 상품명 정제
        if name:
            # 불필요한 텍스트 제거
            name = re.sub(r'(리뷰\s*\d+|별점\s*[\d.]+|갯수\s*\d+)', '', name)
            name = re.sub(r'(할인율\s*\d+%|정상가격|판매가격)', '', name)
            name = re.sub(r'(배송|무료배송|당일배송|택배)', '', name)
            name = re.sub(r'(카드할인|즉시할인|추가할인)', '', name)
            name = re.sub(r'(사은품|증정|이벤트)', '', name)
            name = re.sub(r'\s+', ' ', name).strip()  # 연속 공백 제거
            
            # 상품명이 너무 길면 자르기
            if len(name) > 100:
                name = name[:100] + "..."
            
            return name
        
        # 5. 최후 수단: 기본값 반환
        return f"{keyword} 관련 상품"
        
    except Exception as e:
        return f"{keyword} 관련 상품"

def get_product_name_from_ssg_page(product_url):
    """SSG 개별 상품 페이지에서 상품명 추출"""
    try:
        headers = get_headers()
        response = requests.get(product_url, headers=headers, timeout=8)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # SSG 상품 페이지의 상품명 선택자들
        name_selectors = [
            'h2.cdtl_prd_nm',
            'h1.cdtl_prd_nm', 
            '.prod_tit',
            '.item_tit',
            '.product_title',
            '.goods_name',
            'title'
        ]
        
        for selector in name_selectors:
            name_elem = soup.select_one(selector)
            if name_elem:
                name = name_elem.get_text(strip=True)
                if name and name != "SSG.COM" and len(name) > 10:
                    return name
        
        return None
        
    except Exception as e:
        return None

def extract_brand_from_ssg(link, product_name):
    """SSG에서 브랜드 정보 추출"""
    try:
        # 1. 링크 주변 요소에서 브랜드 정보 찾기
        current = link.parent
        for _ in range(5):  # 최대 5단계 부모까지 확인
            if current:
                # 브랜드 관련 클래스나 속성 찾기
                brand_selectors = [
                    '.brand', '.brand_name', '.brand_info', '.brand_txt',
                    '.maker', '.maker_name', '.company', '.company_name',
                    '.vendor', '.vendor_name', '.seller', '.seller_name'
                ]
                
                for selector in brand_selectors:
                    brand_elem = current.select_one(selector)
                    if brand_elem:
                        brand_text = brand_elem.get_text(strip=True)
                        if brand_text and len(brand_text) < 50:  # 브랜드명은 보통 짧음
                            return brand_text
                
                # 텍스트에서 브랜드 패턴 찾기
                current_text = current.get_text()
                brand_match = re.search(r'브랜드[:\s]*([가-힣A-Za-z0-9\s&]+)', current_text)
                if brand_match:
                    brand = brand_match.group(1).strip()
                    if len(brand) < 30:
                        return brand
                
                current = current.parent
            else:
                break
        
        # 2. 상품명에서 브랜드 추출
        if product_name:
            # 잘 알려진 브랜드 패턴
            known_brands = [
                # 전자제품
                'APPLE', '삼성', 'SAMSUNG', 'LG', '소니', 'SONY', '화웨이', 'HUAWEI',
                '샤오미', 'XIAOMI', '구글', 'GOOGLE', '마이크로소프트', 'MICROSOFT',
                # 패션
                '나이키', 'NIKE', '아디다스', 'ADIDAS', '푸마', 'PUMA', '언더아머', 'UNDER ARMOUR',
                '유니클로', 'UNIQLO', '자라', 'ZARA', 'H&M',
                # 식품
                '농심', '오뚜기', '삼양', '팔도', '롯데', 'LOTTE', 'CJ', '동원',
                # 화장품
                '아모레퍼시픽', '더페이스샵', '이니스프리', '에뛰드', '미샤', 'MISSHA',
                # 생활용품
                'P&G', '유한킴벌리', '애경', '라이온', 'LION'
            ]
            
            product_upper = product_name.upper()
            for brand in known_brands:
                if brand.upper() in product_upper:
                    return brand
            
            # 상품명 첫 단어가 브랜드일 가능성
            first_word = product_name.split()[0] if product_name.split() else ''
            if first_word and len(first_word) > 1 and len(first_word) < 20:
                # 영문이나 한글로만 구성된 경우
                if re.match(r'^[A-Za-z가-힣]+$', first_word):
                    return first_word
        
        # 3. 기본값 반환
        return '브랜드 정보 없음'
        
    except Exception as e:
        return '브랜드 정보 없음'

def extract_price_from_text(text):
    """텍스트에서 가격 추출"""
    if not text:
        return 0
    
    # 여러 가격 패턴 시도
    patterns = [
        r'판매가격\s*(\d{1,3}(?:,\d{3})*)',
        r'정상가격\s*(\d{1,3}(?:,\d{3})*)',
        r'(\d{1,3}(?:,\d{3})*)\s*원',
        r'가격\s*(\d{1,3}(?:,\d{3})*)',
        r'(\d{1,3}(?:,\d{3})*)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            # 가장 큰 숫자를 가격으로 간주 (할인가보다 정가가 클 수 있음)
            prices = [int(match.replace(',', '')) for match in matches]
            valid_prices = [p for p in prices if 1000 <= p <= 10000000]  # 합리적인 가격 범위
            if valid_prices:
                return min(valid_prices)  # 최저가 반환
    
    return 0

def get_product_price_from_page(url):
    """개별 상품 페이지에서 가격 정보 가져오기"""
    try:
        headers = get_headers()
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 가격 선택자들
        price_selectors = [
            '.cdtl_old_price .blind',
            '.cdtl_price .blind', 
            '.price_original',
            '.price_discount',
            '.ssg_price',
            '.price'
        ]
        
        for selector in price_selectors:
            price_elem = soup.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price = extract_price_from_text(price_text)
                if price > 0:
                    return price
        
        # 전체 페이지에서 가격 패턴 찾기
        page_text = soup.get_text()
        price = extract_price_from_text(page_text)
        return price
        
    except Exception as e:
        print(f"개별 페이지 가격 추출 오류: {e}")
        return 0

def test_search():
    """검색 기능 테스트"""
    keyword = "아이폰"
    print(f"'{keyword}' 검색 결과:")
    products = search_ssg_products(keyword, limit=3)
    
    for i, product in enumerate(products, 1):
        print(f"{i}. {product['name'][:50]}...")
        
        # 가격이 0이면 개별 페이지에서 가져오기 시도
        if product['price'] == 0 and product['url'] and 'itemView.ssg' in product['url']:
            print(f"   개별 페이지에서 가격 확인 중...")
            product['price'] = get_product_price_from_page(product['url'])
        
        print(f"   가격: {product['price']:,}원")
        print(f"   브랜드: {product['brand']}")
        print(f"   URL: {product['url']}")
        print()

def test_compare():
    """가격 비교 테스트"""
    keyword = "무선이어폰"
    print(f"'{keyword}' 가격 비교:")
    products = compare_products(keyword, limit=3)
    
    for product in products:
        print(f"[{product['price_rank']}] {product['name'][:50]}...")
        print(f"가격: {product['price']:,}원 (+{product['price_diff']:,}원)")
        print(f"브랜드: {product['brand']}")
        print()

def test_single_product():
    """단일 상품 크롤링 테스트"""
    test_url = "https://www.ssg.com/item/itemView.ssg?itemId=1000618003010"
    print(f"단일 상품 테스트: {test_url}")
    result = crawl_ssg_product(test_url)
    if result:
        print(f"상품명: {result['name']}")
        print(f"가격: {result['price']:,}원")
        print(f"이미지: {result['image_url']}")
    else:
        print("크롤링 실패")

def extract_product_name_fast(link, keyword):
    """빠른 상품명 추출 (완전히 새로운 접근법)"""
    try:
        # 1. 링크와 주변 모든 텍스트 수집
        all_texts = []
        
        # 링크 자체 텍스트
        link_text = link.get_text(strip=True)
        if link_text:
            all_texts.append(link_text)
        
        # 부모 요소들의 텍스트 (더 광범위하게)
        current = link.parent
        for level in range(8):  # 더 많은 레벨 확인
            if current:
                # 모든 자식 텍스트 노드 수집
                text_nodes = current.find_all(text=True)
                for text_node in text_nodes:
                    text = text_node.strip()
                    if text and len(text) > 5:
                        all_texts.append(text)
                
                # 특정 태그들의 텍스트도 수집
                for tag in ['span', 'div', 'p', 'h1', 'h2', 'h3', 'strong', 'em']:
                    elements = current.find_all(tag)
                    for elem in elements[:10]:  # 각 태그당 최대 10개
                        elem_text = elem.get_text(strip=True)
                        if elem_text and len(elem_text) > 5:
                            all_texts.append(elem_text)
                
                current = current.parent
            else:
                break
        
        # 2. 수집된 텍스트들을 분석하여 가장 적합한 상품명 찾기
        best_candidates = []
        
        for text in all_texts:
            if not text or len(text) < 10:
                continue
            
            # 텍스트 정제
            cleaned_text = clean_text_line(text)
            if not cleaned_text or len(cleaned_text) < 10:
                continue
            
            # 상품명 점수 계산
            score = calculate_product_name_score(cleaned_text, keyword)
            if score > 0:
                best_candidates.append((cleaned_text, score))
        
        # 3. 가장 높은 점수의 상품명 선택
        if best_candidates:
            best_candidates.sort(key=lambda x: x[1], reverse=True)
            best_name = best_candidates[0][0]
            return clean_product_name(best_name[:120])
        
        return f"{keyword} 관련 상품"
        
    except Exception:
        return f"{keyword} 관련 상품"

def calculate_product_name_score(text, keyword):
    """상품명 적합성 점수 계산"""
    if not text or is_generic_text(text):
        return 0
    
    score = 0
    text_lower = text.lower()
    keyword_lower = keyword.lower()
    
    # 기본 점수
    score += 10
    
    # 검색 키워드 포함 시 높은 점수
    if keyword_lower in text_lower:
        score += 50
    
    # 브랜드명 포함 시 점수 추가
    brands = [
        'apple', '삼성', 'samsung', 'lg', '나이키', 'nike', 'adidas', 
        '농심', '오뚜기', '삼양', '팔도', '롯데', 'lotte', 'cj',
        '아모레', '이니스프리', '에뛰드', '미샤', '더페이스샵',
        '지오다노', '유니클로', 'uniqlo', '자라', 'zara'
    ]
    
    for brand in brands:
        if brand in text_lower:
            score += 30
            break
    
    # 상품 관련 키워드 포함 시 점수 추가
    product_keywords = [
        'gb', '프로', '맥스', '미니', '플러스', '울트라', '에어',
        '티셔츠', '후드', '바지', '원피스', '스커트', '자켓',
        '스니커즈', '부츠', '샌들', '슬리퍼',
        '크림', '로션', '세럼', '마스크', '클렌저',
        '노트북', '태블릿', '스마트폰', '이어폰', '케이스'
    ]
    
    for keyword in product_keywords:
        if keyword in text_lower:
            score += 20
            break
    
    # 모델명이나 제품 코드 포함 시 점수 추가
    if re.search(r'[A-Z0-9]{3,}', text):
        score += 15
    
    # 가격이나 리뷰 정보가 포함된 경우 점수 감소
    if any(word in text_lower for word in ['원', '리뷰', '별점', '할인', '배송']):
        score -= 20
    
    # 너무 짧거나 긴 텍스트 점수 감소
    if len(text) < 15 or len(text) > 150:
        score -= 10
    
    return max(0, score)

def clean_text_line(text):
    """텍스트 라인 정제 (개선된 버전)"""
    if not text:
        return ""
    
    # 판매가격 이전까지만 추출 (상품명 부분)
    text = re.sub(r'판매가격.*', '', text)
    # 가격 이후 텍스트 제거
    text = re.sub(r'(\d{1,3}(?:,\d{3})*원).*', '', text)
    # 불필요한 텍스트 제거
    text = re.sub(r'(리뷰|별점|할인|배송|무료배송|당일배송|택배).*', '', text)
    text = re.sub(r'(카드할인|즉시할인|추가할인|사은품|증정).*', '', text)
    text = re.sub(r'(100g당|개당|ml당).*', '', text)  # 단위당 가격 제거
    # 연속 공백 제거
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def is_generic_text(text):
    """일반적인 텍스트인지 확인"""
    if not text:
        return True
    
    generic_patterns = [
        r'^(상품|제품|아이템)$',
        r'^(이미지|사진|그림)$',
        r'^(링크|바로가기)$',
        r'^(더보기|자세히)$',
        r'^\d+$',  # 숫자만
        r'^[가-힣]{1,2}$',  # 한글 1-2자
    ]
    
    for pattern in generic_patterns:
        if re.match(pattern, text.strip()):
            return True
    
    return False

def has_product_keywords(text, keyword):
    """상품 관련 키워드가 포함되어 있는지 확인"""
    if not text:
        return False
    
    text_lower = text.lower()
    keyword_lower = keyword.lower()
    
    # 검색 키워드가 포함된 경우
    if keyword_lower in text_lower:
        return True
    
    # 브랜드 키워드가 포함된 경우
    brand_keywords = [
        'apple', '삼성', 'samsung', 'lg', '나이키', 'nike', 'adidas',
        '농심', '오뚜기', '삼양', '팔도', '롯데', 'lotte'
    ]
    
    for brand in brand_keywords:
        if brand in text_lower:
            return True
    
    # 상품 관련 키워드가 포함된 경우
    product_keywords = ['gb', '프로', '맥스', '미니', '플러스', '울트라']
    for prod_keyword in product_keywords:
        if prod_keyword in text_lower:
            return True
    
    return False

def extract_price_fast(text):
    """빠른 가격 추출 (간소화된 버전)"""
    if not text:
        return 0
    
    # 가장 간단한 가격 패턴만 사용
    price_match = re.search(r'(\d{1,3}(?:,\d{3})*)\s*원', text)
    if price_match:
        try:
            price = int(price_match.group(1).replace(',', ''))
            if 100 <= price <= 10000000:
                return price
        except:
            pass
    
    return 0

def extract_brand_fast(link, product_name):
    """빠른 브랜드 추출 (간소화된 버전)"""
    try:
        if product_name:
            # 잘 알려진 브랜드만 빠르게 확인
            known_brands = [
                'APPLE', '삼성', 'SAMSUNG', 'LG', '나이키', 'NIKE', 
                '농심', '오뚜기', '삼양', '아디다스', 'ADIDAS'
            ]
            
            product_upper = product_name.upper()
            for brand in known_brands:
                if brand.upper() in product_upper:
                    return brand
            
            # 첫 단어만 확인
            first_word = product_name.split()[0] if product_name.split() else ''
            if first_word and 2 < len(first_word) < 15:
                return first_word
        
        return '브랜드 정보 없음'
        
    except Exception:
        return '브랜드 정보 없음'

def get_product_name_from_page_fast(product_url):
    """개별 페이지에서 빠른 상품명 추출"""
    try:
        headers = get_headers()
        response = requests.get(product_url, headers=headers, timeout=3)  # 매우 짧은 타임아웃
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 가장 확실한 선택자들만 사용
        name_selectors = [
            'h2.cdtl_prd_nm',
            'h1.cdtl_prd_nm',
            '.prod_tit',
            '.item_tit'
        ]
        
        for selector in name_selectors:
            name_elem = soup.select_one(selector)
            if name_elem:
                name = name_elem.get_text(strip=True)
                if name and name != "SSG.COM" and len(name) > 10:
                    return name
        
        return None
        
    except Exception:
        return None

def clean_product_name(name):
    """상품명 정제 (강화된 버전)"""
    if not name:
        return name
    
    # 불필요한 텍스트 제거
    name = re.sub(r'(리뷰\s*\d+|별점|할인|배송)', '', name)
    name = re.sub(r'(정상가격|판매가격|최고판매가)', '', name)
    name = re.sub(r'(ADAD란\?\s*툴팁\s*열기)', '', name)  # 광고 관련 텍스트
    name = re.sub(r'(검색\s*필터|브랜드\s*전체보기)', '', name)  # 필터 관련 텍스트
    name = re.sub(r'(\d+만원\s*이하|\d+만원~\d+만원)', '', name)  # 가격 범위 텍스트
    name = re.sub(r'(인기|BEST|추천|선물)', '', name)  # 마케팅 텍스트
    name = re.sub(r'(새벽배송|당일배송|무료배송)', '', name)  # 배송 관련
    
    # 연속 공백 제거
    name = re.sub(r'\s+', ' ', name).strip()
    
    # 길이 제한 (더 짧게)
    if len(name) > 60:
        name = name[:60] + "..."
    
    return name

def search_ssg_products(keyword, page=1, limit=20):
    """메인 SSG 상품 검색 함수 (비동기 우선, 동기 폴백)"""
    try:
        if ASYNC_AVAILABLE:
            print("🚀 비동기 크롤러 사용")
            return search_ssg_products_enhanced(keyword, page, limit)
        else:
            print("🐌 기존 동기 크롤러 사용")
            return search_ssg_products_legacy(keyword, page, limit)
    except Exception as e:
        print(f"⚠️ 비동기 크롤러 오류, 동기 크롤러로 폴백: {e}")
        return search_ssg_products_legacy(keyword, page, limit)

if __name__ == '__main__':
    print("=== SSG 검색 테스트 ===")
    test_search()
    print("\n=== SSG 가격 비교 테스트 ===")
    test_compare()
    print("\n=== 단일 상품 테스트 ===")
    test_single_product()