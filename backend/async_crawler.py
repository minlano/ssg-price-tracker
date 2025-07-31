#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import re
import time
from urllib.parse import quote
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
import threading
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# 선택적 import
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    print("⚠️ aiohttp 라이브러리가 없습니다. 동기 방식을 사용합니다.")

try:
    from database_models import Product, SessionLocal, get_db
    from sqlalchemy.orm import Session
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    print("⚠️ SQLAlchemy 라이브러리가 없습니다. 데이터베이스 기능을 비활성화합니다.")

try:
    from cache_manager import cache_manager
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    print("⚠️ 캐시 매니저를 사용할 수 없습니다.")

class AsyncSSGCrawler:
    """비동기 SSG 크롤러"""
    
    def __init__(self, max_concurrent=10):
        self.max_concurrent = max_concurrent
        self.session = None
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        if not AIOHTTP_AVAILABLE:
            return self
            
        connector = aiohttp.TCPConnector(limit=50, limit_per_host=20)
        timeout = aiohttp.ClientTimeout(total=10, connect=5)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        if self.session:
            await self.session.close()
    
    async def fetch_page(self, url: str) -> Optional[str]:
        """비동기 페이지 요청"""
        if not AIOHTTP_AVAILABLE or not self.session:
            # 동기 방식으로 폴백
            return self.fetch_page_sync(url)
            
        async with self.semaphore:
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        print(f"⚠️ HTTP {response.status}: {url}")
                        return None
            except Exception as e:
                print(f"⚠️ 페이지 요청 오류: {e}")
                return None
    
    def fetch_page_sync(self, url: str) -> Optional[str]:
        """동기 페이지 요청 (폴백)"""
        try:
            import requests
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.text
            else:
                print(f"⚠️ HTTP {response.status_code}: {url}")
                return None
        except Exception as e:
            print(f"⚠️ 동기 페이지 요청 오류: {e}")
            return None
    
    async def search_products_async(self, keyword: str, limit: int = 20) -> List[Dict]:
        """비동기 상품 검색"""
        start_time = time.time()
        
        # 1. 캐시 확인 (캐시 매니저가 사용 가능한 경우)
        if CACHE_AVAILABLE:
            cached_results = cache_manager.get_cached_results(keyword, limit)
            if cached_results:
                return cached_results[:limit]
        
        # 2. 데이터베이스 기능 제거 (DB 테이블 없음)
        
        # 3. 실제 크롤링 수행
        print(f"🕷️ 실제 크롤링 시작: {keyword}")
        
        try:
            encoded_keyword = quote(keyword)
            search_url = f"https://www.ssg.com/search.ssg?target=all&query={encoded_keyword}&page=1"
            
            # 검색 페이지 요청
            html_content = await self.fetch_page(search_url)
            if not html_content:
                return []
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 상품 링크 추출
            product_links = soup.select('a[href*="itemView.ssg"][href*="itemId="]')
            
            # 광고 링크 제외
            filtered_links = []
            for link in product_links[:limit * 5]:
                href = link.get('href', '')
                link_text = link.get_text(strip=True)
                
                if ('advertBidId' not in href and 
                    'ADAD' not in link_text and
                    'advertExtensTeryDivCd' not in href):
                    filtered_links.append(link)
                    if len(filtered_links) >= limit * 2:
                        break
            
            print(f"🔗 유효한 상품 링크 {len(filtered_links)}개 발견")
            
            # 병렬 상품 정보 추출
            tasks = []
            for link in filtered_links[:limit * 2]:
                task = self.extract_product_info_async(link, keyword)
                tasks.append(task)
            
            # 모든 작업 병렬 실행
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 성공한 결과만 필터링
            products = []
            for result in results:
                if isinstance(result, dict) and result.get('name'):
                    products.append(result)
                    if len(products) >= limit:
                        break
            
            elapsed_time = time.time() - start_time
            print(f"⚡ 비동기 크롤링 완료: {elapsed_time:.2f}초, {len(products)}개 상품")
            
            # 4. 데이터베이스 저장 기능 제거 (DB 테이블 없음)
                
            # 5. 캐시에 저장 (캐시가 사용 가능한 경우)
            if products and CACHE_AVAILABLE:
                cache_manager.cache_results(keyword, products, limit)
            
            return products
            
        except Exception as e:
            print(f"❌ 비동기 크롤링 오류: {e}")
            return []
    
    async def extract_product_info_async(self, link, keyword: str) -> Optional[Dict]:
        """비동기 상품 정보 추출"""
        try:
            href = link.get('href')
            if href.startswith('/'):
                product_url = f"https://www.ssg.com{href}"
            else:
                product_url = href
            
            # 상품명 추출 (기존 로직 사용)
            name = self.extract_product_name_fast(link, keyword)
            
            # 가격 추출
            price = 0
            current = link.parent
            for _ in range(3):
                if current:
                    price_text = current.get_text()
                    price = self.extract_price_fast(price_text)
                    if price > 0:
                        break
                    current = current.parent
                else:
                    break
            
            # 브랜드 추출
            brand = self.extract_brand_fast(link, name)
            
            # 이미지 URL 추출
            image_url = None
            current = link.parent
            for _ in range(2):
                if current:
                    img = current.find('img')
                    if img:
                        image_url = img.get('src') or img.get('data-src')
                        if image_url:
                            if image_url.startswith('//'):
                                image_url = f"https:{image_url}"
                            elif image_url.startswith('/'):
                                image_url = f"https://www.ssg.com{image_url}"
                            break
                    current = current.parent
                else:
                    break
            
            return {
                'name': name.strip(),
                'price': price,
                'url': product_url,
                'image_url': image_url,
                'brand': brand,
                'source': 'SSG'
            }
            
        except Exception as e:
            return None
    
    def extract_product_name_fast(self, link, keyword: str) -> str:
        """빠른 상품명 추출 (기존 로직 재사용)"""
        try:
            # 모든 텍스트 수집
            all_texts = []
            
            link_text = link.get_text(strip=True)
            if link_text:
                all_texts.append(link_text)
            
            current = link.parent
            for level in range(8):
                if current:
                    text_nodes = current.find_all(text=True)
                    for text_node in text_nodes:
                        text = text_node.strip()
                        if text and len(text) > 5:
                            all_texts.append(text)
                    
                    for tag in ['span', 'div', 'p', 'h1', 'h2', 'h3', 'strong', 'em']:
                        elements = current.find_all(tag)
                        for elem in elements[:10]:
                            elem_text = elem.get_text(strip=True)
                            if elem_text and len(elem_text) > 5:
                                all_texts.append(elem_text)
                    
                    current = current.parent
                else:
                    break
            
            # 최적 상품명 선택
            best_candidates = []
            
            for text in all_texts:
                if not text or len(text) < 10:
                    continue
                
                cleaned_text = self.clean_text_line(text)
                if not cleaned_text or len(cleaned_text) < 10:
                    continue
                
                score = self.calculate_product_name_score(cleaned_text, keyword)
                if score > 0:
                    best_candidates.append((cleaned_text, score))
            
            if best_candidates:
                best_candidates.sort(key=lambda x: x[1], reverse=True)
                best_name = best_candidates[0][0]
                return self.clean_product_name(best_name[:120])
            
            return f"{keyword} 관련 상품"
            
        except Exception:
            return f"{keyword} 관련 상품"
    
    def clean_text_line(self, text: str) -> str:
        """텍스트 라인 정제"""
        if not text:
            return ""
        
        text = re.sub(r'판매가격.*', '', text)
        text = re.sub(r'(\d{1,3}(?:,\d{3})*원).*', '', text)
        text = re.sub(r'(리뷰|별점|할인|배송|무료배송|당일배송|택배).*', '', text)
        text = re.sub(r'(카드할인|즉시할인|추가할인|사은품|증정).*', '', text)
        text = re.sub(r'(100g당|개당|ml당).*', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def calculate_product_name_score(self, text: str, keyword: str) -> int:
        """상품명 적합성 점수 계산"""
        if not text:
            return 0
        
        score = 10
        text_lower = text.lower()
        keyword_lower = keyword.lower()
        
        if keyword_lower in text_lower:
            score += 50
        
        brands = [
            'apple', '삼성', 'samsung', 'lg', '나이키', 'nike', 'adidas', 
            '농심', '오뚜기', '삼양', '팔도', '롯데', 'lotte', 'cj'
        ]
        
        for brand in brands:
            if brand in text_lower:
                score += 30
                break
        
        if re.search(r'[A-Z0-9]{3,}', text):
            score += 15
        
        if any(word in text_lower for word in ['원', '리뷰', '별점', '할인', '배송']):
            score -= 20
        
        if len(text) < 15 or len(text) > 150:
            score -= 10
        
        return max(0, score)
    
    def extract_price_fast(self, text: str) -> int:
        """빠른 가격 추출"""
        if not text:
            return 0
        
        price_match = re.search(r'(\d{1,3}(?:,\d{3})*)\s*원', text)
        if price_match:
            try:
                price = int(price_match.group(1).replace(',', ''))
                if 100 <= price <= 10000000:
                    return price
            except:
                pass
        
        return 0
    
    def extract_brand_fast(self, link, product_name: str) -> str:
        """빠른 브랜드 추출"""
        try:
            if product_name:
                known_brands = [
                    'APPLE', '삼성', 'SAMSUNG', 'LG', '나이키', 'NIKE', 
                    '농심', '오뚜기', '삼양', '아디다스', 'ADIDAS'
                ]
                
                product_upper = product_name.upper()
                for brand in known_brands:
                    if brand.upper() in product_upper:
                        return brand
                
                first_word = product_name.split()[0] if product_name.split() else ''
                if first_word and 2 < len(first_word) < 15:
                    return first_word
            
            return '브랜드 정보 없음'
            
        except Exception:
            return '브랜드 정보 없음'
    
    def clean_product_name(self, name: str) -> str:
        """상품명 정제"""
        if not name:
            return name
        
        name = re.sub(r'(리뷰\s*\d+|별점|할인|배송)', '', name)
        name = re.sub(r'(정상가격|판매가격|최고판매가)', '', name)
        name = re.sub(r'(ADAD란\?\s*툴팁\s*열기)', '', name)
        name = re.sub(r'(검색\s*필터|브랜드\s*전체보기)', '', name)
        name = re.sub(r'(\d+만원\s*이하|\d+만원~\d+만원)', '', name)
        name = re.sub(r'(인기|BEST|추천|선물)', '', name)
        name = re.sub(r'(새벽배송|당일배송|무료배송)', '', name)
        name = re.sub(r'\s+', ' ', name).strip()
        
        if len(name) > 60:
            name = name[:60] + "..."
        
        return name
    
# 데이터베이스 관련 함수들 제거됨 (DB 테이블 없음)

# 비동기 검색 함수
async def search_products_async(keyword: str, limit: int = 20) -> List[Dict]:
    """비동기 상품 검색 메인 함수"""
    async with AsyncSSGCrawler(max_concurrent=10) as crawler:
        return await crawler.search_products_async(keyword, limit)

# 동기 래퍼 함수 (기존 코드와의 호환성)
def search_ssg_products_enhanced(keyword: str, page: int = 1, limit: int = 20) -> List[Dict]:
    """향상된 SSG 상품 검색 (비동기 + 캐싱 + DB)"""
    try:
        # 이벤트 루프 실행
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            results = loop.run_until_complete(search_products_async(keyword, limit))
            return results
        finally:
            loop.close()
            
    except Exception as e:
        print(f"❌ 향상된 검색 오류: {e}")
        # 기존 동기 방식으로 폴백
        from crawler import search_ssg_products
        return search_ssg_products(keyword, page, limit)