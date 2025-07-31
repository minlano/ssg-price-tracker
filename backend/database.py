import sqlite3
import os

DATABASE_PATH = '../database/ssg_tracker.db'

def get_db_connection():
    """데이터베이스 연결"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    
    # 한국 시간대 설정
    conn.execute("PRAGMA timezone = '+09:00'")
    
    return conn

def init_db():
    """데이터베이스 초기화"""
    # 데이터베이스 디렉토리 생성
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    conn = get_db_connection()
    
    # 테이블 생성
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            current_price INTEGER,
            image_url TEXT,
            brand TEXT,
            description TEXT,
            source TEXT DEFAULT 'SSG',
            created_at TIMESTAMP DEFAULT (datetime('now', '+09:00'))
        );
        
        CREATE TABLE IF NOT EXISTS price_logs (
            id INTEGER PRIMARY KEY,
            product_id INTEGER,
            price INTEGER,
            logged_at TIMESTAMP DEFAULT (datetime('now', '+09:00')),
            FOREIGN KEY (product_id) REFERENCES products(id)
        );
        
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY,
            product_id INTEGER,
            user_email TEXT,
            target_price INTEGER,
            is_active BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (product_id) REFERENCES products(id)
        );
    ''')
    
    # 기존 테이블에 새 컬럼 추가 (이미 존재하는 경우 무시)
    try:
        conn.execute('ALTER TABLE products ADD COLUMN image_url TEXT')
    except:
        pass
    
    try:
        conn.execute('ALTER TABLE products ADD COLUMN brand TEXT')
    except:
        pass
    
    try:
        conn.execute('ALTER TABLE products ADD COLUMN description TEXT')
    except:
        pass
    
    try:
        conn.execute('ALTER TABLE products ADD COLUMN source TEXT DEFAULT "SSG"')
    except:
        pass
    
    conn.commit()
    conn.close()
    print("데이터베이스가 초기화되었습니다.")

if __name__ == '__main__':
    init_db()