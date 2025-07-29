import time
import threading
from database import get_db_connection
from crawler import crawl_ssg_product
from notification import check_price_alerts

def update_product_prices():
    """모든 상품의 가격을 업데이트"""
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    
    for product in products:
        try:
            # 상품 정보 크롤링
            product_info = crawl_ssg_product(product['url'])
            if product_info and product_info['price'] > 0:
                new_price = product_info['price']
                
                # 가격이 변경된 경우에만 업데이트
                if new_price != product['current_price']:
                    # 상품 현재 가격 업데이트
                    conn.execute(
                        'UPDATE products SET current_price = ? WHERE id = ?',
                        (new_price, product['id'])
                    )
                    
                    # 가격 이력 추가
                    conn.execute(
                        'INSERT INTO price_logs (product_id, price) VALUES (?, ?)',
                        (product['id'], new_price)
                    )
                    
                    print(f"상품 '{product['name']}' 가격 업데이트: {product['current_price']} → {new_price}")
                
        except Exception as e:
            print(f"상품 '{product['name']}' 가격 업데이트 실패: {e}")
    
    conn.commit()
    conn.close()

def price_monitoring_scheduler():
    """가격 모니터링 스케줄러"""
    while True:
        try:
            print("가격 업데이트 시작...")
            update_product_prices()
            
            print("알림 체크 시작...")
            check_price_alerts()
            
            print("다음 업데이트까지 대기 중... (30분)")
            time.sleep(1800)  # 30분마다 실행
            
        except Exception as e:
            print(f"스케줄러 오류: {e}")
            time.sleep(300)  # 오류 시 5분 후 재시도

def start_scheduler():
    """스케줄러 시작"""
    thread = threading.Thread(target=price_monitoring_scheduler, daemon=True)
    thread.start()
    print("가격 모니터링 스케줄러가 시작되었습니다.")

if __name__ == '__main__':
    start_scheduler()
    # 메인 스레드 유지
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("스케줄러가 종료되었습니다.")