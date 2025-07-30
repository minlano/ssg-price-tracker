import requests
import sqlite3
import os
import json
from urllib.parse import quote
import random
from dotenv import load_dotenv

class NaverShoppingCrawler:
    def __init__(self):
        # .env 파일 로드
        load_dotenv()
        
        self.client_id = os.getenv('NAVER_CLIENT_ID')
        self.client_secret = os.getenv('NAVER_CLIENT_SECRET')
        
        if not self.client_id or not self.client_secret:
            raise ValueError("네이버 API 키가 설정되지 않았습니다. .env 파일을 확인하세요.")
        
        self.db_path = os.path.join(os.path.dirname(__file__), '../../database/naver_shopping_tracker.db')
        self.init_database()
    
    def init_database(self):
        """네이버 쇼핑 전용 데이터베이스 초기화 (SSG와 동일한 구조)"""
        if os.path.exists(self.db_path):
            print(f"데이터베이스가 이미 존재합니다: {self.db_path}")
            return
        
        # 데이터베이스 디렉토리 생성
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # SSG와 동일한 products 테이블 구조
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                current_price INTEGER,
                image_url TEXT,
                brand TEXT,
                source TEXT DEFAULT 'NaverShopping',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # SSG와 동일한 price_logs 테이블 구조
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                price INTEGER NOT NULL,
                logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            )
        ''')
        
        # SSG와 동일한 alerts 테이블 구조
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                user_email TEXT NOT NULL,
                target_price INTEGER NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            )
        ''')
        
        # 인덱스 생성
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_price_logs_product_id ON price_logs(product_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_price_logs_logged_at ON price_logs(logged_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_product_id ON alerts(product_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_is_active ON alerts(is_active)')
        
        conn.commit()
        conn.close()
        print(f"네이버 쇼핑 데이터베이스 생성 완료: {self.db_path}")
    
    def search_products(self, keyword, limit=20):
        """네이버 쇼핑 API로 상품 검색"""
        try:
            encoded_keyword = quote(keyword)
            api_url = f"https://openapi.naver.com/v1/search/shop.json?query={encoded_keyword}&display={limit}&sort=sim"
            
            headers = {
                'X-Naver-Client-Id': self.client_id,
                'X-Naver-Client-Secret': self.client_secret,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            print(f"네이버 쇼핑 API 호출 중: {keyword}")
            response = requests.get(api_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            products = []
            
            if 'items' in data:
                print(f"네이버 쇼핑에서 {len(data['items'])}개 상품 발견")
                
                for item in data['items']:
                    try:
                        product_data = self.extract_product_info(item)
                        if product_data:
                            products.append(product_data)
                    except Exception as e:
                        print(f"상품 정보 추출 오류: {e}")
                        continue
            else:
                print("검색 결과가 없습니다.")
            
            return products
            
        except Exception as e:
            print(f"네이버 쇼핑 API 오류: {e}")
            return []
    
    def extract_product_info(self, item):
        """네이버 쇼핑 API 응답에서 상품 정보 추출"""
        try:
            # HTML 태그 제거 함수
            def remove_html_tags(text):
                import re
                clean = re.compile('<.*?>')
                return re.sub(clean, '', text)
            
            # 상품명 (HTML 태그 제거)
            name = remove_html_tags(item.get('title', ''))
            
            # URL
            url = item.get('link', '')
            
            # 가격 (문자열에서 숫자만 추출)
            price_str = item.get('lprice', '0')
            current_price = int(price_str) if price_str.isdigit() else 0
            
            # 이미지 URL
            image_url = item.get('image', '')
            
            # 브랜드/쇼핑몰명
            brand = item.get('mallName', '네이버쇼핑')
            
            # 디버깅 정보 출력
            print(f"추출된 정보 - 이름: {name[:30]}..., 가격: {current_price:,}원, 쇼핑몰: {brand}")
            
            if name and current_price > 0 and url:
                return {
                    'name': name[:200],  # 길이 제한
                    'url': url,
                    'current_price': current_price,
                    'image_url': image_url,
                    'brand': brand,
                    'source': 'NaverShopping'
                }
            
            return None
            
        except Exception as e:
            print(f"상품 정보 추출 오류: {e}")
            return None
    
    def save_product(self, product_data):
        """상품 정보를 데이터베이스에 저장 (SSG 구조에 맞춤)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 기존 상품 확인
            cursor.execute('SELECT id, current_price FROM products WHERE url = ?', (product_data['url'],))
            existing = cursor.fetchone()
            
            if existing:
                product_id, old_price = existing
                # 가격이 변경된 경우 업데이트
                if old_price != product_data['current_price']:
                    cursor.execute('''
                        UPDATE products 
                        SET current_price = ?
                        WHERE id = ?
                    ''', (product_data['current_price'], product_id))
                    
                    # 가격 이력 추가
                    cursor.execute('''
                        INSERT INTO price_logs (product_id, price)
                        VALUES (?, ?)
                    ''', (product_id, product_data['current_price']))
                    
                    print(f"상품 가격 업데이트: {product_data['name'][:30]}... ({old_price:,}원 → {product_data['current_price']:,}원)")
            else:
                # 새 상품 추가
                cursor.execute('''
                    INSERT INTO products 
                    (name, url, current_price, image_url, brand, source)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (product_data['name'], product_data['url'], product_data['current_price'],
                      product_data['image_url'], product_data['brand'], product_data['source']))
                
                product_id = cursor.lastrowid
                
                # 초기 가격 이력 추가
                cursor.execute('''
                    INSERT INTO price_logs (product_id, price)
                    VALUES (?, ?)
                ''', (product_id, product_data['current_price']))
                
                print(f"새 상품 추가: {product_data['name'][:30]}... ({product_data['current_price']:,}원)")
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"데이터베이스 저장 오류: {e}")
            return False
    
    def get_products_from_db(self, limit=50):
        """데이터베이스에서 상품 목록 조회 (SSG 구조에 맞춤)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, url, current_price, image_url, brand, source, created_at
                FROM products 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            products = []
            for row in cursor.fetchall():
                products.append({
                    'id': row[0],
                    'name': row[1],
                    'url': row[2],
                    'current_price': row[3],
                    'image_url': row[4],
                    'brand': row[5],
                    'source': row[6],
                    'created_at': row[7]
                })
            
            conn.close()
            return products
            
        except Exception as e:
            print(f"데이터베이스 조회 오류: {e}")
            return []
    
    def search_and_save(self, keyword, limit=20):
        """상품 검색 후 데이터베이스에 저장"""
        print(f"네이버 쇼핑에서 '{keyword}' 검색 중...")
        products = self.search_products(keyword, limit)
        
        saved_count = 0
        for product in products:
            if self.save_product(product):
                saved_count += 1
        
        print(f"총 {len(products)}개 상품 중 {saved_count}개 저장 완료")
        return products

def test_naver_shopping_crawler():
    """네이버 쇼핑 크롤러 테스트"""
    try:
        crawler = NaverShoppingCrawler()
        
        # 검색 테스트
        print("=== 네이버 쇼핑 크롤러 테스트 ===")
        keyword = "라면"
        products = crawler.search_and_save(keyword, limit=5)
        
        print(f"\n검색 결과 ({len(products)}개):")
        for i, product in enumerate(products, 1):
            print(f"{i}. {product['name'][:50]}...")
            print(f"   가격: {product['current_price']:,}원")
            print(f"   쇼핑몰: {product['brand']}")
            print(f"   소스: {product['source']}")
            print(f"   URL: {product['url'][:80]}...")
            print()
        
        # 데이터베이스 조회 테스트
        print("=== 데이터베이스 저장된 상품 ===")
        saved_products = crawler.get_products_from_db(limit=10)
        print(f"저장된 상품 수: {len(saved_products)}개")
        
    except ValueError as e:
        print(f"설정 오류: {e}")
        print("1. .env 파일에 NAVER_CLIENT_ID와 NAVER_CLIENT_SECRET을 설정하세요.")
        print("2. pip install python-dotenv 명령어로 dotenv를 설치하세요.")
    except Exception as e:
        print(f"테스트 오류: {e}")

if __name__ == '__main__':
    test_naver_shopping_crawler()