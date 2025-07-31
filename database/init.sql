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

-- 상품 추적 목록 테이블 (가격 추적 기능)
CREATE TABLE IF NOT EXISTS watch_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    product_url TEXT NOT NULL,
    image_url TEXT,
    source TEXT NOT NULL,
    current_price REAL NOT NULL,
    target_price REAL,
    user_email TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 가격 변동 히스토리 테이블
CREATE TABLE IF NOT EXISTS price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    watch_id INTEGER NOT NULL,
    price REAL NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (watch_id) REFERENCES watch_list(id) ON DELETE CASCADE
);

-- 가격 알림 로그 테이블
CREATE TABLE IF NOT EXISTS price_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    watch_id INTEGER NOT NULL,
    old_price REAL NOT NULL,
    new_price REAL NOT NULL,
    alert_type TEXT NOT NULL,
    email_sent INTEGER DEFAULT 0,
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (watch_id) REFERENCES watch_list(id) ON DELETE CASCADE
);

-- 임시 추적 목록 테이블 (이메일 입력 전 임시 저장)
CREATE TABLE IF NOT EXISTS temp_watch_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    product_url TEXT NOT NULL,
    image_url TEXT,
    source TEXT NOT NULL,
    current_price REAL NOT NULL,
    target_price REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_price_logs_product_id ON price_logs(product_id);
CREATE INDEX IF NOT EXISTS idx_price_logs_logged_at ON price_logs(logged_at);
CREATE INDEX IF NOT EXISTS idx_alerts_product_id ON alerts(product_id);
CREATE INDEX IF NOT EXISTS idx_alerts_is_active ON alerts(is_active);

-- 추적 목록 관련 인덱스
CREATE INDEX IF NOT EXISTS idx_watch_list_user_email ON watch_list(user_email);
CREATE INDEX IF NOT EXISTS idx_watch_list_source ON watch_list(source);
CREATE INDEX IF NOT EXISTS idx_watch_list_is_active ON watch_list(is_active);
CREATE INDEX IF NOT EXISTS idx_watch_list_created_at ON watch_list(created_at);

-- 가격 히스토리 관련 인덱스
CREATE INDEX IF NOT EXISTS idx_price_history_watch_id ON price_history(watch_id);
CREATE INDEX IF NOT EXISTS idx_price_history_recorded_at ON price_history(recorded_at);

-- 가격 알림 관련 인덱스
CREATE INDEX IF NOT EXISTS idx_price_alerts_watch_id ON price_alerts(watch_id);
CREATE INDEX IF NOT EXISTS idx_price_alerts_alert_type ON price_alerts(alert_type);
CREATE INDEX IF NOT EXISTS idx_price_alerts_email_sent ON price_alerts(email_sent);

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