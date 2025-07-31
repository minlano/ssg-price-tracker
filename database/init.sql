-- SSG 가격 추적 시스템 데이터베이스 초기화

-- 상품 테이블 (개선된 버전)
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    current_price INTEGER,
    image_url TEXT,
    brand TEXT,
    description TEXT,
    source TEXT DEFAULT 'SSG',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 가격 이력 테이블
CREATE TABLE IF NOT EXISTS price_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    price INTEGER NOT NULL,
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- 알림 설정 테이블
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    user_email TEXT NOT NULL,
    target_price INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_price_logs_product_id ON price_logs(product_id);
CREATE INDEX IF NOT EXISTS idx_price_logs_logged_at ON price_logs(logged_at);
CREATE INDEX IF NOT EXISTS idx_alerts_product_id ON alerts(product_id);
CREATE INDEX IF NOT EXISTS idx_alerts_is_active ON alerts(is_active);

-- 샘플 데이터 (테스트용)
INSERT OR IGNORE INTO products (name, url, current_price) VALUES 
('테스트 상품 1', 'https://www.ssg.com/item/itemView.ssg?itemId=1000000000001', 50000),
('테스트 상품 2', 'https://www.ssg.com/item/itemView.ssg?itemId=1000000000002', 75000);

-- 샘플 가격 이력
INSERT OR IGNORE INTO price_logs (product_id, price) VALUES 
(1, 55000),
(1, 52000),
(1, 50000),
(2, 80000),
(2, 77000),
(2, 75000);