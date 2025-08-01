import sqlite3
from database import get_db_connection

try:
    conn = get_db_connection()
    
    # products 테이블 구조 확인
    cursor = conn.execute("PRAGMA table_info(products)")
    columns = cursor.fetchall()
    print("products 테이블 구조:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # 최근 추가된 상품 확인
    cursor = conn.execute("SELECT * FROM products ORDER BY id DESC LIMIT 5")
    recent_products = cursor.fetchall()
    print(f"\n최근 추가된 상품 (총 {len(recent_products)}개):")
    for product in recent_products:
        print(f"  - ID: {product['id']}, 이름: {product['name']}, URL: {product['url']}, 가격: {product['current_price']}")
    
    conn.close()
    
except Exception as e:
    print(f"오류: {e}") 