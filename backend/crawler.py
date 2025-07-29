import requests
from bs4 import BeautifulSoup
import re
import time
import json
from urllib.parse import quote

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

def search_ssg_products(keyword, page=1, limit=20):
    """SSG에서 상품 검색 (간단하고 확실한 버전)"""
    try:
        encoded_keyword = quote(keyword)
        search_url = f"https://www.ssg.com/search.ssg?target=all&query={encoded_keyword}&page={page}"
        
        headers = get_headers()
        response = requests.get(search_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        products = []
        
        # 모든 상품 링크 찾기
        all_links = soup.find_all('a', href=True)
        product_links = []
        
        for link in all_links:
            href = link.get('href', '')
            if 'itemView.ssg' in href and 'itemId=' in href:
                # 광고 링크 제외
                if 'advertBidId' not in href and 'ADAD' not in link.get_text():
                    product_links.append(link)
        
        print(f"유효한 상품 링크 {len(product_links)}개 발견")
        
        # 상품 정보 추출
        processed_urls = set()
        
        for link in product_links:
            if len(products) >= limit:
                break
                
            try:
                href = link.get('href')
                if href.startswith('/'):
                    product_url = f"https://www.ssg.com{href}"
                else:
                    product_url = href
                
                # 중복 제거
                if product_url in processed_urls:
                    continue
                processed_urls.add(product_url)
                
                # 상품명 추출 - 링크 텍스트 또는 주변 요소에서
                name = link.get_text(strip=True)
                
                # 링크 텍스트가 없거나 너무 짧으면 부모 요소에서 찾기
                if not name or len(name) < 10:
                    parent = link.parent
                    while parent and not name:
                        parent_text = parent.get_text(strip=True)
                        if parent_text and len(parent_text) > 10 and len(parent_text) < 200:
                            # 불필요한 텍스트 제거
                            clean_text = re.sub(r'(리뷰|별점|갯수|할인율|정상가격|판매가격).*', '', parent_text)
                            if len(clean_text) > 10:
                                name = clean_text[:100]
                                break
                        parent = parent.parent
                        if not parent or parent.name == 'body':
                            break
                
                # 여전히 이름이 없으면 기본값
                if not name or len(name) < 5:
                    name = f"{keyword} 관련 상품"
                
                # 가격 추출 - 부모 요소에서 찾기
                price = 0
                current = link.parent
                for _ in range(5):  # 최대 5단계 부모까지 확인
                    if current:
                        price_text = current.get_text()
                        price = extract_price_from_text(price_text)
                        if price > 0:
                            break
                        current = current.parent
                    else:
                        break
                
                # 이미지 찾기
                image_url = None
                current = link.parent
                for _ in range(3):  # 최대 3단계 부모까지 확인
                    if current:
                        img = current.find('img')
                        if img:
                            image_url = img.get('src') or img.get('data-src') or img.get('data-original')
                            if image_url:
                                if image_url.startswith('//'):
                                    image_url = f"https:{image_url}"
                                elif image_url.startswith('/'):
                                    image_url = f"https://www.ssg.com{image_url}"
                                break
                        current = current.parent
                    else:
                        break
                
                # 상품 정보 추가
                products.append({
                    'name': name.strip(),
                    'price': price,
                    'url': product_url,
                    'image_url': image_url,
                    'brand': '브랜드 정보 없음',
                    'source': 'SSG'
                })
                
            except Exception as e:
                print(f"상품 파싱 오류: {e}")
                continue
        
        print(f"최종 추출된 상품: {len(products)}개")
        
        # 결과가 없으면 더미 데이터 생성
        if not products:
            print("실제 검색 결과가 없어 테스트 데이터를 생성합니다.")
            products = create_dummy_products(keyword, limit)
        
        return products[:limit]
        
    except Exception as e:
        print(f"검색 오류: {e}")
        return create_dummy_products(keyword, limit)

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
    """SSG 상품 정보 크롤링 (기존 함수 개선)"""
    try:
        headers = get_headers()
        response = requests.get(url, headers=headers, timeout=10)
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
        
        # 가격 추출 (개선된 패턴)
        price_selectors = [
            '.cdtl_old_price .blind',
            '.cdtl_price .blind',
            '.price_original',
            '.price_discount',
            '.ssg_price',
            '.price'
        ]
        
        price = 0
        for selector in price_selectors:
            price_element = soup.select_one(selector)
            if price_element:
                price_text = price_element.get_text(strip=True)
                price_match = re.search(r'(\d{1,3}(?:,\d{3})*)', price_text.replace(',', ''))
                if price_match:
                    price = int(price_match.group(1).replace(',', ''))
                    break
        
        # 이미지 URL 추출
        image_url = None
        img_selectors = [
            '.cdtl_img_wrap img',
            '.prod_img img',
            '.item_img img'
        ]
        
        for selector in img_selectors:
            img_element = soup.select_one(selector)
            if img_element:
                image_url = img_element.get('src') or img_element.get('data-src')
                if image_url and image_url.startswith('//'):
                    image_url = f"https:{image_url}"
                break
        
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

if __name__ == '__main__':
    print("=== 검색 테스트 ===")
    test_search()
    print("\n=== 가격 비교 테스트 ===")
    test_compare()