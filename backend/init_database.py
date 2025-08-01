#!/usr/bin/env python3
"""
데이터베이스 초기화 및 샘플 데이터 생성 스크립트
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

def init_database():
    """데이터베이스 초기화 (사용자 데이터 보존)"""
    # database/ssg_tracker.db 사용
    db_path = '../database/ssg_tracker.db'
    
    # 데이터베이스 디렉토리 생성
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # 기존 데이터베이스가 있는지 확인
    db_exists = os.path.exists(db_path)
    
    if db_exists:
        print("📋 기존 데이터베이스 발견 - 사용자 데이터 보존 모드")
        
        # 기존 사용자 데이터 백업
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 사용자가 추가한 상품들 백업 (샘플 데이터가 아닌 것들)
        cursor.execute('''
            SELECT * FROM products 
            WHERE name NOT LIKE '[SAMPLE]%'
            ORDER BY created_at DESC
        ''')
        user_products = cursor.fetchall()
        
        print(f"💾 사용자 상품 {len(user_products)}개 백업됨")
        
        # 기본 샘플 상품들만 삭제 (SAMPLE 태그가 있는 것들)
        cursor.execute('''
            DELETE FROM products 
            WHERE name LIKE '[SAMPLE]%'
        ''')
        deleted_count = cursor.rowcount
        print(f"🗑️ 기본 샘플 상품 {deleted_count}개 삭제됨")
        
        conn.commit()
        conn.close()
        
        # 새로운 샘플 데이터 추가
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
    else:
        print("🆕 새 데이터베이스 생성")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 테이블 생성
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT,
                image_url TEXT,
                current_price INTEGER,
                brand TEXT,
                source TEXT DEFAULT 'SSG',
                created_at DATETIME DEFAULT (datetime('now', '+09:00'))
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                user_email TEXT NOT NULL,
                target_price INTEGER,
                is_active INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT (datetime('now', '+09:00')),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                price INTEGER,
                logged_at DATETIME DEFAULT (datetime('now', '+09:00')),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                price INTEGER,
                recorded_at DATETIME DEFAULT (datetime('now', '+09:00')),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        conn.commit()
        print("✅ 데이터베이스 테이블 생성 완료")
    
    return conn, cursor

def generate_sample_data(conn, cursor):
    """샘플 데이터 생성"""
    
    # 샘플 상품 데이터 (SAMPLE 태그 추가)
    sample_products = [
        {
            'name': '[SAMPLE] 삼성 갤럭시 S24 Ultra 256GB 자급제',
            'url': 'https://www.ssg.com/item/itemView.ssg?itemId=1000624234995',
            'image_url': 'https://via.placeholder.com/300x200/4A90E2/FFFFFF?text=Galaxy+S24+Ultra',
            'current_price': 1850000,
            'brand': 'Samsung',
            'source': 'SSG'
        },
        {
            'name': '[SAMPLE] Apple iPhone 15 Pro 256GB 자급제',
            'url': 'https://www.ssg.com/item/itemView.ssg?itemId=1000618003010',
            'image_url': 'https://via.placeholder.com/300x200/000000/FFFFFF?text=iPhone+15+Pro',
            'current_price': 1650000,
            'brand': 'Apple',
            'source': 'SSG'
        },
        {
            'name': '[SAMPLE] LG OLED TV 65인치 4K 스마트TV',
            'url': 'https://www.ssg.com/item/itemView.ssg?itemId=1000644998500',
            'image_url': 'https://via.placeholder.com/300x200/FF0000/FFFFFF?text=LG+OLED+TV',
            'current_price': 2800000,
            'brand': 'LG',
            'source': 'SSG'
        },
        {
            'name': '[SAMPLE] Sony WH-1000XM5 무선 노이즈 캔슬링 헤드폰',
            'url': 'https://www.ssg.com/item/itemView.ssg?itemId=1000644998501',
            'image_url': 'https://via.placeholder.com/300x200/000000/FFFFFF?text=Sony+WH-1000XM5',
            'current_price': 450000,
            'brand': 'Sony',
            'source': 'SSG'
        },
        {
            'name': '[SAMPLE] Dell XPS 13 Plus 노트북 13.4인치',
            'url': 'https://www.ssg.com/item/itemView.ssg?itemId=1000644998502',
            'image_url': 'https://via.placeholder.com/300x200/007DB8/FFFFFF?text=Dell+XPS+13',
            'current_price': 2200000,
            'brand': 'Dell',
            'source': 'SSG'
        },
        {
            'name': '[SAMPLE] Nike Air Max 270 운동화',
            'url': 'https://www.ssg.com/item/itemView.ssg?itemId=1000644998503',
            'image_url': 'https://via.placeholder.com/300x200/000000/FFFFFF?text=Nike+Air+Max+270',
            'current_price': 180000,
            'brand': 'Nike',
            'source': 'SSG'
        },
        {
            'name': '[SAMPLE] Adidas Ultraboost 22 러닝화',
            'url': 'https://www.ssg.com/item/itemView.ssg?itemId=1000644998504',
            'image_url': 'https://via.placeholder.com/300x200/000000/FFFFFF?text=Adidas+Ultraboost',
            'current_price': 220000,
            'brand': 'Adidas',
            'source': 'SSG'
        },
        {
            'name': '[SAMPLE] Canon EOS R6 Mark II 미러리스 카메라',
            'url': 'https://www.ssg.com/item/itemView.ssg?itemId=1000644998505',
            'image_url': 'https://via.placeholder.com/300x200/000000/FFFFFF?text=Canon+EOS+R6',
            'current_price': 3200000,
            'brand': 'Canon',
            'source': 'SSG'
        },
        {
            'name': '[SAMPLE] Samsung 970 EVO Plus 1TB NVMe SSD',
            'url': 'https://www.ssg.com/item/itemView.ssg?itemId=1000644998506',
            'image_url': 'https://via.placeholder.com/300x200/1428A0/FFFFFF?text=Samsung+970+EVO',
            'current_price': 120000,
            'brand': 'Samsung',
            'source': 'SSG'
        },
        {
            'name': '[SAMPLE] Apple MacBook Air M2 13.6인치',
            'url': 'https://www.ssg.com/item/itemView.ssg?itemId=1000644998507',
            'image_url': 'https://via.placeholder.com/300x200/000000/FFFFFF?text=MacBook+Air+M2',
            'current_price': 1800000,
            'brand': 'Apple',
            'source': 'SSG'
        },
        {
            'name': '[SAMPLE] LG 그램 16인치 노트북',
            'url': 'https://www.ssg.com/item/itemView.ssg?itemId=1000644998508',
            'image_url': 'https://via.placeholder.com/300x200/000000/FFFFFF?text=LG+Gram+16',
            'current_price': 1600000,
            'brand': 'LG',
            'source': 'SSG'
        },
        {
            'name': '[SAMPLE] Sony PlayStation 5 게임기',
            'url': 'https://www.ssg.com/item/itemView.ssg?itemId=1000644998509',
            'image_url': 'https://via.placeholder.com/300x200/003791/FFFFFF?text=PlayStation+5',
            'current_price': 650000,
            'brand': 'Sony',
            'source': 'SSG'
        },
        {
            'name': '[SAMPLE] Microsoft Xbox Series X 게임기',
            'url': 'https://www.ssg.com/item/itemView.ssg?itemId=1000644998510',
            'image_url': 'https://via.placeholder.com/300x200/107C10/FFFFFF?text=Xbox+Series+X',
            'current_price': 580000,
            'brand': 'Microsoft',
            'source': 'SSG'
        },
        {
            'name': '[SAMPLE] Nintendo Switch OLED 게임기',
            'url': 'https://www.ssg.com/item/itemView.ssg?itemId=1000644998511',
            'image_url': 'https://via.placeholder.com/300x200/FF0000/FFFFFF?text=Nintendo+Switch',
            'current_price': 420000,
            'brand': 'Nintendo',
            'source': 'SSG'
        },
        {
            'name': '[SAMPLE] Apple AirPods Pro 2세대',
            'url': 'https://www.ssg.com/item/itemView.ssg?itemId=1000644998512',
            'image_url': 'https://via.placeholder.com/300x200/000000/FFFFFF?text=AirPods+Pro',
            'current_price': 350000,
            'brand': 'Apple',
            'source': 'SSG'
        }
    ]
    
    # 상품 데이터 삽입
    for product in sample_products:
        cursor.execute('''
            INSERT INTO products (name, url, image_url, current_price, brand, source)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (product['name'], product['url'], product['image_url'], 
              product['current_price'], product['brand'], product['source']))
    
    print(f"✅ {len(sample_products)}개 상품 데이터 추가 완료")
    
    # 샘플 알림 데이터 (일부 상품에 대해)
    sample_alerts = [
        (1, 'user1@example.com', 1800000),  # 갤럭시 S24
        (2, 'user2@example.com', 1600000),  # iPhone 15 Pro
        (3, 'user3@example.com', 2700000),  # LG OLED TV
        (5, 'user4@example.com', 2100000),  # Dell XPS
        (10, 'user5@example.com', 1700000), # MacBook Air
        (12, 'user6@example.com', 600000),  # PlayStation 5
        (14, 'user7@example.com', 400000),  # Nintendo Switch
    ]
    
    for product_id, email, target_price in sample_alerts:
        cursor.execute('''
            INSERT INTO alerts (product_id, user_email, target_price, is_active)
            VALUES (?, ?, ?, 1)
        ''', (product_id, email, target_price))
    
    print(f"✅ {len(sample_alerts)}개 알림 데이터 추가 완료")
    
    # 가격 히스토리 데이터 생성 (최근 30일간)
    for product_id in range(1, len(sample_products) + 1):
        base_price = random.randint(100000, 3000000)
        for days_ago in range(30, -1, -1):
            # 가격 변동 (기본 가격의 ±10% 범위)
            price_variation = random.uniform(-0.1, 0.1)
            price = int(base_price * (1 + price_variation))
            
            recorded_at = datetime.now() - timedelta(days=days_ago)
            
            cursor.execute('''
                INSERT INTO price_history (product_id, price, recorded_at)
                VALUES (?, ?, ?)
            ''', (product_id, price, recorded_at.strftime('%Y-%m-%d %H:%M:%S')))
    
    print("✅ 가격 히스토리 데이터 생성 완료")
    
    # 가격 로그 데이터 생성 (최근 7일간)
    for product_id in range(1, len(sample_products) + 1):
        base_price = random.randint(100000, 3000000)
        for days_ago in range(7, -1, -1):
            # 가격 변동 (기본 가격의 ±5% 범위)
            price_variation = random.uniform(-0.05, 0.05)
            price = int(base_price * (1 + price_variation))
            
            logged_at = datetime.now() - timedelta(days=days_ago)
            
            cursor.execute('''
                INSERT INTO price_logs (product_id, price, logged_at)
                VALUES (?, ?, ?)
            ''', (product_id, price, logged_at.strftime('%Y-%m-%d %H:%M:%S')))
    
    print("✅ 가격 로그 데이터 생성 완료")
    
    conn.commit()
    conn.close()
    print("✅ 데이터베이스 초기화 완료!")

if __name__ == "__main__":
    print("🔄 데이터베이스 초기화 시작...")
    conn, cursor = init_database()
    generate_sample_data(conn, cursor)
    print("🎉 모든 작업이 완료되었습니다!") 