import time
import threading
# from database import get_db_connection  # 기존 코드 주석 처리
# from crawler import crawl_ssg_product  # 기존 코드 주석 처리
# from notification import check_price_alerts  # 기존 코드 주석 처리

# === 가격 추적 스케줄러 기능 추가 시작 ===
from price_tracker import price_tracker
import schedule
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# === 가격 추적 스케줄러 기능 추가 끝 ===

# def update_product_prices():  # 기존 함수 주석 처리 시작
#     """모든 상품의 가격을 업데이트"""
#     conn = get_db_connection()
#     products = conn.execute('SELECT * FROM products').fetchall()
#     
#     for product in products:
#         try:
#             # 상품 정보 크롤링
#             product_info = crawl_ssg_product(product['url'])
#             if product_info and product_info['price'] > 0:
#                 new_price = product_info['price']
#                 
#                 # 가격이 변경된 경우에만 업데이트
#                 if new_price != product['current_price']:
#                     # 상품 현재 가격 업데이트
#                     conn.execute(
#                         'UPDATE products SET current_price = ? WHERE id = ?',
#                         (new_price, product['id'])
#                     )
#                     
#                     # 가격 이력 추가
#                     conn.execute(
#                         'INSERT INTO price_logs (product_id, price) VALUES (?, ?)',
#                         (product['id'], new_price)
#                     )
#                     
#                     print(f"상품 '{product['name']}' 가격 업데이트: {product['current_price']} → {new_price}")
#                 
#         except Exception as e:
#             print(f"상품 '{product['name']}' 가격 업데이트 실패: {e}")
#     
#     conn.commit()
#     conn.close()
# 기존 함수 주석 처리 끝

# === 가격 추적 스케줄러 새 함수 시작 ===
def update_product_prices():
    """모든 추적 상품의 가격을 업데이트 (새 가격 추적 시스템)"""
    try:
        logger.info("🔄 가격 추적 시작...")
        price_tracker.check_all_prices()
        logger.info("✅ 가격 추적 완료")
    except Exception as e:
        logger.error(f"❌ 가격 추적 실패: {e}")

def cleanup_old_data():
    """오래된 가격 히스토리 데이터 정리 (7일 이상)"""
    try:
        import sqlite3
        conn = sqlite3.connect('database/ssg_tracker.db')
        cursor = conn.cursor()
        
        # 7일 이상 된 가격 히스토리 삭제
        cursor.execute('''
            DELETE FROM price_history 
            WHERE recorded_at < datetime('now', '-7 days')
        ''')
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        if deleted_count > 0:
            logger.info(f"🗑️ 오래된 가격 데이터 {deleted_count}개 정리 완료")
            
    except Exception as e:
        logger.error(f"❌ 데이터 정리 실패: {e}")
# === 가격 추적 스케줄러 새 함수 끝 ===

# def price_monitoring_scheduler():  # 기존 함수 주석 처리 시작
#     """가격 모니터링 스케줄러"""
#     while True:
#         try:
#             print("가격 업데이트 시작...")
#             update_product_prices()
#             
#             print("알림 체크 시작...")
#             check_price_alerts()
#             
#             print("다음 업데이트까지 대기 중... (30분)")
#             time.sleep(1800)  # 30분마다 실행
#             
#         except Exception as e:
#             print(f"스케줄러 오류: {e}")
#             time.sleep(300)  # 오류 시 5분 후 재시도
# 기존 함수 주석 처리 끝

# === 가격 추적 스케줄러 새 함수 시작 ===
def price_monitoring_scheduler():
    """가격 모니터링 스케줄러 (3시간마다 실행)"""
    # 스케줄 설정
    schedule.every(3).hours.do(update_product_prices)  # 3시간마다 가격 체크
    schedule.every().day.at("02:00").do(cleanup_old_data)  # 매일 새벽 2시에 데이터 정리
    
    logger.info("📅 가격 추적 스케줄러 시작 (3시간마다 실행)")
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 스케줄 체크
        except Exception as e:
            logger.error(f"❌ 스케줄러 오류: {e}")
            time.sleep(300)  # 오류 시 5분 후 재시도
# === 가격 추적 스케줄러 새 함수 끝 ===

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